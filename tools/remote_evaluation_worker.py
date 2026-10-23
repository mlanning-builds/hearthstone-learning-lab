"""MacBook evaluation-only client. Explicit --start required; no optimizer imports/steps."""
import argparse, hashlib, json, sys, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def semantic(value):
 if isinstance(value,dict):return {k:semantic(v) for k,v in value.items() if k not in ('timing','actions_per_second')}
 if isinstance(value,list):return [semantic(v) for v in value]
 return value

def case_hash(games):return hashlib.sha256(json.dumps(semantic(games),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def validate_result(meta,value):
 if value['job_id']!=meta['job_id'] or value['payload_sha256']!=meta['payload_sha256']:raise ValueError('Snapshot identity mismatch')
 report=value['report'];rows=report['games']
 if report.get('training_updates')!=0:raise ValueError('Evaluation must contain no training updates')
 if not report.get('stopped') and len(rows)!=meta['expected_cases']:raise ValueError('Incomplete evaluation')
 if len(rows)>meta['expected_cases']:raise ValueError('Extra evaluation cases')
 for row,expected in zip(rows,meta['cases']):
  if any(row.get(k)!=v for k,v in expected.items()):raise ValueError('Evaluation schedule mismatch')
  if row.get('reward') not in (-1,0,1,None):raise ValueError('Invalid reward')
 from hearthstone_sim.neural.evaluation import result_summary
 if report['summary']!=result_summary(rows):raise ValueError('Summary does not match games')
 if meta.get('golden_cases_sha256') and case_hash(rows)!=meta['golden_cases_sha256']:raise ValueError('MacBook results differ from the verified Mac mini cases')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--start',action='store_true');parser.add_argument('--once',action='store_true');parser.add_argument('--connection',type=Path,default=ROOT/'connection.json');args=parser.parse_args()
 if not args.start:print('Prepared only. Owner must start evaluation worker.');return
 cfg=json.loads(args.connection.read_text());base=cfg['url'].rstrip('/');token=cfg['token']
 import fcntl,uuid
 cache=ROOT/'runs/macbook_evaluation';cache.mkdir(parents=True,exist_ok=True)
 lock=(cache/'active.lock').open('a+')
 try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:raise RuntimeError('An evaluation worker is already running on this MacBook')
 worker_file=cache/'worker-id.txt'
 if not worker_file.exists():worker_file.write_text(uuid.uuid4().hex)
 worker_id=worker_file.read_text().strip()
 def request(path,value=None,binary=False):
  raw=None if value is None else json.dumps(value).encode()
  req=urllib.request.Request(base+path,data=raw,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','X-Worker-ID':worker_id})
  with urllib.request.urlopen(req,timeout=120) as response:
   raw=response.read();return raw if binary else json.loads(raw)
 import torch
 torch.set_num_threads(1)
 from hearthstone_sim.neural.model import ModelConfig,TransformerPolicyValue
 from hearthstone_sim.neural.encoding import EncoderConfig,VisibleEncoder
 from hearthstone_sim.neural.evaluation import EvaluationConfig,evaluate
 from hearthstone_sim.neural.runner import prepare
 from hearthstone_sim.neural.tactical import assess
 cache=ROOT/'runs/macbook_evaluation';cache.mkdir(parents=True,exist_ok=True)
 print('Evaluation worker ready. This computer never updates model weights.',flush=True)
 while True:
  try:
   meta=request('/next')
   if meta is None:time.sleep(3);continue
   job=meta['job_id'];folder=cache/job;folder.mkdir(exist_ok=True)
   payload_file=folder/'payload.pt'
   if not payload_file.exists() or hashlib.sha256(payload_file.read_bytes()).hexdigest()!=meta['payload_sha256']:
    raw=request('/payload/'+job,binary=True)
    if hashlib.sha256(raw).hexdigest()!=meta['payload_sha256']:raise ValueError('Downloaded snapshot hash mismatch')
    payload_file.write_bytes(raw)
   payload=torch.load(payload_file,map_location='cpu',weights_only=True)
   panel=folder/'decks.json';panel.write_text(payload['panel_raw'])
   decks,_,compat=prepare(panel,ModelConfig(**payload['model_config']),EncoderConfig(**payload['encoder_config']))
   if compat!=payload['compatibility']:raise ValueError('MacBook source, Torch/Python version, encoder, model or card pool differs')
   from expanded.cards import registry
   cards=registry();encoder=VisibleEncoder(EncoderConfig(**payload['encoder_config']),cards)
   def model(weights):
    network=TransformerPolicyValue(ModelConfig(**payload['model_config'])).eval();network.load_state_dict(weights);network.requires_grad_(False);return network
   learner=model(payload['learner']);anchors={n:model(w) for n,w in payload['anchors'].items()}
   safety=payload['safety']
   if meta.get('predecessor'):
    prior=request('/result/'+meta['predecessor'])
    if prior is None:raise ValueError('Missing predecessor evaluation')
    safety=prior['report']['safety']
    if prior['report'].get('stopped'):raise ValueError('Previous evaluation stopped on an engine failure; owner review required')
   def emit(*args,**kwargs):request('/heartbeat/'+job,{'alive':True})
   report=evaluate(learner,anchors,encoder,decks,cards,config=EvaluationConfig(**payload['evaluation']),
    max_actions=payload['max_actions'],emit=emit,folder=folder,iteration=payload['iteration'],
    engine_fingerprint=compat['engine'],cache_dir=cache/'evaluation-cache',safety=safety,workers=4,**payload['failure_limits'])
   if payload['tactical']:report['tactical_assessment']=assess(learner,encoder)
   report.update(payload['report_metadata'])
   value=dict(job_id=job,payload_sha256=meta['payload_sha256'],report=report)
   validate_result(meta,value);(folder/'result.json').write_text(json.dumps(value,allow_nan=False))
   request('/result/'+job,value)
   print(json.dumps(dict(event='evaluation_returned',job_id=job,summary=report['summary'])),flush=True)
   if args.once:return
  except (urllib.error.URLError,TimeoutError,OSError) as error:
   print('Connection unavailable; saved cases retained. Retrying: '+str(error),flush=True);time.sleep(10)
  except Exception as error:
   print('Evaluation blocked; owner review required: '+str(error),flush=True);raise

if __name__=='__main__':main()
