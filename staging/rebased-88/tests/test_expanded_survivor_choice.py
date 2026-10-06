import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class SurvivorChoiceTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.deck=[];self.p.mana=self.p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self):
        c=self.give('CATA_721');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_shuffle_then_draw_removes_enchantments(self):
        c=self.give('CORE_EX1_506');c.attack_bonus=3;c.cost_delta=-1
        self.play();self.assertEqual(self.p.deck,[]);self.assertEqual(len(self.p.hand),1)
        self.g.step(Action('choose',choices=(0,)));drawn=self.p.hand[0]
        self.assertEqual(drawn.card_id,c.card_id);self.assertEqual(drawn.attack_bonus,0)
        self.assertEqual(getattr(drawn,'cost_delta',0),0);self.assertEqual(self.p.fatigue,0)
        self.assertIsNone(self.g.pending_frame)
    def test_empty_hand_still_draws(self):
        self.p.deck=['CORE_CS2_029'];self.play()
        self.assertIsNone(self.g.pending_choice);self.assertEqual(self.p.hand[0].card_id,'CORE_CS2_029')
    def test_empty_hand_and_deck_fatigues(self):
        self.play();self.assertEqual(self.p.fatigue,1);self.assertEqual(self.p.health,29)
    def test_choose_second_duplicate_leaves_first_buffed(self):
        a=self.give('CORE_EX1_506');b=self.give('CORE_EX1_506');a.attack_bonus=2;b.attack_bonus=4
        self.play();self.g.step(Action('choose',choices=(1,)))
        self.assertEqual([c.uid for c in self.p.hand],[a.uid,b.uid])
        self.assertEqual([c.attack_bonus for c in self.p.hand],[2,0])
    def test_choice_is_private_and_draw_happens_once(self):
        self.give('CORE_CS2_029');self.play()
        self.assertNotIn('options',self.g.observe(1)['pending_choice'])
        self.g.step(Action('choose',choices=(0,)));self.assertEqual(len(self.p.hand),1)
        self.assertEqual(len([e for e in self.g.events if e.get('event')=='shuffle_from_hand']),1)
    def test_invalid_choice_restores_pending_state(self):
        c=self.give('CORE_CS2_029');self.play()
        with self.assertRaises(ValueError):self.g.step(Action('choose',choices=(4,)))
        self.assertEqual(self.g.pending_choice['options'][0]['uid'],c.uid)
