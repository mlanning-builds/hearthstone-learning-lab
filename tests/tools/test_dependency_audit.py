import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[2]/'tools/build_dependencies.py'
spec=importlib.util.spec_from_file_location('dependency_audit',path)
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class DependencyAuditTests(unittest.TestCase):
    def test_cycles_terminate_and_include_transitive_dependencies(self):
        graph={'a':{'b'},'b':{'a','c'},'c':{'d'}}
        self.assertEqual(audit.closure('a',graph),['a','b','c','d'])
    def test_unrelated_cards_are_not_dependencies(self):
        self.assertEqual(audit.closure('a',{'b':{'c'}}),[])
    def test_nested_choices_and_fixed_pools_are_traversed(self):
        definition=('none',[('choose',[('summon','token',2)]),('pool',('a','b'))])
        self.assertTrue({'token','a','b'}<=set(audit.strings(definition)))

    def roles(self,source):
        import ast
        tree=ast.parse(source)
        parents={child:parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        return [audit.reference_role(n,parents) for n in ast.walk(tree) if isinstance(n,ast.Constant) and n.value=='CARD']
    def test_inventory_is_not_reported_as_generation(self):
        self.assertEqual(self.roles("COIN_IDS = {'CARD'}"),['identity_inventory'])
    def test_declaration_owner_distinct_from_effect_argument(self):
        self.assertEqual(self.roles("RULES = {'CARD': ('summon', 'CARD')}"),['declaration_key','unresolved_expression'])
    def test_comparison_inside_branch_stays_comparison(self):
        self.assertEqual(self.roles("if cid == 'CARD': pass"),['identity_comparison'])
    def test_local_metadata_not_effect_dependency(self):
        self.assertEqual(self.roles("LOCAL_TOKENS = {'CARD': {'id': 'CARD'}}"),['metadata_record','metadata_record'])
    def test_unknown_containers_remain_unresolved(self):
        self.assertEqual(self.roles("CUSTOM = ['CARD']"),['unresolved_expression'])
