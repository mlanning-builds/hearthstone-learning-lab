"""Research fixtures only. No optimizer.step, self-play or evaluation games."""
import ast
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import torch
from hearthstone_sim.research.models import make_model
from hearthstone_sim.research import comparison as c
from hearthstone_sim.neural.model import ModelConfig
from hearthstone_sim.neural.checkpoints import save,load,SCHEMA

ENCODED=dict(state=[[(1,1.),(2,.5)],[(3,1.)]],actions=[[(4,1.)],[(5,1.)],[(6,1.)]])
class ResearchTests(unittest.TestCase):
    def test_same_action_and_value_interface_and_finite_gradients(self):
        cfg=ModelConfig(buckets=256,width=16,heads=2,layers=1,feedforward=32)
        for name in ('mlp','transformer'):
            model=make_model(name,cfg);logits,values=model([ENCODED,ENCODED])
            self.assertEqual([len(x) for x in logits],[3,3]);self.assertEqual(tuple(values.shape),(2,))
            loss=sum(x.square().mean() for x in logits)+values.square().mean();loss.backward()
            self.assertTrue(all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None))
    def test_no_attention_in_mlp(self):
        m=make_model('mlp',ModelConfig(buckets=256,width=16,heads=2,layers=1,feedforward=32))
        self.assertFalse(any(isinstance(x,torch.nn.MultiheadAttention) for x in m.modules()))
    def test_equal_balanced_evaluation_cases(self):
        names=['class-%s'%i for i in range(11)];cases=c.evaluation_schedule(names)
        self.assertEqual(len(cases),44)
        for n in names:
            self.assertEqual(sum(a==n for a,b,s,f in cases),4)
            self.assertEqual(sum(b==n for a,b,s,f in cases),4)
        self.assertEqual(len(set(cases)),44)
    def test_results_do_not_treat_caps_or_errors_as_losses(self):
        report=c.summarize([dict(terminated=True,reward=1),dict(terminated=True,reward=-1),dict(truncated=True),dict(failed=True)])
        self.assertEqual(report['score'],.5);self.assertEqual(report['finished'],2);self.assertEqual(report['attempts'],4)
        self.assertEqual(report['failed'],1);self.assertEqual(report['capped'],1)
    def test_no_launch_without_owner_activation(self):
        with self.assertRaises(ValueError):c.run()
    def test_latest_numeric_checkpoint_and_integrity(self):
        with tempfile.TemporaryDirectory() as f,patch.object(c,'OUTPUT',Path(f)):
            folder=Path(f)/'mlp';folder.mkdir()
            for count,serial in ((64,0),(128,0),(128,1)):
                save(folder/('checkpoint-%06d-%06d.pt'%(count,serial)),dict(schema=SCHEMA,compatibility={'architecture':'mlp'},x=torch.tensor([count])))
            p=c.latest('mlp');self.assertEqual(p.name,'checkpoint-000128-000001.pt')
            with self.assertRaises(ValueError):load(p,{'architecture':'transformer'})
    def test_config_is_bounded_and_does_not_use_old_weights_for_learners(self):
        cfg=c.config();self.assertEqual(cfg['chunk_games_per_model'],128);self.assertEqual(cfg['soft_limit_minutes'],90)
        self.assertFalse(cfg['tactical_lessons']);self.assertEqual(cfg['training_seeds'],[113])
    def test_fresh_model_does_not_mutate_saved_weights(self):
        cfg=ModelConfig(buckets=256,width=16,heads=2,layers=1,feedforward=32)
        teacher=make_model('transformer',cfg);before={k:v.clone() for k,v in teacher.state_dict().items()}
        make_model('mlp',cfg)([ENCODED]);self.assertTrue(all(torch.equal(v,before[k]) for k,v in teacher.state_dict().items()))
if __name__=='__main__':unittest.main()

class ResearchResumeTests(unittest.TestCase):
    def test_paused_partial_batch_resumes_and_both_arms_reach_same_budget_without_learning(self):
        cfg=c.config();small=ModelConfig(buckets=256,width=16,heads=2,layers=1,feedforward=32)
        s=dict(fingerprint={},opponent=dict(path='fake',sha256='fake'),config=cfg)
        decks={'class-'+str(i):'deck-'+str(i) for i in range(11)}
        teacher_state=make_model('transformer').state_dict()
        training=[];updates=[];paused=[False]
        def fake_collect(*args,**kw):
            meta=kw['diagnostic'].metadata
            if meta['phase']=='training':
                training.append((meta['architecture'],meta['game'],kw['seed']))
                trajectory=[dict(encoded=ENCODED,action=0,logp=-1.,value=0.,advantage=1.,**{'return':1.})]
                if len(training)==1:paused[0]=True
            else:trajectory=[]
            return trajectory,dict(terminated=True,truncated=False,failed=False,reward=1,actions=1)
        def fake_update(model,optimizer,samples,ppo,shuffle):
            updates.append(len(samples));return dict(optimizer_steps=0,samples=len(samples))
        with tempfile.TemporaryDirectory() as folder,patch.object(c,'OUTPUT',Path(folder)),patch.object(c,'make_model',side_effect=lambda name:make_model(name,small)),patch('tools.long_training_campaign.source_payload',return_value=dict(model=teacher_state)),patch.object(c,'collect_game',side_effect=fake_collect),patch.object(c,'update',side_effect=fake_update),patch.object(c.time,'monotonic',side_effect=lambda:2. if paused[0] else 0.):
            # The fake clock expires after one fake training decision; no actual games or updates run.
            c._run_locked(s,decks,cfg,1.,lambda e:None)
            cp=load(c.latest('mlp'),c.compatibility(s,'mlp'))
            self.assertEqual(cp['games'],1);self.assertEqual(len(cp['pending_samples']),1)
            paused[0]=False
            final=c._run_locked(s,decks,cfg,float('inf'),lambda e:None)
            self.assertTrue(final['matched_games']);self.assertEqual(updates,[64,64,64,64])
            for name in ('mlp','transformer'):
                payload=load(c.latest(name),c.compatibility(s,name));self.assertEqual(payload['games'],128)
                self.assertEqual([index for arch,index,seed in training if arch==name],list(range(128)))
            self.assertEqual(len(list(Path(folder).glob('round-*.json'))),1)
