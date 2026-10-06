import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class BulwarkTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=[];p.mana=p.max_mana=10
        self.g._equip(0,'CORE_BT_781')
    def test_damage_replaced_before_armor_health_and_counters(self):
        self.p.armor=4;self.assertEqual(self.g._damage(-1,100),0)
        self.assertEqual((self.p.health,self.p.armor,self.p.weapon['durability']),(30,4,3))
        self.assertEqual((self.p.hero_damage_taken_turn,self.p.hero_damage_events_turn),(0,0))
    def test_each_hit_consumes_one_charge_then_damage_resumes(self):
        for _ in range(4):self.assertEqual(self.g._damage(-1,5),0)
        self.assertIsNone(self.p.weapon);self.assertEqual(self.g._damage(-1,5),5);self.assertEqual(self.p.health,25)
    def test_fatigue_increases_but_damage_is_prevented(self):
        before=self.p.fatigue;self.g._draw(0);self.g._draw(0)
        self.assertEqual(self.p.health,30);self.assertEqual(self.p.fatigue,before+2);self.assertEqual(self.p.weapon['durability'],2)
    def test_hero_attack_consumes_attack_and_prevention_durability(self):
        m=self.g._summon(1,'CS3_025');self.g.step(Action('attack',-1,m.uid))
        self.assertEqual(self.p.health,30);self.assertEqual(m.health,5);self.assertEqual(self.p.weapon['durability'],2)
    def test_last_charge_still_blocks_retaliation(self):
        self.p.weapon['durability']=1;m=self.g._summon(1,'CS3_025')
        self.g.step(Action('attack',-1,m.uid));self.assertEqual(self.p.health,30);self.assertIsNone(self.p.weapon)
    def test_zero_damage_and_other_targets_do_not_spend_charge(self):
        self.g._damage(-1,0);self.g._damage(-2,3);m=self.g._summon(0,'CS3_025');self.g._damage(m.uid,1)
        self.assertEqual(self.p.weapon['durability'],4)
    def test_prevented_damage_has_no_lifesteal_or_freeze(self):
        self.q.health=20;water=self.g._summon(1,'CS2_033');water.keywords.add('LIFESTEAL')
        self.g._deal_effect(-1,3,dict(owner=1,source=water,bonus=0))
        self.assertEqual(self.q.health,20);self.assertEqual(self.p.frozen_until,-1)
    def test_self_damage_and_replacement_weapon(self):
        c=Card(self.g._new_id(),'CORE_EX1_319');self.p.hand.append(c)
        self.g.step(Action('play',c.uid,position=0));self.assertEqual(self.p.health,30);self.assertEqual(self.p.weapon['durability'],3)
        self.g._equip(0,'CS2_082');self.g._damage(-1,3);self.assertEqual(self.p.health,27)
