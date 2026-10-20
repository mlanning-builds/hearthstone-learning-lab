"""Historical forced-combat programs; all new behavior is unvalidated."""
from engine.game import Card

def op(name,*args):return ('historical_utility_combat_spell_'+name,)+args
MINION=(('type','eq','MINION'),)
TOKEN_RULES={
 'BOT_429':('none',[op('start','zooka')]),
 'DAL_731':('none',[op('start','duel')]),
 'DED_508':('none',[('force_recruit_pair',MINION)]),
 'SW_023':('friendly_minion',[op('start','provoke')]),
 'TRL_119':('friendly_beast',[('buff',1,1),op('start','predator')]),
 'TRL_258':('none',[op('start','mass')]),
 'YOP_006':('enemy_minion',[op('start','hysteria')]),
 'ULD_134':('minion',[op('start','bees')]),
 'ULD_134t':('none',[]),
 'VAC_410':('enemy_character',[op('start','birds')]),
 'VAC_410t':('none',[]),
 'RLK_056':('enemy_minion',[op('start','resurrect_attackers')]),
 'SW_460':('enemy_minion',[op('start','return_attackers')]),
 'VAC_926':('none',[op('start','recruit_return')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def split(game,operation,ctx):
 prefix='historical_utility_combat_spell_'
 if not operation[0].startswith(prefix):return None
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner]
 if name=='start':
  mode=operation[1];state=dict(uids=[],mode=mode)
  if mode=='zooka':ops=[op('recruit',owner,state)]*3+[op('group',state),op('kill',state)]
  elif mode=='duel':ops=[op('recruit',owner,state),op('recruit',1-owner,state),op('duel',state)]
  elif mode in ('bees','birds'):
   count,cid=(4,'ULD_134t') if mode=='bees' else (2,'VAC_410t');ops=[op('summon',cid,state)]*count+[op('group',state)]
  elif mode=='provoke':
   state['uids']=[m.uid for m in q.minions if m.health>0];ops=[op('group',state)]
  elif mode=='predator':ops=[op('attack',ctx.get('target'),0,'random_enemy')]
  elif mode=='mass':
   state['uids']=[m.uid for player in game.players for m in player.minions if m.health>0];game.rng.shuffle(state['uids']);ops=[op('group',state)]
  elif mode=='hysteria':ops=[op('hysteria',ctx.get('target'),30)]
  elif mode in ('resurrect_attackers','return_attackers'):
   state['uids']=[m.uid for m in p.minions if m.health>0];state['death_start']=len(p.death_records);ops=[op('group',state),op('recover',state)]
  elif mode=='recruit_return':ops=[op('recruit',owner,state),op('recruit',owner,state)]
  else:raise ValueError('Unknown historical combat program')
  return sequence(game,ctx,ops)
 if name=='group':
  state=operation[1];mode=state['mode']
  selection='random_enemy' if mode=='zooka' else 'random_other' if mode=='mass' else 'bound'
  return sequence(game,ctx,(op('attack',uid,ctx.get('target',0),selection) for uid in state['uids']))
 if name=='attack':
  uid,target,selection=operation[1:];attacker=game._force_live(uid)
  if attacker is None:return ('batch30_noop',),()
  if selection=='random_enemy':
   values=[m.uid for m in game.players[1-attacker.owner].minions if m.health>0];target=game.rng.choice(values) if values else 0
  elif selection=='random_other':
   values=[m.uid for player in game.players for m in player.minions if m.uid!=uid and m.health>0];target=game.rng.choice(values) if values else 0
  if not target or target==uid or target>0 and game._force_live(target) is None:return ('batch30_noop',),()
  return game._split_fixed_summon(('force_pair',uid,target),ctx)
 if name=='duel':
  uids=operation[1]['uids']
  return game._split_fixed_summon(('force_pair',uids[0],uids[1]),ctx) if len(uids)==2 else (('batch30_noop',),())
 if name=='hysteria':
  uid,remaining=operation[1:];attacker=game._force_live(uid);values=[m.uid for player in game.players for m in player.minions if m.uid!=uid and m.health>0]
  if attacker is None or remaining<=0 or not values:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(('force_pair',uid,game.rng.choice(values)),ctx)
  return first,tuple(tail)+(op('hysteria',uid,remaining-1),)
 if name=='recover':
  state=operation[1];records=[r for r in p.death_records[state['death_start']:] if r['entity'].uid in state['uids']]
  if state['mode']=='resurrect_attackers':return sequence(game,ctx,(('summon',r['card_id'],1) for r in records))
  return sequence(game,ctx,(('add',r['card_id'],1) for r in records))
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_combat_spell_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner']
 if name=='recruit':
  side,state=operation[1:];m=game._recruit_from_zone(side,'deck',MINION,keyword='RUSH' if state['mode']=='recruit_return' else None,site='historical_combat_spell')
  if m is not None:
   state['uids'].append(m.uid)
   if state['mode']=='recruit_return':
    key=game._new_id();m.rule_state.setdefault('historical_combat_return',[]).append(key)
    game._schedule_turn_effect(game.current,'end',0,1,(op('return',m.uid,key),),source_card_id='VAC_926')
 elif name=='summon':
  cid,state=operation[1:];m=game._summon(owner,cid,entry_origin='effect',entry_site=ctx.get('card_id'))
  if m is not None:state['uids'].append(m.uid)
 elif name=='kill':
  for uid in operation[1]['uids']:
   m=game._force_live(uid)
   if m is not None:m.health=0
 elif name=='return':
  m=game._force_live(operation[1])
  if m is not None and operation[2] in m.rule_state.get('historical_combat_return',()):game._bounce(m)
 else:return False
 return True
