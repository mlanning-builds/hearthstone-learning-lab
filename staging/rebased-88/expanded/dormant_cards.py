"""Explicit Dormant identities and fixed Dreadseed pool for the pinned patch."""
INITIAL = {'CORE_BT_156': 2, 'EDR_416t': 2, 'EDR_469': -1,
           'EDR_840t': 2, 'EDR_840t1': 1, 'EDR_840t2': 3, 'EDR_979': 2,
           'MEND_040': -1, 'TIME_046': 3, 'TIME_063': 5, 'TLC_253': -1}
DREADSEEDS = ('EDR_840t', 'EDR_840t1', 'EDR_840t2')
RULES = {cid: ('none', []) for cid in INITIAL if cid not in DREADSEEDS and cid != 'EDR_416t'}
RULES.update({
    'EDR_416': ('none', []),
    'EDR_820': ('none', []),
    'EDR_840': ('none', [('draw', 1), ('summon_fixed_random', DREADSEEDS)]),
    'EDR_841': ('none', [('summon_fixed_random', DREADSEEDS)]),
    'JAIL_850': ('none', []),
    'JAIL_997': ('minion', [('dormant_confinement',)]),
    'TIME_022': ('none', []),
    'TIME_442': ('enemy_minion', [('dormant_imprison',)]),
})
TOKEN_IDS = set(DREADSEEDS) | {'EDR_416t'}
CHOICES = {'EDR_820': [
    ('Dreadseeds', 'none', [('summon_fixed_random', DREADSEEDS), ('summon_fixed_random', DREADSEEDS)]),
    ('Damage', 'none', [('area_damage', 'all_minions', 2)]),
]}
DEATH_EFFECTS = {
    'EDR_841': [('summon_fixed_random', DREADSEEDS)],
    'TIME_442': [('dormant_release',)],
}
TRIGGERS = {
    'JAIL_850': ('other_friendly_minion_played', [('dormant_maiev',)]),
    'EDR_469': ('dormant_power_used', [('dormant_awaken_source',)]),
    'TIME_063': ('dormant_newest_played', [('dormant_reduce',)]),
}
WEAPON_TRIGGERS = {'EDR_416': [('summon', 'EDR_416t', 1)]}
