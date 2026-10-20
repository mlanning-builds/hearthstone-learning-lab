"""Explicit pack distributions, preflighted in full before consuming randomness.

Supports joint outcomes and explicitly independent weighted slots. This module
supplies no retail-pack assumptions or default distribution for Avatar.
"""
from engine.cards import UnsupportedCard
from engine.game import Card
from .automatic_cards import validate_automatic_card


def sample_pack(game, contract, owner, *, validator=None):
 validate=validate_automatic_card if validator is None else validator
 if not isinstance(contract, dict) or not contract.get('source'):
  raise UnsupportedCard('Missing reviewed in-game Standard pack distribution')
 model=contract.get('model','joint')
 if model=='rarity_patterns':return sample_rarity_patterns(game,contract,owner,validator=validate)
 if model=='joint':
  groups=(contract.get('outcomes'),)
 elif model=='independent_slots':
  groups=contract.get('slots')
  if not isinstance(groups,(tuple,list)) or len(groups)!=5:
   raise UnsupportedCard('A pack requires exactly five explicit slot distributions')
 else:
  raise UnsupportedCard('Unknown pack distribution model')
 prepared=[]
 for group in groups:
  if not isinstance(group,(tuple,list)) or not group:
   raise UnsupportedCard('Empty pack distribution')
  values=[];weights=[]
  for entry in group:
   if not isinstance(entry,(tuple,list)) or len(entry)!=2:
    raise UnsupportedCard('Invalid weighted pack entry')
   weight,value=entry
   if type(weight) is not int or weight<=0:
    raise UnsupportedCard('Invalid pack outcome weight')
   ids=value if model=='joint' else (value,)
   if not isinstance(ids,(tuple,list)) or len(ids)!=(5 if model=='joint' else 1):
    raise UnsupportedCard('Invalid pack outcome size')
   if any(not isinstance(cid,str) or not cid for cid in ids):
    raise UnsupportedCard('Invalid pack card identity')
   for cid in ids:validate(game,Card(-1,cid),owner)
   values.append(tuple(ids) if model=='joint' else value);weights.append(weight)
  prepared.append((values,weights))
 # Every possible identity has been checked, including later slots. A missing
 # implementation fails before RNG consumption or any card/zone mutation.
 if model=='joint':
  values,weights=prepared[0]
  return tuple(game.rng.choices(values,weights=weights,k=1)[0])
 return tuple(game.rng.choices(values,weights=weights,k=1)[0] for values,weights in prepared)


def prepare_rarity_patterns(game,contract,owner,validator):
 """Explicit joint rarity patterns with explicit conditional identity weights.

 This is a declared factorization, not an assumption about retail/in-game pack
 odds. No defaults, pity timers or duplicate protection are inferred.
 """
 patterns=contract.get('patterns');pools=contract.get('rarity_pools')
 if not isinstance(patterns,(tuple,list)) or not patterns or not isinstance(pools,dict):raise UnsupportedCard('Missing explicit rarity patterns and identity pools')
 allowed={'COMMON','RARE','EPIC','LEGENDARY'}
 prepared={};identities=set();required=set();seen_patterns=set()
 for entry in patterns:
  if not isinstance(entry,(tuple,list)) or len(entry)!=2:raise UnsupportedCard('Invalid weighted rarity pattern')
  weight,pattern=entry
  if type(weight) is not int or weight<=0 or not isinstance(pattern,(tuple,list)) or len(pattern)!=5 or any(r not in allowed for r in pattern):raise UnsupportedCard('Pack rarity pattern requires five explicit rarities and a positive weight')
  key=tuple(pattern)
  if key in seen_patterns:raise UnsupportedCard('Duplicate pack rarity pattern')
  seen_patterns.add(key);required.update(pattern)
 if set(pools)!=required:raise UnsupportedCard('Pack identity pools must exactly cover used rarity labels')
 for rarity,entries in pools.items():
  if not isinstance(entries,(tuple,list)) or not entries:raise UnsupportedCard('Empty pack rarity identity pool')
  values=[];weights=[]
  for entry in entries:
   if not isinstance(entry,(tuple,list)) or len(entry)!=2:raise UnsupportedCard('Invalid weighted pack identity')
   weight,cid=entry
   if type(weight) is not int or weight<=0 or not isinstance(cid,str) or cid in identities:raise UnsupportedCard('Invalid or repeated pack identity')
   if cid not in game.cards or game.cards[cid].get('rarity')!=rarity:raise UnsupportedCard('Pack identity rarity mismatch')
   validator(game,Card(-1,cid),owner)
   identities.add(cid);values.append(cid);weights.append(weight)
  prepared[rarity]=(tuple(values),tuple(weights))
 return tuple((weight,tuple(pattern)) for weight,pattern in patterns),prepared

def sample_rarity_patterns(game,contract,owner,*,validator):
 patterns,pools=prepare_rarity_patterns(game,contract,owner,validator)
 # All identities in all rarity groups are checked before the first RNG call.
 pattern=game.rng.choices([p for _,p in patterns],weights=[w for w,_ in patterns],k=1)[0]
 return tuple(game.rng.choices(pools[rarity][0],weights=pools[rarity][1],k=1)[0] for rarity in pattern)
