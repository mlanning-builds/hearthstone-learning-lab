"""Effect context cleanup and host ownership survive composed execution."""
from copy import deepcopy
import unittest
import test_expanded_choice_continuation as fixtures
from engine.cards import UnsupportedCard


class EffectExecutorTests(unittest.TestCase):
    def test_failed_effect_restores_outer_context_and_damage_origin(self):
        game = fixtures.ChoiceContinuationTests().game()
        outer = dict(owner=1, source=None)
        marker = object()
        game._active_effect_context = outer
        game._damage_origin = marker
        with self.assertRaises(UnsupportedCard):
            game._effect(('unsupported_executor_fixture',), dict(owner=0, source=None))
        self.assertIs(game._active_effect_context, outer)
        self.assertIs(game._damage_origin, marker)
        self.assertFalse(hasattr(game, '_healing_replacement_frame'))

    def test_clone_executes_effects_only_on_its_own_host(self):
        game = fixtures.ChoiceContinuationTests().game()
        clone = deepcopy(game)
        clone._effect(('armor', 3), dict(owner=0, source=None))
        self.assertEqual(clone.players[0].armor, 3)
        self.assertEqual(game.players[0].armor, 0)
        game._effect(('armor', 3), dict(owner=0, source=None))
        self.assertEqual(game.observe(0), clone.observe(0))

    def test_destroy_departed_target_finishes_remaining_effects(self):
        game = fixtures.ChoiceContinuationTests().game()
        game._summon(1, 'CORE_CS2_179')
        victim = game.players[1].minions[0]
        game.players[1].board.remove(victim)
        game._start_play_effects([('destroy',), ('armor', 3)],
                                dict(owner=0, source=None, target=victim.uid,
                                     bonus=0, lifesteal=False))
        self.assertEqual(game.players[0].armor, 3)
        self.assertIsNone(game.pending_frame)

    def test_destroy_live_target_and_zero_target(self):
        game = fixtures.ChoiceContinuationTests().game()
        game._summon(1, 'CORE_CS2_179')
        victim = game.players[1].minions[0]
        game._effect(('destroy',), dict(owner=0, source=None, target=0))
        self.assertGreater(victim.health, 0)
        game._effect(('destroy',), dict(owner=0, source=None, target=victim.uid))
        self.assertEqual(victim.health, 0)
