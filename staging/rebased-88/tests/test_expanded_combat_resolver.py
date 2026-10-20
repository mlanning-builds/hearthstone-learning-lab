"""Combat components preserve game-owned nesting and attack-window cleanup."""
import unittest
from unittest.mock import patch
import test_expanded_forced_combat as fixtures


class CombatResolverTests(unittest.TestCase):
    def setUp(self):
        self.game = fixtures.ForcedCombatTests().game()
        self.attacker = self.game._summon(0, 'CORE_CS2_189')
        self.defender = self.game._summon(1, 'CORE_CS2_189')

    def test_attack_preserves_outer_combat_depth(self):
        self.game._combat_sequence_depth = 4
        observed = []
        with patch.object(self.game, '_resolve_combat', side_effect=lambda *a, **k: observed.append(self.game._combat_sequence_depth)):
            self.game._attack(self.attacker.uid, self.defender.uid)
        self.assertEqual(observed, [5])
        self.assertEqual(self.game._combat_sequence_depth, 4)
        self.assertEqual(self.game._attack_windows, [])

    def test_failed_combat_closes_window_and_restores_depth(self):
        self.game._combat_sequence_depth = 2
        with patch.object(self.game, '_resolve_combat', side_effect=RuntimeError('combat failure')):
            with self.assertRaisesRegex(RuntimeError, 'combat failure'):
                self.game._attack(self.attacker.uid, self.defender.uid)
        self.assertEqual(self.game._combat_sequence_depth, 2)
        self.assertEqual(self.game._attack_windows, [])
