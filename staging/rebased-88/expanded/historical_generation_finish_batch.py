"""Historical complete generation families and paired Discover gains."""
from engine.game import Card
from .generation_cards import pool,random_cards,discover
from .historical_offer_spells import offer
from .historical_family_batches import BASIC_TOTEMS

def op(name,*args):return ('historical_utility_generation_finish_'+name,)+args
CHEAP_MINION=pool(card_type='MINION',maximum=5,classes='own_or_neutral')
COMPANIONS=('SCH_600t1','SCH_600t2','SCH_600t3')
TOKEN_RULES={
 'SW_049':('none',[offer('ordinary',pool(card_type='SPELL',mechanic='SECRET',classes='own_or_neutral'),pool(card_type='WEAPON',classes='own_or_neutral'),pool(card_type='MINION',mechanic='DIVINE_SHIELD',classes='own_or_neutral'))]),
 'ULD_136':('none',[discover(pool(mechanic='CHOOSE_ONE',classes='own_or_neutral'))]),
 'TRL_324':('none',[op('metal')]),
 'WON_070':('character',[('damage',3),('historical_if_combo',('historical_ritual_jade',False,False))]),
 'WON_091':('none',[('summon',cid,1) for cid in BASIC_TOTEMS+('CS2_052',)]),
 'CS2_052':('none',[]),
 'WON_115':('none',[('historical_prime_part',),('historical_prime_part',),('summon','GVG_110t',2),('on_draw_shuffle','BOT_511t',1,1)]),
 'GIL_696':('none',[('historical_utility_archive_opponent_cards',1,'hand',False)]),
 'GDB_123':('none',[random_cards(pool(card_type='MINION',tribe='DEMON'),cost_delta=-2),op('repeat_ray')]),
 'SCH_600':('none',[('summon_fixed_random',COMPANIONS)]),
 'SCH_600t1':('none',[]),'SCH_600t2':('none',[]),'SCH_600t3':('none',[]),
 'WORK_001':('none',[('historical_offer_pair','gain_stats',CHEAP_MINION,CHEAP_MINION)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
AURAS={'SCH_600t3':('others',1,0)}

def split(game,operation,ctx):
 if operation[0]==op('metal')[0]:
  cost=min(10,game.players[ctx['owner']].armor)
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),destination='board'),ctx)
 return None

def execute(game,operation,ctx):
 if operation[0]!=op('repeat_ray')[0]:return False
 card=Card(game._new_id(),'GDB_123');game._make_temporary(card);game._enter_hand(ctx['owner'],card)
 return True
