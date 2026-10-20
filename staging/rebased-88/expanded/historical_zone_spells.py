"""Explicit physical draw, deck and recruitment spell outcomes; unvalidated."""
from .generation_cards import pool,random_cards
from .selectors import has_tribe
TOKEN_RULES={
 'TOY_352':('none',[('historical_zone_fetch','BEAST')]),
 'TOY_510':('none',[('historical_zone_fetch','PIRATE')]),
 'MIS_301':('none',[('summon','MIS_301t',1),('historical_zone_treant_draw',)]),
 'MIS_301t':('none',[]),
 'MIS_902':('none',[('historical_zone_scrapper',)]),
 'DEEP_028':('none',[('historical_zone_cluster',)]),
 'DEEP_028t':('none',[]),
 'DEEP_031':('character',[('damage',6),random_cards(pool(card_type='MINION',minimum=6,maximum=6),destination='board'),('historical_zone_destroy_bottom',6)]),
 'MAW_015':('none',[('summon','CS2_101t',2),('historical_zone_recruits_buff',)]),
 'WW_053':('none',[('historical_zone_tram_heist',)]),
 'TSC_079':('none',[('historical_zone_radar',)]),
 'TOY_602':('none',[('historical_zone_spill',)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_zone_fetch':
  state={}
  return ('historical_draw_capture',(('type','eq','MINION'),),'random',state),(('historical_zone_fetch_finish',op[1],state),)
 if name=='historical_zone_fetch_finish':
  card=op[2].get('card')
  if card is None or not has_tribe(game._card_data(card),op[1]):return ('batch30_noop',),()
  return (('historical_draw_capture',(('type','eq','SPELL'),),'random',{}),()) if op[1]=='BEAST' else (('add','GAME_005',1),())
 if name=='historical_zone_treant_draw':
  from .historical_tribal_batches import TREANTS
  return ('draw',sum(m.card_id in TREANTS for m in p.minions)),()
 if name=='historical_zone_cluster':
  count=max(0,min(3,p.mana_capacity-p.max_mana))
  return ('historical_zone_empty_crystals',count),(('summon','DEEP_028t',3-count),)
 if name=='historical_zone_tram_heist':
  records=[r for r in getattr(game.players[1-owner],'_historical_paid_card_records',()) if r['turn']==game.turn-1]
  operations=tuple(('add',r['card_id'],1) for r in records)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_zone_radar':
  uids=tuple(card.uid for card in p.deck[:5] if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'MECHANICAL'))
  operations=tuple(('historical_zone_draw_uid',uid) for uid in uids)+(('historical_zone_shuffle_deck',),)
  return operations[0],operations[1:]
 if name=='historical_zone_spill':
  cards=[card for card in p.hand if game._card_data(card)['type']=='MINION']
  if not cards or len(p.board)>=7:return ('batch30_noop',),()
  highest=max(game._cost(card,owner) for card in cards);card=game.rng.choice([card for card in cards if game._cost(card,owner)==highest]);state={}
  return ('historical_zone_recruit_uid',card.uid,state),(('historical_zone_spill_damage',state),)
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_zone_scrapper':
  amount=min(5,p.armor);p.armor-=amount
  if amount:p.cost_effects.append(dict(selector='MECHANICAL',amount=amount,remaining_uses=1,expires=None))
  game._refresh_auras()
 elif name=='historical_zone_empty_crystals':p.max_mana=min(p.mana_capacity,p.max_mana+op[1])
 elif name=='historical_zone_destroy_bottom':
  for _ in range(min(op[1],len(p.deck))):
   card=p.deck.pop(0);game._zone_card_removed(owner,card,'deck','destroy')
  game._refresh_auras()
 elif name=='historical_zone_recruits_buff':
  from .identities import canonical_identity
  identity=canonical_identity(game.cards['CS2_101t'],game.cards)
  for minion in p.minions:
   if canonical_identity(game._card_data(minion),game.cards)==identity:game._buff(minion,1,1)
 elif name=='historical_zone_draw_uid':
  index=next((i for i,card in enumerate(p.deck) if card.uid==op[1]),None)
  if index is not None:game._take_deck_draw(owner,index,include_burned=True)
 elif name=='historical_zone_shuffle_deck':game.rng.shuffle(p.deck)
 elif name=='historical_zone_recruit_uid':
  card=next((card for card in p.hand if card.uid==op[1]),None)
  if card is not None and len(p.board)<7:
   p.hand.remove(card)
   minion=game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='recruit',entry_site='chemical_spill',entry_zone='hand',entry_source=card)
   op[2]['uid']=getattr(minion,'uid',None);game._refresh_auras()
 elif name=='historical_zone_spill_damage':
  uid=op[1].get('uid')
  if uid is not None and any(m.uid==uid and m.health>0 for player in game.players for m in player.minions):game._deal_effect(uid,5,ctx)
 else:return False
 return True
