"""Colossal entry checks; fixture token bodies do not certify card abilities."""
import unittest
import json,gzip
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded.colossals import LAYOUTS
from expanded.cards import COLLECTIBLE_IDS
from engine.cards import UnsupportedCard
from standard.catalog import load_catalog

class ColossalEntryTests(unittest.TestCase):
    def setUp(self):
        self.g = fixtures.GenerationTests().game()
        # Entry-only fixtures deliberately isolate army abilities/pool contracts.
        for hook in ('_herald_on_summon','_herald_entry_preflight'):
            context=patch.object(self.g,hook);context.start();self.addCleanup(context.stop)
        records = {c['id']: c for c in load_catalog()}
        with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as handle:
            records.update({row['id']:row for row in json.load(handle)})
        ids = set(LAYOUTS) | {cid for layout in LAYOUTS.values() for cid, _ in layout} | {'CATA_550'}
        self.g.cards.update({cid: deepcopy(records[cid]) for cid in ids})
    @property
    def board(self): return self.g.players[0].board
    def summon(self,cid='CATA_150',**kw): return self.g._summon(0,cid,**kw)
    def fill(self,n):
        for _ in range(n): self.summon('NEW1_034')
    def test_all_ten_layouts_have_expected_sizes(self):
        for cid,count in {'CATA_139':4,'CATA_150':2,'CATA_151':2,'CATA_153':2,'CATA_154':2,'CATA_155':2,'CATA_300':3,'CATA_432':4,'CATA_488':2,'CATA_726':2}.items():
            with self.subTest(cid=cid):
                self.board.clear();body=self.summon(cid)
                self.assertEqual(len(self.board),count+1)
                self.assertEqual(len(body.rule_state['colossal_appendages']),count)
    def test_layouts_do_not_admit_incomplete_cards(self):
        self.assertFalse(set(LAYOUTS)&COLLECTIBLE_IDS)
    def test_right_appendages_preserve_order_and_existing_neighbors(self):
        self.fill(2);old=list(self.board)
        body=self.summon('CATA_139',position=1)
        self.assertEqual([m.card_id for m in self.board],[old[0].card_id,body.card_id]+[c for c,_ in LAYOUTS[body.card_id]]+[old[1].card_id])
    def test_left_right_layout(self):
        self.summon()
        self.assertEqual([m.card_id for m in self.board],['CATA_150t','CATA_150','CATA_150t1'])
    def test_only_one_limb_fits(self):
        self.fill(5);body=self.summon()
        self.assertEqual(len(self.board),7)
        self.assertEqual(self.board[-2].card_id,'CATA_150t')
        self.assertEqual(body.rule_state['colossal_appendages'],[self.board[-2].uid])
    def test_body_fills_last_slot(self):
        self.fill(6);body=self.summon()
        self.assertEqual(len(self.board),7)
        self.assertEqual(body.rule_state['colossal_appendages'],[])
    def test_failed_body_has_no_limb(self):
        self.fill(7);before=list(self.board)
        self.assertIsNone(self.summon());self.assertEqual(self.board,before)
    def test_missing_dependency_fails_before_body_creation(self):
        del self.g.cards['CATA_150t1'];before=self.g._new_id()
        with self.assertRaisesRegex(UnsupportedCard,'Missing Colossal'):self.summon()
        self.assertFalse(self.board);self.assertEqual(self.g._new_id(),before+1)
    def test_missing_dependency_not_hidden_by_full_board(self):
        self.fill(7);del self.g.cards['CATA_150t1']
        with self.assertRaises(UnsupportedCard):self.summon()
        self.assertEqual(len(self.board),7)
    def test_non_minion_dependency_rejected(self):
        self.g.cards['CATA_150t']['type']='SPELL'
        with self.assertRaises(UnsupportedCard):self.summon()
        self.assertFalse(self.board)
    def test_unknown_colossal_not_silently_a_plain_minion(self):
        self.g.cards['NEW1_034']['mechanics']=['COLOSSAL']
        with self.assertRaisesRegex(UnsupportedCard,'explicit layout'):self.summon('NEW1_034')
    def test_magmaw_not_truncated_to_six_appendages(self):
        body=self.summon('CATA_550')
        self.assertEqual(len(self.board),7)
        self.assertEqual(body.rule_state['colossal_remaining'],93)
    def test_copy_creates_new_parent_links_without_copying_limb_buffs(self):
        body=self.summon();old_links=list(body.rule_state['colossal_appendages'])
        limb=self.board[0];self.g._buff(limb,9,9)
        copied=self.summon(copy_from=body)
        links=copied.rule_state['colossal_appendages']
        self.assertEqual(len(links),2);self.assertFalse(set(links)&set(old_links))
        self.assertEqual(body.rule_state['colossal_appendages'],old_links)
        for m in self.board:
            if m.uid in links:
                self.assertEqual(m.rule_state['colossal_parent'],copied.uid)
                self.assertEqual(m.attack,self.g.cards[m.card_id]['attack'])
    def test_opponent_entry_uses_opponent_space(self):
        self.fill(7);body=self.g._summon(1,'CATA_150')
        self.assertEqual(len(self.board),7);self.assertEqual(len(self.g.players[1].board),3)
        self.assertEqual(body.owner,1)
    def test_silenced_copy_rejected_before_mutation(self):
        body=self.summon();body.silenced=True;before=list(self.board)
        with self.assertRaisesRegex(UnsupportedCard,'silenced'):self.summon(copy_from=body)
        self.assertEqual(self.board,before)
    def test_dormant_entry_rejected_before_mutation(self):
        with self.assertRaisesRegex(UnsupportedCard,'dormant'):self.summon(dormant_turns=2)
        self.assertFalse(self.board)
    def test_transform_emits_limb_notifications_but_not_body_summon(self):
        old=self.summon('NEW1_034')
        with patch.object(self.g,'_capture_summon_event',wraps=self.g._capture_summon_event) as capture:
            body=self.g._transform(old,'CATA_150')
        self.assertEqual([call.args[0].card_id for call in capture.call_args_list],['CATA_150t','CATA_150t1'])
        self.assertNotIn(old,self.board);self.assertIn(body,self.board)
    def test_failed_transform_keeps_original_body(self):
        old=self.summon('NEW1_034');del self.g.cards['CATA_150t1']
        with self.assertRaises(UnsupportedCard):self.g._transform(old,'CATA_150')
        self.assertEqual(self.board,[old])
    def test_parent_notification_follows_appendages(self):
        with patch.object(self.g,'_capture_summon_event',wraps=self.g._capture_summon_event) as capture:
            self.summon(entry_origin='play')
        self.assertEqual([call.args[0].card_id for call in capture.call_args_list],['CATA_150t','CATA_150t1','CATA_150'])
    def test_recursive_dependency_rejected(self):
        with patch.dict(LAYOUTS,{'CATA_150':(('CATA_150','right'),)}):
            with self.assertRaisesRegex(UnsupportedCard,'Recursive'):self.summon()
        self.assertFalse(self.board)
    def test_invalid_side_rejected(self):
        with patch.dict(LAYOUTS,{'CATA_150':(('CATA_150t','above'),)}):
            with self.assertRaisesRegex(UnsupportedCard,'position'):self.summon()
        self.assertFalse(self.board)
