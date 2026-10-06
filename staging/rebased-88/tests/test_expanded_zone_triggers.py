import unittest,gzip,json
from pathlib import Path
from unittest.mock import patch
from copy import deepcopy
import test_expanded_generation as fixtures
from expanded import cards,zone_triggers
from engine.game import Card

class ZoneTriggerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in zone_triggers.RULES})
  p=patch.dict(cards.RULES,zone_triggers.RULES);p.start();self.addCleanup(p.stop)
 def grant(self):self.g._effect(('hero_eternal_life',),dict(owner=0))
 def settle(self):self.g._settle(allow_event_choices=True)
 def damage_four(self):
  for _ in range(3):
   m=self.g._summon(0,'NEW1_034');self.g._damage(m.uid,1)
  self.g._damage(-1,1)
 def test_husk_consumes_once_and_spends_at_most_twenty(self):
  self.grant();self.p.corpses=27;self.p.health=-100;self.g._check_heroes()
  self.assertEqual((self.p.health,self.p.corpses,self.p.eternal_life),(20,7,False));self.assertFalse(self.g.terminal)
  self.p.health=0;self.g._check_heroes();self.assertTrue(self.g.terminal)
 def test_repeated_battlecry_does_not_stack(self):
  self.grant();self.grant();self.p.corpses=40;self.p.health=0;self.g._check_heroes()
  self.assertEqual(self.p.corpses,20);self.assertFalse(self.p.eternal_life)
 def test_zero_corpses_does_not_save_hero(self):
  self.grant();self.p.corpses=0;self.p.health=0;self.g._check_heroes();self.assertTrue(self.g.terminal)
 def test_small_payment_and_no_healing_trigger(self):
  self.grant();self.p.corpses=3;self.p.health=-10;self.g._check_heroes()
  self.assertEqual(self.p.health,3);self.assertEqual(self.p.max_health,30);self.assertEqual(self.p.healing_done_turn,0)
 def test_simultaneous_lethal_resurrects_only_enchanted_hero(self):
  self.grant();self.p.corpses=9;self.p.health=self.q.health=0;self.g._check_heroes()
  self.assertEqual(self.p.health,9);self.assertTrue(self.g.terminal);self.assertEqual(self.g.winner,0)
 def test_both_heroes_can_resurrect(self):
  for p in self.g.players:p.eternal_life=True;p.corpses=12;p.health=0
  self.g._check_heroes();self.assertFalse(self.g.terminal);self.assertEqual([p.health for p in self.g.players],[12,12])
 def test_enchantment_survives_source_silence(self):
  m=self.g._summon(0,'TIME_618');self.grant();self.g._silence(m);self.p.corpses=4;self.p.health=0;self.g._check_heroes();self.assertEqual(self.p.health,4)
 def test_warptooth_four_distinct_characters_recruits_physical_hand_buffs(self):
  c=Card(self.g._new_id(),'JAIL_421');c.attack_bonus=2;c.health_bonus=3;self.p.hand.append(c)
  self.damage_four();self.settle();m=next(m for m in self.p.minions if m.card_id=='JAIL_421')
  self.assertEqual((m.attack,m.health),(5,6));self.assertNotIn(c,self.p.hand);self.assertIn('CHARGE',self.g._effective_keywords(m))
 def test_same_character_repeated_damage_does_not_trigger(self):
  self.p.deck=['JAIL_421'];
  for _ in range(4):self.g._damage(-1,1)
  self.settle();self.assertEqual(self.p.deck,['JAIL_421']);self.assertEqual(len(self.p.damaged_characters_turn),1)
 def test_opponent_turn_does_not_count(self):
  self.g.current=1;self.p.deck=['JAIL_421'];self.damage_four();self.settle();self.assertFalse(self.p.damaged_characters_turn);self.assertEqual(self.p.deck,['JAIL_421'])
 def test_deck_recruit_does_not_draw_or_play_battlecry(self):
  self.p.deck=['JAIL_421'];self.damage_four();self.settle();self.assertEqual(self.p.deck,[]);self.assertFalse(self.p.hand);self.assertEqual(self.p.cards_played,0)
 def test_shield_prevents_character_from_counting(self):
  self.p.divine_shield=True;self.g._damage(-1,1);self.assertFalse(self.p.damaged_characters_turn)
 def test_full_board_keeps_card_in_zone(self):
  for _ in range(7):self.g._summon(0,'NEW1_034')
  self.p.deck=['JAIL_421']
  for m in self.p.minions[:4]:self.g._damage(m.uid,1)
  self.settle();self.assertEqual(self.p.deck[0].card_id,'JAIL_421');self.assertEqual(len(self.p.board),7)
 def test_queued_trigger_does_not_summon_card_removed_before_resolution(self):
  self.p.deck=['JAIL_421'];self.damage_four();self.p.deck=[];self.settle();self.assertFalse(any(m.card_id=='JAIL_421' for m in self.p.minions))
 def test_clone_retains_enchantment_and_independent_damage_history(self):
  self.grant();self.g._damage(-1,1);clone=deepcopy(self.g);clone.players[0].damaged_characters_turn.add(999)
  self.assertTrue(clone.players[0].eternal_life);self.assertNotIn(999,self.p.damaged_characters_turn)
 def test_turn_transition_resets_history(self):
  self.g._damage(-1,1);self.g._end_turn();self.assertFalse(self.p.damaged_characters_turn)
 def test_public_state_does_not_expose_hidden_recruit(self):
  self.p.deck=['JAIL_421'];self.grant();view=self.g.observe(1)['players'][0]
  self.assertTrue(view['eternal_life']);self.assertNotIn('JAIL_421',str(view));self.assertEqual(view['damaged_characters_turn'],0)
