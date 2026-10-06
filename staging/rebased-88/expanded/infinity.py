"""Staged Infinity family. Numeric/client cap and interaction audit gates admission."""
# Hearthstone uses finite integer attributes. Keep this explicit and JSON-safe;
# independent pinned-client boundary verification is tracked in fidelity_gaps.
INFINITY=2**31-1
RULES={
 'END_012':('none',[('infinity_weapon',)]),
 'END_018':('none',[('infinity_cost',)]),
 'END_024':('none',[('secret','END_024')]),
 'TIME_024':('none',[('infinity_delayed_attack',)]),
}
DEATH_EFFECTS={'END_018':[('infinity_restore_cost',)]}
SECRETS={'END_024':'flames_infinity'}
class InfinityEffects:
 def _infinity_turn_entries(self,phase):
  if phase=='start':
   return [dict(source=m,order=m.uid,operations=(('infinity_set_attack',m.uid,m.card_id,token),))
           for p in self.players for m in p.minions
           for token,due_owner,due in m.rule_state.get('infinity_attack_due',[])
           if due_owner==self.current and due<=self.players[self.current].turns_taken]
  if phase!='end':return []
  owner=1-self.current
  return [dict(source=None,order=c.uid,operations=(('infinity_secret',owner,c.uid),))
          for c in self.players[owner].secrets if c.card_id=='END_024']
 def _infinity_expire(self):
  for p in self.players:
   w=p.weapon
   if w and 'infinity_delta' in w:
    w['attack']=max(0,w['attack']-w.pop('infinity_delta'))
 def _infinity_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner];source=ctx.get('source')
  if name=='infinity_weapon':
   if p.weapon and p.weapon['card_id']=='END_012':
    previous=p.weapon['attack']-p.weapon.get('infinity_delta',0)
    p.weapon['infinity_delta']=INFINITY-previous;p.weapon['attack']=INFINITY
  elif name=='infinity_cost':
   if p.hand and source is not None:
    c=self.rng.choice(p.hand);token=self._new_id()
    layers=getattr(c,'_infinity_cost_layers',[]);c._infinity_cost_layers=layers+[token]
    source._infinity_cost_receipts=getattr(source,'_infinity_cost_receipts',[])+[(c.uid,token)]
  elif name=='infinity_restore_cost':
   for uid,token in getattr(source,'_infinity_cost_receipts',[]):
    for player in self.players:
     for c in player.hand+player.deck:
      if getattr(c,'uid',None)==uid:
       c._infinity_cost_layers=[x for x in getattr(c,'_infinity_cost_layers',[]) if x!=token]
  elif name=='infinity_delayed_attack':
   if source is not None:source.rule_state.setdefault('infinity_attack_due',[]).append((self._new_id(),owner,p.turns_taken+1))
  elif name=='infinity_set_attack':
   m=next((m for player in self.players for m in player.all_minions if m.uid==op[1] and m.card_id==op[2]),None)
   if m is not None and any(row[0]==op[3] for row in m.rule_state.get('infinity_attack_due',[])):
    m.rule_state['infinity_attack_due']=[row for row in m.rule_state['infinity_attack_due'] if row[0]!=op[3]]
    self._set_minion_attack(m,INFINITY)
  elif name=='infinity_secret':
   beneficiary,uid=op[1:];q=self.players[1-beneficiary]
   secret=next((c for c in self.players[beneficiary].secrets if c.uid==uid),None)
   targets=[m for m in q.minions if m.health>0]
   if secret is not None and self.current!=beneficiary and targets:
    high=max(m.health for m in targets);target=self.rng.choice([m for m in targets if m.health==high])
    self._reveal_secret(beneficiary,secret)
    # Frozen ImmuneToSpellpower tag: use ordinary damage protection without bonus.
    self._damage(target.uid,INFINITY,damage_owner=beneficiary,damage_source=None)
  else:return False
  return True
