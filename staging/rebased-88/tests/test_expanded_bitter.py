import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class BitterEndTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
    def summon(self,owner=1):return self.g._summon(owner,'END_035')
    def play(self,m):
        c=Card(self.g._new_id(),'END_023');self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==m.uid))
    def test_freezes_three_and_destroys_only_damaged(self):
        a,b,c=[self.summon() for _ in range(3)];a.health-=1;self.play(b)
        self.assertNotIn(a,self.q.minions);self.assertTrue(b.frozen_until>=0 and c.frozen_until>=0)
    def test_damaged_target_destroyed_through_divine_shield(self):
        m=self.summon();m.health-=1;m.keywords.add('DIVINE_SHIELD');self.play(m)
        self.assertNotIn(m,self.q.minions)
    def test_farther_minion_unaffected(self):
        a,b,c,d=[self.summon() for _ in range(4)];d.health-=1;self.play(b)
        self.assertIn(d,self.q.minions);self.assertEqual(d.frozen_until,-1)
    def test_location_blocks_adjacency(self):
        a=self.summon();location=self.g._place_location(1,'CORE_REV_990');b=self.summon()
        self.play(a);self.assertEqual(b.frozen_until,-1);self.assertIn(location,self.q.board)
    def test_friendly_minion_can_be_targeted(self):
        m=self.summon(0);self.play(m);self.assertGreaterEqual(m.frozen_until,0)
    def test_destroyed_minion_reborn_is_not_frozen_by_original_spell(self):
        m=self.g._summon(1,'CORE_RLK_745');m.health=1;self.play(m)
        reborn=self.q.minions[0];self.assertNotEqual(reborn.uid,m.uid);self.assertEqual(reborn.frozen_until,-1)
