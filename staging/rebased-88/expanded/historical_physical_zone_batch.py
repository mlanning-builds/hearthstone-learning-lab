"""Physical-zone historical spell programs, awaiting behavioral validation."""
from engine.game import Card
from .selectors import has_tribe
from .historical_draw_batches import draw
from .historical_resurrection_batches import resurrect
from .historical_play_batches import zone_offer

def op(name,*args):return ('historical_utility_physical_'+name,)+args
MINION=(('type','eq','MINION'),)
SPELL=(('type','eq','SPELL'),)
TOKEN_RULES={
 'EX1_345t':('none',[]),
 'ONY_021':('none',[op('whelps')]),
 'AV_264':('none',[('schedule_turn_effect','start',1,1,(('historical_copy_recruit_one','hand',MINION+(('tribe','eq','DEMON'),),None,None),))]),
 'BOT_069':('none',[('historical_copy_recruit_one','hand',MINION,'RUSH',None)]*3),
 'BOT_435':('none',[zone_offer('enemy','deck',MINION,'copy',3,True)]),
 'BOT_436':('none',[op('lens')]),
 'BOT_567':('none',[op('gallery')]),
 'DAL_059':('none',[op('deck_copy',2,0)]),
 'DAL_173':('none',[op('darkest')]),
 'DMF_055':('none',[op('deck_copy',1,10)]),
 'DMF_084':('none',[resurrect('deathrattle',3)]),
 'EX1_345':('none',[op('mindgames')]),
 'GIL_813':('friendly_minion',[op('nightmare')]),
 'GVG_017':('none',[op('draw_conditional','beast')]),
 'GVG_029':('none',[('historical_copy_recruit_one','hand',MINION,None,None),op('opponent_hand')]),
 'ICC_235':('none',[op('deck_copy',1,5)]),
 'OG_073':('none',[op('draw_conditional','copies')]),
 'ONY_017':('none',[op('draw_conditional','dragon')]),
 'SCH_610':('none',[('historical_copy_recruit_one','deck',MINION+(('tribe','eq','BEAST'),('cost','le',5)),'RUSH',None)]*2),
 'TRL_244':('none',[op('draw_conditional','health')]),
 'TRL_255':('none',[('historical_copy_recruit_one','hand',MINION+(('tribe','eq','BEAST'),),'RUSH',None)]),
 'WON_028':('none',[op('small_beasts')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,ops):
 ops=tuple(ops)
 if not ops:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(ops[0],ctx)
 return first,tuple(tail)+ops[1:]

def split(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('opponent_hand')[0]:return game._split_fixed_summon(('replay_context',(('historical_copy_recruit_one','hand',MINION,None,None),),dict(ctx,owner=1-owner)),ctx)
 if name==op('whelps')[0]:return game._split_fixed_summon(('summon','ONY_001t',max(0,7-len(p.board))),ctx)
 if name==op('lens')[0]:
  a={};b={}
  return sequence(game,ctx,(('historical_draw_capture',MINION,'random',a),('historical_draw_capture',SPELL,'random',b),op('lens_finish',a,b)))
 if name==op('draw_conditional')[0]:
  mode=operation[1];state={};filters=MINION+(('tribe','eq','BEAST'),) if mode=='health' else MINION if mode=='dragon' else None
  return sequence(game,ctx,(('historical_draw_capture',filters,'random',state),op('draw_finish',mode,state)))
 if name==op('darkest')[0]:
  victims=tuple(p.minions)
  return op('kill_group',tuple(m.uid for m in victims)),tuple(('historical_copy_recruit_one','deck',MINION,None,None) for _ in victims)
 if name in (op('deck_copy')[0],op('gallery')[0],op('small_beasts')[0],op('mindgames')[0]):
  enemy=name==op('mindgames')[0];side=1-owner if enemy else owner
  candidates=[c for c in game.players[side].deck if game._card_data(c)['type']=='MINION']
  if enemy and not candidates:return game._split_fixed_summon(('summon','EX1_345t',1),ctx)
  if name==op('small_beasts')[0]:candidates=[c for c in candidates if has_tribe(game._card_data(c),'BEAST') and game._cost(c if isinstance(c,Card) else Card(0,c),side)<=3];selected=game.rng.sample(candidates,min(2,len(candidates)));stats=None;count=1
  elif name==op('gallery')[0]:selected=candidates;stats=(1,1);count=1
  else:
   selected=[game.rng.choice(candidates)] if candidates else [];count=1 if enemy else operation[1];size=0 if enemy else operation[2];stats=(size,size) if size else None
  # Capture physical cards before the first summon changes auras or the deck.
  copies=[game._copy_card(c,source_owner=side) for c in selected]
  return sequence(game,ctx,(op('summon_copy',c,stats) for c in copies for _ in range(count)))
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_physical_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='lens_finish':
  a,b=operation[1:];ca,cb=a.get('card'),b.get('card')
  if ca is not None and cb is not None:
   if ca in p.hand:game._set_card_cost(ca,b['cost'])
   if cb in p.hand:game._set_card_cost(cb,a['cost'])
 elif name=='draw_finish':
  mode,state=operation[1:];c=state.get('card')
  if c is None:return True
  if mode=='beast' and c in p.hand and has_tribe(game._card_data(c),'BEAST'):c.cost_delta=getattr(c,'cost_delta',0)-4
  elif mode=='health' and c in p.hand:
   from .historical_saidan import add
   add(c,'health_bonus',game._card_stat(c,'health',owner))
  elif mode=='copies':
   for _ in range(2):game._enter_hand(owner,game._copy_card(c,source_owner=owner))
  elif mode=='dragon' and has_tribe(game._card_data(c),'DRAGON'):
   game._rule_events.append(('captured_effects',dict(operations=(('summon','ONY_001t',2),),context=dict(ctx)),[]))
 elif name=='kill_group':
  for uid in operation[1]:
   m=game._force_live(uid)
   if m is not None:m.health=0
 elif name=='summon_copy':
  c,stats=operation[1:]
  game._summon(owner,c.card_id,attack_bonus=c.attack_bonus,health_bonus=c.health_bonus,entry_source=c,entry_zone='deck',entry_origin='copy',entry_site='historical_physical_spell',entry_stats=stats)
 elif name=='nightmare':
  m=game._force_live(ctx.get('target'))
  if m is not None:
   from copy import deepcopy
   donor=deepcopy(m);donor.health=1
   game._summon(owner,m.card_id,copy_from=donor,entry_origin='copy',entry_site='vivid_nightmare')
 else:return False
 return True
