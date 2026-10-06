import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ChronoclawsTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARLOCK',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=[];p.mana=p.max_mana=10
        self.g._equip(0,'END_016')
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def attack(self):self.g.step(Action('attack',-1,-2))
    def test_attack_discards_highest_and_uses_durability(self):
        low=self.give('CORE_EX1_506');high=self.give('CORE_CS2_029')
        self.attack();self.assertEqual(self.p.hand,[low]);self.assertEqual(self.p.discard_history,[high.card_id])
        self.assertEqual(self.q.health,26);self.assertEqual(self.p.weapon['durability'],2)
    def test_current_cost_discounts_determine_selection(self):
        high=self.give('CORE_CS2_029');high.cost_delta=-4
        low=self.give('CORE_EX1_506');self.attack()
        self.assertEqual(self.p.hand,[high]);self.assertEqual(self.p.discard_history,[low.card_id])
    def test_ties_choose_one_eligible_card(self):
        a=self.give('CORE_CS2_029');b=self.give('CORE_CS2_029');low=self.give('CORE_EX1_506')
        self.attack();self.assertIn(low,self.p.hand);self.assertEqual(len(self.p.hand),2)
        self.assertEqual(len(self.p.discard_history),1)
    def test_last_durability_still_discards(self):
        self.p.weapon['durability']=1;self.give('CORE_CS2_029');self.attack()
        self.assertIsNone(self.p.weapon);self.assertFalse(self.p.hand)
    def test_empty_hand_does_not_fatigue(self):
        self.attack();self.assertEqual(self.p.fatigue,0);self.assertEqual(self.p.discard_history,[])
    def test_minion_attack_does_not_discard(self):
        c=self.give('CORE_CS2_029');m=self.g._summon(0,'CORE_EX1_506');m.summoned_turn=-1
        self.g.step(Action('attack',m.uid,-2));self.assertEqual(self.p.hand,[c])
    def test_maloriak_copies_discard_after_hero_attack(self):
        self.g._summon(0,'CATA_494');self.give('CATA_493');self.attack()
        dukes=[m for m in self.p.minions if m.card_id=='CATA_493']
        self.assertEqual(len(dukes),1);self.assertEqual(dukes[0].attack,4)
