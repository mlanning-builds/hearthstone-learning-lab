import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class LowestHealthTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('SHAMAN',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
    def play(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_lava_reselects_after_each_death_and_overloads(self):
        a=self.g._summon(1,'CORE_EX1_506');b=self.g._summon(1,'CORE_EX1_506')
        self.play('TLC_227')
        self.assertEqual(self.q.minions,[]);self.assertEqual(self.q.health,28)
        self.assertEqual(self.p.overload_next,1)
    def test_hero_health_selection_ignores_armor(self):
        self.q.health=1;self.q.armor=10;m=self.g._summon(1,'CORE_BT_510')
        self.play('TLC_227');self.assertEqual((self.q.health,self.q.armor,m.health),(1,4,6))
    def test_lifesteal_on_each_hit(self):
        self.p.health=10;self.play('EDR_255')
        self.assertEqual((self.p.health,self.q.health),(20,20))
    def test_shield_prevents_damage_and_healing_then_next_hit_retargets(self):
        m=self.g._summon(1,'CORE_EX1_506');m.keywords.add('DIVINE_SHIELD');self.p.health=10
        self.play('EDR_255');self.assertEqual(self.p.health,15);self.assertNotIn(m,self.q.board)
    def test_spell_damage_applies_to_each_hit(self):
        self.g._summon(0,'TIME_856');self.play('TLC_227')
        self.assertEqual(self.q.health,18)
    def test_random_ties_only_select_minimum_health(self):
        a=self.g._summon(1,'CORE_EX1_506');b=self.g._summon(1,'CORE_EX1_506')
        self.g._effect(('damage_lowest_health_enemy',1),dict(owner=0,source=None,target=0,bonus=0))
        self.assertEqual(sorted([a.health,b.health]),[0,1]);self.assertEqual(self.q.health,30)
