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
class MinionForge:
 def _forge_pool(self,kind,stage,owner,first=None):
  contract=getattr(self,'forge_contracts',{}).get((kind,stage))
  if not contract:raise UnsupportedCard('Missing complete reviewed forge pool: '+kind+'/'+str(stage))
  result=[]
  for part in contract:
   if not isinstance(part,ForgePart) or not part.source or part.card_id not in self.cards:raise UnsupportedCard('Unreviewed forge component')
   d=self.cards[part.card_id]
   if d.get('type')!='MINION':raise UnsupportedCard('Forge component must be a minion')
   if first is None or d['cost']+self.cards[first.card_id]['cost']<=10:result.append(part)
  return result
 def _forge_offer(self,owner,kind,discount,first=None):
  parts=self._forge_pool(kind,1 if first is None else 2,owner,first)
  if not parts:return
  offered=self.rng.sample(parts,min(3,len(parts)))
  self.pending_choice=dict(owner=owner,kind='forge_part',forge_kind=kind,discount=discount,first=first,
    parts=offered,options=[dict(card_id=p.card_id) for p in offered]);self.phase='choice'
 def _forge_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='forge_dragon':
   self._forge_pool('dragon',1,owner);self._forge_pool('dragon',2,owner)
   self._forge_offer(owner,'dragon',3 if any(has_tribe(self._card_data(c),'DRAGON') for c in p.hand) else 0)
  elif op[0]=='forge_zombeast':self._forge_offer(owner,'zombeast',3)
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
  part=next(p for p in choice['parts'] if p.card_id==selected['card_id']);first=choice['first'];owner=choice['owner']
  if first is None:self._forge_offer(owner,choice['forge_kind'],choice['discount'],part);return True
  a,b=self.cards[first.card_id],self.cards[part.card_id]
  modes={p.target for p in (first,part) if p.target!='none'}
  if len(modes)>1:raise UnsupportedCard('Incompatible composite Battlecry targets require a reviewed resolver')
  cid='CATA_470t1' if choice['forge_kind']=='dragon' else 'ICC_828t'
  if cid not in self.cards:raise UnsupportedCard('Missing composite minion token')
  c=Card(self._new_id(),cid);c.base_stat_override=(a['attack']+b['attack'],a['health']+b['health'])
  c.set_cost=a['cost']+b['cost'];c.cost_delta=-choice['discount']
  c.rule_state=dict(crafted_target=next(iter(modes),'none'),crafted_ops=first.operations+part.operations,
    forge_parts=(first.card_id,part.card_id),forge_keywords=tuple(sorted(set(first.keywords+part.keywords))),forge_death=first.death_operations+part.death_operations)
  self._discovery_result=self._enter_hand(owner,c)
  return True
 def _forge_entry(self,minion,card):
  state=getattr(card,'rule_state',{})
  if minion is None or 'forge_parts' not in state:return
  minion.rule_state.update(deepcopy(state));minion.keywords.update(state['forge_keywords'])
  if state['crafted_ops']:minion.keywords.add('BATTLECRY')
  minion.attached_death_effects.extend(deepcopy(state['forge_death']))
