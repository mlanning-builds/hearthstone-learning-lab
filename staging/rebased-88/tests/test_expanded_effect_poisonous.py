import unittest
from expanded import Game,Action,random_deck

class EffectPoisonousTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.source=self.g._summon(0,'CORE_BT_510');self.source.keywords.add('POISONOUS')
        self.target=self.g._summon(1,'EDR_471')
    def hit(self,amount=1):
        dealt=self.g._deal_effect(self.target.uid,amount,dict(owner=0,source=self.source))
        self.g._settle();return dealt
    def test_effect_damage_destroys_high_health_minion(self):
        self.assertEqual(self.hit(),1);self.assertNotIn(self.target,self.q.board)
    def test_shield_prevents_poisonous(self):
        self.target.keywords.add('DIVINE_SHIELD');self.assertEqual(self.hit(),0)
        self.assertIn(self.target,self.q.board);self.assertEqual(self.target.health,30)
    def test_immunity_prevents_poisonous(self):
        self.target.keywords.add('IMMUNE');self.assertEqual(self.hit(),0)
        self.assertIn(self.target,self.q.board)
    def test_zero_damage_does_not_poison(self):
        self.assertEqual(self.hit(0),0);self.assertIn(self.target,self.q.board)
    def test_silence_removes_effect_poisonous(self):
        self.g._silence(self.source);self.hit();self.assertEqual(self.target.health,29)
    def test_poisonous_does_not_destroy_hero(self):
        self.g._deal_effect(-2,1,dict(owner=0,source=self.source));self.g._settle()
        self.assertEqual(self.q.health,29);self.assertFalse(self.g.terminal)
    def test_lifesteal_counts_damage_not_poison_destroyed_health(self):
        self.p.health=10;self.source.keywords.add('LIFESTEAL');self.hit()
        self.assertEqual(self.p.health,11)
    def test_unrelated_spell_does_not_inherit_board_poisonous(self):
        self.g._deal_effect(self.target.uid,1,dict(owner=0,source=None,spell=True));self.g._settle()
        self.assertEqual(self.target.health,29)
