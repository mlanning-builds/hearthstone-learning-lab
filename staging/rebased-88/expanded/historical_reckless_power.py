"""Reckless Apprentice uses resumable real Hero Power programs."""
ROOT_RULES={'BAR_544':('none',[('historical_reckless_begin',)])}
PASSIVE_POWERS=frozenset(('ICC_827p','YOD_009h','BOT_238p','AV_258p','AV_258pt7','GIL_504h','END_003p','JAIL_800hp1','JAIL_800hp2'))

def split(game,op,ctx):
 name=op[0];owner=ctx['owner'];player=game.players[owner]
 if name=='historical_reckless_begin':
  # Keep the original enemy roster; newly summoned enemies are not added.
  targets=(game.hero_id(1-owner),)+tuple(m.uid for m in game.players[1-owner].minions if m.health>0)
  operations=tuple(('historical_reckless_fire',uid) for uid in targets)
  first,tail=split(game,operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if name=='historical_reckless_plague':
  from .historical_combined_choices import combined,consume
  if combined(game,owner):
   consume(game,owner);operations=(('hero_attack',3),('armor',3))
  else:operations=(game.rng.choice((('hero_attack',3),('armor',3))),)
  return game._split_fixed_summon(('replay_context',operations,ctx),ctx)
 if name!='historical_reckless_fire':return None
 target=op[1]
 if target>0 and not any(m.uid==target and m.health>0 for m in game.players[1-owner].minions):return ('batch30_noop',),()
 power=player.primary_power
 if power is not None:
  if power['card_id']=='UNG_917t1':
   from .selectors import has_tribe
   victim=next((m for m in game.players[1-owner].minions if m.uid==target),None)
   if victim is None or not has_tribe(game._card_data(victim),'BEAST'):return ('batch30_noop',),()
  if power['card_id'] in PASSIVE_POWERS:return ('batch30_noop',),()
  if power['card_id'] in ('ICC_481p','SC_754p','EDR_448p'):return ('batch30_noop',),()
 operations=game._repeated_power_operations(owner)
 bonus=sum(value['amount'] for value in getattr(player,'historical_next_power_damage',()) if value['turn']==game.turn)
 frame=dict(freeze=getattr(player,'historical_next_power_freeze',False),damage_bonus=bonus)
 player.historical_next_power_freeze=False;player.historical_next_power_damage=[]
 player.next_power_cost_effects.clear();player.next_power_increase=0
 post=[]
 if power is not None and power['card_id'] in ('TLC_632t','TLC_632t2'):post.append(('replacement_power_consumed',power.get('uid')))
 if power is not None and power['card_id'] in ('TOY_400t6p','TOY_400t6p2','BT_429p','BT_429p2'):post.append(('historical_reckless_mint_consumed',power.get('uid')))
 post.append(('historical_reckless_used',))
 repeats=max(game._trigger_repetitions(owner),2 if game._active('TOY_528',owner) else 1)
 program,context=game._power_program(owner,operations,target=target,repeats=repeats,post_operations=tuple(post),frame_override=frame)
 context['automatic_choices']=True
 return game._split_fixed_summon(('replay_context',program,context),ctx)

def execute(game,op,ctx):
 owner=ctx['owner'];player=game.players[owner]
 if op[0]=='historical_reckless_used':
  player.hero_power_uses+=1
  game._queue_event('hero_power_used',owner=owner)
  return True
 if op[0]=='historical_reckless_mint_consumed':
  power=player.primary_power
  if power is not None and power.get('uid')==op[1] and power['card_id'] in ('TOY_400t6p','TOY_400t6p2','BT_429p','BT_429p2'):
   power['remaining']-=1
   if power['remaining']<=0:game._replace_primary_power(owner,power.get('restore'))
   else:power['card_id']='BT_429p2' if power['card_id'] in ('BT_429p','BT_429p2') else 'TOY_400t6p2'
  return True
 return False
