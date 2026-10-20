import sys,unittest
sys.path.insert(0,'.');sys.path.insert(0,'tests')
import test_expanded_generation as fixtures
class HistoricalHealingTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid,target=0):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  g.assert_invariants()
 def test_all_friendly_heal_leaves_opponents_damaged(self):
  for cid in ('DAL_544','DS1_055','LOOT_388'):
   with self.subTest(cid=cid):
    g=self.game();g.players[0].health=20;g.players[1].health=20
    a=g._summon(0,'CS2_182');b=g._summon(1,'CS2_182');a.health-=2;b.health-=2
    self.play(g,cid);self.assertEqual(g.players[0].health,22);self.assertEqual(g.players[1].health,20)
    self.assertEqual(a.health,a.max_health);self.assertEqual(b.health,b.max_health-2)
 def test_target_heals_both_sides_and_overload(self):
  for cid,amount in (('CFM_061',6),('DAL_078',3),('UNG_938',3)):
   for owner in (0,1):
    with self.subTest(cid=cid,owner=owner):
     g=self.game();g.players[owner].health=10
     self.play(g,cid,g.hero_id(owner));self.assertEqual(g.players[owner].health,10+amount)
     self.assertEqual(g.players[0].overload_next,1 if cid=='CFM_061' else 0)
 def test_priestess_heals_own_hero_and_has_taunt(self):
  g=self.game();g.players[0].health=20;self.play(g,'CS2_088')
  self.assertEqual(g.players[0].health,26);self.assertIn('TAUNT',g._effective_keywords(g.players[0].minions[-1]))
 def test_crystallizer_damage_precedes_armor(self):
  g=self.game();g.players[0].health=20;g.players[0].armor=0;self.play(g,'BOT_447')
  self.assertEqual((g.players[0].health,g.players[0].armor),(15,5))
 def test_kobold_draws_then_hurts_hero(self):
  g=self.game();g.players[0].deck=['CS2_182'];g.players[0].health=20;self.play(g,'LOOT_014')
  self.assertEqual(g.players[0].health,18);self.assertEqual(g.players[0].hand[-1].card_id,'CS2_182')
if __name__=='__main__':unittest.main()
