"""Resumable rays, darts, excess damage and Corpse Explosion programs."""
TOKEN_RULES={
 'REV_950':('none',[('historical_volley_toll',)]),
 'WW_006':('none',[('historical_volley_darts',)]),
 'WW_405':('none',[('historical_volley_fan',)]),
 'TOY_640':('minion',[('historical_volley_mishap',)]),
 'REV_369':('none',[('historical_volley_collateral',)]),
 'RLK_035':('none',[('historical_volley_explosion',)]),
 'ETC_528':('none',[('historical_volley_lightshow',)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def live(game,uid):return next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_volley_toll':return ('historical_volley_ray',),tuple(('historical_volley_ray',) for _ in range(4))
 if name=='historical_volley_darts':
  state=dict(targets=[])
  return ('historical_volley_dart',state),(('historical_volley_dart',state),('historical_volley_coin',state))
 if name=='historical_volley_fan':
  count=max(0,6+ctx.get('bonus',0))
  if ctx.get('spell'):count*=game._spell_multiplier(owner)
  operations=tuple(('historical_volley_lowest',) for _ in range(count))
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_volley_lightshow':
  previous=getattr(p,'historical_lightshow_count',0);p.historical_lightshow_count=previous+1
  operations=tuple(('historical_volley_beam',) for _ in range(2+previous))
  return operations[0],operations[1:]
 if name=='historical_volley_mishap':
  target=live(game,ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  board=game.players[target.owner].board;index=board.index(target)
  neighbors=tuple(m.uid for i,m in enumerate(board) if abs(i-index)==1 and m in game.players[target.owner].minions)
  state=dict(excess=0)
  return ('historical_volley_excess_hit',target.uid,5,state,bool(ctx.get('outcast'))),tuple(('historical_volley_excess_follow',uid,state,bool(ctx.get('outcast'))) for uid in neighbors)
 if name=='historical_volley_collateral':
  values=[m.uid for m in game.players[1-owner].minions if m.health>0];selected=game.rng.sample(values,min(3,len(values)));operations=[]
  for uid in selected:
   state=dict(excess=0);operations.extend((('historical_volley_excess_hit',uid,6,state,False),('historical_volley_excess_follow',game.hero_id(1-owner),state,False)))
  return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())
 if name=='historical_volley_explosion':
  if p.corpses<=0 or not any(m.health>0 for player in game.players for m in player.minions):return ('batch30_noop',),()
  return ('historical_volley_detonate',),(('area_damage','all_minions',1),('historical_volley_explosion',))
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_volley_ray':
  values=[m for player in game.players for m in player.minions if m.health>0]
  if values:
   minion=game.rng.choice(values)
   if minion.owner==owner:game._buff(minion,2,2)
   else:game._deal_effect(minion.uid,2,ctx)
 elif name=='historical_volley_dart':
  values=[m for m in game.players[1-owner].minions if m.health>0]
  if values:
   minion=game.rng.choice(values);op[1]['targets'].append(minion.uid);game._deal_effect(minion.uid,2,ctx)
 elif name=='historical_volley_coin':
  targets=op[1]['targets']
  if len(targets)==2 and targets[0]==targets[1]:game._add(owner,'GAME_005')
 elif name=='historical_volley_lowest':
  values=[(game.hero_id(1-owner),game.players[1-owner].health)]+[(m.uid,m.health) for m in game.players[1-owner].minions if m.health>0]
  low=min(health for _,health in values);uid=game.rng.choice([uid for uid,health in values if health==low])
  game._deal_effect(uid,1,dict(ctx,bonus=0,spell_multiplier_applied=True))
 elif name=='historical_volley_beam':
  values=[game.hero_id(1-owner)]+[m.uid for m in game.players[1-owner].minions if m.health>0]
  game._deal_effect(game.rng.choice(values),2,ctx)
 elif name=='historical_volley_excess_hit':
  target=live(game,op[1])
  if target is not None:
   before=target.health;dealt=game._deal_effect(target.uid,op[2],dict(ctx,lifesteal=bool(ctx.get('lifesteal') or op[4])))
   op[3]['excess']=max(0,dealt-before)
 elif name=='historical_volley_excess_follow':
  if op[2].get('excess',0)>0:game._deal_effect(op[1],op[2]['excess'],dict(ctx,bonus=0,spell_multiplier_applied=True,lifesteal=bool(ctx.get('lifesteal') or op[3])))
 elif name=='historical_volley_detonate':game._spend_corpses(owner,1)
 else:return False
 return True
