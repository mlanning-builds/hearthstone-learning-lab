"""Explicitly budgeted random-policy trajectory collection, not training."""
import argparse
import json
from pathlib import Path
import random
import sys
import uuid


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--engine-root',type=Path,required=True)
    parser.add_argument('--episodes',type=int,required=True)
    parser.add_argument('--max-actions',type=int,required=True)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not 1<=args.episodes<=10000 or not 1<=args.max_actions<=10000:
        parser.error('Use 1..10000 episodes and actions per episode')
    sys.path.insert(0,str(args.engine_root.resolve()))
    from expanded import random_deck
    from expanded.trajectories import record_episode,save_episode
    from standard.catalog import CLASSES
    folder=args.output.resolve()/uuid.uuid4().hex;folder.mkdir(parents=True)
    receipts=[]
    for episode in range(args.episodes):
        seed=args.seed+episode
        decks=[random_deck(CLASSES[(episode+i)%len(CLASSES)],seed+1000*i) for i in (0,1)]
        policies=[];ids=[]
        for player in (0,1):
            policy_seed=seed+2000+player;rng=random.Random(policy_seed)
            policies.append(lambda d,rng=rng:rng.randrange(len(d['actions'])))
            ids.append('uniform-legal-v1:seed='+str(policy_seed))
        def progress(records):
            for record in records:
                if record['record']=='decision' and record['step']%25==0:
                    print(json.dumps(dict(event='progress',episode=episode+1,total=args.episodes,actions=record['step']+1)),flush=True)
                yield record
        records=record_episode(decks,policies,policy_ids=ids,seed=seed,
                               max_actions=args.max_actions,first_player=episode%2,experimental=True)
        receipt=save_episode(folder/f'episode-{episode:05d}.jsonl',progress(records))
        receipts.append(receipt)
        print(json.dumps(dict(event='saved',episode=episode+1,total=args.episodes,**receipt)),flush=True)
    manifest=dict(schema='hearthstone-recording-run-v1',policy='uniform random legal actions; no learning',
                  seed=args.seed,episodes=args.episodes,max_actions=args.max_actions,receipts=receipts)
    path=folder/'manifest.json';path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(event='complete',manifest=str(path),episodes=len(receipts))),flush=True)

if __name__=='__main__':main()
