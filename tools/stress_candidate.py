"""Bounded random legal-play validation; never trains or ranks decks.

Use --engine-root staging/rebased-88. Failures include full deterministic replay
inputs. A capped game is not a completed game, nor is a pass conformance proof.
"""
import argparse
import hashlib
from dataclasses import asdict
import json
import math
from pathlib import Path
import random
import sys
import time
import uuid



def validate_observations(game, *, include_events=False):
    """Check serialization and explicit private-zone/action ownership contracts."""
    actor=(game.pending_choice['owner'] if game.phase=='choice' and game.pending_choice
           else game.current)
    expected=[asdict(a) for a in game.legal_actions()]
    for viewer in (0,1):
        observation=game.observe(viewer,include_events=include_events)
        json.dumps(observation,allow_nan=False)
        enemy=observation['players'][1-viewer]
        if any(key in enemy for key in ('hand','starting_deck','runes','secrets','cost_effects')):
            raise AssertionError('Opponent private-zone field exposed')
        if observation['legal_actions']!=(expected if viewer==actor else []):
            raise AssertionError('Observation legal actions disagree with decision owner')


def validate_features(game):
    """Encode one actor-visible decision without invoking a policy or optimizer."""
    if game.terminal:return 0
    from expanded.features import encode_decision
    actor=(game.pending_choice['owner'] if game.phase=='choice' and game.pending_choice else game.current)
    observation=game.observe(actor,include_events=False)
    actions=observation['legal_actions']
    rows=encode_decision(dict(actor=actor,observation=observation,actions=actions))
    if len(rows)!=len(actions):raise AssertionError('Feature rows disagree with legal candidates')
    for row in rows:
        if not isinstance(row,dict) or not all(isinstance(key,str) and isinstance(value,(int,float)) and math.isfinite(value) for key,value in row.items()):
            raise AssertionError('Invalid sparse feature row')
    return len(rows)


def save_report(out,report):
    """Keep an immutable run archive and atomically replace the convenience link."""
    run_id=uuid.uuid4().hex
    archive=out/f"summary-{report['fingerprint'][:12]}-{run_id}.json"
    report=dict(report,run_id=run_id,report_path=str(archive.resolve()))
    payload=json.dumps(report,indent=2)+'\n'
    with archive.open('x') as stream:stream.write(payload)
    latest=out/f'.summary-{run_id}.tmp'
    try:
        latest.write_text(payload)
        latest.replace(out/'summary.json')
    finally:
        if latest.exists():latest.unlink()
    return report


def save_failure(out,case):
    """Preserve each failure independently, including repeated seeds."""
    payload=json.dumps(case,indent=2,allow_nan=False)+'\n'
    path=out/f"failure-{case['game_seed']}-{case['fingerprint'][:12]}-{uuid.uuid4().hex}.json"
    with path.open('x') as stream:stream.write(payload)
    return path


def restore_deck(data,deck_type):
    return deck_type(data['hero_class'],tuple(data['cards']),tuple(data['runes']),
                     beatrix_minion=data.get('beatrix_minion'),
                     contraband_beasts=tuple(data.get('contraband_beasts',())))


def main():
    p=argparse.ArgumentParser();p.add_argument('--engine-root',type=Path,required=True)
    p.add_argument('--seeds',type=int,default=1);p.add_argument('--max-actions',type=int,default=120)
    p.add_argument('--replay',type=Path)
    p.add_argument('--check-features',action='store_true',help='Validate policy inputs without training')
    args=p.parse_args()
    if args.seeds<1 or not 1<=args.max_actions<=10000:p.error('Use positive seeds and 1..10000 max-actions')
    root=args.engine_root.resolve();sys.path.insert(0,str(root))
    from expanded import Game,Action,Deck,random_deck
    from expanded.cards import COLLECTIBLE_IDS
    from expanded.status import code_fingerprint
    from standard.catalog import CLASSES
    fingerprint=code_fingerprint()
    if args.replay:
        case=json.loads(args.replay.read_text())
        if case['fingerprint']!=fingerprint:raise ValueError('Replay source fingerprint differs; retain original evidence')
        decks=[restore_deck(d,Deck) for d in case['decks']]
        game=Game(decks,seed=case['game_seed'])
        check_features=case.get('check_features',False) or args.check_features
        if check_features:validate_features(game)
        for index,raw in enumerate(case['actions']):
            raw=dict(raw);raw['choices']=tuple(raw.get('choices',()))
            try:
                game.step(Action(**raw));game.assert_invariants();validate_observations(game,include_events=True)
                if check_features:validate_features(game)
            except Exception as exc:
                print(json.dumps(dict(action=index,error=type(exc).__name__,message=str(exc))))
                return 1
        print('Replay completed without exception');return 0
    out=root/'runs/random_validation';out.mkdir(parents=True,exist_ok=True)
    results=[];started=time.monotonic();classes=list(CLASSES)
    for seed in range(args.seeds):
        for i,hero_class in enumerate(classes):
            game_seed=10000+seed*len(classes)+i
            decks=[random_deck(hero_class,game_seed),random_deck(classes[(i+1)%len(classes)],game_seed+1000)]
            case=dict(fingerprint=fingerprint,check_features=args.check_features,game_seed=game_seed,decks=[asdict(d) for d in decks],actions=[])
            game=Game(decks,seed=game_seed);rng=random.Random(game_seed+2000)
            result=dict(seed=game_seed,classes=[d.hero_class for d in decks],status='action_cap',actions=0,feature_decisions_checked=0)
            try:
                game.assert_invariants()
                validate_observations(game)
                for step in range(args.max_actions):
                    if game.terminal:break
                    legal=game.legal_actions()
                    if not legal:raise AssertionError('Nonterminal state has no legal action')
                    if args.check_features:
                        validate_features(game);result['feature_decisions_checked']+=1
                    action=rng.choice(legal);case['actions'].append(asdict(action))
                    game.step(action);game.assert_invariants();validate_observations(game);result['actions']=step+1
                validate_observations(game,include_events=True)
                if game.terminal:result['status']='terminal'
            except Exception as exc:
                result.update(status='error',error=type(exc).__name__,message=str(exc),actions=len(case['actions']))
                case['failure']=result
                path=save_failure(out,case)
                result['replay_file']=str(path)
            result['played_card_ids']=sorted({e['card'] for e in game.events if e.get('event')=='play' and 'card' in e})
            result['summoned_card_ids']=sorted({e['card'] for e in game.events if e.get('event')=='summon' and 'card' in e})
            results.append(result)
            print(json.dumps(result),flush=True)
    played=sorted({cid for result in results for cid in result['played_card_ids']})
    summoned=sorted({cid for result in results for cid in result['summoned_card_ids']})
    feature_schema=None
    if args.check_features:
        from expanded.features import SCHEMA
        feature_schema=SCHEMA
    report=dict(feature_schema=feature_schema,feature_decisions_checked=sum(r['feature_decisions_checked'] for r in results),observation_checks='Both views at each step; full event serialization at game end; private zone keys and decision-owner actions.',tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                played_card_ids=played,summoned_card_ids=summoned,
                unseen_implemented_collectibles=sorted(COLLECTIBLE_IDS-set(played)-set(summoned)),
                coverage_note='An observed play or summon does not prove its effects or interactions were exercised.',
                fingerprint=fingerprint,scope='Random legal play of implemented candidate decks only; not full Standard certification.',
                max_actions=args.max_actions,seeds_per_class=args.seeds,games=len(results),
                errors=sum(r['status']=='error' for r in results),terminal=sum(r['status']=='terminal' for r in results),
                capped=sum(r['status']=='action_cap' for r in results),seconds=round(time.monotonic()-started,3),results=results)
    report=save_report(out,report)
    print(json.dumps({k:v for k,v in report.items() if k!='results'}))
    return int(report['errors']>0)

if __name__=='__main__':raise SystemExit(main())
