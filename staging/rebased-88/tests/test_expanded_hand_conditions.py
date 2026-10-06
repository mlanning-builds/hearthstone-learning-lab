import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HandConditionTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
    def hand(self,ids):
        self.p.hand=[Card(self.g._new_id(),cid) for cid in ids]
    def play(self,index,target=0):
        c=self.p.hand[index]
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def test_exact_center_before_removal(self):
        self.hand(['TOKEN_COIN','TIME_600','TOKEN_COIN']);self.play(1,-2)
        self.assertEqual(self.q.health,25)
    def test_single_card_is_center(self):
        self.hand(['TIME_600']);self.play(0,-2);self.assertEqual(self.q.health,25)
    def test_even_hand_has_no_center(self):
        self.hand(['TIME_600','TOKEN_COIN']);self.play(0,-2);self.assertEqual(self.q.health,27)
    def test_off_center_gets_base_damage(self):
        self.hand(['TIME_600','TOKEN_COIN','TOKEN_COIN']);self.play(0,-2);self.assertEqual(self.q.health,27)
    def test_center_damage_gets_spell_damage(self):
        self.g._summon(0,'TIME_856');self.hand(['TIME_600']);self.play(0,-2);self.assertEqual(self.q.health,23)
    def test_broodmother_does_not_count_itself(self):
        self.hand(['CATA_111']);cost=self.g.cards['CATA_111']['cost'];self.play(0)
        self.assertEqual(self.p.mana,10-cost)
    def test_broodmother_refreshes_with_another_dragon(self):
        self.hand(['CATA_111','TIME_856']);cost=self.g.cards['CATA_111']['cost'];self.play(0)
        self.assertEqual(self.p.mana,min(10,10-cost+2))
