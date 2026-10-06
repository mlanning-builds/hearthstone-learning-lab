import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.selectors import has_tribe

class RandomHandDiscountTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
        self.beast=next(cid for cid,d in self.g.cards.items() if d['type']=='MINION' and has_tribe(d,'BEAST') and d.get('cost',0)>=2)
    def give(self,owner,cid):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c
    def kill_explorer(self,silenced=False):
        m=self.g._summon(0,'TLC_244')
        if silenced:self.g._silence(m)
        m.health=0;self.g._settle()
    def test_explorer_only_discounts_opponent_minion(self):
        a=self.give(0,self.beast);b=self.give(1,self.beast);c=self.give(1,'CORE_CS2_029')
        self.kill_explorer();self.assertEqual([getattr(a,'cost_delta',0),getattr(b,'cost_delta',0),getattr(c,'cost_delta',0)],[0,-2,0])
    def test_explorer_silence_and_no_eligible_card(self):
        b=self.give(1,self.beast);self.kill_explorer(True);self.assertEqual(getattr(b,'cost_delta',0),0)
        self.q.hand=[];self.kill_explorer();self.assertEqual(self.q.hand,[])
    def test_explorer_selects_one_physical_copy(self):
        copies=[self.give(1,self.beast) for _ in range(3)]
        self.kill_explorer();self.assertEqual(sorted(getattr(c,'cost_delta',0) for c in copies),[-2,0,0])
    def test_dinositter_only_owner_end_and_beasts(self):
        a=self.give(0,self.beast);b=self.give(1,self.beast);c=self.give(0,'TLC_244')
        self.g._summon(0,'TLC_822');self.g.step(Action('end'))
        self.assertEqual([getattr(a,'cost_delta',0),getattr(b,'cost_delta',0),getattr(c,'cost_delta',0)],[-1,0,0])
        self.g.step(Action('end'));self.assertEqual(a.cost_delta,-1)
    def test_dinositter_silence_stops_discount(self):
        a=self.give(0,self.beast);m=self.g._summon(0,'TLC_822');self.g._silence(m)
        self.g.step(Action('end'));self.assertEqual(getattr(a,'cost_delta',0),0)
    def test_multiple_dinositters_stack_and_cost_floors(self):
        a=self.give(0,self.beast);a.cost_delta=-20
        self.g._summon(0,'TLC_822');self.g._summon(0,'TLC_822');self.g.step(Action('end'))
        self.assertEqual(a.cost_delta,-22);self.assertEqual(self.g._cost(a,0),0)
    def test_dinositter_empty_hand_is_safe(self):
        self.g._summon(0,'TLC_822');self.g.step(Action('end'));self.assertEqual(self.p.hand,[])
