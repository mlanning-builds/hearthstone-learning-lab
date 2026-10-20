"""Evolve cap and board eligibility across production shared helpers."""
import unittest
from expanded.transformations import evolve_pool,cost_pool
from expanded.generation_cards import board_pool
from engine.cards import UnsupportedCard
import test_expanded_transformations as fixtures

class EvolveBoundaryTests(fixtures.TransformationTests):
 def test_evolve_high_cost_uses_ten_cost_outcome(self):
  original=self.fake('HIGH_ORIGINAL',10);result=self.fake('TEN_RESULT',10)
  m=self.g._summon(0,original);self.install(board_pool(cost_pool(10)),[result])
  self.run_card('CATA_567')
  self.assertEqual(self.p.minions[0].card_id,result)
 def test_board_evolve_rejects_colossal_before_mutation_or_rng(self):
  original=self.fake('EVOLVE_SOURCE',9);colossal=self.fake('EVOLVE_COLOSSAL',10)
  self.g.cards[colossal]['mechanics']=['COLOSSAL']
  m=self.g._summon(0,original);before=self.g.rng.getstate()
  self.install(board_pool(cost_pool(10)),[colossal])
  with self.assertRaisesRegex(UnsupportedCard,'ineligible'):self.run_card('CATA_567')
  self.assertEqual(m.card_id,original);self.assertEqual(self.g.rng.getstate(),before)
 def test_hand_pool_keeps_colossal_eligible(self):
  self.assertEqual(evolve_pool(9,2,board=False),cost_pool(10))
  self.assertEqual(evolve_pool(9,2),board_pool(cost_pool(10)))
