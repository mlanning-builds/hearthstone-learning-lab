"""Explicit Concoction, repeated heal, tribal draw and literal utility effects."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .selectors import has_school,has_tribe,effective_tribes
from .pools import require_fixed_cards
from .generation_cards import pool,PoolRequest
TOKEN_RULES={
 'ONY_005':('none',[('historical_utility_kazakusan',)]),
 # Printed Taunt/Lifesteal use native keywords; Start of Game is handled
 # by historical_anomalies.choose_opening, never by a played Battlecry.
 'YOG_530':('none',[]),
 'RLK_569':('none',[('historical_utility_potion',),('historical_utility_potion',)]),
 'TSC_952':('character',[('heal',2)]),
 'ETC_372':('none',[('historical_utility_applause',)]),
 'DEEP_017':('none',[('historical_utility_recruit',),('historical_utility_recruit',)]),
 'ETC_320':('historical_friendly_shield',[('historical_utility_spotlight',)]),
 'ETC_320t':('none',[]),
 'TTN_090':('none',[]),
}
LOCATION_RULES={'TTN_090':'character'}
LOCATION_EFFECTS={'TTN_090':[('historical_utility_prison',4)]}
TOKEN_RULES.update({
 'ETC_316':('enemy_minion',[('historical_utility_pair_choice','fight')]),
 'TTN_932':('friendly_minion',[('historical_utility_pair_choice','consume')]),
})
TOKEN_RULES.update({
 'WW_348':('none',[('historical_utility_misfire',)]),
 'TSC_023':('enemy_character',[('damage',2),('historical_utility_nets',)]),
})
TOKEN_RULES.update({
 'DEEP_022':('none',[('historical_utility_gold',)]),
 'REV_931':('none',[('historical_utility_banner',),('historical_utility_banner',),('historical_utility_banner',)]),
})
TOKEN_RULES.update({'ETC_084':('none',[]),'RLK_655':('minion',[('historical_utility_wither',)])})
TOKEN_RULES['REV_337']=('none',[('historical_utility_riot',)])
TOKEN_RULES.update({'WW_425':('none',[('historical_utility_stargazing',)]),'MIS_027':('minion',[('historical_utility_domino',)])})
CHAMELEONS={keyword:'WW_810t'+str(index) for index,keyword in enumerate(('DIVINE_SHIELD','TAUNT','RUSH','WINDFURY','ELUSIVE','POISONOUS','LIFESTEAL','REBORN'),1)}
TOKEN_RULES.update({cid:('none',[]) for cid in CHAMELEONS.values()})
TOKEN_RULES['WW_810']=('minion',[('buff',3,3),('historical_utility_mount',)])
TOKEN_RULES.update({'TSC_006':('none',[('hero_attack',2),('historical_utility_multistrike',)]),'ETC_413':('none',[('hero_attack',2),('historical_utility_swing',)])})
TOKEN_RULES.update({
 'TOY_829':('none',[('historical_utility_horseman',)]),
 'TOY_829t2':('none',[('historical_utility_horseman',)]),
 'TOY_829t':('none',[('historical_utility_horseman_head',)]),
 'TOY_829hp':('none',[]),'TOY_829hp3':('none',[]),
})
RENO_BULLETS=tuple('WW_0700p'+str(i) for i in range(1,8))
TOKEN_RULES.update({cid:('none',[]) for cid in RENO_BULLETS})
RENO_STAGED_RULE=('none',[('historical_utility_reno_clear',)])
TOKEN_RULES['YOG_522']=('none',[('historical_utility_conductivity',)])
TOKEN_RULES.update({
 'ONY_005ta1':('minion',[('destroy',)]),
 'ONY_005ta2':('minion',[('buff',4,4),('keyword','TAUNT')]),
 'ONY_005ta4':('none',[('damage_enemy_hero',8),('historical_utility_pure_cold',)]),
 'ONY_005ta8':('none',[('draw',2),('armor',4)]),
 'ONY_005tb2':('minion',[('keyword',keyword) for keyword in ('RUSH','WINDFURY','DIVINE_SHIELD','LIFESTEAL','POISONOUS','TAUNT','STEALTH')]),
 'ONY_005tb4':('none',[('historical_utility_disintegration',)]),
 'ONY_005tb5':('none',[('summon','ONY_005tb5t',3)]),
 'ONY_005tb5t':('none',[]),
 'ONY_005tb7':('none',[('historical_utility_jars',)]),
 'ONY_005tc1':('none',[('historical_utility_embers',),('historical_utility_embers',),('historical_utility_embers',)]),
 'ONY_005tc2':('none',[('area_damage','enemies',7)]),
 'ONY_005tc6':('minion',[('buff',3,3)]),
})
TOKEN_RULES.update({
 'ONY_005ta10':('none',[('historical_utility_spyglass',)]),
 'ONY_005tb9':('friendly_minion',[('buff',2,2),('historical_utility_banana_split',)]),
 'ONY_005tb14':('minion',[('historical_utility_fangs',)]),
 'ONY_005ta6':('minion',[('historical_utility_holy_book',)]),
 'ONY_005ta3':('none',[]),'ONY_005tb1':('none',[]),'ONY_005tb6':('none',[]),'ONY_005tc7':('none',[]),
})
TOKEN_RULES.update({
 'ONY_005ta11':('none',[]),'ONY_005ta12':('none',[]),'ONY_005tb13':('none',[]),
 'ONY_005ta9':('none',[]),'ONY_005ta9t':('none',[]),
 'ONY_005ta7':('minion',[('historical_utility_crusty',)]),
 'ONY_005ta5':('none',[('force_summon_group','ONY_005ta5t',6,'random_enemy_minion')]),
 'ONY_005ta5t':('none',[]),
 'ONY_005tb12':('none',[('summon','GVG_110t',7)]),
 'ONY_005tc3':('none',[('historical_utility_annoy',)]),
})
TOKEN_RULES.update({
 'ONY_005ta13':('none',[('historical_utility_puzzle',)]),
 'ONY_005tb8':('minion',[('historical_utility_reflections',)]),
 'ONY_005tb3':('enemy_character',[('historical_utility_locusts',),('add','ONY_005tb3t',1)]),
 'ONY_005tb3t':('enemy_character',[('historical_utility_locusts',)]),
 'ONY_005tb3t2':('none',[]),
})
TOKEN_RULES.update({'ONY_005tc5':('none',[]),'ONY_005tc7t':('none',[('historical_utility_quel_forge',)])})
TOKEN_RULES['GDB_145']=('none',[('historical_utility_demon_portal',)])
TOKEN_RULES.update({
 'SC_004':('none',[('summon','SC_003',2),('area_damage','enemies',3)]),
 'SC_004hp':('none',[]),
 'WON_092h':('none',[('filtered_draw',(('mechanic','eq',keyword),),1) for keyword in ('CHARGE','DIVINE_SHIELD','TAUNT','WINDFURY')]),
 'WON_092p':('none',[]),
})
TOKEN_RULES.update({'SC_400':('none',[('historical_utility_raynor',)]),'SC_400p':('none',[])})
YOGG_WHEEL=tuple('DMF_004t'+str(i) for i in range(1,7))
TOKEN_RULES.update({'DMF_004':('none',[('historical_utility_yogg_wheel',)])})
TOKEN_RULES.update({cid:('none',[('historical_utility_yogg_outcome',i)]) for i,cid in enumerate(YOGG_WHEEL,1)})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def different_types(game,owner):
 types=[effective_tribes(game._card_data(m)) for m in game.players[owner].minions if m.health>0]
 matches={}
 def augment(index,seen):
  for tribe in sorted(types[index]):
   if tribe in seen:continue
   seen.add(tribe)
   if tribe not in matches or augment(matches[tribe],seen):matches[tribe]=index;return True
  return False
 for index in range(len(types)):augment(index,set())
 return len(matches)


def split(game,op,ctx):
 from .historical_pool_spells import split as split_pool
 result=split_pool(game,op,ctx)
 if result is not None:return result
 owner=ctx['owner'];name=op[0]
 if name=='historical_utility_earthen_might':
  target=game._force_live(ctx.get('target'))
  if target is not None and has_tribe(game._card_data(target),'ELEMENTAL'):
   from .generation_cards import random_cards
   return game._generation_split(random_cards(pool(card_type='MINION',tribe='ELEMENTAL')),ctx)
  return ('batch30_noop',),()
 if name=='historical_utility_eonar_draw':
  count=max(0,getattr(game.players[owner],'hand_capacity',10)-len(game.players[owner].hand))
  return (('draw',count),()) if count else (('batch30_noop',),())

 if name=='historical_utility_protect_innocent':
  require_fixed_cards(('AV_342t',),game.cards)
  operations=(('summon','AV_342t',1),)*(2 if game.players[owner].hero_healed_turn else 1)
  return operations[0],operations[1:]
 if name=='historical_utility_togwaggle_scheme':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  count=1+game._b60_state(ctx.get('physical_card')).get('held_turn_ends',0)
  return ('historical_copy_target_snapshot',deepcopy(target),'deck',count,None,None,None,False),()

 if name=='historical_utility_overdraft':
  player=game.players[owner]
  amount=player.locked_mana+player.overload_next
  return ('unlock_mana',),(('damage',amount),)

 if name=='historical_utility_sapphire_copy':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  donor=deepcopy(target)
  operations=(('historical_utility_treasure_copy',donor,False),)*op[1]
  return operations[0],operations[1:]

 if name=='historical_utility_charged_call':
  from .generation_cards import discover
  count=sum(bool(record.get('overload_card',game.cards[record['card_id']].get('overload',0))) for record in game.players[owner].played_history)
  cost=min(10,1+count)
  return game._split_fixed_summon(discover(pool(card_type='MINION',minimum=cost,maximum=cost,classes='own_or_neutral'),destination='board'),ctx)

 if name=='historical_utility_runic':
  require_fixed_cards(('SCH_612t',),game.cards)
  operations=(('historical_utility_runic_summon',op[1]),)*4
  return operations[0],operations[1:]

 if name=='historical_utility_devolving_missiles':
  # All hits need their own split pass, including the first one.
  return ('batch30_noop',),(('historical_utility_devolving_hit',),)*3
 if name=='historical_utility_devolving_hit':
  from .transformations import evolve_pool
  victims=tuple(m for m in game.players[1-owner].minions if m.health>0)
  prepared=[]
  for victim in victims:
   values=game._generation_candidates(evolve_pool(game._card_stat(victim,'cost',victim.owner),-1),owner)
   prepared.append((victim.uid,tuple(values)))
  if not prepared:return ('batch30_noop',),()
  uid,values=game.rng.choice(prepared)
  return (('historical_copy_literal_uid',uid,game.rng.choice(values)),()) if values else (('batch30_noop',),())

 if name=='historical_utility_landslide':
  player=game.players[owner]
  operations=(('area_damage','enemy_minions',1),)*(2 if player.overload_next>0 or player.locked_mana>0 else 1)
  return operations[0],operations[1:]

 if name=='historical_utility_healing_wave':
  revealed=[]
  for side in (owner,1-owner):
   deck=game.players[side].deck;values=[card for card in deck if game._card_data(card)['type']=='MINION']
   card=game.rng.choice(values) if values else None;revealed.append(card)
   if card is not None:game._log('joust_reveal',player=side,card=game._card_data(card)['id'])
  own,other=revealed
  won=own is not None and (other is None or game._card_stat(own,'cost',owner)>game._card_stat(other,'cost',1-owner))
  return ('heal',16 if won else 8),()
 if name=='historical_utility_reincarnate':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  donor=deepcopy(target)
  return ('destroy',),(('historical_utility_reincarnate_summon',donor),)

 if name=='historical_utility_transform_board':
  from .transformations import evolve_pool
  mode=op[1];side=1-owner if mode=='enemy' else owner
  victims=tuple(m for m in game.players[side].minions if m.health>0)
  prepared=[]
  for victim in victims:
   request=pool(card_type='MINION',rarity='LEGENDARY',excluded_mechanic='COLOSSAL') if mode=='legendary' else evolve_pool(game._card_stat(victim,'cost',victim.owner),op[2])
   values=game._generation_candidates(request,owner)
   prepared.append((victim.uid,tuple(values)))
  # Every original target pool must be complete before the first RNG draw.
  operations=tuple(('historical_copy_literal_uid',uid,game.rng.choice(values)) for uid,values in prepared if values)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())

 if name=='historical_utility_potion_illusion':
  donors=[deepcopy(m) for m in game.players[owner].minions if m.health>0]
  operations=tuple(('historical_copy_target_snapshot',m,'hand',1,1,1,1,False) for m in donors)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())

 if name=='historical_utility_plot_twist':
  originals=tuple(game.players[owner].hand)
  return ('historical_utility_plot_shuffle',originals),(('draw',len(originals)),)

 if name=='historical_utility_dark_skies':
  operations=(('historical_utility_dark_skies_hit',),)*(1+len(game.players[owner].hand))
  return operations[0],operations[1:]

 if name=='historical_utility_unsleep_copy':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  return ('historical_utility_treasure_copy',deepcopy(target),False),()
 if name=='historical_utility_ramming_speed':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  board=game.players[target.owner].board;position=board.index(target)
  neighbors=[board[index] for index in (position-1,position+1) if 0<=index<len(board) and board[index] in game.players[target.owner].minions and board[index].health>0]
  if not neighbors:return ('batch30_noop',),()
  return ('force_pair',target.uid,game.rng.choice(neighbors).uid),()

 from .historical_soul_mirror import split as split_mirror
 result=split_mirror(game,op,ctx)
 if result is not None:return result
 from .historical_iconic_followups import split as split_iconic
 result=split_iconic(game,op,ctx)
 if result is not None:return result
 if name=='historical_utility_vanish':
  # Capture all original minions in entity order; earlier bounces cannot
  # cause a replacement or later entry to be bounced as an original target.
  operations=tuple(('historical_utility_vanish_uid',m.uid) for m in sorted([m for player in game.players for m in player.minions],key=lambda m:m.uid))
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_utility_yogg_wheel':
  if getattr(game.players[owner],'historical_spells_cast',0)<10:return ('batch30_noop',),()
  require_fixed_cards(YOGG_WHEEL,game.cards);roll=game.rng.randrange(100);index=min(5,roll//19)
  return game._cast_spell_split(('cast_fixed_spell',YOGG_WHEEL[index],'random'),ctx)
 if name=='historical_utility_yogg_outcome':
  outcome=op[1]
  if outcome==1:return ('historical_utility_yogg_random_casts',getattr(game.players[owner],'historical_spells_cast',0)),()
  if outcome==3:
   from .generation_cards import random_cards
   operations=[]
   for recipient in (owner,1-owner):
    for _ in range(max(0,7-len(game.players[recipient].board))):operations.append(('replay_context',(random_cards(pool(card_type='MINION'),destination='board'),),dict(ctx,owner=recipient)))
   operations.append(('historical_utility_yogg_rush',))
   return operations[0],tuple(operations[1:])
  if outcome==4:return ('historical_utility_yogg_steal',),(('historical_utility_yogg_steal',),('historical_utility_yogg_steal',))
  if outcome==6:return ('historical_utility_yogg_roast',),()
  return None
 if name=='historical_utility_yogg_random_casts':
  if op[1]<=0 or game.terminal:return ('batch30_noop',),()
  values=game._autocast_candidates(pool(card_type='SPELL'),owner)
  if not values:return ('batch30_noop',),()
  first,tail=game._cast_spell_split(('cast_fixed_spell',game.rng.choice(values),'random'),ctx)
  return first,tuple(tail)+(('historical_utility_yogg_random_casts',op[1]-1),)
 if name=='historical_utility_yogg_roast':
  if game.terminal or any(p.health<=0 for p in game.players):return ('batch30_noop',),()
  first,tail=game._cast_spell_split(('cast_fixed_spell','EX1_279','random'),ctx)
  return first,tuple(tail)+(('historical_utility_yogg_roast',),)
 if name=='historical_utility_raynor':
  history=tuple(deepcopy(getattr(game.players[owner],'_historical_launched_ships',())))
  operations=tuple(('historical_utility_relaunch',card) for card in history)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_utility_ravage':
  from .historical_copy_batches import ZERG_IDS
  from .historical_damage_modifiers import power_multiplier
  p=game.players[owner]
  zerg=sum(m.health>0 and m.card_id in ZERG_IDS for m in p.minions)
  bonus=sum((1 if m.card_id=='AT_003' else 2 if m.card_id=='YOD_008' else 0) for m in p.minions if not m.silenced and m.health>0)
  count=max(0,(3+zerg+bonus+ctx.get('power_damage_bonus',0))*power_multiplier(game,owner))
  operations=(('historical_utility_ravage_ray',),)*count
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_utility_locusts':
  count=max(0,7-len(game.players[owner].board))
  return game._split_fixed_summon(('force_summon_group','ONY_005tb3t2',count,'target'),ctx)
 if name=='historical_utility_reflections':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  donor=deepcopy(target);operations=tuple(('historical_utility_reflection_one',donor) for _ in range(max(0,7-len(game.players[owner].board))))
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_utility_puzzle':
  from .transformations import evolve_pool
  operations=[]
  for player in game.players:
   for minion in tuple(player.minions):
    if minion.health>0:
     values=game._generation_created_candidates(evolve_pool(game._card_stat(minion,'cost',minion.owner),3),dict(ctx,owner=minion.owner))
     if values:operations.append(('historical_utility_puzzle_one',minion.uid,game.rng.choice(values)))
  return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())
 if name in ('historical_utility_banana_split','historical_utility_holy_book','historical_utility_fangs'):
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  if name=='historical_utility_banana_split':
   donor=deepcopy(target);operations=(('historical_utility_treasure_copy',donor,False),)*2
  elif name=='historical_utility_holy_book':
   operations=(('historical_utility_holy_capture',target.uid,{}),)
  else:operations=(('historical_utility_pair_kill',target.uid),('heal_own_hero',target.health))
  return operations[0],operations[1:]
 if name=='historical_utility_horseman':
  enemies=[m for m in game.players[1-owner].minions if m.health>0]
  operations=[]
  if enemies:
   attack=max(m.attack for m in enemies);victim=game.rng.choice([m for m in enemies if m.attack==attack]);operations.append(('historical_utility_pair_kill',victim.uid))
  operations.append(('insert_fixed','TOY_829t',1,'shuffle'))
  return operations[0],tuple(operations[1:])
 if name=='historical_utility_swing':
  game.players[owner].historical_swing_immune_turn=game.turn
  operations=tuple(('historical_utility_hero_force',m.uid) for m in game.players[1-owner].minions if m.health>0)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_utility_stargazing':
  state={}
  return ('historical_utility_arcane_draw',state),(('historical_utility_arcane_repeat',state),)
 if name=='historical_utility_domino':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  board=game.players[target.owner].board;position=board.index(target)
  directions=[direction for direction in (-1,1) if 0<=position+direction<len(board) and board[position+direction] in game.players[target.owner].minions]
  direction=game.rng.choice(directions) if len(directions)>1 else directions[0] if directions else 1
  victims=[target.uid];index=position+direction
  while 0<=index<len(board) and board[index] in game.players[target.owner].minions:
   victims.append(board[index].uid);index+=direction
  operations=tuple(('historical_utility_domino_hit',uid,2+i) for i,uid in enumerate(victims))
  return operations[0],operations[1:]
 if name=='historical_utility_riot':
  units=[m for m in game.players[owner].minions if m.health>0]
  for m in units:m.rule_state['historical_riot_turn']=game.turn
  state=dict(summoned=[m.uid for m in units],mode='random_enemy_minion')
  return game._split_fixed_summon(('force_group_attacks',state),ctx)
 if name=='historical_utility_wither':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  operations=tuple(('historical_utility_wither_steal',target.uid,m.uid) for m in game.players[owner].minions if m.health>0 and has_tribe(game._card_data(m),'UNDEAD'))
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_utility_banner':
  revealed=[]
  for player_id in (owner,1-owner):
   deck=game.players[player_id].deck;index=game.rng.randrange(len(deck)) if deck else None;revealed.append(index)
   if index is not None:game._log('joust_reveal',player=player_id,card=game._card_data(deck[index])['id'])
  own,other=revealed
  won=own is not None and (other is None or game._card_stat(game.players[owner].deck[own],'cost',owner)>game._card_stat(game.players[1-owner].deck[other],'cost',1-owner))
  return (('historical_batch_joust_draw',own),()) if won else (('batch30_noop',),())
 if name=='historical_utility_misfire':
  choose=getattr(ctx.get('physical_card'),'_hand_entry_turn',None)==game.turn
  operations=tuple(('historical_utility_target_damage',amount,'minion',choose) for amount in (3,2,1))
  return operations[0],operations[1:]
 if name=='historical_utility_nets':
  if getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_cost_naga_played'):return ('historical_utility_target_damage',2,'enemy_character',True),()
  return ('batch30_noop',),()
 if name=='historical_utility_spotlight':
  target=next((m for m in game.players[owner].minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is None or 'DIVINE_SHIELD' not in game._effective_keywords(target):return ('batch30_noop',),()
  return ('historical_utility_convert_shield',),(('summon','ETC_320t',1),)
 if name=='historical_utility_applause':return ('draw',1+different_types(game,owner)),()
 if name=='historical_utility_prison':
  request=pool(card_type='SPELL');values=game._autocast_candidates(request,owner)
  if op[1]<=0 or not values:return ('batch30_noop',),()
  first,tail=game._cast_spell_split(('cast_fixed_spell',game.rng.choice(values),'prefer_selected'),ctx)
  return first,tuple(tail)+((('historical_utility_prison',op[1]-1),) if op[1]>1 else ())
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 from .historical_pool_closure import execute as execute_pool
 if execute_pool(game,op,ctx):return True
 from .historical_soul_mirror import execute as execute_mirror
 if execute_mirror(game,op,ctx):return True
 from .historical_iconic_followups import execute as execute_iconic
 if execute_iconic(game,op,ctx):return True
 from .historical_iconic_attack_secrets import execute as execute_attack_secret
 if execute_attack_secret(game,op,ctx):return True
 if name=='historical_utility_boom_squad':
  from .historical_family_batches import LACKEYS
  require_fixed_cards(LACKEYS,game.cards)
  groups=[tuple(LACKEYS)]
  for tribe in ('MECHANICAL','DRAGON'):
   groups.append(tuple(game._generation_discover_candidates(pool(card_type='MINION',tribe=tribe,classes='own_or_neutral'),ctx)))
  # All categories are checked before any selection; overlapping tribes may
  # independently produce the same identity in different category slots.
  options=[dict(card_id=game.rng.choice(values)) for values in groups if values]
  if options:
   game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='boom_squad',options=options);game.phase='choice'
  return True
 if name=='historical_utility_forbidden_words':
  amount=p.mana
  p.mana=0
  game._b60_spend_mana(owner,amount)
  target=game._force_live(ctx.get('target'))
  if target is not None and target.attack<=amount:target.health=0
  return True
 if name=='historical_utility_dark_skies_hit':
  values=[m.uid for player in game.players for m in player.minions if m.health>0]
  if values:game._deal_effect(game.rng.choice(values),1,ctx)
  return True
 if name=='historical_utility_plot_shuffle':
  originals=op[1];cards=[]
  for original in originals:
   if not any(card is original for card in p.hand):continue
   game._remember_crafted(original)
   clean=game._fresh_replay_card(original);clean.uid=original.uid
   game._carry_origin(original,clean)
   if getattr(original,'rule_state',{}).get('shatter_combined'):game._b60_state(clean)['shatter_combined']=True
   cards.append(clean)
  moved={card.uid for card in cards}
  p.hand=[card for card in p.hand if card.uid not in moved]
  p.deck.extend(cards);game.rng.shuffle(p.deck);game._refresh_auras()
  if cards:game._record_deck_insertion(owner,owner,len(cards),'shuffle',cards=tuple(cards))
  game._log('shuffle_from_hand',player=owner,count=len(cards))
  return True
 if name=='historical_utility_repeat_brew':
  card=Card(game._new_id(),'DAL_432')
  game._make_temporary(card)
  game._enter_hand(owner,card)
  return True
 if name=='historical_utility_virnaal':
  p.historical_virnaal_turn=game.turn
  return True
 if name=='historical_utility_crackle':
  game._deal_effect(ctx.get('target'),game.rng.randint(3,6),ctx)
  return True
 if name=='historical_utility_primal_fusion':
  target=game._force_live(ctx.get('target'))
  count=sum(has_tribe(game._card_data(m),'TOTEM') for m in p.minions if m.health>0)
  if target is not None:game._buff(target,count,count)
  return True
 if name=='historical_utility_reincarnate_summon':
  donor=op[1]
  game._summon(donor.owner,donor.card_id,entry_origin='resurrection',entry_site='reincarnate',entry_source=donor)
  return True
 if name=='historical_utility_rockbiter':
  uid=ctx.get('target')
  if uid==game.hero_id(owner):game._effect(('hero_attack',3),ctx)
  elif game._force_live(uid) is not None:game._effect(('temporary_attack_buff',3),ctx)
  return True
 if name=='historical_utility_eonar_heal':
  game._heal(game.hero_id(owner),max(0,p.max_health-p.health),healer=owner,spell=False)
  return True
 if name=='historical_utility_eonar_after':
  source=game._force_live(op[1])
  if source is not None and source.card_id=='TTN_903' and not source.silenced:game._summon(source.owner,'TTN_903t4')
  return True
 if name=='historical_utility_wish_attack':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   amount=1 if op[1]=='one' else target.health if op[1]=='health' else target.attack*2
   game._set_minion_attack(target,amount)
  return True
 if name=='historical_utility_wish_savagery':
  game._deal_effect(ctx.get('target'),game._hero_attack(owner),ctx)
  return True
 if name=='historical_utility_wish_coldblood':
  game._effect(('buff',4 if ctx.get('combo') else 2,0),ctx)
  return True
 if name=='historical_utility_wish_battlerage':
  count=int(p.health<p.max_health)+sum(m.health<m.max_health for m in p.minions)
  game._effect(('draw',count),ctx)
  return True
 if name=='historical_utility_wish_bloodlust':
  for m in tuple(p.minions):
   game._effect(('temporary_attack_buff',3),dict(ctx,target=m.uid))
  return True
 if name=='historical_utility_wish_flare':
  for player in game.players:
   for m in player.minions:
    m.keywords.discard('STEALTH')
    m.temporary_keywords[:]=[e for e in m.temporary_keywords if e['keyword']!='STEALTH']
  # Destroyed Secrets do not trigger their reveal effects or Eaglehorn Bow.
  q=game.players[1-owner]
  for secret in tuple(q.secrets):
   q.secrets.remove(secret)
   from .historical_movements import record
   record(game,'destroyed')
  return True
 if name=='historical_utility_wish_soulforest':
  require_fixed_cards(('EX1_158t',),game.cards)
  for m in tuple(p.minions):
   m.attached_death_effects.append(('summon','EX1_158t',1));m.keywords.add('DEATHRATTLE')
  return True
 if name=='historical_utility_wish_explosive':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   board=game.players[target.owner].board;pos=board.index(target)
   victims=[(target.uid,5)]+[(board[i].uid,2) for i in (pos-1,pos+1) if 0<=i<len(board) and board[i] in game.players[target.owner].minions]
   with game._damage_batch():
    for uid,amount in victims:game._deal_effect(uid,amount,ctx)
  return True
 if name=='historical_utility_wish_betrayal':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   board=game.players[target.owner].board;pos=board.index(target)
   victims=[board[i] for i in (pos-1,pos+1) if 0<=i<len(board) and board[i] in game.players[target.owner].minions]
   keywords=game._effective_keywords(target);amount=target.attack
   with game._damage_batch():
    for victim in victims:
     dealt=game._damage(victim.uid,amount,'POISONOUS' in keywords,damage_source=target,damage_owner=target.owner)
     if dealt and 'LIFESTEAL' in keywords:game._heal(game.hero_id(target.owner),dealt,healer=target.owner)
  return True
 if name=='historical_utility_lightbomb':
  victims=tuple((m.uid,m.attack) for player in game.players for m in player.minions if m.health>0)
  with game._damage_batch():
   for uid,amount in victims:game._deal_effect(uid,amount,ctx)
  return True
 if name=='historical_utility_darkbomb':
  uid=ctx.get('target');victim=game.players[-uid-1] if uid and uid<0 else game._force_live(uid)
  if victim is not None:
   game._deal_effect(uid,3,ctx)
   died=victim.health<=0
   game._settle()
   if died and not game.terminal:game._effect(('filtered_draw',(('school','eq','SHADOW'),),1),ctx)
  return True
 if name=='historical_utility_lackey_discover':
  from .historical_family_batches import LACKEYS
  require_fixed_cards(LACKEYS,game.cards)
  if game.pending_choice is not None:raise UnsupportedCard('Cannot replace an active Lackey Discover')
  values=game.rng.sample(list(LACKEYS),3)
  game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='lackey',context=dict(ctx),options=[dict(card_id=cid) for cid in values]);game.phase='choice'
  return True
 if name=='historical_utility_elemental_destruction':
  victims=tuple(m for player in game.players for m in player.minions if m.health>0)
  amounts=[game.rng.randint(4,5) for m in victims]
  with game._damage_batch():
   for victim,amount in zip(victims,amounts):game._deal_effect(victim.uid,amount,ctx)
  return True
 if name=='historical_utility_lightning_breath':
  target=game._force_live(ctx.get('target'))
  if target is None:return True
  victims=[target]
  if any(has_tribe(game._card_data(card),'DRAGON') for card in p.hand):
   board=game.players[target.owner].board;position=board.index(target)
   victims.extend(board[index] for index in (position-1,position+1) if 0<=index<len(board) and board[index] in game.players[target.owner].minions and board[index].health>0)
  with game._damage_batch():
   for victim in victims:game._deal_effect(victim.uid,4,ctx)
  return True
 if name=='historical_utility_vivid_spores':
  for minion in tuple(p.minions):
   if minion.health>0:
    minion.attached_death_effects.append(('historical_event_resummon_bearer',))
    minion.keywords.add('DEATHRATTLE')
  return True
 if name=='historical_utility_elementary_reaction':
  ready=getattr(p,'historical_elemental_completed_streak',0)>0
  card=game._draw(owner,include_burned=True)
  if ready and card is not None:game._enter_hand(owner,game._copy_card(card,source_owner=owner))
  return True
 if name=='historical_utility_runic_summon':
  game._summon(owner,'SCH_612t',entry_keywords=('RUSH',) if op[1] else (),entry_origin='effect',entry_site='runic_carvings')
  return True
 if name=='historical_utility_moment_discovery':
  requests=(pool(card_type='SPELL',classes='DRUID',maximum=p.mana),pool(card_type='MINION',classes='DRUID',maximum=p.mana),pool(card_type='MINION',classes='NEUTRAL',maximum=p.mana))
  groups=[tuple(game._generation_discover_candidates(request,ctx)) for request in requests]
  options=[dict(card_id=game.rng.choice(values)) for values in groups if values]
  if options:
   if game.pending_choice is not None:raise UnsupportedCard('Moment of Discovery cannot replace an active choice')
   game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='moment_discovery',options=options);game.phase='choice'
  return True
 if name=='historical_utility_brukan':
  p.historical_brukan_spells_twice=True
  return True
 if name=='historical_utility_quest_accepted':
  from .historical_whizbang_quests import begin
  begin(game,owner)
  return True
 if name=='historical_utility_ramp_excess':
  if p.max_mana>=p.mana_capacity:
   require_fixed_cards(('CS2_013t',),game.cards)
   game._add(owner,'CS2_013t')
  else:game._effect(('empty_crystals','friendly',op[1]),ctx)
  return True
 if name=='historical_utility_frost_hand_copies':
  originals=tuple(card for card in p.hand if game._card_data(card)['type']=='SPELL' and has_school(game._card_data(card),'FROST'))
  for original in originals:game._enter_hand(owner,game._copy_card(original,source_owner=owner))
 elif name=='historical_utility_metamorphosis':
  require_fixed_cards(('BT_429p','BT_429p2'),game.cards)
  game._replace_primary_power(owner,dict(card_id='BT_429p',remaining=2,restore=deepcopy(p.primary_power)))
 elif name=='historical_utility_blood_boil':
  for minion in game.players[1-owner].minions:
   minion.rule_state.setdefault('historical_blood_boil',[]).append(dict(owner=owner,order=game._new_id()))
 elif name=='historical_utility_boil_tick':
  target=next((m for player in game.players for m in player.minions if m.uid==op[1] and m.health>0),None)
  if target is not None and any(mark['owner']==owner and mark['order']==op[2] for mark in target.rule_state.get('historical_blood_boil',())):
   # Infection is an attached damage-over-time effect, not another paid cast.
   game._deal_effect(target.uid,2,dict(owner=owner,source=None,target=target.uid,bonus=0,lifesteal=True,spell=False,card_id='RLK_730'))
 elif name=='historical_utility_skull_tick':
  if p.weapon and p.weapon['card_id']=='LOOT_420' and getattr(p.equipped_card,'uid',None)==op[1]:
   game._rule_events.append(('captured_effects',dict(operations=(('historical_copy_recruit_one','hand',(('tribe','eq','DEMON'),),None,None),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
 elif name=='historical_utility_refresh_all':
  game._effect(('refresh_mana',max(0,p.max_mana)),ctx)
 elif name=='historical_utility_inner_rage':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target')),None)
  if target is not None:
   with game._damage_batch():
    game._deal_effect(target.uid,1,ctx);game._buff(target,2,0)
 elif name=='historical_utility_ice_lance':
  target=ctx.get('target',0)
  victim=game.players[-target-1] if target<0 else next((m for player in game.players for m in player.minions if m.uid==target),None)
  if victim is not None:
   if victim.frozen_until>=0:game._deal_effect(target,4,ctx)
   else:game._freeze(target)
 elif name=='historical_utility_shadowstep':
  target=next((m for m in p.minions if m.uid==ctx.get('target')),None)
  if target is not None:
   card=game._bounce(target)
   if card is not None:card.cost_delta=getattr(card,'cost_delta',0)-2
 elif name=='historical_utility_vampiric_blood':
  amount=5
  if p.corpses>=3:
   game._spend_corpses(owner,3);amount+=5
   game._rule_events.append(('captured_effects',dict(operations=(('draw',1),),context=dict(ctx)),[]))
  p.max_health+=amount;p.health+=amount
  game._log('hero_health_increased',player=owner,amount=amount)
 elif name=='historical_utility_howling_blast':
  target=ctx.get('target',0)
  victim=game.players[-target-1] if target<0 else next((m for player in game.players for m in player.minions if m.uid==target and m.health>0),None)
  if victim is not None:
   others=tuple([m.uid for m in game.players[1-owner].minions if m.uid!=target]+([game.hero_id(1-owner)] if target!=game.hero_id(1-owner) else []))
   with game._damage_batch():
    game._deal_effect(target,3,ctx);game._freeze(target)
    for uid in others:game._deal_effect(uid,1,ctx)
 elif name=='historical_utility_vanish_uid':
  target=next((m for player in game.players for m in player.minions if m.uid==op[1]),None)
  if target is not None:game._bounce(target)
 elif name=='historical_utility_zola_golden':
  target=game._force_live(ctx.get('target',0))
  if target is not None and target.owner==owner:
   card=game._fresh_replay_card(target);card._golden=True
   game._carry_origin(target,card,copied=True,source_owner=owner)
   game._enter_hand(owner,card)
 elif name=='historical_utility_kazakusan':
  from .historical_kazakusan import begin
  begin(game,ctx)
 elif name=='historical_utility_anomaly_shuffle':
  from .historical_anomalies import shuffle_play_copy
  shuffle_play_copy(game,owner,op[1])
 elif name=='historical_utility_anomaly_end':
  from .historical_anomalies import end_effect
  end_effect(game,owner,op[1])
 elif name=='historical_utility_harth':
  from .historical_iconic_hands import replace_hand
  replace_hand(game,owner)
 elif name=='historical_utility_yogg_outcome':
  if op[1]==2:
   values=game._generation_created_candidates(pool(card_type='SPELL'),ctx)
   for _ in range(max(0,getattr(p,'hand_capacity',10)-len(p.hand))):
    if not values:break
    card=Card(game._new_id(),game.rng.choice(values));card.temporary_cost_discounts=[dict(amount=game._cost(card,owner),end=game.turn)];game._enter_hand(owner,card)
  elif op[1]==5:
   source=ctx.get('source') or game._force_live(ctx.get('caster_uid'));victims=[m for player in game.players for m in player.minions if m is not source and m.health>0]
   attack=sum(m.attack for m in victims);health=sum(m.health for m in victims)
   for minion in victims:minion.health=0
   if source is not None and game._force_live(source.uid) is source:game._buff(source,attack,health)
  else:return False
 elif name=='historical_utility_yogg_rush':
  for minion in p.minions:
   if minion.health>0:minion.keywords.add('RUSH')
 elif name=='historical_utility_yogg_steal':
  values=[m for m in game.players[1-owner].minions if m.health>0]
  if values and len(p.board)<7:
   minion=game.rng.choice(values);game.players[1-owner].board.remove(minion);minion.owner=owner;minion.summoned_turn=game.turn;minion.attacks=0;p.board.append(minion);game._refresh_auras()
 elif name=='historical_utility_relaunch':
  from .historical_starships import relaunch
  relaunch(game,owner,op[1])
 elif name=='historical_utility_stimpack':
  from .historical_starships import is_terran
  for minion in tuple(p.minions):
   if minion.health>0 and is_terran(minion):game._buff(minion,2,0)
 elif name=='historical_utility_ravage_ray':
  values=[game.hero_id(1-owner)]+[m.uid for m in game.players[1-owner].minions if m.health>0];uid=game.rng.choice(values)
  dealt=game._deal_effect(uid,1,dict(ctx,bonus=0,spell=False));p.historical_power_damage_total=getattr(p,'historical_power_damage_total',0)+dealt
  if (ctx.get('power_freeze') or game._active('ICC_068',owner)) and (uid<0 or game._force_live(uid) is not None):game._freeze(uid)
 elif name=='historical_utility_demon_portal':
  from .historical_demon_portal import open_portal
  open_portal(game,owner)
 elif name=='historical_utility_portal_grow':
  from .historical_demon_portal import grow
  grow(game,owner)
 elif name=='historical_utility_quel_forge':forge_quel_delar(game,owner)
 elif name=='historical_utility_reflection_one':
  donor=op[1];game._summon(owner,donor.card_id,copy_from=donor,entry_stats=(1,1),entry_origin='copy',entry_site='ancient_reflections')
 elif name=='historical_utility_puzzle_one':
  target=game._force_live(op[1])
  if target is not None:
   from .game import Minion
   from .historical_copy_batches import replace
   raw=game.cards[op[2]];donor=Minion(game._new_id(),op[2],target.owner,raw['attack'],raw['health'],raw['health'],set(raw.get('mechanics',())))
   replace(game,target,donor)
 elif name=='historical_utility_annoy':
  values=('ETC_109','GVG_085','BOT_911','OG_145','ETC_321')
  require_fixed_cards(values,game.cards)
  for _ in range(max(0,7-len(p.board))):game._summon(owner,game.rng.choice(values),entry_origin='effect',entry_site='annoy_o_horn')
 elif name=='historical_utility_crusty':
  target=game._force_live(ctx.get('target'));source=ctx.get('source')
  if target is not None and source is not None:
   attack,health=target.attack,target.health;target.health=0;game._buff(source,attack,health)
 elif name=='historical_utility_beauty':
  source=ctx.get('source')
  if source is not None and game._force_live(source.uid) is source:
   from .game import Minion
   from .historical_copy_batches import replace
   cid='VAC_464t27t' if source.card_id=='VAC_464t27' else 'ONY_005ta9t'
   raw=game.cards[cid];donor=Minion(game._new_id(),cid,owner,raw['attack'],raw['health'],raw['health'],set(raw.get('mechanics',())))
   replace(game,source,donor)
 elif name=='historical_utility_spyglass':
  hand=game.players[1-owner].hand
  if hand:
   card=game._copy_card(game.rng.choice(hand),source_owner=1-owner);card.cost_delta=getattr(card,'cost_delta',0)-(3);game._enter_hand(owner,card)
 elif name=='historical_utility_holy_capture':
  target=game._force_live(op[1])
  if target is not None:
   game._silence(target);donor=deepcopy(target);target.health=0
   game._rule_events.append(('captured_effects',dict(operations=(('historical_utility_treasure_copy',donor,True),),context=dict(ctx)),[]))
 elif name=='historical_utility_treasure_copy':
  donor=op[1]
  game._summon(owner,donor.card_id,copy_from=donor,entry_stats=(10,10) if op[2] else None,entry_origin='copy',entry_site='kazakusan_treasure')
 elif name=='historical_utility_pure_cold':game._freeze(game.hero_id(1-owner))
 elif name=='historical_utility_disintegration':
  for minion in tuple(game.players[1-owner].minions):
   if minion.health>0:game._silence(minion);minion.health=0
 elif name=='historical_utility_jars':
  from .generation_cards import random_cards
  request=pool(card_type='MINION',rarity='LEGENDARY')
  game._generation_created_candidates(request,ctx)
  for minion in tuple(p.minions):
   if minion.health>0:minion.attached_death_effects.append(random_cards(request,destination='board'));minion.keywords.add('DEATHRATTLE')
 elif name=='historical_utility_embers':
  values=[game.hero_id(1-owner)]+[m.uid for m in game.players[1-owner].minions if m.health>0]
  game._deal_effect(game.rng.choice(values),8,ctx)
 elif name=='historical_utility_conductivity':p.historical_conductivity_turn=game.turn
 elif name=='historical_utility_reno_clear':
  from .identities import canonical_identity
  identities=[canonical_identity(game._starting_card_data(owner,cid),game.cards) for cid in p.starting_deck]
  if len(identities)==len(set(identities)):
   victims=tuple(minion for minion in game.players[1-owner].minions if not minion.dormant)
   for minion in victims:
    game.players[1-owner].board.remove(minion)
    game._pending_summon_events.pop(minion.uid,None)
    game._log('remove_from_game',player=1-owner,entity=minion.uid,card=minion.card_id)
   game._refresh_auras()
 elif name=='historical_utility_horseman_head':
  power=p.primary_power
  if power is not None and power['card_id']=='TOY_829hp3':
   power['card_id']='TOY_829hp';game._log('horseman_power_upgraded',player=owner,card='TOY_829hp')
 elif name=='historical_utility_multistrike':
  state=getattr(p,'historical_multistrike',{})
  if state.get('turn')!=game.turn:state=dict(turn=game.turn,grants=0,minion_attacks=0)
  state['grants']+=1;p.historical_multistrike=state
 elif name=='historical_utility_hero_force':
  if game._force_live(op[1]) is not None and p.health>0:game._attack(game.hero_id(owner),op[1],forced=True)
 elif name=='historical_utility_mount':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   require_fixed_cards(tuple(CHAMELEONS.values()),game.cards)
   values=game._bonus_pool(target)
   if not values:
    from .approximation_policy import mark
    mark(game,'camouflage');values=tuple(sorted(CHAMELEONS))
   keyword=game.rng.choice(values);target.keywords.add(keyword)
   target.attached_death_effects.append(('summon',CHAMELEONS[keyword],1));target.keywords.add('DEATHRATTLE')
 elif name=='historical_utility_arcane_draw':
  from .identities import canonical_identity
  creator=canonical_identity(game.cards['WW_425'],game.cards)
  choices=[i for i,c in enumerate(p.deck) if game._card_data(c)['type']=='SPELL' and has_school(game._card_data(c),'ARCANE') and canonical_identity(game._card_data(c),game.cards)!=creator]
  if choices:
   card=game._take_deck_draw(owner,game.rng.choice(choices),include_burned=True)
   if card is not None:op[1]['card']=card
 elif name=='historical_utility_arcane_repeat':
  card=op[1].get('card')
  if card is not None and card in p.hand:game._b60_state(card)['historical_stargazing_turn']=game.turn
 elif name=='historical_utility_domino_hit':
  if game._force_live(op[1]) is not None:game._deal_effect(op[1],op[2],ctx)
 elif name=='historical_utility_wither_steal':
  target=game._force_live(op[1]);recipient=game._force_live(op[2])
  if target is not None and recipient is not None:
   attack=min(1,max(0,target.attack));health=min(1,max(0,target.health))
   game._buff(target,-attack,-health);game._buff(recipient,attack,health)
 elif name=='historical_utility_gold':
  groups=[game._generation_created_candidates(pool(card_type='MINION',tribe=tribe,classes='other'),ctx) for tribe in ('PIRATE','ELEMENTAL')]
  for values in groups:
   if values:
    card=Card(game._new_id(),game.rng.choice(values));game._b60_state(card)['historical_golden']=True;game._enter_hand(owner,card)
 elif name=='historical_utility_target_damage':
  values=game._targets_for(ctx['card_id'],owner,op[2]) if op[3] else [m.uid for player in game.players for m in player.minions if m.health>0]
  if values:
   if op[3]:
    if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite damage-target choice')
    game.pending_choice=dict(owner=owner,kind='historical_utility_damage_target',context=dict(ctx),amount=op[1],options=[dict(uid=uid,card_id=game._force_live(uid).card_id if uid>0 else 'HERO') for uid in values]);game.phase='choice'
   else:game._deal_effect(game.rng.choice(values),op[1],ctx)
 elif name=='historical_utility_target_hit':game._deal_effect(op[1],op[2],ctx)
 elif name=='historical_utility_pair_choice':
  target=game._force_live(ctx.get('target'))
  if target is not None and target.health>0:
   candidates=[m for m in game.players[1-owner].minions if m.health>0 and m.uid!=target.uid and m.uid in game._targets_for(ctx['card_id'],owner,'enemy_minion')]
   if candidates:
    if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite second-target choice')
    game.pending_choice=dict(owner=owner,kind='historical_utility_pair_target',context=dict(ctx),mode=op[1],first=target,options=[dict(card_id=m.card_id,uid=m.uid) for m in candidates]);game.phase='choice'
 elif name=='historical_utility_pair_kill':
  target=game._force_live(op[1])
  if target is not None and target.health>0:target.health=0
 elif name=='historical_utility_pair_copy_dead':
  for target in op[1]:
   if target.health<=0:game._enter_hand(owner,game._fresh_replay_card(target))
 elif name=='historical_utility_potion':
  from .historical_copy_batches import CONCOCTIONS,CONCOCTION_IDS
  require_fixed_cards(CONCOCTION_IDS,game.cards)
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Concoction Discover')
  game.pending_choice=dict(owner=owner,kind='historical_utility_potion',context=dict(ctx),options=[dict(card_id=cid) for cid in game.rng.sample(list(CONCOCTIONS),3)])
  game.phase='choice'
 elif name=='historical_utility_maki_copy':
  card=Card(game._new_id(),'TSC_952');game._make_temporary(card);game._enter_hand(owner,card)
 elif name=='historical_utility_recruit':
  require_fixed_cards(('CS2_101t','HERO_11bpt'),game.cards)
  card=Card(game._new_id(),'CS2_101t');game._b60_state(card)['historical_granted_deaths']=[('summon','HERO_11bpt',1)]
  game._summon(owner,'CS2_101t',entry_source=card,entry_origin='effect',entry_site='mining_casualties')
 elif name=='historical_utility_convert_shield':
  target=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is not None and 'DIVINE_SHIELD' in game._effective_keywords(target):
   target.keywords.discard('DIVINE_SHIELD');target.temporary_keywords[:]=[e for e in target.temporary_keywords if e['keyword']!='DIVINE_SHIELD']
   game._queue_event('shield_lost',owner=owner,target=target.uid)
 else:return False
 return True


def resolve_choice(game,choice,selected):
 from .historical_final_spell_roots import resolve_choice as final_root_choice
 if final_root_choice(game,choice,selected):return True
 from .historical_obligation_spells import resolve_choice as obligation_choice
 if obligation_choice(game,choice,selected):return True
 from .historical_trade_spell_finish import resolve_choice as trade_finish_choice
 if trade_finish_choice(game,choice,selected):return True
 from .historical_deck_choice_finish import resolve_choice as deck_finish_choice
 if deck_finish_choice(game,choice,selected):return True
 from .historical_history_spell_batch import resolve_choice as history_batch_choice
 if history_batch_choice(game,choice,selected):return True
 from .historical_spell_continuation import resolve_choice as continuation_choice
 if continuation_choice(game,choice,selected):return True
 from .historical_spell_archive_batch import resolve_choice as archive_choice
 if archive_choice(game,choice,selected):return True
 from .historical_nature_pool import resolve_choice as resolve_nature
 if resolve_nature(game,choice,selected):return True
 from .historical_mage_offers import resolve_choice as resolve_mage_offer
 if resolve_mage_offer(game,choice,selected):return True
 from .historical_mage_decks import resolve_choice as resolve_mage_deck
 if resolve_mage_deck(game,choice,selected):return True
 from .historical_iconic_followups import resolve_choice as resolve_iconic
 if resolve_iconic(game,choice,selected):return True
 if choice['kind']=='historical_utility_damage_target':
  game._rule_events.append(('captured_effects',dict(operations=(('historical_utility_target_hit',selected['uid'],choice['amount']),),context=dict(choice['context'])),[]))
  return True
 if choice['kind']=='historical_utility_pair_target':
  owner=choice['owner'];first=choice['first'];second=game._force_live(selected['uid']);ctx=choice['context']
  if game._force_live(first.uid) is first and first.health>0 and second is not None and second.health>0:
   if choice['mode']=='fight':operations=(('force_pair',first.uid,second.uid),('historical_utility_pair_copy_dead',(first,second)))
   else:operations=(('historical_utility_pair_kill',first.uid),('historical_utility_pair_kill',second.uid))
   game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(ctx)),[]))
  return True
 if choice['kind']!='historical_utility_potion':return False
 game._discovery_result=game._add(choice['owner'],selected['card_id'])
 return True


def reno_power_operations(game,owner):
 from .generation_cards import discover,random_cards
 power=game.players[owner].primary_power
 if power is None or power['card_id'] not in RENO_BULLETS:return None
 cid=power['card_id'];operations=[('damage',2)]
 if cid=='WW_0700p1':operations.append(('refresh_mana',2))
 elif cid=='WW_0700p2':operations.append(('armor',4))
 elif cid=='WW_0700p3':operations.append(('area_damage','enemy_minions',1))
 elif cid=='WW_0700p4':operations.append(('buff_random_friendly',2,2))
 elif cid=='WW_0700p5':operations.append(discover(pool(card_type='SPELL',classes='own_or_neutral')))
 elif cid=='WW_0700p6':operations.append(random_cards(pool(card_type='MINION',minimum=3,maximum=3),destination='board'))
 elif cid=='WW_0700p7':operations.append(('draw',1))
 return tuple(operations)


def conductivity_program(game,operations,context):
 owner=context['owner'];p=game.players[owner]
 if getattr(p,'historical_conductivity_turn',None)!=game.turn:return operations
 p.historical_conductivity_turn=None
 target=game._force_live(context.get('target'))
 if target is None:return operations
 board=game.players[target.owner].board;index=board.index(target)
 neighbors=[board[i] for i in (index-1,index+1) if 0<=i<len(board) and board[i] in game.players[target.owner].minions and board[i].health>0]
 original=tuple(operations)
 return list(original)+[('replay_context',original,dict(context,target=m.uid)) for m in neighbors]


def forge_quel_delar(game,owner):
 if getattr(game,'_historical_quel_forging',False):return
 p=game.players[owner]
 blades=[(zone,card) for zone in (p.hand,p.deck) for card in zone if (card if isinstance(card,str) else card.card_id) in ('ONY_005tc5','VAC_464t29')]
 hilts=[(zone,card) for zone in (p.hand,p.deck) for card in zone if (card if isinstance(card,str) else card.card_id) in ('ONY_005tc6','VAC_464t30')]
 if not blades or not hilts:return
 require_fixed_cards(tuple('VAC_464t31' if (card if isinstance(card,str) else card.card_id)=='VAC_464t29' else 'ONY_005tc7' for zone,card in blades[:len(hilts)]),game.cards)
 game._historical_quel_forging=True
 try:
  for (blade_zone,blade),(hilt_zone,hilt) in zip(blades,hilts):
   hilt_zone.remove(hilt)
   if isinstance(blade,str):
    index=blade_zone.index(blade);blade=Card(game._new_id(),blade);blade_zone[index]=blade
   game._b60_transform_card(blade,'VAC_464t31' if blade.card_id=='VAC_464t29' else 'ONY_005tc7')
   game._log('quel_delar_forged',player=owner,entity=blade.uid,in_hand=blade_zone is p.hand)
 finally:game._historical_quel_forging=False


# Literal historic iconic-hand dependencies. Frozen printed versions are used;
# launch Demon Hunter tokens are a separate existing family.
TOKEN_RULES.update({
 'RLK_125':('minion',[('destroy',),('damage_own_hero',3)]),
 'LEG_RLK_125':('minion',[('destroy',),('damage_own_hero',3)]),
 'RLK_042':('none',[('refresh_mana',2)]),
 'RLK_018':('minion',[('historical_damage_then',3,'dead',(('summon','RLK_018t',1),))]),
 'RLK_512':('character',[('damage',4),('historical_copy_lunar_eclipse',)]),
 'EX1_161':('minion',[('destroy',),('historic_opponent_draw',2)]),
 'CS2_026':('none',[('freeze_enemies',)]),
 'CS2_031':('character',[('historical_utility_ice_lance',)]),
 'BRM_007':('minion',[('historical_copy_target_delivery','deck',3,None,None,None,False)]),
 'EX1_144':('friendly_minion',[('historical_utility_shadowstep',)]),
 'NEW1_004':('none',[('historical_utility_vanish',)]),
 'UNG_025':('none',[('missiles','all_minions',15)]),
 'LOOT_017':('friendly_minion',[('destroy',),('heal_own_hero',8)]),
 'EX1_607':('minion',[('historical_utility_inner_rage',)]),
 'EX1_400':('none',[('area_damage','all_minions',1)]),
 'RLK_051':('none',[('historical_utility_vampiric_blood',)]),
 'RLK_015':('enemy_character',[('historical_utility_howling_blast',)]),
})

# Keep all late-declared historic spell outcomes in the generated registry.
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


TOKEN_RULES.update({
 'ICC_041':('none',[('historical_sleep_repeat_area',1)]),
 'RLK_730':('none',[('historical_utility_blood_boil',)]),
 'LOOT_392':('none',[]),
 'LOOT_420':('none',[]),
 'YOP_011':('none',[]),'YOP_011t':('none',[]),
 'KAR_004':('none',[('secret','KAR_004')]),
 'CORE_KAR_004':('none',[('secret','CORE_KAR_004')]),
 'KAR_004a':('none',[]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def iconic_turn_entries(game,phase):
 owner=game.current;p=game.players[owner];entries=[]
 if phase=='start' and p.weapon and p.weapon['card_id']=='LOOT_420':
  entries.append(dict(source=None,order=getattr(p.equipped_card,'uid',0),card_id='LOOT_420',operations=(('historical_utility_skull_tick',getattr(p.equipped_card,'uid',None)),)))
 if phase=='end':
  for player in game.players:
   for minion in player.minions:
    for mark in minion.rule_state.get('historical_blood_boil',()):
     if mark['owner']==owner:
      entries.append(dict(source=None,order=mark['order'],operations=(('historical_utility_boil_tick',minion.uid,mark['order']),)))
 return entries

from .historical_iconic_followups import TOKEN_RULES as ICONIC_FOLLOWUP_RULES
TOKEN_RULES.update(ICONIC_FOLLOWUP_RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES.update({
 'RLK_713':('none',[]),
 'LOOT_079':('none',[('secret','LOOT_079')]),
 'CORE_LOOT_079':('none',[('secret','CORE_LOOT_079')]),
 'EX1_533':('none',[('secret','EX1_533')]),
 'VAN_EX1_533':('none',[('secret','VAN_EX1_533')]),
 'BT_175':('none',[('hero_attack',2),('add','BT_175t',1)]),
 'BT_175t':('none',[('hero_attack',2)]),
 'BT_601':('none',[('historical_mint_skull',)]),
 'BT_429':('none',[('historical_utility_metamorphosis',)]),
 'CORE_BT_429':('none',[('historical_utility_metamorphosis',)]),
 'BT_430':('none',[]),'CORE_BT_430':('none',[]),
 'BT_429p':('none',[]),'BT_429p2':('none',[]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES['BT_198']=('none',[('historical_utility_soul_mirror',)])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Written source consumers of the complete explicit Standard Zombeast contracts.
from .generation_cards import discover as _iconic_discover
TOKEN_RULES.update({
 'RLK_821':('none',[('forge_zombeast_plain',)]),
 'ICC_828':('none',[('area_damage','enemy_minions',2)]),
 'CORE_ICC_828':('none',[('area_damage','enemy_minions',2)]),
 'ICC_828p':('none',[]),'ICC_828t':('none',[]),
 'VAC_336':('none',[_iconic_discover(pool(era='past',card_type='HERO',classes='other'))]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Constructed body requires a physical compiled component definition at entry.
TOKEN_RULES['CATA_470t1']=('none',[])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Eudora treasure printings share the same complete effect programs.
EUDORA_TREASURE_EQUIVALENTS={'VAC_464t10': 'ONY_005ta10', 'VAC_464t11': 'ONY_005ta11', 'VAC_464t12': 'ONY_005ta13', 'VAC_464t14': 'ONY_005tb1', 'VAC_464t15': 'ONY_005tb2', 'VAC_464t16': 'ONY_005tb4', 'VAC_464t17': 'ONY_005tb5', 'VAC_464t18': 'ONY_005tb7', 'VAC_464t19': 'ONY_005tb8', 'VAC_464t2': 'ONY_005ta1', 'VAC_464t20': 'ONY_005tb9', 'VAC_464t21': 'ONY_005tb12', 'VAC_464t22': 'ONY_005tb13', 'VAC_464t23': 'ONY_005tc1', 'VAC_464t24': 'ONY_005tc2', 'VAC_464t25': 'ONY_005tc3', 'VAC_464t26': 'ONY_005ta12', 'VAC_464t27': 'ONY_005ta9', 'VAC_464t27t': 'ONY_005ta9t', 'VAC_464t28': 'ONY_005tb14', 'VAC_464t29': 'ONY_005tc5', 'VAC_464t3': 'ONY_005ta2', 'VAC_464t30': 'ONY_005tc6', 'VAC_464t31': 'ONY_005tc7', 'VAC_464t31t': 'ONY_005tc7t', 'VAC_464t4': 'ONY_005ta3', 'VAC_464t5': 'ONY_005ta4', 'VAC_464t6': 'ONY_005ta5', 'VAC_464t7': 'ONY_005ta6', 'VAC_464t8': 'ONY_005ta7', 'VAC_464t9': 'ONY_005ta8'}
for _eudora_id,_treasure_id in EUDORA_TREASURE_EQUIVALENTS.items():
 TOKEN_RULES[_eudora_id]=deepcopy(TOKEN_RULES[_treasure_id])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES.update({cid:('none',[('historical_eudora_start',)]) for cid in ('VAC_464','VAC_464t')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Root remains staged until the exact bullet transition contract is sourced.
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Non-activatable base Handcannon is immediately replaced with a live bullet.
TOKEN_RULES['WW_0700p']=('none',[])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Full fixed-tour dependencies, using each legacy printing's frozen text.
TOKEN_RULES.update({
 'CS1_113':('enemy_minion',[('historical_tour_mind_control',)]),
 'CS2_011':('none',[('historic_temporary_attack','friendly',2,'end'),('hero_attack',2)]),
 'CS2_012':('enemy_character',[('historical_tour_swipe',)]),
 'CS2_028':('none',[('area_damage','enemy_minions',2),('freeze_enemies',)]),
 'EX1_124':('character',[('historical_tour_eviscerate',)]),
 'EX1_246':('minion',[('transform','hexfrog')]),
 'EX1_303':('friendly_minion',[('historical_tour_shadowflame',)]),
 'EX1_308':('character',[('damage',4),('discard',1)]),
 'EX1_312':('none',[('destroy_battlefield',)]),
 'EX1_334':('historical_copy_shadow_madness_target',[('historical_copy_shadow_madness',)]),
 'EX1_354':('character',[('heal',8),('draw',3)]),
 'EX1_383':('none',[]),
 'EX1_384':('none',[('missiles','enemies',8)]),
 'EX1_407':('none',[('historical_tour_brawl',)]),
 'EX1_408':('character',[('historical_tour_mortal',)]),
 'EX1_626':('none',[('historic_board_silence','enemy'),('draw',1)]),
 'NEW1_007':('none',[]),
 'WORK_027':('none',[('historical_tour_begin',)]),
})
TOKEN_RULES.update({cid:('none',[('historical_tour_generate',cid)]) for cid in ('WORK_027t1','WORK_027t2','WORK_027t3')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Frozen original printings needed by Elise's complete non-Quest pack pool.
from .generation_cards import discover as _ungoro_discover,random_cards as _ungoro_random
TOKEN_RULES.update({
 'UNG_004':('minion',[('set_target_stats',7,14)]),
 'UNG_029':('none',[('historical_play_zone_offer','own','deck',(('type','eq','SPELL'),),'copy',3,True)]),
 'UNG_030':('minion',[('heal',5),('heal_own_hero',5)]),
 'UNG_057':('none',[('add','UNG_057t1',2)]),
 'UNG_060':('none',[('historical_ungoro_mimic',)]),
 'UNG_072':('none',[_ungoro_discover(pool(card_type='MINION',mechanic='TAUNT',classes='own_or_neutral'))]),
 'UNG_084':('character',[('damage',3)]),
 'UNG_103':('none',[('historical_upgrade_adapt','friendly')]),
 'UNG_108':('friendly_minion',[('buff',1,1),('historical_ungoro_scales',)]),
 'UNG_809':('none',[('add','UNG_809t1',1)]),
 'UNG_823':('weapon_required',[('historical_ungoro_envenom',)]),
 'UNG_854':('none',[_ungoro_discover(pool(card_type='MINION',minimum=8),destination='board')]),
 'UNG_856':('none',[('historical_ungoro_spore',)]),
 'UNG_910':('minion',[('historical_ungoro_cleave',3,1)]),
 'UNG_912':('none',[_ungoro_random(pool(card_type='MINION',tribe='BEAST'))]),
 'UNG_927':('none',[('historical_ungoro_genesis',)]),
 'UNG_941':('none',[_ungoro_discover(pool(card_type='SPELL',classes='own_or_neutral'),cost_delta=-2)]),
 'UNG_948':('friendly_minion',[('historical_ungoro_reflection',)]),
 'UNG_950':('none',[]),
 'UNG_952':('minion',[('buff',2,6),('keyword','TAUNT'),('grant_death_target',(('death_summon','UNG_810',1),))]),
 'UNG_955':('minion',[('historical_ungoro_cleave',15,4)]),
 'UNG_956':('none',[('historical_ungoro_echo',)]),
 'UNG_961':('friendly_minion',[('historical_upgrade_adapt','target')]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES.update({
 'UNG_831':('none',[('historical_ungoro_mist',)]),
 'UNG_834':('minion',[('damage',3),('historical_ungoro_feeding',)]),
 'UNG_834t1':('none',[]),
 'UNG_917':('none',[('historical_ungoro_dinomancy',)]),
 'UNG_917t1':('minion',[('buff',3,3)]),
 'UNG_922':('none',[('historical_ungoro_explore',)]),
 'UNG_922t1':('none',[_ungoro_discover(pool(classes='own_or_neutral'))]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES.update({'UNG_024':('none',[('secret','UNG_024')]),'UNG_061':('none',[]),'UNG_916':('none',[('historical_ungoro_stampede',)]),'UNG_929':('none',[])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES['UNG_832']=('none',[('historical_copy_next_payment','health','spell',1)])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES.update({'UNG_111':('none',[('historical_ungoro_living',)]),'UNG_111t1':('none',[])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES.update({cid:('none',[('secret',cid)]) for cid in ('EX1_287','EX1_289')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Explicit alternate printings; metadata and all native hooks stay per identity.
TOKEN_RULES.update({'CORE_RLK_741': ('none', [('historical_copy_soulstealer',)]), 'RLK_706': ('none', [('permanent_end_damage', 3)]), 'CORE_RLK_051': ('none', [('historical_utility_vampiric_blood',)]), 'RLK_087': ('none', [('asphyxiate',)]), 'RLK_071': ('none', [('historical_copy_patchwerk', 'hand'), ('historical_copy_patchwerk', 'deck'), ('historical_copy_patchwerk', 'board')]), 'RLK_063': ('character', [('damage', 5), ('freeze_enemies',), ('summon', 'RLK_063t', 1)]), 'CORE_RLK_042': ('none', [('refresh_mana', 2)]), 'RLK_062': ('none', [('copy_self_right', 2)]), 'BT_493': ('none', []), 'VAN_EX1_161': ('minion', [('destroy',), ('historic_opponent_draw', 2)]), 'CORE_ICC_832': ('none', []), 'CORE_ICC_054': ('none', [('historical_utility_plague',)]), 'CORE_KAR_006': ('none', []), 'CORE_VAN_EX1_561': ('hero', [('historical_event_alexstrasza',)]), 'VAN_EX1_561': ('hero', [('historical_event_alexstrasza',)]), 'VAN_NEW1_021': ('none', []), 'VAN_CS2_026': ('none', [('freeze_enemies',)]), 'VAN_CS2_031': ('character', [('historical_utility_ice_lance',)]), 'VAN_CS2_029': ('character', [('damage', 6)]), 'VAN_CS2_024': ('character', [('damage', 3), ('freeze',)]), 'VAN_EX1_559': ('none', []), 'CORE_BT_334': ('none', [('historical_copy_friendly_spell_history',)]), 'EX1_145': ('none', [('next_discount', 'SPELL', 2, 'turn')]), 'CORE_EX1_049': ('friendly_minion', [('bounce',)]), 'VAN_EX1_049': ('friendly_minion', [('bounce',)]), 'CORE_LOE_077': ('none', []), 'CORE_EX1_050': ('none', [('draw', 2), ('historical_copy_enemy_draw', 2)]), 'VAN_EX1_050': ('none', [('draw', 2), ('historical_copy_enemy_draw', 2)]), 'CORE_EX1_144': ('friendly_minion', [('historical_utility_shadowstep',)]), 'VAN_EX1_144': ('friendly_minion', [('historical_utility_shadowstep',)]), 'VAN_NEW1_004': ('none', [('historical_utility_vanish',)]), 'LOOT_373': ('none', [('random_heal', 12)]), 'GIL_622': ('none', [('damage_enemy_heal_own', 3, 3)]), 'CORE_ICC_831': ('none', [('historical_resurrection_pick', 'demon', -1, ())]), 'CORE_EX1_564': ('minion', [('historical_copy_transform_target', None, None)]), 'VAN_EX1_564': ('minion', [('historical_copy_transform_target', None, None)]), 'EX1_310': ('none', [('discard', 2)]), 'VAN_EX1_310': ('none', [('discard', 2)]), 'CORE_ICC_041': ('none', [('historical_sleep_repeat_area', 1)]), 'VAN_EX1_607': ('minion', [('historical_utility_inner_rage',)]), 'CS2_108': ('damaged_enemy_minion', [('destroy',)]), 'VAN_CS2_108': ('damaged_enemy_minion', [('destroy',)]), 'VAN_EX1_604': ('none', []), 'CORE_EX1_084': ('none', []), 'VAN_EX1_084': ('none', []), 'CORE_EX1_400': ('none', [('area_damage', 'all_minions', 1)]), 'VAN_EX1_400': ('none', [('area_damage', 'all_minions', 1)]), 'CORE_LOOT_051': ('minion', [('damage', 2)]), 'VAN_EX1_145': ('none', [('next_discount', 'SPELL', 3, 'turn')]), 'CORE_ICC_466': ('none', [('copy_self_right', 1)]), 'EX1_610': ('none', [('secret', 'EX1_610')]), 'VAN_EX1_610': ('none', [('secret', 'VAN_EX1_610')]), 'EX1_611': ('none', [('secret', 'EX1_611')]), 'VAN_EX1_611': ('none', [('secret', 'VAN_EX1_611')])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES.update({'CORE_FB_Champs_LOOT_080':('none',[('summon','LOOT_077t',2)]),'CORE_LOOT_516':('friendly_minion',[('historical_utility_zola_golden',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Scythe's nontrivial opening behavior is installed before mulligan.
TOKEN_RULES.update({'RLK_214':('none',[]),'RLK_214t':('none',[('historical_scythe_discover',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'CS2_072': ('undamaged_minion', [('damage', 2)]), 'EX1_012': ('none', []), 'DAL_720': ('none', []), 'ULD_271': ('none', [('damage_self', 3)]), 'EX1_581': ('enemy_minion', [('bounce',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'EX1_410': ('minion', [('damage_armor',)]), 'DRG_301': ('none', [('historical_family_lackeys', 1)]), 'ULD_708': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'DAL_063': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'DAL_065': ('friendly_minion', [('silence',), ('historical_utility_unsleep_copy',)]), 'DRG_022': ('minion', [('historical_utility_ramming_speed',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'YOD_023': ('none', [('historical_utility_boom_squad',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'DAL_723': ('minion', [('historical_utility_forbidden_words',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'CS2_053': ('none', [('draw_discount', 3)]), 'EX1_302': ('minion', [('damage_draw_if_dead', 1)]), 'DAL_071': ('friendly_minion', [('historical_copy_evolve_target', 1)]), 'ULD_178': ('none', [('choose_unique_keyword',), ('choose_unique_keyword',)]), 'YOD_025': ('none', [('generate_discover', PoolRequest(era='', rune='', card_type='', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='WARLOCK', attack_minimum=None, attack_maximum=None), 'hand', ()), ('generate_discover', PoolRequest(era='', rune='', card_type='', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='WARLOCK', attack_minimum=None, attack_maximum=None), 'hand', ())])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'DRG_204': ('none', [('historical_utility_dark_skies',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'DAL_602': ('none', [('historical_utility_plot_twist',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'DAL_432': ('character', [('heal', 4), ('historical_utility_repeat_brew',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'DAL_009': ('none', [('held_scheme_area',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'ULD_140': ('none', [('quest_start', 'ULD_140')]), 'ULD_140p': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'ULD_291': ('none', [('quest_start', 'ULD_291')]), 'ULD_291p': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'CS2_041': ('minion', [('heal_full',), ('keyword', 'TAUNT')]), 'GIL_600': ('minion', [('damage', 2)]), 'OG_206': ('minion', [('damage', 4)]), 'SCH_427': ('none', [('refresh_mana', 2)]), 'ULD_181': ('none', [('area_damage', 'all_minions', 5), ('area_damage', 'all_minions', 2)]), 'LOOT_504': ('friendly_minion', [('historical_copy_evolve_target', 1)]), 'YOD_020': ('minion', [('historical_copy_evolve_target', 3)]), 'DRG_215': ('none', [('board_buff', 1, 1)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'BT_100': ('character', [('damage', 3), ('generate_random', PoolRequest(era='', rune='', card_type='MINION', tribe='', school='', minimum=3, maximum=3, rarity='', mechanic='', excluded_mechanic='COLOSSAL', family='', minimum_tribes=0, classes='any', attack_minimum=None, attack_maximum=None), 1, 'board', ())]), 'VAC_329': ('none', [('generate_random', PoolRequest(era='', rune='', card_type='MINION', tribe='NAGA', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='any', attack_minimum=None, attack_maximum=None), 1, 'hand', (('cost_delta', -2),)), ('generate_random', PoolRequest(era='', rune='', card_type='SPELL', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='any', attack_minimum=None, attack_maximum=None), 1, 'hand', (('cost_delta', -2),))]), 'ULD_171': ('none', [('tribe_board_buff', 'TOTEM', 2, 0)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'GVG_038': ('character', [('historical_utility_crackle',)]), 'EX1_251': ('none', [('historical_batch_sample_damage', 'enemy', 2, 2)]), 'OG_023': ('minion', [('historical_utility_primal_fusion',)]), 'GIL_586': ('minion', [('buff', 2, 2), ('historical_utility_earthen_might',)]), 'SCH_352': ('none', [('historical_utility_potion_illusion',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'OG_027': ('none', [('historical_utility_transform_board', 'own', 1)]), 'CFM_696': ('none', [('historical_utility_transform_board', 'enemy', -1)]), 'BOT_245': ('none', [('historical_utility_transform_board', 'legendary', 0)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'AT_048': ('character', [('historical_utility_healing_wave',)]), 'WON_320': ('character', [('historical_utility_healing_wave',)]), 'FP1_025': ('minion', [('historical_utility_reincarnate',)]), 'WON_335': ('minion', [('historical_utility_reincarnate',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'CFM_707': ('character', [('damage', 3), ('historical_ritual_jade', False, False)]), 'WON_082': ('character', [('damage', 3), ('historical_ritual_jade', False, False)]), 'BT_110': ('minion', [('damage', 8)]), 'YOP_023': ('none', [('historical_utility_landslide',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'AT_051': ('none', [('historical_utility_elemental_destruction',)]), 'DRG_219': ('minion', [('historical_utility_lightning_breath',)]), 'CS2_045': ('friendly_character', [('historical_utility_rockbiter',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'GDB_479': ('none', [('generate_discover', PoolRequest(era='', rune='', card_type='MINION', tribe='', school='', minimum=8, maximum=8, rarity='', mechanic='', excluded_mechanic='COLOSSAL', family='', minimum_tribes=0, classes='own_or_neutral', attack_minimum=None, attack_maximum=None), 'board', (('keywords', ('TAUNT', 'ELUSIVE')),)), ('generate_discover', PoolRequest(era='', rune='', card_type='MINION', tribe='', school='', minimum=8, maximum=8, rarity='', mechanic='', excluded_mechanic='COLOSSAL', family='', minimum_tribes=0, classes='own_or_neutral', attack_minimum=None, attack_maximum=None), 'board', (('keywords', ('TAUNT', 'ELUSIVE')),))]), 'GDB_445': ('none', [('area_damage', 'all_minions', 5), ('insert_fixed', 'GDB_430', 5, 'shuffle')])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'BT_101': ('none', [('historical_utility_vivid_spores',)]), 'SCH_235': ('none', [('historical_utility_devolving_missiles',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'BOT_093': ('none', [('historical_utility_elementary_reaction',)]), 'DMF_701': ('character', [('damage', 4)]), 'DMF_701t': ('character', [('damage', 4), ('area_damage', 'enemy_minions', 2)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'SCH_612': ('none', []), 'SCH_612a': ('none', [('historical_utility_runic', False)]), 'SCH_612b': ('none', [('historical_utility_runic', True)]), 'SCH_612t': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'SCH_270': ('none', [('generate_discover', PoolRequest(era='', rune='', card_type='MINION', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='SPELLPOWER', excluded_mechanic='', family='', minimum_tribes=0, classes='own_or_neutral', attack_minimum=None, attack_maximum=None), 'hand', ()), ('next_discount', 'SPELLPOWER', 1, 'persistent')])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'SW_035': ('none', [('historical_utility_charged_call',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'LOOT_064': ('friendly_minion', [('historical_utility_sapphire_copy', 1)]), 'LOOT_064t1': ('friendly_minion', [('historical_utility_sapphire_copy', 2)]), 'LOOT_064t2': ('friendly_minion', [('historical_utility_sapphire_copy', 3)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'TOY_700t': ('none', [('historical_utility_moment_discovery',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'TOY_700t13': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'UNG_942': ('none', [('quest_start', 'UNG_942')])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES.update({'SW_031': ('none', [('quest_start', 'SW_031')]), 'SW_031t': ('none', [('quest_start', 'SW_031t')]), 'SW_031t2': ('none', [('quest_start', 'SW_031t2')]), 'SW_031t7': ('none', [('historical_utility_brukan',)]), 'SW_031t8': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

TOKEN_RULES.update({'TOY_700t14': ('none', [('historical_utility_quest_accepted',), ('filtered_draw', (('tribe', 'eq', 'MURLOC'),), 1), ('filtered_draw', (('mechanic', 'eq', 'OVERLOAD'),), 1)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'CFM_313': ('none', [('generate_discover', PoolRequest(era='', rune='', card_type='', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='OVERLOAD', excluded_mechanic='', family='', minimum_tribes=0, classes='own_or_neutral', attack_minimum=None, attack_maximum=None), 'hand', ())]), 'BAR_041': ('none', [('board_buff', 1, 1), ('tribe_board_buff', 'MURLOC', 1, 1)]), 'EX1_164': ('none', []), 'WON_014': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'CS2_013': ('none', [('historical_utility_ramp_excess', 1)]), 'BT_130': ('none', [('historical_utility_ramp_excess', 2)]), 'CS2_013t': ('none', [('draw', 1)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original printings required by sourced Zayle recipe candidates.
TOKEN_RULES.update({'SW_114': ('character', [('historical_utility_overdraft',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original experimental recipe printings; printed Lifesteal uses native weapon combat.
TOKEN_RULES.update({'EX1_193': ('none', [('copy_enemy_deck',)]), 'KAR_069': ('none', [('generate_random', PoolRequest(era='', rune='', card_type='', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='', excluded_mechanic='', family='', minimum_tribes=0, classes='other', attack_minimum=None, attack_maximum=None), 1, 'hand', ())]), 'YOP_001': ('none', [('generate_discover', PoolRequest(era='', rune='', card_type='', tribe='', school='', minimum=0, maximum=None, rarity='', mechanic='OUTCAST', excluded_mechanic='', family='', minimum_tribes=0, classes='any', attack_minimum=None, attack_maximum=None), 'hand', ()), ('next_discount', 'OUTCAST', 1, 'permanent')]), 'BT_416': ('none', [('next_discount', 'DEMON', 2, 'persistent')]), 'BT_921': ('none', []), 'LOOT_088': ('minion', [('keyword', 'DIVINE_SHIELD'), ('draw', 1)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original experimental recipe printings; printed Lifesteal uses native weapon combat.
TOKEN_RULES.update({'CS2_234': ('small_attack_minion', [('destroy',)]), 'EX1_622': ('historical_attack_at_least_five', [('destroy',)]), 'SW_040': ('none', [('damage_lowest_health_enemy', 2), ('damage_lowest_health_enemy', 2)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original experimental recipe printings; printed Lifesteal uses native weapon combat.
TOKEN_RULES.update({'AV_342': ('none', [('historical_utility_protect_innocent',)]), 'AV_342t': ('none', []), 'BRM_001': ('none', [('draw', 2)]), 'DAL_010': ('minion', [('historical_utility_togwaggle_scheme',)]), 'GVG_008': ('none', [('historical_utility_lightbomb',)]), 'GVG_015': ('character', [('historical_utility_darkbomb',)]), 'ULD_160': ('none', [('historical_utility_lackey_discover',)]), 'VAC_700': ('none', [('destroy_random_enemy',), ('destroy_random_enemy',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original experimental recipe printings; printed Lifesteal uses native weapon combat.
TOKEN_RULES.update({'TTN_903': ('none', []), 'TTN_903t': ('none', [('historical_utility_eonar_draw',)]), 'TTN_903t2': ('none', [('historical_utility_eonar_heal',)]), 'TTN_903t3': ('none', [('refresh_mana', 100)]), 'TTN_903t4': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Original experimental recipe printings; printed Lifesteal uses native weapon combat.
TOKEN_RULES.update({'CS2_004': ('minion', [('buff', 0, 2), ('draw', 1)]), 'DS1_184': ('none', [('discover_deck',)]), 'EX1_154': ('none', []), 'EX1_160': ('none', []), 'EX1_278': ('character', [('damage', 1), ('draw', 1)]), 'EX1_391': ('minion', [('damage_draw_if_alive', 2)]), 'NEW1_031': ('none', [('companions_random',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Complete historical Zephrys candidate-list dependencies; native keywords and weapon hooks below.
TOKEN_RULES.update({'EX1_059': ('minion', [('swap_stats',)]), 'EX1_014': ('none', [('add_opponent', 'EX1_014t', 2)]), 'EX1_103': ('none', [('other_murloc_health', 2)]), 'EX1_043': ('none', [('self_hand_health',)]), 'EX1_005': ('large_minion', [('destroy',)]), 'EX1_002': ('enemy_taunt', [('destroy',)]), 'EX1_198': ('minion', [('destroy_gain_health',)]), 'NEW1_003': ('historical_friendly_demon', [('destroy',), ('heal_own_hero', 5)]), 'CS2_037': ('enemy_character', [('damage', 1), ('freeze',)]), 'EX1_360': ('minion', [('historical_utility_wish_attack', 'one')]), 'EX1_578': ('minion', [('historical_utility_wish_savagery',)]), 'CS1_129': ('minion', [('historical_utility_wish_attack', 'health')]), 'EX1_126': ('enemy_minion', [('historical_utility_wish_betrayal',)]), 'CS2_114': ('none', [('historical_batch_sample_damage', 'enemy', 2, 2)]), 'CS2_073': ('minion', [('historical_utility_wish_coldblood',)]), 'EX1_544': ('none', [('historical_utility_wish_flare',), ('draw', 1)]), 'EX1_339': ('none', [('historical_copy_enemy_random_two',)]), 'EX1_392': ('none', [('historical_utility_wish_battlerage',)]), 'EX1_617': ('none', [('destroy_random_enemy',)]), 'BT_740': ('none', [('historical_batch_sample_damage', 'enemy', 2, 2)]), 'EX1_536': ('none', []), 'EX1_189': ('none', [('generate_random', PoolRequest(era='', rune='', card_type='MINION', tribe='', school='', minimum=0, maximum=None, rarity='LEGENDARY', mechanic='', excluded_mechanic='COLOSSAL', family='', minimum_tribes=0, classes='any', attack_minimum=None, attack_maximum=None), 1, 'hand', ())]), 'DS1_183': ('none', [('historical_batch_sample_damage', 'enemy', 2, 3)]), 'EX1_158': ('none', [('historical_utility_wish_soulforest',)]), 'EX1_158t': ('none', []), 'CS2_092': ('minion', [('buff', 4, 4)]), 'EX1_537': ('minion', [('historical_utility_wish_explosive',)]), 'CS2_046': ('none', [('historical_utility_wish_bloodlust',)]), 'EX1_567': ('none', []), 'EX1_355': ('minion', [('historical_utility_wish_attack', 'double')]), 'EX1_250': ('none', []), 'EX1_411': ('none', []), 'DS1_188': ('none', [])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Owner-authorized approximate Zephrys and Wish; executable shared choice pipeline.
TOKEN_RULES.update({'ULD_003':('none',[('historical_zephrys_begin',)]),'TOY_700t9t2':('none',[('historical_zephrys_wish',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Thrive in the Shadows: native physical spell-deck Discover and draw.
from .historical_play_batches import zone_offer as _special_zone_offer
TOKEN_RULES.update({cid:('none',[_special_zone_offer('own','deck',(('type','eq','SPELL'),),'draw')]) for cid in ('CS3_028','LEG_CS3_028')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

# Complete literal outcomes used by historical pool consumers.
from .historical_pool_closure import TOKEN_RULES as POOL_CLOSURE_RULES
TOKEN_RULES.update(POOL_CLOSURE_RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

from .historical_summon_faction_finish import LOCATION_EFFECTS as SUMMON_FACTION_LOCATION_EFFECTS
LOCATION_EFFECTS.update(SUMMON_FACTION_LOCATION_EFFECTS)
