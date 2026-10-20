"""Physical historical spell outcomes: captured draws, neighbors and conditions."""
from .generation_cards import pool,random_cards,discover
from .selectors import has_tribe,has_school
from .pools import require_fixed_cards
TOKEN_RULES={
 'AT_004':('minion',[('historical_utility_pool_arcane_blast',)]),
 'BT_002':('none',[('historical_utility_pool_flow',)]),
 'BT_006':('none',[('historical_utility_pool_evocation',)]),
 'BT_291':('character',[('damage',5),('historical_utility_pool_apexis',)]),
 'DRG_106':('minion',[('damage',2),('historical_utility_pool_breath',)]),
 'EX1_179':('minion',[('historical_utility_pool_icicle',)]),
 'EX1_275':('minion',[('historical_utility_pool_cone',)]),
 'BOT_453':('minion',[('historical_utility_pool_shooting',)]),
 'GVG_005':('none',[('historical_utility_pool_echo',)]),
 'ICC_823':('none',[('historical_utility_pool_simulacrum',)]),
 'ICC_836':('none',[('historical_utility_pool_sindragosa',)]),
 'LOE_002':('character',[('damage',3),('insert_fixed','LOE_002t',1,'shuffle')]),
 'LOE_002t':('character',[('damage',6)]),
 'OG_086':('minion',[('historical_utility_pool_forbidden',)]),
 'ONY_006':('minion',[('historical_utility_pool_deep_breath',)]),
 'SCH_353':('none',[('historical_utility_pool_cram',)]),
 'SCH_509':('minion',[('freeze',),('historical_if_combo',('damage',3))]),
 'GIL_801':('minion',[('historical_utility_pool_snap',)]),
 'GDB_852':('none',[('historical_utility_pool_draw_sequence','revelation',1)]),
 'GIL_548':('none',[('historical_utility_pool_draw_sequence','specters',3)]),
 'BAR_542':('none',[('historical_utility_pool_draw_sequence','water',2)]),
 'CFM_811':('none',[('historical_utility_pool_draw_sequence','visions',2)]),
 'AV_116':('none',[('historical_utility_pool_brilliance',)]),
}
TOKEN_RULES.update({
 'AV_282':('none',[('summon','AV_282t',1),('add','AV_282t2',1)]),
 'AV_282t':('none',[]),
 'AV_282t2':('none',[('summon','AV_282t3',1),('add','AV_282t4',1)]),
 'AV_282t3':('none',[]),
 'AV_282t4':('none',[('summon','AV_282t5',1)]),
 'AV_282t5':('none',[]),
 'GDB_301':('none',[('historical_utility_pool_supernova',)]),
 'WORK_012':('none',[('historical_utility_pool_huddle',)]),
 'ULD_216':('none',[('autocast_random',pool(card_type='SPELL'),10)]),
 'DAL_577':('minion',[('historical_utility_pool_ray',),('add','DAL_577ts',1)]),
 'DAL_577ts':('minion',[('historical_utility_pool_ray',)]),
})
# Snow bodies use DAMAGE_FREEZERS, including combat and triggered damage.
TOKEN_RULES.update({
 'BRM_003':('character',[('damage',4)]),
 'TRL_313':('minion',[('damage',4)]),
 'GDB_305':('none',[('area_damage','enemies',2)]),
 'VAC_428':('minion',[('historical_utility_pool_flow_target',)]),
 'VAC_953':('none',[('historical_utility_pool_waves',)]),
})
TOKEN_RULES.update({
 'LOOT_103':('none',[random_cards(pool(card_type='SPELL',classes='MAGE'),1)]),
 'LOOT_103t1':('none',[random_cards(pool(card_type='SPELL',classes='MAGE'),2)]),
 'LOOT_103t2':('none',[random_cards(pool(card_type='SPELL',classes='MAGE'),3)]),
 'LOOT_106':('none',[('insert_fixed','LOOT_106t',5,'shuffle')]),
 'LOOT_106t':('none',[('autocast_random',pool(card_type='SPELL'),1)]),
 'DMF_104':('none',[('historical_utility_pool_finale',)]),
 'DMF_104t':('none',[]),
})
TOKEN_RULES.update({
 'BAR_546':('none',[('historical_utility_pool_wildfire',)]),
 'AV_212':('character',[('historical_utility_pool_siphon',)]),
 'TRL_317':('none',[('historical_utility_pool_blast_wave',)]),
})
TOKEN_RULES.update({
 'BOT_254':('none',[('historical_utility_pool_results',)]),
 'DAL_177':('minion',[('historical_utility_pool_conjure',),('add','DAL_177ts',1)]),
 'DAL_177ts':('minion',[('historical_utility_pool_conjure',)]),
 'ONY_029':('none',[discover(pool(card_type='MINION',tribe='DRAGON'),destination='board'),discover(pool(card_type='MINION',tribe='DRAGON'),destination='board')]),
})
TOKEN_RULES.update({
 'SW_110':('character',[('historical_utility_pool_ignite',)]),
 'GDB_456':('none',[('historical_utility_pool_combustion_target',)]),
 'VAC_509':('none',[('historical_utility_pool_tsunami',)]),
 'VAC_509t':('none',[]),
})
TOKEN_RULES.update({
 'DAL_578':('none',[('historical_utility_pool_creation',)]),
 'DMF_105':('none',[('historical_utility_pool_ring',1)]),
 'DMF_105t':('none',[('historical_utility_pool_ring',2)]),
 'ICC_086':('none',[('historical_secret_deck','each',False)]),
 'WON_040':('none',[('historical_secret_temporary',pool(era='past',card_type='SPELL',mechanic='SECRET'),5)]),
})
TOKEN_RULES.update({
 'SCH_348':('minion',[('historical_utility_pool_combustion',)]),
 'DRG_321':('minion',[('historical_utility_pool_rolling',)]),
 'DED_517':('enemy_minion',[('historical_utility_pool_overflow',)]),
 'DED_517t':('none',[]),
})
from .historical_mage_decks import TOKEN_RULES as DECK_RULES
TOKEN_RULES.update(DECK_RULES)
from .historical_mage_offers import TOKEN_RULES as OFFER_RULES
TOKEN_RULES.update(OFFER_RULES)
from .historical_mage_quests import TOKEN_RULES as QUEST_RULES
TOKEN_RULES.update(QUEST_RULES)
TOKEN_RULES['AV_283']=('none',[('historical_utility_pool_rune',)])
from .historical_nature_pool import TOKEN_RULES as NATURE_RULES
TOKEN_RULES.update(NATURE_RULES)
from .historical_spell_archive_batch import TOKEN_RULES as ARCHIVE_RULES
TOKEN_RULES.update(ARCHIVE_RULES)
from .historical_spell_continuation import TOKEN_RULES as CONTINUATION_RULES
TOKEN_RULES.update(CONTINUATION_RULES)
from .historical_physical_zone_batch import TOKEN_RULES as PHYSICAL_RULES
TOKEN_RULES.update(PHYSICAL_RULES)
from .historical_repeat_spell_batch import TOKEN_RULES as REPEAT_BATCH_RULES
TOKEN_RULES.update(REPEAT_BATCH_RULES)
from .historical_spell_finish_batch import TOKEN_RULES as FINISH_BATCH_RULES
TOKEN_RULES.update(FINISH_BATCH_RULES)
from .historical_mount_spell_batch import TOKEN_RULES as MOUNT_BATCH_RULES
TOKEN_RULES.update(MOUNT_BATCH_RULES)
from .historical_history_spell_batch import TOKEN_RULES as HISTORY_BATCH_RULES
TOKEN_RULES.update(HISTORY_BATCH_RULES)
from .historical_spellstone_finish import TOKEN_RULES as STONE_FINISH_RULES
TOKEN_RULES.update(STONE_FINISH_RULES)
from .historical_zone_spell_batch import TOKEN_RULES as ZONE_SPELL_BATCH_RULES
TOKEN_RULES.update(ZONE_SPELL_BATCH_RULES)
from .historical_damage_finish_batch import TOKEN_RULES as DAMAGE_FINISH_BATCH_RULES
TOKEN_RULES.update(DAMAGE_FINISH_BATCH_RULES)
from .historical_combat_spell_batch import TOKEN_RULES as COMBAT_SPELL_BATCH_RULES
TOKEN_RULES.update(COMBAT_SPELL_BATCH_RULES)
from .historical_sidequest_spell_batch import TOKEN_RULES as SIDEQUEST_BATCH_RULES
TOKEN_RULES.update(SIDEQUEST_BATCH_RULES)
from .historical_aura_finish_batch import TOKEN_RULES as AURA_FINISH_BATCH_RULES
TOKEN_RULES.update(AURA_FINISH_BATCH_RULES)
from .historical_condition_spell_batch import TOKEN_RULES as CONDITION_BATCH_RULES
TOKEN_RULES.update(CONDITION_BATCH_RULES)
from .historical_generation_finish_batch import TOKEN_RULES as GENERATION_FINISH_RULES
TOKEN_RULES.update(GENERATION_FINISH_RULES)
from .historical_deck_choice_finish import TOKEN_RULES as DECK_CHOICE_FINISH_RULES
TOKEN_RULES.update(DECK_CHOICE_FINISH_RULES)
from .historical_delayed_spell_finish import TOKEN_RULES as DELAYED_FINISH_RULES
TOKEN_RULES.update(DELAYED_FINISH_RULES)
from .historical_identified_spell_finish import TOKEN_RULES as IDENTIFIED_RULES
TOKEN_RULES.update(IDENTIFIED_RULES)
from .historical_trade_spell_finish import TOKEN_RULES as TRADE_FINISH_RULES
TOKEN_RULES.update(TRADE_FINISH_RULES)
from .historical_summon_faction_finish import TOKEN_RULES as SUMMON_FACTION_FINISH_RULES
TOKEN_RULES.update(SUMMON_FACTION_FINISH_RULES)
from .historical_stormwind_questline_finish import TOKEN_RULES as STORMWIND_FINISH_RULES
TOKEN_RULES.update(STORMWIND_FINISH_RULES)
from .historical_final_combat_spells import TOKEN_RULES as FINAL_COMBAT_RULES
TOKEN_RULES.update(FINAL_COMBAT_RULES)
from .historical_audit_spell_repairs import TOKEN_RULES as AUDIT_SPELL_RULES
TOKEN_RULES.update(AUDIT_SPELL_RULES)
from .historical_obligation_spells import TOKEN_RULES as OBLIGATION_RULES
TOKEN_RULES.update(OBLIGATION_RULES)
from .historical_final_spell_roots import TOKEN_RULES as FINAL_ROOT_RULES
TOKEN_RULES.update(FINAL_ROOT_RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def split(game,op,ctx):
 from .historical_final_spell_roots import split as final_root_split
 final=final_root_split(game,op,ctx)
 if final is not None:return final
 from .historical_obligation_spells import split as obligation_split
 result=obligation_split(game,op,ctx)
 if result is not None:return result
 from .historical_audit_spell_repairs import split as audit_split
 result=audit_split(game,op,ctx)
 if result is not None:return result
 from .historical_stormwind_questline_finish import split as stormwind_finish_split
 result=stormwind_finish_split(game,op,ctx)
 if result is not None:return result
 from .historical_summon_faction_finish import split as summon_faction_split
 result=summon_faction_split(game,op,ctx)
 if result is not None:return result
 from .historical_trade_spell_finish import split as trade_finish_split
 result=trade_finish_split(game,op,ctx)
 if result is not None:return result
 from .historical_identified_spell_finish import split as identified_split
 result=identified_split(game,op,ctx)
 if result is not None:return result
 from .historical_delayed_spell_finish import split as delayed_finish_split
 result=delayed_finish_split(game,op,ctx)
 if result is not None:return result
 from .historical_deck_choice_finish import split as deck_finish_split
 result=deck_finish_split(game,op,ctx)
 if result is not None:return result
 from .historical_generation_finish_batch import split as generation_finish_split
 result=generation_finish_split(game,op,ctx)
 if result is not None:return result
 from .historical_condition_spell_batch import split as condition_batch_split
 result=condition_batch_split(game,op,ctx)
 if result is not None:return result
 from .historical_combat_spell_batch import split as combat_spell_split
 result=combat_spell_split(game,op,ctx)
 if result is not None:return result
 from .historical_damage_finish_batch import split as damage_finish_split
 result=damage_finish_split(game,op,ctx)
 if result is not None:return result
 from .historical_zone_spell_batch import split as zone_spell_batch_split
 result=zone_spell_batch_split(game,op,ctx)
 if result is not None:return result
 from .historical_spellstone_finish import split as stone_finish_split
 result=stone_finish_split(game,op,ctx)
 if result is not None:return result
 from .historical_history_spell_batch import split as history_batch_split
 result=history_batch_split(game,op,ctx)
 if result is not None:return result
 from .historical_spell_finish_batch import split as finish_batch_split
 result=finish_batch_split(game,op,ctx)
 if result is not None:return result
 from .historical_repeat_spell_batch import split as repeat_batch_split
 result=repeat_batch_split(game,op,ctx)
 if result is not None:return result
 from .historical_physical_zone_batch import split as physical_split
 result=physical_split(game,op,ctx)
 if result is not None:return result
 from .historical_spell_continuation import split as continuation_split
 result=continuation_split(game,op,ctx)
 if result is not None:return result
 from .historical_spell_archive_batch import split as archive_split
 result=archive_split(game,op,ctx)
 if result is not None:return result
 if op[0]=='historical_utility_pool_rune':
  # Full-pool internal admission precedes RNG. The continuation only samples
  # spells whose printed cost fits the unspent budget; zero-cost spells count 0.
  owner=ctx['owner'];game._autocast_candidates(pool(card_type='SPELL',classes='MAGE',maximum=20),owner)
  return split(game,('historical_utility_pool_rune_step',20),ctx)
 if op[0]=='historical_utility_pool_rune_step':
  remaining=op[1];owner=ctx['owner']
  if remaining<=0:return ('batch30_noop',),()
  request=pool(card_type='SPELL',classes='MAGE',maximum=remaining)
  game._autocast_candidates(request,owner)
  values=game._generation_created_candidates(request,dict(ctx,generation_creator_id='AV_283'))
  if not values:return ('batch30_noop',),()
  cid=game.rng.choice(list(values));left=remaining-game.cards[cid]['cost']
  first,tail=game._cast_spell_split(('cast_fixed_spell',cid,'prefer_enemies'),ctx)
  return first,tuple(tail)+(('historical_utility_pool_rune_step',left),)
 from .historical_nature_pool import split as nature_split
 result=nature_split(game,op,ctx)
 if result is not None:return result
 from .historical_mage_offers import split as offer_split
 result=offer_split(game,op,ctx)
 if result is not None:return result
 from .historical_mage_decks import split as deck_split
 result=deck_split(game,op,ctx)
 if result is not None:return result
 name=op[0];p=game.players[ctx['owner']];owner=ctx['owner']
 if name in ('historical_utility_pool_rolling','historical_utility_pool_overflow'):
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  budget=(8+ctx.get('bonus',0))*(1 if ctx.get('spell_multiplier_applied') else game._spell_multiplier(owner))
  if name=='historical_utility_pool_overflow':
   excess=max(0,budget-target.health)
   return ('damage',8),(('historical_utility_pool_remnant',excess),)
  board=list(game.players[target.owner].board);index=board.index(target)
  directions=[d for d in (-1,1) if 0<=index+d<len(board)]
  direction=game.rng.choice(directions) if len(directions)>1 and budget>target.health else directions[0] if directions else 1
  operations=[]
  while budget>0 and 0<=index<len(board):
   victim=board[index]
   if victim not in game.players[target.owner].minions or victim.health<=0 or victim.dormant:break
   amount=budget;budget-=victim.health
   context=dict(ctx,target=victim.uid,bonus=0,spell_multiplier_applied=True)
   operations.append(('replay_context',(('damage',amount),),context))
   index+=direction
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+tuple(operations[1:])
 if name=='historical_utility_pool_creation':
  from .generation_cards import board_pool
  request=board_pool(pool(card_type='MINION',minimum=6,maximum=6))
  return ('historical_offer_open','mage_summon_twice',(request,),{},''),()
 if name=='historical_utility_pool_ring':
  request=pool(card_type='SPELL',mechanic='SECRET',classes='own')
  if not game._generation_candidates(request,owner):request=pool(card_type='SPELL',mechanic='SECRET',classes='MAGE')
  operations=(('historical_secret_discover',request,'cast'),)*op[1]
  return operations[0],operations[1:]
 if name=='historical_utility_pool_tsunami':
  state=dict(summoned=[],mode='random_enemy_character')
  operations=(('historical_utility_pool_water_summon',state),)*3+(('force_group_attacks',state),)
  return operations[0],operations[1:]
 if name=='historical_utility_pool_results':
  cost=max(0,2+ctx.get('bonus',0))
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),2,destination='board'),ctx)
 if name=='historical_utility_pool_conjure':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  from .generation_cards import board_pool
  cost=game._card_stat(target,'cost',target.owner)
  request=board_pool(pool(card_type='MINION',minimum=cost,maximum=cost))
  recipient=target.owner
  game._generation_candidates(request,recipient)
  context=dict(ctx,owner=recipient)
  return ('destroy',),(('replay_context',(random_cards(request,2,destination='board'),),context),)
 if name=='historical_utility_pool_blast_wave':
  state={}
  return ('historical_utility_pool_blast_damage',state),(('historical_utility_pool_blast_rewards',state),)
 if name=='historical_utility_pool_blast_rewards':
  count=op[1].get('overkills',0)
  if count:return game._split_fixed_summon(random_cards(pool(card_type='SPELL',classes='MAGE'),count),ctx)
  return ('batch30_noop',),()
 if name=='historical_utility_pool_finale':
  operations=(('summon','DMF_104t',1),)*(1+getattr(p,'historical_elementals_previous',0))
  return operations[0],operations[1:]
 if name=='historical_utility_pool_waves':
  before=sum(player.minions_died_turn for player in game.players)
  return ('area_damage','all_minions',2),(('historical_utility_pool_waves_finish',before),)
 if name=='historical_utility_pool_supernova':
  return game._split_fixed_summon(random_cards(pool(card_type='SPELL',school='FIRE'),max(0,getattr(p,'hand_capacity',10)-len(p.hand)),set_cost=1),ctx)
 if name=='historical_utility_pool_huddle':
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',tribe='NAGA'),max(0,7-len(p.board)),destination='board'),ctx)
 if name=='historical_utility_pool_evocation':
  return game._split_fixed_summon(random_cards(pool(card_type='SPELL',classes='MAGE'),max(0,getattr(p,'hand_capacity',10)-len(p.hand)),temporary=True),ctx)
 if name=='historical_utility_pool_apexis':
  if not any(game._card_data(c)['type']=='MINION' for c in p.deck):return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=5,maximum=5),destination='board'),ctx)
  return ('batch30_noop',),()
 if name=='historical_utility_pool_breath':
  if any(has_tribe(game._card_data(c),'DRAGON') for c in p.hand):return game._split_fixed_summon(discover(pool(card_type='SPELL',classes='own_or_neutral')),ctx)
  return ('batch30_noop',),()
 if name=='historical_utility_pool_cram':return ('draw',max(0,1+ctx.get('bonus',0))),()
 if name=='historical_utility_pool_draw_sequence':
  states=[{} for _ in range(op[2])]
  operations=[('historical_draw_capture',None,'random',state) for state in states]
  operations.extend(('historical_utility_pool_draw_finish',op[1],state) for state in states)
  return operations[0],tuple(operations[1:])
 if name=='historical_utility_pool_icicle':
  target=game._force_live(ctx.get('target'))
  return ('damage',2), (('draw',1),) if target is not None and target.frozen_until>=0 else ()
 return None

def execute(game,op,ctx):
 from .historical_final_spell_roots import execute as final_root_execute
 if final_root_execute(game,op,ctx):return True
 from .historical_obligation_spells import execute as obligation_execute
 if obligation_execute(game,op,ctx):return True
 from .historical_audit_spell_repairs import execute as audit_execute
 if audit_execute(game,op,ctx):return True
 from .historical_final_combat_spells import execute as final_combat_execute
 if final_combat_execute(game,op,ctx):return True
 from .historical_stormwind_questline_finish import execute as stormwind_finish_execute
 if stormwind_finish_execute(game,op,ctx):return True
 from .historical_summon_faction_finish import execute as summon_faction_execute
 if summon_faction_execute(game,op,ctx):return True
 from .historical_trade_spell_finish import execute as trade_finish_execute
 if trade_finish_execute(game,op,ctx):return True
 from .historical_identified_spell_finish import execute as identified_execute
 if identified_execute(game,op,ctx):return True
 from .historical_delayed_spell_finish import execute as delayed_finish_execute
 if delayed_finish_execute(game,op,ctx):return True
 from .historical_deck_choice_finish import execute as deck_finish_execute
 if deck_finish_execute(game,op,ctx):return True
 from .historical_generation_finish_batch import execute as generation_finish_execute
 if generation_finish_execute(game,op,ctx):return True
 from .historical_condition_spell_batch import execute as condition_batch_execute
 if condition_batch_execute(game,op,ctx):return True
 from .historical_aura_finish_batch import execute as aura_finish_execute
 if aura_finish_execute(game,op,ctx):return True
 from .historical_sidequest_spell_batch import execute as sidequest_batch_execute
 if sidequest_batch_execute(game,op,ctx):return True
 from .historical_combat_spell_batch import execute as combat_spell_execute
 if combat_spell_execute(game,op,ctx):return True
 from .historical_damage_finish_batch import execute as damage_finish_execute
 if damage_finish_execute(game,op,ctx):return True
 from .historical_zone_spell_batch import execute as zone_spell_batch_execute
 if zone_spell_batch_execute(game,op,ctx):return True
 from .historical_spellstone_finish import execute as stone_finish_execute
 if stone_finish_execute(game,op,ctx):return True
 from .historical_history_spell_batch import execute as history_batch_execute
 if history_batch_execute(game,op,ctx):return True
 from .historical_mount_spell_batch import execute as mount_batch_execute
 if mount_batch_execute(game,op,ctx):return True
 from .historical_spell_finish_batch import execute as finish_batch_execute
 if finish_batch_execute(game,op,ctx):return True
 from .historical_repeat_spell_batch import execute as repeat_batch_execute
 if repeat_batch_execute(game,op,ctx):return True
 from .historical_physical_zone_batch import execute as physical_execute
 if physical_execute(game,op,ctx):return True
 from .historical_spell_continuation import execute as continuation_execute
 if continuation_execute(game,op,ctx):return True
 from .historical_spell_archive_batch import execute as archive_execute
 if archive_execute(game,op,ctx):return True
 from .historical_nature_pool import execute as nature_execute
 if nature_execute(game,op,ctx):return True
 from .historical_mage_quests import execute as quest_execute
 if quest_execute(game,op,ctx):return True
 from .historical_mage_offers import execute as offer_execute
 if offer_execute(game,op,ctx):return True
 from .historical_mage_decks import execute as deck_execute
 if deck_execute(game,op,ctx):return True
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_utility_pool_combustion':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   board=game.players[target.owner].board;index=board.index(target)
   neighbors=[board[i] for i in (index-1,index+1) if 0<=i<len(board) and board[i] in game.players[target.owner].minions]
   budget=(4+ctx.get('bonus',0))*(1 if ctx.get('spell_multiplier_applied') else game._spell_multiplier(owner))
   excess=max(0,budget-target.health)
   with game._damage_batch():
    game._deal_effect(target.uid,4,ctx)
    if excess:
     for neighbor in neighbors:game._deal_effect(neighbor.uid,excess,dict(ctx,bonus=0,spell_multiplier_applied=True))
 elif name=='historical_utility_pool_remnant':
  if op[1]>0:game._summon(owner,'DED_517t',entry_stats=(op[1],op[1]),entry_origin='effect',entry_site='arcane_overflow')
 elif name=='historical_utility_pool_ignite':
  from engine.game import Card
  physical=ctx.get('physical_card')
  amount=getattr(physical,'rule_state',{}).get('historical_ignite_damage',2)
  game._deal_effect(ctx.get('target'),amount,ctx)
  card=Card(game._new_id(),'SW_110');game._b60_state(card)['historical_ignite_damage']=amount+1
  p.deck.insert(game.rng.randrange(len(p.deck)+1),card)
  game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_utility_pool_combustion_target':
  if ctx.get('target'):game._deal_effect(ctx['target'],4,ctx)
  else:game._effect(('damage_random_enemy',4),ctx)
 elif name=='historical_utility_pool_water_summon':
  before={m.uid for m in p.minions}
  game._summon(owner,'VAC_509t',entry_origin='effect',entry_site='tsunami')
  op[1]['summoned'].extend(m.uid for m in p.minions if m.uid not in before and m.card_id=='VAC_509t')
 elif name=='historical_utility_pool_wildfire':p.historical_permanent_power_damage=getattr(p,'historical_permanent_power_damage',0)+1
 elif name=='historical_utility_pool_siphon':
  target=game._force_live(ctx.get('target'))
  game._deal_effect(ctx.get('target'),2,ctx)
  if target is not None and target.health==0 and owner==game.current:
   for card in p.hand:
    if game._card_data(card)['type']=='SPELL':card.cost_delta=getattr(card,'cost_delta',0)-1
 elif name=='historical_utility_pool_blast_damage':
  targets=[m for player in game.players for m in player.minions if m.health>0]
  with game._damage_batch():
   for target in targets:game._deal_effect(target.uid,2,ctx)
   overkills=sum(target.health<0 for target in targets) if owner==game.current else 0
  op[1]['overkills']=overkills
 elif name=='historical_utility_pool_flow_target':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   if target.owner==owner:target.rule_state['historical_spell_damage']=target.rule_state.get('historical_spell_damage',0)+1
   else:game._freeze(target.uid)
 elif name=='historical_utility_pool_waves_finish':
  if sum(player.minions_died_turn for player in game.players)==op[1]:game._effect(('area_damage','all_minions',2),ctx)
 elif name=='historical_utility_pool_ray':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   if target.frozen_until>=0:game._deal_effect(target.uid,2,ctx)
   game._freeze(target.uid)
 elif name=='historical_utility_pool_arcane_blast':game._deal_effect(ctx['target'],2+ctx.get('bonus',0),ctx)
 elif name in ('historical_utility_pool_cone','historical_utility_pool_shooting','historical_utility_pool_deep_breath'):
  target=game._force_live(ctx.get('target'))
  if target is None:return True
  board=game.players[target.owner].minions;index=board.index(target)
  neighbors=[m.uid for m in board[max(0,index-1):index+2]]
  amount=1+(sum(game._card_data(c)['type']=='SPELL' for c in p.hand) if name=='historical_utility_pool_deep_breath' else 0)
  with game._damage_batch():
   for uid in neighbors:
    if name=='historical_utility_pool_cone':game._freeze(uid)
    game._deal_effect(uid,amount,ctx)
 elif name=='historical_utility_pool_flow':
  for i,c in enumerate(p.deck):
   if game._card_data(c)['type']=='SPELL':
    if isinstance(c,str):
     from engine.game import Card
     c=Card(game._new_id(),c);p.deck[i]=c
    c.cost_delta=getattr(c,'cost_delta',0)-1
 elif name=='historical_utility_pool_echo':
  for m in list(p.minions):game._effect(('historical_copy_target_snapshot',m,'hand',1,None,None,None,False),ctx)
 elif name=='historical_utility_pool_simulacrum':
  candidates=[c for c in p.hand if game._card_data(c)['type']=='MINION']
  if candidates:
   cost=min(game._cost(c,owner) for c in candidates);c=game.rng.choice([c for c in candidates if game._cost(c,owner)==cost]);game._enter_hand(owner,game._copy_card(c,source_owner=owner))
 elif name=='historical_utility_pool_sindragosa':
  candidates=[m for m in game.players[1-owner].minions if m.health>0]
  if candidates:
   m=game.rng.choice(candidates);game._deal_effect(m.uid,2,ctx);game._freeze(m.uid)
 elif name=='historical_utility_pool_forbidden':
  amount=p.mana;p.mana=0;game._deal_effect(ctx['target'],amount,ctx)
 elif name=='historical_utility_pool_snap':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   game._effect(('destroy',),ctx) if target.frozen_until>=0 else game._freeze(target.uid)
 elif name=='historical_utility_pool_brilliance':
  for cost in (7,8,9,10):
   candidates=[c for c in p.deck if game._card_data(c)['type']=='SPELL' and game._cost(c,owner)==cost]
   if candidates:game._enter_hand(owner,game._copy_card(game.rng.choice(candidates),source_owner=owner))
 elif name=='historical_utility_pool_draw_finish':
  mode,state=op[1:];card=state.get('card')
  if card is None:return True
  d=game._card_data(card)
  if mode=='water' and d['type']=='SPELL':game._effect(('refresh_mana',2),ctx)
  elif mode=='revelation' and d['type']=='SPELL' and card in p.hand:card.cost_delta=getattr(card,'cost_delta',0)-1
  elif mode=='visions' and d['type']=='MINION' and card in p.hand:card.cost_delta=getattr(card,'cost_delta',0)-2
  elif mode=='specters' and d['type']=='SPELL' and card in p.hand:game._discard_card(owner,card)
 else:return False
 return True
