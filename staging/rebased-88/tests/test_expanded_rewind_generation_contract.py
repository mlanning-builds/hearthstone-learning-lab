"""Production binding contract and corrected Rewind generation membership."""
import unittest
from expanded import reviewed_rewind_bindings as bindings
from expanded import rewind_generators as rewind
from expanded.generation_catalog import load_universe
from expanded.generation_cards import pool,board_pool
from expanded.pools import GenerationPool
from engine.cards import UnsupportedCard
import test_expanded_generation as fixtures

class RewindGenerationContractTests(unittest.TestCase):
 def test_twenty_one_frozen_roots_have_full_separate_hooks(self):
  self.assertEqual(len(bindings.COLLECTIBLE_IDS),22)
  self.assertLessEqual(bindings.COLLECTIBLE_IDS,load_universe().records.keys())
  for cid in bindings.COLLECTIBLE_IDS:
   if not bindings.RULES[cid][1]:
    self.assertIn(cid,set(bindings.DEATH_EFFECTS)|set(bindings.TRIGGERS)|set(bindings.LOCATION_EFFECTS))
 def test_tripwire_exact_cast_when_drawn_binding(self):
  self.assertEqual(bindings.TOKEN_IDS,frozenset(('JAIL_879t',)))
  self.assertEqual(tuple(bindings.RULES['JAIL_879t'][1]),bindings.CAST_EFFECTS['JAIL_879t'])
 def test_mana_budget_excludes_colossals_before_rng(self):
  g=fixtures.GenerationTests().game()
  self.assertEqual(rewind.BUDGET_POOL.excluded_mechanic,'COLOSSAL')
  g._generation_pools={(rewind.BUDGET_POOL,g.players[0].hero_class):
    GenerationPool('invalid fixture',('TSC_030',),'Deliberately ineligible Colossal')}
  before=g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'ineligible'):
   g._rewindgen_split(('rewindgen_budget',12,0),dict(owner=0,source=None))
  self.assertEqual(g.rng.getstate(),before)
  self.assertFalse(g.players[0].board)
 def test_holy_generation_cannot_generate_its_own_creator(self):
  g=fixtures.GenerationTests().game()
  g.cards['TIME_018']=dict(load_universe().records['TIME_018'])
  g._generation_pools={(rewind.HOLY,g.players[0].hero_class):
    GenerationPool('fixture',('TIME_018','CORE_CS2_004'),'Controlled identity exclusion')}
  ctx=dict(owner=0,card_id='TIME_018',source=None)
  first,tail=g._rewindgen_split(('rewindgen_holy',),ctx)
  self.assertEqual(first,('add','CORE_CS2_004',1))
  self.assertEqual(tail[0],('add','CORE_CS2_004',1))
