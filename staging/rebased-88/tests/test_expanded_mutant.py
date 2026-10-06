import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class MutantTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARLOCK',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self):
        c=self.give('CATA_697');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_only_fel_spells_offered(self):
        a=self.give('CORE_BT_035');self.give('CORE_CS2_029');self.give('CORE_EX1_506');self.play()
        self.assertEqual([o['uid'] for o in self.g.pending_choice['options']],[a.uid])
    def test_copy_keeps_cost_modification_and_has_independent_identity(self):
        a=self.give('CORE_BT_035');a.cost_delta=-1;self.play();self.g.step(Action('choose',choices=(0,)))
        b=self.p.hand[-1];self.assertEqual(b.card_id,a.card_id);self.assertEqual(b.cost_delta,-1)
        self.assertNotEqual(b.uid,a.uid);b.cost_delta=-2;self.assertEqual(a.cost_delta,-1)
    def test_no_eligible_card_skips_choice(self):
        self.give('CORE_CS2_029');self.play();self.assertIsNone(self.g.pending_choice)
        self.assertEqual(len(self.p.hand),1)
    def test_copy_can_fill_tenth_hand_slot(self):
        for _ in range(9):self.give('CORE_BT_035')
        self.play();self.g.step(Action('choose',choices=(8,)))
        self.assertEqual(len(self.p.hand),10);self.g.assert_invariants()
    def test_copy_does_not_reveal_selected_identity_to_opponent(self):
        self.give('CORE_BT_035');self.play();start=len(self.g.events)
        self.g.step(Action('choose',choices=(0,)))
        self.assertFalse(any(e.get('card')=='CORE_BT_035' for e in self.g.observe(1)['events'][start:]))
        self.assertNotIn('hand',self.g.observe(1)['players'][0])
    def test_invalid_school_rejected_even_without_hand(self):
        with self.assertRaises(ValueError):self.g._holding_matches(0,(('school','eq','MERCENARIES'),))
