"""Final exceptional consumers with explicit distribution and immunity gates.

Pack outcomes and suspicious mutations require reviewed distributions. Missing
contracts fail before sampling; broad uniform guesses are not substituted.
"""
from copy import deepcopy
from engine.cards import UnsupportedCard
from engine.game import Card
from .generation_cards import pool
from .selectors import has_school
from .automatic_cards import validate_automatic_card
FIRE=pool(card_type='SPELL',school='FIRE',maximum=15)
MINIONS=pool(card_type='MINION',classes='own_or_neutral')
RULES={'CORE_WON_145':('none',[('standard_pack',)]),
 'JAIL_EVENT_100':('none',[('suspicious_discover',)]),
 'FIR_959':('none',[('fyrakk_budget',15,0)])}
def requests_for(cid):return {FIRE} if cid=='FIR_959' else {MINIONS} if cid=='JAIL_EVENT_100' else set()
class ExceptionalFinish:
 def _fire_immune_target(self,target,context=None):
  ctx=context if context is not None else getattr(self,'_active_effect_context',{})
  if not ctx.get('spell') or not has_school(self.cards.get(ctx.get('card_id'),{}),'FIRE'):return False
  m=self._force_live(target) if target>0 else None
  return m is not None and m.card_id=='FIR_959' and not m.silenced
 def _fire_effect_guard(self,op,ctx):
  if not ctx.get('spell') or not has_school(self.cards.get(ctx.get('card_id'),{}),'FIRE'):return False
  if not any(m.card_id=='FIR_959' and not m.silenced for p in self.players for m in p.minions):return False
  targeted={'destroy','buff','keyword','freeze','heal','heal_full','set_target_stats','silence','bounce','transform','mutation_life_cycle'}
  if op[0] in targeted and self._fire_immune_target(ctx.get('target',0),ctx):return True
  # Global destruction/stat/zone operations filter their affected entities.
  return False
 def _finish_split(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner]
  if name=='fyrakk_budget':
   remaining,steps=op[1:]
   values=self._autocast_candidates(FIRE,owner)
   if remaining<=0:return ('batch30_noop',),()
   if steps>=256:raise UnsupportedCard('Fire budget chain exceeded bounded depth')
   eligible=[cid for cid in values if self.cards[cid]['cost']<=remaining]
   if not eligible:return ('batch30_noop',),()
   cid=self.rng.choice(eligible)
   return ('batch30_noop',),(('cast_fixed_spell',cid,'enemies'),('fyrakk_budget',remaining-self.cards[cid]['cost'],steps+1))
  if name=='standard_pack':
   contract=getattr(self,'standard_pack_contract',None)
   if not contract or not contract.get('source'):raise UnsupportedCard('Missing reviewed in-game Standard pack distribution')
   outcomes=contract.get('outcomes',())
   if not outcomes:raise UnsupportedCard('Empty pack distribution')
   for weight,ids in outcomes:
    if type(weight) is not int or weight<=0 or len(ids)!=5:raise UnsupportedCard('Invalid pack outcome')
    for cid in ids:validate_automatic_card(self,Card(-1,cid))
   ids=self.rng.choices([ids for weight,ids in outcomes],weights=[weight for weight,ids in outcomes],k=1)[0]
   cards=[self._add(owner,cid) for cid in ids];cards=[c for c in cards if c is not None]
   return ('batch30_noop',),tuple(('pack_play',c.uid) for c in cards)
  if name=='pack_play':
   card=next((c for c in p.hand if c.uid==op[1]),None)
   if card is None:return ('batch30_noop',),()
   validate_automatic_card(self,card);p.hand.remove(card)
   return ('batch30_noop',),(('automatic_card',card,'random'),)
 def _finish_effect(self,op,ctx):
  if op[0]!='suspicious_discover':return False
  owner=ctx['owner'];values=self._generation_discover_candidates(MINIONS,ctx)
  contract=getattr(self,'suspicious_mutation_contract',None)
  if not contract or not contract.get('source'):raise UnsupportedCard('Missing reviewed suspicious mutation distribution')
  mutations=contract.get('mutations',())
  if not mutations or any(m.get('field') not in ('attack','health','cost') or type(m.get('delta')) is not int or not m['delta'] for m in mutations):
   raise UnsupportedCard('Suspicious name/tribe replacement needs complete identity overlays')
  if not values:return True
  ids=self.rng.sample(list(values),min(3,len(values)));suspect=self.rng.randrange(len(ids));mutation=self.rng.choice(mutations);options=[];cards=[]
  for index,cid in enumerate(ids):
   card=Card(self._new_id(),cid);d=self.cards[cid]
   if index==suspect:
    field=mutation['field'];delta=mutation['delta']
    if field=='cost':self._set_card_cost(card,max(0,d['cost']+delta))
    else:setattr(card,field+'_bonus',max(1 if field=='health' else 0,d[field]+delta)-d[field])
   options.append(dict(card_id=cid,attack=d['attack']+card.attack_bonus,health=d['health']+card.health_bonus,cost=self._cost(card,owner)))
   cards.append(card)
  self.pending_choice=dict(owner=owner,kind='suspicious_discover',options=options,cards=cards,suspect=suspect,source_uid=getattr(ctx.get('source'),'uid',None));self.phase='choice';return True
 def _finish_choice(self,choice,selected):
  if choice['kind']!='suspicious_discover':return False
  index=choice['options'].index(selected);owner=choice['owner']
  self._discovery_result=self._enter_hand(owner,choice['cards'][index])
  if index==choice['suspect']:
   source=self._force_live(choice['source_uid']) if choice['source_uid'] else None
   if source and source.owner==owner:self._buff(source,1,1)
  return True
