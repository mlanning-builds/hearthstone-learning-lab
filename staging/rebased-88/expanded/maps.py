"""Staged two-step map choices bound to physical cards and original options."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool
from .pools import deck_choice_options
from .selectors import effective_tribes
REQUESTS={
 'TLC_435':pool(rune='frost',classes='own_or_neutral'),
 'TLC_442':pool(card_type='MINION',tribe='MURLOC'),
 'TLC_464':pool(card_type='MINION'),
 'TLC_824':pool(card_type='MINION',tribe='BEAST'),
 'TLC_900':pool(card_type='SPELL',school='FEL'),
}
RULES={cid:('none',[('map_discover',cid)]) for cid in (*REQUESTS,'TLC_515')}
def requests_for(cid):return {REQUESTS[cid]} if cid in REQUESTS else set()

class Maps:
 def _map_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='map_discover':
   cid=op[1];from_deck=cid=='TLC_515'
   if from_deck:
    # Persistent physical identity is necessary: the first card's play may
    # shuffle, draw or transform the deck before the follow-up choice.
    for i,c in enumerate(p.deck):
     if not isinstance(c,Card):p.deck[i]=Card(self._new_id(),c)
    indexed=[(i,c) for i,c in enumerate(p.deck) if c.card_id!=cid]
    options=deck_choice_options([c for _,c in indexed],self.cards,3,self.rng)
    for option in options:
     option['uid']=indexed[option.pop('index')][1].uid
   else:
    values=self._generation_discover_candidates(REQUESTS[cid],dict(ctx,card_id=cid))
    if cid=='TLC_824':values=[c for c in values if self.cards[c].get('attack',0)%2==1]
    if cid=='TLC_464':
     played=set()
     for entry in p.played_history:
      d=self.cards[entry['card_id']]
      if d['type']=='MINION':played.update(effective_tribes(d))
     values=[c for c in values if effective_tribes(self.cards[c])-played]
    options=[dict(card_id=c) for c in self.rng.sample(list(values),min(3,len(values)))]
   if options:
    if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite map choice')
    self.pending_choice=dict(owner=owner,kind='map_discover',card_id=cid,from_deck=from_deck,deck_owner=owner,options=options)
    self.phase='choice'
  elif op[0]=='map_follow_choice':
   entry=op[1];options=deepcopy(entry['map_options'])
   if entry['from_deck']:
    live={c.uid:c for c in self.players[entry['deck_owner']].deck if isinstance(c,Card)}
    options=[dict(card_id=live[o['uid']].card_id,uid=o['uid']) for o in options if o['uid'] in live]
   if options:
    if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite map follow-up')
    self.pending_choice=dict(owner=owner,kind='map_follow',from_deck=entry['from_deck'],deck_owner=entry['deck_owner'],options=options)
    self.phase='choice'
  else:return False
  return True
 def _map_choice(self,choice,selected):
  if choice['kind'] not in ('map_discover','map_follow'):return False
  owner=choice['owner']
  if choice['from_deck']:
   deck=self.players[choice['deck_owner']].deck
   card=next((c for c in deck if isinstance(c,Card) and c.uid==selected['uid']),None)
   if card is None:raise UnsupportedCard('Map-selected physical card left its deck')
   deck.remove(card);card=self._enter_hand(owner,card);self._refresh_auras()
  else:card=self._generation_place(selected['card_id'],'hand',(),dict(owner=owner))
  self._discovery_result=card
  if card is not None and choice['kind']=='map_discover':
   others=[deepcopy(o) for o in choice['options'] if o is not selected]
   if others:
    card._follow_effects=getattr(card,'_follow_effects',[])+[dict(card_id=choice['card_id'],end=self.turn,
        map_options=others,from_deck=choice['from_deck'],deck_owner=choice['deck_owner'])]
  return True
