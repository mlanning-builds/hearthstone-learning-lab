import unittest
from tools.search_candidate_decks import validate_plan,select_candidate

class SearchRunnerTests(unittest.TestCase):
 def plan(self):
  return dict(schema='candidate-deck-search-v1',rounds=2,neighbors=3,max_actions=500,max_games=72,
              search_seeds=[1,2],heldout_seeds=[3],neighbor_seed=10,opponents={'a':{},'b':{}},checkpoints=[{},{}])
 def test_budget_includes_all_rounds_both_starting_players_and_heldout_baseline(self):
  self.assertEqual(validate_plan(self.plan()),72)
 def test_undersized_budget_rejected_before_games(self):
  p=self.plan();p['max_games']=71
  with self.assertRaisesRegex(ValueError,'reserve 72'):validate_plan(p)
 def test_heldout_seed_reuse_rejected(self):
  p=self.plan();p['heldout_seeds']=[2]
  with self.assertRaisesRegex(ValueError,'disjoint'):validate_plan(p)
 def test_duplicate_or_boolean_seeds_rejected(self):
  for seeds in ([1,1],[True],[]):
   p=self.plan();p['search_seeds']=seeds
   with self.assertRaises(ValueError):validate_plan(p)
 def test_tie_preserves_incumbent(self):
  r=dict(ranking=[{}],results=[dict(candidate='incumbent',panel_score=.5),dict(candidate='a',panel_score=.5)])
  self.assertEqual(select_candidate(r,'old',{'incumbent':'old','a':'new'}),('old',True))
 def test_completed_better_neighbor_selected(self):
  r=dict(ranking=[{}],results=[dict(candidate='incumbent',panel_score=.5),dict(candidate='a',panel_score=1)])
  self.assertEqual(select_candidate(r,'old',{'incumbent':'old','a':'new'}),('new',True))
 def test_capped_result_never_selects(self):
  self.assertEqual(select_candidate(dict(ranking=None),'old',{}),('old',False))
