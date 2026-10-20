"""Client exclusions are independent of written coverage and deck legality."""
import unittest
from expanded.generation import request_matches
from expanded.generation_cards import pool
from expanded.historical_generation_catalog import load_universe,historical_contract
from expanded.generation_catalog import load_universe as standard_universe,standard_contract
from expanded.historical_generation import MINION
from expanded.cards import registry
import test_expanded_generation as fixtures

class GenerationBanTests(unittest.TestCase):
 def test_bare_zilliax_excluded_from_historical_random_pools(self):
  universe=load_universe();data=universe.records['TOY_330']
  self.assertIn('TOY_330',universe.members)
  self.assertFalse(request_matches(MINION,data,'MAGE'))
  self.assertNotIn('TOY_330',historical_contract(MINION,'MAGE',universe).card_ids)
  self.assertIn('TOY_330',registry())
 def test_underbelly_excluded_from_standard_random_and_discover(self):
  universe=standard_universe();request=pool(card_type='MINION',tribe='BEAST')
  self.assertIn('JAIL_831',universe.records)
  for hero in ('MAGE','HUNTER','DEATHKNIGHT'):
   self.assertNotIn('JAIL_831',standard_contract(request,hero,universe).card_ids)
 def test_underbelly_without_submitted_band_has_no_discover(self):
  g=fixtures.GenerationTests().game();p=g.players[0];p.contraband_beasts=()
  before=g.rng.getstate()
  self.assertTrue(g._remaining_setup_effect(('contraband_discover',),dict(owner=0,source=None)))
  self.assertIsNone(g.pending_choice);self.assertEqual(g.rng.getstate(),before)
 def test_underbelly_with_submitted_band_still_offers_actual_members(self):
  g=fixtures.GenerationTests().game();g.players[0].contraband_beasts=('CS2_231',)
  g._remaining_setup_effect(('contraband_discover',),dict(owner=0,source=None))
  self.assertEqual([v['card_id'] for v in g.pending_choice['options']],['CS2_231'])
