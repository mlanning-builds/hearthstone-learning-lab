"""Explicit physical hand/deck, copy and resource operations; unvalidated."""
from .historical_saidan import add as _saidan_add
from engine.game import Card
from .selectors import has_tribe

RULES={
 'MAW_000':('historical_friendly_imp',[('historical_mutation_imp_oster',)]),
 'DRG_309':('none',[('historical_mutation_crystals',10)]),
 'TRL_564':('none',[('historical_mutation_crystals',5)]),
 'BT_249':('none',[]),
 'WON_330':('none',[('historical_mutation_enemy_count_heal',2)]),
 'VAC_423':('none',[('historical_mutation_top_cost',0)]),
 'VAC_701':('none',[('historical_mutation_weapon_set',3)]),
 'WON_140':('none',[('historical_mutation_dragons_hand',1,1,1)]),
 'WW_367':('none',[]),
 'ULD_288':('none',[('historical_mutation_deathrattle_hand',1,1,1)]),
 'ULD_435':('none',[('historical_mutation_spell_cost',5)]),
 'TTN_723':('none',[('filtered_draw',(('type','eq','MINION'),('tribe','eq','MECHANICAL')),1),('next_discount','MECHANICAL',2,'persistent')]),
 'TTN_835':('none',[('historical_mutation_unlock_draw',)]),
 'TRL_059':('friendly_minion',[('historical_mutation_bounce',2,2,None)]),
 'WW_423':('friendly_minion',[('historical_mutation_bounce',2,2,None)]),
 'DMF_071':('friendly_minion',[('historical_mutation_bounce',0,0,1)]),
 'WON_305':('friendly_beast',[('historical_mutation_copy_board',None,None,())]),
 'KAR_065':('friendly_beast',[('historical_mutation_copy_board',None,None,())]),
 'ULD_720':('historical_mutation_damaged_friendly',[('historical_mutation_copy_board',None,None,())]),
 'TSC_649':('historical_friendly_mech',[('historical_mutation_copy_board',None,None,('RUSH','WINDFURY','DIVINE_SHIELD'))]),
 'UNG_022':('minion',[('historical_mutation_copy_board',1,1,())]),
 'DRG_076':('friendly_minion',[('historical_mutation_transform_copy_source',)]),
 'DAL_744':('friendly_minion',[('historical_mutation_copy_health',)]),
 'ETC_420':('friendly_minion',[('historical_mutation_buff_source_stats',)]),
 'UNG_015':('none',[('set_others_attack',3),('set_others_health',3)]),
}
DEATH_EFFECTS={'BT_249':[('historical_mutation_armor_source_attack',)],'WW_367':[('historical_mutation_taunt_zones',1,1)]}
RULES.update({
 'BOT_907':('none',[('historical_mutation_discount_zones',('hand',),(('tribe','MECHANICAL'),),1)]),
 'DRG_257':('none',[('historical_mutation_discount_zones',('deck',),(('tribe','DRAGON'),),2)]),
 'RLK_216':('none',[('historical_mutation_discount_zones',('deck',),(('mechanic','DEATHRATTLE'),),1)]),
 'SW_032':('none',[('historical_mutation_discount_zones',('hand','deck'),(('tribe','ELEMENTAL'),),1)]),
 'UNG_202':('none',[('historical_mutation_discount_zones',('hand',),(('tribe','ELEMENTAL'),),1)]),
 'AV_114':('none',[('historical_mutation_discount_extreme',(('type','SPELL'),),1)]),
 'LOOT_118':('none',[('discount_random_hand','friendly',(('type','eq','WEAPON'),),2)]),
 'ULD_410':('none',[('discount_random_hand','friendly',(('type','eq','MINION'),('tribe','eq','BEAST')),5)]),
 'BAR_854':('none',[('next_discount','ELEMENTAL',1,'persistent')]),
 'BRM_018':('none',[('next_discount','DRAGON',2,'persistent')]),
 'AV_334':('none',[]), 'WC_004':('none',[]), 'TRL_505':('none',[]),
 'REV_374':('none',[]), 'WORK_015':('none',[]),
 'AV_256':('none',[('historical_mutation_swap_hands',)]),
 'WORK_031':('none',[('historical_mutation_hand_top',)]),
 'WORK_063':('none',[('historical_mutation_swap_spell_costs',)]),
 'WW_394':('none',[('historical_mutation_copy_cost_hand',1)]),
 'RLK_711':('none',[('historical_mutation_hand_source_attack',)]),
})
DEATH_EFFECTS.update({
 'AV_334':[('next_discount','BEAST',2,'persistent')],
 'WC_004':[('discount_random_hand','friendly',(('type','eq','MINION'),('tribe','eq','BEAST')),2)],
 'TRL_505':[('discount_random_hand','friendly',(('type','eq','MINION'),('tribe','eq','BEAST')),1)],
 'REV_374':[('historical_mutation_discount_extreme',(('type','SPELL'),('school','SHADOW')),3)],
 'WORK_015':[('discount_random_hand','friendly',(('type','eq','MINION'),),6)],
})


def card_matches(game,card,filters):
 from .selectors import has_school
 data=game._card_data(card)
 for key,value in filters:
  if key=='tribe' and not has_tribe(data,value):return False
  if key=='school' and not has_school(data,value):return False
  if key=='type' and data['type']!=value:return False
  if key=='mechanic' and value not in game._card_mechanics(card):return False
 return True

RULES.update({
 'ETC_106':('none',[('next_discount','MECHANICAL',1,'persistent')]),
 'GDB_875':('none',[('next_discount','COMBO',1,'persistent')]),
 'GDB_333':('none',[]), 'WORK_041':('none',[]),
 'EX1_612':('none',[('next_cost_set','SECRET',0,'turn')]),
 'CFM_066':('none',[('next_cost_set','SECRET',1,'turn')]),
 'REV_841':('none',[('next_cost_set','SECRET',0,'persistent')]),
 'TSC_823':('none',[('next_discount','SPELL',1,'persistent')]),
 'TSC_936':('none',[('next_cost_set','SPELL',0,'turn')]),
 'WW_335':('none',[('next_discount','HOLY',2,'persistent')]),
})
DEATH_EFFECTS.update({'GDB_333':[('next_discount','WEAPON',1,'persistent')],
 'WORK_041':[('next_discount','LOCATION',2,'persistent')]})
RULES.update({
 'TTN_095':('none',[('next_discount','ELEMENTAL',2,'persistent')]),
 'CS3_008':('none',[('next_discount','WEAPON',1,'persistent')]),
 'CS3_012':('none',[('next_discount','SPELL',3,'turn')]),
 'AV_296':('none',[('next_discount','CHOOSE_ONE',2,'persistent')]),
 'BT_131':('none',[('historical_mutation_turn_spell_cost',1)]),
})
RULES.update({'BAR_316':('character',[('historical_mutation_hand_entry_damage',2,4)]),'GDB_440':('none',[('historical_mutation_health_42',)])})
GENERATED_IDS=frozenset(RULES)


def targets(game,cid,owner,mode):
 if mode=='historical_friendly_imp':
  from .historical_imps import is_imp
  return [uid for uid in game._targets_for(cid,owner,'friendly_minion') if uid>0 and is_imp(game,game._find(uid))] or [0]
 if mode!='historical_mutation_damaged_friendly':return None
 return [uid for uid in game._targets_for(cid,owner,'friendly_minion') if uid>0 and game._find(uid).health<game._find(uid).max_health] or [0]


def split(game,op,ctx):
 if op[0]=='historical_mutation_recruit_demons':
  count=sum(game._card_data(c)['type']=='MINION' and has_tribe(game._card_data(c),'DEMON') for c in game.players[ctx['owner']].hand)
  operation=('summon_from_zone','hand',(('type','eq','MINION'),('tribe','eq','DEMON')))
  return (operation,(operation,)*(count-1)) if count else (('batch30_noop',),())
 if op[0]!='historical_mutation_unlock_draw':return None
 p=game.players[ctx['owner']];count=p.locked_mana+p.overload_next
 p.mana=min(p.max_mana,p.mana+p.locked_mana);p.locked_mana=0;p.overload_next=0
 return game._split_fixed_summon(('draw',count),ctx)


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_mutation_'):return False
 owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner];source=ctx.get('source');uid=ctx.get('target',0)
 target=next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)
 if name=='historical_mutation_hand_entry_damage':
  card=ctx.get('physical_card');amount=op[2] if getattr(card,'_hand_entry_turn',None)==game.turn else op[1]
  game._deal_effect(ctx.get('target',0),amount,ctx)
 elif name=='historical_mutation_health_42':
  if p.health+q.health==42:p.max_health=max(p.max_health,42);p.health=42
 elif name=='historical_mutation_copy_whole_hand':
  for card in tuple(p.hand):game._clone_hand_card(owner,card,source_owner=owner)
 elif name=='historical_mutation_bounce_delta':
  if target is not None:game._bounce(target,op[1])
 elif name=='historical_mutation_full_hero_heal':game._heal(game.hero_id(owner),max(0,p.max_health-p.health),healer=owner)
 elif name=='historical_mutation_turn_spell_cost':p.cost_effects.append(dict(selector='SPELL',set_cost=op[1],consume_on_play=False,expires=game.turn))
 elif name=='historical_mutation_discount_zones':
  for zone in op[1]:
   cards=getattr(p,zone)
   for index,value in enumerate(cards):
    if card_matches(game,value,op[2]):
     card=value if isinstance(value,Card) else Card(game._new_id(),value)
     card.cost_delta=getattr(card,'cost_delta',0)-op[3];cards[index]=card
 elif name=='historical_mutation_discount_extreme':
  cards=[c for c in p.hand if card_matches(game,c,op[1])]
  if cards:
   highest=max(game._cost(c,owner) for c in cards)
   card=game.rng.choice([c for c in cards if game._cost(c,owner)==highest])
   card.cost_delta=getattr(card,'cost_delta',0)-op[2]
 elif name=='historical_mutation_swap_hands':
  for player in game.players:
   for card in player.hand:
    if game._card_data(card)['type']=='MINION':
     attack=game._card_stat(card,'attack',game.players.index(player))
     health=game._card_stat(card,'health',game.players.index(player))
     game._mutation_set_stats(card,game.players.index(player),health,attack)
 elif name=='historical_mutation_hand_top':
  if p.hand:
   cost=max(game._cost(c,owner) for c in p.hand)
   card=game.rng.choice([c for c in p.hand if game._cost(c,owner)==cost]);p.hand.remove(card);p.deck.append(card)
 elif name=='historical_mutation_swap_spell_costs':
  cards=[c for c in p.hand if game._card_data(c)['type']=='SPELL']
  if len(cards)>1:
   low=min(game._cost(c,owner) for c in cards);high=max(game._cost(c,owner) for c in cards)
   first=game.rng.choice([c for c in cards if game._cost(c,owner)==low])
   others=[c for c in cards if c is not first and game._cost(c,owner)==high]
   if others:
    second=game.rng.choice(others);game._set_card_cost(first,high);game._set_card_cost(second,low)
 elif name=='historical_mutation_copy_cost_hand':
  for card in tuple(p.hand):
   if game._cost(card,owner)==op[1]:game._clone_hand_card(owner,card,source_owner=owner)
 elif name=='historical_mutation_hand_source_attack':
  cards=[c for c in p.hand if game._card_data(c)['type']=='MINION']
  if cards and source is not None:_saidan_add(game.rng.choice(cards),'attack_bonus',max(0,source.attack))
 elif name=='historical_mutation_crystals':
  for player in game.players:
   before=player.max_mana;player.max_mana=min(op[1],player.mana_capacity);player.locked_mana=min(player.locked_mana,player.max_mana)
   player.mana=max(0,min(player.max_mana-player.locked_mana,player.mana+player.max_mana-before))
 elif name=='historical_mutation_enemy_count_heal':game._heal(game.hero_id(owner),len(q.minions)*op[1],healer=owner,spell=ctx.get('spell',False))
 elif name=='historical_mutation_top_cost':
  if p.deck:
   value=p.deck[-1];card=value if isinstance(value,Card) else Card(game._new_id(),value);p.deck[-1]=card;game._set_card_cost(card,op[1])
 elif name=='historical_mutation_weapon_set':
  if p.weapon:
   game._buff_weapon(owner,attack=op[1]-p.weapon['attack'],durability=op[1]-p.weapon['durability'])
 elif name=='historical_mutation_dragons_hand':
  for card in p.hand:
   if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'DRAGON'):card.cost_delta=getattr(card,'cost_delta',0)-op[1];_saidan_add(card,'attack_bonus',op[2]);_saidan_add(card,'health_bonus',op[3])
 elif name=='historical_mutation_deathrattle_hand':
  for card in p.hand:
   if game._card_data(card)['type']=='MINION' and 'DEATHRATTLE' in game._card_mechanics(card):game._mutation_set_stats(card,owner,op[1],op[2]);game._set_card_cost(card,op[3])
 elif name=='historical_mutation_spell_cost':
  for card in p.hand:
   if game._card_data(card)['type']=='SPELL':game._set_card_cost(card,op[1])
 elif name=='historical_mutation_taunt_zones':
  for zone in ('hand','deck'):
   values=getattr(p,zone)
   for i,value in enumerate(values):
    if game._card_data(value)['type']=='MINION' and 'TAUNT' in game._card_mechanics(value):
     card=value if isinstance(value,Card) else Card(game._new_id(),value);_saidan_add(card,'attack_bonus',op[1]);_saidan_add(card,'health_bonus',op[2]);values[i]=card
 elif name=='historical_mutation_bounce':
  if target is not None:
   recipient=target.owner;before={c.uid for c in game.players[recipient].hand};game._bounce(target)
   card=next((c for c in game.players[recipient].hand if c.uid not in before),None)
   if card is not None:
    _saidan_add(card,'attack_bonus',op[1]);_saidan_add(card,'health_bonus',op[2])
    if op[3] is not None:game._b60_state(card)['historical_turn_cost']={'turn':game.turn,'cost':op[3]}
 elif name=='historical_mutation_copy_board':
  if target is not None:
   stats=None if op[1] is None else (op[1],op[2])
   game._summon(owner,target.card_id,copy_from=target,entry_stats=stats,entry_keywords=op[3],entry_origin='copy',entry_site='historical_copy_target',entry_source=target)
 elif name=='historical_mutation_transform_copy_source':
  if source is not None and target is not None:
   from .historical_copy_batches import replace
   replace(game,target,source)
 elif name=='historical_mutation_imp_oster':
  from .historical_imps import is_imp
  if target is not None and target.owner==owner and is_imp(game,target):
   from .historical_copy_batches import replace
   replace(game,source,target)
 elif name=='historical_mutation_copy_health':
  if source is not None and target is not None:game._set_entity_stats(source,source.attack-source.aura_attack,target.health)
 elif name=='historical_mutation_buff_source_stats':
  if source is not None and target is not None:game._buff(target,source.attack,max(0,source.health))
 elif name=='historical_mutation_armor_source_attack':
  if source is not None:game._gain_armor(owner,max(0,source.attack))
 else:return False
 return True
