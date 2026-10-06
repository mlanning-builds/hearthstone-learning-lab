import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HandTransformTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self,c):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def agent(self):self.play(self.give('CATA_200'))
    def test_replacement_retains_position_and_clears_buffs(self):
        a=self.give('CORE_EX1_506');b=self.give('CORE_EX1_506');c=self.give('CORE_CS2_029')
        b.attack_bonus=5;b.health_bonus=4;b.cost_delta=-1
        self.agent();self.g.step(Action('choose',choices=(1,)))
        self.assertEqual([x.card_id for x in self.p.hand],['CORE_EX1_506','TOKEN_COIN','CORE_CS2_029'])
        coin=self.p.hand[1];self.assertNotEqual(coin.uid,b.uid)
        self.assertEqual((coin.attack_bonus,coin.health_bonus,getattr(coin,'cost_delta',0)),(0,0,0))
        self.assertEqual((self.p.hand[0].uid,self.p.hand[2].uid),(a.uid,c.uid))
    def test_duplicate_cards_are_distinguishable_to_policy(self):
        a=self.give('CORE_EX1_506');b=self.give('CORE_EX1_506');self.agent()
        self.assertEqual([o['uid'] for o in self.g.observe(0)['pending_choice']['options']],[a.uid,b.uid])
        self.assertNotIn('options',self.g.observe(1)['pending_choice'])
    def test_no_other_hand_cards_has_no_choice(self):
        self.agent();self.assertIsNone(self.g.pending_choice);self.assertEqual(self.p.hand,[])
    def test_coin_is_playable_and_gains_mana(self):
        self.give('CORE_EX1_506');self.agent();self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(self.p.mana,9);self.play(self.p.hand[0]);self.assertEqual(self.p.mana,10)
    def test_no_discard_or_burn_event(self):
        self.give('CORE_EX1_506');self.agent();start=len(self.g.events)
        self.g.step(Action('choose',choices=(0,)))
        self.assertFalse(any(e['event'] in ('discard','burn','burn_generated') for e in self.g.events[start:]))
    def test_invalid_choice_preserves_hand(self):
        self.give('CORE_EX1_506');self.agent();before=self.g.observe(0)
        with self.assertRaises(ValueError):self.g.step(Action('choose',choices=(2,)))
        self.assertEqual(self.g.observe(0),before)
