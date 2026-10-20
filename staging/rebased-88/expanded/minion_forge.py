"""Physical two-part minion construction using explicit reviewed part contracts.

Curated Wild/Standard component pools are supplied separately. No text-length
heuristic, collectible-only approximation or supported-only fallback is used.
"""
from copy import deepcopy
from dataclasses import dataclass
from engine.game import Card
from engine.cards import UnsupportedCard
from .selectors import has_tribe
RULES={'CATA_470':('none',[('forge_dragon',)]),'TLC_EVENT_400':('none',[('forge_sidequest',)])}
TOKEN_RULES={'CATA_470t1':('none',[]),'ICC_828t':('none',[])}
@dataclass(frozen=True)
class ForgePart:
 card_id:str
 target:str='none'
 operations:tuple=()
 death_operations:tuple=()
 # A contract must explicitly cover all intrinsic behavior of this component.
 keywords:tuple=()
 source:str=''
 intrinsics:tuple=()
class MinionForge:
 def _forge_pool(self,kind,stage,owner,first=None):
  contract=getattr(self,'forge_contracts',{}).get((kind,stage))
  if not contract:raise UnsupportedCard('Missing complete reviewed forge pool: '+kind+'/'+str(stage))
  if not isinstance(contract,(tuple,list)):raise UnsupportedCard('Forge pool must be an explicit component sequence')
  result=[];seen=set()
  for part in contract:
   if not isinstance(part,ForgePart) or not part.source or part.card_id not in self.cards:raise UnsupportedCard('Unreviewed forge component')
   if part.card_id in seen:raise UnsupportedCard('Duplicate forge component identity')
   seen.add(part.card_id)
   if not isinstance(part.target,str) or not isinstance(part.operations,tuple) or not isinstance(part.death_operations,tuple) or not isinstance(part.keywords,tuple):raise UnsupportedCard('Invalid forge component payload shape')
   from .effect_schema import validate_operations,EffectSchemaError
   try:
    validate_operations(part.operations,'forge['+part.card_id+'].operations',strict_unknown=True)
    validate_operations(part.death_operations,'forge['+part.card_id+'].death_operations',strict_unknown=True)
   except EffectSchemaError as exc:raise UnsupportedCard(str(exc)) from exc
   if any(not isinstance(keyword,str) for keyword in part.keywords):raise UnsupportedCard('Invalid forge component keyword')
   from .forge_intrinsics import validate_intrinsics
   validate_intrinsics(part.intrinsics,'forge['+part.card_id+']')
   d=self.cards[part.card_id]
   if any(type(d.get(field)) is not int or d[field]<0 for field in ('cost','attack','health')):raise UnsupportedCard('Invalid forge component base statistics')
   if d.get('type')!='MINION':raise UnsupportedCard('Forge component must be a minion')
   if first is None or d['cost']+self.cards[first.card_id]['cost']<=10:result.append(part)
  return result
 def _forge_offer(self,owner,kind,discount,first=None):
  if type(discount) is not int or discount<0:raise UnsupportedCard('Invalid composite discount')
  if first is not None:
   first_ids={part.card_id for part in self._forge_pool(kind,1,owner)}
   if first.card_id not in first_ids:raise UnsupportedCard('First composite part is outside the complete stage-one pool')
  parts=self._forge_pool(kind,1 if first is None else 2,owner,first)
  if first is None:
   # Keep only first parts with an affordable completion; the discount is
   # applied after construction and must not widen the base ten-mana cap.
   parts=[part for part in parts if self._forge_pool(kind,2,owner,part)]
  if not parts:raise UnsupportedCard('Reviewed forge pool has no legal completion: no legal second component')
  if self.pending_choice is not None:raise UnsupportedCard('Forge cannot overwrite an active choice')
  offered=self.rng.sample(parts,min(3,len(parts)))
  self.pending_choice=dict(owner=owner,kind='forge_part',forge_kind=kind,discount=discount,first=first,
    parts=offered,options=[dict(card_id=p.card_id) for p in offered]);self.phase='choice'
 def _forge_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='forge_dragon':
   self._forge_pool('dragon',1,owner);self._forge_pool('dragon',2,owner)
   self._forge_offer(owner,'dragon',3 if any(has_tribe(self._card_data(c),'DRAGON') for c in p.hand) else 0)
  elif op[0] in ('forge_zombeast','forge_zombeast_plain'):
   # Storm grants a three-mana reduction; Rexxar and Scourge Tamer do not.
   discount=3 if op[0]=='forge_zombeast' else 0
   self._forge_offer(owner,'zombeast',discount)
  elif op[0]=='forge_sidequest':
   quests=getattr(p,'forge_sidequests',[])
   if quests:raise UnsupportedCard('Duplicate Storm the Gates sidequest')
   p.forge_sidequests=[dict(card_id='TLC_EVENT_400',progress=0,total=3)]
  else:return False
  return True
 def _forge_played(self,owner,card):
  p=self.players[owner];d=self._card_data(card)
  if d.get('type')!='MINION' or not (has_tribe(d,'BEAST') or has_tribe(d,'UNDEAD')):return
  for q in list(getattr(p,'forge_sidequests',[])):
   q['progress']+=1
   if q['progress']>=3:
    p.forge_sidequests.remove(q)
    self._rule_events.append(('captured_effects',dict(operations=(('forge_zombeast',),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
 def _forge_choice(self,choice,selected):
  if choice['kind']!='forge_part':return False
  matches=[p for p in choice['parts'] if p.card_id==selected.get('card_id')]
  if len(matches)!=1:raise UnsupportedCard('Selected forge component was not offered')
  part=matches[0];first=choice['first'];owner=choice['owner']
  if first is None:self._forge_offer(owner,choice['forge_kind'],choice['discount'],part);return True
  a,b=self.cards[first.card_id],self.cards[part.card_id]
  modes={p.target for p in (first,part) if p.target!='none'}
  if len(modes)>1:raise UnsupportedCard('Incompatible composite Battlecry targets require a reviewed resolver')
  cid='CATA_470t1' if choice['forge_kind']=='dragon' else 'ICC_828t'
  if cid not in self.cards:raise UnsupportedCard('Missing composite minion token')
  c=Card(self._new_id(),cid);c.base_stat_override=(a['attack']+b['attack'],a['health']+b['health'])
  c.set_cost=a['cost']+b['cost'];c.cost_delta=-choice['discount']
  c.rule_state=deepcopy(dict(crafted_target=next(iter(modes),'none'),crafted_ops=first.operations+part.operations,
    forge_parts=(first.card_id,part.card_id),forge_tribes=('ALL',) if any('ALL' in (data.get('races') or (data.get('race'),)) for data in (a,b)) else tuple(self.cards[cid].get('races',())),forge_keywords=tuple(sorted(set(first.keywords+part.keywords))),forge_death=first.death_operations+part.death_operations,
    forge_intrinsics=first.intrinsics+part.intrinsics))
  self._discovery_result=self._enter_hand(owner,c)
  return True
 def _forge_entry(self,minion,card):
  state=getattr(card,'rule_state',{})
  if card.card_id in TOKEN_RULES and 'forge_parts' not in state:raise UnsupportedCard('Composite minion has no physical component payload')
  if minion is None or 'forge_parts' not in state:return
  self._remember_crafted(card);self._carry_origin(card,minion)
  minion.rule_state.update(deepcopy(state));minion.keywords.update(state['forge_keywords'])
  if state['crafted_ops']:minion.keywords.add('BATTLECRY')
  minion.attached_death_effects.extend(deepcopy(state['forge_death']))
