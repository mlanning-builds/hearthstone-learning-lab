"""Explicit opening-deck effects and a shared maximum mana capacity."""
from engine.game import Card
RULES={'EDR_000':('none',[('gain_full_crystals',3)]),'JAIL_384':('none',[])}

STAGED_RULES={'JAIL_509':('none',[]),'JAIL_800':('none',[])}

class StartingRules:
 def _starting_rules(self):
  self._historical_starting_rules()
  self._deadline_start_game()
  self._mug_start()
  self._brox_start()
  self._garona_start()
  # Inspect original submitted decks before either player's effects mutate them.
  increases=sum(self._opening_effect_ids(owner).count('EDR_000') for owner in range(2))
  if increases:
   for p in self.players:p.mana_capacity+=5*increases
   self._log('mana_capacity_increased',amount=5*increases)
  for owner,p in enumerate(self.players):
   p.overdraw_return_active='JAIL_509' in self._opening_effect_ids(owner)
   for _ in range(self._opening_effect_ids(owner).count('JAIL_384')):
    candidates=[self._card_data(c)['id'] for c in p.deck+p.hand
                if self._card_data(c)['id']!='JAIL_384' and self._card_data(c).get('rarity')=='LEGENDARY']
    self.rng.shuffle(candidates)
    additions=[self._starting_replay_card(owner,cid) for cid in candidates[:max(0,99-len(p.deck))]]
    p.deck.extend(additions)
    if additions:self.rng.shuffle(p.deck)
    self._log('starting_legendary_duplicates',player=owner,count=len(additions))

 def _recover_overdraw(self):
  for owner,p in enumerate(self.players):
   while p.overdraw_return_active and p.overdraw_cache and len(p.hand)<getattr(p,'hand_capacity',10):
    card=p.overdraw_cache.pop(self.rng.randrange(len(p.overdraw_cache)))
    self._enter_hand(owner,card)
    self._log('overdraw_return',player=owner,card=card.card_id)

 def _mug_start(self):
  for owner,p in enumerate(self.players):
   if 'JAIL_800' not in self._opening_effect_ids(owner):continue
   powers=[]
   if not any(cid!='JAIL_800' and self.cards[cid]['type']=='MINION' for cid in p.starting_deck):powers.append('JAIL_800hp1')
   if not any(self.cards[cid]['type']=='SPELL' for cid in p.starting_deck):powers.append('JAIL_800hp2')
   if any(cid not in self.cards for cid in powers):
    from engine.cards import UnsupportedCard
    raise UnsupportedCard('Missing MugZee passive power')
   if powers:self._replace_primary_power(owner,dict(card_id=powers[0],played=0))
   if len(powers)==2:p.secondary_power=dict(card_id=powers[1],played=0,used=False)

 def _mug_power(self,owner,cid):
  p=self.players[owner]
  return next((power for power in (p.primary_power,p.secondary_power) if power and power['card_id']==cid),None)

 def _mug_discount(self,owner,cid):
  p=self.players[owner]
  return 2 if self.cards[cid]['type']=='MINION' and p.turns_taken>=3 and not p.minion_played_this_turn and self._mug_power(owner,'JAIL_800hp1') else 0

 def _mug_play_operations(self,owner,cid,operations):
  if self.cards[cid]['type']!='MINION':return operations
  power=self._mug_power(owner,'JAIL_800hp2')
  if power is None:return operations
  power['played']=(power.get('played',0)+1)%5
  return list(operations)*2 if power['played']==0 and 'BATTLECRY' in self.cards[cid].get('mechanics',[]) else operations

 def _historical_starting_rules(self):
  from .generation_cards import pool
  from .identities import canonical_identity
  from .genn import POWERS
  for owner,p in enumerate(self.players):
   ids=self._opening_effect_ids(owner)
   if 'GIL_692' in ids and all(self._starting_card_data(owner,cid)['cost']%2==0 for cid in p.starting_deck):p.historical_genn=True
   if 'GIL_826' in ids and all(self._starting_card_data(owner,cid)['cost']%2==1 for cid in p.starting_deck):
    power=POWERS[p.starting_hero_class]
    self._replace_primary_power(owner,dict(card_id=power,upgraded_starting_class=p.starting_hero_class,cost=self.cards[power]['cost']))
   if 'SW_448' in ids and all(self.cards[cid].get('spellSchool')=='SHADOW' for cid in p.starting_deck if self.cards[cid]['type']=='SPELL'):
    upgraded=p.primary_power is not None and p.primary_power.get('upgraded_starting_class')=='PRIEST'
    self._replace_primary_power(owner,dict(card_id='EX1_625t2' if upgraded else 'EX1_625t'))
   for _ in range(ids.count('GDB_234')):
    cards=[Card(self._new_id(),'GDB_234t') for _ in range(7)]
    p.deck.extend(cards)
    self.rng.shuffle(p.deck);self._record_deck_insertion(owner,owner,7,'shuffle',cards=cards)
   # Original-deck parity checks above precede replacement and opening draws.
   from .historical_copy_batches import CTHUN_PIECES
   shattered=[card for card in p.deck if self._card_data(card)['id']=='DMF_254']
   for card in shattered:
    p.deck.remove(card)
    p.deck.extend(Card(self._new_id(),cid) for cid in CTHUN_PIECES)
   if shattered:
    self.rng.shuffle(p.deck)
    self._log('historical_cthun_shattered',player=owner,count=len(shattered))
   for _ in range(ids.count('KAR_096')):
    values=self._generation_candidates(pool(card_type='MINION',rarity='LEGENDARY',classes='own_or_neutral'),owner)
    excluded={canonical_identity(self._card_data(card),self.cards) for card in p.deck+p.hand}
    values=[cid for cid in values if canonical_identity(self.cards[cid],self.cards) not in excluded]
    chosen=self.rng.sample(list(values),min(5,len(values)))
    cards=[Card(self._new_id(),cid) for cid in chosen]
    p.deck.extend(cards)
    if chosen:self.rng.shuffle(p.deck);self._record_deck_insertion(owner,owner,len(chosen),'shuffle',cards=cards)
