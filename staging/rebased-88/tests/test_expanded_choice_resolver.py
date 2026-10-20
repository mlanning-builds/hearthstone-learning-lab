"""Composed choice handling follows the host game across cloned continuations."""
from copy import deepcopy
import unittest
from expanded import Action
from engine.cards import UnsupportedCard
import test_expanded_choice_continuation as fixtures


class ChoiceResolverTests(unittest.TestCase):
    def test_cloned_pending_choice_resumes_only_its_own_game(self):
        fixture = fixtures.ChoiceContinuationTests()
        game = fixture.game()
        fixture.start(game)
        clone = deepcopy(game)
        clone.step(clone.legal_actions()[0])
        self.assertEqual(clone.players[0].armor, 3)
        self.assertIsNone(clone.pending_choice)
        self.assertEqual(game.players[0].armor, 0)
        self.assertIsNotNone(game.pending_choice)
        game.step(game.legal_actions()[0])
        self.assertEqual(game.observe(0), clone.observe(0))

    def test_unsupported_selection_rolls_back_pending_state(self):
        game = fixtures.ChoiceContinuationTests().game()
        game.pending_choice = dict(owner=0, kind='unsupported_fixture', options=[dict(card_id='EDR_851t')])
        game.phase = 'choice'
        before = deepcopy(game.pending_choice)
        rng = game.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard, 'Unknown choice kind'):
            game.step(Action('choose', choices=(0,)))
        self.assertEqual(game.pending_choice, before)
        self.assertEqual(game.phase, 'choice')
        self.assertEqual(game.rng.getstate(), rng)
