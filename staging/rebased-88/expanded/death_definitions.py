"""Resolve dead physical definitions without replaying removable enchantments."""
from collections import defaultdict,deque


def definitions(game,owner):
    player=game.players[owner];records=defaultdict(deque)
    for record in player.death_records:records[record['card_id']].append(record['entity'])
    for cid in player.death_history:
        entity=records[cid].popleft() if records[cid] else None
        state=getattr(entity,'_crafted_definition',{}).get('state',{})
        yield entity if 'forge_parts' in state else cid


def cost(game,value):
    definition=getattr(value,'_crafted_definition',{})
    stored=definition.get('cost')
    return stored if stored is not None else game._card_data(value)['cost']


def summon(game,owner,value,context,site):
    cid=getattr(value,'card_id',value)
    return game._summon(owner,cid,entry_origin='resurrection',entry_site=site,
                        entry_source=value if hasattr(value,'card_id') else context.get('source'))


def has_deathrattle(game,value):
    state=getattr(value,'_crafted_definition',{}).get('state',{})
    if 'forge_parts' in state:return bool(state.get('forge_death'))
    return 'DEATHRATTLE' in game._card_data(value).get('mechanics',())
