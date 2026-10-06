import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class NablyaTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def play(self,g):
        c=Card(g._new_id(),'TLC_624');g.players[0].hand.append(c);g.step(Action('play',c.uid,position=len(g.players[0].board)))
    def test_copies_damaged_only_and_does_not_recursively_copy(self):
        g=self.game();a=g._summon(0,'CS3_025');a.health=4;g._summon(0,'CORE_EX1_319');enemy=g._summon(1,'CS3_025');enemy.health=1
        self.play(g);self.assertEqual(len(g.players[0].minions),4)
        copy=g.players[0].minions[-1];self.assertEqual((copy.card_id,copy.health,copy.max_health),('CS3_025',4,6));self.assertNotEqual(copy.uid,a.uid)
    def test_copied_stats_damage_and_keywords_are_independent(self):
        g=self.game();a=g._summon(0,'CS3_025');g._buff(a,2,3);a.health-=2;a.keywords.add('LIFESTEAL')
        self.play(g);copy=g.players[0].minions[-1]
        self.assertEqual((copy.attack,copy.health,copy.max_health),(5,7,9));self.assertIn('LIFESTEAL',copy.keywords)
        g._buff(copy,1,1);self.assertEqual((a.attack,a.health),(5,7))
    def test_copy_has_rush_and_fresh_attack_state(self):
        g=self.game();a=g._summon(0,'DINO_132');a.health=4;a.attacks=1;enemy=g._summon(1,'CS3_025');self.play(g);copy=g.players[0].minions[-1]
        self.assertEqual(copy.attacks,0);self.assertIn(Action('attack',copy.uid,enemy.uid),g.legal_actions())
        self.assertNotIn(Action('attack',copy.uid,-2),g.legal_actions())
    def test_copy_does_not_run_battlecry(self):
        g=self.game();a=g._summon(0,'CORE_EX1_319');a.health=1;self.play(g)
        self.assertEqual(g.players[0].health,30);self.assertEqual(g.players[0].minions[-1].health,1)
    def test_board_limit_and_no_damaged_minions(self):
        g=self.game();self.play(g);self.assertEqual(len(g.players[0].minions),1)
        g=self.game()
        for _ in range(5):g._summon(0,'DINO_132').health=4
        self.play(g);self.assertEqual(len(g.players[0].minions),7)
        self.assertEqual(sum('RUSH' in m.keywords for m in g.players[0].minions),1)
