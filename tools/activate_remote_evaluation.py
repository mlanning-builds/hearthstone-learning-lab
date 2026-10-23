"""Owner-triggered activation only after remote equivalence and an idle trainer."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
STAGE=ROOT/'runs/prepared_fixes/remote-evaluation';QUEUE=ROOT/'runs/remote_evaluation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--activate',action='store_true');args=parser.parse_args()
 manifest=json.loads((STAGE/'manifest.json').read_text());prep=json.loads((QUEUE/'preparation.json').read_text())
 marker=QUEUE/'verified-worker.json';ready=marker.exists() and json.loads(marker.read_text())['compatibility']==prep['compatibility']
 if not args.activate:print(json.dumps(dict(remote_verified=ready,training_started=False)));return
 from tools.learning_rate_comparison import active_training
 if active_training():raise RuntimeError('Current run is active. No live sources or saved models were changed.')
 if not ready:raise RuntimeError('Start the MacBook worker and pass its fixed-case equivalence check first. Training has not started.')
 from tools.long_training_campaign import acquire_campaign_lock,CAMPAIGN
 lock=acquire_campaign_lock(CAMPAIGN/'active.lock')
 try:
  rows=manifest['files']
  if all(sha(ROOT/r['path'])==r['after_sha256'] for r in rows):print('Remote evaluation already installed.');return
  for r in rows:
   if sha(STAGE/r['path'])!=r['after_sha256'] or sha(ROOT/r['path'])!=r['before_sha256']:raise ValueError('Sources changed; rebase and review remote patch before activation')
  originals={r['path']:(ROOT/r['path']).read_bytes() if (ROOT/r['path']).exists() else None for r in rows}
  backup=STAGE/'activation-backup'
  for rel,raw in originals.items():
   if raw is not None:
    path=backup/rel;path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():path.write_bytes(raw)
  try:
   for r in rows:
    target=ROOT/r['path'];temp=target.with_suffix('.remote-partial');temp.write_bytes((STAGE/r['path']).read_bytes());temp.replace(target)
   from hearthstone_sim.neural.checkpoints import code_digest
   if code_digest()!=manifest['next_neural_code']:raise ValueError('Installed remote source fingerprint mismatch')
  except BaseException:
   for rel,raw in originals.items():
    path=ROOT/rel
    if raw is None:path.unlink(missing_ok=True)
    else:path.write_bytes(raw)
   raise
  print('Remote evaluation activated. No checkpoint files changed; campaign preflight preserves progress in a verified migration copy.')
 finally:lock.close()

if __name__=='__main__':main()
