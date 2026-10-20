"""Explicit frozen historical Spell Damage bodies and attack restrictions.

Printed amounts override the archive's Boolean SPELLPOWER tag. These identities
are generated dependencies; this table does not approve any outcome pool.
"""
SPELL_DAMAGE_VALUES = {
 'AT_093':1, 'BOT_604':2, 'CFM_039':2, 'CS2_142':1, 'CS2_155':1,
 'CS2_197':1, 'DAL_096':1, 'DAL_748':1, 'DRG_211':2, 'EX1_284':1,
 'EX1_563':5, 'EX1_582':1, 'GIL_121':2, 'GVG_109':1, 'ICC_856':2,
 'ICC_913':1, 'OG_082':2, 'SCH_310':1, 'SW_061':2, 'TSC_053':1,
 'WON_365':2,
}
ATTACK_RESTRICTED = frozenset(('EX1_045','TSC_065','UNG_844'))
CONDITIONAL_SPELL_DAMAGE = {'TRL_312':('damaged',2)}
RULES = {cid:('none',[]) for cid in
         set(SPELL_DAMAGE_VALUES)|ATTACK_RESTRICTED|set(CONDITIONAL_SPELL_DAMAGE)}
RULES['EX1_284']=('none',[('draw',1)])
GENERATED_IDS=frozenset(RULES)
