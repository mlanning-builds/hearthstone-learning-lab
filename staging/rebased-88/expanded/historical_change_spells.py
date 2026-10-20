"""Historical full-pool transformations and physical card/death-state effects."""
from copy import deepcopy
from dataclasses import replace
from engine.cards import UnsupportedCard
from .generation_cards import pool
from .transformations import evolve_pool
from .identities import canonical_identity
from .selectors import has_tribe
from .historical_saidan import add as add_stat
TOKEN_RULES={
 'TSC_209':('none',[('historical_change_whirlpool',)]),
 'MIS_701':('none',[('historical_change_nostalgia',pool(era='past',card_type='MINION',rarity='LEGENDARY',excluded_mechanic='COLOSSAL'))]),
 'REV_924':('none',[('historical_change_wave',)]),
 'TTN_485':('none',[('historical_change_align',)]),
 'NX2_008':('minion',[('historical_change_blazing',)]),
 'REV_240':('none',[('historical_change_tampering',)]),
 'MAW_012':('none',[('historical_change_demons',1)]),
 'MAW_012t':('none',[('historical_change_demons',3)]),
 'WW_811':('none',[('historical_change_hat',)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def live(game,uid):return next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name in ('historical_change_nostalgia','historical_change_wave'):
  states=[]
  for player in game.players:
   for minion in player.minions:
    if minion.health<=0 or game._fire_immune_target(minion.uid,ctx):continue
    if name=='historical_change_nostalgia':request=op[1]
    else:
     cost=game._card_stat(minion,'cost',minion.owner)
     if cost==0 and minion.owner!=owner:continue
     request=evolve_pool(cost,1 if minion.owner==owner else -1)
    values=game._generation_created_candidates(request,ctx)
    states.append((minion.uid,values))
  operations=tuple(('historical_change_board_one',uid,values) for uid,values in states)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_change_align':
  operations=[]
  for card in p.hand:
   if game._card_data(card)['type']!='MINION':continue
   request=evolve_pool(game._card_stat(card,'cost',owner),3,board=False)
   values=game._generation_created_candidates(request,ctx)
   operations.append(('historical_change_hand_one',card.uid,values,game._cost(card,owner)))
  return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())
 if name=='historical_change_tampering':return ('historical_change_shuffle_hand',),(('historical_change_discard_hand',),)
 if name=='historical_change_demons':
  records=[record for record in p.death_records if has_tribe(game._card_data(record['entity']),'DEMON')]
  selected=game.rng.sample(records,min(op[1],len(records)))
  operations=tuple(('historical_change_resurrect',game._fresh_replay_card(record['entity'])) for record in selected)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_change_hat':
  state={}
  return ('historical_draw_capture',(('type','eq','MINION'),),'random',state),(('historical_change_hat_finish',state),)
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_change_whirlpool':
  victims=[m for player in game.players for m in player.minions if m.health>0 and not game._fire_immune_target(m.uid,ctx)]
  identities={canonical_identity(game._card_data(m),game.cards) for m in victims}
  for victim in victims:victim.health=0
  for recipient,player in enumerate(game.players):
   for zone_name in ('hand','deck'):
    zone=getattr(player,zone_name)
    for card in tuple(zone):
     if canonical_identity(game._card_data(card),game.cards) in identities:
      zone.remove(card);game._zone_card_removed(recipient,card,zone_name,'destroy')
  game._refresh_auras()
 elif name=='historical_change_board_one':
  victim=live(game,op[1])
  if victim is not None and op[2]:game._transform(victim,game.rng.choice(op[2]))
 elif name=='historical_change_hand_one':
  card=next((card for card in p.hand if card.uid==op[1]),None)
  if card is not None and op[2]:game._b60_transform_card(card,game.rng.choice(op[2]));game._set_card_cost(card,op[3])
 elif name=='historical_change_blazing':
  target=live(game,ctx.get('target'))
  if target is None:return True
  request=replace(evolve_pool(game._card_stat(target,'cost',target.owner),1),classes='own_or_neutral')
  values=game._generation_discover_candidates(request,ctx)
  if values:
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite transformation Discover')
   game.pending_choice=dict(owner=owner,kind='historical_change_transform',target=target.uid,options=[dict(card_id=cid) for cid in game.rng.sample(list(values),min(3,len(values)))])
   game.phase='choice'
 elif name=='historical_change_shuffle_hand':
  cards=[]
  for original in tuple(p.hand):
   card=game._copy_card(original,source_owner=owner);game._set_card_cost(card,1);cards.append(card)
  p.deck.extend(cards);game.rng.shuffle(p.deck)
  if cards:game._record_deck_insertion(owner,owner,len(cards),'shuffle',cards=tuple(cards))
 elif name=='historical_change_discard_hand':game._discard_cards(owner,list(p.hand))
 elif name=='historical_change_resurrect':
  card=op[1];game._summon(owner,card.card_id,entry_source=card,entry_zone='deck',entry_origin='resurrection',entry_site='all_fel_breaks_loose')
 elif name=='historical_change_hat_finish':
  card=op[1].get('card')
  if card is not None:
   add_stat(card,'attack_bonus',1);add_stat(card,'health_bonus',1)
   game._b60_state(card).setdefault('historical_granted_deaths',[]).append(('add','WW_811',1))
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_change_transform':return False
 target=live(game,choice['target'])
 if target is not None:game._transform(target,selected['card_id'])
 return True
