"""Run an explicit JSON comparison plan with frozen checkpoints, no training."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid


def restore_deck(data,deck_type):
    return deck_type(data['hero_class'],tuple(data['cards']),tuple(data['runes']),
                     beatrix_minion=data.get('beatrix_minion'),
                     contraband_beasts=tuple(data.get('contraband_beasts',())))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--engine-root',type=Path,required=True)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--experimental',action='store_true')
    args=parser.parse_args()
    if not args.experimental:parser.error('Incomplete simulator requires --experimental')
    plan_bytes=args.plan.read_bytes();plan=json.loads(plan_bytes)
    if plan.get('schema')!='deck-comparison-plan-v1':parser.error('Unsupported comparison plan')
    if type(plan.get('max_games')) is not int or not 1<=plan['max_games']<=10000:
        parser.error('Explicit game budget must be 1..10000')
    if type(plan.get('max_actions')) is not int or not 1<=plan['max_actions']<=10000:
        parser.error('Explicit action limit must be 1..10000')
    sys.path.insert(0,str(args.engine_root.resolve()))
    from expanded import Deck
    from expanded.frozen_policy import checkpoint_policy_factory
    from expanded.deck_comparison import compare_decks
    def decks(panel):
        return {name:restore_deck(d,Deck) for name,d in panel.items()}
    checkpoints=plan['checkpoints']
    if len(checkpoints)!=2:parser.error('Two checkpoint descriptors required')
    paths=[Path(c['path']) for c in checkpoints]
    paths=[p if p.is_absolute() else args.plan.resolve().parent/p for p in paths]
    factory,metadata=checkpoint_policy_factory(*paths,expected_sha256=[c['sha256'] for c in checkpoints])
    print(json.dumps(dict(event='started',max_games=plan['max_games'],max_actions=plan['max_actions'])),flush=True)
    result=compare_decks(decks(plan['candidates']),decks(plan['opponents']),factory,
                         seeds=plan['seeds'],max_actions=plan['max_actions'],max_games=plan['max_games'],
                         policy_id=json.dumps(metadata,sort_keys=True),experimental=True)
    result['policy_metadata']=metadata
    result['plan_sha256']=hashlib.sha256(plan_bytes).hexdigest()
    result['runner_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    folder=args.output.resolve()/uuid.uuid4().hex;folder.mkdir(parents=True)
    (folder/'plan.json').write_bytes(plan_bytes)
    encoded=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode()
    path=folder/'report.json'
    with path.open('xb') as stream:stream.write(encoded)
    receipt=dict(report=str(path),sha256=hashlib.sha256(encoded).hexdigest(),games=result['games'])
    (folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(event='complete',**receipt,ranking=result['ranking'])),flush=True)

if __name__=='__main__':main()
