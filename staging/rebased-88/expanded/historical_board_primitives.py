"""Explicit frozen historical board and zone effects; validation deferred.

Declarations use printed selectors, never rules-text parsing or supported-only
pools. This module does not change Standard eligibility or generation membership.
"""
from .historical_saidan import add as _saidan_add
from engine.game import Card
from .selectors import has_tribe

RULES={
 'AT_054':('none',[('historic_zone_buff','hand_deck',None,1,1)]),
 'AT_106':('historic_demon',[('silence',)]),
 'AV_294':('none',[('historic_temporary_attack','friendly_other',1,'end'),('hero_attack',1)]),
 'BOT_562':('none',[('temporary_keyword_self','STEALTH','next_start')]),
 'BRM_008':('none',[('historic_board_damage','enemy_undamaged',2)]),
 'WON_073':('none',[('historic_board_damage','enemy_undamaged',2)]),
 'BRM_012':('none',[('historic_random_attack',1,4)]),
 'BT_010':('none',[('historic_board_buff','other_murlocs',1,1)]),
 'BT_142':('none',[('hero_attack',1)]),
 'BT_729':('minion',[('tribal_damage',3)]),
 'CFM_067':('minion',[('heal_full',)]),
 'CFM_610':('none',[('tribe_board_buff','DEMON',1,1)]),
 'CFM_657':('minion',[('silence',)]),
 'CFM_667':('enemy_minion',[('damage',5)]),
 'CFM_694':('historic_stealthed',[('buff',2,2)]),
 'CFM_751':('none',[('area_damage','other_characters',3)]),
 'CFM_855':('historic_deathrattle',[('silence',)]),
 'CS2_064':('none',[('area_damage','other_characters',1)]),
 'CS2_181':('none',[('damage_self',4)]),
 'CS2_203':('minion',[('silence',)]),
 'DAL_581':('none',[('historic_full_heal_heroes',)]),
 'DAL_735':('none',[('historic_board_silence','adjacent')]),
 'DMF_091':('none',[('historic_board_buff','adjacent',1,1)]),
 'DMF_110':('none',[('historic_board_damage','non_demons',2)]),
 'DMF_111':('historic_friendly_demon',[('temporary_attack_buff',3),('temporary_keyword_target','LIFESTEAL','end')]),
 'DMF_235':('none',[('historic_board_buff','recruits',1,0),('historic_board_keyword','recruits','DIVINE_SHIELD','permanent')]),
 'DRG_074':('none',[('historic_board_keyword','other_mechs','STEALTH','next_start')]),
 'EX1_048':('minion',[('silence',)]),
 'EX1_093':('none',[('historic_board_buff','adjacent',1,1),('adjacent_taunt',)]),
 'EX1_196':('enemy_minion',[('historic_temporary_attack','target',-2,'next_start')]),
 'EX1_593':('none',[('damage_enemy_hero',3)]),
 'EX1_603':('minion',[('historic_damage_buff',1,2,0)]),
 'FP1_016':('none',[('historic_board_silence','friendly_other')]),
 'GVG_011':('minion',[('temporary_attack_buff',-3)]),
 'WON_314':('minion',[('temporary_attack_buff',-3)]),
 'GVG_048':('none',[('historic_board_buff','other_mechs',2,0)]),
 'GVG_060':('none',[('historic_board_buff','recruits',2,2)]),
 'ICC_467':('friendly_minion',[('temporary_keyword_target','IMMUNE','end')]),
 'ICC_807':('none',[('historic_board_buff','friendly_taunts',2,2)]),
 'LOOT_132':('historic_dragon',[('damage',6)]),
 'LOOT_152':('none',[('buff_others',0,1)]),
 'LOOT_167':('none',[('historic_board_buff','adjacent',2,2)]),
 'NEW1_014':('friendly_minion',[('temporary_keyword_target','STEALTH','next_start')]),
 'OG_161':('none',[('historic_board_damage','non_murlocs',2)]),
 'REV_338':('none',[('hand_buff',0,1)]),
 'SW_067':('friendly_minion',[('keyword','TAUNT')]),
 'SW_093':('none',[('hero_attack',2)]),
 'TID_710':('none',[('historic_zone_buff','deck','BATTLECRY',1,1)]),
 'TID_716':('character',[('damage',5),('armor',8)]),
 'TRL_524':('enemy_taunt',[('silence',)]),
 'TSC_926':('none',[('historic_board_silence','all_other')]),
 'ULD_158':('none',[('area_damage','enemy_minions',1)]),
 'ULD_196':('none',[('historic_full_heal_board','adjacent')]),
 'ULD_197':('none',[('historic_temporary_attack','enemy',-2,'end')]),
 'VAC_327':('minion',[('buff',3,3),('freeze',)]),
 'VAC_947':('none',[('historic_board_buff','all_other',-1,-1)]),
 'WON_062':('none',[('historical_heroes_damage',3)]),
 'YOD_043':('none',[('historic_board_keyword','friendly_murlocs','DIVINE_SHIELD','permanent')]),
 'YOP_032':('none',[('historic_both_armor',4)]),
}
DEATH_EFFECTS={
 'CFM_667':[('damage_own_hero',5)],
 'DAL_040':[('heal_enemy_hero',5)],
 'FP1_001':[('heal_enemy_hero',5)],
 'ICC_099':[('historic_board_damage','friendly',5)],
 'LOOT_351':[('empty_crystals','friendly',1)],
 'OG_147':[('heal_enemy_hero',8)],
 'VAC_947':[('historic_board_buff','all_other',1,1)],
}
END_EFFECTS={
 'AT_063t':[('area_damage','enemies',1)],
 'WON_025':[('area_damage','enemies',1)],
 'CFM_654':[('heal_own_hero',1)],
 'EX1_249':[('area_damage','other_characters',2)],
 'GIL_117':[('historic_board_damage','other_damaged',2)],
 'GVG_020':[('historic_random_board_damage','non_mechs',2)],
 'GVG_039':[('heal_own_hero',4)],
 'LOOT_398':[('heal_own_hero',3)],
 'RLK_926':[('damage_own_hero',2)],
 'TRL_057':[('damage_enemy_hero',2)],
}
# Additional explicit fixed-token, draw, removal and board recipes.
RULES.update({
 'AV_219':('none',[('add','AV_219t',2)]),
 'AV_260':('none',[('add','AV_266',1)]),
 'AV_323':('none',[('add','AV_323t',2)]),
 'AV_255':('none',[('historic_board_freeze','all_other')]),
 'BOT_538':('none',[('add','BOT_102t',1)]),
 'DMF_100':('none',[('add','DMF_100t',2)]),
 'DRG_035':('none',[('add','DRG_035t',2)]),
 'ULD_439':('none',[('add','ULD_439t',2)]),
 'UNG_058':('none',[('add','UNG_057t1',1)]),
 'TRL_509':('none',[('add','TRL_509t',2)]),
 'DMF_065':('none',[('add','DMF_065t',2),('add_opponent','DMF_065t',2)]),
 'SW_434':('none',[('add_opponent','TOKEN_COIN',1)]),
 'TRL_504':('none',[('add_opponent','TOKEN_COIN',1)]),
 'BT_702':('historic_stealthed',[('temporary_attack_buff',3),('temporary_keyword_target','IMMUNE','end')]),
 'BT_722':('minion',[('historic_damage_keyword',1,'DIVINE_SHIELD')]),
 'BT_723':('minion',[('historic_damage_keyword',1,'RUSH')]),
 'CFM_335':('character',[('source_attack_damage',)]),
 'DRG_067':('none',[('damage_random_enemy_minion',3)]),
 'GVG_099':('none',[('damage_random_enemy_minion',4)]),
 'EX1_049':('friendly_minion',[('bounce',)]),
 'EX1_057':('friendly_minion',[('bounce',)]),
 'EX1_283':('character',[('freeze',)]),
 'ICC_028':('none',[('historic_board_buff','adjacent',0,2)]),
 'ICC_855':('none',[('historic_board_freeze','friendly_other')]),
 'OG_292':('none',[('historical_hand_buff',None,'DEATHRATTLE',1,1,False)]),
 'WON_137':('none',[('historical_hand_buff',None,None,5,5,True)]),
 'BT_202':('none',[]),
 'ICC_810':('none',[('historical_hand_buff',None,'LIFESTEAL',2,2,True)]),
 'CFM_655':('none',[('historic_weapon_wear',1)]),
 'EX1_186':('none',[('historic_remove_secrets','one')]),
 'GIL_648':('none',[('historic_remove_secrets','all')]),
 'AT_081':('none',[('historic_enemy_attack_set',1)]),
 'DRG_095':('none',[('historic_enemy_health_set',1)]),
 'SW_056':('none',[('historic_hand_size_heal',)]),
 'SW_089':('none',[('historic_hand_size_area',)]),
 'GVG_101':('none',[('historic_board_damage','deathrattles',2)]),
 'DED_507':('none',[('historic_board_damage','enemy_edges',2)]),
 'GIL_124':('none',[('historic_destroy_small_others',2)]),
 'NEW1_041':('none',[('historic_destroy_random_small',2)]),
 'ICC_018':('none',[('historic_weapon_stats',)]),
 'YOD_014':('minion',[('historic_target_attack_damage',)]),
 'LOOT_152':('none',[('buff_others',0,1)]),
})
DEATH_EFFECTS.update({
 'BT_407':[('add','BT_407t',1)],
 'DAL_146':[('add','DAL_146t',2)],
 'DAL_354':[('add','DAL_354t',2)],
 'UNG_845':[('add','UNG_809t1',2)],
 'BOT_102':[('add','BOT_102t',2)],
 'SW_434':[('add','TOKEN_COIN',2)],
 'LOE_012':[('add','TOKEN_COIN',1)],
 'WON_340':[('add','TOKEN_COIN',1)],
 'FP1_023':[('buff_random_other',0,3)],
 'FP1_026':[('bounce_random_friendly',)],
 'GIL_513':[('board_buff',1,0)],
 'OG_158':[('buff_random_other',1,1)],
 'OG_221':[('historic_random_keyword','friendly_other','DIVINE_SHIELD')],
 'OG_267':[('weapon_buff',2,0)],
 'WON_307':[('historical_hand_buff',None,None,2,2,True)],
 'BT_202':[('historical_hand_buff','BEAST',None,1,1,True)],
 'DMF_191':[('historic_board_silence','all')],
 'CFM_341':[('historic_source_attack_area','enemy')],
 'WW_807':[('filtered_draw',(('type','eq','MINION'),('tribe','eq','BEAST')),1),('hand_buff',1,1)],
 'TSC_935':[('historic_opponent_draw',2)],
})
END_EFFECTS.update({
 'UNG_201':[('summon','UNG_201t',1)],
 'BT_256':[('buff_random_other',2,2)],
 'DEEP_008':[('armor',2),('draw',1)],
 'EX1_575':[('draw',1)],
 'JAM_001':[('filtered_draw',(('mechanic','eq','SECRET'),),1)],
 'SCH_142':[('draw_until',3)],
 'WON_046':[('hand_buff',1,1)],
 'WORK_011':[('historic_board_buff','adjacent',1,1)],
 'WW_391':[('draw',1)],
 'ULD_270':[('historic_random_damaged_heal',5)],
})
TOKEN_RULES={cid:('none',[]) for cid in (
 'AV_219t','AV_323t','BOT_102t','BT_407t','DAL_146t','DAL_354t',
 'DMF_100t','DRG_035t','ULD_439t','UNG_809t1','UNG_201t')}
TOKEN_RULES.update({
 'AV_266':('minion',[('freeze',),('draw',1)]),
 'UNG_057t1':('character',[('damage',2)]),
 'TRL_509t':('minion',[('buff',1,1)]),
 'DMF_065t':('minion',[('buff',1,1)]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

RULES.update({
 'CFM_062':('none',[('historic_board_keyword','adjacent','DIVINE_SHIELD','permanent')]),
 'DED_521':('none',[('missiles','other_characters',12)]),
 'GVG_090':('none',[('missiles','other_characters',6)]),
 'SW_054':('none',[('historic_board_buff','adjacent',1,1)]),
 'SW_086':('none',[('tribe_board_buff','DEMON',2,2)]),
 'SW_307':('none',[('historical_self_scale','other_friendly',1,1)]),
 'SW_317':('enemy_minion',[('source_attack_damage',)]),
 'TRL_512':('character',[('damage',1)]),
 'TTN_456':('none',[('damage_random_enemy_minion',2)]),
 'TTN_832':('none',[('damage_own_hero',4)]),
 'WW_342':('none',[('historical_self_scale','hand',1,0)]),
 'WW_346':('none',[('historic_source_attack_area','enemy')]),
 'VAC_942':('none',[('historical_self_scale','hero_damage',1,1)]),
 'ETC_410':('none',[('historical_self_scale','deaths',1,1)]),
 'SCH_526':('none',[('set_others_health',1)]),
 'GIL_578':('none',[('filtered_draw',(('mechanic','eq','RUSH'),),1),('filtered_draw',(('mechanic','eq','LIFESTEAL'),),1),('filtered_draw',(('mechanic','eq','DEATHRATTLE'),),1)]),
 'SW_305':('none',[('historic_attack_threshold_keyword',4,'RUSH')]),
 'ICC_903':('friendly_minion',[('historic_destroy_target_buff',2,2)]),
 'DED_523':('friendly_beast',[('historic_destroy_target_buff',1,1)]),
 'UNG_807':('historic_pirate',[('historic_destroy_target_buff',1,1)]),
 'NEW1_017':('historic_murloc',[('historic_destroy_target_buff',2,2)]),
 'WON_311':('minion',[('set_target_stats',3,3)]),
})
# Golakka Glutton can consume either player's Beast.
RULES['DED_523']=('historic_beast',[('historic_destroy_target_buff',1,1)])
DEATH_EFFECTS.update({
 'AV_325':[('historic_source_attack_area','enemy')],
 'TOY_606':[('missiles','enemy_minions',8)],
 'TOY_646':[('area_damage','enemies',1)],
 'SCH_526':[('area_damage','all_minions',1)],
})

for cid in DEATH_EFFECTS.keys()|END_EFFECTS.keys():RULES.setdefault(cid,('none',[]))
TRIGGERS={
 'AV_261':('b60_friendly_death',[('buff_self',1,0)]),
 'CFM_658':('b60_friendly_death',[('buff_self',1,0)]),
 'BT_355':('b60_friendly_death',[('damage_random_enemy',3)]),
 'EX1_595':('b60_friendly_death',[('draw',1)]),
 'TRL_257':('b60_friendly_death',[('damage_enemy_hero',2)]),
 'EX1_055':('spell_cast',[('historical_temporary_self_attack',2)]),
 'WON_031':('spell_cast',[('buff_self',1,0)]),
 'GVG_049':('damaged_self',[('double_self_attack',)]),
 'ICC_031':('damaged_self',[('buff_self',2,0)]),
 'ICC_218':('damaged_self',[('discard',1)]),
 'AT_026':('damaged_self',[('historic_damage_echo_hero',)]),
 'BT_727':('damaged_self',[('historic_damage_echo_hero',)]),
 'VAC_512':('damaged_self',[('historic_damage_echo_hero',)]),
}
START_EFFECTS={
 'BAR_043':('owner',[('filtered_draw',(('type','eq','MINION'),('tribe','eq','MURLOC')),1)]),
 'BAR_912':('owner',[('summon_from_zone','deck',(('type','eq','MINION'),('cost','eq',1)))]),
 'CFM_609':('owner',[('damage_self',2)]),
 'DRG_057':('owner',[('buff_self',0,1)]),
 'DRG_078':('owner',[('area_damage','all_minions',5)]),
 'EX1_102':('owner',[('damage_random_enemy',2)]),
 'EX1_341':('owner',[('historic_random_damaged_heal',3)]),
 'EX1_557':('owner',[('historic_coinflip_draw',)]),
 'FP1_027':('owner',[('historic_heal_source',None)]),
 'GIL_693':('owner',[('damage_own_hero',1)]),
 'LOOT_134':('owner',[('historic_set_source_attack',4)]),
 'OG_200':('owner',[('historic_set_source_attack',7)]),
 'OG_271':('owner',[('double_self_attack',)]),
 'SW_319':('owner',[('draw',1)]),
 'TRL_508':('owner',[('historic_heal_source',2)]),
 'TRL_516':('owner',[('destroy_self',),('armor',8)]),
}
TRIGGERS.update({
 'CS2_237':(('summon','friendly','BEAST'),[('draw',1)]),
 'CFM_900':(('summon','friendly',None),[('damage_own_hero',5)]),
 'DRG_023':(('summon','friendly','PIRATE'),[('damage_random_enemy',2)]),
 'GVG_075':(('summon','friendly','PIRATE'),[('damage_random_enemy',2)]),
 'GVG_025':(('summon','friendly','PIRATE'),[('keyword_self','STEALTH')]),
 'NEW1_019':(('summon','friendly',None),[('damage_random_enemy',1)]),
 'OG_113':(('summon','friendly',None),[('buff_self',1,0)]),
 'ULD_145':(('summon','friendly',None),[('buff_self',1,0)]),
 'RLK_824':(('summon','friendly','UNDEAD'),[('buff_event_source',1,0)]),
 'TOY_505':(('summon','friendly','PIRATE'),[('draw',1)]),
 'TOY_518':(('summon','friendly','PIRATE'),[('buff_event_source',1,0)]),
 'TTN_479':(('summon','friendly','ELEMENTAL'),[('buff_event_source',1,1)]),
 'OG_313':(('summon','friendly','BEAST'),[('buff_event_source',1,1)]),
 'WON_009':(('summon','friendly','BEAST'),[('buff_event_source',1,1)]),
 'WON_065':(('summon','friendly',None),[('buff_event_source',0,1)]),
 'YOG_512':(('summon','friendly','UNDEAD'),[('historic_event_keyword','POISONOUS')]),
 'TSC_928':(('summon','friendly','MECHANICAL'),[('buff_self',1,1)]),
 'TSC_054':(('summon','friendly','MECHANICAL'),[('missiles','enemies',3)]),
 'BAR_063':(('summon','friendly','MURLOC'),[('buff_event_source',1,0),('historic_event_keyword','RUSH')]),
})

for cid in TRIGGERS.keys()|START_EFFECTS.keys():RULES.setdefault(cid,('none',[]))

CHOICES={
 'BOT_422':[
  ('Old Growth','none',[('buff_others',1,1)]),
  ('New Growth','none',[('summon','EX1_158t',2)])],
 'CFM_308':[
  ('Forgotten Armor','none',[('armor',10)]),
  ('Forgotten Mana','none',[('historic_refresh_all_mana',)])],
 'EX1_166':[
  ('Moonfire','character',[('damage',2)]),
  ('Dispel','minion',[('silence',)])],
 'EX1_178':[
  ('Uproot','none',[('buff_self',5,0)]),
  ('Rooted','none',[('buff_self',0,5),('keyword_self','TAUNT')])],
 'EX1_573':[
  ('Demigod Favor','none',[('buff_others',2,2)]),
  ('Shando Lesson','none',[('summon','EX1_573t',2)])],
 'GVG_030':[
  ('Attack Mode','none',[('buff_self',1,0)]),
  ('Tank Mode','none',[('buff_self',0,1)])],
 'GVG_032':[
  ('Gift of Mana','none',[('historic_full_crystals_both',1)]),
  ('Gift of Cards','none',[('draw_both',)])],
 'JAM_026':[
  ('Refresh','none',[('refresh_power',)]),
  ('Free Power','none',[('next_power_set_cost',0)])],
 'JAM_027':[
  ('Attack and Rush','friendly_minion',[('buff',2,0),('keyword','RUSH')]),
  ('Health and Lifesteal','friendly_minion',[('buff',0,2),('keyword','LIFESTEAL')])],
 'MAW_025':[
  ('Silence','minion',[('silence',)]),
  ('Immune','minion',[('temporary_keyword_target','IMMUNE','end')])],
 'NEW1_008':[
  ('Ancient Teachings','none',[('draw',2)]),
  ('Ancient Secrets','character',[('heal',7)])],
 'OG_202':[
  ('Slime','none',[('summon','OG_202c',1)]),
  ('Empty Crystal','none',[('empty_crystals','friendly',1)])],
 'WON_302':[
  ('Slime','none',[('summon','OG_202c',1)]),
  ('Empty Crystal','none',[('empty_crystals','friendly',1)])],
 'ULD_292':[
  ('Focused Burst','none',[('buff_self',2,2)]),
  ('Divide and Conquer','none',[('copy_self_right',1)])],
}
for cid in CHOICES:RULES.setdefault(cid,('none',[]))
TOKEN_RULES.update({cid:('none',[]) for cid in ('EX1_158t','EX1_573t','OG_202c')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

GENERATED_IDS=frozenset(RULES)
GROUPS=('source','all','deathrattles','enemy_edges','target','friendly','friendly_other','enemy','enemy_undamaged','adjacent',
        'all_other','other_damaged','non_demons','non_murlocs','non_mechs',
        'other_murlocs','friendly_murlocs','other_mechs','friendly_taunts','recruits')
TARGET_MODES=('historic_undead','historic_beast','historic_murloc','historic_pirate','historic_demon','historic_friendly_demon','historic_dragon',
              'historic_stealthed','historic_deathrattle')


def targets(game,cid,owner,mode):
 if mode not in TARGET_MODES:return None
 base='friendly_minion' if mode=='historic_friendly_demon' else 'minion'
 result=[]
 for uid in game._targets_for(cid,owner,base):
  if uid<=0:continue
  m=game._find(uid);data=game._card_data(m)
  if mode in ('historic_demon','historic_friendly_demon'):ok=has_tribe(data,'DEMON')
  elif mode in ('historic_undead','historic_dragon','historic_beast','historic_murloc','historic_pirate'):ok=has_tribe(data,{'historic_undead':'UNDEAD','historic_dragon':'DRAGON','historic_beast':'BEAST','historic_murloc':'MURLOC','historic_pirate':'PIRATE'}[mode])
  elif mode=='historic_stealthed':ok='STEALTH' in game._effective_keywords(m)
  else:ok=bool(game._death_operations(m))
  if ok:result.append(uid)
 return result or [0]


def selected(game,group,ctx):
 owner=ctx['owner'];source=ctx.get('source');p=game.players[owner]
 own=list(p.minions);enemy=list(game.players[1-owner].minions);all_minions=own+enemy
 if group=='source':return [source] if source in all_minions else []
 if group=='target':
  uid=ctx.get('target',0)
  return [game._find(uid)] if uid>0 and game._find(uid) in all_minions else []
 if group=='all':return all_minions
 if group=='deathrattles':return [m for m in all_minions if game._death_operations(m)]
 if group=='enemy_edges':return enemy[:1]+enemy[-1:] if len(enemy)>1 else enemy
 if group=='friendly':return own
 if group=='enemy':return enemy
 if group=='friendly_other':return [m for m in own if m is not source]
 if group=='all_other':return [m for m in all_minions if m is not source]
 if group=='enemy_undamaged':return [m for m in enemy if m.health==m.max_health]
 if group=='other_damaged':return [m for m in all_minions if m is not source and m.health<m.max_health]
 if group=='adjacent':
  if source not in p.board:return []
  i=p.board.index(source)
  return [p.board[j] for j in (i-1,i+1) if 0<=j<len(p.board) and p.board[j] in own]
 if group=='friendly_taunts':return [m for m in own if 'TAUNT' in game._effective_keywords(m)]
 if group=='recruits':return [m for m in own if game._card_data(m)['id'] in ('CS2_101t','CORE_CS2_101t')]
 if group in ('other_murlocs','friendly_murlocs','other_mechs'):
  tribe='MECHANICAL' if group=='other_mechs' else 'MURLOC'
  return [m for m in own if (group=='friendly_murlocs' or m is not source) and has_tribe(game._card_data(m),tribe)]
 excluded={'non_demons':'DEMON','non_murlocs':'MURLOC','non_mechs':'MECHANICAL'}
 if group in excluded:return [m for m in all_minions if not has_tribe(game._card_data(m),excluded[group])]
 raise ValueError('Unknown historical board selector: '+group)


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historic_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historic_zone_buff':
  zone,mechanic,attack,health=op[1:]
  for z in (('hand','deck') if zone=='hand_deck' else (zone,)):
   values=getattr(p,z)
   for i,value in enumerate(values):
    data=game._card_data(value)
    if data['type']!='MINION' or (mechanic is not None and mechanic not in game._card_mechanics(value)):continue
    card=value if isinstance(value,Card) else Card(game._new_id(),value)
    _saidan_add(card,'attack_bonus',attack);_saidan_add(card,'health_bonus',health);values[i]=card
 elif name=='historic_damage_keyword':
  uid=ctx.get('target',0)
  if uid>0:
   target=game._find(uid);game._deal_effect(uid,op[1],ctx)
   if target.health>0 and target in game.players[target.owner].minions:target.keywords.add(op[2])
 elif name=='historic_board_freeze':
  for target in selected(game,op[1],ctx):game._freeze(target.uid)
 elif name=='historic_random_keyword':
  values=selected(game,op[1],ctx)
  if values:game.rng.choice(values).keywords.add(op[2])
 elif name=='historic_weapon_wear':
  weapon=game.players[1-owner].weapon
  if weapon:
   from .historical_arsenal_batches import lose_durability
   lose_durability(game,1-owner,op[1])
 elif name=='historic_remove_secrets':
  secrets=list(game.players[1-owner].secrets)
  if op[1]=='one' and secrets:secrets=[game.rng.choice(secrets)]
  for secret in secrets:game._reveal_secret(1-owner,secret)
 elif name=='historic_enemy_attack_set':
  for target in selected(game,'enemy',ctx):game._set_minion_attack(target,op[1]+target.aura_attack)
 elif name=='historic_enemy_health_set':
  for target in selected(game,'enemy',ctx):target.health=target.max_health=op[1]+target.aura_health
 elif name=='historic_hand_size_heal':
  game._heal(game.hero_id(owner),len(p.hand),healer=owner,spell=ctx.get('spell',False))
 elif name=='historic_hand_size_area':
  amount=len(p.hand)
  with game._damage_batch():
   for target in selected(game,'all_other',ctx):game._deal_effect(target.uid,amount,ctx)
 elif name=='historic_destroy_small_others':
  for target in selected(game,'all_other',ctx):
   if target.attack<=op[1] and not game._fire_immune_target(target.uid,ctx):target.health=0
 elif name=='historic_destroy_random_small':
  values=[m for m in selected(game,'enemy',ctx) if m.attack<=op[1]]
  if values:
   target=game.rng.choice(values)
   if not game._fire_immune_target(target.uid,ctx):target.health=0
 elif name=='historic_weapon_stats':
  if source is not None and p.weapon:game._buff(source,p.weapon['attack'],p.weapon['durability'])
 elif name=='historic_target_attack_damage':
  if ctx.get('target',0)>0:game._deal_effect(ctx['target'],max(0,game._find(ctx['target']).attack),ctx)
 elif name=='historic_source_attack_area':
  amount=max(0,source.attack) if source is not None else 0
  with game._damage_batch():
   for target in selected(game,op[1],ctx):game._deal_effect(target.uid,amount,ctx)
 elif name=='historic_random_damaged_heal':
  values=[m.uid for m in p.minions if m.health<m.max_health]
  if p.health<p.max_health:values.append(game.hero_id(owner))
  if values:game._heal(game.rng.choice(values),op[1],healer=owner,spell=ctx.get('spell',False))
 elif name=='historic_opponent_draw':
  for _ in range(op[1]):
   game._draw(1-owner)
   if game._check_heroes():break
 elif name=='historic_bounce_source':
  if source is not None and source in p.minions:game._bounce(source)
 elif name=='historic_opponent_class_generate':
  from .generation_cards import pool,random_cards
  request=pool(card_type=op[1] or '',classes=game.players[1-owner].hero_class)
  game._generation_created_candidates(request,ctx)
  for _ in range(op[2]):game._effect(('generate_one',request,'hand',()),ctx)
 elif name=='historic_opponent_one_cost_summon':
  from .generation_cards import pool,random_cards
  request=random_cards(pool(card_type='MINION',minimum=1,maximum=1),destination='board')[1]
  game._effect(('generate_one',request,'board',()),dict(ctx,owner=1-owner))
 elif name=='historic_damage_echo_hero':
  amount=ctx.get('event',{}).get('amount',0)
  if amount>0:game._deal_effect(game.hero_id(owner),amount,ctx)
 elif name=='historic_coinflip_draw':
  if game.rng.randrange(2)==0:game._draw(owner)
 elif name=='historic_heal_source':
  if source is not None and source in p.minions:
   amount=source.max_health-source.health if op[1] is None else op[1]
   game._heal(source.uid,amount,healer=owner,spell=ctx.get('spell',False))
 elif name=='historic_set_source_attack':
  if source is not None and source in p.minions:game._set_minion_attack(source,op[1]+source.aura_attack)
 elif name=='historic_event_keyword':
  uid=ctx.get('event',{}).get('source',0)
  target=next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)
  if target is not None:target.keywords.add(op[1])
 elif name=='historic_full_crystals_both':
  for recipient in (owner,1-owner):
   player=game.players[recipient];gain=min(op[1],max(0,player.mana_capacity-player.max_mana))
   player.max_mana+=gain;player.mana=min(player.max_mana,player.mana+gain)
 elif name=='historic_refresh_all_mana':
  p.mana=max(p.mana,max(0,p.max_mana-p.locked_mana))
 elif name=='historic_attack_threshold_keyword':
  if source is not None and source.attack>=op[1]:source.keywords.add(op[2])
 elif name=='historic_destroy_target_buff':
  uid=ctx.get('target',0)
  target=next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)
  if target is not None and not game._fire_immune_target(uid,ctx):
   target.health=0
   if source is not None:game._buff(source,op[1],op[2])
 elif name=='historic_random_attack':
  if source is not None:game._buff(source,game.rng.randint(op[1],op[2]),0)
 elif name=='historic_full_heal_heroes':
  for recipient in (owner,1-owner):
   player=game.players[recipient]
   game._heal(game.hero_id(recipient),player.max_health-player.health,healer=owner,spell=ctx.get('spell',False))
 elif name=='historic_both_armor':
  for recipient in (owner,1-owner):game._gain_armor(recipient,op[1])
 elif name=='historic_damage_buff':
  uid=ctx.get('target',0)
  if uid>0:
   target=game._find(uid);game._deal_effect(uid,op[1],ctx)
   if target.health>0 and target in game.players[target.owner].minions:game._buff(target,op[2],op[3])
 elif name in ('historic_board_damage','historic_random_board_damage'):
  victims=selected(game,op[1],ctx)
  if name=='historic_random_board_damage' and victims:victims=[game.rng.choice(victims)]
  with game._damage_batch():
   for target in victims:game._deal_effect(target.uid,op[2],ctx)
 elif name=='historic_board_buff':
  for target in selected(game,op[1],ctx):game._buff(target,op[2],op[3])
 elif name=='historic_board_silence':
  for target in selected(game,op[1],ctx):game._silence(target)
 elif name=='historic_full_heal_board':
  for target in selected(game,op[1],ctx):game._heal(target.uid,target.max_health-target.health,healer=owner,spell=ctx.get('spell',False))
 elif name=='historic_board_keyword':
  for target in selected(game,op[1],ctx):
   if op[3]=='permanent':target.keywords.add(op[2])
   else:game._temporary_keyword(target,op[2],op[3])
 elif name=='historic_temporary_attack':
  for target in selected(game,op[1],ctx):
   game._adjust_minion_attack(target,op[2])
   if op[3]=='next_start':target.imbue_attack_expiries.append(dict(owner=owner,amount=op[2]))
   else:target.temporary_attack+=op[2]
 else:return False
 return True


def split(game,op,ctx):
 """Expand dynamic opponent-class requests at the existing effect checkpoint."""
 if op[0]!='historic_opponent_class_generate':return None
 from .generation_cards import pool,random_cards
 request=pool(card_type=op[1] or '',classes=game.players[1-ctx['owner']].hero_class)
 return game._generation_split(random_cards(request,op[2]),ctx)
