import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class SpellDamageValuesTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def test_instructor_contributes_two_without_mutating_frozen_record(self):
        self.g._summon(0,'TIME_856')
        self.assertEqual(self.g.cards['TIME_856']['spellDamage'],1)
        self.assertEqual(self.g._spell_damage(0),2)
        c=Card(self.g._new_id(),'CORE_CS2_029');self.p.hand.append(c)
        self.g.step(Action('play',c.uid,self.g.hero_id(1)))
        self.assertEqual(self.q.health,22)
    def test_multiple_sources_add_and_silence_removes_only_one(self):
        m=self.g._summon(0,'TIME_856');self.g._summon(0,'TIME_856')
        self.g._summon(0,'CORE_EX1_012')
        self.assertEqual(self.g._spell_damage(0),5)
        self.g._silence(m);self.assertEqual(self.g._spell_damage(0),3)
    def test_enemy_source_and_removed_source_do_not_contribute(self):
        m=self.g._summon(0,'TIME_856');self.g._summon(1,'TIME_856')
        m.health=0;self.g._settle()
        self.assertEqual(self.g._spell_damage(0),0)
        self.assertEqual(self.g._spell_damage(1),2)
