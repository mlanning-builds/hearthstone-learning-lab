"""Historical physical copies and stat exchanges; gameplay review deferred."""
from .historical_saidan import add as _saidan_add
from copy import deepcopy
from engine.game import Card
from .selectors import has_tribe

RULES={
 'EX1_564':('minion',[('historical_copy_transform_target',None,None)]),
 'DAL_030':('historical_copy_friendly_deathrattle',[('historical_copy_transform_target',2,2)]),
 'YOG_501':('historical_copy_damaged',[('historical_copy_transform_target',None,None)]),
 'AV_267':('none',[('historical_copy_transform_zone','deck','DEMON',6,6)]),
 'TTN_441':('none',[('historical_copy_transform_zone','hand',None,8,8)]),
 'DAL_070':('none',[('historical_copy_summon_zone','deck',None,None,('RUSH',))]),
 'KAR_114':('none',[('historical_copy_summon_zone','deck',1,1,())]),
 'BOT_507':('none',[('historical_copy_group','adjacent',None,None)]),
 'OG_316':('none',[('historical_copy_group','others',1,1)]),
 'JAM_014':('friendly_minion',[('historical_mutation_transform_copy_source',)]),
 'OG_102':('friendly_minion',[('historical_copy_swap','source','stats')]),
 'TOY_894':('minion',[('historical_copy_swap','source','attack')]),
 'TOY_895':('minion',[('historical_copy_swap','source','health')]),
 'TOY_896':('minion',[('historical_copy_swap','source','stats')]),
 'LOOT_529':('none',[('historical_copy_swap_others',)]),
 'RLK_593':('none',[('historical_copy_double_deck',)]),
 'ULD_229':('none',[('historical_copy_swap_deck_tops',)]),
 'TSC_020':('none',[('historical_copy_swap_spell_costs',)]),
 'SW_074':('none',[('historical_copy_random_hand',)]),
 'TRL_318':('none',[('historical_copy_opening_hand',)]),
 'TRL_527':('none',[('historical_copy_opponent_decks',)]),
 'BOT_280':('none',[]),'BOT_555':('none',[]),'SW_419':('none',[]),
 'BT_190':('none',[]),
 'MAW_034':('none',[('historical_copy_destroy_deck',),('keyword_self','IMMUNE')]),
 'TOY_516':('none',[('historical_if_combo',('copy_self_right',1))]),
 'WW_406':('none',[('outcast_operation',('copy_self_right',1))]),
}
DEATH_EFFECTS={
 'LOOT_412':[('historical_copy_summon_zone','hand',1,1,())],
 'REV_015':[('historical_copy_summon_zone','deck',2,2,())],
 'RLK_845':[('historical_copy_enemy_deck_hand',)],
}
END_EFFECTS={'BT_190':[('historical_copy_neighbor',)]}
TRIGGERS={
 'BOT_280':(('historical_copy_event','enemy_play'),[('historical_copy_played','summon',1,1)]),
 'BOT_555':(('historical_copy_event','enemy_play'),[('historical_copy_played','transform',None,None)]),
 'SW_419':(('historical_copy_event','cheap_play'),[('historical_copy_played','summon',None,None)]),
}
RULES.update({
 'DMF_231':('none',[('historical_copy_hand_edges',)]),
 'CS3_005':('none',[('historical_if_combo',('historical_copy_last_enemy',))]),
 'BT_301':('none',[('discard_highest_cost',)]),
 'KAR_070':('none',[('historical_copy_discount_hand','foreign',2)]),
 'LOOT_537':('none',[('historical_copy_discount_hand','nonstarting',2)]),
 'CFM_656':('none',[('historical_copy_remove_enemy_stealth',)]),
 'DEEP_036':('none',[]),
 'DED_500':('none',[('historical_copy_attack_extremes',)]),
 'WC_030':('none',[('historical_copy_eat_enemy_hand',)]),
 'UNG_833':('none',[('historical_copy_discard_lowest',2)]),
 'DRG_075':('none',[]),
 'ULD_327':('none',[]),
 'DMF_081':('none',[]),
 'DRG_064':('none',[]),
 'YOG_515':('none',[('add','YOG_514',2)]),
 'DAL_751':('none',[('historical_copy_fill_both','DAL_751t')]),
 'WW_822':('none',[('historical_copy_dragons_self',)]),
 'BAR_077':('none',[('historical_copy_watch_posts',)]),
})
from .generation_cards import pool,random_cards,discover
RULES['DRG_075']=('none',[random_cards(pool(card_type='SPELL',minimum=1,maximum=1,classes='own'),2)])
RULES['ULD_327']=('none',[random_cards(pool(card_type='MINION',classes='other'))])
# The enemy owns the generated card, but eligibility belongs to the full any-class pool.
RULES['DRG_064']=('none',[('historical_copy_enemy_generate',pool(card_type='MINION',minimum=1,maximum=1),3,'board')])
RULES['DMF_081']=('none',[('historical_copy_enemy_generate',pool(card_type='MINION',minimum=4,maximum=4),1,'hand')])
DEATH_EFFECTS.update({'UNG_032':[('historical_copy_enemy_deck_hand',)],
 'TTN_859':[('historical_copy_last_enemy',)],
 'DEEP_036':[('historical_copy_double_elementals',)]})
START_EFFECTS={'BAR_312':('owner',[('historical_copy_enemy_spell',)])}
RULES['BAR_312']=('none',[])
FIXED_TOKEN_IDS=frozenset(('DAL_751t','BAR_077t'))
TOKEN_RULES={cid:('none',[]) for cid in FIXED_TOKEN_IDS}
for cid in DEATH_EFFECTS:RULES.setdefault(cid,('none',[]))

# Backward-zone copies reset board enchantments; battlefield copies retain them.
RULES.update({
 'CFM_660':('friendly_minion',[('historical_copy_target_delivery','deck',1,None,None,None,False)]),
 'GIL_815':('friendly_minion',[('historical_copy_target_delivery','deck',1,None,None,None,False)]),
 'DRG_070':('friendly_dragon',[('historical_copy_target_delivery','hand',1,None,None,None,False)]),
 'DRG_402':('friendly_minion',[('historical_copy_target_all',)]),
 'GIL_658':('friendly_minion',[('historical_copy_target_delivery','hand',1,10,10,10,False)]),
 'LOOT_516':('friendly_minion',[('historical_copy_target_delivery','hand',1,None,None,None,False)]),
 'OG_291':('friendly_minion',[('historical_copy_target_delivery','hand',1,1,1,1,False)]),
 'SW_064':('friendly_beast',[('historical_copy_target_delivery','deck',3,3,3,None,False)]),
 'TTN_742':('friendly_minion',[('historical_copy_target_delivery','hand',1,None,None,None,True)]),
})

# These intrinsic bodies are implemented by the scoped repetition consumers.
RULES.update({cid:('none',[]) for cid in ('LOE_077','FP1_031','ICC_901','RLK_912')})
RULES['DEEP_020']=('none',[('historical_copy_permanent_battlecries',)])
RULES.update({
 'BOT_288':('friendly_minion',[('historical_copy_target_delivery','deck',3,None,None,None,False)]),
 'ETC_110':('minion',[('historical_copy_transform_target',3,3)]),
 'DAL_052':('none',[('historical_copy_muckmorph',)]),
 'DAL_546':('none',[('historical_copy_barista',)]),
 'DAL_799':('none',[('historical_copy_healed_self',)]),
 'TOY_827':('none',[('historical_copy_corpse_self',5)]),
 'WW_360':('none',[('copy_self_right',1)]),
 'AV_139':('none',[]),
})
DEATH_EFFECTS.update({'LOOT_056':[('historical_copy_death_shuffle',)],'EX1_016':[('historical_copy_random_control',)]})
for cid in DEATH_EFFECTS:RULES.setdefault(cid,('none',[]))
END_EFFECTS['AV_139']=[('historical_copy_devour_enemy',)]
# Target-memory bodies are populated by record_targeted_spell before resolution.
RULES.update({cid:('none',[]) for cid in ('BOT_258','BOT_558','UNG_953')})
RULES['BT_334']=('none',[('historical_copy_friendly_spell_history',)])
RULES.update({
 'AT_003':('none',[]),'YOD_008':('none',[]),'ICC_068':('none',[]),'TOY_528':('none',[]),
 'DRG_253':('none',[]),'GVG_087':('none',[]),
 'AV_115':('none',[('historical_copy_snowflurry',)]),
 'TRL_390':('none',[('historical_copy_power_bonus',2)]),
 'AT_086':('none',[('historical_copy_saboteur',)]),
 'BAR_547':('none',[('historical_copy_power_threshold',10,'damage')]),
 'TRL_316':('none',[('historical_copy_power_threshold',8,'ragnaros')]),
 'ETC_382':('none',[('historical_copy_power_permanent','armor')]),
 'ETC_385':('none',[('historical_copy_power_permanent','attack')]),
 'AT_023':('none',[]),
})
DEATH_EFFECTS.update({'ETC_382':[('historical_copy_power_permanent','armor')],'ETC_385':[('historical_copy_power_permanent','attack')]})
TRIGGERS['AT_023']=('hero_power_used',[('historical_copy_void_crusher',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('EX1_298',))
RULES.update({
 'BAR_064':('none',[('historical_copy_next_spell_bonus',2)]),
 'BOT_531':('none',[('historical_copy_next_spell_bonus',2)]),
 'BOT_411':('none',[('historical_copy_next_spell_repeat',)]),
 'VAC_919':('none',[('historical_copy_next_spell_lifesteal',)]),
 'BT_733':('none',[]),'RLK_952':('none',[]),'SCH_539':('none',[]),
 'ETC_081':('none',[]),'KAR_712':('none',[]),'ETC_398':('none',[]),
 'GIL_685':('none',[]),'WC_015':('none',[]),
 'ULD_189':('none',[('double_self_health',)]),
 'GIL_128':('none',[('historical_copy_double_hand',)]),
 'GIL_837':('none',[('historical_copy_odd_health',)]),
 'SC_763':('none',[('historical_copy_spend_double',4)]),
})
RULES.update({
 'DAL_058':('none',[('historical_copy_enemy_recruit',)]),
 'TRL_126':('none',[('historical_copy_recruit_one','deck',(('tribe','eq','PIRATE'),),'RUSH',None) for _ in range(3)]),
 'TRL_259':('none',[('historical_copy_recruit_hand_all','foreign')]),
 'TOY_812':('none',[]),
 'NX2_026':('none',[('historical_copy_recruit_conditional','held_demon')]),
 'AV_100':('none',[('historical_copy_recruit_conditional','drekthar')]),
 'OG_290':('none',[]),
 'DMF_089':('none',[('historical_copy_maxima',)]),
 'BAR_038':('none',[]),
 'CFM_637':('none',[]),'DRG_056':('none',[]),
 'DAL_603':('none',[('historical_copy_mana_cyclone',)]),
})
DEATH_EFFECTS.update({
 'FP1_009':[('historical_copy_enemy_recruit',)],
 'ETC_328':[('historical_copy_less_attack_recruit',)],
 'ICC_812':[('historical_copy_less_attack_recruit',)],
 'OG_317':[('historical_copy_recruit_hand_all','dragon')],
 'TOY_812':[('historical_copy_recruit_one','deck',(('mechanic','eq',keyword),),None,None) for keyword in ('DIVINE_SHIELD','RUSH','TAUNT')],
 'DAL_376':[('historical_copy_oblivitron',)],
})
TRIGGERS['BAR_038']=(('historical_event','friendly_beast_attacked'),[('historical_copy_tavish',)])
START_EFFECTS['OG_290']=('owner',[('historical_copy_put_ten',)])
for cid in DEATH_EFFECTS:RULES.setdefault(cid,('none',[]))
TOXINS=('OG_080b','OG_080c','OG_080d','OG_080e','OG_080f')
RULES.update({
 'OG_080':('none',[('historical_copy_toxin',)]),
 'LOOT_161':('friendly_minion',[('historical_copy_cube',)]),
})
DEATH_EFFECTS.update({
 'ICC_019':[('historical_copy_enemy_turn_summon','ICC_019t')],
 'ICC_034':[('historical_copy_enemy_turn_summon','ICC_900t')],
 'ICC_067':[('historical_copy_enemy_turn_summon','ICC_900t')],
 'CFM_095':[('historical_copy_weasel',)],
 'OG_335':[('historical_copy_enemy_deck_hand',)],
 'OG_080':[('historical_copy_toxin',)],
 'LOOT_415':[('add','LOOT_415t1',1)],
 'UNG_027':[('historical_copy_pyros','UNG_027t2')],
 'UNG_027t2':[('historical_copy_pyros','UNG_027t4')],
})
TOKEN_RULES.update({
 'OG_080b':('none',[('draw',1)]),
 'OG_080c':('friendly_minion',[('historical_copy_toxin_bounce',)]),
 'OG_080d':('minion',[('buff',3,0)]),
 'OG_080e':('friendly_minion',[('temporary_keyword_target','STEALTH','next_start')]),
 'OG_080f':('character',[('damage',2)]),
 'UNG_027t2':('none',[]),'UNG_027t4':('none',[]),
 'ICC_019t':('none',[]),'ICC_900t':('none',[]),
 'LOOT_415t6':('none',[('historical_copy_azari',)]),
})
SEAL_IDS=tuple('LOOT_415t'+str(i) for i in range(1,6))
SEAL_DEMONS=tuple(cid+'t' for cid in SEAL_IDS)
for index,cid in enumerate(SEAL_IDS):
 next_id=SEAL_IDS[index+1] if index<4 else 'LOOT_415t6'
 TOKEN_RULES[cid]=('none',[('summon',SEAL_DEMONS[index],1),('add',next_id,1)])
for cid in SEAL_DEMONS:TOKEN_RULES[cid]=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(TOXINS+SEAL_IDS+SEAL_DEMONS+('LOOT_415t6','UNG_027t2','UNG_027t4','ICC_019t','ICC_900t'))
for cid in DEATH_EFFECTS:
 if cid not in FIXED_TOKEN_IDS:RULES.setdefault(cid,('none',[]))
RULES.update({
 'BT_106':('none',[('historical_copy_evolve_adjacent',1)]),
 'GVG_108':('friendly_minion',[('historical_copy_evolve_target',0)]),
 'OG_328':('friendly_minion',[('historical_copy_evolve_target',1)]),
 'EX1_083':('none',[('historical_copy_tinkmaster',)]),
 'GVG_080':('none',[('historical_copy_fang',)]),
 'LOOT_150':('friendly_minion',[('historical_copy_literal_target','LOOT_150t1')]),
 'TRL_341':('none',[('historical_copy_treespeaker',)]),
 'ICC_852':('historical_copy_taldaram',[('historical_copy_taldaram',)]),
 'TOY_878':('none',[]),'RLK_831':('none',[]),'GDB_230':('none',[]),'DED_511':('none',[]),'DRG_092':('none',[]),
})
DEATH_EFFECTS['RLK_831']=[('historical_copy_spread_plague',)]
TRIGGERS['TOY_878']=(('historical_copy_event','enemy_play'),[('historical_copy_played','transform',3,4)])
TRIGGERS['DRG_092']=('friendly_card_drawn',[('historical_copy_transmogrifier',)])
END_EFFECTS['DED_511']=[('historical_copy_weapon_evolve',)]
TOKEN_RULES.update({cid:('none',[]) for cid in ('EX1_tk28','EX1_tk29','GVG_080t','LOOT_150t1','TRL_341t')})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('EX1_tk28','EX1_tk29','GVG_080t','LOOT_150t1','TRL_341t'))
RULES.update({
 'GVG_014':('minion',[('historical_copy_swap','source','health')]),
 'TRL_501':('none',[('historical_copy_healing_damage_turn',)]),
 'YOG_300':('none',[('historical_copy_healing_damage_next',)]),
})
ADVENTURERS=('WC_034t','WC_034t2','WC_034t3','WC_034t4','WC_034t5','WC_034t6','WC_034t7','WC_034t8')
SOLDIERS=('TOY_814t',)+tuple('TOY_814t'+str(i) for i in range(2,9))
SPARKBOTS=('TTN_719t',)+tuple('TTN_719t'+str(i) for i in range(1,8))
CREWMATES=('GDB_471t',)+tuple('GDB_471t'+str(i) for i in range(2,9))
RULES.update({
 'DEEP_035':('none',[]),
 'ETC_409':('none',[('historical_copy_amalgam_band',)]),
 'GDB_450':('none',[('historical_copy_wayfinder',)]),
 'GDB_471':('none',[]),
 'TOY_350':('none',[('historical_copy_board_bonus','other_beasts')]),
 'TOY_814':('none',[]),
 'TTN_860':('none',[('historical_copy_literal_family','sparkbot','hand')]),
 'WC_027':('none',[]),'WC_028':('none',[]),
 'REV_961':('none',[('historical_copy_elitist_snob',)]),
})
DEATH_EFFECTS.update({
 'DEEP_035':[('historical_copy_board_bonus','all')],
 'TOY_814':[('historical_copy_literal_family','soldier','board') for _ in range(5)],
 'WC_027':[('historical_copy_literal_family','adventurer','board')],
})
END_EFFECTS.update({'GDB_471':[('historical_copy_literal_family','crewmate','hand')],'WC_028':[('historical_copy_literal_family','adventurer','hand')]})
for cid in ADVENTURERS+SOLDIERS+SPARKBOTS:TOKEN_RULES[cid]=('none',[])
for cid in CREWMATES:TOKEN_RULES[cid]=('none',[('historical_copy_crewmates',)])
TOKEN_RULES['WC_034']=('none',[('historical_copy_literal_family','adventurer','board') for _ in range(5)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(ADVENTURERS+SOLDIERS+SPARKBOTS+CREWMATES+('WC_034',))
RULES.update({
 'TSC_087':('none',[('historical_copy_sivara',)]),
 'TSC_658':('none',[('historical_copy_hedra',)]),
 'VAC_304':('none',[('historical_copy_pupil',)]),
 'GIL_640':('none',[]),'GIL_691':('none',[]),'GIL_620':('none',[]),'DAL_607':('none',[]),'WC_023':('none',[]),
})
TRIGGERS.update({
 'GIL_640':('friendly_card_drawn',[('buff_self',1,1)]),
 'GIL_691':('friendly_card_drawn',[('historical_copy_drawn_copy','hand')]),
 'GIL_620':('friendly_card_drawn',[('historical_copy_drawn_copy','dorian')]),
 'DAL_607':('friendly_card_drawn',[('historical_copy_drawn_copy','betrug')]),
 'WC_023':(('historical_event','first_owner_draw'),[('historical_copy_drawn_health',)]),
})
RULES.update({
 'AV_238':('none',[]),'WW_300':('none',[]),
 'DRG_026':('none',[('force_all_others',)]),
 'ETC_419':('none',[]),'ETC_833':('none',[]),'LOOT_041':('none',[]),'TSC_218':('none',[]),
 'REV_934':('none',[('historical_copy_olgra_buff',),('historical_copy_force_enemies',)]),
 'WW_815':('none',[('historical_copy_theldurin',)]),
 'OG_174':('friendly_minion',[('historical_copy_shambler',)]),
 'SCH_149':('none',[('historical_copy_braggart',)]),
 'TOY_642':('none',[('historical_copy_lowest_damage',3)]),
 'GDB_840':('none',[]),'RLK_504':('none',[('historical_copy_corpse_bride',)]),
 'AT_019':('none',[]),'DMF_708':('none',[]),'TID_080':('none',[]),'SW_024':('none',[]),
 'ULD_212':('none',[('historical_copy_bloodstinger',)]),
})
DEATH_EFFECTS.update({'TOY_642':[('historical_copy_lowest_damage',3)],'GDB_840':[('historical_copy_egg_attack',)],'AT_019':[('historical_copy_dreadsteed',)]})
TRIGGERS.update({
 'AV_238':(('historical_copy_event','enemy_play'),[('historical_copy_force_event',)]),
 'WW_300':(('historical_copy_event','enemy_play'),[('historical_copy_force_event',)]),
 'ETC_419':('attacked_self',[('buff_self',1,0),('historical_copy_force_random','minion')]),
 'ETC_833':('spell_cast',[('historical_copy_lowest_damage',1)]),
 'TSC_218':('spell_cast',[('historical_copy_force_random','lowest')]),
})
START_EFFECTS['LOOT_041']=('owner',[('historical_copy_force_random','character')])
END_EFFECTS['SW_024']=[('historical_copy_lothar',)]
TOKEN_RULES.update({'GDB_840t':('none',[]),'RLK_506t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('GDB_840t','RLK_506t'))
RULES.update({
 'WW_373':('none',[]),'CFM_020':('none',[('historical_copy_raza',)]),'JAM_028':('none',[]),
 'GDB_470':('none',[('historical_copy_next_payment','corpses','all',1)]),
 'RLK_659':('none',[('armor',5),('historical_copy_next_payment','armor','minion',3)]),
 'RLK_927':('none',[('historical_copy_next_payment','health','paladin_minion',1)]),
 'TID_719':('none',[('historical_copy_ulthok',)]),'VAC_507':('none',[]),
 'ETC_068':('none',[('historical_copy_fatigue','buff')]),'ETC_070':('none',[('historical_copy_fatigue','summon')]),
})
DEATH_EFFECTS['WW_373']=[('historical_copy_random_control',)]
TOKEN_RULES['ETC_070t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('ETC_070t',))
RULES.update({
 'AV_286':('none',[('historical_copy_cast_zone','own','hand','FEL','highest','random')]),
 'SW_109':('none',[('historical_copy_cast_zone','own','hand',None,'highest','random')]),
 'DAL_538':('none',[('historical_copy_cast_zone','enemy','hand',None,'random','random')]),
 'LOOT_414':('none',[]),'DAL_558':('none',[]),
 'TSC_630':('none',[('historical_copy_cast_school_copy',school) for school in ('FIRE','FROST','NATURE')]),
 'DED_515':('none',[('historical_copy_history_spell','parrot')]),
 'RLK_608':('none',[('historical_copy_history_spell','asvedon')]),
 'DED_501':('none',[('historical_copy_history_spell','squawker')]),
 'LOE_053':('none',[]),'GVG_028':('none',[]),'MIS_303':('none',[]),'UNG_843':('none',[]),
})
END_EFFECTS.update({'LOOT_414':[('historical_copy_cast_zone','own','deck',None,'random','random')],'DAL_558':[('historical_copy_history_spell','vargoth')]})
TRIGGERS.update({
 'LOE_053':(('historical_event','friendly_spell_other_minion'),[('historical_copy_cast_event_self',)]),
 'GVG_028':(('historical_event','enemy_spell_for_gallywix'),[('historical_copy_gallywix',)]),
 'MIS_303':('spell_cast',[('historical_copy_spell_plus_one',)]),
 'UNG_843':(('historical_event','friendly_spell_source'),[('historical_copy_voraxx',)]),
})
TOKEN_RULES.update({'GVG_028t':('none',[('temporary_mana',1)]),'UNG_999t2t1':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('GVG_028t','UNG_999t2t1'))
RULES.update({
 'FP1_030':('none',[('historical_copy_timed_cost','SPELL',5,None,'enemy')]),
 'NEW1_029':('none',[('historical_copy_timed_cost','SPELL',0,0,'enemy')]),
 'REV_378':('none',[('historical_copy_timed_cost','MINION',1,None,'enemy')]),
 'YOD_033':('none',[('historical_copy_timed_cost','BATTLECRY',5,None,'enemy')]),
 'VAC_524':('none',[('historical_copy_timed_cost','SPELL',0,5,'both')]),
 'VAC_332':('none',[('historical_copy_sea_shill',)]),
 'DAL_081':('none',[('historical_copy_jeweler',)]),
 'RLK_527':('none',[('historical_copy_timewarden',)]),
 'GDB_874':('none',[('historical_copy_astrobiologist',)]),
 'MAW_014':('none',[('historical_copy_edge_lock',)]),
 'TID_744':('none',[('historical_copy_hand_lock_choice',)]),
 'SW_418':('none',[('historical_copy_next_draw_discount',1)]),
 'WW_383':('none',[('historical_copy_next_draw_spell_copy',)]),
 'AV_403':('none',[('historical_copy_replace_zones','foreign')]),
 'DAL_422':('none',[('historical_copy_replace_zones','legendary')]),
})
RULES.update({
 'AV_142t':('none',[('historical_copy_ivus',)]),
 'BT_230':('enemy_minion',[('historical_copy_lurker',)]),
 'DRG_037':('minion',[('historical_copy_flik',)]),
 'GDB_132':('enemy_minion',[('historical_copy_wrathguard',)]),
 'GDB_302':('none',[('historical_copy_blazing',)]),
 'LEG_RLK_071':('none',[('historical_copy_patchwerk',zone) for zone in ('hand','deck','board')]),
 'TOY_100':('none',[]),
 'WORK_042':('friendly_minion',[('historical_copy_capture_destroy',1,True)]),
 'TTN_754':('friendly_minion',[('historical_copy_capture_destroy',1,False)]),
 'VAC_946':('none',[('historical_copy_chef',)]),
 'WW_397':('none',[]),
 'UNG_907':('none',[('historical_copy_ozruk',)]),
})
DEATH_EFFECTS.update({'TOY_100':[('area_damage','enemies',2)],'WW_397':[('historical_copy_dang_blasted',)]})
END_EFFECTS['WORK_042']=[('historical_copy_cubicle_summon',)]
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('FP1_007',))
PLAGUES=('TTN_450t','TTN_450t2','TTN_450t3')
RULES.update({
 'TTN_450':('none',[]),'TTN_455':('none',[('historical_copy_tomb_traitor',)]),
 'TTN_850':('none',[('historical_copy_helya',)]),'TRL_541':('none',[]),
 'TSC_955':('none',[('historical_copy_give_curse',)]),'TSC_959':('none',[('historical_copy_give_curse',)]),
})
DEATH_EFFECTS.update({'TTN_450':[('historical_copy_shuffle_plagues',2)],'TRL_541':[('on_draw_shuffle','TRL_541t',1,0),('on_draw_shuffle','TRL_541t',1,1)]})
TOKEN_RULES.update({
 'TTN_454':('character',[('damage',3),('historical_copy_shuffle_plagues',2)]),
 'TTN_736':('none',[]),'RLK_070t':('none',[]),
 'TRL_541t':('none',[('on_draw_hurt_owner',3)]),
 'TSC_955t':('none',[]),
 'TSC_956':('minion',[('damage',4),('historical_copy_give_curse',)]),
 'TSC_924':('none',[('area_damage','all_minions',4),('historical_copy_give_curse',)]),
})
for cid in PLAGUES:TOKEN_RULES[cid]=('none',[('on_draw_hurt_owner',2),('historical_copy_plague_effect',cid)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(PLAGUES+('TTN_454','TTN_736','RLK_070t','TRL_541t','TSC_955t','TSC_956','TSC_924'))

RULES.update({
 'BAR_721':('none',[('on_draw_shuffle','BAR_721t',1,0)]),
 'DRG_308':('enemy_minion',[('historical_copy_kaahrj',)]),
 'DMF_521':('none',[('equip','DMF_521t')]),
 'DAL_379':('none',[('equip','DAL_379t')]),
 'DRG_082':('none',[('historical_copy_steal_weapon',)]),
})
TOKEN_RULES.update({'BAR_721t':('none',[('historical_copy_mankrik',)]),'BAR_721t2':('none',[]),'DMF_521t':('none',[]),'DAL_379t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('BAR_721t','BAR_721t2','DMF_521t','DAL_379t'))

RULES['EX1_050']=('none',[('draw',2),('historical_copy_enemy_draw',2)])

RULES.update({
 'JAM_005':('friendly_minion',[('historical_batch_trigger_target_death',),('historical_batch_trigger_target_death',)]),
 'OG_309':('friendly_minion',[('historical_batch_trigger_target_death',)]),
 'ICC_215':('none',[('historical_copy_enemy_deck_all',)]),
 'JAM_023':('none',[('historical_copy_enemy_top',)]),
 'LOOT_383':('none',[('historical_copy_enemy_random_two',)]),
 'MIS_314':('none',[]),
 'MIS_703':('none',[('historical_copy_hero_set',15)]),
 'OG_312':('none',[('equip','OG_058')]),
})
from .generation_cards import pool,random_cards
DEATH_EFFECTS['MIS_314']=[random_cards(pool(card_type='MINION',minimum=1,maximum=1),3,destination='board')]
TOKEN_RULES['OG_058']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('OG_058',))

RULES.update({
 'SCH_160':('none',[random_cards(pool(card_type='SPELL',classes='own',minimum=1,maximum=1))]),
 'SCH_244':('none',[]),
 'SCH_428':('none',[('historical_copy_polkelts_order',)]),
 'SCH_522':('none',[('historical_copy_steeldancer',)]),
 'RLK_900':('none',[('historical_copy_die',)]),
 'RLK_113':('none',[]),'RLK_217':('none',[]),
 'RLK_592':('none',[('historical_copy_invincible',)]),
 'RLK_731':('none',[('historical_copy_corpse_hand_attack',2,2)]),
 'RLK_825':('character',[('historical_copy_shockspitter',)]),
 'GIL_198':('none',[('historical_copy_replace_enemy_hand',)]),
 'MAW_022':('none',[]),
})
DEATH_EFFECTS.update({
 'SCH_244':[random_cards(pool(card_type='MINION',tribe='BEAST',minimum=3,maximum=3),destination='board')],
 'RLK_113':[('historical_copy_brittleskin',)],
 'RLK_217':[('historical_copy_illusionist',)],
 'RLK_592':[('historical_copy_invincible',)],
 'MAW_022':[('historical_copy_enemy_hand_sample',2)],
})

RULES.update({
 'TID_707':('none',[]),
 'TOY_382':('none',[]),
 'TOY_526':('none',[('historical_copy_rook_attack',)]),
 'TOY_806':('none',[random_cards(pool(card_type='MINION',rarity='LEGENDARY'),10,destination='deck',set_cost=1)]),
 'TTN_716':('none',[random_cards(pool(card_type='MINION',tribe='MECHANICAL',mechanic='MAGNETIC'),2,cost_delta=-2)]),
 'TTN_718':('none',[('historical_copy_random_starting_hand',)]),
 'TTN_475':('none',[('historical_copy_previous_elemental_draw',)]),
 'TSC_648':('none',[('historical_copy_coral',)]),
 'TRL_545':('none',[('historical_copy_templar',)]),
 'TTN_471':('none',[]),'TTN_700':('none',[]),
})
DEATH_EFFECTS.update({
 'TID_707':[random_cards(pool(card_type='SPELL',school='ARCANE',classes='MAGE'),2,temporary=True)],
 'TOY_382':[('add','TOY_382t',2)],
 'TTN_700':[random_cards(pool(card_type='MINION',minimum=8,maximum=8),destination='board')],
})
TOKEN_RULES.update({'TOY_382t':('character',[('heal',3)]),'TSC_648t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('TOY_382t','TSC_648t'))

RULES.update({
 'LEG_RLK_077':('none',[('summon','RLK_077t',2)]),
 'LEG_RLK_753':('none',[('historical_copy_geist',)]),
 'LEG_RLK_226':('none',[]),
})
DEATH_EFFECTS['LEG_RLK_226']=[('historical_copy_ymirjar',)]
TOKEN_RULES.update({'RLK_077t':('none',[]),'RLK_226t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('RLK_077t','RLK_226t'))

RULES.update({
 'VAC_442':('character',[('historical_copy_streak_damage','target')]),
 'WW_026':('none',[('historical_copy_streak_damage','enemies')]),
 'WW_424':('none',[('historical_copy_streak_copies',)]),
 'WW_024':('none',[('historical_copy_prairie',)]),
 'VAC_301':('none',[('historical_copy_razzle',)]),
 'VAC_339':('none',[]),'VAC_413':('none',[]),
 'WW_814':('none',[('historical_copy_spurfang',)]),
 'WW_434':('character',[('historical_copy_quickdraw_operation',('damage',6))]),
 'WW_808':('none',[('historical_copy_quickdraw_operation',('temporary_keyword_self','IMMUNE','end'))]),
 'WW_358':('none',[('historical_copy_farm_hand',)]),
 'WW_398':('none',[('historical_copy_gatekeeper',)]),
 'YOP_007':('none',[('historical_copy_xanesh',)]),
})
END_EFFECTS.update({'VAC_339':[('historical_copy_cheese_elemental',)],'VAC_413':[('add','VAC_413t',1)]})
DEATH_EFFECTS.update({'VAC_413':[('hand_buff',2,3)],'WW_814':[('historical_copy_spurfang',)]})
TOKEN_RULES.update({cid:('none',[]) for cid in ('WW_024t','VAC_339t','VAC_413t')})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('WW_024t','VAC_339t','VAC_413t'))

RULES.update({
 'ETC_408':('none',[('historical_copy_power_slider',)]),
 'ETC_536':('none',[]),
 'ETC_836':('none',[('historical_copy_fill_bananas',)]),
 'EX1_085':('historical_copy_mct',[('historical_copy_control','board_four')]),
 'EX1_091':('historical_copy_cabal',[('historical_copy_control','small_attack')]),
 'EX1_382':('enemy_minion',[('historical_copy_aldor',)]),
 'GDB_303':('none',[random_cards(pool(card_type='SPELL',school='FIRE'),5,destination='deck',cost_delta=-2)]),
 'GDB_461':('none',[('historical_copy_last_draenei',)]),
 'GDB_477':('none',[('historical_copy_eight_hands',)]),
 'GDB_723':('none',[random_cards(pool(card_type='MINION',tribe='DRAENEI'),3,temporary=True)]),
 'GIL_125':('none',[('historical_copy_hat',)]*3),
 'GDB_877':('none',[]),
})
DEATH_EFFECTS.update({'ETC_536':[('historical_copy_highest_spell',)],'GDB_877':[('historical_copy_escape_pod',)]})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('EX1_014t',))

RULES.update({
 'JAM_029':('none',[('historical_copy_doomkin',)]),
 'LOE_020':('none',[('historical_copy_camel_one','own'),('historical_copy_camel_one','enemy')]),
 'LOOT_358':('none',[('historical_copy_grumble',)]),
 'LOOT_535':('none',[('historical_copy_alanna',)]),
 'LOOT_539':('none',[('historical_copy_spiteful',)]),
 'MAW_008':('none',[('draw_until',5),('historical_copy_enemy_draw_five',)]),
 'MAW_030':('none',[('historical_copy_custodian',)]),
 'NX2_032':('none',[]),
})
DEATH_EFFECTS['NX2_032']=[('historical_copy_lost_exarch',)]
TOKEN_RULES.update({'LOOT_535t':('none',[]),'NX2_032t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('LOOT_535t','NX2_032t'))
TRIGGERS['LOOT_329']=(('historical_copy_event','own_play'),[('historical_copy_played','summon',None,None)])
RULES['LOOT_329']=('none',[])

RULES.update({
 'DRG_208':('none',[('historical_copy_hand_capacity',12,False),('draw',4)]),
 'ETC_087':('none',[('historical_copy_hand_capacity',11,True)]),
 'BAR_315':('enemy_minion',[('historical_copy_serena',)]),
 'DRG_207':('none',[('historical_copy_abyssal_summoner',)]),
 'BT_309':('none',[]),
 'LEG_RLK_082':('none',[]),
})
DEATH_EFFECTS.update({'BT_309':[('on_draw_shuffle','BT_309t',1,0)],'LEG_RLK_082':[('historical_copy_health_return',)]})
TOKEN_RULES.update({'BT_309t':('none',[('historical_resurrection_pick','demon',3,())]),'DRG_207t':('none',[]),'DRG_104t2':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('BT_309t','DRG_207t','DRG_104t2'))

RULES.update({
 'SW_080':('none',[]),
 'TID_000':('none',[]),
 'TOY_386':('none',[('historical_copy_giftwrapped',)]),
 'RLK_741':('none',[('historical_copy_soulstealer',)]),
 'SCH_337':('none',[]),'SCH_426':('none',[]),
})
START_EFFECTS['SW_080']=('every',[('draw',1)])
END_EVERY_EFFECTS={'SW_080':[('draw',1)]}
END_EFFECTS['TID_000']=[('historical_copy_tides',)]
END_EFFECTS['SCH_337']=[('historical_copy_attack_tokens','SCH_337t',2)]
DEATH_EFFECTS['SCH_426']=[('historical_copy_attack_tokens','SCH_426t',1)]
TOKEN_RULES.update({cid:('none',[]) for cid in ('SCH_126t','SCH_337t','SCH_426t')})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('SCH_126t','SCH_337t','SCH_426t'))

SPIRIT_IDS=frozenset(('TRL_060','TRL_223','TRL_251','TRL_309','TRL_327','TRL_502','TRL_901','TRL_092','TOY_028','TTN_923'))
RULES.update({cid:('none',[]) for cid in SPIRIT_IDS})
RULES.update({
 'ULD_167':('none',[]),'ULD_702':('none',[]),
 'ULD_304':('none',[('historical_copy_phaoris',)]),
 'ULD_706':('none',[]),'ULD_198':('none',[]),
 'TSC_659':('none',[('historical_copy_trenchstalker',)]),
 'TRL_253':('none',[('copy_self_right',1)]*6),
})
DEATH_EFFECTS['ULD_706']=[('historical_copy_decoy',)]
START_EFFECTS['ULD_198']=('owner',[('historical_copy_mirage',)])
TOKEN_RULES['TRL_309t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('TRL_309t',))

RULES.update({
 'TSC_039':('none',[('historical_copy_bottom_token','TSC_039t')]),
 'TSC_776':('none',[('historical_copy_bottom_token','TSC_776t')]),
 'TSC_057':('none',[]),'TSC_919':('none',[]),'TSC_945':('none',[]),
 'TTN_482':('none',[]),'TOY_897':('none',[]),'TSC_653':('none',[]),
 'TRL_306':('none',[]),'VAC_958':('none',[]),
})
DEATH_EFFECTS.update({
 'TSC_057':[('historical_copy_bottom_token','TSC_057t')],
 'TSC_919':[('historical_copy_bottom_token','TSC_919t')],
 'TSC_945':[('historical_copy_bottom_token','TSC_945t')],
 'TTN_482':[('historical_copy_permanent_shuffle','add',3,'shuffle')],
 'TOY_897':[('historical_copy_permanent_shuffle','double',2,'shuffle')],
 'TSC_653':[('historical_copy_permanent_shuffle','base_add',2,'bottom')],
 'TRL_306':[('historical_copy_retained_shuffle',)],
 'VAC_958':[('historical_copy_retained_shuffle',)],
 'TSC_945t':[('historical_copy_recruit_one','deck',(('tribe','eq','BEAST'),),None,None)],
})
TOKEN_RULES.update({
 'TSC_039t':('none',[('historical_copy_sunken_scavenger',)]),
 'TSC_776t':('none',[random_cards(pool(card_type='MINION',tribe='MECHANICAL'),3,cost_delta=-1)]),
 'TSC_057t':('none',[]),'TSC_919t':('none',[]),'TSC_945t':('none',[]),
})
TRIGGERS['TSC_057t']=('attacked_self',[('damage_random_enemy_minion',5)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('TSC_039t','TSC_776t','TSC_057t','TSC_919t','TSC_945t'))

RULES.update({cid:('none',[]) for cid in ('GVG_079','GVG_122','LOOT_193','LOE_107','GIL_800','SW_063')})
RULES.update({cid:('minion',[('historical_copy_bind_fan',)]) for cid in ('ETC_107','ETC_108','ETC_109')})
END_EVERY_EFFECTS['GVG_094']=[('historical_copy_jeeves',)]
RULES['GVG_094']=('none',[])

RULES.update({
 'GDB_229':('none',[('historical_copy_next_minion','DRAENEI',1,'attack')]),
 'GDB_232':('none',[('historical_copy_next_minion','DRAENEI',1,'hero_attack')]),
 'GDB_455':('none',[('historical_copy_next_minion','DRAENEI',2,'copy')]),
 'GDB_720':('none',[('historical_copy_next_minion','DRAENEI',1,'buff_2_1')]),
 'GDB_861':('none',[('historical_copy_next_minion','DRAENEI',1,'health_2_rush')]),
 'TTN_752':('none',[('historical_copy_next_minion','MINION',3,'set_8_8')]),
 'GDB_235':('none',[]),'GDB_469':('none',[]),
 'WORK_013':('none',[('historical_copy_turbulus',)]),
 'GDB_117':('none',[('historical_copy_dirdra',)]),
 'WW_331':('none',[]),'WW_332':('none',[]),
})
DEATH_EFFECTS.update({'GDB_117':[('filtered_draw',(('id','in',CREWMATES),),2)],'WW_331':[('add','WW_331t',1)],'WW_332':[('on_draw_shuffle','WW_331t',2,1)]})
TOKEN_RULES['WW_331t']=('character',[('damage',0)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('WW_331t',))

from .generation_cards import discover
RULES.update({
 'RLK_834':('none',[('historical_copy_vizier',)]),
 'RLK_867':('friendly_minion',[('grant_death_target',(('summon','RLK_018t',1),))]),
 'ONY_019':('none',[discover(pool(mechanic='CHOOSE_ONE'),choose_both=True)]),
})
TOKEN_RULES['RLK_018t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('RLK_018t',))
RULES.update({'VAC_443':('none',[('historical_copy_draw_cast_charges',1)]),'SW_447':('none',[('historical_copy_draw_cast_charges',3)]),'TTN_842':('none',[('historical_copy_jotun',)])})
RULES.update({'SC_756':('none',[]),'SC_783':('none',[('historical_copy_void_ray',)])})
END_EFFECTS['SC_756']=[('historical_copy_attack_tokens','SC_756t',4)]
TOKEN_RULES['SC_756t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('SC_756t',))
RULES.update({cid:('none',[]) for cid in ('EX1_350','GIL_646','EX1_591','LEG_RLK_115','LOE_119','SW_446','VAC_936','GDB_144','LOOT_382')})
RULES.update({cid:('none',[]) for cid in ('AT_088','DMF_068','GVG_065','GVG_066','GVG_088','WW_418','GVG_112','TRL_532','WW_420')})

RULES.update({
 'WW_419':('none',[]),
 'WW_421':('none',[('historical_resurrection_pick','ogre_gang',-1,('WINDFURY',))]),
 'WW_041':('none',[('historical_copy_bottom_token','WW_044t')]),
 'WW_043':('none',[]),'WW_044':('none',[]),
 'WW_091':('none',[('add','WW_044t',2)]),
 'YOG_506':('none',[]),
})
DEATH_EFFECTS.update({'WW_041':[('historical_copy_bottom_token','WW_044t')],'WW_044':[('add','WW_044t',1)],'YOG_506':[('historical_copy_chimaera',)]})
TOKEN_RULES.update({'WW_044t':('none',[('historical_copy_sludge_damage',)]),'YOG_506t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('WW_044t','YOG_506t'))
# Rustwix rolls independently from all nine collectible class Prime outcomes.
RUSTWIX_PRIMES=('BT_019t','BT_028t','BT_109t','BT_123t','BT_136t','BT_197t','BT_210t','BT_309t','BT_713t')
RULES['YOP_004']=('none',[])
DEATH_EFFECTS['YOP_004']=[('historical_copy_rustwix',)]
TOKEN_RULES['UNG_018']=('character',[('damage',2),('add','UNG_809t1',1)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('UNG_018',))|frozenset(RUSTWIX_PRIMES)
RULES['UNG_919']=('none',[])
TRIGGERS['UNG_919']=(('historical_copy_event','enemy_play'),[('historical_copy_force_event',)])
RULES.update({
 'TRL_409':('none',[('historical_copy_gral',)]),
 'SW_069':('none',[]),
 'LOOT_541':('none',[('historical_copy_swap_decks',),('historical_copy_ransom',)]),
 'TOY_357':('none',[('historical_copy_plush',)]),
 'ETC_113':('none',[('historical_copy_fizzle',)]),
 'WON_104':('none',[('historical_copy_witch',)]),
})
DEATH_EFFECTS.update({'TRL_409':[('historical_copy_stored_hand','historical_gral')],'SW_069':[('historical_copy_stored_hand','historical_banker')]})
END_EFFECTS['SW_069']=[('historical_copy_banker_store',)]
TOKEN_RULES.update({'LOOT_541t':('none',[('historical_copy_swap_decks',)]),'ETC_113t':('none',[('historical_copy_snapshot_restore',)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('LOOT_541t','ETC_113t','CS2_065'))
RULES.update({'GIL_614':('minion',[('historical_copy_doll_bind',)]),'FP1_003':('none',[('historical_copy_ooze_schedule',)])})
DEATH_EFFECTS['GIL_614']=[('historical_copy_doll_destroy',)]
RULES.update({cid:('none',[]) for cid in ('BOT_566','GDB_448','VAC_503','TRL_092')})
RULES['TID_078']=('none',[('historical_copy_shattershambler',)])
RULES['LOOT_517']=('none',[('historical_copy_murmuring',)])
HORSEMEN=('NX2_034','NX2_034t','NX2_034t1','NX2_034t2')
RULES.update({
 'TTN_856':('none',[]),'TTN_900':('none',[]),
 'BT_735':('none',[]),'DRG_224':('none',[('summon','DRG_224t',2)]),
 'NX2_034':('none',[]),'OG_173':('none',[]),
 'ULD_705':('none',[('historical_copy_mogu',)]),
})
TOKEN_RULES.update({cid:('none',[]) for cid in ('TTN_900t','BT_735t','DRG_224t','DRG_224t2','OG_173a','ULD_705t')+HORSEMEN[1:]})
DEATH_EFFECTS.update({
 'TTN_900':[('summon','TTN_900t',1)],'BT_735':[('summon','BT_735t',1)],
 'NX2_034':[('historical_prime_shuffle',cid) for cid in HORSEMEN[1:]],
})
for cid in HORSEMEN[1:]:DEATH_EFFECTS[cid]=[('historical_copy_horsemen_win',)]
START_EFFECTS.update({'BT_735t':('owner',[('historical_copy_hatch','BT_735')]),'DRG_224t':('owner',[('historical_copy_hatch','DRG_224t2')])})
END_EFFECTS.update({'TTN_856':[('summon','TTN_900t',1)],'OG_173':[('historical_copy_ancient_merge',)],'ULD_705t':[('area_damage','enemies',20)]})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('TTN_900t','BT_735t','DRG_224t','DRG_224t2','OG_173a','ULD_705t'))|frozenset(HORSEMEN[1:])
RULES.update({
 'BAR_080':('minion',[('historical_copy_zone_swap','target','own','hand',())]),
 'BOT_433':('none',[]),'ETC_329':('none',[]),
 'MAW_004':('none',[('historical_copy_zone_swap','source','enemy','deck',())]),
 'EX1_006':('none',[]),
 'AV_331':('enemy_minion',[('historical_copy_najak_take',)]),
})
DEATH_EFFECTS.update({'BOT_433':[('historical_copy_zone_swap','source','own','deck',())],'ETC_329':[('historical_copy_zone_swap','source','own','hand',('LIFESTEAL',))],'AV_331':[('historical_copy_najak_return',)]})
START_EFFECTS['EX1_006']=('owner',[('historical_copy_zone_swap','source','own','hand',())])
RULES['DEEP_012']=('none',[('historical_copy_skulker_take',)])
DEATH_EFFECTS['DEEP_012']=[('historical_copy_skulker_return',)]
RULES.update({cid:('none',[]) for cid in ('TTN_926','TTN_940','ETC_375','WORK_025')})
RULES['TTN_927']=('historical_copy_treant',[('historical_copy_literal_target','TTN_903t4')])
TOKEN_RULES['TTN_903t4']=('none',[])
TOKEN_RULES['TTN_950t2']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('TTN_903t4','TTN_950t2'))
CHOICES={
 'TTN_926':[('Treant Growth','none',[('summon','TTN_950t2',3)]),('Ancient Growth','none',[('historical_copy_growth_treants',)])],
 'TTN_940':[('Duplicate hand','none',[('historical_copy_duplicate_hand',)]),('Copy battlefield','none',[('historical_copy_group','others',None,None)])],
 'ETC_375':[('Draw a Beast','none',[('filtered_draw',(('type','eq','MINION'),('tribe','eq','BEAST')),1)]),('Discover a Beast','none',[discover(pool(card_type='MINION',tribe='BEAST',classes='own_or_neutral'))])],
}
# Preserve every ordering of the three independent stat choices.
from itertools import product
CHOICES['WORK_025']=[(' / '.join('Attack' if bit==0 else 'Health' for bit in bits),'none',[('buff_self',2,0) if bit==0 else ('buff_self',0,2) for bit in bits]) for bits in product((0,1),repeat=3)]
RULES['ICC_047']=('none',[])
CHOICES['ICC_047']=[('Decay','none',[('historical_copy_fate_bind','decay')]),('Growth','none',[('historical_copy_fate_bind','growth')])]
TOKEN_RULES.update({'ICC_047t':('none',[]),'ICC_047t2':('none',[])})
for cid in ('ICC_047','ICC_047t','ICC_047t2'):DEATH_EFFECTS[cid]=[('historical_copy_fate_death',)]
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('ICC_047t','ICC_047t2'))
RULES.update({
 'RLK_950':('enemy_minion',[('historical_copy_zone_swap','target','own','deck',())]),
 'REV_247':('none',[('historical_copy_ooze_schedule',)]),
 'REV_246':('none',[('historical_copy_visitor',)]),
 'REV_020':('none',[('historical_copy_dinner',)]),
 'VAC_424':('none',[]),'VAC_426':('none',[]),
 'REV_314':('none',[('historical_copy_topior',)]),'RLK_541':('none',[]),
})
TRIGGERS['VAC_424']=('spell_cast',[random_cards(pool(card_type='MINION',minimum=2,maximum=2),destination='board',keyword='DIVINE_SHIELD')])
DEATH_EFFECTS['VAC_426']=[('historical_copy_eliza',)]
TOKEN_RULES['REV_314t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('REV_314t',))
RULES['TOY_823']=('none',[('historical_copy_seamstress',)])
RULES['WW_379']=('none',[('historical_copy_flint',)])
RULES.update({cid:('none',[]) for cid in ('EX1_560','REV_018','KAR_096','GIL_692','GIL_826')})
RULES['LOOT_538']=('none',[('historical_copy_temporus',)])
RULES['REV_014']=('none',[])
RULES.update({cid:('none',[('historical_copy_replay_spells',mode)]) for cid,mode in (('SW_044','jace'),('RLK_803','rommath'),('LOOT_216','lynessa'),('VAC_407','chatty'),('OG_134','yogg'))})
RULES.update({'EX1_335':('none',[]),'SW_112':('none',[('historical_copy_next_fire_bonus',)]),'SW_113':('none',[('historical_copy_antonidas',)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('CS2_029',))
RULES.update({'BT_481':('none',[('historical_copy_nethrandamus',)]),'REV_906':('none',[('historical_copy_denathrius',)]),'DRG_089':('none',[('historical_copy_dragonqueen',)]),'DRG_235':('none',[])})
DEATH_EFFECTS['DRG_235']=[('historical_copy_talritha',)]
BASIC_POWERS={name:'HERO_%02dbp'%(index+1) for index,name in enumerate(('WARRIOR','SHAMAN','ROGUE','PALADIN','HUNTER','DRUID','WARLOCK','MAGE','PRIEST','DEMONHUNTER','DEATHKNIGHT'))}
RULES.update({'AT_098':('none',[('historical_copy_spelleater',)]),'DRG_401':('none',[('historical_copy_wizard_swap',)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(BASIC_POWERS.values())
RULES.update({'VAC_506':('none',[('historical_copy_random_location',),('historical_copy_random_location',)]),'VAC_529':('historical_copy_location',[('historical_copy_location_clone',)]),'ETC_078':('none',[('historical_copy_microphones',)]),'ETC_425':('none',[('historical_copy_pozzik_bots',)])})
DEATH_EFFECTS['ETC_425']=[('historical_copy_pozzik_recruit',)]
TOKEN_RULES.update({cid:('none',[]) for cid in ('ETC_425t','ETC_078t','ETC_078t2')})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('ETC_425t','ETC_078t','ETC_078t2'))
RULES.update({'TOY_385':('none',[('historical_copy_zarimi',)]),'AT_128':('none',[])})
DEATH_EFFECTS['AT_128']=[('historical_batch_joust','MINION',False,(('historical_copy_gibberer',),))]
RULES.update({'REV_940':('none',[('historical_copy_draka',)]),'WW_392':('none',[('historical_copy_elise_badlands',)]),'TOY_882':('none',[('filtered_draw',(('type','eq','MINION'),('mechanic','eq','DIVINE_SHIELD')),1),('historical_copy_draw_aura',)])})
TOKEN_RULES['REV_940t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('REV_940t',))
RULES.update({'SW_075':('none',[]),'WW_010':('none',[('historical_copy_hollidae',)])})
DEATH_EFFECTS['SW_075']=[('historical_copy_boar_sword',)]
TOKEN_RULES.update({cid:('none',[]) for cid in ('SW_075t','WW_010t','WW_010hexfrog')})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('SW_075t','WW_010t','WW_010hexfrog'))
RULES.update({'ONY_030':('none',[('historical_copy_smuggler',)]),'TOY_960':('none',[('historical_copy_jepetto',)]),'TOY_524':('none',[('historical_draw_batch',(('type','eq','MINION'),('tribe','eq','DEMON')),'nemsy',(),'random')])})
DEATH_EFFECTS['TOY_524']=[('historical_copy_nemsy_swap',)]
RULES.update({'TSC_908':('none',[('historical_copy_finley_swap',)]),'SCH_159':('none',[('historical_copy_illucia',)]),'JAM_036':('none',[('historical_draw_batch',None,'magatha',(),'random')]*5)})
RULES['AV_143']=('none',[])
DEATH_EFFECTS['AV_143']=[('historical_copy_korrak',)]
RULES['DMF_733']=('none',[('add','DMF_058',1),('add','DMF_057',1)])
TOKEN_RULES.update({'DMF_058':('none',[('historical_copy_solar_eclipse',)]),'DMF_057':('minion',[('damage',3),('historical_copy_lunar_eclipse',)])})
TOKEN_RULES.update({'CORE_DMF_058':TOKEN_RULES['DMF_058'],'CORE_DMF_057':TOKEN_RULES['DMF_057']})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('DMF_058','DMF_057','CORE_DMF_058','CORE_DMF_057'))
RULES['LOE_079']=('none',[('insert_fixed','LOE_019t',1,'shuffle')])
TOKEN_RULES.update({'LOE_019t':('none',[('insert_fixed','LOE_019t2',1,'shuffle'),('draw',1)]),'LOE_019t2':('none',[('historical_copy_replace_zones','legendary')])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('LOE_019t','LOE_019t2'))
RULES['MIS_706']=('none',[('historical_copy_dust_junk',)])
DEATH_EFFECTS['MIS_706']=[('historical_copy_dust_junk',)]
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('GAME_005','WW_001t','EX1_014t','CS2_082'))
RULES.update({'RLK_225':('none',[('historical_copy_blightfang',)]),'REV_373':('none',[('historical_copy_darkvein',)]),'RLK_822':('none',[])})
DEATH_EFFECTS['RLK_822']=[('historical_copy_haunt',)]
TOKEN_RULES.update({'REV_373t':('none',[]),'RLK_822t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('RLK_118t3','REV_373t','RLK_822t'))
RULES.update({'RLK_591':('none',[]),'REV_960':('none',[('historical_copy_ashen',)])})
DEATH_EFFECTS['RLK_591']=[('historical_copy_bonelord',)]
LICH_KING_CARDS=tuple('ICC_314t'+str(n) for n in range(1,9))
RULES.update({'ICC_314':('none',[]),'ICC_854':('none',[])})
END_EFFECTS['ICC_314']=[('historical_copy_lich_gift',)]
DEATH_EFFECTS.update({'ICC_854':[('historical_copy_lich_gift',)],'ICC_314t1':[('stored_weapon_kills',)]})
TOKEN_RULES.update({'ICC_314t1':('none',[]),'ICC_314t2':('none',[('historical_copy_lich_army',)]),'ICC_314t3':('none',[('historical_copy_doom_pact',)]),'ICC_314t4':('none',[('historical_copy_death_grip',)]),'ICC_314t5':('character',[('historical_copy_death_coil',)]),'ICC_314t6':('minion',[('historical_copy_obliterate',)]),'ICC_314t7':('none',[('historical_copy_antimagic',)]),'ICC_314t8':('none',[('area_damage','enemies',3)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(LICH_KING_CARDS)
GELBIN_INVENTIONS=('Mekka1','Mekka2','Mekka3','Mekka4')
POWER_CHORDS=('PRO_001a','PRO_001b','PRO_001c')
HORDE_WARRIORS=('CS2_121','CS2_179','EX1_021','EX1_023','EX1_110','EX1_390')
RULES.update({'EX1_112':('none',[('historical_copy_gelbin_invention',)]),'PRO_001':('none',[('historical_copy_power_chord',False),('historical_copy_power_chord',True)])})
TOKEN_RULES.update({cid:('none',[]) for cid in GELBIN_INVENTIONS+('Mekka4t','PRO_001at')})
TOKEN_RULES.update({'PRO_001a':('none',[('historical_copy_murloc_chord',)]),'PRO_001b':('character',[('damage',4),('draw',1)]),'PRO_001c':('none',[('historical_copy_horde_chord',)])})
START_EFFECTS.update({'Mekka1':('owner',[('historical_copy_chicken_depart',),('draw',3)]),'Mekka4':('owner',[('historical_copy_poultryizer',)])})
END_EFFECTS.update({'Mekka2':[('historical_copy_repair_bot',)],'Mekka3':[('historical_copy_emboldener',)]})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(GELBIN_INVENTIONS+('Mekka4t','PRO_001at')+POWER_CHORDS+HORDE_WARRIORS)
RULES.update({'ULD_180':('none',[]),'VAC_406':('none',[])})
START_EFFECTS['ULD_180']=('owner',[('historical_copy_sunstruck',)])
DEATH_EFFECTS['VAC_406']=[('historical_copy_sleep_others',)]
EXCAVATE_COMMON=('WW_001t','WW_001t2','WW_001t3','WW_001t4','WW_001t18','DEEP_999t1')
EXCAVATE_RARE=('WW_001t5','WW_001t7','WW_001t8','WW_001t9','WW_001t16','DEEP_999t2')
EXCAVATE_EPIC=('WW_001t11','WW_001t12','WW_001t13','WW_001t14','WW_001t17','DEEP_999t3')
TOKEN_RULES.update({'WW_001t2':('character',[('heal',3),('draw',1)]),'WW_001t3':('none',[discover(pool(minimum=2,maximum=2,classes='own_or_neutral'),set_cost=0)]),'WW_001t4':('none',[]),'WW_001t18':('none',[('add','GAME_005',2)]),'DEEP_999t1':('friendly_minion',[('buff',2,2),('damage_random_enemy_minion',2)]),'WW_001t5':('minion',[('damage',3),('damage_enemy_hero',3)]),'WW_001t7':('enemy_minion',[('bounce',)]),'WW_001t8':('minion',[('historical_copy_excavate_glyph',)]),'WW_001t9':('none',[discover(pool(minimum=3,maximum=3,classes='own_or_neutral'),set_cost=0)]),'WW_001t16':('none',[]),'DEEP_999t2':('none',[]),'WW_001t11':('minion',[('set_target_stats',6,7)]),'WW_001t12':('none',[('area_damage','enemies',3)]),'WW_001t13':('none',[]),'WW_001t14':('none',[discover(pool(minimum=5,maximum=5,classes='own_or_neutral'),set_cost=0)]),'WW_001t17':('none',[]),'DEEP_999t3':('none',[('historical_treasure_pillar',)])})
DEATH_EFFECTS['WW_001t16']=[random_cards(pool(card_type='MINION',minimum=2,maximum=2),destination='board')]
END_EFFECTS['DEEP_999t2']=[('area_damage','enemies',2)]
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(EXCAVATE_COMMON+EXCAVATE_RARE+EXCAVATE_EPIC)|{'GAME_005'}
from . import historical_excavate
RULES.update(historical_excavate.RULES)
TOKEN_RULES.update(historical_excavate.TOKEN_RULES)
DEATH_EFFECTS.update(historical_excavate.DEATH_EFFECTS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_excavate.FIXED_TOKEN_IDS
MIMIRON_GADGETS=tuple('TTN_920t'+str(n) for n in (5,6,7,8,9,10))
RULES['VAC_957']=('historical_copy_pair',[('historical_copy_pair_offer',)])
TOKEN_RULES.update({'TTN_920t5':('none',[('historical_copy_coolant',)]),'TTN_920t6':('friendly_minion',[('buff',3,0),('temporary_keyword_target','STEALTH','next_start')]),'TTN_920t7':('historical_copy_pair',[('historical_copy_pair_offer',)]),'TTN_920t8':('minion',[('keyword','TAUNT'),('keyword','DIVINE_SHIELD')]),'TTN_920t9':('minion',[('bounce',)]),'TTN_920t10':('character',[('damage',3)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(MIMIRON_GADGETS)
RULES.update({'BAR_919':('none',[('historical_copy_neeru',)]),'GVG_111':('none',[]),'REV_514':('none',[('historical_copy_kel_skeletons',)])})
START_EFFECTS['GVG_111']=('owner',[('historical_copy_mimiron_head',)])
TOKEN_RULES.update({'BAR_919t':('none',[]),'GVG_111t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('BAR_919t','BAR_914t3','GVG_111t','REV_845'))
RULES.update({'REV_951':('none',[('historical_copy_countess',)]),'TSC_052':('none',[('learned_school_teacher',)]),'TOY_504':('none',[('historical_draw_hagatha',)])})
TOKEN_RULES.update({'REV_951t':('none',[discover(pool(card_type='MINION',rarity='LEGENDARY',classes='other'),set_cost=0)]),'TSC_052t':('none',[('learned_cast',)]),'TOY_504t':('none',[('learned_cast',)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('REV_951t','TSC_052t','TOY_504t'))
CTHUN_PIECES=('DMF_254t3','DMF_254t4','DMF_254t5','DMF_254t7')
RULES['DMF_254']=('none',[('missiles','enemies',30)])
TOKEN_RULES.update({
 'DMF_254t3':('none',[('missiles','enemies',7),('historical_copy_cthun_piece','DMF_254t3')]),
 'DMF_254t4':('none',[('area_damage','all_minions',3),('historical_copy_cthun_piece','DMF_254t4')]),
 'DMF_254t5':('none',[('summon','DMF_254t5t',1),('historical_copy_cthun_piece','DMF_254t5')]),
 'DMF_254t7':('minion',[('destroy',),('historical_copy_cthun_piece','DMF_254t7')]),
 'DMF_254t5t':('none',[]),
})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(CTHUN_PIECES+('DMF_254t5t',))
RULES.update({
 'DMF_188':('none',[('historical_copy_corrupted_recovery',)]),
 'ETC_121':('none',[('historical_copy_tribal_hand','copy')]),
 'ETC_350':('none',[('historical_copy_tribal_hand','buff')]),
 'NX2_023':('none',[('historical_copy_purator',)]),
 'DMF_002':('none',[('historical_copy_nzoth_deep',)]),
})
# Continuous damage consumers are implemented in the shared damage pipeline.
RULES.update({cid:('none',[]) for cid in ('AT_124','TRL_535','VAC_501','DMF_230')})
RULES['WORK_043']=('none',[('historical_copy_dungar',3,())])
# Frozen Zerg affiliation is separate from Constructed minion tribes.
ZERG_IDS=frozenset(('SC_002','SC_003','SC_003t','SC_006','SC_008','SC_009','SC_010','SC_012','SC_018','SC_019t','SC_022','SC_023'))
RULES.update({
 'SC_008':('none',[('historical_copy_hydralisk',)]),
 'SC_009':('none',[]),
 'SC_012':('none',[('historical_copy_roach',)]),
 'SC_018':('none',[('historical_copy_viper',)]),
 'VAC_421':('none',[('historical_copy_zookeeper',)]),
})
TRIGGERS['SC_009']=(('historical_event','owner_minion_attacked'),[('historical_copy_lurker_shot',)])
TOKEN_RULES['VAC_421t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'VAC_421t'}
ZERG_MINION_POOL=('SC_002','SC_003','SC_008','SC_009','SC_010','SC_012','SC_018','SC_022','SC_023')
RULES.update({cid:('none',[]) for cid in ('SC_002','SC_003','SC_022')})
DEATH_EFFECTS['SC_002']=[('historical_copy_infestor',)]
END_EFFECTS['SC_003']=[('add','SC_003t',1)]
TOKEN_RULES.update({'SC_003t':('none',[]),'SC_006':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(ZERG_MINION_POOL)|{'SC_003t','SC_006'}
HISTORICAL_POWER_OPERATIONS={
 'EX1_625t':(('damage',2),),'EX1_625t2':(('damage',3),),
 'BRM_027p':(('damage_random_enemy',8),),
 'GDB_846hp':(('discover_deck',),),'TTN_717t':(('historical_copy_algalon_vision',),),
}
RULES.update({'SW_448':('none',[]),'BRM_027':('none',[]),
 'GDB_846':('none',[('historical_copy_replace_power','GDB_846hp')]),
 'TTN_717':('none',[('historical_copy_replace_power','TTN_717t')])})
DEATH_EFFECTS['BRM_027']=[('historical_copy_majordomo',)]
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(HISTORICAL_POWER_OPERATIONS)|{'BRM_027h','TTN_717t2','TTN_717t3'}
# Concrete Discover, power draw and damage consumers live in shared handlers.
RULES.update({cid:('none',[]) for cid in ('GDB_841','AT_027','TRL_315')})
SPIRIT_IDS=SPIRIT_IDS|{'TRL_319'}
RULES.update({'TRL_319':('none',[]),'REV_238':('none',[('historical_copy_theotar',)]),'REV_511':('none',[('historical_copy_bibliomite',)])})
RULES.update({
 'DED_525':('none',[('historical_copy_manual_shots','goliath',5,())]),
 'TOY_101':('none',[('historical_copy_manual_shots','huntress',3,())]),
 'WW_399':('none',[]),
})
DEATH_EFFECTS['WW_399']=[('historical_copy_high_noon',)]
CONCOCTIONS=('RLK_570t1','RLK_570t2','RLK_570t3','RLK_570t4','RLK_570t5')
CONCOCTION_PARTS=(
 (random_cards(pool(card_type='MINION',minimum=3,maximum=3),destination='board'),),
 (('destroy_random_enemy',),),
 (('damage',3),),
 (random_cards(pool(classes='other'),cost_delta=-3),),
 (('draw',2),),
)
# Explicit frozen identities and printed resolution order for every unordered pair.
CONCOCTION_MIXES={
 (0,0):('RLK_570t1t4',(0,0)),(0,1):('RLK_570t1t2',(0,1)),
 (0,2):('RLK_570t1t3',(2,0)),(0,3):('RLK_570t1t1',(0,3)),
 (0,4):('RLK_570tt1',(4,0)),(1,1):('RLK_570t2t2',(1,1)),
 (1,2):('RLK_570t2t1',(2,1)),(1,3):('RLK_570t4t1',(3,1)),
 (1,4):('RLK_570tt4',(4,1)),(2,2):('RLK_570t3t',(2,2)),
 (2,3):('RLK_570t4t2',(2,3)),(2,4):('RLK_570tt2',(2,4)),
 (3,3):('RLK_570t4t3',(3,3)),(3,4):('RLK_570tt3',(4,3)),
 (4,4):('RLK_570tt5',(4,4)),
}
for index,cid in enumerate(CONCOCTIONS):TOKEN_RULES[cid]=('character' if index==2 else 'none',list(CONCOCTION_PARTS[index]))
for cid,parts in CONCOCTION_MIXES.values():
 TOKEN_RULES[cid]=('character' if 2 in parts else 'none',[operation for index in parts for operation in CONCOCTION_PARTS[index]])
CONCOCTION_IDS=frozenset(CONCOCTIONS)|frozenset(cid for cid,parts in CONCOCTION_MIXES.values())
RULES.update({'RLK_568':('none',[('historical_copy_concoction',)]),'RLK_570':('none',[('historical_copy_concoction_free',)]),'RLK_571':('none',[]),'RLK_572':('none',[])})
END_EFFECTS['RLK_571']=[('historical_copy_concoction',)]
TRIGGERS['RLK_572']=(('historical_event','any_death'),[('historical_copy_concoction',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|CONCOCTION_IDS
RULES.update({'VAC_945':('none',[('historical_copy_vona',)]),'WW_824':('none',[('historical_copy_rheastrasza',)])})
TOKEN_RULES.update({'VAC_945t':('none',[]),'WW_824t':('none',[])})
DEATH_EFFECTS['VAC_945t']=[('historical_copy_ouroboros',)]
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'VAC_945t','WW_824t'}
RULES.update({
 'VAC_321':('none',[('on_draw_shuffle','VAC_321t',5,0)]),
 'VAC_933':('none',[('on_draw_shuffle','VAC_933t',6,0)]),
 'GDB_234':('none',[('cast_fixed_spell','GDB_234t','random')]),
})
END_EFFECTS['VAC_321']=[('historical_copy_upgrade_eruptions',)]
TOKEN_RULES.update({
 'VAC_321t':('none',[('historical_drawn_eruption',)]),
 'VAC_933t':('none',[('summon','VAC_926t',1)]),
 'VAC_926t':('none',[]),
 'GDB_234t':('none',[('historical_copy_spore',)]),
})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'VAC_321t','VAC_933t','VAC_926t','GDB_234t'}
ANCIENT_RELICS=('TSC_641ta','TSC_641tb','TSC_641tc','TSC_641td')
RULES['TSC_641']=('none',[('historical_copy_azshara',)])
TOKEN_RULES.update({
 'TSC_641ta':('none',[]),
 'TSC_641tb':('none',[random_cards(pool(card_type='MINION',mechanic='COLOSSAL'),set_cost=1)]),
 'TSC_641tc':('none',[]),
 'TSC_641td':('none',[random_cards(pool(card_type='SPELL'),5,destination='deck',set_cost=1),('draw',2)]),
})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(ANCIENT_RELICS)
RULES['WW_359']=('none',[('historical_copy_sheriff',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'WW_359t'}
TOKEN_RULES['WW_359t']=('none',[])
RULES['TSC_067']=('none',[('historical_copy_faelin',)])
RULES['VAC_444']=('none',[('historical_copy_overplanner',)])
# Keyword-only body: Rush, Taunt and Stealth are native frozen mechanics.
RULES['GDB_343']=('none',[])
RULES['WW_900']=('none',[('historical_copy_horseshoe',)])
RULES['KAR_097']=('none',[('equip','KAR_097t')])
# Keeneye's pre-damage operation is implemented in CombatResolver.resolve.
RULES['RLK_827']=('none',[])
TOKEN_RULES['KAR_097t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'KAR_097t'}
# Explicit Drink family and physical remaining-use forms from the pinned snapshot.
DRINK_FORMS=(('VAC_323','VAC_323t','VAC_323t2'),('VAC_338','VAC_338t','VAC_338t2'),('VAC_404','VAC_404t1','VAC_404t2'),('VAC_520','VAC_520t','VAC_520t2'),('VAC_916','VAC_916t2','VAC_916t3'),('VAC_951','VAC_951t','VAC_951t2'))
DRINKS=tuple(forms[0] for forms in DRINK_FORMS)
DRINK_RECIPES=(('none',(('area_damage','enemies',1),)),('historical_copy_hand_minion',(('historical_copy_cup_muscle',),)),('minion',(('damage',2),('damage_own_hero',2))),('none',(('missiles','enemy_minions',2),)),('character',(('historical_copy_divine_brew',),)),('minion',(('damage',3),)))
for forms,(mode,operations) in zip(DRINK_FORMS,DRINK_RECIPES):
 for index,cid in enumerate(forms):
  TOKEN_RULES[cid]=(mode,list(operations)+([('add',forms[index+1],1)] if index<2 else []))
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(cid for forms in DRINK_FORMS for cid in forms)
RULES['VAC_461']=('none',[])
DEATH_EFFECTS['VAC_461']=[('historical_copy_drink',)]
RULES['RLK_816']=('none',[('add','RLK_816t3',1)])
# The replacement occupies its hand slot before the generated choice resolves.
TOKEN_RULES['RLK_816t3']=('none',[('add','RLK_816t3',1),discover(pool(card_type='SPELL',school='SHADOW',classes='own_or_neutral'))])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'RLK_816t3'}
RULES['WORK_006']=('none',[('historical_copy_robocaller',)])
RULES['DMF_074']=('none',[('historical_copy_silas',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'DMF_074a','DMF_074b'}
HELBRIM_POISONS=('CS2_074','ICC_221','YOP_015','BAR_318','BAR_321')
RULES['BAR_324']=('none',[('historical_copy_poison',)])
DEATH_EFFECTS['BAR_324']=[('historical_copy_poison',)]
TOKEN_RULES.update({
 'CS2_074':('weapon_required',[('weapon_buff',2,0)]),
 'ICC_221':('weapon_required',[('historical_copy_weapon_poison','leeching')]),
 'YOP_015':('minion',[('buff',2,0)]),
 'YOP_015t':('minion',[('buff',2,0),('weapon_buff',2,0)]),
 'BAR_318':('weapon_required',[('historical_copy_weapon_poison','silverleaf')]),
 'BAR_321':('weapon_required',[('weapon_buff',1,0),('historical_copy_weapon_poison','paralytic')]),
})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(HELBRIM_POISONS)|{'YOP_015t'}
PROTOSS_SPELLS=frozenset(('SC_750','SC_753','SC_755','SC_757','SC_759','SC_760','SC_761'))
PROTOSS_COLLECTIBLE_MINIONS=('SC_752','SC_756','SC_758','SC_762','SC_763','SC_764','SC_765','SC_783')
PROTOSS_MINIONS=frozenset(PROTOSS_COLLECTIBLE_MINIONS+('SC_751t','SC_756t','SC_671t1'))
RULES.update({'SC_758':('none',[('historical_copy_colossus',)]),'SC_762':('none',[('historical_copy_mothership',),('historical_copy_mothership',)]),'SC_764':('none',[])})
DEATH_EFFECTS.update({'SC_762':[('historical_copy_mothership',),('historical_copy_mothership',)],'SC_764':[('historical_copy_sentry',)]})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(PROTOSS_COLLECTIBLE_MINIONS)
TEMPLARS=frozenset(('SC_752','SC_765'))
RULES.update({'SC_752':('enemy_minion',[('destroy',)]),'SC_765':('none',[('area_damage','enemies',2)])})
TRIGGERS.update({cid:(('historical_copy_event','templar_play'),[('historical_copy_templar_merge',)]) for cid in TEMPLARS})
TOKEN_RULES['SC_671t1']=('none',[])
END_EFFECTS['SC_671t1']=[('damage_enemy_hero',8),('area_damage','enemy_minions',2)]
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'SC_671t1'}
PROTOSS_CARDS=PROTOSS_MINIONS|PROTOSS_SPELLS|{'SC_751','SC_754'}
TOKEN_RULES.update({
 'SC_750':('none',[('historical_copy_protoss_draw','card',False),('historical_copy_protoss_draw','card',False),('summon','SC_751t',1)]),
 'SC_753':('character',[('historical_copy_photon',)]),
 'SC_755':('none',[('historical_copy_protoss_next','card',2,True)]),
 'SC_757':('historical_copy_protoss_target',[('historical_copy_hallucination',)]),
 'SC_759':('none',[('armor',6),('historical_copy_protoss_next','spell',2,False)]),
 'SC_760':('minion',[('damage',5),('historical_copy_protoss_spell',)]),
 'SC_761':('none',[('historical_copy_protoss_draw','minion',True)]),
 'SC_751':('none',[]),
 'SC_751t':('none',[]),
})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|PROTOSS_SPELLS|{'SC_751','SC_751t'}
TOKEN_RULES['SC_754']=('none',[('summon','SC_751t',1),('summon','SC_751t',1),('historical_copy_sentry',),('historical_copy_sentry',)])
HISTORICAL_POWER_OPERATIONS['SC_754p']=(('historical_copy_twin_blades',),)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'SC_754','SC_754p'}
RULES['DED_514']=('none',[('historical_copy_copycat_wait',)])
RULES['WW_401']=('none',[('historical_copy_kurtrus',)])
RULES.update({'DRG_090':('none',[('historical_copy_history_replay','murozond')]),'VAC_415':('none',[('historical_copy_history_replay','sasquawk')]),'VAC_333':('none',[('historical_copy_history_replay','conman')]),'VAC_961':('none',[('historical_copy_history_replay','parrot')])})
RULES.update({'GIL_598':('none',[('historical_copy_history_replay','tess')]),'VAC_519':('none',[('historical_copy_vistah_start',)])})
TOKEN_RULES['VAC_519t3']=('none',[('historical_copy_vistah_start',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'VAC_519t3'}
RULES.update({'DED_509':('none',[('historical_copy_repeat_battlecry','last')]),'SW_115':('none',[])})
TRIGGERS['SW_115']=(('historical_copy_event','battlecry_play'),[('historical_copy_repeat_battlecry','first_turn')])
RULES['GIL_820']=('none',[('historical_copy_shudderwock',)])
ONYXIA_WHELPS=frozenset(('BOT_066','BRM_004','BRM_004t','BRM_022t','CATA_132t','CATA_210t','CATA_484','CATA_556','DRG_054','ds1_whelptoken','EX1_116t','FIR_927','GIL_190t','KAR_010a','ONY_001t','REV_314t','RLK_915','TIME_045','TIME_056','TOT_303t','TOY_380t2','TOY_386','TTN_718','VAC_511t','WW_816t','WW_819'))
# Blindeye's phase belongs to the physical entity, including battlefield copies.
RULES['ONY_004']=('none',[('historical_copy_onyxia_whelp',side) for side in (0,1,0,1,0,1)])
TOKEN_RULES['ONY_001t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'ONY_001t'}
RULES['WW_402']=('none',[])
TRIGGERS['WW_402']=(('historical_copy_event','sharpshooter'),[('historical_copy_sharpshooter',)])
RULES['SCH_607']=('none',[])
CHOICES['SCH_607']=[('Rile the Herd','none',[('historical_copy_beast_deck_buff',)]),('Transfiguration','friendly_beast',[('historical_copy_transform_target',None,None)])]
RULES['TTN_490']=('none',[('historical_copy_disciple',False)])
TOKEN_RULES['TTN_490t']=('none',[('historical_copy_disciple',True)])
TOKEN_RULES['TTN_960t6']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'TTN_490t','TTN_960t6'}
YREL_LIBRAMS=('BT_011','BT_024','BT_025')
RULES['GDB_141']=('none',[])
DEATH_EFFECTS['GDB_141']=[('historical_copy_yrel_librams',)]
TOKEN_RULES.update({'BT_011':('none',[('equip','BT_011t'),('historical_copy_justice_health',)]),'BT_025':('minion',[('buff',1,1),('grant_death_target',(('add','BT_025',1),))]),'BT_011t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(YREL_LIBRAMS)|{'BT_011t'}
KABAL_POTIONS=('CFM_021','CFM_065','CFM_094','CFM_603','CFM_604','CFM_608','CFM_611','CFM_620','CFM_661','CFM_662')
RULES['CFM_619']=('none',[('historical_copy_kabal_potion',)])
TOKEN_RULES.update({
 'CFM_603':('historical_copy_madness_target',[('historical_copy_madness',)]),
 'CFM_604':('friendly_character',[('heal',12),('draw',1)]),
 'CFM_608':('minion',[('destroy',),('destroy_crystals',1)]),
 'CFM_611':('minion',[('historical_copy_bloodfury',)]),
 'CFM_620':('none',[('secret','CFM_620')]),
 'CFM_661':('none',[('historic_temporary_attack','enemy',-3,'end')]),
 'CFM_662':('none',[('historical_copy_dragonfire',)]),
})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(KABAL_POTIONS)|{'CS2_tk1'}
CHOICES['SW_079']=[('Westfall','none',[('historical_sleep_dungar_depart',1)]),('Ironforge','none',[('historical_sleep_dungar_depart',3)]),('Eastern Plaguelands','none',[('historical_sleep_dungar_depart',5)])]
RULES['TOY_501']=('none',[('historical_copy_shudderblock',)])
TOKEN_RULES['TOY_501t']=('none',[('historical_copy_shudderblock',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'TOY_501t'}
RULES.update({'LEG_CS3_001':('none',[]),'REV_377':('none',[])})
DEATH_EFFECTS['LEG_CS3_001']=[('historical_copy_aegwynn_death',)]
TRIGGERS['REV_377']=(('historical_copy_event','courier'),[('historical_copy_courier',)])
RULES.update({'REV_916':('none',[]),'SCH_351':('none',[('historical_copy_jandice',)])})
TRIGGERS['REV_916']=(('historical_event','any_death'),[('historical_copy_painting',)])
RULES.update({'SW_436':('none',[]),'ETC_386':('none',[('historical_copy_zok',)]),'VAC_920':('none',[])})
TRIGGERS.update({'SW_436':(('historical_copy_event','hero_attack_gain'),[('buff_self',2,0)]),'VAC_920':(('historical_copy_event','self_attack_gain'),[('historical_copy_service_ace',)])})
TOKEN_RULES['ETC_386t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'ETC_386t'}
RULES.update({'TSC_032':('none',[('historical_copy_okani_offer',)]),'MIS_916':('none',[('historical_copy_gamer',)])})
START_EFFECTS['MIS_916']=('every',[('historical_copy_gamer_turn',)])
RULES['REV_370']=('enemy_minion',[('historical_copy_party_crasher',)])
RULES.update({cid:('none',[]) for cid in ('TRL_085','TSC_074','RLK_677')})
TRIGGERS['TSC_074']=(('historical_copy_event','kotori'),[('historical_copy_kotori',)])
RULES.update({'VAC_935':('none',[('historical_copy_pack_suitcase',)]),'VAC_420':('none',[('historical_copy_fortunes',)]),'WW_337':('none',[('historical_copy_permanent_mirage',)])})
TOKEN_RULES.update({'VAC_935t':('none',[('historical_copy_unpack_suitcase',)]),'VAC_935t2':('none',[('historical_copy_unpack_suitcase',)]),'VAC_420t':('historical_copy_blank_mirror',[('historical_copy_blank_mirror',)]),'WW_337t':('historical_copy_blank_mirror',[('historical_copy_blank_mirror',)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'VAC_935t','VAC_935t2','VAC_420t','WW_337t'}
RULES['RLK_919']=('none',[('historical_copy_future_board',)])
RULES.update({cid:('none',[]) for cid in ('BOT_559','DAL_719')})
TRIGGERS.update({'BOT_559':(('historical_copy_event','shuffle_extra'),[('historical_copy_shuffle_extra',)]),'DAL_719':(('historical_copy_event','shuffle_hand'),[('historical_copy_shuffle_hand',)])})
RULES.update({'TRL_096':('none',[('historical_copy_griftah',)]),'UNG_035':('none',[('historical_copy_guess','original')]),'DRG_306':('none',[('historical_copy_guess','hand')])})
BOTFACE_MINIS=('MIS_025t', 'TOY_307t', 'TOY_312t', 'TOY_340t1', 'TOY_341t', 'TOY_351t', 'TOY_375t', 'TOY_380t', 'TOY_501t', 'TOY_513t', 'TOY_521t1', 'TOY_601t', 'TOY_604t', 'TOY_652t', 'TOY_801t', 'TOY_811t', 'TOY_813t', 'TOY_828t', 'TOY_915t')
RULES.update({'TOY_906':('none',[]),'TOY_830':('none',[('historical_copy_stitch',)]),'TOY_604':('none',[])})
TRIGGERS['TOY_906']=('damaged_self',[('historical_copy_botface',)])
TOKEN_RULES['TOY_604t']=('none',[])
DEATH_EFFECTS.update({cid:[('historical_copy_wrench',)] for cid in ('TOY_604','TOY_604t')})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(BOTFACE_MINIS)
from .generation_cards import PoolRequest
CHOOSE_SPELL_BRANCHES={'CORE_AT_037': ('AT_037a', 'AT_037b'), 'CORE_EX1_154': ('EX1_154a', 'EX1_154b'), 'CORE_EX1_160': ('EX1_160b', 'EX1_160a'), 'CORE_OG_047': ('OG_047a', 'OG_047b'), 'CORE_TSC_650': ('TSC_650a', 'TSC_650d'), 'EDR_233': ('EDR_233a', 'EDR_233b'), 'EDR_570': ('EDR_570A', 'EDR_570B'), 'EDR_263': ('EDR_263a', 'EDR_263b'), 'EDR_490': ('EDR_490a', 'EDR_490b'), 'EDR_813': ('EDR_813a', 'EDR_813b'), 'EDR_843': ('EDR_843a', 'EDR_843b'), 'EDR_820': ('EDR_820a', 'EDR_820b'), 'Core_LOE_115': ('LOE_115a', 'LOE_115b'), 'EDR_872': ('EDR_872A', 'EDR_872B'), 'JAIL_201': ('JAIL_201a', 'JAIL_201b'), 'EDR_463': ('EDR_463a', 'EDR_463b')}
TOKEN_RULES.update({'AT_037a': ('character', [('damage', 2)]), 'AT_037b': ('none', [('summon', 'AT_037t', 2)]), 'EX1_154a': ('minion', [('damage', 3)]), 'EX1_154b': ('minion', [('damage', 1), ('draw', 1)]), 'EX1_160b': ('none', [('board_buff', 1, 1)]), 'EX1_160a': ('none', [('summon', 'EX1_160t', 1)]), 'OG_047a': ('none', [('hero_attack', 4)]), 'OG_047b': ('none', [('armor', 8)]), 'TSC_650a': ('none', [('summon', 'TSC_650t', 1)]), 'TSC_650d': ('none', [('summon', 'TSC_650t4', 6)]), 'EDR_233a': ('none', [('summon', 'EX1_tk11', 3)]), 'EDR_233b': ('none', [('summon', 'EDR_233t2', 2)]), 'EDR_570A': ('none', [('area_damage', 'all_minions', 1)]), 'EDR_570B': ('damaged_minion', [('buff', 2, 2)]), 'EDR_263a': ('none', [('damage_enemy_hero', 4)]), 'EDR_263b': ('none', [('summon', 'EDR_850pe', 2)]), 'EDR_490a': ('none', [('summon', 'EDR_490t', 2)]), 'EDR_490b': ('enemy_minion', [('destroy',)]), 'EDR_813a': ('none', [('summon', 'EDR_813at', 2)]), 'EDR_813b': ('minion', [('corpse_target_damage', 2, 4)]), 'EDR_843a': ('none', [('filtered_draw', (('type', 'eq', 'SPELL'),), 1)]), 'EDR_843b': ('none', [('filtered_draw', (('type', 'eq', 'MINION'),), 1)]), 'EDR_820a': ('none', [('summon_fixed_random', ('EDR_840t', 'EDR_840t1', 'EDR_840t2')), ('summon_fixed_random', ('EDR_840t', 'EDR_840t1', 'EDR_840t2'))]), 'EDR_820b': ('none', [('area_damage', 'all_minions', 2)]), 'LOE_115a': ('none', [('generate_discover', PoolRequest(era='', rune='', card_type='MINION', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='own_or_neutral', attack_minimum=None, attack_maximum=None), 'hand', ())]), 'LOE_115b': ('none', [('generate_discover', PoolRequest(era='', rune='', card_type='SPELL', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='own_or_neutral', attack_minimum=None, attack_maximum=None), 'hand', ())]), 'EDR_872A': ('none', [('generate_discover', PoolRequest(era='', rune='', card_type='SPELL', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='MAGE', attack_minimum=None, attack_maximum=None), 'hand', ())]), 'EDR_872B': ('none', [('generate_discover', PoolRequest(era='', rune='', card_type='SPELL', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='DRUID', attack_minimum=None, attack_maximum=None), 'hand', ())]), 'JAIL_201a': ('none', [('hero_attack', 2)]), 'JAIL_201b': ('none', [('generate_random', PoolRequest(era='', rune='', card_type='', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='DRUID', attack_minimum=None, attack_maximum=None), 1, 'hand', ())]), 'EDR_463a': ('small_attack_minion', [('destroy',)]), 'EDR_463b': ('none', [('generate_random', PoolRequest(era='', rune='', card_type='MINION', tribe='', school='', minimum=2, maximum=2, rarity='', mechanic='', excluded_mechanic='COLOSSAL', family='', minimum_tribes=0, classes='any', attack_minimum=None, attack_maximum=None), 1, 'board', ())])})
from .historical_choose_splits import SPLIT_BRANCHES
CHOOSE_SPELL_BRANCHES.update(SPLIT_BRANCHES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{token for tokens in CHOOSE_SPELL_BRANCHES.values() for token in tokens}
RULES.update({'DAL_732':('none',[]),'DED_003':('none',[('historical_copy_jerry',)]),'AV_210':('historical_copy_pathmaker_target',[('historical_copy_pathmaker',)])})
TRIGGERS['DAL_732']=(('historical_copy_event','choose_spell'),[('historical_copy_stalladris',)])
RULES.update({'WW_372':('none',[('on_draw_shuffle','WW_372t',3,1)]),'YOD_027':('none',[('historical_copy_chaos_gaze',)]),'TOY_511':('none',[])})
TOKEN_RULES['WW_372t']=('none',[('historical_copy_tnt_zone',zone) for zone in ('hand','deck','board')])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'WW_372t'}
TRIGGERS['TOY_511']=(('summon','friendly','PIRATE'),[('historical_copy_goldbeard',)])
RULES.update({'TTN_330':('none',[]),'TTN_727':('none',[]),'AV_336':('none',[('historical_copy_ichman_recruit',)])})
TRIGGERS.update({'TTN_330':(('historical_event','source_before_minion_attack'),[('historical_copy_kologarn_grab',)]),'TTN_727':('attacking_self',[('historical_copy_thorignir',)])})
DEATH_EFFECTS['TTN_330']=[('historical_copy_kologarn_return',)]
TOKEN_RULES['TTN_727t']=('none',[])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'TTN_727t'}
from . import historical_starships
RULES.update({cid:('none',[]) for cid in ('GDB_100','GDB_101','GDB_105','GDB_109')})
DEATH_EFFECTS['GDB_100']=[('armor',4)]
RULES.update({'GDB_130':('none',[('historical_ship_welder',)]),'GDB_340':('historical_ship_enemy',[('destroy',)]),'GDB_856':('none',[('historical_ship_othaar',)]),'GDB_876':('none',[('historical_ship_shipwright',)]),'SC_401':('none',[('historical_ship_discount',)])})
TOKEN_RULES.update({cid:('none',[('historical_ship_definition_required',)]) for cid in historical_starships.STARSHIPS})
TOKEN_RULES[historical_starships.CONSTRUCTION]=('historical_copy_blank_mirror',[('historical_ship_definition_required',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_starships.TOKEN_IDS
RULES.update({cid:('none',[]) for cid in ('GDB_103','GDB_104','GDB_106','GDB_107','GDB_108','GDB_110','GDB_111','GDB_112','GDB_466')})
DEATH_EFFECTS.update({'GDB_111':[('historical_ship_biopod',)],'GDB_112':[('historical_ship_spire',)]})
RULES.update({'SC_405':('none',list(historical_starships.BATTLECRIES['SC_405'])),'SC_406':('none',list(historical_starships.BATTLECRIES['SC_406'])),'SC_409':('none',list(historical_starships.BATTLECRIES['SC_409'])),'SC_408':('none',[('historical_ship_ghost',)]),'GDB_120':('none',[('historical_ship_exodar',)])})
TOKEN_RULES.update({cid:('none',[]) for cid in ('SC_403a','SC_403b','SC_403c','SC_403d','SC_403f','SC_403t')})
TOKEN_RULES.update({cid:('historical_copy_blank_mirror',[('historical_ship_protocol_unbound',)]) for cid in historical_starships.PROTOCOLS})
for cid in historical_starships.STARSHIPS:TOKEN_RULES[cid]=('none',[('historical_ship_definition_required',),('historical_ship_battlecry',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'SC_403a','SC_403b','SC_403c','SC_403d','SC_403f','SC_403t'}|set(historical_starships.PROTOCOLS)
RULES.update({'SC_412':('none',[]),'SC_413':('none',[('historical_ship_tank',False)]),'SC_414':('character',[('historical_ship_thor',False)])})
TOKEN_RULES.update({'SC_412t':('none',[]),'SC_413t':('none',[('historical_ship_tank',True)]),'SC_414t':('character',[('historical_ship_thor',True)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'SC_412t','SC_413t','SC_414t'}
EPOCH_RULES={'WON_041t':('none',[random_cards(pool(card_type='MINION',rarity='LEGENDARY'),2)]),'WON_041t2':('none',[('board_buff',2,2)]),'WON_041t3':('none',[random_cards(pool(card_type='SPELL'),2)]),'WON_041t4':('none',[('area_damage','enemies',2)])}
FUTURE_LOCATIONS=('WON_053t','WON_053t2','WON_053t3','WON_053t4','WON_053t5','WON_053t6','WON_053t7')
TIME_LOCATION_EFFECTS={'WON_053t':(('historical_copy_lordaeron',),),'WON_053t2':(random_cards(pool(card_type='MINION',minimum=3,maximum=3),destination='board',keyword='CHARGE'),),'WON_053t3':(('historical_copy_xenedar',),),'WON_053t4':(('historical_copy_nighthold',),),'WON_053t5':(random_cards(pool(card_type='MINION',tribe='DRAGON'),2,attack=2,health=2),),'WON_053t6':(('historical_copy_korune',),),'WON_053t7':(('historical_copy_temple_earth',),)}
RULES.update({'WON_041':('none',[('historical_copy_epoch',)]),'WON_053':('none',[('historical_copy_future_location',)]),'TOY_809':('none',[('historical_copy_cardboard',)])})
TOKEN_RULES.update(EPOCH_RULES)
TOKEN_RULES.update({cid:('none',[]) for cid in FUTURE_LOCATIONS})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(EPOCH_RULES)|set(FUTURE_LOCATIONS)
RULES.update({'VAC_955':('none',[('add','VAC_955t',1)]),'GDB_143':('none',[])})
TOKEN_RULES['VAC_955t']=('none',[('historical_copy_cheese',)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'VAC_955t'}
RULES['SC_013']=('none',[('historical_copy_grunty',)])
BOB_ACTIONS=('BG31_BOBt','BG31_BOBt2','BG31_BOBt3','BG31_BOBt4')
PLUNDER_ACTIONS=('TSC_934t','TSC_934t2','TSC_934t3')
RULES.update({'BG31_BOB':('none',[('historical_copy_bob_offer',)]),'TSC_934':('none',[('historical_copy_plunder_offer',)])})
TOKEN_RULES.update({
 'BG31_BOBt':('none',[('historic_board_freeze','enemy')]),
 'BG31_BOBt2':('enemy_minion',[('historical_copy_target_delivery','hand',1,None,None,None,False),('historical_copy_bob_coins',)]),
 'BG31_BOBt3':('none',[discover(pool(card_type='MINION',minimum=3,maximum=3)),('refresh_mana',3)]),
 'BG31_BOBt4':('none',[('historical_copy_bob_triple',)]),
 'TSC_934t':('none',[('historical_copy_plunder_take','deck',5)]),
 'TSC_934t2':('none',[('historical_copy_plunder_take','hand',2)]),
 'TSC_934t3':('none',[('historical_copy_plunder_ship',)]),
})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(BOB_ACTIONS)|set(PLUNDER_ACTIONS)|{'GAME_005'}
AMULET_PAIRS={good:good[:-1] for good in ('VAC_959t01t','VAC_959t05t','VAC_959t06t','VAC_959t07t','VAC_959t08t','VAC_959t09t','VAC_959t10t')}
RULES['VAC_959']=('none',[('historical_copy_amulet_vendor',)])
TOKEN_RULES.update({
 'VAC_959t01t':('historical_copy_passions_target',[('historical_copy_passions',False)]),
 'VAC_959t01':('historical_copy_passions_target',[('historical_copy_passions',True)]),
 'VAC_959t05t':('none',[random_cards(pool(rarity='LEGENDARY'),3)]),
 'VAC_959t05':('none',[('historical_copy_phony_tracking',)]),
 'VAC_959t06t':('none',[('historical_copy_amulet_critter',False)]),
 'VAC_959t06':('none',[('historical_copy_amulet_critter',True)]),
 'VAC_959t07t':('character',[('damage',6)]),'VAC_959t07':('minion',[('damage',6)]),
 'VAC_959t08t':('none',[('heal_own_hero',12)]),'VAC_959t08':('none',[('heal_own_hero',12),('damage_own_hero',6)]),
 'VAC_959t09t':('none',[('draw',3)]),'VAC_959t09':('none',[('historical_copy_phony_mobility',)]),
 'VAC_959t10t':('none',[('historical_copy_amulet_discount',False)]),'VAC_959t10':('none',[('historical_copy_amulet_discount',True)]),
})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(AMULET_PAIRS)|set(AMULET_PAIRS.values())
STAR_IDS=('GDB_118t','GDB_118t2')
RULES['GDB_118']=('none',[('historical_copy_xortoth',)])
TOKEN_RULES.update({cid:('none',[('historical_copy_star_unplayable',)]) for cid in STAR_IDS})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(STAR_IDS)
RULES['REV_925']=('none',[]) # Executable transformation replacement hooks.
RULES.update({'REV_316':('none',[]),'VAC_923':('none',[])})
TRIGGERS.update({'REV_316':(('historical_event','source_attacked'),[('historical_copy_remornia_equip',)]),'VAC_923':(('historical_event','source_attacked'),[('historical_copy_sanc_location',)])})
TOKEN_RULES.update({'REV_316t':('none',[]),'VAC_923t':('none',[])})
TIME_LOCATION_EFFECTS['VAC_923t']=(('historical_copy_sanc_activate',),)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|{'REV_316t','VAC_923t'}
from . import historical_potion_crafting
RULES.update(historical_potion_crafting.ROOT_RULES)
TOKEN_RULES.update(historical_potion_crafting.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(historical_potion_crafting.TOKEN_RULES)
from . import historical_golem_crafting
RULES.update(historical_golem_crafting.ROOT_RULES)
TOKEN_RULES.update(historical_golem_crafting.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(historical_golem_crafting.TOKEN_RULES)
# Jaxon's passive is consumed by Systems._trade, not a Battlecry.
RULES['SW_045']=('none',[])
from . import historical_horror_crafting
RULES.update(historical_horror_crafting.ROOT_RULES)
TOKEN_RULES.update(historical_horror_crafting.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(historical_horror_crafting.TOKEN_RULES)
from . import historical_rock_duel
RULES.update(historical_rock_duel.ROOT_RULES)
TOKEN_RULES.update(historical_rock_duel.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(historical_rock_duel.TOKEN_RULES)
from . import historical_mint_cards
RULES.update(historical_mint_cards.ROOT_RULES)
TOKEN_RULES.update(historical_mint_cards.TOKEN_RULES)
DEATH_EFFECTS.update(historical_mint_cards.DEATH_EFFECTS)
TRIGGERS.update(historical_mint_cards.TRIGGERS)
END_EFFECTS.update(historical_mint_cards.END_EFFECTS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_mint_cards.FIXED_TOKEN_IDS
# Default Discover class restriction remains own class plus neutral.
RULES['VAC_432']=('none',[discover(pool(mechanic='NEWEST_EXPANSION',classes='own_or_neutral'))])
from . import historical_combined_choices
RULES.update(historical_combined_choices.ROOT_RULES)
TOKEN_RULES.update(historical_combined_choices.TOKEN_RULES)
CHOICES.update(historical_combined_choices.CHOICES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_combined_choices.FIXED_TOKEN_IDS
from . import historical_galaxy_lens
RULES.update(historical_galaxy_lens.ROOT_RULES)
TOKEN_RULES.update(historical_galaxy_lens.TOKEN_RULES)
DEATH_EFFECTS.update(historical_galaxy_lens.DEATH_EFFECTS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|set(historical_galaxy_lens.TOKEN_RULES)
TIME_LOCATION_EFFECTS['GDB_136t']=[('historical_lens_cast',)]
from . import historical_velen
RULES.update(historical_velen.ROOT_RULES)
DEATH_EFFECTS.update(historical_velen.DEATH_EFFECTS)
from . import historical_ebon_heroes
RULES.update(historical_ebon_heroes.ROOT_RULES)
TOKEN_RULES.update(historical_ebon_heroes.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_ebon_heroes.FIXED_TOKEN_IDS
from . import historical_dark_heroes
RULES.update(historical_dark_heroes.ROOT_RULES)
TOKEN_RULES.update(historical_dark_heroes.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_dark_heroes.FIXED_TOKEN_IDS
from . import historical_reckless_power
RULES.update(historical_reckless_power.ROOT_RULES)
from . import historical_masquerade
RULES.update(historical_masquerade.ROOT_RULES)
from . import historical_late_heroes
RULES.update(historical_late_heroes.ROOT_RULES)
TOKEN_RULES.update(historical_late_heroes.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_late_heroes.FIXED_TOKEN_IDS
from . import historical_guff_cariel
RULES.update(historical_guff_cariel.ROOT_RULES)
TOKEN_RULES.update(historical_guff_cariel.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_guff_cariel.FIXED_TOKEN_IDS
from . import historical_rhyssa
RULES.update(historical_rhyssa.ROOT_RULES)
from . import historical_harvester
RULES.update(historical_harvester.ROOT_RULES)
TRIGGERS.update(historical_harvester.TRIGGERS)
from . import historical_frozen_heroes
RULES.update(historical_frozen_heroes.ROOT_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_frozen_heroes.FIXED_TOKEN_IDS
from . import historical_jaina
RULES.update(historical_jaina.ROOT_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_jaina.FIXED_TOKEN_IDS
from . import historical_scabbs
RULES.update(historical_scabbs.ROOT_RULES)
TOKEN_RULES.update(historical_scabbs.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_scabbs.FIXED_TOKEN_IDS
from . import historical_etc
RULES.update(historical_etc.ROOT_RULES)
from . import historical_replay_heroes
RULES.update(historical_replay_heroes.ROOT_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_replay_heroes.FIXED_TOKEN_IDS
from . import historical_brukan
RULES.update(historical_brukan.ROOT_RULES)
TOKEN_RULES.update(historical_brukan.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_brukan.FIXED_TOKEN_IDS
from . import historical_mad_genius
RULES.update(historical_mad_genius.ROOT_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_mad_genius.FIXED_TOKEN_IDS
from . import historical_devout
RULES.update(historical_devout.ROOT_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_devout.FIXED_TOKEN_IDS
from . import historical_amazing_reno
RULES.update(historical_amazing_reno.ROOT_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_amazing_reno.FIXED_TOKEN_IDS
from . import historical_valeera
RULES.update(historical_valeera.ROOT_RULES)
TOKEN_RULES.update(historical_valeera.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_valeera.FIXED_TOKEN_IDS
from . import historical_ignis_crafting
RULES.update(historical_ignis_crafting.ROOT_RULES)
TOKEN_RULES.update(historical_ignis_crafting.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_ignis_crafting.FIXED_TOKEN_IDS
from . import historical_holmes
from . import historical_tavish
RULES.update(historical_tavish.ROOT_RULES)
TOKEN_RULES.update(historical_tavish.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_tavish.FIXED_TOKEN_IDS
from . import historical_zilliax
RULES.update(historical_zilliax.ROOT_RULES)
TOKEN_RULES.update(historical_zilliax.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_zilliax.FIXED_TOKEN_IDS
from . import historical_transfer_student
TOKEN_RULES.update(historical_transfer_student.TOKEN_RULES)
DEATH_EFFECTS.update(historical_transfer_student.DEATH_EFFECTS)
END_EFFECTS.update(historical_transfer_student.END_EFFECTS)
TRIGGERS.update(historical_transfer_student.TRIGGERS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_transfer_student.FIXED_TOKEN_IDS
from . import historical_student_spells
TOKEN_RULES.update(historical_student_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_student_spells.FIXED_TOKEN_IDS
from . import historical_student_outcomes
TOKEN_RULES.update(historical_student_outcomes.TOKEN_RULES)
CHOICES.update(historical_student_outcomes.CHOICES)
END_EFFECTS.update(historical_student_outcomes.END_EFFECTS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_student_outcomes.FIXED_TOKEN_IDS
from . import historical_student_equipment
TOKEN_RULES.update(historical_student_equipment.TOKEN_RULES)
DEATH_EFFECTS.update(historical_student_equipment.DEATH_EFFECTS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_student_equipment.FIXED_TOKEN_IDS
from . import historical_harmonics
TOKEN_RULES.update(historical_harmonics.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_harmonics.FIXED_TOKEN_IDS
from . import historical_conditional_spells
TOKEN_RULES.update(historical_conditional_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_conditional_spells.FIXED_TOKEN_IDS
from . import historical_damage_spells
TOKEN_RULES.update(historical_damage_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_damage_spells.FIXED_TOKEN_IDS
from . import historical_summoning_spells
TOKEN_RULES.update(historical_summoning_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_summoning_spells.FIXED_TOKEN_IDS
from . import historical_forge_spells
TOKEN_RULES.update(historical_forge_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_forge_spells.FIXED_TOKEN_IDS
from . import historical_discover_spells
TOKEN_RULES.update(historical_discover_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_discover_spells.FIXED_TOKEN_IDS
from . import historical_movement_spells
TOKEN_RULES.update(historical_movement_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_movement_spells.FIXED_TOKEN_IDS
from . import historical_death_spells
TOKEN_RULES.update(historical_death_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_death_spells.FIXED_TOKEN_IDS
from . import historical_timed_spells
TOKEN_RULES.update(historical_timed_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_timed_spells.FIXED_TOKEN_IDS
from . import historical_secret_events
TOKEN_RULES.update(historical_secret_events.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_secret_events.FIXED_TOKEN_IDS
from . import historical_misc_spells
TOKEN_RULES.update(historical_misc_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_misc_spells.FIXED_TOKEN_IDS
from .historical_printing_aliases import FIXED_TOKEN_IDS as PRINTING_ALIAS_IDS
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|PRINTING_ALIAS_IDS
from . import historical_bottle_spells
TOKEN_RULES.update(historical_bottle_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_bottle_spells.FIXED_TOKEN_IDS
from . import historical_location_timed
TOKEN_RULES.update(historical_location_timed.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_location_timed.FIXED_TOKEN_IDS
from . import historical_secret_v3
TOKEN_RULES.update(historical_secret_v3.TOKEN_RULES)
DEATH_EFFECTS.update(historical_secret_v3.DEATH_EFFECTS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_secret_v3.FIXED_TOKEN_IDS
from . import historical_utility_spells
TOKEN_RULES.update(historical_utility_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_utility_spells.FIXED_TOKEN_IDS
from . import historical_volley_spells
TOKEN_RULES.update(historical_volley_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_volley_spells.FIXED_TOKEN_IDS
from . import historical_held_upgrades
TOKEN_RULES.update(historical_held_upgrades.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_held_upgrades.FIXED_TOKEN_IDS
from . import historical_music_spells
TOKEN_RULES.update(historical_music_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_music_spells.FIXED_TOKEN_IDS
CHOICES.update(historical_music_spells.CHOICES)
from . import historical_lingering_spells
TOKEN_RULES.update(historical_lingering_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_lingering_spells.FIXED_TOKEN_IDS
from . import historical_change_spells
TOKEN_RULES.update(historical_change_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_change_spells.FIXED_TOKEN_IDS
from . import historical_growing_weapons
TOKEN_RULES.update(historical_growing_weapons.TOKEN_RULES)
DEATH_EFFECTS.update(historical_growing_weapons.DEATH_EFFECTS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_growing_weapons.FIXED_TOKEN_IDS
from . import historical_literal_bonus
TOKEN_RULES.update(historical_literal_bonus.TOKEN_RULES)
DEATH_EFFECTS.update(historical_literal_bonus.DEATH_EFFECTS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_literal_bonus.FIXED_TOKEN_IDS
from . import historical_physical_spells
TOKEN_RULES.update(historical_physical_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_physical_spells.FIXED_TOKEN_IDS
CHOICES.update(historical_physical_spells.CHOICES)
from . import historical_state_spells
TOKEN_RULES.update(historical_state_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_state_spells.FIXED_TOKEN_IDS
from . import historical_attack_weapons
TOKEN_RULES.update(historical_attack_weapons.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_attack_weapons.FIXED_TOKEN_IDS
from . import historical_offer_spells
TOKEN_RULES.update(historical_offer_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_offer_spells.FIXED_TOKEN_IDS
from . import historical_resolution_spells
TOKEN_RULES.update(historical_resolution_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_resolution_spells.FIXED_TOKEN_IDS
from . import historical_zone_spells
TOKEN_RULES.update(historical_zone_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_zone_spells.FIXED_TOKEN_IDS
from . import historical_numeric_spells
TOKEN_RULES.update(historical_numeric_spells.TOKEN_RULES)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|historical_numeric_spells.FIXED_TOKEN_IDS
GENERATED_IDS=frozenset(RULES)


def ichman_killed(game,source):
 if source is None or getattr(source,'silenced',False):return
 state=getattr(source,'rule_state',{})
 if state.get('historical_ichman_turn')!=game.turn:return
 # Consume the one-use grant before publishing a repeat, including cleaves
 # or an effect that destroys several minions in one operation.
 state.pop('historical_ichman_turn',None)
 context=dict(owner=source.owner,source=None,target=0,bonus=0,lifesteal=False,card_id='AV_336')
 game._rule_events.append(('captured_effects',dict(operations=(('historical_copy_ichman_recruit',),),context=context),[]))


def capture_choose_spell(game,owner,card,branch):
 if card.card_id not in CHOOSE_SPELL_BRANCHES:return
 card._historical_choose_branch=branch
 game.players[owner]._historical_last_choose=dict(card=deepcopy(card),branch=branch)


def publish_choose_spell(game,owner,card):
 if card.card_id in CHOOSE_SPELL_BRANCHES:
  game._queue_event('historical_choose_spell',owner=owner,card_id=card.card_id,card=deepcopy(card))


def choose_branch_cards(game,owner,card):
 tokens=CHOOSE_SPELL_BRANCHES.get(card.card_id)
 if tokens is None:
  from engine.cards import UnsupportedCard
  raise UnsupportedCard('Choose One spell has no explicit split family: '+card.card_id)
 from .pools import require_fixed_cards
 require_fixed_cards(tokens,game.cards)
 result=[]
 for token in tokens:
  child=game._copy_card(card,source_owner=owner);child.card_id=token
  for field in ('_historical_choose_branch',):
   if hasattr(child,field):delattr(child,field)
  result.append(child)
 return result


def pathmaker_other(game,owner):
 record=getattr(game.players[owner],'_historical_last_choose',None)
 if record is None or record['branch'] not in (0,1):return None
 token=CHOOSE_SPELL_BRANCHES[record['card'].card_id][1-record['branch']]
 child=game._copy_card(record['card'],source_owner=owner);child.card_id=token
 if hasattr(child,'_historical_choose_branch'):delattr(child,'_historical_choose_branch')
 return child


def offer_stitch(game,owner,state):
 stage=len(state['selected'])
 if stage>=3:
  source=state['source']
  if source is not None:
   source.attached_death_effects.append(('historical_copy_stitched_summon',tuple(state['selected'])))
   source.keywords.add('DEATHRATTLE')
  return
 values=state['pools'][stage]
 ids=game.rng.sample(list(values),min(3,len(values)))
 if not ids:return
 if game.pending_choice is not None:raise ValueError('Stitchensew cannot overwrite a choice')
 game.pending_choice=dict(owner=owner,kind='historical_stitch',options=[dict(card_id=cid) for cid in ids],_state=state,_automatic=state['automatic'])
 game.phase='choice'


def offer_griftah(game,owner,state):
 values=state['candidates']
 ids=game.rng.sample(list(values),min(3,len(values)))
 if not ids:return
 if game.pending_choice is not None:raise ValueError('Griftah cannot overwrite a choice')
 game.pending_choice=dict(owner=owner,kind='historical_griftah',options=[dict(card_id=cid) for cid in ids],_state=state,_automatic=state['automatic'])
 game.phase='choice'


def offer_guess(game,ctx,mode):
 from .identities import canonical_identity
 from .selectors import has_class
 owner=ctx['owner'];enemy=game.players[1-owner]
 def identity(cid):return canonical_identity(game.cards[cid],game.cards)
 original=list(enemy.starting_deck)
 original_ids={identity(cid) for cid in original}
 if mode=='hand':
  if not enemy.hand:return
  donor=game.rng.choice(list(enemy.hand))
  held={identity(card.card_id) for card in enemy.hand}
  candidates={identity(cid):cid for cid in original if identity(cid) not in held}
  decoys=game.rng.sample(list(candidates.values()),min(2,len(candidates)))
  correct=donor.card_id
  payload=deepcopy(donor)
 else:
  class_cards=[cid for cid in original if has_class(game.cards[cid],enemy.hero_class)]
  candidates=class_cards or [cid for cid in original if has_class(game.cards[cid],'NEUTRAL')]
  if not candidates:return
  correct=game.rng.choice(candidates);payload=Card(0,correct)
  from .generation_catalog import load_universe
  universe=load_universe()
  selected_class=enemy.hero_class if class_cards else 'NEUTRAL'
  # These are visual decoys, not generated outcomes. Do not use executable
  # coverage or generation-only bans to remove possible false answers.
  decoys=[cid for cid,data in universe.records.items() if has_class(data,selected_class) and canonical_identity(data,universe.records) not in original_ids]
  decoys=game.rng.sample(decoys,min(2,len(decoys)))
 options=[dict(card_id=correct)]+[dict(card_id=cid) for cid in decoys]
 game.rng.shuffle(options)
 if game.pending_choice is not None:raise ValueError('Guess cannot overwrite a choice')
 game.pending_choice=dict(owner=owner,kind='historical_card_guess',options=options,_correct=correct,_payload=payload,_automatic=bool(ctx.get('automatic_choices',False)))
 game.phase='choice'


def aegwynn_draw(game,owner,card):
 player=game.players[owner];count=getattr(player,'historical_aegwynn_pending',0)
 if not count or game._card_data(card)['type']!='MINION':return
 player.historical_aegwynn_pending=0
 state=game._b60_state(card)
 state['historical_aegwynn_stacks']=state.get('historical_aegwynn_stacks',0)+count


def gamer_options():
 return [dict(card_id='MIS_916',label=label,throw=index) for index,label in enumerate(('Rock','Paper','Scissors'))]


def gamer_winner(owner,first,second):
 if first==second:return None
 return owner if (first-second)%3==1 else 1-owner


def counter_play_admitted(game,actor,card,*,paid_cost=None):
 kind=game._card_data(card)['type']
 if kind not in ('MINION','SPELL'):return False
 owner=1-actor;entries=[]
 for minion in game.players[owner].minions:
  if not minion.silenced and minion.health>0 and kind in minion.rule_state.get('historical_okani_counters',()):entries.append((minion.uid,'minion',minion))
 if kind in ('SPELL','MINION') and game.current!=owner:
  from .historical_secret_batches import blocked
  from .secrets import SECRETS
  if not blocked(game):
   entries.extend((getattr(secret,'_secret_entry_order',secret.uid),'secret',secret) for secret in game.players[owner].secrets if SECRETS.get(secret.card_id) in (('counterspell','improved_ice','ice_trap','never_surrender','mana_bind','oh_my_yogg') if kind=='SPELL' else ('objection',)))
 if not entries:return False
 for _,category,entity in sorted(entries,key=lambda entry:entry[0]):
  if category=='secret':
   if entity not in game.players[owner].secrets:continue
   if game._secret_event('before_spell' if kind=='SPELL' else 'before_minion',actor,_only_secret_uid=entity.uid,physical_card=card,paid_cost=paid_cost):return True
  elif entity in game.players[owner].minions and not entity.silenced and entity.health>0 and kind in entity.rule_state.get('historical_okani_counters',()):
   entity.rule_state['historical_okani_counters'].remove(kind)
   game._log('counter',player=owner,source=entity.uid,card_type=kind)
   return True
 return False


def redirect_sanctum(game,owner,target_uid):
 if live(game,target_uid) is None:return target_uid
 # Capture eligibility for this targeting event, then resolve each bearer once
 # in physical entry order. Newly redirected targeting cannot form a loop.
 bearers=[m for m in game.players[1-owner].minions if m.card_id=='RLK_677' and not m.silenced and m.health>0 and m.uid!=target_uid]
 for bearer in sorted(bearers,key=lambda m:m.uid):
  if bearer in game.players[bearer.owner].minions and bearer.health>0 and not bearer.silenced:
   game._log('spell_redirect',player=bearer.owner,source=bearer.uid,previous_target=target_uid,target=bearer.uid)
   target_uid=bearer.uid
 return target_uid


def publish_zentimo(game,owner,card):
 values=getattr(card,'_historical_zentimo_targets',())
 if not values:return
 combo=getattr(card,'_historical_target_combo',False)
 operations=tuple(('historical_copy_targeted_recast',dict(card=game._copy_card(card,source_owner=owner),uid=uid,combo=combo)) for uid in values)
 game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='TRL_085')),[]))


def apply_hand_mirror(game,owner,card,donor):
 mode=card._historical_mirror_mode
 baseline=getattr(card,'_historical_mirror_baseline',{})
 # Keep enchantments applied to the held mirror separate from the donor's
 # copied additive modifiers, so repeated updates do not stack those modifiers.
 fields=('attack_bonus','health_bonus','cost_delta')
 deltas={key:getattr(card,key,0)-baseline.get(key,0) for key in fields}
 own_set=getattr(card,'set_cost',None)
 preserve_set=own_set!=baseline.get('set_cost')
 blank='VAC_420t' if mode=='fortune' else 'WW_337t'
 replacement=deepcopy(donor) if donor is not None else Card(card.uid,blank)
 replacement.uid=card.uid
 game._carry_origin(donor if donor is not None else card,replacement,copied=True,source_owner=owner)
 copied={key:getattr(replacement,key,0) for key in fields}
 copied['set_cost']=getattr(replacement,'set_cost',None)
 for key in fields:setattr(replacement,key,copied[key]+deltas[key])
 if preserve_set:replacement.set_cost=own_set
 for key in ('_hand_entry_turn','_drawn_turn'):
  if hasattr(card,key):setattr(replacement,key,getattr(card,key))
 replacement._historical_mirror_mode=mode
 replacement._historical_mirror_baseline=copied
 card.__dict__.clear();card.__dict__.update(replacement.__dict__)


def refresh_fortunes(game):
 for owner,player in enumerate(game.players):
  donor=player.deck[-1] if player.deck else None
  for card in player.hand:
   if getattr(card,'_historical_mirror_mode',None)=='fortune':apply_hand_mirror(game,owner,card,donor)


def roll_mirage(game,owner,card):
 values=[value for value in game.players[owner].deck if game._card_data(value)['type']=='MINION']
 apply_hand_mirror(game,owner,card,game.rng.choice(values) if values else None)


def elemental_streak(game,owner):
 p=game.players[owner]
 return getattr(p,'historical_elemental_completed_streak',0)+int(bool({'ELEMENTAL','ALL'} & p.played_tribes))


def mix_concoction(game,owner,card):
 if card.card_id not in CONCOCTIONS:return card
 player=game.players[owner]
 older=next((held for held in player.hand if held is not card and held.card_id in CONCOCTIONS),None)
 if older is None:return card
 from .pools import require_fixed_cards
 key=tuple(sorted((CONCOCTIONS.index(older.card_id),CONCOCTIONS.index(card.card_id))))
 mixed=CONCOCTION_MIXES[key][0];require_fixed_cards((mixed,),game.cards)
 player.hand.remove(card)
 game._b60_transform_card(older,mixed)
 game._log('concoction_mixed',player=owner,entity=older.uid)
 return older


def live(game,uid):
 return next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)


def targets(game,cid,owner,mode):
 from .historical_summon_faction_finish import targets as summon_faction_targets
 result=summon_faction_targets(game,cid,owner,mode)
 if result is not None:return result
 if mode=='historical_copy_passions_target':
  return game._targets_for(cid,owner,'enemy_minion') if len(game.players[owner].board)<7 else []
 if mode=='historical_ship_enemy':
  return [uid for uid in game._targets_for(cid,owner,'enemy_minion') if uid>0 and {'STARSHIP','STARSHIP_PIECE'}&set(game._card_data(live(game,uid)).get('mechanics',()))] or [0]
 if mode=='historical_copy_pathmaker_target':
  record=getattr(game.players[owner],'_historical_last_choose',None)
  if record is None or record['branch'] not in (0,1):return [0]
  token=CHOOSE_SPELL_BRANCHES[record['card'].card_id][1-record['branch']]
  from .cards import RULES as all_rules
  return game._targets_for(token,owner,all_rules[token][0]) or [0]
 if mode=='historical_copy_blank_mirror':return []
 if mode in ('historical_copy_madness_target','historical_copy_shadow_madness_target'):
  if len(game.players[owner].board)>=7:return []
  return [uid for uid in game._targets_for(cid,owner,'enemy_minion') if live(game,uid).attack<=(3 if mode=='historical_copy_shadow_madness_target' else 2)]
 if mode=='historical_copy_protoss_target':return [uid for uid in game._targets_for(cid,owner,'friendly_minion') if live(game,uid).card_id in PROTOSS_MINIONS]
 if mode=='historical_copy_hand_minion':return [card.uid for card in game.players[owner].hand if game._card_data(card)['type']=='MINION']
 if mode=='historical_copy_pair':
  values=game._targets_for(cid,owner,'minion')
  if game.cards[cid]['type']=='SPELL':return values if len([uid for uid in values if uid>0])>=2 else []
  return values or [0]
 excavation=historical_excavate.targets(game,cid,owner,mode)
 if excavation is not None:return excavation
 if mode=='historical_copy_location':return [location.uid for location in game.players[owner].locations] or [0]
 if mode=='historical_copy_treant':
  from .historical_tribal_batches import TREANTS
  return [m.uid for m in game.players[owner].minions if m.card_id in TREANTS and m.health>0] or [0]
 if mode in ('historical_copy_mct','historical_copy_cabal'):
  enemies=game.players[1-owner].minions
  if mode=='historical_copy_mct' and len(enemies)<4:return [0]
  values=game._targets_for(cid,owner,'enemy_minion')
  return [uid for uid in values if mode=='historical_copy_mct' or live(game,uid).attack<=2] or [0]
 if mode=='historical_copy_taldaram':
  return game._targets_for(cid,owner,'minion') if all(game._card_data(c)['cost']!=3 for c in game.players[owner].deck) else [0]
 if mode not in ('historical_copy_friendly_deathrattle','historical_copy_damaged'):return None
 base='friendly_minion' if mode=='historical_copy_friendly_deathrattle' else 'minion'
 result=[]
 for uid in game._targets_for(cid,owner,base):
  m=live(game,uid)
  if m is not None and (bool(game._death_operations(m)) if base=='friendly_minion' else m.health<m.max_health):result.append(uid)
 return result or [0]


def matches(game,wanted,kind,data,minion):
 if not isinstance(wanted,tuple) or len(wanted)!=2 or wanted[0]!='historical_copy_event':return None
 if wanted[1]=='harvester_play':return data.get('owner')==minion.owner and data.get('historical_harvester_link',(None,))[0]==1-minion.owner
 if wanted[1]=='choose_spell':return kind=='historical_choose_spell' and data['owner']==minion.owner
 if wanted[1] in ('shuffle_extra','shuffle_hand'):
  if kind!='historical_card_shuffled' or data['owner']!=minion.owner:return False
  if wanted[1]=='shuffle_extra':return not data.get('suppress_elekk',False)
  return data['destination']==minion.owner
 if wanted[1]=='kotori':return kind=='spell_cast' and data['owner']==minion.owner and data.get('cast_target',{}).get('uid')==minion.uid and game.cards[data['card_id']].get('spellSchool')=='HOLY'
 if wanted[1]=='hero_attack_gain':return kind=='historical_hero_attack_gained' and data['owner']==minion.owner
 if wanted[1]=='self_attack_gain':return kind=='historical_minion_attack_gained' and data['source']==minion.uid
 if wanted[1]=='courier':
  if kind!='historical_hand_entry' or data['owner']!=minion.owner or data.get('creator_uid')==minion.uid:return False
  from .selectors import has_class
  card=data['card'];definition=game._card_data(card)
  return not has_class(definition,'NEUTRAL') and not has_class(definition,game.players[minion.owner].hero_class)
 if wanted[1]=='sharpshooter':
  if data.get('owner')!=minion.owner or data.get('source')==minion.uid:return False
  if minion.rule_state.get('historical_sharpshooter_spell',False):return kind=='spell_cast'
  return kind=='minion_played' and has_tribe(game._event_card_data(data),'NAGA')
 if kind!='minion_played' or data.get('source')==minion.uid:return False
 if wanted[1]=='battlecry_play':return data['owner']==minion.owner and 'BATTLECRY' in game.cards[data['card_id']].get('mechanics',())
 if wanted[1]=='templar_play':return data['owner']==minion.owner and data.get('card_id') in TEMPLARS
 if wanted[1]=='own_play':return data['owner']==minion.owner
 if wanted[1]=='enemy_play':return data['owner']!=minion.owner
 if wanted[1]=='cheap_play':return data['owner']==minion.owner and data['cost']<=2
 return False


def replace(game,old,donor,stats=None):
 if old is None or donor is None or old.dormant:return None
 owner=old.owner;player=game.players[owner]
 if old not in player.minions:return None
 from .historical_replacements import vashj_replaces,vashj_summon
 if vashj_replaces(game,old,donor.card_id):return vashj_summon(game,old,donor.card_id,donor=donor,stats=stats)
 game._colossal_preflight(donor.card_id,owner=owner,copy_from=donor);game._herald_entry_preflight(owner,donor.card_id,donor)
 position=player.board.index(old);player.board.remove(old)
 result=game._create_minion(owner,donor.card_id,position,copy_from=donor)
 if result is not None:
  for field in ('_control_return','_control_no_attack_until'):
   if hasattr(old,field):setattr(result,field,deepcopy(getattr(old,field)))
  if stats is not None:game._set_entity_stats(result,*stats)
  game._colossal_enter(result);game._refresh_auras();game._log('transform',entity=old.uid,replacement=result.uid,card=result.card_id)
 return result


def split(game,op,ctx):
 if op[0]=='historical_wisdomball_cast':
  from .historical_wisdomball import split as wisdomball_split
  return wisdomball_split(game,op,ctx)
 if op[0]=='historical_ungoro_living':
  from .historical_ungoro_pack_dependencies import split as ungoro_split
  return ungoro_split(game,op,ctx)
 if op[0].startswith('historical_bottle_'):return historical_bottle_spells.split(game,op,ctx)
 if op[0].startswith('historical_location_timed_'):return historical_location_timed.split(game,op,ctx)
 if op[0].startswith('historical_secret_v3_'):return historical_secret_v3.split(game,op,ctx)
 if op[0].startswith('historical_utility_'):return historical_utility_spells.split(game,op,ctx)
 if op[0].startswith('historical_volley_'):return historical_volley_spells.split(game,op,ctx)
 if op[0].startswith('historical_music_'):return historical_music_spells.split(game,op,ctx)
 if op[0].startswith('historical_lingering_'):return historical_lingering_spells.split(game,op,ctx)
 if op[0].startswith('historical_change_'):return historical_change_spells.split(game,op,ctx)
 if op[0].startswith('historical_bonus_'):return historical_literal_bonus.split(game,op,ctx)
 if op[0].startswith('historical_physical_'):return historical_physical_spells.split(game,op,ctx)
 if op[0].startswith('historical_state_'):return historical_state_spells.split(game,op,ctx)
 if op[0].startswith('historical_attack_weapon_'):return historical_attack_weapons.split(game,op,ctx)
 if op[0].startswith('historical_offer_'):return historical_offer_spells.split(game,op,ctx)
 if op[0].startswith('historical_resolution_'):return historical_resolution_spells.split(game,op,ctx)
 if op[0].startswith('historical_zone_'):return historical_zone_spells.split(game,op,ctx)
 if op[0].startswith('historical_numeric_'):return historical_numeric_spells.split(game,op,ctx)
 if op[0].startswith('historical_misc_'):return historical_misc_spells.split(game,op,ctx)
 if op[0].startswith('historical_death_spell_'):return historical_death_spells.split(game,op,ctx)
 if op[0].startswith('historical_movement_'):return historical_movement_spells.split(game,op,ctx)
 if op[0].startswith('historical_discover_'):return historical_discover_spells.split(game,op,ctx)
 if op[0].startswith('historical_forge_spell_'):return historical_forge_spells.split(game,op,ctx)
 if op[0].startswith('historical_summoning_'):return historical_summoning_spells.split(game,op,ctx)
 if op[0].startswith('historical_damage_'):return historical_damage_spells.split(game,op,ctx)
 if op[0].startswith('historical_equipment_'):return historical_student_equipment.split(game,op,ctx)
 if op[0].startswith('historical_outcome_'):return historical_student_outcomes.split(game,op,ctx)
 if op[0].startswith('historical_student_spell_'):return historical_student_spells.split(game,op,ctx)
 if op[0]=='historical_student_awaken':return historical_transfer_student.split(game,op,ctx)
 if op[0]=='historical_ignis_summon':return historical_ignis_crafting.split(game,op,ctx)
 if op[0] in ('historical_devout_replay','historical_devout_death'):return historical_devout.split(game,op,ctx)
 if op[0]=='historical_boom_kaboom':return historical_mad_genius.split(game,op,ctx)
 if op[0]=='historical_brukan_lightning':return historical_brukan.split(game,op,ctx)
 if op[0] in ('historical_replay_hero','historical_arcane_burst'):return historical_replay_heroes.split(game,op,ctx)
 if op[0]=='historical_jaina_touch':return historical_jaina.split(game,op,ctx)
 if op[0]=='historical_guff_random':return historical_guff_cariel.split(game,op,ctx)
 if op[0].startswith('historical_reckless_'):return historical_reckless_power.split(game,op,ctx)
 if op[0]=='historical_dark_kurtrus':return historical_dark_heroes.split(game,op,ctx)
 if op[0]=='historical_ebon_horsemen':return historical_ebon_heroes.split(game,op,ctx)
 if op[0].startswith('historical_velen_'):
  return historical_velen.split(game,op,ctx)
 if op[0]=='historical_lens_cast':
  from .historical_galaxy_lens import split as lens_split
  return lens_split(game,op,ctx)
 if op[0]=='historical_headmaster_summon':
  from .historical_headmaster import split as headmaster_split
  return headmaster_split(game,op,ctx)
 if op[0].startswith('historical_mint_'):return historical_mint_cards.split(game,op,ctx)
 if op[0].startswith('historical_horror_'):return historical_horror_crafting.split(game,op,ctx)
 if op[0].startswith('historical_golem_'):
  return historical_golem_crafting.split(game,op,ctx)
 if op[0]=='historical_copy_phony_mobility':
  states=[{} for _ in range(3)]
  operations=tuple(('historical_draw_capture',None,'random',state) for state in states)+(('historical_copy_mobility_discard',states),)
  return operations[0],operations[1:]
 if op[0]=='historical_copy_phony_tracking':
  legendary=tuple(game._generation_candidates(pool(rarity='LEGENDARY'),ctx['owner']))
  common=tuple(game._generation_candidates(pool(rarity='COMMON'),ctx['owner']))
  if not legendary or not common:return ('batch30_noop',),()
  state={'legendary':legendary,'common':common,'cards':[]}
  return ('historical_copy_tracking_create',state),(('historical_copy_tracking_create',state),)*2+(('historical_copy_tracking_transform',state),)
 if op[0]=='historical_copy_bob_triple':
  state={}
  return ('historical_draw_capture',(('type','eq','MINION'),),'random',state),(('historical_copy_bob_copies',state),)
 if op[0]=='historical_copy_plunder_take':
  operations=(('historical_copy_plunder_one',op[1]),)*op[2]
  return operations[0],operations[1:]
 if op[0]=='historical_copy_rafaam_imps':
  from .historical_imps import is_imp
  records=[record for record in game.players[ctx['owner']].death_records if is_imp(game,record['entity'])]
  selected=game.rng.sample(records,min(4,len(records)))
  operations=tuple(('summon',record['card_id'],1) for record in selected)
  if op[1]:operations+=(('historical_copy_buff_imps',2,2),)
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_grunty':
  from .generation_cards import board_pool
  request=board_pool(pool(card_type='MINION',tribe='MURLOC'))
  values=tuple(game._generation_candidates(request,ctx['owner']))
  if not values:return ('batch30_noop',),()
  state={'summoned':[],'candidates':values,'index':0}
  return ('historical_copy_grunty_summon',state),(('historical_copy_grunty_summon',state),)*3+(('historical_copy_grunty_offer',state),)
 if op[0]=='historical_copy_cheese':
  from .generation_cards import board_pool
  card=ctx.get('physical_card');level=getattr(card,'rule_state',{}).get('historical_cheese_level',1)
  request=board_pool(pool(card_type='MINION',minimum=level,maximum=level))
  game._generation_candidates(request,ctx['owner'])
  operation=random_cards(request,destination='board')
  first,tail=game._split_fixed_summon(operation,ctx)
  return first,tuple(tail)+(operation,operation)
 if op[0]=='historical_copy_nighthold':
  values=game._generation_candidates(pool(card_type='SPELL',mechanic='SECRET',classes='PALADIN'),ctx['owner'])
  if not values:return ('batch30_noop',),()
  operations=tuple(('cast_fixed_spell',game.rng.choice(values),'random') for _ in range(3))
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tail+operations[1:]
 if op[0]=='historical_copy_korune':
  first={};second={}
  return ('historical_draw_capture',None,'random',first),(('historical_draw_capture',None,'random',second),('historical_copy_korune_swap',first,second))
 ship_split=historical_starships.split(game,op,ctx)
 if ship_split is not None:return ship_split
 excavation=historical_excavate.split(game,op,ctx)
 if excavation is not None:return excavation
 if op[0]=='historical_copy_thorignir':
  target=ctx['event']['target']
  first={'target':target,'created':[]};second={'target':target,'created':[]}
  return ('historical_copy_whelp_summon',first),(('historical_copy_whelp_attacks',first),('historical_copy_whelp_summon',second),('historical_copy_whelp_attacks',second))
 if op[0]=='historical_copy_whelp_attacks':
  state=op[1];target=state['target']
  if target>0 and game._force_live(target) is None:return ('batch30_noop',),()
  operations=tuple(('force_pair',uid,target) for uid in state['created'] if game._force_live(uid) is not None)
  if not operations:return ('batch30_noop',),()
  head,tail=game._split_fixed_summon(operations[0],ctx)
  return head,tail+operations[1:]
 if op[0]=='historical_copy_goldbeard':
  donor=ctx['event'].get('historical_goldbeard_donor')
  if donor is None:return ('batch30_noop',),()
  state={'donor':donor,'created':[]}
  return ('historical_copy_goldbeard_summon',state),(('historical_copy_goldbeard_step',state,0),)
 if op[0]=='historical_copy_goldbeard_step':
  state,index=op[1:]
  if index>=len(state['created']):return ('batch30_noop',),()
  uid=state['created'][index];attacker=game._force_live(uid)
  rest=(('historical_copy_goldbeard_step',state,index+1),)
  if attacker is None:return ('batch30_noop',),rest
  target=game._force_target(attacker.owner,'random_enemy_character')
  if not target:return ('historical_copy_goldbeard_die',uid),rest
  head,tail=game._force_split(('force_pair',uid,target),ctx)
  return head,tail+(('historical_copy_goldbeard_die',uid),)+rest
 if op[0]=='historical_copy_pathmaker':
  card=pathmaker_other(game,ctx['owner'])
  if card is None:return ('batch30_noop',),()
  return game._split_fixed_summon(('cast_physical_spell',card,'selected'),ctx)
 if op[0]=='historical_copy_jerry':
  filters=(('type','eq','SPELL'),('mechanic','eq','CHOOSE_ONE'))
  # Preflight every actual eligible card without restricting the draw pool.
  for card in game.players[ctx['owner']].deck:
   if game._matches_filter(card,filters,zone_owner=ctx['owner']) and card.card_id not in CHOOSE_SPELL_BRANCHES:
    from engine.cards import UnsupportedCard
    raise UnsupportedCard('Jerry split family missing: '+card.card_id)
  state={}
  return ('historical_draw_capture',filters,'random',state),(('historical_copy_jerry_finish',state),)
 if op[0]=='historical_copy_future_return':
  key=op[1]
  payload=game._stored_payloads.pop(key)['values']
  operations=[('historical_copy_future_one',key,index) for index in range(len(payload))]
  # Keep physical entities private; only opaque IDs cross scheduled boundaries.
  game._stored_payloads[key]=dict(owner=ctx['owner'],kind='future_board_return',values=payload)
  operations.append(('historical_copy_future_clear',key))
  return operations[0],tuple(operations[1:])
 if op[0]=='historical_copy_targeted_recast':
  state=op[1];card=state['card'];target=live(game,state['uid'])
  if target is None:return ('batch30_noop',),()
  context=dict(ctx,target=target.uid,combo=state.get('combo',False),outcast=False)
  return game._split_fixed_summon(('replay_context',(('cast_physical_spell',card,'selected'),),context),ctx)
 if op[0]=='historical_copy_kotori':
  owner=ctx['owner'];source=ctx.get('source');card=ctx['event'].get('physical_card')
  if source is None or card is None:return ('batch30_noop',),()
  from .cards import RULES as all_rules
  mode=(game._crafted_rule(card) or all_rules.get(card.card_id,('none',())))[0]
  values=[uid for uid in game._targets_for(card.card_id,owner,mode) if uid>0 and uid!=source.uid and live(game,uid) is not None and live(game,uid).owner==owner]
  if not values:return ('batch30_noop',),()
  state=dict(card=game._copy_card(card,source_owner=owner),uid=game.rng.choice(values),combo=getattr(card,'_historical_target_combo',False))
  return split(game,('historical_copy_targeted_recast',state),ctx)
 if op[0]=='historical_copy_party_crasher':
  target=live(game,ctx.get('target',0))
  if target is None:return ('batch30_noop',),()
  state={'target':target.uid}
  return ('historical_copy_party_recruit',state),(('historical_copy_party_attack',state),)
 if op[0]=='historical_copy_party_attack':
  state=op[1];uid=state.get('uid')
  if uid is None or live(game,uid) is None or live(game,state['target']) is None:return ('batch30_noop',),()
  return game._force_split(('force_pair',uid,state['target']),ctx)
 if op[0]=='historical_copy_gamer':
  source=ctx.get('source')
  if source is None:return ('batch30_noop',),()
  if ctx.get('automatic_choices') or source.card_id!='MIS_916':
   first=game.rng.randrange(3);second=game.rng.randrange(3)
   winner=gamer_winner(ctx['owner'],first,second)
   if winner is None:return ('batch30_noop',),()
   return game._split_fixed_summon(('replay_context',(('draw',2),),dict(ctx,owner=winner)),ctx)
  return ('historical_copy_gamer_first',),()
 if op[0]=='historical_copy_gamer_turn':
  source=ctx.get('source')
  if source is None or source.silenced or source.health<=0 or source not in game.players[source.owner].minions or game.current==source.owner:return ('batch30_noop',),()
  games=source.rule_state.get('historical_gamer_games',[])
  if not games:return ('batch30_noop',),()
  state=dict(source_uid=source.uid,owner=source.owner,first=games.pop(0))
  return ('historical_copy_gamer_second',state),(('historical_copy_gamer_turn',),)
 if op[0]=='historical_copy_zok':
  state=getattr(game.players[ctx['owner']],'historical_hero_stat_gains',{})
  attack=1+(state.get('attack',0) if state.get('turn')==game.turn else 0)
  health=1+(state.get('armor',0) if state.get('turn')==game.turn else 0)
  return ('historical_copy_zok_fan',attack,health),(('historical_copy_zok_fan',attack,health),)
 if op[0]=='historical_copy_jandice':
  from .generation_cards import board_pool
  values=game._generation_candidates(board_pool(pool(card_type='MINION',minimum=5,maximum=5)),ctx['owner'])
  if not values:return ('batch30_noop',),()
  state={'members':[]}
  return ('historical_copy_jandice_summon',game.rng.choice(values),state),(('historical_copy_jandice_next',state),)
 if op[0]=='historical_copy_jandice_next':
  from .generation_cards import board_pool
  values=game._generation_candidates(board_pool(pool(card_type='MINION',minimum=5,maximum=5)),ctx['owner'])
  if not values:return ('historical_copy_jandice_choose',op[1]),()
  return ('historical_copy_jandice_summon',game.rng.choice(values),op[1]),(('historical_copy_jandice_choose',op[1]),)
 if op[0]=='historical_copy_disciple':
  owner=ctx['owner'];spells=[card for card in game.players[owner].hand if game._card_data(card)['type']=='SPELL']
  if not spells:return ('batch30_noop',),()
  card=game.rng.choice(spells)
  return ('historical_copy_disciple_discard',{'card':card}),tuple(('historical_copy_disciple_imp',op[1]) for _ in range(2))
 if op[0]=='historical_copy_sharpshooter':
  source=ctx.get('source')
  if source is None:return ('batch30_noop',),()
  spell_phase=source.rule_state.get('historical_sharpshooter_spell',False)
  owner=source.owner;targets=[game.hero_id(1-owner)]+[m.uid for m in game.players[1-owner].minions if m.health>0]
  tail=(('historical_copy_sharpshooter_draw',spell_phase),('historical_copy_sharpshooter_switch',not spell_phase))
  if not targets:return ('batch30_noop',),tail
  context=dict(ctx,owner=owner,target=game.rng.choice(targets))
  head,more=game._split_fixed_summon(('replay_context',(('damage',2),),context),ctx)
  return head,tuple(more)+tail
 if op[0]=='historical_copy_shudderwock':
  from .identities import canonical_identity
  owner=ctx['owner'];excluded=getattr(ctx.get('physical_card'),'uid',None)
  identity=canonical_identity(game.cards['GIL_820'],game.cards)
  records=[deepcopy(record) for record in getattr(game.players[owner],'_historical_battlecry_records',()) if record['played_uid']!=excluded and canonical_identity(game.cards[record['played_card_id']],game.cards)!=identity]
  game.rng.shuffle(records)
  state=dict(records=records,index=0,budget=ctx.get('historical_wock_budget',{'remaining':30}))
  return game._split_fixed_summon(('historical_copy_wock_step',state),ctx)
 if op[0]=='historical_copy_wock_step':
  state=op[1];source=ctx.get('source')
  if source is None or source not in game.players[source.owner].minions or source.health<=0 or source.silenced:return ('batch30_noop',),()
  if state['budget']['remaining']<=0 or state['index']>=len(state['records']):return ('batch30_noop',),()
  record=state['records'][state['index']];state['index']+=1;state['budget']['remaining']-=1
  context=dict(ctx,owner=source.owner,historical_wock_budget=state['budget'])
  first,tail=repeat_battlecry_program(game,record,context)
  return first,tuple(tail)+(('historical_copy_wock_step',state),)
 if op[0]=='historical_copy_repeat_battlecry':
  owner=ctx['owner'];source=ctx.get('source');exclude=getattr(ctx.get('physical_card'),'uid',None)
  records=[record for record in getattr(game.players[owner],'_historical_battlecry_records',()) if record['played_uid']!=exclude]
  if op[1]=='first_turn':records=[record for record in records if record['turn']==game.turn][:1]
  else:records=records[-1:]
  if not records:return ('batch30_noop',),()
  return repeat_battlecry_program(game,records[0],ctx)

 if op[0]=='historical_copy_vistah_finish':
  from .automatic_cards import validate_automatic_card
  records=tuple(getattr(game.players[ctx['owner']],'_historical_cast_records',()))[op[1]:]
  cards=[game._fresh_replay_card(record['card']) for record in records]
  for card in cards:validate_automatic_card(game,card,ctx['owner'])
  operations=tuple(('cast_physical_spell',card,'random') for card in cards)
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_history_replay':
  from .selectors import has_class
  from .automatic_cards import validate_automatic_card
  owner=ctx['owner'];mode=op[1];player=game.players[1-owner if mode=='murozond' else owner]
  exclude=getattr(ctx.get('physical_card'),'uid',None)
  records=[record for record in player.replay_history if record.card.uid!=exclude]
  if mode in ('murozond','sasquawk'):
   previous=getattr(player,'last_turn_ended',-1)
   records=[record for record in records if record.turn==previous]
  elif mode in ('conman','tess','stash'):
   records=[record for record in records if not has_class(game._card_data(record.card),game.players[owner].hero_class) and not has_class(game._card_data(record.card),'NEUTRAL')]
   if mode=='conman':records=records[-1:]
  elif mode=='parrot':records=[record for record in records if game._card_data(record.card)['cost']==1][-1:]
  cards=[game._fresh_replay_card(record.card) for record in records]
  # Check the complete captured set before random ordering or partial replay.
  for card in cards:validate_automatic_card(game,card,owner)
  if mode=='murozond':cards.reverse()
  elif mode in ('sasquawk','tess','stash'):game.rng.shuffle(cards)
  if mode=='tess':cards=cards[:30]
  elif mode=='stash':cards=cards[:5]
  operations=tuple(('historical_copy_history_card',{'card':card}) for card in cards)
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_history_card':
  source=ctx.get('source');owner=source.owner if source is not None else ctx['owner']
  context=dict(ctx,owner=owner,combo=False,outcast=False)
  return game._split_fixed_summon(('replay_context',(('automatic_card',op[1]['card'],'random'),),context),ctx)
 if op[0]=='historical_copy_kurtrus':
  from .identities import canonical_identity
  p=game.players[ctx['owner']];identities=[canonical_identity(game.cards[cid],game.cards) for cid in p.starting_deck]
  if len(identities)!=len(set(identities)):return ('batch30_noop',),()
  return ('historical_copy_kurtrus_shot',),(('historical_copy_kurtrus_shot',),)*5
 if op[0]=='historical_copy_photon':
  state={}
  return ('historical_copy_photon_damage',state),(('historical_copy_photon_reward',state),)
 if op[0]=='historical_copy_photon_hit':
  return ('historical_copy_photon_damage',op[1]),(('historical_copy_photon_reward',op[1]),)
 if op[0]=='historical_copy_colossus':
  amount=1+getattr(game.players[ctx['owner']],'historical_protoss_spells',0)
  first,tail=game._split_fixed_summon(('historical_copy_colossus_wave',amount),ctx)
  return first,tuple(tail)+(('historical_copy_colossus_wave',amount),)
 if op[0]=='historical_copy_colossus_wave':
  source=ctx.get('source');owner=source.owner if source is not None else ctx['owner']
  return game._split_fixed_summon(('replay_context',(('area_damage','enemies',op[1]),),dict(ctx,owner=owner)),ctx)
 if op[0]=='historical_copy_robocaller':
  digits=getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_robocaller_digits',(8,8,8))
  operations=tuple(('filtered_draw',(('cost','eq',digit),),1) for digit in digits)
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_horseshoe':
  owner=ctx['owner'];player=game.players[1-owner]
  values=[m for m in player.minions if m.health>0]
  if not values:return ('batch30_noop',),()
  victim=game.rng.choice(values);uids=[victim.uid]
  if getattr(ctx.get('physical_card'),'_hand_entry_turn',None)==game.turn:
   position=player.board.index(victim)
   neighbors=[player.board[i] for i in (position-1,position+1) if 0<=i<len(player.board) and player.board[i] in player.minions and player.board[i].health>0]
   if neighbors:uids.append(game.rng.choice(neighbors).uid)
  operations=tuple(('replay_context',(('damage',2),),dict(ctx,target=uid)) for uid in uids)
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_mimiron_head':
  player=game.players[ctx['owner']];values=[m for m in player.minions if m.health>0 and has_tribe(game._card_data(m),'MECHANICAL')]
  if len(values)<3:return ('batch30_noop',),()
  return ('historical_copy_head_sacrifice',tuple(m.uid for m in values)),(('summon','GVG_111t',1),)
 if op[0]=='historical_copy_kel_skeletons':
  from .identities import canonical_identity
  identity=canonical_identity(game.cards['REV_845'],game.cards);count=sum(canonical_identity(game.cards[cid],game.cards)==identity for cid in game.players[ctx['owner']].death_history)
  return ('historical_copy_kel_step',count),()
 if op[0]=='historical_copy_kel_step':
  count=op[1];owner=ctx['owner']
  if count<=0:return ('batch30_noop',),()
  if len(game.players[owner].board)<7:first,tail=game._split_fixed_summon(('summon','REV_845',1),ctx)
  else:
   from .game import Minion
   raw=game.cards['REV_845'];dummy=Minion(game._new_id(),'REV_845',owner,raw['attack'],raw['health'],raw['health'],set(raw.get('mechanics',())))
   operations=tuple(game._death_operations(dummy))
   context=dict(ctx,source=dummy,card_id='REV_845',bonus=0,lifesteal=False)
   first,tail=game._split_fixed_summon(('replay_context',operations,context),ctx) if operations else (('batch30_noop',),())
  return first,tuple(tail)+(('historical_copy_kel_step',count-1),)
 if op[0]=='historical_copy_burning_portal':
  obj=game._permanent_entity(op[1]);owner=ctx['owner']
  if obj is None or obj.owner!=owner or obj.card_id!='BAR_919t':return ('batch30_noop',),()
  return game._split_fixed_summon(('summon','BAR_914t3',max(0,7-len(game.players[owner].board))),ctx)
 if op[0]=='historical_copy_gelbin_invention':return game._split_fixed_summon(('summon',game.rng.choice(GELBIN_INVENTIONS),1),ctx)
 if op[0]=='historical_copy_murloc_chord':return game._split_fixed_summon(('summon','PRO_001at',game.rng.choice((3,4,5))),ctx)
 if op[0]=='historical_copy_horde_chord':return game._split_fixed_summon(('summon',game.rng.choice(HORDE_WARRIORS),1),ctx)
 if op[0]=='historical_copy_obliterate':
  victim=live(game,ctx.get('target',0))
  return (('destroy',),(('damage_own_hero',max(0,victim.health)),)) if victim is not None else (('batch30_noop',),())
 if op[0]=='historical_copy_doom_pact':
  victims=tuple(m.uid for player in game.players for m in player.minions if m.health>0)
  return ('destroy_all_minions',),(('historical_copy_doom_remove',victims),)
 if op[0]=='historical_copy_lich_army':
  player=game.players[ctx['owner']];removed=[]
  for _ in range(min(5,len(player.deck))):
   card=player.deck.pop();removed.append(card);game._zone_card_removed(ctx['owner'],card,'deck','destroy');game._log('remove_deck_card',player=ctx['owner'],card=game._card_data(card)['id'])
  ops=tuple(('historical_copy_army_summon',card) for card in removed if game._card_data(card)['type']=='MINION')
  return (ops[0],ops[1:]) if ops else (('batch30_noop',),())
 if op[0]=='historical_copy_darkvein_cast':return game._split_fixed_summon(('cast_physical_spell',game._copy_card(op[1],source_owner=ctx['owner']),'random'),ctx)
 if op[0]=='historical_copy_smuggler':
  from .historical_draw_batches import SI7_IDS
  count=1+sum(record.card.card_id in SI7_IDS for record in game.players[ctx['owner']].replay_history if record.card.uid!=getattr(ctx.get('physical_card'),'uid',None))
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=count,maximum=count),destination='board'),ctx)
 if op[0]=='historical_copy_lina':
  cost=ctx.get('event',{}).get('cost',0);count=max(0,7-len(game.players[ctx['owner']].board))
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),count,destination='board'),ctx)
 if op[0]=='historical_copy_draw_aura':
  from .gelbin import AURA_IDS
  return ('filtered_draw',(('id','in',tuple(sorted(AURA_IDS))),),1),()
 if op[0]=='historical_copy_dungar':
  remaining,used=op[1:];player=game.players[ctx['owner']]
  if remaining<=0 or len(player.board)>=7:return ('batch30_noop',),()
  # Frozen set IDs already group mini-sets with their parent expansion.
  values=[card for card in player.deck if game._card_data(card)['type']=='MINION' and game._card_data(card)['set'] not in used]
  if not values:return ('batch30_noop',),()
  card=game.rng.choice(values);expansion=game._card_data(card)['set']
  return ('historical_copy_recruit_uid','deck',card.uid),(('historical_copy_dungar',remaining-1,tuple(used)+(expansion,)),)
 if op[0]=='historical_copy_atiesh':
  owner=ctx['owner'];player=game.players[owner]
  if not player.weapon or player.weapon['card_id']!='KAR_097t' or getattr(player.equipped_card,'uid',None)!=op[1] or len(player.board)>=7:return ('batch30_noop',),()
  from .generation_cards import board_pool
  cost=max(0,op[2]);candidates=game._generation_candidates(board_pool(pool(card_type='MINION',minimum=cost,maximum=cost)),owner)
  wear=('historical_copy_atiesh_wear',op[1])
  if not candidates:return wear,()
  return ('summon',game.rng.choice(candidates),1),(wear,)
 if op[0]=='historical_copy_xalatath':
  player=game.players[ctx['owner']]
  if not player.weapon or player.weapon['card_id']!='TSC_641tc' or getattr(player.equipped_card,'uid',None)!=op[1]:return ('batch30_noop',),()
  context=dict(owner=ctx['owner'],source=None,target=game.hero_id(1-ctx['owner']),card_id='TSC_641tc',bonus=0,lifesteal=False)
  return game._split_fixed_summon(('replay_context',(('damage_enemy_hero',2),('historical_copy_xalatath_wear',op[1])),context),ctx)
 if op[0]=='historical_copy_spore':
  owner=ctx['owner'];player=game.players[owner]
  from .generation_cards import board_pool
  request=board_pool(pool(card_type='MINION',minimum=5,maximum=5))
  values=game._generation_created_candidates(request,ctx)
  if not values:return ('batch30_noop',),()
  chosen=game.rng.choice(values)
  previous=tuple(getattr(player,'historical_spore_outcomes',()))
  player.historical_spore_outcomes=list(previous)+( [chosen] )
  operations=tuple(('summon',cid,1) for cid in (chosen,)+previous)
  return operations[0],operations[1:]
 if op[0]=='historical_copy_vona':
  if getattr(game.players[ctx['owner']],'historical_own_turn_damage_total',0)<8:return ('batch30_noop',),()
  return game._split_fixed_summon(('summon','VAC_945t',1),ctx)
 if op[0]=='historical_copy_nest_discover':
  permanent=game._permanent_entity(op[1])
  if permanent is None or permanent.owner!=ctx['owner'] or permanent.card_id!='WW_824t':return ('batch30_noop',),()
  context=dict(ctx,card_id='WW_824t',generation_creator_id='WW_824')
  return game._split_fixed_summon(('replay_context',(discover(pool(card_type='MINION',tribe='DRAGON',classes='own_or_neutral'),cost_delta=-4),),context),ctx)
 if op[0]=='historical_copy_high_noon':
  a={};b={}
  return ('historical_draw_capture',None,'random',a),(('replay_context',(('historical_draw_capture',None,'random',b),),dict(ctx,owner=1-ctx['owner'])),('historical_copy_high_noon_finish',a,b))
 if op[0]=='historical_copy_power_origin_draw':
  state={'wilfred':game._active('AT_027',ctx['owner'])}
  return ('historical_copy_power_origin_capture',op[1],op[2],state),(('historical_copy_power_draw_finish',state),)
 if op[0] in ('historical_copy_power_draw','historical_copy_power_filtered_draw'):
  filtered=op[0]=='historical_copy_power_filtered_draw';count=op[2] if filtered else op[1]
  if count<=0:return ('batch30_noop',),()
  state={'wilfred':game._active('AT_027',ctx['owner'])}
  following=('historical_copy_power_filtered_draw',op[1],count-1) if filtered else ('historical_copy_power_draw',count-1)
  return ('historical_draw_capture',op[1] if filtered else None,'random',state),(('historical_copy_power_draw_finish',state),following)
 if op[0]=='historical_copy_hydralisk':
  count=1+sum(m is not ctx.get('source') and m.health>0 and m.card_id in ZERG_IDS for m in game.players[ctx['owner']].minions)
  operations=tuple(('damage_random_enemy',2) for _ in range(count))
  return operations[0],operations[1:]
 if op[0] in ('historical_copy_viper','historical_copy_zookeeper'):
  state={};mode='viper' if op[0]=='historical_copy_viper' else 'zookeeper'
  return ('historical_copy_summon_adversary',mode,state),(('historical_copy_adversary_attacks',mode,state),)
 if op[0]=='historical_copy_adversary_attacks':
  mode,state=op[1:];owner=ctx['owner'];operations=[]
  if mode=='viper':
   values=[m for m in game.players[owner].minions if m is not ctx.get('source') and m.health>0 and m.card_id in ZERG_IDS]
   for minion in values:minion.keywords.add('REBORN')
   if state.get('uid') is not None:operations=[('force_pair',m.uid,state['uid']) for m in values]
  else:
   beast=live(game,state.get('uid'))
   if beast is not None:
    targets=[m.uid for m in game.players[1-owner].minions if m.uid!=beast.uid and m.health>0]
    game.rng.shuffle(targets);operations=[('force_pair',beast.uid,uid) for uid in targets]
  return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_purator':
  from .selectors import has_class,TRIBES
  player=game.players[ctx['owner']]
  if any(has_class(game._card_data(card),'NEUTRAL') for card in player.deck):return ('batch30_noop',),()
  values=[card for card in player.deck if game._card_data(card)['type']=='MINION']
  chosen=game._distinct_type_group(values,len(TRIBES))
  operations=tuple(('tribal_draw_physical',card) for card in chosen)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_nzoth_deep':
  from .selectors import TRIBES
  values=[record['entity'] for record in game.players[ctx['owner']].death_records]
  chosen=game._distinct_type_group(values,len(TRIBES))
  # Distinct physical death records remain independently eligible.
  operations=tuple(('historical_copy_tribal_resurrect',game._fresh_replay_card(card)) for card in chosen)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_elise_badlands':
  from .identities import canonical_identity
  p=game.players[ctx['owner']];identities=[canonical_identity(game.cards[cid],game.cards) for cid in p.starting_deck]
  if len(identities)!=len(set(identities)):return ('batch30_noop',),()
  values=[card for card in p.deck if game._card_data(card)['type']=='MINION']
  chosen=game.rng.sample(values,min(4,len(values)))
  operations=tuple(('historical_copy_elise_summon',game._copy_card(card,source_owner=ctx['owner'])) for card in chosen)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_nethrandamus':
  cost=min(10,getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_held_deaths',0))
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),2,destination='board'),ctx)
 if op[0]=='historical_copy_denathrius':
  damage=5+getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_held_deaths',0)//2
  return game._split_fixed_summon(('missiles','enemies',damage),ctx)
 if op[0]=='historical_copy_dragonqueen':
  from .identities import canonical_identity
  player=game.players[ctx['owner']];identities=[canonical_identity(game._card_data(card),game.cards) for card in player.deck]
  if len(identities)!=len(set(identities)):return ('batch30_noop',),()
  # Random creation excludes the creator through the shared generation path.
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',tribe='DRAGON'),2,set_cost=0),ctx)
 if op[0]=='historical_copy_antonidas':
  player=game.players[ctx['owner']];turn=player.turns_taken
  turns={record.get('owner_turn') for record in getattr(player,'_historical_cast_records',()) if game._card_data(record['card']).get('spellSchool')=='FIRE'}
  if turn<=3 or not all(prior in turns for prior in range(turn-3,turn)):return ('batch30_noop',),()
  return game._split_fixed_summon(('replay_context',(('cast_fixed_spell','CS2_029','enemies'),)*3,ctx),ctx)
 if op[0]=='historical_copy_replay_spells':
  owner=ctx['owner'];player=game.players[owner];mode=op[1];history=list(getattr(player,'_historical_cast_records',()))
  if mode=='yogg':return game._split_fixed_summon(('historical_copy_yogg_casts',len(history)),ctx)
  if mode=='jace':records=[dict(card=record.card) for record in player.replay_history if game._card_data(record.card)['type']=='SPELL' and game._card_data(record.card).get('spellSchool')=='FEL']
  elif mode=='rommath':
   if getattr(player,'historical_rommath_used',False):return ('batch30_noop',),()
   player.historical_rommath_used=True;records=[record for record in history if not record['started']]
  elif mode=='lynessa':records=[record for record in history if record['target_minion'] and record['target_owner']==owner]
  else:
   records=[record for record in history if record['target_owner']==1-owner]
   records=records[-1:]
  if mode!='chatty':game.rng.shuffle(records)
  operations=[]
  for record in records:
   card=game._fresh_replay_card(record['card'])
   operations.append(('historical_copy_replay_cast',card,'selected' if mode=='lynessa' else 'prefer_enemies' if mode in ('jace','chatty') else 'random'))
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+tuple(operations[1:])
 if op[0]=='historical_copy_replay_cast':
  source=ctx.get('source');owner=getattr(source,'owner',ctx['owner']);context=dict(ctx,owner=owner)
  if op[2]=='selected':context['target']=getattr(source,'uid',0)
  return game._split_fixed_summon(('replay_context',(('cast_physical_spell',op[1],op[2]),),context),ctx)
 if op[0]=='historical_copy_yogg_casts':
  if op[1]<=0:return ('batch30_noop',),()
  source=ctx.get('source');context=dict(ctx,owner=getattr(source,'owner',ctx['owner']))
  first,tail=game._split_fixed_summon(('replay_context',(('autocast_random',pool(card_type='SPELL'),1),),context),ctx)
  return first,tuple(tail)+((('historical_copy_yogg_casts',op[1]-1),) if op[1]>1 else ())
 if op[0]=='historical_copy_fate_death':
  source=ctx.get('source');choices=getattr(source,'rule_state',{}).get('historical_fatespinner',('growth','decay') if getattr(source,'card_id',None)=='ICC_047t2' else ())
  operations=((('historic_board_buff','all',2,2),) if 'growth' in choices else ()) + ((('area_damage','all_minions',3),) if 'decay' in choices else ())
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_growth_treants':
  from .historical_tribal_batches import TREANTS
  operations=tuple(('historical_copy_literal_uid',m.uid,'TTN_903t4') for m in game.players[ctx['owner']].minions if m.card_id in TREANTS and m.health>0)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_mogu':
  player=game.players[ctx['owner']]
  if len(player.board)!=7 or any(m not in player.minions or m.card_id!='ULD_705' for m in player.board):return ('batch30_noop',),()
  return ('historical_copy_mogu_sacrifice',),(('summon','ULD_705t',1),)
 if op[0]=='historical_copy_witch':
  owner=ctx['owner'];source=ctx.get('source')
  if len(game.players[owner].board)>=7:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(('summon','CS2_065',1),ctx)
  return first,tuple(tail)+(('historical_copy_witch_repeat',),)
 if op[0]=='historical_copy_witch_repeat':
  owner=ctx['owner']
  if len(game.players[1-owner].minions)>len(game.players[owner].minions):return split(game,('historical_copy_witch',),ctx)
  return ('batch30_noop',),()
 if op[0]=='historical_copy_tomb_traitor':
  q=game.players[1-ctx['owner']];cards=[card for card in q.deck if game._card_data(card)['id'] in PLAGUES]
  if not cards:return ('batch30_noop',),()
  selected=game.rng.choice(cards)
  return ('historical_copy_destroy_plague',selected.uid),(('area_damage','enemy_minions',3),)
 if op[0] in ('historical_copy_lurker','historical_copy_wrathguard'):
  victim=live(game,ctx.get('target',0))
  if victim is None:return ('batch30_noop',),()
  player=game.players[victim.owner];position=player.board.index(victim)
  neighbors=tuple(player.board[i].uid for i in (position-1,position+1) if 0<=i<len(player.board) and player.board[i] in player.minions)
  state=dict(victim=victim,neighbors=neighbors)
  return ('historical_copy_hit_bound',victim.uid,3 if op[0]=='historical_copy_lurker' else 2),(('historical_copy_lurker_continue' if op[0]=='historical_copy_lurker' else 'historical_copy_wrathguard_discover',state),)
 if op[0]=='historical_copy_lurker_continue':
  state=op[1]
  if state['victim'].health>0:return ('batch30_noop',),()
  neighbors=[m for uid in state['neighbors'] for m in (live(game,uid),) if m is not None]
  if not neighbors:return ('batch30_noop',),()
  return game._split_fixed_summon(('replay_context',(('historical_copy_lurker',),),dict(ctx,target=game.rng.choice(neighbors).uid)),ctx)
 if op[0]=='historical_copy_wrathguard_discover':
  if op[1]['victim'].health>0:return ('batch30_noop',),()
  return game._split_fixed_summon(discover(pool(card_type='MINION',tribe='DEMON',classes='own_or_neutral')),ctx)
 if op[0]=='historical_copy_blazing':
  operations=tuple(('historical_copy_blazing_card',card.uid) for card in reversed(game.players[ctx['owner']].deck[-3:]))
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_vizier':
  from .historical_condition_batches import matches
  discount=-2 if matches(game,('undead_since_last_turn',),ctx) else 0
  return game._split_fixed_summon(discover(pool(card_type='SPELL',classes='own_or_neutral'),cost_delta=discount),ctx)
 if op[0]=='historical_copy_next_follow':
  source=ctx.get('source')
  if source is None or live(game,source.uid) is None:return ('batch30_noop',),()
  if op[1]=='attack':return game._force_split(('force_pair',source.uid,game._force_target(ctx['owner'],'random_enemy_character')),ctx)
  if op[1]=='copy':return game._split_fixed_summon(('copy_self_right',1),ctx)
  return ('historical_copy_next_hero_attack',),()
 if op[0]=='historical_copy_jeeves':return game._split_fixed_summon(('replay_context',(('draw_until',3),),dict(ctx,owner=game.current)),ctx)
 if op[0]=='historical_copy_spirit_frog':
  cost=max(0,ctx['event']['cost'])+1
  return game._split_fixed_summon(('filtered_draw',(('type','eq','SPELL'),('cost','eq',cost)),1),ctx)
 if op[0]=='historical_copy_phaoris':
  owner=ctx['owner'];cards=[card for card in game.players[owner].hand if game._card_data(card)['type']=='SPELL']
  operations=tuple(random_cards(pool(card_type='MINION',minimum=max(0,game._cost(card,owner)),maximum=max(0,game._cost(card,owner))),destination='board') for card in cards)
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_decoy':
  return ('historical_copy_lowest_hand_recruit',),(('replay_context',(('historical_copy_lowest_hand_recruit',),),dict(ctx,owner=1-ctx['owner'])),)
 if op[0]=='historical_copy_trenchstalker':
  owner=ctx['owner'];source=ctx.get('source');targets=[game.hero_id(1-owner)]+[m.uid for m in game.players[1-owner].minions if m.health>0]
  targets=game.rng.sample(targets,min(3,len(targets)))
  if source is None or not targets:return ('batch30_noop',),()
  operations=tuple(('force_pair',source.uid,uid) for uid in targets);first,tail=game._force_split(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_soulstealer':
  p=game.players[ctx['owner']];q=game.players[1-ctx['owner']];source=ctx.get('source');state={'enemies':{m.uid for m in q.minions if m.health>0}}
  return ('historical_copy_soulstealer_kill',), (('historical_copy_soulstealer_corpses',state),)
 if op[0]=='historical_copy_gandling':
  uid=ctx['event'].get('source')
  return ('historical_copy_kill_bound',uid),(('summon','SCH_126t',1),)
 if op[0]=='historical_copy_attack_tokens':
  state={}
  return ('historical_copy_capture_tokens',op[1],op[2],state),(('historical_copy_token_attacks',state),)
 if op[0]=='historical_copy_token_attacks':
  ops=tuple(('historical_copy_random_bound_attack',uid) for uid in op[1].get('uids',()))
  if not ops:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(ops[0],ctx)
  return first,tuple(tail)+ops[1:]
 if op[0]=='historical_copy_random_bound_attack':
  minion=live(game,op[1]);target=game._force_target(ctx['owner'],'random_enemy_character')
  return game._force_split(('force_pair',op[1],target),ctx) if minion is not None and target else (('batch30_noop',),())
 if op[0]=='historical_copy_cheesemonger':
  cost=max(0,ctx['event']['cost']);return game._split_fixed_summon(random_cards(pool(card_type='SPELL',minimum=cost,maximum=cost)),ctx)
 if op[0]=='historical_copy_enemy_draw_five':return game._split_fixed_summon(('replay_context',(('draw_until',5),),dict(ctx,owner=1-ctx['owner'])),ctx)
 if op[0]=='historical_copy_alanna':
  count=sum(record['cost']>=5 and game.cards[record['card_id']]['type']=='SPELL' for record in game.players[ctx['owner']].played_history)
  return game._split_fixed_summon(('summon','LOOT_535t',count),ctx)
 if op[0]=='historical_copy_spiteful':
  choices=[card for card in game.players[ctx['owner']].deck if game._card_data(card)['type']=='SPELL']
  if not choices:return ('batch30_noop',),()
  card=game.rng.choice(choices);cost=max(0,game._cost(card,ctx['owner']));game._log('reveal',player=ctx['owner'],card=card.card_id)
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),destination='board'),ctx)
 if op[0]=='historical_copy_lost_exarch':
  p=game.players[ctx['owner']];spent=p.mana;p.mana=0;game._b60_spend_mana(ctx['owner'],spent)
  return game._split_fixed_summon(('summon','NX2_032t',spent),ctx)
 if op[0]=='historical_copy_spell_cost_summon':
  cost=max(0,ctx['event']['cost'])
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),destination='board'),ctx)
 if op[0]=='historical_copy_cookie':
  cost=game.cards[ctx['event']['card_id']]['cost']+1
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),destination='board'),ctx)
 if op[0]=='historical_copy_quickdraw_operation':
  return game._split_fixed_summon(op[1],ctx) if getattr(ctx.get('physical_card'),'_hand_entry_turn',None)==game.turn else (('batch30_noop',),())
 if op[0]=='historical_copy_farm_hand':
  quick=getattr(ctx.get('physical_card'),'_hand_entry_turn',None)==game.turn
  return game._split_fixed_summon(discover(pool(card_type='MINION',tribe='UNDEAD',classes='own_or_neutral'),cost_delta=-2 if quick else 0),ctx)
 if op[0]=='historical_copy_gatekeeper':
  owner=ctx['owner'];cards=tuple(game.players[owner].hand)
  for card in cards:game._shuffle_hand_card(owner,card,actor=owner)
  return game._split_fixed_summon(('draw',len(cards)),ctx)
 if op[0]=='historical_copy_streak_copies':
  operations=tuple(('copy_self_right',1) for _ in range(elemental_streak(game,ctx['owner'])))
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_prairie':
  return game._split_fixed_summon(('summon','WW_024t',2),ctx) if {'ELEMENTAL','ALL'} & game.players[ctx['owner']].previous_tribes else (('batch30_noop',),())
 if op[0]=='historical_copy_razzle':return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=5,maximum=5),1+len(getattr(game.players[ctx['owner']],'historical_spell_schools',())),destination='board'),ctx)
 if op[0]=='historical_copy_spurfang':
  source=ctx.get('source')
  if source is None:return ('batch30_noop',),()
  cost=max(0,source.attack)
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',tribe='BEAST',minimum=cost,maximum=cost),destination='board'),ctx)
 if op[0]=='historical_copy_ymirjar':
  owner=ctx['owner']
  if game.players[owner].corpses<3:return ('batch30_noop',),()
  game._spend_corpses(owner,3)
  return game._split_fixed_summon(('summon','RLK_226t',1),ctx)
 if op[0]=='historical_copy_rook_attack':
  source=ctx.get('source')
  return game._force_split(('force_pair',source.uid,game.hero_id(ctx['owner'])),ctx) if source is not None else (('batch30_noop',),())
 if op[0]=='historical_copy_previous_elemental_draw':
  p=game.players[ctx['owner']]
  count=sum(record.turn==p.last_turn_ended and game._card_data(record.card)['type']=='MINION' and has_tribe(game._card_data(record.card),'ELEMENTAL') for record in p.replay_history)
  return game._split_fixed_summon(('draw',1+count),ctx)
 if op[0]=='historical_copy_coral':
  return game._split_fixed_summon(('summon','TSC_648t',len(getattr(game.players[ctx['owner']],'historical_spell_schools',()))),ctx)
 if op[0]=='historical_copy_steeldancer':
  p=game.players[ctx['owner']]
  if not p.weapon:return ('batch30_noop',),()
  cost=max(0,p.weapon['attack'])
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),destination='board'),ctx)
 if op[0]=='historical_copy_enemy_random_two':
  return game._split_fixed_summon(('replay_context',(random_cards(pool(card_type='MINION',minimum=2,maximum=2),destination='board'),),dict(ctx,owner=1-ctx['owner'])),ctx)
 if op[0]=='historical_copy_enemy_draw':return game._split_fixed_summon(('replay_context',(('draw',op[1]),),dict(ctx,owner=1-ctx['owner'])),ctx)
 if op[0]=='historical_copy_mankrik':
  state={}
  return ('historical_copy_mankrik_summon',state),(('historical_copy_mankrik_attacks',state),)
 if op[0]=='historical_copy_mankrik_attacks':
  operations=tuple(('historical_copy_recruited_attack',dict(uid=uid)) for uid in op[1].get('uids',()))
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_cubicle_summon':
  source=ctx.get('source');ids=tuple(getattr(source,'rule_state',{}).get('historical_cubicle_ids',()))
  operations=tuple(('summon',cid,1) for cid in ids)
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_cast_zone':
  owner=ctx['owner'] if op[1]=='own' else 1-ctx['owner'];zone=getattr(game.players[owner],op[2])
  from .selectors import has_school
  choices=[card for card in zone if game._card_data(card)['type']=='SPELL' and (op[3] is None or has_school(game._card_data(card),op[3]))]
  if op[4]=='highest' and choices:
   cost=max(game._cost(card,owner) for card in choices);choices=[card for card in choices if game._cost(card,owner)==cost]
  if not choices:return ('batch30_noop',),()
  selected=game.rng.choice(choices)
  if owner!=ctx['owner']:return ('replay_context',(('cast_zone_spell',op[2],selected.uid,op[5]),),dict(ctx,owner=owner)),()
  return game._split_fixed_summon(('cast_zone_spell',op[2],selected.uid,op[5]),ctx)
 if op[0]=='historical_copy_cast_school_copy':
  from .selectors import has_school
  choices=[card for card in game.players[ctx['owner']].hand if game._card_data(card)['type']=='SPELL' and has_school(game._card_data(card),op[1])]
  if not choices:return ('batch30_noop',),()
  return game._split_fixed_summon(('cast_physical_spell',game._copy_card(game.rng.choice(choices)),'random'),ctx)
 if op[0]=='historical_copy_history_spell':
  owner=ctx['owner'];mode=op[1];player=game.players[1-owner if mode=='asvedon' else owner];records=[record for record in player.replay_history if game._card_data(record.card)['type']=='SPELL']
  if mode=='vargoth':records=[record for record in records if record.turn==game.turn]
  if mode=='parrot':records=[record for record in records if record.paid_cost>=6]
  if mode=='squawker':
   history=getattr(player,'_historical_friendly_minion_target_spells',())
   if not history:return ('batch30_noop',),()
   card=game._fresh_replay_card(history[-1]);source=ctx.get('source')
   return game._split_fixed_summon(('replay_context',(('cast_physical_spell',card,'selected'),),dict(ctx,target=getattr(source,'uid',0))),ctx)
  if not records:return ('batch30_noop',),()
  record=game.rng.choice(records) if mode=='vargoth' else records[-1]
  return game._split_fixed_summon(('cast_physical_spell',game._fresh_replay_card(record.card),'random'),ctx)
 if op[0]=='historical_copy_cast_event_self':
  event=ctx['event'];card=game._fresh_replay_card(event['physical_card']);source=ctx.get('source')
  return game._split_fixed_summon(('replay_context',(('cast_physical_spell',card,'selected'),),dict(ctx,target=getattr(source,'uid',0))),ctx)
 if op[0]=='historical_copy_spell_plus_one':
  cost=ctx['event']['cost']+1;values=game._generation_candidates(pool(card_type='SPELL',minimum=cost,maximum=cost),ctx['owner'])
  return game._split_fixed_summon(('cast_fixed_spell',game.rng.choice(values),'random'),ctx) if values else (('batch30_noop',),())
 if op[0]=='historical_copy_voraxx':
  state=dict(card=game._fresh_replay_card(ctx['event']['physical_card']))
  return ('historical_copy_voraxx_plant',state),(('historical_copy_voraxx_cast',state),)
 if op[0]=='historical_copy_voraxx_cast':
  uid=op[1].get('uid')
  if live(game,uid) is None:return ('batch30_noop',),()
  return game._split_fixed_summon(('replay_context',(('cast_physical_spell',op[1]['card'],'selected'),),dict(ctx,target=uid)),ctx)
 if op[0]=='historical_copy_fatigue':
  state={};return ('historical_copy_take_fatigue',state),(('historical_copy_fatigue_reward',op[1],state),)
 if op[0]=='historical_copy_fatigue_reward' and op[1]=='summon':return game._split_fixed_summon(('summon','ETC_070t',op[2].get('amount',0)),ctx)
 if op[0] in ('historical_copy_force_event','historical_copy_force_random','historical_copy_lothar'):
  source=ctx.get('source');owner=ctx['owner']
  if source not in game.players[owner].minions or source.health<=0:return ('batch30_noop',),()
  if op[0]=='historical_copy_force_event':uid=ctx.get('event',{}).get('source',0)
  else:
   mode='random_enemy_minion' if op[0]=='historical_copy_lothar' or op[1]=='minion' else 'lowest' if op[1]=='lowest' else 'random_enemy_character'
   uid=game._force_target(owner,mode)
  if not uid:return ('batch30_noop',),()
  first,tail=game._force_split(('force_pair',source.uid,uid),ctx)
  if op[0]=='historical_copy_lothar':
   before=len(getattr(game,'_combat_kill_history',{}).get(source.uid,()))
   tail=tuple(tail)+(('historical_copy_lothar_reward',source.uid,uid,before),)
  return first,tail
 if op[0] in ('historical_copy_force_enemies','historical_copy_theldurin'):
  owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
  if source not in p.minions or source.health<=0:return ('batch30_noop',),()
  if op[0]=='historical_copy_theldurin':
   from .identities import canonical_identity
   identities=[canonical_identity(game.cards[cid],game.cards) for cid in p.starting_deck]
   if len(identities)!=len(set(identities)):return ('batch30_noop',),()
   game._temporary_keyword(source,'IMMUNE','end')
  targets=[m.uid for m in game.players[1-owner].minions if m.health>0]+[game.hero_id(1-owner)]
  game.rng.shuffle(targets);operations=tuple(('force_pair',source.uid,uid) for uid in targets)
  first,tail=game._force_split(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0] in ('historical_copy_egg_attack','historical_copy_bloodstinger'):
  state={};summon=('historical_copy_egg_summon',state) if op[0]=='historical_copy_egg_attack' else ('historical_copy_enemy_hand',state)
  return summon,(('historical_copy_bound_attack',state,'lowest' if op[0]=='historical_copy_egg_attack' else 'recruited'),)
 if op[0]=='historical_copy_bound_attack':
  owner=ctx['owner'];state=op[1]
  source=live(game,state.get('uid')) if op[2]=='lowest' else ctx.get('source')
  target=game._force_target(owner,'lowest') if op[2]=='lowest' else state.get('uid')
  return game._force_split(('force_pair',source.uid,target),ctx) if source is not None and target else (('batch30_noop',),())
 if op[0]=='historical_copy_sivara':
  memory=getattr(ctx.get('physical_card'),'_historical_held_spell_memory',())
  operations=tuple(('historical_copy_spell_delivery',dict(card=row['card']),'hand') for row in memory[:3]) if len(memory)>=3 else ()
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_hedra':
  from .generation_cards import board_pool
  memory=getattr(ctx.get('physical_card'),'_historical_held_spell_memory',())
  requests=[board_pool(pool(card_type='MINION',minimum=row['cost'],maximum=row['cost'])) for row in memory]
  for request in set(requests):game._generation_candidates(request,ctx['owner'])
  operations=tuple(random_cards(request,destination='board') for request in requests)
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_copy_crewmates':
  p=game.players[ctx['owner']];operations=[];seen=set()
  for uid in ctx.get('hand_neighbors',()):
   card=next((c for c in p.hand if c.uid==uid),None)
   if card is None or card.card_id not in CREWMATES:continue
   index=p.hand.index(card)
   # Follow the connected run on both sides of the removed played card.
   for direction in (-1,1):
    cursor=index
    while 0<=cursor<len(p.hand) and p.hand[cursor].card_id in CREWMATES:
     selected=p.hand[cursor]
     if selected.uid not in seen:seen.add(selected.uid);operations.append(('historical_copy_recruit_uid','hand',selected.uid))
     cursor+=direction
  return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_evolve_adjacent':
  owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
  if source not in p.minions:return ('batch30_noop',),()
  index=p.board.index(source);victims=[p.board[i] for i in (index-1,index+1) if 0<=i<len(p.board) and p.board[i] in p.minions and p.board[i].health>0]
  from .transformations import evolve_pool
  for victim in victims:game._generation_candidates(evolve_pool(game._card_stat(victim,'cost',victim.owner),op[1]),owner)
  operations=tuple(('historical_copy_evolve_uid',m.uid,op[1]) for m in victims)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_treespeaker':
  from .historical_tribal_batches import TREANTS
  operations=tuple(('historical_copy_literal_uid',m.uid,'TRL_341t') for m in game.players[ctx['owner']].minions if m.card_id in TREANTS and m.health>0)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_enemy_turn_summon':
  return game._split_fixed_summon(('summon',op[1],1),ctx) if game.current!=ctx['owner'] else (('batch30_noop',),())
 if op[0]=='historical_copy_enemy_recruit':
  return ('historical_copy_recruit_other',1-ctx['owner']),()
 if op[0] in ('historical_copy_maxima','historical_copy_oblivitron'):
  state={};maxima=op[0]=='historical_copy_maxima'
  filters=() if maxima else (('tribe','eq','MECHANICAL'),)
  follow=('historical_copy_recruited_attack',state) if maxima else ('historical_copy_recruited_death',state)
  tail=(follow,('historical_copy_recruited_kill',state)) if maxima else (follow,)
  return ('historical_copy_recruit_one','deck' if maxima else 'hand',filters,None,state),tail
 if op[0]=='historical_copy_recruited_attack':
  uid=op[1].get('uid');minion=live(game,uid)
  if minion is None:return ('batch30_noop',),()
  return game._force_split(('force_pair',uid,game.hero_id(1-ctx['owner'])),ctx)
 if op[0]=='historical_copy_recruit_hand_all':
  owner=ctx['owner'];values=[c for c in game.players[owner].hand if game._card_data(c)['type']=='MINION' and (has_tribe(game._card_data(c),'DRAGON') if op[1]=='dragon' else not game._started_in_deck(c,owner))]
  operations=tuple(('historical_copy_recruit_uid','hand',c.uid) for c in values)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_mana_cyclone':
  count=len(game.players[ctx['owner']].spells_turn)
  return game._split_fixed_summon(random_cards(pool(card_type='SPELL',classes='MAGE'),count),ctx) if count else (('batch30_noop',),())
 if op[0]=='historical_copy_power_threshold':
  if getattr(game.players[ctx['owner']],'historical_power_damage_total',0)<op[1]:return ('batch30_noop',),()
  operation=('area_damage','enemies',10) if op[2]=='damage' else ('summon','EX1_298',1)
  return game._split_fixed_summon(operation,ctx)
 if op[0]=='historical_copy_friendly_spell_history':
  values=deepcopy(getattr(game.players[ctx['owner']],'_historical_friendly_target_spells',()))
  operations=tuple(('historical_copy_spell_delivery',dict(card=card),'hand') for card in values)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_copy_quickdraw_self':
  if getattr(ctx.get('physical_card'),'_hand_entry_turn',None)==game.turn:return game._split_fixed_summon(('copy_self_right',1),ctx)
  return ('batch30_noop',),()
 if op[0]=='historical_copy_barista':
  source=ctx.get('source');donors=[deepcopy(m) for m in game.players[ctx['owner']].minions if m is not source and m.health>0 and 'BATTLECRY' in game._card_data(m).get('mechanics',[])]
  operations=tuple(('historical_copy_target_snapshot',m,'hand',1,None,None,None,False) for m in donors)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0] in ('historical_copy_healed_self','historical_copy_corpse_self'):
  owner=ctx['owner'];player=game.players[owner]
  if op[0]=='historical_copy_healed_self':allowed=getattr(player,'historical_healing_done_total',0)>=5
  else:
   allowed=player.corpses>=op[1]
   if allowed:game._spend_corpses(owner,op[1])
  return game._split_fixed_summon(('copy_self_right',1),ctx) if allowed else (('batch30_noop',),())
 if op[0]=='historical_copy_devour_enemy':
  enemies=[m for m in game.players[1-ctx['owner']].minions if m.health>0]
  if not enemies:return ('batch30_noop',),()
  victim=game.rng.choice(enemies)
  return ('historical_copy_kill_bound',victim.uid),(('historical_copy_devour_gain',victim.attack,victim.health),)

 if op[0]=='historical_copy_target_all':
  donor=live(game,ctx.get('target',0))
  if donor is None:return ('batch30_noop',),()
  snapshot=deepcopy(donor)
  return ('historical_copy_target_snapshot',snapshot,'hand',1,None,None,None,False),(('historical_copy_target_snapshot',snapshot,'deck',1,None,None,None,False),('historical_copy_snapshot',snapshot,None,None))

 if op[0]=='historical_copy_enemy_generate':
  game._generation_candidates(op[1],1-ctx['owner'])
  return ('replay_context',(('generate_random',op[1],op[2],op[3],()),),dict(ctx,owner=1-ctx['owner'])),()
 if op[0]=='historical_copy_fill_both':
  owner=ctx['owner'];ops=[]
  for recipient in (owner,1-owner):
   count=max(0,7-len(game.players[recipient].board))
   if count:ops.append(('replay_context',(('summon',op[1],count),),dict(ctx,owner=recipient)))
  return (ops[0],tuple(ops[1:])) if ops else (('batch30_noop',),())
 if op[0]=='historical_copy_dragons_self':
  count=sum(has_tribe(game._card_data(c),'DRAGON') for c in game.players[ctx['owner']].hand)
  return game._split_fixed_summon(('copy_self_right',count),ctx)
 if op[0]=='historical_copy_watch_posts':
  counts=getattr(game.players[ctx['owner']],'historical_summoned_ids',{})
  count=sum(counts.get(cid,0) for cid in ('BAR_074','BAR_075','BAR_076'))
  return game._split_fixed_summon(('summon','BAR_077t',count),ctx)
 if op[0]=='historical_copy_group':
  p=game.players[ctx['owner']];source=ctx.get('source')
  if source not in p.minions:return ('batch30_noop',),()
  if op[1]=='adjacent':
   index=p.board.index(source);donors=[p.board[i] for i in (index-1,index+1) if 0<=i<len(p.board) and p.board[i] in p.minions]
  else:donors=[m for m in p.minions if m is not source]
  operations=tuple(('historical_copy_snapshot',deepcopy(m),op[2],op[3]) for m in donors)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 return None


def execute(game,op,ctx):
 if op[0]=='historical_scythe_discover':
  from .historical_scythe import execute as scythe_execute
  return scythe_execute(game,op,ctx)
 if op[0] in ('historical_zephrys_begin','historical_zephrys_wish'):
  from .historical_zephrys import execute as zephrys_execute
  return zephrys_execute(game,op,ctx)
 if op[0]=='historical_wisdomball_wear':
  from .historical_wisdomball import execute as wisdomball_execute
  return wisdomball_execute(game,op,ctx)
 if op[0].startswith('historical_ungoro_'):
  from .historical_ungoro_pack_dependencies import execute as ungoro_execute
  return ungoro_execute(game,op,ctx)
 if op[0] in ('historical_elise_shuffle','historical_elise_open'):
  from .historical_elise_pack import execute as elise_execute
  return elise_execute(game,op,ctx)
 if op[0].startswith('historical_tour_'):
  from .historical_dreamplanner import execute as tour_execute,legacy_effect
  return tour_execute(game,op,ctx) or legacy_effect(game,op,ctx)
 if op[0] in ('historical_eudora_start','historical_eudora_reward'):
  from .historical_eudora import execute as eudora_execute
  return eudora_execute(game,op,ctx)
 if op[0]=='historical_zilliax_validate':return historical_zilliax.execute(game,op,ctx)
 if op[0]=='historical_holmes_begin':return historical_holmes.execute(game,op,ctx)
 if op[0].startswith('historical_tavish_'):return historical_tavish.execute(game,op,ctx)
 if op[0].startswith('historical_ignis_'):return historical_ignis_crafting.execute(game,op,ctx)
 if op[0].startswith('historical_valeera_'):return historical_valeera.execute(game,op,ctx)
 if op[0]=='historical_reno_poof':return historical_amazing_reno.execute(game,op,ctx)
 if op[0]=='historical_devout_heal':return historical_devout.execute(game,op,ctx)
 if op[0]=='historical_boom_rush':return historical_mad_genius.execute(game,op,ctx)
 if op[0].startswith('historical_brukan_'):return historical_brukan.execute(game,op,ctx)
 if op[0]=='historical_arcane_burst_after':return historical_replay_heroes.execute(game,op,ctx)
 if op[0]=='historical_etc_discover':return historical_etc.execute(game,op,ctx)
 if op[0]=='historical_scabbs_return':return historical_scabbs.execute(game,op,ctx)
 if op[0].startswith('historical_jaina_'):return historical_jaina.execute(game,op,ctx)
 if op[0]=='historical_frozen_anduin':return historical_frozen_heroes.execute(game,op,ctx)
 if op[0].startswith('historical_rhyssa_'):return historical_rhyssa.execute(game,op,ctx)
 if op[0]=='historical_harvester_steal':return historical_harvester.execute(game,op,ctx)
 if op[0].startswith(('historical_guff_','historical_cariel_')):return historical_guff_cariel.execute(game,op,ctx)
 if op[0].startswith('historical_late_'):return historical_late_heroes.execute(game,op,ctx)
 if op[0]=='historical_maestra_reveal':
  historical_masquerade.reveal(game,ctx['owner']);return True
 if op[0].startswith('historical_reckless_'):return historical_reckless_power.execute(game,op,ctx)
 if op[0].startswith('historical_dark_'):return historical_dark_heroes.execute(game,op,ctx)
 if op[0].startswith('historical_ebon_'):return historical_ebon_heroes.execute(game,op,ctx)
 if op[0]=='historical_lens_open':
  from .historical_galaxy_lens import execute as lens_execute
  return lens_execute(game,op,ctx)
 if op[0]=='historical_uluu_refresh':
  from .historical_uluu import execute as uluu_execute
  return uluu_execute(game,op,ctx)
 if op[0].startswith('historical_student_spell_'):return historical_student_spells.execute(game,op,ctx)
 if op[0].startswith('historical_student_'):return historical_transfer_student.execute(game,op,ctx)
 if op[0].startswith('historical_outcome_'):return historical_student_outcomes.execute(game,op,ctx)
 if op[0].startswith('historical_equipment_'):return historical_student_equipment.execute(game,op,ctx)
 if op[0].startswith('historical_harmonic_'):return historical_harmonics.execute(game,op,ctx)
 if op[0].startswith('historical_damage_'):return historical_damage_spells.execute(game,op,ctx)
 if op[0].startswith('historical_summoning_'):return historical_summoning_spells.execute(game,op,ctx)
 if op[0].startswith('historical_forge_spell_'):return historical_forge_spells.execute(game,op,ctx)
 if op[0].startswith('historical_discover_'):return historical_discover_spells.execute(game,op,ctx)
 if op[0].startswith('historical_movement_'):return historical_movement_spells.execute(game,op,ctx)
 if op[0].startswith('historical_death_spell_'):return historical_death_spells.execute(game,op,ctx)
 if op[0].startswith('historical_timed_'):return historical_timed_spells.execute(game,op,ctx)
 if op[0].startswith('historical_secret_v2_'):return historical_secret_events.execute(game,op,ctx)
 if op[0].startswith('historical_misc_'):return historical_misc_spells.execute(game,op,ctx)
 if op[0].startswith('historical_bottle_'):return historical_bottle_spells.execute(game,op,ctx)
 if op[0].startswith('historical_location_timed_'):return historical_location_timed.execute(game,op,ctx)
 if op[0].startswith('historical_secret_v3_'):return historical_secret_v3.execute(game,op,ctx)
 if op[0].startswith('historical_utility_'):return historical_utility_spells.execute(game,op,ctx)
 if op[0].startswith('historical_volley_'):return historical_volley_spells.execute(game,op,ctx)
 if op[0] in ('historical_held_spellstone_buff','historical_held_seedling_tick'):return historical_held_upgrades.execute(game,op,ctx)
 if op[0].startswith('historical_music_'):return historical_music_spells.execute(game,op,ctx)
 if op[0].startswith('historical_lingering_'):return historical_lingering_spells.execute(game,op,ctx)
 if op[0].startswith('historical_change_'):return historical_change_spells.execute(game,op,ctx)
 if op[0].startswith('historical_growing_weapon_'):return historical_growing_weapons.execute(game,op,ctx)
 if op[0].startswith('historical_bonus_'):return historical_literal_bonus.execute(game,op,ctx)
 if op[0].startswith('historical_physical_'):return historical_physical_spells.execute(game,op,ctx)
 if op[0].startswith('historical_state_'):return historical_state_spells.execute(game,op,ctx)
 if op[0].startswith('historical_attack_weapon_'):return historical_attack_weapons.execute(game,op,ctx)
 if op[0].startswith('historical_offer_'):return historical_offer_spells.execute(game,op,ctx)
 if op[0].startswith('historical_resolution_'):return historical_resolution_spells.execute(game,op,ctx)
 if op[0].startswith('historical_zone_'):return historical_zone_spells.execute(game,op,ctx)
 if op[0].startswith('historical_numeric_'):return historical_numeric_spells.execute(game,op,ctx)
 if op[0]=='historical_eonar_prepare':
  game.players[ctx['owner']].historical_eonar_pending=True
  return True
 if op[0]=='historical_headmaster_one':
  from .historical_headmaster import execute as headmaster_execute
  return headmaster_execute(game,op,ctx)
 if op[0].startswith('historical_mint_'):return historical_mint_cards.execute(game,op,ctx)
 if op[0].startswith('historical_rock_'):return historical_rock_duel.execute(game,op,ctx)
 if op[0].startswith('historical_horror_'):return historical_horror_crafting.execute(game,op,ctx)
 if op[0].startswith('historical_golem_'):return historical_golem_crafting.execute(game,op,ctx)
 if op[0].startswith('historical_potion_'):return historical_potion_crafting.execute(game,op,ctx)
 name=op[0]
 if name.startswith('historical_ship_'):return historical_starships.execute(game,op,ctx)
 if name.startswith('historical_excavate_'):return historical_excavate.execute(game,op,ctx)
 if not name.startswith('historical_copy_'):return False
 owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner];source=ctx.get('source');target=live(game,ctx.get('target',0))
 if name=='historical_copy_trade_finish':
  card=ctx['trade_card']
  p.deck.insert(game.rng.randrange(len(p.deck)+1),card)
  game._refresh_auras()
  game._record_deck_insertion(owner,owner,1,'trade',cards=(card,))
  game._log('trade',player=owner,card=card.card_id)
  from .historical_trade_spell_finish import after_trade
  after_trade(game,owner,card)
 elif name=='historical_copy_remornia_equip':
  from .historical_physical_forms import equip_remornia
  equip_remornia(game,source)
 elif name=='historical_copy_remornia_return':
  from .historical_physical_forms import return_remornia
  return_remornia(game,owner,ctx.get('weapon_uid'))
 elif name=='historical_copy_sanc_location':
  from .historical_physical_forms import make_sanc_location
  make_sanc_location(game,source)
 elif name=='historical_copy_sanc_activate':
  from .historical_physical_forms import activate_sanc
  activate_sanc(game,source,target)
 elif name=='historical_copy_xortoth':
  from .pools import require_fixed_cards
  require_fixed_cards(STAR_IDS,game.cards)
  first=game._enter_hand(owner,Card(game._new_id(),STAR_IDS[0]))
  if first is not None:
   p.hand.remove(first);p.hand.insert(0,first)
  game._enter_hand(owner,Card(game._new_id(),STAR_IDS[1]))
  game._refresh_auras()
 elif name=='historical_copy_star_unplayable':
  from engine.cards import UnsupportedCard
  raise UnsupportedCard('Stars resolve only by physical hand adjacency, not card play or casting')
 elif name=='historical_copy_star_collide':
  pair=op[1];pending=getattr(game,'_historical_star_pending',set());pending.difference_update(pair)
  indices=[next((i for i,card in enumerate(p.hand) if card.uid==uid),None) for uid in pair]
  if all(index is not None for index in indices) and abs(indices[0]-indices[1])==1:
   cards=[p.hand[index] for index in indices]
   if {card.card_id for card in cards}==set(STAR_IDS):
    # Remove both physical objects before publishing any damage; duplicate
    # queued checks cannot consume the same Star a second time.
    for card in cards:p.hand.remove(card)
    for card in cards:game._zone_card_removed(owner,card,'hand','destroy')
    game._refresh_auras()
    origin=next(card for card in cards if card.card_id==STAR_IDS[0])
    context=dict(owner=owner,source=None,target=0,card_id=STAR_IDS[0],physical_card=origin,spell=True,bonus=game._spell_damage(owner,STAR_IDS[0],origin),lifesteal=False)
    game._effect(('area_damage','enemies',5),context)
 elif name=='historical_copy_amulet_vendor':
  from .pools import require_fixed_cards
  require_fixed_cards(tuple(AMULET_PAIRS)+tuple(AMULET_PAIRS.values()),game.cards)
  offered=game.rng.sample(list(AMULET_PAIRS),3)
  if game.pending_choice is not None:raise ValueError('Cannot overwrite Amulet Discover')
  game.pending_choice=dict(owner=owner,kind='historical_amulet_vendor',options=[dict(card_id=cid) for cid in offered],_automatic=bool(ctx.get('automatic_choices',False)))
  game.phase='choice'
 elif name=='historical_copy_passions':
  if target is not None and target.owner!=owner and len(p.board)<7:
   original=target.owner;token=game._new_id()
   game._add_control_layer(target,owner,deadline_owner=original,due=game.players[original].turns_taken+1,token=token,ready=True,end_timer=True)
   if op[1]:
    delta=1-target.attack;game._adjust_minion_attack(target,delta);target.temporary_attack+=delta
   game._schedule_turn_effect(game.current,'end',0,1,(('historical_copy_madness_return',token),),source_card_id=ctx.get('card_id','VAC_959t01t'))
   game._refresh_auras()
 elif name=='historical_copy_amulet_critter':
  from .generation_cards import board_pool
  values=game._generation_candidates(board_pool(pool(card_type='MINION',minimum=4,maximum=4)),owner)
  if values and len(p.board)<7:
   game._summon(owner,game.rng.choice(values),entry_origin='effect',entry_site='amulet_of_critters',entry_source=source,entry_keywords=('TAUNT','CANT_ATTACK') if op[1] else ('TAUNT',))
 elif name=='historical_copy_amulet_discount':
  for card in p.hand:
   if not op[1] or game._card_data(card)['type']!='SPELL':card.cost_delta=getattr(card,'cost_delta',0)-(1)
 elif name=='historical_copy_tracking_create':
  state=op[1];card=Card(game._new_id(),game.rng.choice(state['legendary']))
  entered=game._enter_hand(owner,card)
  if entered is not None:state['cards'].append(entered)
 elif name=='historical_copy_tracking_transform':
  state=op[1]
  for card in state['cards']:
   if any(value is card for value in p.hand):game._b60_transform_card(card,game.rng.choice(state['common']))
  game._refresh_auras()
 elif name=='historical_copy_mobility_discard':
  cards=[state['card'] for state in op[1] if state.get('card') is not None and any(value is state['card'] for value in p.hand)]
  if cards:game._discard_cards(owner,game.rng.sample(cards,min(2,len(cards))))
 elif name in ('historical_copy_bob_offer','historical_copy_plunder_offer'):
  from .pools import require_fixed_cards
  plunder=name=='historical_copy_plunder_offer'
  if plunder:
   count=getattr(p,'historical_summoned_tribes',{}).get('PIRATE',0)
   count-=int(source is not None and has_tribe(game._card_data(source),'PIRATE'))
   if count<7:return True
  ids=PLUNDER_ACTIONS if plunder else BOB_ACTIONS
  require_fixed_cards(ids,game.cards)
  if game.pending_choice is not None:raise ValueError('Cannot overwrite action choice')
  game.pending_choice=dict(owner=owner,kind='historical_action_menu',options=[dict(card_id=cid) for cid in ids],_context=dict(ctx),_automatic=bool(ctx.get('automatic_choices',False)))
  game.phase='choice'
 elif name=='historical_copy_bob_coins':
  for _ in range(3):game._add(1-owner,'GAME_005')
 elif name=='historical_copy_bob_copies':
  card=op[1].get('card')
  if card is not None:
   for _ in range(2):game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 elif name=='historical_copy_plunder_one':
  zone=getattr(q,op[1])
  if zone:
   index=game.rng.randrange(len(zone))
   value=zone.pop(index);card=value if isinstance(value,Card) else Card(game._new_id(),value)
   game._enter_hand(owner,card);game._refresh_auras()
 elif name=='historical_copy_plunder_ship':
  candidates=[minion for minion in q.minions if minion.health>0]
  if candidates and len(p.board)<7:
   attack=max(minion.attack for minion in candidates);minion=game.rng.choice([m for m in candidates if m.attack==attack])
   q.board.remove(minion);minion.owner=owner;minion.summoned_turn=game.turn;minion.attacks=0;p.board.append(minion);game._refresh_auras()
 elif name=='historical_copy_buff_imps':
  from .historical_imps import is_imp
  for minion in p.minions:
   if minion.health>0 and is_imp(game,minion):game._buff(minion,op[1],op[2])
 elif name=='historical_copy_grunty_summon':
  if len(p.board)<7:
   state=op[1];cid=game.rng.choice(state['candidates']);before={m.uid for m in p.all_minions}
   game._summon(owner,cid,entry_origin='effect',entry_site='grunty',entry_source=source)
   state['summoned'].extend(m.uid for m in p.all_minions if m.uid not in before and m.card_id==cid)
 elif name=='historical_copy_grunty_offer':
  state=op[1]
  while state['index']<len(state['summoned']):
   attacker=live(game,state['summoned'][state['index']])
   if attacker is not None and attacker.owner==owner:break
   state['index']+=1
  if state['index']<len(state['summoned']):
   targets=[uid for uid in game._targets_for('SC_013',owner,'enemy_minion') if uid>0]
   if targets:
    if game.pending_choice is not None:raise ValueError('Grunty cannot overwrite a pending choice')
    game.pending_choice=dict(owner=owner,kind='historical_grunty',options=[dict(card_id=live(game,uid).card_id,target_uid=uid) for uid in targets],_state=state,_context=dict(ctx),_automatic=bool(ctx.get('automatic_choices',False)))
    game.phase='choice'
 elif name=='historical_copy_ceaseless':
  for player in game.players:
   for minion in player.minions:
    if minion is not source:minion.health=0
 elif name=='historical_copy_cheese_tick':
  card=next((card for card in p.hand if card.uid==op[1] and card.card_id=='VAC_955t'),None)
  if card is not None:
   state=game._b60_state(card);state['historical_cheese_level']=min(10,state.get('historical_cheese_level',1)+1)
 elif name=='historical_copy_shaffar':
  values=[card for card in p.hand if game._card_data(card)['type']=='MINION']
  if values:
   card=game.rng.choice(values);state=game._b60_state(card)
   if not state.get('historical_shaffar_beacon'):
    _saidan_add(card,'attack_bonus',3);_saidan_add(card,'health_bonus',3);state['historical_shaffar_beacon']=True
 elif name in ('historical_copy_epoch','historical_copy_future_location'):
  from .pools import require_fixed_cards
  ids=tuple(EPOCH_RULES) if name=='historical_copy_epoch' else FUTURE_LOCATIONS
  require_fixed_cards(ids,game.cards)
  offered=list(ids) if name=='historical_copy_epoch' else game.rng.sample(list(ids),3)
  if game.pending_choice is not None:raise ValueError('Cannot overwrite historical time choice')
  game.pending_choice=dict(owner=owner,kind='historical_epoch' if name=='historical_copy_epoch' else 'historical_future_location',options=[dict(card_id=cid) for cid in offered],_context=dict(ctx),_automatic=bool(ctx.get('automatic_choices',False)))
  game.phase='choice'
 elif name=='historical_copy_epoch_shuffle':
  cards=[Card(game._new_id(),cid) for cid in EPOCH_RULES if cid!=op[1]]
  p.deck.extend(cards);game.rng.shuffle(p.deck)
  game._record_deck_insertion(owner,owner,len(cards),'shuffle',cards=cards)
  game._refresh_auras()
 elif name=='historical_copy_lordaeron':
  if target is not None:
   attack=target.attack
   for player in game.players:
    for minion in player.minions:
     if minion.attack<attack:minion.health=0
 elif name=='historical_copy_xenedar':p.historical_murmuring_turn=game.turn
 elif name=='historical_copy_korune_swap':
  first=op[1].get('card');second=op[2].get('card')
  if first is not None and second is not None:
   costs=(game._cost(first,owner),game._cost(second,owner))
   if any(card is first for card in p.hand):game._set_card_cost(first,costs[1])
   if any(card is second for card in p.hand):game._set_card_cost(second,costs[0])
 elif name=='historical_copy_temple_earth':
  if target is not None and target.owner==owner:
   donor=deepcopy(target);donor.max_health+=3;donor.health+=3
   game._summon(owner,donor.card_id,copy_from=donor,entry_origin='copy',entry_site='temple_of_earth',entry_source=target,entry_keywords=('TAUNT','CANT_ATTACK'))
 elif name=='historical_copy_cardboard':
  from .gelbin import AURA_IDS
  for card in list(p.hand)+list(p.deck):
   if card.card_id in AURA_IDS:
    state=game._b60_state(card);state['aura_duration_delta']=state.get('aura_duration_delta',0)+1
  for effect in p.scheduled_effects:
   if effect.get('source_card_id') in AURA_IDS and effect['remaining']>0:effect['remaining']+=1
  p.end_repeat_expiries=[end+1 if end>=p.turns_taken else end for end in p.end_repeat_expiries]
  for player in game.players:
   for effect in player.timed_cost_increases:
    if effect.get('aura_owner')==owner and effect.get('source_card_id') in AURA_IDS and effect['end']>=game.turn:effect['end']+=2
 elif name=='historical_copy_ichman_recruit':
  before={m.uid for m in p.all_minions}
  minion=game._recruit_from_zone(owner,'deck',(('tribe','eq','BEAST'),),keyword='RUSH',site='ichman')
  if minion is not None:
   for body in p.all_minions:
    if body.uid not in before and body.card_id==minion.card_id:
     body.keywords.add('RUSH');body.rule_state['historical_ichman_turn']=game.turn
 elif name=='historical_copy_whelp_summon':
  before={m.uid for m in p.all_minions}
  game._summon(owner,'TTN_727t',entry_origin='effect',entry_site='thorignir',entry_source=source)
  op[1]['created']=[m.uid for m in p.all_minions if m.uid not in before and m.card_id=='TTN_727t']
 elif name=='historical_copy_kologarn_grab':
  victim=live(game,ctx['event']['target'])
  if source is not None and victim is not None:
   if len(p.hand)>=getattr(p,'hand_capacity',10):victim.health=0
   else:
    key=source.rule_state.setdefault('historical_kologarn_key',source.uid)
    card=game._fresh_replay_card(victim);game._carry_origin(victim,card)
    links=set(getattr(card,'_historical_kologarn_links',()))|{key}
    card._historical_kologarn_links=tuple(sorted(links))
    game.players[victim.owner].board.remove(victim)
    game._enter_hand(owner,card)
    game._log('kologarn_grab',player=owner,card=card.card_id)
   game._refresh_auras()
 elif name=='historical_copy_kologarn_return':
  key=getattr(source,'rule_state',{}).get('historical_kologarn_key')
  if key is not None:
   cards=[card for card in p.hand if key in getattr(card,'_historical_kologarn_links',())]
   for card in cards:
    p.hand.remove(card)
    card._historical_kologarn_links=tuple(link for link in card._historical_kologarn_links if link!=key)
    game._enter_hand(1-owner,card)
   game._refresh_auras()
 elif name=='historical_copy_tnt_zone':
  zone=op[1]
  if zone in ('hand','deck'):
   values=[card for card in getattr(p,zone) if card.card_id!='WW_372t']
   if values:
    card=game.rng.choice(values);getattr(p,zone).remove(card)
    game._zone_card_removed(owner,card,zone,'destroy')
    game._log('tnt_destroy',player=owner,zone=zone,card=card.card_id)
  elif zone=='board':
   values=[m for m in p.minions if m.health>0]+list(p.locations)
   if values:
    entity=game.rng.choice(values)
    if entity in p.locations:game._remove_location(entity)
    else:entity.health=0
    game._log('tnt_destroy',player=owner,zone=zone,card=entity.card_id)
  game._refresh_auras()
 elif name=='historical_copy_chaos_gaze':
  available=max(0,min(q.mana_capacity,q.max_mana+1)-q.overload_next)
  values=[card for card in q.hand if game._cost(card,1-owner)<=available]
  if values:
   card=game.rng.choice(values)
   game._b60_state(card)['historical_chaos_gaze_due']=q.turns_taken+1
   game._log('chaos_gaze',player=owner,recipient=1-owner)
 elif name=='historical_copy_chaos_expire':
  card=next((card for card in p.hand if card.uid==op[1]),None)
  if card is not None and getattr(card,'rule_state',{}).get('historical_chaos_gaze_due',p.turns_taken+1)<=p.turns_taken:
   game._discard_card(owner,card)
 elif name=='historical_copy_goldbeard_summon':
  state=op[1];donor=state['donor'];before={m.uid for m in p.all_minions}
  game._summon(owner,donor.card_id,copy_from=donor,entry_origin='goldbeard',entry_site='goldbeard',entry_source=source)
  state['created']=[m.uid for m in p.all_minions if m.uid not in before and m.card_id==donor.card_id]
 elif name=='historical_copy_goldbeard_die':
  minion=game._force_live(op[1])
  if minion is not None:minion.health=0
 elif name=='historical_copy_stalladris':
  for card in choose_branch_cards(game,owner,ctx['event']['card']):game._enter_hand(owner,card)
 elif name=='historical_copy_jerry_finish':
  card=op[1].get('card')
  if card is not None and any(held is card for held in p.hand):
   children=choose_branch_cards(game,owner,card)
   p.hand.remove(card)
   for child in children:game._enter_hand(owner,child)
   game._refresh_auras()
 elif name=='historical_copy_botface':
  from .pools import require_fixed_cards
  from .cards import RULES as all_rules
  require_fixed_cards(BOTFACE_MINIS,game.cards)
  missing=set(BOTFACE_MINIS)-set(all_rules)
  if missing:
   from engine.cards import UnsupportedCard
   raise UnsupportedCard('Botface Mini rules missing: '+', '.join(sorted(missing)))
  for _ in range(2):game._add(owner,game.rng.choice(BOTFACE_MINIS))
 elif name=='historical_copy_wrench':
  values=[m for m in p.minions if m.health>0 and has_tribe(game._card_data(m),'MECHANICAL')]
  if values:
   minion=game.rng.choice(values)
   game._rule_events.append(('captured_effects',dict(operations=tuple(game._death_operations(minion)),context=dict(owner=owner,source=minion,target=0,bonus=0,lifesteal=False)),[]))
 elif name=='historical_copy_stitch':
  pools=tuple(tuple(game._generation_discover_candidates(pool(card_type='MINION',minimum=cost,maximum=cost,classes='own_or_neutral'),ctx)) for cost in (5,3,1))
  offer_stitch(game,owner,dict(pools=pools,selected=(),source=source,automatic=bool(ctx.get('automatic_choices',False))))
 elif name=='historical_copy_stitched_summon':
  chain=op[1]
  if chain:
   before={m.uid for player in game.players for m in player.all_minions}
   game._summon(owner,chain[0],entry_origin='deathrattle',entry_site='stitchensew',entry_source=source)
   if len(chain)>1:
    for minion in p.all_minions:
     if minion.uid not in before and minion.card_id==chain[0]:
      minion.attached_death_effects.append(('historical_copy_stitched_summon',tuple(chain[1:])))
      minion.keywords.add('DEATHRATTLE')
 elif name=='historical_copy_griftah':
  candidates=game._generation_discover_candidates(pool(classes='own_or_neutral'),ctx)
  offer_griftah(game,owner,dict(candidates=tuple(candidates),selected=(),automatic=bool(ctx.get('automatic_choices',False))))
 elif name=='historical_copy_guess':offer_guess(game,ctx,op[1])
 elif name=='historical_copy_shuffle_extra':
  event=ctx['event'];recipient=event['destination']
  card=game._copy_card(event['card'],source_owner=recipient)
  deck=game.players[recipient].deck;deck.insert(game.rng.randrange(len(deck)+1),card)
  game._record_deck_insertion(recipient,owner,1,'shuffle',cards=(card,),suppress_elekk=True)
  game._refresh_auras()
 elif name=='historical_copy_shuffle_hand':
  game._enter_hand(owner,game._copy_card(ctx['event']['card'],source_owner=owner),creator_uid=getattr(source,'uid',None))
 elif name=='historical_copy_future_board':
  values=[]
  # Freeze both boards before aura removal; physical objects retain links,
  # damage, silence, attached effects and private state while set aside.
  for recipient,player in enumerate(game.players):
   for index,minion in enumerate(list(player.board)):
    if minion not in player.minions or minion.health<=0 or minion is source:continue
    values.append((recipient,index,minion))
  for recipient,index,minion in values:
   game.players[recipient].board.remove(minion)
   game._adjust_minion_attack(minion,-minion.aura_attack)
   minion.max_health-=minion.aura_health
   minion.health=min(minion.health,minion.max_health)
   minion.aura_attack=minion.aura_health=0
  key=game._stored_save(owner,'future_board',values)
  game._schedule_turn_effect(owner,'start',2,1,(('historical_copy_future_return',key),),source_card_id='RLK_919')
  game._refresh_auras()
  game._log('future_board_depart',player=owner,count=len(values))
 elif name=='historical_copy_future_one':
  recipient,position,minion=game._stored_payloads[op[1]]['values'][op[2]]
  if len(game.players[recipient].board)<7:
   game._summon_one(recipient,minion.card_id,copy_from=minion,entry_origin='future',entry_site='historical_copy.future_return',entry_source=minion)
  else:game._log('future_board_overflow',player=recipient,card=minion.card_id,entity=minion.uid)
 elif name=='historical_copy_future_clear':
  game._stored_payloads.pop(op[1],None)
 elif name=='historical_copy_pack_suitcase':
  packed=tuple(p.deck.pop() for _ in range(min(2,len(p.deck))))
  token=Card(game._new_id(),'VAC_935t2' if len(packed)==1 else 'VAC_935t')
  token._historical_suitcase_cards=deepcopy(packed)
  game._refresh_auras();game._enter_hand(owner,token)
 elif name=='historical_copy_unpack_suitcase':
  physical=ctx.get('physical_card')
  for card in getattr(physical,'_historical_suitcase_cards',()):game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 elif name=='historical_copy_fortunes':
  for _ in range(2):
   card=Card(game._new_id(),'VAC_420t');card._historical_mirror_mode='fortune'
   apply_hand_mirror(game,owner,card,p.deck[-1] if p.deck else None)
   game._enter_hand(owner,card)
 elif name=='historical_copy_permanent_mirage':
  from .identities import canonical_identity
  identities=[canonical_identity(game.cards[cid],game.cards) for cid in p.starting_deck]
  if len(identities)==len(set(identities)):
   card=Card(game._new_id(),'WW_337t');card._historical_mirror_mode='mirage'
   roll_mirage(game,owner,card);game._enter_hand(owner,card)
 elif name=='historical_copy_mirage_tick':
  card=next((card for card in p.hand if card.uid==op[1] and getattr(card,'_historical_mirror_mode',None)=='mirage'),None)
  if card is not None:roll_mirage(game,owner,card)
 elif name=='historical_copy_blank_mirror':
  raise ValueError('A blank Fortune or Mirage has no playable copied card')
 elif name=='historical_copy_party_recruit':
  minion=game._recruit_from_zone(owner,'hand',(),site='party_crasher')
  op[1]['uid']=minion.uid if minion is not None else None
 elif name=='historical_copy_okani_offer':
  if source is not None and source in p.minions:
   available=[kind for kind in ('MINION','SPELL') if kind not in source.rule_state.get('historical_okani_counters',())]
   if available:
    from engine.cards import UnsupportedCard
    if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Okani secret choice')
    game.pending_choice=dict(owner=owner,kind='historical_okani',source_uid=source.uid,options=[dict(card_id='TSC_032',label=kind.title()+' Counter',counter_kind=kind) for kind in available],_automatic=bool(ctx.get('automatic_choices',False)))
    game.phase='choice'
 elif name=='historical_copy_gamer_first':
  if source is not None and source in p.minions:
   game.pending_choice=dict(owner=owner,kind='historical_gamer_first',source_uid=source.uid,options=gamer_options())
   game.phase='choice'
 elif name=='historical_copy_gamer_second':
  state=op[1]
  game.pending_choice=dict(owner=1-state['owner'],kind='historical_gamer_second',_game=state,options=gamer_options())
  game.phase='choice'
 elif name=='historical_copy_zok_fan':
  game._summon(owner,'ETC_386t',entry_stats=(op[1],op[2]),entry_origin='effect',entry_site='zok_fogsnout',entry_source=source)
 elif name=='historical_copy_service_ace':
  if p.hand:
   highest=max(game._cost(card,owner) for card in p.hand)
   values=[card for card in p.hand if game._cost(card,owner)==highest]
   card=game.rng.choice(values);card.cost_delta=getattr(card,'cost_delta',0)-(1)
 elif name=='historical_copy_painting':
  uid=ctx['event']['source']
  if source is not None and source.uid!=uid and source in p.minions:
   records=[record for player in game.players for record in player.death_records if record['entity'].uid==uid]
   if records:
    donor=deepcopy(records[-1]['entity']);donor.health=donor.max_health
    replace(game,source,donor)
 elif name=='historical_copy_jandice_summon':
  before={m.uid for m in p.all_minions}
  game._summon(owner,op[1],entry_origin='effect',entry_site='jandice_barov',entry_source=source)
  op[2]['members'].extend(m.uid for m in p.all_minions if m.uid not in before)
 elif name=='historical_copy_jandice_choose':
  members=[m for m in p.all_minions if m.uid in op[1]['members'] and m.health>0]
  for minion in members:minion._illusion_possible=True;minion._jandice_illusion=True
  if members:
   from engine.cards import UnsupportedCard
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Jandice secret choice')
   game.pending_choice=dict(owner=owner,kind='historical_jandice',options=[dict(card_id=m.card_id,uid=m.uid) for m in members],_automatic=bool(ctx.get('automatic_choices',False)))
   game.phase='choice'
 elif name=='historical_copy_aegwynn_death':
  p.historical_aegwynn_pending=getattr(p,'historical_aegwynn_pending',0)+1
 elif name=='historical_copy_courier':
  card=game._copy_card(ctx['event']['card'],source_owner=owner)
  game._enter_hand(owner,card,creator_uid=source.uid if source is not None else None)
 elif name=='historical_copy_shudderblock':
  p.historical_shudderblock_pending=True
 elif name=='historical_copy_kabal_potion':
  from .pools import require_fixed_cards
  from .cards import RULES as all_rules
  from engine.cards import UnsupportedCard
  require_fixed_cards(KABAL_POTIONS,game.cards)
  if any(cid not in all_rules for cid in KABAL_POTIONS):raise UnsupportedCard('Incomplete Kabal Potion family')
  game._enter_hand(owner,Card(game._new_id(),game.rng.choice(KABAL_POTIONS)))
 elif name=='historical_copy_bloodfury':
  if target is not None:game._buff(target,3,3 if has_tribe(game._card_data(target),'DEMON') else 0)
 elif name=='historical_copy_dragonfire':
  victims=[m for player in game.players for m in player.minions if m.health>0 and not has_tribe(game._card_data(m),'DRAGON')]
  with game._damage_batch():
   for minion in victims:game._deal_effect(minion.uid,5,ctx)
 elif name in ('historical_copy_madness','historical_copy_shadow_madness'):
  if target is not None and target.owner!=owner and target.attack<=(3 if name=='historical_copy_shadow_madness' else 2) and len(p.board)<7:
   original=target.owner;token=game._new_id()
   game._add_control_layer(target,owner,deadline_owner=original,due=game.players[original].turns_taken+1,token=token,ready=True,end_timer=True)
   game._schedule_turn_effect(game.current,'end',0,1,(('historical_copy_madness_return',token),),source_card_id='CFM_603')
   game._refresh_auras()
 elif name=='historical_copy_madness_return':
  game._expire_control_layers(lambda layer:layer['token']==op[1])
 elif name=='historical_copy_yrel_librams':
  from .pools import require_fixed_cards
  require_fixed_cards(YREL_LIBRAMS,game.cards)
  for cid in YREL_LIBRAMS:game._enter_hand(owner,Card(game._new_id(),cid))
 elif name=='historical_copy_justice_health':
  for minion in q.minions:minion.health=minion.max_health=1+minion.aura_health
  game._refresh_auras()
 elif name=='historical_copy_beast_deck_buff':
  for card in p.deck:
   if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'BEAST'):
    _saidan_add(card,'attack_bonus',1);_saidan_add(card,'health_bonus',1)
  game._refresh_auras()
 elif name=='historical_copy_disciple_discard':
  card=op[1]['card']
  if card in p.hand:game._discard_card(owner,card)
 elif name=='historical_copy_disciple_imp':
  game._summon(owner,'TTN_960t6',entry_stats=(3,4) if op[1] else None,entry_keywords=('TAUNT',) if op[1] else (),entry_origin='effect',entry_site='disciple_of_sargeras',entry_source=source)
 elif name=='historical_copy_onyxia_whelp':
  position=p.board.index(source)+op[1] if source in p.board else -1
  game._summon(owner,'ONY_001t',position,entry_origin='effect',entry_site='raid_boss_onyxia',entry_source=source)
 elif name=='historical_copy_sharpshooter_draw':
  game._draw(owner,predicate=lambda data:has_tribe(data,'NAGA') if op[1] else data['type']=='SPELL')
 elif name=='historical_copy_sharpshooter_switch':
  if source is not None:source.rule_state['historical_sharpshooter_spell']=op[1]
 elif name=='historical_copy_vistah_start':
  start=len(getattr(p,'_historical_cast_records',()))
  game._schedule_turn_effect(owner,'start',3,1,(('historical_copy_vistah_finish',start),),source_card_id=ctx.get('card_id','VAC_519'))
 elif name=='historical_copy_kurtrus_shot':
  values=[card for card in q.hand if game._card_data(card)['type']=='MINION']
  if values:
   card=game.rng.choice(values);state=game._b60_state(card)
   state['historical_hand_damage']=state.get('historical_hand_damage',0)+2
   game._log('hand_minion_damaged',player=1-owner,entity=card.uid,amount=2)
   if game._card_stat(card,'health',1-owner)-state['historical_hand_damage']<=0:
    q.hand.remove(card)
    game._zone_card_removed(1-owner,card,'hand','damage')
    game._log('hand_minion_removed',player=1-owner,entity=card.uid,cause='damage')
   game._refresh_auras()
 elif name=='historical_copy_copycat_wait':
  p.historical_copycat_pending=getattr(p,'historical_copycat_pending',0)+1
 elif name=='historical_copy_copycat_receive':
  game._enter_hand(owner,op[1]['card'])
 elif name=='historical_copy_twin_blades':
  if target is not None and target.owner==owner:
   # Groovy Cat improves both Attack grants; common power execution adds
   # its hero bonus separately, so the intrinsic hero grant remains one.
   amount=1+getattr(p,'historical_power_attack',0)
   game._effect(('historic_temporary_attack','target',amount,'end'),ctx)
   target.keywords.add('DIVINE_SHIELD')
  game._gain_hero_attack(owner,1);p.divine_shield=True
 elif name=='historical_copy_protoss_draw':
  allowed=PROTOSS_MINIONS if op[1]=='minion' else PROTOSS_CARDS
  candidates=[i for i,card in enumerate(p.deck) if card.card_id in allowed]
  if candidates:
   card=game._take_deck_draw(owner,game.rng.choice(candidates))
   if card is not None and any(card is held for held in p.hand) and op[2] and ctx.get('combo',False):card.cost_delta=getattr(card,'cost_delta',0)-(2)
 elif name=='historical_copy_protoss_next':
  p.cost_effects.append(dict(selector='HISTORICAL_PROTOSS_'+op[1].upper(),amount=op[2],remaining_uses=1,expires=game.turn if op[3] else None))
 elif name=='historical_copy_protoss_spell':
  from .pools import require_fixed_cards
  require_fixed_cards(PROTOSS_SPELLS,game.cards)
  game._add(owner,game.rng.choice(sorted(PROTOSS_SPELLS)))
 elif name=='historical_copy_hallucination':
  if target is not None and target.owner==owner and target.card_id in PROTOSS_MINIONS:
   snapshot=deepcopy(target)
   snapshot.rule_state['historical_hallucination_layers']=snapshot.rule_state.get('historical_hallucination_layers',0)+1
   game._summon(owner,snapshot.card_id,copy_from=snapshot,entry_origin='copy',entry_site='hallucination',entry_source=target)
 elif name=='historical_copy_photon_damage':
  victim=live(game,ctx.get('target',0));game._deal_effect(ctx.get('target',0),3,ctx)
  op[1]['killed']=victim is not None and victim.health<=0
 elif name=='historical_copy_photon_reward':
  if op[1].get('killed',False):p.historical_protoss_discount=getattr(p,'historical_protoss_discount',0)+1
 elif name=='historical_copy_templar_merge':
  played=live(game,ctx.get('event',{}).get('source',0))
  if source is not None and source in p.minions and source.health>0 and played is not None and played is not source and played.owner==owner and played.card_id in TEMPLARS:
   from .pools import require_fixed_cards
   require_fixed_cards(('SC_671t1',),game.cards)
   position=p.board.index(source)-int(p.board.index(played)<p.board.index(source))
   p.board.remove(source);p.board.remove(played)
   game._refresh_auras()
   game._summon(owner,'SC_671t1',min(position,len(p.board)),entry_origin='effect',entry_site='templar_merge',entry_source=source)
   game._log('templar_merge',player=owner,first=source.uid,second=played.uid)
 elif name=='historical_copy_mothership':
  from .pools import require_fixed_cards
  require_fixed_cards(PROTOSS_COLLECTIBLE_MINIONS,game.cards)
  game._add(owner,game.rng.choice(PROTOSS_COLLECTIBLE_MINIONS))
 elif name=='historical_copy_sentry':
  p.historical_protoss_discount=getattr(p,'historical_protoss_discount',0)+1
 elif name=='historical_copy_poison':
  from .pools import require_fixed_cards
  require_fixed_cards(HELBRIM_POISONS+('YOP_015t',),game.cards)
  game._add(owner,game.rng.choice(HELBRIM_POISONS))
 elif name=='historical_copy_weapon_poison':
  if p.weapon:
   if op[1]=='silverleaf':p.weapon['historical_silverleaf_draws']=p.weapon.get('historical_silverleaf_draws',0)+1
   elif op[1]=='paralytic':p.weapon['historical_paralytic']=True
   elif op[1]=='leeching':p.weapon['historical_leeching_until']=game.turn
 elif name=='historical_copy_silas':
  if ctx.get('automatic_choices',False) or source is not None and source.owner!=owner:
   rotate_silas(game,owner,game.rng.choice(('left','right')))
  else:
   game.pending_choice=dict(owner=owner,kind='historical_silas',options=[dict(card_id='DMF_074a',direction='left'),dict(card_id='DMF_074b',direction='right')])
   game.phase='choice'
 elif name=='historical_copy_drink':
  from .pools import require_fixed_cards
  require_fixed_cards(tuple(cid for forms in DRINK_FORMS for cid in forms),game.cards)
  game._add(owner,game.rng.choice(DRINKS))
 elif name=='historical_copy_cup_muscle':
  card=next((card for card in p.hand if card.uid==ctx.get('target') and game._card_data(card)['type']=='MINION'),None)
  if card is not None:_saidan_add(card,'attack_bonus',2);_saidan_add(card,'health_bonus',1)
 elif name=='historical_copy_divine_brew':
  uid=ctx.get('target',0)
  if uid<0:game.players[-uid-1].divine_shield=True
  elif target is not None:target.keywords.add('DIVINE_SHIELD')
 elif name=='historical_copy_atiesh_wear':
  if p.weapon and p.weapon['card_id']=='KAR_097t' and getattr(p.equipped_card,'uid',None)==op[1]:
   from .historical_arsenal_batches import lose_durability
   lose_durability(game,owner,1)
 elif name=='historical_copy_faelin':
  candidates=game._generation_candidates(pool(card_type='MINION',mechanic='COLOSSAL'),owner)
  for cid in game.rng.sample(list(candidates),min(3,len(candidates))):
   card=Card(game._new_id(),cid);p.deck.insert(0,card)
   game._log('put_bottom',player=owner,card=cid,source='TSC_067')
  game._refresh_auras()
 elif name=='historical_copy_overplanner':
  offer_overplanner(game,owner,(),bool(ctx.get('automatic_choices',False)))
 elif name=='historical_copy_sheriff':
  if p.health<=20:game._place_location(owner,'WW_359t')
 elif name=='historical_copy_azshara':
  if getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_held_casts',0)>=3:
   from .pools import require_fixed_cards
   require_fixed_cards(ANCIENT_RELICS,game.cards)
   game.pending_choice=dict(owner=owner,kind='historical_ancient_relic',options=[dict(card_id=cid) for cid in ANCIENT_RELICS],_automatic=bool(ctx.get('automatic_choices',False)))
   game.phase='choice'
 elif name=='historical_copy_xalatath_wear':
  if p.weapon and p.weapon['card_id']=='TSC_641tc' and getattr(p.equipped_card,'uid',None)==op[1]:
   from .historical_arsenal_batches import lose_durability
   lose_durability(game,owner,1)
 elif name=='historical_copy_upgrade_eruptions':
  for card in p.hand+p.deck:
   if card.card_id=='VAC_321t':
    state=game._b60_state(card);state['historical_eruption_bonus']=state.get('historical_eruption_bonus',0)+1
 elif name=='historical_copy_ouroboros':
  values=[card for card in p.hand if game._card_data(card)['type']=='MINION']
  if values:
   card=game.rng.choice(values);state=game._b60_state(card)
   state['historical_ouroboros_deaths']=state.get('historical_ouroboros_deaths',0)+1
 elif name=='historical_copy_rheastrasza':
  from .identities import canonical_identity
  identities=[canonical_identity(game.cards[cid],game.cards) for cid in p.starting_deck]
  if len(identities)==len(set(identities)):game._place_permanent(owner,'WW_824t')
 elif name=='historical_copy_concoction':
  from .pools import require_fixed_cards
  require_fixed_cards(CONCOCTION_IDS,game.cards)
  game._add(owner,game.rng.choice(CONCOCTIONS))
 elif name=='historical_copy_concoction_free':p.historical_next_concoction_free=True
 elif name=='historical_copy_manual_shots':
  mode,remaining,used=op[1:]
  if remaining>0:
   target_mode='enemy_minion' if mode=='goliath' else 'enemy_character'
   targets=[uid for uid in game._targets_for(ctx['card_id'],owner,target_mode) if uid and (mode!='huntress' or uid not in used)]
   options=[]
   for uid in targets:
    minion=live(game,uid) if uid>0 else None
    options.append(dict(card_id=minion.card_id if minion is not None else ctx['card_id'],target_uid=uid,label='Enemy hero' if uid<0 else game.cards[minion.card_id]['name']))
   if options:
    game.pending_choice=dict(owner=owner,kind='historical_manual_shot',mode=mode,remaining=remaining,used=tuple(used),context=dict(ctx),options=options,_automatic=bool(ctx.get('automatic_choices',False)))
    game.phase='choice'
 elif name=='historical_copy_high_noon_finish':
  a,b=op[1:];left=a.get('card');right=b.get('card')
  if left is not None and right is not None and a['cost']!=b['cost']:
   recipient,card=(owner,left) if a['cost']<b['cost'] else (1-owner,right)
   if card in game.players[recipient].hand:
    game.players[recipient].hand.remove(card);game._zone_card_removed(recipient,card,'hand','destroy')
    game._log('high_noon_destroyed',player=recipient,card=card.card_id);game._refresh_auras()
 elif name=='historical_copy_bibliomite':
  if p.hand:
   game.pending_choice=dict(owner=owner,kind='historical_bibliomite',options=[dict(card_id=card.card_id,uid=card.uid) for card in p.hand],_automatic=bool(ctx.get('automatic_choices',False)))
   game.phase='choice'
 elif name=='historical_copy_theotar':
  if p.hand and q.hand:
   offer_theotar(game,owner,owner,None,bool(ctx.get('automatic_choices',False)))
 elif name=='historical_copy_power_origin_capture':
  started,spells,state=op[1:]
  indices=[i for i,card in enumerate(p.deck) if game._started_in_deck(card,owner)==started and (not spells or game._card_data(card)['type']=='SPELL')]
  if indices:state['card']=game._take_deck_draw(owner,game.rng.choice(indices),include_burned=True)
 elif name=='historical_copy_power_draw_finish':
  state=op[1];card=state.get('card')
  if state.get('wilfred') and card is not None:game._set_card_cost(card,0)
 elif name=='historical_copy_replace_power':game._replace_primary_power(owner,dict(card_id=op[1]))
 elif name=='historical_copy_majordomo':
  p.hero_card_id='BRM_027h';p.hero_class=game.cards['BRM_027h']['cardClass']
  p.health=p.max_health=game.cards['BRM_027h']['health'];p.armor=0
  game._replace_primary_power(owner,dict(card_id='BRM_027p'))
 elif name=='historical_copy_algalon_vision':
  if q.deck:
   card=q.deck[-1]
   game.pending_choice=dict(owner=owner,kind='historical_algalon',deck_owner=1-owner,top_uid=card.uid,revealed_card_id=card.card_id,
    options=[dict(card_id='TTN_717t2',action='keep',revealed_card_id=card.card_id),dict(card_id='TTN_717t3',action='bottom',revealed_card_id=card.card_id)],_automatic=bool(ctx.get('automatic_choices',False)))
   game.phase='choice'
 elif name=='historical_copy_infestor':
  p.historical_zerg_attack_bonus=getattr(p,'historical_zerg_attack_bonus',0)+1
  game._refresh_auras()
 elif name=='historical_copy_roach':
  if source is not None and any(m is not source and m.health>0 and m.card_id in ZERG_IDS for m in p.minions):game._buff(source,1,2)
 elif name=='historical_copy_lurker_shot':
  amount=2 if ctx['event'].get('attacker_card_id') in ZERG_IDS else 1
  game._effect(('damage_random_enemy',amount),ctx)
 elif name=='historical_copy_summon_adversary':
  mode,state=op[1:]
  if mode=='viper':minion=game._recruit_from_zone(1-owner,'hand',(),site='viper')
  else:minion=game._summon(1-owner,'VAC_421t',entry_origin='effect',entry_site='snoozin_zookeeper')
  state['uid']=getattr(minion,'uid',None)
 elif name=='historical_copy_corrupted_recovery':
  from .historical_upgrades import CORRUPT_FORMS
  corrupted={spec[0] for spec in CORRUPT_FORMS.values()}
  snapshots=[record.card for record in p.replay_history if record.card.card_id in corrupted and record.card.uid!=getattr(ctx.get('physical_card'),'uid',None)]
  for original in snapshots:
   card=game._fresh_replay_card(original)
   # Repeated Corrupt growth belongs to the upgraded definition, not ordinary buffs.
   growth=getattr(original,'rule_state',{}).get('historical_corrupt_growth',0)
   if card.card_id=='DMF_124t':_saidan_add(card,'attack_bonus',growth);_saidan_add(card,'health_bonus',growth)
   game._b60_state(card)['historical_corrupt_growth']=growth
   game._b60_state(card)['historical_turn_zero_cost']=game.turn
   game._enter_hand(owner,card)
 elif name=='historical_copy_tribal_hand':
  from .selectors import TRIBES
  values=[card for card in p.hand if game._card_data(card)['type']=='MINION']
  chosen=game._distinct_type_group(values,len(TRIBES))
  # Capture all originals before generated copies can alter the hand.
  copies=[game._copy_card(card,source_owner=owner) for card in chosen] if op[1]=='copy' else []
  if op[1]=='copy':
   for card in copies:game._enter_hand(owner,card)
  elif op[1]=='buff':
   for card in chosen:_saidan_add(card,'attack_bonus',1);_saidan_add(card,'health_bonus',1)
  else:raise ValueError('Unknown tribal hand operation')
 elif name=='historical_copy_tribal_resurrect':
  card=op[1]
  game._summon(owner,card.card_id,entry_origin='resurrection',entry_site='nzoth_deep',entry_source=card)
 elif name=='historical_copy_cthun_piece':
  # Only resolved piece effects advance the caster, including automatic casts.
  if op[1] not in CTHUN_PIECES:raise ValueError('Unknown Cthun piece')
  pieces=set(getattr(p,'historical_cthun_pieces',()))
  pieces.add(op[1]);p.historical_cthun_pieces=tuple(sorted(pieces))
  if len(pieces)==4:
   p.historical_cthun_pieces=()
   card=Card(game._new_id(),'DMF_254');p.deck.append(card);game.rng.shuffle(p.deck)
   game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_copy_countess':
  from .selectors import has_class
  if not any(has_class(game._card_data(card),'NEUTRAL') for card in p.deck):
   for _ in range(3):game._add(owner,'REV_951t')
 elif name=='historical_copy_neeru':
  if not p.deck:game._place_permanent(owner,'BAR_919t')
 elif name=='historical_copy_head_sacrifice':
  for minion in list(p.minions):
   if minion.uid in op[1]:minion.health=0
 elif name=='historical_copy_coolant':p.cost_effects.append(dict(selector='ALL',amount=2,remaining_uses=1,expires=game.turn))
 elif name=='historical_copy_mimiron_gadget':game._add(owner,game.rng.choice(MIMIRON_GADGETS))
 elif name=='historical_copy_pair_offer':
  if target is not None:
   values=[live(game,uid) for uid in game._targets_for(ctx['card_id'],owner,'minion') if uid>0 and uid!=target.uid]
   options=[dict(card_id=m.card_id,target_uid=m.uid) for m in values if m is not None and m.health>0]
   if options:game.pending_choice=dict(kind='historical_stat_pair',owner=owner,first_uid=target.uid,options=options,_automatic=bool(ctx.get('automatic_choices',False)));game.phase='choice'
 elif name=='historical_copy_excavate_glyph':
  if target is not None and target in game.players[target.owner].board:
   board=game.players[target.owner].board;position=board.index(target);values=[board[index] for index in (position-1,position,position+1) if 0<=index<len(board)]
   for minion in values:
    if minion in game.players[target.owner].minions and minion.health>0:game._buff(minion,1,2)
 elif name=='historical_copy_sunstruck':
  if source in p.minions and game.rng.choice((False,True)):source.summoned_turn=game.turn;game._log('fall_asleep',entity=source.uid,player=owner)
 elif name=='historical_copy_sleep_others':
  for player in game.players:
   for minion in player.minions:
    if minion is not source and minion.health>0:minion.summoned_turn=game.turn;game._log('fall_asleep',entity=minion.uid,player=minion.owner)
 elif name=='historical_copy_power_chord':game._add(1-owner if op[1] else owner,game.rng.choice(POWER_CHORDS))
 elif name=='historical_copy_chicken_depart':
  if source in p.minions:source.health=0
 elif name=='historical_copy_poultryizer':
  values=[m for player in game.players for m in player.minions if m.health>0]
  if values:game._transform(game.rng.choice(values),'Mekka4t')
 elif name=='historical_copy_emboldener':
  values=[m for player in game.players for m in player.minions if m.health>0]
  if values:game._buff(game.rng.choice(values),1,1)
 elif name=='historical_copy_repair_bot':
  values=[m.uid for player in game.players for m in player.minions if 0<m.health<m.max_health]+[game.hero_id(index) for index,player in enumerate(game.players) if 0<player.health<player.max_health]
  if values:game._heal(game.rng.choice(values),6,healer=owner)
 elif name=='historical_copy_lich_gift':game._add(owner,game.rng.choice(LICH_KING_CARDS))
 elif name=='historical_copy_army_summon':
  card=op[1];game._summon(owner,game._card_data(card)['id'],attack_bonus=getattr(card,'attack_bonus',0),health_bonus=getattr(card,'health_bonus',0),entry_origin='effect',entry_zone='deck',entry_source=card,entry_site='army_frozen_throne')
 elif name=='historical_copy_doom_remove':
  dead={record['entity'].uid for player in game.players for record in player.death_records};count=len(dead.intersection(op[1]))
  for _ in range(min(count,len(p.deck))):
   card=p.deck.pop();game._zone_card_removed(owner,card,'deck','destroy');game._log('remove_deck_card',player=owner,card=game._card_data(card)['id'])
  game._refresh_auras()
 elif name=='historical_copy_death_grip':
  values=[card for card in q.deck if game._card_data(card)['type']=='MINION']
  if values:
   card=game.rng.choice(values);q.deck.remove(card);game._enter_hand(owner,card);game._refresh_auras()
 elif name=='historical_copy_death_coil':
  uid=ctx.get('target',0);recipient=-uid-1 if uid<0 else target.owner if target is not None else None
  if recipient==owner:game._heal(uid,5,healer=owner,spell=True)
  elif recipient is not None:game._deal_effect(uid,5,ctx)
 elif name=='historical_copy_antimagic':
  for minion in list(p.minions):game._buff(minion,2,2);minion.keywords.add('ELUSIVE')
 elif name=='historical_copy_ashen':
  turns=getattr(q,'historical_ashen_turns',[]);turns.append(q.turns_taken+1);q.historical_ashen_turns=turns
 elif name=='historical_copy_bonelord':
  p.historical_bonelord=True;key=game._new_id();timers=getattr(p,'historical_bonelord_timers',{});timers[key]=3;p.historical_bonelord_timers=timers
  game._schedule_turn_effect(owner,'end',0,3,(('historical_copy_bonelord_tick',key),),source_card_id='RLK_591')
 elif name=='historical_copy_bonelord_tick':
  timers=getattr(p,'historical_bonelord_timers',{})
  if op[1] in timers:
   timers[op[1]]-=1
   if timers[op[1]]<=0:p.health=0;del timers[op[1]];game._log('bonelord_deadline',player=owner)
 elif name=='historical_copy_blightfang':
  for minion in q.minions:
   if minion.health>0:minion.attached_death_effects.append(('summon_opponent','RLK_118t3',1));minion.keywords.add('DEATHRATTLE')
 elif name=='historical_copy_darkvein':
  history=[r for r in getattr(p,'_historical_cast_records',()) if game._card_data(r['card']).get('spellSchool')=='SHADOW']
  for _ in range(2):
   card=Card(game._new_id(),'REV_373t')
   if history:game._b60_state(card)['historical_darkvein_spell']=deepcopy(history[-1]['card'])
   game._summon(owner,'REV_373t',entry_origin='generated',entry_source=card,entry_site='darkvein')
 elif name=='historical_copy_haunt':
  if p.hand:
   card=game.rng.choice(p.hand)
   if not hasattr(card,'_follow_effects'):card._follow_effects=[]
   card._follow_effects.append(dict(card_id='RLK_822',source_card_id='RLK_822',historical_mode='nightmare',end=None))
 elif name=='historical_copy_dust_junk':game._add(owner,game.rng.choice(('GAME_005','WW_001t','EX1_014t','CS2_082')))
 elif name=='historical_copy_solar_eclipse':p.historical_spell_repeat_turn=game.turn
 elif name=='historical_copy_lunar_eclipse':p.cost_effects.append(dict(selector='SPELL',amount=2,remaining_uses=1,expires=game.turn))
 elif name=='historical_copy_korrak':
  if source is not None and not source.rule_state.get('historical_korrak_exact_lethal',False):game._summon(owner,'AV_143',ctx.get('death_position',-1),entry_origin='resurrection',entry_site='korrak')
 elif name=='historical_copy_finley_swap':
  outgoing=list(p.hand);incoming=list(p.deck[:len(outgoing)]);del p.deck[:len(outgoing)];p.hand=[]
  clean=[]
  for card in outgoing:
   replacement=game._fresh_replay_card(card);replacement.uid=card.uid;game._carry_origin(card,replacement);clean.append(replacement)
  p.deck[0:0]=list(reversed(clean))
  for card in incoming:game._enter_hand(owner,card)
  game._refresh_auras();game._log('swap_hand_bottom',player=owner,count=len(incoming))
 elif name=='historical_copy_illucia':
  key=game._new_id();saved=getattr(p,'historical_illucia_hands',{});saved[key]=p.hand;p.historical_illucia_hands=saved;p.hand=[]
  for card in list(q.hand):game._enter_hand(owner,game._copy_card(card,source_owner=1-owner))
  game._schedule_turn_effect(owner,'end',0,1,(('historical_copy_illucia_restore',key),),source_card_id='SCH_159');game._refresh_auras()
 elif name=='historical_copy_illucia_restore':
  saved=getattr(p,'historical_illucia_hands',{}).pop(op[1],None)
  if saved is not None:
   p.hand=[]
   for card in saved:game._enter_hand(owner,card)
   game._refresh_auras()
 elif name=='historical_copy_jepetto':
  records=list(p.replay_history)
  for record in records:
   card=record.card
   if card.uid==getattr(ctx.get('physical_card'),'uid',None):continue
   if game._card_data(card)['type']=='MINION' and (game._card_stat(card,'attack',owner)==1 or game._card_stat(card,'health',owner)==1):game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 elif name=='historical_copy_nemsy_swap':
  uid=getattr(source,'rule_state',{}).get('historical_nemsy_drawn')
  card=next((card for card in p.hand if card.uid==uid),None)
  if source is not None and card is not None and (source in p.board or len(p.board)<7):
   position=p.board.index(source) if source in p.board else ctx.get('death_position',-1)
   if source in p.board:p.board.remove(source)
   p.hand.remove(card);game._summon(owner,card.card_id,position,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='recruit',entry_zone='hand',entry_source=card,entry_site='nemsy_swap')
   game._enter_hand(owner,game._fresh_replay_card(source));game._refresh_auras()
 elif name=='historical_copy_hollidae':
  from .identities import canonical_identity
  identities=[canonical_identity(game.cards[cid],game.cards) for cid in p.starting_deck]
  if len(identities)==len(set(identities)):game._equip(owner,'WW_010t')
 elif name=='historical_copy_boar_sword':
  from .identities import canonical_identity
  boar=canonical_identity(game.cards['SW_075'],game.cards)
  if sum(canonical_identity(game.cards[record['card_id']],game.cards)==boar for record in p.death_records)>=10:game._equip(owner,'SW_075t')
 elif name=='historical_copy_sword_mana':
  q.max_mana=0;q.mana=0;q.locked_mana=0;game._log('destroy_mana_crystals',player=1-owner)
 elif name=='historical_copy_staff_frog':
  card=ctx.get('weapon_card',p.equipped_card)
  if card is not None and card.uid==ctx.get('weapon_uid'):
   state=game._b60_state(card);count=state.get('historical_staff_frogs',0)+1;state['historical_staff_frogs']=count
   game._summon(owner,'WW_010hexfrog',entry_stats=(count,count),entry_origin='generated',entry_site='staff_nine_frogs')
 elif name=='historical_copy_draka':
  game._equip(owner,'REV_940t',attack_bonus=min(10,max(0,ctx.get('prior_card_count',p.cards_played))))
 elif name=='historical_copy_elise_summon':
  card=op[1];game._summon(owner,card.card_id,entry_stats=(5,5),entry_origin='copy',entry_zone='deck',entry_source=card,entry_site='elise_badlands')
 elif name=='historical_copy_zarimi':
  if not getattr(p,'historical_zarimi_used',False):
   current_uid=getattr(ctx.get('physical_card'),'uid',None)
   dragons=sum(has_tribe(game._card_data(record.card),'DRAGON') for record in p.replay_history if record.card.uid!=current_uid)
   # Exclude this play even when a suspended frame resumes after recording.
   if dragons>=8:p.historical_zarimi_used=True;p.extra_turns_pending+=1
 elif name=='historical_copy_random_location':
  values=game._generation_candidates(pool(card_type='LOCATION'),owner)
  if values and len(p.board)<7:game._place_location(owner,game.rng.choice(values))
 elif name=='historical_copy_location_clone':
  donor=next((location for location in p.locations if location.uid==ctx.get('target')),None)
  if donor is not None and len(p.board)<7:
   clone=deepcopy(donor);clone.uid=game._new_id();clone.owner=owner;p.board.append(clone);game._refresh_auras()
   game._log('location_copied',player=owner,card=clone.card_id,entity=clone.uid)
 elif name=='historical_copy_microphones':
  game._equip(owner,'ETC_078t2');game._equip(1-owner,'ETC_078t')
 elif name=='historical_copy_pozzik_bots':
  if source is not None:
   for _ in range(2):
    card=game._add(1-owner,'ETC_425t')
    if card is not None:source.rule_state.setdefault('historical_pozzik_bots',[]).append(card.uid)
 elif name=='historical_copy_pozzik_recruit':
  for uid in getattr(source,'rule_state',{}).get('historical_pozzik_bots',()):
   if len(p.board)>=7:break
   for original in game.players:
    card=next((card for card in original.hand if card.uid==uid),None)
    if card is not None:
     original.hand.remove(card);game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='recruit',entry_zone='hand',entry_source=card,entry_site='pozzik');break
 elif name=='historical_copy_spelleater':game._replace_primary_power(owner,power_snapshot(game,1-owner))
 elif name=='historical_copy_wizard_swap':
  original=(power_snapshot(game,owner),power_snapshot(game,1-owner))
  game._replace_primary_power(owner,original[1]);game._replace_primary_power(1-owner,original[0])
  game._schedule_turn_effect(owner,'start',1,1,(('historical_copy_wizard_restore',original),),source_card_id='DRG_401')
 elif name=='historical_copy_wizard_restore':
  game._replace_primary_power(owner,op[1][0]);game._replace_primary_power(1-owner,op[1][1])
 elif name=='historical_copy_talritha':
  choices=[card for card in p.hand if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'DRAGON')]
  if choices:
   card=game.rng.choice(choices);_saidan_add(card,'attack_bonus',3);_saidan_add(card,'health_bonus',3)
   state=game._b60_state(card);state['historical_talritha_deaths']=state.get('historical_talritha_deaths',0)+1
 elif name=='historical_copy_next_fire_bonus':p.historical_next_fire_bonus=getattr(p,'historical_next_fire_bonus',0)+2
 elif name=='historical_copy_temporus':
  game._historical_turn_queue=[1-owner,1-owner,owner,owner]+list(getattr(game,'_historical_turn_queue',()))
 elif name=='historical_copy_flint':
  values=game._generation_candidates(pool(mechanic='QUICKDRAW'),owner)
  if values:
   card=game._add(owner,game.rng.choice(values))
   if card is not None:attach_same_turn_follow(game,card,ctx,'flint')
 elif name=='historical_copy_follow_mode':
  effect=op[1];mode=effect['historical_mode'];bound=live(game,effect.get('source_uid',0));follow_ctx=dict(owner=owner,source=bound,target=0,bonus=0,lifesteal=False,card_id=effect['source_card_id'])
  if mode=='moonlit':
   index=next((i for i,c in enumerate(p.deck) if getattr(c,'uid',None)==effect['deck_uid']),None)
   if index is not None:game._take_deck_draw(owner,index,include_burned=True)
  elif mode=='shroud':
   if source is not None and source in p.minions:game._temporary_keyword(source,'STEALTH','next_start')
  elif mode=='nightmare':game._summon(owner,'RLK_822t',entry_origin='effect',entry_site='haunting_nightmare')
  elif mode=='edwin':
   if bound is not None and bound.owner==owner:
    game._buff(bound,2,2)
    from .historical_draw_batches import draw
    game._rule_events.append(('captured_effects',dict(operations=(draw(mode='same_turn_follow',args=('edwin',)),),context=follow_ctx),[]))
  elif mode=='cactus':
   if bound is not None and bound.owner==owner:game._buff(bound,1,2);bound.keywords.add('TAUNT')
  elif mode=='stiltstepper':game._effect(('hero_attack',4),follow_ctx)
  else:
   operation=('historical_copy_flint',) if mode=='flint' else ('historical_treasure_pool_offer',pool(card_type='SPELL',minimum=1 if mode=='fireheart' else 0,classes='own_or_neutral'),'follow_'+mode)
   game._rule_events.append(('captured_effects',dict(operations=(operation,),context=follow_ctx),[]))
 elif name=='historical_copy_seamstress':
  if source is not None and source in p.minions:
   for rune,keyword in (('blood','LIFESTEAL'),('frost','REBORN'),('unholy','RUSH')):
    if any(game.cards[cid].get('runeCost',{}).get(rune,0)>0 for cid in p.starting_deck):source.keywords.add(keyword)
 elif name=='historical_copy_visitor':
  for card in p.hand:
   if game._copied_from_opponent(card,owner):card.cost_delta=getattr(card,'cost_delta',0)-(3)
 elif name=='historical_copy_dinner':
  choices=[card for card in p.deck if game._card_data(card)['type']=='MINION' and game._cost(card,owner)<=p.mana]
  if choices:game._effect(('historical_copy_recruit_uid','deck',game.rng.choice(choices).uid),ctx)
 elif name=='historical_copy_topior':p.historical_topior=getattr(p,'historical_topior',0)+1
 elif name=='historical_copy_eliza':p.historical_eliza=getattr(p,'historical_eliza',0)+1;game._refresh_auras()
 elif name=='historical_copy_fate_bind':
  if source is not None:
   choices=source.rule_state.setdefault('historical_fatespinner',[])
   if op[1] not in choices:choices.append(op[1])
   source.card_id='ICC_047t2' if len(choices)==2 else 'ICC_047t';source.keywords.add('DEATHRATTLE')
 elif name=='historical_copy_duplicate_hand':
  for card in list(p.hand):game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 elif name=='historical_copy_skulker_take':
  if source is not None and p.weapon is not None:
   weapon=deepcopy(p.weapon);card=deepcopy(p.equipped_card)
   source.rule_state['historical_skulker_weapon']=(weapon,card);p.weapon=None;p.equipped_card=None
   game._buff(source,weapon['attack'],weapon['durability']);game._refresh_auras()
 elif name=='historical_copy_skulker_return':
  held=source.rule_state.get('historical_skulker_weapon') if source is not None else None
  if held:
   weapon,card=held;physical=game._copy_card(card,source_owner=owner) if card is not None else None
   game._equip(owner,weapon['card_id'],attack_bonus=physical.attack_bonus if physical is not None else 0,physical_card=physical)
   previous_attack=game._hero_attack(owner);p.weapon=deepcopy(weapon)
   game._record_hero_stat_gain(owner,'attack',game._hero_attack(owner)-previous_attack);game._refresh_auras()
 elif name=='historical_copy_najak_take':
  if source is not None and target is not None and target.owner!=owner and len(p.board)<7:
   original=target.owner;source.rule_state['historical_najak_binding']=(target.uid,original)
   game.players[original].board.remove(target);target.owner=owner;target.summoned_turn=game.turn;target.attacks=0;p.board.append(target);game._refresh_auras()
 elif name=='historical_copy_najak_return':
  binding=source.rule_state.get('historical_najak_binding') if source is not None else None
  victim=live(game,binding[0]) if binding else None
  if victim is not None and victim.owner!=binding[1]:
   destination=game.players[binding[1]]
   if len(destination.board)>=7:victim.health=0
   else:
    game.players[victim.owner].board.remove(victim);victim.owner=binding[1];victim.summoned_turn=game.turn;victim.attacks=0;destination.board.append(victim);game._refresh_auras()
 elif name=='historical_copy_zone_swap':
  outgoing=target if op[1]=='target' else source
  if outgoing is None:return True
  board_owner=outgoing.owner;player=game.players[board_owner]
  live_source=outgoing in player.minions
  if not live_source and 'death_position' not in ctx:return True
  zone_owner=1-board_owner if op[2]=='enemy' else board_owner
  zone=getattr(game.players[zone_owner],op[3]);choices=[i for i,card in enumerate(zone) if game._card_data(card)['type']=='MINION']
  if not choices or not live_source and len(player.board)>=7:return True
  index=game.rng.choice(choices);incoming=zone[index]
  position=player.board.index(outgoing) if live_source else min(ctx['death_position'],len(player.board))
  returned=game._fresh_replay_card(outgoing);game._carry_origin(outgoing,returned)
  if live_source:player.board.remove(outgoing)
  if op[3]=='deck':zone[index]=returned
  else:
   zone.pop(index);game._enter_hand(zone_owner,returned)
   if returned in game.players[zone_owner].hand:
    game.players[zone_owner].hand.remove(returned);game.players[zone_owner].hand.insert(min(index,len(game.players[zone_owner].hand)),returned)
  game._refresh_auras()
  game._summon(board_owner,incoming.card_id,position,attack_bonus=incoming.attack_bonus,health_bonus=incoming.health_bonus,entry_keywords=op[4],entry_origin='recruit',entry_zone=op[3],entry_source=incoming,entry_site='historical_zone_swap')
  game._log('zone_swap',player=board_owner,zone=op[3],zone_owner=zone_owner)
 elif name=='historical_copy_earthen_growth':
  minion=live(game,op[1])
  if minion is not None:game._buff(minion,2*op[2],2*op[2])
 elif name=='historical_copy_hatch':
  if source in p.minions:game._transform(source,op[1])
 elif name=='historical_copy_horsemen_win':
  from .identities import canonical_identity
  deaths={canonical_identity(game.cards[cid],game.cards) for cid in p.death_history}
  if all(canonical_identity(game.cards[cid],game.cards) in deaths for cid in HORSEMEN):q.health=0
 elif name=='historical_copy_ancient_merge':
  if source in p.minions:
   others=[m for m in p.minions if m is not source and m.card_id=='OG_173' and m.health>0]
   if others:
    other=min(others,key=lambda m:m.uid);position=p.board.index(source)
    p.board.remove(source);p.board.remove(other);game._refresh_auras()
    game._summon(owner,'OG_173a',position,entry_origin='effect',entry_site='ancient_merge',entry_source=source)
 elif name=='historical_copy_mogu_sacrifice':
  for minion in p.minions:
   if minion.card_id=='ULD_705':minion.health=0
 elif name=='historical_copy_shattershambler':
  p.cost_effects.append(dict(selector='DEATHRATTLE',amount=1,remaining_uses=1,historical_minion_play='die',expires=None))
 elif name=='historical_copy_murmuring':p.historical_murmuring_turn=game.turn
 elif name=='historical_copy_experimenter_end':
  victim=live(game,op[1])
  if victim is not None and victim.rule_state.get('historical_experimenter_death'):victim.health=0
 elif name=='historical_copy_doll_bind':
  if source is not None and target is not None:source.rule_state['historical_doll_target']=target.uid
 elif name=='historical_copy_doll_destroy':
  victim=live(game,source.rule_state.get('historical_doll_target',0)) if source is not None else None
  if victim is not None:victim.health=0
 elif name=='historical_copy_ooze_schedule':
  if source is not None:
   source.rule_state['historical_ooze_pending']=source.rule_state.get('historical_ooze_pending',0)+1
   game._schedule_turn_effect(game.current,'end',0,1,(('historical_copy_ooze_end',owner,source.uid),),source_card_id='FP1_003')
 elif name=='historical_copy_ooze_end':
  donor=live(game,op[2])
  if donor is not None and donor.rule_state.get('historical_ooze_pending',0)>0:
   donor.rule_state['historical_ooze_pending']-=1
   game._summon(op[1],donor.card_id,copy_from=donor,entry_origin='copy',entry_site='echoing_ooze',entry_source=donor)
 elif name=='historical_copy_gral':
  choices=[i for i,card in enumerate(p.deck) if game._card_data(card)['type']=='MINION']
  if choices and source is not None:
   card=p.deck.pop(game.rng.choice(choices));source.rule_state.setdefault('historical_gral',[]).append(deepcopy(card))
   attack=game._card_stat(card,'attack',owner);health=game._card_stat(card,'health',owner)
   game._zone_card_removed(owner,card,'deck','destroy');game._log('destroy_deck_card',player=owner,card=card.card_id)
   if source in p.minions:game._buff(source,attack,health)
 elif name=='historical_copy_banker_store':
  if p.deck and source is not None:
   card=p.deck.pop();source.rule_state.setdefault('historical_banker',[]).append(card)
   game._log('card_stored',player=owner,source=source.uid)
 elif name=='historical_copy_stored_hand':
  if source is not None:
   for card in source.rule_state.get(op[1],()):game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 elif name=='historical_copy_swap_decks':
  p.deck,q.deck=q.deck,p.deck;game._log('decks_swapped',player=owner)
 elif name=='historical_copy_ransom':game._add(1-owner,'LOOT_541t')
 elif name=='historical_copy_plush':
  if source is not None:
   victims=[m for player in game.players for m in player.minions if m.attack<source.attack]
   for minion in victims:
    player=game.players[minion.owner];player.board.remove(minion)
    card=game._fresh_replay_card(minion);game._carry_origin(minion,card)
    player.deck.insert(game.rng.randrange(len(player.deck)+1),card);game._record_deck_insertion(minion.owner,owner,1,'shuffle',cards=(card,))
   game._refresh_auras()
 elif name=='historical_copy_fizzle':
  if not getattr(p,'historical_fizzle_used',False):
   p.historical_fizzle_used=True;card=Card(game._new_id(),'ETC_113t')
   card._historical_snapshot=tuple(game._copy_card(held,source_owner=owner) for held in p.hand)
   p.deck.insert(game.rng.randrange(len(p.deck)+1),card);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_copy_snapshot_restore':
  if not getattr(p,'historical_snapshot_used',False):
   p.historical_snapshot_used=True
   for card in getattr(ctx.get('physical_card'),'_historical_snapshot',()):game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 elif name=='historical_copy_rustwix':
  from .pools import require_fixed_cards
  require_fixed_cards(RUSTWIX_PRIMES,game.cards)
  for _ in range(3):
   cid=game.rng.choice(RUSTWIX_PRIMES)
   game._effect(('historical_prime_shuffle',cid),ctx)
 elif name=='historical_copy_sludge_damage':
  targets=[game.hero_id(1-owner)]+[m.uid for m in q.minions if m.health>0]
  def health(uid):return q.health if uid<0 else live(game,uid).health
  minimum=min(health(uid) for uid in targets);uid=game.rng.choice([uid for uid in targets if health(uid)==minimum]);game._deal_effect(uid,4,ctx)
 elif name=='historical_copy_chimaera':
  if source is not None:game._summon(owner,'YOG_506t',attack_bonus=max(0,source.attack)-1,health_bonus=max(0,source.attack)-1,entry_origin='deathrattle',entry_site='twisted_frostwing',entry_source=source)
 elif name=='historical_copy_ogre_ace':
  if source in p.minions and source.health>0:source.keywords.add('DIVINE_SHIELD' if game.rng.randrange(2)==0 else 'LIFESTEAL')
 elif name=='historical_copy_void_ray':
  if ctx.get('paid_cost')==0 and source in p.minions:game._buff(source,2,2)
 elif name=='historical_copy_draw_cast_charges':p.historical_draw_cast_charges=getattr(p,'historical_draw_cast_charges',0)+op[1]
 elif name=='historical_copy_jotun':p.historical_jotun=True
 elif name=='historical_copy_next_minion':p.cost_effects.append(dict(selector=op[1],amount=0,remaining_uses=op[2],historical_minion_play=op[3],expires=None))
 elif name=='historical_copy_next_hero_attack':
  if source in p.minions and source.health>0:game._effect(('hero_attack',source.attack),ctx)
 elif name=='historical_copy_akama':
  for minion in p.minions:
   if minion.card_id!='GDB_235' and minion.health>0:minion.attacks=0
 elif name=='historical_copy_reborn_copy':
  event=ctx['event'];donor=live(game,event.get('source'))
  if event.get('origin')=='reborn' and donor is not None and donor is not source:game._summon(owner,donor.card_id,copy_from=donor,entry_origin='copy',entry_site='auchenai_death_speaker',entry_source=donor)
 elif name=='historical_copy_turbulus':
  for minion in p.minions:
   if minion is not source and minion.health>0 and 'BATTLECRY' in game._card_data(minion).get('mechanics',()):game._buff(minion,1,1)
  for card in p.hand+p.deck:
   if game._card_data(card)['type']=='MINION' and 'BATTLECRY' in game._card_mechanics(card):_saidan_add(card,'attack_bonus',1);_saidan_add(card,'health_bonus',1)
 elif name=='historical_copy_dirdra':
  from .pools import require_fixed_cards
  require_fixed_cards(CREWMATES,game.cards);cards=[Card(game._new_id(),cid) for cid in CREWMATES];p.deck.extend(cards);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,len(CREWMATES),'shuffle',cards=cards)
 elif name=='historical_copy_bind_fan':
  if source in p.minions and target is not None:source.rule_state['historical_bound_aura_target']=target.uid;game._refresh_auras()
 elif name=='historical_copy_mill_three':
  for _ in range(min(3,len(p.deck))):
   card=p.deck.pop();game._zone_card_removed(owner,card,'deck','destroy');game._log('destroy_deck_card',player=owner,card=card.card_id)
 elif name=='historical_copy_bottom_token':
  from .pools import require_fixed_cards
  require_fixed_cards((op[1],),game.cards);card=Card(game._new_id(),op[1]);p.deck.insert(0,card);game._record_deck_insertion(owner,owner,1,'bottom',cards=(card,))
 elif name=='historical_copy_sunken_scavenger':
  for minion in p.minions:
   if minion is not source and minion.health>0 and has_tribe(game._card_data(minion),'MURLOC'):game._buff(minion,1,1)
  for card in p.hand+p.deck:
   if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'MURLOC'):_saidan_add(card,'attack_bonus',1);_saidan_add(card,'health_bonus',1)
 elif name=='historical_copy_permanent_shuffle':
  if source is not None:
   from .base_stats import base_stats
   a,h=base_stats(game,source,owner) if op[1]=='base_add' else (source.attack-source.aura_attack,source.max_health-source.aura_health)
   stats=(a*op[2],h*op[2]) if op[1]=='double' else (a+op[2],h+op[2])
   card=game._fresh_replay_card(source);card.base_stat_override=stats;card._historical_permanent_stats=True;game._carry_origin(source,card,copied=op[1]!='base_add',source_owner=owner)
   if op[3]=='bottom':p.deck.insert(0,card)
   else:p.deck.append(card);game.rng.shuffle(p.deck)
   game._record_deck_insertion(owner,owner,1,'bottom' if op[3]=='bottom' else 'shuffle',cards=(card,))
 elif name=='historical_copy_retained_shuffle':
  if source is not None:
   from .base_stats import base_stats,carry_base_stats
   card=Card(game._new_id(),source.card_id);carry_base_stats(source,card)
   base_a,base_h=base_stats(game,card,owner);card.attack_bonus=source.attack+source.attack_deficit-source.aura_attack-base_a;card.health_bonus=source.max_health-source.aura_health-base_h
   snapshot=deepcopy(source);snapshot.aura_attack=snapshot.aura_health=0;snapshot.attack-=source.aura_attack;snapshot.max_health-=source.aura_health;snapshot.health=snapshot.max_health;snapshot.attacks=0
   card._historical_retained_minion=snapshot;game._carry_origin(source,card);p.deck.append(card);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_copy_spirit_tiger':
  cost=max(0,ctx['event']['cost']);game._summon(owner,'TRL_309t',attack_bonus=cost-1,health_bonus=cost-1,entry_origin='effect',entry_site='spirit_tiger',entry_source=source)
 elif name=='historical_copy_spirit_dead':
  records=[record for record in p.death_records if record['entity'].uid==ctx['event'].get('source')]
  if records:
   card=game._fresh_replay_card(records[-1]['entity']);game._set_card_cost(card,1);p.deck.append(card);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_copy_mirage':
  if source in p.minions:
   card=game._fresh_replay_card(source);game._carry_origin(source,card);p.board.remove(source);p.deck.append(card);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,));game._refresh_auras()
 elif name=='historical_copy_lowest_hand_recruit':
  cards=[card for card in p.hand if game._card_data(card)['type']=='MINION']
  if cards:
   cost=min(game._cost(card,owner) for card in cards);card=game.rng.choice([card for card in cards if game._cost(card,owner)==cost]);game._effect(('historical_copy_recruit_uid','hand',card.uid),ctx)
 elif name=='historical_copy_reborn_enemy_played':
  minion=live(game,ctx['event'].get('source'))
  if minion is not None:minion.keywords.add('REBORN')
 elif name=='historical_copy_giftwrapped':
  choices=[card for card in p.hand if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'DRAGON')]
  if choices:
   card=game.rng.choice(choices);_saidan_add(card,'attack_bonus',1);_saidan_add(card,'health_bonus',1)
   if source in p.minions:game._buff(source,1,1)
 elif name=='historical_copy_tides':
  if p.mana>0 and source in p.minions:game._buff(source,1,2)
 elif name=='historical_copy_soulstealer_kill':
  for player in game.players:
   for minion in tuple(player.minions):
    if minion is not source:game._effect(('destroy',),dict(ctx,target=minion.uid))
 elif name=='historical_copy_soulstealer_corpses':
  dead={record['entity'].uid for record in q.death_records};game._gain_corpses(owner,len(dead & op[1]['enemies']))
 elif name=='historical_copy_capture_tokens':
  before={m.uid for m in p.all_minions}
  for _ in range(op[2]):game._summon(owner,op[1],entry_origin='effect',entry_site='historical_attacking_token',entry_source=source)
  op[3]['uids']=[m.uid for m in p.all_minions if m.uid not in before]
 elif name=='historical_copy_playmaker':
  donor=live(game,ctx['event'].get('source'))
  if donor is not None:
   snapshot=deepcopy(donor);snapshot.health=1;game._summon(owner,donor.card_id,copy_from=snapshot,entry_origin='copy',entry_site='playmaker',entry_source=donor)
 elif name=='historical_copy_waterdancer':
  donor=live(game,ctx['event'].get('source'))
  if donor is not None:
   card=game._fresh_replay_card(donor);game._set_card_cost(card,0);game._enter_hand(owner,card)
 elif name=='historical_copy_plaguemaw':
  records=[record for record in p.death_records if record['entity'].uid==ctx['event'].get('source')]
  if records:
   card=game._fresh_replay_card(records[-1]['entity']);game._summon(owner,card.card_id,entry_source=card,entry_origin='effect',entry_site='plaguemaw',entry_remove_keywords=('TAUNT',))
 elif name=='historical_copy_pelagos':
  uid=ctx['event'].get('cast_target',{}).get('uid');minion=live(game,uid)
  if minion is not None:
   amount=max(minion.attack,minion.health);game._set_entity_stats(minion,amount,amount)
 elif name=='historical_copy_hand_capacity':
  p.historical_hand_capacity_peak=max(getattr(p,'historical_hand_capacity_peak',10),p.hand_capacity,op[1]);p.hand_capacity=op[1]
  if op[2]:
   p.mana_capacity=op[1];p.max_mana=min(p.max_mana,p.mana_capacity);p.mana=min(p.mana,p.max_mana);p.locked_mana=min(p.locked_mana,p.max_mana)
 elif name=='historical_copy_serena':
  if source in p.minions and target is not None:
   attack=max(0,(target.attack-source.attack)//2+1) if source.attack<=target.attack else 0
   health=max(0,(target.health-source.health)//2+1) if source.health<=target.health else 0
   attack=min(target.attack,attack);health=min(target.health,health)
   game._buff(target,-attack,-health);game._buff(source,attack,health)
 elif name=='historical_copy_abyssal_summoner':game._summon(owner,'DRG_207t',entry_stats=(len(p.hand),len(p.hand)),entry_origin='effect',entry_site='abyssal_summoner',entry_source=source)
 elif name=='historical_copy_health_return':
  if source is not None:
   card=game._fresh_replay_card(source);game._b60_state(card)['health_payment']=True;game._enter_hand(owner,card)
 elif name=='historical_copy_risa':
  if source in p.minions:
   card=game._bounce(source)
   if card is not None:game._set_card_cost(card,1)
 elif name=='historical_copy_lieutenant':
  donor=live(game,ctx['event'].get('source'))
  if source in p.minions and donor is not None:
   result=replace(game,source,donor,(2,2))
   if result is not None:result.keywords.add('RUSH')
 elif name=='historical_copy_doomkin':
  if q.max_mana>q.mana:
   q.max_mana-=1;q.locked_mana=min(q.locked_mana,q.max_mana)
   p.max_mana=min(p.mana_capacity,p.max_mana+1)
 elif name=='historical_copy_camel_one':game._recruit_from_zone(owner if op[1]=='own' else 1-owner,'deck',(('cost','eq',1),),site='desert_camel')
 elif name=='historical_copy_grumble':
  for minion in tuple(p.minions):
   if minion is not source and minion.health>0:
    card=game._bounce(minion)
    if card is not None:game._set_card_cost(card,1)
 elif name=='historical_copy_custodian':
  if source in p.minions:
   for _ in q.minions:source.keywords.add(game.rng.choice(('RUSH','DIVINE_SHIELD','WINDFURY')))
 elif name=='historical_copy_sonya':
  uid=ctx['event']['source'];records=[record for record in p.death_records if record['entity'].uid==uid]
  if records:
   card=game._fresh_replay_card(records[-1]['entity']);game._mutation_set_stats(card,owner,1,1);game._set_card_cost(card,1);game._enter_hand(owner,card)
 elif name=='historical_copy_gibberer':
  if source is not None:game._enter_hand(owner,game._fresh_replay_card(source))
 elif name=='historical_copy_power_slider':
  from .quest_families import maximum_tribe_matching
  from .selectors import effective_tribes,TRIBES
  plays=[]
  for record in p.played_history:
   data=game.cards[record['card_id']]
   if data['type']=='MINION':plays.append(set(TRIBES)-{'ALL'} if 'ALL' in effective_tribes(data) else set(effective_tribes(data)))
  tribes=effective_tribes(game.cards[ctx['card_id']]);plays.append(set(TRIBES)-{'ALL'} if 'ALL' in tribes else set(tribes))
  count=len(maximum_tribe_matching(plays))
  if source in p.minions:game._buff(source,count,count)
 elif name=='historical_copy_fill_bananas':
  for _ in range(max(0,getattr(q,'hand_capacity',10)-len(q.hand))):game._add(1-owner,'EX1_014t')
 elif name=='historical_copy_highest_spell':
  choices=[card for card in p.hand if game._card_data(card)['type']=='SPELL']
  if choices:
   cost=max(game._cost(card,owner) for card in choices);card=game.rng.choice([c for c in choices if game._cost(c,owner)==cost]);game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 elif name=='historical_copy_control':
  allowed=len(q.minions)>=4 if op[1]=='board_four' else target is not None and target.attack<=2
  if target is not None and target.owner!=owner and allowed and len(p.board)<7:
   q.board.remove(target);target.owner=owner;target.summoned_turn=game.turn;target.attacks=0;p.board.append(target);game._refresh_auras()
 elif name=='historical_copy_aldor':
  if target is not None:game._set_minion_attack(target,1+target.aura_attack)
 elif name=='historical_copy_last_draenei':
  records=[record for record in p.replay_history if game._card_data(record.card)['type']=='MINION' and has_tribe(game._card_data(record.card),'DRAENEI')]
  if records:game._enter_hand(owner,game._fresh_replay_card(records[-1].card))
 elif name=='historical_copy_eight_hands':
  for recipient,player in enumerate(game.players):
   cards=list(player.deck);game.rng.shuffle(cards);cards.sort(key=lambda card:game._cost(card,recipient),reverse=True)
   keep={card.uid for card in cards[:8]}
   for card in tuple(player.deck):
    if card.uid not in keep:player.deck.remove(card);game._zone_card_removed(recipient,card,'deck','destroy');game._log('destroy_deck_card',player=recipient,card=card.card_id)
 elif name=='historical_copy_hat':
  choices=[m for player in game.players for m in player.minions if m is not source and m.health>0]
  if choices:game._buff(game.rng.choice(choices),1,1)
 elif name=='historical_copy_escape_pod':
  position=ctx.get('death_position',len(p.board));neighbors=[p.board[i] for i in (position-1,position) if 0<=i<len(p.board) and p.board[i] in p.minions]
  for minion in neighbors:
   game._buff(minion,1,1);minion.keywords.add('RUSH')
 elif name=='historical_copy_streak_damage':
  amount=1+elemental_streak(game,owner)
  if op[1]=='target':game._deal_effect(ctx.get('target',0),amount,ctx)
  else:
   with game._damage_batch():
    for uid in [game.hero_id(1-owner)]+[m.uid for m in q.minions if m.health>0]:game._deal_effect(uid,amount,ctx)
 elif name=='historical_copy_cheese_elemental':
  if source in p.minions and source.health>0:game._summon(owner,'VAC_339t',entry_stats=(source.attack,source.health),entry_origin='effect',entry_site='muensterosity',entry_source=source)
 elif name=='historical_copy_xanesh':
  for card in p.hand+p.deck:
   if {'CORRUPT','CORRUPTED'} & set(game._card_mechanics(card)):card.cost_delta=getattr(card,'cost_delta',0)-(2)
 elif name=='historical_copy_geist':
  if p.corpses>=1:
   game._spend_corpses(owner,1)
   if source in p.minions:game._buff(source,1,2)
 elif name=='historical_copy_random_starting_hand':
  cards=getattr(p,'_starting_hand',())
  if cards:game._enter_hand(owner,game._fresh_replay_card(game.rng.choice(cards)))
 elif name=='historical_copy_templar':
  if getattr(p,'historical_healing_done_total',0)>=10 and source in p.minions:game._buff(source,4,4);source.keywords.add('TAUNT')
 elif name=='historical_copy_polkelts_order':
  game.rng.shuffle(p.deck);p.deck.sort(key=lambda card:game._cost(card,owner))
  game._log('deck_reordered',player=owner)
 elif name=='historical_copy_die':
  if source in p.minions:source.health=0
 elif name=='historical_copy_brittleskin':
  if game.current!=owner:game._deal_effect(game.hero_id(1-owner),3,ctx)
 elif name=='historical_copy_invincible':
  choices=[m for m in p.minions if m is not source and m.health>0 and has_tribe(game._card_data(m),'UNDEAD')]
  if choices:
   minion=game.rng.choice(choices);game._buff(minion,5,5);minion.keywords.add('TAUNT')
 elif name=='historical_copy_corpse_hand_attack':
  if p.corpses>=op[1]:
   game._spend_corpses(owner,op[1])
   for card in p.hand:
    if game._card_data(card)['type']=='MINION':_saidan_add(card,'attack_bonus',op[2])
 elif name=='historical_copy_shockspitter':game._deal_effect(ctx.get('target',0),1+p.hero_attacks_total,ctx)
 elif name=='historical_copy_replace_enemy_hand':
  cards=[game._copy_card(card,source_owner=1-owner) for card in tuple(q.hand)]
  for card in tuple(p.hand):game._zone_card_removed(owner,card,'hand','replace')
  p.hand.clear()
  for card in cards:game._enter_hand(owner,card)
 elif name=='historical_copy_enemy_hand_sample':
  choices=game.rng.sample(list(q.hand),min(op[1],len(q.hand)))
  for card in choices:game._enter_hand(owner,game._copy_card(card,source_owner=1-owner))
 elif name=='historical_copy_illusionist':
  from .identities import canonical_identity
  identity=canonical_identity(game._card_data(source),game.cards) if source is not None else 'RLK_217'
  choices=[card for card in p.deck if game._card_data(card)['type']=='MINION' and 'DEATHRATTLE' in game._card_mechanics(card) and canonical_identity(game._card_data(card),game.cards)!=identity]
  if choices:
   card=game._copy_card(game.rng.choice(choices),source_owner=owner);game._mutation_set_stats(card,owner,4,4);card.cost_delta=getattr(card,'cost_delta',0)-(4);game._enter_hand(owner,card)
 elif name=='historical_copy_enemy_deck_all':
  cards=[game._copy_card(c,source_owner=1-owner) for c in tuple(q.deck)]
  p.deck.extend(cards);game.rng.shuffle(p.deck)
  if cards:game._record_deck_insertion(owner,owner,len(cards),'shuffle',cards=cards)
 elif name=='historical_copy_enemy_top':
  if q.deck:game._enter_hand(owner,game._copy_card(q.deck[-1],source_owner=1-owner))
 elif name=='historical_copy_hero_set':
  before=p.health
  if p.health!=op[1]:p.hero_health_changed_turn=True
  p.health=op[1];p.max_health=max(p.max_health,p.health)
  if p.health>before:game._queue_event('historical_hero_health_gained',owner=owner,amount=p.health-before)
 elif name=='historical_copy_kaahrj':
  if target is not None and source in p.minions and source.card_id=='DRG_308':source.attached_death_effects.append(('summon',target.card_id,1))
 elif name=='historical_copy_mankrik_summon':
  before={m.uid for m in p.all_minions}
  game._summon(owner,'BAR_721t2',entry_origin='effect',entry_site='mankrik_wife')
  op[1]['uids']=[m.uid for m in p.all_minions if m.uid not in before]
 elif name=='historical_copy_steal_weapon':
  if q.weapon is not None:
   weapon=deepcopy(q.weapon);card=q.equipped_card;q.weapon=None;q.equipped_card=None
   game._equip(owner,weapon['card_id'],attack_bonus=card.attack_bonus if card is not None else 0,physical_card=card)
   previous_attack=game._hero_attack(owner);p.weapon=weapon
   game._record_hero_stat_gain(owner,'attack',game._hero_attack(owner)-previous_attack);game._log('weapon_stolen',player=owner,card=weapon['card_id'])
 elif name=='historical_copy_weapon_spell_bonus':
  values=getattr(p,'historical_weapon_spell_bonuses',[]);values.append(dict(turn=game.turn,amount=op[1]));p.historical_weapon_spell_bonuses=values
 elif name=='historical_copy_shuffle_plagues':
  from .pools import require_fixed_cards
  require_fixed_cards(PLAGUES,game.cards)
  cards=[Card(game._new_id(),game.rng.choice(PLAGUES)) for _ in range(op[1])]
  q.deck.extend(cards);game.rng.shuffle(q.deck);game._record_deck_insertion(1-owner,owner,len(cards),'shuffle',cards=cards)
  p.historical_plagues_shuffled=getattr(p,'historical_plagues_shuffled',0)+len(cards)
 elif name=='historical_copy_helya':
  from .pools import require_fixed_cards
  require_fixed_cards(PLAGUES,game.cards);q.historical_unending_plagues=True
  cards=[Card(game._new_id(),cid) for cid in PLAGUES];q.deck.extend(cards);game.rng.shuffle(q.deck);game._record_deck_insertion(1-owner,owner,3,'shuffle',cards=cards)
  p.historical_plagues_shuffled=getattr(p,'historical_plagues_shuffled',0)+3
 elif name=='historical_copy_destroy_plague':
  card=next((c for c in q.deck if c.uid==op[1]),None)
  if card is not None:q.deck.remove(card);game._zone_card_removed(1-owner,card,'deck','destroy');game._log('destroy_deck_card',player=1-owner,card=card.card_id)
 elif name=='historical_copy_plague_effect':
  if op[1]=='TTN_450t':game._heal(game.hero_id(1-owner),2,healer=owner,spell=True)
  elif op[1]=='TTN_450t2':game._summon(1-owner,'RLK_070t',entry_origin='effect',entry_site='unholy_plague')
  else:p.historical_frost_fever=getattr(p,'historical_frost_fever',0)+1
 elif name=='historical_copy_unending_plague':
  if ctx.get('cast_when_drawn') and getattr(p,'historical_unending_plagues',False):
   card=Card(game._new_id(),ctx['card_id']);p.deck.append(card);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
   q.historical_plagues_shuffled=getattr(q,'historical_plagues_shuffled',0)+1
 elif name=='historical_copy_give_curse':
  p.historical_abyssal_counter=getattr(p,'historical_abyssal_counter',0)+1
  card=Card(game._new_id(),'TSC_955t');game._b60_state(card).update(abyssal_damage=p.historical_abyssal_counter,abyssal_caster=owner,abyssal_ticks=0)
  game._enter_hand(1-owner,card)
 elif name=='historical_copy_curse_tick':
  card=next((c for c in p.hand if c.uid==op[1] and c.card_id=='TSC_955t'),None)
  if card is not None:
   state=game._b60_state(card);state['abyssal_ticks']=state.get('abyssal_ticks',0)+1
   damage=state.get('abyssal_damage',1);caster=state.get('abyssal_caster',1-owner)
   dealt=game._deal_effect(game.hero_id(owner),damage,dict(owner=owner,source=None,target=game.hero_id(owner),spell=True,card_id='TSC_955t',physical_card=card,bonus=game._spell_damage(owner,'TSC_955t',card),lifesteal=False))
   if dealt and game._active('TSC_959',caster):game._heal(game.hero_id(caster),dealt,healer=caster)
 elif name=='historical_copy_curse_expire':
  card=next((c for c in p.hand if c.uid==op[1] and c.card_id=='TSC_955t'),None)
  if card is not None and getattr(card,'rule_state',{}).get('abyssal_ticks',0)>=2:game._zone_manager.discard_cards(game,owner,[card])
 elif name=='historical_copy_ivus':
  spent=p.mana;p.mana=0;game._b60_spend_mana(owner,spent)
  if source in p.minions and source.health>0:
   for _ in range(spent):
    choices=['stats']+[keyword for keyword in ('RUSH','DIVINE_SHIELD','TAUNT') if keyword not in game._effective_keywords(source)]
    result=game.rng.choice(choices)
    if result=='stats':game._buff(source,2,2)
    else:source.keywords.add(result)
 elif name=='historical_copy_hit_bound':game._deal_effect(op[1],op[2],ctx)
 elif name=='historical_copy_flik':
  if target is not None:
   from .identities import canonical_identity
   identity=canonical_identity(game._card_data(target),game.cards)
   for recipient,player in enumerate(game.players):
    for minion in player.minions:
     if canonical_identity(game._card_data(minion),game.cards)==identity:minion.health=0
    for zone_name in ('hand','deck'):
     zone=getattr(player,zone_name)
     for card in tuple(zone):
      if canonical_identity(game._card_data(card),game.cards)==identity:
       zone.remove(card);game._zone_card_removed(recipient,card,zone_name,'destroy');game._log('destroy_zone_card',player=recipient,zone=zone_name,card=card.card_id)
 elif name=='historical_copy_blazing_card':
  from .selectors import has_school
  index=next((i for i,card in enumerate(p.deck) if card.uid==op[1]),None)
  if index is not None:
   card=p.deck[index];data=game._card_data(card)
   if has_school(data,'FIRE') or has_tribe(data,'ELEMENTAL'):game._take_deck_draw(owner,index)
   else:p.deck.pop(index);game._zone_card_removed(owner,card,'deck','destroy');game._log('destroy_deck_card',player=owner,card=card.card_id)
 elif name=='historical_copy_patchwerk':
  if op[1]=='board':
   victims=[m for m in q.minions if m.health>0]
   if victims:game.rng.choice(victims).health=0
  else:
   zone=getattr(q,op[1]);victims=[card for card in zone if game._card_data(card)['type']=='MINION']
   if victims:
    card=game.rng.choice(victims);zone.remove(card);game._zone_card_removed(1-owner,card,op[1],'destroy');game._log('destroy_zone_card',player=1-owner,zone=op[1],card=card.card_id)
 elif name=='historical_copy_capture_destroy':
  if target is not None:
   cid=target.card_id
   if source in p.minions:
    if op[2]:source.rule_state.setdefault('historical_cubicle_ids',[]).append(cid)
    elif source.card_id=='TTN_754':source.attached_death_effects.append(('summon',cid,op[1]))
   target.health=0
 elif name=='historical_copy_chef':
  before={m.uid for m in p.all_minions};game._summon(owner,'FP1_007',entry_origin='effect',entry_site='historical_chef',entry_source=source)
  if source in p.minions and source.card_id=='VAC_946':
   for minion in p.all_minions:
    if minion.uid not in before and minion.card_id=='FP1_007':source.attached_death_effects.append(('historical_copy_kill_bound',minion.uid))
 elif name=='historical_copy_dang_blasted':
  victims=[m.uid for player in game.players for m in player.minions if m.health>0 and not(m.owner==owner and has_tribe(game._card_data(m),'ELEMENTAL'))]
  with game._damage_batch():
   for uid in victims:game._deal_effect(uid,2,ctx)
 elif name=='historical_copy_ozruk':
  count=sum(record.turn==p.last_turn_ended and game._card_data(record.card)['type']=='MINION' and has_tribe(game._card_data(record.card),'ELEMENTAL') for record in p.replay_history)
  if source in p.minions:game._buff(source,0,5*count)
 elif name=='historical_copy_timed_cost':
  for recipient in ((1-owner,) if op[4]=='enemy' else (owner,1-owner)):
   effect=dict(selector=op[1],amount=op[2],start=game.turn+1 if op[4]=='enemy' else game.turn,end=game.turn+1 if op[4]=='enemy' else game.turn+2)
   if op[3] is not None:effect['set_cost']=op[3]
   game.players[recipient].timed_cost_increases.append(effect)
 elif name=='historical_copy_sea_shill':p.cost_effects.append(dict(selector='HISTORICAL_FOREIGN',owner=owner,amount=2,expires=None))
 elif name=='historical_copy_jeweler':p.historical_elusive_until=max(getattr(p,'historical_elusive_until',-1),game.turn+2)
 elif name=='historical_copy_timewarden':p.historical_timewarden_until=max(getattr(p,'historical_timewarden_until',-1),game.turn+2)
 elif name=='historical_copy_astrobiologist':
  game._schedule_turn_effect(owner,'start',1,1,(discover(pool(card_type='SPELL',classes='own_or_neutral')),),source_card_id='GDB_874')
 elif name=='historical_copy_edge_lock':q.historical_edge_lock_turn=game.turn+1
 elif name=='historical_copy_hand_lock_choice':
  from engine.cards import UnsupportedCard
  if q.hand:
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite hand-lock choice')
   options=[dict(card_id=card.card_id,uid=card.uid) for card in game.rng.sample(list(q.hand),min(3,len(q.hand)))]
   game.pending_choice=dict(kind='historical_hand_lock',owner=owner,recipient=1-owner,turn=game.turn+1,options=options);game.phase='choice'
 elif name=='historical_copy_next_draw_discount':p.historical_next_draw_discount=getattr(p,'historical_next_draw_discount',0)+op[1]
 elif name=='historical_copy_next_draw_spell_copy':p.historical_next_draw_spell_copies=getattr(p,'historical_next_draw_spell_copies',0)+1
 elif name=='historical_copy_replace_zones':
  request=pool(card_type='MINION',classes='other') if op[1]=='foreign' else pool(card_type='MINION',rarity='LEGENDARY')
  values=game._generation_candidates(request,owner)
  if values:
   for zone_name in ('hand','deck'):
    zone=getattr(p,zone_name)
    for old in tuple(zone):
     if op[1]=='foreign' and game._card_data(old)['type']!='MINION':continue
     index=zone.index(old);card=Card(game._new_id(),game.rng.choice(values))
     if op[1]=='foreign':card.cost_delta=-2
     if zone_name=='deck':zone[index]=card
     else:
      zone.remove(old);entered=game._enter_hand(owner,card)
      if entered is not None:zone.remove(entered);zone.insert(index,entered)
 elif name=='historical_copy_gallywix':
  card=game._fresh_replay_card(ctx['event']['physical_card']);game._enter_hand(owner,card);game._add(1-owner,'GVG_028t')
 elif name=='historical_copy_voraxx_plant':
  minion=game._summon(owner,'UNG_999t2t1',entry_origin='effect',entry_site='historical_voraxx',entry_source=source);op[1]['uid']=getattr(minion,'uid',None)
 elif name=='historical_copy_raza':
  from .identities import canonical_identity
  identities=[canonical_identity(game._card_data(card),game.cards) for card in p.deck]
  if len(identities)==len(set(identities)):p.historical_raza=True
 elif name=='historical_copy_next_payment':p.payment_effects.append(dict(kind='historical_payment',payment=op[1],selector=op[2],uses=op[3],start=game.turn,end=game.turn))
 elif name=='historical_copy_ulthok':q.payment_effects.append(dict(kind='historical_payment',payment='health',selector='all',start=game.turn+1,end=game.turn+1))
 elif name=='historical_copy_take_fatigue':
  p.fatigue+=1;op[1]['amount']=p.fatigue;game._damage(game.hero_id(owner),p.fatigue,damage_source=None,damage_cause='fatigue')
 elif name=='historical_copy_fatigue_reward':
  if op[1]=='buff' and source in p.minions and source.health>0:game._buff(source,op[2].get('amount',0),op[2].get('amount',0))
 elif name=='historical_copy_lowest_damage':
  uid=game._force_target(owner,'lowest')
  if uid:game._deal_effect(uid,op[1],ctx)
 elif name=='historical_copy_olgra_buff':
  count=sum(m.health<m.max_health and m.health>0 for player in game.players for m in player.minions)
  if source in p.minions:game._buff(source,count,count)
 elif name=='historical_copy_shambler':
  if source in p.minions and target is not None:game._set_entity_stats(source,target.attack,target.health)
 elif name=='historical_copy_braggart':
  minions=[m for player in game.players for m in player.minions if m.health>0]
  if source in p.minions and minions:game._set_entity_stats(source,max(m.attack for m in minions),max(m.health for m in minions))
 elif name=='historical_copy_egg_summon':
  minion=game._summon(owner,'GDB_840t',entry_origin='deathrattle',entry_site='historical_egg',entry_source=source);op[1]['uid']=getattr(minion,'uid',None)
 elif name=='historical_copy_enemy_hand':
  minion=game._recruit_from_zone(1-owner,'hand',(),site='historical_bloodstinger');op[1]['uid']=getattr(minion,'uid',None)
 elif name=='historical_copy_corpse_bride':
  spent=min(10,p.corpses);game._spend_corpses(owner,spent)
  game._summon(owner,'RLK_506t',entry_stats=(spent,spent),entry_origin='effect',entry_site='historical_corpse_bride',entry_source=source)
 elif name=='historical_copy_dreadsteed':
  game._schedule_turn_effect(game.current,'end',0,1,(('historical_copy_summon_owner',owner,'AT_019'),),source_card_id='AT_019')
 elif name=='historical_copy_summon_owner':game._summon(op[1],op[2],entry_origin='deathrattle',entry_site='historical_delayed_death')
 elif name=='historical_copy_lothar_reward':
  minion=live(game,op[1]);history=getattr(game,'_combat_kill_history',{}).get(op[1],())
  if minion is not None and any(victim.uid==op[2] for victim in history[op[3]:]):game._buff(minion,3,3)
 elif name=='historical_copy_steal_target_health':
  if target is not None and source in p.minions:
   game._buff(target,0,-op[1]);game._buff(source,0,op[1])
 elif name=='historical_copy_pupil':
  memory=getattr(ctx.get('physical_card'),'_historical_held_spell_memory',())
  if len(memory)>=3:
   from engine.cards import UnsupportedCard
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite held-spell choice')
   seen=set();options=[]
   for row in memory[:3]:
    cid=row['card'].card_id
    if cid not in seen:seen.add(cid);options.append(dict(card_id=cid))
   game.pending_choice=dict(owner=owner,kind='historical_held_spell',options=options);game.phase='choice'
 elif name=='historical_copy_drawn_copy':
  card=ctx['event']['card']
  if game._card_data(card)['type']=='MINION':
   if op[1]=='hand':game._enter_hand(owner,game._copy_card(card,source_owner=owner))
   else:
    before={m.uid for m in p.all_minions}
    game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_stats=(1,1) if op[1]=='dorian' else None,entry_keywords=('RUSH',) if op[1]=='betrug' else (),entry_origin='copy',entry_zone='hand',entry_source=card,entry_site='historical_drawn_copy')
    if op[1]=='betrug':
     for minion in p.all_minions:
      if minion.uid not in before and minion.card_id==card.card_id:game._schedule_turn_effect(game.current,'end',0,1,(('historical_copy_recruited_kill',dict(uid=minion.uid)),),source_card_id='DAL_607')
 elif name=='historical_copy_drawn_health':
  uid=ctx['event']['card'].uid;card=next((c for c in p.hand if c.uid==uid),None)
  if card is not None:game._b60_state(card)['health_payment']=True
 elif name=='historical_copy_literal_family':
  from .pools import require_fixed_cards
  families={'adventurer':ADVENTURERS,'soldier':SOLDIERS,'sparkbot':SPARKBOTS,'crewmate':CREWMATES}
  ids=families[op[1]];require_fixed_cards(ids,game.cards)
  cid=game.rng.choice(ids)
  if op[2]=='hand':game._add(owner,cid)
  else:game._summon(owner,cid,entry_origin='deathrattle' if source is not None and source.health<=0 else 'effect',entry_site='historical_literal_bonus',entry_source=source)
 elif name=='historical_copy_board_bonus':
  for minion in p.minions:
   if minion.health>0 and (op[1]=='all' or minion is not source and has_tribe(game._card_data(minion),'BEAST')):game._grant_bonus_effects(minion,1)
 elif name=='historical_copy_wayfinder':
  if source in p.minions and source.health>0:
   before=set(source.keywords);game._grant_bonus_effects(source,2)
   for keyword in sorted(set(source.keywords)-before):p.cost_effects.append(dict(selector='DRAENEI',amount=0,grant_keyword=keyword,expires=None))
 elif name=='historical_copy_amalgam_band':
  from .quest_families import maximum_tribe_matching
  from .selectors import effective_tribes,TRIBES
  plays=[]
  for record in p.played_history:
   data=game.cards[record['card_id']]
   if data['type']=='MINION':plays.append(set(TRIBES)-{'ALL'} if 'ALL' in effective_tribes(data) else set(effective_tribes(data)))
  current=game.cards[ctx['card_id']];tribes=effective_tribes(current)
  if current['type']=='MINION':plays.append(set(TRIBES)-{'ALL'} if 'ALL' in tribes else set(tribes))
  if source in p.minions:game._grant_bonus_effects(source,len(maximum_tribe_matching(plays)))
 elif name=='historical_copy_elitist_snob':
  from .selectors import has_class
  count=sum(has_class(game._card_data(card),'PALADIN') for card in p.hand)
  if source in p.minions and source.health>0:
   for _ in range(count):
    choices=sorted(set(('DIVINE_SHIELD','LIFESTEAL','RUSH','TAUNT'))-game._effective_keywords(source))
    if not choices:break
    source.keywords.add(game.rng.choice(choices))
 elif name=='historical_copy_healing_damage_turn':p.historical_healing_damage_turn=game.turn
 elif name=='historical_copy_healing_damage_next':p.historical_healing_damage_charges=getattr(p,'historical_healing_damage_charges',0)+1
 elif name in ('historical_copy_evolve_target','historical_copy_evolve_uid'):
  victim=target if name.endswith('target') else live(game,op[1]);increase=op[1] if name.endswith('target') else op[2]
  if victim is not None:
   from .transformations import evolve_pool
   request=evolve_pool(game._card_stat(victim,'cost',victim.owner),increase)
   candidates=game._generation_candidates(request,owner)
   if candidates:game._transform(victim,game.rng.choice(candidates))
 elif name=='historical_copy_tinkmaster':
  from .pools import require_fixed_cards
  outcomes=('EX1_tk28','EX1_tk29');require_fixed_cards(outcomes,game.cards)
  victims=[m for player in game.players for m in player.minions if m is not source and m.health>0]
  if victims:game._transform(game.rng.choice(victims),game.rng.choice(outcomes))
 elif name=='historical_copy_fang':
  if source in p.minions and any(has_tribe(game._card_data(m),'BEAST') for m in p.minions):game._transform(source,'GVG_080t')
 elif name in ('historical_copy_literal_target','historical_copy_literal_uid'):
  victim=target if name.endswith('target') else live(game,op[1]);cid=op[1] if name.endswith('target') else op[2]
  if victim is not None:game._transform(victim,cid)
 elif name=='historical_copy_taldaram':
  if all(game._card_data(c)['cost']!=3 for c in p.deck):replace(game,source,target,(3,3))
 elif name=='historical_copy_spread_plague':
  candidates=[c for c in q.hand if game._card_data(c)['type']=='MINION']
  if candidates:game._mutation_replace_card(game.rng.choice(candidates),'RLK_831')
 elif name=='historical_copy_weapon_evolve':
  if p.weapon is not None:
   cost=game.cards[p.weapon['card_id']]['cost']+1
   candidates=game._generation_candidates(pool(card_type='WEAPON',minimum=cost,maximum=cost),owner)
   if candidates:
    cid=game.rng.choice(candidates);data=game.cards[cid];p.equipped_card=Card(game._new_id(),cid)
    previous_attack=game._hero_attack(owner)
    p.weapon=dict(card_id=cid,attack=data['attack'],durability=data.get('durability') or data.get('health',0))
    game._record_hero_stat_gain(owner,'attack',game._hero_attack(owner)-previous_attack)
    game._refresh_auras();game._log('transform_weapon',player=owner,card=cid)
 elif name=='historical_copy_transmogrifier':
  uid=ctx.get('event',{}).get('card').uid
  card=next((c for c in p.hand if c.uid==uid),None)
  if card is not None:
   candidates=game._generation_candidates(pool(card_type='MINION',rarity='LEGENDARY'),owner)
   if candidates:game._mutation_replace_card(card,game.rng.choice(candidates))
 elif name=='historical_copy_toxin':
  from .pools import require_fixed_cards
  require_fixed_cards(TOXINS,game.cards);game._add(owner,game.rng.choice(TOXINS))
 elif name=='historical_copy_toxin_bounce':
  if target is not None:game._bounce(target,-2)
 elif name=='historical_copy_pyros':
  card=Card(game._new_id(),op[1])
  if source is not None:game._carry_origin(source,card)
  game._enter_hand(owner,card)
 elif name=='historical_copy_weasel':
  if source is not None:
   card=game._fresh_replay_card(source);game._carry_origin(source,card)
   q.deck.append(card);game.rng.shuffle(q.deck);game._record_deck_insertion(1-owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_copy_azari':
  values=list(q.deck);q.deck.clear()
  for card in values:
   game._zone_card_removed(1-owner,card,'deck','destroy');game._log('destroy_deck_card',player=1-owner,card=game._card_data(card)['id'])
  game._refresh_auras()
 elif name=='historical_copy_cube':
  if source in p.minions and target is not None:
   cid=target.card_id
   
   if source.card_id=='LOOT_161':source.attached_death_effects.append(('summon',cid,2))
   target.health=0
 elif name=='historical_copy_recruit_one':
  minion=game._recruit_from_zone(owner,op[1],op[2],keyword=op[3],site='historical_recruit')
  if op[4] is not None:op[4]['uid']=getattr(minion,'uid',None)
 elif name=='historical_copy_recruit_other':game._recruit_from_zone(op[1],'deck',(),site='historical_enemy_recruit')
 elif name=='historical_copy_less_attack_recruit':
  if source is not None:game._recruit_from_zone(owner,'deck',(('attack','le',source.attack-1),),site='historical_less_attack')
 elif name=='historical_copy_recruited_death':
  uid=op[1].get('uid')
  if uid is not None:game._effect(('historical_batch_trigger_target_death',),dict(ctx,target=uid))
 elif name=='historical_copy_recruited_kill':
  minion=live(game,op[1].get('uid'))
  if minion is not None:minion.health=0
 elif name=='historical_copy_recruit_uid':
  zone=getattr(p,op[1]);card=next((c for c in zone if getattr(c,'uid',None)==op[2]),None)
  if card is not None and len(p.board)<7:
   zone.remove(card);game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='recruit',entry_site='historical_bound_recruit',entry_zone=op[1],entry_source=card)
 elif name=='historical_copy_recruit_conditional':
  from .identities import canonical_identity
  if op[1]=='held_demon':
   if getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_held_casts',0)>=3:
    identity=canonical_identity(game.cards['NX2_026'],game.cards)
    candidates=[c for c in p.deck if game._card_data(c)['type']=='MINION' and has_tribe(game._card_data(c),'DEMON') and canonical_identity(game._card_data(c),game.cards)!=identity]
    if candidates:
     chosen=game.rng.choice(candidates);game._effect(('historical_copy_recruit_uid','deck',chosen.uid),ctx)
  else:
   minions=[c for c in p.deck if game._card_data(c)['type']=='MINION']
   cost=game._card_stat(source,'cost',owner) if source is not None else game.cards['AV_100']['cost']
   if minions and all(game._card_stat(c,'cost',owner)<cost for c in minions):game._recruit_from_zone(owner,'deck',(),site='historical_drekthar')
 elif name=='historical_copy_tavish':
  event=ctx.get('event',{});cost=game.cards[event['attacker_card_id']]['cost']-1
  game._recruit_from_zone(owner,'deck',(('tribe','eq','BEAST'),('cost','eq',cost)),site='historical_tavish')
 elif name=='historical_copy_put_ten':
  candidates=[c for c in p.deck if game._card_data(c)['type']=='MINION' and game._card_stat(c,'cost',owner)==10]
  if candidates:
   card=game.rng.choice(candidates);p.deck.remove(card);game._enter_hand(owner,card if isinstance(card,Card) else Card(game._new_id(),card))
 elif name=='historical_copy_next_spell_bonus':
  values=getattr(p,'historical_next_spell_bonuses',[]);values.append(dict(turn=game.turn,amount=op[1]));p.historical_next_spell_bonuses=values
 elif name=='historical_copy_next_spell_repeat':p.historical_spell_repeat_turn=game.turn
 elif name=='historical_copy_next_spell_lifesteal':p.historical_next_spell_lifesteal=True
 elif name=='historical_copy_double_hand':
  for card in p.hand:
   if game._card_data(card)['type']=='MINION':game._mutation_set_stats(card,owner,2*game._card_stat(card,'attack',owner),2*game._card_stat(card,'health',owner))
 elif name=='historical_copy_odd_health':
  if all(game._card_data(card)['cost']%2 for card in p.deck):
   for minion in p.minions:
    if minion is not source and minion.health>0:game._buff(minion,0,minion.health)
 elif name=='historical_copy_spend_double':
  if p.mana>=op[1] and source in p.minions:
   p.mana-=op[1];game._b60_spend_mana(owner,op[1]);game._buff(source,source.attack,source.health)
 elif name=='historical_copy_snowflurry':
  p.next_power_cost_effects.append(dict(kind='set',amount=0))
  p.historical_next_power_freeze=True
 elif name=='historical_copy_power_bonus':
  values=getattr(p,'historical_next_power_damage',[]);values.append(dict(turn=game.turn,amount=op[1]));p.historical_next_power_damage=values
 elif name=='historical_copy_saboteur':q.next_power_cost_effects.append(dict(kind='add',amount=5,not_before=game.turn+1,expires=game.turn+1))
 elif name=='historical_copy_power_permanent':
  field='historical_power_armor' if op[1]=='armor' else 'historical_power_attack'
  setattr(p,field,getattr(p,field,0)+1)
 elif name=='historical_copy_void_crusher':
  victims=[]
  for player in game.players:
   candidates=[m for m in player.minions if m.health>0]
   if candidates:victims.append(game.rng.choice(candidates))
  for victim in victims:victim.health=0
 elif name=='historical_copy_power_hit':
  mode,amount=op[1:];uid=ctx.get('target',0)
  if mode=='own_hero':uid=game.hero_id(owner)
  elif mode=='enemy_hero':uid=game.hero_id(1-owner)
  elif mode=='random_enemy':uid=game.rng.choice([game.hero_id(1-owner)]+[m.uid for m in q.minions if m.health>0])
  if uid:
   bonus=sum((1 if m.card_id=='AT_003' else 2 if m.card_id=='YOD_008' else 0) for m in p.minions if not m.silenced and m.health>0)
   from .historical_damage_modifiers import power_multiplier
   amount=(amount+bonus+ctx.get('power_damage_bonus',0))*power_multiplier(game,owner)
   dealt=game._deal_effect(uid,amount,dict(ctx,bonus=0,spell=False))
   p.historical_power_damage_total=getattr(p,'historical_power_damage_total',0)+dealt
   if ctx.get('power_freeze') or game._active('ICC_068',owner):
    if uid<0 or live(game,uid) is not None:game._freeze(uid)
 elif name=='historical_copy_spell_delivery':
  donor=op[1]['card'];card=game._fresh_replay_card(donor)
  game._carry_origin(donor,card,copied=True,source_owner=owner)
  if op[2]=='hand':game._enter_hand(owner,card)
  else:
   p.deck.append(card);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_copy_muckmorph':
  from .identities import canonical_identity
  identity=canonical_identity(game._card_data(source),game.cards) if source is not None else None
  candidates=[c for c in p.deck if game._card_data(c)['type']=='MINION' and canonical_identity(game._card_data(c),game.cards)!=identity]
  if candidates and source in p.minions:
   donor=game.rng.choice(candidates)
   # A deck-to-board transformation retains the physical donor enchantments.
   from .game import Minion
   data=game._card_data(donor)
   snapshot=Minion(-1,data['id'],owner,game._card_stat(donor,'attack',owner),game._card_stat(donor,'health',owner),game._card_stat(donor,'health',owner),set(data.get('mechanics',())))
   if isinstance(donor,Card):
    from .base_stats import carry_base_stats
    carry_base_stats(donor,snapshot)
    game._held_bonus_entry(snapshot,donor);game._dark_entry(snapshot,donor);game._stored_entry(snapshot,donor);game._forge_entry(snapshot,donor)
   replace(game,source,snapshot,(4,4))
 elif name=='historical_copy_death_shuffle':
  if source is not None:
   card=game._fresh_replay_card(source);game._carry_origin(source,card,copied=True,source_owner=owner)
   p.deck.append(card);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_copy_random_control':
  candidates=[m for m in q.minions if m.health>0]
  if candidates and len(p.board)<7:
   chosen=game.rng.choice(candidates);q.board.remove(chosen);chosen.owner=owner;chosen.summoned_turn=game.turn;chosen.attacks=0;p.board.append(chosen);game._refresh_auras()
 elif name=='historical_copy_kill_bound':
  victim=live(game,op[1])
  if victim is not None:victim.health=0
 elif name=='historical_copy_devour_gain':
  if source in p.minions and source.health>0:game._buff(source,op[1],op[2])
 elif name=='historical_copy_permanent_battlecries':
  from .identities import canonical_identity
  identities=[canonical_identity(game.cards[cid],game.cards) for cid in p.starting_deck]
  if len(identities)==len(set(identities)):p.historical_double_battlecries=True
 elif name in ('historical_copy_target_delivery','historical_copy_target_snapshot'):
  donor=target if name=='historical_copy_target_delivery' else op[1]
  args=op[1:] if name=='historical_copy_target_delivery' else op[2:]
  zone,count,attack,health,cost,temporary=args
  if donor is not None:
   shuffled=[]
   for _ in range(count):
    card=game._fresh_replay_card(donor)
    game._carry_origin(donor,card,copied=True,source_owner=donor.owner)
    if attack is not None:game._mutation_set_stats(card,owner,attack,health)
    if cost is not None:game._set_card_cost(card,cost)
    if temporary:game._make_temporary(card)
    if zone=='hand':game._enter_hand(owner,card)
    else:p.deck.append(card);shuffled.append(card)
   if zone=='deck':
    game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,count,'shuffle',cards=shuffled)
 elif name=='historical_copy_hand_edges':
  values=list(p.hand)
  if values:
   donors=(values[0],values[-1])
   for card in donors:game._clone_hand_card(owner,card,source_owner=owner)
 elif name=='historical_copy_last_enemy':
  if q.replay_history:game._clone_hand_card(owner,q.replay_history[-1].card,source_owner=1-owner)
 elif name=='historical_copy_discount_hand':
  from .selectors import has_class
  for card in p.hand:
   data=game._card_data(card)
   applies=(not has_class(data,p.hero_class) and not has_class(data,'NEUTRAL')) if op[1]=='foreign' else not game._started_in_deck(card,owner)
   if applies:card.cost_delta=getattr(card,'cost_delta',0)-(op[2])
 elif name=='historical_copy_remove_enemy_stealth':
  for m in q.minions:
   m.keywords.discard('STEALTH');m.temporary_keywords[:]=[e for e in m.temporary_keywords if e['keyword']!='STEALTH']
 elif name=='historical_copy_double_elementals':
  for zone in (p.hand,p.deck):
   for i,value in enumerate(zone):
    if has_tribe(game._card_data(value),'ELEMENTAL'):
     card=value if isinstance(value,Card) else Card(game._new_id(),value)
     game._mutation_set_stats(card,owner,2*game._card_stat(card,'attack',owner),2*game._card_stat(card,'health',owner));zone[i]=card
 elif name=='historical_copy_attack_extremes':
  minions=[m for player in game.players for m in player.minions if m.health>0]
  if len(minions)>=2:
   high=max(m.attack for m in minions);low=min(m.attack for m in minions)
   if high!=low:
    a=game.rng.choice([m for m in minions if m.attack==high]);b=game.rng.choice([m for m in minions if m.attack==low])
    game._set_minion_attack(a,low);game._set_minion_attack(b,high)
 elif name=='historical_copy_eat_enemy_hand':
  choices=[c for c in q.hand if game._card_data(c)['type']=='MINION']
  if choices:
   card=game.rng.choice(choices);attack=game._card_stat(card,'attack',1-owner);health=game._card_stat(card,'health',1-owner)
   q.hand.remove(card);game._zone_card_removed(1-owner,card,'hand','destroy');game._log('devour_hand',player=1-owner,card=card.card_id)
   if source is not None and source in p.minions:game._buff(source,attack,health)
 elif name=='historical_copy_discard_lowest':
  for _ in range(op[1]):
   if not p.hand:break
   minimum=min(game._cost(c,owner) for c in p.hand);card=game.rng.choice([c for c in p.hand if game._cost(c,owner)==minimum])
   game._zone_manager.discard_cards(game,owner,[card])
 elif name=='historical_copy_enemy_spell':
  choices=[c for c in q.deck if game._card_data(c)['type']=='SPELL']
  if choices:game._enter_hand(owner,game._copy_card(game.rng.choice(choices),source_owner=1-owner))
 elif name=='historical_copy_transform_target':
  replace(game,source,target,None if op[1] is None else (op[1],op[2]))
 elif name=='historical_copy_transform_zone':
  cards=[c for c in getattr(p,op[1]) if game._card_data(c)['type']=='MINION' and (op[2] is None or has_tribe(game._card_data(c),op[2]))]
  if cards and source in p.minions:
   card=game.rng.choice(cards);cid=game._card_data(card)['id'];position=p.board.index(source)
   from .historical_replacements import vashj_replaces,vashj_summon
   if vashj_replaces(game,source,cid):
    vashj_summon(game,source,cid,stats=(op[3],op[4]));return True
   game._colossal_preflight(cid,owner=owner);game._herald_entry_preflight(owner,cid)
   p.board.remove(source);result=game._create_minion(owner,cid,position)
   if result is not None:
    game._set_entity_stats(result,op[3],op[4]);game._colossal_enter(result);game._refresh_auras();game._log('transform',entity=source.uid,replacement=result.uid,card=cid)
 elif name=='historical_copy_snapshot':
  game._summon(owner,op[1].card_id,copy_from=op[1],entry_stats=None if op[2] is None else (op[2],op[3]),entry_origin='copy',entry_site='historical_group_copy',entry_source=op[1])
 elif name=='historical_copy_summon_zone':
  cards=[c for c in getattr(p,op[1]) if game._card_data(c)['type']=='MINION']
  if cards:
   card=game.rng.choice(cards);cid=game._card_data(card)['id']
   game._summon(owner,cid,attack_bonus=getattr(card,'attack_bonus',0),health_bonus=getattr(card,'health_bonus',0),entry_stats=None if op[2] is None else (op[2],op[3]),entry_keywords=op[4],entry_origin='copy',entry_zone=op[1],entry_source=card,entry_site='historical_zone_copy')
 elif name=='historical_copy_played':
  donor=live(game,ctx['event'].get('source'));stats=None if op[2] is None else (op[2],op[3])
  if donor is not None:
   if op[1]=='transform':replace(game,source,donor,stats)
   else:game._summon(owner,donor.card_id,copy_from=donor,entry_stats=stats,entry_origin='copy',entry_site='historical_played_copy',entry_source=donor)
 elif name=='historical_copy_neighbor':
  if source in p.minions:
   i=p.board.index(source);neighbors=[p.board[j] for j in (i-1,i+1) if 0<=j<len(p.board) and p.board[j] in p.minions]
   if neighbors:replace(game,game.rng.choice(neighbors),source)
 elif name=='historical_copy_swap':
  if source in p.minions and target is not None:
   sa,sh=source.attack,source.health;ta,th=target.attack,target.health
   game._set_entity_stats(source,ta if op[2] in ('attack','stats') else sa,th if op[2] in ('health','stats') else sh)
   game._set_entity_stats(target,sa if op[2] in ('attack','stats') else ta,sh if op[2] in ('health','stats') else th)
 elif name=='historical_copy_swap_others':
  for player in game.players:
   for m in player.minions:
    if m is not source:game._set_entity_stats(m,m.health,m.attack)
 elif name=='historical_copy_double_deck':
  for i,value in enumerate(p.deck):
   if game._card_data(value)['type']=='MINION':
    card=value if isinstance(value,Card) else Card(game._new_id(),value)
    a=game._card_stat(card,'attack',owner);h=game._card_stat(card,'health',owner)
    game._mutation_set_stats(card,owner,a*2,h*2);p.deck[i]=card
 elif name=='historical_copy_swap_deck_tops':
  if p.deck and q.deck:p.deck[-1],q.deck[-1]=q.deck[-1],p.deck[-1]
 elif name=='historical_copy_swap_spell_costs':
  options=[[c for c in player.hand if game._card_data(c)['type']=='SPELL'] for player in (p,q)]
  if all(options):
   a=game.rng.choice(options[0]);b=game.rng.choice(options[1]);ac=game._cost(a,owner);bc=game._cost(b,1-owner)
   game._set_card_cost(a,bc);game._set_card_cost(b,ac)
 elif name=='historical_copy_random_hand':
  if p.hand:game._clone_hand_card(owner,game.rng.choice(p.hand),source_owner=owner)
 elif name=='historical_copy_opening_hand':
  for card in getattr(p,'_starting_hand',()):
   if card.card_id!='TRL_318':game._clone_hand_card(owner,card,source_owner=owner)
 elif name=='historical_copy_opponent_decks':
  # Capture both donors before either copy enters a hand and triggers reactions.
  donors=[game.rng.choice(player.deck) if player.deck else None for player in game.players]
  for recipient in (owner,1-owner):
   donor=donors[1-recipient]
   if donor is not None:game._enter_hand(recipient,game._copy_card(donor,source_owner=1-recipient))
 elif name=='historical_copy_enemy_deck_hand':
  if q.deck:game._enter_hand(owner,game._copy_card(game.rng.choice(q.deck),source_owner=1-owner))
 elif name=='historical_copy_destroy_deck':
  removed=list(p.deck);p.deck.clear()
  for card in removed:
   game._zone_card_removed(owner,card,'deck','destroy')
   game._log('destroy_deck_card',player=owner,card=game._card_data(card)['id'])
 else:return False
 return True


def repeat_battlecry_program(game,record,ctx):
 source=ctx.get('source');owner=source.owner if source is not None else ctx['owner']
 operations=deepcopy(record['operations'])
 if not operations:return ('batch30_noop',),()
 cid=record['card_id'];targets=game._targets_for(cid,owner,record['mode'])
 if source is not None:targets=[uid for uid in targets if uid!=source.uid]
 if not targets:return ('batch30_noop',),()
 context=dict(ctx,owner=owner,source=source,target=game.rng.choice(targets),card_id=cid,physical_card=deepcopy(record['card']),bonus=0,lifesteal=source is not None and 'LIFESTEAL' in game._effective_keywords(source),combo=False,outcast=False,automatic_choices=True)
 return game._split_fixed_summon(('replay_context',operations,context),ctx)


def capture_battlecry_program(game,owner,card,mode,operations):
 if 'BATTLECRY' not in game._card_mechanics(card):return
 player=game.players[owner];records=getattr(player,'_historical_battlecry_records',[])
 if card.card_id=='DED_509':
  # Macaw records the repeated program, never a recursive instruction to
  # search for Macaw's own last Battlecry when another Macaw is played.
  program=deepcopy(records[-1]) if records else dict(card_id=card.card_id,card=deepcopy(card),mode='none',operations=())
 else:
  # Combo triggers are separate from a card's Battlecry.
  program=dict(card_id=card.card_id,card=deepcopy(card),mode=mode,operations=tuple(deepcopy(op) for op in operations if op[0] not in ('combo_operation','historical_if_combo')))
 program.update(played_uid=card.uid,played_card_id=card.card_id,turn=game.turn)
 records.append(program);player._historical_battlecry_records=records


def copycat_play_admitted(game,actor,card):
 recipient=1-actor;player=game.players[recipient]
 count=getattr(player,'historical_copycat_pending',0)
 if not count:return
 player.historical_copycat_pending=0
 # Physical snapshots are private continuations; no copied hand data is logged.
 operations=tuple(('historical_copy_copycat_receive',{'card':game._copy_card(card,source_owner=actor)}) for _ in range(count))
 game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=recipient,source=None,target=0,bonus=0,lifesteal=False,card_id='DED_514')),[]))


def record_targeted_spell(game,owner,card,target_uid,*,history=True,targeting=True):
 """Bind the cast target before a lethal spell can remove its recipient."""
 target=live(game,target_uid)
 friendly=target is not None and target.owner==owner
 hero_friendly=target_uid==game.hero_id(owner)
 if targeting:
  card._historical_cast_target=dict(uid=target_uid,owner=target.owner if target is not None else -target_uid-1 if target_uid<0 else None,minion=target is not None)
  neighbors=[]
  if target is not None:
   player=game.players[target.owner];index=player.board.index(target)
   neighbors=[player.board[i].uid for i in (index-1,index+1) if 0<=i<len(player.board) and player.board[i] in player.minions]
  count=sum(m.card_id=='TRL_085' and not m.silenced and m.health>0 for m in game.players[owner].minions)
  card._historical_zentimo_targets=tuple(neighbors)*count
  card._historical_target_combo=game.players[owner].cards_played>0
 if history and friendly:
  player=game.players[owner];values=getattr(player,'_historical_friendly_minion_target_spells',[]);values.append(deepcopy(card));player._historical_friendly_minion_target_spells=values
 if history and (friendly or hero_friendly):
  player=game.players[owner]
  history=getattr(player,'_historical_friendly_target_spells',[])
  history.append(deepcopy(card));player._historical_friendly_target_spells=history
  player.historical_friendly_target_spell_count=getattr(player,'historical_friendly_target_spell_count',0)+1
 if target is None:return
 if history and friendly and not target.silenced:
  if target.card_id in ('BOT_558','UNG_953'):
   destination='deck' if target.card_id=='BOT_558' else 'hand'
   target.attached_death_effects.append(('historical_copy_spell_delivery',dict(card=deepcopy(card)),destination))
  elif target.card_id=='BOT_258' and not target.rule_state.get('historical_zerek_bound'):
   target.rule_state['historical_zerek_bound']=True
   target.attached_death_effects.append(('summon','BOT_258',1))
 if targeting:game._queue_event('historical_spell_targeted',owner=owner,card_id=card.card_id,target=target.uid)


def pirate_zone_event(game,kind,data):
 if kind!='minion_played' or not has_tribe(game.cards[data['card_id']],'PIRATE'):return
 owner=data['owner'];player=game.players[owner]
 operations=[]
 for zone,cid in (('deck','CFM_637'),('hand','DRG_056')):
  for card in tuple(getattr(player,zone)):
   if game._card_data(card)['id']==cid:
    operations.append(('historical_copy_recruit_uid',zone,card.uid))
 if operations:
  game._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))


def offer_theotar(game,owner,hand_owner,first_uid,automatic):
 from .pools import deck_choice_options
 hand=game.players[hand_owner].hand
 options=deck_choice_options(hand,game.cards,3,game.rng)
 for option in options:option['uid']=hand[option.pop('index')].uid
 if options:
  game.pending_choice=dict(owner=owner,kind='historical_theotar',hand_owner=hand_owner,first_uid=first_uid,options=options,_automatic=automatic)
  game.phase='choice'


def offer_overplanner(game,owner,selected_uids,automatic=False):
 player=game.players[owner]
 candidates=[card for card in player.deck if card.uid not in selected_uids]
 if len(selected_uids)>=3 or not candidates:
  chosen=[]
  for uid in selected_uids:
   card=next((card for card in player.deck if card.uid==uid),None)
   if card is not None:player.deck.remove(card);chosen.append(card)
  player.deck.extend(reversed(chosen))
  game._refresh_auras()
  game._log('reorder_deck_top',player=owner,count=len(chosen),source='VAC_444')
  return
 offered=game.rng.sample(candidates,min(3,len(candidates)))
 game.pending_choice=dict(owner=owner,kind='historical_overplanner',options=[dict(card_id=card.card_id,uid=card.uid) for card in offered],_selected_uids=selected_uids,_automatic=automatic)
 game.phase='choice'


def rotate_silas(game,owner,direction):
 own=game.players[owner];other=game.players[1-owner]
 groups=[[m for m in player.minions if m.health>0] for player in (own,other)]
 outgoing=[(groups[0][0 if direction=='left' else -1] if groups[0] else None),(groups[1][-1 if direction=='left' else 0] if groups[1] else None)]
 # Preserve non-minion slots when both sides exchange an edge minion.
 incoming=(outgoing[1],outgoing[0]);boards=[list(own.board),list(other.board)]
 for index in (0,1):
  if incoming[index] is not None and outgoing[index] is None and len(boards[index])>=7:
   # A failed cross-zone transfer destroys the original entity. Keep it on
   # its source board for the ordinary death phase and its original owner.
   incoming[index].health=0
   outgoing[1-index]=None
   incoming=tuple(None if i==index else value for i,value in enumerate(incoming))
 for index,player in enumerate((own,other)):
  moving=outgoing[index];received=incoming[index]
  active=groups[index]
  survivors=[m for m in active if m is not moving]
  new=survivors+([received] if received is not None else []) if (direction=='left')==(index==0) else ([received] if received is not None else [])+survivors
  slots=[i for i,entity in enumerate(boards[index]) if entity in active]
  if len(new)==len(slots):
   for i,minion in zip(slots,new):boards[index][i]=minion
  else:
   boards[index]=[entity for entity in boards[index] if entity is not moving]
   if received is not None:
    if (direction=='left')==(index==0):boards[index].append(received)
    else:boards[index].insert(0,received)
 for player,board in zip((own,other),boards):player.board[:]=board
 for index,received in enumerate(incoming):
  if received is not None:
   received.owner=owner if index==0 else 1-owner
   received.summoned_turn=game.turn;received.attacks=0
 game._refresh_auras()
 game._log('rotate_minions',player=owner,direction=direction)


def resolve_held_spell_choice(game,choice,selected):
 from .historical_scythe import resolve_choice as scythe_choice
 if scythe_choice(game,choice,selected):return True
 from .historical_zephrys import resolve_choice as zephrys_choice
 if zephrys_choice(game,choice,selected):return True
 from .historical_dreamplanner import resolve_choice as tour_choice
 if tour_choice(game,choice,selected):return True
 from .historical_eudora import resolve_choice as eudora_choice
 if eudora_choice(game,choice,selected):return True
 from .historical_kazakusan import resolve_choice as resolve_kazakusan
 if resolve_kazakusan(game,choice,selected):return True
 if historical_holmes.resolve_choice(game,choice,selected):return True
 if historical_tavish.resolve_choice(game,choice,selected):return True
 if historical_ignis_crafting.resolve_choice(game,choice,selected):return True
 if historical_brukan.resolve_choice(game,choice,selected):return True
 if historical_etc.resolve_choice(game,choice,selected):return True
 if historical_guff_cariel.resolve_choice(game,choice,selected):return True
 if historical_combined_choices.resolve_choice(game,choice,selected):return True
 if historical_horror_crafting.resolve_choice(game,choice,selected):return True
 if historical_golem_crafting.resolve_choice(game,choice,selected):return True
 if historical_potion_crafting.resolve_choice(game,choice,selected):return True
 if choice['kind']=='historical_amulet_vendor':
  cid=selected['card_id'];game._add(choice['owner'],cid);game._add(1-choice['owner'],AMULET_PAIRS[cid])
  return True
 if choice['kind']=='historical_action_menu':
  cid=selected['card_id'];mode,operations=TOKEN_RULES[cid];context=dict(choice['_context'])
  if mode!='none':
   targets=[uid for uid in game._targets_for(cid,choice['owner'],mode) if uid]
   if targets:
    game.pending_choice=dict(owner=choice['owner'],kind='historical_action_target',options=[dict(card_id=live(game,uid).card_id,target_uid=uid) for uid in targets],_context=context,_action=cid,_automatic=choice.get('_automatic',False))
    game.phase='choice'
   return True
  game._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=context),[]))
  return True
 if choice['kind']=='historical_action_target':
  context=dict(choice['_context'],target=selected['target_uid'])
  game._rule_events.append(('captured_effects',dict(operations=tuple(TOKEN_RULES[choice['_action']][1]),context=context),[]))
  return True
 if choice['kind']=='historical_grunty':
  state=choice['_state'];attacker=state['summoned'][state['index']];state['index']+=1
  operations=(('force_pair',attacker,selected['target_uid']),('historical_copy_grunty_offer',state))
  game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(choice['_context'])),[]))
  return True
 if choice['kind']=='historical_future_location':
  game._discovery_result=game._add(choice['owner'],selected['card_id'])
  return True
 if choice['kind']=='historical_epoch':
  operations=(('cast_fixed_spell',selected['card_id'],'random'),('historical_copy_epoch_shuffle',selected['card_id']))
  game._rule_events.append(('captured_effects',dict(operations=operations,context=choice['_context']),[]))
  return True
 if historical_starships.resolve_choice(game,choice,selected):return True
 if choice['kind']=='historical_stitch':
  state=choice['_state']
  offer_stitch(game,choice['owner'],dict(state,selected=state['selected']+(selected['card_id'],)))
  return True
 if choice['kind']=='historical_griftah':
  owner=choice['owner'];state=choice['_state'];selected_ids=state['selected']+(selected['card_id'],)
  if len(selected_ids)<2:
   offer_griftah(game,owner,dict(state,selected=selected_ids))
  else:
   gifts=list(selected_ids);game.rng.shuffle(gifts)
   # Delay actual admission until both choices and the random assignment.
   game._add(owner,gifts[0]);game._add(1-owner,gifts[1])
  return True
 if choice['kind']=='historical_card_guess':
  owner=choice['owner'];success=selected['card_id']==choice['_correct']
  game._log('card_guess',player=owner,correct=choice['_correct'],success=success)
  if success:game._enter_hand(owner,game._copy_card(choice['_payload'],source_owner=1-owner))
  return True
 if choice['kind']=='historical_okani':
  source=live(game,choice['source_uid'])
  if source is not None and not source.silenced:
   values=source.rule_state.setdefault('historical_okani_counters',[])
   if selected['counter_kind'] not in values:values.append(selected['counter_kind'])
  return True
 if choice['kind']=='historical_gamer_first':
  source=live(game,choice['source_uid'])
  if source is not None and not source.silenced:source.rule_state.setdefault('historical_gamer_games',[]).append(selected['throw'])
  return True
 if choice['kind']=='historical_gamer_second':
  state=choice['_game'];winner=gamer_winner(state['owner'],state['first'],selected['throw'])
  game._log('rock_paper_scissors',player=state['owner'],first=state['first'],second=selected['throw'],winner=winner)
  if winner is not None:game._rule_events.append(('captured_effects',dict(operations=(('draw',2),),context=dict(owner=winner,source=None,target=0,bonus=0,lifesteal=False,card_id='MIS_916')),[]))
  return True
 if choice['kind']=='historical_jandice':
  minion=next((m for m in game.players[choice['owner']].all_minions if m.uid==selected['uid']),None)
  if minion is not None:minion._fragile_illusion=True
  return True
 if choice['kind']=='historical_silas':
  rotate_silas(game,choice['owner'],selected['direction'])
  return True
 if choice['kind']=='historical_overplanner':
  offer_overplanner(game,choice['owner'],choice['_selected_uids']+(selected['uid'],),choice.get('_automatic',False))
  return True
 if choice['kind']=='historical_ancient_relic':
  game._add(choice['owner'],selected['card_id'])
  return True
 if choice['kind']=='historical_manual_shot':
  uid=selected['target_uid'];mode=choice['mode'];context=dict(choice['context'],target=uid)
  used=choice['used']+(uid,) if mode=='huntress' else choice['used']
  operations=(('damage',2 if mode=='goliath' else 3),('historical_copy_manual_shots',mode,choice['remaining']-1,used))
  # Child effects checkpoint before the next target offer and before the parent resumes.
  game._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
  return True
 if choice['kind']=='historical_bibliomite':
  owner=choice['owner'];player=game.players[owner]
  card=next((card for card in player.hand if card.uid==selected['uid']),None)
  if card is not None:
   player.hand.remove(card);player.deck.append(card);game.rng.shuffle(player.deck)
   game._refresh_auras();game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
  return True
 if choice['kind']=='historical_theotar':
  owner=choice['owner'];hand_owner=choice['hand_owner']
  card=next((card for card in game.players[hand_owner].hand if card.uid==selected['uid']),None)
  if card is None:return True
  game._discovery_result=card
  if choice['first_uid'] is None:
   offer_theotar(game,owner,1-owner,card.uid,choice.get('_automatic',False))
  else:
   own=game.players[owner];other=game.players[1-owner]
   first=next((card for card in own.hand if card.uid==choice['first_uid']),None)
   if first is not None and card in other.hand:
    own.hand.remove(first);other.hand.remove(card)
    game._enter_hand(owner,card);game._enter_hand(1-owner,first);game._refresh_auras()
  return True
 if choice['kind']=='historical_algalon':
  deck=game.players[choice['deck_owner']].deck
  if selected['action']=='bottom' and deck and deck[-1].uid==choice['top_uid']:
   deck.insert(0,deck.pop());game._refresh_auras()
  return True
 if choice['kind']=='historical_hand_lock':
  card=next((c for c in game.players[choice['recipient']].hand if c.uid==selected['uid']),None)
  if card is not None:game._b60_state(card)['historical_unplayable_turn']=choice['turn']
  return True
 if choice['kind']!='historical_held_spell':return False
 game._add(choice['owner'],selected['card_id'])
 return True


def drawn_modifiers(game,owner,card):
 player=game.players[owner]
 discount=getattr(player,'historical_next_draw_discount',0)
 if discount:card.cost_delta=getattr(card,'cost_delta',0)-(discount);player.historical_next_draw_discount=0
 count=getattr(player,'historical_next_draw_spell_copies',0)
 if count and game._card_data(card)['type']=='SPELL':
  player.historical_next_draw_spell_copies=0
  for _ in range(count):game._enter_hand(owner,game._copy_card(card,source_owner=owner))


def curse_turn_entries(game,phase):
 if phase not in ('start','end'):return []
 result=[]
 for card in game.players[game.current].hand:
  if card.card_id!='TSC_955t':continue
  operation=('historical_copy_curse_tick' if phase=='start' else 'historical_copy_curse_expire',card.uid)
  result.append(dict(source=None,order=card.uid,operations=(operation,)))
 return result


def persistent_spell_event(game,kind,data):
 if kind=='spell_cast' and data['card_id'] in PROTOSS_SPELLS:
  player=game.players[data['owner']]
  player.historical_protoss_spells=getattr(player,'historical_protoss_spells',0)+1
 if kind!='spell_cast' or game.cards[data['card_id']].get('spellSchool')!='NATURE':return
 owner=data['owner'];count=getattr(game.players[owner],'historical_topior',0)
 if count:game._rule_events.append(('captured_effects',dict(operations=(('summon','REV_314t',count),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))


def attach_same_turn_follow(game,card,context,mode):
 effects=getattr(card,'_follow_effects',[])
 effects.append(dict(card_id=context['card_id'],historical_mode=mode,source_uid=getattr(context.get('source'),'uid',0),source_card_id=context['card_id'],end=game.turn))
 card._follow_effects=effects


def record_spell_cast(game,owner,card,target,*,automatic=False):
 victim=live(game,target) if target>0 else None
 target_owner=victim.owner if victim is not None else -target-1 if target<0 else None
 # Do not merge minion-cast spells into the player's 'you cast' history.
 field='_historical_automatic_cast_records' if automatic else '_historical_cast_records'
 records=getattr(game.players[owner],field,[])
 records.append(dict(card=deepcopy(card),turn=game.turn,owner_turn=game.players[owner].turns_taken,started=game._started_in_deck(card,owner),target_owner=target_owner,target_minion=victim is not None,automatic=automatic))
 setattr(game.players[owner],field,records)


def power_snapshot(game,owner):
 p=game.players[owner]
 if p.primary_power is not None:return deepcopy(p.primary_power)
 hero_class=p.hero_class;cid=BASIC_POWERS[hero_class]
 return dict(card_id=cid,basic_starting_class=hero_class,cost=1 if getattr(p,'historical_genn',False) else game.cards[cid]['cost'])


def ashen_draw(game,owner):
 player=game.players[owner];count=getattr(player,'historical_ashen_turns',[]).count(player.turns_taken) if game.current==owner else 0
 if count:game._rule_events.append(('captured_effects',dict(operations=(('damage_own_hero',2),)*count,context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='REV_960')),[]))


def resolve_pair_choice(game,choice,selected):
 if choice['kind']!='historical_stat_pair':return False
 first=live(game,choice['first_uid']);second=live(game,selected['target_uid'])
 if first is not None and second is not None and first.health>0 and second.health>0:
  attack,health=first.attack,first.health
  game._set_entity_stats(first,second.attack,second.health);game._set_entity_stats(second,attack,health);game._refresh_auras()
 return True


def check_star_collisions(game):
 if getattr(game,'phase',None)=='mulligan' or getattr(game,'terminal',False):return
 pending=getattr(game,'_historical_star_pending',None)
 if pending is None:pending=set();game._historical_star_pending=pending
 for owner,player in enumerate(game.players):
  for first,second in zip(player.hand,player.hand[1:]):
   if first.uid in pending or second.uid in pending:continue
   if {first.card_id,second.card_id}!=set(STAR_IDS):continue
   pair=(first.uid,second.uid);pending.update(pair)
   game._rule_events.append(('captured_effects',dict(operations=(('historical_copy_star_collide',pair),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
