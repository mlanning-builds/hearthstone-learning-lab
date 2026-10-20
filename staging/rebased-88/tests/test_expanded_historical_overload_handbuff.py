import unittest
import test_expanded_generation as fixtures
from expanded import cards,Action

class OverloadHandBuffTests(unittest.TestCase):
 def game(self):
  return fixtures.GenerationTests().game()
 def play(self,g,cid,target=0):
  c=g._add(0,cid);g.players[0].mana=10;g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));g.assert_invariants()
 def test_lava_burst_spell_damage_and_printed_overload(self):
  g=self.game();g._summon(0,'CORE_EX1_012');self.play(g,'EX1_241',g.hero_id(1));self.assertEqual(g.players[1].health,24);self.assertEqual(g.players[0].overload_next,2);g.step(Action('end'));g.step(Action('end'));self.assertEqual(g.players[0].locked_mana,2)
 def test_arena_fanatic_only_buffs_minions_in_hand(self):
  g=self.game();m=g._add(0,'CS2_182');spell=g._add(0,'CS2_008');self.play(g,'TRL_517');self.assertEqual((m.attack_bonus,m.health_bonus),(1,1));self.assertEqual((spell.attack_bonus,spell.health_bonus),(0,0));body=next(x for x in g.players[0].minions if x.card_id=='TRL_517');self.assertEqual((body.attack,body.health),(g.cards['TRL_517']['attack'],g.cards['TRL_517']['health']))

if __name__=="__main__":unittest.main()
