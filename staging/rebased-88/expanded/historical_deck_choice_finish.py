"""Physical deck Discover, guessing and detached Deathrattle continuations."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool
from .historical_draw_batches import draw
from .historical_resurrection_batches import card_deaths
from .historical_devout import base_source
from .identities import canonical_identity
from .selectors import has_tribe
from .discover_offer import DiscoverOffer

def op(name,*args):return ('historical_utility_deck_finish_'+name,)+args
MINION=(('type','eq','MINION'),)
TOKEN_RULES={
 'DMF_075':('none',[op('guess')]),
 'GDB_451':('none',[op('offer','triangulate')]),
 'WORK_070':('none',[op('offer','soul')]),
 'TRL_339':('none',[op('offer','masters')]),
 'ONY_031':('none',[op('draw_deaths',5,None)]),
 'SW_405':('none',[op('draw_deaths',1,(('mechanic','eq','DEATHRATTLE'),('cost','le',4)))]),
 'SW_440':('none',[op('offer','grave')]),
 'WC_016':('none',[draw(MINION,'same_turn_follow',('shroud',)),draw(MINION,'same_turn_follow',('shroud',))]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def split(game,operation,ctx):
 name=operation[0]
 if name==op('guess')[0]:
  state={};return ('historical_draw_capture',None,'random',state),(op('guess_offer',state),)
 if name==op('draw_deaths')[0]:
  count,filters=operation[1:];states=[{} for _ in range(count)]
  return sequence(game,ctx,tuple(('historical_draw_capture',filters,'random',s) for s in states)+tuple(op('trigger_state',s) for s in states))
 if name==op('trigger_state')[0]:
  card=operation[1].get('card')
  if card is None or 'DEATHRATTLE' not in game._card_mechanics(card):return ('batch30_noop',),()
  return replay_death(game,ctx,card)
 if name==op('trigger_card')[0]:return replay_death(game,ctx,operation[1])
 return None

def replay_death(game,ctx,card):
 owner=ctx['owner'];data=game._card_data(card)
 if data['type']=='WEAPON':
  operations=game._printed_death_operations(card.card_id)
  context=dict(ctx,source=None,physical_card=card,card_id=card.card_id,spell=False,power=False,bonus=0,lifesteal='LIFESTEAL' in game._card_mechanics(card),poisonous='POISONOUS' in game._card_mechanics(card),target=0,death_position=len(game.players[owner].board),broken_weapon=dict(card_id=card.card_id,attack=game._card_stat(card,'attack',owner),durability=data.get('durability',data.get('health',0))),broken_weapon_card=card)
 else:
  operations=card_deaths(game,card,owner);source,definition=base_source(game,owner,card)
  context=dict(ctx,source=source,physical_card=definition,card_id=card.card_id,spell=False,power=False,bonus=0,lifesteal=False,target=0,death_position=len(game.players[owner].board))
 if not operations:return ('batch30_noop',),()
 return game._split_fixed_summon(('replay_context',operations,context),ctx)

def offer(game,ctx,mode,cards):
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite physical deck choice')
 if cards:
  game.pending_choice=dict(owner=ctx['owner'],kind='historical_deck_finish',mode=mode,context=dict(ctx),_cards=tuple(cards),options=[dict(card_id=c.card_id,slot=i) for i,c in enumerate(cards)]);game.phase='choice'

def execute(game,operation,ctx):
 prefix='historical_utility_deck_finish_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='guess_offer':
  state=operation[1]
  if state.get('card') is not None and p.deck:
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Guess the Weight choice')
   game.pending_choice=dict(owner=owner,kind='historical_weight_guess',context=dict(ctx),_cost=state['cost'],options=[dict(name='Costs more',guess='more'),dict(name='Costs less',guess='less')]);game.phase='choice'
 elif name=='offer':
  mode=operation[1]
  if mode=='grave':
   values=game._generation_discover_candidates(pool(card_type='MINION',mechanic='DEATHRATTLE',classes='own_or_neutral'),ctx)
   offer(game,ctx,mode,[Card(game._new_id(),cid) for cid in game.rng.sample(list(values),min(3,len(values)))])
  else:
   groups={};creator=canonical_identity(game.cards[ctx['card_id']],game.cards)
   for i,value in enumerate(p.deck):
    data=game._card_data(value)
    if mode=='masters' and data['type']!='MINION':continue
    if mode=='triangulate' and (data['type']!='SPELL' or canonical_identity(data,game.cards)==creator):continue
    if isinstance(value,str):value=Card(game._new_id(),value);p.deck[i]=value
    groups.setdefault(canonical_identity(data,game.cards),[]).append(value)
   keys=game.rng.sample(list(groups),min(3,len(groups)));cards=[game.rng.choice(groups[k]) for k in keys]
   if mode=='masters' and len(cards)==3 and all(has_tribe(game._card_data(c),'BEAST') for c in cards):
    state=dict(results=[],options=tuple(dict(card_id=c.card_id) for c in cards))
    ops=tuple(op('draw_uid',c.uid,state) for c in cards)+(op('publish_all',state),)
    game._rule_events.append(('captured_effects',dict(operations=ops,context=dict(ctx)),[]))
   else:offer(game,ctx,mode,cards)
 elif name=='draw_uid':
  uid,state=operation[1:];index=next((i for i,c in enumerate(p.deck) if getattr(c,'uid',None)==uid),None)
  if index is not None:state['results'].append(game._take_deck_draw(owner,index))
 elif name=='publish_all':
  state=operation[1];offer_snapshot=DiscoverOffer(owner,'historical_masters_all',0,state['options'],getattr(p.equipped_card,'uid',None),(0,1,2));game._record_discover(owner,offer_snapshot)
  for result in state['results']:game._defer_discover_followups(owner,result)
 elif name=='shuffle_copies':
  copies=[game._copy_card(operation[1],source_owner=owner) for _ in range(3)]
  p.deck.extend(copies);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,3,'shuffle',cards=tuple(copies))
 else:return False
 return True

def resolve_choice(game,choice,selected):
 owner=choice['owner'];p=game.players[owner]
 if choice['kind']=='historical_weight_guess':
  if p.deck:
   card=p.deck[-1];value=card if isinstance(card,Card) else Card(0,card);cost=game._cost(value,owner)
   if cost>choice['_cost'] and selected['guess']=='more' or cost<choice['_cost'] and selected['guess']=='less':
    game._rule_events.append(('captured_effects',dict(operations=(('draw',1),),context=dict(choice['context'])),[]))
  return True
 if choice['kind']!='historical_deck_finish':return False
 mode=choice['mode'];ctx=choice['context'];card=choice['_cards'][selected['slot']]
 if mode=='grave':
  enough=p.mana>=game._cost(card,owner);game._discovery_result=game._enter_hand(owner,card)
  if enough:game._rule_events.append(('captured_effects',dict(operations=(op('trigger_card',card),),context=dict(ctx)),[]))
 else:
  index=next((i for i,c in enumerate(p.deck) if c is card),None)
  if index is not None:
   snapshot=game._copy_card(card,source_owner=owner);game._discovery_result=game._take_deck_draw(owner,index)
   if mode=='triangulate':game._rule_events.append(('captured_effects',dict(operations=(op('shuffle_copies',snapshot),),context=dict(ctx)),[]))
   elif mode=='soul' and p.corpses>=5:
    game._spend_corpses(owner,5);game._enter_hand(owner,game._copy_card(snapshot,source_owner=owner))
 return True
