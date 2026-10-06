"""Staged finite Void storage and physical generated-card completion tasks."""
from engine.game import Card
from .generation_cards import pool

PAST_SPELLS=pool(card_type='SPELL',era='past')
RULES={'JAIL_719':('none',[('obligation_void',)]),
       'TIME_861':('none',[('obligation_toki',)])}

def requests_for(cid):return {PAST_SPELLS} if cid=='TIME_861' else set()

class StoredObligations:
 def _obligation_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner]
  if name=='obligation_void':
   keep=self.rng.randrange(len(p.deck)) if p.deck else None
   removed=[card for index,card in enumerate(p.deck) if index!=keep]
   p.deck[:]=[p.deck[keep]] if keep is not None else []
   key=self._stored_save(owner,'void',removed)
   self._log('void_created',player=owner,count=len(removed))
   # Each captured payload is finite and belongs to its player, independent of
   # the source minion surviving. The creation key orders its turn trigger.
   self._refresh_auras()
  elif name=='obligation_void_take':
   entry=getattr(self,'_stored_payloads',{}).get(op[1])
   if entry and entry['owner']==owner and entry['kind']=='void' and entry['values']:
    values=entry['values'];card=values.pop(self.rng.randrange(len(values)))
    self._enter_hand(owner,card)
    self._refresh_auras()
  elif name=='obligation_toki':
   values=self._generation_candidates(PAST_SPELLS,owner)
   if not values:return True
   if not hasattr(p,'_toki_tasks'):p._toki_tasks=[]
   generated=[Card(self._new_id(),self.rng.choice(values)) for _ in range(3)]
   p._toki_tasks.append(dict(required={card.uid for card in generated},played=set()))
   # Burned originals stay required, so two successful additions cannot count
   # as having played all three. Equal printed identities remain distinct.
   for card in generated:self._enter_hand(owner,card)
  else:return False
  return True

 def _obligation_turn_entries(self,phase):
  if phase!='start':return []
  return [dict(source=None,order=key,operations=(('obligation_void_take',key),('obligation_void_take',key)))
   for key,entry in getattr(self,'_stored_payloads',{}).items()
   if entry['kind']=='void' and entry['owner']==self.current and entry['values']]

 def _obligation_event(self,kind,data):
  if kind!='spell_cast':return
  owner=data['owner'];card=data.get('physical_card')
  if not isinstance(card,Card) or self.cards.get(card.card_id,{}).get('type')!='SPELL':return
  p=self.players[owner];remaining=[]
  for task in getattr(p,'_toki_tasks',[]):
   if card.uid in task['required']:task['played'].add(card.uid)
   if task['played']==task['required']:
    self._rule_events.append(('captured_effects',dict(operations=(('add','TIME_861',1),),
     context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
   else:remaining.append(task)
  p._toki_tasks=remaining

 def _obligation_view(self,owner,viewer):
  result={'void_remaining':sum(len(e['values']) for e in getattr(self,'_stored_payloads',{}).values()
   if e['kind']=='void' and e['owner']==owner)}
  if owner==viewer:result['toki_tasks_remaining']=[len(t['required']-t['played']) for t in getattr(self.players[owner],'_toki_tasks',[])]
  return result
