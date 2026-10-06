"""Bounded-zone choices and fixed-token families from the pinned Standard pool."""
RULES = {
    'CAP_102': ('none', [('draw', 2), ('summon', 'CAP_107t', 2)]),
    'CAP_107': ('none', [('add', 'CAP_107t', 1)]),
    'CAP_103': ('none', []),
    'CAP_106': ('none', [('summon', 'CAP_107t', 2)]),
    'CAP_403': ('none', [('destroy_random_enemy',), ('destroy_random_enemy',), ('local_enemy_deck_top',)]),
    'CATA_586': ('none', []),
    'EDR_271': ('none', []),
    'EDR_455': ('none', [('local_dead_dragon',)]),
    'EDR_494': ('none', []),
    'JAIL_734': ('none', [('local_deck_or_buff',)]),
    'TIME_713': ('none', [('local_enemy_summon', 'TIME_713t')]),
    'TIME_870': ('none', [('summon_from_zone', 'deck', (('type', 'eq', 'MINION'),)), ('local_enemy_summon', 'TIME_870t')]),
}
TOKEN_IDS = {'CAP_107t', 'EDR_271t', 'TIME_713t', 'TIME_870t'}
TOKEN_RULES = {cid: ('none', []) for cid in TOKEN_IDS}
TRIGGERS = {
    'CATA_586': ('self_survived_damage', [('summon', 'CATA_586', 1)]),
    'EDR_271': (('spell_school_cast', 'NATURE'), [('local_spell_treant', 'EDR_271t')]),
    'CAP_107t': ('local_cannoneers_fire', [('local_cannon_fire',)]),
}
DEATH_EFFECTS = {
    'CATA_586': [('damage_random_enemy', 2)],
    'TIME_713t': [('local_fill_enemy_coins', 'GAME_005')],
}
END_EFFECTS = {
    'CAP_107t': [('local_cannon_fire',)],
    'EDR_494': [('local_eat_deck_minion',)],
}
WEAPON_TRIGGERS = {'CAP_103': [('local_fire_event',)]}
