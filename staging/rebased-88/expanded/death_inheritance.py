"""Private, immutable-by-convention bindings for copied Deathrattle memories.

Only effect-owned references are captured. Stats, controller, damage cause and
self-history still belong to the new bearer. Payloads never enter observations;
attached effects contain an opaque definition key and the public donor ID.
"""
from copy import deepcopy
from engine.cards import UnsupportedCard
from engine.game import Card, Minion

BOUND = frozenset(('muradin_return','hammer_shuffle','brox_return','historic_gigafin_dispose','historical_secret_v3_sack_return','stored_release','stored_return_devoured','historic_gigafin_return',
                   'historic_nellie_return','return_remembered_discards','cast_absorbed_spell',
                   'dormant_release','infinity_restore_cost','b60_discard_remembered',
                   'b60_discard_secret','b60_hatch'))
PHYSICAL_REVIEW = frozenset()


def _valid_memory(name,value):
    integer=lambda item:type(item) is int
    identity=lambda item:isinstance(item,str) and bool(item)
    sequence=lambda item:isinstance(item,(tuple,list))
    if name=='muradin_return':return sequence(value) and all(isinstance(v,Card) for v in value)
    if name=='hammer_shuffle':return value is None
    if name=='brox_return':return value is None or integer(value)
    if name=='historic_gigafin_dispose':return integer(value)
    if name=='historical_secret_v3_sack_return':return value is None or isinstance(value,Minion)
    if name=='stored_release':
        return ((value[0] is None or isinstance(value[0],Minion)) and
                (value[1] is None or isinstance(value[1],Card)))
    if name=='stored_return_devoured':
        return sequence(value) and all(sequence(row) and len(row)==2 and integer(row[0]) and row[0] in (0,1) and isinstance(row[1],Card) for row in value)
    if name in ('historic_gigafin_return','historic_nellie_return'):
        return sequence(value) and all(identity(cid) for cid in value)
    if name=='return_remembered_discards':return all(identity(cid) for cid in value[0]) and integer(value[1])
    if name=='cast_absorbed_spell':return value is None or identity(value)
    if name in ('dormant_release','b60_discard_remembered'):return value is None or integer(value)
    if name=='infinity_restore_cost':
        return sequence(value) and all(sequence(row) and len(row)==2 and all(integer(item) for item in row) for row in value)
    if name=='b60_discard_secret':
        return sequence(value) and len(value)==2 and integer(value[0]) and value[0] in (0,1) and (value[1] is None or integer(value[1]))
    if name=='b60_hatch':return integer(value) and value>=0
    return False


def _remember(game, source, operation):
    name=operation[0]
    state=getattr(source,'rule_state',{})
    if name=='muradin_return':
        held=([source._muradin_hammer]+list(getattr(source,'_muradin_extra_hammers',()))) if hasattr(source,'_muradin_hammer') else []
        value=tuple(h['card'] for h in held)
    elif name=='hammer_shuffle':value=None
    elif name=='brox_return':value=getattr(source,'_brox_chain',None)
    elif name=='historic_gigafin_dispose':value=state.get('colossal_parent',0)
    elif name=='historical_secret_v3_sack_return':value=getattr(source,'_bound_minion',None)
    elif name=='stored_release':
        value=(getattr(source,'_bound_minion',None),getattr(source,'_bound_card',None))
    elif name in ('stored_return_devoured','historic_gigafin_return'):
        value=getattr(source,'_devoured_cards',())
    elif name=='historic_nellie_return':value=getattr(source,'_nellie_crew',())
    elif name=='return_remembered_discards':value=(tuple(source.remembered_discards),operation[1])
    elif name=='cast_absorbed_spell':value=state.get('absorbed_spell_id')
    elif name=='dormant_release':value=state.get('imprisoned_entity')
    elif name=='infinity_restore_cost':value=getattr(source,'_infinity_cost_receipts',())
    elif name=='b60_discard_remembered':value=getattr(source,'remembered_draw',None)
    elif name=='b60_discard_secret':value=getattr(source,'secret_discard',(1-source.owner,None))
    elif name=='b60_hatch':value=state.get('egg_bonus',0)
    else:raise UnsupportedCard('No inherited binding schema: '+name)
    if not _valid_memory(name,value):raise UnsupportedCard('Invalid inherited Deathrattle memory: '+name)
    if not hasattr(game,'_inherited_death_definitions'):game._inherited_death_definitions={}
    key=len(game._inherited_death_definitions)+1
    game._inherited_death_definitions[key]=dict(kind=name,value=deepcopy(value),card_id=source.card_id)
    return ('inherited_deathrattle',key,source.card_id)


def capture(game, source, operations):
    """Bind explicit memory operands before the donor's own effects consume them."""
    def bind(op):
        name=op[0]
        if name in PHYSICAL_REVIEW:return ('unreviewed_inherited_physical',name,source.card_id)
        if name in BOUND:return _remember(game,source,op)
        if name in ('when_state','if_state','historical_if_combo'):
            return tuple(op[:-1])+(bind(op[-1]),)
        if name=='if_holding':return tuple(op[:2])+tuple(bind(child) for child in op[2:])
        if name=='schedule_turn_effect':
            return tuple(op[:4])+(tuple(bind(child) for child in op[4]),)
        # A previously inherited definition is immutable and can be shared. Each
        # execution materializes its own deep copy, including repeated triggers.
        return deepcopy(op)
    return tuple(bind(op) for op in operations)


def check_supported(operations):
    def walk(value):
        if not isinstance(value,(tuple,list)) or not value:return
        if value[0]=='unreviewed_inherited_physical':
            raise UnsupportedCard('Inherited physical-card relationship requires review: '+value[1])
        for child in value:walk(child)
    walk(operations)


def _definition(game, op):
    if len(op)!=3 or type(op[1]) is not int:
        raise UnsupportedCard('Invalid inherited Deathrattle reference')
    record=getattr(game,'_inherited_death_definitions',{}).get(op[1])
    if record is None or record['card_id']!=op[2]:
        raise UnsupportedCard('Missing inherited Deathrattle definition')
    return deepcopy(record)


def split(game, op, context):
    if op[0]!='inherited_deathrattle':return None
    record=_definition(game,op);name=record['kind'];value=record['value'];operations=()
    if name=='stored_return_devoured':
        operations=tuple(('stored_return_one',owner,card) for owner,card in value)
    elif name=='historic_gigafin_return':
        operations=tuple(('historic_gigafin_spit',cid,1-context['owner']) for cid in value)
    elif name=='historic_nellie_return':
        operations=tuple(('inherited_add_at_cost',cid,1,0) for cid in value)
    elif name=='return_remembered_discards':
        identities,discount=value
        operations=tuple(('inherited_add_at_cost',cid,None,-discount) for cid in identities)
    elif name=='cast_absorbed_spell':
        operations=(('cast_fixed_spell',value,'random'),) if value else ()
    else:
        return ('inherited_death_atomic',op[1],op[2]),()
    if not operations:return ('batch30_noop',),()
    first,tail=game._split_fixed_summon(operations[0],context)
    return first,tuple(tail)+operations[1:]


def execute(game, op, context):
    name=op[0];owner=context['owner']
    if name=='unreviewed_inherited_physical':
        raise UnsupportedCard('Inherited physical-card relationship requires review: '+op[1])
    if name=='inherited_deathrattle':
        _definition(game,op)
        game._rule_events.append(('captured_effects',dict(operations=(op,),context=dict(context)),[]))
        return True
    if name=='inherited_add_at_cost':
        card=Card(game._new_id(),op[1]);card.cost_delta=op[3]
        if op[2] is not None:card.set_cost=op[2]
        game._enter_hand(owner,card)
        return True
    if name!='inherited_death_atomic':return False
    record=_definition(game,op);kind=record['kind'];value=record['value']
    if kind in ('muradin_return','hammer_shuffle'):
        from .approximation_policy import mark
        mark(game,kind)
        if kind=='muradin_return':
            for card in value:game._enter_hand(owner,game._copy_card(card))
        else:
            card=Card(game._new_id(),'TIME_209t')
            card.attack_bonus=max(0,getattr(context.get('source'),'attack',game.cards['TIME_209t']['attack']))+2-game.cards['TIME_209t']['attack']
            game.players[owner].deck.insert(game.rng.randrange(len(game.players[owner].deck)+1),card)
            game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
    elif kind=='brox_return':
        from types import SimpleNamespace
        proxy=SimpleNamespace()
        if value is not None:proxy._brox_chain=value
        game._brox_effect(('brox_return',),dict(context,source=proxy))
    elif kind=='historic_gigafin_dispose':
        parent=next((m for player in game.players for m in player.all_minions if m.uid==value),None)
        if parent is not None and parent.card_id=='TSC_962':parent._devoured_cards=[]
    elif kind=='historical_secret_v3_sack_return':
        from .historical_secret_v3 import return_bound
        return_bound(game,value)
    elif kind=='stored_release':
        bound,card=value
        game._stored_release_value(owner,bound,card,context.get('death_position',-1))
    elif kind=='dormant_release':game._awaken(game._dormant_entity(value))
    elif kind=='infinity_restore_cost':
        for uid,token in value:
            for player in game.players:
                for card in player.hand+player.deck:
                    if getattr(card,'uid',None)==uid:
                        card._infinity_cost_layers=[layer for layer in getattr(card,'_infinity_cost_layers',()) if layer!=token]
    elif kind in ('b60_discard_remembered','b60_discard_secret'):
        recipient,uid=(owner,value) if kind=='b60_discard_remembered' else value
        card=next((c for c in game.players[recipient].hand if c.uid==uid),None)
        if card is not None:game._discard_card(recipient,card)
    elif kind=='b60_hatch':
        game._summon(owner,'CATA_210t',context.get('death_position',-1),attack_bonus=value,health_bonus=value,
                     entry_origin='deathrattle',entry_site='inherited_twilight_egg',entry_source=context.get('source'))
    else:raise UnsupportedCard('Inherited atomic effect not implemented: '+kind)
    return True


def bearer_uses(game, minion, name):
    """Check explicit inherited operations without treating donor state as self."""
    if not minion.attached_death_effects:return False
    def contains(value):
        if not isinstance(value,(tuple,list)) or not value:return False
        if value[0]==name:return True
        return any(contains(child) for child in value)
    return contains(minion.attached_death_effects)
