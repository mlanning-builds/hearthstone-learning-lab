"""Explicitly requested, bounded experimental self-play training entry point."""
import argparse
from dataclasses import asdict
import json
import hashlib
import math
from pathlib import Path
import sys
import uuid


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--engine-root',type=Path,required=True)
    parser.add_argument('--episodes',type=int,required=True)
    parser.add_argument('--max-actions',type=int,required=True)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--learning-rate',type=float,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--experimental',action='store_true')
    parser.add_argument('--resume-receipt',type=Path)
    args=parser.parse_args()
    if not args.experimental:parser.error('Incomplete simulator requires --experimental')
    if not 1<=args.episodes<=10000 or not 1<=args.max_actions<=10000:
        parser.error('Use 1..10000 episodes and actions per episode')
    if not math.isfinite(args.learning_rate) or not 0<args.learning_rate<=1:
        parser.error('Learning rate must be finite and in (0,1]')
    sys.path.insert(0,str(args.engine_root.resolve()))
    from expanded import random_deck
    from expanded.learning import SparsePolicy
    from expanded.training import train_episode
    from expanded.checkpoints import save_policy,load_policy
    from expanded.status import code_fingerprint
    from expanded.features import SCHEMA
    from standard.catalog import CLASSES
    config=dict(schema='candidate-training-run-v2',runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),engine_fingerprint=code_fingerprint(),
                feature_schema=SCHEMA,seed=args.seed,episodes=args.episodes,
                max_actions=args.max_actions,learning_rate=args.learning_rate,
                experimental=True,full_standard=False,
                schedule='adjacent classes cycling; random implemented decks; alternating first player',
                policy='shared sparse linear policy; no opponent archive')
    policy=SparsePolicy(seed=args.seed);offset=0
    if args.resume_receipt:
        receipt_path=args.resume_receipt.resolve()
        previous=json.loads(receipt_path.read_text())
        old_config=json.loads((receipt_path.parent/'config.json').read_text())
        for key in ('schema','runner_sha256','engine_fingerprint','feature_schema','seed',
                    'max_actions','learning_rate','schedule','policy','experimental','full_standard'):
            if old_config.get(key)!=config[key]:parser.error('Resume configuration mismatch: '+key)
        checkpoint=previous['checkpoint']
        policy,metadata=load_policy(checkpoint['path'],expected_sha256=checkpoint['sha256'])
        offset=metadata['completed_episodes']
        if type(previous['episode']) is not int or previous['episode']!=offset:
            parser.error('Resume receipt episode does not match checkpoint')
        config['resumed_from']=dict(receipt=str(receipt_path),checkpoint=checkpoint)
    config['starting_episode']=offset
    folder=args.output.resolve()/uuid.uuid4().hex;folder.mkdir(parents=True)
    (folder/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    initial=save_policy(folder/'policy-initial.json',policy,completed_episodes=offset)
    print(json.dumps(dict(event='started',folder=str(folder),initial_checkpoint=initial)),flush=True)
    receipts=[]
    for local_episode in range(args.episodes):
        episode=offset+local_episode
        seed=args.seed+episode
        decks=[random_deck(CLASSES[(episode+i)%len(CLASSES)],seed+1000*i) for i in (0,1)]
        print(json.dumps(dict(event='progress',episode=local_episode+1,total=args.episodes,global_episode=episode+1)),flush=True)
        result=train_episode(policy,decks,seed=seed,max_actions=args.max_actions,
                             learning_rate=args.learning_rate,first_player=episode%2,experimental=True)
        checkpoint=save_policy(folder/f'policy-{episode+1:05d}.json',policy,completed_episodes=episode+1)
        receipt=dict(episode=episode+1,seed=seed,first_player=episode%2,
                     replay_only_decks=[asdict(d) for d in decks],result=result,checkpoint=checkpoint)
        path=folder/f'episode-{episode+1:05d}.json'
        with path.open('x') as stream:json.dump(receipt,stream,indent=2,allow_nan=False)
        receipts.append(str(path))
        print(json.dumps(dict(event='saved',episode=local_episode+1,total=args.episodes,global_episode=episode+1,receipt=str(path),
                              result=result,checkpoint=checkpoint)),flush=True)
    manifest=dict(config=config,initial_checkpoint=initial,episode_receipts=receipts,
                  final_checkpoint=checkpoint,complete=True)
    path=folder/'manifest.json'
    with path.open('x') as stream:json.dump(manifest,stream,indent=2,allow_nan=False)
    print(json.dumps(dict(event='complete',manifest=str(path))),flush=True)

if __name__=='__main__':main()
