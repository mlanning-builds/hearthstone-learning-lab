import unittest
from dataclasses import asdict
from expanded.generation_cards import pool,PoolRequest
from expanded.generation import request_matches
class AttackPoolTests(unittest.TestCase):
 def card(self,attack=8,**kw):
  return dict(dict(id='FIXTURE_BEAST',type='MINION',cost=2,attack=attack,races=['BEAST'],cardClass='NEUTRAL'),**kw)
 def test_exact_attack_independent_of_cost(self):
  r=pool(card_type='MINION',tribe='BEAST',attack_minimum=8,attack_maximum=8)
  self.assertTrue(request_matches(r,self.card(),'HUNTER'));self.assertFalse(request_matches(r,self.card(7),'HUNTER'))
 def test_both_cost_and_attack_constraints_apply(self):
  r=pool(minimum=3,attack_minimum=8);self.assertFalse(request_matches(r,self.card(),'HUNTER'))
 def test_missing_attack_never_becomes_zero(self):
  d=self.card();del d['attack'];self.assertFalse(request_matches(pool(attack_maximum=0),d,'HUNTER'))
 def test_zero_attack_is_valid(self):
  self.assertTrue(request_matches(pool(attack_minimum=0,attack_maximum=0),self.card(0),'HUNTER'))
 def test_invalid_bounds_rejected(self):
  for kw in [dict(attack_minimum=-1),dict(attack_maximum=True),dict(attack_minimum=3.0),dict(attack_minimum=8,attack_maximum=6)]:
   with self.subTest(kw=kw),self.assertRaises(ValueError):pool(**kw)
 def test_roundtrip_contract_key(self):
  r=pool(attack_minimum=6,attack_maximum=6);self.assertEqual(PoolRequest(**asdict(r)),r);self.assertEqual(hash(PoolRequest(**asdict(r))),hash(r))
 def test_attack_pools_have_distinct_keys(self):
  self.assertNotEqual(pool(attack_minimum=8),pool(attack_minimum=6))
 def test_legacy_request_does_not_require_attack(self):
  d=self.card();del d['attack'];self.assertTrue(request_matches(pool(),d,'HUNTER'))
