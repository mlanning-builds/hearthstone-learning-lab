import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class GoonTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('SHAMAN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g,g._summon(0,'JAIL_802')
    def play(self,g,cid):
        c=Card(g._new_id(),cid);g.players[0].hand.append(c);g.step(Action('play',c.uid,position=len(g.players[0].board)))
        return g.players[0].minions[-1]
    def test_battlecry_completes_then_played_minion_buffed(self):
        g,goon=self.game();m=self.play(g,'CORE_EX1_319')
        self.assertEqual(g.players[0].health,27);self.assertEqual((m.attack,m.health),(4,3))
        self.assertEqual((goon.attack,goon.health),(2,3))
    def test_summoned_battlecry_does_not_trigger(self):
        g,_=self.game();m=g._summon(0,'CORE_EX1_319');g._settle()
        self.assertEqual((m.attack,m.health),(3,2));self.assertEqual(g.players[0].health,30)
    def test_non_battlecry_and_opponent_do_not_trigger(self):
        g,_=self.game();m=self.play(g,'JAIL_802');self.assertEqual((m.attack,m.health),(2,3))
        enemy=g._summon(1,'CORE_EX1_319');g._queue_event('minion_played',owner=1,card_id=enemy.card_id,source=enemy.uid,cost=1);g._settle()
        self.assertEqual((enemy.attack,enemy.health),(3,2))
    def test_multiple_sources_and_silence(self):
        g,goon=self.game();g._summon(0,'JAIL_802');m=self.play(g,'CORE_EX1_319')
        self.assertEqual((m.attack,m.health),(5,4));g._silence(goon)
        m=self.play(g,'CORE_EX1_319');self.assertEqual((m.attack,m.health),(4,3))
    def test_removed_event_source_is_not_recreated(self):
        g,_=self.game();m=g._summon(0,'CORE_EX1_319');g.players[0].board.remove(m)
        g._queue_event('minion_played',owner=0,card_id=m.card_id,source=m.uid,cost=1);g._settle()
        self.assertEqual(len(g.players[0].minions),1)
