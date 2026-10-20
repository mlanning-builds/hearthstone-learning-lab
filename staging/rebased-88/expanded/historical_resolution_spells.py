"""Captured destruction, damage, healing and physical movement spell programs."""
from .selectors import has_tribe
from .historical_saidan import add as add_stat
TOKEN_RULES={
 'DEEP_013':('none',[('area_damage','all_minions',2),('schedule_turn_effect','start',1,1,(('area_damage','all_minions',2),))]),
 'DEEP_032':('minion',[('historical_resolution_soulfreeze',)]),
 'ETC_069':('none',[('historical_resolution_crescendo',)]),
 'REV_248':('minion',[('buff',0,2),('historical_resolution_kyrian',)]),
 'REV_248t':('none',[]),
 'RLK_537':('minion',[('historical_resolution_tether',)]),
 'TTN_460':('none',[('historical_resolution_eradication',)]),
 'WW_377':('enemy_minion',[('historical_resolution_heat_wave',)]),
 'JAM_025':('minion',[('historical_resolution_funnel',)]),
 'TID_920':('enemy_minion',[('historical_resolution_drown',)]),
 'MAW_013':('minion',[('historical_resolution_sentence',)]),
 'REV_840':('none',[('historical_resolution_deathborne',)]),
 'TTN_463':('none',[('historical_resolution_weld',)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def live(game,uid):return next((m for p in game.players for m in p.minions if m.uid==uid and m.health>0),None)

def neighbors(game,target):
 if target is None:return ()
 board=game.players[target.owner].board;index=board.index(target)
 return tuple(m.uid for i,m in enumerate(board) if abs(i-index)<=1 and m in game.players[target.owner].minions and m.health>0)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0];target=live(game,ctx.get('target'))
 if name=='historical_resolution_tether':
  if target is None:return ('batch30_noop',),()
  state=dict(uid=target.uid,stats=(target.attack,target.health))
  return ('destroy',),(('historical_resolution_tether_buff',state),)
 if name=='historical_resolution_crescendo':
  state={}
  return ('historical_resolution_fatigue',state),(('historical_resolution_fatigue_area',state),)
 if name=='historical_resolution_fatigue_area':return ('area_damage','enemies',op[1]['amount']),()
 if name=='historical_resolution_eradication':
  state=dict(lethal=[]);count=max(0,5+ctx.get('bonus',0))
  if ctx.get('spell'):count*=game._spell_multiplier(owner)
  operations=tuple(('historical_resolution_missile',state) for _ in range(count))+(('historical_resolution_kill_reward','heal',state),)
  return operations[0],operations[1:]
 if name=='historical_resolution_heat_wave':
  if getattr(ctx.get('physical_card'),'_hand_entry_turn',None)==game.turn:return ('area_damage','enemies',2),()
  return ('historical_resolution_damage_uids',neighbors(game,target),2,{}),()
 if name=='historical_resolution_funnel':
  operations=tuple(('historical_resolution_funnel_heal',uid) for uid in neighbors(game,target))
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_resolution_deathborne':
  state=dict(lethal=[]);uids=tuple(m.uid for player in game.players for m in player.minions if m.health>0)
  return ('historical_resolution_damage_uids',uids,2,state),(('historical_resolution_kill_reward','skeleton',state),)
 if name=='historical_resolution_weld':
  if not p.hand:return ('batch30_noop',),()
  cost=max(game._cost(card,owner) for card in p.hand);card=game.rng.choice([card for card in p.hand if game._cost(card,owner)==cost])
  return ('historical_resolution_discard_uid',card.uid),(('area_damage','all_minions',cost),)
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0];target=live(game,ctx.get('target'))
 if name=='historical_resolution_soulfreeze':
  count=0
  for uid in neighbors(game,target):
   minion=live(game,uid)
   if minion is not None:
    game._freeze(uid)
    if minion.frozen_until>=0:count+=1
  if count:game._deal_effect(game.hero_id(owner),count,ctx)
 elif name=='historical_resolution_fatigue':
  p.fatigue+=1;op[1]['amount']=p.fatigue
  game._damage(game.hero_id(owner),p.fatigue,damage_source=None,damage_owner=owner,damage_cause='fatigue')
 elif name=='historical_resolution_kyrian':
  if target is not None:game._summon(owner,'REV_248t',entry_stats=(target.attack,target.health),entry_origin='effect',entry_site='boon_of_the_ascended')
 elif name=='historical_resolution_tether_buff':
  if not any(record['entity'].uid==op[1]['uid'] for player in game.players for record in player.death_records):return True
  cards=[card for card in p.hand if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'UNDEAD')]
  if cards:
   card=game.rng.choice(cards);add_stat(card,'attack_bonus',op[1]['stats'][0]);add_stat(card,'health_bonus',op[1]['stats'][1])
 elif name=='historical_resolution_missile':
  values=[m for m in game.players[1-owner].minions if m.health>0]
  if values:
   minion=game.rng.choice(values);game._deal_effect(minion.uid,1,dict(ctx,bonus=0,spell_multiplier_applied=True))
   if minion.health<=0:op[1]['lethal'].append(minion.uid)
 elif name=='historical_resolution_damage_uids':
  with game._damage_batch():
   for uid in op[1]:
    minion=live(game,uid)
    if minion is not None:
     game._deal_effect(uid,op[2],ctx)
     if minion.health<=0:op[3].setdefault('lethal',[]).append(uid)
 elif name=='historical_resolution_kill_reward':
  dead={record['entity'].uid for player in game.players for record in player.death_records}
  count=len(set(op[2]['lethal']) & dead)
  if op[1]=='heal':game._heal(game.hero_id(owner),2*count,healer=owner,spell=ctx.get('spell',False))
  elif count:game._effect(('summon','REV_845',count),ctx)
 elif name=='historical_resolution_funnel_heal':
  minion=live(game,op[1])
  if minion is not None:
   receipt={};game._heal(minion.uid,3,healer=owner,spell=ctx.get('spell',False),_receipt=receipt)
   if receipt.get('overheal',0)>0:game._effect(('refresh_mana',1),ctx)
 elif name in ('historical_resolution_drown','historical_resolution_sentence'):
  if target is not None and not game._fire_immune_target(target.uid,ctx):
   card=game._fresh_replay_card(target) if name=='historical_resolution_drown' else None
   game.players[target.owner].board.remove(target);game._pending_summon_events.pop(target.uid,None)
   if card is not None:
    p.deck.insert(0,card);game._record_deck_insertion(owner,owner,1,'bottom',cards=(card,))
   else:game._log('remove_from_game',player=target.owner,entity=target.uid,card=target.card_id)
   game._refresh_auras()
 elif name=='historical_resolution_discard_uid':
  card=next((card for card in p.hand if card.uid==op[1]),None)
  if card is not None:game._discard_cards(owner,[card])
 else:return False
 return True
