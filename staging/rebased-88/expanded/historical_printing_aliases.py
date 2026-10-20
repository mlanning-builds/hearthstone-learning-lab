"""Explicit equivalent frozen historical printings of implemented Core cards.

The alias list is reviewed, never inferred at runtime from names or text.
Frozen semantic field equality is verified separately in the metadata receipt.
"""
from copy import deepcopy
ALIASES={'ETC_111': 'CORE_ETC_111', 'ETC_523': 'CORE_ETC_523', 'NX2_028': 'CORE_NX2_028', 'REV_023': 'CORE_REV_023', 'REV_308': 'CORE_REV_308', 'REV_946': 'CORE_REV_946', 'RLK_116': 'CORE_RLK_116', 'RLK_121': 'CORE_RLK_121', 'RLK_506': 'CORE_RLK_506', 'RLK_657': 'CORE_RLK_657', 'RLK_814': 'CORE_RLK_814', 'TTN_843': 'CORE_TTN_843', 'TTN_866': 'CORE_TTN_866', 'WW_329': 'CORE_WW_329'}
ALIASES['RLK_567']='CORE_RLK_567'
FIXED_TOKEN_IDS=frozenset(ALIASES)
TABLES=('RULES','DEATH_EFFECTS','END_EFFECTS','START_EFFECTS','END_EVERY_EFFECTS','TRIGGERS','AURAS','CONDITIONAL_ATTACK','SPELL_DAMAGE_VALUES','CONDITIONAL_SPELL_DAMAGE')

def apply(namespace):
 for alias,core in ALIASES.items():
  if core not in namespace['RULES'] and core not in namespace['PASSIVE']:
   raise ValueError('Missing reviewed Core implementation: '+core)
  for name in TABLES:
   table=namespace.get(name)
   if isinstance(table,dict) and core in table:table[alias]=deepcopy(table[core])
  if core in namespace['PASSIVE']:namespace['PASSIVE'].add(alias)
 namespace['PLAYABLE_TOKENS'].update(ALIASES)
 namespace['TOKEN_IDS']=namespace['TOKEN_IDS']|set(ALIASES)
