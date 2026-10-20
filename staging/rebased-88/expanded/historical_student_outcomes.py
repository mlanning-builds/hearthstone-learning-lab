"""Explicit generated historical spell outcomes; implementation-only batch."""
from .generation_cards import pool,random_cards,discover
def finale(*operations):return ('historical_play_finale',tuple(operations))

TOKEN_RULES={
 'DEEP_009':('minion',[('damage',8),('historical_excavate_dig',False)]),
 'DEEP_018':('minion',[('keyword','DIVINE_SHIELD'),('historical_excavate_dig',False)]),
 'ETC_075':('none',[('draw',2),finale(('weapon_buff',2,0))]),
 'ETC_200':('none',[('historical_draw_batch',(('type','eq','MINION'),('mechanic','eq','RUSH')),'discount',(1,),'random')]*2),
 'ETC_370':('none',[random_cards(pool(card_type='MINION',minimum=n,maximum=n),destination='board') for n in (6,5,4,3)]),
 'ETC_535':('none',[random_cards(pool(card_type='MINION',tribe='ELEMENTAL',minimum=n,maximum=n)) for n in (1,2,3)]),
 'JAM_017':('minion',[('keyword','RUSH'),finale(('buff',1,1))]),
 'JAM_022':('minion',[('silence',),('historical_if_combo',('damage',2))]),
 'REV_239':('none',[('destroy_random_enemy',1)]),
 'REV_249':('minion',[('historical_outcome_attack_damage',)]),
 'REV_307':('character',[('damage',2),('summon','EX1_158t',1)]),
 'REV_313':('none',[discover(pool(card_type='SPELL',classes='own_or_neutral'),turn_cost_delta=-2)]),
 'REV_364':('character',[('damage',3),('historical_sleep_wildseed',)]),
 'REV_365':('none',[('autocast_random',pool(card_type='SPELL',classes='DRUID'),8)]),
 'REV_505':('none',[('summon','REV_845',2),('armor',4)]),
 'RLK_573':('character',[('damage',1),('historical_if_combo',('draw',1))]),
 'RLK_656':('none',[('armor',4),('schedule_turn_effect','start',1,1,(('armor',4),))]),
 'RLK_918':('friendly_minion',[('buff',3,0),('hero_attack',2)]),
 'TID_001':('enemy_character',[('damage',1),('damage',1)]),
 'TID_931':('none',[random_cards(pool(card_type='SPELL',classes='other',minimum=5),2)]),
 'TOY_037':('none',[discover(pool(card_type='SPELL',mechanic='SECRET',classes='own_or_neutral'),set_cost=1)]),
 'TOY_046':('none',[discover(pool(card_type='MINION',minimum=4,maximum=4,classes='own_or_neutral'),stats=(7,7))]),
 'TOY_605':('none',[('historical_draw_batch',(('type','eq','MINION'),('mechanic','eq','TAUNT')),'none',(),'random')]*2),
 'TOY_644':('minion',[('historical_event_sleep_target',2)]),
 'TOY_877':('none',[('historic_zone_buff','hand_deck',None,2,3),('board_buff',2,3)]),
 'TOY_384':('none',[('historical_outcome_purify',),('board_buff',1,2)]),
 'TSC_055':('none',[('filtered_draw',(('type','eq','MINION'),('tribe','eq','MECHANICAL')),1),('historical_mutation_discount_zones',('hand',),(('tribe','MECHANICAL'),),1)]),
 'TSC_072':('none',[('filtered_draw',(('type','eq','MINION'),('tribe','eq','NAGA')),1),('filtered_draw',(('type','eq','SPELL'),),1)]),
 'TSC_608':('none',[('historical_draw_batch',(('type','eq','MINION'),),'none',(),'lowest')]*2),
 'TSC_631':('none',[('add','TSC_638',3)]),
 'TSC_650':('none',[]),
 'TSC_939':('none',[('historical_outcome_forged_flame',)]),
 'TSC_946':('none',[('historical_outcome_spell_poison',)]),
 'YOG_401':('none',[('schedule_turn_effect','start',1,1,(('draw',3),))]),
 'YOG_410':('none',[discover(pool(card_type='MINION',tribe='MECHANICAL',classes='other'))]),
 'WW_080':('character',[('heal',5),discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'WW_374':('none',[('generation_dynamic_summon','corpses_up_to',8)]),
 'WW_368':('none',[('summon','WW_368t',4)]),
 'WW_427':('none',[('missiles','enemies',10),random_cards(pool(card_type='MINION',minimum=10,maximum=10),destination='board')]),
 'RLK_654':('none',[]),'ETC_373':('none',[]),'WW_821':('none',[]),'TTN_955':('none',[]),
 # Printed vanilla/Rush/Taunt bodies; the Gnome has its explicit end trigger.
 'RLK_654t':('none',[]),'ETC_373t':('none',[]),'WW_368t':('none',[]),
}
CHOICES={
 'TSC_650':[('Orca','none',[('summon','TSC_650t',1)]),('Otters','none',[('summon','TSC_650t4',6)])],
 'RLK_654':[('Beetle Juice','none',[('armor',12)]),('Bug Snacks','none',[('summon','RLK_654t',2)])],
 'ETC_373':[('Flower Power','none',[('summon','ETC_373t',5)]),('Good Vibrations','none',[('board_buff',2,4),('board_keyword','TAUNT')])],
 'WW_821':[('Small Dragons','none',[random_cards(pool(card_type='MINION',tribe='DRAGON',maximum=5),2)]),('Large Dragons','none',[random_cards(pool(card_type='MINION',tribe='DRAGON',minimum=6),2)])],
 'TTN_955':[('Summer Growth','none',[random_cards(pool(card_type='SPELL',school='NATURE',classes='own_or_neutral'),2)]),('Autumn Leaves','none',[('historical_mutation_discount_zones',('hand',),(('type','SPELL'),),1)])],
}
END_EFFECTS={'WW_368t':[('destroy_self',)]}
DISCARD_EFFECTS={'REV_239':[('destroy_random_enemy',1)]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 if op[0]!='historical_outcome_forged_flame':return None
 weapon=game.players[ctx['owner']].weapon
 count=max(0,weapon['attack']) if weapon else 0
 return ('historical_outcome_break_weapon',),(('draw',count),)


def execute(game,op,ctx):
 owner=ctx['owner']
 if op[0]=='historical_outcome_attack_damage':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is not None:game._deal_effect(target.uid,max(0,target.attack),ctx)
 elif op[0]=='historical_outcome_purify':
  for target in tuple(game.players[owner].minions):game._silence(target)
 elif op[0]=='historical_outcome_break_weapon':game._break_weapon(owner)
 elif op[0]=='historical_outcome_spell_poison':game.players[owner].historical_spell_poisonous_turn=game.turn
 else:return False
 return True
