"""Ready cards in the temporary/attached-effect family; blockers remain explicit."""
RULES={
 'TLC_450':('none',[('temporary_next_discount',2)]),
 'TLC_451':('none',[('temporary_deck_discover',)]),
 'CAP_402':('none',[('on_draw_shuffle','CAP_400t2t',1,1),('follow_attach','CAP_402')]),
 'CAP_101':('none',[('damage_random_enemy',2),('follow_attach','CAP_101')]),
 'CAP_802':('none',[('summon','CAP_802t',1),('follow_attach','CAP_802')]),
}
TOKEN_IDS={'CAP_802t'}
