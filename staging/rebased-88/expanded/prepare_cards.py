"""Prepare cards with executable effects; unresolved family members stay gated."""
RULES = {
    'CATA_EVENT_401': ('none', []),
    'JAIL_395': ('friendly_deathrattle', [('replay_friendly_deathrattle',)]),
    'JAIL_444': ('none', [('sawbones_destroy',)]),
    'JAIL_721': ('none', []),
    'JAIL_906': ('none', []),
    'JAIL_326': ('friendly_minion', [('prepare_judgment',)]),
    'JAIL_453': ('none', []),
    'JAIL_457': ('none', [('buff_other_minions', 1, 1)]),
    'JAIL_718': ('none', []),
    'JAIL_890': ('none', []),
    'JAIL_909': ('none', [('prepare_combo_stats',)]),
    'JAIL_913': ('minion', [('buff', 5, 5), ('keyword', 'LIFESTEAL')]),
    'JAIL_998': ('friendly_minion', [('buff', 2, 0), ('keyword', 'RUSH')]),
}
PREPARE_IDS = (set(RULES) - {'JAIL_453'}) | {'JAIL_435'}
TRIGGERS = {'JAIL_718': ('spell_cast', [('draw', 1)])}

DEATH_EFFECTS = {'JAIL_906': [('moragg_recruit',)]}
TRIGGERS['JAIL_721'] = (('summon','friendly','DEMON'), [('gain_summoned_stats',)])
