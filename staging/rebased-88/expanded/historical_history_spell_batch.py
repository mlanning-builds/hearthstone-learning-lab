"""Explicit historical death-record consumers; behavioral validation deferred."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .selectors import has_tribe
from .identities import canonical_identity
from .historical_resurrection_batches import card_deaths

def op(name,*args):return ('historical_utility_history_batch_'+name,)+args
TOKEN_RULES={
 'LOE_026':('none',[op('resurrect','all_murlocs')]),
 'YOP_009':('none',[op('resurrect','costs')]),
 'TRL_566':('none',[op('resurrect','beasts_turn')]),
 'LOOT_187':('none',[op('resurrect','deathrattle_small')]),
 'VAC_457':('none',[op('resurrect','highest_both')]),
 'VAC_948':('none',[op('resurrect','highest_taunts')]),
 'SCH_514':('none',[('damage_own_hero',3),op('death_hand')]),
 'ICC_213':('none',[op('offer','resurrect')]),
 'DAL_377':('none',[op('offer','nine_lives')]),
 'AV_317':('none',[op('offer','phylactery')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def split(game,operation,ctx):
 if operation[0]!=op('resurrect')[0]:return None
 owner=ctx['owner'];mode=operation[1];own=list(game.players[owner].death_records);selected=[]
 if mode=='all_murlocs':
  values=[r for p in game.players for r in p.death_records if has_tribe(game.cards[r['card_id']],'MURLOC')]
  selected=[(owner,r,None) for r in game.rng.sample(values,min(7,len(values)))]
 elif mode=='costs':
  for cost in (1,2,3):
   values=[r for r in own if game.cards[r['card_id']].get('cost',0)==cost]
   if values:selected.append((owner,game.rng.choice(values),None))
 elif mode=='beasts_turn':
  values=[r for r in own if r['turn']==game.turn and has_tribe(game.cards[r['card_id']],'BEAST')]
  selected=[(owner,r,None) for r in game.rng.sample(values,len(values))]
 elif mode=='deathrattle_small':
  values=[r for r in own if 'DEATHRATTLE' in game.cards[r['card_id']].get('mechanics',())]
  selected=[(owner,r,(1,1)) for r in game.rng.sample(values,min(2,len(values)))]
 elif mode=='highest_both':
  for side in (owner,1-owner):
   values=list(game.players[side].death_records)
   if values:
    highest=max(game.cards[r['card_id']].get('cost',0) for r in values)
    selected.append((side,game.rng.choice([r for r in values if game.cards[r['card_id']].get('cost',0)==highest]),None))
 elif mode=='highest_taunts':
  values=[r for r in own if 'TAUNT' in game.cards[r['card_id']].get('mechanics',())]
  for _ in range(3):
   if not values:break
   highest=max(game.cards[r['card_id']].get('cost',0) for r in values);r=game.rng.choice([r for r in values if game.cards[r['card_id']].get('cost',0)==highest]);selected.append((owner,r,None))
   identity=canonical_identity(game.cards[r['card_id']],game.cards);values=[other for other in values if canonical_identity(game.cards[other['card_id']],game.cards)!=identity]
 else:raise ValueError('Unknown explicit death-record selection')
 return sequence(game,ctx,(op('summon',side,r['card_id'],stats) for side,r,stats in selected))

def execute(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('summon')[0]:
  side,cid,stats=operation[1:];game._summon(side,cid,entry_origin='resurrection',entry_site=ctx.get('card_id'),entry_stats=stats);return True
 if name==op('death_hand')[0]:
  values=list(p.death_records)
  for r in game.rng.sample(values,min(2,len(values))):game._enter_hand(owner,Card(game._new_id(),r['card_id']))
  return True
 if name==op('offer')[0]:
  mode=operation[1];values=[r for r in p.death_records if mode=='resurrect' or 'DEATHRATTLE' in game.cards[r['card_id']].get('mechanics',())]
  unique={}
  for r in values:unique.setdefault(canonical_identity(game.cards[r['card_id']],game.cards),r['card_id'])
  ids=list(unique.values())
  if ids:
   ids=game.rng.sample(ids,min(3,len(ids)))
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite death-history Discover')
   game.pending_choice=dict(owner=owner,kind='historical_history_batch',mode=mode,context=dict(ctx),options=[dict(card_id=cid) for cid in ids]);game.phase='choice'
  return True
 return False

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_history_batch':return False
 owner=choice['owner'];mode=choice['mode'];cid=selected['card_id'];ctx=choice['context'];card=Card(game._new_id(),cid)
 if mode=='resurrect':
  game._discovery_result=game._summon(owner,cid,entry_origin='resurrection',entry_site='eternal_servitude')
 elif mode=='nine_lives':
  game._discovery_result=game._enter_hand(owner,card);operations=card_deaths(game,Card(game._new_id(),cid),owner)
  if operations:
   from .historical_devout import base_source
   source,definition=base_source(game,owner,Card(game._new_id(),cid));context=dict(ctx,source=source,physical_card=definition,card_id=cid,spell=False,bonus=0,lifesteal=False,target=0,death_position=len(game.players[owner].board))
   game._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
 elif mode=='phylactery':
  operations=card_deaths(game,card,owner)
  for m in game.players[owner].minions:
   m.attached_death_effects.extend(deepcopy(operations))
   if operations:m.keywords.add('DEATHRATTLE')
 return True
