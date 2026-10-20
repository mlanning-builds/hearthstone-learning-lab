"""Full Wisdomball execution pipeline; exact usefulness evaluator still gated.

A sourced evaluator supplies weighted spell/target outcomes, not arbitrary
operations. No guessed usefulness thresholds or replacement AI is installed.
"""
from engine.cards import UnsupportedCard
from dataclasses import dataclass
from copy import deepcopy
from .pools import require_fixed_cards
SPELLS=('CS2_023','CS2_032','CS2_022','EX1_277','CS2_027','EX1_287','EX1_289','CS2_028','CS2_024','CS2_029')
STAGED_RULES={'TOY_373':('none',[('equip','TOY_373t')]),'TOY_373t':('none',[])}

@dataclass(frozen=True)
class WisdomballPolicy:
 source: str
 build: str
 pool: tuple
 evaluator: object
 complete: bool=False
 approximate: bool=False

def checked_policy(game):
 policy=getattr(game,'wisdomball_policy',None)
 if not isinstance(policy,WisdomballPolicy) or (policy.complete is not True and policy.approximate is not True) or policy.build!='36.6.0.251952' or not isinstance(policy.source,str) or not policy.source.strip() or not callable(policy.evaluator):
  raise UnsupportedCard('Missing complete sourced pinned Wisdomball policy')
 if not isinstance(policy.pool,tuple) or len(policy.pool)!=len(SPELLS) or set(policy.pool)!=set(SPELLS):
  raise UnsupportedCard('Wisdomball policy must retain the complete ten-spell pool')
 return policy


def turn_entries(game,phase):
 if phase!='end':return []
 p=game.players[game.current];weapon=p.weapon;card=p.equipped_card
 if not weapon or weapon['card_id']!='TOY_373t' or card is None:return []
 return [dict(source=None,order=card.uid,operations=(('historical_wisdomball_cast',card.uid),))]

def split(game,op,ctx):
 if op[0]!='historical_wisdomball_cast':return None
 owner=ctx['owner'];p=game.players[owner];weapon=p.weapon;card=p.equipped_card
 if not weapon or weapon['card_id']!='TOY_373t' or getattr(card,'uid',None)!=op[1]:return ('batch30_noop',),()
 require_fixed_cards(SPELLS,game.cards)
 if any(not game._supports_internal_spell(cid,owner) for cid in SPELLS):raise UnsupportedCard('Wisdomball spell dependency is not executable')
 policy=checked_policy(game)
 from .historical_zephrys import public_snapshot
 # The selection policy receives public combat information, never live state
 # or concealed hand/deck/Secret identities.
 state=deepcopy(public_snapshot(game,owner))
 state['wisdomball']=dict(card_id='TOY_373t',durability=weapon['durability'],pool=SPELLS)
 contract=policy.evaluator(state)
 if not isinstance(contract,dict):raise UnsupportedCard('Malformed Wisdomball evaluation')
 if 'useful_spells' in contract:
  from .cards import RULES
  useful=contract['useful_spells']
  if not isinstance(useful,(tuple,list)) or len(set(useful))!=len(useful) or any(cid not in SPELLS for cid in useful):raise UnsupportedCard('Invalid useful-spell list')
  groups=[]
  for cid in useful:
   targets=game._targets_for(cid,owner,RULES[cid][0])
   targets=[t for t in targets if not t or t==game.hero_id(1-owner) or any(m.uid==t for m in game.players[1-owner].minions)]
   if cid in ('EX1_287','EX1_289') and any(c.card_id==cid for c in p.secrets):continue
   if targets:groups.append((cid,targets))
  if not groups:return ('batch30_noop',),(('historical_wisdomball_wear',card.uid),)
  cid,targets=game.rng.choice(groups);target=game.rng.choice(targets)
  cast_context=dict(ctx,target=target)
  return ('batch30_noop',),(('replay_context',(('cast_fixed_spell',cid,'selected'),),cast_context),('historical_wisdomball_wear',card.uid))
 outcomes=contract.get('outcomes')
 if not isinstance(outcomes,(list,tuple)) or not outcomes:raise UnsupportedCard('Empty Wisdomball evaluation')
 values=[];weights=[];seen=set()
 for row in outcomes:
  if not isinstance(row,(list,tuple)) or len(row)!=3:raise UnsupportedCard('Malformed Wisdomball outcome')
  weight,cid,target=row
  if type(weight) is not int or weight<=0 or cid not in SPELLS or type(target) is not int:raise UnsupportedCard('Invalid Wisdomball outcome')
  from .cards import RULES
  allowed=game._targets_for(cid,owner,RULES[cid][0])
  if target not in allowed:raise UnsupportedCard('Wisdomball evaluator selected an illegal target')
  if target and target!=game.hero_id(1-owner) and not any(m.uid==target for m in game.players[1-owner].minions):raise UnsupportedCard('Wisdomball targets must be enemies')
  if (cid,target) in seen:raise UnsupportedCard('Repeated Wisdomball spell/target outcome')
  seen.add((cid,target))
  values.append((cid,target));weights.append(weight)
 cid,target=game.rng.choices(values,weights=weights,k=1)[0]
 cast_context=dict(ctx,target=target)
 return ('batch30_noop',),(('replay_context',(('cast_fixed_spell',cid,'selected'),),cast_context),('historical_wisdomball_wear',card.uid))

def execute(game,op,ctx):
 if op[0]!='historical_wisdomball_wear':return False
 p=game.players[ctx['owner']]
 if p.weapon and p.weapon['card_id']=='TOY_373t' and getattr(p.equipped_card,'uid',None)==op[1]:
  p.weapon['durability']-=1
  if p.weapon['durability']<=0:game._break_weapon(ctx['owner'])
 return True
