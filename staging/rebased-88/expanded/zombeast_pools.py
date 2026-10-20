"""Pinned Standard Zombeast offers, independent of implementation coverage.

The text stage uses the complete affordable Hunter/neutral Standard census,
excluding obstructive text/keyword combinations. The keyword stage retains
its explicit historical Beast pool; Standard excludes Wild-only Echo.

Membership is literal. New recipes never change these source-backed pools.
Client fidelity is unvalidated; frozen identities and schemas are checked.
"""
from .zombeast_text_parts import PARTS as TEXT_PARTS
from .zombeast_keyword_parts import PARTS as KEYWORD_PARTS
TEXT_IDS=('CORE_BT_201', 'CORE_EDR_004_2026', 'CORE_EX1_014', 'CORE_EX1_162', 'CORE_GIL_622', 'CORE_LOE_039', 'CORE_LOOT_413', 'CORE_SCH_605', 'CORE_SW_072', 'CORE_UNG_084', 'CORE_UNG_912', 'DINO_435', 'EDR_014', 'EDR_492', 'EDR_849', 'END_013', 'END_015', 'JAIL_395', 'JAIL_878', 'JAIL_EVENT_100', 'TIME_042', 'TIME_058', 'TIME_601', 'TLC_102', 'TLC_242', 'TLC_245', 'TLC_246', 'TLC_250', 'TLC_256', 'TLC_603', 'TLC_825', 'TLC_827')
KEYWORD_IDS=('CORE_EX1_028', 'CORE_GIL_558', 'TIME_053', 'CS2_119', 'CS2_120', 'CS2_125', 'CS2_127', 'CS2_169', 'CS2_171', 'CS2_172', 'DMF_190', 'DRG_065', 'DRG_066', 'EX1_017', 'EX1_170', 'GIL_143', 'GIL_562', 'GVG_071', 'ICC_023', 'ICC_419', 'ICC_905', 'LEG_CS3_037', 'LOOT_125', 'LOOT_258', 'OG_325', 'OG_326', 'UNG_808', 'UNG_810', 'UNG_814', 'TIME_046', 'TSC_647', 'DMF_532', 'GIL_681', 'NX2_050')
SOURCE='Pinned 36.6.0.251952 metadata and https://hearthstone.wiki.gg/wiki/Template%3ADeathstalker_Rexxar_notes ; https://hearthstone.wiki.gg/wiki/Scourge_Tamer'
def contracts():
 return {('zombeast',1):tuple(TEXT_PARTS[cid] for cid in TEXT_IDS),('zombeast',2):tuple(KEYWORD_PARTS[cid] for cid in KEYWORD_IDS)}
def install(game):
 current=dict(getattr(game,'forge_contracts',{}))
 for key,value in contracts().items():current.setdefault(key,value)
 game.forge_contracts=current
