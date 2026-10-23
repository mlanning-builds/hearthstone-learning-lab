"""Fantastic treasure choices and literal generated dependencies; unvalidated."""
from engine.game import Card
from .generation_cards import pool,board_pool,discover
from .historical_draw_batches import draw
from .pools import require_fixed_cards

ARTIFACTS=('LOEA16_3','LOEA16_4','LOEA16_5')
INVOCATIONS=('UNG_211a','UNG_211b','UNG_211c','UNG_211d')
ORIGINAL=('LOOT_998h','LOOT_998j','LOOT_998k','LOOT_998l')
MANAGER=('VAC_702t2','VAC_702t','VAC_702t4','VAC_702t3')
LEGENDARY=pool(card_type='MINION',rarity='LEGENDARY')
CROWN=board_pool(LEGENDARY)
RULES={
 'DAL_417':('none',[('historical_treasure_offer','lackey')]),
 'LOOT_357':('none',[('summon_opponent','LOOT_357l',1)]),
 'VAC_702':('none',[('historical_treasure_offer','manager')]),
}
TOKEN_RULES={'LOOT_357l':('none',[])}
for cid in ('LOOT_998h','VAC_702t2'):TOKEN_RULES[cid]=('none',[('historical_treasure_goblet',)])
for cid in ('LOOT_998j','VAC_702t'):TOKEN_RULES[cid]=('none',[('historical_treasure_crown',CROWN)])
for cid in ('LOOT_998k','VAC_702t4'):TOKEN_RULES[cid]=('none',[('historical_treasure_replace',LEGENDARY)])
for cid in ('LOOT_998l','VAC_702t3'):TOKEN_RULES[cid]=('none',[draw(mode='set_cost',args=(1,))]*3)
DEATH_EFFECTS={'LOOT_357l':[('historical_treasure_chest',)]}
END_EFFECTS={};TRIGGERS={}
RULES.update({'LOE_092':('none',[('historical_treasure_offer','artifact')]),'UNG_211':('none',[('historical_treasure_invocation',)])})
TOKEN_RULES.update({
 'LOEA16_3':('minion',[('buff',10,10)]),
 'LOEA16_4':('none',[('missiles','enemies',10)]),
 'LOEA16_5':('none',[('fill_board_summon','LOEA16_5t')]),
 'LOEA16_5t':('none',[]),
 'UNG_211a':('none',[('fill_board_summon','UNG_211aa')]),
 'UNG_211aa':('none',[]),
 'UNG_211b':('none',[('heal_own_hero',12)]),
 'UNG_211c':('none',[('damage_enemy_hero',6)]),
 'UNG_211d':('none',[('area_damage','enemy_minions',3)]),
})
RULES.update({
 'UNG_088':('none',[('historical_treasure_pool_offer',pool(card_type='SPELL',classes='own_or_neutral'),'cast')]),
 'UNG_835':('none',[('historical_treasure_pool_offer',pool(card_type='SPELL',classes='own_or_neutral'),'hurt')]),
 'WON_116':('none',[('historical_treasure_pool_offer',pool(card_type='MINION',mechanic='TAUNT',classes='own_or_neutral'),'armor')]),
 'TRL_077':('none',[discover(pool(card_type='MINION',mechanic='BATTLECRY',classes='own_or_neutral'),stats=(1,1),set_cost=1)]),
})
RULES.update({'DAL_736':('none',[('historical_treasure_elysiana',())]),'ULD_209':('none',[('historical_treasure_mystery',)])})
RULES.update({cid:('none',[('historical_treasure_filtered',mode)]) for cid,mode in (
 ('ETC_103','hipster'),('SW_065','importer'),('DEEP_037','maruut'),('WON_066','murozond'),('YOP_018','ivory'))})
RULES['WW_400']=('none',[('historical_treasure_dice',)])
RULES['TSC_069']=('friendly_minion',[('historical_treasure_filtered','amalgam')])
RULES.update({'SCH_507':('none',[('historical_treasure_pool_offer',pool(card_type='SPELL',minimum=1,classes='own_or_neutral'),'follow_fireheart')]),'GDB_136':('none',[('historical_treasure_pool_offer',pool(card_type='SPELL',classes='own_or_neutral'),'follow_hataaru')])})
RULES.update({
 'REV_000':('none',[('historical_treasure_pool_offer',pool(card_type='SPELL',classes='own_or_neutral'),'suspicious')]),
 'REV_002':('none',[('historical_treasure_pool_offer',pool(card_type='MINION',rarity='LEGENDARY',classes='own_or_neutral'),'suspicious')]),
 'REV_006':('none',[('historical_treasure_pool_offer',pool(card_type='WEAPON',classes='own_or_neutral'),'suspicious')]),
 'NX2_044':('none',[('historical_treasure_pool_offer',pool(minimum=1,maximum=1,classes='own_or_neutral'),'suspicious')]),
})
RULES['DRG_086']=('none',[('historical_treasure_pool_offer',pool(card_type='MINION',tribe='DRAGON',classes='own_or_neutral'),'chromatic')])
DEATH_EFFECTS['DRG_086']=[('historical_treasure_egg_hatch',)]
RULES.update({'LOE_076':('none',[('historical_treasure_power','basic')]),'ULD_500':('none',[('historical_treasure_power','upgraded')])})
from .genn import POWERS as UPGRADED_POWERS
from .historical_copy_batches import BASIC_POWERS
FIXED_POWER_IDS=frozenset(BASIC_POWERS.values())|frozenset(UPGRADED_POWERS.values())
MALYGOS_SPELLS=tuple('DRG_270t'+str(n) for n in (1,2,4,5,6,7,8,9,11))
RULES['DRG_270']=('none',[('historical_treasure_malygos',)])
from .generation_cards import random_cards
TOKEN_RULES.update({'DRG_270t1':('none',[('draw',4)]),'DRG_270t2':('none',[random_cards(pool(card_type='SPELL',classes='MAGE'),3)]),'DRG_270t4':('none',[('area_damage','enemy_minions',2)]),'DRG_270t5':('none',[('freeze_enemies',)]),'DRG_270t6':('minion',[('transform','DRG_270t6t')]),'DRG_270t6t':('none',[]),'DRG_270t7':('none',[('area_damage','enemy_minions',8)]),'DRG_270t8':('character',[('damage',3),('freeze',)]),'DRG_270t9':('character',[('damage',8)]),'DRG_270t11':('none',[('missiles','enemies',6)])})
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|FIXED_POWER_IDS


def split(game,op,ctx):
 if op[0]=='historical_treasure_egg_hatch':
  cid=getattr(ctx.get('source'),'rule_state',{}).get('historical_chromatic_dragon')
  return game._split_fixed_summon(('summon',cid,1),ctx) if cid else (('batch30_noop',),())
 if op[0]=='historical_treasure_dice':
  first=game.rng.randint(1,6);second=game.rng.randint(1,6)
  costs=(first,second)+( (first,) if first==second else () )
  operations=tuple(discover(pool(minimum=cost,maximum=cost,classes='own_or_neutral')) for cost in costs)
  return operations[0],operations[1:]
 if op[0]=='historical_treasure_goblet':
  state={}
  return ('historical_draw_capture',None,'random',state),(('historical_treasure_fill',state),)
 if op[0]=='historical_treasure_fill':
  card=op[1].get('card')
  if card is None or len(game.players[ctx['owner']].hand)>=10:return ('batch30_noop',),()
  return ('historical_treasure_copy',op[1]),(('historical_treasure_fill',op[1]),)
 if op[0]=='historical_treasure_chest':
  require_fixed_cards(ORIGINAL,game.cards)
  return game._split_fixed_summon(('replay_context',(('historical_treasure_random',),),dict(ctx,owner=1-ctx['owner'],source=None)),ctx)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_treasure_'):return False
 owner=ctx['owner'];p=game.players[owner]
 if name=='historical_treasure_pillar':
  request=board_pool(pool(card_type='MINION',tribe='ELEMENTAL',classes='own_or_neutral'));values=game._generation_discover_candidates(request,ctx)
  if values:game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='pillar',context=dict(ctx),options=[dict(card_id=cid) for cid in game.rng.sample(list(values),min(3,len(values)))]);game.phase='choice'
 elif name=='historical_treasure_malygos':
  from .selectors import has_tribe
  if any(has_tribe(game._card_data(card),'DRAGON') for card in p.hand):
   require_fixed_cards(MALYGOS_SPELLS,game.cards)
   game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='malygos',options=[dict(card_id=cid) for cid in game.rng.sample(MALYGOS_SPELLS,3)]);game.phase='choice'
 elif name=='historical_treasure_power':
  from .historical_copy_batches import power_snapshot
  if op[1]=='upgraded':
   from .identities import canonical_identity
   identities=[canonical_identity(game._card_data(card),game.cards) for card in p.deck]
   if len(identities)!=len(set(identities)):return True
  powers=BASIC_POWERS if op[1]=='basic' else UPGRADED_POWERS;require_fixed_cards(tuple(powers.values()),game.cards)
  current=power_snapshot(game,owner)['card_id'];options=[dict(card_id=cid,hero_class=hero_class) for hero_class,cid in powers.items() if cid!=current]
  if options:
   game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='power_'+op[1],options=game.rng.sample(options,min(3,len(options))));game.phase='choice'
 elif name=='historical_treasure_suspicious_guess':
  from .historical_copy_batches import live
  source=live(game,op[1])
  if source is None or source.silenced:return True
  memories=source.rule_state.get('historical_suspicious_memory',[])
  memory=next((item for item in memories if item['uid']==op[2]),None)
  if memory is None:return True
  memories.remove(memory);options=[dict(card_id=cid) for cid in memory['options']];game.rng.shuffle(options)
  game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='suspicious_guess',answer=memory['answer'],options=options);game.phase='choice'
 elif name=='historical_treasure_ivory_copy':
  source=ctx.get('source');cid=source.rule_state.get('historical_ivory_choice') if source is not None else None
  if cid:game._add(owner,cid)
 elif name=='historical_treasure_filtered':
  from .identities import canonical_identity
  from .selectors import classes,HERO_CLASSES,shares_tribe
  mode=op[1];source=ctx.get('source');q=game.players[1-owner]
  def identity(cid):return canonical_identity(game.cards[cid],game.cards)
  if mode in ('maruut','murozond'):
   deck=p.starting_deck if mode=='maruut' else [game._card_data(c)['id'] for c in p.deck]
   ids=[identity(cid) for cid in deck]
   if len(ids)!=len(set(ids)):return True
  request=pool(card_type='SPELL',classes=q.hero_class) if mode=='hipster' else pool(card_type='SPELL',classes='any') if mode=='ivory' else pool(card_type='SPELL',classes='own_or_neutral') if mode=='importer' else board_pool(pool(card_type='MINION',tribe='ELEMENTAL',classes='own_or_neutral')) if mode=='maruut' else pool(card_type='MINION',tribe='DRAGON',classes='own_or_neutral') if mode=='murozond' else pool(card_type='MINION',classes='own_or_neutral')
  values=game._generation_discover_candidates(request,ctx)
  if mode=='hipster':
   excluded={identity(game._card_data(c)['id']) for c in q.deck};values=[cid for cid in values if identity(cid) not in excluded]
  elif mode=='importer':
   excluded={identity(cid) for cid in p.starting_deck};values=[cid for cid in values if identity(cid) not in excluded]
  elif mode=='ivory':values=[cid for cid in values if len(classes(game.cards[cid])&HERO_CLASSES)>1]
  elif mode=='amalgam':
   target=next((m for m in p.minions if m.uid==ctx.get('target')),None)
   if target is None:return True
   values=[cid for cid in values if shares_tribe(game.cards[cid],game._card_data(target))]
  if values:
   options=[dict(card_id=cid) for cid in game.rng.sample(list(values),min(3,len(values)))]
   game.pending_choice=dict(owner=owner,kind='historical_treasure',mode=mode,context=dict(ctx),options=options);game.phase='choice'
 elif name in ('historical_treasure_elysiana','historical_treasure_mystery'):

  mystery=name=='historical_treasure_mystery';request=pool(card_type='SPELL',classes='own_or_neutral') if mystery else pool(classes='own_or_neutral')
  values=game._generation_discover_candidates(request,ctx)
  if values:
   ids=game.rng.sample(list(values),min(3,len(values)));options=[dict(card_id=cid) for cid in ids]
   if mystery:options.append(dict(card_id='ULD_209',label='Mystery choice',mystery=True))
   game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='mystery' if mystery else 'elysiana',context=dict(ctx),picked=tuple(op[1]) if not mystery else (),options=options);game.phase='choice'
 elif name=='historical_treasure_pool_offer':
  values=game._generation_discover_candidates(op[1],ctx)
  if values:
   ids=game.rng.sample(list(values),min(3,len(values)))
   game.pending_choice=dict(owner=owner,kind='historical_treasure',mode=op[2],context=dict(ctx),options=[dict(card_id=cid) for cid in ids]);game.phase='choice'
 elif name=='historical_treasure_invocation':
  from .historical_condition_batches import matches
  if not matches(game,('elemental_previous',),ctx):return True
  require_fixed_cards(INVOCATIONS,game.cards)
  game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='invocation',context=dict(ctx),options=[dict(card_id=cid) for cid in INVOCATIONS]);game.phase='choice'
 elif name=='historical_treasure_offer':
  from .historical_family_batches import LACKEYS
  if op[1]=='lackey' and not any(m.card_id in LACKEYS for m in p.minions):return True
  values=MANAGER if op[1]=='manager' else ARTIFACTS if op[1]=='artifact' else ORIGINAL;require_fixed_cards(values,game.cards)
  game.pending_choice=dict(owner=owner,kind='historical_treasure',mode=op[1],options=[dict(card_id=cid) for cid in values]);game.phase='choice'
 elif name=='historical_treasure_crown':
  values=game._generation_discover_candidates(op[1],ctx)
  if values:
   game.pending_choice=dict(owner=owner,kind='historical_treasure',mode='crown',context=dict(ctx),options=[dict(card_id=cid) for cid in game.rng.sample(list(values),min(3,len(values)))]);game.phase='choice'
 elif name=='historical_treasure_copy':
  card=op[1].get('card')
  if card is not None and len(p.hand)<getattr(p,'hand_capacity',10):game._clone_hand_card(owner,card,source_owner=owner)
 elif name=='historical_treasure_random':require_fixed_cards(ORIGINAL,game.cards);game._add(owner,game.rng.choice(ORIGINAL))
 elif name=='historical_treasure_replace':
  values=game._generation_candidates(op[1],owner)
  if values:
   for i,old in enumerate(p.hand):
    card=Card(game._new_id(),game.rng.choice(values));card.cost_delta=-1;game._carry_origin(old,card);card._hand_entry_turn=getattr(old,'_hand_entry_turn',game.turn);p.hand[i]=card
   game._refresh_auras()
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_treasure':return False
 owner=choice['owner'];p=game.players[owner];cid=selected['card_id']
 if choice['mode'] in ('power_basic','power_upgraded'):
  key='basic_starting_class' if choice['mode']=='power_basic' else 'upgraded_starting_class'
  game._replace_primary_power(owner,dict(card_id=cid,cost=game.cards[cid]['cost'],**{key:selected['hero_class']}))
 elif choice['mode']=='chromatic':
  source=choice['context'].get('source')
  if source is not None:source.rule_state['historical_chromatic_dragon']=cid
 elif choice['mode']=='suspicious':
  game._discovery_result=game._add(owner,cid)
  source=choice['context'].get('source')
  if source is not None:
   memory=dict(uid=game._new_id(),answer=cid,options=tuple(option['card_id'] for option in choice['options']))
   source.rule_state.setdefault('historical_suspicious_memory',[]).append(memory)
   game._schedule_turn_effect(1-owner,'start',1,1,(('historical_treasure_suspicious_guess',source.uid,memory['uid']),),source_card_id=choice['context'].get('card_id'))
 elif choice['mode']=='suspicious_guess':
  if cid==choice['answer']:game._discovery_result=game._add(owner,cid)
 elif choice['mode'] in ('follow_fireheart','follow_hataaru'):
  from .historical_copy_batches import attach_same_turn_follow
  card=game._add(owner,cid);game._discovery_result=card
  if card is not None:
   if choice['mode']=='follow_hataaru':card.cost_delta=getattr(card,'cost_delta',0)-1
   attach_same_turn_follow(game,card,choice['context'],choice['mode'][7:])
 elif choice['mode'] in ('hipster','importer','maruut','murozond','ivory','amalgam','pillar'):
  context=choice['context'];mode=choice['mode']
  if mode in ('maruut','pillar'):
   operations=(('summon',cid,1),)+tuple(('add',option['card_id'],1) for option in choice['options'] if option['card_id']!=cid)
   game._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
  else:
   game._discovery_result=game._add(owner,cid)
   if mode=='ivory' and context.get('source') is not None:context['source'].rule_state['historical_ivory_choice']=cid
   if mode=='murozond':game._rule_events.append(('captured_effects',dict(operations=(('area_damage','other_minions',game.cards[cid].get('cost',0)),),context=context),[]))
 elif choice['mode']=='elysiana':
  picked=choice['picked']+(cid,)
  if len(picked)<5:
   game._rule_events.append(('captured_effects',dict(operations=(('historical_treasure_elysiana',picked),),context=choice['context']),[]))
  else:
   p.deck=[Card(game._new_id(),value) for value in picked for _ in range(2)]
   game.rng.shuffle(p.deck);game._log('deck_replaced',player=owner,count=len(p.deck))
 elif choice['mode']=='mystery':
  if selected.get('mystery'):
   offered={option['card_id'] for option in choice['options'] if not option.get('mystery')}
   values=[value for value in game._generation_candidates(pool(card_type='SPELL',classes='own_or_neutral'),owner) if value not in offered]
   if values:game._discovery_result=game._add(owner,game.rng.choice(values))
  else:game._discovery_result=game._add(owner,cid)
 elif choice['mode'] in ('cast','hurt','armor'):

  if choice['mode']=='cast':operations=(('cast_fixed_spell',cid,'random'),)
  else:
   game._add(owner,cid);cost=game.cards[cid].get('cost',0)
   operations=((('damage_own_hero',cost) if choice['mode']=='hurt' else ('armor',cost)),)
  game._rule_events.append(('captured_effects',dict(operations=operations,context=choice['context']),[]))
 elif choice['mode']=='invocation':game._rule_events.append(('captured_effects',dict(operations=tuple(TOKEN_RULES[cid][1]),context=choice['context']),[]))
 elif choice['mode']=='crown':game._rule_events.append(('captured_effects',dict(operations=(('summon',cid,2),),context=choice['context']),[]))
 else:
  game._add(owner,cid)
  if choice['mode']=='manager':
   cards=[Card(game._new_id(),other) for other in MANAGER if other!=cid]
   p.deck.extend(cards)
   game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,3,'shuffle',cards=cards)
 return True
