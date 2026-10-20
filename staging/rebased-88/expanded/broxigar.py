"""Staged Broxigar: a finite disappeared card and the four Argus portals.

A copied final portal can release the original to either player. It never
creates an additional Broxigar. Physical chain identity distinguishes both players' originals. Unbound copied
portals with multiple waiting originals remain explicitly gated.
"""
from engine.game import Card
from engine.cards import UnsupportedCard

PORTALS=tuple('TIME_020t'+str(i) for i in range(2,6))
DEMONS=tuple(cid+'t' for cid in PORTALS)
RULES={'TIME_020':('none',[])}
TOKEN_RULES={'TIME_020t1':('none',[])}
TOKEN_RULES.update({cid:('none',[('brox_portal',demon)]) for cid,demon in zip(PORTALS,DEMONS)})
TOKEN_RULES.update({cid:('none',[]) for cid in DEMONS})
DEATH_EFFECTS={cid:[('brox_reward',PORTALS[i+1])] for i,cid in enumerate(DEMONS[:-1])}
DEATH_EFFECTS[DEMONS[-1]]=[('brox_return',)]
WEAPON_TRIGGERS={'TIME_020t1':[('brox_axe',)]}

class Broxigar:
 def _brox_start(self):
  if not hasattr(self,'_broxigar_waiting'):self._broxigar_waiting=[]
  for owner,p in enumerate(self.players):
   originals=[c for c in p.deck if isinstance(c,Card) and c.card_id=='TIME_020' and (self._started_in_deck(c,owner) or getattr(c,'_copied_opening_effect',False))]
   for card in originals:
    for portal in p.deck:
     if isinstance(portal,Card) and portal.card_id==PORTALS[0]:
      portal._brox_chain=card.uid
    p.deck.remove(card);self._broxigar_waiting.append(card)
    self._log('broxigar_disappears',player=owner)

 def _brox_split(self,op,ctx):
  if op[0]!='brox_reward':return None
  beneficiary=1-ctx['owner']
  chain=getattr(ctx.get('source'),'_brox_chain',None)
  return ('brox_draw',beneficiary),(('brox_shuffle',beneficiary,op[1],chain),)

 def _brox_effect(self,op,ctx):
  owner=ctx['owner'];name=op[0]
  if name=='brox_portal':
   portal=ctx.get('physical_card')
   before={m.uid for m in self.players[1-owner].all_minions}
   self._summon(1-owner,op[1],entry_origin='effect',entry_site='broxigar_portal',entry_source=portal)
   chain=getattr(portal,'_brox_chain',None)
   if chain is not None:
    for demon in self.players[1-owner].all_minions:
     if demon.uid not in before and demon.card_id==op[1]:demon._brox_chain=chain
  elif name=='brox_draw':self._draw(op[1])
  elif name=='brox_shuffle':
   beneficiary,cid=op[1:3]
   chain=op[3] if len(op)>3 else None
   if cid not in self.cards:raise UnsupportedCard('Missing Argus portal: '+cid)
   card=Card(self._new_id(),cid)
   if chain is not None:card._brox_chain=chain
   self.players[beneficiary].deck.append(card);self.rng.shuffle(self.players[beneficiary].deck)
   self._record_deck_insertion(beneficiary,beneficiary,1,'shuffle',cards=(card,))
  elif name=='brox_return':
   waiting=getattr(self,'_broxigar_waiting',[])
   chain=getattr(ctx.get('source'),'_brox_chain',None)
   if chain is not None:
    card=next((c for c in waiting if c.uid==chain),None)
   elif len(waiting)>1:
    raise UnsupportedCard('Multiple disappeared Broxigars with an unbound portal require ownership evidence')
   else:card=waiting[0] if waiting else None
   if card is not None:
    waiting.remove(card);beneficiary=1-owner
    self._enter_hand(beneficiary,card)
    self._log('broxigar_returns',player=beneficiary)
  elif name=='brox_axe':
   if ctx.get('attack_killed',False):
    self._rule_events.append(('captured_effects',dict(operations=(('brox_draw_portal',),),
      context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
  elif name=='brox_draw_portal':self._draw(owner,predicate=lambda d:d['id'] in PORTALS)
  else:return False
  return True
