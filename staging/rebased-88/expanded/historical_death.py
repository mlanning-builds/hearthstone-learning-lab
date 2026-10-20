"""Explicit generated-only historical Deathrattles; no pool approval."""
RULES={cid:('none',[]) for cid in ('BOT_031', 'CFM_646', 'EX1_029', 'EX1_096', 'GVG_076', 'KAR_029', 'LEG_CS3_013', 'LOOT_413', 'OG_120', 'OG_151', 'OG_256', 'OG_323', 'TRL_525', 'TSC_001', 'ULD_177', 'ULD_184')}
DEATH_EFFECTS={'BOT_031': [('damage_enemy_hero', 2)],
 'CFM_646': [('damage_enemy_hero', 2)],
 'EX1_029': [('damage_enemy_hero', 2)],
 'EX1_096': [('draw', 1)],
 'GVG_076': [('area_damage', 'all_minions', 2)],
 'KAR_029': [('draw', 1)],
 'LEG_CS3_013': [('damage_enemy_hero', 3)],
 'LOOT_413': [('armor', 3)],
 'OG_120': [('area_damage', 'all_minions', 8)],
 'OG_151': [('area_damage', 'all_minions', 1)],
 'OG_256': [('board_buff', 1, 1)],
 'OG_323': [('draw', 1)],
 'TRL_525': [('draw', 2)],
 'TSC_001': [('damage_enemy_hero', 4)],
 'ULD_177': [('draw', 8)],
 'ULD_184': [('damage_enemy_hero', 3)]}
ROOTS={'EX1_556': (('death_summon', 'skele21', 1),),
 'EX1_534': (('death_summon', 'EX1_534t', 2),),
 'FP1_002': (('death_summon', 'FP1_002t', 2),),
 'FP1_007': (('death_summon', 'FP1_007t', 1),),
 'FP1_012': (('death_summon', 'FP1_012t', 1),),
 'ULD_183': (('hand_buff', 3, 3),),
 'ULD_208': (('heal_own_hero', 3),)}
ROOTS.update({'AV_130':(('hand_buff',2,2),),'WON_128':(('death_summon','FP1_012t',1),)})
ROOTS.update({'AV_211': (('death_summon', 'AV_211t', 1),),
 'AV_309': (('death_summon', 'AV_309t', 1),),
 'BAR_072': (('death_summon', 'BAR_072t', 1),),
 'BAR_751': (('death_summon', 'BAR_751t', 1),),
 'BOT_066': (('death_summon', 'BOT_066t', 1),),
 'BOT_445': (('death_summon', 'BOT_445t', 1),),
 'BOT_537': (('death_summon', 'BOT_537t', 1),),
 'BOT_565': (('death_summon', 'BOT_565t', 1),),
 'BT_008': (('death_summon', 'BT_008t', 1),),
 'BT_155': (('death_summon', 'BT_155t', 1),),
 'BT_304': (('death_summon', 'BT_304t', 1),),
 'BT_703': (('death_summon', 'BT_703t', 1),),
 'BT_726': (('death_summon', 'BT_726t', 1),),
 'BT_728': (('death_summon', 'BT_728t', 1),),
 'BT_761': (('death_summon', 'BT_761t', 1),),
 'DAL_088': (('death_summon', 'DAL_088t2', 1),),
 'DAL_566': (('death_summon', 'DAL_566t', 4),),
 'DAL_743': (('death_summon', 'DAL_743t', 1),),
 'DMF_223': (('death_summon', 'DMF_223t', 2),),
 'DMF_533': (('death_summon', 'DMF_533t', 2),),
 'ETC_526': (('death_summon', 'ETC_526t', 1),),
 'KAR_005': (('death_summon', 'KAR_005a', 1),),
 'LOOT_153': (('death_summon', 'LOOT_153t1', 7),),
 'LOOT_233': (('death_summon', 'LOOT_233t', 1),),
 'OG_216': (('death_summon', 'OG_216a', 2),),
 'OG_241': (('death_summon', 'OG_241a', 1),),
 'OG_249': (('death_summon', 'OG_249a', 1),),
 'OG_272': (('death_summon', 'OG_272t', 1),),
 'REV_012': (('death_summon', 'REV_012t', 1),),
 'REV_356': (('death_summon', 'REV_350t', 1),),
 'REV_375': (('death_summon', 'REV_375t', 1),),
 'RLK_070': (('death_summon', 'RLK_070t', 1),),
 'RLK_554': (('death_summon', 'RLK_554t', 1),),
 'RLK_833': (('death_summon', 'RLK_833t', 1),),
 'SCH_340': (('death_summon', 'SCH_340t', 1),),
 'SW_455': (('death_summon', 'SW_455t', 5),),
 'TOY_914': (('death_summon', 'TOY_914t', 2),),
 'TRL_503': (('death_summon', 'TRL_503t', 3),),
 'TRL_531': (('death_summon', 'TRL_531t', 1),),
 'TTN_861': (('death_summon', 'TTN_862t4', 2),),
 'ULD_174': (('death_summon', 'ULD_174t', 1),),
 'UNG_010': (('death_summon', 'UNG_201t', 3),),
 'UNG_076': (('death_summon', 'UNG_076t1', 2),),
 'UNG_083': (('death_summon', 'UNG_083t1', 1),)})
ROOTS.update({'EX1_577': (('summon_opponent', 'EX1_finkle', 1),),
 'GDB_331': (('death_summon', 'GDB_331t1', 2),),
 'GIL_616': (('death_summon', 'GIL_616t', 2),),
 'RLK_650': (('death_summon', 'RLK_650t', 1),),
 'TRL_363': (('summon_opponent', 'TRL_363t', 1),)})
NESTED_DEATH_EFFECTS={'GDB_331t1': (('death_summon', 'GDB_331t2', 2),),
 'GDB_331t2': (('death_summon', 'GDB_331t3', 2),),
 'GIL_616t': (('death_summon', 'GIL_616t2', 2),),
 'RLK_650t': (('death_summon', 'RLK_650t2', 1),)}
FIXED_TOKEN_IDS=frozenset(op[1] for ops in ROOTS.values() for op in ops if op[0] in ('death_summon','summon_opponent'))
FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(NESTED_DEATH_EFFECTS)|frozenset(op[1] for ops in NESTED_DEATH_EFFECTS.values() for op in ops if op[1] not in ROOTS)
RULES.update({cid:('none',[]) for cid in set(ROOTS)|FIXED_TOKEN_IDS})
DEATH_EFFECTS.update({cid:list(operations) for cid,operations in ROOTS.items()})
DEATH_EFFECTS.update({cid:list(ops) for cid,ops in NESTED_DEATH_EFFECTS.items()})
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Physical draw and a resumable post-draw set-stat operation.
RULES['YOG_510']=('none',[])
DEATH_EFFECTS['YOG_510']=[('historical_security_draw',)]
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)

# Required by the observed Nefarius Dragon component pool.
from .generation_cards import pool,random_cards
PROTODRAKE_POOL=pool(card_type="MINION",minimum=7,maximum=7)
RULES["SCH_711"]=("none",[])
DEATH_EFFECTS["SCH_711"]=[random_cards(PROTODRAKE_POOL,destination="board")]
GENERATED_IDS=frozenset(set(RULES)-FIXED_TOKEN_IDS)
