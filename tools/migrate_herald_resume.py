"""Explicit offline continuation of the stopped medium run after Herald repairs."""
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
from tools.migrate_400_game_checkpoint import equal

PARENT = ROOT / 'runs/neural_ppo/d32d9bc1dcf64bb7b11363ad6f191a27/training-000207.pt'
PARENT_SHA = '28187bcc839f1a3a2ce801d68aff24b466e6ab28231311911a39bb0987ad90bf'
OLD_ENGINE = '8c2f5c4d0392acca58f53b396f46f44d06f804c5e88e5030fcf9a4d94d1ed1e1'
NEW_ENGINE = '86e0a823dc7a474078b1ab423e05f182e5ca24b4b297d03766f3f8a1529e3db2'
CODE = '1a0f07a7fa2c75ddbd73aaaefb0d7185d01318af521454ae81a56a7b3e6cb4c8'
DEST = ROOT / 'runs/neural_migrations/herald-repaired-medium-finish'


def migrate():
    current = prepare()[2]
    if current['engine'] != NEW_ENGINE or current['neural_code'] != CODE:
        raise ValueError('Unapproved repaired source')
    if digest(PARENT) != PARENT_SHA:
        raise ValueError('Unapproved stopped checkpoint')
    old = dict(current, engine=OLD_ENGINE)
    previous = load(PARENT, old, PARENT_SHA)
    if (previous['iteration'], previous['global_game'], previous['stopped']) != (206, 1649, True):
        raise ValueError('Unexpected stopped position')
    for name, expected in UNCHANGED.items():
        if hashlib.sha256((ROOT / 'hearthstone_sim/neural' / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Learning implementation changed: ' + name)
    descriptors = previous['league'] + list(previous['evaluation_anchors'].values())
    originals = {d['name']: load(PARENT.parent / d['name'], old, d['sha256']) for d in descriptors}
    # No mutation of any existing artifact. Exclusive destination and receipts.
    DEST.mkdir(parents=True, exist_ok=False)
    lineage = dict(kind='explicit-herald-engine-repair', parent=str(PARENT), parent_sha256=PARENT_SHA,
                   previous_compatibility=old, compatibility=current,
                   previous_migration_receipt='runs/neural_migrations/400-game-repaired-engine-medium/migration.json',
                   preserved_completed_medium_batches=155, updated_medium_games=1240,
                   discarded_partial_games=1, additional_games=760,
                   schedule_before=1649, schedule_after=1648,
                   note='Replays the unupdated partial-batch schedule slot with the next unused seed. All RNGs, Adam, weights, failure totals and opponents are preserved.')
    mapped = {}
    for name, payload in originals.items():
        saved = save(DEST / name, dict(payload, compatibility=current, migration=lineage))
        assert equal(payload['model'], load(saved['path'], current)['model'])
        mapped[name] = dict(name=name, sha256=saved['sha256'])
    result = copy.deepcopy(previous)
    result.update(compatibility=current, migration=lineage, stopped=False, global_game=1648,
                  evaluation_history=[])
    result['settings']['evaluation_at'] = [296, 760]
    result['settings']['evaluate_at_start'] = True
    result['league'] = [mapped[d['name']] for d in previous['league']]
    result['evaluation_anchors'] = {k: mapped[d['name']] for k,d in previous['evaluation_anchors'].items()}
    retired = {}
    for field in ('safety','evaluation_safety'):
        retired[field] = result[field]['signatures'].pop('UnsupportedCard:_herald', 0)
    # Only the repaired exception's repeat counter is retired. Historical failure
    # totals remain intact and other exception signature limits remain active.
    lineage['retired_repaired_signatures'] = retired
    saved = save(DEST / 'training-000206-herald-migrated.pt', result)
    restored = load(saved['path'], current, saved['sha256'])
    changed = {'compatibility','migration','settings','league','evaluation_anchors',
               'evaluation_history','global_game','stopped','safety','evaluation_safety'}
    for key in previous.keys() - changed:
        if not equal(previous[key], restored[key]):
            raise AssertionError('Altered preserved state: ' + key)
    for field in ('safety','evaluation_safety'):
        expected = copy.deepcopy(previous[field])
        expected['signatures'].pop('UnsupportedCard:_herald', None)
        assert equal(expected, restored[field])
    (DEST / 'previous-engine-evaluation-history.json').write_text(json.dumps(previous['evaluation_history'], indent=2)+'\n')
    receipt = dict(lineage, checkpoint=saved, old_settings=previous['settings'], settings=result['settings'],
                   updated_global_games_after_run=2408, preserved_state_verified=True,
                   training_started=False, evaluation_started=False)
    (DEST / 'migration.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    return saved

if __name__ == '__main__':
    migrate()
