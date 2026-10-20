"""Captured excess definitions for three Bottles and damage-cost Shimmer Shot."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,random_cards
from .pools import require_fixed_cards
BOTTLES=frozenset(('WW_052t2','WW_393t','WW_395t'))
TOKEN_RULES={
 'WW_052':('none',[('historical_bottle_swarm',10,True)]),
 'WW_052t':('none',[]),
 'WW_052t2':('none',[('historical_bottle_contents','bugs')]),
 'WW_393':('enemy_minion',[('historical_bottle_shadeleaf',)]),
 'WW_393t':('enemy_minion',[('historical_bottle_contents','damage')]),
 'WW_395':('historical_damaged_character',[('historical_bottle_springwater',)]),
 'WW_395t':('character',[('historical_bottle_contents','heal')]),
 'DEEP_003':('character',[('historical_bottle_shimmer',)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def amount(card):
 value=getattr(card,'_historical_bottle_amount',None)
 if type(value) is not int or value<=0:raise UnsupportedCard('Bottled spell requires its captured positive excess definition')
 return value


def preserve(source,card):
 if source.card_id in BOTTLES:card._historical_bottle_amount=amount(source)


def create(game,owner,cid,value):
 if value<=0:return
 require_fixed_cards((cid,),game.cards)
 card=Card(game._new_id(),cid);card._historical_bottle_amount=value
 game._enter_hand(owner,card)


def split(game,op,ctx):
 owner=ctx['owner'];name=op[0]
 if name=='historical_bottle_swarm':
  require_fixed_cards(('WW_052t','WW_052t2'),game.cards)
  count=op[1]*game._card_summon_repetitions(owner,'effect');state=dict(excess=0)
  operations=tuple(('historical_bottle_bug_one',state) for _ in range(count))
  if op[2]:operations+=(('historical_bottle_save_bugs',state),)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name in ('historical_bottle_shadeleaf','historical_bottle_springwater','historical_bottle_shimmer'):
  state={}
  if name=='historical_bottle_shadeleaf':
   require_fixed_cards(('WW_393t',),game.cards)
   return ('historical_bottle_capture_damage',10,state),(('historical_bottle_save_damage',state),)
  if name=='historical_bottle_springwater':
   require_fixed_cards(('WW_395t',),game.cards)
   return ('historical_bottle_capture_heal',state),(('historical_bottle_save_heal',state),)
  return ('historical_bottle_capture_damage',1,state),(('historical_bottle_shimmer_summon',state),)
 if name=='historical_bottle_shimmer_summon':
  value=max(0,op[1].get('dealt',0))
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=value,maximum=value),destination='board'),ctx)
 if name=='historical_bottle_contents':
  value=amount(ctx.get('physical_card'))
  if op[1]=='bugs':return game._split_fixed_summon(('historical_bottle_swarm',value,False),ctx)
  return (('damage',value) if op[1]=='damage' else ('heal',value)),()
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];name=op[0]
 if name=='historical_bottle_bug_one':
  if game._summon_one(owner,'WW_052t',entry_origin='effect',entry_site='swarm_of_lightbugs') is None:op[1]['excess']+=1
 elif name=='historical_bottle_save_bugs':create(game,owner,'WW_052t2',op[1]['excess'])
 elif name=='historical_bottle_capture_damage':
  uid=ctx.get('target',0);target=game.players[-uid-1] if uid<0 else next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)
  if target is not None:
   before=target.health;dealt=game._deal_effect(uid,op[1],ctx);op[2].update(dealt=dealt,excess=max(0,dealt-before))
 elif name=='historical_bottle_save_damage':create(game,owner,'WW_393t',op[1].get('excess',0))
 elif name=='historical_bottle_capture_heal':game._heal(ctx.get('target',0),8,healer=owner,spell=ctx.get('spell',False),_receipt=op[1])
 elif name=='historical_bottle_save_heal':create(game,owner,'WW_395t',op[1].get('overheal',0))
 else:return False
 return True
