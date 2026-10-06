import gzip
import json
import unittest
from expanded.cards import registry,_token_records

class RegistryCacheTests(unittest.TestCase):
    def test_changed_snapshot_bytes_are_not_served_stale(self):
        a=gzip.compress(json.dumps([dict(id='x',health=1)]).encode())
        b=gzip.compress(json.dumps([dict(id='x',health=2)]).encode())
        self.assertEqual(_token_records(a,('x',))['x']['health'],1)
        self.assertEqual(_token_records(b,('x',))['x']['health'],2)
    def test_requested_token_membership_is_part_of_cache_key(self):
        payload=gzip.compress(json.dumps([dict(id='x'),dict(id='y')]).encode())
        self.assertEqual(set(_token_records(payload,('x',))),{'x'})
        self.assertEqual(set(_token_records(payload,('y',))),{'y'})
    def test_registry_results_do_not_share_mutable_records(self):
        a=registry();b=registry()
        for cid in ('HERO_11bpt','TOKEN_COIN','ENGINE_HYENA','CORE_CS2_029'):
            original=b[cid]['name'];a[cid]['name']='mutated'
            self.assertEqual(b[cid]['name'],original)
            self.assertEqual(registry()[cid]['name'],original)
    def test_cache_reuses_identical_snapshot_parse(self):
        payload=gzip.compress(json.dumps([dict(id='cache_probe')]).encode())
        _token_records(payload,('cache_probe',));before=_token_records.cache_info().hits
        _token_records(payload,('cache_probe',))
        self.assertEqual(_token_records.cache_info().hits,before+1)
