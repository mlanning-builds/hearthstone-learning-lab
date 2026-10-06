"""Bounded experimental local deck search with separate held-out evaluation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid


def validate_plan(plan):
    if plan.get('schema')!='candidate-deck-search-v1':raise ValueError('Unsupported search plan')
    for field,maximum in (('rounds',50),('neighbors',100),('max_actions',10000),('max_games',10000)):
        if type(plan.get(field)) is not int or not 1<=plan[field]<=maximum:
            raise ValueError('Invalid explicit budget: '+field)
    for field in ('search_seeds','heldout_seeds'):
        values=plan.get(field)
        if not isinstance(values,list) or not values or any(type(v) is not int for v in values) or len(set(values))!=len(values):
            raise ValueError('Unique integer seeds required: '+field)
    if set(plan['search_seeds'])&set(plan['heldout_seeds']):raise ValueError('Search and held-out seeds must be disjoint')
    if type(plan.get('neighbor_seed')) is not int:raise ValueError('Explicit neighbor seed required')
    if not isinstance(plan.get('opponents'),dict) or not plan['opponents']:raise ValueError('Explicit opponent panel required')
    if len(plan.get('checkpoints',()))!=2:raise ValueError('Two frozen checkpoints required')
    required=2*len(plan['opponents'])*(plan['rounds']*(plan['neighbors']+1)*len(plan['search_seeds'])+2*len(plan['heldout_seeds']))
    if required>plan['max_games']:raise ValueError('Game budget too small; reserve '+str(required))
    return required


def select_candidate(report,current,panel):
    # Capped matches are never used as selection labels. Keep the incumbent on
    # a tie rather than letting alphabetic presentation order change the deck.
    if report['ranking'] is None:return current,False
    scores={r['candidate']:r['panel_score'] for r in report['results']}
    best=max(scores.values())
    winner='incumbent' if scores['incumbent']==best else min(k for k,v in scores.items() if v==best)
    return panel[winner],True


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--engine-root',type=Path,required=True)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--experimental',action='store_true')
    args=parser.parse_args()
    raw=args.plan.read_bytes();plan=json.loads(raw);reserved=validate_plan(plan)
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    from tools.compare_candidate_decks import restore_deck
    sys.path.insert(0,str(args.engine_root.resolve()))
    from expanded import Deck,validate
    from expanded.status import require_full_standard,code_fingerprint
    from expanded.deck_search import sample_neighbors
    from expanded.deck_comparison import compare_decks
    from expanded.frozen_policy import checkpoint_policy_factory
    if not args.experimental:require_full_standard()
    original=restore_deck(plan['initial_deck'],Deck)
    opponents={name:restore_deck(data,Deck) for name,data in plan['opponents'].items()}
    for deck in (original,*opponents.values()):
        errors=validate(deck)
        if errors:raise ValueError('; '.join(errors))
    paths=[Path(c['path']) for c in plan['checkpoints']]
    paths=[p if p.is_absolute() else args.plan.resolve().parent/p for p in paths]
    factory,metadata=checkpoint_policy_factory(*paths,expected_sha256=[c['sha256'] for c in plan['checkpoints']])
    fingerprint=code_fingerprint()
    folder=args.output.resolve()/uuid.uuid4().hex;folder.mkdir(parents=True)
    (folder/'plan.json').write_bytes(raw)
    current=original;receipts=[];games=0;completed=True
    def evaluate(panel,seeds):
        return compare_decks(panel,opponents,factory,seeds=seeds,max_actions=plan['max_actions'],
                             max_games=plan['max_games']-games,policy_id=json.dumps(metadata,sort_keys=True),experimental=args.experimental)
    print(json.dumps(dict(event='started',reserved_games=reserved,folder=str(folder))),flush=True)
    for turn in range(plan['rounds']):
        neighbors=sample_neighbors(current,count=plan['neighbors'],seed=plan['neighbor_seed']+turn,experimental=args.experimental)
        panel={'incumbent':current,**{f'neighbor-{i:04}':d for i,d in enumerate(neighbors)}}
        report=evaluate(panel,plan['search_seeds']);games+=report['games']
        path=folder/f'round-{turn+1:03}.json';path.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');receipts.append(str(path))
        current,complete=select_candidate(report,current,panel)
        print(json.dumps(dict(event='round',round=turn+1,games=games,complete=complete)),flush=True)
        if not complete:completed=False;break
    heldout=None
    if completed:
        report=evaluate({'initial':original,'selected':current},plan['heldout_seeds']);games+=report['games']
        heldout=folder/'heldout.json';heldout.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
        completed=report['ranking'] is not None
    if code_fingerprint()!=fingerprint:raise ValueError('Engine source changed during search; results remain unverified')
    from dataclasses import asdict
    manifest=dict(schema='candidate-deck-search-result-v1',engine_fingerprint=fingerprint,
                  runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),plan_sha256=hashlib.sha256(raw).hexdigest(),
                  experimental=args.experimental,full_standard=not args.experimental,round_reports=receipts,
                  heldout_report=str(heldout) if heldout else None,games=games,reserved_games=reserved,
                  completed=completed,selected_deck=asdict(current) if completed else None,
                  interpretation='Local search over implemented decks and supplied opponents. Separate seeds reduce selection reuse; small panels do not establish Standard strength or global optimality.')
    path=folder/'manifest.json';path.write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(event='complete',manifest=str(path),games=games,completed=completed)),flush=True)

if __name__=='__main__':main()
