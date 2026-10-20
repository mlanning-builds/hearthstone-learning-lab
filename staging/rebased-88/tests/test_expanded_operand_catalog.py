"""Legacy declarations reject malformed operands before effect execution."""
import unittest
from expanded import cards
from expanded.operand_catalog import contracts
from expanded.effect_schema import validate_namespace,validate_operation,EffectSchemaError

class OperandCatalogTests(unittest.TestCase):
 def test_all_515_original_gaps_have_explicit_contracts(self):
  self.assertEqual(len(contracts()),515)
  reports=validate_namespace(vars(cards),strict_unknown=True)
  self.assertFalse(set().union(*(report.uncovered for report in reports.values())))
 def test_zero_operand_operations_reject_extra_payload(self):
  validate_operation(('ashalon_adapt',),strict_unknown=True)
  with self.assertRaises(EffectSchemaError):validate_operation(('ashalon_adapt',None),strict_unknown=True)
 def test_integer_is_not_boolean_or_text(self):
  for value in (True,'2',None):
   with self.subTest(value=value),self.assertRaises(EffectSchemaError):validate_operation(('aoe_draw_dead',value),strict_unknown=True)
 def test_missing_operands_reject_before_runtime(self):
  with self.assertRaises(EffectSchemaError):validate_operation(('add_spell_damage',),strict_unknown=True)
 def test_unknown_operations_are_still_rejected(self):
  with self.assertRaisesRegex(EffectSchemaError,'uncovered'):validate_operation(('fixture_new_unreviewed_op',1),strict_unknown=True)
 def test_nested_selector_structure_cannot_be_replaced_by_scalar(self):
  # A real known legacy declaration carrying a nested tuple.
  name=next(name for name,variants in contracts().items() if any(any(spec['kind']=='sequence' for spec in variant) for variant in variants))
  variant=next(v for v in contracts()[name] if any(spec['kind']=='sequence' for spec in v))
  def example(spec):
   if spec['kind']=='int':return 1
   if spec['kind']=='bool':return False
   if spec['kind']=='none':return None
   if spec['kind']=='text':return 'fixture'
   if spec['kind']=='literal':return spec['value']
   if spec['kind']=='sequence':return tuple(example(s) for s in spec['items'])
   self.fail('Unexpected test operand '+spec['kind'])
  operands=[example(spec) for spec in variant]
  index=next(i for i,s in enumerate(variant) if s['kind']=='sequence');operands[index]=7
  with self.assertRaises(EffectSchemaError):validate_operation((name,*operands),strict_unknown=True)
