"""Constructed identity selectors; never infer behavior from card text.

These functions inspect printed identity, not current enchantments/keywords.
Deck legality and generation eligibility remain separate caller responsibilities.
"""
from __future__ import annotations

from dataclasses import dataclass

TRIBES = frozenset(('BEAST','DEMON','DRAENEI','DRAGON','ELEMENTAL','MECHANICAL',
                   'MURLOC','NAGA','PIRATE','QUILBOAR','TOTEM','UNDEAD'))
SCHOOLS = frozenset(('ARCANE','FEL','FIRE','FROST','HOLY','NATURE','SHADOW'))
HERO_CLASSES = frozenset(('DEATHKNIGHT','DEMONHUNTER','DRUID','HUNTER','MAGE',
                          'PALADIN','PRIEST','ROGUE','SHAMAN','WARLOCK','WARRIOR'))
CARD_TYPES = frozenset(('MINION','SPELL','WEAPON','HERO','LOCATION'))


def tribes(card):
    if card.get('type') != 'MINION':
        return frozenset()
    values = card.get('races') or ([card['race']] if card.get('race') else [])
    return frozenset(values)


def effective_tribes(card):
    """Canonical Constructed types, expanding ALL only to known minion types."""
    values = tribes(card)
    return TRIBES if 'ALL' in values else values & TRIBES


def common_tribes(cards):
    """Intersection across minion identities; no cards provides no type proof."""
    cards = list(cards)
    if not cards:
        return frozenset()
    common = effective_tribes(cards[0])
    for card in cards[1:]:
        common = common & effective_tribes(card)
    return frozenset(common)


def has_tribe(card, tribe):
    # ALL is a stored identity marker, not a wildcard over arbitrary strings.
    if tribe not in TRIBES:
        raise ValueError('Unknown Constructed tribe: '+str(tribe))
    values = tribes(card)
    return tribe in values or 'ALL' in values


def has_any_tribe(card):
    return bool(tribes(card) & (TRIBES | {'ALL'}))


def shares_tribe(left, right):
    a, b = tribes(left), tribes(right)
    if not has_any_tribe(left) or not has_any_tribe(right):
        return False
    return 'ALL' in a or 'ALL' in b or bool(a & b & TRIBES)


def has_school(card, school):
    if school not in SCHOOLS:
        raise ValueError('Unknown Constructed spell school: '+str(school))
    return card.get('type') == 'SPELL' and card.get('spellSchool') == school


def classes(card):
    return frozenset(card.get('classes') or ([card['cardClass']] if card.get('cardClass') else []))


def has_class(card, hero_class, include_neutral=False):
    if hero_class not in HERO_CLASSES:
        raise ValueError('Unknown Constructed hero class: '+str(hero_class))
    values = classes(card)
    return hero_class in values or (include_neutral and 'NEUTRAL' in values)


@dataclass(frozen=True)
class CardSelector:
    """Explicit, composable AND predicate for frozen card metadata.

    Pool membership is supplied separately: matching this does NOT establish
    legality, discoverability, implementation, or current entity properties.
    """
    card_type: str | None = None
    tribe: str | None = None
    school: str | None = None
    hero_class: str | None = None
    include_neutral: bool = False
    min_cost: int | None = None
    max_cost: int | None = None

    def __post_init__(self):
        for value, domain, name in ((self.card_type,CARD_TYPES,'type'),
                                    (self.tribe,TRIBES,'tribe'),
                                    (self.school,SCHOOLS,'school'),
                                    (self.hero_class,HERO_CLASSES,'class')):
            if value is not None and value not in domain:
                raise ValueError('Unknown selector '+name+': '+str(value))
        if self.include_neutral and self.hero_class is None:
            raise ValueError('include_neutral requires a hero class')
        for cost in (self.min_cost,self.max_cost):
            if cost is not None and (type(cost) is not int or cost < 0):
                raise ValueError('Cost bounds must be nonnegative integers')
        if self.min_cost is not None and self.max_cost is not None and self.min_cost > self.max_cost:
            raise ValueError('Minimum cost exceeds maximum cost')

    def matches(self, card):
        if self.card_type is not None and card.get('type') != self.card_type: return False
        if self.tribe is not None and not has_tribe(card,self.tribe): return False
        if self.school is not None and not has_school(card,self.school): return False
        if self.hero_class is not None and not has_class(card,self.hero_class,self.include_neutral): return False
        if self.min_cost is not None and (card.get('cost') is None or card['cost'] < self.min_cost): return False
        if self.max_cost is not None and (card.get('cost') is None or card['cost'] > self.max_cost): return False
        return True

    def select(self, candidates):
        # Preserve candidate multiplicity/order. Deck instances and unique
        # generation pools have different sampling semantics.
        return [card for card in candidates if self.matches(card)]
