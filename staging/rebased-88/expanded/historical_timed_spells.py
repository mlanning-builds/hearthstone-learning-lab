"""Timed generated spell effects with explicit owner-turn expiry state."""
from .generation_cards import pool,random_cards
from .selectors import has_tribe,has_school
TOKEN_RULES={
 'JAM_006':('none',[('historical_copy_timed_cost','MINION',5,None,'enemy')]),
 'MAW_026':('minion',[('historical_event_sleep_target',3)]),
 'REV_504':('none',[('historical_timed_alibi',)]),
 'TTN_854':('none',[('historical_timed_inventor',)]),
 'TOY_808':('none',[('schedule_turn_effect','end',0,3,(random_cards(pool(card_type='MINION',minimum=6,maximum=6),destination='board'),))]),
 'MAW_024':('none',[('historical_timed_dew',)]),
 'TTN_830':('none',[('draw',1),('historical_timed_lightning',)]),
 'RLK_923':('none',[('hero_attack',3),('historical_timed_feast',)]),
 'MAW_021':('friendly_minion',[('buff',2,3),('historical_timed_elusive',)]),
 'TTN_726':('character',[('historical_timed_tar',),('damage',1)]),
 'ETC_335':('none',[('historical_timed_love',)]),
}
TOKEN_RULES.update({
 'TOY_529':('none',[('historical_copy_destroy_deck',),('historical_timed_wheel',)]),
 'TID_718':('none',[('historical_timed_immolate',)]),
})
TOKEN_RULES.update({
 'TTN_486':('friendly_minion',[('historical_timed_form',)]),
 'TTN_079':('minion',[('buff',2,0),('historical_timed_jormungar',)]),
})
TOKEN_RULES['WW_341']=('none',[('historical_timed_deputization',)])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def cost(game,card,owner,value):
 p=game.players[owner];data=game._card_data(card)
 if data['type']=='MINION' and has_tribe(data,'MECHANICAL'):value-=len(getattr(p,'historical_inventor_auras',()))
 if data['type']=='SPELL':
  paid=getattr(p,'historical_paid_spell_turn',{})
  if paid.get('turn')!=game.turn or paid.get('count',0)==0:value-=2*getattr(p,'historical_love_stacks',0)
  if has_school(data,'NATURE'):value-=sum(e['amount'] for e in getattr(p,'historical_lightning_discounts',()) if e['owner_turn']==p.turns_taken)
 return value


def paid(game,owner,card):
 if game._card_data(card)['type']!='SPELL':return
 p=game.players[owner];state=getattr(p,'historical_paid_spell_turn',{})
 if state.get('turn')!=game.turn:state=dict(turn=game.turn,count=0)
 state['count']+=1;p.historical_paid_spell_turn=state


def turn_entries(game,phase):
 owner=game.current;p=game.players[owner];entries=[]
 if phase=='start':
  for player in game.players:
   for minion in player.all_minions:
    for effect in minion.rule_state.get('historical_monstrous_forms',()):
     if effect['owner']==owner and effect['due']<=p.turns_taken:entries.append(dict(source=None,order=effect['uid'],card_id='TTN_486',operations=(('historical_timed_form_expire',minion.uid,effect['uid']),)))
  for uid in getattr(game,'historical_dew_sources',()):entries.append(dict(source=None,order=uid,card_id='MAW_024',operations=(('draw',1),)))
 if phase=='end':
  from .historical_demon_portal import PortalDeck
  if isinstance(p.deck,PortalDeck):entries.append(dict(source=None,order=0,card_id='GDB_145',operations=(('historical_utility_portal_grow',),)))
  for effect in getattr(p,'historical_deputization_auras',()):
   if effect['until']<=p.turns_taken:entries.append(dict(source=None,order=effect['uid'],card_id='WW_341',operations=(('historical_timed_deputization_expire',effect['uid']),)))
  for card in tuple(p.hand):
   burns=getattr(card,'rule_state',{}).get('historical_immolate',())
   if any(e['owner']==owner and e['due']<=p.turns_taken for e in burns):entries.append(dict(source=None,order=card.uid,card_id='TID_718',operations=(('historical_timed_immolate_burn',card.uid),)))
  for effect in getattr(p,'historical_inventor_auras',()):
   if effect['until']<=p.turns_taken:entries.append(dict(source=None,order=effect['uid'],card_id='TTN_854',operations=(('historical_timed_inventor_expire',effect['uid']),)))
  if getattr(p,'historical_love_stacks',0):entries.append(dict(source=None,order=getattr(p,'historical_love_uid',0),card_id='ETC_335',operations=(('historical_timed_love_expire',),)))
 return entries


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_timed_deputization':
  duration=3+getattr(ctx.get('physical_card'),'rule_state',{}).get('aura_duration_delta',0)
  if duration>0:p.historical_deputization_auras=getattr(p,'historical_deputization_auras',[])+[dict(uid=game._new_id(),until=p.turns_taken+duration-1)]
  game._refresh_auras()
 elif name=='historical_timed_deputization_expire':
  p.historical_deputization_auras=[e for e in getattr(p,'historical_deputization_auras',()) if e['uid']!=op[1]]
  game._refresh_auras()
 elif name=='historical_timed_form':
  target=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is not None:
   before_attack=target.attack+target.attack_deficit;before_health=target.max_health
   game._buff(target,3,3)
   target.rule_state.setdefault('historical_monstrous_forms',[]).append(dict(uid=game._new_id(),owner=owner,due=p.turns_taken+1,attack=target.attack+target.attack_deficit-before_attack,health=target.max_health-before_health))
 elif name=='historical_timed_form_expire':
  target=next((m for player in game.players for m in player.all_minions if m.uid==op[1] and m.health>0),None)
  if target is not None:
   effects=target.rule_state.get('historical_monstrous_forms',[])
   effect=next((e for e in effects if e['uid']==op[2]),None)
   if effect is not None:
    effects.remove(effect);game._adjust_minion_attack(target,-effect['attack'])
    target.max_health-=effect['health'];target.health=min(target.health,target.max_health);game._refresh_auras()
 elif name=='historical_timed_jormungar':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is not None:target.rule_state['historical_jormungar']=target.rule_state.get('historical_jormungar',0)+1
 elif name=='historical_timed_wheel':
  game._schedule_turn_effect(owner,'start',5,1,(('historical_timed_wheel_destroy',),),source_card_id='TOY_529')
 elif name=='historical_timed_wheel_destroy':
  game.players[1-owner].health=0
  game._log('destroy_hero',player=1-owner,source='TOY_529')
 elif name=='historical_timed_immolate':
  other=1-owner;q=game.players[other]
  for card in tuple(q.hand):game._b60_state(card).setdefault('historical_immolate',[]).append(dict(owner=other,due=q.turns_taken+3))
 elif name=='historical_timed_immolate_burn':
  card=next((c for c in p.hand if c.uid==op[1]),None)
  if card is not None and any(e['owner']==owner and e['due']<=p.turns_taken for e in getattr(card,'rule_state',{}).get('historical_immolate',())):
   p.hand.remove(card);game._zone_card_removed(owner,card,'hand','destroy');game._log('destroy_hand_card',player=owner,card=game._card_data(card)['id']);game._refresh_auras()
 elif name=='historical_timed_alibi':p.historical_alibi_until=max(getattr(p,'historical_alibi_until',-1),p.turns_taken+1)
 elif name=='historical_timed_inventor':
  duration=2+getattr(ctx.get('physical_card'),'rule_state',{}).get('aura_duration_delta',0)
  if duration>0:p.historical_inventor_auras=getattr(p,'historical_inventor_auras',[])+[dict(uid=game._new_id(),until=p.turns_taken+duration-1)]
 elif name=='historical_timed_inventor_expire':p.historical_inventor_auras=[e for e in getattr(p,'historical_inventor_auras',()) if e['uid']!=op[1]]
 elif name=='historical_timed_dew':game.historical_dew_sources=getattr(game,'historical_dew_sources',[])+[game._new_id()]
 elif name=='historical_timed_lightning':p.historical_lightning_discounts=getattr(p,'historical_lightning_discounts',[])+[dict(owner_turn=p.turns_taken+1,amount=1)]
 elif name=='historical_timed_feast':
  if p.max_mana>=4:p.hero_lifesteal_until=max(p.hero_lifesteal_until,game.turn)
 elif name=='historical_timed_elusive':
  target=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is not None:target.rule_state['historical_opponent_elusive']=True
 elif name=='historical_timed_tar':
  state=getattr(game,'historical_tar_slick',{})
  if state.get('turn')!=game.turn:state=dict(turn=game.turn,layers=0)
  state['layers']+=1;game.historical_tar_slick=state
 elif name=='historical_timed_love':
  p.historical_love_stacks=getattr(p,'historical_love_stacks',0)+1;p.historical_love_uid=game._new_id()
 elif name=='historical_timed_love_expire':
  state=getattr(p,'historical_paid_spell_turn',{})
  if state.get('turn')!=game.turn or not state.get('count'):p.historical_love_stacks=0
 else:return False
 return True


def deputization_layers(game,minion):
 p=game.players[minion.owner]
 first=next((m for m in p.minions if m.health>0),None)
 return len(getattr(p,'historical_deputization_auras',())) if minion is first else 0
