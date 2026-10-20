"""Safety fixtures: scripted environments only; optimizer updates always mocked."""
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock
from hearthstone_sim._bootstrap import activate
activate()
from hearthstone_sim.neural.runner import (GameCapture, collect_game, new_safety_state,
    account_attempt, failure_limit, run, prepare)
from hearthstone_sim.neural.ppo import PPOConfig
from hearthstone_sim.neural.model import ModelConfig
from hearthstone_sim.neural.checkpoints import load
from hearthstone_sim.neural.evaluation import evaluate, EvaluationConfig
from hearthstone_sim.neural.dashboard import Dashboard
from tools.summarize_trace import summarize


def decision():
    return dict(actor=0, revision=0, terminated=False, truncated=False,
        observation=dict(turn=1, players=[dict(mana=1,health=30,hand=[],board=[])]*2),
        actions=[dict(kind='end')])


class FakeEnvironment:
    fail = False
    def __init__(self, **kwargs):
        self._game = SimpleNamespace(events=[dict(turn=1,event='approximation_profile',policies={'ULD_003':'heuristic'})])
    def reset(self,*args,**kwargs):
        return decision()
    def step(self,*args,**kwargs):
        self._game.events += [dict(turn=1,event='play',card='ULD_003'),
            dict(turn=1,event='approximation_used',policy='remaining-eight-v1',rule='bashana')]
        if self.fail:
            raise RuntimeError('scripted engine failure')
        return dict(terminated=True,truncated=False,steps=1,rewards=[1,-1],end_reason='scripted')


class SafetyTests(unittest.TestCase):
    def collect(self, folder, fail=False):
        class Env(FakeEnvironment):
            pass
        Env.fail=fail
        capture=GameCapture(dict(seed=3,learner_deck='A',opponent_deck='B',learner_seat=0,
            first_player=0,opponent='fake',engine_fingerprint='fake'),folder,'000001-0001',True)
        with patch('expanded.environment.PolicyEnvironment',Env), patch('hearthstone_sim.neural.runner.policy_action',return_value=(0,-1,0)):
            return collect_game(Mock(),Mock(),Mock(),[],seed=3,learner_seat=0,first_player=0,
                max_actions=2,generator=None,ppo=PPOConfig(),diagnostic=capture)

    def test_failure_discards_trajectory_and_saves_diagnostic(self):
        with tempfile.TemporaryDirectory() as f:
            samples,result=self.collect(f,True)
            self.assertEqual(samples,[]);self.assertTrue(result['failed']);self.assertIsNone(result['reward'])
            d=json.loads(next((Path(f)/'failures').glob('*.json')).read_text())
            for k in ('traceback','last_events','legal_actions','observation_hash','engine_fingerprint','seed','learner_deck','opponent_deck','opponent','action_count'):
                self.assertIn(k,d)
            self.assertIn('RuntimeError',d['traceback']);self.assertFalse((Path(f)/'traces').exists())

    def test_trace_summary_timing_and_approximation_counters(self):
        with tempfile.TemporaryDirectory() as f:
            _,r=self.collect(f)
            trace=json.loads(next((Path(f)/'traces').glob('*.json')).read_text())
            self.assertEqual(trace['policy_visible']['actions'][0]['actor'],0)
            self.assertIn('Result',summarize(trace));self.assertIn('Turn 1',summarize(trace))
            self.assertGreaterEqual(r['timing']['engine_seconds'],0)
            self.assertEqual(r['approximations'],{'remaining-eight-v1:bashana':1})
            self.assertEqual(r['approximation_proxies'],{'ULD_003':1})
            state=new_safety_state();account_attempt(state,r,'A','B')
            self.assertEqual(state['approximations']['A']['remaining-eight-v1:bashana'],1)

    def test_thresholds_and_pair_accounting(self):
        s=new_safety_state()
        for _ in range(5):account_attempt(s,dict(failed=True,signature='E:handler'),'A','B')
        self.assertIn('signature',failure_limit(s,.02,100,5))
        s['signatures']={};s.update(attempted=100,failed=3)
        self.assertIn('fraction',failure_limit(s,.02,100,5))
        self.assertIsNone(failure_limit(dict(s,attempted=99),.02,100,5))
        self.assertEqual(s['by_pair']['A / B']['failed'],5)

    def test_creation_failure_is_captured(self):
        with tempfile.TemporaryDirectory() as f, patch('expanded.environment.PolicyEnvironment',side_effect=ValueError('creation')):
            _,r=collect_game(Mock(),Mock(),Mock(),[],seed=1,learner_seat=0,first_player=0,max_actions=2,generator=None,ppo=PPOConfig(),diagnostic=GameCapture({},f,'create'))
            self.assertTrue(r['failed'])

    def test_evaluation_failure_boundary_with_fake_environment(self):
        class Env(FakeEnvironment):fail=True
        with tempfile.TemporaryDirectory() as f, patch('expanded.environment.PolicyEnvironment',Env), patch('hearthstone_sim.neural.runner.policy_action',return_value=(0,-1,0)), patch('hearthstone_sim.neural.evaluation.heuristic_action',return_value=0):
            r=evaluate(Mock(),{},Mock(),{'A':'fake'},{},config=EvaluationConfig(games_per_opponent=3),max_actions=2,emit=lambda *a,**kw:None,folder=f,failure_repeats=2)
            self.assertEqual(r['summary']['failed'],2);self.assertTrue(r['stopped'])
            self.assertEqual(len(list((Path(f)/'failures').glob('*.json'))),2)

    def test_replacement_resume_and_threshold_stop_without_updates(self):
        config=ModelConfig(width=16,heads=2,layers=1,feedforward=32)
        seen=[]
        def scripted(*args,**kw):
            seen.append((kw['seed'],kw['learner_seat'],kw['first_player'],args[3]))
            if len(seen)==1:
                try:raise RuntimeError('fake')
                except RuntimeError as e:return [],kw['diagnostic'].failure(e)
            return [],dict(terminated=True,truncated=False,reward=1,actions=1)
        with tempfile.TemporaryDirectory() as f, patch('hearthstone_sim.neural.runner.collect_game',side_effect=scripted), patch('hearthstone_sim.neural.runner.update',side_effect=AssertionError('must not update')):
            ck=run(iterations=1,games_per_iteration=1,max_actions=2,seed=7,output=f,model_config=config,allow_training=True,emit=lambda e:None)
            p=load(ck['path'],prepare(model_config=config)[2]);self.assertEqual(p['safety']['failed'],1);self.assertEqual(p['safety']['seed_position'],2)
            self.assertEqual(seen[0][1:],seen[1][1:]);self.assertEqual([x[0] for x in seen],[7,8])
            ck2=run(iterations=1,games_per_iteration=1,max_actions=2,seed=7,output=f,model_config=config,allow_training=True,resume=ck['path'],emit=lambda e:None)
            p2=load(ck2['path'],prepare(model_config=config)[2]);self.assertEqual(p2['safety']['attempted'],3);self.assertEqual(seen[-1][0],9)
            with patch('hearthstone_sim.neural.runner.collect_game',return_value=([],dict(failed=True,signature='X:h',terminated=False,truncated=False,reward=None))):
                stop=run(iterations=1,games_per_iteration=1,max_actions=2,seed=7,output=f,model_config=config,allow_training=True,failure_repeats=1,emit=lambda e:None)
            self.assertTrue(load(stop['path'],prepare(model_config=config)[2])['stopped'])

    def test_evaluation_threshold_checkpoint_preserves_counters(self):
        class Env(FakeEnvironment):fail=True
        config=ModelConfig(width=16,heads=2,layers=1,feedforward=32)
        with tempfile.TemporaryDirectory() as f, patch('expanded.environment.PolicyEnvironment',Env), patch('hearthstone_sim.neural.runner.policy_action',return_value=(0,-1,0)), patch('hearthstone_sim.neural.evaluation.heuristic_action',return_value=0), patch('hearthstone_sim.neural.runner.collect_game',side_effect=AssertionError('no collection')):
            ck=run(iterations=1,games_per_iteration=1,max_actions=2,seed=7,output=f,model_config=config,allow_training=True,evaluation=EvaluationConfig(games_per_opponent=3),failure_repeats=2,emit=lambda e:None)
            payload=load(ck['path'],prepare(model_config=config)[2])
            self.assertEqual(payload['evaluation_safety']['failed'],2)
            self.assertEqual(payload['global_game'],0)

    def test_trial_evaluates_after_200_and_400_with_collection_mocked(self):
        config=ModelConfig(width=16,heads=2,layers=1,feedforward=32)
        report=dict(by_opponent={},by_deck={})
        with tempfile.TemporaryDirectory() as f, patch('hearthstone_sim.neural.runner.collect_game',return_value=([],dict(terminated=True,truncated=False,reward=1,actions=1))), patch('hearthstone_sim.neural.runner.update',side_effect=AssertionError('no updates')), patch('hearthstone_sim.neural.runner.evaluate',return_value=report) as ev:
            ck=run(iterations=50,games_per_iteration=8,max_actions=2,seed=7,output=f,model_config=config,allow_training=True,evaluation=EvaluationConfig(),evaluation_at=(200,400),checkpoint_every_iterations=16,emit=lambda e:None)
            self.assertEqual(ev.call_count,3)
            history=json.loads((Path(ck['path']).parent/'monitoring-history.json').read_text())
            self.assertEqual([r['global_game'] for r in history],[0,200,400])

    def test_resumed_baseline_is_saved_and_labeled_before_any_update(self):
        config=ModelConfig(width=16,heads=2,layers=1,feedforward=32)
        with tempfile.TemporaryDirectory() as f, patch('hearthstone_sim.neural.runner.collect_game',return_value=([],dict(terminated=True,truncated=False,reward=1,actions=1))), patch('hearthstone_sim.neural.runner.update',side_effect=AssertionError('no updates')), patch('hearthstone_sim.neural.runner.evaluate',side_effect=lambda *a,**k:dict(by_opponent={},by_deck={})):
            args=dict(iterations=1,games_per_iteration=1,max_actions=2,seed=7,output=f,model_config=config,allow_training=True,evaluation=EvaluationConfig(),emit=lambda e:None)
            first=run(**args)
            resumed=run(**args,resume=first['path'])
            report=json.loads((Path(resumed['path']).parent/'evaluation-000000.json').read_text())
            self.assertEqual(report['evaluation_kind'],'resumed-start')
            self.assertEqual(report['run_games'],0)
            self.assertEqual(report['global_game'],1)

    def test_medium_schedule_settings_and_batch_boundaries(self):
        import ast
        doc=json.loads(Path('notebooks/16_long_transformer_training.ipynb').read_text())
        source='\n'.join(''.join(c['source']) for c in doc['cells'] if c['cell_type']=='code')
        ast.parse(source)
        self.assertIn("['--evaluation-at', '512', '1024', '1536', '2000']",source)
        self.assertEqual([n//8 for n in (512,1024,1536,2000)],[64,128,192,250])

    def test_summary_cli_reads_only_synthetic_file(self):
        import subprocess,sys
        with tempfile.TemporaryDirectory() as f:
            path=Path(f)/'trace.json';path.write_text(json.dumps(dict(private_diagnostic=dict(events=[dict(turn=1,event='damage',amount=2)]),outcome=dict(end_reason='synthetic'))))
            out=subprocess.run([sys.executable,'tools/summarize_trace.py',str(path)],capture_output=True,text=True,check=True)
            self.assertIn('damage',out.stdout);self.assertIn('synthetic',out.stdout)

    def test_notebook_defaults_and_syntax(self):
        import ast
        d=json.loads(Path('notebooks/16_long_transformer_training.ipynb').read_text())
        text='\n'.join(''.join(c['source']) for c in d['cells'] if c['cell_type']=='code')
        ast.parse(text);self.assertIn('EVALUATE_AT_START = True',text);self.assertIn('medium',text)
        self.assertIn("['--evaluation-at', '200', '400']",text)

    def test_dashboard_failure_timing_and_exposure(self):
        d=Dashboard(8);d.consume(dict(event='iteration_saved',metrics={'optimizer_steps':0},safety={'attempted':3,'failed':1,'approximations':{'A':{'bashana':1}}},timing={'engine_seconds':1,'ppo_seconds':0}))
        self.assertIn('Failed: 1',d.html());self.assertIn('bashana',d.html());self.assertIn('engine_seconds',d.html())
