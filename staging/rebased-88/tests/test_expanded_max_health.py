import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class MaximumHealthTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PRIEST',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20
        return g
    def cast(self,g):
        p=g.players[0];p.mana=p.max_mana=10
        c=Card(g._new_id(),'TLC_835');p.hand.append(c);g.step(Action('play',c.uid))
    def test_sets_current_and_maximum_preserves_armor(self):
        g=self.game();p=g.players[0];p.health=3;p.armor=7;self.cast(g)
        self.assertEqual((p.health,p.max_health,p.armor),(40,40,7))
        self.assertEqual(g.players[1].max_health,30)
    def test_healing_uses_new_ceiling(self):
        g=self.game();self.cast(g);p=g.players[0];p.health=35
        self.assertEqual(g._heal(-1,20,healer=0),5)
        self.assertEqual((p.health,p.healing_done_turn),(40,5))
        self.assertEqual(g._heal(-1,2),0)
    def test_setting_is_not_healing(self):
        g=self.game();p=g.players[0];p.health=1;p.healing_block_expiry_players=[1]
        self.cast(g);self.assertEqual((p.health,p.healing_done_turn),(40,0))
        p.health=35;self.assertEqual(g._heal(-1,5),0);self.assertEqual(p.health,35)
    def test_repeated_setting_and_higher_maximum(self):
        g=self.game();p=g.players[0];p.max_health=p.health=50
        self.cast(g);self.assertEqual((p.health,p.max_health),(40,40))
        p.health=20;self.cast(g);self.assertEqual(p.health,40)
    def test_random_heal_above_thirty(self):
        g=self.game();self.cast(g);p=g.players[0];p.health=35
        g._effect(('random_heal',12),dict(owner=0,source=None,target=0,bonus=0))
        self.assertEqual((p.health,p.healing_done_turn),(40,5))
    def test_default_ceiling_and_public_visibility(self):
        g=self.game();p=g.players[0];p.health=29
        self.assertEqual(g._heal(-1,10),1);self.cast(g)
        for viewer in (0,1):self.assertEqual([p['max_health'] for p in g.observe(viewer)['players']],[40,30])
