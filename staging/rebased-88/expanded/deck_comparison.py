"""Bounded comparison against a fixed, equally weighted opponent panel.

Results are opponent-panel estimates, never a globally best-deck certificate.
Policy factories must return fresh, frozen policies without training side effects.
"""
from dataclasses import asdict
from .decks import validate
from .evaluation import evaluate_pair
from .status import require_full_standard,code_fingerprint


def compare_decks(candidates,opponents,policy_factory,*,seeds,max_actions,max_games,
                  policy_id,experimental=False):
    """Compare named candidates with named opponents under explicit game budget.

    policy_factory(seed) returns two fresh callables for a single seed pair.
    The same seed is reused across candidates/opponents to control policy starts;
    it does not imply identical later random events. Opponents are equally weighted.
    Incomplete candidates are not ranked, even if their completed score looks good.
    """
    if not experimental:require_full_standard()
    seeds=tuple(seeds)
    if not seeds or any(type(s) is not int for s in seeds) or len(set(seeds))!=len(seeds):
        raise ValueError('Unique explicit integer seeds required')
    if not isinstance(policy_id,str) or not policy_id:raise ValueError('Frozen policy identifier required')
    if not callable(policy_factory):raise ValueError('Policy factory required')
    if type(max_actions) is not int or max_actions<1:raise ValueError('Positive action limit required')
    for panel in (candidates,opponents):
        if not isinstance(panel,dict) or not panel:raise ValueError('Nonempty named deck panel required')
        for name,deck in panel.items():
            if not isinstance(name,str) or not name:raise ValueError('Nonempty deck name required')
            errors=validate(deck)
            if errors:raise ValueError(name+': '+'; '.join(errors))
    requested=2*len(seeds)*len(candidates)*len(opponents)
    if type(max_games) is not int or max_games<requested:
        raise ValueError('Game budget too small; requires '+str(requested))
    results=[]
    for name,deck in candidates.items():
        matchups=[];lower=upper=0.0;finished=0
        for opponent_name,opponent in opponents.items():
            reports=[]
            for seed in seeds:
                policies=policy_factory(seed)
                reports.append(evaluate_pair([deck,opponent],policies,seeds=[seed],
                                              max_actions=max_actions,experimental=experimental))
            lo=sum(p['action_cap_score_bounds'][0] for p in reports)/len(reports)
            hi=sum(p['action_cap_score_bounds'][1] for p in reports)/len(reports)
            completed=sum(p['completed'] for p in reports);finished+=completed
            lower+=lo/len(opponents);upper+=hi/len(opponents)
            matchups.append(dict(opponent=opponent_name,reports=reports,
                                 completed=completed,action_cap_score_bounds=[lo,hi]))
        total=2*len(seeds)*len(opponents)
        results.append(dict(candidate=name,matchups=matchups,completed=finished,games=total,
                            action_cap_score_bounds=[lower,upper],
                            panel_score=lower if finished==total else None))
    complete=all(row['panel_score'] is not None for row in results)
    ranking=(sorted([dict(candidate=row['candidate'],score=row['panel_score']) for row in results],
                    key=lambda row:(-row['score'],row['candidate'])) if complete else None)
    return dict(schema='deck-panel-comparison-v1',fingerprint=code_fingerprint(),
                experimental=experimental,policy_id=policy_id,seeds=list(seeds),
                max_actions=max_actions,games=requested,max_games=max_games,
                candidates={k:asdict(v) for k,v in candidates.items()},
                opponents={k:asdict(v) for k,v in opponents.items()},results=results,ranking=ranking,
                interpretation='Equal-weight supplied opponent panel only. Ranking withheld if any game is capped. Ties are listed alphabetically, not evidence of superiority. Action-cap bounds are not statistical confidence intervals. Search-selected winners require independent held-out evaluation.')
