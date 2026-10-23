"""Read-only run observer; writes only its own HTML status page. Stops with trainer."""
import argparse,html,json,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(path):
 try:return json.loads(path.read_text())
 except (OSError,ValueError):return None

def main():
 p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--run',required=True);p.add_argument('--watch',action='store_true');args=p.parse_args()
 folder=ROOT/'runs/all_class_campaign/training'/args.run
 output=ROOT/'notebooks/live_training_status.html'
 while True:
  try:os.kill(args.pid,0);active=True
  except ProcessLookupError:active=False
  cfg=read(folder/'config.json');evaluation=None;progress='Waiting for saved progress';failures=list(folder.rglob('failure-*.json'))
  latest=max(folder.glob('iteration-*.json'),default=None);batch=read(latest) if latest else None
  reports=sorted(folder.glob('evaluation-0*.json'));report=read(reports[-1]) if reports else None
  if batch:
   progress='Latest saved training batch: '+str(batch['iteration'])+' · '+str(len(batch['games']))+' games · learning '+str(round(batch['timing']['ppo_seconds'],1))+' seconds'
  if cfg:
   for contract in sorted((folder.parent/'evaluation-cache').glob('*/contract.json'),key=lambda f:f.stat().st_mtime,reverse=True):
    identity=read(contract)
    if identity and identity['engine']==cfg['compatibility']['engine']:
     cases=list(contract.parent.glob('case-*.json'));total=identity['config']['games_per_opponent']*(1+len(identity['opponents']))
     progress='Evaluation: '+str(len(cases))+' / '+str(total)+' cases saved' if not report or not batch else progress
     break
  status='RUNNING — evaluation/training process active' if active else 'Trainer process has stopped — inspect its latest report'
  body=f'''<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="5"><title>Live Hearthstone run</title></head>
<body style="background:#101820;color:#eef4fa;font:20px system-ui;padding:40px"><h1>Live Hearthstone run</h1><h2>{html.escape(status)}</h2><p style="font-size:28px">{html.escape(progress)}</p><p>Saved failure diagnostics in this run: {len(failures)}</p><p>176 decks · six learning threads · four workers</p><p>Run: {html.escape(args.run)}</p><p>Updated {time.strftime('%H:%M:%S %Z')} · refreshes every five seconds</p><p>This page only reads saved results. It does not start, stop or change training.</p></body></html>'''
  temp=output.with_suffix('.partial');temp.write_text(body);temp.replace(output)
  if not args.watch or not active:return
  time.sleep(5)

if __name__=='__main__':main()
