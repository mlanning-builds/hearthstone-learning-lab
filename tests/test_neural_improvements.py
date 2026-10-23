"""Preparation checks only: all learning and self-play entrypoints are mocked."""
import tempfile
import unittest
from unittest.mock import patch
import torch
from hearthstone_sim._bootstrap import activate
activate()
from hearthstone_sim.neural.tactical import VERSION, build_lessons, warmup
from hearthstone_sim.neural.runner import run, prepare
from hearthstone_sim.neural.model import ModelConfig, TransformerPolicyValue
from hearthstone_sim.neural.checkpoints import load
from hearthstone_sim.neural.ppo import rollout_diagnostics

class ImprovedLearningTests(unittest.TestCase):
    def test_lessons_are_public_legal_and_cover_six_skills(self):
        lessons=build_lessons();self.assertEqual(len(lessons),24)
        self.assertEqual(len(set(x['kind'] for x in lessons)),6)
        for lesson in lessons:
            d=lesson['decision'];self.assertEqual(d['actions'],d['observation']['legal_actions'])
            self.assertTrue(lesson['answers'])
            for answer in lesson['answers']:
                self.assertIn(d['actions'][answer]['kind'],('play','attack'))
            self.assertNotIn('private_game',d)
    def test_lesson_training_requires_explicit_activation(self):
        with self.assertRaisesRegex(ValueError,'activation'):
            warmup(None,None,None,steps=1)
    def test_complete_rollout_diagnostics_do_not_change_weights(self):
        model=TransformerPolicyValue(ModelConfig(width=16,heads=2,layers=1,feedforward=32)).eval()
        encoded=dict(state=[[(1,1.)]],actions=[[(2,1.)],[(3,1.)]])
        with torch.no_grad():logits,_=model([encoded]);logp=logits[0].log_softmax(-1)[0].item()
        old={k:v.clone() for k,v in model.state_dict().items()}
        result=rollout_diagnostics(model,[dict(encoded=encoded,action=0,logp=logp,**{'return':r}) for r in (-1,1)],2)
        self.assertAlmostEqual(result['rollout_kl_after'],0,places=6)
        self.assertTrue(all(torch.equal(v,old[k]) for k,v in model.state_dict().items()))
    def test_heuristic_mixture_and_lesson_resume_without_actual_learning(self):
        config=ModelConfig(width=16,heads=2,layers=1,feedforward=32)
        with tempfile.TemporaryDirectory() as folder, patch('hearthstone_sim.neural.tactical.warmup',return_value=dict(completed=4,version=VERSION)) as teach, patch('hearthstone_sim.neural.runner.collect_game',return_value=([],dict(terminated=True,truncated=False,reward=1,actions=1))) as collect, patch('hearthstone_sim.neural.runner.update',side_effect=AssertionError('No optimizer updates allowed')):
            args=dict(iterations=1,games_per_iteration=1,max_actions=1,seed=7,output=folder,model_config=config,self_play_fraction=0,heuristic_fraction=1,tactical_steps=4,allow_training=True,emit=lambda e:None)
            first=run(**args);second=run(**args,resume=first['path'])
            self.assertEqual(teach.call_count,1)
            self.assertTrue(all(c.kwargs.get('heuristic_opponent') for c in collect.call_args_list))
            state=load(second['path'],prepare(model_config=config)[2])
            self.assertEqual(state['tactical_state']['completed'],4)

    def test_refresher_state_is_saved_and_not_repeated_after_resume(self):
        from pathlib import Path
        from hearthstone_sim.neural.checkpoints import save
        from tools.migrate_400_game_checkpoint import equal
        config=ModelConfig(width=16,heads=2,layers=1,feedforward=32)
        with tempfile.TemporaryDirectory() as folder, patch('hearthstone_sim.neural.tactical.warmup',return_value=dict(completed=128,version=VERSION)) as teach, patch('hearthstone_sim.neural.runner.collect_game',return_value=([],dict(terminated=True,truncated=False,reward=1,actions=1))), patch('hearthstone_sim.neural.runner.update',side_effect=AssertionError('No optimizer updates allowed')):
            args=dict(iterations=1,games_per_iteration=1,max_actions=1,seed=7,output=folder,model_config=config,self_play_fraction=0,heuristic_fraction=1,tactical_steps=128,allow_training=True,emit=lambda e:None)
            first=run(**args)
            compat=prepare(model_config=config)[2]
            original=load(first['path'],compat)
            original.update(iteration=15,global_game=15)
            fixture=save(Path(first['path']).parent/'fixture-before-refresh.pt',original)
            teach.return_value=dict(completed=16,version=VERSION)
            second=run(**args,resume=fixture['path'])
            state=load(second['path'],compat)
            self.assertEqual(state['tactical_state']['completed'],128)
            self.assertEqual(state['tactical_state']['last_refresh_iteration'],16)
            self.assertEqual(state['tactical_state']['refresh_count'],1)
            self.assertTrue(equal(original['model'],state['model']))
            self.assertTrue(equal(original['optimizer'],state['optimizer']))
            self.assertEqual(teach.call_count,2)
            third=run(**args,resume=second['path'])
            restored=load(third['path'],compat)
            self.assertEqual(restored['tactical_state'],state['tactical_state'])
            self.assertEqual(teach.call_count,2)

    def test_actual_collector_uses_heuristic_without_opponent_network(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from hearthstone_sim.neural.runner import collect_game
        from hearthstone_sim.neural.ppo import PPOConfig
        class Env:
            def __init__(self,**kw):self._game=SimpleNamespace(events=[])
            def reset(self,*a,**kw):
                return dict(actor=1,terminated=False,truncated=False,revision=1,
                    observation=dict(turn=1,players=[dict(board=[],hand=[])]*2),actions=[dict(kind='end')])
            def step(self,*a,**kw):
                return dict(terminated=True,truncated=False,steps=1,rewards=[1,-1],end_reason='scripted')
        encoder=Mock();encoder.cards={}
        with patch('expanded.environment.PolicyEnvironment',Env), patch('hearthstone_sim.neural.evaluation.heuristic_action',return_value=0) as choose, patch('hearthstone_sim.neural.runner.policy_action',side_effect=AssertionError('Opponent network must not be used')):
            samples,result=collect_game(Mock(),Mock(),encoder,['A','B'],seed=1,learner_seat=0,first_player=1,max_actions=1,generator=torch.Generator(),ppo=PPOConfig(),heuristic_opponent=True)
        self.assertFalse(result.get('failed'));self.assertEqual(samples,[]);self.assertEqual(choose.call_count,1)

    def test_lesson_objective_has_finite_derivatives_without_optimizer_step(self):
        from hearthstone_sim.neural.encoding import VisibleEncoder
        from expanded.cards import registry
        lesson=build_lessons()[0];encoder=VisibleEncoder(card_definitions=registry())
        model=TransformerPolicyValue(ModelConfig(width=16,heads=2,layers=1,feedforward=32)).eval()
        before={k:v.clone() for k,v in model.state_dict().items()}
        logits,_=model([encoder.encode(lesson['decision'])])
        loss=-torch.logsumexp(logits[0].log_softmax(-1)[lesson['answers']],dim=0)
        loss.backward()
        self.assertTrue(all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters()))
        self.assertTrue(all(torch.equal(v,before[k]) for k,v in model.state_dict().items()))
