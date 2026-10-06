"""Explicit effect recipes awaiting runtime integration. Never playable registration.

Values are ordered operation trees. Hooks distinguish battlecry, spell, death,
setup and passive behavior. Unimplemented operations remain visible; compiling
or executing this registry as though it were cards.RULES is prohibited.
"""
from engine.cards import UnsupportedCard
from . import generation_cards as generation

def definition(family, **hooks):
    return dict(family=family, hooks=hooks, status='defined_pending_integration', detail_level='top_level_recipe', executable=False)

def op(name, *args): return (name, *args)
def discover(**selector): return op('discover', selector)
def random_card(**selector): return op('random_card', selector)
def condition(name, value, *effects): return op('if', name, value, effects)
def dark(selector, **modifiers): return op('discover_with_dark_gift', selector, modifiers)

# Existing explicit generation recipes are incorporated without changing their
# live eligibility or reinterpreting printed card text.
DEFINITIONS={}
for cid,(target,effects) in generation.RULES.items():
    hooks=dict(play=tuple(effects),target=target)
    for attribute,hook in [('DEATH_EFFECTS','deathrattle'),('END_EFFECTS','end_turn'),('TRIGGERS','triggers')]:
        table=getattr(generation,attribute,{})
        if cid in table:hooks[hook]=table[cid]
    DEFINITIONS[cid]=definition('generation',**hooks)

IMBUE=op('imbue',1)
DEFINITIONS.update({
 'EDR_226':definition('imbue',battlecry=(op('draw_filtered',{'tribe':'BEAST'},1),IMBUE)),
 'EDR_227':definition('imbue',deathrattle=(IMBUE,)),
 'EDR_231':definition('imbue',target='character',spell=(op('heal_target',4),op('draw',1),IMBUE)),
 'EDR_264':definition('imbue',spell=(op('summon_random',{'type':'MINION','cost':2},{'keywords':['TAUNT']}),IMBUE)),
 'EDR_449':definition('imbue',battlecry=(IMBUE,)),
 'EDR_451':definition('imbue',battlecry=(IMBUE,),deathrattle=(IMBUE,)),
 'EDR_518':definition('imbue',battlecry=(IMBUE,op('choose_hand_card',{'type':'MINION'},op('cost_delta',-1)))),
 'EDR_519':definition('imbue',battlecry=(IMBUE,op('trigger_current_hero_power'))),
 'EDR_800':definition('imbue',battlecry=(IMBUE,)),
 'EDR_845':definition('imbue',start_game=(condition('all_starting_spells_have_school','NATURE',IMBUE,op('install_spell_counter',3,IMBUE)),)),
 'EDR_852':definition('imbue',battlecry=(IMBUE,)),
 'EDR_860':definition('imbue',target=('minion_if','imbue_count_at_least',2),battlecry=(condition('imbue_count_at_least',2,op('damage_target',4)),)),
 'EDR_871':definition('imbue',battlecry=(op('add_card','EDR_851t'),IMBUE)),
 'EDR_888':definition('imbue',battlecry=(op('discover',{'rarity':'LEGENDARY','wild_god':True},condition('imbue_count_at_least',4,op('selected_set_cost',1))),)),
 'EDR_970':definition('imbue',battlecry=(op('temporary_board_attack','enemy',-2,'next_owner_turn_start'),IMBUE)),
 'END_000':definition('imbue',target='character',spell=(op('damage_target',2),IMBUE)),
 'END_001':definition('imbue',battlecry=(IMBUE,)),
 'END_003':definition('imbue',spell=(op('draw_filtered',{'tribe':'UNDEAD'},1),op('imbue',2))),
 'FIR_921':definition('imbue',battlecry=(condition('imbue_count_at_least',2,op('draw',2)),)),
})

DEFINITIONS.update({
 'EDR_102':definition('dark_gift',battlecry=(dark({'type':'MINION','rarity':'LEGENDARY'}),)),
 'EDR_105':definition('dark_gift',battlecry=(dark({'type':'MINION','cost':3}),)),
 'EDR_456':definition('dark_gift',battlecry=(condition('holding_tribe','DRAGON',dark({'type':'MINION','tribe':'DRAGON'})),)),
 'EDR_487':definition('dark_gift',zones=('hand','deck'),trigger=('dark_gift_given_to_friendly_minion',op('copy_gift_to_self'))),
 'EDR_488':definition('dark_gift',spell=(dark({'type':'MINION','mechanic':'DEATHRATTLE'}),)),
 'EDR_528':definition('dark_gift',spell=(op('discover_copy_from_enemy_deck',{'type':'MINION'},condition('combo',True,op('give_selected_dark_gift'))),)),
 'EDR_654':definition('dark_gift',battlecry=(op('hand_cost_delta',{'type':'MINION','has_dark_gift':True},-2),)),
 'EDR_811':definition('dark_gift',spell=(op('discover',{'type':'MINION','tribe':'UNDEAD'},op('spend_corpses_if_available',2,op('give_selected_dark_gift'))),)),
 'EDR_856':definition('dark_gift',battlecry=(op('discover_from_own_deck',{'type':'MINION'},op('give_selected_dark_gift')),)),
 'EDR_882':definition('dark_gift',spell=(dark({'type':'MINION','tribe':'DEMON','minimum_cost':5},shuffle_unchosen=True),)),
 'END_013':definition('dark_gift',battlecry=(dark({'type':'MINION','cost':1}),)),
 'END_027':definition('dark_gift',spell=(dark({'type':'MINION','tribe':'DRAGON','era':'past'}),)),
 'FIR_900':definition('dark_gift',spell=(dark({'type':'MINION'},cost_delta=-2),)),
 'FIR_901':definition('dark_gift',battlecry=(condition('holding_dark_gift_minion',True,op('summon_token_by_dependency','FIR_901','dragon',2)),)),
 'FIR_920':definition('dark_gift',spell=(dark({'type':'MINION','any_mechanic':['COMBO','BATTLECRY','STEALTH']}),)),
 'FIR_922':definition('dark_gift',battlecry=(condition('holding_dark_gift_minion',True,op('weapon_attack',3)),)),
 'FIR_924':definition('dark_gift',battlecry=(dark({'type':'MINION','tribe':'DEMON'},copy_selected=1),)),
 'FIR_939':definition('dark_gift',target='character',spell=(op('damage_target',2),dark({'type':'MINION','class':'WARRIOR'}))),
 'FIR_956':definition('dark_gift',battlecry=(condition('holding_dark_gift_minion',True,op('temporary_hero_attack',3),op('armor',6)),)),
})

# Rewind wraps the entire effect sequence, not each random roll separately.
# Snapshot/choice/restore semantics and Morchie are runtime dependencies.
def rewind(hook, effects, count=1, **extra):
    return definition('rewind',rewind_count=count,**{hook:effects},**extra)
DEFINITIONS.update({
 'CORE_EDR_004_2026':rewind('battlecry',(dark({'type':'MINION','tribe':'BEAST'},kindred_cost_delta=-1),)),
 'TIME_000':rewind('spell',(op('generate',{'type':'MINION'},1,{'cost_delta':-3}),)),
 'TIME_001':rewind('spell',(op('random_enemy_missiles',3,2),)),
 'TIME_002':rewind('battlecry',(op('generate',{'type':'SPELL','class':'own'},2,{}),)),
 'TIME_003':rewind('battlecry',(op('draw_filtered_and_buff',{'type':'MINION'},2,2),)),
 'TIME_004':rewind('battlecry',(op('damage_random_enemy',7),)),
 'TIME_008':rewind('battlecry',(op('both_players_discard_random',1),)),
 'TIME_014':rewind('spell',(op('summon_random_mana_budget',12),)),
 'TIME_018':rewind('spell',(op('generate_and_heal_total_cost',{'type':'SPELL','school':'HOLY'},2),)),
 'TIME_033':rewind('battlecry',(op('cast_random_spells',{'school':'NATURE'},2),)),
 'TIME_034':rewind('battlecry',(op('both_players_equip_random_weapon'),op('buff_own_weapon',1,1))),
 'TIME_038':rewind('battlecry',(op('summon_random',{'type':'MINION','rarity':'LEGENDARY'},2),),count=3),
 'TIME_433':rewind('spell',(op('choose_random_enemy_minion',op('silence_selected'),op('destroy_selected')),)),
 'TIME_441':rewind('spell',(op('damage_distinct_random_enemies',2,4),)),
 'TIME_602':rewind('spell',(op('summon_random_then_attack',{'type':'MINION','tribe':'BEAST','cost':3},'random_enemy'),)),
 'TIME_610':rewind('spell',(op('summon_token_by_dependency','TIME_610','shade',4,{'random_bonus_effects':2}),)),
 'TIME_EVENT_999':rewind('spell',(op('discover',{'type':'SPELL','class':('any_before_rewind','own_after_rewind')}),)),
 'END_036':definition('rewind',passive=(op('rewind_keep_both_outcomes'),),battlecry=(discover(mechanic='REWIND',classes='any'),)),
 'TIME_035':definition('rewind',deathrattle=(random_card(mechanic='REWIND'),)),
})

def require_integrated(card_id):
    if card_id in DEFINITIONS:
        raise UnsupportedCard('Explicit definition awaits runtime integration: '+card_id)
    raise KeyError(card_id)


# A Herald use is one action. The card-text placeholder names the army;
# unknown numeric XML tags are not interpreted as use counts.
HERALD=op('herald')
DEFINITIONS.update({
 'CATA_156':definition('herald',spell=(HERALD,op('enemy_board_damage',4))),
 'CATA_158':definition('herald',deathrattle=(HERALD,)),
 'CATA_160':definition('herald',battlecry=(HERALD,op('grant_herald_soldier_keyword','RUSH'))),
 'CATA_492':definition('herald',activation=(HERALD,op('draw',1))),
 'CATA_497':definition('herald',battlecry=(HERALD,op('deathwing_cost_delta',('script_data','deathwing_discount')))),
 'CATA_525':definition('herald',battlecry=(HERALD,)),
 'CATA_530':definition('herald',spell=(HERALD,op('temporary_hero_keyword','LIFESTEAL'))),
 'CATA_561':definition('herald',spell=(HERALD,op('add_token_by_dependency','CATA_561','rush_elemental',2))),
 'CATA_565':definition('herald',battlecry=(HERALD,)),
 'CATA_580':definition('herald',battlecry=(HERALD,)),
 'CATA_722':definition('herald',battlecry=(HERALD,)),
 'CATA_725':definition('herald',battlecry=(HERALD,),deathrattle=(op('heal_hero',3),)),
 'CATA_780':definition('herald',battlecry=(HERALD,)),
 'CATA_785':definition('herald',target=('character_if','combo',True),spell=(HERALD,condition('combo',True,op('damage_target',3)))),
})

# Explicit halves; combination and splitting use the shared Shatter contract.
DEFINITIONS.update({
 'CATA_134':definition('shatter',halves=((op('summon_token_by_dependency','CATA_134','treant',2),),(op('grant_board_deathrattle',op('summon_token_by_dependency','CATA_134','treant',1)),))),
 'CATA_306':definition('shatter',target='friendly_minion',halves=((op('buff_target',2,3),op('target_keyword','ELUSIVE')),(op('summon_copy_of_target'),))),
 'CATA_479':definition('shatter',halves=((op('summon_token_by_dependency','CATA_479','drake',2),),(op('board_buff',1,0),op('board_keyword','DIVINE_SHIELD')))),
 'CATA_489':definition('shatter',target='character',halves=((op('damage_target',4),),(op('all_enemy_damage',2),))),
 'CATA_820':definition('shatter',halves=((op('draw_filtered',{'type':'MINION'},3),),(op('hand_buff',{'type':'MINION'},2,2),))),
 'CATA_202':definition('shatter',spell=(op('generate_combined_shatter',{'class':'other'},1),)),
 'TIME_101':definition('shatter',trigger=('owner_shatters_card',op('enemy_board_damage',2))),
})

DEFINITIONS.update({
 'CAP_002':definition('discover',spell=(op('discover',{'type':'MINION','mechanic':'STEALTH'},op('grant_selected_effect_until_turn_end','CAP_002')),)),
 'CAP_105':definition('discover',spell=(discover(type='MINION',tribe='PIRATE'),op('summon_token_by_dependency','CAP_105','cannoneer',2))),
 'CAP_407':definition('discover',spell=(op('discover',{'type':'MINION','minimum_cost':5},op('selected_keyword','PREPARE')),)),
 'CATA_484':definition('discover',battlecry=(discover(type='SPELL',cost=1,classes='any'),)),
 'CORE_BAR_541':definition('discover',target='character',spell=(op('damage_target',2),discover(type='SPELL'))),
 'CORE_CATA_009':definition('discover',target='character',spell=(op('freeze_target'),discover(type='SPELL'))),
 'CORE_RLK_066':definition('discover',battlecry=(op('spend_corpses_if_available',1,discover(rune='BLOOD')),)),
 'CORE_RLK_116':definition('discover',battlecry=(condition('friendly_undead_died_since_previous_turn_end',True,discover(rune='UNHOLY')),)),
 'CORE_YOP_001':definition('discover',spell=(discover(mechanic='OUTCAST'),op('next_card_cost_delta',{'mechanic':'OUTCAST'},-1))),
 'Core_LOE_115':definition('discover',choose_one=((discover(type='MINION'),),(discover(type='SPELL'),))),
 'EDR_270':definition('discover',spell=(op('discover',{'type':'SPELL','school':'NATURE'},op('selected_cost_delta',-2)),)),
 'EDR_273':definition('discover',spell=(discover(mechanic='CHOOSE_ONE',classes='other'),)),
 'EDR_517':definition('discover',battlecry=(op('discover_then_choose_destination',{'type':'SPELL'},('hand','opponent_deck_top')),)),
 'EDR_872':definition('discover',choose_one=((discover(type='SPELL',classes='MAGE'),),(discover(type='SPELL',classes='DRUID'),))),
 'FIR_927':definition('discover',battlecry=(discover(cost=5),op('gain_mana_next_turn_only',1))),
 'FIR_952':definition('discover',battlecry=(discover(type='SPELL',school='FEL'),op('hand_cost_delta',{'type':'SPELL','school':'FEL'},-1))),
 'JAIL_123':definition('discover',battlecry=(op('discover',{'type':'SPELL','minimum_cost':5},op('selected_cast_repetitions',2)),)),
 'JAIL_451':definition('discover',spell=(op('discover',{'type':'MINION','cost':5},op('spend_corpses_if_available',5,op('summon_selected_copy'))),)),
 'JAIL_861':definition('discover',spell=(op('discover',{'mechanic':'CHOOSE_ONE'},op('selected_combine_choices'),op('give_opponent_plain_selected_copy')),)),
 'RLK_025':definition('discover',target='minion',spell=(op('damage_target',3),condition('target_killed_by_effect',True,discover(rune='FROST')))),
 'TIME_016':definition('discover',spell=(op('discover',{'type':'MINION','tribe':'MECHANICAL','classes':'PALADIN','era':'past'},op('selected_buff',5,5)),)),
 'TIME_446':definition('discover',spell=(discover(type='MINION',tribe='DEMON',minimum_cost=5,classes='any'),condition('deck_has_no_minions',True,op('next_card_set_cost',{'type':'MINION'},1)))),
 'TIME_448':definition('discover',spell=(op('repeat',2,discover(type='MINION')),condition('deck_has_no_minions',True,op('hand_cost_delta',{'type':'MINION'},-2)))),
 'TIME_612':definition('discover',payment='health',spell=(discover(type='SPELL'),)),
 'TIME_730':definition('discover',battlecry=(op('repeat',2,op('discover',{'type':'MINION','tribe':'BEAST'},op('selected_buff',5,5),op('selected_destination','deck_bottom'))),)),
 'TIME_857':definition('discover',spell=(op('repeat',2,op('discover',{'type':'SPELL','school':'ARCANE','era':'past'},op('selected_cost_delta',-2))),)),
 'TLC_109':definition('discover',battlecry=(op('destroy_top_deck_card_then_discover_same_rarity'),)),
 'TLC_334':definition('discover',spell=(op('discover',{'type':'SPELL','minimum_cost':8,'classes':'any'},op('selected_set_cost',1)),)),
 'TLC_434':definition('discover',spell=(op('discover',{'type':'MINION','tribe':'UNDEAD'},op('spend_corpses_if_available',5,op('keep_all_options'))),)),
 'TLC_449':definition('discover',spell=(op('discover',{'type':'MINION','cost':1},op('selected_keyword','TEMPORARY')),)),
 'TLC_461':definition('discover',battlecry=(discover(cost=('remaining_mana',)),)),
})

# Additional shared random generation; modifiers bind to the selected physical
# result, not every card sharing its identity.
DEFINITIONS.update({
 'CATA_140':definition('generation',battlecry=(op('fill_hand_random',{'type':'MINION','tribe':'DRAGON'},condition('mana_spent_while_holding_at_least',25,op('selected_set_cost',1))),)),
 'CATA_499':definition('generation',on_play=(op('summon_random',{'type':'MINION','cost':1},2),),on_discard=(op('summon_random',{'type':'MINION','cost':1},2),)),
 'CATA_621':definition('generation',spell=(op('generate',{'type':'SPELL','class':'PALADIN','aura':True},1,{'duration_delta':1}),)),
 'CATA_EVENT_000':definition('generation',battlecry=(random_card(type='MINION',mechanic='COLOSSAL',era='past'),)),
 'CATA_EVENT_400':definition('generation',battlecry=(op('spend_all_mana_bind','spent'),op('summon_random',{'type':'MINION','cost':('bound','spent')},1))),
 'CORE_BOT_256':definition('generation',battlecry=(op('summon_random',{'type':'MINION','cost':('hand_size',)},1),)),
 'CORE_CATA_006':definition('generation',battlecry=(op('grant_other_friendly_minions_deathrattle',op('summon_random',{'type':'MINION','cost':('death_source_cost',)},1)),)),
 'CORE_WW_374':definition('generation',spell=(op('spend_up_to_corpses_bind',8,'spent'),op('summon_random',{'type':'MINION','cost':('bound','spent')},1))),
 'DINO_412':definition('generation',end_turn=(random_card(type='MINION',minimum_tribe_count=2),)),
 'DINO_415':definition('generation',spell=(op('discover',{'type':'MINION','mechanic':'DEATHRATTLE','minimum_cost':5},op('summon_selected'),op('trigger_selected_deathrattle')),)),
 'DINO_422':definition('generation',deathrattle=(op('repeat',2,op('summon_random_then_attack',{'type':'MINION','tribe':'BEAST','cost':3},'random_enemy')),)),
 'DINO_427':definition('generation',battlecry=(op('generate',{'mask':True,'class':'other'},1,{'combo_cost_delta':-2}),)),
 'DINO_430':definition('generation',battlecry=(op('discover',{'type':'MINION','tribe':'BEAST','rarity':'LEGENDARY','classes':'any'},op('store_selected_identity_on_source'),op('source_gain_selected_stats')),),deathrattle=(op('summon_stored_identity'),)),
 'EDR_461':definition('generation',spell=(op('summon_random',{'type':'MINION','cost':('if_spell_upgrade_counter_at_least',3,6,3)},2),)),
 'EDR_463':definition('generation',choose_one=((op('destroy_target',{'maximum_attack':3}),),(op('summon_random',{'type':'MINION','cost':2},1),))),
 'EDR_465':definition('generation',deathrattle=(op('summon_random',{'type':'MINION','tribe':'DRAGON'},('friendly_deaths_of_identity','EDR_465')),)),
 'EDR_781':definition('generation',trigger=('self_enters_hand_from_battlefield',op('summon_random',{'type':'MINION','cost':2},2))),
 'END_005':definition('generation',spell=(op('summon_random',{'type':'MINION','cost':4},1),op('spend_corpses_if_available',4,op('summon_random',{'type':'MINION','cost':4},1)),condition('outcast',True,op('summon_random',{'type':'MINION','cost':4},1)))),
 'END_015':definition('generation',kindred=(op('generate',{'type':'MINION','mechanic':'DEATHRATTLE'},1,{'cost_delta':-2}),),deathrattle=(op('generate',{'type':'MINION','mechanic':'DEATHRATTLE'},1,{'cost_delta':-2}),)),
 'END_020':definition('generation',target='minion',spell=(op('damage_target',1),op('branch_target_survival',(op('draw',1),),(op('summon_random',{'type':'MINION','cost':1},1),)))),
 'END_037':definition('generation',battlecry=(op('fill_board_random',{'type':'MINION','tribe':'DRAGON'},'friendly'),op('fully_heal_hero'),op('skip_next_owner_turn'))),
 'JAIL_200':definition('generation',spell=(op('summon_random',{'type':'MINION','cost':('base_plus_hero_attacks_this_game',3)},2),)),
 'JAIL_201':definition('generation',choose_one=((op('temporary_hero_attack',2),),(random_card(classes='DRUID'),))),
 'JAIL_328':definition('generation',deathrattle=(condition('deck_has_no_neutral_cards',True,op('generate',{'class':'PALADIN'},1,{'cost_delta':-2})),)),
 'JAIL_407':definition('generation',trigger=('after_owner_plays_card',op('generate',{'type':'MINION','mechanic':'BATTLECRY'},1,{'cost_delta':-2}))),
 'JAIL_448':definition('generation',deathrattle=(op('generate',{'type':'MINION','rarity':'LEGENDARY'},3,{'stats':(1,1),'set_cost':1}),)),
 'JAIL_474':definition('generation',spell=(op('generate',{'type':'MINION','cost':8},2,{'cost_delta':('negative_count_paid_cost_this_game',2)}),)),
 'JAIL_735':definition('generation',spell=(op('summon_random',{'type':'MINION','cost':8},1),condition('other_spells_cast_this_turn_at_least',3,op('summon_random',{'type':'MINION','cost':8},1)))),
 'JAIL_806':definition('generation',battlecry=(op('generate',{'type':'SPELL','minimum_cost':5},1,{'conditional_cost_delta':('starting_deck_has_no_spells',-5)}),)),
 'JAIL_878':definition('generation',deathrattle=(op('summon_random',{'type':'MINION','cost':1,'mechanic':'DEATHRATTLE'},1),)),
 'JAIL_879':definition('generation',spell=(op('summon_random',{'type':'MINION','tribe':'BEAST','cost':5},1),op('shuffle_token_by_dependency','JAIL_879','recast_when_drawn',2))),
 'JAIL_892':definition('generation',target='character',spell=(op('damage_target',2),op('generate_into_deck',{'type':'SPELL','class':'DEMONHUNTER'},1),condition('outcast',True,op('damage_target',2),op('generate_into_deck',{'type':'SPELL','class':'DEMONHUNTER'},1)))),
 'JAIL_912':definition('generation',deathrattle=(op('heal_hero',6),op('summon_random',{'type':'MINION','cost':6},1))),
 'JAIL_986':definition('generation',battlecry=(op('generate',{'type':'SPELL','currently_playable':True},1,{'temporary':True}),)),
 'JAIL_987':definition('generation',spell=(op('generate',{'type':'MINION','class':'SHAMAN'},1,{'locked_until_another_card_played':True}),)),
 'TIME_040':definition('generation',deathrattle=(random_card(type='MINION',cost=5,era='past'),)),
 'TIME_052':definition('generation',deathrattle=(op('summon_random',{'type':'MINION','era':'past'},1),)),
 'TIME_058':definition('generation',deathrattle=(op('summon_random',{'type':'MINION','cost':2},1,{'dormant_turns':2}),)),
 'TIME_102':definition('generation',battlecry=(op('generate',{'type':'MINION','cost':8},1,{'owner_turn_start_cost_delta':-1}),)),
 'TIME_444':definition('generation',deathrattle=(random_card(type='MINION',tribe='DEMON',era='past'),)),
 'TIME_615':definition('generation',spell=(op('fill_hand_random',{'type':'MINION','tribe':'UNDEAD'},{'payment':'health','expires':'owner_turn_end'}),)),
 'TIME_711':definition('generation',spell=(op('summon_random',{'type':'MINION','cost':1,'era':'past'},2,{'combo_attack':1}),)),
 'TIME_712':definition('generation',target='minion',spell=(op('destroy_target'),condition('combo',True,op('summon_random',{'type':'MINION','cost':8},1)))),
 'TIME_872':definition('generation',battlecry=(op('fill_board_random',{'type':'MINION','cost':1},'opponent'),)),
 'TIME_EVENT_997':definition('generation',target='location',spell=(op('reopen_target'),op('grant_target_deathrattle',op('summon_random',{'type':'MINION','cost':3},1)))),
 'TLC_462':definition('generation',spell=(op('summon_random',{'type':'MINION','cost':('if_discovered_this_turn',4,2)},1),)),
 'TLC_467':definition('generation',deathrattle=(op('generate',{'type':'SPELL','school':'FEL'},2,{'payment':'health'}),)),
 'TLC_469':definition('generation',deathrattle=(op('generate',{'type':'MINION','cost':2},2,{'temporary':True}),)),
 'TLC_479':definition('generation',deathrattle=(op('summon_random',{'type':'MINION','tribe':'BEAST','spell_school':'FEL'},1),)),
 'TLC_815':definition('generation',spell=(op('summon_random',{'type':'MINION','cost':4},1,{'keywords':['TAUNT']}),condition('kindred',True,op('summon_random',{'type':'MINION','cost':4},1,{'keywords':['TAUNT']})))),
})

# Maps retain all offered options and attach a same-turn play watcher to the
# selected physical card. The second choice excludes that selected option.
for cid,selector in {
 'TLC_435':{'rune':'FROST'},'TLC_442':{'type':'MINION','tribe':'MURLOC'},
 'TLC_464':{'type':'MINION','unplayed_tribe':True},'TLC_515':{'source':'own_deck'},
 'TLC_824':{'type':'MINION','tribe':'BEAST','attack_parity':'odd'},'TLC_900':{'type':'SPELL','school':'FEL'},
}.items():
    DEFINITIONS[cid]=definition('map',spell=(op('discover',selector,op('attach_same_turn_play_followup',op('choose_from_unchosen_original_options',1))),))

DEFINITIONS.update({
 'MEND_300':definition('animal_companion',spell=(op('replace_future_companions',{'tribe':'BEAST','cost_delta':1}),op('draw',1))),
 'MEND_303':definition('animal_companion',battlecry=(op('replace_future_companions',{'tribe':'BEAST','cost_delta':1}),)),
 'MEND_304':definition('animal_companion',battlecry=(op('companion_summon_count_delta',1,'game'),)),
 'MEND_307':definition('animal_companion',spell=(op('replace_future_companions',{'tribe':'BEAST','cost_delta':2}),op('choose_current_companion_to_summon'))),
 'MEND_500':definition('leyline',spell=(op('random_enemy_minion_damage_with_hero_excess',('leyline_effect_value','MEND_500')),)),
 'MEND_501':definition('leyline',battlecry=(op('leyline_cost_delta',-1,'game'),),deathrattle=(random_card(family='leyline'),)),
 'MEND_502':definition('leyline',spell=(op('summon_random',{'type':'MINION','cost':('leyline_effect_value','MEND_502')},1),)),
 'MEND_503':definition('leyline',battlecry=(op('leyline_repetition_delta',1,'game'),)),
 'MEND_504':definition('leyline',spell=(op('draw_with_cost_delta',('negative_leyline_effect_value','MEND_504')),)),
 'MEND_505':definition('leyline',spell=(op('add_each_identity',('MEND_500','MEND_502','MEND_504')),op('choose_leyline_upgrade'))),
 'MEND_506':definition('leyline',battlecry=(op('leyline_effect_delta',1,'game'),)),
})

DEFINITIONS.update({
 'CATA_185':definition('transformation',deathrattle=(op('transform_killing_minion','CATA_185'),)),
 'CATA_496':definition('control',target='enemy_minion',spell=(op('take_control_until_end_of_original_owner_turn'),op('target_cannot_attack_until_turn_end'))),
 'CATA_567':definition('transformation',spell=(op('for_each_friendly_minion',op('capture_original_identity'),op('transform_cost_delta',1),op('grant_transformed_deathrattle',op('summon_captured_original'))),)),
 'CATA_615':definition('transformation',zones=('hand',),condition=('all_other_hand_costs_same_parity',op('transform_self_by_dependency','CATA_615','worgen_king'))),
 'CATA_979':definition('transformation',battlecry=(op('choose_hand_card',{'type':'SPELL'},op('replace_selected_with_random',{'type':'SPELL','cost':('selected_cost',)},2)),)),
 'DINO_414':definition('transformation',target='minion',spell=(op('choose_different_minion',op('transform_initial_target_into_selected_identity')),)),
 'EDR_493':definition('transformation',battlecry=(op('for_each_hand_minion',op('transform_random',{'type':'MINION','tribe':'DEMON'},{'retain_stats':True,'retain_cost':True})),)),
 'EDR_529':definition('transformation',replacement=('self_would_transform_into_minion',op('replace_transform_result_with_cost_delta',2))),
 'EDR_873':definition('transformation',battlecry=(op('for_each_deck_card',{'class':'NEUTRAL'},op('transform_random',{'class':'DRUID'})),)),
 'JAIL_313':definition('transformation',battlecry=(op('choose_hand_card',{},op('transform_random',{'type':'SPELL','cost':('selected_cost_plus',5)},{'retain_cost':True})),)),
 'JAIL_502':definition('transformation',start_turn=(op('swap_self_with_random_enemy_hand_minion'),)),
 'JAIL_EVENT_102':definition('transformation',spell=(op('both_players_summon_random',{'type':'MINION','cost':2},2),op('for_each_friendly_minion',op('transform_cost_delta',1)))),
 'TIME_049':definition('transformation',start_turn=(op('transform_self_random',{'type':'MINION','cost':5}),)),
 'TIME_055':definition('transformation',trigger=('self_survives_damage',op('transform_self_random',{'type':'MINION','cost':7}))),
 'TIME_707':definition('transformation',spell=(op('replace_hand_and_deck_random',{'mechanic':'CHOOSE_ONE','era':'past'},{'cost_delta':-1}),)),
 'TLC_235':definition('transformation',target='minion',spell=(op('capture_target_owner_cost_position'),op('destroy_target'),op('summon_random_for_captured_owner',{'type':'MINION','cost':('captured_cost',)},1))),
 'CATA_786':definition('automatic_casting',trigger=('owner_casts_spell',op('cast_random_spells',{'cost':('event_spell_cost',),'class':'other'},1))),
 'EDR_031':definition('automatic_play',end_turn=(op('repeat',3,op('play_top_deck_card')),)),
 'EDR_520':definition('automatic_casting',activation=(op('spend_all_mana_bind','spent'),op('cast_random_spells',{'cost':('bound','spent')},1))),
 'FIR_959':definition('automatic_casting',immunity=('spell_school','FIRE'),battlecry=(op('cast_random_mana_budget',{'school':'FIRE'},15,{'targets':'enemies'}),)),
 'JAIL_122':definition('automatic_casting',battlecry=(op('install_game_trigger','owner_casts_spell',op('summon_random',{'type':'MINION','cost':('event_spell_cost',)},1)),)),
 'JAIL_321':definition('automatic_casting',battlecry=(condition('cast_spell_this_turn',True,op('cast_random_spells',{'class':'MAGE','mechanic':'SECRET'},2)),)),
 'JAIL_500':definition('automatic_play',spell=(op('replay_other_cards_from_current_turn',{'targets':'prefer_enemies'}),op('end_owner_turn'))),
 'TIME_009':definition('automatic_casting',battlecry=(op('put_each_distinct_deck_aura_into_battlefield'),)),
 'TIME_013':definition('discover',trigger=('owner_casts_spell',discover(type='SPELL',school='NATURE',era='past'))),
 'TIME_860':definition('automatic_casting',battlecry=(op('offer_random_secrets',2,op('cast_selected_for_owner'),op('cast_unchosen_for_opponent')),)),
 'TLC_430':definition('automatic_casting',end_turn=(op('recast_random_spell_from_current_turn',{'school':'HOLY'},{'targets':'prefer_source'}),)),
 'JAIL_730':definition('void_soul',trigger=('owner_hero_attacks',op('add_card','JAIL_732'))),
 'JAIL_732':definition('void_soul',spell=(op('summon_random',{'type':'MINION','tribe':'DEMON','cost':('void_soul_level',1)},1),op('increase_future_void_soul_level',1))),
 'JAIL_733':definition('void_soul',deathrattle=(op('add_card','JAIL_732'),)),
 'JAIL_891':definition('void_soul',target='minion',spell=(op('damage_target',3),condition('target_killed_by_effect',True,op('add_card','JAIL_732')))),
 'JAIL_875':definition('discover',trigger=('owner_hero_attacks',op('discover',{'class':'DRUID'},op('selected_cost_delta',('negative_owner_hero_attack',))))),
})

DEFINITIONS.update({
 'CATA_301':definition('replacement_effect',spell=(op('install_next_healing_replacement','damage','until_owner_turn_end'),)),
 'CATA_307':definition('persistent',battlecry=(op('set_hero_current_health',15),op('install_one_shot_trigger','owner_hero_reaches_full_health',op('damage_enemy_hero',15)))),
 'CATA_481':definition('stored_cards',battlecry=(op('remove_random_enemy_hand_cards_into_source_storage',2),op('source_dormant',2)),deathrattle=(op('return_stored_cards_to_original_hand'),)),
 'CATA_527':definition('location',target='character',activate=(op('damage_target',1),),trigger=('owner_casts_fel_spell',op('reopen_self')),deathrattle=(op('summon_token_by_dependency','CATA_527','unshackled',1),)),
 'CATA_591':definition('persistent',battlecry=(op('replace_owner_turn_draw','discover_from_own_deck',{'selected_cost_delta':-3,'destroy_unchosen':True}),)),
 'CATA_614':definition('persistent',battlecry=(op('discover',{'type':'SPELL','class':('source_current_class',)}),),hand_turn_transition=(op('swap_source_class'),)),
 'CATA_EVENT_001':definition('stored_cards',battlecry=(op('choose_hand_card',{},op('attach_delayed_discard',3,op('summon_source_copy'))),)),
 'CORE_BT_120':definition('forced_combat',target='enemy_minion',battlecry=(op('repeat_combat_until_one_dies','source','target'),)),
 'CORE_CFM_670':definition('replacement_effect',aura=(op('replace_all_target_selection_with_random_legal_target'),)),
 'CORE_DAL_575':definition('replacement_effect',aura=(op('multiply_owner_card_summon_count',2),)),
 'CORE_EDR_003':definition('replacement_effect',aura=(op('multiply_owner_corpses_gained',2),),battlecry=(op('draw_filtered',{'spends_corpses':True},1),)),
 'CORE_LOOT_101':definition('secret',secret=('opponent_played_minion',op('damage_event_minion_with_excess_to_its_hero',6))),
 'CORE_RLK_086':definition('stored_cards',track=('minion_killed_by_this_weapon',op('store_victim_identity')),deathrattle=(op('summon_each_stored_victim'),)),
 'EDR_258':definition('replacement_effect',aura=(op('friendly_divine_shield_hit_requirement',3),)),
 'EDR_453':definition('forced_combat',end_turn=(op('attack_random_enemy_minion',{'excess_to_enemy_hero':True}),)),
 'EDR_454':definition('stored_cards',target='friendly_dragon',spell=(op('summon_token_by_dependency','EDR_454','egg',1,{'stored_minion_copy':'target'}),)),
 'EDR_525':definition('choose_one',choose_one=((op('temporary_source_keyword','POISONOUS','owner_turn_end'),),(op('grant_source_deathrattle',op('all_enemy_damage',2)),))),
 'EDR_780':definition('hidden_state',battlecry=(op('summon_source_copy_bind','copy'),op('secretly_select_one',('source',('bound','copy')),op('destroy_selected_on_damage')))),
 'EDR_819':definition('forced_combat',battlecry=(op('attack_each_other_minion_record_kills'),),deathrattle=(op('resurrect_recorded_kills'),)),
 'END_012':definition('infinity',battlecry=(op('temporary_weapon_attack_set','INFINITY','owner_turn_end'),)),
 'END_018':definition('infinity',battlecry=(op('select_random_hand_card',op('store_selected_cost_state'),op('selected_set_cost','INFINITY')),),deathrattle=(op('restore_stored_card_cost_state'),)),
 'END_024':definition('secret',secret=('opponent_turn_ends',op('select_highest_health_enemy_minion',{'ties':'random'},op('damage_selected','INFINITY')))),
 'JAIL_315':definition('secret',secret=('enemy_minion_declares_attack',op('transform_attacker_by_dependency','JAIL_315','sheep'))),
 'JAIL_330':definition('replacement_effect',zones=('battlefield','hand','deck'),trigger=('self_gains_stats',op('additional_nonrecursive_self_buff',1,1))),
 'JAIL_398':definition('deathrattle',zones=('battlefield','hand','deck'),deathrattle=(op('all_other_character_damage',3),)),
 'JAIL_421':definition('persistent',zones=('hand','deck'),trigger=('four_friendly_characters_damaged_in_owner_turn',op('summon_this_physical_card'))),
 'JAIL_443':definition('replacement_effect',replacement=('self_would_damage_hero',op('shuffle_token_by_dependency_into_victim_deck','JAIL_443','blight',('replaced_damage_amount',)))),
 'JAIL_703':definition('cosmetic',deathrattle=(op('enable_owner_emote','SORRY'),)),
 'JAIL_719':definition('stored_cards',battlecry=(op('retain_one_random_deck_card'),op('move_other_deck_cards_to_void')),start_turn=(op('get_cards_from_void',2),)),
 'JAIL_851':definition('hidden_state',battlecry=(op('investigate_enemy_hand_identity'),op('watch_enemy_next_turn_played_identity',op('add_coins',3)))),
 'JAIL_852':definition('stored_cards',battlecry=(op('shuffle_both_hands_together_and_redistribute'),)),
 'MEND_044':definition('dormant',target='minion',spell=(op('buff_target',0,2),op('target_keyword','TAUNT'),op('target_dormant_until','end_of_next_owner_turn'))),
 'TIME_024':definition('infinity',battlecry=(op('schedule_source_attack_set','next_owner_turn_start','INFINITY'),)),
 'TIME_064':definition('replacement_effect',aura=(op('multiply_owner_trigger_count',('BATTLECRY','DEATHRATTLE','HERO_POWER','END_TURN'),2),)),
 'TIME_217':definition('replacement_effect',replacement=('owner_nature_spell_would_damage_self',op('summon_random',{'type':'MINION','cost':5},1))),
 'TIME_618':definition('persistent',battlecry=(op('grant_hero_deathrattle',op('spend_up_to_corpses_bind',20,'spent'),op('resurrect_owner_hero',('bound','spent'))),)),
 'TIME_620':definition('secret',secret=('friendly_minion_dies_turn_after_played',op('resummon_event_minion'))),
 'TIME_706':definition('stored_cards',battlecry=(op('store_current_hand'),op('replace_hand_with_starting_hand'),op('schedule_hand_swap_back','owner_turn_end'))),
 'TIME_852':definition('conditional_aura',aura=(condition('control_other_dragon',True,op('spell_cost_delta',{'school':'ARCANE'},-2)),)),
 'TIME_861':definition('stored_cards',battlecry=(op('generate_and_track_physical_cards',{'type':'SPELL','era':'past'},3,op('when_all_played',op('add_card','TIME_861'))),)),
 'TIME_875':definition('fabled',battlecry=(condition('enemy_hand_contains_dependency',('TIME_875','king_llane'),op('destroy_enemy_hand_dependency','TIME_875','king_llane'),op('halve_enemy_health')),)),
 'TIME_890':definition('fabled',hand_cost=(condition('control_dependency',('TIME_890','karazhan'),op('set_cost',0)),),battlecry=(op('silence_all_other_minions'),op('destroy_all_other_minions'))),
 'TIME_EVENT_998':definition('stored_cards',battlecry=(op('exile_hand_minions_for_turns',2,{'return_buff':(5,5)}),)),
 'TLC_241':definition('persistent',aura=(op('provide_spell_while_source_alive',{'cost':2,'school':'HOLY','effect':(op('buff_target',2,2),op('target_keyword','DIVINE_SHIELD'))}),)),
 'TLC_251':definition('replacement_effect',battlecry=(op('next_kindred_repetitions',2),)),
 'TLC_452':definition('persistent',zones=('hand',),hand_entry=(op('assign_random_titan_ability'),),hand_turn_transition=(op('replace_random_titan_ability'),)),
 'TLC_821':definition('forced_combat',trigger=('owner_heals_enemy',op('source_attacks_event_target'))),
})

# Setup and deck-construction hooks remain separate from played effects.
DEFINITIONS.update({
 'CATA_213':definition('setup',battlecry=(condition('starting_minion_cost_total_equals',100,op('split_stats_among_deck_minions',100)),)),
 'CS3_035':definition('setup',start_game=(condition('both_starting_decks_contain','CS3_035',op('turn_time_limit_seconds',15)),)),
 'EDR_000':definition('setup',start_game=(op('both_players_maximum_mana_cap_delta',5),),battlecry=(op('gain_mana_crystals',3),)),
 'JAIL_384':definition('setup',start_game=(op('duplicate_other_starting_legendary_cards'),)),
 'JAIL_397':definition('deck_construction',deck_build=(op('choose_card',{'type':'MINION','cost':2},op('add_selected_to_starting_deck',10)),)),
 'JAIL_430':definition('deck_construction',deck_build=(op('base_deck_size',20),op('starting_health',40)),start_game=(op('copy_enemy_starting_deck_cards',20),),battlecry=(op('draw_until_hand_full'),)),
 'JAIL_504':definition('setup',start_game=(op('request_second_player'),),battlecry=(op('choose_upgraded_counterfeit'),op('replace_owner_coins_this_game_with_selected'),op('add_selected',3))),
 'JAIL_509':definition('setup',start_game=(op('install_overdraw_storage',{'return_when_hand_space':True,'cost_delta':-1}),)),
 'JAIL_800':definition('setup',start_game=(condition('starting_deck_has_no_other_minions',True,op('replace_power_by_dependency','JAIL_800','mug')),condition('starting_deck_has_no_spells',True,op('replace_power_by_dependency','JAIL_800','zee')))),
 'JAIL_831':definition('deck_construction',deck_build=(op('choose_contraband_beasts',3),),battlecry=(op('discover_from_deck_build_choices',op('selected_cost_delta',-3)),)),
 'JAIL_860':definition('setup',start_game=(condition('all_starting_card_costs_at_most',3,op('schedule_set_mana_after_owner_turns',5,10)),)),
 'TIME_005':definition('fabled',deck_build=(op('deck_size',40),op('include_fabled_family','TIME_005',10)),battlecry=(condition('played_all_other_family_members','TIME_005',op('destroy_enemy_hero')),)),
 'TIME_020':definition('fabled',start_game=(op('remove_self_from_starting_deck'),op('install_argus_demon_kill_counter',4,op('return_self_to_hand'))),),
})

for cid,progress,reward in (
 ('END_017',('ordered',('hand_full',),('hand_empty',)),'tick_and_tock'),
 ('TLC_229',('played_minions_distinct_tribes',6),'ashalon'),
 ('TLC_460',('cards_discovered',8),'origin_stone'),
 ('TLC_602',('owner_turns_survived',10),'latorvius'),
 ('TLC_631',('damage_events',{'amount':2,'enemy':True,'owner_turn':True},12),'gorishi_colossus'),
 ('TLC_830',('played_beast_attack_values',(1,3,5,7)),'shokk'),
):
    DEFINITIONS[cid]=definition('quest',quest=(progress,op('add_reward_by_dependency',cid,reward)))
DEFINITIONS['TLC_817']=definition('quest',quests=((('spells_cast_school','HOLY',4),op('add_reward_by_dependency','TLC_817','lifes_breath')),(('spells_cast_school','SHADOW',4),op('add_reward_by_dependency','TLC_817','deaths_touch'))))
DEFINITIONS['TLC_EVENT_400']=definition('quest',sidequest=(('played_minions_any_tribe',('BEAST','UNDEAD'),3),op('craft_zombeast',{'cost_delta':-3})))

# Colossal appendage identity/order comes from a required dependency manifest.
# Count alone is insufficient to integrate these definitions into the engine.
for cid,count,hooks in (
 ('CATA_139',4,dict(trigger=('own_wickerfang_leg_gains_stats',op('source_gain_event_stats')))),
 ('CATA_150',2,dict(end_turn=(op('trigger_all_friendly_minion_deathrattles'),))),
 ('CATA_151',2,dict(aura=(op('owner_hero_keyword','WINDFURY'),))),
 ('CATA_153',2,dict(battlecry=(op('generate',{'type':'MINION','cost':('source_attack',)},2,{'set_cost':1}),))),
 ('CATA_154',2,dict(aura=(op('owner_other_class_spell_repetitions',2),))),
 ('CATA_155',2,dict(replacement=('owner_hero_would_lose_health_on_owner_turn',op('gain_hero_max_health_instead',('replaced_health_loss',))))),
 ('CATA_300',3,dict(trigger=('owner_restores_character_health',op('source_attacks_random_enemy_minion')))),
 ('CATA_432',4,dict()),
 ('CATA_488',2,dict(end_turn=(op('all_other_minion_damage',3),))),
 ('CATA_550',99,dict(persistent=(op('queue_unplaced_appendages'),),trigger=('friendly_board_space_available',op('summon_queued_appendages_until_full')))),
 ('CATA_726',2,dict(replacement=('friendly_arm_or_soldier_effect',op('destroy_enemy_deck_minions_instead')))),
):
    DEFINITIONS[cid]=definition('colossal',colossal=op('summon_appendages_by_dependency',cid,count),**hooks)

DEFINITIONS.update({
 'CAP_405':definition('custom_creation',battlecry=(op('choose_sham_trial_components'),op('choose_trial_duration'),op('install_chosen_trial'))),
 'CAP_805':definition('stored_cards',spell=(op('capture_both_boards_by_owner'),op('destroy_all_minions'),op('give_each_owner_bound_resummon_spell',{'cost':3,'payload':'captured_owner_board'}))),
 'CAP_806':definition('resurrection',battlecry=(op('resurrect_friendly_minions_reborn_this_game'),op('each_result_attacks_random_enemy_minion'))),
 'CATA_190h':definition('herald',battlecry=(op('choose_cataclysms',('script_data','cataclysm_choice_count')),op('execute_chosen_cataclysms')),upgrade=(op('herald_threshold_increment',2),)),
 'CATA_470':definition('custom_creation',battlecry=(op('craft_undead_dragon'),condition('holding_tribe','DRAGON',op('creation_cost_delta',-3)))),
 'CATA_EVENT_110':definition('setup',start_game=(op('replace_self_with_dependency_family','CATA_EVENT_110','essences',6),op('install_adjacent_essence_combined_casting'))),
 'CORE_WON_145':definition('automatic_play',battlecry=(op('open_random_standard_pack'),op('play_each_pack_card')),required_contracts=('patch_pack_distribution','generated_card_pools')),
 'EDR_818':definition('stored_cards',deathrattle=(op('split_source_into_bound_beetles',{'stats':(1,1)}),),delayed=('next_owner_turn_start',op('reform_source_from_surviving_bound_beetles'))),
 'EDR_895':definition('persistent',battlecry=(op('start_lunar_cycle',3,op('on_full_moon',op('owner_cards_set_cost',1,'game'))),)),
 'FIR_907':definition('location',activate=(op('summon_random',{'type':'MINION','cost':('location_use_level',1)},1),op('armor',('location_use_level',1)),op('draw',('location_use_level',1)),op('refresh_mana',('location_use_level',1)),op('increase_location_use_level',1))),
 'JAIL_319':definition('discover',spell=(op('discover_with_refresh',{'type':'SPELL'},{'per_refresh_damage_probability':0.2,'per_refresh_damage':5,'target':'owner_hero'}),)),
 'JAIL_458':definition('custom_choice',battlecry=(op('choose_elemental_ammunition'),),trigger=('owner_hero_attacks',op('choose_elemental_ammunition'))),
 'JAIL_887':definition('location',activate=(op('choose_hand_card_to_discard'),op('summon_token_by_dependency','JAIL_887','taunt',1)),deathrattle=(op('summon_token_by_dependency','JAIL_887','zuramat',1),)),
 'JAIL_EVENT_100':definition('hidden_choice',battlecry=(op('discover_with_suspicious_option',{'type':'MINION'},op('if_correct_source_buff',1,1)),)),
 'MEND_046':definition('stored_spells',battlecry=(op('add_bound_tokens','MEND_046','treant',3),op('distribute_nature_spell_mana_budget_among_tokens',12))),
 'MEND_100':definition('stored_spells',battlecry=(op('add_bound_token','MEND_100','bulb',{'cost':3,'spell_count':3,'spell_cost':1,'upgrade_each_turn':True}),)),
 'TIME_030':definition('transformation',spell=(op('select_random_hand_minion',op('split_selected_into_two_halves')),)),
 'TIME_041':definition('hidden_choice',battlecry=(op('offer_enemy_hand_guess',3,op('if_correct_source_buff',0,4)),)),
 'TIME_044':definition('timeline',target='minion',spell=(op('buff_target',2,1),op('advance_dependency_to_present','TIME_044'))),
 'TIME_209':definition('fabled',battlecry=(op('bring_dependency_to_source','TIME_209','high_kings_hammer'),),deathrattle=(op('add_dependency_to_hand','TIME_209','high_kings_hammer',1),)),
 'TIME_211':definition('fabled',choose_one=((op('empower_dependency','TIME_211','zin_azshari'),op('destroy_dependency','TIME_211','well_of_eternity')),(op('empower_dependency','TIME_211','well_of_eternity'),op('destroy_dependency','TIME_211','zin_azshari')))),
 'TIME_436':definition('timeline',spell=(op('summon_random',{'type':'MINION','tribe':'DRAGON','minimum_cost':5},1),op('advance_dependency_to_present','TIME_436'))),
 'TIME_609':definition('fabled',battlecry=(op('all_enemy_damage',2),op('repeat_for_previously_played_dependencies','TIME_609',('alleria','vereesa'),op('all_enemy_damage',2)))),
 'TIME_619':definition('fabled',battlecry=(op('draw_or_resurrect_if_died','TIME_619','bwonsamdi'),op('choose_boon_for_result'))),
 'TIME_704':definition('stored_spells',battlecry=(op('add_bound_token','TIME_704','pupil',{'stats':(2,2)}),op('discover',{'type':'SPELL','minimum_cost':7,'era':'past'},op('teach_selected_spell_to_bound_token')))),
 'TIME_810':definition('timeline',spell=(op('damage_random_enemy_minion',5),op('advance_dependency_to_present','TIME_810'))),
 'TIME_850':definition('fabled',deathrattle=(op('summon_from_hand',{'family':'blood_fighter'},op('buff_result',5,5),op('result_attacks_random_enemy')),)),
 'TIME_859':definition('transformation',spell=(op('summon_random_bind',{'type':'MINION','cost':10},'first'),op('summon_random_bind',{'type':'MINION','cost':1},'second'),op('scramble_bound_minion_stats',('first','second')))),
 'TLC_100':definition('custom_creation',battlecry=(condition('starting_deck_distinct_cost_count_at_least',10,op('craft_custom_location')),)),
 'TLC_841':definition('stored_cards',battlecry=(op('replace_each_hand_minion_with_bound_token','TLC_841','jar',{'stats':(0,1),'cost':1,'on_break':'release_stored_minion'}),)),
})

# These recipes cover the printed top-level sequence. They deliberately retain
# unresolved dependency references and symbolic operation arguments. A recipe
# being present does not mean all choices, tokens or runtime rules are defined.

# Integrated in the live Secret registry; historical recipes remain above.
for _integrated in ('JAIL_315','CORE_LOOT_101','TIME_620','CATA_621','DINO_427'):
    DEFINITIONS.pop(_integrated)

# Integrated Shatter family.
for _integrated in ('CATA_134', 'CATA_202', 'CATA_306', 'CATA_479', 'CATA_489', 'CATA_820', 'TIME_101'):
    DEFINITIONS.pop(_integrated)

# Integrated paid-play Rewind cards with closed outcomes.
for _integrated in ('TIME_001', 'TIME_003', 'TIME_004', 'TIME_008', 'TIME_433', 'TIME_441'):
    DEFINITIONS.pop(_integrated)

# Integrated physical Dark Gift consumers and deck-Discover cards.
for _integrated in ('EDR_487', 'EDR_528', 'EDR_654', 'EDR_856', 'FIR_901', 'FIR_922', 'FIR_956'):
    DEFINITIONS.pop(_integrated)

# Integrated Rewind summon with the shared Bonus Effects pool.
DEFINITIONS.pop('TIME_610')

# Integrated repeated combat, spill damage, and attack kill resurrection.
for _integrated in ('CORE_BT_120', 'EDR_453', 'EDR_819'):
    DEFINITIONS.pop(_integrated)

# Enemy healing attacks resolve before the capped heal.
DEFINITIONS.pop('TLC_821')

# Integrated bound summons, set-aside cards and remembered resurrection.
for _integrated in ('CAP_805', 'CAP_806', 'CATA_481', 'CORE_RLK_086', 'EDR_454', 'EDR_818', 'JAIL_852', 'TIME_706', 'TIME_EVENT_998', 'TLC_841'):
    DEFINITIONS.pop(_integrated)

# Integrated attached three-turn discard/summon payload.
DEFINITIONS.pop('CATA_EVENT_001')

# Integrated persistent player effects, defensive auras, and location sleep.
for _integrated in ('CATA_307', 'CATA_591', 'CORE_EDR_003', 'EDR_258', 'EDR_525', 'JAIL_703', 'MEND_044'):
    DEFINITIONS.pop(_integrated)

# Integrated physical entity changes and source-bound cards.
for _integrated in ('CATA_185', 'DINO_414', 'EDR_780', 'EDR_895', 'JAIL_502', 'TLC_241'):
    DEFINITIONS.pop(_integrated)

# Complete existing Underfel family and shared Deathrattle runtime.
DEFINITIONS.pop('TLC_479')

for _integrated in ('MEND_500','MEND_503','MEND_504','MEND_506'):
    DEFINITIONS.pop(_integrated)

for _integrated in ('EDR_000','JAIL_384'):
    DEFINITIONS.pop(_integrated)

# Complete base Companion consumers and supported Holy-history recasting.
for _integrated in ('MEND_304','TLC_430'):
    DEFINITIONS.pop(_integrated)

# Pool-free production paths; independent interaction review remains provisional.
for _integrated in ('CORE_DAL_575','TIME_044','TIME_810'):
    DEFINITIONS.pop(_integrated)

for _integrated in ('JAIL_397','JAIL_430'):
    DEFINITIONS.pop(_integrated)

for _integrated in ('JAIL_421','TIME_618'):
    DEFINITIONS.pop(_integrated)

for _integrated in ('JAIL_330','JAIL_509','JAIL_860'):
    DEFINITIONS.pop(_integrated)

# Closed Blood Fighter family; independent interaction review remains pending.
DEFINITIONS.pop('TIME_850')

for _integrated in ('JAIL_719','TLC_251'):
    DEFINITIONS.pop(_integrated)
