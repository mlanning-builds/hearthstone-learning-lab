import unittest
from expanded import Game,Action,random_deck

class IncomingDamageTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def test_double_and_extra_damage_use_distinct_values(self):
        for cid,wanted in [('TIME_060',4),('CATA_208',3)]:
            m=self.g._summon(0,cid);before=m.health
            self.assertEqual(self.g._damage(m.uid,2),wanted)
            self.assertEqual(m.health,before-wanted)
    def test_zero_damage_never_becomes_a_hit(self):
        m=self.g._summon(0,'CATA_208');m.keywords.add('DIVINE_SHIELD');before=m.health
        self.assertEqual(self.g._damage(m.uid,0),0)
        self.assertEqual(m.health,before);self.assertIn('DIVINE_SHIELD',m.keywords)
    def test_divine_shield_and_immune_prevent_modified_damage(self):
        m=self.g._summon(0,'TIME_060');before=m.health;m.keywords.add('DIVINE_SHIELD')
        self.assertEqual(self.g._damage(m.uid,3),0);self.assertEqual(m.health,before)
        m.keywords.add('IMMUNE');self.assertEqual(self.g._damage(m.uid,3),0)
        self.assertEqual(m.health,before)
    def test_silence_removes_printed_modifier(self):
        for cid in ('TIME_060','CATA_208'):
            m=self.g._summon(0,cid);self.g._silence(m)
            self.assertEqual(self.g._damage(m.uid,1),1)
    def test_spell_bonus_is_applied_before_incoming_multiplier(self):
        m=self.g._summon(1,'TIME_060');before=m.health
        self.g._deal_effect(m.uid,1,dict(owner=0,bonus=2,lifesteal=False,spell=True))
        self.assertEqual(m.health,before-6)
    def test_combat_uses_modified_damage_and_retaliates_normally(self):
        a=self.g._summon(0,'Core_CS2_200');a.summoned_turn=-1
        b=self.g._summon(1,'TIME_060');self.g._buff(b,0,30)
        ah,bh=a.health,b.health;attack=b.attack
        self.g.step(Action('attack',a.uid,b.uid))
        self.assertEqual(b.health,bh-12);self.assertEqual(a.health,ah-attack)
