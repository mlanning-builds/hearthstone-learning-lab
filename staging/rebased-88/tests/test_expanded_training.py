import unittest
from unittest.mock import patch
from expanded.learning import SparsePolicy
from expanded.training import train_episode
from expanded import random_deck

class TrainingTests(unittest.TestCase):
    def test_batch_uses_unchanged_behavior_probabilities(self):
        p=SparsePolicy(seed=1);rows=[{'a':1},{'b':1}]
        p.reinforce_batch([(rows,0,1),(rows,0,1)],learning_rate=0.1)
        self.assertAlmostEqual(p.weights['a'],0.1)
        self.assertAlmostEqual(p.weights['b'],-0.1)
    def test_invalid_later_sample_rolls_back_whole_batch(self):
        p=SparsePolicy(seed=1,weights={'a':2});old=dict(p.weights)
        with self.assertRaises(ValueError):
            p.reinforce_batch([([{'a':1},{}],0,1),([{}],4,1)],learning_rate=0.1)
        self.assertEqual(p.weights,old)
    def test_action_capped_real_game_has_no_update(self):
        p=SparsePolicy(seed=1);decks=[random_deck('MAGE',31),random_deck('WARRIOR',53)]
        result=train_episode(p,decks,seed=71,max_actions=2,learning_rate=0.01,experimental=True)
        self.assertTrue(result['truncated']);self.assertFalse(result['updated'])
        self.assertIsNone(result['terminal_rewards']);self.assertEqual(p.weights,{})
    def fake_environment(self,fail=False):
        class Fake:
            def __init__(self,**kwargs):self.i=0
            def decision(self):
                return dict(actor=self.i%2,terminated=self.i==2,truncated=False,
                            steps=self.i,revision=self.i,end_reason='fixture',rewards=[1,-1])
            def reset(self,*args,**kwargs):return self.decision()
            def step(self,*args,**kwargs):
                self.i+=1
                if fail:raise RuntimeError('fixture failure')
                return self.decision()
        return Fake
    def test_own_seat_rewards_and_frozen_episode_weights(self):
        p=SparsePolicy(seed=1);seen=[]
        def encode(d):
            seen.append(dict(p.weights));return [{str(d['actor'])+'a':1},{str(d['actor'])+'b':1}]
        with patch('expanded.training.PolicyEnvironment',self.fake_environment()),patch('expanded.training.encode_decision',encode):
            result=train_episode(p,[],seed=1,max_actions=2,learning_rate=0.1,experimental=True)
        self.assertEqual(seen,[{},{}]);self.assertEqual(result['actor_decisions'],[1,1])
        self.assertEqual(result['terminal_rewards'],[1,-1]);self.assertTrue(result['updated'])
        self.assertGreater(p.weights['0a'],0);self.assertLess(p.weights['1b'],0)
    def test_failure_restores_sampling_and_weights(self):
        p=SparsePolicy(seed=1);state=p.rng.getstate()
        with patch('expanded.training.PolicyEnvironment',self.fake_environment(True)),patch('expanded.training.encode_decision',return_value=[{'a':1},{}]):
            with self.assertRaises(RuntimeError):
                train_episode(p,[],seed=1,max_actions=2,learning_rate=0.1,experimental=True)
        self.assertEqual(p.weights,{});self.assertEqual(p.rng.getstate(),state)
