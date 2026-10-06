"""Hero Power continuation contracts, including synthetic choice-bearing powers."""
import copy
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.cards import TRIGGERS
from engine.cards import UnsupportedCard


class PowerSequenceTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10

    def power(self,ops):
        def replacement(game,owner,target=0):
            game._start_power_effects(owner,ops,target=target)
            return True
        with patch.object(Game,'_replacement_power_effect',replacement):
            self.g.step(Action('power'))

    def choose(self,g=None):
        (g or self.g).step(Action('choose',choices=(0,)))

    def test_two_choices_pay_once_and_complete_before_after_use(self):
        self.g._summon(0,'EDR_470');m=self.p.minions[0];hp=m.max_health
        self.power((('discover_deck',),('armor',3),('discover_deck',),('armor',7)))
        self.assertEqual((self.p.mana,self.p.armor,self.p.hero_power_uses),(8,0,0))
        self.assertEqual(m.max_health,hp)
        self.choose();self.assertEqual(self.p.armor,3);self.assertEqual(m.max_health,hp)
        self.choose();self.assertEqual((self.p.mana,self.p.armor,self.p.hero_power_uses),(8,10,1))
        self.assertEqual(m.max_health,hp+2);self.assertIsNone(self.g._power_frame)
        self.assertIsNone(self.g.pending_frame);self.assertTrue(self.p.power_used)

    def test_after_use_choice_does_not_repeat_counter_or_listener(self):
        self.g._summon(0,'EDR_470')
        with patch.dict(TRIGGERS,{'EDR_470':('hero_power_used',[('discover_deck',),('armor',7)])}):
            self.g.step(Action('power'))
            self.assertEqual((self.p.armor,self.p.hero_power_uses),(2,1))
            self.assertEqual(self.g._power_frame['phase'],'after_use')
            self.choose();self.assertEqual((self.p.armor,self.p.hero_power_uses),(9,1))
            self.assertIsNone(self.g._power_frame)

    def test_failed_resume_restores_payment_frame_and_rng(self):
        self.power((('discover_deck',),('unknown_power_operation',)))
        before=copy.deepcopy(self.g.__dict__)
        for _ in range(2):
            with self.assertRaises(UnsupportedCard):self.choose()
            self.assertEqual(self.g.players,before['players'])
            self.assertEqual(self.g._power_frame,before['_power_frame'])
            self.assertEqual(self.g.pending_frame,before['pending_frame'])
            self.assertEqual(self.g.rng.getstate(),before['rng'].getstate())

    def test_invalid_choice_preserves_suspension(self):
        self.power((('discover_deck',),('armor',4)))
        before=copy.deepcopy(self.g._power_frame)
        with self.assertRaises(ValueError):self.g.step(Action('choose',choices=(100,)))
        self.assertEqual(self.g._power_frame,before)
        self.choose();self.assertEqual(self.p.armor,4)

    def test_clone_resumes_identically(self):
        self.power((('discover_deck',),('armor',4)))
        other=copy.deepcopy(self.g)
        self.choose();self.choose(other)
        self.assertEqual(self.g.observe(0),other.observe(0))
        self.assertEqual(self.g.rng.getstate(),other.rng.getstate())

    def test_empty_choice_pool_finishes_without_suspension(self):
        self.p.deck=[]
        self.power((('discover_deck',),('armor',4)))
        self.assertIsNone(self.g._power_frame);self.assertEqual(self.p.hero_power_uses,1)
        self.assertEqual(self.p.armor,4)

    def test_lethal_check_waits_for_choice_in_after_use_listener(self):
        self.p.hero_class='HUNTER';self.q.health=2
        self.g._summon(0,'EDR_470')
        with patch.dict(TRIGGERS,{'EDR_470':('hero_power_used',[('discover_deck',),('armor',7)])}):
            self.g.step(Action('power'))
            self.assertFalse(self.g.terminal);self.assertEqual(self.q.health,0)
            self.choose();self.assertTrue(self.g.terminal);self.assertEqual(self.p.armor,7)
            self.assertIsNone(self.g._power_frame)

    def test_power_frame_is_private(self):
        self.power((('discover_deck',),('armor',4)))
        for owner in (0,1):self.assertNotIn('_power_frame',self.g.observe(owner))
