import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class FletcherTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('HUNTER',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def fill(self,g,n):
        g.players[0].hand=[Card(g._new_id(),'CORE_CS2_029') for _ in range(n)]
    def test_threshold_tracks_live_hand(self):
        g=self.game();g._summon(0,'TIME_606')
        for n,cost in ((0,0),(3,0),(4,2),(3,0),(10,2)):
            self.fill(g,n);self.assertEqual(g._power_cost(0),cost)
    def test_free_power_legal_and_consumed_once(self):
        g=self.game();g._summon(0,'TIME_606');g.players[0].mana=0
        self.assertIn(Action('power'),g.legal_actions());g.step(Action('power'))
        self.assertEqual((g.players[0].mana,g.players[1].health),(0,28))
        self.assertNotIn(Action('power'),g.legal_actions())
    def test_silence_removal_and_other_owner(self):
        g=self.game();m=g._summon(1,'TIME_606');self.assertEqual(g._power_cost(0),2)
        m=g._summon(0,'TIME_606');g._silence(m);self.assertEqual(g._power_cost(0),2)
        m=g._summon(0,'TIME_606');self.assertEqual(g._power_cost(0),0)
        m.health=0;g._settle();self.assertEqual(g._power_cost(0),2)
    def test_multiple_auras_and_silencing_one(self):
        g=self.game();a=g._summon(0,'TIME_606');b=g._summon(0,'TIME_606')
        g._silence(a);self.assertEqual(g._power_cost(0),0)
        g._silence(b);self.assertEqual(g._power_cost(0),2)
    def test_playing_fletcher_leaves_three_cards(self):
        g=self.game();self.fill(g,3);c=Card(g._new_id(),'TIME_606');g.players[0].hand.append(c)
        g.step(Action('play',c.uid,position=0));self.assertEqual(g._power_cost(0),0)
        g._draw(0);self.assertEqual(g._power_cost(0),2)
    def test_observed_cost_in_both_views(self):
        g=self.game();g._summon(0,'TIME_606')
        for viewer in (0,1):self.assertEqual(g.observe(viewer)['players'][0]['hero_power_cost'],0)
        self.fill(g,4)
        for viewer in (0,1):self.assertEqual(g.observe(viewer)['players'][0]['hero_power_cost'],2)
