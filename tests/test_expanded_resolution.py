"""User-run continuation checks; synthetic sequences test engine behavior only."""
import copy
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.cards import RULES
from engine.cards import UnsupportedCard


class ResolutionTests(unittest.TestCase):
    def setUp(self):
        self.g = Game([random_deck('HUNTER',31), random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan')); self.g.step(Action('mulligan'))
        self.p, self.q = self.g.players
        self.p.hand=[]; self.q.hand=[]
        self.p.mana=self.p.max_mana=10
        self.p.deck=['CORE_CS2_029','CORE_CS2_023','CORE_EX1_506']

    def play_sequence(self, operations):
        # This is an engine harness, not a change to the real Tracking rules.
        card=Card(self.g._new_id(),'CORE_DS1_184')
        self.p.hand.append(card)
        with patch.dict(RULES, {'CORE_DS1_184':('none',operations)}):
            self.g.step(Action('play',card.uid))

    def choose(self):
        self.g.step(Action('choose',choices=(0,)))

    def test_later_effect_waits_and_after_cast_fires_once(self):
        self.g._summon(0,'CORE_EX1_559')
        self.play_sequence([('armor',3),('discover_deck',),('armor',7)])
        self.assertEqual(self.p.armor,3)
        self.assertEqual(self.p.hand,[])
        self.assertEqual(self.p.cards_played,1)
        mana=self.p.mana
        self.choose()
        self.assertEqual(self.p.armor,10)
        self.assertEqual(len(self.p.hand),2)  # selected card plus Antonidas reward
        self.assertEqual(self.p.mana,mana)
        self.assertEqual(self.p.cards_played,1)
        self.assertIsNone(self.g.pending_frame)
        self.assertIsNone(self.g.pending_play)
        self.assertEqual(self.g.phase,'play')

    def test_two_choices_resume_in_order(self):
        self.play_sequence([('discover_deck',),('armor',2),('discover_deck',),('armor',5)])
        self.choose()
        self.assertEqual(self.p.armor,2)
        self.assertEqual(len(self.p.hand),1)
        self.assertEqual(self.g.phase,'choice')
        self.assertIsNotNone(self.g.pending_play)
        self.choose()
        self.assertEqual(self.p.armor,7)
        self.assertEqual(len(self.p.hand),2)
        self.assertEqual(len(self.p.deck),1)
        self.assertIsNone(self.g.pending_frame)
        self.assertIsNone(self.g.pending_play)

    def test_empty_choice_continues_without_fatigue(self):
        self.p.deck=[]
        self.play_sequence([('discover_deck',),('armor',4)])
        self.assertEqual(self.p.armor,4)
        self.assertEqual(self.p.fatigue,0)
        self.assertEqual(self.g.phase,'play')
        self.assertIsNone(self.g.pending_frame)

    def test_failed_resumption_restores_choice_frame_and_rng(self):
        self.play_sequence([('discover_deck',),('armor',4),('not_a_supported_effect',)])
        before=self.g.observe(0)
        frame=copy.deepcopy(self.g.pending_frame)
        rng=self.g.rng.getstate()
        for _ in range(2):
            with self.assertRaises(UnsupportedCard): self.choose()
            self.assertEqual(self.g.observe(0),before)
            self.assertEqual(self.g.pending_frame,frame)
            self.assertEqual(self.g.rng.getstate(),rng)
            self.assertIsNotNone(self.g.pending_play)

    def test_invalid_choice_leaves_suspended_action_unchanged(self):
        self.play_sequence([('discover_deck',),('armor',4)])
        before=self.g.observe(0);rng=self.g.rng.getstate()
        with self.assertRaises(ValueError):
            self.g.step(Action('choose',choices=(99,)))
        self.assertEqual(self.g.observe(0),before)
        self.assertEqual(self.g.rng.getstate(),rng)
        self.choose()
        self.assertEqual(self.p.armor,4)

    def test_lethal_before_choice_stops_remaining_effects(self):
        self.play_sequence([('damage_own_hero',40),('discover_deck',),('armor',4)])
        self.assertTrue(self.g.terminal)
        self.assertEqual(self.g.phase,'finished')
        self.assertEqual(self.p.armor,0)
        self.assertIsNone(self.g.pending_frame)
        self.assertIsNone(self.g.pending_choice)
        self.assertEqual(self.g.legal_actions(),[])

    def test_lethal_after_choice_clears_continuation_and_after_cast(self):
        self.g._summon(0,'CORE_EX1_559')
        self.play_sequence([('discover_deck',),('damage_own_hero',40),('armor',4)])
        self.choose()
        self.assertTrue(self.g.terminal)
        self.assertEqual(self.g.phase,'finished')
        self.assertEqual(self.p.armor,0)
        self.assertEqual(len(self.p.hand),1)
        self.assertIsNone(self.g.pending_frame)
        self.assertIsNone(self.g.pending_play)
        self.assertIsNone(self.g.pending_choice)

    def test_full_hand_burn_does_not_skip_remaining_effects(self):
        self.play_sequence([('fill_hand','TOKEN_COIN'),('discover_deck',),('armor',4)])
        self.assertEqual(len(self.p.hand),10)
        self.choose()
        self.assertEqual(len(self.p.hand),10)
        self.assertEqual(len(self.p.deck),2)
        self.assertEqual(self.p.armor,4)
        self.assertTrue(any(e['event']=='burn' for e in self.g.events))

    def test_suspended_copy_replays_identically_without_exposing_frame(self):
        self.play_sequence([('discover_deck',),('missiles','enemies',3)])
        other=self.g.observe(1)
        self.assertNotIn('options',other['pending_choice'])
        self.assertNotIn('pending_frame',other)
        self.assertEqual(other['legal_actions'],[])
        cloned=copy.deepcopy(self.g)
        self.choose();cloned.step(Action('choose',choices=(0,)))
        self.assertEqual(self.g.observe(0),cloned.observe(0))
        self.assertEqual(self.g.rng.getstate(),cloned.rng.getstate())
