import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class TurnCountTests(unittest.TestCase):
    def game(self,first=0):
        g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71,first_player=first)
        self.assertEqual([p.turns_taken for p in g.players],[0,0])
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20
        return g
    def play(self,g):
        p=g.players[g.current];p.mana=p.max_mana=10
        c=Card(g._new_id(),'TIME_048');p.hand.append(c);g.step(Action('play',c.uid,position=0));return p.minions[0]
    def test_first_turn_counts_in_battlecry(self):
        g=self.game();m=self.play(g);self.assertEqual((m.attack,m.health,m.max_health),(5,2,2))
    def test_counts_each_player_separately(self):
        g=self.game()
        for _ in range(4):g.step(Action('end'))
        self.assertEqual([p.turns_taken for p in g.players],[3,2]);m=self.play(g);self.assertEqual(m.health,4)
        g.step(Action('end'));m=self.play(g);self.assertEqual(m.health,4)
    def test_reversed_first_player(self):
        g=self.game(1);self.assertEqual([p.turns_taken for p in g.players],[0,1])
        g.step(Action('end'));self.assertEqual([p.turns_taken for p in g.players],[1,1])
    def test_summon_bypasses_battlecry_and_silence_removes_bonus(self):
        g=self.game();m=g._summon(0,'TIME_048');self.assertEqual(m.health,1)
        played=self.play(g);g._silence(played);self.assertEqual((played.health,played.max_health),(1,1))
    def test_count_public_in_both_views(self):
        g=self.game();g.step(Action('end'))
        for viewer in (0,1):self.assertEqual([p['turns_taken'] for p in g.observe(viewer)['players']],[1,1])
    def test_illegal_action_does_not_advance_count(self):
        g=self.game();before=[p.turns_taken for p in g.players]
        with self.assertRaises(ValueError):g.step(Action('play',999))
        self.assertEqual([p.turns_taken for p in g.players],before)
