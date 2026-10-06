import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures

class DamageAttributionTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.events=[]
  original=self.g._queue_event
  def capture(kind,**data):
   if kind=='damage':self.events.append(data.copy())
   return original(kind,**data)
  self.g._queue_event=capture
 def effect(self,owner,target,amount=2):
  return self.g._deal_effect(target,amount,dict(owner=owner,source=None,bonus=0,lifesteal=False))
 def test_opponent_turn_effect_keeps_controller(self):
  self.effect(1,-1);self.assertEqual(self.events[-1]['damage_owner'],1);self.assertEqual(self.events[-1]['target_owner'],0)
 def test_armor_damage_is_still_damage(self):
  self.g.players[1].armor=5;self.effect(0,-2);self.assertEqual(self.events[-1]['amount'],2);self.assertEqual(self.g.players[1].health,30)
 def test_prevented_damage_publishes_no_event(self):
  self.g.players[1].divine_shield=True;self.effect(0,-2);self.assertEqual(self.events,[])
 def test_unattributed_damage_does_not_inherit_current_player(self):
  self.g._damage(-2,2);self.assertIsNone(self.events[-1]['damage_owner'])
 def test_unattributed_damage_does_not_inherit_outer_minion(self):
  m=self.g._summon(0,'CORE_EX1_162');self.g._damage_origin=m
  self.g._damage(-2,2);self.assertIsNone(self.events[-1]['damage_owner'])
 def test_explicit_minion_source_retains_owner_and_identity(self):
  m=self.g._summon(1,'CORE_EX1_162');self.g._damage(-1,2,damage_source=m)
  self.assertEqual(self.events[-1]['damage_owner'],1);self.assertEqual(self.events[-1]['source_uid'],m.uid)
 def test_combat_retaliation_has_defender_owner(self):
  a=self.g._summon(0,'CORE_EX1_162');b=self.g._summon(1,'CORE_EX1_162');self.events.clear()
  self.g._resolve_combat(a.uid,b.uid,[])
  self.assertEqual([(e['damage_owner'],e['target_owner']) for e in self.events],[(0,1),(1,0)])
 def test_hero_attack_has_owner_without_minion_source(self):
  self.g.players[0].hero_attack=2
  with patch.object(self.g,'_hero_attack',return_value=2):self.g._resolve_combat(-1,-2,[])
  self.assertEqual(self.events[0]['damage_owner'],0);self.assertIsNone(self.events[0]['source_uid'])
 def test_invalid_controller_rejected_before_mutation(self):
  before=self.g.players[1].health
  with self.assertRaises(ValueError):self.g._damage(-2,2,damage_owner=True)
  self.assertEqual(self.g.players[1].health,before)
 def test_explicit_owner_does_not_leak_into_next_damage(self):
  self.effect(1,-1);self.g._damage(-2,2);self.assertIsNone(self.events[-1]['damage_owner'])
 def test_basic_power_has_explicit_controller(self):
  self.g._base_power(-2);self.assertEqual(self.events[-1]['damage_owner'],0)
 def test_replacement_power_has_explicit_controller(self):
  self.g.players[1].primary_power=dict(card_id='JAIL_EVENT_101hp',damage=2)
  self.g._replacement_power_effect(1);self.assertEqual(self.events[-1]['damage_owner'],1)
 def test_fatigue_inside_minion_effect_has_no_source(self):
  self.g.players[1].deck=[];self.g._damage_origin=self.g._summon(0,'CORE_EX1_162')
  self.g._draw(1);self.assertIsNone(self.events[-1]['damage_owner']);self.assertIsNone(self.events[-1]['source_uid'])
 def test_corpse_missiles_keep_opponent_controller(self):
  self.g.players[1].corpses=1
  self.g._system_effect(('corpse_missiles',1,2),dict(owner=1,source=None))
  self.assertEqual(self.events[-1]['damage_owner'],1)
 def test_location_damage_has_controller_and_source(self):
  from expanded import Action
  m=self.g._summon(1,'CORE_EX1_162');loc=self.g._place_location(0,'CORE_REV_990')
  self.g._activate_location(Action('activate',loc.uid,m.uid))
  self.assertEqual(self.events[-1]['damage_owner'],0);self.assertEqual(self.events[-1]['source_uid'],loc.uid)
 def test_location_is_not_a_minion_killer(self):
  from types import SimpleNamespace
  loc=self.g._place_location(0,'CORE_REV_990')
  victim=SimpleNamespace(card_id='CATA_185',health=0,rule_state={},silenced=False)
  self.g._entity_damage(victim,loc,2);self.assertNotIn('killed_by_minion',victim.rule_state)
