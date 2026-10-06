"""Read-only checkpoint adapters for reproducible policy/deck evaluation."""
import hashlib
from types import MappingProxyType
from .checkpoints import load_policy
from .features import encode_decision
from .learning import SparsePolicy


def _sampling_seed(seed,seat):
    if type(seed) is not int:raise ValueError('Integer evaluation seed required')
    return int.from_bytes(hashlib.sha256(f'policy-evaluation-v1:{seed}:{seat}'.encode()).digest(),'big')


class FrozenPolicy:
    """Sampling changes RNG only; this adapter exposes no training operation."""
    def __init__(self,weights,*,seed):
        policy=SparsePolicy(seed=seed,weights=weights)
        policy.weights=MappingProxyType(dict(policy.weights))
        self._policy=policy

    def __call__(self,decision):
        return self._policy.choose(encode_decision(decision))


def checkpoint_policy_factory(player0_path,player1_path,*,expected_sha256=None):
    """Load both snapshots once, then build independent actors for each seed pair.

    Uses fresh evaluation RNGs, not the checkpoint's training RNG. Metadata
    identifies both exact files and the sampling-seed scheme. File changes after
    loading cannot silently change the evaluation. Identical weights still get
    independent seat RNGs. Pairing games does not imply identical random events.
    """
    checks=(None,None) if expected_sha256 is None else tuple(expected_sha256)
    if len(checks)!=2:raise ValueError('Provide two checkpoint checksums')
    loaded=[load_policy(path,expected_sha256=checksum)
            for path,checksum in zip((player0_path,player1_path),checks)]
    snapshots=tuple(MappingProxyType(dict(policy.weights)) for policy,metadata in loaded)
    metadata=dict(schema='checkpoint-policy-pair-v1',
                  checkpoint_sha256=[meta['sha256'] for _,meta in loaded],
                  engine_fingerprint=loaded[0][1]['engine_fingerprint'],
                  feature_schema=loaded[0][1]['feature_schema'],
                  sampling='SHA-256(policy-evaluation-v1:seed:seat); independent seat RNGs')
    def factory(seed):
        return [FrozenPolicy(weights,seed=_sampling_seed(seed,seat))
                for seat,weights in enumerate(snapshots)]
    return factory,metadata
