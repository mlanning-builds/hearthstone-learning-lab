"""Bounded Bonus Effect family; random choices are keywords, not card pools."""
RULES = {
    'CATA_206': ('none', []),
    'EDR_849': ('none', []),
    'JAIL_101': ('enemy_minion', [('bonus_steal',)]),
    'TLC_240': ('none', []),
    'TLC_444': ('minion', [('bonus_target', 3)]),
    'TLC_465': ('none', []),
}
TOKEN_IDS = {'TLC_240t', 'TLC_240t2', 'TLC_240t3'}
TRIGGERS = {'EDR_849': ('other_friendly_minion_played', [('bonus_played',)])}
DEATH_EFFECTS = {
    'TLC_240': [('bonus_summon', 'TLC_240t'), ('bonus_summon', 'TLC_240t2'), ('bonus_summon', 'TLC_240t3')],
    'TLC_465': [('bonus_pass_deathrattle',)],
}
