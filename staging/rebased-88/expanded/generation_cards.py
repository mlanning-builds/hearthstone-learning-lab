"""Sixty staged Constructed generation declarations, NOT playable registration.

Pool eligibility needs a separately reviewed, complete per-class contract. These
recipes are intentionally absent from cards.RULES/COLLECTIBLE_IDS. A recipe and
its full outcome closure must be reviewed before promotion to the live tables.
No rules are inferred from card text at runtime.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PoolRequest:
    era: str = ''
    rune: str = ''
    card_type: str = ''
    tribe: str = ''
    school: str = ''
    minimum: int = 0
    maximum: int | None = None
    rarity: str = ''
    mechanic: str = ''
    excluded_mechanic: str = ''
    family: str = ''
    minimum_tribes: int = 0
    classes: str = 'any'  # any, own, own_or_neutral, other, or an explicit class

    attack_minimum: int | None = None
    attack_maximum: int | None = None

    def __post_init__(self):
        from .selectors import CARD_TYPES, TRIBES, SCHOOLS, HERO_CLASSES
        from .generation_families import FAMILIES
        if self.era not in ('','past'):raise ValueError('Unknown generation era')
        if self.rune not in ('','blood','frost','unholy'):raise ValueError('Unknown Rune selector')
        if self.family and self.family not in FAMILIES:raise ValueError('Unknown generation family')
        for value, domain in ((self.card_type, CARD_TYPES), (self.tribe, TRIBES), (self.school, SCHOOLS)):
            if value and value not in domain:
                raise ValueError('Unknown generation selector: ' + value)
        if self.classes not in {'any', 'own', 'own_or_neutral', 'other'} | HERO_CLASSES:
            raise ValueError('Unknown generation class selector')
        for value in (self.attack_minimum,self.attack_maximum):
            if value is not None and (type(value) is not int or value<0):raise ValueError('Invalid Attack bound')
        if self.attack_minimum is not None and self.attack_maximum is not None and self.attack_maximum<self.attack_minimum:
            raise ValueError('Reversed Attack bounds')
        if type(self.minimum_tribes) is not int or self.minimum_tribes < 0:
            raise ValueError('Invalid minimum minion type count')
        if type(self.minimum) is not int or self.minimum < 0:
            raise ValueError('Invalid minimum Cost')
        if self.maximum is not None and (type(self.maximum) is not int or self.maximum < self.minimum):
            raise ValueError('Invalid maximum Cost')


def pool(**kwargs):
    return PoolRequest(**kwargs)


def random_cards(request, count=1, destination='hand', **modifiers):
    return ('generate_random', request, count, destination, tuple(modifiers.items()))


def discover(request, destination='hand', **modifiers):
    return ('generate_discover', request, destination, tuple(modifiers.items()))


MINION = pool(card_type='MINION')
BEAST = pool(card_type='MINION', tribe='BEAST')
DRAGON = pool(card_type='MINION', tribe='DRAGON')
LEGENDARY = pool(card_type='MINION', rarity='LEGENDARY')
SPELL = pool(card_type='SPELL', classes='own_or_neutral')
TAUNT = pool(card_type='MINION', mechanic='TAUNT', classes='own_or_neutral')
FOUR = pool(card_type='MINION', minimum=4, maximum=4)

# Complete printed effect sequences; hooks stay staged alongside the play rules.
RULES = {
 'CORE_DRG_024': ('none', [random_cards(pool(card_type='MINION', tribe='PIRATE'))]),
 'CORE_EDR_001': ('none', [random_cards(pool(card_type='SPELL', classes='MAGE'), 2)]),
 'CORE_EX1_189': ('none', [random_cards(LEGENDARY)]),
 'CORE_GIL_531': ('none', [random_cards(pool(card_type='SPELL', classes='SHAMAN'))]),
 'CORE_KAR_069': ('none', [random_cards(pool(classes='other'))]),
 'CORE_UNG_912': ('none', [random_cards(BEAST)]),
 'CATA_556': ('none', [random_cards(pool(card_type='MINION', tribe='DRAGON', maximum=3))]),
 'EDR_999': ('none', [random_cards(pool(card_type='MINION', tribe='MURLOC'))]),
 'EDR_848': ('character', [('heal', 6), random_cards(pool(card_type='SPELL', classes='DRUID'), 3)]),
 'JAIL_125': ('enemy_character', [('freeze',), random_cards(pool(card_type='SPELL', school='FROST'))]),
 'JAIL_706': ('none', [random_cards(pool(card_type='SPELL', minimum=4, maximum=4), 2, cost_delta=-2)]),
 'JAIL_460': ('none', []),
 'MEND_045': ('none', []),
 'TIME_613': ('none', []),
 'CATA_723': ('none', []),
 'CORE_GVG_114': ('none', []),
 'CORE_REV_308': ('none', [random_cards(pool(card_type='MINION', minimum=2, maximum=2), destination='board')]),
 'CORE_KAR_077': ('minion', [('buff', 2, 2), random_cards(pool(card_type='MINION', minimum=2, maximum=2), destination='board')]),
 'CORE_WON_337': ('none', [('armor', 4), random_cards(FOUR, destination='board')]),
 'EDR_060': ('none', [('armor', 5), random_cards(pool(card_type='MINION', minimum=5, maximum=5), destination='board', keyword='TAUNT')]),
 'DINO_431': ('none', []),
 'DINO_433': ('none', [random_cards(pool(card_type='MINION', mechanic='TAUNT', minimum=n, maximum=n), destination='board') for n in (6, 4, 2)]),
 'CATA_569': ('none', [random_cards(pool(card_type='MINION', minimum=n, maximum=n), destination='board') for n in (3, 2, 1)]),
 'MEND_042': ('none', [('area_heal', 8), random_cards(pool(card_type='MINION', minimum=8, maximum=8), 2, destination='board')]),
 'TLC_516': ('none', [random_cards(pool(card_type='WEAPON', classes='other'), combo_attack=2)]),
 'TLC_814': ('none', []),
 'DINO_434': ('none', [random_cards(pool(card_type='MINION', minimum=1, maximum=1))]),
 'CATA_474': ('none', []),
 'EDR_462': ('none', []),
 'EDR_530': ('none', []),
 'END_029': ('none', []),
 'CORE_ETC_111': ('none', []),
 'CATA_136': ('none', [random_cards(pool(card_type='MINION', minimum=8), 5, 'deck', double_stats=True)]),
 'CORE_AV_107': ('none', [discover(pool(card_type='MINION', minimum=8, maximum=8, classes='own_or_neutral'), 'board', freeze=True)]),
 'CORE_BAR_541': ('character', [('damage', 2), discover(SPELL)]),
 'CORE_BT_321': ('none', [discover(pool(card_type='MINION', tribe='DEMON', classes='own_or_neutral'))]),
 'CORE_CATA_009': ('character', [('freeze',), discover(SPELL)]),
 'CORE_GIL_836': ('none', [discover(pool(card_type='MINION', mechanic='BATTLECRY', classes='own_or_neutral'), cost_delta=-1)]),
 'CORE_KAR_057': ('none', [discover(SPELL, heal_cost=True)]),
 'CORE_KAR_062': ('none', [('generation_if_holding', 'DRAGON', discover(pool(card_type='MINION', tribe='DRAGON', classes='own_or_neutral')))]),
 'CORE_LOE_039': ('none', [('generation_if_other_tribe', 'MECHANICAL', discover(pool(card_type='MINION', tribe='MECHANICAL', classes='own_or_neutral')))]),
 'CORE_ONY_022': ('none', [discover(pool(card_type='SPELL', school='HOLY', classes='own_or_neutral'))]),
 'CORE_WON_096': ('none', [discover(pool(minimum=1, maximum=1, classes='own_or_neutral'))]),
 'CORE_WON_350': ('none', [discover(TAUNT, attack=1, health=2)]),
 'Core_UNG_072': ('none', [discover(TAUNT)]),
 'CATA_484': ('none', [discover(pool(card_type='SPELL', minimum=1, maximum=1))]),
 'DINO_424': ('none', [discover(pool(card_type='MINION', rarity='LEGENDARY', classes='own_or_neutral'), 'board', stats=(10, 10))]),
 'DINO_426': ('none', [discover(pool(card_type='MINION', minimum=3, maximum=3, classes='own_or_neutral'), 'board', stats=(2, 3))]),
 'EDR_270': ('none', [discover(pool(card_type='SPELL', school='NATURE', classes='own_or_neutral'), cost_delta=-2)]),
 'JAIL_507': ('none', [('generation_mana_branch', 10, random_cards(pool(card_type='MINION', mechanic='TAUNT', minimum=6, maximum=6), destination='board'), random_cards(pool(card_type='MINION', mechanic='TAUNT', minimum=2, maximum=2), destination='board'))]),
 'TLC_334': ('none', [discover(pool(card_type='SPELL', minimum=8), set_cost=1)]),
 'TLC_514': ('none', [discover(pool(card_type='MINION', rarity='LEGENDARY', classes='own_or_neutral'), shuffle_unchosen=True)]),
 'JAIL_876': ('friendly_minion', [('generation_attach', random_cards(FOUR, 2, 'board'))]),
 'TLC_477': ('friendly_minion', [('buff', 4, 4), ('generation_attach', random_cards(FOUR, destination='board'))]),
 'CATA_471': ('none', [('generation_attach_board', random_cards(FOUR, destination='board'))]),
 'CORE_AT_062': ('none', [('summon', 'FP1_011', 3)]),
 'CORE_TID_931': ('none', [random_cards(pool(card_type='SPELL', minimum=5, classes='other'), 2)]),
 'FIR_952': ('none', [discover(pool(card_type='SPELL', school='FEL', classes='own_or_neutral')), ('generation_discount_school', 'FEL', 1)]),
 'FIR_913': ('none', []),
 'CORE_CFM_781': ('none', []),
}
DEATH_EFFECTS = {
 'JAIL_460': [random_cards(pool(card_type='WEAPON'))],
 'MEND_045': [random_cards(DRAGON, cost_delta=-2)],
 'TIME_613': [random_cards(LEGENDARY, cost_delta=-1)],
 'CATA_723': [random_cards(FOUR, 2, 'board')],
 'CORE_GVG_114': [random_cards(LEGENDARY, destination='board')],
 'DINO_431': [random_cards(pool(card_type='MINION', mechanic='TAUNT', minimum=5), destination='board')],
 'TLC_814': [random_cards(pool(card_type='SPELL', school=s)) for s in ('HOLY', 'SHADOW')],
 'DINO_434': [random_cards(pool(card_type='SPELL', minimum=1, maximum=1))],
 'FP1_011': [random_cards(BEAST)],
}
END_EFFECTS = {
 'CATA_474': [random_cards(pool(card_type='SPELL', school='HOLY'), cost_delta=-3)],
 'EDR_462': [random_cards(DRAGON)],
 'EDR_530': [random_cards(pool(card_type='SPELL', school='NATURE'))],
 'END_029': [random_cards(pool(card_type='SPELL', school='SHADOW'))],
 'CORE_ETC_111': [random_cards(pool(card_type='SPELL'), destination='enemy_top')],
}
TRIGGERS = {
 'FIR_913': (('spell_school_cast', 'FIRE'), [random_cards(pool(card_type='MINION', tribe='ELEMENTAL'), cost_delta=-3)]),
 'CORE_CFM_781': ('attacking_self', [random_cards(pool(classes='other'))]),
}
TOKEN_RULES = {'FP1_011': ('none', [])}


def requests_for(card_id):
    """All pool requests, including attached effects and the Webspinner token."""
    found = set()
    def walk(value):
        if isinstance(value, PoolRequest):
            found.add(value)
        elif isinstance(value, (tuple, list)):
            if value and value[0] == 'summon' and value[1] in TOKEN_RULES:
                walk(DEATH_EFFECTS.get(value[1], ()))
            for item in value:
                walk(item)
    for table in (RULES, DEATH_EFFECTS, END_EFFECTS, TRIGGERS):
        walk(table.get(card_id, ()))
    return found
