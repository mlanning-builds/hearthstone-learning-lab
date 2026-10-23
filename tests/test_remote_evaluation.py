"""No games, learning, network listeners or changes to live training."""
import importlib.util,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from dataclasses import dataclass
import torch
from tools.remote_evaluation_worker import validate_result,case_hash
from hearthstone_sim.neural.evaluation import EvaluationConfig,result_summary
from hearthstone_sim.neural.encoding import EncoderConfig
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('hearthstone_sim.neural._prepared_remote',ROOT/'runs/prepared_fixes/remote-evaluation/hearthstone_sim/neural/remote_eval.py')
remote=importlib.util.module_from_spec(spec);spec.loader.exec_module(remote)
@dataclass
class Deck:
 hero_class:str='MAGE'
 cards:tuple=('fixture',)
@dataclass
class Config:
 width:int=1
class Tiny(torch.nn.Linear):
 def __init__(self):super().__init__(1,1);self.config=Config()
class Encoder:
 config=EncoderConfig()

class Checks(unittest.TestCase):
 def test_unverified_macbook_blocks_remote_mode(self):
  with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,HEARTHSTONE_EVALUATION_QUEUE=folder):
   with self.assertRaisesRegex(RuntimeError,'has not passed'):
    remote.RemoteMonitor(folder,{},None,{},None,1000,{}, {})
 def test_queue_freezes_weights_then_imports_only_evaluation_reports(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);queue=root/'queue';queue.mkdir();(queue/'verified-worker.json').write_text(json.dumps({'compatibility':{'engine':'fixture'}}))
   panel=root/'panel.json';panel.write_text('{}')
   with patch.dict(os.environ,HEARTHSTONE_EVALUATION_QUEUE=str(queue)):
    monitor=remote.RemoteMonitor(root/'training',{'engine':'fixture'},panel,{'a':Deck(),'b':Deck()},EvaluationConfig(16,2,10000),1000,{},dict(attempted=0,failed=0,completed=0,seed_position=0,signatures={},by_pair={},approximations={},approximation_proxies={}))
    model=Tiny();before={k:v.clone() for k,v in model.state_dict().items()}
    job=monitor.enqueue(model,{'anchor':Tiny()},Encoder(),16,1024,1024,False,{'path':'existing-immutable.pt'},False)
    pack=torch.load(queue/'jobs'/job/'payload.pt',weights_only=True)
    self.assertNotIn('optimizer',pack)
    for k,v in before.items():self.assertTrue(torch.equal(v,pack['learner'][k]))
    meta=json.loads((queue/'jobs'/job/'job.json').read_text())
    rows=[dict(row,terminated=True,truncated=False,reward=1,actions=1) for row in meta['cases']]
    report=dict(games=rows,training_updates=0,stopped=None,summary=result_summary(rows),safety=pack['safety'],by_opponent={},by_deck={},**meta['report_metadata'])
    result=dict(job_id=job,payload_sha256=meta['payload_sha256'],report=report)
    validate_result(meta,result);(queue/'jobs'/job/'result.json').write_text(json.dumps(result))
    events=[];monitor.reap(lambda *a,**k:events.append((a,k)));monitor.reap(lambda *a,**k:events.append((a,k)))
    self.assertEqual(len(events),1)
    for k,v in before.items():self.assertTrue(torch.equal(v,model.state_dict()[k]))
    self.assertTrue((root/'training/evaluation-000016-remote.json').exists())
 def test_rejects_wrong_snapshot_incomplete_schedule_and_changed_golden_result(self):
  row=dict(opponent='heuristic',seed=1,learner_deck='a',opponent_deck='b',learner_seat=0,first_player=1)
  game=dict(row,terminated=True,truncated=False,reward=1)
  meta=dict(job_id='a',payload_sha256='b',expected_cases=1,cases=[row],golden_cases_sha256=case_hash([game]))
  value=dict(job_id='a',payload_sha256='b',report=dict(training_updates=0,games=[game],summary=result_summary([game])))
  validate_result(meta,value)
  with self.assertRaises(ValueError):validate_result(meta,dict(value,job_id='wrong'))
  value['report']['games'][0]['reward']=-1;value['report']['summary']=result_summary([game])
  with self.assertRaises(ValueError):validate_result(meta,value)

if __name__=='__main__':unittest.main()
