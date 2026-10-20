import unittest
import test_expanded_generation as fixtures
from expanded import cards,Action
RECIPES={'GIL_191':(('GIL_191t',4),),'RLK_544':(('RLK_544t',2),),'TID_005':(('TID_005t',2),),'TRL_351':(('TRL_351t',3),),'YOD_041':(('YOD_041t',3),)}

class MoreSummonTests(unittest.TestCase):
 def game(self):
  return fixtures.GenerationTests().game()
 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10;cost=g._cost(c,0);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(g.players[0].mana,10-cost);g.assert_invariants()
 def test_fixed_summon_recipes_and_printed_overload(self):
  for cid,recipe in RECIPES.items():
   g=self.game();self.play(g,cid);self.assertEqual([m.card_id for m in g.players[0].minions],[child for child,n in recipe for _ in range(n)]);self.assertEqual(g.players[0].overload_next,g.cards[cid].get('overload',0))
   for m in g.players[0].minions:self.assertEqual((m.attack,m.health),(g.cards[m.card_id]['attack'],g.cards[m.card_id]['health']))
 def test_full_board_still_pays_and_locks_printed_overload(self):
  for cid in RECIPES:
   g=self.game()
   for _ in range(7):g._summon(0,'CS2_182')
   before=[m.uid for m in g.players[0].minions];self.play(g,cid);self.assertEqual([m.uid for m in g.players[0].minions],before);self.assertEqual(g.players[0].overload_next,g.cards[cid].get('overload',0))
 def test_elusive_golems_reject_targeted_enemy_spells(self):
  g=self.game();self.play(g,'RLK_544');target=g.players[0].minions[0];g.current=1;g.players[1].mana=10;c=g._add(1,'CS2_008');self.assertFalse(any(a.kind=='play' and a.source==c.uid and a.target==target.uid for a in g.legal_actions()));self.assertIn('TAUNT',target.keywords)
 def test_revenant_rush_cannot_attack_hero_on_entry(self):
  g=self.game();enemy=g._summon(1,'CS2_182');self.play(g,'TID_005')
  for m in g.players[0].minions:
   acts=[a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid];self.assertTrue(any(a.target==enemy.uid for a in acts));self.assertFalse(any(a.target==g.hero_id(1) for a in acts))

if __name__=="__main__":unittest.main()
