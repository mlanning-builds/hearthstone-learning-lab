import unittest
import test_expanded_generation as fixtures
from expanded import cards
class KeywordSpellTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game()
 def play(self,cid,target):
  g=self.g;c=g._add(0,cid);g.players[0].mana=10;cost=g._cost(c,0);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));self.assertEqual(g.players[0].mana,10-cost);g.assert_invariants()
 def test_earth_shock_silences_shield_before_damage_and_blocks_deathrattle(self):
  g=self.g;m=g._summon(1,'EX1_556');m.keywords.add('DIVINE_SHIELD');m.health=1;self.play('EX1_245',m.uid);self.assertFalse(g.players[1].minions)
 def test_earth_shock_damage_receives_spell_damage_after_silence(self):
  g=self.g;g._summon(0,'TID_708t');m=g._summon(1,'CS2_182');self.play('EX1_245',m.uid);self.assertEqual(m.health,2)
 def test_silence_restores_base_stats_and_removes_reborn_shield(self):
  g=self.g;m=g._summon(1,'CS2_182');g._buff(m,4,4);m.keywords.update(('DIVINE_SHIELD','REBORN'));self.play('EX1_332',m.uid);self.assertEqual((m.attack,m.health,m.max_health),(4,5,5));self.assertNotIn('DIVINE_SHIELD',g._effective_keywords(m));self.assertNotIn('REBORN',g._effective_keywords(m))
 def test_focused_will_applies_health_after_silence(self):
  g=self.g;m=g._summon(0,'CS2_182');g._buff(m,4,4);self.play('CS3_027',m.uid);self.assertEqual((m.attack,m.health,m.max_health),(4,8,8))
 def test_hand_of_protection_shields_either_controller_and_prevents_one_hit(self):
  for owner in (0,1):
   self.setUp();g=self.g;m=g._summon(owner,'CS2_182');self.play('EX1_371',m.uid);self.assertEqual(g._damage(m.uid,3),0);self.assertEqual(m.health,5);g._damage(m.uid,3);self.assertEqual(m.health,2)
 def test_rocket_boots_grants_minion_combat_without_hero_attack_and_draws_once(self):
  g=self.g;m=g._summon(0,'CS2_182');enemy=g._summon(1,'CS2_182');before=len(g.players[0].deck);self.play('BOT_067',m.uid);attacks=[a.target for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid];self.assertIn(enemy.uid,attacks);self.assertNotIn(g.hero_id(1),attacks);self.assertEqual(len(g.players[0].deck),before-1)
 def test_seal_of_blood_buffs_shields_and_hits_casters_hero(self):
  g=self.g;m=g._summon(1,'CS2_182');self.play('RLK_922',m.uid);self.assertEqual((m.attack,m.health,m.max_health),(7,8,8));self.assertIn('DIVINE_SHIELD',g._effective_keywords(m));self.assertEqual((g.players[0].health,g.players[1].health),(27,30))


 def test_reviewed_bodies_are_registered_only_as_generated_dependencies(self):
  from expanded.historical_generation import validate_past_candidates
  ids=('BOT_067', 'CS3_027', 'EX1_245', 'EX1_332', 'EX1_371', 'RLK_922')
  metadata=cards.registry();validate_past_candidates(ids,metadata)
  for cid in ids:
   self.assertIn(cid,cards.TOKEN_IDS);self.assertIn(cid,cards.PLAYABLE_TOKENS);self.assertIn(cid,cards.RULES);self.assertNotIn(cid,cards.COLLECTIBLE_IDS)

if __name__=="__main__":unittest.main()
