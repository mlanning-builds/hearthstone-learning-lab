"""Explicit historical event keywords with physical one-use state.

Implementation pass only. Shared phase ordering and client conformance remain
unverified; no generation membership is restricted to executable outcomes.
"""
from .generation_cards import pool,random_cards

FRENZY={
 'BAR_031':[('historical_prime_raptor',2,1)],
 'BAR_020':[('historical_keyword_force_enemy',)],
 'BAR_021':[('historical_keyword_event_armor',)],
 'BAR_022':[random_cards(pool(card_type='SPELL',classes='own'))],
 'BAR_024':[('damage_enemy_hero',3)],
 'BAR_025':[('keyword_self','DIVINE_SHIELD')],
 'BAR_070':[('summon','BAR_070',1)],
 'BAR_071':[('destroy_random_enemy',1)],
 'BAR_073':[('buff_others',2,2)],
 'BAR_078':[('historic_source_attack_area','enemy')],
 'BAR_320':[('historical_keyword_discount_hand',1)],
 'BAR_538':[('historical_keyword_transform_source','BAR_538t')],
 'BAR_840':[('area_damage','other_minions',1)],
 'BAR_843':[('historical_keyword_damaged_attack',1)],
 'BAR_896':[('draw',1)],
 'ONY_003':[('draw',1)],
 'WC_026':[('armor',8)],
}
SPELLBURST={
 'SCH_182':[('buff_spell_cost',1,1)],
 'SCH_230':[random_cards(pool(card_type='SPELL',classes='own'),2)],
 'SCH_231':[('buff_self',2,0)],
 'SCH_232':[('buff_self',1,0),('keyword_self','TAUNT')],
 'SCH_234':[random_cards(pool(mechanic='COMBO'))],
 'SCH_236':[('historical_keyword_copy_cast_spell',)],
 'SCH_239':[('destroy_random_enemy',1)],
 'SCH_241':[('historical_batch_missiles','enemy',4)],
 'SCH_242':[('summon','SCH_242',1)],
 'SCH_243':[('summon','NEW1_012',2)],
 'SCH_248':[('historic_bounce_source',)],
 'SCH_313':[('area_damage','other_minions',2)],
 'SCH_532':[('keyword_self','DIVINE_SHIELD')],
 'SCH_614':[('historic_refresh_all_mana',)],
 'GDB_134':[('summon','GDB_134',1)],
 'GDB_310':[('filtered_draw',(('type','eq','SPELL'),),2)],
 'GDB_311':[('historical_keyword_spell_cost_minion',)],
 'GDB_322':[('keyword_self','DIVINE_SHIELD')],
 'GDB_330':[('force_source_random',)],
 'GDB_454':[('historical_keyword_silence_source',)],
 'GDB_463':[('filtered_draw',(('type','eq','MINION'),('tribe','eq','DRAENEI')),1)],
 'GDB_855':[('hero_attack',8),('armor',8)],
 'GDB_860':[('double_self_attack',)],
 'GDB_870':[('buff_self',2,0),('keyword_self','STEALTH')],
 'YOP_020':[('historical_keyword_frozen_enemy_damage',3)],
}
OVERHEAL={
 'AT_011':[('buff_self',2,0)],
 'CFM_606':[('summon','CFM_606t',1)],
 'CS3_014':[('draw',1)],
 'ETC_334':[('damage_random_enemy',5)],
 'ETC_339':[('historical_keyword_overheal_minion',)],
 'WW_381':[('area_damage','enemy_minions',2)],
}
HONORABLE={'AV_124':[('summon','AV_211t',1)],
 'AV_121':[('buff_self',2,0)],
 'AV_122':[('historical_keyword_other_shields',)],
 'AV_123':[('next_power_set_cost',0)],
 'AV_131':[('buff_self',3,3)],
 'AV_132':[('damage_enemy_hero',8)],
 'AV_215':[('keyword_self','WINDFURY')],
 'AV_340':[('heal_own_hero',4)],
 'AV_565':[('filtered_draw',(('type','eq','WEAPON'),),1)],
 'ONY_003':[('draw',1)],
}
OVERKILL={
 'TRL_010':[('armor',3)],
 'TRL_015':[('draw',2)],
 'TRL_020':[('summon','TRL_020t',2)],
 'TRL_232':[('summon','TRL_232t',1)],
 'TRL_329':[('historical_draw_batch',(('type','eq','MINION'),('mechanic','eq','RUSH')),'buff',(5,5),'random')],
 'TRL_506':[('buff_self',5,0)],
 'TRL_521':[('summon','TRL_521',1)],
 'TRL_528':[('double_self_attack',)],
 'TRL_542':[('summon_from_zone','hand',(('type','eq','MINION'),('tribe','eq','BEAST')))],
}
FRENZY['WC_008']=[('summon','BAR_035t',4)]
SPELLBURST['SCH_157']=[('historical_keyword_cast_same_cost',)]
SPELLBURST['YOP_010']=[('historic_board_keyword','friendly','DIVINE_SHIELD','permanent')]
SPELLBURST['GDB_226']=[('area_damage','other_minions',2)]
for table in (FRENZY,SPELLBURST,HONORABLE,OVERKILL):table['WON_143']=[random_cards(pool(card_type='MINION',minimum=1,maximum=1),destination='board')]
HONORABLE.update({cid:[('draw',1)] for cid in ('TOY_312','TOY_312t')})
SPELLBURST.update({cid:[('buff_self',2,2)] for cid in ('TOY_340','TOY_340t1')})

OVERHEAL['JAM_024']=[('buff_random_other',2,2)]
SPELLBURST['GDB_116']=[('historical_play_shuffle_hand',)]
HONORABLE['AV_313']=[('historical_keyword_gain_victim_attack',)]
from .historical_resource_batches import SPELLBURST as RESOURCE_SPELLBURST
SPELLBURST.update(RESOURCE_SPELLBURST)
TABLES={'frenzy':FRENZY,'spellburst':SPELLBURST,'overheal':OVERHEAL,'honorable':HONORABLE,'overkill':OVERKILL}
SPELLBURST['YOP_018']=[('historical_treasure_ivory_copy',)]
SPELLBURST['SCH_141']=[('historical_copy_cast_zone','own','deck',None,'random','prefer_source')]
SPELLBURST['SCH_224']=[('historical_headmaster_summon',)]
RULES={cid:('none',[]) for table in TABLES.values() for cid in table}
RULES.update({
 'GDB_226':('none',[('area_damage','other_minions',2)]),
 'BAR_840':('none',[('area_damage','other_minions',1)]),
 'SCH_248':('minion',[('damage',1)]),
 'ETC_334':('none',[('damage_self',4)]),
 'WW_381':('none',[('damage_self',4)]),
 'AV_131':('character',[('damage',3)]),
 'GDB_870':('none',[('historical_if_combo',('buff_self',2,0)),('historical_if_combo',('keyword_self','STEALTH'))]),
})
DEATH_EFFECTS={'GDB_226':[('area_damage','other_minions',2)],'WC_026':[('equip','WC_026t')],'GDB_454':[('heal_enemy_hero',6)]}
END_EFFECTS={'AV_340':[('area_damage','enemies',2)],'GDB_134':[('damage_random_enemy',3)]}
TOKEN_RULES={cid:('none',[]) for cid in ('BAR_538t','CFM_606t','TRL_020t','TRL_232t','WC_026t','BAR_035t','AV_211t')}
TRIGGERS={'WON_143':('hero_power_used',[random_cards(pool(card_type='MINION',minimum=1,maximum=1),destination='board')])}
RULES['AV_313']=('none',[('area_damage','enemy_minions',1)])
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
SPELL_DAMAGE_VALUES={'GDB_310':1}


def listeners(game):
 beacon=[(m,(('historical_keyword','shaffar'),[('historical_copy_shaffar',)])) for player in game.players for m in player.minions if m.health>0 and not m.silenced and (m.card_id=='GDB_143' or m.rule_state.get('historical_shaffar_beacon'))]
 return beacon+[(m,(('historical_keyword',kind),ops))
         for player in game.players for m in player.minions
         if not m.silenced and m.health>0
         for kind,table in TABLES.items() for ops in (table.get(m.card_id),)
         if ops is not None]


def snapshot_spell(game,card,owner):
 from .historical_pool_weapons import snapshot_spell as snapshot_weapon
 snapshot_weapon(game,card,owner)
 from .historical_galaxy_lens import snapshot as snapshot_lens
 snapshot_lens(game,card,owner)
 card._historical_shaffar_candidates=tuple(m.uid for m in game.players[owner].minions if m.health>0 and not m.silenced and (m.card_id=='GDB_143' or m.rule_state.get('historical_shaffar_beacon')) and not m.rule_state.get('historical_shaffar_used'))
 from .historical_starships import snapshot_spell as snapshot_starship_spell
 snapshot_starship_spell(game,card,owner)
 pending=getattr(game,'_historical_spellburst_pending',None)
 if pending is None:pending={};game._historical_spellburst_pending=pending
 pending[card.uid]=tuple(m.uid for m in game.players[owner].minions if m.health>0 and not m.silenced and m.card_id in SPELLBURST and not m.rule_state.get('historical_spellburst_used'))


def tag_event(game,kind,data):
 if kind=='damage' and data.get('target',0)<0 and data.get('amount',0)>0:
  recipient=-data['target']-1;player=game.players[recipient]
  if game.current==recipient:
   player.historical_own_turn_damage_total=getattr(player,'historical_own_turn_damage_total',0)+data['amount']
   player.historical_own_turn_damage_events=getattr(player,'historical_own_turn_damage_events',0)+1
  else:
   state=getattr(player,'historical_opponent_turn_damage',{})
   if state.get('turn')!=game.turn:state=dict(turn=game.turn,amount=0)
   state['amount']+=data['amount'];player.historical_opponent_turn_damage=state
 if kind=='damage' and data.get('target',0)<0 and data.get('damage_owner') in (0,1):
  owner=data['damage_owner']
  if data['target']==game.hero_id(1-owner):
   player=game.players[owner];state=getattr(player,'historical_enemy_hero_damage_turn',{})
   if state.get('turn')!=game.turn:state=dict(turn=game.turn,amount=0)
   state['amount']+=data.get('amount',0);player.historical_enemy_hero_damage_turn=state
 if kind=='card_drawn':
  player=game.players[data['owner']];player.historical_drawn_total=getattr(player,'historical_drawn_total',0)+1
  state=getattr(player,'historical_draw_turn',{})
  if state.get('turn')!=game.turn:state={'turn':game.turn,'count':0}
  state['count']+=1;player.historical_draw_turn=state;data['historical_draw_ordinal']=state['count']
 if kind=='historical_secret_played':
  from .historical_held_upgrades import progress
  progress(game,data['owner'],'emerald',1)
 if kind=='spell_cast':
  player=game.players[data['owner']];player.historical_spells_cast=getattr(player,'historical_spells_cast',0)+1
  from .historical_condition_batches import record_held_spell
  record_held_spell(game,data)
  school=game.cards[data['card_id']].get('spellSchool')
  if school:player.historical_spell_schools=sorted(set(getattr(player,'historical_spell_schools',()))|{school})
  if school:
   counts=getattr(player,'historical_school_counts',{});counts[school]=counts.get(school,0)+1;player.historical_school_counts=counts
   if 'SECRET' not in game.cards[data['card_id']].get('mechanics',()):
    visible=getattr(player,'_historical_public_school_counts',{});visible[school]=visible.get(school,0)+1;player._historical_public_school_counts=visible
 if kind=='spell_cast':
  from .historical_galaxy_lens import capture as capture_lens
  capture_lens(game,data)
  card=data.get('physical_card')
  from .historical_headmaster import complete as complete_headmaster
  complete_headmaster(game,data)
  data['historical_spellburst_candidates']=getattr(game,'_historical_spellburst_pending',{}).pop(getattr(card,'uid',None),())


def matches(game,wanted,kind,data,minion):
 if not isinstance(wanted,tuple) or len(wanted)!=2 or wanted[0]!='historical_keyword':return None
 keyword=wanted[1]
 if minion.health<=0 or minion.silenced:return False
 if keyword=='shaffar':
  card=data.get('physical_card')
  if kind!='spell_cast' or data['owner']!=minion.owner or minion.uid not in getattr(card,'_historical_shaffar_candidates',()) or minion.rule_state.get('historical_shaffar_used'):return False
  minion.rule_state['historical_shaffar_used']=True;return True
 if keyword=='frenzy':
  if kind!='damage' or data['target']!=minion.uid or data.get('amount',0)<=0 or minion.rule_state.get('historical_frenzy_used'):return False
  if data.get('target_health_before',0)<=data['amount']:return False
  minion.rule_state['historical_frenzy_used']=True;return True
 if keyword=='spellburst':
  if kind!='spell_cast' or data['owner']!=minion.owner or minion.uid not in data.get('historical_spellburst_candidates',()) or minion.rule_state.get('historical_spellburst_used'):return False
  persistent_school={'GDB_127':'SHADOW','GDB_442':'HOLY'}.get(minion.card_id)
  if game.cards[data['card_id']].get('spellSchool')!=persistent_school or persistent_school is None:minion.rule_state['historical_spellburst_used']=True
  return True
 if keyword=='overheal':return kind=='historical_overheal' and data['target']==minion.uid and data['overheal']>0
 if keyword in ('honorable','overkill'):
  if kind!='damage' or data.get('source_uid')!=minion.uid or data['target']<=0 or game.current!=minion.owner:return False
  before=data.get('target_health_before',0);amount=data.get('amount',0)
  return before>0 and (amount==before if keyword=='honorable' else amount>before)
 return False


def split(game,op,ctx):
 if op[0]=='historical_keyword_cast_same_cost':
  cost=ctx['event']['cost']
  return game._autocast_split(('autocast_random',pool(card_type='SPELL',minimum=cost,maximum=cost),1),ctx)
 if op[0]=='historical_keyword_spell_cost_minion':
  cost=ctx['event']['cost']
  return game._generation_split(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),set_cost=0),ctx)
 if op[0]=='historical_keyword_overheal_minion':
  cost=ctx['event']['overheal']
  return game._generation_split(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),destination='board'),ctx)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_keyword_'):return False
 if name=='historical_keyword_gain_victim_attack':
  if ctx.get('source') is not None:game._buff(ctx['source'],ctx['event'].get('target_attack_before',0),0)
  return True
 owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner];source=ctx.get('source')
 if name=='historical_keyword_force_enemy':
  if source is not None and game._force_live(source.uid):
   target=game._force_target(owner,'random_enemy_character')
   if target:game._force_attack(source.uid,target)
 elif name=='historical_keyword_event_armor':game._gain_armor(owner,ctx['event']['amount'])
 elif name=='historical_keyword_discount_hand':
  for card in p.hand:card.cost_delta-=op[1]
 elif name=='historical_keyword_transform_source':
  if source is not None and source in p.minions:game._transform(source,op[1])
 elif name=='historical_keyword_damaged_attack':
  count=sum(m.health<m.max_health for player in game.players for m in player.minions)+sum(player.health<player.max_health for player in game.players)
  if source is not None:game._buff(source,count*op[1],0)
 elif name=='historical_keyword_copy_cast_spell':
  card=ctx['event'].get('physical_card')
  if card is not None:game._clone_hand_card(owner,card,source_owner=owner)
 elif name=='historical_keyword_silence_source':
  if source is not None and source in p.minions:game._silence(source)
 elif name=='historical_keyword_frozen_enemy_damage':
  values=[m.uid for m in q.minions if m.frozen_until>=0]
  if q.frozen_until>=0:values.append(game.hero_id(1-owner))
  with game._damage_batch():
   for uid in values:game._deal_effect(uid,op[1],ctx)
 elif name=='historical_keyword_other_shields':
  for m in p.minions:
   if m is not source:m.keywords.add('DIVINE_SHIELD')
 else:return False
 return True

# Transfer Student board forms share native damage-keyword dispatch.
from .historical_transfer_student import OVERKILL as STUDENT_OVERKILL,HONORABLE as STUDENT_HONORABLE
OVERKILL.update(STUDENT_OVERKILL)
HONORABLE.update(STUDENT_HONORABLE)
