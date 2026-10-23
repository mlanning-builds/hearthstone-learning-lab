"""Isolated, owner-started saved-model learning-rate pilot. Default: read-only checks."""
import argparse
import copy
import json
import subprocess
import sys
import time
import uuid
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PANEL = ROOT / 'runs/all_class_campaign/panels/continuum-000005703.json'
OUTPUT = ROOT / 'runs/learning_rate_comparison'
RATES = (0.0001, 0.00005)
GAMES = 128
SECONDS = 90 * 60


def active_training():
    rows = subprocess.check_output(['ps', '-axo', 'pid=,args='], text=True)
    import os
    return [row.strip() for row in rows.splitlines()
            if row.split() and int(row.split()[0]) != os.getpid()
            and any(name in row for name in ('tools/train_neural.py',
                'tools/run_architecture_comparison.py', 'tools/learning_rate_comparison.py'))
            and '--train' in row]


def preflight():
    from hearthstone_sim.neural.runner import prepare
    from hearthstone_sim.neural.checkpoints import digest
    decks, _, compatibility = prepare(PANEL)
    classes = Counter(deck.hero_class for deck in decks.values())
    if len(decks) != 176 or len(classes) != 11 or set(classes.values()) != {16}:
        raise ValueError('Expected the exact 176-deck, eleven-class continuum')
    return dict(training_started=False, panel=str(PANEL), panel_sha256=digest(PANEL),
                compatibility=compatibility, decks=len(decks), classes=len(classes),
                learning_rates=list(RATES), games_per_arm=GAMES, threads=6,
                collection_workers=4, soft_minutes=90, active=bool(active_training()),
                note='Start only after the campaign finishes. Latest durable model is frozen then; campaign files stay untouched.')


def clone_arm(previous, source, destination, rate):
    """Copy full Adam/RNG/league state; only LR and common pilot monitoring differ."""
    from hearthstone_sim.neural.checkpoints import load, save, digest
    from tools.migrate_400_game_checkpoint import equal
    destination.mkdir(parents=True)
    result = copy.deepcopy(previous)
    settings = result['settings']
    settings.update(threads=6, collection_workers=4, games_per_iteration=64,
                    checkpoint_every_iterations=1, evaluate_at_start=False,
                    evaluation_at=[GAMES],
                    evaluation=dict(every_iterations=1000000,
                                    games_per_opponent=32, seed=1000030000))
    settings['ppo']['learning_rate'] = rate
    for group in result['optimizer']['param_groups']:
        group['lr'] = rate
    result['evaluation_history'] = []
    result['migration'] = dict(kind='owner-authorized-learning-rate-comparison',
        parent=str(source), parent_sha256=digest(source), learning_rate=rate)
    mapping = {}
    for descriptor in previous['league'] + list(previous['evaluation_anchors'].values()):
        name = descriptor['name']
        if name in mapping:
            continue
        payload = load(source.parent / name, previous['compatibility'], descriptor['sha256'])
        saved = save(destination / name, payload)
        mapping[name] = dict(name=name, sha256=saved['sha256'])
    result['league'] = [mapping[d['name']] for d in previous['league']]
    result['evaluation_anchors'] = {n: mapping[d['name']] for n, d in previous['evaluation_anchors'].items()}
    cp = save(destination / 'parent.pt', result)
    restored = load(cp['path'], previous['compatibility'], cp['sha256'])
    for field in ('model', 'action_rng', 'shuffle_rng', 'league_rng', 'global_game', 'iteration', 'tactical_state'):
        if not equal(previous[field], restored[field]):
            raise ValueError('Comparison copy changed ' + field)
    expected_optimizer = copy.deepcopy(previous['optimizer'])
    for group in expected_optimizer['param_groups']:
        group['lr'] = rate
    if not equal(expected_optimizer, restored['optimizer']):
        raise ValueError('Comparison copy changed Adam state beyond learning rate')
    return cp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--train', action='store_true')
    args = parser.parse_args()
    plan = preflight()
    print(json.dumps(dict(event='comparison_ready', **plan)), flush=True)
    if not args.train:
        return
    if active_training():
        raise RuntimeError('Training is still active. Leave it running; start this comparison after it finishes.')
    from tools.long_training_campaign import acquire_campaign_lock, latest_source, source_payload, CAMPAIGN
    lock = acquire_campaign_lock(CAMPAIGN / 'active.lock')
    try:
        execute(plan)
    finally:
        lock.close()


def execute(plan):
    import torch
    from hearthstone_sim.neural.checkpoints import digest, load
    from hearthstone_sim.neural.runner import run
    from hearthstone_sim.neural.ppo import PPOConfig
    from hearthstone_sim.neural.evaluation import EvaluationConfig
    from tools.long_training_campaign import latest_source, source_payload
    # Resolve only at owner Start, never while preparing the notebook.
    source = latest_source()
    previous = source_payload(source)
    if previous['compatibility'] != plan['compatibility']:
        raise ValueError('Latest checkpoint differs from live sources/panel. A reviewed migration is required; no automatic upgrade or reset.')
    if previous.get('stopped'):
        raise ValueError('Latest campaign stopped on a failure. Review staged engine fixes before comparing learning rates.')
    if previous['settings']['ppo']['learning_rate'] != RATES[0]:
        raise ValueError('Current campaign rate changed; review this pilot configuration')
    folder = OUTPUT / uuid.uuid4().hex
    folder.mkdir(parents=True)
    state = dict(schema='learning-rate-comparison-v1', parent=str(source),
        parent_sha256=digest(source), starting_global_game=previous['global_game'],
        plan=plan, results=[], complete=False,
        note='Single-seed pilot, not a statistically established winner. Main campaign is never promoted or overwritten.')
    state_path = folder / 'study.json'
    def record():
        temp = state_path.with_suffix('.partial')
        temp.write_text(json.dumps(state, indent=2) + '\n')
        temp.replace(state_path)
    parents = [clone_arm(previous, source, folder / ('arm-%d' % i) / 'initial', rate)
               for i, rate in enumerate(RATES)]
    record()
    torch.set_num_threads(6)
    started = time.monotonic()
    for index, (rate, parent) in enumerate(zip(RATES, parents)):
        remaining = SECONDS - (time.monotonic() - started)
        if remaining <= 0:
            state['pause_reason'] = 'Ninety-minute soft budget reached before next arm; no winner.'
            break
        settings = load(parent['path'], previous['compatibility'])['settings']
        kwargs = dict(settings)
        kwargs.pop('threads')
        kwargs['ppo'] = PPOConfig(**kwargs['ppo'])
        kwargs['evaluation'] = EvaluationConfig(**kwargs['evaluation'])
        print(json.dumps(dict(event='arm_started', learning_rate=rate, parent=parent, games=GAMES)), flush=True)
        cp = run(iterations=2, output=folder / ('arm-%d' % index) / 'training',
                 panel=PANEL, resume=parent['path'], allow_training=True,
                 session_seconds=remaining, **kwargs)
        payload = load(cp['path'], previous['compatibility'], cp['sha256'])
        history_path = Path(cp['path']).parent / 'monitoring-history.json'
        history = json.loads(history_path.read_text()) if history_path.exists() else []
        reports = [item for item in history
                   if item['global_game'] == previous['global_game'] + GAMES]
        success = (payload['global_game'] == previous['global_game'] + GAMES
                   and not payload.get('stopped') and bool(reports))
        if reports:
            report = json.loads(Path(reports[-1]['report']).read_text())
            expected_cases = 32 * (1 + len(previous['evaluation_anchors']))
            success = success and not report.get('stopped') and report['summary']['attempted'] == expected_cases
        state['results'].append(dict(learning_rate=rate, checkpoint=cp,
            trained_schedule_slots=payload['global_game']-previous['global_game'],
            complete=success, evaluation=reports[-1] if reports else None))
        record()
        if not success:
            state['pause_reason'] = 'Arm incomplete or stopped: saved safely, comparison inconclusive. Review receipts before continuing.'
            break
    state['complete'] = len(state['results']) == 2 and all(r['complete'] for r in state['results'])
    record()
    print(json.dumps(dict(event='comparison_finished', study=str(state_path), **state)), flush=True)


if __name__ == '__main__':
    main()
