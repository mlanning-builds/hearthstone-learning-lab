"""Staged spell-bearing tokens, targeted casting and a held growing spell.

Pool membership and sampling/timing fidelity still gate live admission. Bound
spell identities are physical card state, never inferred from displayed text.
"""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool
from .cards import RULES as LIVE_RULES, CHOICES

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
 def _learned_mode(self,cid):
  if not self._supports_internal_spell(cid):raise UnsupportedCard('Learned spell lacks internal casting: '+cid)
  if cid in CHOICES:
   modes={mode for _,mode,_ in CHOICES[cid] if mode!='none'}
   if len(modes)>1:raise UnsupportedCard('Learned Choose One targeting requires branch-specific review: '+cid)
   return next(iter(modes),'none')
  return LIVE_RULES[cid][0]

 def _learned_targets(self,card,owner):
  if card.card_id not in ('MEND_046t','TIME_704t'):return None
  cid=getattr(card,'_learned_spell',None)
  if cid is None:return [0]
  mode=self._learned_mode(cid)
  return self._targets_for(cid,owner,mode) or [0]

 def _learned_pool(self,request,owner):
  values=self._autocast_candidates(request,owner)
  for cid in values:self._learned_mode(cid)
  return values

 def _learned_split(self,op,ctx):
  owner=ctx['owner'];name=op[0]
  if name=='learned_cast':
   card=ctx.get('physical_card') or ctx.get('source')
   cid=getattr(card,'_learned_spell',None)
   if cid is None:return ('batch30_noop',),()
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
  if name=='learned_mentor':
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
   count=min(3,10-len(p.hand))
   # Maximal reachable total up to 12, using exactly the number of surviving
   # Treants. With one hand slot, only one spell receives the budget.
   costs={cid:self.cards[cid]['cost'] for cid in values}
   reachable=[{0}]
   for _ in range(count):reachable.append({n+c for n in reachable[-1] for c in costs.values() if n+c<=12})
   if count and not reachable[count]:raise UnsupportedCard('Nature contract cannot fill the carve allocation')
   remaining=max(reachable[count]) if count else 0
   payload=[]
   for slots in range(count,0,-1):
    eligible=[cid for cid in values if remaining-costs[cid] in reachable[slots-1]]
    cid=self.rng.choice(eligible);payload.append(cid);remaining-=costs[cid]
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
