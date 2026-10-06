"""Automatic spell consumers; staged until complete pools and timing review.

Player-cast history/listeners are deliberately separate from spells cast by an
entity. No unsupported outcome is removed from a random pool.
"""
from engine.cards import UnsupportedCard
from .generation_cards import pool
from .selectors import has_school
SPELLS=pool(card_type='SPELL')
OTHER_SPELLS=pool(card_type='SPELL',classes='other')
MINIONS=pool(card_type='MINION')
SECRETS=pool(card_type='SPELL',mechanic='SECRET')
MAGE_SECRETS=pool(card_type='SPELL',mechanic='SECRET',classes='MAGE')
RULES={
 'JAIL_500':('none',[('slice_replay',),('request_end_turn',)]),
 'EDR_031':('none',[]),
 'CATA_786':('none',[]),
 'EDR_520':('none',[]),
 'JAIL_122':('none',[('autocast_install_manastorm',)]),
 'JAIL_321':('none',[('autocast_prepared_secrets',)]),
 'TIME_860':('none',[('autocast_secret_pair',)]),
 'TLC_430':('none',[]),
}
LOCATION_RULES={'EDR_520':'none'}
LOCATION_EFFECTS={'EDR_520':[('autocast_spend_mana',)]}
TRIGGERS={'CATA_786':('spell_cast',[('autocast_other_same_cost',)])}
END_EFFECTS={'EDR_031':[('automatic_top',3)],'TLC_430':[('autocast_holy_history',)]}
UNRESOLVED={
 'FIR_959':'Staged exceptional_finish body includes entity-aware global destruction, stat, transformation and shuffle protection. Complete Fire-pool closure, targeting and budget sampling still require review.',
}
def requests_for(cid):
 return {'CATA_786':{OTHER_SPELLS},'EDR_520':{SPELLS},'JAIL_122':{MINIONS},
         'JAIL_321':{MAGE_SECRETS},'TIME_860':{SECRETS}}.get(cid,set())

class AutomaticCasting:
 def _autocast_candidates(self,request,owner):
  values=self._generation_candidates(request,owner)
  unsupported=[cid for cid in values if not self._supports_internal_spell(cid)]
  if unsupported:raise UnsupportedCard('Automatic spell pool lacks internal support: '+', '.join(unsupported))
  return values
 def _autocast_split(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner]
  if name=='autocast_spend_mana':
   amount=p.mana;request=pool(card_type='SPELL',minimum=amount,maximum=amount)
   values=self._autocast_candidates(request,owner)
   p.mana=0;self._b60_spend_mana(owner,amount)
   return (self._cast_spell_split(('cast_fixed_spell',self.rng.choice(values),'random'),ctx)
           if values else (('batch30_noop',),()))
  if name=='autocast_other_same_cost':
   cost=ctx['event']['cost'];request=pool(card_type='SPELL',classes='other',minimum=cost,maximum=cost)
   values=self._autocast_candidates(request,owner)
   return (self._cast_spell_split(('cast_fixed_spell',self.rng.choice(values),'random'),ctx)
           if values else (('batch30_noop',),()))
  if name=='autocast_prepared_secrets':
   if not p.spells_turn:return ('batch30_noop',),()
   # Check the complete pool once before the first cast; choose again at each
   # checkpoint, allowing existing Secret rules to handle duplicates/full slots.
   self._autocast_candidates(MAGE_SECRETS,owner)
   return self._split_fixed_summon(('autocast_random',MAGE_SECRETS,2),ctx)
  if name=='autocast_random':
   request,count=op[1:];values=self._autocast_candidates(request,owner)
   if count<=0 or not values:return ('batch30_noop',),()
   first,tail=self._cast_spell_split(('cast_fixed_spell',self.rng.choice(values),'random'),ctx)
   return first,tuple(tail)+((('autocast_random',request,count-1),) if count>1 else ())
  if name=='autocast_holy_history':
   values=[cid for cid in p.spells_turn if has_school(self.cards[cid],'HOLY')]
   if not values:return ('batch30_noop',),()
   if any(not self._supports_internal_spell(cid) for cid in values):raise UnsupportedCard('Holy history contains unsupported internal spell')
   return self._cast_spell_split(('cast_fixed_spell',self.rng.choice(values),'prefer_source'),ctx)
  return None
 def _autocast_effect(self,op,ctx):
  name=op[0];owner=ctx['owner']
  if name=='autocast_install_manastorm':self.players[owner].manastorm_effects+=1
  elif name=='autocast_secret_pair':
   values=self._autocast_candidates(SECRETS,owner)
   # Validate the opponent's execution of every outcome too; ownership changes
   # target legality, not the Secret identities offered by this card.
   if not values:return True
   if self.pending_choice is not None:raise UnsupportedCard('Cannot replace a pending Secret choice')
   options=[dict(card_id=cid) for cid in self.rng.sample(list(values),min(2,len(values)))]
   self.pending_choice=dict(owner=owner,kind='autocast_secret_pair',options=options)
   self.phase='choice'
  else:return False
  return True
 def _autocast_choice(self,choice,selected):
  if choice['kind']!='autocast_secret_pair':return False
  owner=choice['owner'];operations=[('cast_fixed_spell',selected['card_id'],'random')]
  for option in choice['options']:
   if option is not selected:
    other=dict(owner=1-owner,source=None,target=0,bonus=0,lifesteal=False)
    operations.append(('replay_context',(('cast_fixed_spell',option['card_id'],'random'),),other))
  self._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
  return True
 def _autocast_event(self,kind,data):
  if kind!='spell_cast':return
  owner=data['owner'];count=self.players[owner].manastorm_effects
  if not count:return
  cost=data['cost'];request=pool(card_type='MINION',minimum=cost,maximum=cost)
  operations=tuple(('generate_one',request,'board',()) for _ in range(count))
  self._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
