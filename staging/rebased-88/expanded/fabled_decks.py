"""Frozen Fabled bundles for Constructed deck construction.

Every mapping comes from the named IS_FABLED_BUNDLE_CARD tags in the pinned
XML. Expanding a bundle does not admit its root or companions to the simulator.
"""
from collections import Counter

BUNDLES={
 'TIME_005':tuple('TIME_005t'+str(i) for i in range(1,10)),
 'TIME_009':('TIME_009t1','TIME_009t2'),
 'TIME_020':('TIME_020t1','TIME_020t2'),
 'TIME_209':('TIME_209t','TIME_209t2'),
 'TIME_211':('TIME_211t1','TIME_211t2'),
 'TIME_609':('TIME_609t1','TIME_609t2'),
 'TIME_619':('TIME_619t','TIME_619t2'),
 'TIME_850':('TIME_850t','TIME_850t1'),
 'TIME_852':('TIME_852t1','TIME_852t3'),
 'TIME_875':('TIME_875t','TIME_875t1'),
 'TIME_890':('TIME_890t','TIME_890t2'),
}
COMPANION_ROOT={cid:root for root,ids in BUNDLES.items() for cid in ids}


def expand_bundle_ids(ids):
 """Accept selected roots or an already-expanded deck; never add twice.

 Companions occupy deck slots. Normal bundles need 28 selected cards including
 the root for a 30-card deck; Rafaam needs 31 selected cards for a 40-card deck.
 Explicit companion entries are permitted only alongside their owning root.
 """
 result=list(ids);counts=Counter(result)
 for root,companions in BUNDLES.items():
  if counts[root]>1:raise ValueError('A Fabled root may appear only once: '+root)
  for cid in companions:
   if counts[cid] and not counts[root]:raise ValueError('Fabled companion requires its root: '+cid)
   if counts[cid]>1:raise ValueError('A Fabled companion may appear only once: '+cid)
  if counts[root]:result.extend(cid for cid in companions if not counts[cid])
 return tuple(result)


def deck_size(ids):
 return 20 if 'JAIL_430' in ids else 40 if 'TIME_005' in ids else 30


def companion_ids(ids):
 return frozenset(cid for root,values in BUNDLES.items() if root in ids for cid in values)


def sample_bundle_slots(slots,seed):
 """Seeded baseline construction treating each root/bundle as one unit.

 This is a reproducible heuristic, not a uniform distribution over legal decks.
 Ordinary deck construction retains its existing sampler when no roots exist.
 """
 import random
 candidates=list(slots);random.Random(seed).shuffle(candidates)
 selected=[];used=0;target=30
 for cid in candidates:
  if cid in COMPANION_ROOT:raise ValueError('Sample roots, not standalone companions')
  if cid in BUNDLES and cid in selected:continue
  # Size modifiers must be selected before too many physical slots are used.
  # Conflicting modifiers cannot coexist in the submitted deck.
  if cid=='JAIL_430' and any(x in selected for x in ('TIME_005','REV_018')):continue
  if cid in ('TIME_005','REV_018') and 'JAIL_430' in selected:continue
  limit=20 if cid=='JAIL_430' else 40 if cid=='TIME_005' else target
  cost=1+len(BUNDLES.get(cid,()))
  if used+cost>limit:continue
  selected.append(cid);used+=cost;target=limit
  if used==target:return tuple(selected)
 raise ValueError('Not enough slots to complete a legal Fabled deck')
