import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class DemiseTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
    def give(self,cid):self.p.hand.append(Card(self.g._new_id(),cid))
    def play(self):
        self.give('TIME_EVENT_301');uid=self.p.hand[-1].uid
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==uid))
    def test_source_does_not_count_as_held_dragon(self):
        for _ in range(3):self.g._summon(1,'CORE_EX1_506')
        self.play();self.assertEqual(len(self.q.minions),2)
    def test_one_extra_destruction_per_held_dragon(self):
        for _ in range(4):self.g._summon(1,'CORE_EX1_506')
        self.give('END_035');self.give('END_034');self.play();self.assertEqual(len(self.q.minions),1)
    def test_non_dragon_does_not_add_repeat(self):
        for _ in range(3):self.g._summon(1,'CORE_EX1_506')
        self.give('CORE_EX1_506');self.play();self.assertEqual(len(self.q.minions),2)
    def test_other_friendly_minion_can_be_destroyed(self):
        m=self.g._summon(0,'CORE_EX1_506');self.play();self.assertNotIn(m,self.p.minions)
        self.assertEqual(len(self.p.minions),1)
    def test_empty_board_never_destroys_self(self):
        self.give('END_035');self.play();self.assertEqual(len(self.p.minions),1)
    def test_reborn_resolves_between_repeats(self):
        self.g._summon(1,'CORE_RLK_745');self.give('END_035');self.play()
        self.assertEqual(self.q.minions,[]);self.assertIsNone(self.g.pending_frame)
    def test_death_choice_pauses_and_resumes_remaining_repeat(self):
        from unittest.mock import patch
        from expanded.cards import DEATH_EFFECTS
        self.g._summon(0,'CORE_EX1_506');self.give('END_035')
        with patch.dict(DEATH_EFFECTS,{'CORE_EX1_506':[('choose_fixed_summon',('END_035',))]}):
            self.play();self.assertIsNotNone(self.g.pending_choice)
            self.assertIsNotNone(self.g.pending_frame)
            self.g.step(Action('choose',choices=(0,)))
        self.assertEqual([m.card_id for m in self.p.minions],['TIME_EVENT_301'])
        self.assertIsNone(self.g.pending_frame);self.assertIsNone(self.g.pending_choice)
