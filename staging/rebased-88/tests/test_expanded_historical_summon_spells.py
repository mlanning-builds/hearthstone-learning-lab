import unittest
import test_expanded_generation as fixtures
from expanded import cards
from expanded.historical_numeric import FIXED_SUMMONS,FIXED_TOKEN_IDS

class HistoricalSummonSpellTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid):
  p=g.players[0];p.mana=10;c=g._add(0,cid);before=p.mana;cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(p.mana,before-cost);self.assertNotIn(c,p.hand);g.assert_invariants()
 def test_exact_fixed_recipes_and_fresh_entities(self):
  for cid,recipe in FIXED_SUMMONS.items():
   with self.subTest(cid=cid):
    g=self.game();self.play(g,cid);expected=[child for child,count in recipe for _ in range(count)]
    self.assertEqual([m.card_id for m in g.players[0].minions],expected)
    self.assertEqual(len({m.uid for m in g.players[0].minions}),len(expected))
    for m in g.players[0].minions:
     record=g.cards[m.card_id];self.assertEqual((m.attack,m.health),(record['attack'],record['health']))
 def test_one_free_slot_keeps_first_printed_outcome(self):
  for cid,recipe in FIXED_SUMMONS.items():
   with self.subTest(cid=cid):
    g=self.game()
    for _ in range(6):g._summon(0,'CS2_182')
    self.play(g,cid);self.assertEqual(len(g.players[0].board),7)
    self.assertEqual(g.players[0].board[-1].card_id,recipe[0][0])
 def test_full_board_still_consumes_spell_once(self):
  for cid in FIXED_SUMMONS:
   with self.subTest(cid=cid):
    g=self.game()
    for _ in range(7):g._summon(0,'CS2_182')
    original=[m.uid for m in g.players[0].board];self.play(g,cid)
    self.assertEqual([m.uid for m in g.players[0].board],original)
 def test_tokens_are_registered_generated_only(self):
  r=cards.registry();self.assertTrue(FIXED_TOKEN_IDS<=r.keys())
  self.assertTrue(FIXED_TOKEN_IDS<=cards.PLAYABLE_TOKENS)
  self.assertFalse((set(FIXED_SUMMONS)|FIXED_TOKEN_IDS)&cards.COLLECTIBLE_IDS)
 def test_lifesteal_tokens_heal_after_dealing_damage(self):
  for cid in ('BAR_327','DAL_733'):
   with self.subTest(cid=cid):
    g=self.game();g.players[0].health=20;self.play(g,cid);m=g.players[0].minions[0]
    self.assertIn('LIFESTEAL',m.keywords)
    m.summoned_turn=g.turn-1
    g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid and a.target==g.hero_id(1)))
    self.assertEqual(g.players[0].health,20+m.attack)
 def test_rush_can_attack_minions_but_not_hero_on_entry(self):
  for cid in ('BT_036','BT_173'):
   with self.subTest(cid=cid):
    g=self.game();enemy=g._summon(1,'CS2_182');self.play(g,cid)
    for m in g.players[0].minions:
     attacks=[a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid]
     self.assertTrue(any(a.target==enemy.uid for a in attacks))
     self.assertFalse(any(a.target==g.hero_id(1) for a in attacks))
 def test_printed_taunt_and_stealth_survive_summon(self):
  for cid,keyword in (('BAR_533','TAUNT'),('CS2_027','TAUNT'),('TSC_076','TAUNT'),('WW_806','STEALTH')):
   with self.subTest(cid=cid):
    g=self.game();self.play(g,cid)
    self.assertTrue(all(keyword in m.keywords for m in g.players[0].minions))
