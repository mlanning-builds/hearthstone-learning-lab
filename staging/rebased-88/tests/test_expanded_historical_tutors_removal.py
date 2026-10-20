"""Physical paid plays exercise historical deck selectors and destruction."""
import unittest
import test_expanded_generation as fixtures
from expanded.historical_tutors import RULES as TUTORS
from expanded.historical_removal import RULES as REMOVAL
class HistoricalTutorsRemovalTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid,target=None):
  c=g._add(0,cid);g.players[0].mana=10
  actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)]
  self.assertTrue(actions,cid);g.step(actions[0]);g.assert_invariants()
 def test_all_roots_paid_play_without_matches(self):
  for cid in TUTORS|REMOVAL:
   with self.subTest(cid=cid):
    g=self.game();g.players[0].deck=[];self.play(g,cid)
 def test_one_cost_minions_drawn_and_other_card_retained(self):
  g=self.game();p=g.players[0];p.deck=['CORE_CS2_029','CORE_CS2_188','CORE_CS2_188']
  self.play(g,'UNG_913');self.assertEqual(p.deck,['CORE_CS2_029']);self.assertEqual([c.card_id for c in p.hand],['CORE_CS2_188']*2)
 def test_weapon_destroy_and_draw_original_durability(self):
  g=self.game();p,q=g.players;p.deck=['CORE_CS2_188']*5
  q.weapon={'card_id':'CORE_CS2_106','attack':3,'durability':2}
  self.play(g,'EX1_558');self.assertIsNone(q.weapon);self.assertEqual(len(p.hand),2);self.assertEqual(len(p.deck),3)
 def test_weapon_attack_becomes_armor(self):
  g=self.game();g.players[1].weapon={'card_id':'CORE_CS2_106','attack':7,'durability':2}
  self.play(g,'UNG_946');self.assertEqual(g.players[0].armor,7);self.assertIsNone(g.players[1].weapon)
 def test_both_players_lose_crystal(self):
  g=self.game();self.play(g,'DMF_115');self.assertEqual([p.max_mana for p in g.players],[9,9])
 def test_damaged_destruction_preserves_healthy_minions(self):
  g=self.game();healthy=g._summon(0,'CORE_EX1_043');hurt=g._summon(1,'CORE_EX1_043');hurt.health-=1
  self.play(g,'UNG_933');self.assertIn(healthy,g.players[0].minions);self.assertNotIn(hurt,g.players[1].minions)
 def test_tribe_target_filter_and_no_target_fallback(self):
  g=self.game();beast=g._summon(1,'CORE_EX1_162');other=g._summon(1,'CORE_CS2_188')
  self.assertEqual(g._targets_for('GVG_120',0),[beast.uid]);self.play(g,'GVG_120',beast.uid);self.assertIn(other,g.players[1].minions)
if __name__=='__main__':unittest.main()
