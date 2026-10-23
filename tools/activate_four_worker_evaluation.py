"""Owner-invoked staged activation after the current run. Never launches training."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
STAGE=ROOT/'runs/prepared_fixes/four-worker-evaluation'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--activate',action='store_true')
 args=parser.parse_args()
 manifest=json.loads((STAGE/'manifest.json').read_text())
 rows=manifest['files']
 for row in rows:
  if sha(STAGE/row['path'])!=row['after_sha256']:raise ValueError('Staged source integrity failure')
  compile((STAGE/row['path']).read_text(),row['path'],'exec')
 evidence=json.loads((STAGE/'equivalence.json').read_text()) if (STAGE/'equivalence.json').exists() else {}
 required={r['path'] for r in rows if r['path'].startswith('hearthstone_sim/neural/')}
 ready=evidence.get('same_results') is True and set(evidence.get('tested_sources',{}))==required
 ready=ready and all(sha(STAGE/rel)==expected for rel,expected in evidence.get('tested_sources',{}).items())
 collection=json.loads((STAGE/'collection-equivalence.json').read_text()) if (STAGE/'collection-equivalence.json').exists() else {}
 ready=ready and collection.get('same_results') is True and collection.get('same_master_rng') is True
 ready=ready and set(collection.get('tested_sources',{}))==required
 ready=ready and all(sha(STAGE/rel)==expected for rel,expected in collection.get('tested_sources',{}).items())
 if not args.activate:
  print(json.dumps(dict(staged=True,equivalence_passed=ready,training_started=False,
                       next_neural_code=manifest['next_neural_code'])));return
 from tools.learning_rate_comparison import active_training
 if active_training():raise RuntimeError('Current training is active. No live file was changed. Wait for it to finish.')
 from tools.long_training_campaign import acquire_campaign_lock,CAMPAIGN
 lock=acquire_campaign_lock(CAMPAIGN/'active.lock')
 try:
  if not ready:raise ValueError('Serial/parallel equivalence check has not passed')
  if all(sha(ROOT/r['path'])==r['after_sha256'] for r in rows):
   print('Four-worker evaluation is already installed; no changes.');return
  for row in rows:
   if sha(ROOT/row['path'])!=row['before_sha256']:raise ValueError('Live source changed; review/rebase the staged patch first')
  originals={r['path']:(ROOT/r['path']).read_bytes() if (ROOT/r['path']).exists() else None for r in rows}
  backup=STAGE/'activation-backup';backup.mkdir(exist_ok=True)
  for rel,raw in originals.items():
   if raw is not None:
    dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():dest.write_bytes(raw)
  try:
   for row in rows:
    destination=ROOT/row['path'];temp=destination.with_suffix('.activation-partial')
    temp.write_bytes((STAGE/row['path']).read_bytes());temp.replace(destination)
   from hearthstone_sim.neural.checkpoints import code_digest
   if code_digest()!=manifest['next_neural_code']:raise ValueError('Installed neural fingerprint mismatch')
  except BaseException:
   for rel,raw in originals.items():
    dest=ROOT/rel
    if raw is None:dest.unlink(missing_ok=True)
    else:dest.write_bytes(raw)
   raise
  (STAGE/'activation.json').write_text(json.dumps(dict(installed=True,training_started=False,
     checkpoint_files_modified=False,neural_code=manifest['next_neural_code']),indent=2)+'\n')
  print('Installed evaluation and collection speed improvements. Checkpoints untouched; campaign preflight will create a verified resume copy.')
 finally:lock.close()

if __name__=='__main__':main()
