"""Staged undiscounted Zombeast consumers; complete pools are still required.

No production registration: source admission must wait for complete stage-one
and stage-two contracts, including every generated component's behavior.
"""
STAGED_RULES={
 'RLK_821':('none',[('forge_zombeast_plain',)]),
 'ICC_828':('none',[('area_damage','enemy_minions',2)]),
}
STAGED_HERO_POWERS={'ICC_828':'ICC_828p'}
STAGED_POWER_OPERATIONS={'ICC_828p':(('forge_zombeast_plain',),)}
FIXED_TOKEN_IDS=frozenset(('ICC_828p','ICC_828t'))
