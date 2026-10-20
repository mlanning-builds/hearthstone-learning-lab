"""Pool audits preserve complete observed membership and explicit blockers."""
import copy
import unittest
from tools.audit_forge_pool import audit


class ForgePoolAuditTests(unittest.TestCase):
    def setUp(self):
        self.manifest = dict(schema=1, card_id='CATA_470', source='observed fixture',
                             approved_for_runtime=False, limitations=['fixture'],
                             stages=dict(dragon=['a','b'], undead=['b','c']))
        self.metadata = {cid:dict(id=cid,name=cid,type='MINION',cost=cost,attack=1,health=1)
                         for cid,cost in [('a',8),('b',2),('c',3)]}

    def test_missing_bodies_never_reduce_observed_pool(self):
        report = audit(self.manifest,self.metadata,{'b'})
        self.assertEqual(report['distinct_components'],3)
        self.assertEqual(report['stage_counts'],dict(dragon=2,undead=2))
        self.assertEqual(report['missing_standalone_ids'],['a','c'])
        self.assertFalse(report['runtime_activated'])
        self.assertFalse(report['full_support_certified'])
        self.assertEqual(next(r for r in report['components'] if r['card_id']=='b')['stages'],['dragon','undead'])

    def test_affordability_uses_base_cost_and_keeps_ordered_pairs(self):
        report = audit(self.manifest,self.metadata,set(self.metadata))
        self.assertEqual(report['affordable_ordered_pairs'],3)
        self.assertFalse(report['first_parts_without_completion'])
        self.metadata['a']['cost']=11
        self.assertEqual(audit(self.manifest,self.metadata,set())['first_parts_without_completion'],['a'])

    def test_missing_metadata_is_not_silently_discarded(self):
        del self.metadata['c']
        with self.assertRaisesRegex(ValueError,'Missing minion metadata: c'):
            audit(self.manifest,self.metadata,set())

    def test_duplicate_stage_members_rejected(self):
        self.manifest['stages']['dragon'].append('a')
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            audit(self.manifest,self.metadata,set())

    def test_invalid_statistics_rejected(self):
        self.metadata['a']['cost']=True
        with self.assertRaisesRegex(ValueError,'Invalid component statistics'):
            audit(self.manifest,self.metadata,set())

    def test_runtime_approval_cannot_be_inferred_from_coverage(self):
        self.manifest['approved_for_runtime']=True
        with self.assertRaisesRegex(ValueError,'runtime prohibition'):
            audit(self.manifest,self.metadata,set(self.metadata))

    def test_complete_recipe_declarations_do_not_certify_runtime(self):
        report=audit(self.manifest,self.metadata,set(self.metadata),set(self.metadata))
        self.assertEqual(report["composite_recipes_declared"],3)
        self.assertFalse(report["full_support_certified"])
        self.assertFalse(report["runtime_activated"])
