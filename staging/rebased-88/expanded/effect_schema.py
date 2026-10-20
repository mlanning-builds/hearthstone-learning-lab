"""Structural validation for declarative effects, independent of support claims.

Known operand schemas are strict. Uncovered operation names are reported and
may be rejected with strict_unknown=True. A structural pass never certifies
that an operation has an executable handler or correct card semantics.
"""
from collections.abc import Mapping
from .selectors import TRIBES, CARD_TYPES, SCHOOLS
from dataclasses import dataclass,field

class EffectSchemaError(ValueError):pass
@dataclass
class ValidationReport:
 operations:int=0
 uncovered:set=field(default_factory=set)

# bool is deliberately excluded from integer operands.
def _integer(value):return type(value) is int
def _text(value):return isinstance(value,str) and bool(value)
def _seq(value):return isinstance(value,(tuple,list))
def _boolean(value):return type(value) is bool
def _optional_text(value):return value is None or _text(value)
def _one_of(*values):return lambda value: _text(value) and value in values
def _filters(value):
 if not _seq(value):return False
 for clause in value:
  if not _seq(clause) or len(clause)!=3:return False
  key,relation,wanted=clause
  if key in ('attack','health','cost'):
   if relation not in ('eq','ge','le') or not _integer(wanted):return False
  elif key=='id':
   if relation!='in' or not isinstance(wanted,tuple) or not wanted or not all(_text(cid) for cid in wanted):return False
  elif key in ('tribe','mechanic','type','school'):
   if relation!='eq' or not _text(wanted):return False
   pool={'tribe':TRIBES,'type':CARD_TYPES,'school':SCHOOLS}.get(key)
   if pool is not None and wanted not in pool:return False
  else:return False
 return True
def _choice_effects(value):
 return (_seq(value) and bool(value) and all(_seq(row) and len(row)==2
         and _text(row[0]) and _seq(row[1]) and bool(row[1]) for row in value))
SCHEMAS={}
for name in ('damage','heal','heal_own_hero','damage_own_hero','damage_enemy_hero','armor','draw','discard','hero_attack','temporary_mana','refresh_mana','set_others_attack','set_others_health','spell_damage_self'):
 SCHEMAS[name]=(_integer,)
for name in ('buff','buff_self','board_buff','hand_buff','weapon_buff','set_target_stats'):
 SCHEMAS[name]=(_integer,_integer)
for name in ('keyword','keyword_self','board_keyword','transform','add_fixed'):
 SCHEMAS[name]=(_text,)
for name in ('destroy','freeze','silence','bounce','heal_full','destroy_all_minions','hero_divine_shield','board_expire','batch30_noop'):
 SCHEMAS[name]=()
SCHEMAS.update(summon=(_text,_integer),add=(_text,_integer),area_damage=(_text,_integer),missiles=(_text,_integer,_integer),schedule_turn_effect=(_text,_integer,_integer,_seq))

# Primitive contracts checked against their explicit executable handlers.
for name in ('combo_damage','permanent_healing_bonus','repeat_end_effects','draw_empty','outcast_draw','area_heal','damage_self','damage_random_enemy_minion','destroy_small','destroy_large','other_murloc_health','beast_weapon_durability'):
 SCHEMAS[name]=(_integer,)
for name in ('taunt_hand_buff','shadow_hand_buff'):
 SCHEMAS[name]=(_integer,_integer)
for name in ('combo_summon','raise_corpses','death_summon'):
 SCHEMAS[name]=(_text,_integer)
for name in ('draw_tribe','tomb_guardians'):
 SCHEMAS[name]=(_text,)
for name in ('draw_both','draw_unspent_mana','freeze_enemies','freeze_self','double_self_attack','double_self_health','reverse_deck','health_one','buff_board_count','damage_armor','grave_strength','blood_tap','asphyxiate','self_hand_health','self_enemy_hand_health','self_weapon_attack','adjacent_taunt','remove_enemy_top','random_shield_taunt','destroy_random_enemy','kindred_twice_next'):
 SCHEMAS[name]=()
SCHEMAS.update(draw_until=(_integer,),buff_random_other=(_integer,_integer),damage_draw_if_dead=(_integer,),damage_draw_if_alive=(_integer,),when_state=(_text,_seq),if_state=(_text,_seq))

# Reviewed family handlers: held_upgrades, temporary, bonus_effects and
# historical conditional/hand/removal/scaling modules. No runtime text parsing.
for name in ('held_ramp','held_whelps','held_draw','held_buff','held_area','held_cleave','held_picklock','temporary_deck_discover','temporary_control','bonus_played','bonus_pass_deathrattle','bonus_steal','historical_remove_armor','historical_destroy_damaged','historical_weapon_armor','historical_weapon_draw','historical_combo_scaled_draw','historical_bounce_target','historical_swap_source_attack','destroy_enemy_weapon','draw_kindred_pair','barnabus_draw','historical_security_draw'):
 SCHEMAS[name]=()
for name in ('temporary_next_discount','bonus_target','historical_destroy_crystals_both','historical_temporary_self_attack','historical_combo_scaled_buff','historical_combo_scaled_damage','historical_heroes_heal','historical_heroes_damage','destroy_crystals','draw_bottom','draw_distinct_costs','draw_if_cheap','opponent_draw_copy'):
 SCHEMAS[name]=(_integer,)
SCHEMAS['inherited_deathrattle']=(_integer,_text)
SCHEMAS['inherited_death_atomic']=(_integer,_text)
SCHEMAS['full_health_buff']=(_integer,_integer)
SCHEMAS['inherit_friendly_deathrattle']=()
SCHEMAS['combo_buff']=(_integer,_integer)
SCHEMAS.update(held_tick=(_integer,_text),follow_attach=(_text,),bonus_summon=(_text,),
 historical_if_combo=(_seq,),if_holding=(_filters,_seq),filtered_draw=(_filters,_integer),
 historical_hand_buff=(_optional_text,_optional_text,_integer,_integer,_boolean),
 historical_self_scale=(_one_of('totems','hero_damage','hand_spells','other_friendly','enemy_hand','hand','other_hand','enemy_deathrattle','damaged','deaths','frost_hand','other_pirates','spells_cast'),_integer,_integer),
 empty_crystals=(_one_of('friendly','enemy','both'),_integer),
 draw_type_keyword=(_integer,_one_of(*CARD_TYPES),_text),draw_minions_mana_buff=(_integer,_integer,_integer,_integer))


def _pool_request(value):
 from .generation_cards import PoolRequest
 return isinstance(value,PoolRequest)

def _gift_request(value):
 from .dark_gift_generators import GiftRequest
 return (isinstance(value,GiftRequest) and type(value.historical) is bool
         and isinstance(value.alternatives,tuple) and bool(value.alternatives)
         and all(_pool_request(request) for request in value.alternatives))

def _gift_modifiers(value):
 if not _seq(value):return False
 seen=set()
 for row in value:
  if not _seq(row) or len(row)!=2 or not _text(row[0]) or row[0] in seen:return False
  name,item=row;seen.add(name)
  if name in ('corpse_cost','cost_delta'):
   if not _integer(item) or (name=='corpse_cost' and item<0):return False
  elif name in ('shuffle_unchosen','copy_selected'):
   if not _boolean(item):return False
  else:return False
 return True

def _generation_modifiers(value):
 if not _seq(value):return False
 numeric={'attack','health','combo_attack','set_cost','cost_delta','combo_cost_delta','duration_delta','growing_discount','dormant_turns','turn_cost_delta'}
 boolean={'double_stats','freeze','heal_cost','shuffle_unchosen','temporary','trigger_deathrattle','prepare','repeat_spell','choose_both','locked_until_play'}
 seen=set()
 for row in value:
  if not _seq(row) or len(row)!=2 or not _text(row[0]) or row[0] in seen:return False
  name,item=row;seen.add(name)
  if name in numeric:
   if not _integer(item):return False
  elif name in boolean:
   if not _boolean(item):return False
  elif name=='keywords':
   if not _seq(item) or any(not _text(keyword) for keyword in item):return False
  elif name in ('keyword','follow'):
   if not _text(item):return False
  elif name=='health_payment':
   if item not in ('turn','permanent'):return False
  elif name=='stats':
   if not _seq(item) or len(item)!=2 or not all(_integer(v) for v in item):return False
  else:return False
 return True

SCHEMAS.update(gain_corpses=(_integer,),draw_school=(_one_of(*SCHOOLS),),
 copy_self_right=(_integer,),kindred=(_seq,),
 generate_random=(_pool_request,_integer,_one_of('hand','board','deck','enemy_top','bottom','nellie_crew'),_generation_modifiers),
 generate_discover=(_pool_request,_one_of('hand','board','deck','enemy_top','bottom','nellie_crew'),_generation_modifiers))

# Explicit Beast-component handlers: validate conditional children recursively.
SCHEMAS.update(add_opponent=(_text,_integer),damage_enemy_heal_own=(_integer,_integer),
 discard_entire_hand=(),prevent_enemy_hero_healing_until_next_turn=(),
 source_attack_damage=(),generation_if_other_tribe=(_one_of(*TRIBES),_seq),
 attack_missiles=(),b60_draw_remember=(),b60_discard_remembered=(),force_cheap_attacks=(),
 fill_hand=(_text,),choose_self_effect=(_choice_effects,),grant_death_self=(_seq,),
 temporary_keyword_self=(_text,_one_of('next_start','end')))

SCHEMAS.update(dark_global_discover=(_gift_request,_gift_modifiers),rewindgen_gift=(),suspicious_discover=())

OP_TABLES=frozenset(('DISCARD_EFFECTS','SINGLE_PLAY_EFFECTS','DEATH_EFFECTS','END_EFFECTS','END_EVERY_EFFECTS','WEAPON_TRIGGERS','LOCATION_EFFECTS','CAST_EFFECTS','TOKEN_CAST_EFFECTS','FRENZY','SPELLBURST','OVERHEAL','HONORABLE','OVERKILL'))
RULE_TABLES=frozenset(('RULES','TOKEN_RULES'))
PAIRED_TABLES=frozenset(('TRIGGERS','START_EFFECTS'))

def _fail(path,message):raise EffectSchemaError(path+': '+message)
def _text_at(value,path):
 if not _text(value):_fail(path,'expected nonempty string')
def validate_operation(op,path='operation',report=None,strict_unknown=False):
 report=report if report is not None else ValidationReport()
 if not _seq(op) or not op:_fail(path,'expected nonempty operation tuple/list')
 _text_at(op[0],path+'[0]');name=op[0];report.operations+=1
 schema=SCHEMAS.get(name)
 if name=='generation_dynamic_summon' and len(op)==3:schema=(_one_of('corpses_up_to'),_integer)
 if name=='insert_fixed' and len(op)==5:schema=(_text,_integer,_one_of('shuffle','bottom'),_integer)
 if name=='summon_from_zone' and len(op)==4:schema=(_one_of('hand','deck'),_filters,_text)
 if name=='filtered_draw' and len(op)==4:schema=(_filters,_integer,_integer)
 if name=='if_holding' and len(op)==4:schema=(_filters,_seq,_seq)
 if name=='destroy_random_enemy' and len(op)==2:schema=(_integer,)
 if name=='missiles' and len(op)==3:schema=(_text,_integer)
 if name=='weapon_buff' and len(op)==2:schema=(_integer,)
 if name=='freeze' and len(op)==2:schema=(lambda value:type(value) is bool,)
 if name=='death_summon' and len(op)==4:schema=(_text,_integer,_integer)
 if name=='buff_random_other' and len(op)==4:schema=(_integer,_integer,_text)
 if name in ('damage_draw_if_dead','damage_draw_if_alive') and len(op)==3:schema=(_integer,_integer)
 if schema is None:
  from .operand_catalog import accepts as catalog_accepts
  accepted=catalog_accepts(name,op[1:])
  if accepted is False:_fail(path,'invalid '+name+' operand types, selector or count')
  if accepted is None:
   report.uncovered.add(name)
   if strict_unknown:_fail(path,'uncovered operation '+name)
 else:
  if len(op)!=len(schema)+1:_fail(path,'invalid '+name+' operand count')
  for index,(predicate,value) in enumerate(zip(schema,op[1:]),1):
   if not predicate(value):_fail(path+'['+str(index)+']','invalid '+name+' operand type')
 # Only explicit operation-bearing positions are descended into. Strings such
 # as target modes, selectors, IDs, and event conditions are never operations.
 if name=='choose_self_effect':
  for index,row in enumerate(op[1]):validate_operation(row[1],path+'[1]['+str(index)+'][1]',report,strict_unknown)
 if name in ('grant_death_self','grant_death_target','historical_batch_grant_other_deaths'):validate_operations(op[1],path+'[1]',report,strict_unknown)
 if name=='historical_batch_joust':validate_operations(op[3],path+'[3]',report,strict_unknown)
 if name=='historical_batch_mana_branch':
  validate_operations(op[2],path+'[2]',report,strict_unknown);validate_operations(op[3],path+'[3]',report,strict_unknown)
 if name=='historical_play_finale':validate_operations(op[1],path+'[1]',report,strict_unknown)
 if name in ('historical_damage_then','historical_damage_follow'):validate_operations(op[3],path+'[3]',report,strict_unknown)
 if name=='historic_when':validate_operations(op[2],path+'[2]',report,strict_unknown)
 if name=='generation_if_other_tribe':validate_operation(op[2],path+'[2]',report,strict_unknown)
 if name=='kindred':validate_operations(op[1],path+'[1]',report,strict_unknown)
 if name=='schedule_turn_effect':validate_operations(op[4],path+'[4]',report,strict_unknown)
 if name=='historical_summoning_naga_follow':validate_operation(op[1],path+'[1]',report,strict_unknown)
 if name in ('when_state','if_state','historical_if_combo','outcast_operation'):
  validate_operation(op[-1],path+'[-1]',report,strict_unknown)
 if name=='if_holding':
  for index in range(2,len(op)):
   validate_operation(op[index],path+'['+str(index)+']',report,strict_unknown)
 return report

def validate_operations(ops,path='operations',report=None,strict_unknown=False):
 report=report if report is not None else ValidationReport()
 if not _seq(ops):_fail(path,'expected ordered operation tuple/list')
 for i,op in enumerate(ops):validate_operation(op,f'{path}[{i}]',report,strict_unknown)
 return report

def validate_rule(rule,path='rule',report=None,strict_unknown=False):
 report=report if report is not None else ValidationReport()
 if not _seq(rule) or len(rule)!=2:_fail(path,'expected (target mode, operations)')
 _text_at(rule[0],path+'[0]')
 return validate_operations(rule[1],path+'[1]',report,strict_unknown)

def validate_table(name,table,strict_unknown=False):
 if not isinstance(table,Mapping):_fail(name,'expected mapping')
 report=ValidationReport()
 for cid,value in table.items():
  _text_at(cid,name+'.key');path=name+'['+repr(cid)+']'
  if name in RULE_TABLES:validate_rule(value,path,report,strict_unknown)
  elif name in OP_TABLES:validate_operations(value,path,report,strict_unknown)
  elif name in PAIRED_TABLES:
   if not _seq(value) or len(value)!=2:_fail(path,'expected (event/scope, operations)')
   event=value[0]
   if not (_text(event) or _seq(event) and event and _text(event[0])):_fail(path+'[0]','invalid event/scope')
   validate_operations(value[1],path+'[1]',report,strict_unknown)
  elif name=='CHOICES':
   if not _seq(value) or not value:_fail(path,'expected nonempty choice branches')
   for i,branch in enumerate(value):
    if not _seq(branch) or len(branch)!=3:_fail(f'{path}[{i}]','expected (label, target mode, operations)')
    _text_at(branch[0],f'{path}[{i}][0]');validate_rule(branch[1:],f'{path}[{i}]',report,strict_unknown)
  elif name=='LOCATION_RULES':_text_at(value,path)
  else:_fail(name,'uncovered table schema')
 return report

def validate_namespace(namespace,strict_unknown=False):
 """Validate recognized declaration tables in module vars or a mapping."""
 result={}
 for name in RULE_TABLES|OP_TABLES|PAIRED_TABLES|{'CHOICES','LOCATION_RULES'}:
  if name in namespace:result[name]=validate_table(name,namespace[name],strict_unknown)
 return result

# Explicit historical board/zone primitives. These schemas certify shape only.
from .historical_board_primitives import GROUPS as _HISTORICAL_BOARD_GROUPS
_historical_group=_one_of(*_HISTORICAL_BOARD_GROUPS)
SCHEMAS.update(
 historic_zone_buff=(_one_of('hand','deck','hand_deck'),_optional_text,_integer,_integer),
 historic_random_attack=(_integer,_integer),historic_full_heal_heroes=(),
 historic_both_armor=(_integer,),historic_damage_buff=(_integer,_integer,_integer),
 historic_board_damage=(_historical_group,_integer),historic_random_board_damage=(_historical_group,_integer),
 historic_board_buff=(_historical_group,_integer,_integer),
 historic_board_silence=(_historical_group,),historic_full_heal_board=(_historical_group,),
 historic_board_keyword=(_historical_group,_text,_one_of('permanent','end','next_start')),
 historic_temporary_attack=(_historical_group,_integer,_one_of('end','next_start')))

SCHEMAS.update(
 historic_damage_keyword=(_integer,_text),historic_board_freeze=(_historical_group,),
 historic_random_keyword=(_historical_group,_text),historic_weapon_wear=(_integer,),
 historic_remove_secrets=(_one_of('one','all'),),historic_enemy_attack_set=(_integer,),
 historic_enemy_health_set=(_integer,),historic_hand_size_heal=(),historic_hand_size_area=(),
 historic_destroy_small_others=(_integer,),historic_destroy_random_small=(_integer,),
 historic_weapon_stats=(),historic_target_attack_damage=(),
 historic_source_attack_area=(_historical_group,),historic_random_damaged_heal=(_integer,),
 historic_opponent_draw=(_integer,))

SCHEMAS.update(historic_bounce_source=(),historic_opponent_class_generate=(_optional_text,_integer),
 historic_opponent_one_cost_summon=())

SCHEMAS.update(historic_damage_echo_hero=(),historic_coinflip_draw=(),
 historic_heal_source=(lambda value: value is None or _integer(value),),
 historic_set_source_attack=(_integer,))

SCHEMAS['historic_event_keyword']=(_text,)

SCHEMAS['historic_full_crystals_both']=(_integer,)

SCHEMAS['historic_refresh_all_mana']=()

SCHEMAS.update(historic_attack_threshold_keyword=(_integer,_text),historic_destroy_target_buff=(_integer,_integer))

def _historical_batch_condition(value):
 from .historical_condition_batches import SPECS
 return _seq(value) and tuple(value) in ({spec[0] for spec in SPECS.values()} | {('source_attack',2),('source_attack',4),('hand_empty',),('mana_at_least',5)})
SCHEMAS['historic_when']=(_historical_batch_condition,_seq)

SCHEMAS.update(
 historical_batch_grant_other_deaths=(_seq,),historical_batch_hand_count_summon=(_text,),
 historical_batch_trigger_target_death=(),historical_batch_manathirst_damage=(_integer,_integer,_integer),
 historical_batch_random_enemy_damage=(_integer,_integer),historical_batch_hand_weapon_buff=(_integer,_integer),
 historical_batch_all_weapon_buff=(_integer,_integer),historical_batch_friendly_heal_enemy_damage=(_integer,),
 historical_batch_eat_shields=(_integer,_integer),historical_batch_spend_mana_buff=(_integer,_integer),
 historical_batch_eat_secrets=(),historical_batch_enemy_count_buff=(_integer,_integer),
 historical_batch_eat_adjacent=(),historical_batch_eat_target=(),
 historical_batch_destroy_cheap_deck=(_integer,),historical_batch_destroy_cost_spells=(_integer,),
 historical_batch_weapon_buff_or_draw=(_integer,_integer),historical_batch_deck_keyword_self=(_seq,))

_optional_filters=lambda value:value is None or _filters(value)
_private_draw_state=lambda value:isinstance(value,dict)
SCHEMAS.update(
 historical_draw_batch=(_optional_filters,_one_of('none','set_cost','armor_cost','damage_hero_cost','nature_elemental','school_discount','source_keyword','buff','discount','turn_zero','health_payment','one_stats_cost','recruit_drawn','copy_drawn_minion','left_hand','frost_elementals','copy_temporary','random_cost_summon','chicken','source_stats','chalk','colifero','same_turn_follow','watercolor','nemsy','magatha'),_seq,_one_of('random','lowest','highest')),
 historical_draw_fill=(_filters,),historical_outcast_draw_batch=(_filters,_integer),
 historical_draw_frost_pair=(),historical_draw_distinct_secrets=(_integer,),
 historical_draw_discount_fire_hand=(_integer,),historical_draw_shuffle_cheapest_hand=(),
 historical_draw_history_buff=(_text,_integer,_integer),
 historical_draw_capture=(_optional_filters,_one_of('random','lowest','highest'),_private_draw_state),
 historical_draw_finish=(_text,_seq,_private_draw_state),
 historical_draw_pair_finish=(_private_draw_state,_private_draw_state),
 historical_draw_secret_step=(_private_draw_state,),historical_draw_secret_continue=(_private_draw_state,))

SCHEMAS.update(
 historical_union_discover=(lambda value:_seq(value) and bool(value) and all(_pool_request(v) for v in value),),
 historical_batch_sample_damage=(_historical_group,_integer,_integer),
 historical_batch_sample_freeze=(_historical_group,_integer),
 historical_batch_sample_buff=(_historical_group,_integer,_integer,_integer),
 historical_batch_missiles=(_historical_group,_integer),historical_batch_missile_one=(_historical_group,),
 historical_batch_menagerie=(_integer,_integer),historical_batch_random_keywords=(_seq,))

SCHEMAS.update(historical_batch_opponent_crystal=(_integer,),historical_batch_damage_stealth_if_kill=(_integer,))

SCHEMAS.update(historical_keyword_force_enemy=(),historical_keyword_event_armor=(),
 historical_keyword_discount_hand=(_integer,),historical_keyword_transform_source=(_text,),
 historical_keyword_damaged_attack=(_integer,),historical_keyword_copy_cast_spell=(),
 historical_keyword_silence_source=(),historical_keyword_frozen_enemy_damage=(_integer,),
 historical_keyword_other_shields=(),historical_keyword_spell_cost_minion=(),
 historical_keyword_overheal_minion=())

SCHEMAS.update(historical_event_discount_drawn=(_integer,),historical_event_copy_drawn=(),
 historical_event_spell_damage=(_one_of('self','target','adjacent'),_integer),
 historical_event_damage_spell_damage=(_integer,_integer),
 historical_event_summon_modify=(_one_of('attack_at_most','health','keyword','cost'),lambda value:_integer(value) or _text(value),_integer,_integer,_optional_text),
 historical_event_summon_self_death_buff=(_integer,_integer),historical_event_trigger_summoned=(),
 historical_event_freeze_random_enemy=(),historical_event_enemy_damage_spell_cost=(),
 historical_event_armor_spell_cost=(),historical_event_destroy_damaged_enemy=(),
 historical_event_destroy_bottom=(_integer,),historical_event_buff_unattacked=(_integer,_integer),
 historical_event_draw_unattacked=(_integer,),historical_event_damage_random_other_friendly=(_integer,))

SCHEMAS.update(historical_event_summon_source_stats=(_text,),historical_event_other_totem_zones=(_integer,_integer),
 historical_event_spellpower_area=(_integer,),historical_event_half_hand_cost=(),
 historical_event_destroy_smaller=(),historical_event_destroy_alone=())

SCHEMAS.update(historical_prime_shuffle=(_text,),historical_prime_part=(),historical_prime_raptor=(_integer,_integer),historical_prime_mage_casts=(_integer,))

SCHEMAS.update(historical_mutation_crystals=(_integer,),historical_mutation_enemy_count_heal=(_integer,),
 historical_mutation_top_cost=(_integer,),historical_mutation_weapon_set=(_integer,),
 historical_mutation_dragons_hand=(_integer,_integer,_integer),historical_mutation_deathrattle_hand=(_integer,_integer,_integer),
 historical_mutation_spell_cost=(_integer,),historical_mutation_taunt_zones=(_integer,_integer),
 historical_mutation_unlock_draw=(),historical_mutation_bounce=(_integer,_integer,lambda value:value is None or _integer(value)),
 historical_mutation_copy_board=(lambda value:value is None or _integer(value),lambda value:value is None or _integer(value),_seq),
 historical_mutation_transform_copy_source=(),historical_mutation_copy_health=(),
 historical_mutation_buff_source_stats=(),historical_mutation_armor_source_attack=())

SCHEMAS.update(historical_mutation_discount_zones=(_seq,_seq,_integer),
 historical_mutation_discount_extreme=(_seq,_integer),historical_mutation_swap_hands=(),
 historical_mutation_hand_top=(),historical_mutation_swap_spell_costs=(),
 historical_mutation_copy_cost_hand=(_integer,),historical_mutation_hand_source_attack=(),
 historical_event_murloc_deaths=())

SCHEMAS.update(historical_event_totem_attack=(_integer,),historical_batch_count_missiles=(_text,_text,_integer,_integer))

SCHEMAS['historical_batch_count_shots']=(_text,_integer,_integer)

SCHEMAS['historical_event_sleep_target']=(_integer,)

SCHEMAS.update(historical_batch_joust=(_text,_boolean,_seq),historical_batch_joust_draw=(_integer,))

SCHEMAS['historical_keyword_cast_same_cost']=()

SCHEMAS.update(historical_event_inspire_attack=(),historical_event_tax_drawn=(_integer,_integer))

SCHEMAS.update(historical_event_copy_death_target=(),historical_event_resummon_bearer=(),historical_event_transfer_summon=(_text,),historical_event_transfer_buff=(_text,_integer,_integer),historical_event_played_buff_death=(_integer,_integer,_text))

SCHEMAS.update(historical_draw_dragon_chain=(),historical_draw_dragon_continue=(_private_draw_state,),historical_batch_mana_branch=(_integer,_seq,_seq),historical_batch_heal_friendly_characters=(_integer,),historical_batch_armor_damage=(),historical_batch_empty_zones_destroy=())

SCHEMAS.update(historical_family_lackeys=(_integer,),historical_family_lackey_one=(),historical_family_evolve_target=(_integer,),historical_family_tekahn=())

_optional_integer=lambda value:value is None or _integer(value)
SCHEMAS.update(historical_copy_transform_target=(_optional_integer,_optional_integer),
 historical_copy_transform_zone=(_text,_optional_text,_integer,_integer),
 historical_copy_summon_zone=(_text,_optional_integer,_optional_integer,_seq),
 historical_copy_group=(_text,_optional_integer,_optional_integer),
 historical_copy_snapshot=(lambda value:hasattr(value,'card_id') and hasattr(value,'max_health'),_optional_integer,_optional_integer),
 historical_copy_swap=(_text,_one_of('attack','health','stats')),historical_copy_swap_others=(),
 historical_copy_double_deck=(),historical_copy_swap_deck_tops=(),historical_copy_swap_spell_costs=(),
 historical_copy_random_hand=(),historical_copy_opening_hand=(),historical_copy_opponent_decks=(),
 historical_copy_enemy_deck_hand=(),historical_copy_destroy_deck=(),historical_copy_neighbor=(),
 historical_copy_played=(_one_of('summon','transform'),_optional_integer,_optional_integer))

SCHEMAS['outcast_operation']=(_seq,)

SCHEMAS['historical_mutation_turn_spell_cost']=(_integer,)

SCHEMAS.update(historical_event_equipped_buff=(_integer,_integer),historical_event_healed_buff=(_integer,_integer),
 historical_event_attacker_buff=(_integer,_integer),historical_event_played_keyword_buff=(_integer,_integer,_text),
 historical_event_extra_attack=(),historical_event_armor_dealt=(),historical_event_drawn_one_copy=(),
 historical_event_drawn_beast_buff=(_integer,_integer),historical_event_chance_draw=(),
 historical_event_temporary_drawn=(),historical_event_draw_count_damage=())

SCHEMAS.update(historical_mutation_recruit_demons=(),historical_mutation_hand_entry_damage=(_integer,_integer),
 historical_mutation_health_42=(),historical_mutation_copy_whole_hand=(),historical_mutation_bounce_delta=(_integer,),
 historical_mutation_full_hero_heal=())

SCHEMAS.update(historical_family_basic_totem=(),historical_family_totems_alakir=(),historical_family_libram_discount=(_integer,),historical_family_both_random=(_pool_request,_seq),historical_family_parts_both=())

SCHEMAS.update(historical_family_power_refresh=(),historical_family_power_cost=(_optional_integer,_optional_integer,_boolean),historical_family_power_upgrade=())

SCHEMAS.update(historical_upgrade_remove_top=(_boolean,_integer),historical_upgrade_quickdraw_damage=(_integer,),
 historical_upgrade_corpse_damage=(_integer,_integer),historical_upgrade_freeze_armor=(),
 historical_upgrade_source_stats=(),historical_upgrade_undead_hand=(_integer,_integer),
 historical_upgrade_copy_beast_deck=(_integer,),historical_upgrade_capture_summon=(_text,_private_draw_state),
 historical_upgrade_attack_summoned=(_private_draw_state,),historical_upgrade_summon_attack=(_text,),
 historical_upgrade_fill_source=(),historical_upgrade_copy_forged=())

SCHEMAS.update(historical_batch_attack_summons=(_text,),historical_batch_shuffle_literal=(_text,_integer,_boolean),historical_batch_other_draw=(_integer,),historical_batch_current_summon=(_text,),historical_batch_armor_resummon=(_integer,_text))

SCHEMAS['historical_upgrade_echo']=(_text,_seq)

SCHEMAS.update(historical_upgrade_adapt=(_one_of('self','target','murlocs','recruits','raptors','friendly'),),historical_upgrade_apply_adaptation=(_text,),historical_upgrade_adapt_sacrifice=(),historical_upgrade_adapt_after_destroy=(_private_draw_state,))

SCHEMAS.update(historical_copy_hand_edges=(),historical_copy_last_enemy=(),historical_copy_discount_hand=(_one_of('foreign','nonstarting'),_integer),historical_copy_remove_enemy_stealth=(),historical_copy_double_elementals=(),historical_copy_attack_extremes=(),historical_copy_eat_enemy_hand=(),historical_copy_discard_lowest=(_integer,),historical_copy_enemy_spell=(),historical_copy_fill_both=(_text,),historical_copy_dragons_self=(),historical_copy_watch_posts=(),historical_copy_enemy_generate=(_pool_request,_integer,_one_of('hand','board')))

SCHEMAS.update(historical_draw_school_count=(),historical_draw_school_damage=(),historical_draw_nonstarting=(_integer,),historical_draw_nonstarting_one=())

SCHEMAS.update(historical_drawn_consume_soul=(_seq,),historical_drawn_souls=(),historical_drawn_boom_bots=(),historical_drawn_overload=(_integer,),historical_drawn_non_mech_damage=(_integer,),historical_drawn_copy_received=())

SCHEMAS.update(historical_upgrade_discover_undead=(),historical_upgrade_shopper=(),historical_upgrade_tinyfin=(),historical_upgrade_hero_windfury=())

SCHEMAS.update(historical_event_source_hero_damage=(_integer,),historical_event_defender_stats=(_integer,_integer),historical_event_silence_defender=(),historical_event_fill_hands=(_integer,),historical_event_source_transform_cost=(_integer,),historical_event_attack_hero=())

SCHEMAS.update(historical_resurrection_pick=(_text,_integer,_seq),historical_resurrection_summon=(_text,_seq,_integer,_integer),historical_resurrection_last_death_copy=(),historical_resurrection_death_hand=(),historical_resurrection_shuffle=(_integer,),historical_resurrection_gain_deaths=(_integer,),historical_resurrection_copy_target_death=(),historical_resurrection_destroy_remember=(),historical_resurrection_destroy_others=(),historical_resurrection_capture_destroy=(_integer,),historical_resurrection_corpse_death=(_integer,))

SCHEMAS.update(historical_resurrection_mech_pair=(),historical_resurrection_capture_summon=(_text,_private_draw_state),historical_resurrection_force=(_private_draw_state,),historical_resurrection_discover=(_one_of('shuffle','gain_trigger'),),historical_resurrection_decay=(),historical_resurrection_pair=(_text,_text),historical_resurrection_attack_victim=(),historical_resurrection_death_whelp=())

SCHEMAS.update(historical_resurrection_deck_death=(),historical_resurrection_discover_generated_death=(),historical_resurrection_draw_death=(_boolean,),historical_resurrection_gain_drawn=(_private_draw_state,),historical_resurrection_sacrifice_recruit=(),historical_resurrection_destroy_return=(),historical_resurrection_undead_attack=(),historical_resurrection_drawn_destroy=())

SCHEMAS.update(historical_play_finale=(_seq,),historical_play_mana_shots=(),historical_play_finale_damage=(_integer,),historical_play_big_draw=(),historical_play_astalor_shots=(),historical_play_copy_enemy_deck=(),historical_play_next_beast=(),historical_play_outcast_edges=(),historical_play_discount_edges=(_integer,),historical_play_shuffle_hand=(),historical_play_windup=(_one_of('damage','refresh','copies'),),historical_play_recruit_self=())

SCHEMAS['historical_play_attack_edges']=()

SCHEMAS['historical_play_zone_offer']=(_one_of('own','enemy'),_one_of('hand','deck'),_filters,_one_of('copy','copy_draw_other','draw','shuffle','top','draw_discount5','wrangler','draw_all','cast_copy','tentacle'),_integer,_boolean)

SCHEMAS.update(historical_hand_swap_tick=(_integer,_text),historical_hand_vanndar=(),historical_hand_deck_inner_fire=(),historical_hand_spell_source_cost=(),historical_hand_discount_schools=(_integer,),historical_hand_copy_tribe=(_text,_boolean),historical_hand_spell_damage=(_seq,_text,_integer),historical_hand_shred_minion=(_integer,),historical_hand_high_spell_refresh=(),historical_hand_demon_discount=(_integer,),historical_hand_summon_nonstarting=(_one_of('DEMON','MINION'),),historical_hand_fire_elementals=(_integer,),historical_hand_discount_spells=(_integer,_integer))

SCHEMAS.update(historical_hand_zero_spells=(),historical_hand_recruit_copies=(),historical_hand_recruit_physical=(_private_draw_state,),historical_hand_transform_zone=(_one_of('hand','deck'),_one_of('neutral','one_cost','spell','minion'),_one_of('own','legendary','enemy_spell','spell_plus_three','dragon'),_boolean))

SCHEMAS.update(historical_arsenal_enemy_armor=(_integer,),historical_arsenal_convert_health=(),historical_arsenal_odyn=(),historical_arsenal_armor_gate=(_integer,),historical_arsenal_changed_draw=(_integer,),historical_arsenal_random_weapon=(_text,),historical_arsenal_both_weapons=(),historical_arsenal_deck_weapon=(),historical_arsenal_pirate_weapon=(),historical_arsenal_old_weapon=(_one_of('hand','equip'),),historical_arsenal_enemy_weapon_card=(),historical_arsenal_armor_minion=(),historical_arsenal_enemy_turn_armor=(_integer,),historical_arsenal_discard_draw=(),historical_arsenal_discard_one=(_private_draw_state,),historical_arsenal_discard_finish=(_private_draw_state,),historical_arsenal_eat_weapons=(),historical_arsenal_discard_all=(_private_draw_state,),historical_arsenal_eat_finish=(_private_draw_state,))

SCHEMAS.update(historical_sleep_rebirth=(_one_of('healed','beast_deaths','friendly_deaths','fire','turn_cards'),_integer),historical_sleep_wake_progress=(),historical_sleep_wildseed=(),historical_sleep_frost_stags=(),historical_sleep_freeze_or_damage=(_integer,),historical_sleep_sample_frozen=(_integer,_integer),historical_sleep_freeze_one=(_integer,_boolean,_integer),historical_sleep_freeze_damage=(_integer,),historical_sleep_nameless=(),historical_sleep_silence_destroy_summoned=(),historical_sleep_gorm=(),historical_sleep_kill=(_integer,),historical_sleep_reduce=(_integer,),historical_sleep_thaw=())

SCHEMAS.update(historical_sleep_repeat_area=(_integer,),historical_sleep_capture_area=(_integer,_private_draw_state),historical_sleep_repeat_after=(_integer,_private_draw_state),historical_sleep_healing_area=(),historical_sleep_hero_damage=(),historical_keyword_gain_victim_attack=())

SCHEMAS.update(historical_hand_discard_select=(_one_of("own","enemy"),_one_of("lowest","highest","undead","minion","spell"),_one_of("none","copies","summon","return")),historical_hand_discard_history=(_one_of("hand","board","health_hand"),_integer),historical_hand_discard_delivery=(_private_draw_state,),historical_hand_discard_intrinsic=(_one_of("summon","copies","grow_return"),),historical_hand_deathwing=(_boolean,),historical_hand_destroy_victims=(_private_draw_state,),historical_hand_deathwing_discard=(_private_draw_state,),historical_hand_rin=(),historical_hand_shred_top=(_integer,))

SCHEMAS.update(historical_resource_inzah=(),historical_resource_prevent=(),historical_resource_next_draenei=(),historical_resource_trogg=(),historical_resource_asteroid_bonus=(_integer,),historical_resource_asteroid_damage=(),historical_resource_draw_libram=(),historical_resource_acolyte=(),historical_resource_steal_health=(_integer,),historical_resource_anchorite=(),historical_resource_dreamboat=(),historical_resource_heal_boat=(_integer,_private_draw_state),historical_resource_boat_finish=(_private_draw_state,))

SCHEMAS.update(historical_resource_next_refresh=(),historical_resource_refresh_attack=(_integer,),historical_resource_refresh_spells=())

SCHEMAS.update(historical_resource_omega_lifesteal=(),historical_resource_no_hero_targets=())

SCHEMAS['on_draw_shuffle']=(_text,_integer,_integer)

SCHEMAS['unlock_mana']=()

SCHEMAS.update(historical_secret_deck=(_one_of('each','one','combo','conditional'),_boolean),historical_secret_copy_enemy=(),historical_secret_sayge=(),historical_secret_steal=(),historical_secret_recast=(),historical_secret_temporary=(_pool_request,_integer),historical_secret_discover=(_pool_request,_one_of('place','cast','other_hand')),historical_secret_solo_discover=(_pool_request,),historical_secret_hand_cast=(),historical_secret_soldiers=(),historical_secret_store_soul=(),historical_secret_soldier_restore=(),historical_secret_if_active=(_one_of('buff','heal'),),historical_secret_random=(_pool_request,_one_of('place','different_cast')),historical_secret_pick_deck=(_boolean,),historical_secret_take_deck=(_private_draw_state,),historical_secret_place=(_private_draw_state,),historical_secret_temporary_cast=(_pool_request,_private_draw_state),historical_secret_schedule_destroy=(_private_draw_state,),historical_secret_destroy_instances=(_seq,),historical_secret_soldier=(_integer,))

SCHEMAS.update(historical_play_two_discounts=(),historical_play_combo_history_buff=(),historical_play_bottom_enemy=(),historical_play_quick_or_combo_coin=(),historical_play_gong=())

SCHEMAS.update(historical_ritual_grow=(_integer,_integer,_boolean),historical_ritual_missiles=(),historical_ritual_ten=(_one_of('heal','health','armor'),),historical_ritual_doomcaller=(),historical_ritual_blade=(),historical_ritual_emperor=(_text,),historical_ritual_jade=(_boolean,_boolean),historical_ritual_display_grow=(),historical_ritual_display_shuffle=(_integer,),historical_ritual_blade_destroy=(_private_draw_state,))

SCHEMAS.update(historical_galakrond_invoke=(),historical_galakrond_cultist=(),historical_galakrond_twice=(_one_of('copies','coins','draw','discount'),),historical_galakrond_kronx=(),historical_galakrond_wolves=(),historical_galakrond_reward=(_text,),historical_galakrond_increment=(),historical_galakrond_summon=(_text,),historical_galakrond_wolf=(_integer,))

SCHEMAS['buff_others']=(_integer,_integer)

SCHEMAS['equip']=(_text,)

SCHEMAS.update(historical_tribal_treant_discover=(_pool_request,),historical_tribal_goru=(),historical_tribal_lothraxion=(),historical_tribal_eat_totems=(),historical_tribal_stonewright=(),historical_tribal_recruits=(_boolean,),historical_tribal_murloc_discount=(),historical_tribal_health_murloc=(),historical_tribal_vilefin=(),historical_tribal_stewart=(),historical_tribal_destroy_totems=(_private_draw_state,),historical_tribal_eat_finish=(_private_draw_state,),historical_tribal_recruit=(_boolean,),historical_tribal_recruit_stewart=(_integer,_integer),historical_tribal_recruit_shield=(_integer,),historical_tribal_howdy=(_integer,_pool_request),historical_treasure_offer=(_one_of('lackey','manager','artifact'),),historical_treasure_goblet=(),historical_treasure_crown=(_pool_request,),historical_treasure_replace=(_pool_request,),historical_treasure_chest=(),historical_treasure_fill=(_private_draw_state,),historical_treasure_copy=(_private_draw_state,),historical_treasure_random=())

SCHEMAS['summon_opponent']=(_text,_integer)

SCHEMAS.update(historical_infuse_devour=(_boolean,),historical_infuse_companions=(_integer,),historical_infuse_relic_choice=(),historical_infuse_control=(),historical_infuse_relic_all=(),historical_infuse_relic=(_one_of('extinction','phantasms','dimensions'),),historical_infuse_totem_choice=(),historical_infuse_all_totems=(),historical_infuse_destroy_small=(_integer,),historical_infuse_bats=(_boolean,),historical_infuse_evolve=(_boolean,),historical_infuse_touch_return=(),historical_infuse_devour_wave=(_private_draw_state,),historical_infuse_devour_buff=(_private_draw_state,),historical_infuse_manathirst=(_integer,_integer,_integer),historical_infuse_relic_upgrade=(),historical_infuse_spirit=(_integer,),historical_infuse_bat=(_boolean,))

SCHEMAS['historical_infuse_other_beasts']=()

SCHEMAS.update(historical_copy_target_all=(),historical_copy_target_delivery=(_one_of('hand','deck'),_integer,_optional_integer,_optional_integer,_optional_integer,_boolean),historical_copy_target_snapshot=(lambda value:hasattr(value,'card_id') and hasattr(value,'max_health'),_one_of('hand','deck'),_integer,_optional_integer,_optional_integer,_optional_integer,_boolean))

SCHEMAS['historical_copy_permanent_battlecries']=()

SCHEMAS.update(historical_copy_muckmorph=(),historical_copy_barista=(),historical_copy_healed_self=(),historical_copy_corpse_self=(_integer,),historical_copy_death_shuffle=(),historical_copy_random_control=(),historical_copy_devour_enemy=(),historical_copy_kill_bound=(_integer,),historical_copy_devour_gain=(_integer,_integer))

SCHEMAS['historical_copy_quickdraw_self']=()

SCHEMAS.update(historical_copy_friendly_spell_history=(),historical_copy_spell_delivery=(_private_draw_state,_one_of('hand','deck')),historical_event_tamsin_copy=())

SCHEMAS['damage_random_enemy']=(_integer,)

SCHEMAS.update(historical_copy_snowflurry=(),historical_copy_power_bonus=(_integer,),historical_copy_saboteur=(),historical_copy_power_threshold=(_integer,_one_of('damage','ragnaros')),historical_copy_power_permanent=(_one_of('armor','attack'),),historical_copy_void_crusher=(),historical_copy_power_hit=(_one_of('target','enemy_hero','random_enemy','own_hero'),_integer))

SCHEMAS.update(historical_copy_next_spell_bonus=(_integer,),historical_copy_next_spell_repeat=(),historical_copy_next_spell_lifesteal=(),historical_copy_double_hand=(),historical_copy_odd_health=(),historical_copy_spend_double=(_integer,))

SCHEMAS['buff_random_hand_minion']=(_one_of('friendly','enemy','both'),_integer,_integer)

SCHEMAS.update(historical_event_refresh_hero=(),historical_event_heal_source_full=(),historical_event_obelisk=(),historical_event_void_hound=(),historical_event_cook=(),historical_event_load_bullets=(),historical_event_hamm=(),historical_event_maw_paw=(),historical_event_piranha=())

SCHEMAS.update(historical_copy_enemy_recruit=(),historical_copy_recruit_other=(_integer,),historical_copy_recruit_one=(_one_of('hand','deck'),_filters,_optional_text,lambda value:value is None or _private_draw_state(value)),historical_copy_maxima=(),historical_copy_oblivitron=(),historical_copy_recruited_attack=(_private_draw_state,),historical_copy_recruited_death=(_private_draw_state,),historical_copy_recruited_kill=(_private_draw_state,),historical_copy_recruit_hand_all=(_one_of('foreign','dragon'),),historical_copy_recruit_uid=(_one_of('hand','deck'),_integer),historical_copy_mana_cyclone=(),historical_copy_less_attack_recruit=(),historical_copy_recruit_conditional=(_one_of('held_demon','drekthar'),),historical_copy_tavish=(),historical_copy_put_ten=())

SCHEMAS.update(historical_copy_enemy_turn_summon=(_text,),historical_copy_toxin=(),historical_copy_toxin_bounce=(),historical_copy_weasel=(),historical_copy_azari=(),historical_copy_cube=())

SCHEMAS['temporary_keyword_target']=(_text,_one_of('next_start','end'))
SCHEMAS['historical_copy_pyros']=(_text,)

SCHEMAS.update(historical_copy_evolve_adjacent=(_integer,),historical_copy_evolve_target=(_integer,),historical_copy_evolve_uid=(_integer,_integer),historical_copy_tinkmaster=(),historical_copy_fang=(),historical_copy_literal_target=(_text,),historical_copy_literal_uid=(_integer,_text),historical_copy_treespeaker=(),historical_copy_taldaram=(),historical_copy_spread_plague=(),historical_copy_weapon_evolve=(),historical_copy_transmogrifier=(),historical_event_swap_source_stats=())

SCHEMAS.update(historical_event_blackguard=(),historical_event_banshee=(),historical_event_lightsteed=(),historical_event_alexstrasza=(),historical_event_static_waveform=(),historical_copy_healing_damage_turn=(),historical_copy_healing_damage_next=())

SCHEMAS.update(historical_copy_literal_family=(_one_of('adventurer','soldier','sparkbot','crewmate'),_one_of('hand','board')),historical_copy_board_bonus=(_one_of('all','other_beasts'),),historical_copy_wayfinder=(),historical_copy_amalgam_band=(),historical_copy_elitist_snob=(),historical_copy_crewmates=())

SCHEMAS.update(historical_copy_steal_target_health=(_integer,),historical_copy_sivara=(),historical_copy_hedra=(),historical_copy_pupil=(),historical_copy_drawn_copy=(_one_of('hand','dorian','betrug'),),historical_copy_drawn_health=())

SCHEMAS.update(historical_copy_force_event=(),historical_copy_force_random=(_one_of('minion','character','lowest'),),historical_copy_lothar=(),historical_copy_lothar_reward=(_integer,_integer,_integer),historical_copy_force_enemies=(),historical_copy_theldurin=(),historical_copy_egg_attack=(),historical_copy_bloodstinger=(),historical_copy_bound_attack=(_private_draw_state,_one_of('lowest','recruited')),historical_copy_lowest_damage=(_integer,),historical_copy_olgra_buff=(),historical_copy_shambler=(),historical_copy_braggart=(),historical_copy_egg_summon=(_private_draw_state,),historical_copy_enemy_hand=(_private_draw_state,),historical_copy_corpse_bride=(),historical_copy_dreadsteed=(),historical_copy_summon_owner=(_integer,_text))

SCHEMAS['force_all_others']=()

SCHEMAS.update(historical_copy_raza=(),historical_copy_next_payment=(_one_of('corpses','armor','health'),_one_of('all','spell','minion','paladin_minion'),_integer),historical_copy_ulthok=(),historical_copy_fatigue=(_one_of('buff','summon'),),historical_copy_take_fatigue=(_private_draw_state,),historical_copy_fatigue_reward=(_one_of('buff','summon'),_private_draw_state))

SCHEMAS.update(historical_copy_cast_zone=(_one_of('own','enemy'),_one_of('hand','deck'),_optional_text,_one_of('highest','random'),_one_of('random','prefer_source')),historical_copy_cast_school_copy=(_text,),historical_copy_history_spell=(_one_of('vargoth','parrot','asvedon','squawker'),),historical_copy_cast_event_self=(),historical_copy_gallywix=(),historical_copy_spell_plus_one=(),historical_copy_voraxx=(),historical_copy_voraxx_plant=(_private_draw_state,),historical_copy_voraxx_cast=(_private_draw_state,))

SCHEMAS.update(historical_copy_timed_cost=(_text,_integer,_optional_integer,_one_of('enemy','both')),historical_copy_sea_shill=(),historical_copy_jeweler=(),historical_copy_timewarden=(),historical_copy_astrobiologist=(),historical_copy_edge_lock=(),historical_copy_hand_lock_choice=(),historical_copy_next_draw_discount=(_integer,),historical_copy_next_draw_spell_copy=(),historical_copy_replace_zones=(_one_of('foreign','legendary'),))

SCHEMAS.update(historical_copy_ivus=(),historical_copy_lurker=(),historical_copy_wrathguard=(),historical_copy_hit_bound=(_integer,_integer),historical_copy_lurker_continue=(_private_draw_state,),historical_copy_wrathguard_discover=(_private_draw_state,),historical_copy_flik=(),historical_copy_blazing=(),historical_copy_blazing_card=(_integer,),historical_copy_patchwerk=(_one_of('hand','deck','board'),),historical_copy_capture_destroy=(_integer,_boolean),historical_copy_cubicle_summon=(),historical_copy_chef=(),historical_copy_dang_blasted=(),historical_copy_ozruk=())

SCHEMAS.update(historical_copy_shuffle_plagues=(_integer,),historical_copy_helya=(),historical_copy_tomb_traitor=(),historical_copy_destroy_plague=(_integer,),historical_copy_plague_effect=(_text,),historical_copy_unending_plague=(),historical_copy_give_curse=(),historical_copy_curse_tick=(_integer,),historical_copy_curse_expire=(_integer,))

SCHEMAS.update(historical_copy_kaahrj=(),historical_copy_mankrik=(),historical_copy_mankrik_summon=(_private_draw_state,),historical_copy_mankrik_attacks=(_private_draw_state,),historical_copy_steal_weapon=(),historical_copy_weapon_spell_bonus=(_integer,))

SCHEMAS['historical_copy_enemy_draw']=(_integer,)

SCHEMAS.update(historical_copy_enemy_deck_all=(),historical_copy_enemy_top=(),historical_copy_enemy_random_two=(),historical_copy_hero_set=(_integer,),historical_event_hurt_played=(_integer,))

SCHEMAS.update(historical_copy_polkelts_order=(),historical_copy_steeldancer=(),historical_copy_die=(),historical_copy_brittleskin=(),historical_copy_invincible=(),historical_copy_corpse_hand_attack=(_integer,_integer),historical_copy_shockspitter=(),historical_copy_replace_enemy_hand=(),historical_copy_enemy_hand_sample=(_integer,),historical_copy_illusionist=(),historical_event_brutal_damage=(),historical_event_liadrin_summon=())

SCHEMAS.update(historical_copy_rook_attack=(),historical_copy_previous_elemental_draw=(),historical_copy_coral=(),historical_copy_random_starting_hand=(),historical_copy_templar=(),historical_event_bubbler=(),historical_event_observer_myths=())

SCHEMAS.update(historical_copy_geist=(),historical_copy_ymirjar=())

SCHEMAS.update(historical_copy_streak_damage=(_one_of('target','enemies'),),historical_copy_streak_copies=(),historical_copy_prairie=(),historical_copy_razzle=(),historical_copy_spurfang=(),historical_copy_quickdraw_operation=(_seq,),historical_copy_farm_hand=(),historical_copy_gatekeeper=(),historical_copy_cheese_elemental=(),historical_copy_xanesh=())

SCHEMAS.update(historical_copy_cookie=(),historical_event_reborn_played=())

SCHEMAS.update(historical_copy_power_slider=(),historical_copy_fill_bananas=(),historical_copy_highest_spell=(),historical_copy_control=(_one_of('board_four','small_attack'),),historical_copy_aldor=(),historical_copy_last_draenei=(),historical_copy_eight_hands=(),historical_copy_hat=(),historical_copy_escape_pod=(),historical_event_holotechnician=(),historical_event_lifeform=(),historical_event_toxmonger=())

SCHEMAS.update(historical_copy_doomkin=(),historical_copy_camel_one=(_one_of('own','enemy'),),historical_copy_grumble=(),historical_copy_alanna=(),historical_copy_spiteful=(),historical_copy_enemy_draw_five=(),historical_copy_custodian=(),historical_copy_lost_exarch=(),historical_copy_spell_cost_summon=(),historical_copy_sonya=(),historical_copy_gibberer=())

SCHEMAS.update(historical_copy_hand_capacity=(_integer,_boolean),historical_copy_serena=(),historical_copy_abyssal_summoner=(),historical_copy_health_return=(),historical_copy_risa=(),historical_copy_lieutenant=(),historical_event_chenvaala=(),historical_event_nat_draw=(),historical_hand_discount_tick=(_integer,))

SCHEMAS.update(historical_copy_giftwrapped=(),historical_copy_tides=(),historical_copy_soulstealer=(),historical_copy_soulstealer_kill=(),historical_copy_soulstealer_corpses=(_private_draw_state,),historical_copy_gandling=(),historical_copy_attack_tokens=(_text,_integer),historical_copy_capture_tokens=(_text,_integer,_private_draw_state),historical_copy_token_attacks=(_private_draw_state,),historical_copy_random_bound_attack=(_integer,),historical_copy_cheesemonger=(),historical_copy_playmaker=(),historical_copy_waterdancer=(),historical_copy_plaguemaw=(),historical_copy_pelagos=())

SCHEMAS['historical_hand_shifter_tick']=(_integer,)

SCHEMAS.update(historical_copy_spirit_frog=(),historical_copy_spirit_tiger=(),historical_copy_spirit_dead=(),historical_copy_phaoris=(),historical_copy_decoy=(),historical_copy_lowest_hand_recruit=(),historical_copy_trenchstalker=(),historical_copy_mirage=(),historical_copy_reborn_enemy_played=(),historical_event_spirit_lynx=())

SCHEMAS.update(historical_copy_bottom_token=(_text,),historical_copy_sunken_scavenger=(),historical_copy_permanent_shuffle=(_one_of('add','base_add','double'),_integer,_one_of('shuffle','bottom')),historical_copy_retained_shuffle=())

SCHEMAS.update(historical_copy_bind_fan=(),historical_copy_jeeves=(),historical_copy_mill_three=(),historical_event_hobgoblin=())

SCHEMAS.update(historical_copy_next_minion=(_text,_integer,_one_of('attack','hero_attack','copy','buff_2_1','health_2_rush','set_8_8')),historical_copy_next_follow=(_one_of('attack','hero_attack','copy'),),historical_copy_next_hero_attack=(),historical_copy_akama=(),historical_copy_reborn_copy=(),historical_copy_turbulus=(),historical_copy_dirdra=())

SCHEMAS['historical_copy_vizier']=()

SCHEMAS['grant_death_target']=(_seq,)

SCHEMAS.update(historical_copy_draw_cast_charges=(_integer,),historical_copy_jotun=())

SCHEMAS['historical_copy_void_ray']=()

SCHEMAS['historical_copy_ogre_ace']=()

SCHEMAS.update(historical_copy_sludge_damage=(),historical_copy_chimaera=())

SCHEMAS['historical_copy_rustwix']=()

SCHEMAS['historical_treasure_invocation']=()

SCHEMAS['fill_board_summon']=(_text,)

SCHEMAS['historical_treasure_pool_offer']=(_pool_request,_one_of('cast','hurt','armor','follow_fireheart','follow_hataaru','suspicious','chromatic'))

SCHEMAS.update(historical_play_banker=(),historical_play_draw_uid=(_integer,_integer))

SCHEMAS.update(historical_treasure_elysiana=(_seq,),historical_treasure_mystery=())

SCHEMAS.update(historical_copy_gral=(),historical_copy_banker_store=(),historical_copy_stored_hand=(_text,),historical_copy_swap_decks=(),historical_copy_ransom=(),historical_copy_plush=(),historical_copy_fizzle=(),historical_copy_snapshot_restore=(),historical_copy_witch=(),historical_copy_witch_repeat=())

SCHEMAS.update(historical_copy_doll_bind=(),historical_copy_doll_destroy=(),historical_copy_ooze_schedule=(),historical_copy_ooze_end=(_integer,_integer))

SCHEMAS.update(historical_treasure_filtered=(_one_of('hipster','importer','maruut','murozond','ivory','amalgam'),),historical_treasure_ivory_copy=(),historical_treasure_dice=())

SCHEMAS.update(historical_copy_shattershambler=(),historical_copy_murmuring=(),historical_copy_experimenter_end=(_integer,))

SCHEMAS.update(historical_draw_balinda=(),historical_draw_menace=(),historical_draw_grapplesniper=(),historical_draw_balinda_finish=(_private_draw_state,_private_draw_state),historical_draw_both_finish=(_one_of('historical_draw_menace','historical_draw_grapplesniper'),_private_draw_state,_private_draw_state))

SCHEMAS.update(historical_copy_earthen_growth=(_integer,_integer),historical_copy_hatch=(_text,),historical_copy_horsemen_win=(),historical_copy_ancient_merge=(),historical_copy_mogu=(),historical_copy_mogu_sacrifice=())

SCHEMAS.update(historical_event_moorabi=(),historical_event_buff_magnetized=())

SCHEMAS.update(historical_copy_zone_swap=(_one_of('source','target'),_one_of('own','enemy'),_one_of('hand','deck'),_seq),historical_copy_najak_take=(),historical_copy_najak_return=())

SCHEMAS.update(historical_copy_skulker_take=(),historical_copy_skulker_return=())

SCHEMAS.update(historical_copy_duplicate_hand=(),historical_copy_growth_treants=())

SCHEMAS.update(historical_copy_fate_bind=(_one_of('growth','decay'),),historical_copy_fate_death=())

SCHEMAS.update(historical_copy_visitor=(),historical_copy_dinner=(),historical_copy_topior=(),historical_copy_eliza=())

SCHEMAS['historical_copy_seamstress']=()

SCHEMAS.update(historical_copy_flint=(),historical_copy_follow_mode=(_private_draw_state,))

SCHEMAS['historical_copy_temporus']=()

SCHEMAS['historical_treasure_suspicious_guess']=(_integer,_integer)

SCHEMAS.update(historical_copy_replay_spells=(_one_of('jace','rommath','lynessa','chatty','yogg'),),historical_copy_yogg_casts=(_integer,))

SCHEMAS['historical_copy_replay_cast']=(lambda value:hasattr(value,'card_id') and hasattr(value,'uid'),_one_of('random','prefer_enemies','selected'))

SCHEMAS.update(historical_copy_next_fire_bonus=(),historical_copy_antonidas=(),historical_hand_watercolor=(_integer,))

SCHEMAS.update(historical_copy_nethrandamus=(),historical_copy_denathrius=(),historical_copy_dragonqueen=(),historical_copy_talritha=(),historical_treasure_egg_hatch=())

SCHEMAS.update(historical_copy_spelleater=(),historical_copy_wizard_swap=(),historical_copy_wizard_restore=(_seq,),historical_treasure_power=(_one_of('basic','upgraded'),))

SCHEMAS.update(historical_copy_random_location=(),historical_copy_location_clone=(),historical_copy_microphones=(),historical_copy_pozzik_bots=(),historical_copy_pozzik_recruit=(),historical_event_metrognome=())

SCHEMAS['historical_copy_zarimi']=()

SCHEMAS.update(historical_copy_draka=(),historical_copy_draw_aura=(),historical_copy_elise_badlands=(),historical_copy_elise_summon=(lambda card:hasattr(card,'card_id') and hasattr(card,'uid'),))

SCHEMAS.update(historical_copy_hollidae=(),historical_copy_boar_sword=(),historical_copy_sword_mana=(),historical_copy_staff_frog=())

SCHEMAS.update(historical_copy_smuggler=(),historical_copy_jepetto=(),historical_copy_nemsy_swap=(),historical_copy_lina=())

SCHEMAS.update(historical_copy_finley_swap=(),historical_copy_illucia=(),historical_copy_illucia_restore=(_integer,))

SCHEMAS.update(historical_copy_korrak=(),historical_event_sporeling=(),historical_event_amet=())

SCHEMAS.update(historical_copy_solar_eclipse=(),historical_copy_lunar_eclipse=())

SCHEMAS['historical_copy_dust_junk']=()

SCHEMAS['insert_fixed']=(_text,_integer,_one_of('shuffle','bottom'))

SCHEMAS.update(historical_copy_blightfang=(),historical_copy_darkvein=(),historical_copy_haunt=(),historical_copy_darkvein_cast=(lambda card:hasattr(card,'card_id') and hasattr(card,'uid'),))

SCHEMAS.update(historical_copy_ashen=(),historical_copy_bonelord=(),historical_copy_bonelord_tick=(_integer,))

SCHEMAS.update(historical_copy_lich_gift=(),historical_copy_lich_army=(),historical_copy_doom_pact=(),historical_copy_doom_remove=(_seq,),historical_copy_death_grip=(),historical_copy_death_coil=(),historical_copy_obliterate=(),historical_copy_antimagic=(),historical_copy_army_summon=(lambda card:isinstance(card,str) or hasattr(card,'card_id'),))
SCHEMAS.setdefault('stored_weapon_kills',())

SCHEMAS.update(historical_copy_gelbin_invention=(),historical_copy_murloc_chord=(),historical_copy_horde_chord=(),historical_copy_power_chord=(_boolean,),historical_copy_chicken_depart=(),historical_copy_poultryizer=(),historical_copy_emboldener=(),historical_copy_repair_bot=())

SCHEMAS['historical_treasure_malygos']=()

SCHEMAS.update(historical_copy_sunstruck=(),historical_copy_sleep_others=())

SCHEMAS.update(historical_copy_excavate_glyph=(),historical_treasure_pillar=())

SCHEMAS.update(historical_excavate_dig=(_boolean,),historical_excavate_bonus=(),historical_excavate_scorpion=(),historical_excavate_snake=(),historical_excavate_rat=(),historical_excavate_dragon=(),historical_excavate_murloc=(),historical_excavate_transform=(_one_of('hand','deck','board'),_integer,_integer,_text))

SCHEMAS.update(historical_excavate_pile_wait=(),historical_excavate_pile_summon=(lambda card:hasattr(card,'card_id') and hasattr(card,'uid'),),historical_excavate_finley=(),historical_excavate_brawl=(),historical_excavate_discount=(),historical_excavate_flinger=(),historical_excavate_miner=(),historical_excavate_secrets=(),historical_excavate_trams=())

SCHEMAS.update(historical_copy_coolant=(),historical_copy_mimiron_gadget=(),historical_copy_pair_offer=())

SCHEMAS.update(historical_hand_forms_nazjar_discount=(),historical_hand_forms_nazjar_fire=(),historical_hand_forms_freeze=(),historical_hand_forms_remember=(),historical_hand_forms_shuffle=())

SCHEMAS.update(historical_copy_neeru=(),historical_copy_mimiron_head=(),historical_copy_head_sacrifice=(_seq,),historical_copy_kel_skeletons=(),historical_copy_kel_step=(_integer,),historical_copy_burning_portal=(_integer,))

SCHEMAS.update(historical_copy_countess=(),learned_school_teacher=(),historical_draw_hagatha=(),historical_draw_hagatha_slime=(_private_draw_state,))
SCHEMAS.setdefault('learned_cast',())

SCHEMAS.update(historical_copy_cthun_piece=(_one_of('DMF_254t3','DMF_254t4','DMF_254t5','DMF_254t7'),))

def _historical_physical_card(value):
 from engine.game import Card
 return isinstance(value,Card)

SCHEMAS.update(historical_copy_corrupted_recovery=(),historical_copy_tribal_hand=(_one_of('copy','buff'),),historical_copy_purator=(),historical_copy_nzoth_deep=(),historical_copy_tribal_resurrect=(_historical_physical_card,))

SCHEMAS.update(historical_draw_mesadune=(),historical_draw_mesadune_finish=(_private_draw_state,),historical_draw_doommaiden=(),historical_draw_doommaiden_return=(_integer,_integer,_integer),historical_copy_dungar=(_integer,_seq))

SCHEMAS.update(historical_copy_hydralisk=(),historical_copy_roach=(),historical_copy_lurker_shot=(),historical_copy_viper=(),historical_copy_zookeeper=(),historical_copy_summon_adversary=(_one_of('viper','zookeeper'),_private_draw_state),historical_copy_adversary_attacks=(_one_of('viper','zookeeper'),_private_draw_state))

SCHEMAS.update(historical_copy_infestor=())

SCHEMAS.update(historical_copy_replace_power=(_one_of('GDB_846hp','TTN_717t','EX1_625t'),),historical_copy_majordomo=(),historical_copy_algalon_vision=())

SCHEMAS.setdefault('discover_deck',())

SCHEMAS.update(historical_copy_power_origin_draw=(_boolean,_boolean),historical_copy_power_origin_capture=(_boolean,_boolean,_private_draw_state),historical_copy_power_filtered_draw=(_optional_filters,_integer),historical_copy_power_draw=(_integer,),historical_copy_power_draw_finish=(_private_draw_state,))

SCHEMAS.update(historical_copy_theotar=(),historical_copy_bibliomite=())

SCHEMAS.update(historical_copy_manual_shots=(_one_of('goliath','huntress'),_integer,_seq),historical_copy_high_noon=(),historical_copy_high_noon_finish=(_private_draw_state,_private_draw_state))

SCHEMAS.update(historical_hand_remix_tick=(_integer,))

SCHEMAS.update(historical_copy_concoction=(),historical_copy_concoction_free=())

SCHEMAS.update(historical_copy_vona=(),historical_copy_ouroboros=(),historical_copy_rheastrasza=(),historical_copy_nest_discover=(_integer,))

SCHEMAS.update(historical_copy_spore=(),historical_copy_upgrade_eruptions=(),historical_drawn_eruption=())

SCHEMAS.setdefault('cast_fixed_spell',(_text,_one_of('random','enemies','prefer_enemies','selected')))

SCHEMAS.update(historical_copy_azshara=(),historical_copy_xalatath=(_integer,),historical_copy_xalatath_wear=(_integer,))

SCHEMAS.update(historical_copy_sheriff=())

SCHEMAS.update(historical_copy_faelin=(),historical_copy_overplanner=())

SCHEMAS.update(historical_copy_horseshoe=())

SCHEMAS.update(historical_copy_atiesh=(_integer,_integer),historical_copy_atiesh_wear=(_integer,))

SCHEMAS.update(historical_copy_drink=(),historical_copy_cup_muscle=(),historical_copy_divine_brew=())

SCHEMAS.update(historical_copy_robocaller=(),historical_hand_robocaller_tick=(_integer,))

SCHEMAS.update(historical_copy_silas=())

SCHEMAS.update(historical_copy_poison=(),historical_copy_weapon_poison=(_one_of("silverleaf","paralytic","leeching"),))

SCHEMAS.update(historical_copy_colossus=(),historical_copy_colossus_wave=(_integer,),historical_copy_mothership=(),historical_copy_sentry=())

SCHEMAS.update(historical_copy_templar_merge=())

SCHEMAS.update(historical_copy_protoss_draw=(_one_of("card","minion"),_boolean),historical_copy_protoss_next=(_one_of("card","spell","minion"),_integer,_boolean),historical_copy_protoss_spell=(),historical_copy_hallucination=(),historical_copy_photon=(),historical_copy_photon_hit=(_private_draw_state,),historical_copy_photon_damage=(_private_draw_state,),historical_copy_photon_reward=(_private_draw_state,))

SCHEMAS.update(historical_copy_twin_blades=())

SCHEMAS.update(historical_copy_copycat_wait=(),historical_copy_copycat_receive=(_private_draw_state,))

SCHEMAS.update(historical_copy_kurtrus=(),historical_copy_kurtrus_shot=())

SCHEMAS.update(historical_copy_history_replay=(_one_of("murozond","sasquawk","conman","parrot","tess","stash"),),historical_copy_history_card=(_private_draw_state,))

SCHEMAS.update(historical_copy_vistah_start=(),historical_copy_vistah_finish=(_integer,))

SCHEMAS.update(historical_copy_repeat_battlecry=(_one_of("last","first_turn"),))

SCHEMAS.update(historical_copy_shudderwock=(),historical_copy_wock_step=(_private_draw_state,))

SCHEMAS.update(historical_copy_onyxia_whelp=(_integer,),historical_copy_sharpshooter=(),historical_copy_sharpshooter_draw=(_boolean,),historical_copy_sharpshooter_switch=(_boolean,))

SCHEMAS.update(historical_copy_beast_deck_buff=(),historical_copy_disciple=(_boolean,),historical_copy_disciple_discard=(_private_draw_state,),historical_copy_disciple_imp=(_boolean,))

SCHEMAS.update(historical_copy_yrel_librams=(),historical_copy_justice_health=())

SCHEMAS.update(historical_copy_kabal_potion=(),historical_copy_bloodfury=(),historical_copy_dragonfire=(),historical_copy_madness=(),historical_copy_madness_return=(_integer,))

# The shared Secret placement consumer takes one literal card identity.
SCHEMAS['secret']=(_text,)

SCHEMAS.update(historical_sleep_magtheridon_destroy=(),historical_sleep_candles=(),historical_sleep_candle=(),historical_sleep_dungar_depart=(_integer,),historical_sleep_dungar_reward=(_integer,))

SCHEMAS.update(historical_copy_shudderblock=())

SCHEMAS.update(historical_copy_aegwynn_death=(),historical_copy_courier=())

SCHEMAS.update(historical_copy_painting=(),historical_copy_jandice=(),historical_copy_jandice_summon=(_text,_private_draw_state),historical_copy_jandice_next=(_private_draw_state,),historical_copy_jandice_choose=(_private_draw_state,))

SCHEMAS.update(historical_copy_zok=(),historical_copy_zok_fan=(_integer,_integer),historical_copy_service_ace=())

SCHEMAS.update(historical_copy_okani_offer=(),historical_copy_gamer=(),historical_copy_gamer_first=(),historical_copy_gamer_second=(_private_draw_state,),historical_copy_gamer_turn=())

SCHEMAS.update(historical_copy_party_crasher=(),historical_copy_party_recruit=(_private_draw_state,),historical_copy_party_attack=(_private_draw_state,))

SCHEMAS.update(historical_copy_kotori=(),historical_copy_targeted_recast=(_private_draw_state,))

SCHEMAS.update(historical_copy_pack_suitcase=(),historical_copy_unpack_suitcase=(),historical_copy_fortunes=(),historical_copy_mirage=(),historical_copy_mirage_tick=(_integer,),historical_copy_blank_mirror=())

SCHEMAS.update(historical_copy_future_board=(),historical_copy_future_return=(_integer,),historical_copy_future_one=(_integer,_integer),historical_copy_future_clear=(_integer,))

SCHEMAS.update(historical_copy_permanent_mirage=(),historical_copy_shuffle_extra=(),historical_copy_shuffle_hand=())

SCHEMAS.update(historical_copy_griftah=(),historical_copy_guess=(_text,))

SCHEMAS.update(historical_copy_botface=(),historical_copy_wrench=(),historical_copy_stitch=(),historical_copy_stitched_summon=(_seq,))

SCHEMAS.update(historical_copy_jerry=(),historical_copy_jerry_finish=(_private_draw_state,),historical_copy_stalladris=(),historical_copy_pathmaker=())

SCHEMAS.update(corpse_target_damage=(_integer,_integer),summon_fixed_random=(lambda value: _seq(value) and bool(value) and all(_text(cid) for cid in value),))

SCHEMAS.update(historical_copy_tnt_zone=(_one_of('hand','deck','board'),),historical_copy_chaos_gaze=(),historical_copy_chaos_expire=(_integer,),historical_copy_goldbeard=(),historical_copy_goldbeard_summon=(_private_draw_state,),historical_copy_goldbeard_step=(_private_draw_state,_integer),historical_copy_goldbeard_die=(_integer,))

SCHEMAS.update(historical_copy_ichman_recruit=(),historical_copy_thorignir=(),historical_copy_whelp_summon=(_private_draw_state,),historical_copy_whelp_attacks=(_private_draw_state,),historical_copy_kologarn_grab=(),historical_copy_kologarn_return=())

SCHEMAS.update(historical_ship_launch=(),historical_ship_definition_required=(),historical_ship_welder=(),historical_ship_discount=(),historical_ship_othaar=(),historical_ship_shipwright=())

SCHEMAS.update(historical_ship_thrusters=(),historical_ship_thruster_hit=(_integer,_integer),historical_ship_guiding=(),historical_ship_claw=(),historical_ship_reactor=(),historical_ship_battery=(),historical_ship_biopod=(),historical_ship_spire=(),historical_ship_capacitor=(),historical_ship_displace=(),historical_ship_bonus=(),historical_ship_ghost=(),historical_ship_battlecry=(),historical_ship_exodar=(),historical_ship_exodar_launch=(_private_draw_state,),historical_ship_exodar_choose=(_private_draw_state,),historical_ship_protocol=(_text,_private_draw_state),historical_ship_protocol_unbound=(),historical_ship_crew=(_text,))

SCHEMAS.update(historical_ship_tank=(_boolean,),historical_ship_thor=(_boolean,),historical_ship_tank_hit=(_private_draw_state,),historical_ship_tank_excess=(_private_draw_state,))

SCHEMAS.update(historical_copy_epoch=(),historical_copy_future_location=(),historical_copy_epoch_shuffle=(_text,),historical_copy_lordaeron=(),historical_copy_xenedar=(),historical_copy_nighthold=(),historical_copy_korune=(),historical_copy_korune_swap=(_private_draw_state,_private_draw_state),historical_copy_temple_earth=(),historical_copy_cardboard=())

SCHEMAS.update(historical_copy_cheese=(),historical_copy_cheese_tick=(_integer,),historical_copy_shaffar=())

SCHEMAS['historical_copy_ceaseless']=()

SCHEMAS.update(historical_copy_grunty=(),historical_copy_grunty_summon=(_private_draw_state,),historical_copy_grunty_offer=(_private_draw_state,))

SCHEMAS.update(historical_mutation_imp_oster=(),historical_copy_rafaam_imps=(_boolean,),historical_copy_buff_imps=(_integer,_integer))

SCHEMAS.update(historical_copy_bob_offer=(),historical_copy_plunder_offer=(),historical_copy_bob_coins=(),historical_copy_bob_triple=(),historical_copy_bob_copies=(_private_draw_state,),historical_copy_plunder_take=(_one_of('hand','deck'),_integer),historical_copy_plunder_one=(_one_of('hand','deck'),),historical_copy_plunder_ship=())

SCHEMAS.update(historical_copy_amulet_vendor=(),historical_copy_passions=(_boolean,),historical_copy_amulet_critter=(_boolean,),historical_copy_amulet_discount=(_boolean,),historical_copy_phony_tracking=(),historical_copy_tracking_create=(_private_draw_state,),historical_copy_tracking_transform=(_private_draw_state,),historical_copy_phony_mobility=(),historical_copy_mobility_discard=(_seq,))

SCHEMAS.update(historical_copy_xortoth=(),historical_copy_star_unplayable=(),historical_copy_star_collide=(_seq,))

SCHEMAS.update(historical_copy_remornia_equip=(),historical_copy_remornia_return=(),historical_copy_sanc_location=(),historical_copy_sanc_activate=())

SCHEMAS.update(historical_potion_begin=(_one_of('kazakus','mixologist'),),historical_potion_cost_guard=(),historical_potion_freeze=(_integer,),historical_potion_wool=(_boolean,))

SCHEMAS['crafted_spell']=()

SCHEMAS.update(historical_golem_begin=(),historical_golem_unbound=(),historical_golem_freeze=(_integer,),historical_golem_fire=(_integer,))

SCHEMAS.update(historical_copy_trade_finish=())

SCHEMAS.update(historical_horror_begin=(_pool_request,),historical_horror_unbound=(),historical_horror_cast=(_text,))

SCHEMAS.update(historical_rock_begin=(),historical_rock_unplayable=(),historical_rock_explode=(_integer,))

SCHEMAS.update(historical_mint_generate=(),historical_mint_skull=(),historical_mint_skull_draw=(),historical_mint_metamorphosis=(),historical_mint_warglaives=())

SCHEMAS.update(historical_headmaster_summon=(),historical_headmaster_one=(lambda value:hasattr(value,"card_id") and hasattr(value,"uid"),))

SCHEMAS.update(historical_eonar_prepare=())

SCHEMAS.update(historical_lens_open=(),historical_lens_cast=())

SCHEMAS.update(historical_velen_repeat=(),historical_velen_battlecry=(lambda value:isinstance(value,dict),),historical_velen_death=(lambda value:isinstance(value,dict),))

SCHEMAS.update(historical_ebon_horsemen=(),historical_ebon_check=(),historical_ebon_bladestorm=())

SCHEMAS.update(historical_dark_kurtrus=(),historical_dark_bat=(_integer,),historical_dark_siphon=())

SCHEMAS.update(historical_reckless_begin=(),historical_reckless_fire=(_integer,),historical_reckless_plague=(),historical_reckless_used=(),historical_reckless_mint_consumed=(_integer,))

SCHEMAS.update(historical_maestra_reveal=())

SCHEMAS.update(historical_late_slam=(),historical_late_smash=())

SCHEMAS.update(historical_guff_cap=(),historical_guff_crystal=(),historical_guff_random=(),historical_cariel_buff=())

SCHEMAS.update(historical_rhyssa_notify=(_text,),historical_rhyssa_transform=(_integer,),historical_rhyssa_bounce=(_integer,),historical_rhyssa_runes=(_integer,),historical_rhyssa_pressure=(),historical_rhyssa_resummon=(_text,_integer),historical_rhyssa_infinity=())

SCHEMAS['historical_harvester_steal']=()

SCHEMAS['historical_frozen_anduin']=()

SCHEMAS['mutation_board']=(_integer,_boolean)

SCHEMAS.update(historical_jaina_aura=(),historical_jaina_touch=(),historical_jaina_after=(lambda value:isinstance(value,Mapping),))

SCHEMAS['historical_scabbs_return']=()

SCHEMAS['historical_etc_discover']=()

SCHEMAS.update(historical_replay_hero=(_one_of('schools','played'),),historical_arcane_burst=(),historical_arcane_burst_after=(lambda value:isinstance(value,Mapping),))

SCHEMAS.update(historical_brukan_choose=(),historical_brukan_install=(_seq,),historical_brukan_lightning=())

SCHEMAS.update(historical_boom_rush=(),historical_boom_kaboom=())

SCHEMAS.update(historical_devout_replay=(),historical_devout_death=(lambda value:hasattr(value,'card_id'),),historical_devout_heal=())

SCHEMAS['historical_reno_poof']=()

SCHEMAS['autocast_random']=(_pool_request,_integer)

SCHEMAS.update(historical_valeera_stealth=(),historical_valeera_add=(),historical_valeera_unbound=())

SCHEMAS.update(historical_ignis_begin=(),historical_ignis_pain=(_integer,),historical_ignis_summon=(_integer,),historical_ignis_unbound=())

SCHEMAS.update(historical_tavish_begin=(),historical_tavish_continue=(_integer,_seq),historical_tavish_bounce=(_integer,),historical_tavish_pack=(lambda value:hasattr(value,'card_id'),),historical_tavish_companion=(),historical_tavish_cages=(_integer,),historical_tavish_ice=(lambda value:hasattr(value,'card_id'),_integer))

SCHEMAS['forge_zombeast_plain']=()

SCHEMAS['historical_holmes_begin']=()

SCHEMAS['historical_zilliax_validate']=()

# Physical held-card refresh; no production Uluu pool is implied.
SCHEMAS['historical_uluu_refresh']=(_integer,)

# Existing Standard Choose One handlers: exact no-argument weapon programs and
# the two literal Azshara location families accepted by the executable handler.
SCHEMAS.update(lasting_weapon_poison=(), lasting_weapon_death=())
SCHEMAS['azshara_empower']=(
 lambda value: _seq(value) and tuple(value) in (('TIME_211t1','TIME_211t1t'),('TIME_211t2','TIME_211t2t')),
 lambda value: _seq(value) and tuple(value) in (('TIME_211t1','TIME_211t1t'),('TIME_211t2','TIME_211t2t')))

SCHEMAS.update(historical_student_gift=(_one_of('portal','plague','ranked','dual'),),historical_student_omega=(),historical_student_awaken=())

SCHEMAS.update(generation_dynamic_summon=(_one_of('hand_size','remaining_mana','death_source_cost'),),discount_random_hand=(_one_of('friendly','enemy','both'),_filters,_integer))

for _student_op in ('murlocs','wrath','other_knife','flames','death'):
 SCHEMAS['historical_student_spell_'+_student_op]=()
for _student_op in ('chain','freeze','conviction'):
 SCHEMAS['historical_student_spell_'+_student_op]=(_integer,)
for _student_op in ('sacrifice','flames_finish'):
 SCHEMAS['historical_student_spell_'+_student_op]=(_private_draw_state,)

SCHEMAS['historical_student_expansion']=(_one_of('THE_SUNKEN_CITY','REVENDRETH','RETURN_OF_THE_LICH_KING','BATTLE_OF_THE_BANDS','TITANS','WILD_WEST','WHIZBANGS_WORKSHOP','YEAR_OF_THE_RAPTOR','YEAR_OF_THE_SCARAB'),)

for _outcome_op in ('attack_damage','purify','forged_flame','break_weapon','spell_poison'):
 SCHEMAS['historical_outcome_'+_outcome_op]=()

SCHEMAS.setdefault('destroy_self',())

for _equipment_op in ('fan_club','reborn','kennels','library','depths','dollhouse','gym','giant','expanse'):
 SCHEMAS['historical_equipment_'+_equipment_op]=()

SCHEMAS.update(historical_harmonic_popstar=(_integer,),historical_harmonic_metal=(_integer,_integer),historical_harmonic_swap=(_integer,_text))

SCHEMAS.setdefault('generation_fill_plain_hand',(_pool_request,))

SCHEMAS.update(historical_damage_then=(_integer,_one_of('dead','alive'),_seq),historical_damage_capture=(_integer,_private_draw_state),historical_damage_follow=(_one_of('dead','alive'),_private_draw_state,_seq),historical_damage_descend=(_integer,))
for _damage_op in ('hero_attack','discard_area','warband','unleash','blazing','undeath','ricochet','shelves','threads','volcano_bind','corpses','twilight','keeper'):
 SCHEMAS['historical_damage_'+_damage_op]=()

for _summon_op in ('imp_draw','lineup','pride','waltz','felfiends','embers','plant','lionfish','companions'):
 SCHEMAS['historical_summoning_'+_summon_op]=()
SCHEMAS.update(historical_summoning_naga_follow=(_seq,),historical_summoning_copy=(lambda value:hasattr(value,'card_id') and hasattr(value,'health'),),historical_summoning_stats=(_text,lambda value:_seq(value) and len(value)==2 and all(_integer(n) for n in value)))

for _forge_spell_op in ('draw_match','draw_combined','armor_damage','blackrock','ensmallen','distort','zombies','implocs','suffusion','campaign','campaign_death'):
 SCHEMAS['historical_forge_spell_'+_forge_spell_op]=()
SCHEMAS.update(historical_forge_spell_combine=(_private_draw_state,),historical_forge_spell_campaign_copy=(lambda value:hasattr(value,'card_id') and hasattr(value,'health'),),historical_forge_spell_random_damage=(_integer,))

for _discover_op in ('bronze','repeat_empty','blind_box','demonic'):
 SCHEMAS['historical_discover_'+_discover_op]=()
SCHEMAS['historical_discover_deck']=(_one_of('pendant','pit','navigation','quiver','chest','copy_one','copy_two'),)

for _movement_op in ('order','opponent_recruit','barrage','yogg_box','downsize','smelt','smelt_again','pay_armor','gear_shift','chum','manufacture','crane','posse','breakdance','bounce_all'):
 SCHEMAS['historical_movement_'+_movement_op]=()
for _movement_op in ('shuffle_uid','bounce_uid','ritual'):
 SCHEMAS['historical_movement_'+_movement_op]=(_integer,)
SCHEMAS.update(historical_movement_copy_minion=(lambda value:hasattr(value,'card_id') and hasattr(value,'health'),),historical_movement_copy_card=(lambda value:hasattr(value,'card_id') and hasattr(value,'uid'),_boolean),historical_movement_dancer=(lambda value:_seq(value) and len(value)==2 and all(_integer(n) for n in value),),historical_movement_discount_drawn=(_seq,))

SCHEMAS['historical_death_spell_resurrect']=(_one_of('large_beasts','small_all','small_one','last_demon','class_three','class_four'),)
for _death_spell_op in ('dead_air','destroy_target','spread','saddle','colossal_hands'):
 SCHEMAS['historical_death_spell_'+_death_spell_op]=()
SCHEMAS.update(historical_death_spell_summon=(lambda value:hasattr(value,'card_id'),lambda value:value is None or _seq(value) and len(value)==2 and all(_integer(n) for n in value)),historical_death_spell_destroy_uids=(_seq,),historical_death_spell_resummon_confirmed=(_private_draw_state,))

for _timed_op in ('alibi','inventor','dew','lightning','feast','elusive','tar','love','love_expire'):
 SCHEMAS['historical_timed_'+_timed_op]=()
SCHEMAS['historical_timed_inventor_expire']=(_integer,)

SCHEMAS.update(historical_secret_v2_buff_uid=(_integer,),historical_secret_v2_random_three=(),historical_secret_v2_highest_copy=(),historical_secret_v2_turn=(_integer,_integer))

for _misc_op in ('health_one','tribe_draw','showdown','soulcage','pay_five','enemy_next_cost','load_chamber','trolley_discard','fatigue_both'):
 SCHEMAS['historical_misc_'+_misc_op]=()
SCHEMAS.update(historical_misc_outlaw=(_integer,_boolean),historical_misc_cage_copy=(_integer,),historical_misc_fatigue_hit=(_integer,))

SCHEMAS.update(choicegen_undead_history=(_pool_request,),destroy_location=(),origin_clean_decks=(),force_enemies_into_source=())

for _numeric_op in ('mark','prescience','last_stand','arrow','eversong','switcheroo','whispers','bioluminescence','phial','ransack','jam_damage','cannibalize'):
 SCHEMAS['historical_numeric_'+_numeric_op]=()
SCHEMAS.update(historical_numeric_draw_finish=(_text,_private_draw_state),historical_numeric_spirit=(_private_draw_state,),historical_numeric_damage_capture=(_integer,_private_draw_state),historical_numeric_damage_finish=(_text,_private_draw_state),historical_numeric_swap_health=(_private_draw_state,_private_draw_state),historical_numeric_silence_snapshot=(_private_draw_state,),historical_numeric_attack_missiles=(_private_draw_state,),historical_numeric_heal_friendly=(_integer,))

# Physical historical zone spell programs.
for _zone_op in ("treant_draw","scrapper","cluster","recruits_buff","tram_heist","radar","spill","shuffle_deck"):
 SCHEMAS["historical_zone_"+_zone_op]=()
SCHEMAS.update(historical_zone_fetch=(_one_of("BEAST","PIRATE"),),historical_zone_fetch_finish=(_one_of("BEAST","PIRATE"),_private_draw_state),historical_zone_empty_crystals=(_integer,),historical_zone_destroy_bottom=(_integer,),historical_zone_draw_uid=(_integer,),historical_zone_recruit_uid=(_integer,_private_draw_state),historical_zone_spill_damage=(_private_draw_state,))

# Captured historical spell continuations; no runtime text interpretation.
for _resolution_op in ("soulfreeze","crescendo","kyrian","tether","eradication","heat_wave","funnel","drown","sentence","deathborne","weld"):
 SCHEMAS["historical_resolution_"+_resolution_op]=()
SCHEMAS.update(historical_resolution_fatigue=(_private_draw_state,),historical_resolution_fatigue_area=(_private_draw_state,),historical_resolution_tether_buff=(_private_draw_state,),historical_resolution_missile=(_private_draw_state,),historical_resolution_damage_uids=(_seq,_integer,_private_draw_state),historical_resolution_kill_reward=(_one_of("heal","skeleton"),_private_draw_state),historical_resolution_funnel_heal=(_integer,),historical_resolution_discard_uid=(_integer,))

# Complete-pool historical Discover spell declarations.
SCHEMAS.update(historical_offer_open=(_text,lambda value:_seq(value) and all(_pool_request(r) for r in value),_private_draw_state,lambda value:isinstance(value,str)),historical_offer_pair=(_one_of("stats","cost","gain_stats"),_pool_request,_pool_request),historical_offer_swap=(_one_of("stats","cost","gain_stats"),_private_draw_state),historical_offer_return=(),historical_offer_return_hand=(lambda value:hasattr(value,"card_id") and hasattr(value,"uid"),),historical_offer_rewind=())

for _attack_weapon_op in ("tempest","soulbreaker","watercannon","water_group"):
 SCHEMAS["historical_attack_weapon_"+_attack_weapon_op]=()
SCHEMAS["historical_attack_weapon_water_summon"]=(_private_draw_state,)

for _state_spell_op in ("frozen_copy","synchronize","steal","grace","dreams","front_lines","recruit_opponent","rampage","depths"):
 SCHEMAS["historical_state_"+_state_spell_op]=()
for _state_spell_op in ("heal_capture","grace_discover","hound","hound_buff"):
 SCHEMAS["historical_state_"+_state_spell_op]=(_private_draw_state,)
SCHEMAS["historical_state_fires"]=(_pool_request,)

# Physical historical spell choices retain private state and literal zone identity.
SCHEMAS.update(historical_physical_mixtape=(),historical_physical_draw_three=(lambda value:type(value) is bool,),historical_physical_draw_offer=(lambda value:type(value) is bool,_seq),historical_physical_offer=(_one_of("enemy_hand","enemy_deck","dispose","bell","fracking","companions","bud_spell","bud_minion","corpses"),),historical_physical_bell_draw=(_text,),historical_physical_companion_copy=(_private_draw_state,),historical_physical_draw_uid=(_integer,),historical_physical_destroy_uid=(_integer,),historical_physical_recruit=(_integer,_private_draw_state),historical_physical_copy_summon=(lambda value:hasattr(value,"card_id") and hasattr(value,"uid"),),historical_physical_resurrect=(lambda value:hasattr(value,"card_id") and hasattr(value,"uid"),))

for _literal_bonus_op in ("companion","inspiration","bandits","vortex","valkyr"):
 SCHEMAS["historical_bonus_"+_literal_bonus_op]=()
SCHEMAS["historical_bonus_deliver_bandit"]=(_text,)

SCHEMAS.update(historical_growing_weapon_death=(_text,),historical_growing_weapon_keyboard=(_integer,_integer),historical_growing_weapon_wear=(_integer,),historical_growing_weapon_durability=(_integer,))

for _change_spell_op in ("whirlpool","wave","align","blazing","tampering","shuffle_hand","discard_hand","hat"):
 SCHEMAS["historical_change_"+_change_spell_op]=()
SCHEMAS.update(historical_change_nostalgia=(_pool_request,),historical_change_demons=(_integer,),historical_change_board_one=(_integer,_seq),historical_change_hand_one=(_integer,_seq,_integer),historical_change_resurrect=(lambda value:hasattr(value,"card_id") and hasattr(value,"uid"),),historical_change_hat_finish=(_private_draw_state,))

for _lingering_spell_op in ("melomania","allies","groove","brand","reverberations","hand_copies"):
 SCHEMAS["historical_lingering_"+_lingering_spell_op]=()
SCHEMAS.update(historical_lingering_copy_attack=(_one_of("original","enemy"),lambda value:type(value) is bool),historical_lingering_kill_uid=(_integer,),historical_lingering_kill_copies=(_private_draw_state,),historical_lingering_attack_original=(_private_draw_state,_integer),historical_lingering_copy_board=(lambda value:hasattr(value,"uid") and hasattr(value,"card_id"),_private_draw_state,_text),historical_lingering_copy_hand=(lambda value:hasattr(value,"uid") and hasattr(value,"card_id"),_private_draw_state))

SCHEMAS.update(historical_music_symphony=(),historical_music_envy=(),historical_music_gluttony=(),historical_music_riff=(_text,),historical_music_replay=(_text,),historical_music_shuffle_movements=(_text,),historical_music_forbidden=(_one_of("attack","armor"),))

SCHEMAS['historical_held_spellstone_buff']=(_integer,)

for _volley_spell_op in ("toll","darts","fan","mishap","collateral","explosion","lightshow","ray","lowest","beam","detonate"):
 SCHEMAS["historical_volley_"+_volley_spell_op]=()
SCHEMAS.update(historical_volley_dart=(_private_draw_state,),historical_volley_coin=(_private_draw_state,),historical_volley_excess_hit=(_integer,_integer,_private_draw_state,lambda value:type(value) is bool),historical_volley_excess_follow=(_integer,_private_draw_state,lambda value:type(value) is bool))

for _utility_spell_op in ("potion","applause","recruit","convert_shield","maki_copy"):
 SCHEMAS["historical_utility_"+_utility_spell_op]=()
SCHEMAS["historical_utility_prison"]=(_integer,)

SCHEMAS['historical_utility_spotlight']=()

SCHEMAS.update(historical_secret_v3_sack_return=(),historical_secret_v3_azerite=(lambda value:hasattr(value,"uid") and hasattr(value,"card_id"),),historical_secret_v3_zombees=(_integer,),historical_secret_v3_kidnap=(_integer,),historical_secret_v3_zombee_group=(_integer,),historical_secret_v3_zombee_summon=(_private_draw_state,),historical_secret_v3_zombee_attacks=(_private_draw_state,_integer),historical_secret_v3_visage=(lambda value:hasattr(value,"uid") and hasattr(value,"card_id"),),historical_secret_v3_visage_group=(lambda value:hasattr(value,"uid") and hasattr(value,"card_id"),),historical_secret_v3_visage_summon=(lambda value:hasattr(value,"uid") and hasattr(value,"card_id"),_private_draw_state),historical_secret_v3_visage_attacks=(_private_draw_state,),historical_secret_v3_emergency=(_integer,lambda value:hasattr(value,"uid") and hasattr(value,"card_id"),_integer),historical_secret_v3_emergency_summon=(lambda value:hasattr(value,"uid") and hasattr(value,"card_id"),_integer))

for _location_timed_op in ("frozen","curse","ghost","vault","cove","hulk"):
 SCHEMAS["historical_location_timed_"+_location_timed_op]=()
SCHEMAS["historical_location_timed_lock"]=(_integer,_seq)

SCHEMAS.update(historical_bottle_swarm=(_integer,lambda value:type(value) is bool),historical_bottle_contents=(_one_of("bugs","damage","heal"),),historical_bottle_shadeleaf=(),historical_bottle_springwater=(),historical_bottle_shimmer=(),historical_bottle_capture_damage=(_integer,_private_draw_state))
for _bottle_op in ("bug_one","save_bugs","capture_heal","save_heal","save_damage","shimmer_summon"):
 SCHEMAS["historical_bottle_"+_bottle_op]=(_private_draw_state,)

SCHEMAS.update(historical_sleep_wild_spirits=(),historical_growing_weapon_axe=(_integer,_integer))

SCHEMAS.update(historical_music_roots=(_integer,_text))

SCHEMAS.update(historical_lingering_accusation=(_one_of('arson','murder','theft'),))

SCHEMAS.update(historical_music_projection=())

SCHEMAS.update(historical_timed_wheel=(),historical_timed_wheel_destroy=(),historical_timed_immolate=(),historical_timed_immolate_burn=(_integer,))

SCHEMAS.update(historical_timed_form=(),historical_timed_form_expire=(_integer,_integer),historical_timed_jormungar=())

SCHEMAS.update(historical_utility_pair_choice=(_one_of('fight','consume'),),historical_utility_pair_kill=(_integer,),historical_utility_pair_copy_dead=(_seq,))

SCHEMAS.update(historical_utility_misfire=(),historical_utility_nets=(),historical_utility_target_damage=(_integer,_text,_boolean),historical_utility_target_hit=(_integer,_integer))

SCHEMAS.update(historical_utility_gold=(),historical_utility_banner=())

SCHEMAS.update(historical_utility_wither=(),historical_utility_wither_steal=(_integer,_integer))

SCHEMAS.update(historical_utility_riot=(),historical_held_seedling_tick=(_integer,))

SCHEMAS.update(historical_utility_stargazing=(),historical_utility_arcane_draw=(_private_draw_state,),historical_utility_arcane_repeat=(_private_draw_state,),historical_utility_domino=(),historical_utility_domino_hit=(_integer,_integer))

SCHEMAS.update(historical_utility_mount=())

SCHEMAS.update(historical_physical_return_policy=(),historical_physical_policy_trigger=(lambda value:hasattr(value,'card_id') and hasattr(value,'uid'),))

SCHEMAS.update(historical_timed_deputization=(),historical_timed_deputization_expire=(_integer,))

SCHEMAS.update(historical_utility_multistrike=(),historical_utility_swing=(),historical_utility_hero_force=(_integer,))

SCHEMAS.update(historical_physical_repackage=(),historical_physical_box=(),historical_physical_box_add=(lambda value:hasattr(value,'card_id') and hasattr(value,'uid'),))

SCHEMAS.update(historical_utility_horseman=(),historical_utility_horseman_head=())

SCHEMAS.update(historical_utility_reno_clear=())

SCHEMAS.update(historical_utility_conductivity=())

SCHEMAS.update(historical_utility_pure_cold=(),historical_utility_disintegration=(),historical_utility_jars=(),historical_utility_embers=())

SCHEMAS.update(historical_utility_spyglass=(),historical_utility_banana_split=(),historical_utility_fangs=(),historical_utility_holy_book=(),historical_utility_holy_capture=(_integer,_private_draw_state),historical_utility_treasure_copy=(lambda value:hasattr(value,'uid') and hasattr(value,'health'),_boolean),historical_attack_weapon_phaoris=())

SCHEMAS.update(historical_utility_annoy=(),historical_utility_crusty=(),historical_utility_beauty=())

SCHEMAS['force_summon_group']=(_text,_integer,_one_of('target','random','random_enemy_minion','random_enemy_character','lowest','empty_deck_lowest'))

SCHEMAS.update(historical_utility_locusts=(),historical_utility_reflections=(),historical_utility_reflection_one=(lambda value:hasattr(value,'uid') and hasattr(value,'health'),),historical_utility_puzzle=(),historical_utility_puzzle_one=(_integer,_text))

SCHEMAS.update(historical_utility_quel_forge=())

SCHEMAS.update(historical_utility_demon_portal=(),historical_utility_portal_grow=())

SCHEMAS.update(historical_utility_ravage=(),historical_utility_ravage_ray=())

SCHEMAS.update(historical_utility_raynor=(),historical_utility_stimpack=(),historical_utility_relaunch=(lambda value:hasattr(value,'card_id') and hasattr(value,'uid'),))

SCHEMAS.update(historical_utility_yogg_wheel=(),historical_utility_yogg_outcome=(_integer,),historical_utility_yogg_random_casts=(_integer,),historical_utility_yogg_roast=(),historical_utility_yogg_rush=(),historical_utility_yogg_steal=())

SCHEMAS.update(historical_utility_harth=())

SCHEMAS.update(historical_utility_anomaly_end=(_text,))

SCHEMAS.update(historical_utility_anomaly_shuffle=(lambda value: hasattr(value,'card_id') and hasattr(value,'uid'),))

SCHEMAS.update(historical_utility_kazakusan=())

SCHEMAS.update(historical_utility_inner_rage=(),historical_utility_ice_lance=(),historical_utility_shadowstep=(),historical_utility_vampiric_blood=(),historical_utility_howling_blast=(),historical_utility_vanish=(),historical_utility_vanish_uid=(_integer,))
SCHEMAS.setdefault('refresh_mana',(_integer,))

SCHEMAS.update(historical_utility_blood_boil=(),historical_utility_boil_tick=(_integer,_integer),historical_utility_skull_tick=(_optional_integer,),historical_utility_refresh_all=())

SCHEMAS.update(historical_utility_paths=(_integer,),historical_utility_ice_block=(),historical_utility_plague=(),historical_utility_plague_again=())

SCHEMAS.update(historical_utility_frost_hand_copies=(),historical_utility_metamorphosis=(),historical_utility_attack_secret=(_text,_integer,_integer,_private_draw_state))

SCHEMAS.update(historical_utility_soul_mirror=(),historical_utility_mirror_copy=(lambda value:hasattr(value,"card_id") and hasattr(value,"max_health"),_private_draw_state),historical_utility_mirror_attacks=(_private_draw_state,),historical_utility_mirror_attack=(_integer,_integer),historical_utility_mirror_resolve=(_private_draw_state,))

SCHEMAS.setdefault("replay_friendly_deathrattle",())

SCHEMAS.setdefault("forge_sidequest",())

SCHEMAS.setdefault("forge_dragon",())

SCHEMAS.update({'historical_eudora_start':(),'historical_eudora_reward':()})

SCHEMAS.update({name:() for name in ('historical_tour_begin','historical_tour_mind_control','historical_tour_swipe','historical_tour_shadowflame','historical_tour_brawl','historical_tour_mortal','historical_tour_eviscerate','historical_copy_shadow_madness')})
SCHEMAS['historical_tour_generate']=(_text,)

SCHEMAS['destroy_battlefield']=()

SCHEMAS.update(historical_elise_shuffle=(),historical_elise_open=())

SCHEMAS.update({name:() for name in ('historical_ungoro_mimic','historical_ungoro_scales','historical_ungoro_envenom','historical_ungoro_spore','historical_ungoro_reflection','historical_ungoro_genesis','historical_ungoro_echo')})
SCHEMAS['historical_ungoro_cleave']=(_integer,_integer)

SCHEMAS.update({name:() for name in ('historical_ungoro_mist','historical_ungoro_explore','historical_ungoro_dinomancy','historical_ungoro_feeding')})
SCHEMAS['historical_ungoro_mist_destroy']=(_integer,)

SCHEMAS['historical_ungoro_stampede']=()
SCHEMAS['historical_ungoro_mana_bind']=(lambda value:hasattr(value,'card_id') and hasattr(value,'uid'),)

SCHEMAS.update(historical_ungoro_living=(),historical_ungoro_living_crystals=(_integer,))

SCHEMAS.update(historical_wisdomball_cast=(_integer,),historical_wisdomball_wear=(_integer,))

SCHEMAS.update(permanent_end_damage=(_integer,),random_heal=(_integer,),next_discount=(_text,_integer,_text))

SCHEMAS['historical_utility_zola_golden']=()

SCHEMAS['historical_zephrys_begin']=()

SCHEMAS['historical_scythe_discover']=()

SCHEMAS.update(historical_utility_unsleep_copy=(),historical_utility_ramming_speed=())

SCHEMAS.update(historical_utility_boom_squad=())

SCHEMAS.update(historical_utility_forbidden_words=())

SCHEMAS.update(draw_discount=(_integer,))

SCHEMAS.update(draw_discount=(_integer,),choose_unique_keyword=())

SCHEMAS.update(historical_utility_dark_skies=(),historical_utility_dark_skies_hit=())

SCHEMAS.update(historical_utility_plot_twist=(),historical_utility_plot_shuffle=(_seq,))

SCHEMAS.update(historical_utility_repeat_brew=())

SCHEMAS.update(held_scheme_area=())

SCHEMAS.update(quest_start=(_text,))

SCHEMAS.update(historical_utility_virnaal=())

SCHEMAS.update(tribe_board_buff=(_text,_integer,_integer))

SCHEMAS.update(historical_utility_crackle=(),historical_utility_primal_fusion=(),historical_utility_earthen_might=(),historical_utility_potion_illusion=())

SCHEMAS.update(historical_utility_transform_board=(_one_of('own','enemy','legendary'),_integer))

SCHEMAS.update(historical_utility_healing_wave=(),historical_utility_reincarnate=(),historical_utility_reincarnate_summon=(lambda value:hasattr(value,'card_id') and hasattr(value,'owner'),))

SCHEMAS.update(historical_utility_landslide=())

SCHEMAS.update(historical_utility_rockbiter=(),historical_utility_elemental_destruction=(),historical_utility_lightning_breath=())

SCHEMAS.update(historical_utility_vivid_spores=(),historical_utility_devolving_missiles=(),historical_utility_devolving_hit=())

SCHEMAS.update(historical_utility_elementary_reaction=())

SCHEMAS.update(historical_utility_runic=(_boolean,),historical_utility_runic_summon=(_boolean,))

SCHEMAS.update(historical_utility_charged_call=())

SCHEMAS.update(historical_utility_sapphire_copy=(_integer,))

SCHEMAS.update(historical_utility_moment_discovery=())

SCHEMAS.update(historical_utility_brukan=())

SCHEMAS.update(historical_utility_quest_accepted=())

SCHEMAS['historical_zephrys_wish']=()

SCHEMAS['gain_full_crystals']=(_integer,)

SCHEMAS.update(historical_utility_ramp_excess=(_integer,))

SCHEMAS.update(historical_utility_overdraft=())

SCHEMAS['copy_enemy_deck']=()

SCHEMAS['damage_lowest_health_enemy']=(_integer,)

SCHEMAS.update(historical_utility_protect_innocent=(),historical_utility_togwaggle_scheme=(),historical_utility_lightbomb=(),historical_utility_darkbomb=(),historical_utility_lackey_discover=())

SCHEMAS.update(historical_utility_eonar_draw=(),historical_utility_eonar_heal=(),historical_utility_eonar_after=(_integer,))

SCHEMAS['companions_random']=()

SCHEMAS.update(historical_utility_wish_attack=(_one_of('one','health','double'),),historical_utility_wish_savagery=(),historical_utility_wish_betrayal=(),historical_utility_wish_coldblood=(),historical_utility_wish_flare=(),historical_utility_wish_battlerage=(),historical_utility_wish_soulforest=(),historical_utility_wish_explosive=(),historical_utility_wish_bloodlust=(),swap_stats=(),destroy_gain_health=())

# Owner-authorized Avatar pack approximation uses the native zero-operand dispatcher.
SCHEMAS['standard_pack']=()

# Shared discard handler used by normal spells and weapon triggers.
SCHEMAS['discard_highest_cost']=()

# Physical recruitment declares its source zone and validated filter clauses.
SCHEMAS['summon_from_zone']=(_one_of('hand','deck'),_filters)

for name in ('historical_utility_pool_sheep','historical_utility_pool_shattering','historical_utility_pool_shatter','historical_utility_pool_flamecannon','historical_utility_pool_phaser','historical_utility_pool_dormant'):SCHEMAS[name]=()

for name in ('arcane_blast','flow','apexis','breath','icicle','cone','shooting','echo','simulacrum','sindragosa','forbidden','deep_breath','cram','snap','brilliance'):SCHEMAS['historical_utility_pool_'+name]=()
SCHEMAS['historical_utility_pool_draw_sequence']=(_text,_integer)
SCHEMAS['historical_utility_pool_draw_finish']=(_text,_private_draw_state)

SCHEMAS['historical_utility_pool_evocation']=()

for name in ('mystery','rally','horn','valanyr','reequip','sword','rod','farraki'):SCHEMAS['historical_utility_weapon_'+name]=()
SCHEMAS['historical_utility_weapon_shield']=(_integer,_boolean)
SCHEMAS['historical_utility_weapon_student']=(_integer,)
for name in ('discard_hand','alignment','cosmic'):SCHEMAS['historical_utility_state_'+name]=()

for name in ('supernova','huddle','ray'):SCHEMAS['historical_utility_pool_'+name]=()

for name in ('flow_target','waves'):SCHEMAS['historical_utility_pool_'+name]=()
SCHEMAS['historical_utility_pool_waves_finish']=(_integer,)

SCHEMAS.update(historical_secret_v2_mirror=(lambda value:hasattr(value,'card_id'),),historical_secret_v2_vaporize=(_integer,),historical_secret_v2_portal=())

SCHEMAS['historical_utility_pool_finale']=()

for name in ('wildfire','siphon','blast_wave'):SCHEMAS['historical_utility_pool_'+name]=()

for name in ('blast_damage','blast_rewards'):SCHEMAS['historical_utility_pool_'+name]=(_private_draw_state,)

for name in ('results','conjure'):SCHEMAS['historical_utility_pool_'+name]=()

SCHEMAS.update(historical_secret_v2_bender_summon=(_private_draw_state,),historical_secret_v2_death=(_integer,lambda value:hasattr(value,'card_id') and hasattr(value,'uid'),_integer),historical_secret_v2_effigy=(_integer,))

for name in ('ignite','combustion_target','tsunami'):SCHEMAS['historical_utility_pool_'+name]=()
SCHEMAS['historical_utility_pool_water_summon']=(_private_draw_state,)

SCHEMAS['historical_utility_pool_creation']=()
SCHEMAS['historical_utility_pool_ring']=(lambda value:type(value) is int and value in (1,2),)

for name in ('combustion','rolling','overflow'):SCHEMAS['historical_utility_pool_'+name]=()
SCHEMAS['historical_utility_pool_remnant']=(_integer,)

# Explicit authored Secret archive operations; all validation remains deferred.
for name in ('cache','companion'):SCHEMAS['historical_secret_v2_archive_'+name]=()
for name in ('shield','repent','justice','destroy'):SCHEMAS['historical_secret_v2_archive_'+name]=(_integer,)
SCHEMAS['historical_secret_v2_archive_hit']=(_integer,_integer)
SCHEMAS['historical_secret_v2_archive_copy']=(lambda value:hasattr(value,'uid') and hasattr(value,'card_id'),_one_of('pack','shadow'))
SCHEMAS['historical_secret_v2_archive_turn']=(_integer,_integer)

for name in ('evasion','avenge'):SCHEMAS['historical_secret_v2_archive_'+name]=()
SCHEMAS['historical_secret_v2_archive_dispatch']=(_one_of('damage','hero_power_used'),_private_draw_state)
SCHEMAS['historical_secret_v2_archive_death']=(_integer,lambda value:hasattr(value,'uid') and hasattr(value,'card_id'),_integer)
SCHEMAS['historical_secret_v2_archive_return']=(lambda value:hasattr(value,'uid') and hasattr(value,'card_id'),_integer)
SCHEMAS['historical_secret_v2_archive_redemption']=(lambda value:hasattr(value,'uid') and hasattr(value,'card_id'),_integer)
SCHEMAS['historical_secret_v2_archive_plagiarize_turn']=(_integer,_integer,_seq)
SCHEMAS['historical_secret_v2_archive_plagiarize_cards']=(_seq,)

SCHEMAS['historical_secret_v2_archive_ice_return']=(lambda value:hasattr(value,'uid') and hasattr(value,'card_id'),_integer)
SCHEMAS['historical_secret_v2_archive_redirect']=(_one_of('BT_042','EX1_130','LOOT_210'),_integer,_integer,_private_draw_state)

SCHEMAS['historical_secret_v2_archive_banana']=(lambda value:hasattr(value,'uid') and hasattr(value,'card_id'),)

for name in ('tower','tower_cast','fury','sea','burndown','lunacy','moonlit'):SCHEMAS['historical_utility_mage_deck_'+name]=()
for name in ('sea_summon','ignite_hand'):SCHEMAS['historical_utility_mage_deck_'+name]=(_private_draw_state,)

for name in ('font','pocket','gift'):SCHEMAS['historical_utility_mage_offer_'+name]=()
SCHEMAS['historical_utility_mage_offer_pocket_open']=(_private_draw_state,)
SCHEMAS['historical_utility_mage_offer_scroll_tick']=(_integer,)

SCHEMAS['historical_utility_mage_quest_sidequest']=(_one_of('DRG_323','DRG_324'),)
SCHEMAS['historical_utility_mage_quest_gambit']=(lambda value:type(value) is int and value in (0,1,2),)
for name in ('allies_reset','dawngrasp','school_offer'):SCHEMAS['historical_utility_mage_quest_'+name]=()

SCHEMAS['historical_utility_pool_rune']=()
SCHEMAS['historical_utility_pool_rune_step']=(_integer,)
SCHEMAS['historical_secret_v2_archive_yogg_replace']=(_integer,_integer)

for name in ('mulch','revive','spikeshell','opponent_crystals','gloop','germination','crystalsong','corrosive','embiggen','dreams','seeds','woods','recycle','toxic','infest','compost','trail','trail_begin'):SCHEMAS['historical_utility_nature_'+name]=()
SCHEMAS['historical_utility_nature_draw_sequence']=(_one_of('fungal','brochure_minion','brochure_spell'),_integer)
SCHEMAS['historical_utility_nature_draw_finish']=(_one_of('fungal','brochure_minion','brochure_spell'),_private_draw_state)
for name in ('heal_all','trail_end','bear_tick'):SCHEMAS['historical_utility_nature_'+name]=(_integer,)

_archive_minion=lambda value:hasattr(value,"uid") and hasattr(value,"health")
_archive_card=lambda value:hasattr(value,"uid") and hasattr(value,"card_id")
SCHEMAS['historical_utility_archive_admission_finish']=(_private_draw_state,_private_draw_state,)
SCHEMAS['historical_utility_archive_after_hit']=(_text,_private_draw_state,)
SCHEMAS['historical_utility_archive_altar']=()
SCHEMAS['historical_utility_archive_arsenal']=()
SCHEMAS['historical_utility_archive_attack_group']=(_one_of('BT_163t','VAC_445t'),_integer,)
SCHEMAS['historical_utility_archive_black_hole']=()
SCHEMAS['historical_utility_archive_blade_dance']=()
SCHEMAS['historical_utility_archive_bless']=()
SCHEMAS['historical_utility_archive_board_death']=(_one_of('ancestral','mech','murloc'),)
SCHEMAS['historical_utility_archive_board_stats']=(_one_of('lower','one','swap'),)
SCHEMAS['historical_utility_archive_bulk_up']=()
SCHEMAS['historical_utility_archive_cannons']=()
SCHEMAS['historical_utility_archive_chaos']=()
SCHEMAS['historical_utility_archive_circle']=(_integer,)
SCHEMAS['historical_utility_archive_cloak']=()
SCHEMAS['historical_utility_archive_coliseum']=()
SCHEMAS['historical_utility_archive_conceal']=()
SCHEMAS['historical_utility_archive_copy_snapshot']=(_archive_minion,)
SCHEMAS['historical_utility_archive_corpsicle']=()
SCHEMAS['historical_utility_archive_corruption']=()
SCHEMAS['historical_utility_archive_corruption_expire']=(_integer,_integer,)
SCHEMAS['historical_utility_archive_defrost']=()
SCHEMAS['historical_utility_archive_demonfire']=()
SCHEMAS['historical_utility_archive_destroy_sample']=(_integer,)
SCHEMAS['historical_utility_archive_devour']=()
SCHEMAS['historical_utility_archive_discount_hand_spells']=(_integer,)
SCHEMAS['historical_utility_archive_divine_favor']=()
SCHEMAS['historical_utility_archive_divine_spirit']=()
SCHEMAS['historical_utility_archive_dragon_shield']=()
SCHEMAS['historical_utility_archive_draw_finish']=(_text,_private_draw_state,)
SCHEMAS['historical_utility_archive_draw_state']=(_one_of('felfire','holy_wrath','portal','runeforging','soularium','vitality'),_integer,)
SCHEMAS['historical_utility_archive_ectomancy']=()
SCHEMAS['historical_utility_archive_escape']=()
SCHEMAS['historical_utility_archive_expire_target']=()
SCHEMAS['historical_utility_archive_expire_uid']=(_integer,_integer,)
SCHEMAS['historical_utility_archive_feast']=()
SCHEMAS['historical_utility_archive_felbolt']=()
SCHEMAS['historical_utility_archive_fill_undead']=()
SCHEMAS['historical_utility_archive_fishes']=()
SCHEMAS['historical_utility_archive_free_admission']=()
SCHEMAS['historical_utility_archive_fresh_summon']=(_archive_minion,_integer,_integer,)
SCHEMAS['historical_utility_archive_glowflies']=()
SCHEMAS['historical_utility_archive_graveyard']=()
SCHEMAS['historical_utility_archive_group_summon']=(_text,_private_draw_state,)
SCHEMAS['historical_utility_archive_hand_copy']=(_one_of('MINION'),)
SCHEMAS['historical_utility_archive_health_one']=()
SCHEMAS['historical_utility_archive_healthstone']=()
SCHEMAS['historical_utility_archive_hit_capture']=(_integer,_private_draw_state,)
SCHEMAS['historical_utility_archive_hit_follow']=(_integer,_one_of('deliverance','frostbite','glaive','holy_water','spring_trap','wanted'),)
SCHEMAS['historical_utility_archive_hounds']=()
SCHEMAS['historical_utility_archive_howl']=()
SCHEMAS['historical_utility_archive_hunting_party']=()
SCHEMAS['historical_utility_archive_immune']=()
SCHEMAS['historical_utility_archive_infiltrate']=()
SCHEMAS['historical_utility_archive_infinite_breath']=()
SCHEMAS['historical_utility_archive_jettison']=()
SCHEMAS['historical_utility_archive_kill_uid']=(_integer,)
SCHEMAS['historical_utility_archive_lackey']=()
SCHEMAS['historical_utility_archive_left_minion']=()
SCHEMAS['historical_utility_archive_lock_load']=()
SCHEMAS['historical_utility_archive_lose_armor']=(_integer,)
SCHEMAS['historical_utility_archive_mind_vision']=()
SCHEMAS['historical_utility_archive_molten_breath']=()
SCHEMAS['historical_utility_archive_myra']=()
SCHEMAS['historical_utility_archive_naaru']=()
SCHEMAS['historical_utility_archive_neighbors']=(_integer,)
SCHEMAS['historical_utility_archive_nether_breath']=()
SCHEMAS['historical_utility_archive_omega']=()
SCHEMAS['historical_utility_archive_opponent_cards']=(_integer,_one_of('deck','hand'),_boolean,)
SCHEMAS['historical_utility_archive_opponent_summon']=(_one_of('AT_036t'),_integer,)
SCHEMAS['historical_utility_archive_petting']=()
SCHEMAS['historical_utility_archive_piercing']=()
SCHEMAS['historical_utility_archive_pursuit']=()
SCHEMAS['historical_utility_archive_reborn_all']=()
SCHEMAS['historical_utility_archive_repeat_hand']=(_one_of('AV_285','DMF_225'),)
SCHEMAS['historical_utility_archive_resummon']=()
SCHEMAS['historical_utility_archive_return_card']=(_archive_card,)
SCHEMAS['historical_utility_archive_revenge']=()
SCHEMAS['historical_utility_archive_secret_plan']=()
SCHEMAS['historical_utility_archive_sermon']=()
SCHEMAS['historical_utility_archive_silence_enemies']=()
SCHEMAS['historical_utility_archive_slope']=()
SCHEMAS['historical_utility_archive_snack']=()
SCHEMAS['historical_utility_archive_snowed']=()
SCHEMAS['historical_utility_archive_swap_target']=()
SCHEMAS['historical_utility_archive_sweep_finish']=(_text,_private_draw_state,)
SCHEMAS['historical_utility_archive_sweep_hit']=(_integer,_private_draw_state,)
SCHEMAS['historical_utility_archive_sweep_reward']=(_integer,_one_of('armor','burn'),)
SCHEMAS['historical_utility_archive_totemic']=()
SCHEMAS['historical_utility_archive_upgrade']=()
SCHEMAS['historical_utility_archive_weapons_project']=()

SCHEMAS['temporary_attack_buff']=(_integer,)
SCHEMAS['opponent_next_turn_cost']=(_text,_integer)

SCHEMAS['historical_utility_continuation_adjacent_damage']=(_integer,)
SCHEMAS['historical_utility_continuation_battle_rage_copies']=()
SCHEMAS['historical_utility_continuation_buff_enemy_count']=()
SCHEMAS['historical_utility_continuation_copy_target']=()
SCHEMAS['historical_utility_continuation_crushing_walls']=()
SCHEMAS['historical_utility_continuation_deck_buff']=(_integer,_integer,)
SCHEMAS['historical_utility_continuation_demonheart']=()
SCHEMAS['historical_utility_continuation_destroy_low']=()
SCHEMAS['historical_utility_continuation_discount_random_spell']=(_integer,)
SCHEMAS['historical_utility_continuation_doom']=()
SCHEMAS['historical_utility_continuation_draw_if_beast']=()
SCHEMAS['historical_utility_continuation_enemy_attack_one']=()
SCHEMAS['historical_utility_continuation_enemy_deck_copies']=(_integer,_boolean,)
SCHEMAS['historical_utility_continuation_enemy_hand_discount']=(_integer,)
SCHEMAS['historical_utility_continuation_fel_gorger_damage']=()
SCHEMAS['historical_utility_continuation_flurry']=()
SCHEMAS['historical_utility_continuation_forbidden_heal']=()
SCHEMAS['historical_utility_continuation_gift']=(_text,)
SCHEMAS['historical_utility_continuation_give_target']=()
SCHEMAS['historical_utility_continuation_halve_decks']=()
SCHEMAS['historical_utility_continuation_harbor']=()
SCHEMAS['historical_utility_continuation_heal_friends']=(_integer,)
SCHEMAS['historical_utility_continuation_malt']=()
SCHEMAS['historical_utility_continuation_odd_destroy']=()
SCHEMAS['historical_utility_continuation_outcast_opponent_draw']=()
SCHEMAS['historical_utility_continuation_overwhelm']=()
SCHEMAS['historical_utility_continuation_pilfer']=()
SCHEMAS['historical_utility_continuation_random_attack']=(_integer,)
SCHEMAS['historical_utility_continuation_random_buff']=(_integer,_integer,)
SCHEMAS['historical_utility_continuation_random_hand_beast']=()
SCHEMAS['historical_utility_continuation_reckless']=()
SCHEMAS['historical_utility_continuation_reserved']=()
SCHEMAS['historical_utility_continuation_shuffle_hand_copies']=()
SCHEMAS['historical_utility_continuation_top_demon']=(_pool_request,)
SCHEMAS['historical_utility_continuation_trigger_all']=()

SCHEMAS['historical_utility_physical_lens']=()
SCHEMAS['historical_utility_physical_gallery']=()
SCHEMAS['historical_utility_physical_small_beasts']=()
SCHEMAS['historical_utility_physical_mindgames']=()
SCHEMAS['historical_utility_physical_darkest']=()
SCHEMAS['historical_utility_physical_nightmare']=()
SCHEMAS['historical_utility_physical_opponent_hand']=()
SCHEMAS['historical_utility_physical_whelps']=()
SCHEMAS['historical_utility_physical_deck_copy']=(_integer,_integer,)
SCHEMAS['historical_utility_physical_draw_conditional']=(_one_of("beast","copies","dragon","health"),)
SCHEMAS['historical_utility_physical_draw_finish']=(_one_of("beast","copies","dragon","health"),_private_draw_state,)
SCHEMAS['historical_utility_physical_lens_finish']=(_private_draw_state,_private_draw_state,)
SCHEMAS['historical_utility_physical_kill_group']=(lambda value:_seq(value) and all(_integer(uid) for uid in value),)
SCHEMAS['historical_utility_physical_summon_copy']=(_archive_card,lambda value:value is None or (_seq(value) and len(value)==2 and all(_integer(n) and n>0 for n in value)),)

SCHEMAS['historical_utility_repeat_batch_start']=(_one_of('storm','blade','snow','flame'),)
for _repeat_name in ('step','after','hit'):SCHEMAS['historical_utility_repeat_batch_'+_repeat_name]=(_private_draw_state,)
for _repeat_name in ('demon_discount','launch_discount'):SCHEMAS['historical_utility_repeat_batch_'+_repeat_name]=()

SCHEMAS['historical_utility_finish_batch_ship_draw']=()
SCHEMAS['historical_utility_finish_batch_ship_damage']=()
SCHEMAS['historical_utility_finish_batch_ship_destroy']=()
SCHEMAS['historical_utility_finish_batch_quasar']=()
SCHEMAS['historical_utility_finish_batch_pouch']=()
SCHEMAS['historical_utility_finish_batch_forbidden_minion']=()
SCHEMAS['historical_utility_finish_batch_tentacles']=()
SCHEMAS['historical_utility_finish_batch_duelists']=()
SCHEMAS['historical_utility_finish_batch_pawns']=()
SCHEMAS['historical_utility_finish_batch_lightwarden']=()
SCHEMAS['historical_utility_finish_batch_scheduled_heal']=()
SCHEMAS['historical_utility_finish_batch_defense']=()
SCHEMAS['historical_utility_finish_batch_survival']=()
SCHEMAS['historical_utility_finish_batch_four_buffs']=()
SCHEMAS['historical_utility_finish_batch_kill_uid']=(_integer,)
SCHEMAS['historical_utility_finish_batch_heal_uid']=(_integer,_integer,)
SCHEMAS['historical_utility_finish_batch_damage_group']=(lambda value:_seq(value) and all(_integer(uid) for uid in value),)

SCHEMAS['historical_utility_mount_batch_attach']=(_seq,)
for _mount_name in ('delayed_dreadsteed','resummon_one_health','recruit'):SCHEMAS['historical_utility_mount_batch_'+_mount_name]=()

SCHEMAS['historical_utility_history_batch_resurrect']=(_one_of('all_murlocs','costs','beasts_turn','deathrattle_small','highest_both','highest_taunts'),)
SCHEMAS['historical_utility_history_batch_summon']=(_integer,_text,lambda value:value is None or (_seq(value) and len(value)==2 and all(_integer(n) and n>0 for n in value)))
SCHEMAS['historical_utility_history_batch_death_hand']=()
SCHEMAS['historical_utility_history_batch_offer']=(_one_of('resurrect','nine_lives','phylactery'),)

SCHEMAS['historical_utility_stone_finish_diamond']=(_integer,)
SCHEMAS['historical_utility_stone_finish_tick']=(_integer,)
SCHEMAS['historical_utility_stone_finish_scheme']=(_one_of('armor','attack'),)

SCHEMAS['historical_utility_zone_spell_revolve']=()
SCHEMAS['historical_utility_zone_spell_evolve_copy']=()
SCHEMAS['historical_utility_zone_spell_demonic_project']=()
SCHEMAS['historical_utility_zone_spell_council']=()
SCHEMAS['historical_utility_zone_spell_deviate']=()
SCHEMAS['historical_utility_zone_spell_scream']=()
SCHEMAS['historical_utility_zone_spell_entomb']=()
SCHEMAS['historical_utility_zone_spell_glide']=()
SCHEMAS['historical_utility_zone_spell_parrrley']=()
SCHEMAS['historical_utility_zone_spell_frenzy']=()
SCHEMAS['historical_utility_zone_spell_espionage']=()
SCHEMAS['historical_utility_zone_spell_shuffle_hand']=()
SCHEMAS['historical_utility_zone_spell_transform_uid']=(_integer,_pool_request,_boolean,)
SCHEMAS['historical_utility_zone_spell_transform_group']=(lambda value:_seq(value) and all(_seq(row) and len(row)==2 and all(_integer(n) for n in row) for row in value),)

SCHEMAS['historical_utility_damage_finish_hit']=(_integer,_text,)
SCHEMAS['historical_utility_damage_finish_implosion']=()
SCHEMAS['historical_utility_damage_finish_capture']=(_integer,_integer,_private_draw_state,)
SCHEMAS['historical_utility_damage_finish_after']=(_private_draw_state,)
SCHEMAS['historical_utility_damage_finish_area']=(_integer,_one_of("excess_hero","spirits","honor_attack"),)
SCHEMAS['historical_utility_damage_finish_area_hit']=(_integer,_private_draw_state,)
SCHEMAS['historical_utility_damage_finish_area_after']=(_one_of("excess_hero","spirits","honor_attack"),_private_draw_state,)
SCHEMAS['historical_utility_damage_finish_hand_gain']=(_integer,)
SCHEMAS['historical_utility_damage_finish_bola']=()

SCHEMAS['historical_utility_combat_spell_start']=(_one_of("zooka","duel","provoke","predator","mass","hysteria","bees","birds","resurrect_attackers","return_attackers","recruit_return"),)
SCHEMAS['historical_utility_combat_spell_group']=(_private_draw_state,)
SCHEMAS['historical_utility_combat_spell_attack']=(_integer,_integer,_one_of("random_enemy","random_other","bound"),)
SCHEMAS['historical_utility_combat_spell_duel']=(_private_draw_state,)
SCHEMAS['historical_utility_combat_spell_hysteria']=(_integer,_integer,)
SCHEMAS['historical_utility_combat_spell_recover']=(_private_draw_state,)
SCHEMAS['historical_utility_combat_spell_recruit']=(_integer,_private_draw_state,)
SCHEMAS['historical_utility_combat_spell_summon']=(_text,_private_draw_state,)
SCHEMAS['historical_utility_combat_spell_kill']=(_private_draw_state,)
SCHEMAS['historical_utility_combat_spell_return']=(_integer,_integer,)

SCHEMAS['force_recruit_pair']=(_filters,)

SCHEMAS['historical_utility_sidequest_batch_start']=(_one_of('DRG_008','DRG_051','DRG_251','DRG_255','DRG_258','DRG_317'),)
SCHEMAS['historical_utility_sidequest_batch_sanctuary']=(_integer,)

SCHEMAS['historical_utility_aura_finish_aura']=(_one_of('bridge','strife','crusader','spawning','lifesaving','celestial','graveyard'),)
SCHEMAS['historical_utility_aura_finish_expire']=(_integer,)
SCHEMAS['historical_utility_aura_finish_attach_attack']=(_one_of('glory','wisdom'),)
SCHEMAS['historical_utility_aura_finish_curse']=()

SCHEMAS['historical_utility_condition_batch_ritual']=()
SCHEMAS['historical_utility_condition_batch_breach']=()
SCHEMAS['historical_utility_condition_batch_breach_repeat']=()
SCHEMAS['historical_utility_condition_batch_omen']=()
SCHEMAS['historical_utility_condition_batch_clarity']=()
SCHEMAS['historical_utility_condition_batch_divinity']=()
SCHEMAS['historical_utility_condition_batch_faith']=()
SCHEMAS['historical_utility_condition_batch_commence']=()
SCHEMAS['historical_utility_condition_batch_barricade']=()
SCHEMAS['historical_utility_condition_batch_felosophy']=()
SCHEMAS['historical_utility_condition_batch_fiend']=()
SCHEMAS['historical_utility_condition_batch_aimed']=()
SCHEMAS['historical_utility_condition_batch_heights']=()
SCHEMAS['historical_utility_condition_batch_luminance']=()
SCHEMAS['historical_utility_condition_batch_hero_health']=(_integer,)
SCHEMAS['historical_utility_condition_batch_faith_one']=(_private_draw_state,)
SCHEMAS['historical_utility_condition_batch_shield_recruit']=(_private_draw_state,)
SCHEMAS['historical_utility_condition_batch_return']=(_archive_card,)

SCHEMAS['historical_utility_generation_finish_metal']=()
SCHEMAS['historical_utility_generation_finish_repeat_ray']=()

SCHEMAS['historical_utility_deck_finish_guess']=()
SCHEMAS['historical_utility_deck_finish_draw_deaths']=(_integer,_optional_filters,)
SCHEMAS['historical_utility_deck_finish_trigger_state']=(_private_draw_state,)
SCHEMAS['historical_utility_deck_finish_trigger_card']=(_archive_card,)
SCHEMAS['historical_utility_deck_finish_guess_offer']=(_private_draw_state,)
SCHEMAS['historical_utility_deck_finish_offer']=(_one_of("triangulate","soul","masters","grave"),)
SCHEMAS['historical_utility_deck_finish_draw_uid']=(_integer,_private_draw_state,)
SCHEMAS['historical_utility_deck_finish_publish_all']=(_private_draw_state,)
SCHEMAS['historical_utility_deck_finish_shuffle_copies']=(_archive_card,)

SCHEMAS['historical_utility_delayed_finish_resummon_twice']=()
SCHEMAS['historical_utility_delayed_finish_voodoo']=()
SCHEMAS['historical_utility_delayed_finish_death_roll']=()
SCHEMAS['historical_utility_delayed_finish_sensory']=()
SCHEMAS['historical_utility_delayed_finish_embrace']=()
SCHEMAS['historical_utility_delayed_finish_talismans']=()
SCHEMAS['historical_utility_delayed_finish_agony']=()
SCHEMAS['historical_utility_delayed_finish_curse_enemy']=()
SCHEMAS['historical_utility_delayed_finish_attach']=(_seq,)
SCHEMAS['historical_utility_delayed_finish_summon_card']=(_archive_card,)
SCHEMAS['historical_utility_delayed_finish_copy']=(_archive_minion,)
SCHEMAS['historical_utility_delayed_finish_sensory_after']=(_integer,)
SCHEMAS['historical_utility_delayed_finish_control']=(_integer,_integer,)

SCHEMAS['historical_utility_delayed_finish_held_curse_damage']=()

SCHEMAS['historical_utility_repeat_batch_zerg_buff']=()

SCHEMAS['historical_utility_identified_recruit']=()
SCHEMAS['historical_utility_identified_turncoat']=()
SCHEMAS['historical_utility_identified_shadow']=()
SCHEMAS['historical_utility_identified_hope']=()
SCHEMAS['historical_utility_identified_return']=()
SCHEMAS['historical_utility_identified_adjacent']=(_archive_minion,_seq,_integer,_seq,)
SCHEMAS['historical_utility_trade_finish_shipment']=()
SCHEMAS['historical_utility_trade_finish_amulet']=()
SCHEMAS['historical_utility_trade_finish_biscuit']=()

SCHEMAS['historical_utility_summon_finish_scheme']=()
SCHEMAS['historical_utility_summon_finish_companions']=()
SCHEMAS['historical_utility_summon_finish_cannon']=()
SCHEMAS['historical_utility_summon_finish_banelings']=()
SCHEMAS['historical_utility_summon_finish_orbital_discover']=()
SCHEMAS['historical_utility_summon_finish_entree']=()
SCHEMAS['historical_utility_summon_finish_consume']=()
SCHEMAS['historical_utility_summon_finish_explode']=()
SCHEMAS['historical_utility_summon_finish_rat']=()
SCHEMAS['historical_utility_summon_finish_banana']=()
SCHEMAS['historical_utility_summon_finish_forbid']=()
SCHEMAS['historical_utility_summon_finish_time_out']=()
SCHEMAS['historical_utility_summon_finish_zerg_rush']=()
SCHEMAS['historical_utility_summon_finish_siren']=()
SCHEMAS['historical_utility_summon_finish_orbital_reborn']=()
SCHEMAS['historical_utility_summon_finish_meeting']=(_pool_request,)
SCHEMAS['companion_random_series']=(_integer,)

SCHEMAS['historical_utility_stormwind_discount_drawn']=()
SCHEMAS['historical_utility_stormwind_kurtrus']=()
SCHEMAS['historical_utility_stormwind_seed_reward']=()
SCHEMAS['historical_utility_stormwind_tamsin']=()
SCHEMAS['historical_utility_stormwind_tavish']=()
SCHEMAS['historical_utility_stormwind_target_power']=()
SCHEMAS['historical_utility_stormwind_zero_power']=()
SCHEMAS['historical_utility_stormwind_upgrade_power']=()
SCHEMAS['historical_utility_stormwind_distractor']=()
SCHEMAS['historical_utility_stormwind_gyroblade']=()
SCHEMAS['historical_utility_stormwind_warrior_weapon']=()
SCHEMAS['historical_utility_stormwind_gizmo']=()
SCHEMAS['historical_utility_stormwind_shard']=()
SCHEMAS['historical_utility_stormwind_begin']=(_text,)
SCHEMAS['historical_utility_stormwind_juggernaut']=(_integer,)

SCHEMAS['open_permanent']=(_text,)
SCHEMAS['recruit_bonus']=(_integer,_integer)

for _final_combat_name in ("cleave","hero_minions_only","hero_cleave"):
 SCHEMAS["historical_utility_final_combat_"+_final_combat_name]=()

for _audit_name in ('front','bones','different_types','skirt'):
 SCHEMAS['historical_utility_audit_'+_audit_name]=()
SCHEMAS['historical_utility_audit_bones_continue']=(lambda value:isinstance(value,dict),)

SCHEMAS['historical_utility_audit_icecrown']=()
SCHEMAS['historical_utility_audit_blackrock']=()
SCHEMAS['historical_utility_audit_brochure_damage']=(_integer,lambda value:isinstance(value,tuple) and all(type(x) is int for x in value),_boolean)

SCHEMAS['historical_utility_audit_doomerang']=()
SCHEMAS['historical_utility_audit_weapon_hit']=(_integer,)
SCHEMAS['historical_utility_audit_weapon_return']=(lambda value:isinstance(value,dict) and set(value)=={'card','weapon'},)

# Explicit historical physical obligations.
for _name in ('mana_burn','shout','flanking','performers','acrobatics','passage','shadows','shadow_summon','comet'):
 SCHEMAS['historical_utility_obligation_'+_name]=()
for _name in ('acrobatics_arm','summon_arm'):
 SCHEMAS['historical_utility_obligation_'+_name]=(_integer,)
SCHEMAS['historical_utility_obligation_watched_summon']=(_text,_integer)

for _name in ('yoink','guidance','guidance_both'):
 SCHEMAS['historical_utility_obligation_'+_name]=()
SCHEMAS['historical_utility_obligation_yoink_used']=(_integer,)

for _name in ('kangor','impfestation','champions'):
 SCHEMAS['historical_utility_final_roots_'+_name]=()
SCHEMAS['historical_utility_final_roots_dwarf']=(_pool_request,)
SCHEMAS['historical_utility_final_roots_dwarf_one']=(_seq,lambda value:isinstance(value,dict))
SCHEMAS['historical_utility_final_roots_imp_pair']=(_integer,)
for _name in ('imp_summon','imp_attacks'):
 SCHEMAS['historical_utility_final_roots_'+_name]=(lambda value:isinstance(value,dict),)
SCHEMAS['historical_utility_final_roots_mech_return']=(lambda value:isinstance(value,str) or hasattr(value,'card_id'),)
SCHEMAS['historical_utility_final_roots_darkness']=(_boolean,)
SCHEMAS['historical_utility_final_roots_champion_side']=(_one_of('alliance','horde'),)

SCHEMAS['historical_utility_obligation_passage_restore']=(_integer,_integer)

# Opaque immutable stored-definition reference; no private Card in public effects.
SCHEMAS['mutation_restore_learned']=(_integer,)
