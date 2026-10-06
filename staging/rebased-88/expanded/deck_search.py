"""Legal local-search neighbors; no evaluation, training or optimality claim.

The experimental mode searches validated implemented decks at their submitted
size. Size-changing roots require separately constructed seeds. Full Standard
search remains gated on simulator completeness.
"""
from collections import Counter
import random
from .cards import COLLECTIBLE_IDS,registry
from .decks import Deck,eligible,validate
from .status import require_full_standard


def rune_profiles(hero_class):
    from standard.catalog import CLASSES
    if hero_class not in CLASSES:raise ValueError('Unknown hero class')
    if hero_class!='DEATHKNIGHT':return ((0,0,0),)
    return tuple((blood,frost,3-blood-frost) for blood in range(4)
                 for frost in range(4-blood))


def single_card_neighbors(deck,*,experimental=False):
    """Yield each distinct legal one-card replacement in deterministic order.

    Cosmetic aliases sharing a copy-limit ID are not treated as new additions.
    This does not change rune allocation; seed separate searches for each profile.
    """
    if not experimental:require_full_standard()
    cards=registry();errors=validate(deck,cards)
    if errors:raise ValueError('; '.join(errors))
    def canonical(cid):return cards[cid].get('countAsCopyOfDbfId',cards[cid]['dbfId'])
    groups={}
    for cid in sorted(COLLECTIBLE_IDS):
        if eligible(cards[cid],deck.hero_class,deck.runes):
            groups.setdefault(canonical(cid),cid)
    removed_groups=set()
    for removed in sorted(set(deck.cards)):
        removed_group=canonical(removed)
        if removed_group in removed_groups:continue
        removed_groups.add(removed_group)
        remaining=list(deck.cards);remaining.remove(removed)
        counts=Counter(canonical(cid) for cid in remaining)
        for group,added in groups.items():
            if group==removed_group:continue
            limit=1 if cards[added].get('rarity')=='LEGENDARY' else 2
            if counts[group]>=limit:continue
            ids=tuple(sorted(remaining+[added]))
            selections=(deck.beatrix_minion,)
            if 'JAIL_397' not in ids:selections=(None,)
            elif deck.beatrix_minion is None:
                # Adding Beatrix adds an explicit construction decision, not a
                # silently sampled default. Each legal choice is a distinct deck.
                selections=tuple(sorted(cid for cid in COLLECTIBLE_IDS
                    if cards[cid].get('type')=='MINION' and cards[cid].get('cost')==2
                    and eligible(cards[cid],deck.hero_class,deck.runes)))
            beasts=deck.contraband_beasts if 'JAIL_831' in ids else ()
            for selection in selections:
                candidate=Deck(deck.hero_class,ids,tuple(deck.runes),
                               beatrix_minion=selection,contraband_beasts=beasts)
                # Final validation also handles aliases and size modifiers.
                if not validate(candidate,cards):yield candidate


def sample_neighbors(deck,*,count,seed,experimental=False):
    """Uniform reservoir sample without replacement, bounded by explicit count.

    Enumerates the finite neighborhood, but stores at most count decks. No games
    run here. RNG is local, so discovery doesn't perturb policy sampling state.
    """
    if type(count) is not int or count<1:raise ValueError('Positive neighbor count required')
    if type(seed) is not int:raise ValueError('Integer seed required')
    rng=random.Random(seed);result=[]
    for index,candidate in enumerate(single_card_neighbors(deck,experimental=experimental)):
        if index<count:result.append(candidate)
        else:
            position=rng.randrange(index+1)
            if position<count:result[position]=candidate
    return result
