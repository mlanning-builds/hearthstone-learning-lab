"""Staged Leyline family, with values pinned to build 251952 card tags.

Runtime paths are not live registration. Dynamic summons require a complete
exact-cost generation contract and all generated behavior.
"""
from engine.cards import UnsupportedCard
from .generation_cards import pool
LEYLINES=('MEND_500','MEND_502','MEND_504')
# Frozen data/standard/card_tags.json TAG_SCRIPT_DATA_NUM_1.
BASE={'MEND_500':4,'MEND_502':6,'MEND_504':1}
UPGRADES={'MEND_505t':('repeat',1),'MEND_505t2':('discount',2),'MEND_505t3':('effect',2)}
RULES={
 'MEND_500':('none',[('leyline_cast','MEND_500')]),
 'MEND_501':('none',[('leyline_upgrade','discount',1)]),
 'MEND_502':('none',[('leyline_cast','MEND_502')]),
 'MEND_503':('none',[('leyline_upgrade','repeat',1)]),
 'MEND_504':('none',[('leyline_cast','MEND_504')]),
 'MEND_505':('none',[('add','MEND_500',1),('add','MEND_502',1),('add','MEND_504',1),('leyline_choose',)]),
 'MEND_506':('none',[('leyline_upgrade','effect',1)]),
}
DEATH_EFFECTS={'MEND_501':[('leyline_random',)]}
TOKEN_RULES={cid:('none',[('leyline_upgrade',*upgrade)]) for cid,upgrade in UPGRADES.items()}

class Leylines:
 def _leyline_split(self,op,ctx):
  if op[0]!='leyline_cast':return None
  cid=op[1];p=self.players[ctx['owner']]
  value=BASE[cid]+p.leyline_effect
  if cid=='MEND_500':effect=('leyline_burst',value)
  elif cid=='MEND_502':
   request=pool(card_type='MINION',minimum=value,maximum=value)
   self._generation_candidates(request,ctx['owner']);effect=('generate_one',request,'board',())
  else:effect=('draw_discount',value)
  # Snapshot repetition/value for this cast. Every repetition has a checkpoint.
  return effect,tuple(effect for _ in range(p.leyline_repeats))
 def _leyline_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner]
  if name=='leyline_upgrade':
   field={'repeat':'leyline_repeats','effect':'leyline_effect','discount':'leyline_discount'}[op[1]]
   setattr(p,field,getattr(p,field)+op[2])
  elif name=='leyline_random':
   if not set(LEYLINES)<=self.cards.keys():raise UnsupportedCard('Complete Leyline outcome closure required')
   self._add(owner,self.rng.choice(LEYLINES))
  elif name=='leyline_choose':
   if not set(UPGRADES)<=self.cards.keys():raise UnsupportedCard('Missing Leyline upgrade identities')
   if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite a choice')
   self.pending_choice=dict(owner=owner,kind='leyline_upgrade',options=[dict(card_id=cid) for cid in UPGRADES]);self.phase='choice'
  elif name=='leyline_burst':
   targets=[m for m in self.players[1-owner].minions if m.health>0]
   if targets:
    m=self.rng.choice(targets);health=m.health
    with self._damage_batch():
     dealt=self._deal_effect(m.uid,op[1],dict(ctx,bonus=0))
     if dealt>health:self._deal_effect(self.hero_id(1-owner),dealt-health,dict(ctx,bonus=0))
  else:return False
  return True
 def _leyline_choice(self,choice,selected):
  if choice['kind']!='leyline_upgrade':return False
  self._leyline_effect(('leyline_upgrade',*UPGRADES[selected['card_id']]),dict(owner=choice['owner']))
  return True
