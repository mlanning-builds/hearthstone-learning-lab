import unittest
import test_expanded_historical_death as fixtures
from expanded import cards,Action,dependencies
ROOTS={'EX1_577': ('EX1_finkle', 1), 'TRL_363': ('TRL_363t', 1)}

class OpponentDeathTests(unittest.TestCase):
 def game(self):
  return fixtures.HistoricalDeathTests().game()
 def kill(self,g,m):m.health=0;g._settle();g.assert_invariants()
 def test_printed_child_belongs_to_other_controller_and_appends_after_existing_board(self):
  for cid,(child,n) in ROOTS.items():
   for owner in (0,1):
    g=self.game();left=g._summon(1-owner,'CS2_182');m=g._summon(owner,cid);self.kill(g,m)
    self.assertFalse(g.players[owner].board);self.assertEqual([x.card_id for x in g.players[1-owner].minions],['CS2_182',child]);new=g.players[1-owner].minions[1];self.assertEqual(new.owner,1-owner);self.assertEqual((new.attack,new.health),(g.cards[child]['attack'],g.cards[child]['health']));self.assertNotEqual(new.uid,m.uid)
 def test_enemy_full_board_does_not_use_source_freed_friendly_slot(self):
  for cid in ROOTS:
   g=self.game()
   for _ in range(7):g._summon(1,'CS2_182')
   before=[m.uid for m in g.players[1].minions];m=g._summon(0,cid);self.kill(g,m);self.assertEqual([m.uid for m in g.players[1].minions],before);self.assertFalse(g.players[0].board)
 def test_silenced_source_gives_no_opponent_body(self):
  for cid in ROOTS:
   g=self.game();m=g._summon(0,cid);g._silence(m);self.kill(g,m);self.assertFalse(g.players[1].board)
 def test_taskmaster_child_taunt_blocks_original_owners_hero_attack(self):
  g=self.game();attacker=g._summon(0,'CS2_182');attacker.summoned_turn=g.turn-1;m=g._summon(0,'TRL_363');self.kill(g,m);child=g.players[1].minions[0];acts=[a for a in g.legal_actions() if a.kind=='attack' and a.source==attacker.uid];self.assertTrue(any(a.target==child.uid for a in acts));self.assertFalse(any(a.target==g.hero_id(1) for a in acts))
 def test_dependency_scan_accounts_for_opponent_summon_identity(self):
  self.assertEqual(dependencies.literal_dependencies([('armor',10),('summon_opponent','TIME_873t',2)]),{'TIME_873t'})

if __name__=="__main__":unittest.main()
