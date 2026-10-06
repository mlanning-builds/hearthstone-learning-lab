import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class BatMaskTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARLOCK',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def give(self,g):
        c=Card(g._new_id(),'DINO_402');g.players[0].hand.append(c);return c
    def test_sets_original_and_fills_with_independent_copies(self):
        g=self.game();m=g._summon(0,'DINO_132');c=self.give(g);g.step(Action('play',c.uid,m.uid))
        self.assertEqual(len(g.players[0].minions),7)
        self.assertTrue(all((x.attack,x.health,x.max_health)==(1,1,1) for x in g.players[0].minions))
        self.assertEqual(len({x.uid for x in g.players[0].minions}),7)
        self.assertTrue(all('TAUNT' in x.keywords for x in g.players[0].minions))
    def test_full_board_still_sets_original_without_new_entities(self):
        g=self.game()
        for _ in range(7):g._summon(0,'DINO_132')
        before=[m.uid for m in g.players[0].minions];c=self.give(g);g.step(Action('play',c.uid,before[0]))
        self.assertEqual([m.uid for m in g.players[0].minions],before);self.assertEqual(g.players[0].minions[0].health,1)
        self.assertEqual(g.players[0].minions[1].health,12)
    def test_no_target_and_enemy_target_are_illegal(self):
        g=self.game();enemy=g._summon(1,'DINO_132');c=self.give(g)
        self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
        with self.assertRaises(ValueError):g.step(Action('play',c.uid,enemy.uid))
    def test_copies_preserve_frozen_and_do_not_run_battlecry(self):
        g=self.game();m=g._summon(0,'CORE_EX1_319');g._freeze(m.uid);c=self.give(g);g.step(Action('play',c.uid,m.uid))
        self.assertEqual(g.players[0].health,30);self.assertTrue(all(x.frozen_until>=0 for x in g.players[0].minions))
    def test_silencing_one_copy_does_not_reset_others(self):
        g=self.game();m=g._summon(0,'DINO_132');c=self.give(g);g.step(Action('play',c.uid,m.uid));copy=g.players[0].minions[-1];g._silence(copy)
        self.assertEqual((copy.attack,copy.health),(6,12));self.assertEqual((m.attack,m.health),(1,1))
    def test_counterspell_prevents_stat_change_and_copy(self):
        g=self.game();m=g._summon(0,'DINO_132');g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'));c=self.give(g);g.step(Action('play',c.uid,m.uid))
        self.assertEqual(len(g.players[0].minions),1);self.assertEqual((m.attack,m.health),(6,12))
