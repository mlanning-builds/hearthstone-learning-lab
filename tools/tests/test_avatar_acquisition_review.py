import unittest
from tools.review_avatar_pack import resolve,record_hash


class AvatarAcquisitionReviewTests(unittest.TestCase):
    def setUp(self):
        self.metadata={cid:dict(id=cid,name=cid) for cid in ('free','golden_only','ordinary')}
        self.candidates=dict(special_acquisition_requires_review=[dict(id='free'),dict(id='golden_only')],set_filtered_candidate_ids=list(self.metadata))
        self.rows=[dict(id=cid,source='reviewed fixture',record_sha256=record_hash(self.metadata[cid]),pack_qualities=qualities)
                   for cid,qualities in (('free',[]),('golden_only',['GOLDEN']))]

    def test_golden_only_identity_is_retained_without_runtime_admission(self):
        report=resolve(self.candidates,dict(cards=self.rows),self.metadata)
        self.assertEqual(report['identity_candidate_ids'],['golden_only','ordinary'])
        self.assertEqual(report['special_quality_restrictions'],{'golden_only':['GOLDEN']})
        self.assertFalse(report['runtime_activated']);self.assertFalse(report['distribution_established'])

    def test_incomplete_or_duplicate_evidence_rejects(self):
        for rows in (self.rows[:1],self.rows+self.rows[:1]):
            with self.subTest(rows=rows),self.assertRaises(ValueError):resolve(self.candidates,dict(cards=rows),self.metadata)

    def test_changed_pinned_record_invalidates_evidence(self):
        self.metadata['free']['name']='changed'
        with self.assertRaisesRegex(ValueError,'Unbound'):resolve(self.candidates,dict(cards=self.rows),self.metadata)

    def test_quality_must_be_explicit_and_valid(self):
        self.rows[0]['pack_qualities']=['guessed']
        with self.assertRaisesRegex(ValueError,'qualities'):resolve(self.candidates,dict(cards=self.rows),self.metadata)
