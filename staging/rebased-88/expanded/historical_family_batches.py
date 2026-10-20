"""Explicit closed historical token families; implementation-only, unvalidated.

Literal family membership is independent of executable coverage. Complete
families are checked before sampling; no fallback or supported-only subset.
"""
from engine.cards import UnsupportedCard
from engine.game import Card
from .generation_cards import pool,random_cards,discover
from .pools import require_fixed_cards
from .selectors import has_tribe

LACKEYS=('DAL_613','DAL_614','DAL_615','DAL_739','DAL_741','DRG_052','ULD_616')
RULES={
 'DAL_400':('none',[('historical_family_lackeys',1)]),
 'DAL_413':('none',[]),
 'DAL_415':('none',[('historical_if_combo',('historical_family_lackeys',2))]),
 'DAL_433':('none',[('historical_family_lackeys',1)]),
 'DAL_606':('friendly_minion',[('destroy',),('historical_family_lackeys',2)]),
 'DRG_020':('none',[('historical_family_lackeys',1),('armor',3)]),
 'ULD_276':('none',[]),
 'YOD_035':('none',[]),
 'ULD_162':('historical_family_friendly_lackey',[('destroy',),('summon','ULD_162t',1)]),
 'ULD_168':('none',[('historical_family_tekahn',)]),
}
DEATH_EFFECTS={'DAL_413':[('historical_family_lackeys',1)]}
END_EFFECTS={'ULD_276':[('historical_family_lackeys',1)]}
TRIGGERS={'YOD_035':(('historical_event','lackey_played'),[('historical_family_lackeys',1)])}
TOKEN_RULES={
 'DAL_613':('none',[random_cards(pool(card_type='MINION',minimum=2,maximum=2),destination='board')]),
 'DAL_614':('character',[('damage',2)]),
 'DAL_615':('friendly_minion',[('historical_family_evolve_target',1)]),
 'DAL_739':('friendly_minion',[('buff',1,0),('keyword','RUSH')]),
 'DAL_741':('none',[discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'DRG_052':('none',[discover(pool(card_type='MINION',tribe='DRAGON',classes='own_or_neutral'))]),
 'ULD_616':('friendly_minion',[('buff',0,2),('keyword','TAUNT')]),
 'ULD_162t':('none',[]),
}
BASIC_TOTEMS=('CS2_050','CS2_051','CS2_058','NEW1_009')
LIBRAMS=frozenset(('YOP_011','YOP_011t','BT_011','BT_024','BT_025','GDB_137','GDB_138','GDB_139'))
RULES.update({
 'AT_046':('none',[('historical_family_basic_totem',)]),
 'WON_081':('none',[('historical_family_basic_totem',)]),
 'WON_083':('none',[]),
 'SCH_615':('none',[]),
 'LOOT_062':('none',[('choose_self_effect',tuple((label,('summon',cid,1)) for label,cid in zip(('Searing Totem','Stoneclaw Totem','Strength Totem','Healing Totem'),BASIC_TOTEMS)))]),
 'LOOT_518':('none',[('historical_family_totems_alakir',)]),
 'EX1_572':('none',[]),
 'LEG_CS3_033':('none',[('dream_all',)]),
 'BT_020':('none',[('historical_family_libram_discount',1)]),
 'BT_026':('none',[('historical_family_libram_discount',2)]),
 'GDB_721':('none',[('historical_family_libram_discount',1)]),
 'GVG_078':('none',[]),
 'AT_007':('none',[('historical_family_both_random',pool(card_type='SPELL'),(('cost_delta',-2),))]),
 'WON_344':('none',[('historical_family_both_random',pool(card_type='SPELL'),(('cost_delta',-2),))]),
 'GIL_213':('none',[('historical_family_both_random',pool(card_type='MINION',minimum=2,maximum=2),())]),
 'ULD_289':('none',[('historical_family_both_random',pool(card_type='MINION',tribe='MURLOC'),())]),
})
DEATH_EFFECTS.update({'SCH_615':[('summon',cid,1) for cid in BASIC_TOTEMS],
 'GDB_721':[('historical_family_libram_discount',1)],'GVG_078':[('historical_family_parts_both',)]})
TRIGGERS['WON_083']=('spell_cast',[('historical_family_basic_totem',)])
END_EFFECTS['EX1_572']=[('dream_random',),('dream_random',)]
POWER_SET_COST={'AT_085':1,'TOY_381':0}
POWER_COST_DELTA={'YOP_030':-1}
RULES.update({cid:('none',[]) for cid in tuple(POWER_SET_COST)+tuple(POWER_COST_DELTA)+('AT_008','AT_080','ICC_902')})
RULES.update({
 'GIL_561':('none',[('historical_family_power_refresh',)]),
 'SCH_312':('none',[('historical_family_power_cost',0,None,False)]),
 'TRL_407':('none',[('historical_family_power_cost',0,None,True)]),
 'AT_115':('none',[('historical_family_power_cost',None,-2,False)]),
 'AT_132':('none',[('historical_family_power_upgrade',)]),
})
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def targets(game,cid,owner,mode):
 if mode!='historical_family_friendly_lackey':return None
 return [uid for uid in game._targets_for(cid,owner,'friendly_minion') if uid>0 and game._find(uid).card_id in LACKEYS] or [0]


def split(game,op,ctx):
 if op[0]=='historical_family_both_random':
  owner=ctx['owner'];request=op[1]
  game._generation_candidates(request,owner);game._generation_candidates(request,1-owner)
  first,tail=game._split_fixed_summon(('generate_random',request,1,'hand',op[2]),ctx)
  other=dict(ctx,owner=1-owner)
  return first,tuple(tail)+(('replay_context',(('generate_random',request,1,'hand',()),),other),)
 if op[0]=='historical_family_parts_both':
  from .historical_prime_batches import PARTS
  require_fixed_cards(PARTS,game.cards)
  return ('historical_prime_part',),(('replay_context',(('historical_prime_part',),),dict(ctx,owner=1-ctx['owner'])),)
 if op[0]=='historical_family_lackeys':
  if op[1]<=0:return ('batch30_noop',),()
  require_fixed_cards(LACKEYS,game.cards)
  return ('historical_family_lackey_one',),((('historical_family_lackeys',op[1]-1),) if op[1]>1 else ())
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_family_'):return False
 owner=ctx['owner'];p=game.players[owner]
 if name=='historical_family_power_refresh':
  p.power_used=False
  state=getattr(p,'historical_power_turn',{})
  if state.get('turn')==game.turn:state['count']=max(0,state.get('count',0)-1)
 elif name=='historical_family_power_cost':
  effect=dict(kind='set' if op[1] is not None else 'add',amount=op[1] if op[1] is not None else op[2])
  if op[3]:effect['expires']=game.turn
  p.next_power_cost_effects.append(effect)
 elif name=='historical_family_power_upgrade':
  if p.primary_power is None:
   from .genn import POWERS
   hero=getattr(p,'starting_hero_class',p.hero_class);cid=POWERS[hero]
   require_fixed_cards((cid,),game.cards)
   game._replace_primary_power(owner,dict(card_id=cid,upgraded_starting_class=hero,cost=game.cards[cid]['cost']))
 elif name=='historical_family_basic_totem':
  require_fixed_cards(BASIC_TOTEMS,game.cards);game._summon(owner,game.rng.choice(BASIC_TOTEMS),entry_origin='effect',entry_site='historical_basic_totem',entry_source=ctx.get('source'))
 elif name=='historical_family_totems_alakir':
  if set(BASIC_TOTEMS)<={m.card_id for m in p.minions}:game._summon(owner,'NEW1_010',entry_origin='effect',entry_site='historical_all_totems',entry_source=ctx.get('source'))
 elif name=='historical_family_libram_discount':p.historical_libram_discount=getattr(p,'historical_libram_discount',0)+op[1]
 elif name=='historical_family_lackey_one':
  require_fixed_cards(LACKEYS,game.cards)
  game._add(owner,game.rng.choice(LACKEYS))
 elif name=='historical_family_evolve_target':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is not None:
   from .transformations import evolve_pool
   candidates=game._generation_candidates(evolve_pool(game._card_stat(target,'cost',target.owner),op[1]),owner)
   if candidates:game._transform(target,game.rng.choice(candidates))
 elif name=='historical_family_tekahn':
  p.historical_lackeys_four=True
  for zone in (p.hand,p.deck):
   for i,value in enumerate(zone):
    if game._card_data(value)['id'] in LACKEYS:
     card=value if isinstance(value,Card) else Card(game._new_id(),value)
     card.base_stat_override=(4,4);card.attack_bonus=card.health_bonus=0;zone[i]=card
  for minion in p.minions:
   if minion.card_id in LACKEYS:
    minion.base_stat_override=(4,4)
    game._set_entity_stats(minion,4,4)
 else:return False
 return True


def powers_disabled(game):
 return any(m.card_id=='ICC_902' and not m.silenced and m.health>0 for player in game.players for m in player.minions)


def power_available(game,owner):
 if powers_disabled(game):return False
 p=game.players[owner]
 if not p.power_used or game._active('AT_008',owner):return True
 state=getattr(p,'historical_power_turn',{})
 used=state.get('count',0) if state.get('turn')==game.turn else 0
 return game._active('AT_080',owner) and used<2


def power_cost(game,owner,cost):
 if getattr(game.players[owner],'historical_raza',False):cost=0
 for m in game.players[owner].minions:
  if not m.silenced and m.health>0:
   if m.card_id in POWER_SET_COST:cost=POWER_SET_COST[m.card_id]
 cost+=sum(POWER_COST_DELTA.get(m.card_id,0) for m in game.players[owner].minions if not m.silenced and m.health>0)
 return cost
