"""Timed spell auras and attached attack/start triggers; unvalidated."""
def is_zerg(minion):
 from .historical_copy_batches import ZERG_IDS
 return minion.card_id in ZERG_IDS

def op(name,*args):return ('historical_utility_aura_finish_'+name,)+args
TOKEN_RULES={
 'AV_344':('none',[op('aura','bridge')]),
 'AV_661':('none',[op('aura','strife')]),
 'LEG_TTN_908':('none',[op('aura','crusader')]),
 'SC_011':('none',[op('aura','spawning')]),
 'VAC_922':('none',[op('aura','lifesaving')]),
 'AT_013':('minion',[op('attach_attack','glory')]),
 'EX1_363':('minion',[op('attach_attack','wisdom')]),
 'VAC_944':('minion',[('buff',3,3),op('curse')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def layers(game,owner,kind):return [a for a in getattr(game.players[owner],'historical_finish_auras',()) if a['kind']==kind]

def attack_bonus(game,minion):
 owner=minion.owner
 return len(layers(game,owner,'strife'))+(len(layers(game,owner,'spawning')) if is_zerg(minion) else 0)

def keywords(game,minion):
 return {'RUSH'} if is_zerg(minion) and (layers(game,minion.owner,'spawning') or getattr(game.players[minion.owner],'historical_zerg_rush_turn',None)==game.turn) else set()

def summoned(game,data):
 owner=data['owner'];uid=data['source'];records=layers(game,owner,'bridge')
 if records:
  game._rule_events.append(('captured_effects',dict(operations=tuple(('buff',2,2) for _ in records),context=dict(owner=owner,source=None,target=uid,bonus=0,lifesteal=False,card_id='AV_344')),[]))

def summon_listener(game,owner):return bool(layers(game,owner,'bridge'))

def before_attack(game,uid):
 m=game._force_live(uid)
 if m is None:return
 callbacks=[(a['uid'],m.owner,(('buff',2,1),),'LEG_TTN_908') for a in layers(game,m.owner,'crusader')]
 for grant in m.rule_state.get('historical_finish_attacks',()):
  owner=grant['owner'];kind=grant['kind'];operations=(('heal_own_hero',4),) if kind=='glory' else (('draw',1),)
  callbacks.append((grant['uid'],owner,operations,'AT_013' if kind=='glory' else 'EX1_363'))
 for order,owner,operations,cid in sorted(callbacks,key=lambda row:row[0]):
  game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=owner,source=None,target=uid,bonus=0,lifesteal=False,card_id=cid)),[]))

def turn_entries(game,phase):
 owner=game.current;p=game.players[owner];entries=[]
 if phase=='end':
  for aura in tuple(getattr(p,'historical_finish_auras',())):
   operations=[]
   if aura['kind']=='lifesaving':operations.append(('add','VAC_917t',1))
   if aura['until']<=p.turns_taken:operations.append(op('expire',aura['uid']))
   if operations:entries.append(dict(source=None,order=aura['uid'],card_id=aura['card_id'],operations=tuple(operations)))
 if phase=='start':
  for m in p.minions:
   for grant in m.rule_state.get('historical_finish_curses',()):entries.append(dict(source=m,order=grant['uid'],card_id='VAC_944',operations=(('damage_own_hero',3),)))
 return entries

def execute(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('aura')[0]:
  duration=3+getattr(ctx.get('physical_card'),'rule_state',{}).get('aura_duration_delta',0)
  if duration>0:
   p.historical_finish_auras=getattr(p,'historical_finish_auras',[])+[dict(uid=game._new_id(),kind=operation[1],card_id=ctx.get('card_id'),until=p.turns_taken+duration-(1 if owner==game.current else 0))]
  game._refresh_auras();return True
 if name==op('expire')[0]:
  p.historical_finish_auras=[a for a in getattr(p,'historical_finish_auras',()) if a['uid']!=operation[1]];game._refresh_auras();return True
 if name==op('attach_attack')[0]:
  m=game._force_live(ctx.get('target'))
  if m is not None:m.rule_state.setdefault('historical_finish_attacks',[]).append(dict(uid=game._new_id(),kind=operation[1],owner=owner))
  return True
 if name==op('curse')[0]:
  m=game._force_live(ctx.get('target'))
  if m is not None:m.rule_state.setdefault('historical_finish_curses',[]).append(dict(uid=game._new_id()))
  return True
 return False
