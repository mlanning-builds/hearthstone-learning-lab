"""Explicit historical draws and resumable post-draw effects; unvalidated."""
from .historical_saidan import add as _saidan_add
from .selectors import has_school,has_tribe

SI7_IDS=frozenset(('CAP_000', 'CAP_003', 'CORE_EX1_134', 'CORE_EX1_186', 'EX1_134', 'EX1_186', 'HERO_09e', 'LETLT_129_01', 'LETLT_130_01', 'LETLT_131_01', 'LETLT_138_01', 'LETL_482_01', 'LETL_482_02', 'LETL_482_03', 'LETL_482_04', 'LETL_863H', 'ONY_030', 'PVPDR_AV_Neutralp2m1', 'PVPDR_Duels_Buckets_RSI7', 'SW_411', 'SW_412', 'SW_413', 'SW_417', 'SW_418', 'TB_BaconShop_HERO_01_Buddy', 'TB_BaconShop_HERO_01_Buddy_G', 'VAN_EX1_134'))

MINION=(('type','eq','MINION'),)
SPELL=(('type','eq','SPELL'),)

def draw(filters=None,mode='none',args=(),priority='random'):
 return ('historical_draw_batch',filters,mode,tuple(args),priority)

RULES={
 'GIL_584':('none',[draw(MINION,priority='lowest')]),
 'VAC_917':('none',[draw(priority='lowest')]),
 'LEG_CS3_034':('none',[('historical_draw_fill',SPELL)]),
 'TRL_260':('none',[('historical_draw_fill',MINION+(('cost','eq',1),))]),
 'UNG_113':('none',[draw(mode='set_cost',args=(5,))]),
 'DED_516':('none',[draw(SPELL,'armor_cost')]),
 'DED_505':('none',[draw(SPELL,'damage_hero_cost')]),
 'WC_005':('none',[draw(SPELL,'nature_elemental')]),
 'WC_013':('none',[draw(SPELL,'school_discount',('HOLY',2))]),
 'SW_081':('none',[draw(MINION+(('mechanic','eq',keyword),),'source_keyword',(keyword,)) for keyword in ('RUSH','TAUNT','DIVINE_SHIELD')]),
 'BAR_328':('none',[('historical_outcast_draw_batch',MINION+(('mechanic','eq','DEATHRATTLE'),),2)]),
 'TTN_468':('none',[draw(SPELL),('historical_draw_discount_fire_hand',1)]),
 'AV_343':('none',[draw(SPELL+(('cost','le',3),),'turn_zero')]),
 'DMF_056':('none',[draw(mode='health_payment')]*2),
 'DAL_752':('none',[draw(MINION,'one_stats_cost')]*2),
 'LEG_RLK_224':('none',[('historical_draw_frost_pair',)]),
 'DMF_125':('none',[('historical_draw_shuffle_cheapest_hand',),('draw',1)]),
 'BOT_573':('none',[('historical_draw_distinct_secrets',5)]),
 'SW_411':('none',[('historical_draw_history_buff','SI7',1,1)]),
 'ETC_336':('none',[('historical_draw_history_buff','ETC_336',1,1)]),
 'BOT_283':('none',[('historical_draw_history_buff','BOT_283',2,2)]),
}
DEATH_EFFECTS={
 'VAC_917':[draw(priority='highest')],
 'DMF_069':[draw(MINION,'buff',(3,3))],
 'VAC_518':[draw(MINION+(('mechanic','eq','TAUNT'),),'discount',(2,))],
 'DED_505':RULES['DED_505'][1],
}
TRIGGERS={
 'AV_321':(('minion_mechanic_played','TAUNT'),[('draw',1)]),
 'CFM_851':('enemy_card_drawn',[('buff_self',1,1)]),
 'DAL_372':(('minion_cost_played',1),[('filtered_draw',SPELL,1)]),
 'TSC_085':('hero_attack',[('filtered_draw',MINION+(('tribe','eq','PIRATE'),),1)]),
 'TTN_711':('defended_self',[('draw',1)]),
}
RULES.update({
 'AT_072':('none',[draw(mode='recruit_drawn')]*3),
 'REV_318':('none',[draw(SPELL+(('school','eq','NATURE'),)),('empty_crystals','friendly',1)]),
 'WC_805':('none',[draw(SPELL,'frost_elementals')]),
 'WW_408':('none',[draw((('mechanic','eq','OUTCAST'),),'left_hand')]),
 'CFM_806':('none',[('historical_draw_dragon_chain',)]),
})
DEATH_EFFECTS.update({
 'REV_319':[draw(MINION,'discount',(8,))],
 'RLK_830':[draw(MINION+(('tribe','eq','UNDEAD'),),'copy_drawn_minion')],
})
RULES.update({
 'VAC_437':('none',[draw(SPELL+(('school','eq',school),)) for school in ('ARCANE','FEL','FIRE','FROST','HOLY','NATURE','SHADOW')]),
 'DED_524':('none',[('historical_draw_school_count',)]),
 'TTN_478':('none',[('historical_draw_school_damage',)]),
 'TOY_391':('none',[draw(MINION+(('cost','ge',5),))]),
 'TTN_712':('none',[('historical_draw_nonstarting',1)]),
 'DRG_034':('none',[('historical_draw_nonstarting',2)]),
 'TOY_916':('none',[draw(SPELL+(('school','eq','SHADOW'),),'copy_temporary')]),
 'BAR_042':('none',[draw(SPELL,'random_cost_summon',priority='highest')]),
 'GVG_092':('none',[draw(mode='chicken')]),
})
FIXED_TOKEN_IDS=frozenset(('GVG_092t',))
TOKEN_RULES={'GVG_092t':('none',[])}
for cid in DEATH_EFFECTS.keys()|TRIGGERS.keys():RULES.setdefault(cid,('none',[]))
RULES.update({
 'AV_284':('none',[('historical_draw_balinda',)]),
 'DRG_084':('none',[('historical_draw_menace',)]),
 'DRG_077':('none',[('historical_draw_grapplesniper',)]),
 'TOY_388':('none',[draw(MINION,'chalk')]),
 'TOY_703':('none',[draw(MINION,'colifero')]),
 'ETC_840':('none',[]),
})
TRIGGERS['ETC_840']=('attacking_self',[draw(MINION+(('tribe','eq','BEAST'),),'source_stats')])
RULES.update({'DED_510':('none',[draw(mode='same_turn_follow',args=('edwin',))]),'DMF_229':('none',[draw(mode='same_turn_follow',args=('stiltstepper',))]),'WW_327':('none',[draw(SPELL,'same_turn_follow',('cactus',))])})
RULES['TOY_376']=('none',[draw(SPELL+(('school','eq','FROST'),),'watercolor')])
RULES.update({'WW_429':('none',[('historical_draw_mesadune',)]),'GDB_129':('none',[('historical_draw_doommaiden',)])})
GENERATED_IDS=frozenset(RULES)


def split(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_draw_mesadune':
  state={}
  return ('historical_draw_capture',MINION+(('tribe','eq','ELEMENTAL'),),'random',state),(('historical_draw_mesadune_finish',state),)
 if name=='historical_draw_hagatha':
  a={};b={};filters=SPELL+(('cost','ge',5),)
  return ('historical_draw_capture',filters,'random',a),(('historical_draw_capture',filters,'random',b),('historical_draw_hagatha_slime',a),('historical_draw_hagatha_slime',b))
 if name=='historical_draw_balinda':
  a={};b={}
  return ('historical_draw_capture',SPELL,'random',a),(('historical_draw_capture',SPELL,'random',b),('historical_draw_balinda_finish',a,b))
 if name in ('historical_draw_menace','historical_draw_grapplesniper'):
  a={};b={};other=dict(ctx,owner=1-owner)
  return ('historical_draw_capture',None,'random',a),(('replay_context',(('historical_draw_capture',None,'random',b),),other),('historical_draw_both_finish',name,a,b))
 if name=='historical_draw_nonstarting':
  count=op[1]
  if count<=0:return ('batch30_noop',),()
  return ('historical_draw_nonstarting_one',),((('historical_draw_nonstarting',count-1),) if count>1 else ())
 if name=='historical_draw_school_count':
  count=len(getattr(p,'historical_spell_schools',()))
  return game._split_fixed_summon(('draw',count),ctx)
 if name=='historical_draw_dragon_chain':
  state={}
  return ('historical_draw_capture',None,'random',state),(('historical_draw_dragon_continue',state),)
 if name=='historical_draw_dragon_continue':
  card=op[1].get('card')
  if card is not None and has_tribe(game._card_data(card),'DRAGON'):return split(game,('historical_draw_dragon_chain',),ctx)
  return ('batch30_noop',),()
 if name=='historical_draw_batch':
  state={}
  return ('historical_draw_capture',op[1],op[4],state),(('historical_draw_finish',op[2],op[3],state),)
 if name=='historical_draw_fill':
  if len(p.hand)>=getattr(p,'hand_capacity',10) or not any(game._matches_filter(c,op[1],zone_owner=owner) for c in p.deck):return ('batch30_noop',),()
  first,tail=split(game,draw(op[1]),ctx)
  return first,tuple(tail)+(op,)
 if name=='historical_outcast_draw_batch':
  return game._split_fixed_summon(('filtered_draw',op[1],op[2]),ctx) if ctx.get('outcast') else (('batch30_noop',),())
 if name=='historical_draw_frost_pair':
  a={};b={}
  return ('historical_draw_capture',SPELL,'random',a),(('historical_draw_capture',SPELL,'random',b),('historical_draw_pair_finish',a,b))
 if name=='historical_draw_distinct_secrets':
  state={'used':set(),'remaining':op[1]}
  return ('historical_draw_secret_step',state),(('historical_draw_secret_continue',state),)
 if name=='historical_draw_secret_continue':
  if op[1]['remaining']<=0:return ('batch30_noop',),()
  return ('historical_draw_secret_step',op[1]),(op,)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_draw_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_draw_mesadune_finish':
  card=op[1].get('card')
  if card is not None and card in p.hand:game._mutation_split_card(card,owner)
 elif name=='historical_draw_doommaiden':
  other=game.players[1-owner]
  if other.deck:
   card=game._take_deck_draw(1-owner,len(other.deck)-1,recipient=owner,include_burned=True)
   if card is not None and card in p.hand:
    game._schedule_turn_effect(game.current,'end',0,1,(('historical_draw_doommaiden_return',owner,1-owner,card.uid),),source_card_id='GDB_129')
 elif name=='historical_draw_doommaiden_return':
  holder,destination,uid=op[1:];hand=game.players[holder].hand
  card=next((card for card in hand if card.uid==uid),None)
  if card is not None:
   hand.remove(card);game.players[destination].deck.append(card)
   game._refresh_auras();game._log('doommaiden_return',player=holder,destination=destination,entity=uid)
 elif name=='historical_draw_hagatha_slime':
  from engine.game import Card
  from copy import deepcopy
  state=op[1];card=state.get('card')
  if card is not None and card in p.hand:
   cost=max(0,state['cost']);slime=Card(card.uid,'TOY_504t');slime._learned_spell=card.card_id;slime._learned_card=deepcopy(card)
   game._set_card_cost(slime,cost);game._mutation_set_stats(slime,owner,cost,cost);game._carry_origin(card,slime)
   slime._hand_entry_turn=getattr(card,'_hand_entry_turn',game.turn)
   if hasattr(card,'_drawn_turn'):slime._drawn_turn=card._drawn_turn
   p.hand[p.hand.index(card)]=slime;game._refresh_auras()
 elif name=='historical_draw_balinda_finish':
  if source is not None and source in p.minions:
   attack=source.attack-source.aura_attack;health=source.max_health-source.aura_health
   a,b=op[1:]
   if a.get('card') is not None:game._set_card_cost(a['card'],max(0,attack));attack=a['cost']
   if b.get('card') is not None:game._set_card_cost(b['card'],max(0,health));health=b['cost']
   game._set_entity_stats(source,attack,health)
 elif name=='historical_draw_both_finish':
  mode,a,b=op[1:];cards=[a.get('card'),b.get('card')]
  if mode=='historical_draw_menace':
   if all(card is not None for card in cards):game._set_card_cost(cards[0],b['cost']);game._set_card_cost(cards[1],a['cost'])
  else:
   for recipient,card in zip((owner,1-owner),cards):
    player=game.players[recipient]
    if card is not None and card in player.hand and has_tribe(game._card_data(card),'DRAGON') and len(player.board)<7:
     player.hand.remove(card);game._summon(recipient,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='recruit',entry_zone='hand',entry_source=card,entry_site='utgarde_grapplesniper')
 elif name=='historical_draw_nonstarting_one':
  choices=[i for i,card in enumerate(p.deck) if not game._started_in_deck(card,owner)]
  if choices:game._take_deck_draw(owner,game.rng.choice(choices),include_burned=True)
 elif name=='historical_draw_school_damage':game._effect(('area_damage','enemy_minions',1+len(getattr(p,'historical_spell_schools',()))),ctx)
 elif name=='historical_draw_capture':
  filters,priority,state=op[1:]
  choices=[i for i,c in enumerate(p.deck) if filters is None or game._matches_filter(c,filters,zone_owner=owner)]
  if priority!='random' and choices:
   costs={i:game._card_stat(p.deck[i],'cost',owner) for i in choices};best=(min if priority=='lowest' else max)(costs.values());choices=[i for i in choices if costs[i]==best]
  if choices:
   index=len(p.deck)-1 if filters is None and priority=='random' else game.rng.choice(choices)
   card=game._take_deck_draw(owner,index,include_burned=True)
  elif filters is None:card=game._draw(owner,include_burned=True)
  else:card=None
  if card is not None:
   state['card']=card;state['cost']=game._cost(card,owner)
 elif name=='historical_draw_finish':
  mode,args,state=op[1:];card=state.get('card')
  if card is None:return True
  if mode=='magatha':
   if card in p.hand and game._card_data(card)['type']=='SPELL':p.hand.remove(card);game._enter_hand(1-owner,card);game._refresh_auras()
  elif mode=='nemsy':
   if source is not None:source.rule_state['historical_nemsy_drawn']=card.uid
  elif mode=='watercolor':
   if card in p.hand:game._b60_state(card).setdefault('historical_watercolor_owners',[]).append(owner)
  elif mode=='same_turn_follow':
   if card in p.hand:
    from .historical_copy_batches import attach_same_turn_follow
    attach_same_turn_follow(game,card,ctx,args[0])
  elif mode=='source_stats':
   if source is not None and source in p.minions:game._buff(source,game._card_stat(card,'attack',owner),game._card_stat(card,'health',owner))
  elif mode=='chalk':
   if card in p.hand:
    from .generation_cards import pool
    values=game._generation_candidates(pool(card_type='MINION',rarity='LEGENDARY'),owner)
    if values:
     attack=game._card_stat(card,'attack',owner);health=game._card_stat(card,'health',owner);cost=game._cost(card,owner)
     game._b60_transform_card(card,game.rng.choice(values));game._mutation_set_stats(card,owner,attack,health);game._set_card_cost(card,cost)
  elif mode=='colifero':
   if game._card_data(card)['type']=='MINION':
    from copy import deepcopy
    # A summoned template copies the drawn physical card's current definition.
    for minion in list(p.minions):
     if minion is source:continue
     if hasattr(card,'_historical_retained_minion'):
      from .historical_copy_batches import replace
      donor=deepcopy(card._historical_retained_minion);donor.health=donor.max_health
      replacement=replace(game,minion,donor)
     else:replacement=game._transform(minion,card.card_id)
     if replacement is not None and replacement.card_id==card.card_id:
      game._held_bonus_entry(replacement,card);game._dark_entry(replacement,card);game._stored_entry(replacement,card);game._forge_entry(replacement,card)
      from .base_stats import carry_base_stats
      carry_base_stats(card,replacement)
      game._set_entity_stats(replacement,game._card_stat(card,'attack',owner),game._card_stat(card,'health',owner))
      for key in ('historical_imposter_spell_damage','historical_fire_spell_damage'):
       if key in getattr(card,'rule_state',{}):replacement.rule_state[key]=card.rule_state[key]
      keyword=getattr(card,'rule_state',{}).get('historical_imposter_keyword')
      if keyword:replacement.keywords.add(keyword)
      game._carry_origin(card,replacement,copied=True,source_owner=owner)
  elif mode=='none':pass
  elif mode=='copy_temporary':
   clone=game._copy_card(card,source_owner=owner);game._make_temporary(clone);game._enter_hand(owner,clone)
  elif mode=='random_cost_summon':
   from .generation_cards import pool,random_cards
   game._effect(random_cards(pool(card_type='MINION',minimum=state['cost'],maximum=state['cost']),destination='board'),ctx)
  elif mode=='chicken':
   if card in p.hand and game._card_data(card)['type']=='MINION':
    from engine.game import Card
    replacement=Card(game._new_id(),'GVG_092t');game._carry_origin(card,replacement)
    replacement._hand_entry_turn=getattr(card,'_hand_entry_turn',game.turn);p.hand[p.hand.index(card)]=replacement;game._refresh_auras()
  elif mode=='set_cost':game._set_card_cost(card,args[0])
  elif mode=='armor_cost':game._gain_armor(owner,state['cost'])
  elif mode=='damage_hero_cost':game._deal_effect(game.hero_id(owner),state['cost'],ctx)
  elif mode=='nature_elemental':
   if has_school(game._card_data(card),'NATURE'):game._effect(('filtered_draw',MINION+(('tribe','eq','ELEMENTAL'),),1),ctx)
  elif mode=='school_discount':
   if has_school(game._card_data(card),args[0]):card.cost_delta=getattr(card,'cost_delta',0)-(args[1])
  elif mode=='source_keyword':
   if source is not None and source in p.minions:source.keywords.add(args[0])
  elif mode=='recruit_drawn':
   if card in p.hand and game._card_data(card)['type']=='MINION' and len(p.board)<7:
    p.hand.remove(card);game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='recruit',entry_zone='hand',entry_source=card,entry_site='historical_draw_recruit')
  elif mode=='copy_drawn_minion':
   if game._card_data(card)['type']=='MINION':game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='copy',entry_zone='hand',entry_source=card,entry_site='historical_draw_copy')
  elif mode=='left_hand':
   if card in p.hand:p.hand.remove(card);p.hand.insert(0,card)
  elif mode=='frost_elementals':
   if has_school(game._card_data(card),'FROST'):
    game._rule_events.append(('captured_effects',dict(operations=(('summon','BAR_888t',2),),context=dict(ctx)),[]))
  elif mode=='buff':_saidan_add(card,'attack_bonus',args[0]);_saidan_add(card,'health_bonus',args[1])
  elif mode=='discount':card.cost_delta=getattr(card,'cost_delta',0)-(args[0])
  elif mode=='turn_zero':
   game._b60_state(card)['historical_turn_zero_cost']=game.turn
  elif mode=='health_payment':game._b60_state(card)['health_payment']=True
  elif mode=='one_stats_cost':game._mutation_set_stats(card,owner,1,1);game._set_card_cost(card,1)
  else:raise ValueError('Unknown post-draw operation: '+mode)
 elif name=='historical_draw_discount_fire_hand':
  choices=[c for c in p.hand if game._card_data(c)['type']=='SPELL' and has_school(game._card_data(c),'FIRE')]
  if choices:
   chosen=game.rng.choice(choices);chosen.cost_delta=getattr(chosen,'cost_delta',0)-op[1]
 elif name=='historical_draw_pair_finish':
  cards=[state.get('card') for state in op[1:]]
  if all(c is not None and has_school(game._card_data(c),'FROST') for c in cards):game._effect(('area_damage','enemies',2),ctx)
 elif name=='historical_draw_shuffle_cheapest_hand':
  if p.hand:
   costs={c.uid:game._cost(c,owner) for c in p.hand};best=min(costs.values());card=game.rng.choice([c for c in p.hand if costs[c.uid]==best]);game._shuffle_hand_card(owner,card,actor=owner)
 elif name=='historical_draw_secret_step':
  state=op[1]
  choices=[i for i,c in enumerate(p.deck) if 'SECRET' in game._card_mechanics(c) and game._card_data(c)['id'] not in state['used']]
  if not choices:state['remaining']=0
  else:
   i=game.rng.choice(choices);state['used'].add(game._card_data(p.deck[i])['id']);state['remaining']-=1;game._take_deck_draw(owner,i,include_burned=True)
 elif name=='historical_draw_history_buff':
  key,attack,health=op[1:]
  count=sum(entry['card_id'] in SI7_IDS if key=='SI7' else entry['card_id']==key for entry in p.played_history)
  if source is not None:game._buff(source,count*attack,count*health)
 else:return False
 return True
