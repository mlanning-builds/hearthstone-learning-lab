"""Explicit historical copy, recruitment, restricted buff and deck spell programs."""
from copy import deepcopy
from engine.game import Card
from .generation_cards import pool,discover
from .selectors import has_tribe
from .historical_saidan import add as add_stat
TOKEN_RULES={
 'YOG_082':('character',[('damage',3),('historical_copy_next_spell_bonus',2)]),
 'ETC_362':('minion',[('transform','EX1_298')]),
 'MIS_302':('minion',[('freeze',),('historical_state_frozen_copy',)]),
 'ETC_338':('minion',[('historical_state_synchronize',)]),
 'REV_842':('historical_recruit',[('buff',3,3),('keyword','TAUNT')]),
 'TOY_881':('historical_shield_minion',[('buff',2,3)]),
 'DEEP_021':('enemy_minion',[('historical_state_steal',)]),
 'TTN_745':('character',[('historical_state_grace',)]),
 'ETC_838':('none',[('historical_state_dreams',)]),
 'TID_949':('none',[('historical_state_front_lines',)]),
 'TOY_354':('none',[('historical_state_rampage',)]),
 'TSC_940':('none',[('historical_state_depths',)]),
 'TSC_944':('none',[('historical_state_fires',pool(card_type='MINION',minimum=5))]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def live(game,uid):return next((m for p in game.players for m in p.minions if m.uid==uid and m.health>0),None)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_state_grace':
  state={}
  return ('historical_state_heal_capture',state),(('historical_state_grace_discover',state),)
 if name=='historical_state_grace_discover':
  amount=op[1].get('overheal',0)
  return game._split_fixed_summon(discover(pool(minimum=amount,maximum=amount,classes='own_or_neutral')),ctx)
 if name=='historical_state_front_lines':
  if any(len(player.board)>=7 for player in game.players):return ('batch30_noop',),()
  if not any(any(game._card_data(card)['type']=='MINION' for card in player.deck) for player in game.players):return ('batch30_noop',),()
  return ('historical_copy_recruit_one','deck',(),None,None),(('historical_state_recruit_opponent',),('historical_state_front_lines',))
 if name=='historical_state_recruit_opponent':return game._split_fixed_summon(('replay_context',(('historical_copy_recruit_one','deck',(),None,None),),dict(ctx,owner=1-owner)),ctx)
 if name=='historical_state_rampage':
  state=dict(overflow=0)
  return ('historical_state_hound',state),tuple(('historical_state_hound',state) for _ in range(5))+(('historical_state_hound_buff',state),)
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0];target=live(game,ctx.get('target'))
 if name=='historical_state_frozen_copy':
  if target is not None:game._summon(owner,target.card_id,copy_from=deepcopy(target),entry_frozen=True,entry_origin='copy',entry_site='buy_one_get_one_freeze')
 elif name=='historical_state_synchronize':
  if target is not None:
   card=game._fresh_replay_card(target);game._carry_origin(target,card,copied=True,source_owner=target.owner)
   if ctx.get('finale'):game._buff(target,1,2);add_stat(card,'attack_bonus',1);add_stat(card,'health_bonus',2)
   game._enter_hand(owner,card)
 elif name=='historical_state_steal':
  if target is not None and not game._fire_immune_target(target.uid,ctx):game._zone_manager.bounce(game,target,recipient=owner)
 elif name=='historical_state_heal_capture':game._heal(ctx.get('target',0),8,healer=owner,spell=ctx.get('spell',False),_receipt=op[1])
 elif name=='historical_state_dreams':
  cards=[card for card in p.hand if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'BEAST')]
  if cards and len(p.board)<7:
   highest=max(game._cost(card,owner) for card in cards);card=game.rng.choice([card for card in cards if game._cost(card,owner)==highest]);p.hand.remove(card)
   game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,dormant_turns=2,entry_source=card,entry_zone='hand',entry_origin='recruit',entry_site='big_dreams');game._refresh_auras()
 elif name=='historical_state_hound':
  if game._summon(owner,'TOY_358t',entry_origin='effect',entry_site='rc_rampage') is None:op[1]['overflow']+=1
 elif name=='historical_state_hound_buff':
  count=op[1]['overflow']
  if count:
   for minion in p.minions:
    if minion.card_id=='TOY_358t':game._buff(minion,count,count)
 elif name=='historical_state_depths':
  for card in p.deck[:5]:card.cost_delta=getattr(card,'cost_delta',0)-(3)
  game._open_zone_choice(owner,owner,'deck','dredge')
 elif name=='historical_state_fires':
  values=game._generation_created_candidates(op[1],ctx)
  if values:
   cards=[]
   for _ in p.deck:
    card=Card(game._new_id(),game.rng.choice(values));card.set_cost=5;cards.append(card)
   p.deck[:]=cards;game._refresh_auras()
 else:return False
 return True
