"""Resumable historical repeat spells and persistent Discover discounts."""
from .generation_cards import pool,discover
from .selectors import has_tribe

def op(name,*args):return ('historical_utility_repeat_batch_'+name,)+args
TOKEN_RULES={
 'BT_117':('none',[op('start','storm')]),
 'GVG_050':('none',[op('start','blade')]),
 'WON_325':('none',[op('start','blade')]),
 'AV_250':('minion',[op('start','snow')]),
 'SCH_158':('none',[discover(pool(card_type='MINION',tribe='DEMON',classes='own_or_neutral')),('next_discount','DEMON',1,'persistent')]),
 'SCH_233':('none',[discover(pool(card_type='MINION',tribe='DRAGON',classes='own_or_neutral')),('next_discount','DRAGON',1,'persistent')]),
 'SCH_237':('none',[discover(pool(card_type='MINION',mechanic='RUSH',classes='own_or_neutral')),('next_discount','RUSH',1,'persistent')]),
 'SCH_300':('none',[discover(pool(card_type='MINION',mechanic='DEATHRATTLE',classes='own_or_neutral')),('next_discount','DEATHRATTLE',1,'persistent')]),
 'SC_021':('none',[('board_buff',1,0),op('zerg_buff')]),
 'SC_407':('minion',[('historical_utility_archive_health_one',),op('launch_discount')]),
 'SC_411':('character',[('damage',2),('armor',2),op('launch_discount')]),
 'GDB_122':('minion',[('buff',3,3),op('demon_discount')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def split(game,operation,ctx):
 prefix='historical_utility_repeat_batch_'
 if not operation[0].startswith(prefix):return None
 name=operation[0][len(prefix):]
 if name=='start':
  mode=operation[1];state=dict(mode=mode,previous=None,first=True,victims=(),remaining=50 if mode=='storm' else None)
  return game._split_fixed_summon(op('step',state),ctx)
 if name=='step':
  state=operation[1];mode=state['mode']
  if state.get('remaining') is not None:
   if state['remaining']<=0:return ('batch30_noop',),()
   state['remaining']-=1
  victims=[m for player in game.players for m in player.minions if m.health>0]
  if mode=='snow':
   if state['first']:victim=game._force_live(ctx.get('target'))
   else:
    options=[m for m in victims if m.uid!=state['previous']];victim=game.rng.choice(options) if options else None
   victims=[victim] if victim is not None else []
  elif mode in ('blade','flame'):
   if mode=='flame':victims=[m for m in victims if m.owner!=ctx['owner']]
   victims=[game.rng.choice(victims)] if victims else []
  if not victims:return ('batch30_noop',),()
  state['first']=False;state['victims']=tuple(victims)
  if mode=='snow':state['previous']=victims[0].uid
  return op('hit',state),(op('after',state),)
 if name=='after':
  state=operation[1];dead=any(m.health<=0 for m in state['victims']);mode=state['mode']
  if mode=='flame':
   return game._split_fixed_summon(('cast_fixed_spell','WC_020','random'),ctx) if dead else (('batch30_noop',),())
  repeat=not dead
  if repeat:return game._split_fixed_summon(op('step',state),ctx)
  return ('batch30_noop',),()
 return None

def execute(game,operation,ctx):
 name=operation[0]
 if name==op('zerg_buff')[0]:
  from .historical_copy_batches import ZERG_IDS
  for m in game.players[ctx['owner']].minions:
   if m.card_id in ZERG_IDS:game._buff(m,1,1)
  return True
 if name==op('hit')[0]:
  state=operation[1];mode=state['mode']
  with game._damage_batch():
   for victim in state['victims']:
    if game._force_live(victim.uid) is None:continue
    game._deal_effect(victim.uid,3 if mode=='flame' else 1,ctx)
    if mode=='snow':game._freeze(victim.uid)
  return True
 if name==op('launch_discount')[0]:
  p=game.players[ctx['owner']];p.historical_ship_discount=getattr(p,'historical_ship_discount',0)+2
  return True
 if name==op('demon_discount')[0]:
  target=game._force_live(ctx.get('target'))
  if target is not None and has_tribe(game._card_data(target),'DEMON'):game._effect(('next_discount','DEMON',2,'persistent'),ctx)
  return True
 return False
