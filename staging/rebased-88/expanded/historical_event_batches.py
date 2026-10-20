"""Explicit historical event, healing and attached Spell Damage recipes.

All bindings in this implementation pass remain unvalidated.
"""
from .historical_saidan import add as _saidan_add
from .generation_cards import pool,random_cards
from .selectors import has_tribe
from engine.game import Card

TRIGGERS={
 'AT_014':('friendly_card_drawn',[('historical_event_discount_drawn',1)]),
 'WON_061':('friendly_card_drawn',[('historical_event_discount_drawn',1)]),
 'BRM_031':('friendly_card_drawn',[('historical_event_copy_drawn',)]),
 'CS2_235':(('historical_event','minion_healed'),[('draw',1)]),
 'TRL_570':(('historical_event','hero_healed_three'),[('draw',1)]),
 'SCH_400':('spell_cast',[('historical_event_spell_damage','self',1)]),
 'EX1_084':(('summon','friendly',None),[('historical_event_summon_modify','attack_at_most',3,0,0,'CHARGE')]),
 'DMF_237':(('summon','friendly',None),[('historical_event_summon_modify','health',1,1,2,None)]),
 'DMF_520':(('summon','friendly',None),[('historical_event_summon_modify','keyword','RUSH',2,0,None)]),
 'OG_310':(('summon','friendly',None),[('historical_event_summon_modify','health',1,0,0,'DIVINE_SHIELD')]),
 'WON_310':(('summon','friendly',None),[('historical_event_summon_modify','health',1,0,0,'DIVINE_SHIELD')]),
 'TSC_922':(('summon','friendly',None),[('historical_event_summon_modify','cost',1,2,1,None)]),
 'FP1_028':(('summon','friendly',None),[('historical_event_summon_self_death_buff',1,1)]),
 'UNG_900':(('summon','friendly',None),[('historical_event_trigger_summoned',)]),
 'DMF_120':('spell_cast',[('discount_random_hand','friendly',(),1)]),
 'OG_085':('spell_cast',[('historical_event_freeze_random_enemy',)]),
 'TSC_073':('spell_cast',[('historical_event_enemy_damage_spell_cost',)]),
 'LOOT_231':('spell_cast',[('historical_event_armor_spell_cost',)]),
 'TSC_827':('spell_cast',[('historic_temporary_attack','source',1,'next_start')]),
 'YOD_022':('other_friendly_minion_played',[('area_damage','all_minions',1)]),
 'ULD_290':('other_friendly_minion_played',[('historical_hand_buff',None,None,1,1,True)]),
 'ULD_709':('hero_attack',[('armor',5)]),
 'ULD_161':('attacking_self',[('damage_own_hero',3)]),
 'TSC_002':('hero_attack',[('area_damage','enemies',1)]),
 'VAC_930':('attacking_self',[('hero_attack',5)]),
 'WON_099':('friendly_discard',[('buff_self',2,1)]),
 'tt_004':(('historical_event','any_death'),[('buff_self',1,0)]),
 'WON_024':('damaged_minion',[('historical_event_destroy_damaged_enemy',)]),
 'YOD_004':(('historical_event','friendly_mech_death'),[random_cards(pool(card_type='MINION',tribe='MECHANICAL'))]),
 'YOG_520':(('historical_event','friendly_undead_death'),[('damage_enemy_hero',2),random_cards(pool(card_type='SPELL',school='SHADOW',classes='PRIEST'))]),
 'YOP_028':(('minion_mechanic_played','BEAST'),[]),
}
# Tribe-play listeners have a distinct explicit predicate from mechanic listeners.
TRIGGERS['YOP_028']=(('historical_event','beast_played'),[random_cards(pool(card_type='MINION',tribe='BEAST'))])
RULES={cid:('none',[]) for cid in TRIGGERS}
RULES.update({
 'BT_724':('minion',[('historical_event_damage_spell_damage',1,1)]),
 'EX1_584':('none',[('historical_event_spell_damage','adjacent',1)]),
 'ICC_093':('friendly_minion',[('historical_event_spell_damage','target',1)]),
})
START_EFFECTS={'DAL_548':('owner',[('historical_event_spell_damage','self',2)])}
END_EFFECTS={
 'WON_133':[('historical_keyword_discount_hand',1)],
 'WW_042':[('historical_event_destroy_bottom',3)],
 'VAC_446':[('historical_event_buff_unattacked',2,2)],
 'TTN_907':[('historical_event_draw_unattacked',2)],
 'ULD_182':[('historical_event_damage_random_other_friendly',1)],
 'TOY_824':[('attack_missiles',)],
 'TTN_833':[('discount_random_hand','friendly',(('mechanic','eq','OVERLOAD'),),1)],
}
END_EFFECTS.update({
 'BOT_423':[('discount_random_hand','friendly',(('type','eq','MINION'),),7)],
 'BRM_028':[('historical_keyword_discount_hand',1)],
 'BT_721':[('historical_event_summon_source_stats','BT_721t')],
 'DMF_709':[('historical_event_other_totem_zones',1,1)],
 'DRG_091':[('fill_board_summon','DRG_091t')],
 'EX1_004':[('buff_random_other',0,1)],
 'EX1_597':[('damage_self',1),('summon','EX1_598',1)],
 'GIL_833':[('draw_both',)],
 'GVG_027':[('buff_random_other',2,2,'MECHANICAL')],
 'ICC_029':[('buff_random_other',3,0)],
 'ICC_075':[('area_damage','enemy_minions',1)],
 'LOE_009':[('summon','LOE_009t',1)],
 'LOOT_131':[('summon','LOOT_131t1',1)],
 'LOOT_540':[('summon_from_zone','deck',(('type','eq','MINION'),('tribe','eq','DRAGON')))],
 'NEW1_037':[('buff_random_other',1,0)],
 'NEW1_040':[('summon','NEW1_040t',1)],
 'OG_042':[('summon_from_zone','deck',(('type','eq','MINION'),))],
 'OG_229':[('historic_random_damaged_heal',8)],
 'REV_513':[('historic_when',('secret',),(('area_damage','enemies',2),))],
 'REV_839':[('buff_self',0,1)],
 'SCH_273':[('historical_event_spellpower_area',1)],
 'SW_030':[('armor',3)],
 'SW_036':[('historical_event_half_hand_cost',)],
 'SW_060':[('discount_random_hand','friendly',(('type','eq','SPELL'),('school','eq','NATURE')),1)],
 'TOY_820':[('historical_event_destroy_smaller',)],
})
END_EVERY_EFFECTS={
 'LEG_CS3_032':[('fill_board_summon','ds1_whelptoken')],
 'NEW1_038':[('buff_self',1,1)],
 'GVG_077':[('historical_event_destroy_alone',)],
}
TOKEN_RULES={cid:('none',[]) for cid in ('BT_721t','DRG_091t','EX1_598','LOE_009t','LOOT_131t1','NEW1_040t')}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TRIGGERS.update({
 'AT_063':('damaged_minion',[('historical_event_destroy_damaged_enemy',)]),
 'AT_021':('friendly_discard',[('buff_self',2,1)]),
 'AT_006':('hero_power_used',[('historical_event_spell_damage','self',1)]),
 'WON_029':('hero_power_used',[('historical_event_spell_damage','self',1)]),
 'AV_127':(('spell_school_cast','FROST'),[('buff_self',2,2)]),
 'BAR_720':(('spell_school_cast','NATURE'),[('buff_random_other',2,2)]),
 'BAR_744':(('spell_school_cast','HOLY'),[('buff_random_other',0,2)]),
 'SW_111':(('spell_school_cast','FIRE'),[('filtered_draw',(('type','eq','SPELL'),),1)]),
 'SW_445':(('spell_school_cast','SHADOW'),[('historical_heroes_damage',2)]),
 'RLK_609':(('spell_school_cast','FIRE'),[('area_damage','all_minions',1)]),
 'TOY_821':(('spell_school_cast','FROST'),[('keyword_self','REBORN')]),
 'BT_254':('spell_cast_on_minion',[random_cards(pool(card_type='SPELL',classes='PRIEST'))]),
 'BT_715':('damaged_self',[('buff_self',2,0)]),
 'BT_716':('damaged_self',[('buff_self',2,0)]),
 'WORK_019':('damaged_self',[('add','TOKEN_COIN',1)]),
 'WORK_023':('damaged_self',[('armor',3)]),
 'YOD_024':('damaged_self',[('summon','GVG_110t',1)]),
 'BAR_902':('attacking_self',[('historical_mutation_discount_zones',('hand',),(('type','SPELL'),('school','HOLY')),1)]),
})
RULES.update({cid:('none',[]) for cid in TRIGGERS if cid not in RULES})
RULES.update({
 'LOE_017':('minion',[('set_target_stats',3,3)]),
 'OG_295':('none',[('historical_mutation_enemy_count_heal',2)]),
 'RLK_921':('none',[('damage_own_hero',2)]),
 'SCH_311':('none',[('historic_board_keyword','friendly_other','RUSH','permanent')]),
 'LOOT_144':('none',[]), 'GIL_608':('none',[]),
 'ULD_266':('none',[]), 'UNG_037':('none',[]),
 'RLK_551':('none',[]),
 'LOOT_347':('none',[('missiles','enemies',3)]),
 'WON_142':('none',[('historical_batch_menagerie',2,2)]),
 'BAR_915':('none',[('buff_random_other',1,1)]),
 'RLK_550':('none',[('historical_batch_grant_other_deaths',(('historic_board_buff','friendly',1,1),))]),
 'GDB_878':('none',[('historical_event_murloc_deaths',)]),
})
DEATH_EFFECTS={
 'LOOT_144':[('add_opponent','TOKEN_COIN',2)],
 'GIL_608':[('buff_random_other',0,2)],
 'ULD_266':[('buff_random_other',1,1)],
 'UNG_037':[('buff_random_other',1,1)],
 'RLK_551':[('damage_random_enemy',3)],
 'BAR_915':[('buff_random_other',1,1)],
}
SPELL_DAMAGE_VALUES={'AT_006':1,'WON_029':1}

TRIGGERS.update({
 'BRM_019':('self_survived_damage',[('summon','BRM_019',1)]),
 'DAL_550':('self_survived_damage',[('copy_self_right',1)]),
 'BAR_888':(('spell_school_cast','FROST'),[('summon','BAR_888t',1)]),
 'WC_036':(('spell_school_cast','NATURE'),[('summon','WC_036t1',1)]),
 'BT_352':('hero_attack',[('summon','BT_352t',1)]),
 'AV_118':('hero_attack',[('summon','BT_922t',2)]),
 'AT_059':('hero_power_used',[('historic_when',('hand_empty',),(('damage_enemy_hero',2),))]),
 'AT_049':('hero_power_used',[('historical_event_totem_attack',2)]),
 'WON_085':('hero_power_used',[('historical_event_totem_attack',2)]),
})
RULES.update({cid:('none',[]) for cid in TRIGGERS if cid not in RULES})
RULES.update({cid:('none',[('historical_event_totem_attack',2)]) for cid in ('AT_049','WON_085')})
END_EFFECTS['BT_341']=[random_cards(pool(card_type='MINION',tribe='DRAGON'))]
START_EFFECTS['BAR_871']=('owner',[('summon','CS2_101t',2)])
TOKEN_RULES.update({cid:('none',[]) for cid in ('BAR_888t','WC_036t1','BT_352t','BT_922t')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Timed dormancy is an entry rule; awakening effects use ordinary frames.
DORMANT_INITIAL={cid:2 for cid in ('BT_004','BT_009','BT_121','BT_127','BT_211','BT_258','BT_305','BT_934','WON_146','YOP_010','YOP_021','TOY_647','VAC_511','WC_035')}
DORMANT_INITIAL['TSC_013']=1
AWAKEN_EFFECTS={
 'BT_004':[('area_damage','enemy_minions',2)],
 'BT_009':[('summon','BT_009t',2)],
 'BT_121':[('equip','CS2_106')],
 'BT_127':[('discount_random_hand','friendly',(('type','eq','MINION'),),5)],
 'BT_211':[('historical_keyword_force_enemy',)],
 'BT_305':[('historic_zone_buff','hand',None,2,2)],
 'BT_934':[('missiles','enemies',10)],
 'WON_146':[('historical_mutation_discount_zones',('hand',),(('tribe','DRAGON'),),4)],
}
DORMANT_END_EFFECTS={
 'TOY_647':[('area_damage','enemies',3)],
 'VAC_511':[('summon','VAC_511t',1)],
 'WC_035':[('dream_random',)],
}
RULES.update({cid:('none',[]) for cid in DORMANT_INITIAL})
RULES['BT_737']=('minion',[('historical_event_sleep_target',2)])
TOKEN_RULES.update({cid:('none',[]) for cid in ('BT_009t','VAC_511t')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
SPELL_DAMAGE_VALUES['YOP_021']=2

TRIGGERS.update({
 'AT_109':('hero_power_used',[('historical_event_inspire_attack',)]),
 'BAR_074':('enemy_card_drawn',[('historical_event_tax_drawn',1,10)]),
 'BAR_075':(('historical_event','enemy_spell'),[('historic_board_buff','friendly',1,1)]),
 'BAR_076':(('historical_event','enemy_minion'),[('summon','BAR_076t',1)]),
 'GIL_152':('damaged_self',[('damage_random_enemy',3)]),
})
RULES.update({cid:('none',[]) for cid in TRIGGERS if cid not in RULES})
RULES['UNG_099']=('none',[('temporary_keyword_self','CANT_ATTACK_HERO','end')])
END_EFFECTS['EX1_298']=[('damage_random_enemy',8)]
TOKEN_RULES['BAR_076t']=('none',[])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

RULES.update({
 'BT_212':('friendly_minion',[('historical_event_copy_death_target',)]),
 'LOE_019':('friendly_minion',[('historical_event_copy_death_target',)]),
 'ICC_257':('friendly_minion',[('grant_death_target',(('historical_event_resummon_bearer',),))]),
 'LEG_RLK_752':('none',[('summon','RLK_907t',2)]),
 'DMF_734':('none',[]),'RLK_653':('none',[]),'ETC_104':('none',[]),
 'AT_036':('none',[]),'WON_076':('none',[]),'TTN_734':('none',[]),
})
DEATH_EFFECTS.update({
 'DMF_734':[('historical_event_transfer_summon','DMF_734')],
 'RLK_653':[('historical_event_transfer_summon','RLK_653')],
 'ETC_104':[('historical_event_transfer_buff','all',1,1)],
 'TTN_734':[('historical_event_transfer_buff','MECHANICAL',2,2)],
 'AT_036':[('summon','AT_036t',1)],
 'WON_076':[('summon','WON_076t',1)],
 'AT_036t':[('summon','AT_036',1)],
 'WON_076t':[('summon','WON_076',1)],
 'RLK_907t':[('damage_random_enemy',2)],
})
TOKEN_RULES.update({cid:('none',[]) for cid in ('AT_036t','WON_076t','RLK_907t','RLK_970t')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
TRIGGERS['RLK_970']=('other_friendly_minion_played',[('historical_event_played_buff_death',1,1,'RLK_970t')])
RULES['RLK_970']=('none',[])

TRIGGERS.update({
 'AT_029':(('historical_event','weapon_equipped'),[('historical_event_equipped_buff',1,0)]),
 'AT_031':(('historical_event','source_attacked_hero'),[('add','TOKEN_COIN',1)]),
 'AT_121':(('historical_event','battlecry_played'),[('buff_self',1,1)]),
 'AV_137':(('historical_event','enemy_spell'),[('summon','AV_137',1)]),
 'AV_326':(('historical_event','friendly_healed'),[('historical_event_healed_buff',2,0)]),
 'BAR_317':(('historical_event','battlecry_combo_played'),[('draw',1)]),
 'BAR_847':(('historical_event','friendly_attack_survived'),[('historical_event_attacker_buff',1,1)]),
 'BAR_860':(('historical_event','murloc_played'),[('area_damage','enemies',1)]),
 'BAR_890':(('historical_event','secret_revealed'),[('buff_self',2,2)]),
 'BOT_218':('damaged_self',[('summon','BOT_218t',1)]),
 'BT_133':('attacked_self',[random_cards(pool(card_type='MINION',minimum=8,maximum=8))]),
 'BT_487':(('historical_event','source_attack_kill'),[('historical_event_extra_attack',)]),
 'DAL_592':(('historical_event','source_attack_kill'),[('historical_event_extra_attack',)]),
 'CFM_025':(('historical_event','source_attacked_minion_survived'),[('draw',1)]),
 'CFM_669':(('historical_event','enemy_spell'),[('add','TOKEN_COIN',1)]),
 'CFM_756':(('historical_event','source_dealt_damage'),[('historical_event_armor_dealt',)]),
 'DAL_759':(('historical_event','source_dealt_damage'),[('historical_event_armor_dealt',)]),
 'TTN_466':(('historical_event','source_dealt_damage'),[('historical_event_armor_dealt',)]),
 'WON_339':(('historical_event','source_dealt_damage'),[('historical_event_armor_dealt',)]),
 'DAL_049':(('historical_event','murloc_played'),[random_cards(pool(card_type='MINION',tribe='MURLOC'))]),
 'DAL_355':(('historical_event','owner_healed'),[random_cards(pool(card_type='SPELL',classes='DRUID'))]),
 'DAL_771':('attacking_self',[('add_opponent','TOKEN_COIN',1)]),
 'DAL_773':(('minion_cost_played',1),[('historical_event_played_keyword_buff',1,0,'RUSH')]),
 'DED_519':('hero_attack',[('damage_random_enemy',2),('damage_random_enemy',2)]),
 'DMF_222':(('historical_event','outcast_card_played'),[('buff_self',1,1)]),
 'DMF_529':(('historical_event','rush_minion_attacked'),[('damage_enemy_hero',2)]),
 'DRG_209':(('historical_event','owner_hero_damaged'),[('summon','DRG_209t',1)]),
 'BT_022':(('historical_event','secret_cast'),[('generate_discover',pool(card_type='SPELL',classes='own_or_neutral'),'hand',())]),
 'ULD_240':(('historical_event','secret_cast'),[('area_damage','enemy_minions',2)]),
 'TTN_731':(('historical_event','second_card_drawn'),[('destroy_self',)]),
 'MIS_026':('friendly_card_drawn',[('historical_event_drawn_one_copy',)]),
 'TRL_405':('friendly_card_drawn',[('historical_event_drawn_beast_buff',2,2)]),
 'VAC_441':('friendly_card_drawn',[('historical_event_chance_draw',)]),
 'WORK_040':(('historical_event','any_card_drawn'),[('historical_event_temporary_drawn',)]),
})
RULES.update({cid:('none',[]) for cid in TRIGGERS if cid not in RULES})
RULES['YOG_402']=('character',[('historical_event_draw_count_damage',)])
TOKEN_RULES.update({cid:('none',[]) for cid in ('BOT_218t','DRG_209t')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

for cid in START_EFFECTS.keys()|END_EFFECTS.keys()|END_EVERY_EFFECTS.keys():RULES.setdefault(cid,('none',[]))
TRIGGERS.update({
 'CFM_634':(('historical_event','source_attack_kill'),[('keyword_self','STEALTH')]),
 'GIL_547':(('historical_event','source_attack_kill'),[('buff_self',2,2)]),
 'OG_300':(('historical_event','source_attack_kill'),[('buff_self',2,2)]),
 'OG_308':(('historical_event','source_attack_kill'),[('historical_event_extra_attack',)]),
 'GIL_655':(('historical_event','friendly_attack'),[('buff_self',1,0)]),
 'ICC_468':('attacking_self',[('historical_event_source_hero_damage',2)]),
 'RLK_220':('attacking_self',[('historical_event_source_hero_damage',2)]),
 'SCH_135':(('historical_event','source_before_minion_attack'),[('historical_event_defender_stats',3,3)]),
 'SCH_276':(('historical_event','source_before_minion_attack'),[('historical_event_silence_defender',)]),
 'SCH_425':('attacking_self',[('weapon_buff',1,1)]),
 'SCH_616':('attacking_self',[('draw',2)]),
 'CFM_808':('attacking_self',[('historical_event_fill_hands',3)]),
 'ETC_399':(('historical_event','rush_minion_attacked'),[('board_buff',1,0)]),
 'VAC_927':(('historical_event','friendly_pirate_attacked'),[('hero_attack',1)]),
 'VAC_938':(('historical_event','other_pirate_before_attack'),[('historical_event_attacker_buff',1,1)]),
 'MIS_911':('hero_attack',[('summon','MIS_911',1)]),
 'NX2_006':('hero_attack',[('summon','NX2_006t',1)]),
 'CFM_697':(('historical_event','source_attacked_hero'),[('historical_event_source_transform_cost',6)]),
 'CFM_333':(('historical_event','source_attacked_minion_survived'),[('historical_event_attack_hero',)]),
})
TOKEN_RULES['NX2_006t']=('none',[])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
TRIGGERS.update({
 'AT_129':(('historical_event','own_spell_targets_source'),[('keyword_self','DIVINE_SHIELD')]),
 'AT_131':(('historical_event','own_spell_targets_source'),[('damage_random_enemy',3)]),
 'BRM_020':(('historical_event','own_spell_targets_source'),[('buff_self',1,1)]),
 'BAR_918':(('historical_event','shadow_spell_nonzero'),[('historical_event_tamsin_copy',)]),
})
RULES.update({cid:('none',[]) for cid in TRIGGERS if cid not in RULES})
TRIGGERS.update({
 'GVG_100':(('historical_event','own_turn_hero_damage'),[('buff_self',2,2)]),
 'REV_332':(('historical_event','friendly_minion_damaged'),[('buff_random_hand_minion','friendly',1,1)]),
})
for cid in ('GVG_100','REV_332'):RULES.setdefault(cid,('none',[]))
# Attack, shield and turn listeners share the existing physical event frames.
TRIGGERS.update({
 'AV_339':(('historical_event','source_attacked_minion_survived'),[('summon','AV_342t',1)]),
 'ETC_324':('friendly_shield_lost',[('draw',1)]),
 'ICC_858':(('historical_event','friendly_minion_shield_lost'),[('buff_self',2,0)]),
 'SW_084':('attacking_self',[('damage_own_hero',2)]),
 'SW_413':(('historical_event','source_attacked_minion_survived'),[('keyword_self','STEALTH')]),
 'TID_704':('hero_attack',[('filtered_draw',(('type','eq','SPELL'),('school','eq','FEL')),1)]),
 'TOY_103':(('historical_event','source_attack_kill'),[('historical_event_extra_attack',)]),
 'TRL_241':(('historical_event','owner_hero_attack_kill'),[('historical_event_refresh_hero',)]),
 'TRL_507':('hero_attack',[('summon','TRL_507t',1)]),
 'TTN_733':(('historical_event','source_attack_kill'),[('historical_event_heal_source_full',)]),
 'TTN_812':('attacked_self',[('add','TTN_812t',1)]),
})
END_EFFECTS.update({
 'KAR_044':[('summon','KAR_044a',1)],
 'RLK_539':[('damage_enemy_hero',6)],
 'ULD_703':[('historical_event_obelisk',)],
 'WW_357':[('gain_corpses',5)],
 'WW_827':[('add','WW_816t',1)],
 'SCH_354':[('historical_event_void_hound',)],
 'REV_016':[('historical_event_cook',)],
 'WW_431':[('historical_event_load_bullets',)],
 'VAC_340':[('historical_event_hamm',)],
 'TSC_633':[('add','TSC_638t',1)],
})
START_EFFECTS['WW_357']=('owner',[('historical_event_maw_paw',)])
RULES['TSC_640']=('none',[('summon','TSC_638t',1)])
DEATH_EFFECTS['TSC_640']=[('summon','TSC_638t',1)]
PIRANHAS=frozenset(('TSC_638','TSC_638t','TSC_638t2','TSC_638t3','TSC_638t4'))
for cid in PIRANHAS:TRIGGERS[cid]=(('summon','friendly',None),[('historical_event_piranha',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('AV_342t','KAR_044a','TRL_507t','TTN_812t','WW_816t'))|(PIRANHAS-{'TSC_638'})
TOKEN_RULES.update({cid:('none',[]) for cid in FIXED_TOKEN_IDS if cid not in TOKEN_RULES})
for cid in set(TRIGGERS)|set(END_EFFECTS)|set(START_EFFECTS):
 if cid not in FIXED_TOKEN_IDS:RULES.setdefault(cid,('none',[]))
END_EVERY_EFFECTS['GDB_230']=[('historical_event_swap_source_stats',)]
TRIGGERS.update({
 'EX1_001':(('historical_event','any_character_healed'),[('buff_self',2,0)]),
 'GIL_190':(('historical_event','friendly_healed'),[('summon','GIL_190t',1)]),
 'GIL_817':(('historical_event','owner_healed'),[('keyword_self','DIVINE_SHIELD')]),
 'GVG_072':(('historical_event','minion_healed'),[('damage_random_enemy',1)]),
 'ICC_245':(('historical_event','owner_hero_healed'),[('historical_event_blackguard',)]),
 'ETC_522':(('historical_event','owner_hero_health_gain'),[('historical_event_banshee',)]),
 'ICC_808':(('summon','friendly',None),[('buff_self',0,1)]),
 'YOP_008':(('historical_event','owner_minion_healing_effect'),[('historical_event_lightsteed',)]),
})
for cid in ('EX1_001','GIL_190','GIL_817','GVG_072','ICC_245','ETC_522','ICC_808','YOP_008'):RULES.setdefault(cid,('none',[]))
RULES.update({'EX1_561':('hero',[('historical_event_alexstrasza',)]),'ETC_089':('none',[])})
START_EFFECTS['ETC_089']=('every',[('historical_event_static_waveform',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('GIL_190t','ETC_522t'))
TOKEN_RULES.update({'GIL_190t':('none',[]),'ETC_522t':('none',[])})
TRIGGERS.update({
 'EX1_044':(('historical_event','owner_other_card_played_before'),[('buff_self',1,1)]),
 'EX1_531':(('historical_event','friendly_beast_death'),[('buff_self',2,1)]),
 'EX1_614':(('historical_event','owner_other_card_played_after'),[('summon','EX1_614t',1)]),
})
START_EFFECTS['FP1_005']=('owner',[('buff_self',1,1)])
for cid in ('EX1_044','EX1_531','EX1_614','FP1_005'):RULES[cid]=('none',[])
TOKEN_RULES['EX1_614t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('EX1_614t',))

TRIGGERS.update({
 'ICC_238':('other_friendly_minion_played',[('historical_event_hurt_played',1)]),
 'GVG_117':(('historical_event','owner_one_cost_spell'),[random_cards(pool(card_type='MINION',tribe='MECHANICAL'))]),
 'GVG_118':(('historical_event','enemy_spell'),[('summon','GVG_068',1)]),
 'GVG_068':(('historical_event','enemy_spell'),[('buff_self',2,0)]),
 'GVG_116':(('historical_event','enemy_minion_death'),[('summon','EX1_029',1)]),
 'ICC_405':(('historical_event','source_survived_damage'),[random_cards(pool(card_type='MINION',rarity='LEGENDARY'),destination='board')]),
 'ICC_408':(('historical_event','source_survived_damage'),[('summon','ICC_900t',1)]),
 'ICC_900':(('historical_event','other_friendly_death'),[('summon','ICC_900t',1)]),
 'OG_318':('damaged_self',[('summon','NEW1_040t',1)]),
 'ONY_020':(('historical_event','own_spell_cast_source'),[('buff_self',2,0)]),
})
for cid in ('GVG_068','ICC_238','GVG_117','GVG_118','GVG_116','ICC_405','ICC_408','ICC_900','OG_318','ONY_020'):RULES[cid]=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('GVG_068','EX1_029','ICC_900t','NEW1_040t'))
# Existing roots retain their actual intrinsic listeners/Deathrattles.
for cid in ('ICC_900t','NEW1_040t'):TOKEN_RULES.setdefault(cid,('none',[]))

TRIGGERS.update({
 'SCH_710':(('historical_event','enemy_spell'),[('summon','SCH_710t',1)]),
 'RLK_212':(('historical_event','source_survived_damage'),[('historical_event_brutal_damage',)]),
 'RLK_924':(('summon','friendly',None),[('historical_event_liadrin_summon',)]),
})
for cid in ('SCH_710','RLK_212','RLK_924'):RULES[cid]=('none',[])
TOKEN_RULES['SCH_710t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('SCH_710t',))

TRIGGERS.update({
 'TID_098':(('historical_event','own_spell_cast_source'),[('draw',1)]),
 'TID_713':('damaged_self',[('historical_event_bubbler',)]),
 'TOY_355':(('historical_event','friendly_beast_death'),[random_cards(pool(era='past',card_type='MINION',tribe='BEAST',rarity='LEGENDARY'),cost_delta=-2)]),
 'TTN_078':(('summon','friendly',None),[('historical_event_observer_myths',)]),
})
for cid in ('TID_098','TID_713','TOY_355','TTN_078'):RULES[cid]=('none',[])
TRIGGERS['VAC_436']=(('historical_event','friendly_deathrattle_play'),[('historical_event_reborn_played',)])
TRIGGERS['VAC_450']=(('historical_event','other_friendly_death'),[('historical_copy_cookie',)])
RULES.update({cid:('none',[]) for cid in ('VAC_436','VAC_450')})

TRIGGERS.update({
 'ETC_534':('damaged_minion',[('historical_event_holotechnician',)]),
 'GDB_321':(('historical_event','source_survived_damage'),[('historical_event_lifeform',)]),
 'GIL_607':(('historical_event','one_cost_minion_played'),[('historical_event_toxmonger',)]),
})
for cid in ('ETC_534','GDB_321','GIL_607'):RULES[cid]=('none',[])

TRIGGERS.update({
 'LOE_016':(('historical_event','battlecry_played'),[('damage_random_enemy',2)]),
 'LOE_086':('spell_cast',[('historical_copy_spell_cost_summon',)]),
 'LOOT_165':(('historical_event','other_friendly_death'),[('historical_copy_sonya',)]),
 'LOOT_218':(('historical_event','source_attacked_hero'),[('historical_copy_gibberer',)]),
})
for cid in ('LOE_016','LOE_086','LOOT_165','LOOT_218'):RULES[cid]=('none',[])

TRIGGERS.update({
 'JAM_019':('hero_attack',[('historical_copy_risa',)]),
 'AV_601':(('historical_event','friendly_deathrattle_play'),[('historical_copy_lieutenant',)]),
 'DRG_104':('spell_cast',[('historical_event_chenvaala',)]),
})
for cid in ('JAM_019','AV_601','DRG_104'):RULES[cid]=('none',[])
START_EFFECTS['OG_338']=('enemy',[('historical_event_nat_draw',)])
RULES['OG_338']=('none',[])

TRIGGERS.update({
 'SW_431':('attacking_self',[('hero_attack',3)]),
 'SW_073':(('historical_event','enemy_spell'),[('historical_copy_cheesemonger',)]),
 'TOY_515':(('historical_event','one_cost_minion_played'),[('historical_copy_waterdancer',)]),
 'REV_250':(('historical_event','friendly_spell_any_minion'),[('historical_copy_pelagos',)]),
 'SCH_126':('other_friendly_minion_played',[('historical_copy_gandling',)]),
 'SCH_317':(('historical_event','friendly_rush_play'),[('historical_copy_playmaker',)]),
 'BAR_540':(('historical_event','friendly_taunt_death'),[('historical_copy_plaguemaw',)]),
})
for cid in ('SW_431','SW_073','TOY_515','REV_250','SCH_126','SCH_317','BAR_540'):RULES[cid]=('none',[])

TRIGGERS.update({
 'TRL_060':('spell_cast',[('historical_copy_spirit_frog',)]),
 'TRL_223':(('historical_event','owner_hero_attack_kill'),[('draw',1)]),
 'TRL_251':(('historical_event','other_friendly_death'),[('buff_random_hand_minion','friendly',1,1)]),
 'TRL_309':('spell_cast',[('historical_copy_spirit_tiger',)]),
 'TRL_502':(('historical_event','other_friendly_death'),[('historical_copy_spirit_dead',)]),
 'TRL_901':(('summon','friendly','BEAST'),[('historical_event_spirit_lynx',)]),
 'ULD_167':('friendly_hero_damaged_own_turn',[random_cards(pool(card_type='MINION',minimum=3,maximum=3),destination='board')]),
 'ULD_702':(('historical_copy_event','enemy_play'),[('historical_copy_reborn_enemy_played',)]),
})
for cid in ('TRL_060','TRL_223','TRL_251','TRL_309','TRL_502','TRL_901','ULD_167','ULD_702'):RULES[cid]=('none',[])

TRIGGERS.update({
 'GVG_067':(('historical_event','enemy_spell'),[('buff_self',1,0)]),
 'GVG_104':(('historical_event','friendly_one_attack_play'),[('historical_event_hobgoblin',)]),
 'GVG_106':(('historical_event','friendly_mech_death'),[('buff_self',2,2)]),
 'ICC_911':(('historical_event','owner_other_card_played_before'),[('historical_copy_mill_three',)]),
 'GVG_016':(('historical_event','enemy_card_played_before'),[('historical_copy_mill_three',)]),
})
for cid in ('GVG_067','GVG_104','GVG_106','ICC_911','GVG_016'):RULES[cid]=('none',[])
TRIGGERS['GDB_235']=('attacked_self',[('historical_copy_akama',)])
TRIGGERS['GDB_469']=(('summon','friendly',None),[('historical_copy_reborn_copy',)])
TRIGGERS['WW_420']=('attacking_self',[('historical_copy_ogre_ace',)])
TRIGGERS['WW_043']=('damaged_self',[('add','WW_044t',1),('historical_copy_bottom_token','WW_044t')])
RULES['AV_293']=('none',[])
TRIGGERS['AV_293']=(('historical_event','friendly_honorable_damage'),[('summon','AV_293t',1)])
TOKEN_RULES['AV_293t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('AV_293t',))
TRIGGERS.update({
 'BOT_103':(('historical_event','right_edge_play'),[('draw',1)]),
 'BT_937':(('historical_event','either_edge_play'),[('area_damage','enemies',1)]),
 'ONY_036':(('historical_event','either_edge_play'),[('draw',1)]),
 'TOY_943':(('historical_event','either_edge_play'),[('damage_random_enemy',1)]),
 'ICC_289':(('historical_event','another_frozen'),[('historical_event_moorabi',)]),
 'VAC_532':(('historical_event','adjacent_attacked'),[('damage_random_enemy',1)]),
 'TTN_732':(('historical_event','owner_magnetized'),[('historical_event_buff_magnetized',)]),
 'VAC_956':(('historical_event','owner_location_used'),[('armor',3)]),
})
RULES.update({cid:('none',[]) for cid in ('BOT_103','BT_937','ONY_036','TOY_943','ICC_289','VAC_532','TTN_732','VAC_956')})
RULES['ETC_422']=('none',[])
TRIGGERS['ETC_422']=(('historical_event','metrognome_play'),[('historical_event_metrognome',)])
RULES['YOD_006']=('none',[])
TRIGGERS['YOD_006']=(('historical_event','source_attacked'),[('temporary_mana',1)])
RULES['TOY_531']=('none',[])
TRIGGERS['TOY_531']=('spell_cast',[('historical_copy_lina',)])
RULES.update({'BT_731':('none',[]),'ULD_262':('none',[])})
TRIGGERS['BT_731']=(('historical_event','source_damaged_minion'),[('historical_event_sporeling',)])
TRIGGERS['ULD_262']=(('summon','friendly',None),[('historical_event_amet',)])
RULES['WW_415']=('none',[])
TRIGGERS['WW_415']=(('historical_event','owner_coin_played'),[random_cards(pool(card_type='MINION',rarity='LEGENDARY',classes='other'),set_cost=1)])
RULES['TTN_920']=('none',[])
TRIGGERS['TTN_920']=(('historical_event','owner_other_mech_play'),[('historical_copy_mimiron_gadget',)])
GENERATED_IDS=frozenset(RULES)


def matches(game,wanted,kind,data,minion):
 if not isinstance(wanted,tuple) or len(wanted)!=2 or wanted[0]!='historical_event':return None
 condition=wanted[1];owner=minion.owner
 if condition=='owner_minion_attacked':return kind=='minion_attack' and data.get('owner')==owner
 if condition=='any_spell_played':return kind=='spell_played'
 if condition=='owner_other_mech_play':return kind=='minion_played' and data.get('owner')==owner and data.get('source')!=minion.uid and has_tribe(game._event_card_data(data),'MECHANICAL')
 if condition=='owner_coin_played':
  from .cards import COIN_IDS
  return kind=='historical_edge_play' and data.get('owner')==owner and data.get('card_id') in COIN_IDS
 if condition=='source_damaged_minion':return kind=='damage' and data.get('source_uid')==minion.uid and data.get('target',0)>0 and data.get('amount',0)>0
 if condition=='source_attacked':return kind=='minion_attack' and data.get('source')==minion.uid
 if condition=='metrognome_play':return kind=='historical_edge_play' and data.get('owner')==owner and data.get('source')!=minion.uid and data.get('cost')==minion.rule_state.get('historical_metrognome_cost',1)
 if condition in ('right_edge_play','either_edge_play'):return kind=='historical_edge_play' and data.get('owner')==owner and data.get('source')!=minion.uid and (data.get('right') or condition=='either_edge_play' and data.get('left'))
 if condition=='another_frozen':return kind=='historical_frozen' and data.get('target',0)>0 and data.get('target')!=minion.uid
 if condition=='adjacent_attacked':return kind=='minion_attack' and data.get('owner')==owner and minion.uid in data.get('attacker_neighbors',())
 if condition=='owner_magnetized':return kind=='historical_magnetized' and data.get('owner')==owner
 if condition=='owner_location_used':return kind=='historical_location_used' and data.get('owner')==owner
 if condition=='friendly_one_attack_play':return kind=='minion_played' and data.get('owner')==owner and data.get('source')!=minion.uid and data.get('historical_played_entry_attack',data.get('entry_attack'))==1
 if condition=='enemy_card_played_before':return kind in ('minion_played','spell_played','dormant_other_card_played') and data.get('owner')!=owner
 if condition=='friendly_spell_any_minion':return kind=='spell_cast' and data.get('owner')==owner and data.get('cast_target',{}).get('minion',False) and data.get('cast_target',{}).get('owner')==owner
 if condition=='friendly_rush_play':
  return kind=='minion_played' and data.get('owner')==owner and data.get('source')!=minion.uid and any(m.uid==data.get('source') and 'RUSH' in game._effective_keywords(m) for m in game.players[owner].minions)
 if condition=='friendly_taunt_death':
  return kind=='minion_died' and data.get('owner')==owner and data.get('source')!=minion.uid and any(record['entity'].uid==data.get('source') and 'TAUNT' in game._effective_keywords(record['entity']) for record in game.players[owner].death_records)
 if condition=='source_attacked_hero':return kind=='minion_attack' and data.get('source')==minion.uid and data.get('target',0)<0
 if condition=='one_cost_minion_played':return kind=='minion_played' and data.get('owner')==owner and data.get('source')!=minion.uid and data.get('cost')==1
 if condition=='friendly_deathrattle_play':return kind=='minion_played' and data.get('owner')==owner and data.get('source')!=minion.uid and 'DEATHRATTLE' in game._event_card_data(data).get('mechanics',())
 if condition=='owner_one_cost_spell':return kind=='spell_cast' and data.get('owner')==owner and data.get('cost')==1
 if condition=='enemy_minion_death':return kind=='minion_died' and data.get('owner')!=owner
 if condition=='other_friendly_death':return kind=='minion_died' and data.get('owner')==owner and data.get('source')!=minion.uid
 if condition=='source_survived_damage':return kind=='damage' and data.get('target')==minion.uid and minion.health>0
 if condition=='own_spell_cast_source':return kind=='spell_cast' and data.get('owner')==owner and data.get('cast_target',{}).get('uid')==minion.uid
 if condition in ('owner_other_card_played_before','owner_other_card_played_after'):
  spell_kind='spell_played' if condition.endswith('before') else 'spell_cast'
  return kind in ('minion_played',spell_kind,'dormant_other_card_played') and data.get('owner')==owner and data.get('source')!=minion.uid
 if condition=='friendly_beast_death':return kind=='minion_died' and data.get('owner')==owner and data.get('source')!=minion.uid and has_tribe(game._event_card_data(data),'BEAST')
 if condition=='enemy_spell_for_gallywix':return kind=='spell_played' and data.get('owner')!=owner and data.get('card_id')!='GVG_028t'
 if condition in ('friendly_spell_other_minion','friendly_spell_source'):
  target=data.get('cast_target',{})
  return kind=='spell_cast' and data.get('owner')==owner and target.get('minion',False) and target.get('owner')==owner and ((target.get('uid')!=minion.uid) if condition=='friendly_spell_other_minion' else (target.get('uid')==minion.uid))
 if condition=='first_owner_draw':return kind=='card_drawn' and data.get('owner')==owner and data.get('historical_draw_ordinal')==1
 if condition=='owner_hero_healed':return kind=='historical_healed' and data.get('target')==game.hero_id(owner) and data.get('restored',0)>0
 if condition=='owner_hero_health_gain':return kind=='historical_hero_health_gained' and data.get('owner')==owner and data.get('amount',0)>0
 if condition=='friendly_honorable_damage':return kind=='damage' and game.current==owner and data.get('damage_owner')==owner and (data.get('source_uid') or 0)>0 and data.get('target',0)>0 and data.get('target_health_before',0)>0 and data.get('target_health_before')==data.get('amount')
 if condition=='owner_minion_healing_effect':return kind=='historical_healing_effect' and data.get('healer')==owner and data.get('target',0)>0 and data.get('amount',0)>0
 if condition=='friendly_beast_attacked':return kind=='minion_attack' and data.get('owner')==owner and has_tribe(game.cards[data['attacker_card_id']],'BEAST')
 if condition=='friendly_minion_shield_lost':return kind=='shield_lost' and data.get('owner')==owner and data.get('target',0)>0
 if condition=='owner_hero_attack_kill':return kind=='hero_attack' and data.get('owner')==owner and bool(data.get('killed'))
 if condition=='own_turn_hero_damage':return kind=='damage' and data.get('target')==game.hero_id(owner) and game.current==owner and data.get('amount',0)>0
 if condition=='own_spell_targets_source':return kind=='historical_spell_targeted' and data.get('owner')==owner and data.get('target')==minion.uid
 if condition=='shadow_spell_nonzero':return kind=='spell_played' and data.get('owner')==owner and data.get('cost',0)>=1 and game.cards[data['card_id']].get('spellSchool')=='SHADOW'
 if condition=='friendly_murloc_death':return kind=='minion_died' and data['owner']==owner and has_tribe(game.cards[data['card_id']],'MURLOC')
 if condition=='any_character_healed':return kind=='historical_healed' and data['restored']>0
 if condition=='combo_card_played':return kind=='historical_combo_card_played' and data['owner']==owner
 if condition=='any_secret_played':return kind=='historical_secret_played'
 if condition=='secret_played':return kind=='historical_secret_played' and data['owner']==owner
 if condition=='overload_card_played':return kind=='historical_overload_card_played' and data['owner']==owner
 if condition=='siren_alternating':
  if data.get('owner')!=owner:return False
  spell=bool(minion.rule_state.get('historical_siren_spell'))
  matches=(kind=='spell_cast') if spell else (kind=='minion_played' and data.get('source')!=minion.uid and has_tribe(game._event_card_data(data),'NAGA'))
  if matches:minion.rule_state['historical_siren_spell']=not spell
  return matches
 if condition=='mana_overloaded':return kind=='historical_overloaded' and data['owner']==owner and data['amount']>0
 if condition=='other_friendly_murloc_died':return kind=='minion_died' and data['owner']==owner and data.get('source')!=minion.uid and has_tribe(game.cards[data['card_id']],'MURLOC')
 if condition=='another_overhealed':return kind=='historical_overheal' and data['target']!=minion.uid and data['overheal']>0
 if condition=='spell_fire_thaw':return kind=='spell_cast' and data['owner']==owner and game.cards[data['card_id']].get('spellSchool')=='FIRE'
 if condition=='enemy_frozen':return kind=='historical_frozen' and data['target_owner']!=owner
 if condition=='own_weapon_broken':return kind=='historical_weapon_broken' and data['owner']==owner
 if condition=='friendly_minion_damaged':return kind=='damage' and data['target']>0 and data['target_owner']==owner and data['amount']>0
 if condition=='armor_patron':
  if kind!='armor_gained' or data['owner']!=owner or minion.rule_state.get('historical_patron_turn')==game.turn:return False
  minion.rule_state['historical_patron_turn']=game.turn;return True
 if condition=='friendly_attack':return kind=='minion_attack' and data['owner']==owner
 if condition=='source_before_minion_attack':return kind=='before_minion_attack' and data['source']==minion.uid and data['target']>0
 if condition=='friendly_pirate_attacked':return kind=='minion_attack' and data['owner']==owner and has_tribe(game.cards[data['attacker_card_id']],'PIRATE')
 if condition=='other_pirate_before_attack':
  if kind!='before_minion_attack' or data['owner']!=owner or data['source']==minion.uid:return False
  return any(m.uid==data['source'] and has_tribe(game._card_data(m),'PIRATE') for m in game.players[owner].minions)
 if condition=='weapon_equipped':return kind=='historical_weapon_equipped' and data['owner']==owner
 if condition=='source_attacked_hero':return kind=='minion_attack' and data['source']==minion.uid and data['target']<0
 if condition=='source_attacked_minion_survived':return kind=='minion_attack' and data['source']==minion.uid and data['target']>0 and minion.health>0
 if condition in ('battlecry_played','battlecry_combo_played','outcast_card_played'):
  if kind not in ('minion_played','spell_cast','dormant_other_card_played') or data['owner']!=owner or data.get('source')==minion.uid:return False
  mechanics=game._event_card_data(data).get('mechanics',())
  return bool(set(mechanics)&({'BATTLECRY','COMBO'} if condition=='battlecry_combo_played' else {'OUTCAST'} if condition=='outcast_card_played' else {'BATTLECRY'}))
 if condition=='friendly_healed':return kind=='historical_healed' and data['target']>0 and any(m.uid==data['target'] for m in game.players[owner].minions)
 if condition=='owner_healed':return kind=='historical_healed' and data.get('healer')==owner and data['restored']>0
 if condition=='friendly_attack_survived':return kind=='minion_attack' and data['owner']==owner and any(m.uid==data['source'] and m.health>0 for m in game.players[owner].minions)
 if condition=='murloc_played':return kind=='minion_played' and data['owner']==owner and data.get('source')!=minion.uid and has_tribe(game._event_card_data(data),'MURLOC')
 if condition=='secret_revealed':return kind=='historical_secret_revealed' and data['owner']==owner
 if condition=='source_dealt_damage':return kind=='damage' and data.get('source_uid')==minion.uid and data['amount']>0
 if condition=='owner_hero_damaged':return kind=='damage' and data['target']==game.hero_id(owner) and data['amount']>0
 if condition=='secret_cast':return kind=='spell_cast' and data['owner']==owner and 'SECRET' in game._event_card_data(data).get('mechanics',())
 if condition=='rush_minion_attacked':return kind=='minion_attack' and data['owner']==owner and 'RUSH' in data.get('attacker_keywords',())
 if condition=='second_card_drawn':return kind=='card_drawn' and data['owner']==owner and data.get('historical_draw_ordinal')==2
 if condition=='any_card_drawn':return kind=='card_drawn'
 if condition=='lackey_played':
  from .historical_family_batches import LACKEYS
  return kind=='minion_played' and data['owner']==owner and data['card_id'] in LACKEYS and data.get('source')!=minion.uid
 if condition=='enemy_spell':return kind=='spell_cast' and data['owner']!=owner
 if condition=='enemy_minion':return kind=='minion_played' and data['owner']!=owner
 if condition=='source_attack_kill':return kind=='minion_attack' and data['source']==minion.uid and bool(data.get('killed'))
 if condition=='minion_healed':return kind=='historical_healed' and data['target']>0 and data['restored']>0
 if condition=='hero_healed_three':return kind=='historical_healed' and data['target']==game.hero_id(owner) and data['restored']>=3
 if condition=='any_death':return kind=='minion_died'
 if condition in ('friendly_mech_death','friendly_undead_death'):
  return kind=='minion_died' and data['owner']==owner and has_tribe(game._event_card_data(data),'MECHANICAL' if condition=='friendly_mech_death' else 'UNDEAD')
 if condition=='beast_played':return kind=='minion_played' and data['owner']==owner and data['source']!=minion.uid and has_tribe(game._event_card_data(data),'BEAST')
 return False


def execute(game,op,ctx):
 name=op[0]
 if name=='historical_event_tamsin_copy':
  event=ctx['event'];donor=event.get('physical_card')
  card=game._fresh_replay_card(donor) if donor is not None else Card(game._new_id(),event['card_id'])
  game._set_card_cost(card,0);game._enter_hand(ctx['owner'],card)
  return True
 if name=='historical_event_hurt_played':
  uid=ctx['event'].get('source',0)
  if uid:game._deal_effect(uid,op[1],ctx)
  return True
 if not name.startswith('historical_event_'):return False
 owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner];source=ctx.get('source');event=ctx.get('event',{})
 if name=='historical_event_sporeling':
  victim=next((m for player in game.players for m in player.minions if m.uid==event.get('target') and m.health>0),None)
  if victim is not None:game._transform(victim,'BT_731')
 elif name=='historical_event_amet':
  victim=next((m for m in p.minions if m.uid==event.get('source') and m.health>0),None)
  if victim is not None and source is not None and source.health>0:
   victim.health=victim.max_health=source.health+victim.aura_health;game._refresh_auras()
 elif name=='historical_event_metrognome':
  cost=source.rule_state.get('historical_metrognome_cost',1)+1;source.rule_state['historical_metrognome_cost']=cost
  game._effect(('filtered_draw',(('cost','eq',cost),),1),ctx)
 elif name=='historical_event_moorabi':
  game._effect(('historical_copy_target_delivery','hand',1,None,None,None,False),dict(ctx,target=event['target']))
 elif name=='historical_event_buff_magnetized':
  victim=next((m for m in p.minions if m.uid==event.get('target') and m.health>0),None)
  if victim is not None:game._buff(victim,1,1)
 elif name=='historical_event_chenvaala':
  state=source.rule_state if source is not None else {}
  if state.get('historical_chenvaala_turn')!=game.turn:state['historical_chenvaala_turn']=game.turn;state['historical_chenvaala_casts']=0
  state['historical_chenvaala_casts']=state.get('historical_chenvaala_casts',0)+1
  if state['historical_chenvaala_casts']%3==0:game._summon(owner,'DRG_104t2',entry_origin='effect',entry_site='chenvaala',entry_source=source)
 elif name=='historical_event_nat_draw':
  if game.rng.randrange(2)==0:game._effect(('draw',1),dict(ctx,owner=1-owner))
 elif name=='historical_event_holotechnician':
  victim=next((m for player in game.players for m in player.minions if m.uid==event.get('target') and m.health>0),None)
  if event.get('amount')==1 and victim is not None:victim.health=0
 elif name=='historical_event_lifeform':
  if source in p.minions and source.health>0:game._grant_bonus_effects(source,1)
 elif name=='historical_event_toxmonger':
  victim=next((m for m in p.minions if m.uid==event.get('source') and m.health>0),None)
  if victim is not None:victim.keywords.add('POISONOUS')
 elif name=='historical_event_reborn_played':
  minion=next((m for m in p.minions if m.uid==event.get('source') and m.health>0),None)
  if minion is not None:minion.keywords.add('REBORN')
 elif name=='historical_event_bubbler':
  if event.get('amount')==1 and source in p.minions:source.health=0
 elif name=='historical_event_observer_myths':
  if source in p.minions and source.health>0 and event.get('entry_attack',0)>source.attack:
   for minion in p.minions:
    if minion.health>0:game._buff(minion,1,0)
 elif name=='historical_event_brutal_damage':game._deal_effect(game.hero_id(1-owner),event.get('amount',0),ctx)
 elif name=='historical_event_liadrin_summon':
  minion=next((m for m in p.minions if m.uid==event.get('source') and m.health>0),None)
  if minion is not None and source in p.minions and source.health>0 and event.get('entry_attack',minion.attack)<source.attack:minion.keywords.update(('DIVINE_SHIELD','RUSH'))
 elif name=='historical_event_blackguard':
  candidates=[m for m in q.minions if m.health>0]
  if candidates:game._deal_effect(game.rng.choice(candidates).uid,event['restored'],ctx)
 elif name=='historical_event_banshee':
  amount=event['amount'];game._summon(owner,'ETC_522t',entry_stats=(amount,amount),entry_origin='effect',entry_site='historical_banshee',entry_source=source)
 elif name=='historical_event_lightsteed':
  victim=next((m for player in game.players for m in player.minions if m.uid==event['target'] and m.health>0),None)
  if victim is not None:game._buff(victim,0,2)
 elif name=='historical_event_alexstrasza':
  uid=ctx.get('target',0)
  if uid<0:
   recipient=-uid-1;hero=game.players[recipient];before=hero.health;hero.max_health=max(hero.max_health,15);hero.health=15
   if hero.health!=before:hero.hero_health_changed_turn=True
   if hero.health>before:game._queue_event('historical_hero_health_gained',owner=recipient,amount=hero.health-before)
 elif name=='historical_event_static_waveform':
  if source in p.minions and source.health>0:
   if game.rng.randrange(2)==0:game._buff(source,-1,0)
   else:game._buff(source,0,-1)
 elif name=='historical_event_swap_source_stats':
  if source in p.minions and source.health>0:game._set_entity_stats(source,source.health,source.attack)
 elif name=='historical_event_refresh_hero':p.hero_attacks=max(0,p.hero_attacks-1)
 elif name=='historical_event_heal_source_full':
  if source in p.minions and source.health>0:game._heal(source.uid,max(0,source.max_health-source.health),healer=owner)
 elif name=='historical_event_obelisk':
  if sum(m.card_id=='ULD_703' and m.health>0 for m in p.minions)>=3:game._effect(('damage_random_enemy',5),ctx)
 elif name=='historical_event_void_hound':
  attack=health=0
  for minion in q.minions:
   if minion.health<=0:continue
   a=min(1,max(0,minion.attack));h=min(1,minion.health)
   game._buff(minion,-a,-h);attack+=a;health+=h
  if source in p.minions and source.health>0:game._buff(source,attack,health)
 elif name=='historical_event_cook':
  state=getattr(p,'historical_enemy_hero_damage_turn',{})
  if state.get('turn')==game.turn and state.get('amount',0)>=3:game._draw(owner)
 elif name=='historical_event_load_bullets':
  if source in p.minions:source.attached_death_effects.extend((('damage_random_enemy',1),('damage_random_enemy',1)))
 elif name=='historical_event_hamm':
  candidates=[c for c in q.deck if game._card_data(c)['type']=='MINION']
  if candidates:
   card=game.rng.choice(candidates);q.deck.remove(card);game._zone_card_removed(1-owner,card,'deck','destroy');game._log('destroy_deck_card',player=1-owner,card=game._card_data(card)['id'])
   if source in p.minions and source.health>0:game._buff(source,2,2)
 elif name=='historical_event_maw_paw':
  if p.corpses>=5:
   game._spend_corpses(owner,5);p.max_health+=5;p.health+=5;p.hero_health_changed_turn=True
   game._queue_event('historical_hero_health_gained',owner=owner,amount=5)
 elif name=='historical_event_piranha':
  if event.get('card_id') in PIRANHAS and source in p.minions and source.health>0:game._buff(source,1,0)
 elif name=='historical_event_source_hero_damage':
  lifesteal=source is not None and 'LIFESTEAL' in game._effective_keywords(source)
  game._deal_effect(game.hero_id(1-owner),op[1],dict(ctx,lifesteal=lifesteal))
 elif name=='historical_event_defender_stats':
  target=next((m for player in game.players for m in player.minions if m.uid==event['target'] and m.health>0),None)
  if target is not None:game._set_entity_stats(target,op[1],op[2])
 elif name=='historical_event_silence_defender':
  target=next((m for player in game.players for m in player.minions if m.uid==event['target'] and m.health>0),None)
  if target is not None:game._silence(target)
 elif name=='historical_event_fill_hands':
  for recipient in (owner,1-owner):
   count=max(0,op[1]-len(game.players[recipient].hand))
   if count:game._rule_events.append(('captured_effects',dict(operations=(('draw',count),),context=dict(owner=recipient,source=None,target=0,bonus=0,lifesteal=False)),[]))
 elif name=='historical_event_source_transform_cost':
  if source is not None and source in p.minions:
   candidates=game._generation_candidates(pool(card_type='MINION',minimum=op[1],maximum=op[1]),owner)
   if candidates:game._transform(source,game.rng.choice(candidates))
 elif name=='historical_event_attack_hero':game._deal_effect(game.hero_id(1-owner),event['attack_damage'],ctx)
 elif name=='historical_event_equipped_buff':
  if p.weapon is not None and getattr(p.equipped_card,'uid',None)==event['weapon_uid']:game._buff_weapon(owner,attack=op[1],durability=op[2])
 elif name in ('historical_event_healed_buff','historical_event_attacker_buff','historical_event_played_keyword_buff'):
  uid=event['target'] if name=='historical_event_healed_buff' else event['source']
  target=next((m for m in p.minions if m.uid==uid and m.health>0),None)
  if target is not None:
   game._buff(target,op[1],op[2])
   if name=='historical_event_played_keyword_buff':target.keywords.add(op[3])
 elif name=='historical_event_extra_attack':
  if source in p.minions:source.attacks=max(0,source.attacks-1)
 elif name=='historical_event_armor_dealt':game._gain_armor(owner,event['amount'])
 elif name=='historical_event_drawn_one_copy':
  card=event['card']
  if game._card_data(card)['type']=='MINION':
   copy=game._copy_card(card,source_owner=owner);game._mutation_set_stats(copy,owner,1,1);game._set_card_cost(copy,1);game._enter_hand(owner,copy)
 elif name=='historical_event_drawn_beast_buff':
  card=next((c for c in p.hand if c.uid==event['card'].uid),None)
  if card is not None and game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'BEAST'):_saidan_add(card,'attack_bonus',op[1]);_saidan_add(card,'health_bonus',op[2])
 elif name=='historical_event_chance_draw':
  if game.rng.randrange(2)==0:game._draw(owner)
 elif name=='historical_event_temporary_drawn':
  player=game.players[event['owner']];card=next((c for c in player.hand if c.uid==event['card'].uid),None)
  if card is not None:game._make_temporary(card)
 elif name=='historical_event_draw_count_damage':
  counts=getattr(p,'historical_draw_turn',{});amount=counts.get('count',0) if counts.get('turn')==game.turn else 0
  game._deal_effect(ctx.get('target',0),amount,ctx)
 elif name=='historical_event_copy_death_target':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target')),None)
  if source is not None and target is not None:
   from .death_inheritance import capture,check_supported
   operations=capture(game,target,game._death_operations(target));check_supported(operations)
   source.attached_death_effects.extend(operations)
 elif name=='historical_event_resummon_bearer':
  if source is not None:game._summon(owner,source.card_id,min(ctx.get('death_position',len(p.board)),len(p.board)),entry_origin='resurrection',entry_source=source,entry_site='historical_resummon_bearer')
 elif name=='historical_event_transfer_summon':
  candidates=[m for m in p.minions if m is not source and m.health>0]
  if candidates:game.rng.choice(candidates).attached_death_effects.append(('summon',op[1],1))
 elif name=='historical_event_transfer_buff':
  candidates=[m for player in (game.players if op[1]=='all' else (p,)) for m in player.minions if m is not source and m.health>0 and (op[1]=='all' or has_tribe(game._card_data(m),op[1]))]
  if candidates:
   target=game.rng.choice(candidates);game._buff(target,op[2],op[3]);target.attached_death_effects.append(tuple(op))
 elif name=='historical_event_played_buff_death':
  target=next((m for m in p.minions if m.uid==event.get('source') and m.health>0),None)
  if target is not None:game._buff(target,op[1],op[2]);target.attached_death_effects.append(('summon',op[3],1))
 elif name=='historical_event_inspire_attack':
  if source is not None:source.rule_state['historical_inspire_attack_turn']=game.turn
 elif name=='historical_event_tax_drawn':
  other=event['owner'];snapshot=event['card'];card=next((c for c in game.players[other].hand if c.uid==snapshot.uid),None)
  if card is not None:card.cost_delta+=max(0,min(op[1],op[2]-game._cost(card,other)))
 elif name=='historical_event_sleep_target':game._sleep_minion(game._dormant_entity(ctx.get('target',0)),op[1])
 elif name=='historical_event_totem_attack':
  for minion in p.minions:
   if has_tribe(game._card_data(minion),'TOTEM'):game._buff(minion,op[1],0)
 elif name=='historical_event_murloc_deaths':
  for minion in p.minions:
   if minion is not source and has_tribe(game._card_data(minion),'MURLOC'):minion.attached_death_effects.append(('draw',1))
 elif name=='historical_event_discount_drawn':
  snapshot=event['card'];card=next((c for c in p.hand if c.uid==snapshot.uid),None)
  if card is not None:card.cost_delta-=op[1]
 elif name=='historical_event_copy_drawn':game._clone_hand_card(owner,event['card'],source_owner=owner)
 elif name=='historical_event_spell_damage':
  if op[1]=='self':values=[source] if source in p.minions else []
  elif op[1]=='target':values=[m for player in game.players for m in player.minions if m.uid==ctx.get('target',0)]
  else:
   from .historical_board_primitives import selected
   values=selected(game,'adjacent',ctx)
  for m in values:
   m.rule_state['historical_spell_damage']=m.rule_state.get('historical_spell_damage',0)+op[2]
 elif name=='historical_event_damage_spell_damage':
  uid=ctx.get('target',0);target=next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)
  if target is not None:
   game._deal_effect(uid,op[1],ctx)
   if target.health>0:target.rule_state['historical_spell_damage']=target.rule_state.get('historical_spell_damage',0)+op[2]
 elif name=='historical_event_summon_modify':
  uid=event.get('source');target=next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)
  condition,value,attack,health,keyword=op[1:]
  matched=(event.get('entry_attack',0)<=value if condition=='attack_at_most' else
           event.get('entry_health')==value if condition=='health' else
           value in event.get('entry_keywords',()) if condition=='keyword' else
           event.get('printed_cost')==value)
  if target is not None and matched:
   game._buff(target,attack,health)
   if keyword:target.keywords.add(keyword)
 elif name=='historical_event_summon_self_death_buff':
  if event.get('entry_deathrattle') and source is not None:game._buff(source,op[1],op[2])
 elif name=='historical_event_trigger_summoned':game._effect(('historical_batch_trigger_target_death',),dict(ctx,target=event['source']))
 elif name=='historical_event_freeze_random_enemy':
  values=[game.hero_id(1-owner)]+[m.uid for m in q.minions if m.health>0]
  if values:game._freeze(game.rng.choice(values))
 elif name=='historical_event_enemy_damage_spell_cost':game._deal_effect(game.hero_id(1-owner),event['cost'],ctx)
 elif name=='historical_event_armor_spell_cost':game._gain_armor(owner,event['cost'])
 elif name=='historical_event_destroy_damaged_enemy':
  target=next((m for m in q.minions if m.uid==event['target'] and m.health>0),None)
  if target is not None and not game._fire_immune_target(target.uid,ctx):target.health=0
 elif name=='historical_event_destroy_bottom':
  del p.deck[:min(op[1],len(p.deck))]
 elif name=='historical_event_buff_unattacked':
  for m in p.minions:
   if m is not source and getattr(game,'_historical_attack_turns',{}).get(m.uid)!=game.turn:game._buff(m,op[1],op[2])
 elif name=='historical_event_draw_unattacked':
  if source is not None and getattr(game,'_historical_attack_turns',{}).get(source.uid)!=game.turn:game._effect(('draw',op[1]),ctx)
 elif name=='historical_event_summon_source_stats':
  if source is not None:game._summon(owner,op[1],entry_stats=(max(0,source.attack),max(1,source.health)),entry_origin='effect',entry_site='historical_event_source_stats',entry_source=source)
 elif name=='historical_event_other_totem_zones':
  from engine.game import Card
  for zone in ('hand','deck'):
   values=getattr(p,zone)
   for i,value in enumerate(values):
    if game._card_data(value)['type']=='MINION' and has_tribe(game._card_data(value),'TOTEM'):
     card=value if isinstance(value,Card) else Card(game._new_id(),value);_saidan_add(card,'attack_bonus',op[1]);_saidan_add(card,'health_bonus',op[2]);values[i]=card
  for m in p.minions:
   if m is not source and has_tribe(game._card_data(m),'TOTEM'):game._buff(m,op[1],op[2])
 elif name=='historical_event_spellpower_area':game._effect(('area_damage','enemies',op[1]+game._spell_damage(owner)),ctx)
 elif name=='historical_event_half_hand_cost':
  if p.hand:
   card=game.rng.choice(p.hand);card.cost_delta+=-1 if game.rng.randrange(2)==0 else 1
 elif name=='historical_event_destroy_smaller':
  if source is not None:
   values=[m for player in game.players for m in player.minions if m.health>0 and m.attack<source.attack]
   if values:
    target=game.rng.choice(values)
    if not game._fire_immune_target(target.uid,ctx):target.health=0
 elif name=='historical_event_destroy_alone':
  if source is not None and not any(m is not source and m.health>0 for m in p.minions):source.health=0
 elif name=='historical_event_damage_random_other_friendly':
  values=[m for m in p.minions if m is not source and m.health>0]
  if values:game._deal_effect(game.rng.choice(values).uid,op[1],ctx)
 else:return False
 return True

from .historical_sleep_batches import AWAKEN_EFFECTS as SLEEP_AWAKEN, DORMANT_END_EFFECTS as SLEEP_END
AWAKEN_EFFECTS.update(SLEEP_AWAKEN)
DORMANT_END_EFFECTS.update(SLEEP_END)

# First-edition Antaen uses the real two-turn Dormant/awakening program.
DORMANT_INITIAL['TOY_400t4']=2
AWAKEN_EFFECTS['TOY_400t4']=[('missiles','enemies',10)]

# Outland board Student: two owner turns Dormant, then two distinct targets.
DORMANT_INITIAL['SCH_199t22']=2
AWAKEN_EFFECTS['SCH_199t22']=[('historical_student_awaken',)]
