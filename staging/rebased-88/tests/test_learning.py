import copy
import json
import math
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from engine import Game, Action
from engine.cards import registry, supported_pool
from engine.experiment import random_policy
from lab import population
from learner.policy import Policy, Adam, FEATURE_NAMES, encode, probabilities, log_gradient
from learner.training import train, evaluate, make_pools, episode, score_summary


class LearningTests(unittest.TestCase):
    def test_log_gradient_matches_finite_difference(self):
        vectors=[[(0,1),(1,0.5)],[(0,-0.25),(1,2)]]
        w=[0.0]*len(FEATURE_NAMES); w[0]=0.3; w[1]=-0.2
        p=probabilities(w,vectors); gradient=log_gradient(vectors,p,0)
        for i in (0,1):
            plus=w.copy(); minus=w.copy(); plus[i]+=1e-6; minus[i]-=1e-6
            numeric=(math.log(probabilities(plus,vectors)[0])-math.log(probabilities(minus,vectors)[0]))/2e-6
            self.assertAlmostEqual(gradient[i],numeric,places=7)

    def test_entropy_gradient_matches_finite_difference(self):
        vectors=[[(0,1)],[(1,1)]]
        w=[0.0]*len(FEATURE_NAMES); w[0]=2
        p=probabilities(w,vectors)
        full=log_gradient(vectors,p,0,entropy=1)
        plain=log_gradient(vectors,p,0)
        def entropy(weights): return -sum(x*math.log(x) for x in probabilities(weights,vectors))
        for i in (0,1):
            plus=w.copy(); minus=w.copy(); plus[i]+=1e-6; minus[i]-=1e-6
            numeric=(entropy(plus)-entropy(minus))/2e-6
            self.assertAlmostEqual(full[i]-plain[i],numeric,places=7)

    def test_rewarded_action_becomes_more_likely(self):
        policy=Policy(seed=1); optimizer=Adam(len(FEATURE_NAMES)); vectors=[[(0,1)],[(1,1)]]
        before=probabilities(policy.weights,vectors)[0]
        previous=before
        for _ in range(20):
            gradient=log_gradient(vectors,probabilities(policy.weights,vectors),0)
            optimizer.update(policy,gradient,0.01)
            current=probabilities(policy.weights,vectors)[0]
            self.assertGreater(current,previous)
            previous=current
        self.assertGreater(previous,before)

    def test_softmax_stable_and_finite(self):
        weights=[0.0]*len(FEATURE_NAMES); weights[0]=10000; weights[1]=9999
        p=probabilities(weights,[[(0,1)],[(1,1)]])
        self.assertAlmostEqual(sum(p),1)
        self.assertTrue(all(math.isfinite(x) for x in p))

    def test_initialization_repeatable_and_export_round_trip(self):
        p=Policy(7)
        self.assertEqual(p.weights,Policy(7).weights)
        self.assertNotEqual(p.weights,Policy(8).weights)
        self.assertEqual(p.weights,Policy.restore(json.loads(json.dumps(p.export()))).weights)
        invalid=p.export(); invalid['features'][0]='changed'
        with self.assertRaises(ValueError): Policy.restore(invalid)

    def test_nonfinite_weights_and_gradient_rejected(self):
        weights=[0.0]*len(FEATURE_NAMES); weights[0]=float('nan')
        with self.assertRaises(ValueError): Policy(weights=weights)
        with self.assertRaises(ValueError): Adam(len(FEATURE_NAMES)).update(Policy(),weights,0.01)

    def test_training_monitor_and_test_decks_disjoint(self):
        pools=make_pools(42)
        keys=[{tuple(d['cards']) for d in pool} for pool in pools]
        self.assertFalse(keys[0]&keys[1] or keys[0]&keys[2] or keys[1]&keys[2])

    def test_features_use_only_observable_information(self):
        decks=population(supported_pool(),1,42)
        g=Game([decks[0]['cards'],decks[1]['cards']],[tuple(d['runes'].values()) for d in decks[:2]])
        g.step(Action('mulligan')); g.step(Action('mulligan'))
        observation=g.observe(0)
        before=encode(observation,registry())
        observation['players'][1]['hand']=['DO NOT READ']
        observation['players'][1]['deck']=['DO NOT READ']
        observation['players'][1]['runes']=['DO NOT READ']
        observation['players'][0]['deck']=['DO NOT READ']
        self.assertEqual(before,encode(observation,registry()))

    def test_policy_actions_are_legal_and_eval_does_not_update(self):
        policy=Policy(); before=policy.export(); pools=make_pools(42)
        result=evaluate(policy,None,pools[1],4,777)
        self.assertEqual(result['games'],4)
        self.assertEqual(before,policy.export())
        result2=evaluate(policy,None,pools[1],4,777)
        self.assertEqual(result,result2)

    def test_episode_gradient_is_nonzero_and_finite(self):
        result=episode(Policy(),None,make_pools(42)[0],121,0,learn=True)
        self.assertGreater(result['decisions'],0)
        self.assertTrue(any(abs(x)>1e-8 for x in result['gradient']))
        self.assertTrue(all(math.isfinite(x) for x in result['gradient']))

    def test_resume_matches_uninterrupted_training_exactly(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            partial=train(2,2,2,9,output_dir=a)
            resumed=train(4,2,2,9,output_dir=a)
            direct=train(4,2,2,9,output_dir=b)
            self.assertEqual(resumed['policy'].weights,direct['policy'].weights)
            self.assertEqual(resumed['state']['optimizer'],direct['state']['optimizer'])
            self.assertEqual(resumed['state']['evaluations'],direct['state']['evaluations'])
            self.assertEqual(resumed['state']['results'],direct['state']['results'])
            self.assertTrue(Path(partial['directory'],'model_000002.json').exists())
            self.assertTrue(Path(resumed['directory'],'model_000004.json').exists())
            again=train(4,2,2,9,output_dir=a)
            self.assertEqual(resumed['policy'].weights,again['policy'].weights)

    def test_interrupt_resumes_at_last_completed_episode(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            def stop(state):
                if state['phase']=='training' and state['completed']==2: raise KeyboardInterrupt()
            with self.assertRaises(KeyboardInterrupt): train(4,2,2,21,output_dir=a,progress=stop)
            resumed=train(4,2,2,21,output_dir=a)
            direct=train(4,2,2,21,output_dir=b)
            self.assertEqual(resumed['policy'].weights,direct['policy'].weights)
            self.assertEqual(resumed['state']['evaluations'],direct['state']['evaluations'])

    def test_crash_does_not_commit_partial_update(self):
        with tempfile.TemporaryDirectory() as a:
            real_update=Adam.update
            def bad_update(optimizer,policy,gradient,rate):
                real_update(optimizer,policy,gradient,rate)
                raise RuntimeError('failure during update')
            with patch.object(Adam,'update',bad_update):
                with self.assertRaises(RuntimeError): train(2,2,2,21,output_dir=a)
            saved=json.loads(next(Path(a).glob('*/checkpoint.json')).read_text())
            self.assertEqual(saved['completed'],0)
            self.assertEqual(saved['optimizer']['steps'],0)
            self.assertEqual(saved['policy'],saved['initial'])

    def test_summary_and_draw_accounting(self):
        r=score_summary([1,-1,0,1])
        self.assertEqual((r['wins'],r['losses'],r['draws'],r['win_rate'],r['score']),(2,1,1,0.5,0.625))
        self.assertLessEqual(r['win_interval'][0],0.5)
        self.assertGreaterEqual(r['win_interval'][1],0.5)

    def test_invalid_configuration_fails(self):
        for args in [dict(total_games=1),dict(eval_games=3),dict(learning_rate=float('nan')),
                     dict(seed=-1),dict(entropy_bonus=-1)]:
            with self.assertRaises(ValueError): train(**args)

if __name__=='__main__': unittest.main()
