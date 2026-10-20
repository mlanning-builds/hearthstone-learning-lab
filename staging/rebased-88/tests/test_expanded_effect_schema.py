import sys,unittest
from expanded import cards,locations
from expanded.effect_schema import (EffectSchemaError,validate_rule,validate_operation,
 validate_table,validate_namespace)
class EffectSchemaTests(unittest.TestCase):
 def test_target_mode_is_not_an_operation(self):
  report=validate_rule(('friendly_minion',[('buff',1,2)]),strict_unknown=True)
  self.assertEqual(report.operations,1);self.assertFalse(report.uncovered)
 def test_wrong_rule_container(self):
  for rule in ('none',('none',),('none','damage'),(False,[])):
   with self.subTest(rule=rule),self.assertRaises(EffectSchemaError):validate_rule(rule)
 def test_operand_types_counts_and_boolean_rejection(self):
  for op in (('damage',True),('damage','3'),('damage',),('buff',1),('summon',17,1),('draw',1,2),()):
   with self.subTest(op=op),self.assertRaises(EffectSchemaError):validate_operation(op)
 def test_nested_operations_are_checked(self):
  with self.assertRaisesRegex(EffectSchemaError,'operand type'):
   validate_operation(('schedule_turn_effect','start',1,3,(('damage','oops'),)))
  with self.assertRaises(EffectSchemaError):validate_operation(('when_state','condition',('buff',1)))
 def test_unknown_operations_explicitly_reported_or_rejected(self):
  report=validate_operation(('unimplemented_fixture',17))
  self.assertEqual(report.uncovered,{'unimplemented_fixture'})
  with self.assertRaisesRegex(EffectSchemaError,'uncovered'):validate_operation(('unimplemented_fixture',),strict_unknown=True)
 def test_trigger_condition_and_choice_modes_not_operations(self):
  report=validate_table('TRIGGERS',{'fixture':(('summon','friendly','BEAST'),[('buff_self',1,1)])},True)
  self.assertEqual(report.operations,1)
  report=validate_table('CHOICES',{'fixture':[('label','none',[('draw',1)])]},True)
  self.assertEqual(report.operations,1)
 def test_error_has_card_table_and_operand_path(self):
  with self.assertRaisesRegex(EffectSchemaError,r"RULES\['fixture'\].*\[1\].*operand type"):
   validate_table('RULES',{'fixture':('none',[('damage','bad')])})
 def test_real_published_tables_validate_without_support_claim(self):
  reports=validate_namespace(vars(cards));self.assertGreater(sum(r.operations for r in reports.values()),2000)
  self.assertFalse(set().union(*(r.uncovered for r in reports.values())))
 def test_known_live_variants(self):
  for op in (('freeze',True),('weapon_buff',2),('weapon_buff',2,2),('missiles','enemies',3),('missiles','enemies',3,1)):
   validate_operation(op,strict_unknown=True)

 def test_new_primitive_schemas_reject_bad_operands(self):
  for op in (('combo_damage',True),('death_summon','fixture','2'),('death_summon','fixture',1,False),('buff_random_other',1,2,17),('damage_draw_if_dead',1,True),('reverse_deck',1),('taunt_hand_buff',1)):
   with self.subTest(op=op),self.assertRaises(EffectSchemaError):validate_operation(op)
 def test_condition_wrappers_validate_shape_and_nested_operands(self):
  for op in (('when_state',False,('draw',1)),('if_state','ready'),('when_state','ready',('combo_damage',True)),('if_state','ready',('armor',1),('armor',2))):
   with self.subTest(op=op),self.assertRaises(EffectSchemaError):validate_operation(op)
  for op in (('when_state','ready',('draw',1)),('if_state','ready',('armor',2)),('death_summon','fixture',1,0),('buff_random_other',1,2,'BEAST'),('damage_draw_if_dead',1,2)):
   validate_operation(op,strict_unknown=True)

if __name__=='__main__':unittest.main()
