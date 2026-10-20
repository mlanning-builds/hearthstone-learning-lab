import gzip,hashlib,json,unittest
from expanded.cards import UnsupportedCard,_reviewed_records,registry

class ReviewedCacheTests(unittest.TestCase):
 def payload(self,record):
  return json.dumps([record]).encode(),json.dumps({record['id']:hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()}).encode()
 def test_changed_catalog_bytes_are_revalidated(self):
  catalog,manifest=self.payload(dict(id='x',health=1))
  self.assertEqual(_reviewed_records(catalog,manifest,gzip.compress(b'[]'),('x',),())['x']['health'],1)
  changed,_=self.payload(dict(id='x',health=2))
  with self.assertRaises(UnsupportedCard):_reviewed_records(changed,manifest,gzip.compress(b'[]'),('x',),())
 def test_changed_manifest_is_revalidated(self):
  catalog,manifest=self.payload(dict(id='x',health=1));archive=gzip.compress(b'[]')
  _reviewed_records(catalog,manifest,archive,('x',),())
  with self.assertRaises(UnsupportedCard):_reviewed_records(catalog,b'{"x":"unreviewed"}',archive,('x',),())
 def test_changed_archive_is_revalidated(self):
  record=dict(id='x',health=1);_,manifest=self.payload(record)
  _reviewed_records(b'[]',manifest,gzip.compress(json.dumps([record]).encode()),(),('x',))
  with self.assertRaises(UnsupportedCard):_reviewed_records(b'[]',manifest,gzip.compress(b'[{"id":"x","health":2}]'),(),('x',))
 def test_changed_collectible_membership_is_revalidated(self):
  catalog,manifest=self.payload(dict(id='x',health=1));archive=gzip.compress(b'[]')
  _reviewed_records(catalog,manifest,archive,('x',),())
  with self.assertRaises(UnsupportedCard):_reviewed_records(catalog,manifest,archive,(),())
 def test_changed_token_membership_is_revalidated(self):
  record=dict(id='x');_,manifest=self.payload(record);archive=gzip.compress(json.dumps([record]).encode())
  _reviewed_records(b'[]',manifest,archive,(),('x',))
  with self.assertRaises(UnsupportedCard):_reviewed_records(b'[]',manifest,archive,(),())
 def test_only_identical_inputs_reuse_review(self):
  catalog,manifest=self.payload(dict(id='x'));args=(catalog,manifest,gzip.compress(b'[]'),('x',),())
  _reviewed_records(*args);before=_reviewed_records.cache_info().hits;_reviewed_records(*args)
  self.assertEqual(_reviewed_records.cache_info().hits,before+1)
 def test_cached_registry_results_are_independent(self):
  first=registry();second=registry();cid='CORE_CS2_029';original=second[cid]['name']
  first[cid]['name']='mutated'
  self.assertEqual(registry()[cid]['name'],original)
