"""Historical damage-result continuations and generated bodies; unvalidated."""
from engine.game import Card
from .generation_cards import pool,random_cards,discover
from .historical_draw_batches import draw
from .historical_saidan import add

def op(name,*args):return ('historical_utility_damage_finish_'+name,)+args
TOKEN_RULES={
 'ONY_010':('character',[op('hit',2,'dragonbane')]),
 'ONY_032':('character',[op('hit',3,'foreign_discover')]),
 'WON_095':('character',[op('hit',3,'shadow_draw')]),
 'WON_323':('character',[op('hit',3,'demon_summon')]),
 'VAC_952':('minion',[op('hit',4,'deathrattle_discount')]),
 'TRL_347':('character',[op('hit',3,'devilsaur')]),
 'TRL_347t':('none',[]),
 'TRL_012':('character',[op('hit',2,'totem')]),
 'SCH_271':('character',[op('hit',2,'elementals')]),
 'SCH_271t':('none',[]),
 'GVG_045':('minion',[op('implosion')]),
 'GVG_045t':('none',[]),
 'VAC_526':('minion',[op('hit',7,'excess_hand')]),
 'WC_021':('minion',[op('hit',6,'excess_hero')]),
 'WORK_008':('none',[op('area',4,'excess_hero')]),
 'SCH_253':('none',[op('area',3,'spirits')]),
 'SCH_253t':('none',[]),
 'ONY_014':('none',[op('area',1,'honor_attack')]),
 'YOP_027':('minion',[op('bola')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def split(game,operation,ctx):
 prefix='historical_utility_damage_finish_'
 if not operation[0].startswith(prefix):return None
 name=operation[0][len(prefix):];owner=ctx['owner']
 if name=='implosion':return game._split_fixed_summon(op('hit',game.rng.randint(2,4),'imps'),ctx)
 if name=='hit':
  amount,mode=operation[1:];uid=ctx.get('target',0);target=game.players[-uid-1] if uid<0 else game._force_live(uid)
  if target is None:return ('batch30_noop',),()
  state=dict(victim=target,health=target.health,dealt=0,mode=mode)
  if mode=='elementals':state['summons']=max(0,amount+ctx.get('bonus',0))*(game._spell_multiplier(owner) if ctx.get('spell') and not ctx.get('spell_multiplier_applied') else 1)
  return op('capture',uid,amount,state),(op('after',state),)
 if name=='after':
  state=operation[1];mode=state['mode'];victim=state['victim'];dealt=state['dealt'];excess=max(0,dealt-state['health']);dead=state.get('dead',False);honor=state.get('exact',False) and game.current==owner;overkill=state.get('overkill',False) and game.current==owner
  if mode=='adventurer' and dead:return ('historical_copy_literal_family','adventurer','board'),()
  if mode=='dragonbane' and honor:return ('add','ONY_010',1),()
  if mode=='foreign_discover' and honor:return game._split_fixed_summon(discover(pool(card_type='SPELL',classes='other')),ctx)
  if mode=='shadow_draw' and dead:return game._split_fixed_summon(draw((('type','eq','SPELL'),('school','eq','SHADOW'))),ctx)
  if mode=='demon_summon' and dead:return game._split_fixed_summon(random_cards(pool(card_type='MINION',tribe='DEMON'),destination='board'),ctx)
  if mode=='deathrattle_discount' and dead:return ('next_discount','DEATHRATTLE',3,'persistent'),()
  if mode=='devilsaur' and overkill:return game._split_fixed_summon(('summon','TRL_347t',1),ctx)
  if mode=='totem' and overkill:return ('historical_family_basic_totem',),()
  if mode=='elementals':return game._split_fixed_summon(('summon','SCH_271t',state['summons']),ctx)
  if mode=='imps':return game._split_fixed_summon(('summon','GVG_045t',dealt),ctx)
  if mode=='excess_hand' and excess:return op('hand_gain',excess),()
  if mode=='excess_hero' and excess:return game._split_fixed_summon(('replay_context',(('damage_own_hero',excess),),dict(ctx,bonus=0,spell_multiplier_applied=True)),ctx)
  return ('batch30_noop',),()
 if name=='area':
  amount,mode=operation[1:];state=dict(victims=tuple(m for player in game.players for m in player.minions if m.health>0),kills=0,excess=0,exact=0)
  return op('area_hit',amount,state),(op('area_after',mode,state),)
 if name=='area_after':
  mode,state=operation[1:]
  if mode=='spirits':return game._split_fixed_summon(('summon','SCH_253t',state['kills']),ctx)
  if mode=='honor_attack':return ('hero_attack',state['exact'] if game.current==owner else 0),()
  if mode=='excess_hero' and state['excess']:return game._split_fixed_summon(('replay_context',(('damage_own_hero',state['excess']),),dict(ctx,bonus=0,spell_multiplier_applied=True)),ctx)
  return ('batch30_noop',),()
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_damage_finish_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='capture':
  uid,amount,state=operation[1:];state['dealt']=game._deal_effect(uid,amount,ctx)
  state['dead']=state['victim'].health<=0;state['exact']=state['dealt']>0 and state['victim'].health==0;state['overkill']=state['dealt']>state['health'] and state['victim'].health<0
 elif name=='hand_gain':
  values=[c for c in p.hand if game._card_data(c)['type']=='MINION']
  if values:
   c=game.rng.choice(values);add(c,'attack_bonus',operation[1]);add(c,'health_bonus',operation[1])
 elif name=='area_hit':
  amount,state=operation[1:]
  with game._damage_batch():
   for m in state['victims']:
    if game._force_live(m.uid) is None:continue
    before=m.health;dealt=game._deal_effect(m.uid,amount,ctx)
    state['kills']+=int(m.health<=0);state['exact']+=int(dealt>0 and m.health==0);state['excess']+=max(0,dealt-before)
 elif name=='bola':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   board=game.players[target.owner].board;i=board.index(target);neighbors=[board[j] for j in (i-1,i+1) if 0<=j<len(board) and board[j] in game.players[target.owner].minions]
   with game._damage_batch():
    game._deal_effect(target.uid,1,ctx)
    for m in neighbors:game._deal_effect(m.uid,2,ctx)
 else:return False
 return True
