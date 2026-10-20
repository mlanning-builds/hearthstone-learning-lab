"""Persistent spell grants and resumable physical copy/attack programs."""
from copy import deepcopy
from .generation_cards import pool,random_cards
from .selectors import has_tribe,has_school
TOKEN_RULES={
 'ETC_367':('none',[('historical_lingering_melomania',)]),
 'RLK_823':('none',[('historical_lingering_allies',)]),
 'ETC_330':('none',[('hero_divine_shield',),('historical_lingering_groove',)]),
 'REV_506':('enemy_minion',[('historical_lingering_brand',)]),
 'JAM_031':('minion',[('historical_lingering_reverberations',)]),
 'MIS_714':('enemy_minion',[('historical_lingering_copy_attack','original',False)]),
 'TOY_603':('historical_friendly_mech',[('historical_lingering_copy_attack','enemy',True)]),
 'RLK_911':('none',[('historical_lingering_hand_copies',)]),
}
TOKEN_RULES.update({cid:('minion',[('historical_lingering_accusation',kind)]) for cid,kind in (('MAW_001','arson'),('MAW_019','murder'),('MAW_023','theft'))})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
SHAMAN_SPELLS=pool(card_type='SPELL',classes='SHAMAN')


def find(game,uid):return next((m for player in game.players for m in player.minions if m.uid==uid),None)


def event(game,kind,data):
 accusation_event(game,kind,data)
 if kind=='minion_played':
  owner=data['owner'];p=game.players[owner];minion=find(game,data['source']);operations=[]
  if has_tribe(game._event_card_data(data),'ELEMENTAL'):
   p.historical_elementals_played=getattr(p,'historical_elementals_played',0)+1
   from .historical_held_upgrades import progress
   progress(game,owner,'ruby',1)
  if minion is not None and minion.health>0 and getattr(p,'historical_allies_turn',None)==game.turn and has_tribe(game._card_data(minion),'UNDEAD'):minion.keywords.add('REBORN')
  stampede=getattr(p,'historical_stampede',{})
  if stampede.get('turn')==game.turn and has_tribe(game._event_card_data(data),'BEAST'):
   operations.extend(random_cards(pool(card_type='MINION',tribe='BEAST')) for _ in range(stampede.get('count',0)))
  state=getattr(p,'historical_melomania',{})
  if state.get('turn')==game.turn:operations.extend(random_cards(SHAMAN_SPELLS) for _ in range(state.get('count',0)))
  if operations:game._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='ETC_367')),[]))
 if kind=='damage' and data.get('target',0)>0 and data.get('amount',0)>0:
  minion=find(game,data['target'])
  if minion is None:return
  for owner in tuple(minion.rule_state.get('historical_sinful_brands',())):
   game._rule_events.append(('captured_effects',dict(operations=(('damage_enemy_hero',1),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='REV_506')),[]))
  if minion.rule_state.get('historical_reverberation_fragile'):
   game._rule_events.append(('captured_effects',dict(operations=(('historical_lingering_kill_uid',minion.uid),),context=dict(owner=minion.owner,source=None,target=0,bonus=0,lifesteal=False,card_id='JAM_031')),[]))


def paid(game,owner,card):
 p=game.players[owner]
 if game._copied_from_opponent(card,owner):accusation_event(game,'historical_opponent_copy_played',dict(owner=owner))
 if getattr(p,'historical_starlight_groove',False) and game._card_data(card)['type']=='SPELL' and has_school(game._card_data(card),'HOLY'):p.divine_shield=True


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name in ('historical_lingering_copy_attack','historical_lingering_reverberations'):
  target=find(game,ctx.get('target'))
  if target is None or target.health<=0:return ('batch30_noop',),()
  state=dict(summoned=[],mode='random_enemy_character')
  mode=op[1] if name=='historical_lingering_copy_attack' else 'fragile';kill=op[2] if name=='historical_lingering_copy_attack' else False
  operations=[('historical_lingering_copy_board',deepcopy(target),state,mode)]
  if mode=='original':operations.append(('historical_lingering_attack_original',state,target.uid))
  elif mode=='enemy':operations.append(('force_group_attacks',state))
  if kill:operations.append(('historical_lingering_kill_copies',state))
  return operations[0],tuple(operations[1:])
 if name=='historical_lingering_hand_copies':
  cards=[game._copy_card(card,source_owner=owner) for card in p.hand if game._card_data(card)['type']=='MINION']
  if not cards:return ('batch30_noop',),()
  state=dict(summoned=[],mode='random_enemy_minion')
  operations=tuple(('historical_lingering_copy_hand',card,state) for card in cards)+(('force_group_attacks',state),('historical_lingering_kill_copies',state))
  return operations[0],operations[1:]
 if name=='historical_lingering_attack_original':
  operations=tuple(('force_pair',uid,op[2]) for uid in op[1]['summoned'])
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_lingering_kill_copies':
  operations=tuple(('historical_lingering_kill_uid',uid) for uid in op[1]['summoned'])
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0];target=find(game,ctx.get('target'))
 if name=='historical_lingering_accusation':
  if target is not None and target.health>0:target.rule_state.setdefault('historical_accusations',[]).append(dict(owner=owner,kind=op[1]))
 elif name=='historical_lingering_melomania':
  game._generation_created_candidates(SHAMAN_SPELLS,ctx)
  state=getattr(p,'historical_melomania',{})
  p.historical_melomania=dict(turn=game.turn,count=1+(state.get('count',0) if state.get('turn')==game.turn else 0))
 elif name=='historical_lingering_allies':p.historical_allies_turn=game.turn
 elif name=='historical_lingering_groove':p.historical_starlight_groove=True
 elif name=='historical_lingering_brand':
  if target is not None and target.health>0:target.rule_state.setdefault('historical_sinful_brands',[]).append(owner)
 elif name in ('historical_lingering_copy_board','historical_lingering_copy_hand'):
  donor=op[1];state=op[2];before={m.uid for m in p.minions}
  if name=='historical_lingering_copy_board':
   if op[3]=='fragile':
    target=find(game,donor.uid)
    if target is not None:target.rule_state['historical_reverberation_fragile']=True
    donor.rule_state['historical_reverberation_fragile']=True
   game._summon(owner,donor.card_id,copy_from=donor,entry_origin='copy',entry_site='historical_spell_board_copy')
  else:game._summon(owner,donor.card_id,attack_bonus=donor.attack_bonus,health_bonus=donor.health_bonus,entry_source=donor,entry_zone='hand',entry_origin='copy',entry_site='from_de_other_side')
  state['summoned'].extend(m.uid for m in p.minions if m.uid not in before and m.card_id==donor.card_id)
 elif name=='historical_lingering_kill_uid':
  minion=find(game,op[1])
  if minion is not None and minion.health>0:minion.health=0
 else:return False
 return True


def accusation_event(game,kind,data):
 if kind not in ('damage','minion_died','historical_opponent_copy_played'):return
 for player in game.players:
  for minion in tuple(player.minions):
   if minion.health<=0 or minion.silenced:continue
   marks=minion.rule_state.get('historical_accusations',());remaining=[];triggered=[]
   for mark in marks:
    owner=mark['owner'];rule=mark['kind']
    matches=(rule=='arson' and kind=='damage' and data.get('target')==game.hero_id(owner) and data.get('amount',0)>0 or
             rule=='murder' and kind=='minion_died' and data.get('owner')==1-owner and data.get('source')!=minion.uid or
             rule=='theft' and kind=='historical_opponent_copy_played' and data.get('owner')==owner)
    (triggered if matches else remaining).append(mark)
   if triggered:
    minion.rule_state['historical_accusations']=remaining
    for mark in triggered:
     game._rule_events.append(('captured_effects',dict(operations=(('historical_lingering_kill_uid',minion.uid),),context=dict(owner=mark['owner'],source=None,target=0,bonus=0,lifesteal=False,card_id={'arson':'MAW_001','murder':'MAW_019','theft':'MAW_023'}[mark['kind']])),[]))
