"""Staged Broxigar: a finite disappeared card and the four Argus portals.

A copied final portal can release the original to either player. It never
creates an additional Broxigar. Multiple originals remain explicitly gated.
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
    p.deck.remove(card);self._broxigar_waiting.append(card)
    self._log('broxigar_disappears',player=owner)

 def _brox_split(self,op,ctx):
  if op[0]!='brox_reward':return None
  beneficiary=1-ctx['owner']
  return ('brox_draw',beneficiary),(('brox_shuffle',beneficiary,op[1]),)

 def _brox_effect(self,op,ctx):
  owner=ctx['owner'];name=op[0]
  if name=='brox_portal':
   self._summon(1-owner,op[1],entry_origin='effect',entry_site='broxigar_portal',entry_source=ctx.get('physical_card'))
  elif name=='brox_draw':self._draw(op[1])
  elif name=='brox_shuffle':
   beneficiary,cid=op[1:]
   if cid not in self.cards:raise UnsupportedCard('Missing Argus portal: '+cid)
   self.players[beneficiary].deck.append(Card(self._new_id(),cid));self.rng.shuffle(self.players[beneficiary].deck)
   self._record_deck_insertion(beneficiary,beneficiary,1,'shuffle')
  elif name=='brox_return':
   waiting=getattr(self,'_broxigar_waiting',[])
   if len(waiting)>1:raise UnsupportedCard('Multiple disappeared Broxigars require independent ownership evidence')
   if waiting:
    card=waiting.pop();beneficiary=1-owner
    self._enter_hand(beneficiary,card)
    self._log('broxigar_returns',player=beneficiary)
  elif name=='brox_axe':
   if ctx.get('attack_killed',False):
    self._rule_events.append(('captured_effects',dict(operations=(('brox_draw_portal',),),
      context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
  elif name=='brox_draw_portal':self._draw(owner,predicate=lambda d:d['id'] in PORTALS)
  else:return False
  return True
