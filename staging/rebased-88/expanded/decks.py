"""Class-aware construction with explicit frozen Fabled bundle expansion."""
from collections import Counter
from dataclasses import dataclass
import random
from standard.catalog import CLASSES
from .cards import COLLECTIBLE_IDS, registry, RULES, PASSIVE, PLAYABLE_TOKENS
from .selectors import has_class
from .fabled_decks import expand_bundle_ids,deck_size,companion_ids

RUNES=('blood','frost','unholy')

@dataclass(frozen=True)
class Deck:
    hero_class: str
    cards: tuple
    runes: tuple = (0,0,0)
    beatrix_minion: str = None
    contraband_beasts: tuple = ()


def eligible(card, hero_class, runes):
    return has_class(card,hero_class,include_neutral=True) and all(card.get('runeCost',{}).get(k,0)<=n for k,n in zip(RUNES,runes))


def validate(deck, cards=None):
    cards=registry() if cards is None else cards
    errors=[]
    if deck.hero_class not in CLASSES: return ['Unknown hero class: '+str(deck.hero_class)]
    if len(deck.runes)!=3 or any(type(v) is not int or v<0 for v in deck.runes): return ['Invalid rune tuple.']
    if sum(deck.runes)!=(3 if deck.hero_class=='DEATHKNIGHT' else 0): errors.append('Death Knight uses three runes; other classes use zero.')
    try:expanded=expand_bundle_ids(deck.cards)
    except ValueError as exc:return [str(exc)]
    expected=deck_size(expanded);companions=companion_ids(expanded)
    if len(expanded)!=expected:errors.append(f'Deck requires exactly {expected} cards including Fabled companions; got {len(expanded)}.')
    selected=deck.beatrix_minion
    if 'JAIL_397' in expanded:
        c=cards.get(selected,{})
        if selected not in COLLECTIBLE_IDS or c.get('type')!='MINION' or c.get('cost')!=2 or not eligible(c,deck.hero_class,deck.runes):
            errors.append('Beatrix requires an implemented, class/rune-legal collectible 2-Cost minion selection.')
    elif selected is not None:errors.append('Beatrix selection requires Commander Beatrix in the submitted deck.')
    if 'JAIL_831' in expanded:
        from .selectors import has_tribe,classes
        if len(deck.contraband_beasts)!=3 or len(set(deck.contraband_beasts))!=3:
            errors.append('King of the Underbelly requires three distinct contraband selections.')
        for cid in deck.contraband_beasts:
            c=cards.get(cid,{})
            if cid not in COLLECTIBLE_IDS or c.get('type')!='MINION' or not has_tribe(c,'BEAST') or classes(c)&{'NEUTRAL',deck.hero_class}:
                errors.append('Contraband must be an implemented off-class collectible Beast: '+str(cid))
    elif deck.contraband_beasts:errors.append('Contraband selections require King of the Underbelly.')
    if 'JAIL_430' in expanded and any(cid in expanded for cid in ('TIME_005','REV_018')):
        errors.append('Azalina cannot share a submitted deck with a conflicting deck-size modifier.')
    counts=Counter(); limits={}
    for cid in expanded:
        executable_token=cid in companions and (cid in RULES or cid in PASSIVE or cid in PLAYABLE_TOKENS)
        if (cid not in COLLECTIBLE_IDS and not executable_token) or cid not in cards:
            errors.append('Effect not implemented: '+str(cid)); continue
        c=cards[cid]
        if not eligible(c,deck.hero_class,deck.runes): errors.append('Class or rune mismatch: '+cid)
        canonical=c.get('countAsCopyOfDbfId',c.get('dbfId',cid))
        counts[canonical]+=1
        limits[canonical]=min(limits.get(canonical,2),1 if c.get('rarity')=='LEGENDARY' else 2)
    errors.extend('Copy limit exceeded: '+str(key) for key,count in counts.items() if count>limits[key])
    return errors


def random_deck(hero_class, seed, runes=None):
    if hero_class not in CLASSES: raise ValueError('Unknown hero class')
    if runes is None: runes=(1,1,1) if hero_class=='DEATHKNIGHT' else (0,0,0)
    cards=registry(); probe=Deck(hero_class,(),tuple(runes))
    if len(runes)!=3 or any(type(v) is not int or v<0 for v in runes) or sum(runes)!=(3 if hero_class=='DEATHKNIGHT' else 0):
        raise ValueError('Invalid runes for class')
    groups={}
    for cid in sorted(COLLECTIBLE_IDS):
        c=cards[cid]
        if eligible(c,hero_class,runes):
            groups.setdefault(c.get('countAsCopyOfDbfId',c['dbfId']),c)
    slots=[c['id'] for c in groups.values() for _ in range(1 if c.get('rarity')=='LEGENDARY' else 2)]
    if len(slots)<30: raise ValueError('Not enough implemented cards for this class/rune profile')
    from .fabled_decks import BUNDLES, sample_bundle_slots
    chosen=(sample_bundle_slots(slots,seed) if set(slots)&(BUNDLES.keys()|{'JAIL_430'}) else tuple(random.Random(seed).sample(slots,30)))
    selection=None
    if 'JAIL_397' in chosen:
        choices=sorted(c['id'] for c in groups.values() if c.get('type')=='MINION' and c.get('cost')==2)
        if not choices:raise ValueError('No implemented legal Beatrix selection')
        selection=random.Random(seed).choice(choices)
    deck=Deck(hero_class,tuple(sorted(expand_bundle_ids(chosen))),tuple(runes),beatrix_minion=selection)
    errors=validate(deck,cards)
    if errors: raise ValueError('; '.join(errors))
    return deck
