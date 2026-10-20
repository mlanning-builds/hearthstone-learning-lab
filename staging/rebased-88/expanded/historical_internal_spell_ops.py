"""Explicit automatic-cast admission for authored historical outcome programs.

This list is frozen from the named executable declaration modules. It does not
approve generation membership, certify behavior or accept arbitrary opcodes.
"""
IMPLEMENTED_OPERATIONS=frozenset(('add',
 'area_damage',
 'armor',
 'autocast_random',
 'board_buff',
 'board_keyword',
 'buff',
 'buff_random_hand_minion',
 'damage',
 'damage_enemy_hero',
 'damage_own_hero',
 'destroy',
 'destroy_random_enemy',
 'destroy_self',
 'draw',
 'draw_until',
 'equip',
 'filtered_draw',
 'freeze',
 'generate_discover',
 'generate_random',
 'generation_dynamic_summon',
 'generation_fill_plain_hand',
 'heal',
 'hero_attack',
 'hero_divine_shield',
 'historic_zone_buff',
 'historical_attack_weapon_soulbreaker',
 'historical_attack_weapon_tempest',
 'historical_attack_weapon_watercannon',
 'historical_batch_trigger_target_death',
 'historical_bonus_bandits',
 'historical_bonus_companion',
 'historical_bonus_inspiration',
 'historical_bonus_valkyr',
 'historical_bottle_contents',
 'historical_bottle_shadeleaf',
 'historical_bottle_shimmer',
 'historical_bottle_springwater',
 'historical_bottle_swarm',
 'historical_change_align',
 'historical_change_blazing',
 'historical_change_demons',
 'historical_change_hat',
 'historical_change_nostalgia',
 'historical_change_tampering',
 'historical_change_wave',
 'historical_change_whirlpool',
 'historical_copy_coolant',
 'historical_copy_literal_family',
 'historical_copy_next_spell_bonus',
 'historical_copy_quickdraw_operation',
 'historical_copy_recruit_one',
 'historical_copy_target_all',
 'historical_copy_target_delivery',
 'historical_copy_timed_cost',
 'historical_damage_blazing',
 'historical_damage_corpses',
 'historical_damage_descend',
 'historical_damage_discard_area',
 'historical_damage_hero_attack',
 'historical_damage_keeper',
 'historical_damage_ricochet',
 'historical_damage_shelves',
 'historical_damage_then',
 'historical_damage_threads',
 'historical_damage_twilight',
 'historical_damage_undeath',
 'historical_damage_unleash',
 'historical_damage_volcano_bind',
 'historical_damage_warband',
 'historical_death_spell_colossal_hands',
 'historical_death_spell_dead_air',
 'historical_death_spell_destroy_target',
 'historical_death_spell_resurrect',
 'historical_death_spell_saddle',
 'historical_death_spell_spread',
 'historical_discover_blind_box',
 'historical_discover_bronze',
 'historical_discover_deck',
 'historical_discover_demonic',
 'historical_discover_repeat_empty',
 'historical_draw_batch',
 'historical_equipment_depths',
 'historical_equipment_dollhouse',
 'historical_equipment_expanse',
 'historical_equipment_fan_club',
 'historical_equipment_giant',
 'historical_equipment_gym',
 'historical_equipment_kennels',
 'historical_equipment_library',
 'historical_equipment_reborn',
 'historical_event_sleep_target',
 'historical_excavate_dig',
 'historical_family_basic_totem',
 'historical_family_evolve_target',
 'historical_forge_spell_armor_damage',
 'historical_forge_spell_blackrock',
 'historical_forge_spell_campaign',
 'historical_forge_spell_distort',
 'historical_forge_spell_draw_combined',
 'historical_forge_spell_draw_match',
 'historical_forge_spell_ensmallen',
 'historical_forge_spell_implocs',
 'historical_forge_spell_suffusion',
 'historical_forge_spell_zombies',
 'historical_growing_weapon_death',
 'historical_harmonic_metal',
 'historical_harmonic_popstar',
 'historical_held_spellstone_buff',
 'historical_if_combo',
 'historical_lingering_allies',
 'historical_lingering_brand',
 'historical_lingering_copy_attack',
 'historical_lingering_groove',
 'historical_lingering_hand_copies',
 'historical_lingering_melomania',
 'historical_lingering_reverberations',
 'historical_location_timed_curse',
 'historical_location_timed_frozen',
 'historical_misc_enemy_next_cost',
 'historical_misc_fatigue_both',
 'historical_misc_health_one',
 'historical_misc_load_chamber',
 'historical_misc_showdown',
 'historical_misc_soulcage',
 'historical_misc_tribe_draw',
 'historical_misc_trolley_discard',
 'historical_movement_barrage',
 'historical_movement_bounce_all',
 'historical_movement_breakdance',
 'historical_movement_chum',
 'historical_movement_crane',
 'historical_movement_downsize',
 'historical_movement_gear_shift',
 'historical_movement_manufacture',
 'historical_movement_opponent_recruit',
 'historical_movement_order',
 'historical_movement_posse',
 'historical_movement_ritual',
 'historical_movement_smelt',
 'historical_movement_yogg_box',
 'historical_music_envy',
 'historical_music_forbidden',
 'historical_music_gluttony',
 'historical_music_riff',
 'historical_music_symphony',
 'historical_mutation_discount_zones',
 'historical_numeric_arrow',
 'historical_numeric_bioluminescence',
 'historical_numeric_cannibalize',
 'historical_numeric_eversong',
 'historical_numeric_jam_damage',
 'historical_numeric_last_stand',
 'historical_numeric_mark',
 'historical_numeric_phial',
 'historical_numeric_prescience',
 'historical_numeric_ransack',
 'historical_numeric_switcheroo',
 'historical_numeric_whispers',
 'historical_offer_open',
 'historical_offer_pair',
 'historical_offer_return',
 'historical_offer_rewind',
 'historical_outcome_attack_damage',
 'historical_outcome_forged_flame',
 'historical_outcome_purify',
 'historical_outcome_spell_poison',
 'historical_physical_draw_three',
 'historical_physical_mixtape',
 'historical_physical_offer',
 'historical_play_finale',
 'historical_resolution_crescendo',
 'historical_resolution_deathborne',
 'historical_resolution_drown',
 'historical_resolution_eradication',
 'historical_resolution_funnel',
 'historical_resolution_heat_wave',
 'historical_resolution_kyrian',
 'historical_resolution_sentence',
 'historical_resolution_soulfreeze',
 'historical_resolution_tether',
 'historical_resolution_weld',
 'historical_sleep_wildseed',
 'historical_state_depths',
 'historical_state_dreams',
 'historical_state_fires',
 'historical_state_front_lines',
 'historical_state_frozen_copy',
 'historical_state_grace',
 'historical_state_rampage',
 'historical_state_steal',
 'historical_state_synchronize',
 'historical_student_spell_chain',
 'historical_student_spell_conviction',
 'historical_student_spell_death',
 'historical_student_spell_flames',
 'historical_student_spell_freeze',
 'historical_student_spell_murlocs',
 'historical_student_spell_other_knife',
 'historical_student_spell_wrath',
 'historical_summoning_companions',
 'historical_summoning_embers',
 'historical_summoning_felfiends',
 'historical_summoning_imp_draw',
 'historical_summoning_lineup',
 'historical_summoning_lionfish',
 'historical_summoning_naga_follow',
 'historical_summoning_plant',
 'historical_summoning_pride',
 'historical_summoning_waltz',
 'historical_timed_alibi',
 'historical_timed_dew',
 'historical_timed_elusive',
 'historical_timed_feast',
 'historical_timed_inventor',
 'historical_timed_lightning',
 'historical_timed_love',
 'historical_timed_tar',
 'historical_utility_applause',
 'historical_utility_convert_shield',
 'historical_utility_maki_copy',
 'historical_utility_potion',
 'historical_utility_prison',
 'historical_utility_recruit',
 'historical_utility_spotlight',
 'historical_volley_collateral',
 'historical_volley_darts',
 'historical_volley_explosion',
 'historical_volley_fan',
 'historical_volley_lightshow',
 'historical_volley_mishap',
 'historical_volley_toll',
 'historical_zone_cluster',
 'historical_zone_destroy_bottom',
 'historical_zone_fetch',
 'historical_zone_radar',
 'historical_zone_recruits_buff',
 'historical_zone_scrapper',
 'historical_zone_spill',
 'historical_zone_tram_heist',
 'historical_zone_treant_draw',
 'insert_fixed',
 'keyword',
 'missiles',
 'outcast_operation',
 'refresh_mana',
 'schedule_turn_effect',
 'secret',
 'set_target_stats',
 'silence',
 'summon',
 'transform',
 'weapon_buff'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_sleep_wild_spirits',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_music_roots',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_lingering_accusation',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_music_projection',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_copy_destroy_deck','historical_timed_wheel','historical_timed_immolate'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_timed_form','historical_timed_jormungar'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_pair_choice',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_misfire','historical_utility_nets'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_gold','historical_utility_banner'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_wither',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_riot',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_stargazing','historical_utility_domino'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_mount',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_physical_return_policy',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_timed_deputization',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_multistrike','historical_utility_swing'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_physical_repackage','historical_physical_box'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_horseman_head',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_conductivity',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_pure_cold','historical_utility_disintegration','historical_utility_jars','historical_utility_embers'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_spyglass','historical_utility_banana_split','historical_utility_fangs','historical_utility_holy_book'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_annoy',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_locusts','historical_utility_reflections','historical_utility_puzzle'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_quel_forge',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_yogg_outcome',))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_inner_rage', 'destroy', 'damage_own_hero', 'refresh_mana', 'historical_damage_then', 'historical_copy_lunar_eclipse', 'historic_opponent_draw', 'freeze_enemies', 'historical_copy_target_delivery', 'heal_own_hero', 'historical_utility_ice_lance', 'historical_utility_shadowstep', 'historical_utility_vampiric_blood', 'historical_utility_howling_blast', 'historical_utility_vanish', 'historical_utility_vanish_uid'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_sleep_repeat_area', 'historical_utility_blood_boil', 'historical_utility_boil_tick', 'historical_utility_skull_tick', 'historical_utility_refresh_all'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_paths', 'historical_utility_ice_block', 'historical_utility_plague', 'historical_utility_plague_again'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_frost_hand_copies', 'historical_utility_metamorphosis', 'historical_utility_attack_secret'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_utility_soul_mirror', 'historical_utility_mirror_copy', 'historical_utility_mirror_attacks', 'historical_utility_mirror_attack', 'historical_utility_mirror_resolve'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(("forge_sidequest","forge_zombeast_plain"))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|frozenset(('historical_eudora_start','historical_eudora_reward'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|set(('historical_tour_begin','historical_tour_generate','historical_tour_mind_control','historical_tour_swipe','historical_tour_shadowflame','historical_tour_brawl','historical_tour_mortal','historical_tour_eviscerate','historical_copy_shadow_madness'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|{'historical_elise_shuffle','historical_elise_open'}

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|set(('historical_ungoro_mimic','historical_ungoro_scales','historical_ungoro_envenom','historical_ungoro_spore','historical_ungoro_reflection','historical_ungoro_genesis','historical_ungoro_echo','historical_ungoro_cleave'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|set(('historical_ungoro_mist','historical_ungoro_mist_destroy','historical_ungoro_explore','historical_ungoro_dinomancy','historical_ungoro_feeding'))

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|{'historical_ungoro_stampede','historical_ungoro_mana_bind'}

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|{'historical_ungoro_living','historical_ungoro_living_crystals'}

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|{'historical_utility_zola_golden'}

IMPLEMENTED_OPERATIONS=IMPLEMENTED_OPERATIONS|{'historical_scythe_discover'}
