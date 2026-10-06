import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[2]/'tools/sync_candidate_inventory.py'
spec=importlib.util.spec_from_file_location('inventory_sync',path)
sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)

class InventorySyncTests(unittest.TestCase):
    def inventories(self):
        index=dict(catalog_size=2,implemented_card_ids=['a'],effect_implementations_written=1,
                   provisional_card_ids=['b'],full_standard_ready=False)
        audit=dict(total=2,written=1,missing=1,scope='unverified',cards=[
            dict(id='a',implementation='written_unverified',rules_text='retained',dependency_hints=['retained']),
            dict(id='b',implementation='missing',rules_text='new')])
        return index,audit

    def test_registry_change_updates_both_ledgers_without_claiming_fidelity(self):
        index,audit=self.inventories();new_index,new_audit=sync.reconcile(index,audit,{'a','b'},{'a','b'})
        self.assertEqual((new_index['effect_implementations_written'],new_audit['written'],new_audit['missing']),(2,2,0))
        self.assertEqual(new_audit['cards'][1]['implementation'],'written_unverified')
        self.assertFalse(new_index['full_standard_ready']);self.assertEqual(new_audit['scope'],'unverified')
        self.assertEqual(new_audit['cards'][0]['dependency_hints'],['retained'])
        self.assertEqual(audit['cards'][1]['implementation'],'missing')

    def test_duplicate_catalog_row_is_rejected(self):
        index,audit=self.inventories();audit['cards'][1]['id']='a'
        with self.assertRaises(ValueError):sync.reconcile(index,audit,{'a','b'},{'a','b'})

    def test_out_of_catalog_registration_is_rejected(self):
        index,audit=self.inventories()
        with self.assertRaises(ValueError):sync.reconcile(index,audit,{'a','b','unknown'},{'a','b'})

    def test_wrong_catalog_total_is_not_silently_rewritten(self):
        index,audit=self.inventories();index['catalog_size']=3
        with self.assertRaises(ValueError):sync.reconcile(index,audit,{'a','b'},{'a','b'})

    def test_nonregistered_provisional_identity_is_rejected(self):
        index,audit=self.inventories()
        with self.assertRaises(ValueError):sync.reconcile(index,audit,{'a'},{'a','b'})

    def test_historical_bodies_are_counted_separately_without_admitting_standard_cards(self):
        index,audit=self.inventories()
        index['provisional_card_ids']=['a']
        updated,ledger=sync.reconcile(index,audit,{'a'},{'a','b'},{'old1','old2'})
        self.assertEqual(updated['generated_historical_card_ids'],['old1','old2'])
        self.assertEqual(updated['generated_historical_effects_written'],2)
        self.assertEqual(updated['implemented_card_ids'],['a']);self.assertEqual(ledger['missing'],1)
        self.assertFalse(updated['full_standard_ready'])

    def test_historical_ids_cannot_relabel_standard_catalog_entries(self):
        index,audit=self.inventories()
        index['provisional_card_ids']=['a']
        with self.assertRaisesRegex(ValueError,'outside Standard'):
            sync.reconcile(index,audit,{'a'},{'a','b'},{'b'})
