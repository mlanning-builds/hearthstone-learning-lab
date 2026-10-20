"""Literal historical generation outcomes, using native complete-pool programs.

Eligibility remains catalog driven. These declarations never filter a pool by
registration, and cost modifiers attach to physical cards through native rules.
"""
from .generation_cards import pool, random_cards, discover

def draw(priority):return ('historical_draw_batch',None,'none',(),priority)
TOKEN_RULES={
 'BOT_101':('none',[random_cards(pool(card_type='MINION'),2)]),
 'BOT_600':('none',[('draw',2),('historical_copy_enemy_draw',2)]),
 'CFM_623':('none',[('damage_random_enemy',3)]*3),
 'DMF_103':('none',[('missiles','enemies',10)]),
 'GIL_147':('none',[('missiles','enemies',5)]),
 'GVG_003':('none',[random_cards(pool(card_type='MINION'),cost_delta=-3)]),
 'EX1_180':('none',[random_cards(pool(card_type='SPELL',classes='MAGE'))]),
 'OG_090':('none',[random_cards(pool(card_type='SPELL',classes='MAGE'),3)]),
 'WON_037':('none',[random_cards(pool(card_type='SPELL',classes='MAGE'),3)]),
 'DAL_608':('none',[discover(pool(card_type='SPELL',classes='own_or_neutral',maximum=3))]),
 'GDB_857':('none',[discover(pool(era='past',card_type='MINION',minimum=10,maximum=10),set_cost=1)]),
 'GVG_001':('none',[('historical_utility_pool_flamecannon',)]),
 'SW_107':('none',[('area_damage','all_minions',3)]),
 'SW_462':('none',[('next_discount','FIRE',2,'turn')]),
 'TRL_310':('none',[('next_discount','ELEMENTAL',2,'turn')]),
 'GDB_883':('none',[random_cards(pool(card_type='MINION',minimum=2,maximum=2),2,destination='board'),('refresh_mana',2)]),
 'YOP_019':('none',[('add','YOP_019t',1)]),
 'YOP_019t':('none',[('refresh_mana',2)]),
 'AV_218':('none',[('historical_utility_pool_sheep',)]),
 'OG_081':('historical_frozen_minion',[('historical_utility_pool_shatter',)]),
 'WC_041':('none',[('historical_utility_pool_shattering',)]),
 'AV_295':('none',[]),'CFM_602':('none',[]),'DAL_350':('none',[]),
 'DRG_311':('none',[]),'EX1_155':('none',[]),'GVG_041':('none',[]),
 'OG_195':('none',[]),'SW_422':('none',[]),'TRL_254':('none',[]),
 'ULD_135':('none',[]),'YOD_001':('none',[]),'YOD_001ts':('none',[]),'GDB_851':('none',[]),
}
CHOICES={
 'AV_295':[('Lowest','none',[draw('lowest')]),('Highest','none',[draw('highest')])],
 'CFM_602':[('Jade Golem','none',[('historical_ritual_jade',False,False)]),('Shuffle','none',[('insert_fixed','CFM_602',3,'shuffle')])],
 'DAL_350':[('Damage','minion',[('damage',2)]),('Heal','character',[('heal',5)])],
 'DRG_311':[('Reinforce','minion',[('buff',0,2),('keyword','TAUNT')]),('Treant','none',[('summon','DRG_311t',1)])],
 'EX1_155':[('Attack','minion',[('buff',4,0)]),('Health','minion',[('buff',0,4),('keyword','TAUNT')])],
 'GVG_041':[('Wisps','none',[('summon','CS2_231',5)]),('Buff','minion',[('buff',5,5),('keyword','TAUNT')])],
 'OG_195':[('Wisps','none',[('summon','CS2_231',7)]),('Buff','none',[('board_buff',2,2)])],
 'SW_422':[('Attack','none',[('board_buff',1,0)]),('Treant','none',[('summon','SW_422t',1)])],
 'TRL_254':[('Buff','minion',[('buff',2,4),('keyword','TAUNT')]),('Raptors','none',[('summon','TRL_254t',2)])],
 'ULD_135':[('Ancient','none',[('summon','ULD_135at',1)]),('Heal','character',[('heal',12)])],
 'YOD_001':[('Draw','none',[('add','YOD_001ts',1),('draw',1)]),('Eagle','none',[('add','YOD_001ts',1),('summon','YOD_001t',1)])],
 'YOD_001ts':[('Draw','none',[('draw',1)]),('Eagle','none',[('summon','YOD_001t',1)])],
 'GDB_851':[('Rays','none',[('historical_utility_pool_phaser',)]),('Dormant','enemy_minion',[('historical_utility_pool_dormant',)])],
}
# Literal generated bodies have no extra effect beyond metadata keywords.
for cid in ('DRG_311t','SW_422t','TRL_254t','ULD_135at','YOD_001t'):
 TOKEN_RULES[cid]=('none',[])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def execute(game,op,ctx):
 from .historical_pool_weapons import execute as execute_weapon
 from .historical_pool_state import execute as execute_state
 if execute_weapon(game,op,ctx) or execute_state(game,op,ctx):return True
 from .historical_pool_spells import execute as execute_spells
 if execute_spells(game,op,ctx):return True
 if op[0]=='historical_utility_pool_sheep':
  for player in game.players:
   for minion in list(player.minions):
    if minion.health>0:game._transform(minion,'CS2_tk1')
 elif op[0]=='historical_utility_pool_shattering':
  for player in game.players:
   for minion in list(player.minions):
    if minion.health>0 and minion.frozen_until>=0:game._effect(('destroy',),dict(ctx,target=minion.uid))
 elif op[0]=='historical_utility_pool_shatter':
  target=game._force_live(ctx.get('target'))
  if target is not None and target.frozen_until>=0:game._effect(('destroy',),ctx)
 elif op[0]=='historical_utility_pool_flamecannon':
  targets=[m.uid for m in game.players[1-ctx['owner']].minions if m.health>0]
  if targets:game._deal_effect(game.rng.choice(targets),4,ctx)
 elif op[0]=='historical_utility_pool_phaser':
  targets=[m.uid for m in game.players[1-ctx['owner']].minions if m.health>0]
  for uid in game.rng.sample(targets,min(2,len(targets))):game._deal_effect(uid,2,ctx)
 elif op[0]=='historical_utility_pool_dormant':
  game._sleep_minion(game._force_live(ctx.get('target')),2)
 else:return False
 return True

COMBINED_CHOICES={'YOD_001':(('add','YOD_001ts',1),('draw',1),('summon','YOD_001t',1))}

from .historical_pool_spells import TOKEN_RULES as SPELL_RULES
TOKEN_RULES.update(SPELL_RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

from .historical_pool_weapons import TOKEN_RULES as WEAPON_RULES
from .historical_pool_state import TOKEN_RULES as STATE_RULES, CHOICES as STATE_CHOICES
TOKEN_RULES.update(WEAPON_RULES)
TOKEN_RULES.update(STATE_RULES)
CHOICES.update(STATE_CHOICES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
