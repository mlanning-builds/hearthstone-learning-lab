"""The complete fixed Leech family in the pinned Standard catalog."""
RULES = {
    'EDR_810': ('none', [('summon', 'EDR_810t', 2)]),
    'EDR_814': ('character', [('damage', 2), ('summon', 'EDR_810t', 1)]),
    'EDR_817': ('none', [('draw', 2), ('summon', 'EDR_810t', 2)]),
}
TOKEN_IDS = {'EDR_810t'}
END_EFFECTS = {'EDR_810t': [('leech_steal_health',)]}
