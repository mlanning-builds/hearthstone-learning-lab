import unittest
from expanded.dependencies import dependency_report, literal_dependencies


class GenerationDependencyTests(unittest.TestCase):
    def test_nested_conditional_and_choices(self):
        data=('none',[('if_holding',(('tribe','eq','DRAGON'),),('equip','weapon')),('choose_fixed_summon',('a','b'))])
        self.assertEqual(literal_dependencies(data),{'weapon','a','b'})
    def test_no_text_or_arbitrary_id_inference(self):
        self.assertEqual(literal_dependencies([('buff',1,1),('label','summon TOKEN'),('unknown','TOKEN')]),set())
    def test_recursive_missing_path(self):
        result=dependency_report({'a':[('summon','b',1)],'b':[('add','c',1)]},{'a','b'},['a'])
        self.assertEqual(result['missing_paths'],[dict(root='a',missing='c',path=['a','b','c'])])
    def test_cycles_terminate_and_keep_external_dependency(self):
        result=dependency_report({'a':[('summon','b',1)],'b':[('summon','a',1),('equip','c')]},{'a','b'},['a'])
        self.assertEqual(result['missing_ids'],['c'])
        self.assertEqual(len(result['missing_paths']),1)
    def test_shortest_path_and_duplicate_edges(self):
        result=dependency_report({'a':[('summon','b',1),('add','c',1),('add','c',1)],'b':[('add','c',1)]},{'a','b'},['a'])
        self.assertEqual(result['missing_paths'][0]['path'],['a','c'])
    def test_vanilla_leaf_is_not_marked_missing(self):
        result=dependency_report({'a':[('summon','b',1)]},{'a','b'},['a'])
        self.assertEqual(result['missing_ids'],[])
        self.assertFalse(result['complete_dependency_coverage'])
    def test_missing_root_is_explicit(self):
        result=dependency_report({},set(),['a'])
        self.assertEqual(result['missing_paths'],[dict(root='a',missing='a',path=['a'])])
    def test_mixed_death_group(self):
        self.assertEqual(literal_dependencies([('death_summon_group',('a','b'),2)]),{'a','b'})

    def test_trigger_labels_are_not_generation_operations(self):
        from expanded.dependencies import declaration_operations
        declarations=declaration_operations({
            'TRIGGERS':{'a':(('summon','friendly','MURLOC'),[('summon','b',1)])},
            'CHOICES':{'b':[('summon','none',[('add','c',1)])]},
            'LOCATION_RULES':{'location':'minion'}})
        result=dependency_report(declarations,{'a','b','c'},['a'])
        self.assertEqual(result['missing_ids'],[])
        self.assertEqual(result['edges'],2)
        self.assertNotIn('location',declarations)
