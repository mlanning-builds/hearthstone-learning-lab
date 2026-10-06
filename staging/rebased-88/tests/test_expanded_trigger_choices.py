"""User-run continuation scenarios with synthetic card rules."""
import copy
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.cards import RULES, TRIGGERS
from engine.cards import UnsupportedCard


class TriggerChoiceTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.p.hand=[];self.p.mana=10
        self.p.deck=['CORE_CS2_029','CORE_CS2_023','CORE_EX1_506']
        self.g._summon(0,'Core_CS2_200');self.g._summon(0,'CORE_EX1_007')
        patcher=patch.dict(RULES,{'CORE_DS1_184':('none',[('armor',2)])})
        patcher.start();self.addCleanup(patcher.stop)

    def start(self, operations=None):
        if operations is None: operations=[('armor',3),('discover_deck',),('armor',7)]
        patcher=patch.dict(TRIGGERS,{
            'Core_CS2_200':('spell_cast',operations),
            'CORE_EX1_007':('spell_cast',[('armor',11)])},clear=True)
        patcher.start();self.addCleanup(patcher.stop)
        c=Card(self.g._new_id(),'CORE_DS1_184');self.p.hand.append(c)
        self.g.step(Action('play',c.uid))

    def choose(self, game=None):
        (game or self.g).step(Action('choose',choices=(0,)))

    def test_choice_pauses_remaining_operations_and_listeners(self):
        self.start()
        self.assertEqual(self.p.armor,5)
        self.assertEqual(self.g.phase,'choice')
        self.assertTrue(self.g._event_frames)
        self.choose()
        self.assertEqual(self.p.armor,23)
        self.assertEqual(len(self.p.hand),1)
        self.assertEqual(self.p.cards_played,1)
        self.assertFalse(self.g._event_frames)
        self.assertEqual(self.g.phase,'play')

    def test_two_choices_resume_same_trigger_once(self):
        self.start([('discover_deck',),('armor',3),('discover_deck',),('armor',7)])
        self.choose();self.assertEqual(self.p.armor,5)
        self.assertEqual(self.g.phase,'choice')
        self.choose();self.assertEqual(self.p.armor,23)
        self.assertEqual(len(self.p.hand),2)

    def test_empty_pool_does_not_suspend(self):
        self.p.deck=[];self.start()
        self.assertEqual(self.p.armor,23)
        self.assertIsNone(self.g.pending_choice)
        self.assertFalse(self.g._event_frames)
        self.assertEqual(self.p.fatigue,0)

    def test_invalid_choice_preserves_suspended_state(self):
        self.start();before=self.g.observe(0);rng=self.g.rng.getstate()
        with self.assertRaises(ValueError): self.g.step(Action('choose',choices=(99,)))
        self.assertEqual(self.g.observe(0),before)
        self.assertEqual(self.g.rng.getstate(),rng)
        self.choose();self.assertEqual(self.p.armor,23)

    def test_failure_after_choice_rolls_back_frames_and_rng(self):
        self.start([('discover_deck',),('armor',3),('not_supported',)])
        before=copy.deepcopy(self.g.__dict__)
        for _ in range(2):
            with self.assertRaises(UnsupportedCard): self.choose()
            self.assertEqual(self.g._event_frames,before['_event_frames'])
            self.assertEqual(self.g.pending_choice,before['pending_choice'])
            self.assertEqual(self.g.players,before['players'])
            self.assertEqual(self.g.rng.getstate(),before['rng'].getstate())

    def test_suspended_game_copy_resumes_identically(self):
        self.start();cloned=copy.deepcopy(self.g)
        self.choose();self.choose(cloned)
        self.assertEqual(self.g.observe(0),cloned.observe(0))
        self.assertEqual(self.g.rng.getstate(),cloned.rng.getstate())

    def test_opponent_cannot_see_options_or_event_frames(self):
        self.start();other=self.g.observe(1)
        self.assertNotIn('options',other['pending_choice'])
        self.assertNotIn('_event_frames',other)
        self.assertEqual(other['legal_actions'],[])

    def test_lethal_after_choice_cancels_later_listener(self):
        self.start([('discover_deck',),('damage_own_hero',100),('armor',7)])
        self.choose()
        self.assertTrue(self.g.terminal)
        self.assertEqual(self.p.armor,0)
        self.assertFalse(self.g._event_frames)
        self.assertIsNone(self.g.pending_choice)
        self.assertEqual(self.g.legal_actions(),[])

    def test_full_hand_burn_still_resumes_trigger(self):
        self.start([('fill_hand','TOKEN_COIN'),('discover_deck',),('armor',7)])
        self.choose()
        self.assertEqual(len(self.p.hand),10)
        self.assertEqual(self.p.armor,20)
        self.assertTrue(any(e['event']=='burn' for e in self.g.events))

    def test_mid_card_trigger_choice_resumes_before_remaining_card_effect(self):
        rules={'CORE_DS1_184':('none',[('area_damage','all_minions',1),('armor',17)])}
        triggers={'Core_CS2_200':('damaged_self',[('discover_deck',),('armor',3)]),
                  'CORE_EX1_007':('spell_cast',[('armor',11)])}
        with patch.dict(RULES,rules),patch.dict(TRIGGERS,triggers,clear=True):
            c=Card(self.g._new_id(),'CORE_DS1_184');self.p.hand.append(c)
            self.g.step(Action('play',c.uid))
            self.assertEqual(self.p.armor,0)
            self.assertIsNotNone(self.g.pending_frame)
            self.choose()
        self.assertEqual(self.p.armor,31)
        self.assertEqual(self.p.cards_played,1)
        self.assertIsNone(self.g.pending_frame)
        self.assertIsNone(self.g.pending_play)
        self.assertFalse(self.g._event_frames)
