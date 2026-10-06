import unittest,gzip,json
from unittest.mock import patch
from copy import deepcopy
import test_expanded_generation as fixtures
from expanded import Action,cards,secrets,infinity
from engine.game import Card
class InfinityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f) if c['id'] in infinity.RULES}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players;self.g.cards.update(deepcopy(self.records))
  for table,data in ((cards.RULES,infinity.RULES),(cards.DEATH_EFFECTS,infinity.DEATH_EFFECTS),(secrets.SECRETS,infinity.SECRETS)):
   c=patch.dict(table,data);c.start();self.addCleanup(c.stop)
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def test_weapon_attack_and_hero_exclusion(self):
  self.play('END_012');self.assertEqual(self.p.weapon['attack'],infinity.INFINITY);self.assertFalse(any(a.kind=='attack' and a.target<0 for a in self.g.legal_actions()))
 def test_weapon_restores_after_turn_retaining_buff(self):
  self.play('END_012');self.g._buff_weapon(0,attack=2);self.g.step(Action('end'));self.assertEqual(self.p.weapon['attack'],6)
 def test_replacement_weapon_not_modified_by_old_expiry(self):
  self.play('END_012');self.g._equip(0,next(cid for cid,d in self.g.cards.items() if d['type']=='WEAPON' and cid!='END_012'));before=self.p.weapon['attack'];self.g.step(Action('end'));self.assertEqual(self.p.weapon['attack'],before)
 def test_acolyte_cost_restores_existing_discount(self):
  c=self.g._add(0,'CORE_CS2_029');c.cost_delta=-2;before=self.g._cost(c,0);self.play('END_018');self.assertEqual(self.g._cost(c,0),infinity.INFINITY-2)
  self.p.minions[0].health=0;self.g._settle();self.assertEqual(self.g._cost(c,0),before)
 def test_cost_layers_restore_independently(self):
  c=self.g._add(0,'CORE_CS2_029');self.play('END_018');self.play('END_018');a,b=self.p.minions;a.health=0;self.g._settle();self.assertEqual(self.g._cost(c,0),infinity.INFINITY);b.health=0;self.g._settle();self.assertEqual(self.g._cost(c,0),4)
 def test_silence_removes_restoration(self):
  c=self.g._add(0,'CORE_CS2_029');self.play('END_018');m=self.p.minions[0];self.g._silence(m);m.health=0;self.g._settle();self.assertEqual(self.g._cost(c,0),infinity.INFINITY)
 def test_empty_hand_acolyte_is_noop(self):
  self.play('END_018');self.p.minions[0].health=0;self.g._settle();self.assertFalse(self.p.hand)
 def test_murozond_waits_until_next_own_turn(self):
  self.play('TIME_024');m=self.p.minions[0];self.assertEqual(m.attack,8);self.g.step(Action('end'));self.assertEqual(m.attack,8);self.g.step(Action('end'));self.assertEqual(m.attack,infinity.INFINITY)
 def test_murozond_does_not_affect_new_copy_after_death(self):
  self.play('TIME_024');self.p.minions[0].health=0;self.g._settle();m=self.g._summon(0,'TIME_024');self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(m.attack,8)
 def test_flames_waits_for_enemy_end_and_uses_highest_health(self):
  low=self.g._summon(1,'CORE_EX1_162');high=self.g._summon(1,'TIME_024');self.play('END_024');self.g.step(Action('end'));self.assertIn(high,self.q.minions);self.g.step(Action('end'));self.assertNotIn(high,self.q.minions);self.assertIn(low,self.q.minions);self.assertFalse(self.p.secrets)
 def test_flames_empty_enemy_board_keeps_secret(self):
  self.play('END_024');self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(len(self.p.secrets),1)
 def test_flames_divine_shield_prevents_damage(self):
  m=self.g._summon(1,'TIME_024');m.keywords.add('DIVINE_SHIELD');self.play('END_024');self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(m.health,8);self.assertNotIn('DIVINE_SHIELD',m.keywords)
 def test_infinity_observations_remain_json_serializable(self):
  self.g._add(0,'CORE_CS2_029');self.play('END_018');json.dumps(self.g.observe(0),allow_nan=False);json.dumps(self.g.observe(1),allow_nan=False)
 def test_silencing_murozond_cancels_delayed_enchantment(self):
  self.play('TIME_024');m=self.p.minions[0];self.g._silence(m);self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(m.attack,8)
 def test_copy_inherits_murozond_pending_enchantment(self):
  self.play('TIME_024');m=self.p.minions[0];other=self.g._summon(0,'TIME_024',copy_from=m);self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual((m.attack,other.attack),(infinity.INFINITY,infinity.INFINITY))
