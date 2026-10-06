"""Opening Essence split and a captured contiguous hand chain."""
from engine.game import Card
from engine.cards import UnsupportedCard
ROOT='CATA_EVENT_110'
ESSENCES=tuple(ROOT+'t'+str(n) for n in range(2,8))
RULES={ROOT:('none',[])}
TOKEN_RULES={
 ESSENCES[0]:('enemy_character',[('damage',8),('essence_chain',)]),
 ESSENCES[1]:('none',[('filtered_draw',(('type','eq','SPELL'),),3),('essence_chain',)]),
 ESSENCES[2]:('none',[('refresh_mana',8),('essence_chain',)]),
 ESSENCES[3]:('none',[('armor',12),('essence_chain',)]),
 ESSENCES[4]:('none',[('summon',ROOT+'t6t',1),('essence_chain',)]),
 ESSENCES[5]:('none',[('area_damage','enemy_minions',4),('essence_chain',)]),
}
class DragonSoul:
 def _essence_setup(self):
  for p in self.players:
   if not any(self._card_data(c)['id']==ROOT for c in p.deck):continue
   missing=[cid for cid in ESSENCES if cid not in self.cards]
   if missing:raise UnsupportedCard('Missing Dragon Soul Essences: '+', '.join(missing))
   result=[]
   for c in p.deck:
    if self._card_data(c)['id']==ROOT:result.extend(Card(self._new_id(),cid) for cid in ESSENCES)
    else:result.append(c)
   p.deck=result;self.rng.shuffle(p.deck)
 def _essence_neighbors(self,card,owner):
  hand=self.players[owner].hand
  if card.card_id not in ESSENCES or card not in hand:return ()
  index=hand.index(card);left=index;right=index+1
  while left>0 and hand[left-1].card_id in ESSENCES:left-=1
  while right<len(hand) and hand[right].card_id in ESSENCES:right+=1
  return tuple(c.uid for c in hand[left:right] if c is not card)
 def _essence_split(self,op,ctx):
  if op[0]!='essence_chain':return None
  p=self.players[ctx['owner']];ids=ctx.get('essence_neighbors',())
  cards=[c for uid in ids for c in p.hand if c.uid==uid and c.card_id in ESSENCES]
  for c in cards:
   if not self._supports_internal_spell(c.card_id):raise UnsupportedCard('Essence lacks internal cast support: '+c.card_id)
  for c in cards:p.hand.remove(c)
  return ('batch30_noop',),tuple(('cast_physical_spell',c,'random') for c in cards)
