import unittest
from expanded import Game,Action,random_deck

class HorrorTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEATHKNIGHT',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0]
    def summon(self):return self.g._summon(0,'CORE_RLK_745')
    def test_new_copy_does_not_trigger_again_same_turn(self):
        self.summon();self.p.corpses=12;self.g.step(Action('end'))
        self.assertEqual(len(self.p.minions),2);self.assertEqual(self.p.corpses,8)
    def test_insufficient_corpses_not_partially_spent(self):
        self.summon();self.p.corpses=3;self.g.step(Action('end'))
        self.assertEqual(len(self.p.minions),1);self.assertEqual(self.p.corpses,3)
    def test_copies_damage_buffs_and_reborn(self):
        m=self.summon();self.g._buff(m,2,3);m.health-=2;self.p.corpses=4
        self.g.step(Action('end'));c=self.p.minions[1]
        self.assertEqual((c.attack,c.health,c.max_health),(m.attack,m.health,m.max_health))
        self.assertIn('REBORN',c.keywords)
    def test_silence_prevents_spending(self):
        self.g._silence(self.summon());self.p.corpses=8;self.g.step(Action('end'))
        self.assertEqual(self.p.corpses,8);self.assertEqual(len(self.p.minions),1)
    def test_opponents_end_does_not_trigger(self):
        self.summon();self.g.step(Action('end'));self.p.corpses=4;self.g.step(Action('end'))
        self.assertEqual(self.p.corpses,4);self.assertEqual(len(self.p.minions),1)
    def test_existing_sources_share_corpse_budget(self):
        self.summon();self.summon();self.p.corpses=4;self.g.step(Action('end'))
        self.assertEqual(self.p.corpses,0);self.assertEqual(len(self.p.minions),3)
