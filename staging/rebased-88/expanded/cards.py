"""Explicit effect declarations. No natural-language fallback or automatic support.

The manifest pins every allowed card to the exact reviewed data record. New effects
remain unvalidated until the user runs the prepared fixtures.
"""
import gzip
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from engine.cards import SUPPORTED as LEGACY_SUPPORTED, TOKENS as LEGACY_TOKENS, UnsupportedCard

ROOT=Path(__file__).resolve().parents[1]
# Each rule is (target restriction, ordered operations). A spell with no target
# uses 'none'; minion battlecries may resolve without a target when none exists.
HELD_TARGETS = {
 'held_large_spell_character': ((('type','eq','SPELL'),('cost','ge',5)), 'character'),
}

RULES = {
 'TLC_365': ('minion', [('damage', 3)]),
 'TLC_483': ('none', []),
 'TIME_015': ('none',[('heal_own_hero',3),('hero_divine_shield',)]),
 'TLC_232': ('none',[('schedule_turn_effect','start',1,1,(('summon','TLC_237t',3),))]),
 'TLC_466': ('none',[('schedule_turn_effect','end',0,3,(('discard',1),('fill_board_summon','UNG_829t3')))]),
 'END_011': ('none',[('schedule_turn_effect','start',1,3,(('temporary_mana',1),))]),
 'JAIL_327': ('none',[('schedule_turn_effect','end',0,3,(('summon_from_zone','deck',(('cost','le',2),)),))]),
 'CATA_528': ('none',[('schedule_turn_effect','start',1,1,(('summon','CATA_528t',1),))]),
 'DINO_405': ('none',[('schedule_turn_effect','end',1,1,(('board_buff',2,2),))]),
 'TIME_700': ('none',[('schedule_turn_effect','end',0,3,(('summon','TIME_700t',1),))]),
 'CATA_216': ('none',[('permanent_healing_bonus',2)]),
 'DINO_402': ('friendly_minion',[('set_target_stats',1,1),('fill_board_target_copies',)]),
 'JAIL_462': ('none',[('draw_type_keyword',2,'MINION','CHARGE')]),
 'DINO_417': ('none',[('board_buff',1,0),('board_keyword','RUSH'),('board_expire',)]),
 'EDR_238': ('none',[('resurrect_distinct_min_cost',8)]),
 'TLC_624': ('none',[('copy_damaged_board','RUSH')]),
 'JAIL_516': ('none',[('summon_from_zone','deck',(('cost','le',2),),'RUSH'),('summon_from_zone','deck',(('cost','le',2),),'RUSH')]),
 'JAIL_387': ('none',[('zone_minion_buff',('hand',),1,1),('zone_minion_buff',('hand',),2,1,'LEGENDARY')]),
 'JAIL_307': ('none',[('area_damage','all_minions',2),('area_damage','all_minions',2)]),
 'TIME_705': ('none',[('set_bottom_cost',5,1)]),
 'TLC_835': ('none',[('set_hero_health',40)]),
 'TIME_048': ('none',[('buff_self_turns_taken',0,1)]),
 'EDR_522': ('none',[('opponent_draw_copy',2)]),
 'CORE_CATA_007': ('none',[('random_minion_damage_draw_kills',3,2)]),
 'END_014': ('enemy_character',[('damage_buff_if_dead',3,3,3)]),
 'EDR_847': ('none',[('next_power_set_cost',0)]),
 'CORE_CATA_001': ('none',[('next_cost_set','DEMON',0,'turn')]),
 'TIME_021': ('none',[('outcast_hero_immune',)]),
 'CORE_BAR_812': ('none',[('secret','CORE_BAR_812')]),
 'CORE_BT_072': ('enemy_character',[('freeze',),('summon','CS2_033',2)]),
 'CORE_SCH_181': ('none',[('summon_from_zone','hand',(('tribe','eq','DEMON'),)),('summon_from_zone','deck',(('tribe','eq','DEMON'),))]),
 'FIR_940': ('none',[('discount_distinct_cost_hand',2)]),
 'TLC_250': ('none',[('prevent_enemy_hero_healing_until_next_turn',)]),
 'TLC_888': ('none',[('copy_random_hand_any',((('tribe','eq','ELEMENTAL'),),(('tribe','eq','DRAGON'),)))]),
 'END_004': ('none',[('draw',2)]),
 'CATA_564': ('friendly_minion',[('keyword','MEGA_WINDFURY'),('keyword','CANT_ATTACK_HERO')]),
 'CATA_897': ('none',[('choose_hand_discard','remember')]),
 'FIR_906': ('none',[('board_buff',1,1),('discard_filtered',(('school','eq','NATURE'),)),('if_discarded',('board_buff',1,1))]),
 'FIR_910': ('character',[('damage',3),('discard_filtered',(('school','eq','FIRE'),)),('if_discarded',('damage',3))]),
 'CATA_490': ('none',[('choose_hand_discard',)]),
 'TIME_EVENT_301': ('none',[('repeat_held_tribe','DRAGON',('destroy_random_other',))]),
 'END_023': ('minion',[('freeze_neighbors_destroy_damaged',)]),
 'END_034': ('none',[('destroy_random_enemy',),('destroy_random_enemy_location',),('destroy_enemy_weapon',)]),
 'END_035': ('none',[('empty_deck_destroy_enemy_top',5)]),
 'CAP_804': ('friendly_minion',[('keyword_or_copy','REBORN')]),
 'TIME_703': ('none',[('low_health_buff_copy',10,5,5)]),
 'EDR_481': ('none',[('attack_threshold_copy',4)]),
 'EDR_524': ('none',[('shuffle_matching_enemy_hand',)]),
 'CATA_721': ('none',[('choose_hand_shuffle',),('draw',1)]),
 'EDR_521': ('none',[('copy_lowest_enemy_hand',)]),
 'CATA_697': ('none',[('choose_hand_copy',(('school','eq','FEL'),))]),
 'CATA_200': ('none',[('choose_hand_transform','TOKEN_COIN')]),
 'TLC_242': ('none',[('choose_self_effect',(('Taunt',('keyword_self','TAUNT')),('Poisonous',('keyword_self','POISONOUS')),('+1/+1',('buff_self',1,1))))]),
 'MEND_301': ('none',[('choose_fixed_summon',('NEW1_034','NEW1_033','NEW1_032'))]),
 'CORE_BAR_313': ('none',[('healed_this_turn_self_buff',3,3)]),
 'END_019': ('none',[('hero_damaged_self_buff',3,3)]),
 'DINO_137': ('none',[('discount_hand_neighbors',1)]),
 'END_021': ('none',[('hand_attack_types',('MINION','WEAPON'),2)]),
 'RLK_223': ('none',[('damage_random_enemy',2)]),
 'TIME_037': ('none',[('filtered_draw',(('type','eq','MINION'),),1),('hand_buff',0,2)]),
 'EDR_457': ('none',[('if_holding',(('tribe','eq','DRAGON'),),('equip','EDR_457t'))]),
 'EDR_472': ('held_large_spell_character',[('if_holding',(('type','eq','SPELL'),('cost','ge',5)),('damage',3))]),
 'TIME_750': ('character',[('damage',3),('if_holding',(('type','eq','MINION'),('cost','ge',5)),('filtered_draw',(('type','eq','MINION'),),1))]),
 'FIR_923': ('none',[('if_holding',(('cost','ge',8),),('damage_random_enemy_minion',8),('damage_random_enemy_minion',4))]),
 'CATA_111': ('none',[('if_holding',(('tribe','eq','DRAGON'),),('refresh_mana',2))]),
 'TIME_600': ('character',[('damage_hand_center',3,5)]),
 'CORE_OG_211': ('none',[('summon','NEW1_034',1),('summon','NEW1_033',1),('summon','NEW1_032',1)]),
 'TLC_227': ('none',[('damage_lowest_health_enemy',2)]*3),
 'EDR_255': ('none',[('damage_lowest_health_enemy',5)]*2),
 'CATA_135': ('none',[('summon_spend_mana_buff','CATA_135t',2)]),
 'CATA_465': ('none',[('summon_corpse_keyword','CATA_465t',5,8,'RUSH')]),
 'CATA_452': ('none',[('summon','CATA_452t',1)]),
 'TIME_006': ('none',[('summon','TIME_006t1',1),('held_tribe_summon','DRAGON','TIME_006t1',1)]),
 'TLC_622': ('none',[('summon','TLC_622t',2)]),
 'TLC_441': ('friendly_minion',[('buff_shared_type',1,2)]),
 'MEND_305': ('friendly_beast',[('buff',2,2),('buff_random_hand_tribe','BEAST',2,2)]),
 'DINO_435': ('none', [('kindred',[('copy_self_right',1)])]),
 'DINO_403': ('minion', [('set_target_stats',8,8),('keyword','CHARGE')]),
 'DINO_432': ('minion', [('set_target_stats',5,4),('keyword','STEALTH'),('draw',2)]),
 'EDR_252': ('minion', [('set_target_stats_by_owner',3,3,1,1)]),
 'CORE_SCH_713': ('none', [('opponent_next_turn_cost','SPELL',1)]),
 'CORE_DRG_403': ('none', [('opponent_next_power_cost',2)]),
 'TIME_716': ('none', [('opponent_next_turn_cost','ALL',1)]),
 'TLC_439': ('none', [('area_damage','enemy_minions',2), ('opponent_next_turn_cost','MINION',2)]),
 # Original subset cards now use the shared play lifecycle too.
 'CORE_CS2_189': ('character', [('damage',1)]),
 'CORE_UNG_084': ('character', [('damage',3)]),
 'CORE_EX1_011': ('character', [('heal',2)]),
 'CORE_ULD_191': ('friendly_minion', [('buff',0,2)]),
 'RLK_958': ('friendly_undead', [('buff',2,0)]),
 'CORE_ULD_271': ('none', [('damage_self',3)]),
 'CORE_GIL_622': ('none', [('damage_enemy_heal_own',3,3)]),
 'CORE_EX1_506': ('none', [('summon_right','TOKEN_SCOUT',1)]),
 'RLK_503': ('none', [('gain_corpses',1)]),
 'RLK_708': ('none', [('draw',1)]),
 'CORE_RLK_062': ('none', [('copy_self_right',2)]),
 'CORE_RLK_505': ('none', [('corpse_missiles',5,2)]),

 'CORE_EX1_145': ('none', [('next_discount', 'SPELL', 2, 'turn')]),
 'CORE_DMF_511': ('none', [('next_discount', 'COMBO', 2, 'turn')]),
 'CORE_BT_416': ('none', [('next_discount', 'DEMON', 2, 'persistent')]),
 'CORE_CS2_053': ('none', [('draw_discount', 3)]),
 'CORE_EX1_287': ('none', [('secret', 'CORE_EX1_287')]),
 'CORE_EX1_289': ('none', [('secret', 'CORE_EX1_289')]),
 'CORE_EX1_610': ('none', [('secret', 'CORE_EX1_610')]),
 'CORE_EX1_611': ('none', [('secret', 'CORE_EX1_611')]),
 'CORE_GIL_577': ('none', [('secret', 'CORE_GIL_577')]),
 'CORE_ULD_152': ('none', [('secret', 'CORE_ULD_152')]),

 'CORE_EX1_002': ('enemy_taunt', [('destroy',)]),
 'CORE_EX1_005': ('large_minion', [('destroy',)]),
 'CORE_SW_066': ('minion', [('silence',)]),
 'CORE_SW_072': ('none', [('destroy_enemy_weapon',)]),
 'CATA_203': ('legendary_minion', [('destroy',)]),
 'TLC_255': ('none', [('match_max_mana',)]),
 'CORE_EX1_246': ('minion', [('transform', 'hexfrog')]),
 'CATA_201': ('none', [('bounce_all_enemies',)]),
 'CORE_ULD_280': ('none', []),
 'CORE_EX1_059': ('minion', [('swap_stats',)]),
 'CORE_CS2_188': ('minion', [('temporary_attack_buff', 2)]),
 'CORE_EX1_198': ('minion', [('destroy_gain_health',)]),
 'CORE_ULD_165': ('minion', [('destroy_hurt_hero',)]),
 'CORE_EX1_193': ('none', [('copy_enemy_deck',)]),
 'CORE_CFM_790': ('none', [('pull_enemy_hand',)]),
 'CORE_LOOT_309': ('none', [('armor', 6), ('recruit', 4)]),
 'CORE_TRL_240': ('enemy_minion', [('damage_hero_attack',)]),
 'CORE_BOT_576': ('combo_friendly_minion', [('combo_buff', 4, 0)]),
 'CS3_022': ('weapon_character', [('damage', 2)]),
 'CORE_SW_429': ('none', [('summon', 'SW_429t', 2)]),
 'CORE_DS1_184': ('none', [('discover_deck',)]),
 'CORE_EX1_014': ('none', [('add_opponent', 'EX1_014t', 2)]),
 'EX1_014t': ('minion', [('buff', 1, 1)]),
 'CORE_GVG_061': ('none', [('summon', 'CS2_101t', 3), ('equip', 'CS2_091')]),
 'CORE_EX1_383': ('none', []),
 'CORE_OG_031': ('none', []),
 'CORE_DAL_720': ('none', []),
 'CORE_TRL_900': ('none', [('fill_hand', 'TRL_348t')]),
 'CORE_SCH_512': ('minion', [('damage_resummon', 4)]),
 'CORE_EX1_082': ('none', [('missiles', 'other_characters', 3)]),
 'CORE_BAR_311': ('none', [('missiles', 'enemy_minions', 4)]),
 'CORE_LOOT_373': ('none', [('random_heal', 12)]),
 'CORE_AT_123': ('none', []),
 'CORE_BT_201': ('none', []),
 'CORE_YOD_026': ('none', []),
 'CATA_720': ('none', [('remove_cheap_decks', 2)]),
 'CATA_724': ('none', []),
 'CATA_303': ('minion', [('damage_heal_enemy_if_dead', 5, 5)]),
 'CATA_308': ('none', [('area_damage', 'all_minions', 4)]),
 'CATA_491': ('none', [('descending_aoe', 3)]),
 'CATA_581': ('none', [('board_count_aoe',)]),
 'TLC_601': ('none', [('armor_aoe', 5)]),
 'TLC_606': ('enemy_minion', [('damage_armor_if_dead', 2, 5)]),
 'TLC_633': ('tribal_enemy_minion', [('damage', 6)]),
 'TLC_621': ('none', []),
 'CORE_AT_037': ('none', []),
 'CORE_EX1_154': ('none', []),
 'CORE_EX1_160': ('none', []),
 'CORE_OG_047': ('none', []),
 'CORE_ONY_018': ('none', []),
 'CORE_TSC_650': ('none', []),
 'EDR_233': ('none', []),
 'EDR_257': ('none', []),
 'END_010': ('none', []),
 'EDR_570': ('none', []),

 'RLK_060': ('none', [('raise_corpses', 'RLK_008t', 5)]),
 'CORE_RLK_506': ('none', [('raise_corpses', 'RLK_061t', 6)]),
 'CORE_RLK_118': ('none', [('tomb_guardians','RLK_118t3')]),
 'CORE_RLK_063': ('character', [('damage', 5), ('freeze_enemies',), ('summon', 'RLK_063t', 1)]),
 'CORE_TSC_076': ('none', [('summon', 'TSC_076t3', 1), ('summon', 'TSC_076t2', 1), ('summon', 'TSC_076t', 1)]),
 'CORE_DMF_067': ('none', [('draw_both',)]),
 'CORE_KAR_061': ('none', [('draw_tribe', 'BEAST'), ('draw_tribe', 'DRAGON'), ('draw_tribe', 'MURLOC')]),

 'CAP_801': ('minion', [('buff',2,3),('keyword','REBORN'),('keyword','TAUNT')]),
 'CATA_138': ('friendly_minion', [('buff_board_count',)]),
 'CATA_302': ('minion', [('heal_full',),('draw',1)]),
 'CATA_304': ('none', [('damage_self',4)]),
 'CATA_485': ('character', [('damage',2),('damage_random_enemy_minion',1)]),
 'CATA_582': ('none', [('area_damage','all_minions',1),('hero_attack',3)]),
 'CATA_612': ('none', [('freeze_self',)]),
 'EDR_531': ('friendly_minion', [('destroy',),('armor',8)]),
 'END_007': ('character', [('damage',1),('hero_attack',1),('draw',1),('armor',1)]),
 'END_028': ('none', [('destroy_small',4)]),
 'TIME_051': ('none', [('double_self_attack',)]),
 'TIME_061': ('none', [('reverse_deck',)]),
 'TIME_216': ('minion', [('damage_draw_if_alive',5,2)]),
 'TIME_218': ('minion', [('damage',1),('hero_attack',1)]),
 'TIME_601': ('none', [('draw_until',3)]),
 'TIME_720': ('none', [('double_self_health',)]),
 'TLC_620': ('enemy_minion', [('armor',3),('damage_armor',)]),
 'CORE_AT_055': ('character', [('heal',5)]),
 'CORE_AT_064': ('character', [('damage',3),('armor',3)]),
 'CORE_BAR_801': ('character', [('damage',1),('summon','ENGINE_HYENA',1)]),
 'CORE_BOT_222': ('minion', [('damage',4),('damage_own_hero',4)]),
 'CORE_BOT_451': ('none', [('summon','ENGINE_SPARK',2)]),
 'CORE_BRM_013': ('character', [('damage',3),('draw_empty',1)]),
 'CORE_BT_035': ('none', [('hero_attack',2),('draw',1)]),
 'CORE_BT_292': ('minion', [('buff',2,1),('draw',1)]),
 'CORE_BT_480': ('none', [('outcast_draw',1)]),
 'CORE_BT_491': ('none', [('draw',1),('outcast_draw',1)]),
 'CORE_BT_801': ('minion', [('damage',3)]),
 'CORE_CFM_604': ('friendly_character', [('heal',12),('draw',1)]),
 'CORE_CFM_753': ('none', [('hand_buff',1,1)]),
 'CORE_CS1_112': ('none', [('area_damage','enemy_minions',2),('area_heal',2)]),
 'CORE_CS1_130': ('minion', [('damage',3)]),
 'CORE_CS2_004': ('minion', [('buff',0,2),('draw',1)]),
 'CORE_CS2_009': ('minion', [('buff',2,3),('keyword','TAUNT')]),
 'CORE_CS2_023': ('none', [('draw',2)]),
 'CORE_CS2_024': ('character', [('damage',3),('freeze',)]),
 'CORE_CS2_028': ('none', [('area_damage','enemy_minions',2),('freeze_enemies',)]),
 'CORE_CS2_029': ('character', [('damage',6)]),
 'CORE_CS2_032': ('none', [('area_damage','enemy_minions',5)]),
 'CORE_CS2_042': ('character', [('damage',4)]),
 'CORE_CS2_062': ('none', [('area_damage','all_characters',3)]),
 'CORE_CS2_072': ('undamaged_minion', [('damage',2)]),
 'CORE_CS2_074': ('weapon_required', [('weapon_buff',2)]),
 'CORE_CS2_076': ('enemy_minion', [('destroy',)]),
 'CORE_CS2_093': ('none', [('area_damage','enemies',2)]),
 'CORE_CS2_094': ('character', [('damage',3),('draw',1)]),
 'CORE_CS2_108': ('damaged_enemy_minion', [('destroy',)]),
 'CORE_DS1_185': ('character', [('damage',2)]),
 'CORE_EX1_043': ('none', [('self_hand_health',)]),
 'CORE_EX1_058': ('none', [('adjacent_taunt',)]),
 'CORE_EX1_103': ('none', [('other_murloc_health',2)]),
 'CORE_EX1_129': ('none', [('area_damage','enemy_minions',1),('draw',1)]),
 'CORE_EX1_131': ('none', [('combo_summon','EX1_131t',1)]),
 'CORE_EX1_134': ('combo_character', [('combo_damage',3)]),
 'CORE_EX1_169': ('none', [('temporary_mana',1)]),
 'CORE_EX1_197': ('none', [('destroy_large',5)]),
 'CORE_EX1_238': ('character', [('damage',3)]),
 'CORE_EX1_259': ('none', [('area_damage','enemy_minions',3)]),
 'CORE_EX1_278': ('character', [('damage',1),('draw',1)]),
 'CORE_EX1_302': ('minion', [('damage_draw_if_dead',1)]),
 'CORE_EX1_309': ('minion', [('destroy',),('heal_own_hero',3)]),
 'CORE_EX1_310': ('none', [('discard',2)]),
 'CORE_EX1_319': ('none', [('damage_own_hero',3)]),
 'CORE_EX1_362': ('friendly_minion', [('keyword','DIVINE_SHIELD')]),
 'CORE_EX1_391': ('minion', [('damage_draw_if_alive',2)]),
 'CORE_EX1_606': ('none', [('armor',5),('draw',1)]),
 'CORE_EX1_619': ('none', [('health_one',)]),
 'CORE_GIL_623': ('none', [('self_enemy_hand_health',)]),
 'CORE_GVG_059': ('none', [('random_shield_taunt',)]),
 'CORE_ICC_055': ('minion', [('damage',3)]),
 'CORE_ICC_407': ('none', [('remove_enemy_top',)]),
 'CORE_LOOT_013': ('none', [('damage_own_hero',2)]),
 'CORE_NEW1_018': ('none', [('self_weapon_attack',)]),
 'CORE_OG_149': ('none', [('area_damage','other_minions',1)]),
 'CORE_RLK_657': ('none', [('armor',6)]),
 'CORE_RLK_814': ('none', [('shadow_hand_buff',1,1)]),
 'CORE_SW_088': ('character', [('damage',3),('summon','CS2_065',2)]),
 'CORE_SW_108': ('minion', [('damage',2),('add','SW_108t',1)]),
 'CORE_SW_442': ('character', [('damage',4)]),
 'CORE_TRL_111': ('none', [('beast_weapon_durability',1)]),
 'CORE_TRL_307': ('character', [('heal',4),('draw',1)]),
 'CORE_UNG_205': ('enemy_character', [('freeze',)]),
 'CORE_UNG_809': ('none', [('add','UNG_809t1',1)]),
 'CORE_UNG_848': ('none', [('area_damage','other_minions',2)]),
 'CORE_WW_329': ('none', [('taunt_hand_buff',2,2)]),
 'SW_108t': ('minion', [('damage',2)]),
 # Explicitly replace legacy spell resolution so spell damage/lifesteal are correct.
 'TOKEN_COIN': ('none', [('temporary_mana',1)]),
 'RLK_024': ('minion', [('damage',6)]),
 'CORE_EDR_002': ('friendly_undead', [('keyword','POISONOUS')]),
 'RLK_048': ('none', [('board_buff',1,1),('board_keyword','ELUSIVE')]),
 'RLK_707': ('none', [('grave_strength',)]),
 'CORE_RLK_712': ('none', [('blood_tap',)]),
 'CORE_RLK_087': ('none', [('asphyxiate',)]),
 'RLK_709': ('none', [('area_damage','enemies',2),('draw',1)]),
 'DINO_419': ('friendly_beast', [('buff', 2, 2), ('keyword', 'RUSH')]),
 'EDR_476': ('none', [('area_damage', 'enemies', 4), ('area_heal', 4)]),
 'EDR_492': ('none', [('summon', 'EDR_492t', 3)]),
 'EX1_277': ('none', [('missiles', 'enemies', 3)]),
 'JAIL_312': ('none', [('add', 'EX1_277', 3)]),
 'JAIL_441': ('minion', [('damage', 3), ('refresh_power',)]),
 'JAIL_513': ('none', [('self_hand_health',)]),
 'TIME_059': ('none', [('summon', 'TIME_059', 2)]),
 'TIME_605': ('none', [('copy_self_right', 1)]),
 'TIME_710': ('none', [('combo_copy_self', 1)]),
 'TLC_427': ('none', [('add', 'WW_001t', 1)]),
 'TLC_823': ('minion', [('damage', 3), ('next_discount', 'BEAST', 2, 'turn')]),
 'WW_001t': ('character', [('damage', 3)]),
 'CATA_526': ('none', [('aoe_draw_dead', 1)]),
 'CATA_EVENT_002': ('fire_turn_minion', [('fire_turn_destroy',)]),
 'CATA_EVENT_402': ('minion', [('destroy',), ('add_opponent', 'TOKEN_COIN', 1), ('combo_add', 'TOKEN_COIN')]),
 'CORE_EX1_312': ('none', [('destroy_battlefield',)]),
 'CORE_NEW1_031': ('none', [('summon_fixed_random', ('NEW1_032', 'NEW1_033', 'NEW1_034'))]),
 'CORE_REV_023': ('enemy_location', [('destroy_location',)]),
 'DINO_138': ('none', [('kindred', [('enemy_edges_damage', 6)])]),
 'DINO_404': ('none', [('kindred', [('others_keyword', 'RUSH')])]),
 'DINO_406': ('character', [('damage', 4), ('tribe_board_buff', 'ELEMENTAL', 1, 1)]),
 'DINO_408': ('none', [('shuffle_left_hand',)]),
 'DINO_411': ('none', [('filtered_draw', (('type', 'eq', 'MINION'), ('attack', 'eq', 0)), 1)]),
 'DINO_413': ('none', [('kindred_random_damage_freeze', 2, 2)]),
 'EDR_230': ('none', [('top_deck_minion_buff', 3, 4, 4)]),
 'EDR_459': ('none', [('own_others_damage', 3)]),
 'EDR_468': ('minion', [('damage_buff_attack', 1, 4)]),
 'FIR_909': ('none', [('random_distinct_damage', 2, 3)]),
 'FIR_954': ('minion', [('damage_owner_draw', 5)]),
 'FIR_960': ('none', [('copy_lowest_hand_tribe', 'BEAST')]),
 'FIR_961': ('none', [('held_keywords', (('type', 'eq', 'SPELL'), ('cost', 'ge', 5)), ('DIVINE_SHIELD', 'LIFESTEAL'))]),
 'JAIL_118': ('none', [('destroy_not_class', 'PALADIN')]),
 'JAIL_377': ('none', [('draw_if_cheap', 2)]),
 'JAIL_456': ('none', [('deck_size_draw', 25)]),
 'JAIL_514': ('none', [('draw', 3)]),
 'JAIL_866': ('none', [('draw_minions_mana_buff', 2, 10, 3, 3)]),
 'JAIL_941': ('character', [('heal', 4), ('add', 'JAIL_941t', 1)]),
 'JAIL_941t': ('character', [('damage', 4)]),
 'TIME_023': ('none', [('draw_bottom', 2)]),
 'TIME_031': ('none', [('draw_distinct_costs', 3)]),
 'TIME_062': ('none', [('held_keywords', (('tribe', 'eq', 'DRAGON'),), ('TAUNT', 'DIVINE_SHIELD'))]),
 'TIME_427': ('enemy_minion', [('source_health_damage',)]),
 'TIME_431': ('character', [('source_health_heal',)]),
 'TIME_611': ('character', [('damage', 3), ('freeze_random_enemies', 2)]),
 'TIME_855': ('enemy_character', [('damage_other_random', 3, 2, 2)]),
 'TIME_858': ('enemy_minion', [('excess_draw', 5)]),
 'TIME_871': ('none', [('buff_self_damaged_count', 2, 2)]),
 'TIME_873': ('none', [('armor', 10), ('summon_opponent', 'TIME_873t', 2)]),
 'TLC_221': ('character', [('damage_summon_count', 3, 'TLC_249')]),
 'TLC_226': ('none', [('kindred', [('copy_self_right', 1)])]),
 'TLC_231': ('none', [('barnabus_draw',)]),
 'TLC_233': ('none', [('small_others_buff', 2, 1, 1, 'TAUNT')]),
 'TLC_236': ('none', [('kindred_cost_draws',)]),
 'TLC_429': ('none', [('kindred', [('summon', 'TLC_429t', 2)])]),
 'TLC_432': ('none', [('kindred_deathrattle_draw',)]),
 'TLC_440': ('character', [('damage', 4), ('draw', 1), ('kindred', [('draw', 1)])]),
 'TLC_447': ('enemy_minion', [('destroy',), ('kindred', [('area_damage', 'all_minions', 2)])]),
 'TLC_454': ('none', [('kindred_destroy_attack',)]),
 'TLC_463': ('none', [('kindred_discard',)]),
 'TLC_482': ('none', [('summon', 'TLC_249', 2), ('kindred', [('trigger_cinders',)])]),
 'TLC_519': ('none', [('summon', 'TLC_519t', 1), ('kindred', [('summon', 'TLC_519t', 1)])]),
 'TLC_600': ('character', [('damage', 5), ('armor', 5)]),
 'TLC_630t': ('character', [('damage', 2), ('summon', 'TLC_903t', 1)]),
 'TLC_816': ('none', [('draw', 2)]),
 'TLC_825': ('kindred_enemy_minion', [('kindred', [('source_attack_damage',)])]),
 'TLC_828': ('none', [('all_zone_tribe_buff', 'BEAST', 2, 2)]),
 'TLC_829': ('minion', [('kindred_destroy_gain',)]),
 'TLC_901': ('minion', [('tribal_damage', 3)]),
 'TLC_902': ('none', [('add', 'TLC_630t', 2)]),
 'TLC_903': ('none', [('kindred', [('hero_attack', 5)])]),
 'CATA_483': ('none', [('spell_damage_turn_copy',)]),
 'CATA_557': ('repeated_enemy_character', [('repeat_copy_damage', 3, 'CATA_557')]),
 'CATA_560': ('none', [('summon_played_one_cost',)]),
 'CATA_568': ('none', [('draw', 2)]),
 'CORE_CATA_002': ('none', [('resurrect_highest', None)]),
 'CORE_RLK_706': ('none', [('permanent_end_damage', 3)]),
 'CORE_TRL_345': ('none', [('return_last_turn_spells',)]),
 'EDR_430': ('none', [('death_threshold_missiles', 20, 20)]),
 'TIME_616': ('none', [('resurrect_highest', 'UNDEAD')]),
 'TIME_715': ('none', [('draw', 2)]),
 'TLC_818': ('none', [('resurrect_costs_reborn', (1, 2, 3))]),
}
# Only listed keyword/stat cards have been reviewed for this engine.
PASSIVE = {
 'EDR_942',
 'CORE_EX1_509', 'TLC_220', 'EDR_815',
 'JAIL_459',
 'TLC_520',
 'JAIL_802',
 'DINO_131',
 'DINO_421',
 'DINO_132','EDR_110',
 'TLC_224',
 'TIME_606',
 'CORE_EX1_100',
 'EDR_540',
 'END_026',
 'CORE_SW_047',
 'JAIL_029',
 'FIR_955',
 'EDR_889',
 'EDR_495',
 'EDR_861',
 'FIR_904',
 'CORE_BT_781',
 'CORE_BAR_878','CORE_RLK_083',
 'CS3_024',
 'CS3_025',
 'EDR_890',
 'TLC_244','TLC_822',
 'JAIL_503',
 'END_030','TIME_047',
 'END_033','TLC_819','EDR_477',
 'CATA_613','CATA_898',
 'END_016',
 'CATA_494',
 'CATA_493',
 'CORE_RLK_745',
 'CORE_BT_510','TLC_840','EDR_471',
 'CAP_003',
 'TIME_060','CATA_208',
 'END_022','JAIL_202',
 'TIME_054','JAIL_883',
 'END_008','EDR_470','CORE_DRG_256',
 'TIME_856',
 'EDR_853', 'JAIL_440',
 'CORE_CS2_179', 'CORE_EX1_096', 'CORE_EX1_110', 'CORE_GIL_558', 'CORE_GVG_085', 'CORE_LOOT_137', 'CORE_LOOT_413', 'CORE_NEW1_023', 'CORE_SW_068', 'CORE_ULD_723', 'CS3_038', 'Core_CS2_200', 'RLK_067', 'RLK_511',
 'CATA_133','CATA_305','CATA_467','CATA_475','CORE_BT_187','CORE_BT_351','CORE_CS2_122','CORE_CS2_222','CORE_EX1_007','CORE_EX1_162','CORE_EX1_414','CORE_EX1_507','CORE_EX1_559','CORE_EX1_604','CORE_GIL_534','CORE_GVG_103','CORE_LOOT_044','CORE_NEW1_020','CORE_NEW1_021','CORE_NEW1_022','CORE_NEW1_027','CORE_NX2_028','CORE_OG_044','CORE_OG_218','CORE_UNG_928','CORE_WC_042','CORE_WON_351','EDR_253','EDR_254','JAIL_872','TLC_101','TLC_256','TLC_478','TLC_480','TLC_605',
 'CORE_AV_337','CORE_BAR_310','CORE_ICC_210','CORE_LOOT_368','CORE_ULD_133','CORE_YOP_034','RLK_061',
 'CATA_558','EDR_272','EDR_486','EDR_598','END_031','TIME_045','TIME_053','TIME_056','TLC_248','TIME_603',
 'CORE_AT_052', 'CORE_EX1_250', 'CORE_BT_701', 'CORE_BT_921',
 'CORE_DRG_079', 'CORE_EX1_010', 'CORE_EX1_028', 'CORE_ICC_038', 'CS3_007',
 'CORE_EX1_012', 'CORE_ICC_214', 'CORE_WC_701',
 'CATA_476',
 'CATA_999',
 'CORE_BT_493',
 'CORE_DRG_107',
 'DINO_130',
 'EDR_816',
 'EDR_971',
 'FIR_778',
 'FIR_929',
 'JAIL_007',
 'JAIL_720',
 'TIME_100',
 'TIME_428',
 'TLC_225',
 'TLC_237',
 'TLC_249',
 'TLC_443',
 'TLC_468',
 'TLC_EVENT_402',
 'CATA_473',
 'CATA_478',
 'EDR_485',
 'EDR_571',
 'EDR_572',
 'END_002',
 'JAIL_204',
 'JAIL_311',
 'JAIL_376',
 'JAIL_450',
 'JAIL_942',
 'TIME_617',
 'TLC_366',
 'TLC_401',
 'TLC_623',
 'TLC_630',
 'TLC_833',
 'CATA_529',
 'CATA_616',
 'EDR_891',
 'EDR_892',
}
DEATH_EFFECTS = {
 'DINO_131': [('summon_from_zone','deck',(('tribe','eq','BEAST'),),'LIFESTEAL')],
 'DINO_421': [('zone_minion_buff',('hand','deck'),3,3)],
 'EDR_110': [('damage_random_enemy_minion',1)],
 'EDR_495': [('buff_random_hand_minion','both',-2,0)],
 'EDR_847': [('next_power_set_cost',0)],
 'EDR_861': [('empty_crystals','both',1)],
 'CS3_024': [('draw_extreme_cost',(('type','eq','MINION'),),'highest')],
 'EDR_890': [('discount_hand_position',-1,2)],
 'TLC_244': [('discount_random_hand','enemy',(('type','eq','MINION'),),2)],
 'JAIL_503': [('draw',1)],
 'CATA_897': [('return_remembered_discards',1)],
 'RLK_223': [('damage_random_enemy',2)],
 'JAIL_877t': [('draw',1)],
 'CORE_ULD_280': [('bounce_random_enemy',)],
 'CORE_EX1_383': [('equip', 'EX1_383t')],
 'CORE_OG_031': [('death_summon', 'OG_031a', 1)],
 'CORE_DAL_720': [('bounce_random_friendly', -2)],
 'CORE_YOD_026': [('death_attack_gift',)],
 'CORE_BT_201': [('attack_missiles',)],
 'CORE_AT_123': [('dragon_held_aoe', 3)],
 'CATA_724': [('unlock_mana',)],
 'TLC_621': [('remove_own_top', 3)],

 'CORE_AV_337': [('death_summon', 'AV_337t', 2)],
 'CORE_LOOT_368': [('death_summon', 'CS2_065', 3)],
 'CORE_BAR_310': [('area_heal', 8)],
 'CORE_DMF_067': [('draw_both',)],

 'TIME_603': [('destroy_random_enemy',)],
 'CORE_EX1_012': [('draw',1)],
 'CORE_RLK_657': [('armor',6)],
 'CORE_ICC_214': [('destroy_random_enemy',)],
 'CORE_WC_701': [('area_damage','enemy_minions',1)],
 'CORE_DRG_107': [('add', 'EX1_277', 1)],
 'DINO_130': [('death_summon', 'DINO_130t', 1), ('board_buff', 1, 1)],
 'FIR_778': [('area_damage', 'enemy_minions', 9)],
 'FIR_929': [('draw_school', 'FIRE')],
 'JAIL_007': [('area_damage', 'enemies', 2)],
 'JAIL_720': [('add', 'TOKEN_COIN', 1)],
 'TLC_225': [('death_summon', 'TLC_249', 1)],
 'TLC_237': [('death_summon', 'TLC_237t', 4)],
 'TLC_249': [('missiles', 'enemies', 2)],
 'TLC_443': [('death_summon', 'TLC_443t', 1)],
 'TLC_468': [('death_summon_group', ('TLC_468t1', 'TLC_468t2'))],
 'TLC_EVENT_402': [('destroy_all_minions',)],
 'DINO_408': [('draw', 2)],
 'EDR_459': [('area_damage', 'enemy_minions', 3)],
 'EDR_485': [('filtered_draw', (('type', 'eq', 'MINION'), ('cost', 'ge', 7)), 1)],
 'EDR_571': [('filtered_draw', (('type', 'eq', 'SPELL'), ('cost', 'ge', 5)), 1)],
 'EDR_572': [('filtered_draw', (('tribe', 'eq', 'DRAGON'),), 2, -1)],
 'END_002': [('weapon_buff_or_equip', 2, 'CS2_082')],
 'JAIL_376': [('buff_damaged_board', 1, 2)],
 'TLC_226': [('filtered_draw', (('type', 'eq', 'SPELL'),), 1)],
 'TLC_401': [('random_distinct_damage', 6, 3)],
 'EDR_891': [('resurrect_deathrattle_copies', 0, 4, False)],
 'EDR_892': [('resurrect_deathrattle_copies', 5, 100, True)],
}
END_EFFECTS = {
 'EDR_942': [('hero_divine_shield',)],
 'DINO_132': [('damage_random_enemy_minion',5)],
 'EDR_889': [('buff_random_other',1,1,'DRAGON')],
 'TLC_822': [('discount_random_hand','friendly',(('type','eq','MINION'),('tribe','eq','BEAST')),1)],'CORE_RLK_745': [('corpse_copy',4)],'RLK_061': [('raise_corpses', 'RLK_061t', 1)], 'CORE_ICC_210': [('buff_random_other', 1, 1)], 'CORE_ULD_133': [('draw_unspent_mana',)], 'CORE_YOP_034': [('damage_random_enemy_minion', 10)], 'CATA_133': [('buff_others', 1, 1)], 'CATA_305': [('full_health_buff', 0, 3)], 'CATA_475': [('area_damage', 'enemies', 2)], 'TLC_480': [('set_enemies_stats', 1, 1)],
 'CATA_476': [('summon', 'CATA_476t', 1)],
 'CATA_999': [('damage_enemy_hero', 4)],
 'CORE_BT_493': [('missiles', 'enemies', 6)],
 'EDR_816': [('buff_others', 1, 0)],
 'EDR_971': [('heal_both_heroes', 3)],
 'TIME_100': [('hand_buff', 1, 1)],
 'TIME_428': [('buff_others', 0, 1)],
 'CATA_473': [('shield_or_buff', 3, 3)],
 'CATA_478': [('summon_source_stats', 'CATA_478t')],
 'TLC_623': [('buff_other_damaged', 2, 2)],
}
# Explicit token rules; never inferred by parsing card text.
NO_CORPSE = {'RLK_008t','RLK_061t'}
TOKEN_IDS = {'BAR_878t','CS2_033','EDR_457t','CATA_135t','CATA_465t','CATA_452t','TIME_006t1','TLC_622t','JAIL_877t','GIL_577t','AT_037t','CS2_091','EDR_233t2','EX1_014t','EX1_160t','EX1_383t','EX1_tk11','OG_031a','SW_429t','TRL_348t','TSC_650t','TSC_650t4','hexfrog','AV_337t','RLK_008t','RLK_061t','RLK_063t','RLK_118t3','TSC_076t','TSC_076t2','TSC_076t3','CS2_050','CS2_051','CS2_058','NEW1_009','CS2_101t','CS2_082','EX1_131t','CS2_065','SW_108t','UNG_809t1',
 'CATA_476t',
 'DINO_130t',
 'EDR_492t',
 'EX1_277',
 'TLC_237t',
 'TLC_443t',
 'TLC_468t1',
 'TLC_468t2',
 'WW_001t',
 'CATA_478t',
 'HERO_11bpt',
 'JAIL_941t',
 'NEW1_032',
 'NEW1_033',
 'NEW1_034',
 'TIME_873t',
 'TLC_429t',
 'TLC_519t',
 'TLC_630t',
 'TLC_903t',
}
LOCAL_TOKENS = {
 'ENGINE_HYENA':dict(id='ENGINE_HYENA',name='Hyena',type='MINION',cost=1,attack=1,health=1,races=['BEAST'],mechanics=['RUSH'],collectible=False),
 'ENGINE_SPARK':dict(id='ENGINE_SPARK',name='Spark',type='MINION',cost=1,attack=1,health=1,races=['ELEMENTAL'],mechanics=['RUSH'],collectible=False),
}
PLAYABLE_TOKENS = {'BAR_878t','CS2_033','EDR_457t',
 'AV_337t','CS2_065','CS2_101t','EX1_131t','RLK_008t','RLK_061t',
 'RLK_063t','RLK_118t3','TSC_076t','TSC_076t2','TSC_076t3',
 'TOKEN_GHOUL','TOKEN_SCOUT','TOKEN_BAINE','ENGINE_HYENA','ENGINE_SPARK','CS2_050','CS2_051','CS2_058','NEW1_009','CATA_135t','CATA_465t','CATA_452t','TIME_006t1','TLC_622t','JAIL_877t','GIL_577t','EX1_014t', 'EX1_383t', 'EDR_233t2', 'TSC_650t', 'SW_429t', 'CS2_091', 'EX1_tk11', 'OG_031a', 'hexfrog', 'UNG_809t1', 'TRL_348t', 'TSC_650t4', 'EX1_160t', 'AT_037t',
 'CATA_476t',
 'DINO_130t',
 'EDR_492t',
 'EX1_277',
 'TLC_237t',
 'TLC_443t',
 'TLC_468t1',
 'TLC_468t2',
 'WW_001t',
 'CATA_478t',
 'HERO_11bpt',
 'JAIL_941t',
 'NEW1_032',
 'NEW1_033',
 'NEW1_034',
 'TIME_873t',
 'TLC_429t',
 'TLC_519t',
 'TLC_630t',
 'TLC_903t',
}
COIN_IDS = {'REV_COIN2', 'TIME_EVENT_COIN', 'RLK_COIN1', 'TIME_COIN3', 'BT_COIN', 'JAIL_COIN1', 'TOY_COIN2', 'TSC_COIN2', 'GAME_005', 'MUDAN_COIN1', 'EDR_COIN2', 'GVG_COIN', 'ULD_COIN', 'ETC_COIN1', 'JAIL_COIN2', 'CATA_COIN4', 'BAR_COIN3', 'DAL_COIN', 'DMF_COIN2', 'BAR_COIN1', 'TOY_COIN1', 'DMF_COIN1', 'TLC_COIN1', 'CATA_COIN3', 'TLC_COIN2', 'LOE_COIN', 'AV_COIN2', 'BAR_COIN2', 'TOY_COIN3', 'GDB_COIN2', 'DINO_COIN2', 'JAIL_COIN5', 'SW_COIN1', 'TIME_COIN1', 'GDB_COIN1', 'TIME_COIN4', 'SW_COIN2', 'ETC_COIN2', 'TTN_COIN2', 'CATA_COIN1', 'DFT_ALEX_COIN1', 'RLK_COIN2', 'WW_COIN1', 'DINO_COIN1', 'JAIL_EVENT_COIN', 'MONK_COIN', 'CATA_COIN2', 'CATA_COIN5', 'EDR_COIN1', 'JAIL_COIN3', 'TSC_COIN1', 'TIME_COIN2', 'REV_COIN1', 'TOKEN_COIN', 'TTN_COIN1', 'FP1_COIN', 'AV_COIN1', 'VAC_COIN2', 'WW_COIN2', 'VAC_COIN1', 'DRG_COIN', 'CATA_COIN6', 'AT_COIN'}
TOKEN_IDS.update({'CATA_528t','TIME_700t','UNG_829t3'})
PLAYABLE_TOKENS.update({'CATA_528t','TIME_700t','UNG_829t3'})
TOKEN_IDS.update(COIN_IDS-{'TOKEN_COIN'})
PLAYABLE_TOKENS.update(COIN_IDS-{'TOKEN_COIN'})
RULES.update({cid: ('none',[('temporary_mana',1)]) for cid in COIN_IDS})

from .locations import LOCATION_RULES

from . import batch30_cards
RULES.update(batch30_cards.RULES)
RULES.update(batch30_cards.TOKEN_RULES)
DEATH_EFFECTS.update(batch30_cards.DEATH_EFFECTS)
END_EFFECTS['EDR_940']=[('armor_board_identity','Wisp',1)]
START_EFFECTS_BATCH30={'NEW1_021':('owner',[('destroy_all_minions',)])}
TOKEN_IDS.update(batch30_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(batch30_cards.TOKEN_IDS)

from . import composed_cards
RULES.update(composed_cards.RULES)
TOKEN_IDS.update(composed_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(composed_cards.TOKEN_IDS)

from . import persistent_cards
RULES.update(persistent_cards.RULES)
RULES.update(persistent_cards.TOKEN_RULES)
TOKEN_IDS.update(persistent_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(persistent_cards.TOKEN_IDS)
DEATH_EFFECTS.update(persistent_cards.DEATH_EFFECTS)

RULES['TLC_102'] = ('none', [('draw_kindred_pair',)])
RULES.update({'CORE_SCH_717':('none',[]), 'CORE_TTN_843':('none',[])})
TOKEN_IDS.add('TTN_843t1')
PLAYABLE_TOKENS.add('TTN_843t1')

from . import local_family_cards
RULES.update(local_family_cards.RULES)
RULES.update(local_family_cards.TOKEN_RULES)
TOKEN_IDS.update(local_family_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(local_family_cards.TOKEN_IDS)
DEATH_EFFECTS.update(local_family_cards.DEATH_EFFECTS)
END_EFFECTS.update(local_family_cards.END_EFFECTS)

from . import batch60_cards
RULES.update(batch60_cards.RULES)
RULES.update(batch60_cards.TOKEN_RULES)
TOKEN_IDS.update(batch60_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(batch60_cards.TOKEN_IDS)
DEATH_EFFECTS.update(batch60_cards.DEATH_EFFECTS)
END_EFFECTS.update(batch60_cards.END_EFFECTS)

from . import bonus_cards
RULES.update(bonus_cards.RULES)
TOKEN_IDS.update(bonus_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(bonus_cards.TOKEN_IDS)
DEATH_EFFECTS.update(bonus_cards.DEATH_EFFECTS)

from . import leech_cards
RULES.update(leech_cards.RULES)
TOKEN_IDS.update(leech_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(leech_cards.TOKEN_IDS)
END_EFFECTS.update(leech_cards.END_EFFECTS)

from . import dormant_cards
RULES.update(dormant_cards.RULES)
TOKEN_IDS.update(dormant_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(dormant_cards.TOKEN_IDS)
DEATH_EFFECTS.update(dormant_cards.DEATH_EFFECTS)

from . import provenance_cards
RULES.update(provenance_cards.RULES)
DEATH_EFFECTS.update(provenance_cards.DEATH_EFFECTS)
END_EFFECTS.update(provenance_cards.END_EFFECTS)

from . import held_upgrade_cards
RULES.update(held_upgrade_cards.RULES)
TOKEN_IDS.update(held_upgrade_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(held_upgrade_cards.TOKEN_IDS)

from . import temporary_cards
RULES.update(temporary_cards.RULES)
TOKEN_IDS.update(temporary_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(temporary_cards.TOKEN_IDS)

from . import prepare_cards
RULES.update(prepare_cards.RULES)
DEATH_EFFECTS.update(prepare_cards.DEATH_EFFECTS)
RULES.update({
    'JAIL_940': ('none', [('replay_dead_minions',1)]),
    'TLC_106': ('none', [('replay_dead_minions',5)]),
    'CATA_472': ('none', []),
})
DEATH_EFFECTS['CATA_472']=[('replay_random_end',)]

from . import on_draw_cards
RULES.update(on_draw_cards.RULES)
RULES.update(on_draw_cards.TOKEN_RULES)
DEATH_EFFECTS.update(on_draw_cards.DEATH_EFFECTS)
TOKEN_IDS.update(on_draw_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(on_draw_cards.TOKEN_IDS)

from . import forced_combat_cards
RULES.update(forced_combat_cards.RULES)
DEATH_EFFECTS.update(forced_combat_cards.DEATH_EFFECTS)
END_EFFECTS.update(forced_combat_cards.END_EFFECTS)
TOKEN_IDS.update(forced_combat_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(forced_combat_cards.TOKEN_IDS)

from . import alternate_play
RULES.update(alternate_play.RULES)
DEATH_EFFECTS.update(alternate_play.DEATH_EFFECTS)

from . import tribal_groups
RULES.update(tribal_groups.RULES)
END_EFFECTS.update(tribal_groups.END_EFFECTS)

from . import hero_powers
RULES.update(hero_powers.RULES)
TOKEN_IDS.update(hero_powers.TOKEN_IDS)
PLAYABLE_TOKENS.update(hero_powers.PLAYABLE_TOKENS)

from . import permanents
RULES.update(permanents.TOKEN_RULES)
TOKEN_IDS.update(permanents.TOKEN_IDS)
PLAYABLE_TOKENS.update(permanents.PLAYABLE_TOKENS)

from . import dreams
RULES.update(dreams.RULES)
RULES.update(dreams.TOKEN_RULES)
TOKEN_IDS.update(dreams.TOKEN_IDS)
PLAYABLE_TOKENS.update(dreams.TOKEN_IDS)

from . import quests
RULES.update(quests.RULES)
TOKEN_IDS.update(quests.TOKEN_IDS)
PLAYABLE_TOKENS.update(quests.TOKEN_IDS)
DEATH_EFFECTS.update(quests.DEATH_EFFECTS)

from . import modifier_cards
RULES.update(modifier_cards.RULES)
TOKEN_IDS.update(modifier_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(modifier_cards.TOKEN_IDS)

from . import spell_casting_cards
RULES.update(spell_casting_cards.RULES)
TOKEN_IDS.update(spell_casting_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(spell_casting_cards.TOKEN_IDS)
DEATH_EFFECTS.update(spell_casting_cards.DEATH_EFFECTS)

RULES.update({cid:('none',[('secret',cid)]) for cid in ('JAIL_315','CORE_LOOT_101','TIME_620')})
TOKEN_IDS.add('CS2_tk1')
PLAYABLE_TOKENS.add('CS2_tk1')

# Closed generation families: every outcome is already live.
from . import generation_extensions
RULES.update({cid:generation_extensions.RULES[cid] for cid in ('CATA_621','DINO_427')})

from . import shatter
RULES.update(shatter.RULES)
TOKEN_IDS.update(shatter.TOKEN_IDS)
PLAYABLE_TOKENS.update(shatter.TOKEN_IDS)

from . import rewind
RULES.update(rewind.RULES)
TOKEN_IDS.update(rewind.TOKEN_IDS)
PLAYABLE_TOKENS.update(rewind.TOKEN_IDS)

from . import dark_gifts
RULES.update(dark_gifts.RULES)
TOKEN_IDS.update(dark_gifts.TOKEN_IDS)
PLAYABLE_TOKENS.update(dark_gifts.TOKEN_IDS)

from . import entity_effects
RULES.update(entity_effects.RULES)
TOKEN_IDS.update(entity_effects.TOKEN_IDS)
PLAYABLE_TOKENS.update(entity_effects.TOKEN_IDS)
DEATH_EFFECTS.update(entity_effects.DEATH_EFFECTS)
from . import lasting_rules
RULES.update(lasting_rules.RULES)
DEATH_EFFECTS.update(lasting_rules.DEATH_EFFECTS)
from . import stored_cards
RULES.update(stored_cards.RULES)
TOKEN_IDS.update(stored_cards.TOKEN_IDS)
PLAYABLE_TOKENS.update(stored_cards.TOKEN_IDS)
DEATH_EFFECTS.update(stored_cards.DEATH_EFFECTS)

from . import starting_rules
RULES.update(starting_rules.RULES)

from . import leylines
RULES.update({cid:leylines.RULES[cid] for cid in ('MEND_500','MEND_503','MEND_504','MEND_506')})

# Deathrot Maw shares the complete, implemented Underfel token family.
RULES['TLC_479']=('none',[])
DEATH_EFFECTS['TLC_479']=[('summon_fixed_random',permanents.FEL_BEASTS)]

from . import future_summons, automatic_casting
RULES['MEND_304']=future_summons.RULES['MEND_304']
RULES['TLC_430']=automatic_casting.RULES['TLC_430']
END_EFFECTS['TLC_430']=automatic_casting.END_EFFECTS['TLC_430']

# Closed runtime admissions use the ordinary registry, without injected pools.
# They remain provisional pending independent interaction evidence.
from . import replacements, evolving_locations
RULES['CORE_DAL_575']=replacements.RULES['CORE_DAL_575']
CLOSED_TIMELINE_ROOTS=('TIME_044','TIME_810')
CLOSED_TIMELINE_TOKEN_IDS={cid for root in CLOSED_TIMELINE_ROOTS
                         for cid in evolving_locations.TIMELINES[root][1:]}
for root in CLOSED_TIMELINE_ROOTS:
    RULES[root]=evolving_locations.RULES[root]
    for cid in evolving_locations.TIMELINES[root]:
        LOCATION_RULES[cid]=evolving_locations.LOCATION_RULES[cid]
TOKEN_IDS.update(CLOSED_TIMELINE_TOKEN_IDS)
PLAYABLE_TOKENS.update(CLOSED_TIMELINE_TOKEN_IDS)

from . import deck_setup
RULES.update(deck_setup.RULES)
from . import zone_triggers
for _cid in ('JAIL_421','TIME_618'):
    RULES[_cid]=zone_triggers.RULES[_cid]
from . import stat_rules,turn_deadlines
RULES['JAIL_330']=stat_rules.RULES['JAIL_330']
RULES['JAIL_509']=starting_rules.STAGED_RULES['JAIL_509']
RULES['JAIL_860']=turn_deadlines.RULES['JAIL_860']
from . import fabled_effects
BLOOD_FIGHTER_TOKEN_IDS=set(fabled_effects.BLOOD_FIGHTERS[1:])
RULES['TIME_850']=fabled_effects.RULES['TIME_850']
for _cid in BLOOD_FIGHTER_TOKEN_IDS:
    RULES[_cid]=fabled_effects.TOKEN_RULES[_cid]
for _cid in fabled_effects.BLOOD_FIGHTERS:
    DEATH_EFFECTS[_cid]=fabled_effects.DEATH_EFFECTS[_cid]
TOKEN_IDS.update(BLOOD_FIGHTER_TOKEN_IDS)
PLAYABLE_TOKENS.update(BLOOD_FIGHTER_TOKEN_IDS)
from . import kindred
RULES['TLC_251']=kindred.RULES['TLC_251']
from . import stored_obligations
RULES['JAIL_719']=stored_obligations.RULES['JAIL_719']
from . import historical_death
RULES.update(historical_death.RULES)
DEATH_EFFECTS.update(historical_death.DEATH_EFFECTS)
TOKEN_IDS.update(historical_death.GENERATED_IDS)
PLAYABLE_TOKENS.update(historical_death.GENERATED_IDS)

from . import historical_numeric
RULES.update(historical_numeric.RULES)
TOKEN_IDS.update(historical_numeric.GENERATED_IDS)
PLAYABLE_TOKENS.update(historical_numeric.GENERATED_IDS)
from . import historical_vanilla
RULES.update(historical_vanilla.RULES)
TOKEN_IDS.update(historical_vanilla.GENERATED_IDS)
PLAYABLE_TOKENS.update(historical_vanilla.GENERATED_IDS)
from . import historical_simple
RULES.update(historical_simple.RULES)
TOKEN_IDS.update(historical_simple.GENERATED_IDS)
PLAYABLE_TOKENS.update(historical_simple.GENERATED_IDS)

COLLECTIBLE_IDS = (LEGACY_SUPPORTED | PASSIVE | set(RULES) | set(LOCATION_RULES)) - historical_death.GENERATED_IDS - historical_numeric.GENERATED_IDS - BLOOD_FIGHTER_TOKEN_IDS - historical_simple.GENERATED_IDS - historical_vanilla.GENERATED_IDS - CLOSED_TIMELINE_TOKEN_IDS - entity_effects.TOKEN_IDS - stored_cards.TOKEN_IDS - shatter.TOKEN_IDS - spell_casting_cards.TOKEN_IDS - modifier_cards.TOKEN_IDS - hero_powers.TOKEN_IDS - permanents.TOKEN_IDS - dreams.TOKEN_IDS - quests.TOKEN_IDS - on_draw_cards.TOKEN_IDS - batch30_cards.TOKEN_IDS - composed_cards.TOKEN_IDS - persistent_cards.TOKEN_IDS - batch60_cards.TOKEN_IDS - local_family_cards.TOKEN_IDS - COIN_IDS - {'TOKEN_COIN','SW_108t','EX1_014t','EX1_277','WW_001t','TLC_630t','JAIL_941t'}


@lru_cache(maxsize=2)
def _token_records(compressed_snapshot, token_ids):
    # The key is actual file bytes plus requested IDs, never path/mtime.
    # Each registry call still reads the current snapshot and verifies hashes.
    wanted=set(token_ids)
    return {card['id']:card for card in json.loads(gzip.decompress(compressed_snapshot))
            if card['id'] in wanted}


def registry():
    catalog=json.loads((ROOT/'data/standard/cards.json').read_text())
    manifest=json.loads((Path(__file__).parent/'reviewed_cards.json').read_text())
    selected={c['id']:c for c in catalog if c['id'] in COLLECTIBLE_IDS}
    tokens=_token_records((ROOT/'data/standard/all_cards.json.gz').read_bytes(),tuple(sorted(TOKEN_IDS)))
    reviewed={**selected,**tokens}
    if set(selected)!=COLLECTIBLE_IDS or set(tokens)!=TOKEN_IDS or set(reviewed)!=set(manifest):
        raise UnsupportedCard('Explicit expanded card registry and manifest disagree.')
    for cid,c in reviewed.items():
        if hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()!=manifest[cid]:
            raise UnsupportedCard('Card changed; review its implementation: '+cid)
    return deepcopy({**reviewed,**LEGACY_TOKENS,**LOCAL_TOKENS})

CHOICES = {'CORE_AT_037': [('Living Roots: damage', 'character', [('damage', 2)]), ('Living Roots: Saplings', 'none', [('summon', 'AT_037t', 2)])], 'CORE_EX1_154': [('Wrath: damage', 'minion', [('damage', 3)]), ('Wrath: draw', 'minion', [('damage', 1), ('draw', 1)])], 'CORE_EX1_160': [('Power: buff', 'none', [('board_buff', 1, 1)]), ('Power: Panther', 'none', [('summon', 'EX1_160t', 1)])], 'CORE_OG_047': [('Feral Rage: Attack', 'none', [('hero_attack', 4)]), ('Feral Rage: Armor', 'none', [('armor', 8)])], 'CORE_ONY_018': [('Boomkin: heal', 'none', [('heal_own_hero', 8)]), ('Boomkin: damage', 'character', [('damage', 4)])], 'CORE_TSC_650': [('Flipper Friends: Orca', 'none', [('summon', 'TSC_650t', 1)]), ('Flipper Friends: Otters', 'none', [('summon', 'TSC_650t4', 6)])], 'EDR_233': [('Spirits: Wolves', 'none', [('summon', 'EX1_tk11', 3)]), ('Spirits: Falcons', 'none', [('summon', 'EDR_233t2', 2)])], 'EDR_257': [('Lightmender: Attack and Shield', 'none', [('buff_self', 3, 0), ('keyword_self', 'DIVINE_SHIELD')]), ('Lightmender: Health and Lifesteal', 'none', [('buff_self', 0, 3), ('keyword_self', 'LIFESTEAL')])], 'EDR_570': [('Nightmares: damage', 'none', [('area_damage', 'all_minions', 1)]), ('Nightmares: buff', 'damaged_minion', [('buff', 2, 2)])], 'END_010': [('Timereaver: Attack', 'none', [('set_others_attack', 1)]), ('Timereaver: Health', 'none', [('set_others_health', 1)])]}

AURAS = {'CORE_CS2_122': ('others', 1, 0), 'CORE_CS2_222': ('others', 1, 1), 'CORE_EX1_162': ('adjacent', 1, 0), 'CORE_EX1_507': ('MURLOC', 2, 0), 'CORE_NEW1_027': ('PIRATE', 1, 1),
 'NEW1_033': ('others', 1, 0),
}

CONDITIONAL_ATTACK = {'CORE_EX1_414': ('damaged', 6), 'CORE_OG_218': ('damaged', 3), 'TLC_101': ('damaged', 3), 'CORE_UNG_928': ('enemy_turn', 2), 'TLC_605': ('enemy_turn', 6), 'CORE_WON_351': ('weapon', 2),
 'JAIL_311': ('large_deck', 5),
}

TRIGGERS = {
 'CORE_EX1_509': (('summon','friendly','MURLOC'),[('buff_self',1,0)]),
 'TLC_220': (('summon','friendly','ELEMENTAL'),[('damage_random_enemy',3)]),
 'EDR_815': (('summon','enemy',None),[('spend_corpses_damage_summoned',2,3)]),
 'JAIL_802': (('minion_mechanic_played','BATTLECRY'),[('buff_event_source',1,1)]),
 'TLC_224': (('spell_school_played','FIRE'),[('buff_spell_cost',1,1)]),
 'CORE_EX1_100': ('any_spell_played',[('copy_cast_spell_to_other_player',)]),
 'EDR_540': ('other_repeated_minion_played',[('draw',1)]),
 'END_026': ('spell_cast_on_minion',[('draw',1)]),
 'CORE_SW_047': ('friendly_shield_lost',[('buff_random_hand_minion','friendly',5,5)]),
 'JAIL_029': ('friendly_minion_survived_damage',[('buff_event_target',1,0)]),
 'FIR_955': ('friendly_hero_damaged_own_turn',[('damage_random_enemy_minion',3)]),
 'FIR_904': (('spell_school_cast','FEL'),[('destroy_self',),('area_damage','enemies',2)]),
 'CORE_BAR_878': (('spell_school_cast','HOLY'),[('summon','BAR_878t',1)]),
 'CORE_RLK_083': ('spell_cast',[('random_distinct_damage',1,2)]),
 'CS3_025': ('attacking_self',[('hand_buff',1,1)]),
 'CATA_494': ('friendly_minion_discard',[('summon_discarded_copy',)]),
 'CORE_BT_510': ('defended_self',[('area_damage','enemies',1)]),
 'TLC_840': ('attacked_self',[('damage_enemy_hero',2)]),
 'EDR_471': ('damaged_self',[('armor',1),('buff_self',1,0)]),
 'CAP_003': ('attacked_self',[('draw',1)]),
 'TLC_622t': ('damaged_self',[('buff_self',1,0)]),
 'END_008': ('hero_power_used',[('refresh_mana',2)]),
 'EDR_470': ('hero_power_used',[('buff_self',0,2)]),
 'CORE_DRG_256': ('hero_power_used',[('damage_random_enemy',5)]),
 'EDR_853': ('spell_cast',[('summon_fixed_random',('NEW1_032','NEW1_033','NEW1_034'))]),
 'JAIL_440': ('damaged_self',[('summon','HERO_11bpt',2)]),'CORE_EX1_007': ('damaged_self', [('draw', 1)]), 'CORE_EX1_604': ('damaged_minion', [('buff_self', 1, 0)]), 'CORE_BT_351': ('hero_attack', [('buff_self', 1, 0)]), 'CORE_GIL_534': ('hero_attack', [('buff_self', 1, 1)]), 'CORE_NX2_028': ('hero_attack', [('armor', 4), ('draw', 1)]), 'JAIL_872': ('hero_attack', [('draw', 1)]), 'CORE_NEW1_020': ('spell_cast', [('area_damage', 'all_minions', 1)]), 'CORE_EX1_559': ('spell_played', [('add', 'CORE_CS2_029', 1)]), 'TLC_256': ('spell_cast', [('keyword_self', 'DIVINE_SHIELD')]), 'EDR_254': ('spell_cast', [('buff_spell_cost',)]), 'CORE_WC_042': ('elemental_played', [('buff_self', 1, 0)]),
 'TLC_630': ('damaged_self', [('add', 'TLC_630t', 1)]),
}

WEAPON_TRIGGERS = {'TLC_239t': [('board_buff',2,2)], 'END_016': [('discard_highest_cost',)], 'EDR_253': [('draw', 1)], 'TLC_478': [('area_damage', 'all_minions', 1)], 'CATA_467': [('buff_random_friendly', 2, 0)],
 'JAIL_450': [('frail_ghoul','HERO_11bpt')],
 'TLC_833': [('summon', 'TLC_903t', 1)],
}

START_EFFECTS = {'CORE_GVG_103': ('every', [('buff_self', 1, 0)]), 'CORE_NEW1_021': ('owner', [('destroy_all_minions',)])}

# Frozen API SPELLPOWER tag is 1; printed text and official card library say +2.
# Keep the raw snapshot unchanged. Values here are explicit reviewed behavior.
# https://hearthstone.blizzard.com/en-gb/cards/119632/
SPELL_DAMAGE_VALUES = {'TIME_856': 2}

# Explicit end-of-either-player-turn listeners, separate from owner-only effects.
END_EVERY_EFFECTS = {
 'TIME_054': [('_turn_add','TOKEN_COIN',1)],
 'JAIL_883': [('keyword_self','REBORN')],
}

CONDITIONAL_SPELL_DAMAGE = {'END_022': ('damaged', 2)}
HERO_ATTACK_AURAS = {'JAIL_202': ('owner_turn', 1)}

# Printed self damage modifiers: multiplier, then flat extra damage.
INCOMING_DAMAGE_MODIFIERS = {'TIME_060': (2,0), 'CATA_208': (1,1)}

DAMAGE_FREEZERS = {'CS2_033'}

HERO_DAMAGE_WEAPON_REPLACEMENTS = {'CORE_BT_781': 'lose_durability'}

HERO_IMMUNE_AURAS = {'CORE_CATA_001'}

# (maximum hand size, set Hero Power cost); live friendly unsilenced auras.
HERO_POWER_HAND_COST_AURAS = {
    'TIME_606': (3,0),
}

FRIENDLY_KEYWORD_AURAS = {'JAIL_459':'POISONOUS'}

CHOICES.update(batch30_cards.CHOICES)
START_EFFECTS.update(START_EFFECTS_BATCH30)

TRIGGERS.update(composed_cards.TRIGGERS)
CHOICES.update(composed_cards.CHOICES)

WEAPON_TRIGGERS.update(composed_cards.WEAPON_TRIGGERS)

TRIGGERS.update(persistent_cards.TRIGGERS)

TRIGGERS.update(batch60_cards.TRIGGERS)
CHOICES.update(batch60_cards.CHOICES)
START_EFFECTS.update(batch60_cards.START_EFFECTS)
WEAPON_TRIGGERS.update(batch60_cards.WEAPON_TRIGGERS)

TRIGGERS.update(local_family_cards.TRIGGERS)
WEAPON_TRIGGERS.update(local_family_cards.WEAPON_TRIGGERS)

TRIGGERS.update({
    'CORE_SCH_717':('enemy_card_drawn',[('copy_drawn_set_cost',1)]),
    'CORE_TTN_843':('friendly_card_drawn',[('summon','TTN_843t1',1)]),
})

TRIGGERS.update(bonus_cards.TRIGGERS)

CHOICES.update(dormant_cards.CHOICES)
TRIGGERS.update(dormant_cards.TRIGGERS)
WEAPON_TRIGGERS.update(dormant_cards.WEAPON_TRIGGERS)

TRIGGERS.update(prepare_cards.TRIGGERS)

TRIGGERS.update(forced_combat_cards.TRIGGERS)

TRIGGERS.update(spell_casting_cards.TRIGGERS)

TRIGGERS.update(shatter.TRIGGERS)

START_EFFECTS.update(stored_cards.START_EFFECTS)

CHOICES.update(lasting_rules.CHOICES)

START_EFFECTS.update(entity_effects.START_EFFECTS)

# Existing Companion consumers route through persistent owner upgrades. New
# replacement sources and Void Soul cards remain staged; Talya is live above.
RULES.update(future_summons.CONSUMER_RULES)
TRIGGERS.update(future_summons.CONSUMER_TRIGGERS)
