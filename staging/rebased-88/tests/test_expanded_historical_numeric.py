import unittest
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.historical_numeric import GENERATED_IDS
from expanded.historical_generation import validate_past_candidates

class HistoricalNumericTests(unittest.TestCase):
 def game(self):
  g=fixtures.GenerationTests().game()
  for p in g.players:p.mana_capacity=p.mana=p.max_mana=10;p.overload_next=p.locked_mana=0
  g._summon(0,'CS2_182');g._summon(1,'CS2_182')
  return g
 def play(self,g,cid,target=0):
  c=g._add(0,cid);cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  self.assertEqual(g.players[0].last_paid_cost,cost)
 def test_all_nineteen_identities_complete_paid_play(self):
  self.assertEqual(len(GENERATED_IDS),19)
  for cid in sorted(GENERATED_IDS):
   with self.subTest(cid=cid):
    g=self.game();c=g._add(0,cid);cost=g._cost(c,0)
    g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    self.assertEqual(g.players[0].last_paid_cost,cost);g.assert_invariants()
 def test_generated_only_registry_excludes_standard_decks(self):
  self.assertTrue(GENERATED_IDS<=cards.TOKEN_IDS)
  self.assertFalse(GENERATED_IDS&cards.COLLECTIBLE_IDS)
  validate_past_candidates(GENERATED_IDS,cards.registry())
 def test_pyroblast_spell_damage_and_kraken_battlecry_differ(self):
  g=self.game();g._summon(0,'CORE_EX1_012');self.play(g,'EX1_279',g.hero_id(1))
  self.assertEqual(g.players[1].health,19)
  g=self.game();g._summon(0,'CORE_EX1_012');self.play(g,'AT_103',g.hero_id(1))
  self.assertEqual(g.players[1].health,26)
 def test_healing_touch_and_zero_cost_regenerate_cap_at_maximum(self):
  for cid,damage,health in [('CS2_007',10,28),('TRL_128',2,30)]:
   g=self.game();g.players[0].health=30-damage
   self.play(g,cid,g.hero_id(0));self.assertEqual(g.players[0].health,health)
 def test_sprint_draws_four_and_inventor_draws_one(self):
  for cid,count in [('CS2_077',4),('CS2_147',1)]:
   g=self.game();p=g.players[0];p.hand=[];before=len(p.deck)
   self.play(g,cid);self.assertEqual(len(p.deck),before-count);self.assertEqual(len(p.hand),count)
 def test_power_infusion_and_divine_strength_buff_printed_amount(self):
  for cid,expected in [('EX1_194',(2,6)),('OG_223',(1,2))]:
   g=self.game();m=g.players[0].minions[0];a,h=m.attack,m.max_health
   self.play(g,cid,m.uid);self.assertEqual((m.attack-a,m.max_health-h),expected)
 def test_iron_hide_and_shieldmaiden_grant_five_armor(self):
  for cid in ('UNG_923','GVG_053'):
   g=self.game();self.play(g,cid);self.assertEqual(g.players[0].armor,5)
