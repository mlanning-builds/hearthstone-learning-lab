"""Frozen physical split identities, ordered to match explicit CHOICES programs.

Branch order is declared explicitly: several XML suffix orders reverse the
parent program order. No text parsing or supported-only outcome filtering.
"""
SPLIT_BRANCHES = {'AV_295': ('AV_295a', 'AV_295b'), 'CFM_602': ('CFM_602a', 'CFM_602b'), 'DAL_350': ('DAL_350a', 'DAL_350b'), 'DRG_311': ('DRG_311b', 'DRG_311a'), 'ETC_373': ('ETC_373a', 'ETC_373b'), 'ETC_387': ('ETC_387b', 'ETC_387c'), 'EX1_154': ('EX1_154a', 'EX1_154b'), 'EX1_155': ('EX1_155a', 'EX1_155b'), 'EX1_160': ('EX1_160b', 'EX1_160a'), 'EX1_164': ('EX1_164a', 'EX1_164b'), 'GDB_851': ('GDB_851a', 'GDB_851b'), 'GVG_041': ('GVG_041b', 'GVG_041a'), 'NEW1_007': ('NEW1_007b', 'NEW1_007a'), 'OG_195': ('OG_195a', 'OG_195b'), 'REV_311': ('REV_311t2', 'REV_311t'), 'RLK_654': ('RLK_654a', 'RLK_654b'), 'SCH_612': ('SCH_612a', 'SCH_612b'), 'SW_422': ('SW_422b', 'SW_422a'), 'TRL_254': ('TRL_254a', 'TRL_254b'), 'TSC_650': ('TSC_650a', 'TSC_650d'), 'TTN_955': ('TTN_955A', 'TTN_955B'), 'ULD_135': ('ULD_135a', 'ULD_135b'), 'WON_014': ('WON_014s', 'WON_014s2'), 'WW_821': ('WW_821t1', 'WW_821t2'), 'YOG_529': ('YOG_529a', 'YOG_529b')}

SPLIT_BRANCHES['YOD_001']=('YOD_001b','YOD_001c')

def install(rules, choices):
 from copy import deepcopy
 for parent, tokens in SPLIT_BRANCHES.items():
  branches=choices[parent]
  if len(branches)!=2:raise ValueError('Expected two split branches: '+parent)
  for token, (_, mode, effects) in zip(tokens, branches):
   # Physical Rising Winds branches have no Twinspell tag. The parent
   # grants its Twinspell copy in its own program; split cards do not.
   if parent=='YOD_001':effects=[op for op in effects if op!=('add','YOD_001ts',1)]
   rules[token]=(mode,deepcopy(effects))
