"""Tavish and all six Improved Secret consumers; implementation unvalidated."""
from engine.cards import UnsupportedCard
OPTIONS=('AV_113t1','AV_113t2','AV_113t3','AV_113t7','AV_113t8','AV_113t9')
ROOT_RULES={'AV_113':('none',[('historical_tavish_begin',)])}
FIXED_TOKEN_IDS=frozenset(OPTIONS)|{'AV_113p','AV_113t3t2','NEW1_032','NEW1_033','NEW1_034'}


def offer(game,owner,remaining,chosen,context):
 from .historical_secret_batches import admissible
 ids=[cid for cid in OPTIONS if cid not in chosen and admissible(game,owner,cid)]
 if not ids or remaining<=0:return
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Tavish Secret Discover')
 game.pending_choice=dict(owner=owner,kind='historical_tavish_secret',options=[dict(card_id=cid) for cid in game.rng.sample(ids,min(3,len(ids)))],remaining=remaining,chosen=tuple(chosen),context=context,_automatic=bool(context.get('automatic_choices',False)))
 game.phase='choice'


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_tavish_secret':return False
 cid=selected['card_id'];chosen=choice['chosen']+(cid,)
 operations=(('cast_fixed_spell',cid,'random'),('historical_tavish_continue',choice['remaining']-1,chosen))
 game._rule_events.append(('captured_effects',dict(operations=operations,context=choice['context']),[]))
 return True


def attack_program(game,secret,owner,actor,data):
 """Return an activation program plus cancellation, without revealing early."""
 cid=secret.card_id;enemy=game.players[actor];player=game.players[owner]
 attacker=next((m for m in enemy.minions if m.uid==data['source'] and m.health>0),None)
 defender=next((m for m in player.minions if m.uid==data['target'] and m.health>0),None)
 if cid=='AV_113t1' and data['target']==game.hero_id(owner):return (('area_damage','enemies',3),),False
 if cid=='AV_113t2' and attacker is not None:return (('historical_tavish_bounce',attacker.uid),),True
 if cid=='AV_113t3' and defender is not None and len(player.board)<7:return (('summon','AV_113t3t2',3),),False
 if cid=='AV_113t7' and defender is not None and len(player.board)<7:return (('historical_tavish_pack',defender),)*2,False
 return None


def turn_entries(game,phase):
 if phase!='start':return []
 player=game.players[game.current]
 return [dict(source=None,order=getattr(secret,'_secret_entry_order',secret.uid),operations=(('historical_tavish_cages',secret.uid),)) for secret in player.secrets if secret.card_id=='AV_113t8']


def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];player=game.players[owner]
 if name=='historical_tavish_begin':
  from .pools import require_fixed_cards
  require_fixed_cards(FIXED_TOKEN_IDS,game.cards)
  offer(game,owner,2,(),dict(ctx));return True
 if name=='historical_tavish_continue':offer(game,owner,op[1],op[2],dict(ctx));return True
 if name=='historical_tavish_bounce':
  victim=next((m for p in game.players for m in p.minions if m.uid==op[1] and m.health>0),None)
  if victim is not None:game._bounce(victim,4)
  return True
 if name=='historical_tavish_pack':
  original=op[1]
  if len(player.board)<7:
   game._summon(owner,original.card_id,copy_from=original,entry_origin='secret',entry_site='improved_pack_tactics',entry_stats=(3,3))
  return True
 if name=='historical_tavish_companion':
  for _ in range(1+player.companion_extra):
   ids=game._companion_ids(owner)
   if len(player.board)<7:game._summon(owner,game.rng.choice(ids),entry_origin='secret',entry_site='improved_open_cages')
  return True
 if name=='historical_tavish_cages':
  from .historical_secret_batches import blocked
  secret=next((c for c in player.secrets if c.uid==op[1] and c.card_id=='AV_113t8'),None)
  if secret is not None and not blocked(game) and len(player.minions)>=2 and len(player.board)<7:
   game._trigger_secret_program(owner,secret,(('historical_tavish_companion',),)*2,dict(ctx,secret_card=secret))
  return True
 if name=='historical_tavish_ice':
  card=op[1];recipient=op[2];hand=game.players[recipient].hand
  # Repeated activations can adjust the same returned card; never manufacture
  # a second physical copy of the countered spell.
  if not any(c is card for c in hand):
   card.cost_delta=getattr(card,'cost_delta',0)+2;game._enter_hand(recipient,card)
  else:card.cost_delta=getattr(card,'cost_delta',0)+2
  return True
 return False

TOKEN_RULES={cid:('none',[('secret',cid)]) for cid in OPTIONS}
TOKEN_RULES['AV_113t3t2']=('none',[])
