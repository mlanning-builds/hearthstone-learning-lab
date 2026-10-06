"""Forced combat families; no random global generation pools."""
RULES={
 'DINO_400':('none',[]),
 'DINO_136':('none',[('feast_raptors',)]),
 'TLC_810':('none',[('force_recruit_pair',(('mechanic','eq','DEATHRATTLE'),))]),
 'CORE_TTN_866':('none',[]),
 'CS3_020':('none',[]),
 'DINO_428':('minion',[('set_target_stats',8,10),('keyword','LIFESTEAL'),('force_enemy_into_target',)]),
 'EDR_014':('none',[('force_cheap_attacks',)]),
 'JAIL_435':('none',[('force_enemies_into_source',)]),
 'JAIL_454':('enemy_minion',[('force_summon_group','JAIL_454t',4,'target')]),
 'RLK_720':('none',[]),
 'TIME_434':('none',[]),
 'TIME_443':('none',[('force_summon_group','TIME_443t',2,'empty_deck_lowest')]),
 'TLC_230':('minion',[('force_summon_group','TLC_230t',4,'target')]),
 'TLC_107':('none',[('kindred',[('keyword_self','RUSH')])]),
}
TOKEN_IDS={'DINO_136t','JAIL_454t','TIME_434t','TIME_443t','TLC_230t','JAIL_511t'}
DEATH_EFFECTS={'TIME_434':[('force_summon_group','TIME_434t',1,'random')]}
END_EFFECTS={'CORE_TTN_866':[('force_enemies_into_source',)],'RLK_720':[('force_source_lowest',)]}
TRIGGERS={'DINO_400':('friendly_armor_gained',[('buff_self',2,2),('force_source_random',)]),'CS3_020':('hero_attack',[('force_follow_hero',)]),'TLC_107':('attacking_self',[('force_pre_damage',3)])}

# Closed combat outcomes: physical target identities, never global generation.
RULES.update({
 'CORE_BT_120':('enemy_minion',[('force_duel',)]),
 'EDR_453':('none',[]),
 'EDR_819':('none',[('force_all_others',)]),
})
END_EFFECTS['EDR_453']=[('force_source_excess',)]
DEATH_EFFECTS['EDR_819']=[('force_resurrect_kills',)]

RULES['TLC_821']=('none',[])
