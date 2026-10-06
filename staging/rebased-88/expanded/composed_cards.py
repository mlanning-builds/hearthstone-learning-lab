"""Second 30-card batch, composed against the pinned Standard snapshot."""
RULES = {
    'END_006': ('none', [('hero_attack',3),('schedule_turn_effect','start',1,2,(('hero_attack',3),))]),
    'EDR_482': ('none', [('heal_own_hero',12),('schedule_turn_effect','end',0,2,(('damage_own_hero',3),))]),
    'EDR_483': ('none', [('destroy_crystals',1),('schedule_turn_effect','start',2,1,(('gain_full_crystals',2),))]),
    'TIME_050': ('none', []),
    'CATA_469': ('none', []),
    'TLC_243': ('none', [('kindred',[('temporary_keyword_self','IMMUNE','end')])]),
    'CATA_161': ('none', [('choose_attack_recipient',)]),
    'EDR_812': ('none', [('weapon_previous_runes',)]),
    'JAIL_329': ('none', []),
    'JAIL_880': ('none', []),
    'TIME_215': ('none', [('area_damage','all_minions',1),('add','TIME_218',1)]),
    'EDR_813': ('none', []),
    'END_009': ('none', [('summon_death_identity','END_009t',2,'Treant')]),
    'JAIL_225': ('minion', [('damage',3),('shuffle_dead_target',2)]),
    'FIR_941': ('none', [('draw_summon_set_stats',8,8,'DIVINE_SHIELD')]),
    'TIME_043': ('friendly_minion', [('set_target_stats',8,8),('temporary_keyword_target','CANT_ATTACK_HERO','end')]),
    'CATA_533': ('none', [('enemy_edges_damage',5),('outcast_operation',('enemy_edges_damage',5))]),
    'TIME_039': ('none', [('zone_choice','enemy','hand','copy')]),
    'TIME_432': ('none', [('zone_choice','friendly','deck','copy'),('zone_choice','enemy','deck','copy')]),
    'TLC_521': ('none', [('zone_choice','enemy','deck','top')]),
    'TIME_770': ('none', [('draw_pick',2,'discount',2)]),
    'JAIL_206': ('none', [('draw_pick',3,'give',0)]),
    'TIME_032': ('none', [('extreme_draw_transfer','high','friendly'),('extreme_draw_transfer','high','friendly'),('extreme_draw_transfer','low','enemy'),('extreme_draw_transfer','low','enemy')]),
    'EDR_950': ('none', [('draw_temporary_discount',1)]),
    'TLC_245': ('none', [('choose_self_effect',(('Attack',('buff_self',3,0)),('Divine Shield',('keyword_self','DIVINE_SHIELD')),('Plants',('grant_death_self',(('death_summon','UNG_999t2t1',2),)))))]),
    'TLC_246': ('none', [('choose_self_effect',(('Stealth',('temporary_keyword_self','STEALTH','next_start')),('Elusive',('keyword_self','ELUSIVE')),('Windfury',('keyword_self','WINDFURY'))))]),
    'CORE_UNG_952': ('minion', [('buff',2,6),('keyword','TAUNT'),('grant_death_target',(('death_summon','UNG_810',1),))]),
    'DINO_429': ('minion', [('set_target_stats',1,1),('grant_death_target',(('area_damage','all_minions',2),))]),
    'TIME_701': ('none', [('zone_choice','friendly','deck','draw_bottom')]),
    'TIME_614': ('health_changed_enemy_minion', [('when_health_changed',('damage',6))]),
}
TRIGGERS = {
    'TIME_050': ('self_survived_damage',[('swap_self_stats',)]),
    'CATA_469': ('attacking_self',[('refresh_source_attack',)]),
    'JAIL_880': (('minion_mechanic_played','DEATHRATTLE'),[('event_minion_keyword','RUSH')]),
}
CHOICES = {'EDR_813': [('Ants','none',[('summon','EDR_813at',2)]),('Bug bites','minion',[('corpse_target_damage',2,4)])]}
TOKEN_IDS = {'END_009t','EDR_813at','UNG_999t2t1','UNG_810'}

WEAPON_TRIGGERS = {'JAIL_329':[('class_board_buff','PALADIN',2,2)]}
