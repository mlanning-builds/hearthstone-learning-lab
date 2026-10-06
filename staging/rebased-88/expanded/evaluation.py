"""Bounded paired policy evaluation; no learning or implicit deck search."""
from dataclasses import asdict
from .environment import PolicyEnvironment
from .status import code_fingerprint



def summarize_games(games):
    """Descriptive paired evidence; bounds concern caps, not sampling error.

    The seed pair is the sampling unit for standard error because the two
    starting positions intentionally share a seed. Incomplete pairs are omitted
    from paired estimates, but remain in the action-cap bounds.
    """
    def score(game):
        reward=game['rewards'][0]
        return 1.0 if reward>0 else 0.0 if reward<0 else 0.5
    complete=[g for g in games if g['terminated']]
    total=len(games);points=sum(score(g) for g in complete)
    by_start=[]
    for first in (0,1):
        group=[g for g in games if g['first_player']==first]
        finished=[g for g in group if g['terminated']]
        by_start.append(dict(first_player=first,games=len(group),completed=len(finished),
                             score=sum(score(g) for g in finished)/len(finished) if finished else None))
    grouped={}
    for game in games:grouped.setdefault(game['seed'],[]).append(game)
    pairs=[]
    for seed,pair in grouped.items():
        if len(pair)!=2 or {g['first_player'] for g in pair}!={0,1}:
            raise ValueError('Each seed must have exactly one game per starting position')
        finished=all(g['terminated'] for g in pair)
        pairs.append(dict(seed=seed,complete=finished,
                          score=sum(score(g) for g in pair)/2 if finished else None))
    values=[p['score'] for p in pairs if p['complete']];n=len(values)
    mean=sum(values)/n if n else None
    se=(sum((x-mean)**2 for x in values)/(n*(n-1)))**0.5 if n>1 else None
    return dict(by_starting_player=by_start,seed_pairs=pairs,complete_pairs=n,
                paired_score=mean,paired_score_standard_error=se,
                action_cap_score_bounds=[points/total,(points+total-len(complete))/total] if total else None,
                uncertainty_note='Standard error describes variation across complete seed pairs; it is not a confidence guarantee or evidence against other opponents. Action-cap bounds assign unfinished games scores of 0 or 1; they are not confidence intervals. Excluding incomplete pairs may bias the paired score.')

def evaluate_pair(decks,policies,*,seeds,max_actions,experimental=False):
    """Keep deck/player IDs fixed and alternate who starts for every seed.

    Policies receive only their actor-visible decision and return a candidate
    index. Their own randomness must be controlled by the caller. Pairing seeds
    does not imply identical subsequent random events across different games.
    """
    seeds=tuple(seeds)
    if not seeds or any(type(seed) is not int for seed in seeds):
        raise ValueError('Provide an explicit nonempty sequence of integer seeds')
    if len(set(seeds))!=len(seeds):raise ValueError('Duplicate seeds inflate repeated evidence')
    if len(policies)!=2 or not all(callable(policy) for policy in policies):
        raise ValueError('Provide exactly two policy callables')
    env=PolicyEnvironment(experimental=experimental)
    games=[]
    for seed in seeds:
        for first in (0,1):
            decision=env.reset(decks,seed=seed,max_actions=max_actions,first_player=first)
            while not decision['terminated'] and not decision['truncated']:
                actor=decision['actor'];revision=decision['revision']
                index=policies[actor](decision)
                decision=env.step(index,revision=revision)
            games.append(dict(seed=seed,first_player=first,terminated=decision['terminated'],
                              truncated=decision['truncated'],steps=decision['steps'],
                              reason=decision['end_reason'],rewards=decision['rewards']))
    completed=[g for g in games if g['terminated']]
    wins=sum(g['rewards'][0]>0 for g in completed)
    losses=sum(g['rewards'][0]<0 for g in completed)
    draws=len(completed)-wins-losses
    return dict(**summarize_games(games),fingerprint=code_fingerprint(),experimental=experimental,
                decks=[asdict(deck) for deck in decks],seeds=list(seeds),max_actions=max_actions,
                games=games,completed=len(completed),truncated=len(games)-len(completed),
                player0_wins=wins,player0_losses=losses,draws=draws,
                completed_score=(wins+0.5*draws)/len(completed) if completed else None,
                interpretation='Descriptive score against the supplied policy only; not a best-deck claim. Truncation can bias completed-game scores.')
