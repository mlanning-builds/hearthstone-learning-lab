"""Real Gelbin bundle, physical deck Aura placement and paid companions."""
import unittest
from expanded import Action,cards
from expanded.gelbin import AURA_IDS,AURA_RULES
from expanded.generation_catalog import load_universe
import test_expanded_imbue_azure_admission as fixtures
class GelbinAdmissionTests(unittest.TestCase):
 def test_all_frozen_standard_auras_have_placement_rules(self):
  standard=set(load_universe().records)
  self.assertFalse((AURA_IDS&standard)-set(AURA_RULES))
 def test_native_bundle_places_physical_auras_without_paid_casts(self):
  fx=fixtures.ImbueAzureAdmissionTests();g=fx.game('PALADIN','TIME_009');p=g.players[0]
  self.assertTrue({'TIME_009','TIME_009t1','TIME_009t2'}<=set(p.starting_deck))
  p.deck=[g._add(0,'TIME_009t1'),g._add(0,'TIME_009t2')];p.hand=[]
  fx.play(g,'TIME_009');self.assertFalse(p.deck);self.assertEqual(len(p.scheduled_effects),2)
  self.assertFalse(p.spells_turn);self.assertEqual([e['card_id'] for e in p.played_history],['TIME_009'])
  p.health=10;g.step(Action('end'));self.assertEqual(p.health,14)
  self.assertIn('DIVINE_SHIELD',p.minions[0].keywords);g.assert_invariants()
 def test_native_companion_paid_spell_and_trade_are_distinct(self):
  fx=fixtures.ImbueAzureAdmissionTests();g=fx.game('PALADIN','TIME_009');p=g.players[0]
  fx.play(g,'TIME_009t1');self.assertEqual(len(p.scheduled_effects),1)
  c=g._add(0,'TIME_009t2');p.mana=10;p.deck=['CORE_CS2_188']
  g.step(next(a for a in g.legal_actions() if a.kind=='trade' and a.source==c.uid))
  self.assertEqual(p.mana,9);self.assertEqual(len(p.scheduled_effects),1);g.assert_invariants()
