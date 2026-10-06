"""Frozen Rafaam family effects, separate from the nine-card win checklist.

Baaaafam belongs to the effect family, but is not a required Fabled companion.
Historical Rafaams are not inferred from their displayed names.
"""
from .fabled_decks import BUNDLES
from .pools import deck_choice_options

REQUIRED=frozenset(BUNDLES['TIME_005'])
FAMILY=REQUIRED|{'TIME_005','TIME_005t9t'}
RULES={'TIME_005':('none',[('rafaam_win',)])}
TOKEN_RULES={
 'TIME_005t1':('none',[('rafaam_draw',)]),
 'TIME_005t2':('none',[('rafaam_buff',)]),
 'TIME_005t3':('none',[('rafaam_discover',)]),
 'TIME_005t4':('none',[('armor',5),('rafaam_holding',('armor',5))]),
 'TIME_005t5':('none',[('rafaam_holding',('copy_self_right',1))]),
 'TIME_005t6':('none',[('rafaam_damage',)]),
 'TIME_005t7':('none',[]),
 'TIME_005t8':('none',[('next_discount','RAFAAM',3,'permanent')]),
 'TIME_005t9':('none',[('rafaam_transform',)]),
 'TIME_005t9t':('none',[]),
}
DEATH_EFFECTS={'TIME_005t1':[('rafaam_draw',)]}

class Rafaam:
 def _rafaam_split(self,op,ctx):
  if op[0]!='rafaam_holding':return None
  held=any(c.card_id in FAMILY for c in self.players[ctx['owner']].hand)
  return (op[1] if held else ('batch30_noop',)),()

 def _rafaam_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner];source=ctx.get('source')
  if name=='rafaam_win':
   if REQUIRED<={e['card_id'] for e in p.played_history}:
    self.players[1-owner].health=0
    self._log('rafaam_destroy_hero',player=owner)
  elif name=='rafaam_draw':
   self._draw(owner,predicate=lambda data:data['id'] in FAMILY)
  elif name=='rafaam_buff':
   for card in p.hand:
    if card.card_id in FAMILY:card.attack_bonus+=2;card.health_bonus+=2
   for m in p.minions:
    if m is not source and m.card_id in FAMILY:self._buff(m,2,2)
  elif name=='rafaam_discover':
   indexed=[(i,c) for i,c in enumerate(p.deck) if self._card_data(c)['id'] in FAMILY]
   options=deck_choice_options([c for _,c in indexed],self.cards,3,self.rng)
   for option in options:option['index']=indexed[option['index']][0]
   if options:
    self.pending_choice=dict(owner=owner,kind='draw_from_deck',options=options)
    self.phase='choice'
  elif name=='rafaam_damage':
   targets=[m.uid for player in self.players for m in player.minions if m.card_id not in FAMILY]
   with self._damage_batch():
    for uid in targets:self._deal_effect(uid,6,ctx)
  elif name=='rafaam_transform':
   # Transformation replaces entities without invoking their Deathrattles.
   targets=[m for player in self.players for m in player.minions if m.card_id not in FAMILY]
   for m in targets:self._transform(m,'TIME_005t9t')
  else:return False
  return True
