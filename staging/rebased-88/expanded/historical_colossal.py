"""Explicit retired Colossal roots and their frozen appendage identities.

Named-body checks intentionally follow the current controller, not parent links.
No historical generation membership is approved by these implementations.
"""

ROOT_IDS=frozenset(('TID_711','TSC_937','TSC_950','TSC_219','TSC_216','TSC_639','NX2_037'))

TENTACLES=tuple('TID_711t'+(str(i) if i>1 else '') for i in range(1,7))

STALKS=('TSC_219t','TSC_219t2','TSC_219t3','TSC_219t4')

HEADS=('TSC_950t','TSC_950t2')

CLAWS=('TSC_937t','TSC_937t3')

TAILS=('TSC_639t','TSC_639t2','TSC_639t3')

WINGS=('NX2_037t','NX2_037t2')

FIXED_TOKEN_IDS=frozenset(TENTACLES+STALKS+HEADS+CLAWS+TAILS+WINGS+('TSC_216t','TSC_937t2'))

RULES={cid:('none',[]) for cid in ROOT_IDS|FIXED_TOKEN_IDS}

RULES['TSC_950']=('none',[('historic_hydralodon_rush',)])

DEATH_EFFECTS={'TID_711':[('historic_ozumat_destroy',)],
 **{cid:[('equip','TSC_937t2')] for cid in CLAWS},
 **{cid:[('historic_hydralodon_heads',)] for cid in HEADS}}

START_EFFECTS={'TSC_219':('owner',[('historic_xhilag_upgrade',)])}

END_EFFECTS={**{cid:[('historic_stalk_damage',)] for cid in STALKS},
 'TSC_216t':[('historic_behemoth_lure',)]}

TRIGGERS={'TSC_639':('b60_friendly_death',[('historic_glugg_stats',)])}

LAYOUTS={
 'TID_711':tuple((cid,'right') for cid in TENTACLES),
 'TSC_937':((CLAWS[0],'right'),(CLAWS[1],'right')),
 'TSC_950':((HEADS[0],'right'),(HEADS[1],'right')),
 'TSC_219':tuple((cid,'right') for cid in STALKS),
 'TSC_216':(('TSC_216t','left'),),
 'TSC_639':tuple((cid,'right') for cid in TAILS),
 'NX2_037':((WINGS[0],'right'),(WINGS[1],'right')),
}

from .generation_cards import pool,discover

PIRATES=pool(card_type='MINION',tribe='PIRATE',classes='own_or_neutral')

ROOT_IDS=ROOT_IDS|frozenset(('TID_712','TSC_660','TSC_962'))

FIXED_TOKEN_IDS=FIXED_TOKEN_IDS|frozenset(('TID_712t','TID_712t2','TSC_660t','TSC_962t'))

RULES.update({cid:('none',[]) for cid in ('TID_712','TID_712t','TID_712t2','TSC_660t','TSC_962t')})

RULES['TSC_660']=('none',[('historic_nellie_crew',)])

RULES['TSC_962']=('none',[('historic_gigafin_devour',)])

DEATH_EFFECTS.update({'TSC_660t':[('historic_nellie_return',)],'TSC_962':[('historic_gigafin_return',)],'TSC_962t':[('historic_gigafin_dispose',)]})

LAYOUTS.update({'TID_712':(('TID_712t','right'),('TID_712t2','right')),'TSC_660':(('TSC_660t','right'),),'TSC_962':(('TSC_962t','right'),)})


class HistoricalColossal:
 def _historic_colossal_basic_split(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='historic_ozumat_destroy':
   ops=tuple(('destroy_random_enemy',) for m in p.minions if m.health>0 and m.card_id in TENTACLES)
  elif op[0]=='historic_hydralodon_heads':
   if not any(m.health>0 and m.card_id=='TSC_950' for m in p.minions):return ('batch30_noop',),()
   ops=(('death_summon',HEADS[0],1),('death_summon',HEADS[1],1))
  else:return None
  return (ops[0],ops[1:]) if ops else (('batch30_noop',),())

 def _historic_colossal_basic_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner];source=ctx.get('source');name=op[0]
  if name=='historic_hydralodon_rush':
   for m in p.minions:
    if m.card_id in HEADS and m.health>0:m.keywords.add('RUSH')
  elif name=='historic_xhilag_upgrade':
   for m in p.minions:
    if m.card_id in STALKS and m.health>0:m.rule_state['xhilag_damage']=m.rule_state.get('xhilag_damage',2)+1
  elif name=='historic_stalk_damage':
   targets=[m.uid for m in self.players[1-owner].minions if m.health>0]+[self.hero_id(1-owner)]
   self._deal_effect(self.rng.choice(targets),source.rule_state.get('xhilag_damage',2),ctx)
  elif name=='historic_behemoth_lure':
   bodies=[m for m in p.minions if m.card_id=='TSC_216' and m.health>0]
   enemies=[m for m in self.players[1-owner].minions if m.health>0]
   # Lures follow the oldest friendly named body, not their parent link.
   # Direct client observation: reddit.com/r/hearthstone/comments/1kjc7cz
   if bodies and enemies:self._force_attack(self.rng.choice(enemies).uid,min(bodies,key=lambda body:body.uid).uid)
  elif name=='historic_glugg_stats':
   data=self.cards[ctx['event']['card_id']]
   self._buff(source,data.get('attack',0),data.get('health',0))
  else:return False
  return True

 def _historic_crabatoa_aura(self,owner):
  return 2*sum(m.card_id=='TSC_937' and m.health>0 and not m.silenced for m in self.players[owner].minions)

 def _historic_colossal_frozen(self,target):
  m=self._find(target) if target>0 else None
  if m is not None and any(x.card_id=='NX2_037' and x.health>0 and not x.silenced for x in self.players[1-m.owner].minions):m.health=0

 def _historic_colossal_split(self,op,ctx):
  if op[0]=='historic_nellie_crew':
   source=ctx.get('source');ships=[m for m in self.players[ctx['owner']].minions if m.card_id=='TSC_660t' and source is not None and m.rule_state.get('colossal_parent')==source.uid]
   if not ships:return ('batch30_noop',),()
   self._generation_candidates(PIRATES,ctx['owner'])
   return ('historic_nellie_offer',ships[0].uid),(('historic_nellie_offer',ships[0].uid),('historic_nellie_offer',ships[0].uid))
  if op[0]=='historic_gigafin_return':
   source=ctx.get('source');identities=getattr(source,'_devoured_cards',()) if source is not None else ()
   if source is not None:source._devoured_cards=[]
   ops=tuple(('historic_gigafin_spit',cid,1-ctx['owner']) for cid in identities)
   return (ops[0],ops[1:]) if ops else (('batch30_noop',),())
  return self._historic_colossal_basic_split(op,ctx)
 def _historic_colossal_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner];source=ctx.get('source')
  if name=='historic_nellie_offer':
   self._generation_effect(discover(PIRATES,'nellie_crew'),dict(ctx,nellie_ship_uid=op[1]))
  elif name=='historic_nellie_return':
   for cid in getattr(source,'_nellie_crew',()) if source is not None else ():
    card=self._add(owner,cid)
    if card is not None:card.set_cost=1;card.cost_delta=0
  elif name=='historic_gigafin_devour':
   if source is None:return True
   q=self.players[1-owner];targets=[m for m in q.minions if m.health>0]
   source._devoured_cards=getattr(source,'_devoured_cards',[])+[m.card_id for m in targets]
   for m in targets:q.board.remove(m);self._log('devour',player=owner,card=m.card_id,entity=m.uid)
   self._refresh_auras()
  elif name=='historic_gigafin_spit':self._summon(op[2],op[1],entry_origin='resummon',entry_site='historical_colossal.gigafin',entry_source=source)
  elif name=='historic_gigafin_dispose':
   if source is not None:
    parent=next((m for player in self.players for m in player.all_minions if m.uid==source.rule_state.get('colossal_parent',0)),None)
    if parent is not None and parent.card_id=='TSC_962':parent._devoured_cards=[]
  else:return self._historic_colossal_basic_effect(op,ctx)
  return True
 def _historic_nellie_store(self,cid,ctx):
  ship=self._find(ctx.get('nellie_ship_uid',0))
  if ship is None or ship.card_id!='TSC_660t' or ship.health<=0:return None
  ship._nellie_crew=getattr(ship,'_nellie_crew',[])+[cid]
  return None
 def _historic_neptulon_combat(self,source,target,listeners,forced=False):
  attacker=self._find(source) if source>0 else None
  if attacker is None or attacker.card_id!='TID_712':return False
  p=self.players[attacker.owner]
  if not any(m.card_id=='TID_712' and m.health>0 and not m.silenced for m in p.minions):return False
  hands=[m.uid for m in p.minions if m.card_id in ('TID_712t','TID_712t2') and m.health>0]
  if not hands:return False
  if not forced:attacker.attacks+=1
  attacker.keywords.discard('STEALTH');attacker.temporary_keywords[:]=[e for e in attacker.temporary_keywords if e['keyword']!='STEALTH']
  self._log('attack_replaced',player=attacker.owner,source=source,target=target,hands=hands)
  for uid in hands:
   if self.terminal:break
   self._force_attack(uid,target)
  # Resolve the forced replacements before completing the original attack.
  self._settle(allow_event_choices=True)
  self._rule_events.append(('minion_attack',dict(owner=attacker.owner,source=source,target=target,attacker_neighbors=[],killed=False,victim_card_id=None),listeners))
  return True

def requests_for(cid):
 return {PIRATES} if cid=='TSC_660' else set()
