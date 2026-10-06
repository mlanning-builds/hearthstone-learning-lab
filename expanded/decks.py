"""Class-aware construction for explicitly implemented 30-card decks only."""
from collections import Counter
from dataclasses import dataclass
import random
from standard.catalog import CLASSES
from .cards import COLLECTIBLE_IDS, registry
from .selectors import has_class

RUNES=('blood','frost','unholy')

@dataclass(frozen=True)
class Deck:
    hero_class: str
    cards: tuple
    runes: tuple = (0,0,0)


def eligible(card, hero_class, runes):
    return has_class(card,hero_class,include_neutral=True) and all(card.get('runeCost',{}).get(k,0)<=n for k,n in zip(RUNES,runes))


def validate(deck, cards=None):
    cards=registry() if cards is None else cards
    errors=[]
    if deck.hero_class not in CLASSES: return ['Unknown hero class: '+str(deck.hero_class)]
    if len(deck.runes)!=3 or any(type(v) is not int or v<0 for v in deck.runes): return ['Invalid rune tuple.']
    if sum(deck.runes)!=(3 if deck.hero_class=='DEATHKNIGHT' else 0): errors.append('Death Knight uses three runes; other classes use zero.')
    if len(deck.cards)!=30: errors.append('This implemented ruleset requires exactly 30 cards; size-changing cards are not supported.')
    counts=Counter(); limits={}
    for cid in deck.cards:
        if cid not in COLLECTIBLE_IDS or cid not in cards:
            errors.append('Effect not implemented: '+str(cid)); continue
        c=cards[cid]
        if not eligible(c,deck.hero_class,deck.runes): errors.append('Class or rune mismatch: '+cid)
        canonical=c.get('countAsCopyOfDbfId',c['dbfId'])
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
    deck=Deck(hero_class,tuple(sorted(random.Random(seed).sample(slots,30))),tuple(runes))
    errors=validate(deck,cards)
    if errors: raise ValueError('; '.join(errors))
    return deck
