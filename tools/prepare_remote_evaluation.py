"""Prepare an AirDrop-ready evaluation-only MacBook bundle. Does not launch services/training."""
from pathlib import Path
import argparse,hashlib,json,secrets,shutil,sys,zipfile,difflib,re,socket,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
STAGE=ROOT/'runs/prepared_fixes/remote-evaluation'
LOCAL=ROOT/'runs/prepared_fixes/four-worker-evaluation'
QUEUE=ROOT/'runs/remote_evaluation'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def prepare():
 import torch
 from hearthstone_sim.neural.checkpoints import load,digest
 from hearthstone_sim.neural.runner import prepare as validate,match_schedule
 from tools.remote_evaluation_worker import case_hash
 from tools.evaluation_relay import atomic
 for file in (LOCAL/'hearthstone_sim/neural').glob('*.py'):
  target=STAGE/'hearthstone_sim/neural'/file.name
  if file.name!='runner.py':shutil.copyfile(file,target)
 # Include identical dashboard, with an explicit asynchronous status label.
 dashboard=(ROOT/'hearthstone_sim/neural/dashboard.py').read_text().replace('        elif kind == "evaluation_started":','        elif kind == "evaluation_queued":\n            self.status = "MacBook evaluating a frozen snapshot; training continues"\n        elif kind == "evaluation_started":')
 (STAGE/'hearthstone_sim/neural/dashboard.py').write_text(dashboard)
 files={p.name:p.read_bytes() for p in (ROOT/'hearthstone_sim/neural').glob('*.py')}
 files.update({p.name:p.read_bytes() for p in (STAGE/'hearthstone_sim/neural').glob('*.py')})
 h=hashlib.sha256()
 for name in sorted(files):h.update(name.encode());h.update(files[name])
 train=ROOT/'tools/train_neural.py';h.update(train.name.encode());h.update(train.read_bytes());fingerprint=h.hexdigest()
 campaign=(LOCAL/'tools/long_training_campaign.py').read_text();campaign=re.sub(r"APPROVED_CODE='[a-f0-9]+'","APPROVED_CODE='"+fingerprint+"'",campaign)
 (STAGE/'tools').mkdir(exist_ok=True);(STAGE/'tools/long_training_campaign.py').write_text(campaign)
 rows=[]
 for file in list((STAGE/'hearthstone_sim/neural').glob('*.py'))+[STAGE/'tools/long_training_campaign.py']:
  rel=file.relative_to(STAGE);compile(file.read_text(),str(rel),'exec')
  rows.append(dict(path=str(rel),before_sha256=sha(ROOT/rel),after_sha256=sha(file)))
 atomic(STAGE/'manifest.json',dict(files=rows,next_neural_code=fingerprint))
 QUEUE.mkdir(parents=True,exist_ok=True)
 connection=QUEUE/'connection.json'
 if not connection.exists():
  atomic(connection,dict(url='http://'+socket.gethostname()+':8766',token=secrets.token_urlsafe(32)))
  connection.chmod(0o600)
 config=json.loads(connection.read_text())
 try:config['url']='http://'+subprocess.check_output(['scutil','--get','LocalHostName'],text=True).strip()+'.local:8766'
 except (OSError,subprocess.CalledProcessError):pass
 atomic(connection,config);connection.chmod(0o600)
 panel=ROOT/'runs/all_class_campaign/panels/continuum-000005703.json';decks,_,compat=validate(panel);compat['neural_code']=fingerprint
 source=ROOT/'runs/all_class_campaign/training/3de2d5984dfd4424bdfb622be336278c/training-000432.pt'
 original=validate(panel)[2];payload=load(source,original,'dc28a93d1d48b132ec374efac1d96401cd96bbae038e5dd09897270d1241d744')
 anchors={name:load(source.parent/d['name'],original,d['sha256'])['model'] for name,d in payload['evaluation_anchors'].items()}
 report=json.loads((source.parent/'evaluation-000432.json').read_text());golden=[r for name in ['heuristic']+list(anchors) for r in report['games'] if r['opponent']==name and r['seed']<1000020004]
 job=hashlib.sha256(('macbook-equivalence:'+fingerprint).encode()).hexdigest();folder=QUEUE/'jobs'/job;folder.mkdir(parents=True,exist_ok=True)
 meta=dict(iteration=432,global_game=report['global_game'],run_games=report['run_games'],evaluation_kind='remote-equivalence',compatibility=compat)
 pack=dict(compatibility=compat,panel_raw=panel.read_text(),model_config=compat['model'],encoder_config=compat['encoder'],learner=payload['model'],anchors=anchors,
  evaluation=dict(every_iterations=16,games_per_opponent=4,seed=1000020000),max_actions=1000,
  failure_limits=dict(failure_fraction=.02,failure_min_attempts=100,failure_repeats=5),
  safety=dict(attempted=0,failed=0,completed=0,seed_position=0,signatures={},by_pair={},approximations={},approximation_proxies={}),tactical=False,iteration=432,report_metadata=meta)
 if not (folder/'payload.pt').exists():torch.save(pack,folder/'payload.pt')
 keys=('opponent','seed','learner_deck','opponent_deck','learner_seat','first_player')
 atomic(folder/'job.json',dict(job_id=job,payload_sha256=sha(folder/'payload.pt'),expected_cases=16,cases=[{k:r[k] for k in keys} for r in golden],golden_cases_sha256=case_hash(golden),report_metadata=meta))
 for old in (QUEUE/'jobs').glob('*/job.json'):
  old_meta=json.loads(old.read_text())
  if old_meta.get('golden_cases_sha256') and old_meta['job_id']!=job:
   atomic(old.parent/'superseded.json',dict(replaced_by=job))
 bundle=QUEUE/'MacBook-Evaluation';bundle.mkdir(exist_ok=True)
 # Source files and frozen card data only. No training checkpoints, optimizer states or prior run outputs.
 paths={}
 for sub in ('hearthstone_sim','configs','data','staging/rebased-88/expanded','staging/rebased-88/engine','staging/rebased-88/standard','staging/rebased-88/tests'):
  for file in (ROOT/sub).rglob('*'):
   if file.is_file() and file.suffix in ('.py','.json','.jsonl','.csv') and '__pycache__' not in file.parts:paths[str(file.relative_to(ROOT))]=file
 for file in (ROOT/'data').rglob('*'):
  if file.is_file():paths['staging/rebased-88/data/'+str(file.relative_to(ROOT/'data'))]=file
 for file in (STAGE/'hearthstone_sim/neural').glob('*.py'):paths[str(file.relative_to(STAGE))]=file
 for name in ('train_neural.py','remote_evaluation_worker.py'):paths['tools/'+name]=ROOT/'tools'/name
 paths['staging/rebased-88/lab.py']=ROOT/'staging/rebased-88/lab.py'
 paths['connection.json']=connection
 with zipfile.ZipFile(QUEUE/'MacBook-Evaluation.zip','w',zipfile.ZIP_DEFLATED) as archive:
  def command(name,body):
   info=zipfile.ZipInfo('MacBook-Evaluation/'+name);info.external_attr=0o100755 << 16;info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,body)
  for rel,file in sorted(paths.items()):archive.write(file,'MacBook-Evaluation/'+rel)
  command('SETUP.command',(ROOT/'tools/macbook_evaluation_setup.command').read_text())
  command('START-EVALUATION.command','#!/bin/zsh\nset -e\ncd "${0:A:h}"\ncaffeinate -i .venv/bin/python tools/remote_evaluation_worker.py --start\n')
  archive.writestr('MacBook-Evaluation/READ-ME.txt', 'MacBook evaluation setup\n\n1. Extract this ZIP into your home folder.\n2. Double-click SETUP.command once. It checks for matching Python 3.9.6 and installs Torch 2.8.0. If macOS blocks a script, use Finder Open or run it in Terminal with zsh. If Python is missing or has a different version, stop and report that message; do not bypass compatibility.\n3. On the Mac mini, run only the relay cell in notebook 21. This does not start or stop training.\n4. On the MacBook, double-click START-EVALUATION.command. Leave its Terminal open, plugged in, and awake.\n5. The worker first checks 16 fixed cases against the mini. Training activation stays blocked until they match.\n6. After the current notebook 18 run ends, you start the remaining notebook 21 cells on the mini.\n\nThis ZIP contains a private LAN connection key. Send it only to yourself. It contains no optimizer state or training checkpoint. Frozen evaluation weights are downloaded from the mini when needed.\n\nNo ChatGPT/Codex chat transfer is required.\n')
 atomic(QUEUE/'preparation.json',dict(bundle=str(QUEUE/'MacBook-Evaluation.zip'),probe_job=job,compatibility=compat,training_started=False,remote_verified=False))
 print('Prepared '+str(QUEUE/'MacBook-Evaluation.zip')+'; no relay, worker or training started.')

if __name__=='__main__':prepare()
