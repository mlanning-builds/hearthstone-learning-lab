import unittest
from expanded.learning import SparsePolicy

class SparsePolicyTests(unittest.TestCase):
    def test_uniform_initial_policy_supports_variable_action_counts(self):
        p=SparsePolicy(seed=1)
        for n in (1,3,17):self.assertEqual(p.probabilities([{'bias':1}]*n),[1/n]*n)
    def test_positive_advantage_increases_selected_probability(self):
        p=SparsePolicy(seed=1);rows=[{'a':1},{'b':1}]
        p.reinforce(rows,0,advantage=1,learning_rate=0.1)
        self.assertGreater(p.probabilities(rows)[0],0.5)
        self.assertAlmostEqual(p.weights['a'],0.05);self.assertAlmostEqual(p.weights['b'],-0.05)
    def test_negative_advantage_reduces_selected_probability(self):
        p=SparsePolicy(seed=1);rows=[{'a':1},{'b':1}]
        p.reinforce(rows,1,advantage=-1,learning_rate=0.1)
        self.assertLess(p.probabilities(rows)[1],0.5)
    def test_large_logits_remain_finite(self):
        p=SparsePolicy(seed=1,weights={'a':10000,'b':9999})
        probs=p.probabilities([{'a':1},{'b':1}]);self.assertAlmostEqual(sum(probs),1)
    def test_sampling_reproduces_with_local_seed(self):
        a,b=SparsePolicy(seed=3),SparsePolicy(seed=3);rows=[{'x':1},{'y':1}]
        self.assertEqual([a.choose(rows) for _ in range(30)],[b.choose(rows) for _ in range(30)])
    def test_invalid_update_does_not_change_weights(self):
        p=SparsePolicy(seed=1,weights={'a':2});before=dict(p.weights)
        with self.assertRaises(ValueError):p.reinforce([{'a':1}],0,advantage=float('nan'),learning_rate=0.1)
        self.assertEqual(p.weights,before)
