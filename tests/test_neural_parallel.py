"""Parallel control-flow checks with fake collection; no games or PPO updates."""
import tempfile
import unittest
from unittest.mock import patch
import torch
from hearthstone_sim.neural.runner import run,prepare
from hearthstone_sim.neural.model import ModelConfig
from hearthstone_sim.neural.checkpoints import load
from hearthstone_sim.neural.parallel import action_seed

class FakeCollector:
    all_tasks=[]
    retried=[]
    fail_first=False
    closed=False
    def __init__(self,workers,model_config,encoder_config,weights,tasks):
        self.tasks=tasks;type(self).all_tasks.extend(tasks)
        self.weights={k:v.clone() for k,v in weights.items()}
    def result(self,index):
        if self.fail_first and index==0:return [],dict(failed=True,signature='Fake:error',terminated=False,truncated=False,actions=1)
        return [],dict(terminated=True,truncated=False,actions=1,reward=1,seed=self.tasks[index]['seed'])
    def retry(self,task):
        type(self).retried.append(task)
        return [],dict(terminated=True,truncated=False,actions=1,reward=1,seed=task['seed'])
    def close(self):type(self).closed=True

class ParallelTests(unittest.TestCase):
    def setUp(self):
        FakeCollector.all_tasks=[];FakeCollector.retried=[];FakeCollector.fail_first=False;FakeCollector.closed=False
        self.config=ModelConfig(width=16,heads=2,layers=1,feedforward=32)
    def launch(self,folder,**kw):
        with patch('hearthstone_sim.neural.parallel.BatchCollector',FakeCollector),patch('hearthstone_sim.neural.runner.collect_game',side_effect=AssertionError('No real game collection')),patch('hearthstone_sim.neural.runner.update',side_effect=AssertionError('No learning')):
            return run(iterations=1,games_per_iteration=4,max_actions=2,seed=71,output=folder,collection_workers=2,model_config=self.config,allow_training=True,emit=lambda e:None,**kw)
    def test_reserved_seeds_order_and_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            cp=self.launch(folder);p=load(cp['path'],prepare(model_config=self.config)[2])
            self.assertEqual(p['global_game'],4);self.assertEqual(p['safety']['seed_position'],4)
            self.assertEqual([t['seed'] for t in FakeCollector.all_tasks],[71,72,73,74])
            self.assertEqual(len({t['action_seed'] for t in FakeCollector.all_tasks}),4)
            self.assertTrue(FakeCollector.closed)
            self.launch(folder,resume=cp['path'])
            self.assertEqual([t['seed'] for t in FakeCollector.all_tasks[4:]],[75,76,77,78])
    def test_retry_does_not_collide_or_change_opponent(self):
        FakeCollector.fail_first=True
        with tempfile.TemporaryDirectory() as folder:
            cp=self.launch(folder);p=load(cp['path'],prepare(model_config=self.config)[2])
            task=FakeCollector.retried[0];self.assertEqual(task['seed'],75)
            for k in ('pair','seat','first','descriptor','heuristic'):self.assertEqual(task[k],FakeCollector.all_tasks[0][k])
            self.assertEqual(p['safety']['attempted'],5);self.assertEqual(p['safety']['seed_position'],5)
    def test_threshold_discards_partial_batch(self):
        FakeCollector.fail_first=True
        with tempfile.TemporaryDirectory() as folder:
            cp=self.launch(folder,failure_repeats=1);p=load(cp['path'],prepare(model_config=self.config)[2])
            self.assertTrue(p['stopped']);self.assertEqual(p['global_game'],0)
            self.assertEqual(p['safety']['attempted'],1);self.assertEqual(p['safety']['seed_position'],4)
            self.assertTrue(FakeCollector.closed)
    def test_master_rng_restore_is_reproducible(self):
        g=torch.Generator().manual_seed(11);action_seed(g);state=g.get_state();seeds=[action_seed(g) for _ in range(8)]
        g.set_state(state);self.assertEqual(seeds,[action_seed(g) for _ in range(8)])
    def test_worker_guard(self):
        with self.assertRaises(ValueError):run(iterations=1,games_per_iteration=1,max_actions=2,seed=71,output="unused",collection_workers=5)
        with self.assertRaises(ValueError):run(iterations=1,games_per_iteration=1,max_actions=2,seed=71,output='unused',collection_workers=2,device='mps')
if __name__=='__main__':unittest.main()

class WorkerTests(unittest.TestCase):
    def test_worker_uses_frozen_model_and_per_game_rng(self):
        from hearthstone_sim._bootstrap import activate
        activate()
        from hearthstone_sim.neural import parallel
        from hearthstone_sim.neural.encoding import EncoderConfig
        from hearthstone_sim.neural.model import TransformerPolicyValue
        from hearthstone_sim.neural.ppo import PPOConfig
        config=ModelConfig(width=16,heads=2,layers=1,feedforward=32)
        model=TransformerPolicyValue(config);weights={k:v.clone() for k,v in model.state_dict().items()}
        parallel.initialize(config,EncoderConfig(),weights)
        task=dict(metadata={},folder=None,name='fixture',trace=False,descriptor=None,pair=[],seed=4,seat=0,first=1,max_actions=2,action_seed=123,ppo=PPOConfig(),heuristic=False)
        with patch('hearthstone_sim.neural.runner.collect_game',return_value=([],{})) as collect:
            parallel.execute(task)
        learner,opponent=collect.call_args.args[:2]
        self.assertTrue(all(torch.equal(learner.state_dict()[k],v) for k,v in weights.items()))
        self.assertTrue(all(torch.equal(opponent.state_dict()[k],v) for k,v in weights.items()))
        self.assertTrue(all(not p.requires_grad for p in learner.parameters()))
        self.assertEqual(collect.call_args.kwargs['generator'].initial_seed(),123)
