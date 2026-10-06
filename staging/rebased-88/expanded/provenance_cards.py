"""Cards sharing physical-origin and hand-entry predicates."""
RULES = {
 'CORE_REV_946': ('none', [('origin_clean_decks',)]),
 'DINO_409': ('none', []),
 'EDR_251': ('none', [('origin_draw',True,True), ('origin_draw',False,True)]),
 'EDR_256': ('none', [('origin_dreamwarden',)]),
 'JAIL_205': ('none', []),
 'JAIL_380': ('none', []),
 'JAIL_432': ('none', [('origin_sweeper',)]),
 'JAIL_433': ('minion', [('destroy',)]),
 'JAIL_434': ('none', []),
 'TLC_364': ('none', [('origin_discount','nonstarting')]),
}
DEATH_EFFECTS = {'JAIL_380': [('origin_draw',False,True)],
                 'JAIL_434': [('origin_discount','opponent_copy')]}
END_EFFECTS = {'JAIL_205': [('origin_steal_new_hand',)]}
