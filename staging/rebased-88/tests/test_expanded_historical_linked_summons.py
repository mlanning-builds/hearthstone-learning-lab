import unittest
import test_expanded_generation as fixtures
from expanded import cards
RECIPES={'BOT_420': (('EX1_tk9', 2),),
 'EX1_571': (('EX1_tk9', 3),),
 'CFM_310': (('CFM_310t', 4),),
 'WON_086': (('CFM_310t', 4),),
 'ICC_050': (('ICC_832t3', 2),),
 'ULD_713': (('ULD_430t', 7),),
 'EX1_248': (('EX1_tk11', 2),),
 'OG_273': (('CS2_101t', 5),),
 'UNG_960': (('CS2_101t', 2),)}

class LinkedSummonTests(unittest.TestCase):
 def test_generated_dependencies_keep_standard_deck_membership_closed(self):
  from expanded.historical_generation import validate_past_candidates
  roots=set(RECIPES);children={child for recipe in RECIPES.values() for child,n in recipe}
  self.assertFalse((roots|children)&cards.COLLECTIBLE_IDS)
  self.assertTrue((roots|children)<=cards.PLAYABLE_TOKENS)
  records=cards.registry();validate_past_candidates(roots,records)

 def game(self):
  return fixtures.GenerationTests().game()
 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10;cost=g._cost(c,0);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(g.players[0].mana,10-cost);g.assert_invariants()
 def test_exact_linked_tokens_and_printed_stats(self):
  for cid,recipe in RECIPES.items():
   g=self.game();self.play(g,cid);self.assertEqual([m.card_id for m in g.players[0].minions],[child for child,n in recipe for _ in range(n)]);self.assertEqual(g.players[0].overload_next,g.cards[cid].get('overload',0));self.assertEqual(len({m.uid for m in g.players[0].minions}),sum(n for c,n in recipe))
   for m in g.players[0].minions:self.assertEqual((m.attack,m.health),(g.cards[m.card_id]['attack'],g.cards[m.card_id]['health']))
 def test_one_slot_keeps_exact_first_token(self):
  for cid,recipe in RECIPES.items():
   g=self.game()
   for _ in range(6):g._summon(0,'CS2_182')
   self.play(g,cid);self.assertEqual(len(g.players[0].minions),7);self.assertEqual(g.players[0].minions[-1].card_id,recipe[0][0])
 def test_arbor_up_summons_distinct_treant_identity_then_buffs_existing_and_new(self):
  g=self.game();old=g._summon(0,'CS2_182');self.play(g,'YOP_026');self.assertEqual((old.attack,old.health),(6,6));self.assertEqual([(m.card_id,m.attack,m.health) for m in g.players[0].minions if m is not old],[('DMF_061t2',4,3)]*2)
 def test_arbor_up_full_board_still_buffs_existing_minions(self):
  g=self.game()
  for _ in range(7):g._summon(0,'CS2_182')
  before=[m.uid for m in g.players[0].minions];self.play(g,'YOP_026');self.assertEqual([m.uid for m in g.players[0].minions],before);self.assertTrue(all((m.attack,m.health)==(6,6) for m in g.players[0].minions))
 def test_poisonous_spider_kills_larger_target_after_positive_damage(self):
  g=self.game();self.play(g,'ICC_050');spider=g.players[0].minions[0];enemy=g._summon(1,'CS2_182');g._buff(enemy,0,20);spider.summoned_turn=g.turn-1;g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==spider.uid and a.target==enemy.uid));self.assertNotIn(enemy,g.players[1].minions)
 def test_locusts_have_rush_without_immediate_hero_attacks(self):
  g=self.game();enemy=g._summon(1,'CS2_182');self.play(g,'ULD_713')
  for m in g.players[0].minions:
   actions=[a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid];self.assertTrue(any(a.target==enemy.uid for a in actions));self.assertFalse(any(a.target==g.hero_id(1) for a in actions))

if __name__=="__main__":unittest.main()
