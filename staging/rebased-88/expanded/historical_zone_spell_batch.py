"""Historical full-pool transformations and physical zone movement; unvalidated."""
from engine.game import Card
from .generation_cards import pool,board_pool,random_cards
from .selectors import has_tribe,HERO_CLASSES
from .transformations import evolve_pool
from .historical_saidan import add

def op(name,*args):return ('historical_utility_zone_spell_'+name,)+args
TOKEN_RULES={
 'DMF_700':('none',[op('revolve')]),
 'VAC_324':('minion',[op('evolve_copy')]),
 'BOT_913':('none',[op('demonic_project')]),
 'BT_306':('none',[op('council')]),
 'WC_017':('none',[op('deviate')]),
 'LOOT_008':('none',[op('scream')]),
 'LOE_104':('enemy_minion',[op('entomb')]),
 'SCH_356':('none',[op('glide')]),
 'DED_005':('none',[op('parrrley')]),
 'GIL_828':('historic_beast',[('buff',3,3),op('frenzy')]),
 'WORK_004':('none',[op('espionage')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def split(game,operation,ctx):
 prefix='historical_utility_zone_spell_'
 if not operation[0].startswith(prefix):return None
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='revolve':
  captured=[(m.uid,game._card_stat(m,'cost',m.owner)) for player in game.players for m in tuple(player.minions) if m.health>0]
  return op('transform_group',tuple(captured)),()
 if name=='evolve_copy':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  request=evolve_pool(game._card_stat(target,'cost',target.owner),1)
  return op('transform_uid',target.uid,request,True),()
 if name=='glide':
  owners=(owner,1-owner) if ctx.get('outcast') else (owner,)
  ops=[]
  for side in owners:ops.extend((('replay_context',(op('shuffle_hand'),),dict(ctx,owner=side,shuffle_actor=owner)),('replay_context',(('draw',4),),dict(ctx,owner=side,shuffle_actor=owner))))
  return sequence(game,ctx,ops)
 if name=='espionage':
  operations=[random_cards(pool(classes=hero),destination='deck',set_cost=1) for hero in sorted(HERO_CLASSES) if hero!=p.hero_class]
  return sequence(game,ctx,operations+[('draw',1)])
 return None

def shuffle_minions(game,ctx,victims,recipient):
 cards=[]
 for m in victims:
  card=game._fresh_replay_card(m);game._carry_origin(m,card,copied=False,source_owner=m.owner);cards.append(card)
 for m in victims:
  game.players[m.owner].board.remove(m);game._log('remove_minion',player=m.owner,entity=m.uid,card=m.card_id)
 game._refresh_auras()
 game.players[recipient].deck.extend(cards);game.rng.shuffle(game.players[recipient].deck)
 if cards:game._record_deck_insertion(recipient,ctx['owner'],len(cards),'shuffle',cards=tuple(cards))

def execute(game,operation,ctx):
 prefix='historical_utility_zone_spell_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='transform_group':
  changes=[]
  for uid,cost in operation[1]:
   values=game._generation_candidates(board_pool(pool(card_type='MINION',minimum=cost,maximum=cost)),owner)
   if values:changes.append((uid,game.rng.choice(values)))
  for uid,cid in changes:
   target=next((m for player in game.players for m in player.minions if m.uid==uid),None)
   if target is not None:game._transform(target,cid)
 elif name=='transform_uid':
  uid,request,copy=operation[1:];target=game._force_live(uid)
  if target is not None:
   values=game._generation_candidates(request,owner)
   if values:
    result=game._transform(target,game.rng.choice(values))
    if copy and result is not None:game._summon(owner,result.card_id,copy_from=result,entry_origin='copy',entry_site='natural_talent')
 elif name in ('demonic_project','deviate'):
  request=pool(card_type='MINION',tribe='DEMON')
  for side in (owner,1-owner):
   values=[c for c in game.players[side].hand if game._card_data(c)['type']=='MINION']
   if not values:continue
   if name=='demonic_project':outcomes=game._generation_candidates(request,side)
   else:outcomes=sorted(set(game._generation_candidates(pool(card_type='MINION',tribe='PIRATE'),side))|set(game._generation_candidates(pool(card_type='MINION',mechanic='STEALTH'),side)))
   if outcomes:game._mutation_replace_card(game.rng.choice(values),game.rng.choice(outcomes))
  game._refresh_auras()
 elif name=='council':
  values=game._generation_candidates(pool(card_type='MINION',tribe='DEMON'),owner)
  if values:
   for c in tuple(p.hand):game._mutation_replace_card(c,game.rng.choice(values));add(c,'attack_bonus',2);add(c,'health_bonus',2)
   game._refresh_auras()
 elif name=='scream':shuffle_minions(game,ctx,[m for player in game.players for m in tuple(player.minions) if m.health>0],1-owner)
 elif name=='entomb':
  target=game._force_live(ctx.get('target'))
  if target is not None:shuffle_minions(game,ctx,[target],owner)
 elif name=='shuffle_hand':
  for c in tuple(p.hand):game._shuffle_hand_card(owner,c,actor=ctx.get('shuffle_actor',owner))
 elif name=='parrrley':
  q=game.players[1-owner];card=ctx.get('physical_card')
  if q.deck and card is not None:
   index=game.rng.randrange(len(q.deck));other=q.deck.pop(index)
   if isinstance(other,str):other=Card(game._new_id(),other)
   # Swapping ownership is not destruction and must not trigger Sludge.
   game._enter_hand(owner,other)
   clean=game._fresh_replay_card(card);clean.uid=card.uid;game._carry_origin(card,clean)
   q.deck.insert(index,clean);game._record_deck_insertion(1-owner,owner,1,'swap',cards=(clean,));game._refresh_auras()
 elif name=='frenzy':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   cards=[game._fresh_replay_card(target) for _ in range(3)]
   for card in cards:add(card,'attack_bonus',3);add(card,'health_bonus',3);game._carry_origin(target,card,copied=True,source_owner=target.owner)
   p.deck.extend(cards);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,3,'shuffle',cards=tuple(cards))
 else:return False
 return True

def requests_for(game,cid,owner):
 if cid in ('BOT_913','BT_306'):return {pool(card_type='MINION',tribe='DEMON')}
 if cid=='WC_017':return {pool(card_type='MINION',tribe='PIRATE'),pool(card_type='MINION',mechanic='STEALTH')}
 if cid=='WORK_004':return {pool(classes=hero) for hero in HERO_CLASSES if hero!=game.players[owner].hero_class}
 if cid=='VAC_324':
  return {evolve_pool(game._card_stat(m,'cost',m.owner),1) for player in game.players for m in player.minions if m.health>0}
 if cid=='DMF_700':
  return {board_pool(pool(card_type='MINION',minimum=game._card_stat(m,'cost',m.owner),maximum=game._card_stat(m,'cost',m.owner))) for player in game.players for m in player.minions if m.health>0}
 return set()
