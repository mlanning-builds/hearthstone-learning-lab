import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ConditionalAuraTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def test_seer_switches_with_damage_healing_and_silence(self):
        m=self.g._summon(0,'END_022');self.assertEqual(self.g._spell_damage(0),0)
        self.g._damage(m.uid,1);self.g._settle();self.assertEqual(self.g._spell_damage(0),2)
        self.g._heal(m.uid,1);self.assertEqual(self.g._spell_damage(0),0)
        self.g._damage(m.uid,1);self.g._silence(m);self.assertEqual(self.g._spell_damage(0),0)
    def test_damaged_seers_stack_and_modify_real_spell_damage(self):
        for _ in range(2):
            m=self.g._summon(0,'END_022');self.g._damage(m.uid,1)
        self.g._settle();c=Card(self.g._new_id(),'CORE_CS2_029');self.p.hand.append(c)
        self.g.step(Action('play',c.uid,self.g.hero_id(1)))
        self.assertEqual(self.q.health,20)
    def test_spiderlings_grant_hero_attack_only_on_owner_turn(self):
        self.g._summon(0,'JAIL_202');self.g._summon(0,'JAIL_202');self.g._summon(1,'JAIL_202')
        self.assertEqual((self.g._hero_attack(0),self.g._hero_attack(1)),(2,0))
        self.g.step(Action('attack',self.g.hero_id(0),self.g.hero_id(1)));self.assertEqual(self.q.health,28)
        self.g.step(Action('end'));self.assertEqual((self.g._hero_attack(0),self.g._hero_attack(1)),(0,1))
    def test_spiderling_removal_and_silence_remove_attack(self):
        a=self.g._summon(0,'JAIL_202');b=self.g._summon(0,'JAIL_202')
        self.g._silence(a);self.assertEqual(self.g._hero_attack(0),1)
        b.health=0;self.g._settle();self.assertEqual(self.g._hero_attack(0),0)
