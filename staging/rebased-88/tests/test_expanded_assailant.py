import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class AssailantTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.q.hand=[];self.q.deck=[]
        self.p.mana=self.p.max_mana=10
    def give(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c
    def play(self):
        c=self.give('EDR_524');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_only_matching_enemy_card_moves_and_loses_buffs(self):
        own=self.give('CORE_EX1_506');enemy=self.give('CORE_EX1_506',1);enemy.attack_bonus=3;enemy.cost_delta=-1
        other=self.give('CORE_CS2_029',1);self.play()
        self.assertEqual(self.q.hand,[other]);self.assertEqual(self.p.hand,[own])
        self.assertEqual(self.q.deck[0].uid,enemy.uid);self.assertEqual(self.q.deck[0].attack_bonus,0)
        self.assertEqual(getattr(self.q.deck[0],'cost_delta',0),0)
    def test_only_one_duplicate_is_shuffled(self):
        self.give('CORE_EX1_506')
        for _ in range(3):self.give('CORE_EX1_506',1)
        self.play();self.assertEqual(len(self.q.hand),2);self.assertEqual(len(self.q.deck),1)
    def test_no_match_does_nothing(self):
        self.give('CORE_EX1_506');c=self.give('CORE_CS2_029',1);self.play()
        self.assertEqual(self.q.hand,[c]);self.assertEqual(self.q.deck,[])
    def test_played_assailant_is_not_still_held(self):
        c=self.give('EDR_524',1);self.play();self.assertEqual(self.q.hand,[c])
    def test_each_matching_entity_can_be_selected(self):
        self.give('CORE_EX1_506');self.give('CORE_CS2_029');seen=set()
        for seed in range(20):
            self.q.hand=[];self.q.deck=[];self.give('CORE_EX1_506',1);self.give('CORE_CS2_029',1)
            self.g.rng.seed(seed);self.g._batch_effect(('shuffle_matching_enemy_hand',),{'owner':0})
            seen.add(self.q.deck[0].card_id)
        self.assertEqual(seen,{'CORE_EX1_506','CORE_CS2_029'})
    def test_empty_enemy_hand_skips(self):
        self.give('CORE_EX1_506');self.play();self.assertEqual(self.q.deck,[]);self.g.assert_invariants()
