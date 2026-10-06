import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card

class SatyrTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.q.hand=[]
        self.p.mana=self.p.max_mana=10
    def give(self,cid,player=1):
        c=Card(self.g._new_id(),cid);self.g.players[player].hand.append(c);return c
    def play(self):
        c=self.give('EDR_521',0)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_lowest_current_cost_preserves_modifications(self):
        self.give('CORE_EX1_506')
        c=self.give('CORE_CS2_029');c.cost_delta=-4
        self.play();copy=self.p.hand[0]
        self.assertEqual(copy.card_id,c.card_id);self.assertEqual(copy.cost_delta,-4)
        self.assertNotEqual(copy.uid,c.uid);copy.cost_delta=2;self.assertEqual(c.cost_delta,-4)
        self.assertEqual(len(self.q.hand),2)
    def test_minion_hand_buffs_copied(self):
        c=self.give('CORE_EX1_506');c.attack_bonus=3;c.health_bonus=4
        self.play();copy=self.p.hand[0]
        self.assertEqual((copy.attack_bonus,copy.health_bonus),(3,4))
    def test_empty_opponent_hand(self):
        self.play();self.assertEqual(self.p.hand,[]);self.assertIsNone(self.g.pending_choice)
    def test_ties_can_select_each_entity(self):
        a=self.give('CORE_EX1_506');b=self.give('CORE_EX1_506')
        a.attack_bonus=1;b.attack_bonus=2
        seen=set()
        for seed in range(20):
            self.p.hand=[];self.g.rng.seed(seed)
            self.g._batch_effect(('copy_lowest_enemy_hand',),{'owner':0})
            seen.add(self.p.hand[0].attack_bonus)
        self.assertEqual(seen,{1,2})
    def test_copy_fills_last_hand_slot(self):
        self.give('CORE_EX1_506')
        for _ in range(9):self.give('CORE_CS2_029',0)
        self.play();self.assertEqual(len(self.p.hand),10);self.g.assert_invariants()
    def test_no_public_copy_identity(self):
        self.give('CORE_CS2_029');self.play()
        self.assertNotIn('hand',self.g.observe(1)['players'][0])
        self.assertFalse(any(e.get('card')=='CORE_CS2_029' for e in self.g.observe(1)['events']))
