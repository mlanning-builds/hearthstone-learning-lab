import json
from pathlib import Path
import tempfile
import unittest
from expanded import random_deck
from expanded.environment import PolicyEnvironment
from expanded.learning import SparsePolicy
from expanded.checkpoints import save_policy
from expanded.frozen_policy import checkpoint_policy_factory,FrozenPolicy

class FrozenPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'policy.json'
        self.receipt=save_policy(self.path,SparsePolicy(seed=31),completed_episodes=0)
        env=PolicyEnvironment(experimental=True)
        self.decision=env.reset([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71,max_actions=1)
    def factory(self):return checkpoint_policy_factory(self.path,self.path,expected_sha256=[self.receipt['sha256']]*2)
    def test_fresh_factory_calls_reproduce_sampling(self):
        factory,metadata=self.factory();a=factory(5);b=factory(5)
        self.assertEqual([a[0](self.decision) for _ in range(40)],[b[0](self.decision) for _ in range(40)])
        self.assertEqual(metadata['checkpoint_sha256'],[self.receipt['sha256']]*2)
    def test_seat_rng_is_independent(self):
        factory,_=self.factory();a=factory(5);b=factory(5)
        for _ in range(30):a[0](self.decision)
        self.assertEqual([a[1](self.decision) for _ in range(20)],[b[1](self.decision) for _ in range(20)])
    def test_weights_are_read_only_and_copied(self):
        weights={'test':2.0};policy=FrozenPolicy(weights,seed=1);weights['test']=99
        self.assertEqual(policy._policy.weights['test'],2.0)
        with self.assertRaises(TypeError):policy._policy.weights['test']=3
    def test_loaded_snapshot_unaffected_by_file_changes(self):
        factory,_=self.factory();before=factory(5)
        self.path.write_text('{}')
        after=factory(5)
        self.assertEqual([before[0](self.decision) for _ in range(20)],[after[0](self.decision) for _ in range(20)])
    def test_wrong_checksum_rejected(self):
        with self.assertRaisesRegex(ValueError,'checksum'):
            checkpoint_policy_factory(self.path,self.path,expected_sha256=['bad','bad'])
