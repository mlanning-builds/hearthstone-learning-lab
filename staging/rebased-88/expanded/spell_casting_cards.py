"""Bounded consumers of shared internal spell casting."""
RULES={
 'EDR_259e1':('none',[('schedule_stored_payload',)]),
 'EDR_259':('none',[('store_highest_spell_aura','EDR_259e1',3)]),
 'EDR_464':('none',[('next_spells_twice',3)]),
 'TLC_836':('none',[]),
 'CATA_563':('none',[('choose_absorb_spell',4)]),
 'TLC_438':('none',[('cast_deck_spell',2,'prefer_source')]),
 'JAIL_515':('enemy_minion',[('shadow_rounds',)]),
 'TLC_522':('none',[('cast_fixed_spell','EX1_129','random'),('combo_cast_fixed_spell','EX1_129','random')]),
 'JAIL_974':('none',[]),
 'EX1_129':('none',[('area_damage','enemy_minions',1),('draw',1)]),
 'CS2_029':('character',[('damage',6)]),
}
TOKEN_IDS={'EX1_129','CS2_029','EDR_259e1'}
DEATH_EFFECTS={
 'CATA_563':[('cast_absorbed_spell',)],
 'TLC_522':[('cast_fixed_spell','EX1_129','random')],
 'JAIL_974':[('archmage_cast','CS2_029')],
}
# These fixed definitions plus existing spell CHOICES have internal cast paths.
# General dynamic spell pools are not admitted yet.
INTERNAL_SPELLS={'EX1_129','CS2_029','JAIL_515'}

TRIGGERS={'TLC_836':(('minion_cost_played',1),[('double_played_minion',)])}
