import unittest
from copy import deepcopy
from expanded.quest_progress import objective,advance_objective,advance_count

class QuestProgressTests(unittest.TestCase):
 def count(self,total=2,**where):return dict(kind='count',event='damage',total=total,where=where)
 def test_counter_caps(self):self.assertEqual(advance_count(1,4,9),4)
 def test_invalid_counter_rejects(self):
  for args in ((0,0,1),(-1,3,1),(4,3,1),(0,3,-1),(True,3,1),(0,3,1.5)):
   with self.subTest(args=args),self.assertRaises(ValueError):advance_count(*args)
 def test_exact_damage_is_one_occurrence(self):
  s=objective(self.count(amount=2,enemy=True,owner_turn=True));s,c=advance_objective(s,dict(kind='damage',amount=2,enemy=True,owner_turn=True));self.assertEqual(s['progress'],1);self.assertFalse(c)
 def test_damage_filters_exclude_wrong_amount_side_and_turn(self):
  s=objective(self.count(amount=2,enemy=True,owner_turn=True))
  for event in (dict(kind='damage',amount=1,enemy=True,owner_turn=True),dict(kind='damage',amount=2,enemy=False,owner_turn=True),dict(kind='damage',amount=2,enemy=True,owner_turn=False)):
   self.assertEqual(advance_objective(s,event),(s,()))
 def test_boolean_does_not_match_integer_condition(self):
  s=objective(self.count(amount=1));self.assertEqual(advance_objective(s,dict(kind='damage',amount=True)),(s,()))
 def test_missing_fact_does_not_count(self):
  s=objective(self.count(enemy=True));self.assertEqual(advance_objective(s,dict(kind='damage')),(s,()))
 def test_completion_is_emitted_once(self):
  s,c=advance_objective(objective(self.count(1)),dict(kind='damage'));self.assertEqual(c,((),));self.assertEqual(advance_objective(s,dict(kind='damage')),(s,()))
 def test_input_state_and_spec_are_unchanged(self):
  spec=self.count();original=deepcopy(spec);s=objective(spec);before=deepcopy(s);advance_objective(s,dict(kind='damage'));self.assertEqual(s,before);self.assertEqual(spec,original)
 def test_full_then_empty_order(self):
  s=objective(dict(kind='sequence',children=[dict(kind='value',event='hand',field='count',equals=n) for n in (10,0)]))
  s,c=advance_objective(s,dict(kind='hand',count=0));self.assertFalse(c)
  s,c=advance_objective(s,dict(kind='hand',count=10));self.assertEqual(c,((0,),));self.assertFalse(s['complete'])
  s,c=advance_objective(s,dict(kind='hand',count=0));self.assertEqual(c,((1,),()));self.assertTrue(s['complete'])
 def test_one_event_cannot_complete_two_sequential_stages(self):
  s=objective(dict(kind='sequence',children=[self.count(1),self.count(1)]));s,c=advance_objective(s,dict(kind='damage'));self.assertEqual(c,((0,),));self.assertFalse(s['complete'])
 def test_parallel_schools_keep_independent_progress(self):
  s=objective(dict(kind='parallel',children=[dict(kind='count',event='spell',total=4,where={'school':school}) for school in ('HOLY','SHADOW')]))
  for _ in range(4):s,c=advance_objective(s,dict(kind='spell',school='HOLY'))
  self.assertEqual(c,((0,),));self.assertEqual(s['children'][1]['progress'],0)
  for _ in range(4):s,c=advance_objective(s,dict(kind='spell',school='SHADOW'))
  self.assertEqual(c,((1,),()));self.assertTrue(s['complete'])
 def test_parallel_identical_branches_can_finish_same_event(self):
  s=objective(dict(kind='parallel',children=[self.count(1),self.count(1)]));s,c=advance_objective(s,dict(kind='damage'));self.assertEqual(c,((0,),(1,),()))
 def test_distinct_attack_values_ignore_repetitions_and_nonbeasts(self):
  s=objective(dict(kind='distinct',event='play',field='attack',allowed=[1,3,5,7],total=4,where={'beast':True}))
  for value in (1,1,2,3,7):s,c=advance_objective(s,dict(kind='play',attack=value,beast=True))
  self.assertEqual(s['progress'],3);s,c=advance_objective(s,dict(kind='play',attack=5,beast=False));self.assertFalse(c)
  s,c=advance_objective(s,dict(kind='play',attack=5,beast=True));self.assertEqual(c,((),))
 def test_distinct_boolean_does_not_match_attack_one(self):
  s=objective(dict(kind='distinct',event='play',field='attack',allowed=[1],total=1));self.assertEqual(advance_objective(s,dict(kind='play',attack=True)),(s,()))
 def test_discover_offer_does_not_count_as_discovery(self):
  s=objective(dict(kind='count',event='discover_completed',total=8));self.assertEqual(advance_objective(s,dict(kind='discover_offered')),(s,()))
 def test_invalid_definitions_reject(self):
  for spec in ({'kind':'unknown'},{'kind':'parallel','children':[]},{'kind':'count','event':'x','total':0},{'kind':'value','event':'x','field':'count','equals':True},{'kind':'distinct','event':'x','field':'a','allowed':[1,1],'total':1}):
   with self.subTest(spec=spec),self.assertRaises(ValueError):objective(spec)
 def test_nested_paths_identify_completed_reward_branches(self):
  s=objective(dict(kind='parallel',children=[dict(kind='sequence',children=[self.count(1),self.count(1)]),self.count(2)]));s,_=advance_objective(s,dict(kind='damage'));s,c=advance_objective(s,dict(kind='damage'));self.assertEqual(c,((0,1),(0,),(1,),()))
