"""Explicit generated summon, draw and hand-generation spell outcomes."""
from copy import deepcopy
from .generation_cards import pool,random_cards
from .selectors import has_tribe
from .pools import require_fixed_cards

def recruit():return ('historical_copy_recruit_one','deck',(('cost','eq',1),),None,None)
TOKEN_RULES={
 'MIS_104':('none',[random_cards(pool(card_type='MINION',tribe='BEAST'),5,temporary=True)]),
 'MIS_705':('none',[random_cards(pool(card_type='MINION',mechanic='TAUNT'),5,temporary=True)]),
 'MIS_708':('none',[random_cards(pool(classes='other'),5,temporary=True)]),
 'MIS_903':('none',[('draw',3),('historical_if_combo',('destroy_random_enemy',1))]),
 'NX2_001':('none',[random_cards(pool(era='past',card_type='SPELL',classes='MAGE'),2,cost_delta=-2)]),
 'NX2_009':('minion',[('freeze',),('historical_copy_target_delivery','hand',1,None,None,None,False)]),
 'REV_245':('none',[('historical_summoning_imp_draw',)]),
 'TOY_387':('none',[('historical_draw_batch',(('type','eq','MINION'),('tribe','eq','DRAGON')),'none',(),priority) for priority in ('lowest','highest')]),
 'TOY_506':('none',[random_cards(pool(card_type='MINION',tribe=tribe,minimum=3,maximum=3),destination='board') for tribe in ('BEAST','DRAGON','ELEMENTAL','MURLOC')]),
 'WW_416':('none',[random_cards(pool(rarity=rarity,classes='other')) for rarity in ('EPIC','RARE','COMMON')]),
 'WW_816':('none',[('historical_draw_batch',(('type','eq','MINION'),('tribe','eq','DRAGON')),'buff',(1,1),'random')]*2),
 'ETC_318':('none',[recruit(),recruit(),('historical_play_finale',(recruit(),))]),
 'ETC_411':('none',[('summon','BT_036t',2),('outcast_operation',('summon','BT_036t',1))]),
 'REV_517':('friendly_minion',[('historical_summoning_lineup',)]),
 'REV_334':('none',[('historical_summoning_pride',)]),
 'REV_372':('none',[('historical_summoning_waltz',)]),
 'RLK_211':('none',[('historical_summoning_felfiends',)]),
 'RLK_960':('none',[('historical_summoning_embers',)]),
 'TSC_656':('none',[('draw',3),('historical_summoning_plant',)]),
 'TTN_722':('none',[('hero_attack',3),('summon','TTN_833t',1)]),
 'TTN_081':('none',[('add','TTN_081t',3)]),
 'TSC_912':('none',[('summon','TSC_912t3',2),('insert_fixed','TSC_912t',1,'bottom')]),
 'TSC_912t':('none',[('summon','TSC_912t2',2)]),
 'TSC_948':('none',[('draw',1),('historical_summoning_naga_follow',('draw',1))]),
 'TSC_947':('none',[('historical_summoning_lionfish',)]),
 'TSC_651':('minion',[('damage',4),('historical_summoning_naga_follow',('hero_attack',4))]),
 'TSC_215':('minion',[('buff',1,2),('historical_summoning_naga_follow',('add','TSC_215',1))]),
 'TOY_353':('none',[('historical_summoning_companions',)]),
}
# These bodies have only their printed intrinsic keyword, or no extra text.
for cid in ('REV_334t','REV_372t','RLK_211t','RLK_960t','TSC_656t','TTN_833t','TTN_081t','TSC_912t2','TSC_912t3','TSC_947t'):
 TOKEN_RULES[cid]=('none',[])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
CAST_EFFECTS={'TSC_912t':(('summon','TSC_912t2',2),)}


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_summoning_naga_follow':
  if not getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_cost_naga_played'):return ('batch30_noop',),()
  return game._split_fixed_summon(op[1],ctx)
 if name=='historical_summoning_imp_draw':
  from .historical_imps import is_imp
  return ('draw',1+sum(is_imp(game,m) for m in p.minions)),()
 if name=='historical_summoning_waltz':
  return game._split_fixed_summon(('summon','REV_372t',2 if any(player.minions_died_turn for player in game.players) else 1),ctx)
 if name=='historical_summoning_felfiends':
  count=2 if any(game._card_data(card)['type']=='MINION' for card in p.deck) else 4
  return game._split_fixed_summon(('summon','RLK_211t',count),ctx)
 if name=='historical_summoning_lineup':
  target=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is None:return ('batch30_noop',),()
  operation=('historical_summoning_copy',deepcopy(target))
  return operation,(operation,operation)
 if name in ('historical_summoning_pride','historical_summoning_embers','historical_summoning_lionfish'):
  if name=='historical_summoning_pride':cid,count,stats='REV_334t',3,(2,4) if p.health<=20 else (1,3)
  elif name=='historical_summoning_embers':cid,count,stats='RLK_960t',2,(2,4) if p.max_mana>=6 else (1,2)
  else:
   ready=getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_cost_naga_played')
   cid,count,stats='TSC_947t',2,(3,3) if ready else (2,2)
  operation=('historical_summoning_stats',cid,stats)
  return operation,tuple(operation for _ in range(count-1))
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner]
 if op[0]=='historical_summoning_stats':game._summon(owner,op[1],entry_stats=op[2],entry_origin='effect',entry_site='historical_summoning_stats')
 elif op[0]=='historical_summoning_copy':game._summon(owner,op[1].card_id,copy_from=op[1],entry_origin='copy',entry_site='criminal_lineup')
 elif op[0]=='historical_summoning_plant':
  size=len(p.hand);game._summon(owner,'TSC_656t',entry_stats=(size,size),entry_origin='effect',entry_site='miracle_growth')
 elif op[0]=='historical_summoning_companions':
  companions=('NEW1_032','NEW1_033','NEW1_034');require_fixed_cards(companions,game.cards)
  for cid in companions:
   card=game._add(owner,cid)
   if card is not None:card.cost_delta=getattr(card,'cost_delta',0)-(1)
 else:return False
 return True
