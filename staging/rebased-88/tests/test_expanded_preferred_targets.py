import unittest
import test_expanded_generation as fixtures
class PreferredTargetTests(unittest.TestCase):
 def setUp(self):self.fx=fixtures.GenerationTests();self.g=self.fx.game()
 def cast(self,cid,policy='prefer_enemies'):self.fx.run_ops(self.g,[('cast_fixed_spell',cid,policy)])
 def test_prefers_enemy_hero_for_character_spell(self):
  self.cast('CORE_CS2_029');self.assertEqual([p.health for p in self.g.players],[30,24])
 def test_falls_back_to_friendly_minion(self):
  m=self.g._summon(0,'CORE_EX1_162');self.cast('CORE_CS2_009');self.assertIn(m,self.g.players[0].minions);self.assertEqual((m.attack,m.health),(4,5));self.assertIn('TAUNT',m.keywords)
 def test_strict_enemy_policy_still_fizzles_friendly_only(self):
  m=self.g._summon(0,'CORE_EX1_162');before=(m.attack,m.health);self.cast('CORE_CS2_009','enemies');self.assertEqual((m.attack,m.health),before)
 def test_no_target_spell_executes(self):
  self.g.players[0].mana=1;self.cast('TOKEN_COIN');self.assertEqual(self.g.players[0].mana,2)

 def test_enemy_minion_preferred_over_friendly(self):
  friendly=self.g._summon(0,'CORE_EX1_162');enemy=self.g._summon(1,'CORE_EX1_162');self.cast('CORE_CS2_009');self.assertEqual(friendly.attack,2);self.assertEqual(enemy.attack,4)
