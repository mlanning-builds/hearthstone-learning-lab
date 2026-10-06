"""Bounded, streaming policy-visible trajectories; no parameter updates.

Consume the iterator explicitly. A truncated episode has no terminal training
label. Replay setup is kept in a separate header and must never be model input.
Policy randomness/checkpoint restoration remains the caller's responsibility.
"""
from copy import deepcopy
from dataclasses import asdict
from .environment import PolicyEnvironment
from .status import code_fingerprint


def record_episode(decks,policies,*,policy_ids,seed,max_actions,first_player=0,experimental=False):
    if len(policies)!=2 or not all(callable(p) for p in policies):
        raise ValueError('Exactly two policies are required')
    if len(policy_ids)!=2 or not all(isinstance(p,str) and p for p in policy_ids):
        raise ValueError('Provide two nonempty policy/checkpoint identifiers')
    env=PolicyEnvironment(experimental=experimental)
    decision=env.reset(decks,seed=seed,max_actions=max_actions,first_player=first_player)
    yield dict(record='episode',schema='hearthstone-trajectory-v1',
               fingerprint=code_fingerprint(),experimental=experimental,
               replay_only=dict(decks=[asdict(d) for d in decks],seed=seed,
                                first_player=first_player,max_actions=max_actions,
                                policy_ids=list(policy_ids)))
    while not decision['terminated'] and not decision['truncated']:
        before=deepcopy(decision)
        actor=before['actor']
        index=policies[actor](decision)
        decision=env.step(index,revision=before['revision'])
        yield dict(record='decision',step=before['steps'],actor=actor,
                   observation=before['observation'],legal_actions=before['actions'],
                   action_index=index,action=before['actions'][index])
    yield dict(record='outcome',steps=decision['steps'],terminated=decision['terminated'],
               truncated=decision['truncated'],reason=decision['end_reason'],
               terminal_rewards=decision['rewards'] if decision['terminated'] else None)


def save_episode(path,records):
    """Stream one complete episode envelope to a new JSONL file atomically.

    An action-capped episode is allowed, clearly labelled truncated. Iterator
    failures or missing outcomes never publish a final file. Existing files are
    never overwritten. Replay-only headers must be excluded from model inputs.
    """
    import hashlib
    import json
    import os
    from pathlib import Path
    import tempfile
    path=Path(path)
    if path.exists():raise FileExistsError(path)
    digest=hashlib.sha256();steps=0;header=False;outcome=None
    descriptor,temp=tempfile.mkstemp(prefix='.episode-',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(descriptor,'wb') as stream:
            for record in records:
                kind=record.get('record')
                if outcome is not None:raise ValueError('Records after outcome')
                if not header:
                    if kind!='episode' or record.get('schema')!='hearthstone-trajectory-v1':
                        raise ValueError('Missing supported episode header')
                    header=True
                elif kind=='decision':
                    index=record['action_index'];actions=record['legal_actions']
                    if record['step']!=steps or record['actor'] not in (0,1):raise ValueError('Invalid decision sequence')
                    if type(index) is not int or not 0<=index<len(actions) or record['action']!=actions[index]:
                        raise ValueError('Chosen action does not match legal candidates')
                    steps+=1
                elif kind=='outcome':
                    if record['steps']!=steps or type(record['terminated']) is not bool or type(record['truncated']) is not bool or record['terminated']==record['truncated']:
                        raise ValueError('Invalid episode outcome')
                    rewards=record['terminal_rewards']
                    if record['truncated'] and rewards is not None:raise ValueError('Truncation cannot have terminal labels')
                    if record['terminated'] and rewards not in ([1,-1],[-1,1],[0,0]):raise ValueError('Invalid terminal rewards')
                    outcome=record
                else:raise ValueError('Unexpected trajectory record')
                encoded=(json.dumps(record,sort_keys=True,allow_nan=False)+'\n').encode()
                digest.update(encoded);stream.write(encoded)
            if outcome is None:raise ValueError('Episode stream ended without an outcome')
            stream.flush();os.fsync(stream.fileno())
        os.link(temp,path)  # Atomic publication that refuses an existing destination.
        return dict(path=str(path.resolve()),sha256=digest.hexdigest(),steps=steps,
                    terminated=outcome['terminated'],truncated=outcome['truncated'])
    finally:
        os.unlink(temp)
