import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HandCostConditionTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEMONHUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def give(self,cid='CORE_CS2_029',cost=None):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c)
        if cost is not None:c.cost_delta=cost-self.g.cards[cid]['cost']
        return c
    def play_flame(self):
        c=self.give('FIR_940');self.g.step(Action('play',c.uid,position=len(self.p.board)))
    def kill_dragon(self,silenced=False):
        m=self.g._summon(0,'EDR_890')
        if silenced:self.g._silence(m)
        m.health=0;self.g._settle()
    def test_rightmost_card_uses_current_hand_order(self):
        a=self.give(cost=5);b=self.give(cost=4);self.p.hand.reverse()
        self.kill_dragon();self.assertEqual([self.g._cost(c,0) for c in (a,b)],[3,4])
    def test_silence_and_empty_hand(self):
        a=self.give(cost=5);self.kill_dragon(True);self.assertEqual(self.g._cost(a,0),5)
        self.p.hand=[];self.kill_dragon();self.assertEqual(self.p.hand,[])
    def test_discount_accumulates_and_floors_at_zero(self):
        a=self.give(cost=1);before=a.cost_delta;self.kill_dragon();self.kill_dragon()
        self.assertEqual(a.cost_delta,before-4);self.assertEqual(self.g._cost(a,0),0)
    def test_distinct_current_costs_activate_even_for_identical_ids(self):
        a=self.give(cost=3);b=self.give(cost=5);self.play_flame()
        self.assertEqual([self.g._cost(c,0) for c in (a,b)],[1,3])
    def test_matching_modified_costs_disable_entire_discount(self):
        a=self.give(cost=3);b=self.give('EDR_890',cost=3);self.play_flame()
        self.assertEqual([self.g._cost(c,0) for c in (a,b)],[3,3])
    def test_played_flame_does_not_count_in_condition(self):
        cost=self.g.cards['FIR_940']['cost'];a=self.give(cost=cost);self.play_flame()
        self.assertEqual(self.g._cost(a,0),max(0,cost-2))
    def test_empty_hand_and_summon_only(self):
        self.play_flame();self.assertEqual(self.p.hand,[])
        a=self.give(cost=4);self.g._summon(0,'FIR_940');self.assertEqual(self.g._cost(a,0),4)
    def test_distinctness_uses_floored_payable_cost(self):
        a=self.give(cost=-2);b=self.give(cost=-4);before=[a.cost_delta,b.cost_delta]
        self.play_flame();self.assertEqual([a.cost_delta,b.cost_delta],before)
