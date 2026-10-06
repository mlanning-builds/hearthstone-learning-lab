"""Frozen Standard cards that generate older Constructed outcomes.

No outcome pool is approved here. Retired-set recognition is a rejection guard,
not a substitute for an explicit complete, reviewed membership contract.
"""
from engine.cards import UnsupportedCard
from .generation_cards import pool,PoolRequest,random_cards,discover

# Known retired regular Constructed sets in the frozen archive. In particular,
# VANILLA is the separate Classic-mode catalog, not original Constructed IDs.
PAST_SETS=frozenset('EXPERT1 LEGACY NAXX GVG BRM TGT LOE OG KARA GANGS UNGORO ICECROWN LOOTAPALOOZA GILNEAS BOOMSDAY TROLL DALARAN ULDUM DRAGONS YEAR_OF_THE_DRAGON DEMON_HUNTER_INITIATE BLACK_TEMPLE SCHOLOMANCE DARKMOON_FAIRE THE_BARRENS STORMWIND ALTERAC_VALLEY THE_SUNKEN_CITY REVENDRETH RETURN_OF_THE_LICH_KING PATH_OF_ARTHAS BATTLE_OF_THE_BANDS TITANS WILD_WEST WONDERS WHIZBANGS_WORKSHOP ISLAND_VACATION SPACE'.split())

NATURE=pool(card_type='SPELL',school='NATURE',classes='own_or_neutral',era='past')
MECH=pool(card_type='MINION',tribe='MECHANICAL',classes='PALADIN',era='past')
FIVE=pool(card_type='MINION',minimum=5,maximum=5,era='past')
MINION=pool(card_type='MINION',era='past')
DEMON=pool(card_type='MINION',tribe='DEMON',era='past')
ONE=pool(card_type='MINION',minimum=1,maximum=1,era='past')
ARCANE=pool(card_type='SPELL',school='ARCANE',classes='own_or_neutral',era='past')
COLOSSAL=pool(card_type='MINION',mechanic='COLOSSAL',era='past')
RULES={
 'CATA_EVENT_000':('none',[random_cards(COLOSSAL)]),
 'TIME_013':('none',[]),
 'TIME_016':('none',[discover(MECH,attack=5,health=5)]),
 'TIME_040':('none',[]),
 'TIME_052':('none',[]),
 'TIME_444':('none',[]),
 'TIME_711':('none',[random_cards(ONE,2,'board',combo_attack=1)]),
 'TIME_857':('none',[discover(ARCANE,cost_delta=-2),discover(ARCANE,cost_delta=-2)]),
}
DEATH_EFFECTS={
 'TIME_040':[random_cards(FIVE)],
 'TIME_052':[random_cards(MINION,destination='board')],
 # Weapon destruction executes simple effects directly; no split-only opcode.
 'TIME_444':[('generate_one',DEMON,'hand',())],
}
TRIGGERS={'TIME_013':('spell_cast',[discover(NATURE)])}

def requests_for(cid):
    result=set()
    def walk(value):
        if isinstance(value,PoolRequest):result.add(value)
        elif isinstance(value,(tuple,list)):
            for child in value:walk(child)
    for table in (RULES,DEATH_EFFECTS,TRIGGERS):walk(table.get(cid,()))
    return result


def validate_past_candidates(ids,metadata):
    from standard.catalog import load_catalog
    def canonical(d):return d.get('countAsCopyOfDbfId',d.get('dbfId',d['id']))
    standard={canonical(d) for d in load_catalog()}
    invalid=[cid for cid in ids if not metadata[cid].get('collectible')
             or metadata[cid].get('set') not in PAST_SETS
             or metadata[cid].get('type') not in ('MINION','SPELL','WEAPON','HERO','LOCATION')
             or canonical(metadata[cid]) in standard]
    if invalid:raise UnsupportedCard('Historical contract includes Standard cards, tokens, or unreviewed Constructed sets: '+', '.join(invalid))
