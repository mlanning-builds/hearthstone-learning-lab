import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[2]/'tools/audit_catalog_selection.py'
spec=importlib.util.spec_from_file_location('catalog_audit',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class CatalogSelectionTests(unittest.TestCase):
    def setUp(self):
        self.rules=dict(as_of='2026-09-18',included_sets={'CORE':'Core'},included_exceptions={'EARLY':{'available_from':'2026-09-15'}},excluded_future_cards={'FUTURE':'2026-10-06'},banned_ids=['BAN'])
        self.records=[dict(id=i,set=s,collectible=True) for i,s in [('A','CORE'),('BAN','CORE'),('FUTURE','CORE'),('EARLY','NEXT'),('OTHER','MERCENARIES')]]
        self.good=[self.records[0],self.records[3]]
    def test_exact_selection_is_consistent_not_certified(self):
        r=m.audit_selection(self.records,self.good,self.rules)
        self.assertTrue(r['selection_consistent']);self.assertFalse(r['legality_certified'])
    def test_future_banned_and_other_modes_are_extra(self):
        r=m.audit_selection(self.records,self.records,self.rules)
        self.assertEqual(r['extra'],['BAN','FUTURE','OTHER'])
    def test_changed_record_detected(self):
        r=m.audit_selection(self.records,[dict(self.good[0],cost=99),self.good[1]],self.rules)
        self.assertEqual(r['changed_records'],['A'])
    def test_expired_exclusion_requires_review(self):
        self.rules['excluded_future_cards']['FUTURE']='2026-09-01'
        self.assertEqual(m.audit_selection(self.records,self.good,self.rules)['expired_exclusions'],['FUTURE'])
