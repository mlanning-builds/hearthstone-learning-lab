import unittest
import test_expanded_historical_death as fixtures
from expanded import cards,Action,dependencies
ROOTS={'GDB_331': ('GDB_331t1', 2), 'GIL_616': ('GIL_616t', 2), 'RLK_650': ('RLK_650t', 1)}
NESTED={'GDB_331t1': ('GDB_331t2', 2),
 'GDB_331t2': ('GDB_331t3', 2),
 'GIL_616t': ('GIL_616t2', 2),
 'RLK_650t': ('RLK_650t2', 1)}

class NestedDeathTests(unittest.TestCase):
 def game(self):
  return fixtures.HistoricalDeathTests().game()
 def paid(self,g,cid):return fixtures.HistoricalDeathTests().paid(g,cid)
 def kill(self,g,m):m.health=0;g._settle();g.assert_invariants()
 def test_spacerock_resolves_two_full_generations_then_caps_pebbles_at_seven(self):
  g=self.game();m=self.paid(g,'GDB_331');self.kill(g,m);self.assertEqual([x.card_id for x in g.players[0].minions],['GDB_331t1']*2)
  for x in list(g.players[0].minions):x.health=0
  g._settle();self.assertEqual([x.card_id for x in g.players[0].minions],['GDB_331t2']*4)
  for x in list(g.players[0].minions):x.health=0
  g._settle();self.assertEqual([x.card_id for x in g.players[0].minions],['GDB_331t3']*7);g.assert_invariants()
 def test_festeroot_saplings_then_four_textless_woodchips(self):
  g=self.game();m=self.paid(g,'GIL_616');self.kill(g,m);self.assertEqual([x.card_id for x in g.players[0].minions],['GIL_616t']*2)
  for x in list(g.players[0].minions):self.kill(g,x)
  self.assertEqual([x.card_id for x in g.players[0].minions],['GIL_616t2']*4)
 def test_lingering_zombie_stops_after_final_unarmed_body(self):
  g=self.game();m=self.paid(g,'RLK_650');self.kill(g,m);first=g.players[0].minions[0];self.assertEqual(first.card_id,'RLK_650t');self.kill(g,first);final=g.players[0].minions[0];self.assertEqual(final.card_id,'RLK_650t2');self.assertNotEqual(final.uid,first.uid);self.kill(g,final);self.assertFalse(g.players[0].board)
 def test_silencing_intermediate_bodies_cancels_their_own_deathrattles(self):
  for cid in NESTED:
   g=self.game();m=self.paid(g,cid);g._silence(m);self.kill(g,m);self.assertFalse(g.players[0].board)
 def test_intermediate_tokens_can_be_paid_and_retain_exact_descendants(self):
  for cid,(child,n) in NESTED.items():
   g=self.game();m=self.paid(g,cid);self.kill(g,m);self.assertEqual([x.card_id for x in g.players[0].minions],[child]*n)
 def test_full_board_grants_only_one_descendant_from_each_stage(self):
  for cid,(child,n) in dict(ROOTS,**NESTED).items():
   g=self.game();m=self.paid(g,cid)
   for _ in range(6):g._summon(0,'CS2_182')
   self.kill(g,m);self.assertEqual(len(g.players[0].minions),7);self.assertEqual(sum(x.card_id==child for x in g.players[0].minions),1)

if __name__=="__main__":unittest.main()
