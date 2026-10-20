import unittest
import test_expanded_historical_death as fixtures
from expanded import cards,Action

class NextDeathTests(unittest.TestCase):
 def game(self):
  return fixtures.HistoricalDeathTests().game()
 def paid(self,g,cid):return fixtures.HistoricalDeathTests().paid(g,cid)
 def kill(self,g,m):return fixtures.HistoricalDeathTests().kill(g,m)
 def test_legionnaire_only_buffs_surviving_minions_in_hand(self):
  for silence in (False,True):
   g=self.game();m=self.paid(g,'AV_130');hand=g._add(0,'CS2_182');spell=g._add(0,'CS2_008')
   if silence:g._silence(m)
   self.kill(g,m);self.assertEqual((hand.attack_bonus,hand.health_bonus),((0,0) if silence else (2,2)));self.assertEqual((spell.attack_bonus,spell.health_bonus),(0,0))
 def test_belcher_literal_child_preserves_death_position_and_taunt(self):
  g=self.game();left=g._summon(0,'CS2_182');m=self.paid(g,'WON_128');right=g._summon(0,'CS2_182');g.players[0].board[:]=[left,m,right];self.kill(g,m)
  self.assertEqual([x.card_id for x in g.players[0].minions],['CS2_182','FP1_012t','CS2_182']);child=g.players[0].minions[1];self.assertEqual((child.attack,child.health),(1,2));self.assertIn('TAUNT',child.keywords);self.assertNotEqual(child.uid,m.uid)
 def test_full_board_death_frees_one_slot_for_slime(self):
  g=self.game();m=self.paid(g,'WON_128')
  for _ in range(6):g._summon(0,'CS2_182')
  self.kill(g,m);self.assertEqual(len(g.players[0].minions),7);self.assertEqual(sum(x.card_id=='FP1_012t' for x in g.players[0].minions),1)
 def test_silenced_belcher_has_no_child(self):
  g=self.game();m=self.paid(g,'WON_128');g._silence(m);self.kill(g,m);self.assertFalse(g.players[0].board)

if __name__=="__main__":unittest.main()
