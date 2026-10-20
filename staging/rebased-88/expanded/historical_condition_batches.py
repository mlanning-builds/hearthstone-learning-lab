"""Explicit historical conditional recipes; implementation-only, unvalidated.

Conditions are structured declarations over physical game state. No runtime
rules-text interpretation and no generation pool filtering are used.
"""
from .selectors import has_tribe,has_school,has_class

# cid: (condition, ordinary target restriction, ordered effects)
SPECS={
 'AT_032':(('board_tribe','PIRATE'),'none',[('buff_self',1,1)]),
 'AT_117':(('spell_damage',),'none',[('buff_self',2,2)]),
 'AT_122':(('other_count',4),'character',[('damage',4)]),
 'AV_112':(('held_school','FROST'),'none',[('armor',5)]),
 'AV_125':(('other_count',2),'none',[('buff_self',2,2)]),
 'AV_126':(('enemy_count',2),'none',[('area_damage','enemy_minions',1)]),
 'AV_262':(('held_demon_cost',5),'none',[('buff_self',1,2)]),
 'AV_335':(('secret',),'none',[('buff_self',1,1),('keyword_self','STEALTH')]),
 'BAR_040':(('board_tribe','MURLOC'),'character',[('damage',2)]),
 'UNG_021':(('elemental_previous',),'none',[('add','UNG_018',1)]),
 'BAR_045':(('elemental_previous',),'none',[('keyword_self','RUSH'),('keyword_self','WINDFURY')]),
 'BAR_062':(('board_tribe','MURLOC'),'none',[('buff_self',1,1)]),
 'BAR_743':(('held_school','NATURE'),'none',[('buff_self',0,2)]),
 'BAR_876':(('secret',),'none',[('filtered_draw',(('type','eq','MINION'),),1)]),
 'BAR_916':(('deck_at_most',10),'minion',[('damage',6)]),
 'BOT_296':(('mana_at_least',10),'none',[('buff_self',10,0)]),
 'BOT_550':(('held_spell_cost',5),'none',[('buff_self',1,1)]),
 'BRM_014':(('hand_empty',),'none',[('buff_self',3,3)]),
 'BRM_024':(('enemy_health_at_most',15),'none',[('buff_self',3,3)]),
 'BT_114':(('spell_previous',),'none',[('area_damage','other_minions',2)]),
 'BT_140':(('any_damaged',),'none',[('buff_self',1,1),('keyword_self','RUSH')]),
 'BT_495':(('hero_attacked',),'character',[('damage',4)]),
 'BT_496':(('hero_attacked',),'none',[('buff_self',1,0),('keyword_self','RUSH')]),
 'BT_710':(('friendly_keyword','STEALTH'),'none',[('draw',2)]),
 'CFM_328':(('friendly_health',6),'none',[('draw',2)]),
 'CFM_342':(('weapon_attack',3),'none',[('buff_self',4,4)]),
 'CFM_617':(('friendly_attack',5),'none',[('buff_self',2,2)]),
 'CFM_643':(('weapon',),'none',[('historic_zone_buff','hand_deck',None,2,2)]),
 'CFM_671':(('enemy_frozen',),'none',[('buff_self',2,2)]),
 'CFM_688':(('enemy_keyword','TAUNT'),'none',[('keyword_self','CHARGE')]),
 'CFM_809':(('enemy_hand_at_most',0),'none',[('keyword_self','CHARGE')]),
 'CFM_810':(('enemy_hand_at_least',6),'none',[('keyword_self','CHARGE')]),
 'DAL_086':(('secret',),'none',[('buff_self',1,1)]),
 'DAL_089':(('spell_damage',),'none',[('draw',1)]),
 'DAL_539':(('held_spell_cost',5),'character',[('damage',4)]),
 'DAL_714':(('held_foreign',),'none',[('buff_self',1,1),('keyword_self','RUSH')]),
 'DAL_770':(('mana_at_least',10),'minion',[('damage',10)]),
 'DED_513':(('held_school','SHADOW'),'character',[('damage',2)]),
 'DEEP_034':(('elemental_previous',),'none',[('draw',1)]),
 'DMF_062':(('elemental_previous',),'character',[('damage',3)]),
 'DMF_241':(('deck_no_neutral',),'none',[('keyword_self','RUSH'),('keyword_self','LIFESTEAL'),('keyword_self','TAUNT'),('keyword_self','DIVINE_SHIELD')]),
 'DRG_059':(('board_tribe','MECHANICAL'),'none',[('buff_self',1,1),('keyword_self','RUSH')]),
 'DRG_063':(('enemy_tribe','DRAGON'),'none',[('buff_self',4,4),('keyword_self','RUSH')]),
 'DRG_223':(('overloaded',),'character',[('damage',5)]),
 'ETC_026':(('other_at_most',0),'none',[('filtered_draw',(('type','eq','SPELL'),),1),('filtered_draw',(('type','eq','MINION'),),1),('filtered_draw',(('type','eq','WEAPON'),),1)]),
 'ETC_034':(('other_at_most',0),'none',[('area_damage','enemy_minions',3)]),
 'ETC_035':(('other_at_most',0),'none',[('buff_self',2,2),('keyword_self','RUSH')]),
 'ETC_101':(('other_at_most',0),'character',[('damage',2)]),
 'GIL_130':(('deck_parity',1),'none',[('buff_self',2,2)]),
 'GIL_530':(('deck_parity',0),'character',[('damage',2)]),
 'GIL_565':(('hero_hurt',),'none',[('keyword_self','LIFESTEAL')]),
 'GIL_624':(('only_minion',),'none',[('buff_self',3,3)]),
 'GIL_645':(('elemental_previous',),'none',[('draw',1)]),
 'GIL_838':(('deck_parity',1),'none',[('draw',1)]),
 'GIL_905':(('death_this_turn',),'none',[('keyword_self','POISONOUS')]),
 'GVG_004':(('board_tribe','MECHANICAL'),'none',[('missiles','enemies',6)]),
 'ICC_252':(('enemy_frozen',),'none',[('draw',1)]),
 'ICC_851':(('deck_no_cost',2),'none',[('historic_zone_buff','deck',None,1,1)]),
 'ICC_853':(('deck_no_cost',4),'none',[('keyword_self','LIFESTEAL'),('keyword_self','TAUNT')]),
 'KAR_037':(('secret',),'none',[('buff_self',1,1),('keyword_self','TAUNT')]),
 'KAR_092':(('secret',),'character',[('damage',3)]),
 'LOE_073':(('board_tribe','BEAST'),'none',[('keyword_self','TAUNT')]),
 'LOE_116':(('other_count',6),'none',[('buff_self',4,4)]),
 'LOOT_018':(('hero_health_at_most',15),'none',[('buff_self',3,3),('keyword_self','TAUNT')]),
 'LOOT_124':(('other_at_most',0),'none',[('keyword_self','TAUNT'),('keyword_self','DIVINE_SHIELD')]),
 'MAW_028':(('armor_at_least',4),'none',[('buff_self',4,4)]),
 'MIS_712':(('mana_at_least',10),'none',[('buff_self',7,7)]),
 'OG_315':(('board_tribe','PIRATE'),'none',[('weapon_buff',1,1)]),
 'ONY_026':(('held_holy_shadow',),'none',[('area_damage','other_minions',3)]),
 'SCH_283':(('power_used',),'none',[('draw',1)]),
 'SW_071':(('hero_health_at_most',15),'none',[('buff_self',2,4),('keyword_self','TAUNT')]),
 'SW_444':(('any_hero_hurt',),'none',[('filtered_draw',(('type','eq','SPELL'),('school','eq','SHADOW')),1)]),
 'SW_451':(('fel_this_turn',),'none',[('buff_self',2,2)]),
 'TOY_891':(('location',),'none',[('draw',2)]),
 'TRL_311':(('elemental_previous',),'none',[('area_damage','other_minions',3)]),
 'TRL_514':(('enemy_count',2),'none',[('buff_self',1,0)]),
 'TRL_522':(('spells_this_turn',2),'character',[('damage',2)]),
 'TRL_533':(('friendly_frozen',),'none',[('armor',8)]),
 'TSC_060':(('held_school','HOLY'),'none',[('keyword_self','TAUNT'),('keyword_self','DIVINE_SHIELD')]),
 'TSC_610':(('hero_attacked',),'none',[('area_damage','enemies',2)]),
 'TTN_080':(('friendly_attack',4),'none',[('buff_self',2,2)]),
 'ULD_157':(('quest',),'none',[('draw',1)]),
 'ULD_293':(('secret',),'character',[('damage',6)]),
 'UNG_070':(('elemental_previous',),'none',[('keyword_self','TAUNT'),('keyword_self','DIVINE_SHIELD')]),
 'UNG_801':(('other_count',2),'none',[('keyword_self','TAUNT')]),
 'UNG_847':(('elemental_previous',),'character',[('damage',5)]),
 'WC_024':(('weapon',),'none',[('buff_self',1,1)]),
 'WON_035':(('board_tribe','MECHANICAL'),'none',[('missiles','enemies',6)]),
 'WON_117':(('weapon',),'none',[('historic_zone_buff','hand_deck',None,2,2)]),
 'WW_906':(('held_cost',4),'character',[('damage',4)]),
 'YOD_040':(('held_spell_cost',5),'none',[('armor',5)]),
 'YOG_527':(('board_tribe','MECHANICAL'),'character',[('damage',4)]),
 'YOP_014':(('armor_at_least',1),'none',[('buff_self',2,2)]),
}
SPECS.update({
 'AV_711':(('held_foreign',),'none',[('copy_self_right',1)]),
 'BAR_846':(('hero_attacked',),'none',[('copy_self_right',1)]),
 'BOT_216':(('mana_at_least',10),'none',[('heal_own_hero',10)]),
 'BOT_536':(('mana_at_least',10),'none',[('copy_self_right',2)]),
 'DMF_106':(('secret',),'none',[('copy_self_right',1)]),
 'NX2_027':(('armor_at_least',5),'none',[('copy_self_right',1)]),
 'SCH_530':(('spell_damage',),'none',[('copy_self_right',1)]),
 'VAC_521':(('held_spell_cost',5),'none',[('copy_self_right',1)]),
 'WON_052':(('source_attack',5),'none',[('copy_self_right',1)]),
 'WORK_032':(('hero_hurt',),'none',[('copy_self_right',1)]),
 'YOD_007':(('elemental_previous',),'none',[('copy_self_right',1)]),
 'YOD_030':(('quest',),'none',[('add','TOKEN_COIN',1)]),
 'NX2_010':(('mana_at_least',11),'none',[('buff_self',4,4),('keyword_self','CHARGE')]),
 'NX2_051':(('mana_at_least',6),'none',[('keyword_self','REBORN')]),
 'RLK_518':(('mana_at_least',8),'none',[('buff_self',2,2),('keyword_self','DIVINE_SHIELD')]),
 'RLK_955':(('mana_at_least',7),'none',[('buff_self',2,2)]),
})
# Full random-Beast request; no substitution with a supported subset.
from .generation_cards import pool,random_cards
SPECS['AT_010']=(('board_tribe','BEAST'),'none',[random_cards(pool(card_type='MINION',tribe='BEAST'),destination='board')])

from .generation_cards import discover
SPECS.update({
 'BT_115':(('spell_previous',),'none',[discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'GVG_123':(('board_tribe','MECHANICAL'),'none',[random_cards(pool(card_type='SPELL',school='FIRE'))]),
 'WON_033':(('board_tribe','MECHANICAL'),'none',[random_cards(pool(card_type='SPELL',school='FIRE'))]),
 'WW_428':(('elemental_previous',),'none',[discover(pool(era='past',card_type='MINION',tribe='ELEMENTAL',classes='any'))]),
 'WW_901':(('held_cost',2),'none',[('add','TOKEN_COIN',1)]),
 'WW_433':(('held_cost',3),'none',[random_cards(pool(card_type='MINION',minimum=3,maximum=3),destination='board')]),
})
SPECS.update({
 'DRG_322':(('held_dragon',),'none',[('next_cost_set','SPELL',0,'turn')]),
 'ULD_137':(('held_spell_cost',5),'none',[('summon','EX1_158t',2)]),
 'ETC_029':(('other_at_most',0),'none',[('summon','ETC_029t',2)]),
 'BOT_552':(('exact_health_count',7,3),'none',[('area_damage','enemies',7)]),
 'BT_307':(('hero_hurt',),'none',[('refresh_mana',3)]),
})
SPECS.update({
 'TRL_349':(('weapon',),'none',[discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'TRL_523':(('held_dragon',),'none',[discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'UNG_937':(('board_tribe','MURLOC'),'none',[discover(pool(card_type='MINION',tribe='MURLOC',classes='own_or_neutral'))]),
 'DRG_072':(('held_dragon',),'none',[random_cards(pool(card_type='MINION',tribe='MURLOC'),2,'board')]),
 'ULD_154':(('secret',),'none',[('summon','ULD_154t',2)]),
 'ULD_156':(('deck_unique',),'none',[('summon','EX1_543',1)]),
 'ULD_139':(('deck_unique',),'none',[('historical_mutation_copy_whole_hand',)]),
 'ULD_170':(('lackey_board',),'character',[('damage',3)]),
 'BAR_848':(('elemental_previous',),'enemy_minion',[('transform','hexfrog')]),
 'BT_711':(('secret',),'minion',[('historical_mutation_bounce_delta',2)]),
 'DRG_231':(('deck_no_neutral',),'none',[random_cards(pool(classes='PALADIN'),5)]),
 'DRG_232':(('deck_no_neutral',),'none',[('equip','CS2_097')]),
 'ETC_358':(('other_at_most',0),'none',[('add','ETC_358',1)]),
 'ETC_742':(('last_cost',1),'none',[('buff_self',1,1)]),
 'GIL_508':(('hero_hurt',),'none',[('summon','GIL_508t',2)]),
 'MAW_017':(('deck_no_neutral',),'minion',[('set_target_stats',1,1)]),
 'NX2_003':(('spell_previous',),'none',[discover(pool(card_type='MINION',tribe='ELEMENTAL',classes='own_or_neutral'))]),
 'NX2_007':(('elemental_previous',),'none',[('summon','NX2_007t',3)]),
 'REV_900':(('secret',),'none',[('copy_self_right',1)]),
 'SCH_513':(('hero_health_changed',),'minion',[('destroy',)]),
 'SCH_613':(('held_spell_cost',5),'character',[('heal',5)]),
 'SW_400':(('quest',),'none',[discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'ULD_238':(('deck_unique',),'none',[('missiles','enemy_minions',10)]),
 'CFM_687':(('deck_unique',),'none',[('next_cost_set','SPELL',0,'turn')]),
 'CFM_750':(('deck_unique',),'none',[('historical_mutation_recruit_demons',)]),
 'WON_324':(('deck_unique',),'none',[('historical_mutation_recruit_demons',)]),
 'DAL_554':(('deck_at_most',0),'none',[('summon','DAL_554t',6)]),
 'LOE_011':(('deck_unique',),'none',[('historical_mutation_full_hero_heal',)]),
 'YOD_038':(('quest_played',),'none',[('summon','YOD_038t',1)]),
 'UNG_208':(('elemental_previous',),'none',[('summon','UNG_208t',2)]),
 'UNG_816':(('elemental_previous',),'none',[discover(pool(card_type='MINION',tribe='ELEMENTAL',classes='own_or_neutral'))]),
 'YOG_411':(('spells_cast_game',5),'none',[('area_damage','enemies',2)]),
 'YOG_518':(('spells_cast_game',5),'none',[('draw',2)]),
 'YOG_521':(('spells_cast_game',5),'none',[('hero_attack',4)]),
 'YOG_528':(('spells_cast_game',5),'none',[('refresh_mana',4)]),
 'YOG_519':(('elemental_previous',),'none',[('missiles','enemies',7)]),
 'TSC_646':(('board_tribe','MECHANICAL'),'none',[('summon','TSC_646t',2)]),
 'TSC_917':(('weapon',),'none',[('summon','TSC_917t',1)]),
})
SPECS.update({
 'UNG_009':(('other_count',2),'none',[('historical_upgrade_adapt','self')]),
 'UNG_082':(('elemental_previous',),'none',[('historical_upgrade_adapt','self')]),
 'UNG_109':(('held_attack',5),'none',[('historical_upgrade_adapt','self')]),
})
# Physical held-spell counters are maintained at the completed spell event.
SPECS.update({
 'TSC_017':(('held_casts',1),'character',[('damage',3)]),
 'TSC_064':(('held_casts',3),'none',[('area_damage','enemies',3)]),
 'TSC_071':(('held_casts',1),'none',[('next_spells_twice',1)]),
 'TSC_212':(('held_casts',3),'none',[('draw',3)]),
 'TSC_609':(('held_casts',3),'none',[('copy_self_right',2)]),
 'TSC_643':(('held_casts',1),'none',[discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'TSC_826':(('held_casts',1),'none',[('filtered_draw',(('type','eq','MINION'),('tribe','eq','NAGA')),1)]),
 'TID_706':(('held_school_cast','FEL'),'none',[('keyword_self','RUSH')]),
 'NX2_035':(('held_casts',3),'none',[('historical_batch_sample_freeze','enemy',3)]),
 'WW_407':(('held_casts',1),'none',[('hero_attack',3)]),
 'TOY_341':(('held_higher_cost',),'character',[('damage',4)]),
 'TOY_341t':(('held_higher_cost',),'character',[('damage',4)]),
})

from .historical_play_batches import zone_offer
SPECS.update({
 'CFM_605':(('held_dragon',),'none',[zone_offer('enemy','deck',(),'copy')]),
 'YOD_013':(('held_dragon',),'none',[zone_offer('own','deck',(('type','eq','SPELL'),),'draw')]),
 'WC_803':(('restored_this_turn',),'none',[zone_offer('own','deck',(('type','eq','SPELL'),),'draw')]),
 'ETC_359':(('overloaded',),'none',[zone_offer('own','deck',(('type','eq','SPELL'),),'draw')]),
 'TOY_054':(('held_casts',1),'none',[zone_offer('own','deck',(),'draw')]),
 'REV_959':(('secret',),'none',[zone_offer('enemy','hand',(),'shuffle',0,False)]),
})
SPECS['REV_901']=(('location',),'none',[zone_offer('own','deck',(),'copy')])
SPECS.update({
 'TID_002':(('held_school_cast','NATURE'),'none',[('buff_others',1,1)]),
 'TID_074':(('held_casts',3),'character',[('damage',5)]),
 'TID_085':(('held_school_cast','HOLY'),'none',[('area_heal',6)]),
 'TID_717':(('held_school_cast','SHADOW'),'minion',[('historical_copy_steal_target_health',2)]),
})
SPECS.update({
 'RLK_123':(('undead_since_last_turn',),'character',[('damage',2)]),
 'RLK_529':(('undead_since_last_turn',),'minion',[('damage',1)]),
 'RLK_552':(('undead_since_last_turn',),'none',[('summon','RLK_909t',2)]),
 'RLK_956':(('undead_since_last_turn',),'none',[('summon','RLK_956t',1)]),
})
RULES={cid:('historic_batch_target' if mode!='none' else 'none',
 [('historic_when',condition,tuple(ops))]) for cid,(condition,mode,ops) in SPECS.items()}
TOKEN_RULES={cid:('none',[]) for cid in ('ETC_029t','ULD_154t','hexfrog','CS2_097','GIL_508t','NX2_007t','DAL_554t','YOD_038t','UNG_208t','TSC_646t','TSC_917t')}
WEAPON_TRIGGERS={'CS2_097':[('heal_own_hero',3)]}
TOKEN_RULES.update({'RLK_909t':('none',[]),'RLK_956t':('none',[])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'TOY_341t'}
GENERATED_IDS=frozenset(RULES)-{'TOY_341t'}
SPELL_DAMAGE_VALUES={'ETC_029t':1,'GIL_838':1,'GVG_123':1,'WON_033':1}


def matches(game,condition,ctx):
 owner=ctx['owner'];source=ctx.get('source');p=game.players[owner];q=game.players[1-owner]
 own=[m for m in p.minions if m is not source and m.health>0]
 enemy=[m for m in q.minions if m.health>0]
 hand=[c for c in p.hand if c is not ctx.get('physical_card')]
 kind=condition[0];n=condition[1] if len(condition)>1 else None
 state=getattr(ctx.get('physical_card'),'rule_state',{})
 if kind=='held_casts':return state.get('historical_held_casts',0)>=n
 if kind=='held_school_cast':return n in state.get('historical_held_schools',())
 if kind=='held_higher_cost':return bool(state.get('historical_held_higher_cost'))
 if kind=='undead_since_last_turn':return any(record['turn']>p.last_turn_ended and has_tribe(game._card_data(record['entity']),'UNDEAD') for record in p.death_records)
 if kind=='deck_unique':
  from .identities import canonical_identity
  values=[canonical_identity(game._card_data(c),game.cards) for c in p.deck]
  return len(values)==len(set(values))
 if kind=='lackey_board':
  from .historical_family_batches import LACKEYS
  return any(m.card_id in LACKEYS for m in own)
 if kind=='last_cost':return len(p.played_history)>=2 and p.played_history[-2]['cost']==n
 if kind=='hero_health_changed':return p.hero_health_changed_turn
 if kind=='restored_this_turn':return p.healing_done_turn>0
 if kind=='quest_played':return p.quests_played>0
 if kind=='spells_cast_game':return getattr(p,'historical_spells_cast',0)>=n
 if kind=='held_attack':return any(game._card_data(c)['type']=='MINION' and game._card_stat(c,'attack',owner)>=n for c in hand)
 if kind=='held_dragon':return any(has_tribe(game._card_data(c),'DRAGON') for c in hand)
 if kind=='exact_health_count':return sum(m.health==n for m in p.minions)>=condition[2]
 if kind=='source_attack':return source is not None and source.attack>=n
 if kind=='board_tribe':return any(has_tribe(game._card_data(m),n) for m in own)
 if kind=='enemy_tribe':return any(has_tribe(game._card_data(m),n) for m in enemy)
 if kind=='spell_damage':return game._spell_damage(owner)>0
 if kind=='other_count':return len(own)>=n
 if kind=='other_at_most':return len(own)<=n
 if kind=='enemy_count':return len(enemy)>=n
 if kind=='held_school':return any(game._card_data(c)['type']=='SPELL' and has_school(game._card_data(c),n) for c in hand)
 if kind=='held_holy_shadow':return all(any(game._card_data(c)['type']=='SPELL' and has_school(game._card_data(c),school) for c in hand) for school in ('HOLY','SHADOW'))
 if kind=='held_demon_cost':return any(game._card_data(c)['type']=='MINION' and has_tribe(game._card_data(c),'DEMON') and game._cost(c,owner)>=n for c in hand)
 if kind=='held_spell_cost':return any(game._card_data(c)['type']=='SPELL' and game._cost(c,owner)>=n for c in hand)
 if kind=='held_cost':return any(game._cost(c,owner)==n for c in hand)
 if kind=='held_foreign':return any(not has_class(game._card_data(c),p.hero_class) and not has_class(game._card_data(c),'NEUTRAL') for c in hand)
 if kind=='secret':return bool(p.secrets)
 if kind=='elemental_previous':return bool({'ELEMENTAL','ALL'} & p.previous_tribes)
 if kind=='spell_previous':return bool(p.spells_previous)
 if kind=='deck_at_most':return len(p.deck)<=n
 if kind=='mana_at_least':return p.max_mana>=n
 if kind=='hand_empty':return not hand
 if kind=='enemy_health_at_most':return q.health<=n
 if kind=='hero_health_at_most':return p.health<=n
 if kind=='any_damaged':return any(m.health<m.max_health for m in own+enemy)
 if kind=='hero_attacked':return p.hero_attacks>0
 if kind=='friendly_keyword':return any(n in game._effective_keywords(m) for m in own)
 if kind=='enemy_keyword':return any(n in game._effective_keywords(m) for m in enemy)
 if kind=='friendly_health':return any(m.health>=n for m in own)
 if kind=='friendly_attack':return any(m.attack>=n for m in own)
 if kind=='weapon_attack':return bool(p.weapon and p.weapon['attack']>=n)
 if kind=='weapon':return bool(p.weapon)
 if kind=='enemy_frozen':return q.frozen_until>=0 or any(m.frozen_until>=0 for m in enemy)
 if kind=='friendly_frozen':return p.frozen_until>=0 or any(m.frozen_until>=0 for m in own)
 if kind=='enemy_hand_at_most':return len(q.hand)<=n
 if kind=='enemy_hand_at_least':return len(q.hand)>=n
 if kind=='deck_no_neutral':return not any(has_class(game._card_data(c),'NEUTRAL') for c in p.deck)
 if kind=='overloaded':return p.overload_next>0 or p.locked_mana>0
 if kind=='deck_parity':return all(game._card_stat(c,'cost',owner)%2==n for c in p.deck)
 if kind=='deck_no_cost':return all(game._card_stat(c,'cost',owner)!=n for c in p.deck)
 if kind=='hero_hurt':return p.hero_damage_taken_turn>0
 if kind=='any_hero_hurt':return any(player.hero_damage_taken_turn>0 for player in game.players)
 if kind=='only_minion':return not own and not enemy
 if kind=='death_this_turn':return any(player.minions_died_turn>0 for player in game.players)
 if kind=='armor_at_least':return p.armor>=n
 if kind=='power_used':return p.power_used
 if kind=='fel_this_turn':return 'FEL' in p.played_schools
 if kind=='location':return bool(p.locations)
 if kind=='spells_this_turn':return len(p.spells_turn)>=n
 if kind=='quest':return bool(p.quest)
 raise ValueError('Unknown explicit historical condition: '+str(condition))


def targets(game,cid,owner,mode):
 if mode!='historic_batch_target':return None
 condition,ordinary,_=SPECS[cid]
 if not matches(game,condition,dict(owner=owner)):return [0]
 return game._targets_for(cid,owner,ordinary)


def split(game,op,ctx):
 if op[0]!='historic_when':return None
 ops=op[2] if matches(game,op[1],ctx) else ()
 if not ops:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(ops[0],ctx)
 return first,tuple(tail)+tuple(ops[1:])


def execute(game,op,ctx):
 if op[0]!='historic_when':return False
 if matches(game,op[1],ctx):
  for child in op[2]:game._effect(child,ctx)
 return True


def physical_targets(game,card,owner,current):
 spec=SPECS.get(card.card_id)
 if spec is None or spec[0][0] not in ('held_casts','held_school_cast','held_higher_cost'):return current
 return game._targets_for(card.card_id,owner,spec[1]) if matches(game,spec[0],dict(owner=owner,physical_card=card)) else [0]


def record_held_spell(game,data):
 owner=data['owner'];raw=game.cards[data['card_id']]
 schools=set(raw.get('spellSchools',()))
 if raw.get('spellSchool'):schools.add(raw['spellSchool'])
 for card in tuple(game.players[owner].hand):
  if card.card_id in ('TSC_087','TSC_658','VAC_304'):
   from copy import deepcopy
   memory=getattr(card,'_historical_held_spell_memory',[])
   if card.card_id=='TSC_658' or len(memory)<3:
    memory.append(dict(card=deepcopy(data['physical_card']),cost=data.get('cost',raw['cost'])))
   card._historical_held_spell_memory=memory
  state=game._b60_state(card)
  state['historical_held_casts']=state.get('historical_held_casts',0)+1
  state['historical_held_schools']=sorted(set(state.get('historical_held_schools',()))|schools)


def record_held_play(game,owner,paid):
 for card in tuple(game.players[owner].hand):
  if paid>game._cost(card,owner):game._b60_state(card)['historical_held_higher_cost']=True
