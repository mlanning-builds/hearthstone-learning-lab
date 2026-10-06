import unittest
from expanded import random_deck
from expanded.environment import PolicyEnvironment
from expanded.evaluation import evaluate_pair

class PairedEvaluationTests(unittest.TestCase):
    def decks(self):return [random_deck('MAGE',31),random_deck('WARRIOR',53)]
    def test_first_player_controls_mulligan_and_coin_assignment(self):
        env=PolicyEnvironment(experimental=True);d=env.reset(self.decks(),seed=13,max_actions=20,first_player=1)
        self.assertEqual(d['actor'],1)
        d=env.step(0,revision=d['revision']);self.assertEqual(d['actor'],0)
        d=env.step(0,revision=d['revision']);self.assertEqual(d['actor'],1)
        self.assertTrue(any(c.card_id=='TOKEN_COIN' for c in env._game.players[0].hand))
        self.assertFalse(any(c.card_id=='TOKEN_COIN' for c in env._game.players[1].hand))
    def test_pair_runs_each_starting_position_and_excludes_truncations(self):
        report=evaluate_pair(self.decks(),[lambda d:0,lambda d:0],seeds=[7,8],max_actions=1,experimental=True)
        self.assertEqual([(g['seed'],g['first_player']) for g in report['games']],[(7,0),(7,1),(8,0),(8,1)])
        self.assertEqual(report['truncated'],4);self.assertEqual(report['draws'],0)
        self.assertIsNone(report['completed_score'])
        self.assertTrue(all(g['reason']=='action_limit' for g in report['games']))
    def test_duplicate_seeds_and_illegal_policy_output_are_rejected(self):
        with self.assertRaises(ValueError):evaluate_pair(self.decks(),[lambda d:0]*2,seeds=[7,7],max_actions=1,experimental=True)
        with self.assertRaises(ValueError):evaluate_pair(self.decks(),[lambda d:-1]*2,seeds=[7],max_actions=1,experimental=True)
    def test_completed_games_have_outcomes_separate_from_action_caps(self):
        def pass_turn(d):
            return next(i for i,a in enumerate(d['actions']) if a['kind'] in ('mulligan','end'))
        report=evaluate_pair(self.decks(),[pass_turn]*2,seeds=[17],max_actions=200,experimental=True)
        self.assertEqual(report['completed'],2);self.assertEqual(report['truncated'],0)
        self.assertEqual(report['player0_wins']+report['player0_losses']+report['draws'],2)
        self.assertTrue(all(g['reason']=='lethal' for g in report['games']))

class EvaluationSummaryTests(unittest.TestCase):
    def game(self,seed,first,reward,done=True):
        return dict(seed=seed,first_player=first,rewards=[reward,-reward],terminated=done)
    def summary(self,games):
        from expanded.evaluation import summarize_games
        return summarize_games(games)
    def test_starting_advantage_is_visible_without_changing_pair_score(self):
        r=self.summary([self.game(s,f,1 if f==0 else -1) for s in (1,2) for f in (0,1)])
        self.assertEqual([x['score'] for x in r['by_starting_player']],[1,0])
        self.assertEqual(r['paired_score'],0.5);self.assertEqual(r['paired_score_standard_error'],0)
    def test_standard_error_uses_pairs_as_samples(self):
        r=self.summary([self.game(s,f,1 if s==1 else -1) for s in (1,2) for f in (0,1)])
        self.assertEqual(r['paired_score_standard_error'],0.5)
        self.assertEqual(r['action_cap_score_bounds'],[0.5,0.5])
    def test_partial_pair_is_excluded_and_cap_bounds_include_it(self):
        r=self.summary([self.game(1,0,1),self.game(1,1,0,False)])
        self.assertIsNone(r['paired_score']);self.assertEqual(r['complete_pairs'],0)
        self.assertEqual(r['action_cap_score_bounds'],[0.5,1])
    def test_single_pair_does_not_claim_variance_estimate(self):
        r=self.summary([self.game(1,0,0),self.game(1,1,0)])
        self.assertEqual(r['paired_score'],0.5);self.assertIsNone(r['paired_score_standard_error'])
    def test_all_capped_has_full_bounds(self):
        r=self.summary([self.game(1,f,0,False) for f in (0,1)])
        self.assertEqual(r['action_cap_score_bounds'],[0,1]);self.assertIsNone(r['paired_score'])
    def test_duplicate_start_position_rejected(self):
        with self.assertRaises(ValueError):self.summary([self.game(1,0,1),self.game(1,0,1)])
