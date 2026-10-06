"""Choice application must not consume child choices or reenter parent frames."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck

class ChoiceContinuationTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('ROGUE',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30
        return g

    def start(self,g):
        g._start_play_effects([('choose_fixed_summon',('EDR_851t',)),('armor',3)],
                             dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))

    def test_apply_without_resuming_retains_parent_cursor(self):
        g=self.game();self.start(g);frame=g.pending_frame;cursor=frame.next_operation
        g._resolve_choice(0,resume=False)
        self.assertIs(g.pending_frame,frame);self.assertEqual(frame.next_operation,cursor)
        self.assertIsNone(g.pending_choice);self.assertEqual(g.phase,'play')
        self.assertEqual(g.players[0].armor,0);self.assertEqual(len(g.players[0].minions),1)
        g._resume_play_effects()
        self.assertEqual(g.players[0].armor,3);self.assertIsNone(g.pending_frame)

    def test_default_selection_still_resumes_parent(self):
        g=self.game();self.start(g);g.step(g.legal_actions()[0])
        self.assertEqual(g.players[0].armor,3);self.assertIsNone(g.pending_frame)

    def test_selection_creating_child_preserves_child_and_parent(self):
        g=self.game();source=g._summon(0,'EDR_851t');self.start(g)
        g.pending_choice=dict(owner=0,kind='self_effect',source_uid=source.uid,
            options=[dict(operation=('choose_fixed_summon',('EDR_851t',)))])
        g._resolve_choice(0)
        self.assertIsNotNone(g.pending_choice)
        self.assertEqual(g.pending_choice['kind'],'fixed_summon')
        self.assertEqual(g.phase,'choice');self.assertEqual(g.players[0].armor,0)
        g.step(g.legal_actions()[0])
        self.assertEqual(g.players[0].armor,3);self.assertEqual(len(g.players[0].minions),2)

    def test_nonresuming_selection_never_calls_continuations(self):
        g=self.game();self.start(g)
        with patch.object(g,'_settle') as settle, patch.object(g,'_resume_turn') as turn, patch.object(g,'_resume_play_effects') as play:
            g._resolve_choice(0,resume=False)
        settle.assert_not_called();turn.assert_not_called();play.assert_not_called()

    def test_bad_index_leaves_pending_choice_and_frame(self):
        g=self.game();self.start(g);choice=g.pending_choice;frame=g.pending_frame
        with self.assertRaises(IndexError):g._resolve_choice(7,resume=False)
        self.assertIs(g.pending_choice,choice);self.assertIs(g.pending_frame,frame)
        self.assertEqual(g.players[0].armor,0)
