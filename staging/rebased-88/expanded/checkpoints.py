"""JSON-only policy checkpoints, bound to the exact engine and feature schema.

These resume policy weights/sampling, not an in-flight game or training schedule.
No pickle or executable deserialization. Existing snapshots are never replaced.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from .features import SCHEMA as FEATURE_SCHEMA
from .learning import SparsePolicy
from .status import code_fingerprint

SCHEMA = 'sparse-policy-checkpoint-v1'


def save_policy(path,policy,*,completed_episodes):
    if type(completed_episodes) is not int or completed_episodes<0:
        raise ValueError('Nonnegative completed episode count required')
    # Validate public mutable weights before publishing anything.
    _weights(policy.weights)
    payload=dict(schema=SCHEMA,feature_schema=FEATURE_SCHEMA,
                 engine_fingerprint=code_fingerprint(),completed_episodes=completed_episodes,
                 weights=dict(policy.weights),rng_state=policy.rng.getstate())
    encoded=(json.dumps(payload,sort_keys=True,allow_nan=False)+'\n').encode()
    path=Path(path)
    descriptor,temp=tempfile.mkstemp(prefix='.policy-',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(descriptor,'wb') as stream:
            stream.write(encoded);stream.flush();os.fsync(stream.fileno())
        os.link(temp,path)
    finally:os.unlink(temp)
    return dict(path=str(path.resolve()),sha256=hashlib.sha256(encoded).hexdigest(),
                completed_episodes=completed_episodes)


def _weights(weights):
    if not isinstance(weights,dict) or any(
            not isinstance(k,str) or type(v) not in (int,float) or not math.isfinite(v)
            for k,v in weights.items()):
        raise ValueError('Invalid checkpoint weights')


def load_policy(path,*,expected_sha256=None):
    encoded=Path(path).read_bytes()
    digest=hashlib.sha256(encoded).hexdigest()
    if expected_sha256 is not None and digest!=expected_sha256:
        raise ValueError('Checkpoint checksum mismatch')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate checkpoint field')
            result[key]=value
        return result
    def invalid_constant(value):raise ValueError('Nonfinite checkpoint constant')
    data=json.loads(encoded,object_pairs_hook=unique,parse_constant=invalid_constant)
    fields={'schema','feature_schema','engine_fingerprint','completed_episodes','weights','rng_state'}
    if not isinstance(data,dict) or set(data)!=fields:raise ValueError('Invalid checkpoint envelope')
    if data['schema']!=SCHEMA or data['feature_schema']!=FEATURE_SCHEMA:
        raise ValueError('Unsupported checkpoint schema')
    if data['engine_fingerprint']!=code_fingerprint():
        raise ValueError('Checkpoint belongs to different simulator code')
    count=data['completed_episodes']
    if type(count) is not int or count<0:raise ValueError('Invalid episode count')
    _weights(data['weights'])
    state=data['rng_state']
    if (not isinstance(state,list) or len(state)!=3 or state[0]!=3
            or not isinstance(state[1],list) or len(state[1])!=625
            or any(type(v) is not int or not 0<=v<=4294967295 for v in state[1][:-1])
            or type(state[1][-1]) is not int or not 0<=state[1][-1]<=624
            or (state[2] is not None and (type(state[2]) not in (int,float) or not math.isfinite(state[2])))):
        raise ValueError('Invalid sampling RNG state')
    policy=SparsePolicy(seed=0,weights=data['weights'])
    policy.rng.setstate((3,tuple(state[1]),state[2]))
    return policy,dict(completed_episodes=count,sha256=digest,
                       engine_fingerprint=data['engine_fingerprint'],feature_schema=FEATURE_SCHEMA)
