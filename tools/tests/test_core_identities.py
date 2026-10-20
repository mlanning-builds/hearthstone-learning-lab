"""Reject ledger corruption without approving generation membership."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('core_review',Path(__file__).resolve().parents[1]/'check_core_identities.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)

class CoreReviewTests(unittest.TestCase):
 def fixture(self):
  a=dict(id='CORE_EX1_001',dbfId=2,set='CORE',collectible=True,name='Brute',type='MINION',cardClass='NEUTRAL',cost=2,attack=2,health=3,text='<b>Taunt</b>')
  b=dict(a,id='EX1_001',dbfId=1,set='EXPERT1')
  records={a['id']:a,b['id']:b}
  pair=dict(core=a['id'],original=b['id'],core_dbf=2,original_dbf=1,core_sha=review.record_hash(a),original_sha=review.record_hash(b))
  return dict(pairs=[pair]),records,{a['id']}
 def test_valid_pair_does_not_approve_pool(self):
  result=review.verify(*self.fixture());self.assertEqual(result['verified_pairs'],1);self.assertFalse(result['pool_membership_approved'])
 def test_missing_entry_is_detected(self):
  manifest,records,catalog=self.fixture();manifest['pairs']=[]
  with self.assertRaisesRegex(ValueError,'incomplete'):review.verify(manifest,records,catalog)
 def test_duplicate_entry_is_rejected(self):
  manifest,records,catalog=self.fixture();manifest['pairs']*=2
  with self.assertRaisesRegex(ValueError,'Duplicate'):review.verify(manifest,records,catalog)
 def test_wrong_database_id_is_rejected(self):
  manifest,records,catalog=self.fixture();manifest['pairs'][0]['original_dbf']=3
  with self.assertRaisesRegex(ValueError,'database mismatch'):review.verify(manifest,records,catalog)
 def test_frozen_hash_change_is_rejected(self):
  manifest,records,catalog=self.fixture();records['EX1_001']['attack']=5
  with self.assertRaisesRegex(ValueError,'hash/database'):review.verify(manifest,records,catalog)
 def test_rehashed_different_effect_does_not_become_alias(self):
  manifest,records,catalog=self.fixture();records['EX1_001']['text']='Deal 3 damage.';manifest['pairs'][0]['original_sha']=review.record_hash(records['EX1_001'])
  with self.assertRaisesRegex(ValueError,'printed effect'):review.verify(manifest,records,catalog)
 def test_rehashed_different_stats_do_not_become_alias(self):
  manifest,records,catalog=self.fixture();records['EX1_001']['attack']=5;manifest['pairs'][0]['original_sha']=review.record_hash(records['EX1_001'])
  with self.assertRaisesRegex(ValueError,'gameplay field'):review.verify(manifest,records,catalog)
 def test_html_markup_difference_is_allowed(self):
  manifest,records,catalog=self.fixture();records['EX1_001']['text']='<b><b>Taunt</b></b>';manifest['pairs'][0]['original_sha']=review.record_hash(records['EX1_001'])
  self.assertEqual(review.verify(manifest,records,catalog)['verified_pairs'],1)

if __name__=='__main__':unittest.main()
