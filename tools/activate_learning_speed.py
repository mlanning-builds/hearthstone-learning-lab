"""Activate the checked input-reuse patch only after the owner-started run ends."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
STAGE=ROOT/'runs/prepared_fixes/learning-step-speed'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--activate',action='store_true');args=parser.parse_args()
 manifest=json.loads((STAGE/'manifest.json').read_text());evidence=json.loads((STAGE/'equivalence.json').read_text());benchmark=json.loads((STAGE/'benchmark.json').read_text())
 ready=evidence['forward_bitwise_identical'] and evidence['resumed_adam_identical'] and all(c['bitwise_identical'] for c in evidence['cases']) and all(c['bitwise_identical'] for c in benchmark['rounds'])
 for rel,expected in evidence['tested_sources'].items():ready=ready and sha(STAGE/rel)==expected
 for row in manifest['files']:
  if sha(STAGE/row['path'])!=row['after_sha256']:raise ValueError('Staged source integrity failure')
  compile((STAGE/row['path']).read_text(),row['path'],'exec')
 if not args.activate:print(json.dumps(dict(staged=True,numerical_checks_passed=ready,training_started=False)));return
 from tools.learning_rate_comparison import active_training
 if active_training():raise RuntimeError('Current run is active. No code or saved progress was changed. Wait for it to finish.')
 if not ready:raise ValueError('Exact numerical checks did not pass')
 from tools.long_training_campaign import acquire_campaign_lock,CAMPAIGN
 lock=acquire_campaign_lock(CAMPAIGN/'active.lock')
 try:
  rows=manifest['files']
  if all(sha(ROOT/r['path'])==r['after_sha256'] for r in rows):print('Learning speed patch already installed.');return
  if any(sha(ROOT/r['path'])!=r['before_sha256'] for r in rows):raise ValueError('Source changed; review/rebase before activation')
  originals={r['path']:(ROOT/r['path']).read_bytes() for r in rows}
  backup=STAGE/'activation-backup'
  for rel,raw in originals.items():
   target=backup/rel;target.parent.mkdir(parents=True,exist_ok=True)
   if not target.exists():target.write_bytes(raw)
  try:
   for r in rows:
    dest=ROOT/r['path'];temp=dest.with_suffix('.learning-partial');temp.write_bytes((STAGE/r['path']).read_bytes());temp.replace(dest)
   from hearthstone_sim.neural.checkpoints import code_digest
   if code_digest()!=manifest['next_neural_code']:raise ValueError('Installed source fingerprint mismatch')
  except BaseException:
   for rel,raw in originals.items():(ROOT/rel).write_bytes(raw)
   raise
  print('Input-reuse patch installed. Checkpoints unchanged; preflight prepares a verified resume copy.')
 finally:lock.close()

if __name__=='__main__':main()
