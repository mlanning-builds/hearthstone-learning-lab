"""Pool evidence must not silently become runtime membership."""
import unittest
from tools.audit_observed_zombeasts import compare


class ObservedZombeastTests(unittest.TestCase):
    def test_missing_future_card_is_retained_as_unmapped_evidence(self):
        report=compare(dict(approved_for_runtime=False,visible_candidates=['Future Beast']),[],set())
        self.assertEqual(report['unmapped_titles'],['Future Beast'])
        self.assertFalse(report['runtime_activated'])
        self.assertFalse(report['stage_membership_established'])

    def test_same_name_core_versions_do_not_collapse(self):
        metadata=[dict(id=cid,name='Raptor',type='MINION',collectible=True)
                  for cid in ('CORE_OLD','CORE_CURRENT')]
        report=compare(dict(approved_for_runtime=False,visible_candidates=['Raptor (Core)']),metadata,{'CORE_CURRENT'})
        self.assertEqual(report['ambiguous_titles'],['Raptor (Core)'])
        self.assertEqual(report['rows'][0]['pinned_standard_matches'],['CORE_CURRENT'])

    def test_core_and_original_identity_stay_distinct(self):
        metadata=[dict(id=cid,name='Beast',type='MINION',collectible=True)
                  for cid in ('ORIGINAL','CORE_ORIGINAL')]
        report=compare(dict(approved_for_runtime=False,visible_candidates=['Beast (Core)','Beast']),metadata,set())
        self.assertEqual([row['pinned_matches'] for row in report['rows']],[['CORE_ORIGINAL'],['ORIGINAL']])

    def test_runtime_approval_is_rejected(self):
        with self.assertRaises(ValueError):compare(dict(approved_for_runtime=True,visible_candidates=[]),[],set())
