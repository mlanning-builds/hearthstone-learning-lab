"""Historical physical-deck spell programs; behavioral validation deferred."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,board_pool,random_cards
from .identities import canonical_identity
from .pools import deck_choice_options

def op(name,*args):return ('historical_utility_mage_deck_'+name,)+args
TOKEN_RULES={
 'AV_290':('none',[op('tower')]),
 'LOOT_172':('none',[op('fury')]),
 'DMF_108':('none',[op('lunacy')]),
 'VAC_431':('none',[op('sea')]),
 'WORK_026':('none',[op('burndown')]),
 'DED_002':('none',[op('moonlit')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def different_spells(game,owner,cid):
 identity=canonical_identity(game.cards[cid],game.cards)
 return [(i,c) for i,c in enumerate(game.players[owner].deck) if game._card_data(c)['type']=='SPELL' and canonical_identity(game._card_data(c),game.cards)!=identity]

def split(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('tower_cast')[0]:
  candidates=different_spells(game,owner,'AV_290')
  missing=[game._card_data(c)['id'] for _,c in candidates if not game._supports_internal_spell(game._card_data(c)['id'],owner)]
  if missing:raise UnsupportedCard('Iceblood Tower deck spell programs incomplete: '+', '.join(sorted(set(missing))))
  if not candidates:return ('batch30_noop',),()
  index,value=game.rng.choice(candidates);card=value if isinstance(value,Card) else Card(game._new_id(),value)
  p.deck.pop(index);game._refresh_auras()
  return game._cast_spell_split(('cast_physical_spell',card,'random'),ctx)
 if name==op('sea')[0]:
  ids=tuple(sorted({game._card_data(c)['id'] for _,c in different_spells(game,owner,'VAC_431')}))
  if not ids:return ('batch30_noop',),()
  # Resolve every possible downstream summon before drawing/sampling.
  for _,card in different_spells(game,owner,'VAC_431'):
   cost=game._cost(card if isinstance(card,Card) else Card(0,card),owner)
   game._generation_candidates(board_pool(pool(card_type='MINION',minimum=cost,maximum=cost)),owner)
  state={}
  return ('historical_draw_capture',(('type','eq','SPELL'),('id','in',ids)),'random',state),(op('sea_summon',state),)
 if name==op('sea_summon')[0]:
  state=operation[1]
  if state.get('card') is None:return ('batch30_noop',),()
  cost=state['cost']
  return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=cost,maximum=cost),destination='board'),ctx)
 if name==op('burndown')[0]:
  states=[{} for _ in range(3)]
  operations=tuple(x for state in states for x in (('historical_draw_capture',None,'random',state),op('ignite_hand',state)))
  return operations[0],operations[1:]
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_mage_deck_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='tower':game._schedule_turn_effect(owner,'end',0,3,(op('tower_cast'),),source_card_id='AV_290')
 elif name=='fury':
  cards=[c for c in p.deck if game._card_data(c)['type']=='SPELL']
  if cards:
   card=game.rng.choice(cards);cost=game._cost(card if isinstance(card,Card) else Card(0,card),owner)
   game._log('reveal',player=owner,card=game._card_data(card)['id'],source='LOOT_172')
   game._effect(('area_damage','all_minions',cost),ctx)
 elif name=='ignite_hand':
  card=operation[1].get('card')
  if card is not None and card in p.hand:
   game._b60_state(card).setdefault('historical_immolate',[]).append(dict(owner=owner,due=p.turns_taken+3-int(owner==game.current)))
 elif name=='lunacy':
  replacements=[]
  for i,value in enumerate(p.deck):
   if game._card_data(value)['type']!='SPELL':continue
   card=value if isinstance(value,Card) else Card(0,value);cost=game._cost(card,owner);target=min(10,cost+3)
   candidates=game._generation_created_candidates(pool(card_type='SPELL',minimum=target,maximum=target),ctx)
   replacements.append((i,value,cost,candidates))
  # Full membership has been established for every deck spell before RNG.
  for i,value,cost,candidates in replacements:
   if not candidates:continue
   card=value if isinstance(value,Card) else Card(game._new_id(),value)
   game._b60_transform_card(card,game.rng.choice(candidates));game._set_card_cost(card,cost);p.deck[i]=card
  game._refresh_auras()
 elif name=='moonlit':
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Moonlit Guidance Discover')
  for i,value in enumerate(p.deck):
   if not isinstance(value,Card):p.deck[i]=Card(game._new_id(),value)
  options=deck_choice_options(p.deck,game.cards,3,game.rng)
  for option in options:option['uid']=p.deck[option['index']].uid
  if options:
   game.pending_choice=dict(owner=owner,kind='historical_mage_deck_discover',context=dict(ctx),options=options)
   game.phase='choice'
 else:return False
 return True

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_mage_deck_discover':return False
 owner=choice['owner'];p=game.players[owner]
 original=next((c for c in p.deck if c.uid==selected['uid']),None)
 if original is not None:
  card=game._copy_card(original,source_owner=owner)
  card._follow_effects=getattr(card,'_follow_effects',[])+[dict(card_id='DED_002',source_card_id='DED_002',historical_mode='moonlit',deck_uid=original.uid,end=game.turn)]
  game._discovery_result=game._enter_hand(owner,card)
 return True
