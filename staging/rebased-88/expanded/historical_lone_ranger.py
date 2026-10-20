"""Lone Ranger's neutral hero replacement and seven random magic bullets.

The pinned Battlecry removes active enemy minions only. No obsolete one-slot
board restriction is applied. Newly authored integration remains unvalidated.
"""
from .historical_utility_spells import RENO_BULLETS
from engine.cards import UnsupportedCard
STAGED_RULES={'WW_0700':('none',[('historical_utility_reno_clear',)])}

def rotate(game,owner):
 power=game.players[owner].primary_power
 if power is None or power['card_id'] not in RENO_BULLETS+('WW_0700p',):return
 # Each bullet is a replacement Hero Power, so temporary modifications to
 # the outgoing physical power do not carry to the new power.
 contract=getattr(game,'reno_bullet_contract',None)
 if not isinstance(contract,dict) or not contract.get('source'):
  raise UnsupportedCard('Reno requires a reviewed initial and transition bullet distribution')
 # Validate every future transition before consuming RNG or replacing a power.
 transitions=contract.get('transitions')
 if not isinstance(transitions,dict) or set(transitions)!=set(RENO_BULLETS):
  raise UnsupportedCard('Reno contract must cover all seven transition rows')
 rows=[contract.get('initial')]+[transitions[cid] for cid in RENO_BULLETS]
 for row in rows:
  if not isinstance(row,dict) or set(row)!=set(RENO_BULLETS):
   raise UnsupportedCard('Reno distribution must explicitly account for every bullet')
  if any(type(value) is not int or value<0 for value in row.values()) or not sum(row.values()):
   raise UnsupportedCard('Invalid Reno bullet weights')
 weights=rows[0] if power['card_id']=='WW_0700p' else transitions[power['card_id']]
 cid=game.rng.choices(RENO_BULLETS,weights=[weights[cid] for cid in RENO_BULLETS],k=1)[0]
 game._replace_primary_power(owner,dict(card_id=cid))
 game._log('reno_power_changed',player=owner,card=cid)
