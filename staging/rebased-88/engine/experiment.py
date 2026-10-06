"""Random baseline, deterministic replays, paired matches, and resumable runs."""
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import time

from lab import population
from .cards import supported_pool, registry
from .game import Action, Game

ROOT = Path(__file__).resolve().parent.parent


def fingerprint():
    paths = [ROOT/'lab.py', ROOT/'data/core_pool.json'] + sorted((ROOT/'engine').glob('*.py')) + [ROOT/'engine/reviewed_cards.json']
    h = hashlib.sha256()
    for path in paths:
        h.update(str(path.relative_to(ROOT)).encode()); h.update(path.read_bytes())
    return h.hexdigest()


def random_policy(observation, rng):
    """Uniform over complete legal actions, not over cards or action categories."""
    choices = observation['legal_actions']
    if not choices:
        raise ValueError('No action available.')
    data = dict(rng.choice(choices))
    data['choices'] = tuple(data['choices'])
    return Action(**data)


def play_game(decks, profiles, seed=0, first_player=0, record=False, max_turns=89):
    game = Game(decks, profiles, seed=seed, first_player=first_player,
                record=record, max_turns=max_turns)
    # Policy randomness never consumes the simulator's random stream.
    policy_rngs = [random.Random(seed*2+1000001), random.Random(seed*2+1000002)]
    while not game.terminal:
        if len(game.history) >= 10000:
            raise RuntimeError('Action safety limit reached: this is an error, not a draw.')
        observation = game.observe(game.current, include_events=False)
        game.step(random_policy(observation, policy_rngs[game.current]))
    result = dict(winner=game.winner, reason=game.end_reason, turns=game.turn,
                  actions=len(game.history), health=[p.health for p in game.players],
                  corpses=[p.corpses for p in game.players], first_player=first_player, seed=seed)
    if record:
        result['replay'] = dict(version=Game.VERSION, engine_fingerprint=fingerprint(),
                                decks=decks, profiles=profiles, seed=seed, first_player=first_player,
                                max_turns=max_turns, actions=game.history, events=game.events)
    return result


def replay_game(record):
    if record['engine_fingerprint'] != fingerprint():
        raise ValueError('Replay was recorded with different engine/card data.')
    g = Game(record['decks'], record['profiles'], seed=record['seed'],
             first_player=record['first_player'], max_turns=record['max_turns'])
    for entry in record['actions']:
        if entry['player'] != g.current:
            raise ValueError('Replay actor mismatch.')
        data=dict(entry['action']); data['choices']=tuple(data['choices'])
        g.step(Action(**data))
    if not g.terminal or g.events != record['events']:
        raise ValueError('Replay did not reproduce the original game.')
    return g


def _save(path, data):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2)+'\n')
    temporary.replace(path)


def run_experiment(games=100, decks_per_profile=2, seed=42, output_dir=None, progress=None):
    if type(games) is not int or games < 2 or games % 2:
        raise ValueError('games must be a positive even integer (at least 2).')
    if type(decks_per_profile) is not int or decks_per_profile < 1:
        raise ValueError('decks_per_profile must be a positive integer.')
    if type(seed) is not int or seed < 0:
        raise ValueError('seed must be a nonnegative integer.')
    config = dict(games=games, decks_per_profile=decks_per_profile, seed=seed,
                  policy='uniform-legal-action-v1', engine=Game.VERSION, engine_fingerprint=fingerprint())
    run_id=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()[:12]
    directory=Path(output_dir or ROOT/'runs') / ('matches_'+run_id)
    directory.mkdir(parents=True,exist_ok=True)
    checkpoint=directory/'checkpoint.json'
    decks=population(supported_pool(), per_profile=decks_per_profile, seed=seed)
    # Every sampled pairing gets two games, with starting player reversed.
    # This balances initiative, but does not make deck/rune samples exhaustive.
    rng=random.Random(seed+2000000)
    schedule=[]
    for _ in range(games//2):
        a,b=rng.sample(range(len(decks)),2)
        game_seed=rng.randrange(2**31)
        schedule.extend([dict(pair=[a,b],seed=game_seed,first_player=seat) for seat in (0,1)])
    if checkpoint.exists():
        saved=json.loads(checkpoint.read_text())
        if saved['config'] != config or saved['decks'] != decks or saved['schedule'] != schedule:
            raise ValueError('Checkpoint does not match this experiment.')
        results=saved['results']
        if len(results)>games or any(r['game_index']!=i for i,r in enumerate(results)):
            raise ValueError('Invalid checkpoint results.')
    else:
        saved=dict(config=config,decks=decks,schedule=schedule,results=[],
                   created_at=datetime.now(timezone.utc).isoformat(),status='running')
        results=saved['results']
        _save(checkpoint,saved)
    start=time.monotonic(); resumed=len(results)
    def report(status):
        if progress:
            progress(dict(completed=len(results),total=games,resumed=resumed,
                          elapsed=time.monotonic()-start,status=status))
    report('complete' if len(results)==games else 'running')
    try:
        for i in range(len(results),games):
            spec=schedule[i]
            pair=[decks[j] for j in spec['pair']]
            result=play_game([d['cards'] for d in pair], [tuple(d['runes'].values()) for d in pair],
                             seed=spec['seed'],first_player=spec['first_player'],record=(i==0))
            if i==0:
                _save(directory/'sample_match.json',result.pop('replay'))
            result.update(game_index=i,deck_indices=spec['pair'])
            results.append(result)
            saved['status']='complete' if len(results)==games else 'running'
            _save(checkpoint,saved)
            report(saved['status'])
    except KeyboardInterrupt:
        saved['status']='interrupted'; _save(checkpoint,saved); report('interrupted')
        raise
    except Exception as error:
        saved['status']='failed'
        saved['error']=str(error)
        _save(checkpoint,saved); report('failed')
        raise
    saved.pop('error',None)
    saved['status']='complete'; _save(checkpoint,saved)
    summary=summarize(results)
    _save(directory/'summary.json',summary)
    return dict(directory=str(directory),config=config,results=results,decks=decks,
                summary=summary,sample=json.loads((directory/'sample_match.json').read_text()))


def summarize(results):
    completed=len(results)
    reasons=Counter(r['reason'] for r in results)
    return dict(games=completed, first_player_wins=sum(r['winner']==r['first_player'] for r in results),
                second_player_wins=sum(r['winner'] is not None and r['winner']!=r['first_player'] for r in results),
                draws=sum(r['winner'] is None for r in results), turn_limit_games=reasons['turn_limit'],
                mean_turns=round(sum(r['turns'] for r in results)/completed,1) if completed else 0,
                mean_actions=round(sum(r['actions'] for r in results)/completed,1) if completed else 0,
                trained=False)


def match_log(record, first_turn=1, last_turn=10):
    """Readable public event log; no hidden hands exposed."""
    cards=registry(); names={-1:'Player A',-2:'Player B'}; lines=[]
    label=lambda i: 'Player A' if i==0 else 'Player B'
    for event in record['events']:
        kind=event['event']; turn=event['turn']
        if kind=='summon':
            names[event['entity']]=cards[event['card']]['name']+f" #{event['entity']}"
        if not first_turn<=turn<=last_turn:
            continue
        if kind=='turn':
            lines.append(f"\nTURN {turn} — {label(event['player'])} | {event['mana']} mana | health {event['health']} | corpses {event['corpses']}")
        elif kind=='play':
            target=' → '+names.get(event['target'],str(event['target'])) if event['target'] else ''
            lines.append(f"  {label(event['player'])} plays {cards[event['card']]['name']}{target}")
        elif kind=='attack':
            lines.append(f"  {names[event['source']]} attacks {names[event['target']]}")
        elif kind=='hero_power':
            lines.append(f"  {label(event['player'])} uses Ghoul Charge")
        elif kind=='summon':
            lines.append(f"  Summoned {names[event['entity']]}")
        elif kind=='death':
            lines.append(f"  {names[event['entity']]} dies; {label(event['player'])} gains a Corpse")
        elif kind in ('gain_corpse','spend_corpses','armor'):
            lines.append(f"  {label(event['player'])}: {kind.replace('_',' ')} {event['amount']}")
        elif kind in ('damage','heal'):
            lines.append(f"  {names[event['target']]}: {kind} {event['amount']}")
        elif kind=='shield_lost':
            lines.append(f"  {names[event['entity']]} loses Divine Shield")
        elif kind=='draw':
            lines.append(f"  {label(event['player'])} draws a card")
        elif kind=='burn':
            lines.append(f"  {label(event['player'])} burns {cards[event['card']]['name']} (hand full)")
        elif kind=='fatigue':
            lines.append(f"  {label(event['player'])} takes {event['damage']} fatigue damage")
        elif kind=='finished':
            lines.append('  '+('Draw' if event['winner'] is None else label(event['winner'])+' wins')+' — '+event['reason'])
    return '\n'.join(lines)
