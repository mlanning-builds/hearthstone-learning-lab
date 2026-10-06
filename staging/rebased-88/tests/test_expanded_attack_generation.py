import unittest
from copy import deepcopy
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded import attack_generation as ag
from expanded.generation_cards import pool
from engine.cards import UnsupportedCard
class AttackGenerationTests(unittest.TestCase):
 def setUp(self):self.h=fixtures.GenerationTests();self.g=self.h.game();self.p=self.g.players[0]
 def install(self,cost):
  d=deepcopy(self.g.cards['CS3_025']);d.update(id='ATTACK_TEST',cost=cost,dbfId=-98214)
  self.g.cards[d['id']]=d;self.h.install(self.g,pool(card_type='MINION',minimum=cost,maximum=cost),[d['id']])
 def run_effect(self):self.h.run_ops(self.g,ag.RULES['JAIL_200'][1])
 def test_hero_attack_counts_and_survives_turn(self):
  self.p.temporary_attack=1;self.g.step(Action('attack',-1,-2));self.assertEqual(self.p.hero_attacks_total,1)
  self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(self.p.hero_attacks_total,1);self.assertEqual(self.p.hero_attacks,0)
 def test_opponent_and_minion_attacks_do_not_count_for_owner(self):
  self.g.players[1].temporary_attack=1;self.g._resolve_combat(-2,-1,[])
  self.assertEqual(self.p.hero_attacks_total,0);self.assertEqual(self.g.players[1].hero_attacks_total,1)
  m=self.g._summon(0,'CS3_025');self.g._resolve_combat(m.uid,-2,[]);self.assertEqual(self.p.hero_attacks_total,0)
 def test_base_three_summons_twice(self):
  self.install(3);self.run_effect();self.assertEqual(len(self.p.board),2)
 def test_total_not_current_turn_selects_cost(self):
  self.p.hero_attacks_total=4;self.p.hero_attacks=0;self.install(7);self.run_effect();self.assertEqual(len(self.p.board),2)
 def test_missing_exact_pool_does_not_fall_back(self):
  self.install(3);self.p.hero_attacks_total=1;state=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.run_effect()
  self.assertEqual(state,self.g.rng.getstate());self.assertFalse(self.p.board)
 def test_one_slot_only_summons_one(self):
  self.install(3)
  for _ in range(6):self.g._summon(0,'CS3_025')
  self.run_effect();self.assertEqual(len(self.p.board),7)
 def test_counter_is_public_and_cloned(self):
  self.p.hero_attacks_total=4;other=deepcopy(self.g)
  self.assertEqual(other.players[0].hero_attacks_total,4)
  self.assertEqual(self.g.observe(1)['players'][0]['hero_attacks_total'],4)
 def test_not_live_registered(self):self.assertNotIn('JAIL_200',cards.COLLECTIBLE_IDS)
