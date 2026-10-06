import unittest
from expanded import Game,Action,random_deck

class EffectLifestealTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.health=10
    def test_granted_lifesteal_applies_to_deathrattle_damage(self):
        m=self.g._summon(0,'RLK_223');m.keywords.add('LIFESTEAL');m.health=0;self.g._settle()
        self.assertEqual(self.p.health,12);self.assertEqual(self.q.health,28)
        self.assertEqual(self.p.healing_done_turn,2)
    def test_reborn_does_not_inherit_granted_lifesteal(self):
        m=self.g._summon(0,'RLK_223');m.keywords.add('LIFESTEAL');m.health=0;self.g._settle()
        reborn=next(m for m in self.p.minions if m.card_id=='RLK_223')
        self.assertNotIn('LIFESTEAL',reborn.keywords)
        reborn.health=0;self.g._settle();self.assertEqual(self.p.health,12)
    def test_after_attack_effect_uses_source_lifesteal(self):
        m=self.g._summon(0,'TLC_840');m.summoned_turn=-1;m.keywords.add('LIFESTEAL')
        self.g.step(Action('attack',m.uid,-2))
        self.assertEqual(self.p.health,14);self.assertEqual(self.q.health,26)
    def test_silenced_source_does_not_heal(self):
        m=self.g._summon(0,'TLC_840');m.keywords.add('LIFESTEAL');self.g._silence(m)
        self.g._deal_effect(-2,2,dict(owner=0,source=m,lifesteal=True))
        self.assertEqual(self.p.health,10)
    def test_prevented_damage_does_not_create_healing_event(self):
        m=self.g._summon(1,'CORE_EX1_506');m.keywords.add('DIVINE_SHIELD');start=len(self.g.events)
        self.g._deal_effect(m.uid,3,dict(owner=0,source=None,lifesteal=True))
        self.assertFalse(any(e['event']=='heal' for e in self.g.events[start:]))
