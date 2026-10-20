"""Explicit inherited properties for physical composite minions.

These payloads are supplied by reviewed ForgePart contracts, never derived from
rules text or substituted for complete production membership.
"""
from engine.cards import UnsupportedCard
from .effect_schema import validate_operations, EffectSchemaError

NUMERIC = frozenset(('spell_damage','damaged_spell_damage','damaged_attack','cost_floor','overload','adjacent_attack','friendly_attack','rewind','end_zone_attack','beast_attack'))
BOOLEAN = frozenset(('enemy_taunt','suppress_draw','cleave','beast_charge','prepare','prepare_discount'))


def validate_intrinsics(entries, path):
    if not isinstance(entries, tuple):
        raise UnsupportedCard(path+': intrinsic properties must be a tuple')
    for entry in entries:
        if not isinstance(entry, tuple) or len(entry)!=2 or not isinstance(entry[0],str):
            raise UnsupportedCard(path+': invalid intrinsic property')
        name,value=entry
        if name in NUMERIC:
            valid=type(value) is int and value>=0
        elif name=='dormant_turns':
            valid=type(value) is int and value>0
        elif name in BOOLEAN:
            valid=type(value) is bool
        elif name=='cost_rule':
            valid=isinstance(value,str) and value in ('deaths_turn','hero_healed','friendly_minions')
        elif name in ('start_effects','end_effects','trigger'):
            if name=='trigger':
                valid=(isinstance(value,tuple) and len(value)==2 and
                       (isinstance(value[0],str) and value[0] in ('spell_cast','b60_friendly_death','other_friendly_minion_played') or
                        value[0] in (('summon','friendly','BEAST'),('historical_event','friendly_beast_death'))))
                operations=value[1] if valid else ()
            else:
                valid=True;operations=value
            if valid:
                try:validate_operations(operations,path+'.'+name,strict_unknown=True)
                except EffectSchemaError as exc:raise UnsupportedCard(str(exc)) from exc
        else:
            raise UnsupportedCard(path+': unknown intrinsic property '+name)
        if not valid:raise UnsupportedCard(path+': invalid intrinsic '+name)


def values(entity, name):
    if getattr(entity,'silenced',False):return ()
    return tuple(value for key,value in getattr(entity,'rule_state',{}).get('forge_intrinsics',()) if key==name)


def spell_damage(entity):
    return sum(values(entity,'spell_damage'))+(sum(values(entity,'damaged_spell_damage')) if entity.health<entity.max_health else 0)


def damaged_attack(entity):
    return sum(values(entity,'damaged_attack')) if entity.health<entity.max_health else 0


def cost_floor(entity):
    return max(values(entity,'cost_floor'),default=0)


def intrinsic_cost(game, card, owner, cost):
    for rule in values(card,'cost_rule'):
        if rule=='deaths_turn':cost-=sum(player.minions_died_turn for player in game.players)
        elif rule=='hero_healed' and game.players[owner].hero_healed_turn:cost=0
        elif rule=='friendly_minions':cost-=len(game.players[owner].minions)
    return cost


def listeners(game):
    return [(m,trigger) for player in game.players for m in player.minions if m.health>0
            for trigger in values(m,'trigger')]

