"""Explicit historical physical movement/deck spell outcomes; unvalidated."""
from copy import deepcopy
from engine.game import Card
from .generation_cards import pool
from .selectors import has_tribe
from .historical_saidan import add as add_stat
TOKEN_RULES={
 'MAW_016':('none',[('historical_movement_order',),('draw',1)]),
 'MAW_027':('none',[('historical_movement_opponent_recruit',)]),
 'MIS_100':('minion',[('buff',-5,-5),('buff_random_hand_minion','friendly',5,5)]),
 'MIS_107':('none',[('historical_movement_barrage',)]),
 'MIS_707':('none',[('draw',2),('damage_own_hero',3),('insert_fixed','MIS_707',2,'shuffle')]),
 'RLK_600':('none',[('equip','RLK_600t'),('buff_random_hand_minion','friendly',4,2)]),
 'RLK_600t':('none',[]),
 'TOY_372':('none',[('historical_movement_yogg_box',)]),
 'TTN_483':('none',[('historical_movement_downsize',)]),
 'TTN_803':('none',[('historical_movement_smelt',)]),
 'TTN_922':('none',[('historical_movement_gear_shift',)]),
 'TSC_957':('none',[('historical_movement_chum',)]),
 'TSC_927':('none',[('historic_zone_buff','hand',None,1,1),('insert_fixed','TSC_927t',1,'bottom')]),
 'TSC_927t':('none',[('historic_zone_buff','hand_deck',None,1,1),('board_buff',1,1)]),
 'TSC_775':('minion',[('silence',),('historical_movement_ritual',1),('insert_fixed','TSC_775t',1,'bottom')]),
 'TSC_775t':('minion',[('silence',),('historical_movement_ritual',2)]),
 'TOY_371':('none',[('historical_movement_manufacture',)]),
 'TOY_884':('none',[('historical_movement_crane',)]),
 'WW_600':('none',[('historical_movement_posse',)]),
 'ETC_076':('friendly_minion',[('historical_movement_breakdance',)]),
 'ETC_076t':('none',[]),
 'ETC_079':('none',[('historical_movement_bounce_all',)]),
 'DEEP_025':('minion',[('historical_copy_target_all',)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_movement_opponent_recruit':return game._split_fixed_summon(('replay_context',(('historical_copy_recruit_one','hand',(),None,None),),dict(ctx,owner=1-owner)),ctx)
 if name=='historical_movement_barrage':return game._split_fixed_summon(('missiles','enemy_minions',3 if any(game._card_data(card)['type']=='MINION' for card in p.deck) else 6),ctx)
 if name=='historical_movement_yogg_box':return game._split_fixed_summon(('autocast_random',pool(card_type='SPELL',minimum=0 if any(game._card_data(card)['type']=='MINION' for card in p.deck) else 5),5),ctx)
 if name=='historical_movement_smelt':return ('buff_random_hand_minion','friendly',3,3),(('historical_movement_smelt_again',),)
 if name=='historical_movement_smelt_again':
  if p.armor<3 or not any(game._card_data(card)['type']=='MINION' for card in p.hand):return ('batch30_noop',),()
  return ('historical_movement_pay_armor',),(('historical_movement_smelt',),)
 if name=='historical_movement_gear_shift':
  uids=tuple(card.uid for card in p.hand[:2]);operations=tuple(('historical_movement_shuffle_uid',uid) for uid in uids)+(('draw',3),)
  return operations[0],operations[1:]
 if name=='historical_movement_ritual':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is None:return ('batch30_noop',),()
  operation=('historical_movement_copy_minion',deepcopy(target))
  return operation,tuple(operation for _ in range(op[1]-1))
 if name=='historical_movement_crane':
  cards=[card for card in p.deck if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'DEMON')]
  operations=tuple(('historical_movement_copy_card',game._copy_card(card,source_owner=owner),False) for card in game.rng.sample(cards,min(2,len(cards))))
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_movement_posse':
  cards=[card for card in game.players[1-owner].hand if game._card_data(card)['type']=='MINION']
  return (('historical_movement_copy_card',game._copy_card(game.rng.choice(cards),source_owner=1-owner),True),()) if cards else (('batch30_noop',),())
 if name=='historical_movement_breakdance':
  target=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
  return (('bounce',),(('historical_movement_dancer',(target.attack,target.health)),)) if target is not None else (('batch30_noop',),())
 if name=='historical_movement_bounce_all':
  operations=tuple(('historical_movement_bounce_uid',m.uid) for m in p.minions)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_movement_manufacture':
  states=tuple({} for _ in range(3));operations=tuple(('historical_draw_capture',None,'random',state) for state in states)+(('historical_movement_discount_drawn',states),)
  return operations[0],operations[1:]
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_movement_order':p.deck.sort(key=lambda card:game._card_stat(card,'cost',owner))
 elif name=='historical_movement_downsize':
  for minion in game.players[1-owner].minions:
   game._buff(minion,-2,0)
   if minion.attack<=0 and not game._fire_immune_target(minion.uid,ctx):minion.health=0
 elif name=='historical_movement_pay_armor':p.armor-=3;game._refresh_auras()
 elif name=='historical_movement_shuffle_uid':
  card=next((card for card in p.hand if card.uid==op[1]),None)
  if card is not None:game._shuffle_hand_card(owner,card)
 elif name=='historical_movement_chum':
  n=1+sum(has_tribe(game._card_data(m),'MURLOC') for m in p.minions)
  for card in p.hand:
   if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'MURLOC'):add_stat(card,'attack_bonus',n);add_stat(card,'health_bonus',n)
 elif name=='historical_movement_copy_minion':game._summon(owner,op[1].card_id,copy_from=op[1],entry_origin='copy',entry_site='azsharan_ritual')
 elif name=='historical_movement_copy_card':
  card=op[1];game._summon(owner,card.card_id,entry_source=card,entry_zone='deck',entry_origin='copy',entry_stats=(4,4) if op[2] else None,entry_site='historical_spell_physical_copy')
 elif name=='historical_movement_dancer':game._summon(owner,'ETC_076t',entry_stats=op[1],entry_origin='effect',entry_site='breakdance')
 elif name=='historical_movement_bounce_uid':
  target=next((m for m in p.minions if m.uid==op[1]),None)
  if target is not None:
   card=game._bounce(target)
   if card is not None:game._b60_state(card)['historical_turn_cost']=dict(turn=game.turn,cost=1)
 elif name=='historical_movement_discount_drawn':
  if not any(game._card_data(card)['type']=='MINION' for card in p.deck):
   for state in op[1]:
    card=state.get('card')
    if card is not None and any(card is held for held in p.hand):card.cost_delta=getattr(card,'cost_delta',0)-(3)
 else:return False
 return True
