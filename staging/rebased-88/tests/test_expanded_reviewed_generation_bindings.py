"""Explicit bindings retain full hooks and do not replace closure checks."""
import unittest
from expanded import reviewed_generation_bindings as bindings
from expanded.generation_catalog import load_universe
from expanded.generation_cards import pool
from engine.cards import UnsupportedCard
import test_expanded_generation as fixtures

class ReviewedGenerationBindingTests(unittest.TestCase):
    def test_explicit_frozen_standard_roots(self):
        self.assertEqual(len(bindings.COLLECTIBLE_IDS),137)
        self.assertLessEqual(bindings.COLLECTIBLE_IDS,load_universe().records.keys())
        self.assertNotIn('END_027',bindings.COLLECTIBLE_IDS)

    def test_empty_play_rule_has_real_separate_hook(self):
        hooked={'EDR_781'}|set(bindings.DEATH_EFFECTS)|set(bindings.END_EFFECTS)|set(bindings.TRIGGERS)|set(bindings.CHOICES)|set(bindings.WEAPON_TRIGGERS)|set(bindings.LOCATION_EFFECTS)
        for cid in bindings.COLLECTIBLE_IDS:
            with self.subTest(card=cid):
                if not bindings.RULES[cid][1]:self.assertIn(cid,hooked)

    def test_webspinner_has_exact_death_dependency(self):
        self.assertEqual(bindings.TOKEN_IDS,frozenset(('FP1_011','EDR_461t')))
        self.assertTrue(bindings.RULES['EDR_461t'][1])
        self.assertEqual(bindings.RULES['CORE_AT_062'][1],[('summon','FP1_011',3)])
        self.assertTrue(bindings.DEATH_EFFECTS['FP1_011'])

    def test_binding_does_not_approve_incomplete_pool(self):
        game=fixtures.GenerationTests().game()
        del game.cards['CORE_EX1_162']
        before=game.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'eligible effects not implemented'):
            game._generation_candidates(pool(),0)
        self.assertEqual(game.rng.getstate(),before)
