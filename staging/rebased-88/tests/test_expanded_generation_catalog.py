"""Complete frozen membership remains independent of executable coverage."""
import copy,json,unittest
from expanded.generation_catalog import load_universe,standard_contract,_verified_universe
from expanded.generation_cards import pool
from standard.catalog import DATA
from engine.cards import UnsupportedCard
import test_expanded_generation as fixtures

class StandardGenerationCatalogTests(unittest.TestCase):
    def test_full_membership_retains_deliberately_removed_outcome(self):
        universe=load_universe();self.assertEqual(len(universe.records),1185)
        contract=standard_contract(pool(),'MAGE',universe)
        g=fixtures.GenerationTests().game()
        del g.cards[contract.card_ids[0]]
        missing=set(contract.card_ids)-g.cards.keys()
        self.assertTrue(missing)
        self.assertTrue(missing <= universe.records.keys())
        before=g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'eligible effects not implemented'):
            g._generation_candidates(pool(),0)
        self.assertEqual(g.rng.getstate(),before)
    def test_universe_is_immutable_and_shared_by_game_copies(self):
        universe=load_universe();self.assertIs(copy.deepcopy(universe),universe)
        with self.assertRaises(TypeError):universe.records['new']={}
        first=next(iter(universe.records.values()))
        with self.assertRaises(TypeError):first['cost']=99
    def test_corrupt_snapshot_fails_before_membership(self):
        with self.assertRaisesRegex(ValueError,'changed'):
            _verified_universe(b'[]',(DATA/'manifest.json').read_bytes())
    def test_manifest_count_and_duplicate_identity_fail(self):
        import hashlib
        record=dict(next(iter(load_universe().records.values())))
        snapshot=json.dumps([{'id':record['id'],'cardClass':'MAGE'}]*2).encode()
        manifest=json.dumps({'files_sha256':{'cards.json':hashlib.sha256(snapshot).hexdigest()},'standard_catalog_count':2}).encode()
        with self.assertRaisesRegex(ValueError,'identities'):_verified_universe(snapshot,manifest)
    def test_historical_and_named_families_require_separate_contracts(self):
        self.assertIsNone(standard_contract(pool(era='past'),'MAGE',load_universe()))
    def test_known_empty_cost_pool_does_not_consume_rng(self):
        g=fixtures.GenerationTests().game();before=g.rng.getstate()
        self.assertEqual(g._generation_candidates(pool(minimum=999,maximum=999),0),())
        self.assertEqual(g.rng.getstate(),before)
