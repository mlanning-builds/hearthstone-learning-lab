"""Reviewed family schemas reject malformed rules before runtime conditions."""
import unittest
from expanded.effect_schema import EffectSchemaError, validate_operation, validate_namespace
from expanded.batch_effects import BatchEffects
from expanded import held_upgrade_cards, bonus_cards, historical_hand_primitives, historical_conditional_battlecries, historical_scaling


class FamilySchemaTests(unittest.TestCase):
    def test_reviewed_family_declarations_have_strict_coverage(self):
        for module in (held_upgrade_cards, bonus_cards, historical_hand_primitives, historical_conditional_battlecries, historical_scaling):
            with self.subTest(module=module.__name__):
                reports = validate_namespace(vars(module), strict_unknown=True)
                self.assertTrue(reports)
                self.assertFalse(set().union(*(r.uncovered for r in reports.values())))

    def test_held_and_bonus_operand_types_and_arity(self):
        for op in (('held_draw', 1), ('held_tick', True, 'fixture'), ('bonus_target', False), ('bonus_summon', 1), ('historical_hand_buff', None, None, 1, 2, 1), ('historical_self_scale', 'invented', 1, 1)):
            with self.subTest(op=op), self.assertRaises(EffectSchemaError):
                validate_operation(op)

    def test_nested_holding_else_and_combo_are_validated(self):
        for op in (('if_holding', (), ('draw', 1), ('bonus_target', True)), ('historical_if_combo', ('held_draw', 1)), ('if_holding', (), ('armor', 1), ('draw', 1), ('draw', 1))):
            with self.subTest(op=op), self.assertRaises(EffectSchemaError):
                validate_operation(op)
        report = validate_operation(('if_holding', (('tribe', 'eq', 'DRAGON'),), ('armor', 1), ('draw', 1)), strict_unknown=True)
        self.assertEqual(report.operations, 3)

    def test_filter_contract_matches_runtime_for_empty_or_unmatched_pools(self):
        filters = [(), (('cost', 'le', 3),), (('id', 'in', ('fixture',)),), (('type', 'eq', 'MINION'),), (('cost', 'eq', True),), (('tribe', 'eq', 'invented'),), (('id', 'in', []),), (('unknown', 'eq', 1),), (('cost', 'eq'),)]
        for value in filters:
            with self.subTest(filters=value):
                try:
                    BatchEffects._validate_filters(value)
                except ValueError:
                    with self.assertRaises(EffectSchemaError):
                        validate_operation(('filtered_draw', value, 1))
                else:
                    validate_operation(('filtered_draw', value, 1), strict_unknown=True)
