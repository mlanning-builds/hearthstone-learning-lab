import unittest
from expanded.generation import request_matches
from expanded.generation_cards import pool,board_pool
from expanded.historical_generation import requests_for
from expanded.historical_generation_catalog import load_universe,historical_contract
class GenerationExclusionTests(unittest.TestCase):
 def test_titans_excluded_from_every_random_minion_destination(self):
  u=load_universe();titans=[d for d in u.records.values() if d.get('collectible') and 'TITAN' in d.get('mechanics',())]
  self.assertTrue(titans)
  for d in titans:
   for request in (pool(card_type='MINION'),pool(card_type='MINION',era='past'),board_pool(pool(card_type='MINION',era='past'))):
    with self.subTest(cid=d['id'],request=request):self.assertFalse(request_matches(request,d,'DEATHKNIGHT'))
 def test_actual_amber_request_excludes_colossals_and_titans(self):
  u=load_universe();request,=requests_for('TIME_052')
  self.assertEqual(request.excluded_mechanic,'COLOSSAL')
  contract=historical_contract(request,'DEATHKNIGHT',u)
  self.assertTrue(contract.card_ids)
  self.assertFalse(any(set(u.records[cid].get('mechanics',())) & {'COLOSSAL','TITAN'} for cid in contract.card_ids))
 def test_literal_colossal_pool_remains_intact(self):
  u=load_universe();request=pool(card_type='MINION',mechanic='COLOSSAL',era='past')
  contract=historical_contract(request,'DEATHKNIGHT',u)
  self.assertEqual(len(contract.card_ids),13)
if __name__=='__main__':unittest.main()
