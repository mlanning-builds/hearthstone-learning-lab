"""Explicit historical physical hand/deck mutations; implementation-only."""
from .historical_saidan import add as _saidan_add
from engine.game import Card
from .selectors import has_tribe,has_school

SWAP_FORMS={cid:cid+'t' for cid in ('GIL_200','GIL_201','GIL_202','GIL_528','GIL_529')}
SWAP_FORMS.update({v:k for k,v in tuple(SWAP_FORMS.items())})
RULES={cid:('none',[]) for cid in ('GIL_200','GIL_201','GIL_202','GIL_528','GIL_529','GVG_063','SCH_618','DAL_561','CFM_064','DRG_109','VAC_447')}
RULES.update({
 'AV_223':('none',[('historical_hand_vanndar',)]),
 'GIL_840':('none',[('historical_hand_deck_inner_fire',)]),
 'GDB_863':('none',[('historical_hand_spell_source_cost',)]),
 'VAC_954':('none',[('historical_hand_discount_schools',2)]),
 'TRL_328':('none',[('historical_hand_copy_tribe','DRAGON',False)]),
 'ULD_151':('none',[('historical_hand_copy_tribe','BEAST',True)]),
 'RLK_820':('none',[('historical_hand_spell_damage',('hand','deck'),'ARCANE',1)]),
 'RLK_826':('none',[('historical_hand_spell_damage',('hand',),'ARCANE',1)]),
 'RLK_120':('none',[('historical_hand_shred_minion',4)]),
 'TSC_652':('none',[('historical_hand_high_spell_refresh',)]),
 'GDB_121':('none',[('historical_hand_demon_discount',1)]),
 'GDB_128':('none',[('historical_hand_summon_nonstarting','DEMON')]),
 'GDB_304':('none',[('historical_hand_fire_elementals',1)]),
})
DEATH_EFFECTS={'TOY_390':[('historical_hand_discount_spells',2,1)],'TTN_481':[('historical_hand_summon_nonstarting','MINION')]}
for cid in DEATH_EFFECTS:RULES.setdefault(cid,('none',[]))
TOKEN_RULES={cid:('none',[]) for cid in SWAP_FORMS if cid.endswith('t')}
RULES.update({
 'DRG_062':('none',[('historical_hand_transform_zone','deck','neutral','own',False)]),
 'GIL_694':('none',[('historical_hand_transform_zone','deck','one_cost','legendary',False)]),
 'ICC_811':('none',[('historical_hand_transform_zone','hand','spell','enemy_spell',False)]),
 'RLK_545':('none',[('historical_hand_transform_zone','hand','spell','spell_plus_three',True)]),
 'SW_078':('none',[('historical_hand_transform_zone','deck','minion','dragon',True)]),
 'ETC_395':('none',[('historical_hand_zero_spells',)]),
 'CFM_672':('friendly_minion',[('historical_hand_recruit_copies',)]),
 'DMF_053':('none',[]),
})
END_EFFECTS={'DMF_053':[('historical_copy_summon_zone','deck',5,5,())]}
from .historical_play_batches import zone_offer
RULES.update({
 'ICC_415':('none',[zone_offer('own','deck',(('type','eq','MINION'),),'copy')]),
 'LEG_CS3_015':('none',[zone_offer('own','deck',(('type','eq','MINION'),('tribe','eq','BEAST')),'copy')]),
})
# Discard bodies use physical snapshots; no generated pool is restricted.
RULES.update({
 'KAR_089':('none',[]), 'KAR_205':('none',[]), 'WON_098':('none',[]),
 'RLK_532':('none',[]), 'TRL_252':('none',[]), 'UNG_836':('none',[]),
 'SCH_147':('none',[]),
 'RLK_535':('none',[('discard',2)]),
 'REV_510':('none',[('discard_entire_hand',)]),
 'TRL_551':('none',[('historical_hand_discard_select','own','lowest','none')]),
 'ULD_163':('none',[('historical_hand_discard_select','own','highest','copies')]),
 'RLK_540':('none',[('historical_hand_discard_select','own','undead','summon')]),
 'CS3_003':('none',[('historical_hand_discard_select','enemy','minion','return')]),
 'TRL_247':('none',[('historical_hand_discard_history','hand',3)]),
 'OG_121':('none',[('historical_hand_discard_history','health_hand',-1)]),
 'WON_105':('none',[('historical_hand_discard_history','health_hand',-1)]),
 'UNG_830':('none',[]),
 'NEW1_030':('none',[('historical_hand_deathwing',False)]),
 'LEG_CS3_036':('none',[('historical_hand_deathwing',True)]),
 'ETC_071':('none',[]), 'RLK_607':('none',[]),
})
TOKEN_RULES['SCH_147t']=('none',[])
DEATH_EFFECTS.update({'SCH_147':[('summon','SCH_147t',2)],'REV_510':[('draw',3)],
 'UNG_830':[('historical_hand_discard_history','board',1)],
 'ETC_071':[('historical_hand_rin',)]})
END_EFFECTS['RLK_607']=[('historical_hand_discard_select','enemy','spell','none')]
TRIGGERS={'KAR_089':('friendly_discard',[('draw',1)])}
DISCARD_EFFECTS={cid:[('historical_hand_discard_intrinsic','summon')] for cid in ('KAR_205','WON_098','RLK_532')}
DISCARD_EFFECTS.update({'SCH_147':[('summon','SCH_147t',2)],
 'TRL_252':[('historical_hand_discard_intrinsic','copies')],
 'UNG_836':[('historical_hand_discard_intrinsic','grow_return')]})
RULES.update({cid:('none',[]) for cid in ('OG_138','ONY_002')})
RULES['LOOT_149']=('none',[])

SHIFTERS={
 'TOY_700t13':('mage_playable',None,None,None),
 'SC_003t':('zerg',None,None,None),
 'OG_123':('random',None,None,None),
 'UNG_929':('weapon',None,None,None),
 'DRG_096':('legendary',None,(5,5),5),
 'GIL_142':('enemy_hand',None,None,None),
 'TTN_741':('enemy_deck',None,None,None),
 'WON_026':('cost',3,None,None),
 'WON_039':('cost',2,None,None),
 'WON_077':('cost',4,None,None),
 'BOT_434':('floop',None,(3,4),4),
}
RULES.update({cid:('none',[]) for cid in SHIFTERS})
from . import historical_school_forms
RULES.update(historical_school_forms.RULES)
TOKEN_RULES.update(historical_school_forms.TOKEN_RULES)
TRIGGERS.update(historical_school_forms.TRIGGERS)
DEATH_EFFECTS.update(historical_school_forms.DEATH_EFFECTS)
# Larva is a generated token with persistent hand transformation behavior.
RULES.pop('SC_003t',None)
TOKEN_RULES['SC_003t']=('none',[])
from .generation_cards import pool,random_cards
REMIXED_FORMS={
 'JAM_000':('JAM_000t','JAM_000t2','JAM_000t3','JAM_000t4'),
 'JAM_012':('JAM_012t','JAM_012t2','JAM_012t3','JAM_012t4'),
 'JAM_033':('JAM_033t','JAM_033t2','JAM_033t3','JAM_033t4'),
}
REMIXED_ORIGIN={cid:root for root,forms in REMIXED_FORMS.items() for cid in (root,)+forms}
RULES.update({root:('none',[]) for root in REMIXED_FORMS})
TOKEN_RULES.update({
 'JAM_000t':('none',[random_cards(pool(card_type='SPELL',school='FROST'),2)]),
 'JAM_000t2':('none',[random_cards(pool(card_type='MINION',tribe='MECHANICAL'),2)]),
 'JAM_000t3':('none',[('add','GAME_005',2)]),
 'JAM_000t4':('none',[random_cards(pool(card_type='SPELL',mechanic='SECRET',classes='MAGE'),2)]),
 'JAM_012t':('none',[('summon','ETC_105',1)]),
 'JAM_012t2':('none',[('summon','EX1_575',1)]),
 'JAM_012t3':('none',[('summon','EX1_565',1)]),
 'JAM_012t4':('none',[('summon','JAM_010',1)]),
})
# Musician forms carry real printed Rush plus Shield/Windfury/Lifesteal/Poisonous.
TOKEN_RULES.update({cid:('none',[]) for cid in REMIXED_FORMS['JAM_033']})
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'ETC_105','EX1_575','EX1_565','JAM_010','GAME_005'}


def remix_card(game,owner,card):
 origin=REMIXED_ORIGIN.get(card.card_id)
 if origin is None:return
 from .pools import require_fixed_cards
 forms=REMIXED_FORMS[origin]
 require_fixed_cards(forms,game.cards)
 values=[cid for cid in forms if cid!=card.card_id]
 game._b60_transform_card(card,game.rng.choice(values))
 game._log('hand_remixed',player=owner,entity=card.uid)


def initialize_shifter(game,owner,card):
 if card.card_id=='WORK_006':game._b60_state(card).setdefault('historical_robocaller_digits',(8,8,8))
 if card.card_id=='TSC_641ta':card._historical_ring_tides=True
 if card.card_id in REMIXED_FORMS:remix_card(game,owner,card)
 if card.card_id in SHIFTERS:game._b60_state(card).setdefault('historical_hand_shifter',card.card_id)
 if card.card_id=='TOY_700t13':transform_shifter(game,owner,card,'TOY_700t13')
 if getattr(card,'rule_state',{}).get('historical_hand_shifter')=='BOT_434':
  records=[record for record in game.players[owner].replay_history if game._card_data(record.card)['type']=='MINION']
  if records:transform_shifter(game,owner,card,'BOT_434',records[-1].card)


def transform_shifter(game,owner,card,origin,donor=None):
 from .generation_cards import pool
 mode,cost,stats,fixed=SHIFTERS[origin]
 if donor is None:
  if mode=='mage_playable':
   maximum=game.players[owner].mana+1
   groups=[game._generation_candidates(pool(classes=hero,maximum=maximum),owner) for hero in ('MAGE','NEUTRAL')]
   choices=tuple(sorted({cid for values in groups for cid in values}))
   if not choices:return
   cid=game.rng.choice(choices)
  elif mode=='zerg':
   from .historical_copy_batches import ZERG_MINION_POOL
   from .pools import require_fixed_cards
   require_fixed_cards(ZERG_MINION_POOL,game.cards)
   cid=game.rng.choice(ZERG_MINION_POOL)
  elif mode in ('enemy_hand','enemy_deck'):

   choices=getattr(game.players[1-owner],'hand' if mode=='enemy_hand' else 'deck')
   if not choices:return
   donor=game.rng.choice(choices);cid=game._card_data(donor)['id'];card._copied_from_owner=1-owner
  else:
   request=pool(card_type='WEAPON') if mode=='weapon' else pool(card_type='MINION',rarity='LEGENDARY') if mode=='legendary' else pool(card_type='MINION',minimum=cost,maximum=cost) if mode=='cost' else pool(card_type='MINION')
   choices=game._generation_candidates(request,owner)
   if not choices:return
   cid=game.rng.choice(choices)
 else:cid=game._card_data(donor)['id']
 game._b60_transform_card(card,cid)
 if stats is not None:card.base_stat_override=stats
 if fixed is not None:game._set_card_cost(card,fixed)
 if mode=='mage_playable' and not game._b60_state(card).get('historical_morphing_discount_applied'):
  card.cost_delta=getattr(card,'cost_delta',0)-1
  game._b60_state(card)['historical_morphing_discount_applied']=True
 state=game._b60_state(card);state['historical_hand_shifter']=origin
 if origin in ('WON_026','WON_077'):state['historical_imposter_keyword']='POISONOUS' if origin=='WON_026' else 'STEALTH'
 if origin=='WON_039':state['historical_imposter_spell_damage']=1
 game._log('hand_transformed',player=owner,entity=card.uid)


def turn_entries(game,phase):
 if phase not in ('start','end'):return []
 ticks=[dict(source=None,order=card.uid,operations=(('historical_hand_discount_tick',card.uid),)) for card in game.players[game.current].hand if (card.card_id=='OG_138' and phase=='start' or card.card_id=='ONY_002' and phase=='end' and game.players[game.current].mana>0)]
 if phase=='end':
  ticks.extend(dict(source=None,order=card.uid,operations=(('historical_copy_chaos_expire',card.uid),)) for card in game.players[game.current].hand if getattr(card,'rule_state',{}).get('historical_chaos_gaze_due',game.players[game.current].turns_taken+1)<=game.players[game.current].turns_taken)
  return ticks
 from .historical_held_upgrades import SEEDLINGS
 ticks.extend(dict(source=None,order=card.uid,operations=(('historical_held_seedling_tick',card.uid),)) for card in game.players[game.current].hand if card.card_id in SEEDLINGS)
 ticks.extend(dict(source=None,order=card.uid,operations=(('historical_copy_cheese_tick',card.uid),)) for card in game.players[game.current].hand if card.card_id=='VAC_955t')
 ticks.extend(dict(source=None,order=card.uid,operations=(('historical_copy_mirage_tick',card.uid),)) for card in game.players[game.current].hand if getattr(card,'_historical_mirror_mode',None)=='mirage')
 ticks.extend(dict(source=None,order=card.uid,operations=(('historical_hand_robocaller_tick',card.uid),)) for card in game.players[game.current].hand if card.card_id=='WORK_006')
 ticks.extend(dict(source=None,order=card.uid,operations=(('historical_hand_remix_tick',card.uid),)) for card in game.players[game.current].hand if card.card_id in REMIXED_ORIGIN)
 for card in game.players[game.current].hand:
  if card.card_id in SHIFTERS:game._b60_state(card).setdefault('historical_hand_shifter',card.card_id)
 if phase=='start':ticks.extend(dict(source=None,order=card.uid,operations=(('historical_hand_watercolor',card.uid),)) for card in game.players[game.current].hand if game.current in getattr(card,'rule_state',{}).get('historical_watercolor_owners',()))
 ticks.extend(dict(source=None,order=card.uid,operations=(('historical_hand_shifter_tick',card.uid),)) for card in game.players[game.current].hand if getattr(card,'rule_state',{}).get('historical_hand_shifter') in SHIFTERS and getattr(card,'rule_state',{}).get('historical_hand_shifter')!='BOT_434')
 return ticks+[dict(source=None,order=card.uid,operations=(('historical_hand_swap_tick',card.uid,card.card_id),)) for card in game.players[game.current].hand if card.card_id in SWAP_FORMS]


def held_event(game,kind,data):
 historical_school_forms.held_event(game,kind,data)
 if kind=='minion_died':
  for card in game.players[data['owner']].hand:
   if card.card_id in ('BT_481','REV_906'):
    state=game._b60_state(card);state['historical_held_deaths']=state.get('historical_held_deaths',0)+1
 if kind=='minion_played':
  owner=data['owner'];donor=next((m for m in game.players[owner].minions if m.uid==data.get('source')),None)
  if donor is None:
   records=[record for record in game.players[owner].replay_history if game._card_data(record.card)['type']=='MINION']
   donor=records[-1].card if records else None
  if donor is not None:
   for card in tuple(game.players[owner].hand):
    if card.card_id=='BOT_434':game._b60_state(card).setdefault('historical_hand_shifter','BOT_434')
    if getattr(card,'rule_state',{}).get('historical_hand_shifter')=='BOT_434':transform_shifter(game,owner,card,'BOT_434',donor)

 if kind=='spell_cast':
  owner=data['owner'];source=data.get('physical_card')
  if source is not None:
   for card in tuple(game.players[owner].hand):
    if card.card_id=='TSC_641ta' or getattr(card,'_historical_ring_tides',False):
     copy=game._copy_card(source,source_owner=owner);uid=card.uid;entry=getattr(card,'_hand_entry_turn',None)
     card.__dict__.clear();card.__dict__.update(copy.__dict__);card.uid=uid;card._historical_ring_tides=True
     if entry is not None:card._hand_entry_turn=entry
     game._set_card_cost(card,1)
  player=game.players[owner]
  if player.weapon and player.weapon['card_id']=='TSC_641tc':
   weapon_uid=getattr(player.equipped_card,'uid',None)
   game._rule_events.append(('captured_effects',dict(operations=(('historical_copy_xalatath',weapon_uid),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
  if player.weapon and player.weapon['card_id']=='KAR_097t':
   weapon_uid=getattr(player.equipped_card,'uid',None)
   game._rule_events.append(('captured_effects',dict(operations=(('historical_copy_atiesh',weapon_uid,data['cost']),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='KAR_097t')),[]))
  source=data.get('physical_card');groups=set(getattr(source,'rule_state',{}).get('historical_spell_escalation',()))
  if groups:
   for card in game.players[data['owner']].hand:
    amount=len(groups & set(getattr(card,'rule_state',{}).get('historical_spell_escalation',())))
    if amount:card.cost_delta+=amount
  return
 if kind!='minion_died':return
 for player in game.players:
  for card in player.hand:
   if card.card_id=='LOOT_149':card.cost_delta-=1
 p=game.players[data['owner']];demon=has_tribe(game.cards[data['card_id']],'DEMON')
 for card in p.hand:
  if card.card_id=='GVG_063':_saidan_add(card,'attack_bonus',1)
  elif card.card_id=='SCH_618':_saidan_add(card,'attack_bonus',1);_saidan_add(card,'health_bonus',1)
  elif card.card_id=='DAL_561' and demon:card.cost_delta-=1


def summoned(game,minion):
 if 'BATTLECRY' not in game.cards[minion.card_id].get('mechanics',()):return
 for card in game.players[minion.owner].hand:
  if card.card_id=='CFM_064':_saidan_add(card,'attack_bonus',1);_saidan_add(card,'health_bonus',1)


def split(game,op,ctx):
 school=historical_school_forms.split(game,op,ctx)
 if school is not None:return school
 if op[0]=='historical_hand_deathwing':
  source=ctx.get('source');victims=[m for player in game.players for m in player.minions if m is not source and m.health>0]
  state={'victims':victims,'counted':op[1]}
  return ('historical_hand_destroy_victims',state),(('historical_hand_deathwing_discard',state),)
 if op[0]=='historical_hand_rin':
  operations=[]
  for effect in (('draw',2),('discard',2),('historical_hand_shred_top',2)):
   for owner in (ctx['owner'],1-ctx['owner']):
    operations.append(('replay_context',(effect,),dict(ctx,owner=owner)))
  return game._split_fixed_summon(('replay_context',tuple(operations),dict(ctx)),ctx)
 if op[0]=='historical_hand_discard_history':
  owner=ctx['owner'];values=list(getattr(game.players[owner],'historical_discard_cards',()))
  if op[1]=='board':values=[c for c in values if game._card_data(c)['type']=='MINION']
  operations=tuple(('historical_hand_discard_delivery',{'card':game._copy_card(c,source_owner=owner),'owner':owner,'mode':op[1]}) for c in game.rng.sample(values,len(values) if op[2]<0 else min(op[2],len(values))))
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if op[0]=='historical_hand_recruit_copies':
  from .identities import canonical_identity
  p=game.players[ctx['owner']];target=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is None:return ('batch30_noop',),()
  identity=canonical_identity(game._card_data(target),game.cards);operations=[]
  for i,value in enumerate(p.deck):
   if canonical_identity(game._card_data(value),game.cards)==identity:
    card=value if isinstance(value,Card) else Card(game._new_id(),value);p.deck[i]=card;operations.append(('historical_hand_recruit_physical',{'card':card}))
  return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())
 if op[0]!='historical_hand_summon_nonstarting':return None
 owner=ctx['owner'];source=ctx.get('source');operations=[]
 for record in game.players[owner].replay_history:
  data=game._card_data(record.card)
  if data['type']!='MINION' or game._started_in_deck(record.card,owner):continue
  if op[1]!='MINION' and not has_tribe(data,op[1]):continue
  if op[1]=='MINION' and source is not None and data['id']==source.card_id:continue
  operations.append(('summon',data['id'],1))
 return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())


def execute(game,op,ctx):
 if historical_school_forms.execute(game,op,ctx):return True
 name=op[0]
 if name=='historical_hand_robocaller_tick':
  card=next((card for card in game.players[ctx['owner']].hand if card.uid==op[1] and card.card_id=='WORK_006'),None)
  if card is not None:
   game._b60_state(card)['historical_robocaller_digits']=tuple(game.rng.randrange(10) for _ in range(3))
   game._log('hand_numbers_dialed',player=ctx['owner'],entity=card.uid)
  return True
 if name=='historical_hand_remix_tick':
  card=next((card for card in game.players[ctx['owner']].hand if card.uid==op[1]),None)
  if card is not None:remix_card(game,ctx['owner'],card)
  return True
 if name=='historical_hand_shifter_tick':
  card=next((c for c in game.players[ctx['owner']].hand if c.uid==op[1]),None)
  if card is not None:
   origin=getattr(card,'rule_state',{}).get('historical_hand_shifter',card.card_id)
   if origin in SHIFTERS:transform_shifter(game,ctx['owner'],card,origin)
  return True
 if name=='historical_hand_discount_tick':
  card=next((c for c in game.players[ctx['owner']].hand if c.uid==op[1]),None)
  if card is not None:card.cost_delta-=1
  return True
 if not name.startswith('historical_hand_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_hand_watercolor':
  card=next((c for c in p.hand if c.uid==op[1]),None)
  if card is not None:card.cost_delta-=getattr(card,'rule_state',{}).get('historical_watercolor_owners',()).count(owner)
 elif name=='historical_hand_recruit_physical':
  card=op[1]['card'];index=next((i for i,value in enumerate(p.deck) if value is card),None)
  if index is not None and len(p.board)<7:
   p.deck.pop(index);game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='recruit',entry_zone='deck',entry_source=card,entry_site='madam_goya')
 elif name=='historical_hand_discard_select':
  from copy import deepcopy
  recipient=owner if op[1]=='own' else 1-owner;values=list(game.players[recipient].hand);selector=op[2]
  if selector in ('minion','spell'):values=[c for c in values if game._card_data(c)['type']==selector.upper()]
  elif selector=='undead':values=[c for c in values if has_tribe(game._card_data(c),'UNDEAD')]
  elif values:
   costs=[game._cost(c,recipient) for c in values];extreme=(min if selector=='lowest' else max)(costs)
   values=[c for c,cost in zip(values,costs) if cost==extreme]
  if values:
   card=game.rng.choice(values);remembered=deepcopy(card)
   if source is not None and op[3]!='none':
    mode=op[3];destination=recipient if mode=='return' else owner
    for _ in range(2 if mode=='copies' else 1):
     source.attached_death_effects.append(('historical_hand_discard_delivery',{'card':deepcopy(remembered),'owner':destination,'mode':'board' if mode=='summon' else 'hand'}))
   game._discard_card(recipient,card)
 elif name=='historical_hand_discard_delivery':
  state=op[1];recipient=state['owner'];card=game._copy_card(state['card'],source_owner=recipient)
  if state['mode']=='board':game._summon(recipient,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_source=card,entry_zone='discard',entry_origin='discard')
  else:
   if state['mode']=='health_hand':game._b60_state(card)['health_payment']=True
   game._enter_hand(recipient,card)
 elif name=='historical_hand_discard_intrinsic':
  card=ctx.get('physical_card')
  if card is not None:
   if op[1]=='summon':game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_source=card,entry_zone='discard',entry_origin='discard')
   elif op[1]=='copies':
    for _ in range(2):game._clone_hand_card(owner,card,source_owner=owner)
   else:
    card=game._copy_card(card,source_owner=owner);_saidan_add(card,'attack_bonus',2);_saidan_add(card,'health_bonus',2);game._enter_hand(owner,card)
 elif name=='historical_hand_destroy_victims':
  for m in op[1]['victims']:
   if m.health>0:m.health=0
 elif name=='historical_hand_deathwing_discard':
  state=op[1]
  if state['counted']:
   destroyed=sum(m not in game.players[m.owner].board for m in state['victims']);game._discard_random(owner,destroyed)
  else:game._discard_cards(owner,list(p.hand))
 elif name=='historical_hand_shred_top':
  for _ in range(min(op[1],len(p.deck))):
   card=p.deck.pop();game._zone_card_removed(owner,card,'deck','destroy');game._log('destroy_deck_card',player=owner,card=game._card_data(card)['id'])
 elif name=='historical_hand_zero_spells':
  group=game._new_id()
  for card in p.hand:
   if game._card_data(card)['type']=='SPELL':
    game._set_card_cost(card,0);state=game._b60_state(card);state.setdefault('historical_spell_escalation',[]).append(group)
 elif name=='historical_hand_transform_zone':
  from .generation_cards import pool
  from .selectors import has_class
  zone=getattr(p,op[1]);changes=[]
  for i,old in enumerate(zone):
   data=game._card_data(old);selector=op[2]
   selected=(selector=='neutral' and has_class(data,'NEUTRAL') or selector=='one_cost' and game._card_stat(old,'cost',owner)==1 or selector=='spell' and data['type']=='SPELL' or selector=='minion' and data['type']=='MINION')
   if not selected:continue
   kind=op[3];cost=game._card_stat(old,'cost',owner)
   if kind=='own':request=pool(classes='own')
   elif kind=='legendary':request=pool(card_type='MINION',rarity='LEGENDARY')
   elif kind=='enemy_spell':request=pool(card_type='SPELL',classes=game.players[1-owner].hero_class)
   elif kind=='spell_plus_three':request=pool(card_type='SPELL',minimum=cost+3,maximum=cost+3)
   elif kind=='dragon':request=pool(card_type='MINION',tribe='DRAGON')
   else:raise ValueError('Unknown explicit zone transformation')
   values=game._generation_candidates(request,owner)
   changes.append((i,old,cost,values))
  # Every complete pool is checked before any sampling or physical replacement.
  for i,old,cost,values in changes:
   if not values:continue
   cid=game.rng.choice(values);card=Card(game._new_id(),cid);game._carry_origin(old,card)
   if op[4]:
    game._set_card_cost(card,cost)
    if game._card_data(old)['type']=='MINION':game._mutation_set_stats(card,owner,game._card_stat(old,'attack',owner),game._card_stat(old,'health',owner))
   if op[1]=='hand':
    card._hand_entry_turn=getattr(old,'_hand_entry_turn',game.turn)
    if hasattr(old,'_drawn_turn'):card._drawn_turn=old._drawn_turn
   zone[i]=card
  game._refresh_auras()
 elif name=='historical_hand_swap_tick':
  card=next((c for c in p.hand if c.uid==op[1] and c.card_id==op[2]),None)
  if card is not None:
   attack=game._card_stat(card,'attack',owner);health=game._card_stat(card,'health',owner);card.card_id=SWAP_FORMS[card.card_id]
   game._mutation_set_stats(card,owner,health,attack)
 elif name=='historical_hand_vanndar':
  minions=[c for c in p.deck if game._card_data(c)['type']=='MINION']
  cost=ctx.get('paid_cost')
  if cost is None:
   if source is None:return True
   cost=game._card_stat(source,'cost',owner)
  if all(cost<game._card_stat(c,'cost',owner) for c in minions):
   for i,value in enumerate(p.deck):
    if game._card_data(value)['type']=='MINION':
     card=value if isinstance(value,Card) else Card(game._new_id(),value);card.cost_delta-=3;p.deck[i]=card
 elif name=='historical_hand_deck_inner_fire':
  for i,value in enumerate(p.deck):
   if game._card_data(value)['type']=='MINION':
    card=value if isinstance(value,Card) else Card(game._new_id(),value);health=game._card_stat(card,'health',owner);game._mutation_set_stats(card,owner,health,health);p.deck[i]=card
 elif name=='historical_hand_spell_source_cost':
  values=[c for c in p.hand if game._card_data(c)['type']=='SPELL']
  if values and source is not None:game._set_card_cost(game.rng.choice(values),game._card_stat(source,'cost',owner))
 elif name=='historical_hand_discount_schools':
  for school in ('ARCANE','FEL','FIRE','FROST','HOLY','NATURE','SHADOW'):
   values=[c for c in p.hand if has_school(game._card_data(c),school)]
   if values:game.rng.choice(values).cost_delta-=op[1]
 elif name=='historical_hand_discount_spells':
  values=[c for c in p.hand if game._card_data(c)['type']=='SPELL']
  for card in game.rng.sample(values,min(op[1],len(values))):card.cost_delta-=op[2]
 elif name=='historical_hand_copy_tribe':
  values=[c for c in p.hand if has_tribe(game._card_data(c),op[1])]
  if op[2]:values=[game.rng.choice(values)] if values else []
  for card in values:game._clone_hand_card(owner,card,source_owner=owner)
 elif name=='historical_hand_spell_damage':
  for zone_name in op[1]:
   zone=getattr(p,zone_name)
   for i,value in enumerate(zone):
    if has_school(game._card_data(value),op[2]):
     card=value if isinstance(value,Card) else Card(game._new_id(),value);card.spell_damage_bonus=getattr(card,'spell_damage_bonus',0)+op[3];zone[i]=card
 elif name=='historical_hand_shred_minion':
  values=[i for i,c in enumerate(p.deck) if game._card_data(c)['type']=='MINION']
  if values:
   card=p.deck.pop(game.rng.choice(values));game._zone_card_removed(owner,card,'deck','destroy');game._log('destroy_deck_card',player=owner,card=game._card_data(card)['id']);game._gain_corpses(owner,op[1])
 elif name=='historical_hand_high_spell_refresh':
  costs=[game._cost(c,owner) for c in p.hand if game._card_data(c)['type']=='SPELL']
  if costs:game._effect(('refresh_mana',max(costs)),ctx)
 elif name=='historical_hand_demon_discount':p.historical_nonstarting_demon_discount=getattr(p,'historical_nonstarting_demon_discount',0)+op[1]
 elif name=='historical_hand_fire_elementals':
  for i,value in enumerate(p.deck):
   if has_tribe(game._card_data(value),'ELEMENTAL'):
    card=value if isinstance(value,Card) else Card(game._new_id(),value);state=game._b60_state(card);state['historical_fire_spell_damage']=state.get('historical_fire_spell_damage',0)+op[1];p.deck[i]=card
 else:return False
 return True

from .historical_student_outcomes import DISCARD_EFFECTS as STUDENT_OUTCOME_DISCARDS
DISCARD_EFFECTS.update(STUDENT_OUTCOME_DISCARDS)

from .historical_damage_spells import DISCARD_EFFECTS as DAMAGE_SPELL_DISCARDS
DISCARD_EFFECTS.update(DAMAGE_SPELL_DISCARDS)

from .historical_misc_spells import DISCARD_EFFECTS as MISC_DISCARD_EFFECTS
DISCARD_EFFECTS.update(MISC_DISCARD_EFFECTS)

# Remaining Remixed spell/weapon forms share the physical owner-start reroll.
from .historical_held_upgrades import REMIXED_FORMS as HELD_REMIXED_FORMS
REMIXED_FORMS.update(HELD_REMIXED_FORMS)
REMIXED_ORIGIN.update({cid:root for root,forms in HELD_REMIXED_FORMS.items() for cid in (root,)+forms})

from .historical_spell_archive_batch import DISCARD_EFFECTS as ARCHIVE_DISCARD_EFFECTS
DISCARD_EFFECTS.update(ARCHIVE_DISCARD_EFFECTS)
