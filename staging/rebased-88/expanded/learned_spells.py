"""Staged spell-bearing tokens, targeted casting and a held growing spell.

Pool membership and sampling/timing fidelity still gate live admission. Bound
spell identities are physical card state, never inferred from displayed text.
"""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool

PAST_LARGE=pool(card_type='SPELL',minimum=7,classes='own_or_neutral',era='past')
NATURE=pool(card_type='SPELL',school='NATURE',maximum=12)
RULES={
 'TIME_704':('none',[('learned_mentor',)]),
 'MEND_046':('none',[('learned_carve',)]),
 'MEND_100':('none',[('learned_bulb',)]),
}
TOKEN_RULES={
 'TIME_704t':('none',[('learned_cast',)]),
 'MEND_046t':('none',[('learned_cast',)]),
 'MEND_100t':('none',[('learned_bulb_cast',)]),
}

def requests_for(cid):
 return {'TIME_704':{PAST_LARGE},'MEND_046':{NATURE},'MEND_100':{pool(card_type='SPELL')}}.get(cid,set())

class LearnedSpells:
 def _learned_mode(self,cid,owner=None):
  from .cards import RULES as LIVE_RULES, CHOICES
  if not self._supports_internal_spell(cid,owner):raise UnsupportedCard('Learned spell lacks internal casting: '+cid)
  if cid in CHOICES:
   modes={mode for _,mode,_ in CHOICES[cid] if mode!='none'}
   if len(modes)>1:raise UnsupportedCard('Learned Choose One targeting requires branch-specific review: '+cid)
   return next(iter(modes),'none')
  return LIVE_RULES[cid][0]

 def _learned_targets(self,card,owner):
  if card.card_id not in ('MEND_046t','TIME_704t','TSC_052t','TOY_504t'):return None
  cid=getattr(card,'_learned_spell',None)
  if cid is None:return [0]
  mode=self._learned_mode(cid,owner)
  return self._targets_for(cid,owner,mode) or [0]

 def _learned_pool(self,request,owner):
  values=self._autocast_candidates(request,owner)
  for cid in values:self._learned_mode(cid,owner)
  return values

 def _learned_carve_allocation(self,values,count):
  """Use a reviewed allocation distribution, never infer its probabilities.

  The printed budget and observed full-hand behavior constrain outcomes but
  do not determine how cost tuples or spell identities are sampled.
  """
  if not count:return ()
  # A single available hand slot maximizes the reachable budget. In the
  # pinned pool Typhoon is the unique maximum; there is no distribution to
  # infer in that case. Do not extrapolate this into multi-Treant weights.
  costs={cid:self.cards[cid]['cost'] for cid in values}
  if count==1:
   eligible=[cid for cid,cost in costs.items() if cost<=12]
   if eligible:
    maximum=max(costs[cid] for cid in eligible)
    best=[cid for cid in eligible if costs[cid]==maximum]
    if len(best)==1:return (best[0],)
  contract=getattr(self,'carve_allocation_contract',None)
  if contract is None:
   from functools import lru_cache
   from .approximation_policy import mark
   ids=tuple(sorted(cid for cid,cost in costs.items() if cost<=12))
   @lru_cache(None)
   def ways(slots,budget):
    if slots==0:return int(budget==0)
    return sum(ways(slots-1,budget-costs[cid]) for cid in ids if costs[cid]<=budget)
   totals=[budget for budget in range(13) if ways(count,budget)]
   if not totals:raise UnsupportedCard('Nature pool cannot fill a carve allocation')
   mark(self,'bashana');budget=max(totals);result=[]
   for slots in range(count,0,-1):
    ticket=self.rng.randrange(ways(slots,budget))
    for cid in ids:
     weight=ways(slots-1,budget-costs[cid]) if costs[cid]<=budget else 0
     if ticket<weight:result.append(cid);budget-=costs[cid];break
     ticket-=weight
   return tuple(result)
  if not isinstance(contract,dict) or not contract.get('source'):raise UnsupportedCard('Invalid Bashana allocation contract')
  outcomes=contract.get('outcomes_by_count',{}).get(count,())
  if not outcomes:raise UnsupportedCard('Missing Bashana allocation for surviving Treant count')
  reachable={0}
  for _ in range(count):reachable={n+c for n in reachable for c in costs.values() if n+c<=12}
  if not reachable:raise UnsupportedCard('Nature contract cannot fill the carve allocation')
  total=max(reachable)
  for outcome in outcomes:
   if not isinstance(outcome,(tuple,list)) or len(outcome)!=2:raise UnsupportedCard('Invalid Bashana allocation outcome')
   weight,ids=outcome
   if type(weight) is not int or weight<=0 or not isinstance(ids,(tuple,list)) or len(ids)!=count:
    raise UnsupportedCard('Invalid Bashana allocation weight or count')
   if any(cid not in costs for cid in ids) or sum(costs[cid] for cid in ids)!=total:
    raise UnsupportedCard('Bashana allocation violates eligible Nature identities or reachable budget')
  return tuple(self.rng.choices([ids for _,ids in outcomes],weights=[weight for weight,_ in outcomes],k=1)[0])

 def _learned_split(self,op,ctx):
  owner=ctx['owner'];name=op[0]
  if name=='learned_cast':
   card=ctx.get('physical_card') or ctx.get('source')
   cid=getattr(card,'_learned_spell',None)
   if cid is None:raise UnsupportedCard('Learned minion has no bound spell payload')
   physical=getattr(card,'_learned_card',None)
   if physical is not None:return self._cast_spell_split(('cast_physical_spell',self._copy_card(physical,source_owner=owner),'selected'),ctx)
   return self._cast_spell_split(('cast_fixed_spell',cid,'selected'),ctx)
  if name=='learned_bulb_cast':
   card=ctx.get('physical_card');level=getattr(card,'rule_state',{}).get('bulb_level',1)
   request=pool(card_type='SPELL',minimum=level,maximum=level)
   return self._autocast_split(('autocast_random',request,3),ctx)
  return None

 def _learned_choice(self,choice,selected):
  if choice['kind']!='learned_mentor':return False
  card=choice['pupil'];owner=choice['owner']
  if card is not None and any(c is card for c in self.players[owner].hand):card._learned_spell=selected['card_id']
  self._discovery_result=None
  return True

 def _learned_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner]
  if name=='learned_school_teacher':
   request=pool(card_type='SPELL',maximum=3,classes='own_or_neutral')
   values=self._generation_discover_candidates(request,ctx)
   card=self._add(owner,'TSC_052t')
   if values:
    self.pending_choice=dict(owner=owner,kind='learned_mentor',pupil=card,options=[dict(card_id=cid) for cid in self.rng.sample(list(values),min(3,len(values)))],_automatic=bool(ctx.get('automatic_choices',False)))
    self.phase='choice'
  elif name=='learned_mentor':
   if self.cards.get('TIME_704t',{}).get('type')!='MINION':raise UnsupportedCard('Missing Highborne Pupil')
   values=self._learned_pool(PAST_LARGE,owner)
   card=self._add(owner,'TIME_704t')
   if values:
    self.pending_choice=dict(owner=owner,kind='learned_mentor',pupil=card,
     options=[dict(card_id=cid) for cid in self.rng.sample(list(values),min(3,len(values)))])
    self.phase='choice'
  elif name=='learned_carve':
   if self.cards.get('MEND_046t',{}).get('type')!='MINION':raise UnsupportedCard('Missing Runed Treant')
   values=self._learned_pool(NATURE,owner)
   count=min(3,getattr(p,'hand_capacity',10)-len(p.hand))
   payload=self._learned_carve_allocation(values,count)
   for index in range(3):
    card=self._add(owner,'MEND_046t')
    if card is not None:card._learned_spell=payload[index]
  elif name=='learned_bulb':
   if self.cards.get('MEND_100t',{}).get('type')!='SPELL':raise UnsupportedCard('Missing Blooming Bulb')
   card=self._add(owner,'MEND_100t')
   if card is not None:self._b60_state(card)['bulb_level']=1
  elif name=='learned_bulb_tick':
   card=next((c for c in p.hand if c.uid==op[1] and c.card_id=='MEND_100t'),None)
   if card is not None:
    state=self._b60_state(card)
    if state.get('bulb_last_tick')!=self.turn:
     state['bulb_last_tick']=self.turn;state['bulb_level']=min(10,state.get('bulb_level',1)+1)
  else:return False
  return True

 def _learned_turn_entries(self,phase):
  if phase!='start':return []
  return [dict(source=None,order=c.uid,operations=(('learned_bulb_tick',c.uid),))
   for c in self.players[self.current].hand if c.card_id=='MEND_100t']
