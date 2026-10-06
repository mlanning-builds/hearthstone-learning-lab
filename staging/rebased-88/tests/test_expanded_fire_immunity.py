"""Staged Fyrakk immunity paths; no production admission or pool approval."""
from copy import deepcopy
import unittest
import test_expanded_generation as fixtures
from standard.catalog import load_catalog

class FireImmunityTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game()
  self.g.cards['FIR_959']=deepcopy(next(c for c in load_catalog() if c['id']=='FIR_959'))
  self.a=self.g._summon(0,'FIR_959');self.b=self.g._summon(1,'FIR_959')
 def run_op(self,op,fire=True,**ctx):
  self.fx.run_ops(self.g,[op],spell=True,card_id='CORE_CS2_029' if fire else 'CORE_CS2_004',**ctx)
 def test_global_fire_destruction_preserves_both_protected_entities(self):
  for op in (('destroy_all_minions',),('destroy_small',99),('destroy_large',0)):
   with self.subTest(op=op):
    self.setUp();ordinary=self.g._summon(1,'NEW1_034');self.run_op(op)
    self.assertIn(self.a,self.g.players[0].board);self.assertIn(self.b,self.g.players[1].board)
    self.assertEqual((self.a.health,self.b.health),(7,7));self.assertNotIn(ordinary,self.g.players[1].board)
 def test_global_nonfire_destruction_still_removes_fyrakk(self):
  self.run_op(('destroy_all_minions',),fire=False)
  self.assertFalse(self.g.players[0].board);self.assertFalse(self.g.players[1].board)
 def test_silence_removes_fire_protection(self):
  self.g._silence(self.b);self.run_op(('destroy_all_minions',))
  self.assertIn(self.a,self.g.players[0].board);self.assertNotIn(self.b,self.g.players[1].board)
 def test_global_stat_replacement_does_not_change_protected_stats(self):
  for op in (('health_one',),('set_others_attack',1),('set_others_health',1),('set_enemies_stats',1,1)):
   with self.subTest(op=op):
    self.setUp();ordinary=self.g._summon(1,'NEW1_034');self.run_op(op)
    for m in (self.a,self.b):self.assertEqual((m.attack,m.health,m.max_health),(7,7,7))
    if op[0]!='set_others_attack':self.assertEqual(ordinary.max_health,1)
    else:self.assertEqual(ordinary.attack,1)
 def test_global_fire_shuffle_preserves_board_and_excludes_protected_deck_copies(self):
  self.g._summon(0,'NEW1_034');self.g._summon(1,'NEW1_034')
  before=sum(len(p.deck) for p in self.g.players);self.run_op(('b60_shuffle_all',))
  self.assertEqual(self.g.players[0].board,[self.a]);self.assertEqual(self.g.players[1].board,[self.b])
  self.assertEqual(sum(len(p.deck) for p in self.g.players),before+2)
  self.assertFalse(any(self.g._card_data(c)['id']=='FIR_959' for p in self.g.players for c in p.deck))
 def test_protected_board_transform_does_not_request_pool_or_consume_rng(self):
  before=self.g.rng.getstate();self.run_op(('mutation_board',1,True))
  self.assertEqual(self.a.card_id,'FIR_959');self.assertEqual(self.g.rng.getstate(),before)
 def test_protected_life_cycle_does_not_spawn_a_replacement(self):
  before=self.g.rng.getstate();self.run_op(('mutation_life_cycle',),target=self.b.uid)
  self.assertEqual(self.g.players[1].board,[self.b]);self.assertEqual(self.g.rng.getstate(),before)
 def test_captured_transform_rechecks_current_immunity(self):
  from expanded.transformations import cost_pool
  before=self.g.rng.getstate();self.run_op(('mutation_board_one',self.a.uid,cost_pool(11),False))
  self.assertEqual(self.a.card_id,'FIR_959');self.assertEqual(self.g.rng.getstate(),before)
