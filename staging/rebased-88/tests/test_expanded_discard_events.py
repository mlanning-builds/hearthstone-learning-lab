import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import TRIGGERS

class DiscardEventTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARLOCK',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        for p in self.g.players:p.hand=[];p.deck=[];p.mana=p.max_mana=10
    def discard(self,owner=0,cid='CORE_CS2_029'):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c)
        self.g._discard_card(owner,c);return c
    def test_event_holds_independent_discarded_card_snapshot(self):
        c=self.discard();c.attack_bonus=99
        kind,data,listeners=self.g._rule_events[-1]
        self.assertEqual(kind,'discard');self.assertEqual(data['card'].attack_bonus,0)
        self.assertNotIn(c,self.g.players[0].hand)
    def test_only_owner_listeners_and_no_retroactive_listeners(self):
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('friendly_discard',[('armor',2)])}):
            self.g._summon(0,'CORE_EX1_506');self.g._summon(1,'CORE_EX1_506')
            self.discard();self.g._summon(0,'CORE_EX1_506');self.g._settle()
        self.assertEqual([p.armor for p in self.g.players],[2,0])
    def test_minion_filter_and_silenced_listener(self):
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('friendly_minion_discard',[('armor',2)])}):
            m=self.g._summon(0,'CORE_EX1_506')
            self.discard();self.g._settle();self.assertEqual(self.g.players[0].armor,0)
            self.discard(cid='CORE_EX1_506');self.g._settle();self.assertEqual(self.g.players[0].armor,2)
            self.g._silence(m);self.discard(cid='CORE_EX1_506');self.g._settle()
        self.assertEqual(self.g.players[0].armor,2)
    def test_choice_pauses_then_resumes_same_listener_once(self):
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('friendly_discard',[
                ('choose_fixed_summon',('NEW1_034','NEW1_033')),('armor',3)])}):
            self.g._summon(0,'CORE_EX1_506');self.discard()
            self.g._settle(allow_event_choices=True)
            self.assertEqual(self.g.phase,'choice');self.assertEqual(self.g.players[0].armor,0)
            self.g.step(Action('choose',choices=(0,)))
            self.assertEqual(self.g.players[0].armor,3)
            self.g._settle();self.assertEqual(self.g.players[0].armor,3)

    def test_batch_removes_all_before_draw_triggers(self):
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('friendly_discard',[('draw',1)])}):
            self.g._summon(0,'CORE_EX1_506');p=self.g.players[0]
            p.hand=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(2)]
            p.deck=['CORE_EX1_506']*3
            self.g._discard_random(0,3)
            self.assertFalse(p.hand);self.assertEqual(len(p.discard_history),2)
            self.g._settle()
        self.assertEqual([c.card_id for c in p.hand],['CORE_EX1_506']*2)
        self.assertEqual(len(p.discard_history),2)
    def test_batch_new_listener_does_not_receive_second_event(self):
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('friendly_discard',[('summon','CORE_EX1_506',1),('armor',1)])}):
            self.g._summon(0,'CORE_EX1_506');p=self.g.players[0]
            p.hand=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(2)]
            self.g._discard_random(0,2);self.g._settle()
        self.assertEqual(p.armor,2);self.assertEqual(len(p.minions),3)
    def test_batch_invalid_selection_does_not_remove_any_card(self):
        p=self.g.players[0];c=Card(self.g._new_id(),'CORE_CS2_029');p.hand=[c]
        for cards in ([c,c],[c,Card(self.g._new_id(),'CORE_CS2_029')]):
            with self.assertRaises(ValueError):self.g._discard_cards(0,cards)
            self.assertEqual(p.hand,[c]);self.assertEqual(p.discard_history,[])
    def test_batch_choice_sees_both_discards_already_completed(self):
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('friendly_discard',[('choose_fixed_summon',('NEW1_034',))])}):
            self.g._summon(0,'CORE_EX1_506');p=self.g.players[0]
            p.hand=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(2)]
            self.g._discard_random(0,2);self.g._settle(allow_event_choices=True)
            self.assertEqual(len(p.discard_history),2);self.assertFalse(p.hand)
            self.g.step(Action('choose',choices=(0,)))
            self.assertEqual(self.g.phase,'choice')
            self.g.step(Action('choose',choices=(0,)))
            self.assertEqual(self.g.phase,'play');self.assertEqual(len(p.minions),3)
