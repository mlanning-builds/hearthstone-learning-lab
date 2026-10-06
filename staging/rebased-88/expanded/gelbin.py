"""Staged Gelbin and explicit physical Aura placement, separate from casting.

Membership comes from the frozen PALADIN_AURA XML tag. Historical/context-only
members are recognized and rejected until their effects are connected.
"""
from engine.game import Card
from engine.cards import UnsupportedCard

AURA_IDS=frozenset(('CATA_480','EDR_259e1','END_011','GDB_140','JAIL_327','LEG_TTN_908',
 'TIME_009t1','TIME_009t2','TIME_700','TOY_808','TTN_851','TTN_854','TTN_908','VAC_922','WW_341'))
AURA_RULES={
 'CATA_480':('none',[('repeat_end_effects',3)]),
 'END_011':('none',[('schedule_turn_effect','start',1,3,(('temporary_mana',1),))]),
 'JAIL_327':('none',[('schedule_turn_effect','end',0,3,(('summon_from_zone','deck',(('cost','le',2),)),))]),
 'TIME_700':('none',[('schedule_turn_effect','end',0,3,(('summon','TIME_700t',1),))]),
 'TTN_851':('none',[('resistance_aura',)]),
 'EDR_259e1':('none',[('schedule_stored_payload',)]),
 'TIME_009t1':('none',[('schedule_turn_effect','end',0,3,(('area_heal',4),))]),
 'TIME_009t2':('none',[('schedule_turn_effect','end',0,3,(('aura_random_shield_buff',4,4),))]),
}
RULES={'TIME_009':('none',[('gelbin_auras',)])}
TOKEN_RULES={cid:AURA_RULES[cid] for cid in ('TIME_009t1','TIME_009t2')}

class Gelbin:
 def _gelbin_candidates(self,owner):
  candidates=[c for c in self.players[owner].deck if self._card_data(c)['id'] in AURA_IDS]
  for card in candidates:
   cid=self._card_data(card)['id']
   if cid not in AURA_RULES:raise UnsupportedCard('Aura placement is not implemented: '+cid)
   if cid=='EDR_259e1':
    stored=getattr(card,'stored_spell',None);duration=getattr(card,'aura_duration',None)
    if stored is None or type(duration) is not int or duration<1 or not self._supports_internal_spell(stored.card_id):
     raise UnsupportedCard('Aura placement lacks an executable stored spell payload')
   if cid=='TIME_700' and 'TIME_700t' not in self.cards:raise UnsupportedCard('Missing Chronological Aura Dragon')
  return candidates

 def _gelbin_preflight(self,cid,owner):
  if cid=='TIME_009':self._gelbin_candidates(owner)

 def _gelbin_split(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='gelbin_auras':
   groups={}
   for card in self._gelbin_candidates(owner):
    data=self._card_data(card);key=data.get('countAsCopyOfDbfId',data.get('dbfId',data['id']))
    groups.setdefault(key,[]).append(card)
   selected=[copies[0] if len(copies)==1 else self.rng.choice(copies) for copies in groups.values()]
   # Convert synthetic string fixtures to physical cards before capturing refs.
   for i,card in enumerate(selected):
    if not isinstance(card,Card):
     index=p.deck.index(card);card=Card(self._new_id(),card);p.deck[index]=card;selected[i]=card
   operations=[('gelbin_place',card) for card in selected]
   if not operations:return ('batch30_noop',),()
   first,tail=self._gelbin_split(operations[0],ctx)
   return first,tuple(tail)+tuple(operations[1:])
  if op[0]=='gelbin_place':
   card=op[1]
   if not any(c is card for c in p.deck):return ('batch30_noop',),()
   p.deck.remove(card);self._refresh_auras()
   self._log('aura_placed',player=owner,card=card.card_id)
   context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,
                spell=False,card_id=card.card_id,physical_card=card)
   # Replay only the placement operations. No cast wrapper/history/listener,
   # Secret check, Overload, mana payment, or spell-repeat consumer is involved.
   return self._replay_split(('replay_context',tuple(AURA_RULES[card.card_id][1]),context),ctx)
  return None

 def _gelbin_effect(self,op,ctx):
  if op[0]!='aura_random_shield_buff':return False
  minions=self.players[ctx['owner']].minions
  if minions:
   m=self.rng.choice(minions);self._buff(m,op[1],op[2]);m.keywords.add('DIVINE_SHIELD')
  return True
