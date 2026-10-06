import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class SaucierTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEMONHUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def hand(self,ids):
        self.p.hand=[Card(self.g._new_id(),cid) for cid in ids];return list(self.p.hand)
    def play(self,index):
        c=self.p.hand[index];self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_only_original_neighbors_discounted(self):
        cards=self.hand(['CORE_CS2_029']*2+['DINO_137']+['CORE_CS2_029']*2)
        self.play(2);self.assertEqual([getattr(c,'cost_delta',0) for c in self.p.hand],[0,-1,-1,0])
        self.assertEqual(self.p.mana,7)
    def test_left_edge_has_one_neighbor(self):
        self.hand(['DINO_137','CORE_CS2_029','CORE_CS2_029']);self.play(0)
        self.assertEqual([getattr(c,'cost_delta',0) for c in self.p.hand],[-1,0])
    def test_right_edge_has_one_neighbor(self):
        self.hand(['CORE_CS2_029','CORE_CS2_029','DINO_137']);self.play(2)
        self.assertEqual([getattr(c,'cost_delta',0) for c in self.p.hand],[0,-1])
    def test_only_card_has_no_neighbors(self):
        self.hand(['DINO_137']);self.play(0);self.assertEqual(self.p.hand,[])
    def test_discount_applies_to_weapon_and_minion(self):
        self.hand(['EDR_457t','DINO_137','CORE_EX1_506']);self.play(1)
        self.assertEqual([self.g._cost(c,0) for c in self.p.hand],[1,1])
    def test_direct_summon_does_not_discount(self):
        self.hand(['CORE_CS2_029']);self.g._summon(0,'DINO_137')
        self.assertEqual(getattr(self.p.hand[0],'cost_delta',0),0)
