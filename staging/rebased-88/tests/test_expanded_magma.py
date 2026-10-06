import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class MagmaTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('SHAMAN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g,g._summon(0,'TLC_224')
    def cast(self,g,cid='CORE_CS2_029',target=-2,delta=0):
        c=Card(g._new_id(),cid);c.cost_delta=delta;g.players[0].hand.append(c)
        g.step(Action('play',c.uid,target))
    def test_fire_spell_buffs_both_stats_before_damage(self):
        g,m=self.game();self.cast(g,target=m.uid)
        self.assertIn(m,g.players[0].minions)
        self.assertEqual((m.attack,m.health,m.max_health),(6,3,9))
    def test_paid_cost_including_discount_and_zero(self):
        g,m=self.game();self.cast(g,delta=-3)
        self.assertEqual((m.attack,m.health),(3,6));self.cast(g,delta=-4)
        self.assertEqual((m.attack,m.health),(3,6))
    def test_wrong_school_and_owner(self):
        g,m=self.game();self.cast(g,'TOKEN_COIN',0)
        g._queue_event('spell_played',owner=1,card_id='CORE_CS2_029',cost=4);g._settle()
        self.assertEqual((m.attack,m.health),(2,5))
    def test_silence_and_multiple_sources(self):
        g,m=self.game();other=g._summon(0,'TLC_224');g._silence(m);self.cast(g)
        self.assertEqual((m.attack,m.health),(2,5));self.assertEqual((other.attack,other.health),(6,9))
    def test_countered_spell_pre_trigger_without_spell_damage(self):
        g,m=self.game();g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'))
        self.cast(g);self.assertEqual(g.players[1].health,30)
        self.assertEqual((m.attack,m.health),(6,9))
