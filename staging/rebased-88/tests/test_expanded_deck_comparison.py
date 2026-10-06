import unittest
from unittest.mock import patch
from expanded import random_deck
from expanded.deck_comparison import compare_decks

class DeckComparisonTests(unittest.TestCase):
    def setUp(self):self.deck=random_deck('MAGE',31)
    def run_panel(self,**kwargs):
        args=dict(seeds=[7,8],max_actions=2,max_games=8,policy_id='fixture',experimental=True)
        args.update(kwargs)
        return compare_decks({'a':self.deck,'b':self.deck},{'opponent':self.deck},
                             lambda seed:[lambda d:0,lambda d:0],**args)
    def test_budget_rejected_before_any_games(self):
        with patch('expanded.deck_comparison.evaluate_pair') as evaluate:
            with self.assertRaises(ValueError):self.run_panel(max_games=7)
            evaluate.assert_not_called()
    def test_complete_scores_rank_against_panel(self):
        def evaluate(*args,**kwargs):
            score=1.0 if evaluate.calls<2 else 0.25;evaluate.calls+=1
            return dict(completed=2,action_cap_score_bounds=[score,score])
        evaluate.calls=0
        with patch('expanded.deck_comparison.evaluate_pair',evaluate):report=self.run_panel()
        self.assertEqual(report['games'],8)
        self.assertEqual(report['ranking'],[{'candidate':'a','score':1.0},{'candidate':'b','score':0.25}])
    def test_caps_withhold_entire_ranking(self):
        with patch('expanded.deck_comparison.evaluate_pair',return_value=dict(completed=1,action_cap_score_bounds=[0.5,1.0])):
            report=self.run_panel()
        self.assertIsNone(report['ranking'])
        self.assertTrue(all(r['panel_score'] is None for r in report['results']))
    def test_duplicate_seeds_rejected(self):
        with self.assertRaises(ValueError):self.run_panel(seeds=[7,7])
    def test_real_capped_matchups_record_no_ranking(self):
        report=self.run_panel(seeds=[7],max_games=4,max_actions=1)
        self.assertIsNone(report['ranking']);self.assertEqual(report['games'],4)
        self.assertTrue(all(r['completed']==0 for r in report['results']))
    def test_policy_factory_recreated_for_each_seed_pair(self):
        calls=[]
        def factory(seed):calls.append(seed);return [lambda d:0]*2
        with patch('expanded.deck_comparison.evaluate_pair',return_value=dict(completed=2,action_cap_score_bounds=[0.5,0.5])):
            compare_decks({'a':self.deck,'b':self.deck},{'o':self.deck},factory,
                          seeds=[7,8],max_actions=1,max_games=8,policy_id='fixture',experimental=True)
        self.assertEqual(calls,[7,8,7,8])
