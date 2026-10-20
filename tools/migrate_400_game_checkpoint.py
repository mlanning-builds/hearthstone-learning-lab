"""Offline, owner-authorized migration of the immutable 400-game trial. No games."""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hearthstone_sim.neural.checkpoints import load, save, digest
from hearthstone_sim.neural.runner import prepare
from hearthstone_sim.neural.upgrade import UNCHANGED

PARENT = ROOT / 'runs/neural_ppo/d1d5463d1b554ee0880268b7f0551d75/training-000051-evaluation.pt'
PARENT_SHA = '5f7d68c900ca4dc4b0f05cd056833fb4a9a5b5d63e564dbdc25e72dcfb2be8ac'
OLD_ENGINE = '245c5073fdcfd14eb82e68f1185720522e15984848a4a5622b386e0183b329c5'
OLD_CODE = 'ed5adc4952a2886f5331c55a38bbd31e7352fe91e7344a1f1a2570814ad7fb59'
NEW_CODE = '1a0f07a7fa2c75ddbd73aaaefb0d7185d01318af521454ae81a56a7b3e6cb4c8'
NEW_ENGINE = '8c2f5c4d0392acca58f53b396f46f44d06f804c5e88e5030fcf9a4d94d1ed1e1'
DEST = ROOT / 'runs/neural_migrations/400-game-repaired-engine-medium'


def equal(a, b):
    import torch
    if isinstance(a, torch.Tensor):
        return isinstance(b, torch.Tensor) and torch.equal(a, b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return type(a) is type(b) and len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def migrate():
    import torch
    if digest(PARENT) != PARENT_SHA:
        raise ValueError('Unapproved parent checkpoint')
    current = prepare()[2]
    old = dict(current, engine=OLD_ENGINE, neural_code=OLD_CODE)
    previous = load(PARENT, old, PARENT_SHA)
    if current['neural_code'] != NEW_CODE or current['engine'] != NEW_ENGINE or previous['global_game'] != 408 or previous['iteration'] != 51:
        raise ValueError('Unapproved engine or training position')
    for name, expected in UNCHANGED.items():
        if hashlib.sha256((ROOT / 'hearthstone_sim/neural' / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Learning implementation changed: ' + name)
    descriptors = previous['league'] + list(previous['evaluation_anchors'].values())
    originals = {d['name']: load(PARENT.parent / d['name'], old, d['sha256']) for d in descriptors}
    # All inputs are checked before creating output; existing migrations cannot be overwritten.
    DEST.mkdir(parents=True, exist_ok=False)
    lineage = dict(kind='explicit-engine-migration', parent=str(PARENT), parent_sha256=PARENT_SHA,
                   previous_compatibility=old, compatibility=current,
                   note='Retains learned weights, Adam, RNGs, counters and opponents. New engine baseline runs only when owner starts Jupyter.')
    mapped = {}
    for name, payload in originals.items():
        migrated = dict(payload, compatibility=current, migration=lineage)
        result = save(DEST / name, migrated)
        assert equal(payload['model'], load(result['path'], current)['model'])
        mapped[name] = dict(name=name, sha256=result['sha256'])
    result = copy.deepcopy(previous)
    result['compatibility'] = current
    result['migration'] = lineage
    result['settings']['evaluation_at'] = [512, 1024, 1536, 2000]
    result['settings']['evaluate_at_start'] = True
    result['league'] = [mapped[d['name']] for d in previous['league']]
    result['evaluation_anchors'] = {k: mapped[d['name']] for k, d in previous['evaluation_anchors'].items()}
    # Scores from the earlier engine remain archived, never mixed into the new baseline.
    result['evaluation_history'] = []
    checkpoint = save(DEST / 'training-000051-migrated.pt', result)
    restored = load(checkpoint['path'], current, checkpoint['sha256'])
    changed = {'compatibility', 'migration', 'settings', 'league', 'evaluation_anchors', 'evaluation_history'}
    for key in previous.keys() - changed:
        if not equal(previous[key], restored[key]):
            raise AssertionError('Migration altered ' + key)
    (DEST / 'previous-engine-evaluation-history.json').write_text(json.dumps(previous['evaluation_history'], indent=2) + '\n')
    receipt = dict(lineage, checkpoint=checkpoint, old_settings=previous['settings'],
                   settings=result['settings'], additional_games=2000, total_after_run=2408,
                   preserved_state_verified=True, training_started=False, evaluation_started=False)
    (DEST / 'migration.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    return checkpoint

if __name__ == '__main__':
    migrate()
