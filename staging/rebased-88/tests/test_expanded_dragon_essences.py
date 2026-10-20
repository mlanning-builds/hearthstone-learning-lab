import unittest
import test_expanded_generation as fixtures
from expanded import cards,dragon_soul
from engine.game import Card
TOKENS=(*dragon_soul.ESSENCES,dragon_soul.ROOT+'t6t')
class DragonEssenceTests(unittest.TestCase):
 def game(self):
  return fixtures.GenerationTests().game()
 def add(self,g,*ids):return [g._add(0,cid) for cid in ids]
 def play(self,g,c):
  g.players[0].mana=10;cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (c.card_id!=TOKENS[0] or a.target==g.hero_id(1))))
  self.assertEqual(g.players[0].mana,10-cost if c.card_id!=TOKENS[2] else 10)
  g.assert_invariants()
 def test_fixed_dependencies_are_generated_only_and_root_is_constructible(self):
  self.assertTrue(dragon_soul.TOKEN_IDS<=cards.PLAYABLE_TOKENS)
  self.assertFalse(dragon_soul.TOKEN_IDS&cards.COLLECTIBLE_IDS)
  self.assertIn(dragon_soul.ROOT,cards.RULES)
  self.assertIn(dragon_soul.ROOT,cards.COLLECTIBLE_IDS)
 def test_all_six_paid_essences_and_printed_dragon(self):
  for cid in TOKENS:
   with self.subTest(cid=cid):
    g=self.game();c=self.add(g,cid)[0];self.play(g,c)
    self.assertFalse(any(x.uid==c.uid for x in g.players[0].hand))
    if cid==TOKENS[-1]:self.assertEqual((g.players[0].minions[0].attack,g.players[0].minions[0].health),(8,8))
 def test_adjoining_fixed_chain_pays_only_selected_spell(self):
  g=self.game();a,b,c=self.add(g,TOKENS[3],TOKENS[0],TOKENS[4]);self.play(g,b)
  self.assertEqual((g.players[0].armor,g.players[1].health),(12,22));self.assertFalse(g.players[0].hand)
  self.assertEqual([m.card_id for m in g.players[0].minions],[TOKENS[-1]])
 def test_non_essence_is_a_contiguous_barrier(self):
  g=self.game();a,b,coin,c=self.add(g,TOKENS[3],TOKENS[0],'TOKEN_COIN',TOKENS[4]);self.play(g,b)
  self.assertEqual(g.players[0].armor,12);self.assertEqual([x.uid for x in g.players[0].hand],[coin.uid,c.uid]);self.assertFalse(g.players[0].board)
 def test_blue_draw_does_not_grow_the_captured_chain(self):
  g=self.game();g.players[0].deck=[Card(g._new_id(),TOKENS[3]) for _ in range(3)]
  blue,green=self.add(g,TOKENS[1],TOKENS[4]);self.play(g,blue)
  self.assertEqual([c.card_id for c in g.players[0].hand],[TOKENS[3]]*3)
  self.assertEqual(g.players[0].armor,0);self.assertEqual([m.card_id for m in g.players[0].minions],[TOKENS[-1]])
 def test_spell_damage_applies_to_each_damage_essence(self):
  g=self.game();g._summon(0,'CORE_EX1_012');enemy=g._summon(1,'CORE_EX1_162');enemy.health=enemy.max_health=10
  red,storm=self.add(g,TOKENS[0],TOKENS[5]);self.play(g,red)
  self.assertEqual(g.players[1].health,21);self.assertEqual(enemy.health,5)
 def test_countered_selected_spell_keeps_adjoining_essences(self):
  g=self.game();g._effect(('secret','CORE_EX1_287'),dict(owner=1,target=0,source=None))
  a,b,c=self.add(g,TOKENS[3],TOKENS[0],TOKENS[4]);self.play(g,b)
  self.assertEqual([x.uid for x in g.players[0].hand],[a.uid,c.uid]);self.assertEqual(g.players[0].armor,0);self.assertFalse(g.players[0].board)

 def test_real_opening_replaces_each_root_before_initial_draw(self):
  from test_expanded_fixed_standard_admission import FixedStandardAdmissionTests
  from expanded import Game
  helper=FixedStandardAdmissionTests();deck=helper.deck("WARRIOR",dragon_soul.ROOT)
  g=Game([deck,deck],seed=941)
  for p in g.players:
   actual=p.deck+p.hand
   self.assertEqual(len(p.starting_deck),30);self.assertIn(dragon_soul.ROOT,p.starting_deck)
   self.assertEqual(len(actual),35);self.assertFalse(any(c.card_id==dragon_soul.ROOT for c in actual))
   self.assertEqual(sorted(c.card_id for c in actual if c.card_id in dragon_soul.ESSENCES),sorted(dragon_soul.ESSENCES))
   self.assertEqual(len({c.uid for c in actual}),35)
 def test_generated_root_has_no_retroactive_start_of_game_effect(self):
  g=self.game();before=list(g.players[0].deck);c=self.add(g,dragon_soul.ROOT)[0];self.play(g,c)
  self.assertEqual(g.players[0].deck,before);self.assertFalse(g.players[0].hand)
 def test_repeated_setup_root_uses_separate_physical_essences(self):
  g=self.game();p=g.players[0];p.deck=[Card(g._new_id(),dragon_soul.ROOT),Card(g._new_id(),dragon_soul.ROOT)]
  g._essence_setup();self.assertEqual(len(p.deck),12);self.assertEqual(len({c.uid for c in p.deck}),12)
  self.assertTrue(all(sum(c.card_id==cid for c in p.deck)==2 for cid in dragon_soul.ESSENCES))

if __name__=="__main__":unittest.main()
