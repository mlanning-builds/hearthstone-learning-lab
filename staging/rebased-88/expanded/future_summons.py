"""Staged persistent summon upgrades; complete outcome contracts stay required.

Animal Companion replacements are three stable owner-private identities, not
three new rolls on every summon. Existing consumers share the same slots.
"""
from engine.cards import UnsupportedCard
from .generation_cards import pool
COMPANIONS=('NEW1_032','NEW1_033','NEW1_034')
VOID_SOUL='JAIL_732'
RULES={
 'MEND_300':('none',[('companions_replace',1),('draw',1)]),
 'MEND_303':('none',[('companions_replace',1)]),
 'MEND_304':('none',[('companions_extra',1)]),
 'MEND_307':('none',[('companions_replace',2),('companions_choose',)]),
 'JAIL_730':('none',[]),
 'JAIL_732':('none',[('void_soul_cast',)]),
 'JAIL_733':('none',[]),
 'JAIL_891':('minion',[('damage_add_if_dead',3,VOID_SOUL)]),
}
DEATH_EFFECTS={'JAIL_733':[('add',VOID_SOUL,1)]}
WEAPON_TRIGGERS={'JAIL_730':[('add',VOID_SOUL,1)]}
# These consumers are already live; their default behavior is unchanged.
CONSUMER_RULES={
 'CORE_NEW1_031':('none',[('companions_random',)]),
 'CORE_OG_211':('none',[('companions_all',)]),
 'MEND_301':('none',[('companions_choose',)]),
}
CONSUMER_TRIGGERS={'EDR_853':('spell_cast',[('companions_random',)])}
def requests_for(cid):
 if cid in ('MEND_300','MEND_303','MEND_307'):return {pool(card_type='MINION',tribe='BEAST')}
 if cid==VOID_SOUL:return {pool(card_type='MINION',tribe='DEMON')}
 return set()

class FutureSummons:
 def _companion_ids(self,owner):
  ids=self.players[owner].companion_ids
  if len(ids)!=3 or any(cid not in self.cards for cid in ids):raise UnsupportedCard('Complete three-slot Companion family required')
  return tuple(ids)
 def _future_summon_split(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner]
  if name=='companions_random':
   self._companion_ids(owner)
   # One bonus per originating effect, never per summoned body.
   return self._future_summon_split(('companion_random_series',1+p.companion_extra),ctx)
  if name=='companions_all':
   ids=self._companion_ids(owner)
   operations=tuple(('summon',cid,1) for cid in reversed(ids))+(('companion_random_series',p.companion_extra),)
   return operations[0],operations[1:]
  if name=='companion_random_series':
   count=op[1]
   if count<=0 or len(p.board)>=7:return ('batch30_noop',),()
   return ('companion_random_one',),(('companion_random_series',count-1),)
  if name=='void_soul_cast':
   level=p.void_soul_level
   if not 1<=level<=10:raise UnsupportedCard('Void Soul scaling beyond candidate 1–10 range')
   request=pool(card_type='MINION',tribe='DEMON',minimum=level,maximum=level)
   self._generation_candidates(request,owner)
   return ('generate_one',request,'board',()),(('void_soul_improve',),)
  return None
 def _future_summon_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner]
  if name=='companions_replace':
   old=self._companion_ids(owner);contracts=[]
   for cid in old:
    cost=self.cards[cid]['cost']+op[1]
    request=pool(card_type='MINION',tribe='BEAST',minimum=cost,maximum=cost)
    values=self._generation_candidates(request,owner)
    # A missing/empty successor is not permission to invent a max-cost rule.
    if not values:raise UnsupportedCard('Companion replacement at empty successor Cost requires reviewed boundary semantics')
    contracts.append(values)
   p.companion_ids=[self.rng.choice(values) for values in contracts]
   p.companion_upgrades+=op[1]
   self._log('companions_replaced',player=owner,upgrade=op[1])
  elif name=='companions_extra':p.companion_extra+=op[1]
  elif name=='companion_random_one':
   ids=self._companion_ids(owner)
   if len(p.board)<7:self._summon(owner,self.rng.choice(ids),entry_origin='effect',entry_site='future_summons.companion_random_one')
  elif name=='companions_choose':
   ids=self._companion_ids(owner)
   if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Companion choice')
   self.pending_choice=dict(owner=owner,kind='companion',options=[dict(card_id=cid) for cid in reversed(ids)],extra=p.companion_extra)
   self.phase='choice'
  elif name=='void_soul_improve':p.void_soul_level=min(10,p.void_soul_level+1)
  else:return False
  return True
 def _future_summon_choice(self,choice,selected):
  if choice['kind']!='companion':return False
  owner=choice['owner']
  operations=(('summon',selected['card_id'],1),)+(('companion_random_series',choice['extra']),)
  self._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
  return True
