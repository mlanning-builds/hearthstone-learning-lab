"""Staged evolving locations; identity changes retain the physical location.

Pool closure and client timing review gate admission. No text interpretation.
"""
from engine.cards import UnsupportedCard
from copy import deepcopy
from engine.game import Card
from .generation_cards import pool,random_cards,discover
from .selectors import has_school
DRAGONS=pool(card_type='MINION',tribe='DRAGON',minimum=5)
NAGAS=pool(card_type='MINION',tribe='NAGA',excluded_mechanic='COLOSSAL')
TIMELINES={
 'TIME_044':('TIME_044','TIME_044t1','TIME_044t2'),
 'TIME_436':('TIME_436','TIME_436t1','TIME_436t2'),
 'TIME_810':('TIME_810','TIME_810t1','TIME_810t2'),
}
STAGES={cid:(root,index) for root,ids in TIMELINES.items() for index,cid in enumerate(ids)}
RULES={cid:('none',[]) for cid in (*TIMELINES,'FIR_907','CATA_527','TIME_217')}
LOCATION_RULES={cid:('minion' if root=='TIME_044' else 'none') for cid,(root,_) in STAGES.items()}
LOCATION_RULES.update(FIR_907='none',CATA_527='character',JAIL_887='hand_card')
RULES['JAIL_887']=('none',[])
TOKEN_RULES={'JAIL_887t2':('none',[]),'JAIL_887t3':('none',[])}
END_EFFECTS={'JAIL_887t2':[('prison_replay',)]}
TRIGGERS={'CATA_527t2':(('spell_school_cast','FEL'),[('evolving_naga',)])}

def requests_for(cid):
 if cid=='TIME_217':return {pool(card_type='MINION',minimum=5,maximum=5)}
 if cid=='TIME_436':return {DRAGONS}
 if cid=='FIR_907':return {pool(card_type='MINION')}
 if cid=='CATA_527':return {NAGAS}
 return set()

class EvolvingLocations:
 def _evolving_operations(self,location):
  if 'crafted_location_ops' in location.rule_state:return list(location.rule_state['crafted_location_ops'])
  cid=location.card_id;owner=location.owner
  if cid=='JAIL_887':
   for child in ('JAIL_887t2','JAIL_887t3'):
    if child not in self.cards:raise UnsupportedCard('Missing Prison dependency: '+child)
   return [('prison_discard',),('summon','JAIL_887t3',1)]
  if cid in STAGES:
   root,stage=STAGES[cid]
   for identity in TIMELINES[root]:
    if self.cards.get(identity,{}).get('type')!='LOCATION':raise UnsupportedCard('Missing timeline location: '+identity)
   if root=='TIME_044':
    ops=[('buff',2,1)]
    if stage:ops.append(('evolving_attach_death_damage',2))
    if stage==2:ops.append(('keyword','DIVINE_SHIELD'))
   elif root=='TIME_436':
    self._generation_candidates(DRAGONS,owner)
    ops=[random_cards(DRAGONS,destination='board')] if stage==0 else [('evolving_dragon_choice',stage==2)]
   else:ops=[('evolving_silvermoon',stage)]
   if stage<2:ops.append(('evolving_advance',TIMELINES[root][stage+1]))
   return ops
  if cid=='FIR_907':
   amount=1+location.rule_state.get('uses',0)
   request=pool(card_type='MINION',minimum=amount,maximum=amount)
   self._generation_candidates(request,owner)
   location.rule_state['uses']=amount
   return [random_cards(request,destination='board'),('armor',amount),('draw',amount),('evolving_refresh',amount)]
  if cid=='CATA_527':
   if self.cards.get('CATA_527t2',{}).get('type')!='MINION':raise UnsupportedCard('Missing freed Nespirah')
   return [('evolving_damage',1)]
  return None

 def _evolving_removed(self,location,position):
  if location.card_id=='JAIL_887':
   self._rule_events.append(('captured_effects',dict(operations=(('prison_free',deepcopy(location.rule_state.get('prison_cards',[]))),),
    context=dict(owner=location.owner,source=None,target=0,bonus=0,lifesteal=False,death_position=position)),[]))
  if location.card_id=='CATA_527':
   self._rule_events.append(('captured_effects',dict(operations=(('death_summon','CATA_527t2',1),),
    context=dict(owner=location.owner,source=None,target=0,bonus=0,lifesteal=False,death_position=position)),[]))

 def _evolving_event(self,kind,data):
  if kind!='spell_cast' or not has_school(self.cards.get(data.get('card_id'),{}),'FEL'):return
  for location in self.players[data['owner']].locations:
   if location.card_id=='CATA_527':location.ready_turn=self.turn

 def _evolving_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner]
  if name=='prison_discard':
   card=next((c for c in p.hand if c.uid==ctx['target']),None)
   if card is None:raise UnsupportedCard('Selected prison discard left hand')
   self._discard_card(owner,card)
  elif name=='prison_free':
   m=self._summon(owner,'JAIL_887t2',ctx.get('death_position',-1),entry_origin='deathrattle',entry_site='prison_free')
   if m is not None:m.rule_state['prison_cards']=deepcopy(op[1])
  elif name=='evolving_advance':
   source=ctx.get('source')
   if source in p.locations:source.card_id=op[1]
  elif name=='evolving_attach_death_damage':
   m=next((m for player in self.players for m in player.minions if m.uid==ctx['target']),None)
   if m is not None:m.attached_death_effects.append(('damage_enemy_hero',op[1]))
  elif name=='evolving_refresh':p.mana=min(p.max_mana-p.locked_mana,p.mana+op[1])
  elif name=='evolving_damage':self._deal_effect(ctx['target'],op[1],dict(ctx,source=None))
  elif name=='evolving_silvermoon':
   targets=[m for m in self.players[1-owner].minions if m.health>0]
   if targets:
    if op[1]==2:
     health=min(m.health for m in targets);targets=[m for m in targets if m.health==health]
    m=self.rng.choice(targets);health=m.health;dealt=self._deal_effect(m.uid,5,dict(ctx,source=None))
    if op[1] and dealt>health:self._deal_effect(self.hero_id(1-owner),dealt-health,dict(ctx,source=None))
  elif name=='evolving_dragon_choice':
   values=self._generation_candidates(DRAGONS,owner)
   if values:
    self.pending_choice=dict(owner=owner,kind='evolving_dragon',copy=op[1],
     options=[dict(card_id=cid) for cid in self.rng.sample(list(values),min(3,len(values)))])
    self.phase='choice'
  elif name=='evolving_naga':
   values=self._generation_candidates(NAGAS,owner)
   if values:self._generation_place(self.rng.choice(values),'hand',(('set_cost',1),),ctx)
  else:return False
  return True

 def _evolving_choice(self,choice,selected):
  if choice['kind']!='evolving_dragon':return False
  ctx=dict(owner=choice['owner']);cid=selected['card_id']
  self._discovery_result=self._generation_place(cid,'board',(),ctx)
  if choice['copy']:self._generation_place(cid,'hand',(),ctx)
  return True
