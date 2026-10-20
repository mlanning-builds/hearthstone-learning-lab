"""Physical zone ownership and action rollback survive component extraction."""
from copy import deepcopy
import unittest
import test_expanded_choice_continuation as fixtures
from engine.game import Card
from engine.cards import UnsupportedCard


class ZoneManagerTests(unittest.TestCase):
    def test_cloned_draw_preserves_physical_card_without_touching_original(self):
        game = fixtures.ChoiceContinuationTests().game()
        card = Card(game._new_id(), 'CORE_CS2_029')
        card.cost_delta = -2
        game.players[0].deck = [card]
        clone = deepcopy(game)
        drawn = clone._draw(0)
        self.assertIs(drawn, clone.players[0].hand[-1])
        self.assertEqual(drawn.uid, card.uid)
        self.assertEqual(drawn.cost_delta, -2)
        self.assertIsNot(drawn, card)
        self.assertEqual(game.players[0].deck, [card])
        self.assertEqual(game.players[0].hand, [])
        self.assertEqual(clone.players[0].deck, [])

    def test_failed_continuation_rolls_back_draw_and_summon(self):
        game = fixtures.ChoiceContinuationTests().game()
        game._start_play_effects([
            ('choose_fixed_summon', ('EDR_851t',)),
            ('draw', 1), ('unsupported_zone_fixture',)],
            dict(owner=0, source=None, target=0, bonus=0, lifesteal=False))
        before = deepcopy(game.observe(0))
        rng = game.rng.getstate()
        deck = deepcopy(game.players[0].deck)
        with self.assertRaises(UnsupportedCard):
            game.step(game.legal_actions()[0])
        self.assertEqual(game.observe(0), before)
        self.assertEqual(game.players[0].deck, deck)
        self.assertEqual(game.players[0].hand, [])
        self.assertEqual(game.players[0].board, [])
        self.assertEqual(game.rng.getstate(), rng)
        self.assertEqual(game.pending_frame.next_operation, 1)
