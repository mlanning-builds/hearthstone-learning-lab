import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HeldCostTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PALADIN',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play_knight(self):
        c=self.give('FIR_961')
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return next(m for m in self.p.minions if m.card_id=='FIR_961')
    def test_spell_discount_disables_threshold(self):
        self.give('CORE_CS2_032')
        self.p.cost_effects=[dict(selector='SPELL',amount=3,expires=None)]
        m=self.play_knight();self.assertNotIn('LIFESTEAL',m.keywords)
        self.assertNotIn('DIVINE_SHIELD',m.keywords)
        self.assertEqual(len(self.p.cost_effects),1)
    def test_temporary_increase_enables_threshold(self):
        self.give('CORE_CS2_029')
        self.p.timed_cost_increases=[dict(selector='SPELL',amount=1,start=self.g.turn,end=self.g.turn)]
        m=self.play_knight();self.assertIn('LIFESTEAL',m.keywords);self.assertIn('DIVINE_SHIELD',m.keywords)
    def test_expired_increase_does_not_enable_threshold(self):
        self.give('CORE_CS2_029')
        self.p.timed_cost_increases=[dict(selector='SPELL',amount=1,start=0,end=self.g.turn-1)]
        m=self.play_knight();self.assertNotIn('LIFESTEAL',m.keywords)
    def test_deck_filter_does_not_apply_hand_discount(self):
        c=self.give('CORE_CS2_032');self.p.cost_effects=[dict(selector='SPELL',amount=3,expires=None)]
        filters=(('cost','ge',5),)
        self.assertTrue(self.g._matches_filter(c,filters))
        self.assertFalse(self.g._matches_filter(c,filters,hand_owner=0))
    def test_card_discount_combines_with_current_cost_effects(self):
        c=self.give('CORE_CS2_032');c.cost_delta=-1
        self.p.cost_effects=[dict(selector='SPELL',amount=2,expires=None)]
        self.assertFalse(self.g._matches_filter(c,(('cost','ge',5),),hand_owner=0))
