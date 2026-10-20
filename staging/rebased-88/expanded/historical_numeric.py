"""Explicit historical primitive effects reviewed from frozen printed text.

Generated-only identities; no historical pool membership is approved here.
"""
RULES={'CS2_007': ('character', [('heal', 8)]),
 'CS2_077': ('none', [('draw', 4)]),
 'EX1_194': ('minion', [('buff', 2, 6)]),
 'EX1_279': ('character', [('damage', 10)]),
 'OG_094': ('minion', [('buff', 2, 6)]),
 'OG_223': ('minion', [('buff', 1, 2)]),
 'TRL_128': ('character', [('heal', 3)]),
 'UNG_923': ('none', [('armor', 5)]),
 'AT_103': ('character', [('damage', 4)]),
 'BOT_308': ('character', [('damage', 2)]),
 'CS2_147': ('none', [('draw', 1)]),
 'CS2_150': ('character', [('damage', 2)]),
 'DRG_054': ('none', [('draw', 1)]),
 'EX1_015': ('none', [('draw', 1)]),
 'GVG_053': ('none', [('armor', 5)]),
 'OG_234': ('character', [('heal', 5)]),
 'TSC_963': ('character', [('damage', 1)]),
 'ULD_190': ('character', [('damage', 5)]),
 'WON_315': ('character', [('heal', 5)])}
# Additional frozen primitives; schools/keywords remain per-record metadata.
RULES.update({'AT_001': ('minion', [('damage', 25)]),
 'BAR_745': ('none', [('damage_own_hero', 3)]),
 'BT_235': ('none', [('area_damage', 'all_minions', 4)]),
 'CFM_021': ('enemy_character', [('freeze',)]),
 'CFM_065': ('none', [('area_damage', 'all_minions', 2)]),
 'CS2_025': ('none', [('area_damage', 'enemy_minions', 1)]),
 'CS2_057': ('minion', [('damage', 4)]),
 'CS2_117': ('character', [('heal', 3)]),
 'DRG_226': ('character', [('heal', 8)]),
 'EX1_019': ('friendly_minion', [('buff', 1, 1)]),
 'EX1_195': ('friendly_minion', [('buff', 0, 2)]),
 'EX1_313': ('none', [('damage_own_hero', 5)]),
 'ICC_058': ('enemy_character', [('freeze',)]),
 'ICC_094': ('friendly_minion', [('buff', 1, 1)]),
 'ICC_802': ('none', [('area_damage', 'all_minions', 1)]),
 'LOOT_291': ('character', [('heal', 4)]),
 'OG_083': ('none', [('area_damage', 'enemy_minions', 1)]),
 'SCH_535': ('none', [('area_damage', 'all_minions', 3)]),
 'TRL_526': ('none', [('area_damage', 'other_minions', 1)]),
 'TRL_546': ('none', [('damage_own_hero', 5)]),
 'ULD_714': ('minion', [('damage', 3)]),
 'UNG_817': ('minion', [('damage', 5)]),
 'WON_341': ('minion', [('damage', 25)])})
# Explicit keyword, board/hand and hero primitives. No pool is inferred.
RULES.update({'AT_074': ('minion', [('buff', 3, 0), ('keyword', 'DIVINE_SHIELD')]),
 'BAR_534': ('none', [('board_buff', 1, 3)]),
 'BT_257': ('minion', [('buff', 2, 3), ('keyword', 'LIFESTEAL')]),
 'BT_512': ('none', [('hero_attack', 8)]),
 'CFM_094': ('none', [('area_damage', 'all_characters', 5)]),
 'CFM_305': ('none', [('hand_buff', 1, 1)]),
 'CFM_614': ('none', [('board_buff', 1, 1)]),
 'CS2_039': ('minion', [('keyword', 'WINDFURY')]),
 'CS2_075': ('none', [('damage_enemy_hero', 3)]),
 'CS2_087': ('minion', [('buff', 3, 0)]),
 'CS2_089': ('none', [('heal_own_hero', 8)]),
 'CS2_105': ('none', [('hero_attack', 4)]),
 'DRG_206': ('none', [('area_damage', 'all_characters', 1)]),
 'DS1_233': ('none', [('damage_enemy_hero', 5)]),
 'EX1_184': ('none', [('board_keyword', 'DIVINE_SHIELD')]),
 'EX1_192': ('none', [('heal_own_hero', 5)]),
 'ICC_056': ('minion', [('buff', 3, 3), ('freeze',)]),
 'TRL_243': ('none', [('hero_attack', 2)]),
 'ULD_143': ('minion', [('buff', 4, 4), ('keyword', 'DIVINE_SHIELD'), ('keyword', 'TAUNT')]),
 'ULD_265': ('minion', [('keyword', 'REBORN')]),
 'WORK_005': ('weapon_required', [('weapon_buff', 2, 2)])})
# Frozen textless historical weapons; shared equipment mechanics only.
RULES.update({cid:('none',[]) for cid in ('CS2_080','CS2_106','CS2_112')})
RULES.update({'EX1_583':('none',[('heal_own_hero',4)]),'GVG_069':('none',[('heal_own_hero',8)])})
# Literal fixed summon recipes; these are not random outcome pools.
FIXED_SUMMONS={'BAR_327': (('BAR_327t', 2),),
 'BAR_533': (('BAR_533t', 2),),
 'BT_036': (('BT_036t', 3),),
 'BT_173': (('BT_036t', 6),),
 'CS2_027': (('CS2_mirror', 2),),
 'DAL_733': (('DAL_733t', 2),),
 'KAR_025': (('KAR_025a', 1), ('KAR_025b', 1), ('KAR_025c', 1)),
 'TSC_076': (('TSC_076t3', 1), ('TSC_076t2', 1), ('TSC_076t', 1)),
 'WW_806': (('WW_806t', 2),)}
FIXED_BATTLECRIES={'BAR_060': ('BAR_060t', 1),
 'CFM_315': ('CFM_315t', 1),
 'CFM_648': ('CFM_648t', 1),
 'EX1_025': ('EX1_025t', 1),
 'ICC_026': ('ICC_026t', 2),
 'KAR_030a': ('KAR_030', 1),
 'KAR_710': ('KAR_710m', 1),
 'LOOT_069': ('LOOT_069t', 1),
 'OG_156': ('OG_156a', 1),
 'REV_936': ('REV_936t', 1),
 'SW_076': ('SW_076t', 2),
 'TRL_151': ('TRL_151t', 1)}
FIXED_SUMMONS.update({'GIL_191': (('GIL_191t', 4),),
 'RLK_544': (('RLK_544t', 2),),
 'TID_005': (('TID_005t', 2),),
 'TRL_351': (('TRL_351t', 3),),
 'YOD_041': (('YOD_041t', 3),)})
FIXED_SUMMONS.update({'BOT_420': (('EX1_tk9', 2),),
 'EX1_571': (('EX1_tk9', 3),),
 'CFM_310': (('CFM_310t', 4),),
 'WON_086': (('CFM_310t', 4),),
 'ICC_050': (('ICC_832t3', 2),),
 'ULD_713': (('ULD_430t', 7),),
 'EX1_248': (('EX1_tk11', 2),),
 'OG_273': (('CS2_101t', 5),),
 'UNG_960': (('CS2_101t', 2),)})
FIXED_TOKEN_IDS=frozenset({cid for recipe in FIXED_SUMMONS.values() for cid,count in recipe}
                        |{cid for cid,count in FIXED_BATTLECRIES.values()})
RULES.update({cid:('none',[('summon_right',child,count)])
              for cid,(child,count) in FIXED_BATTLECRIES.items()})
RULES.update({cid:('none',[('summon',child,count) for child,count in recipe])
              for cid,recipe in FIXED_SUMMONS.items()})
RULES.update({cid:('none',[]) for cid in FIXED_TOKEN_IDS})
RULES.update({'CFM_063':('minion',[('swap_stats',)]),'EX1_046':('minion',[('temporary_attack_buff',2)]),'EX1_570':('none',[('hero_attack',4),('armor',4)])})
RULES.update({'BOT_910': ('none', [('hand_buff', 2, 2)]),
 'CFM_626': ('friendly_minion', [('buff', 0, 3)]),
 'CS2_005': ('none', [('hero_attack', 2), ('armor', 2)]),
 'DMF_702': ('minion', [('damage', 3), ('hero_attack', 3)]),
 'EX1_623': ('friendly_minion', [('buff', 0, 3)]),
 'ICC_079': ('none', [('hero_attack', 3), ('armor', 3)]),
 'RLK_104': ('none', [('area_damage', 'other_minions', 2)]),
 'EX1_241': ('character', [('damage', 5)]),
 'TRL_517': ('none', [('hand_buff', 1, 1)]),
 'AT_005': ('minion', [('transform', 'AT_005t')]),
 'CS2_022': ('minion', [('transform', 'CS2_tk1')]),
 'TID_708': ('minion', [('transform', 'TID_708t')]),
 'BOT_257': ('none', [('deck_minions_set_cost', 1)]),
 'AT_005t': ('none', []),
 'TID_708t': ('none', [])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('AT_005t','TID_708t'))
RULES['YOP_026']=('none',[('summon','DMF_061t2',2),('board_buff',2,1)])
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('DMF_061t2',))
RULES['DMF_061t2']=('none',[])
AURAS={'DS1_175': ('BEAST', 1, 0),
 'EX1_185': ('DEMON', 1, 0),
 'EX1_508': ('MURLOC', 1, 0),
 'GIL_119': ('ELEMENTAL', 2, 0),
 'GVG_021': ('DEMON', 2, 2),
 'LOOT_136': ('others', 1, 0)}
HERO_IMMUNE_AURAS=frozenset(('GVG_021',))
FRIENDLY_KEYWORD_AURAS={'GIL_650': ('others', 'RUSH'), 'SCH_146': 'ELUSIVE'}
RULES.update({cid:('none',[]) for cid in set(AURAS)|set(FRIENDLY_KEYWORD_AURAS)})
# Frozen targeted keywords and draw/entry primitives; no generation pool approval.
RULES.update({'AT_053': ('none', [('draw', 2)]),
 'AT_069': ('minion', [('keyword', 'TAUNT')]),
 'AT_084': ('friendly_minion', [('buff', 2, 0)]),
 'AV_266': ('minion', [('freeze',), ('draw', 1)]),
 'BAR_750': ('none', [('area_damage', 'enemy_minions', 1)]),
 'BOT_067': ('minion', [('keyword', 'RUSH'), ('draw', 1)]),
 'BOT_246': ('none', [('area_damage', 'all_minions', 1)]),
 'CS3_027': ('minion', [('silence',), ('buff', 0, 3)]),
 'EX1_245': ('minion', [('silence',), ('damage', 1)]),
 'EX1_332': ('minion', [('silence',)]),
 'EX1_371': ('minion', [('keyword', 'DIVINE_SHIELD')]),
 'RLK_922': ('minion', [('buff', 3, 3), ('keyword', 'DIVINE_SHIELD'), ('damage_own_hero', 3)]),
 'WON_048': ('character', [('heal', 8), ('draw', 3)]),
 'WORK_009': ('friendly_minion', [('keyword', 'LIFESTEAL')]),
 'WW_410': ('minion', [('damage', 7), ('draw', 7)]),
 'YOP_033': ('none', [('draw', 3), ('damage_own_hero', 3)])})
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Frozen Paladin Mech dependencies: finite body, hand and tribe-scoped effects.
RULES.update({
 'ULD_217':('none',[]),
 'NX2_022':('none',[('historical_held_mech_windfury',)]),
 'JAM_010':('none',[]),
 'WORK_002':('none',[('historical_one_attack_buff',)]),
 'TSC_059':('none',[('historical_other_mech_keywords',)]),
})
END_EFFECTS={'ULD_217':[('buff_random_other',1,0)],'JAM_010':[('summon','CS2_101t',1)]}
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

RULES.update({'GVG_062':('none',[]),'DRG_225':('none',[('summon_right','DRG_225t',2)]),'DRG_225t':('none',[])})
AURAS['DRG_225']=('MECHANICAL',1,0)
TRIGGERS={'GVG_062':(('summon','friendly','MECHANICAL'),[('keyword_self','DIVINE_SHIELD')])}
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('DRG_225t',))
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

RULES.update({'TSC_644':('none',[('insert_fixed','TSC_644t',1,'bottom')]),
 'TSC_644t':('none',[('copy_self_right',1)]),'TSC_083':('none',[('historical_dredge_stats',)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('TSC_644t',))
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

RULES.update({'YOG_525':('none',[('hand_buff',1,1)]),'YOG_525t':('none',[('hand_buff',2,2)])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('YOG_525t',))
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Exact one-shot Corrupt identity; higher-paid-play hook is separate from casting.
RULES.update({'DMF_064':('none',[]),'DMF_064t':('none',[])})
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('DMF_064t',))
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Frozen finite Sunken City Colossals; generated-only, with exact appendages.
RULES.update({cid:('none',[]) for cid in ('TSC_026','TSC_026t','TSC_029','TSC_029t','TSC_029t2','TSC_030','TSC_030t2')})
TRIGGERS.update({'TSC_030':('attacked_self',[('zone_choice','friendly','deck','dredge')]),
 'TSC_030t2':('attacked_self',[('draw',1)]),
 'TSC_029':(('friendly_tribe_attacked','MECHANICAL'),[('area_damage','enemies',1)])})
DEATH_EFFECTS={'TSC_026t':[('armor',8)]}
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('TSC_026t','TSC_029t','TSC_029t2','TSC_030t2'))
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Finite historical Dredge consumers; no random outcome pool.
RULES.update({'TSC_909': ('none', [('historical_dredge', 'none')]), 'TSC_915': ('none', [('historical_dredge', 'none')]), 'TSC_637': ('character', [('damage', 2), ('historical_dredge', 'none')]), 'TSC_210': ('none', [('historical_dredge', 'spell_discount')]), 'TSC_911': ('none', [('historical_dredge', 'discount')]), 'TID_714': ('none', [('historical_dredge', 'armor')]), 'NX2_018': ('none', [('historical_dredge', 'undead_damage')]), 'TID_700': ('none', [('historical_dredge', 'opponent_cost')]), 'TSC_942': ('none', [('historical_dredge', 'stats')]), 'TSC_916': ('none', [('historical_dredge', 'none'), ('combo_operation', ('draw', 1))]), 'TSC_642': ('none', [('historical_dredge', 'mech_draw')])})
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Explicit conditional Dredge consumers and one literal Coldlight Lurker.
RULES.update({'TSC_070': ('none', []), 'TSC_086': ('none', [('historical_dredge', 'pirate_weapon')]), 'TSC_654': ('none', [('historical_dredge', 'affordable_draw')]), 'TSC_753': ('none', [('historical_dredge', 'murloc_health')]), 'TID_703': ('none', [('historical_dredge', 'reveal_damage')]), 'TSC_925': ('none', [('summon', 'TSC_925t', 1), ('historical_dredge', 'murloc_summon')]), 'TSC_925t': ('none', [])})
WEAPON_TRIGGERS={'TSC_070':[('historical_dredge','beast_discount')]}
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('TSC_925t',))
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

RULES['TID_099']=('none',[('historical_dredge','one_cost_recruit')])
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

RULES['TID_003']=('none',[('historical_dredge','murloc_copy')])
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Reviewed historical Magnetic bodies and exact Repairbot attachment return.
from . import magnetic
RULES.update(magnetic.RULES)
TRIGGERS.update(magnetic.TRIGGERS)
DEATH_EFFECTS.update(magnetic.DEATH_EFFECTS)
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|magnetic.FIXED_TOKEN_IDS
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Exact retired Colossal roots and appendages.
from . import historical_colossal
RULES.update(historical_colossal.RULES)
DEATH_EFFECTS.update(historical_colossal.DEATH_EFFECTS)
END_EFFECTS.update(historical_colossal.END_EFFECTS)
TRIGGERS.update(historical_colossal.TRIGGERS)
FIXED_TOKEN_IDS|=historical_colossal.FIXED_TOKEN_IDS
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

from . import reviewed_generation_bindings
RULES.update({cid:reviewed_generation_bindings.RULES[cid] for cid in reviewed_generation_bindings.TOKEN_IDS})
DEATH_EFFECTS.update({cid:reviewed_generation_bindings.DEATH_EFFECTS[cid] for cid in reviewed_generation_bindings.TOKEN_IDS if cid in reviewed_generation_bindings.DEATH_EFFECTS})
FIXED_TOKEN_IDS|=reviewed_generation_bindings.TOKEN_IDS-{'FP1_011'}
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Fixed-action and owner-power historical dependencies. No pool is narrowed.
from . import historical_power_primitives
RULES.update(historical_power_primitives.RULES)
RULES.update(historical_power_primitives.TOKEN_RULES)
TRIGGERS.update(historical_power_primitives.TRIGGERS)
DEATH_EFFECTS.update(historical_power_primitives.DEATH_EFFECTS)
FIXED_TOKEN_IDS|=historical_power_primitives.FIXED_TOKEN_IDS
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)
