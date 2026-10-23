"""Crash/resume fixtures only. No real gameplay or learning."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch,Mock
import torch
from hearthstone_sim.neural.evaluation_cache import EvaluationJournal,identity
from hearthstone_sim.neural.evaluation import evaluate,EvaluationConfig
from hearthstone_sim.neural.runner import prepare,new_safety_state
from hearthstone_sim.neural.model import ModelConfig,TransformerPolicyValue
from hearthstone_sim.neural.encoding import VisibleEncoder
from test_neural_safety import FakeEnvironment

class CacheTests(unittest.TestCase):
    def setUp(self):
        self.decks=prepare()[0];self.model=TransformerPolicyValue(ModelConfig(width=16,heads=2,layers=1,feedforward=32))
        self.encoder=Mock(config=VisibleEncoder().config);self.cfg=EvaluationConfig(games_per_opponent=3)
    def invoke(self,folder,safety,emit=lambda *a,**k:None):
        with patch('expanded.environment.PolicyEnvironment',FakeEnvironment) as env,patch('hearthstone_sim.neural.runner.policy_action',return_value=(0,-1.,0.)),patch('hearthstone_sim.neural.evaluation.heuristic_action',return_value=0):
            return evaluate(self.model,{},self.encoder,self.decks,{},config=self.cfg,max_actions=2,emit=emit,safety=safety,cache_dir=folder)
    def test_resume_skips_finished_cases_and_does_not_double_count(self):
        with tempfile.TemporaryDirectory() as folder:
            safety=new_safety_state()
            def interrupt(*args,**kw):raise InterruptedError('scripted shutdown after durable case')
            with self.assertRaises(InterruptedError):self.invoke(folder,safety,interrupt)
            self.assertEqual(safety['attempted'],1)
            report=self.invoke(folder,safety);self.assertEqual(report['summary']['attempted'],3);self.assertEqual(safety['attempted'],3)
            with patch.object(FakeEnvironment,'reset',side_effect=AssertionError('Cached games must not replay')):
                report2=self.invoke(folder,safety)
            self.assertEqual(report2['summary'],report['summary']);self.assertEqual(safety['attempted'],3)
            fresh=new_safety_state()
            with patch.object(FakeEnvironment,'reset',side_effect=AssertionError('No replay')):self.invoke(folder,fresh)
            self.assertEqual(fresh['attempted'],3);self.assertEqual(fresh['failed'],0)
    def test_corruption_fails_instead_of_silently_reusing(self):
        with tempfile.TemporaryDirectory() as folder:
            j=EvaluationJournal(folder,{'test':1});j.write(0,0,{'reward':1})
            p=next(j.folder.glob('case-*.json'));r=json.loads(p.read_text());r['result']['reward']=-1;p.write_text(json.dumps(r))
            with self.assertRaises(ValueError):j.read(0,0)
    def test_contract_isolated_for_new_weights_decks_or_seed(self):
        contract=identity(self.model,{},self.encoder,self.decks,self.cfg,2,'engine')
        with torch.no_grad():next(self.model.parameters()).add_(.01)
        changed=identity(self.model,{},self.encoder,self.decks,self.cfg,2,'engine')
        self.assertNotEqual(contract,changed)
        with tempfile.TemporaryDirectory() as folder:
            a=EvaluationJournal(folder,contract);b=EvaluationJournal(folder,changed)
            self.assertNotEqual(a.key,b.key)
            changed_seed=identity(self.model,{},self.encoder,self.decks,EvaluationConfig(games_per_opponent=3,seed=4),2,'engine')
            self.assertNotEqual(changed_seed,changed)
    def test_unfinished_temporary_write_is_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            j=EvaluationJournal(folder,{});(j.folder/'case-000-00000.json.fake.partial').write_text('unfinished')
            self.assertIsNone(j.read(0,0));j.write(0,0,dict(reward=1));self.assertEqual(j.read(0,0)['reward'],1)
