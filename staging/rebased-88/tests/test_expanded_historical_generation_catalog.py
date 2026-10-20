"""Full historical membership and fail-closed execution are separate contracts."""
import unittest
from dataclasses import replace
from standard.catalog import load_all_records,load_catalog,CLASSES
from expanded.historical_generation import PAST_SETS,NATURE,ARCANE,MECH,MINION
from expanded.historical_generation_catalog import load_universe,historical_contract,_verified_universe
from expanded.generation import request_matches
from expanded.identities import identity_resolver
from expanded.generation_cards import pool
from engine.cards import UnsupportedCard
import test_expanded_generation as fixtures

class HistoricalGenerationCatalogTests(unittest.TestCase):
 def test_complete_canonical_membership_is_independent_of_playable_registry(self):
  records={d['id']:d for d in load_all_records()}
  canonical=identity_resolver(records)
  standard={canonical(d) for d in load_catalog()}
  expected={canonical(d) for d in records.values() if d.get('collectible') and
   d.get('set') in PAST_SETS and d.get('type') in ('MINION','SPELL','WEAPON','HERO','LOCATION') and
   all(c in CLASSES+('NEUTRAL',) for c in (d.get('classes') or (d.get('cardClass'),))) and
   canonical(d) not in standard}
  universe=load_universe()
  actual={canonical(universe.records[cid]) for cid in universe.members}
  self.assertEqual(actual,expected)
  self.assertEqual(len(universe.members),len(expected))
  self.assertGreater(len(universe.members),2000)
 def test_all_classes_and_source_selectors_use_full_universe(self):
  universe=load_universe()
  for hero in CLASSES:
   for request in (NATURE,ARCANE,MECH,pool(card_type='MINION',tribe='DRAGON',classes='own_or_neutral',era='past')):
    contract=historical_contract(request,hero,universe)
    self.assertEqual(set(contract.card_ids),{cid for cid in universe.members if request_matches(request,universe.records[cid],hero)})
 def test_unimplemented_outcomes_reject_before_rng_or_zone_changes(self):
  game=fixtures.GenerationTests().game()
  contract=historical_contract(MINION,'MAGE',load_universe())
  del game.cards[contract.card_ids[0]]
  before=game.rng.getstate();deck=list(game.players[0].deck)
  with self.assertRaisesRegex(UnsupportedCard,'eligible effects not implemented'):
   game._generation_candidates(MINION,0)
  self.assertEqual(game.rng.getstate(),before)
  self.assertEqual(game.players[0].deck,deck)
  self.assertFalse(game.players[0].hand)
 def test_changed_archive_fails_hash_verification(self):
  from standard.catalog import DATA
  with self.assertRaisesRegex(ValueError,'historical catalog changed'):
   _verified_universe((DATA/'all_cards.json.gz').read_bytes()+b'changed',
     (DATA/'cards.json').read_bytes(),(DATA/'manifest.json').read_bytes())
