"""Explicit Nefarius component membership, separate from recipes and coverage.

Source table: https://hearthstone.wiki.gg/wiki/Victor_Nefarius
Observed 2026-10-15; frozen card definitions are build 36.6.0.251952.
No runtime line-count inference, Standard-only replacement or class filtering.
Independent client membership and behavior certification remain deferred.
"""
from .nefarius_parts import PARTS
DRAGON_IDS=('END_022', 'CORE_NEW1_023', 'EDR_571', 'TTN_924', 'TIME_056', 'TIME_045', 'CATA_305', 'CATA_898', 'DRG_211', 'CORE_EX1_043', 'TIME_856', 'TRL_526', 'TIME_720', 'TIME_051', 'BOT_066', 'DEEP_006', 'BRM_025', 'CATA_723', 'SCH_711')
UNDEAD_IDS=('RLK_503', 'RLK_538', 'RLK_958', 'CORE_EX1_012', 'CORE_WON_096', 'RLK_511', 'JAM_021', 'ICC_913', 'ULD_185', 'CORE_NEW1_020', 'ULD_205', 'ICC_700', 'CORE_OG_149', 'END_031', 'ULD_275', 'ICC_820', 'TIME_617', 'JAM_007', 'CATA_898', 'DINO_435')
def contracts():
 return {('dragon',1):tuple(PARTS[cid] for cid in DRAGON_IDS),('dragon',2):tuple(PARTS[cid] for cid in UNDEAD_IDS)}
def install(game):
 current=dict(getattr(game,'forge_contracts',{}))
 for key,value in contracts().items():current.setdefault(key,value)
 game.forge_contracts=current
