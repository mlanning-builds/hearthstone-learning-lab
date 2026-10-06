import unittest
from expanded import Game,Action,random_deck

class EmptyCrystalTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DRUID',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.max_mana=4;p.mana=2
    def kill(self,owner=0,silence=False):
        m=self.g._summon(owner,'EDR_861')
        if silence:self.g._silence(m)
        m.health=0;self.g._settle()
    def test_both_gain_capacity_without_spendable_mana(self):
        self.kill();self.assertEqual([(p.max_mana,p.mana) for p in self.g.players],[(5,2),(5,2)])
    def test_opponent_owned_death_also_affects_both(self):
        self.kill(1);self.assertEqual((self.p.max_mana,self.q.max_mana),(5,5))
    def test_caps_independently_without_overflow_draw(self):
        self.p.max_mana=10;self.q.max_mana=9;self.kill()
        self.assertEqual((self.p.max_mana,self.q.max_mana),(10,10));self.assertEqual(len(self.p.hand)+len(self.q.hand),0)
    def test_silence_removes_deathrattle(self):
        self.kill(silence=True);self.assertEqual((self.p.max_mana,self.q.max_mana),(4,4))
    def test_multiple_deaths_and_overload_unchanged(self):
        self.p.locked_mana=2;self.p.overload_next=1
        for owner in (0,1):self.g._summon(owner,'EDR_861').health=0
        self.g._settle();self.assertEqual((self.p.max_mana,self.q.max_mana),(6,6))
        self.assertEqual((self.p.mana,self.p.locked_mana,self.p.overload_next),(2,2,1))
    def test_next_turn_fills_new_capacity_plus_natural_crystal(self):
        self.kill();self.g.step(Action('end'))
        self.assertEqual((self.q.max_mana,self.q.mana),(6,6))
