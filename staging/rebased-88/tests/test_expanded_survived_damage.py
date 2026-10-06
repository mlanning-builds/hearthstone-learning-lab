import unittest
from expanded import Game,Action,random_deck

class SurvivedDamageTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
        self.rioter=self.g._summon(0,'JAIL_029')
    def hit(self,m,amount=1):
        self.g._damage(m.uid,amount);self.g._settle()
    def test_friendly_survivor_and_self_gain_attack(self):
        m=self.g._summon(0,'CS3_025');self.hit(m);self.hit(self.rioter)
        self.assertEqual((m.attack,m.health,self.rioter.attack),(4,5,2))
    def test_enemy_and_hero_damage_do_not_buff(self):
        m=self.g._summon(1,'CS3_025');self.hit(m);self.g._damage(-1,1);self.g._settle()
        self.assertEqual((m.attack,self.rioter.attack),(3,1))
    def test_lethal_damage_does_not_buff(self):
        m=self.g._summon(0,'CORE_WON_351');self.hit(m,2)
        self.assertNotIn(m,self.p.minions);self.assertEqual(m.attack,1)
    def test_shield_immune_and_zero_damage_do_not_buff(self):
        m=self.g._summon(0,'CS3_025');m.keywords.add('DIVINE_SHIELD');self.hit(m)
        m.keywords.add('IMMUNE');self.hit(m);m.keywords.remove('IMMUNE');self.hit(m,0)
        self.assertEqual(m.attack,3)
    def test_silence_and_new_listener_do_not_react(self):
        self.g._silence(self.rioter);m=self.g._summon(0,'CS3_025');self.g._damage(m.uid,1)
        self.g._summon(0,'JAIL_029');self.g._settle();self.assertEqual(m.attack,3)
    def test_multiple_listeners_and_enemy_turn(self):
        self.g._summon(0,'JAIL_029');m=self.g._summon(0,'CS3_025')
        self.g.step(Action('end'));self.hit(m);self.assertEqual(m.attack,5)
    def test_poisonous_damage_not_survived(self):
        m=self.g._summon(0,'CS3_025');self.g._damage(m.uid,1,poisonous=True);self.g._settle()
        self.assertNotIn(m,self.p.minions);self.assertEqual(m.attack,3)
    def test_mortally_wounded_listener_does_not_buff_other_survivor(self):
        m=self.g._summon(0,'CS3_025')
        with self.g._damage_batch():
            self.g._damage(self.rioter.uid,6);self.g._damage(m.uid,1)
        self.g._settle();self.assertEqual(m.attack,3)
