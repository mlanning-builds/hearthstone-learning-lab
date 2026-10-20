import sys,gzip,json,unittest
from pathlib import Path
sys.path.insert(0,'.');sys.path.insert(0,'tests')
import test_expanded_generation as fixtures
from expanded import cards,Action
class HistoricalStatPrimitiveTests(unittest.TestCase):
 def game(self):
  return fixtures.GenerationTests().game()
 def play(self,g,cid,target=0):
  c=g._add(0,cid);g.players[0].mana=10;cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  self.assertEqual(g.players[0].mana,10-cost);g.assert_invariants()
 def test_kooky_swaps_current_health_with_attack_on_either_side(self):
  for owner in (0,1):
   g=self.game();m=g._summon(owner,'CS2_182');g._buff(m,1,3);m.health-=2;a,h=m.attack,m.health
   self.play(g,'CFM_063',m.uid);self.assertEqual((m.attack,m.health,m.max_health),(h,a,a))
 def test_dwarf_attack_bonus_expires_at_current_turn_end(self):
  for owner in (0,1):
   g=self.game();m=g._summon(owner,'CS2_182');g._buff(m,1,3);a,h=m.attack,m.health
   self.play(g,'EX1_046',m.uid);self.assertEqual((m.attack,m.health),(a+2,h))
   g.step(Action('end'));self.assertEqual((m.attack,m.health),(a,h))
 def test_bite_attack_expires_but_armor_remains(self):
  g=self.game();self.play(g,'EX1_570');self.assertEqual((g._hero_attack(0),g.players[0].armor),(4,4))
  g.step(Action('end'));self.assertEqual((g._hero_attack(0),g.players[0].armor),(0,4))
 def test_no_target_minion_battlecries_still_complete(self):
  for cid in ('CFM_063','EX1_046'):
   g=self.game();self.play(g,cid);self.assertEqual(g.players[0].minions[0].card_id,cid)

if __name__=="__main__":unittest.main()
