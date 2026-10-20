import unittest
from collections import Counter
import test_expanded_generation as fixtures
from expanded import cards,Action
from expanded.lost_city_rewards import REWARDS,TOKEN_IDS,PLAYABLE_IDS
from expanded.adapt import ADAPTATIONS
from expanded.quest_families import MURLOCS

class LostCityRegistryTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid):
  p=g.players[0];p.mana=10;c=g._add(0,cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  count=0
  while g.pending_choice:
   g.step(Action('choose',choices=(0,)));count+=1
   self.assertLessEqual(count,5)
  g.assert_invariants();return count
 def test_recipe_is_complete_and_generated_only(self):
  records=cards.registry();self.assertTrue(TOKEN_IDS<=records.keys())
  self.assertFalse(TOKEN_IDS&cards.COLLECTIBLE_IDS)
  self.assertTrue(PLAYABLE_IDS<=cards.PLAYABLE_TOKENS)
  self.assertTrue(PLAYABLE_IDS<=cards.RULES.keys())
  self.assertIn('TLC_602',cards.COLLECTIBLE_IDS)
 def test_adapt_choices_are_ui_records_without_paid_card_bodies(self):
  self.assertFalse(set(ADAPTATIONS)&PLAYABLE_IDS)
  self.assertFalse(set(ADAPTATIONS)&cards.COLLECTIBLE_IDS)
 def test_all_nine_rewards_complete_ordinary_paid_play(self):
  for cid in REWARDS:
   with self.subTest(cid=cid):
    g=self.game();count=self.play(g,cid)
    self.assertEqual(count,5 if cid=='UNG_954t1' else 0)
    self.assertEqual(g.players[0].last_paid_cost,g.cards[cid]['cost'])
 def test_latorvius_partitions_all_nine_physical_rewards(self):
  g=self.game();p=g.players[0];p.deck=[];self.play(g,'TLC_602t')
  self.assertEqual(len(p.hand),2);self.assertEqual(len(p.deck),7)
  self.assertEqual(Counter(c.card_id for c in p.hand+p.deck),Counter(REWARDS))
  self.assertEqual(len({c.uid for c in p.hand+p.deck}),9)
 def test_megafin_uses_complete_production_pool(self):
  g=self.game();expected=set(g._generation_candidates(MURLOCS,0))
  self.assertGreater(len(expected),1);self.play(g,'UNG_942t')
  self.assertEqual(len(g.players[0].hand),10)
  self.assertTrue({c.card_id for c in g.players[0].hand}<=expected)
 def test_portal_and_imps_use_registered_printed_identities(self):
  g=self.game();self.play(g,'UNG_829t1');g.step(Action('end'))
  self.assertEqual([entity.card_id for entity in g.players[0].board],['UNG_829t3','UNG_829t2','UNG_829t3'])
 def test_sulfuras_power_remains_after_weapon_break(self):
  g=self.game();self.play(g,'UNG_934t1');g._break_weapon(0)
  self.assertEqual(g.players[0].primary_power['card_id'],'UNG_934t2')
  before=g.players[1].health;g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='power'))
  self.assertEqual(g.players[1].health,before-8)
 def test_carnassa_brood_has_twenty_distinct_cards(self):
  g=self.game();g.players[0].deck=[];self.play(g,'UNG_920t1')
  brood=g.players[0].deck;self.assertEqual(len(brood),20)
  self.assertEqual({c.card_id for c in brood},{'UNG_920t2'})
  self.assertEqual(len({c.uid for c in brood}),20)
