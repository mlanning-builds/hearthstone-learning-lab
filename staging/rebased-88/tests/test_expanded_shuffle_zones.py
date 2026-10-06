import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ShuffleZonesTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.deck=[]
    def card(self):
        c=Card(self.g._new_id(),'CORE_EX1_506');c.attack_bonus=3;c.health_bonus=4;c.cost_delta=-2
        self.p.hand.append(c);return c
    def shuffle(self):
        self.g._batch_effect(('shuffle_left_hand',),{'owner':0})
    def test_backward_move_removes_buffs_and_discount(self):
        c=self.card();self.shuffle();d=self.p.deck[0]
        self.assertEqual((d.attack_bonus,d.health_bonus,getattr(d,'cost_delta',0)),(0,0,0))
        self.assertEqual((d.uid,d.card_id),(c.uid,c.card_id));self.assertEqual(self.p.hand,[])
    def test_redraw_does_not_restore_removed_enchantments(self):
        self.card();self.shuffle();c=self.g._draw(0)
        self.assertEqual((c.attack_bonus,c.health_bonus,getattr(c,'cost_delta',0)),(0,0,0))
    def test_only_leftmost_card_moves(self):
        a=self.card();b=self.card();self.shuffle()
        self.assertEqual([c.uid for c in self.p.hand],[b.uid])
        self.assertEqual(self.p.hand[0].attack_bonus,3);self.assertEqual(self.p.deck[0].uid,a.uid)
    def test_empty_hand_does_not_create_card_or_fatigue(self):
        self.shuffle();self.assertEqual(self.p.deck,[]);self.assertEqual(self.p.fatigue,0)
    def test_forward_draw_preserves_deck_enchantments(self):
        c=self.card();self.p.hand=[];self.p.deck=[c];drawn=self.g._draw(0)
        self.assertEqual((drawn.attack_bonus,drawn.health_bonus,drawn.cost_delta),(3,4,-2))
    def test_shuffle_does_not_publicly_reveal_identity(self):
        self.card();start=len(self.g.events);self.shuffle()
        self.assertFalse(any(e.get('card')=='CORE_EX1_506' for e in self.g.observe(1)['events'][start:]))
