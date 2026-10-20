"""Bru'kan's two distinct choices, literal invocations and rotating power."""
from engine.cards import UnsupportedCard
OPTIONS=('AV_258t','AV_258t2','AV_258t3','AV_258t4')
POWERS=('AV_258pt','AV_258p2','AV_258pt3','AV_258pt4')
ROOT_RULES={'AV_258':('none',[('historical_brukan_choose',)])}
TOKEN_RULES={
 'AV_258t':('none',[('summon','AV_258t6',2)]),
 'AV_258t2':('none',[('historical_batch_heal_friendly_characters',6)]),
 'AV_258t3':('none',[('damage_enemy_hero',6)]),
 'AV_258t4':('none',[('area_damage','enemy_minions',2)]),
 'AV_258t6':('none',[]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|frozenset(POWERS)|{'AV_258p','AV_258pt7'}


def offer(game,owner,picks,context):
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Bru kan choice')
 game.pending_choice=dict(owner=owner,kind='historical_brukan_elements',options=[dict(card_id=cid) for cid in OPTIONS if cid not in picks],picks=tuple(picks),context=context,_automatic=bool(context.get('automatic_choices',False)))
 game.phase='choice'


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_brukan_elements':return False
 picks=choice['picks']+(selected['card_id'],);owner=choice['owner']
 if len(picks)<2:offer(game,owner,picks,choice['context'])
 else:
  operations=tuple(('cast_fixed_spell',cid,'random') for cid in picks)+(('historical_brukan_install',picks),)
  game._rule_events.append(('captured_effects',dict(operations=operations,context=choice['context']),[]))
 return True


def rotate(game,owner):
 player=game.players[owner];power=player.primary_power
 if power is None or power['card_id'] not in POWERS:return
 # Preserve the physical power entity and modifiers during its automatic swap.
 power['card_id']=game.rng.choice(tuple(cid for cid in POWERS if cid!=power['card_id']))
 game._log('brukan_power_changed',player=owner,card=power['card_id'])


def power_operations(game,owner):
 power=game.players[owner].primary_power
 if power is None or power['card_id'] not in POWERS:return None
 cid=power['card_id']
 if cid=='AV_258pt':return (('summon','AV_258t6',2),)
 if cid=='AV_258p2':return (('historical_batch_heal_friendly_characters',6),)
 if cid=='AV_258pt3':return (('historical_copy_power_hit','enemy_hero',6),)
 return (('historical_brukan_lightning',),)


def split(game,op,ctx):
 if op[0]!='historical_brukan_lightning':return None
 operations=tuple(('replay_context',(('historical_copy_power_hit','target',2),),dict(ctx,target=m.uid)) for m in tuple(game.players[1-ctx['owner']].minions) if m.health>0)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]


def execute(game,op,ctx):
 if op[0]=='historical_brukan_choose':
  from .pools import require_fixed_cards
  require_fixed_cards(FIXED_TOKEN_IDS,game.cards)
  offer(game,ctx['owner'],(),dict(ctx));return True
 if op[0]=='historical_brukan_install':
  available=tuple(power for choice,power in zip(OPTIONS,POWERS) if choice not in op[1])
  game._replace_primary_power(ctx['owner'],dict(card_id=game.rng.choice(available)))
  return True
 return False
