"""Private physical snapshots of completed hand-play admission.

Records do not decide a replay consumer's eligibility or Battlecry semantics.
In particular, automatic execution and countered plays are not recorded here.
"""
from copy import deepcopy
from dataclasses import dataclass

@dataclass(frozen=True)
class ReplayRecord:
 turn: int
 owner: int
 card: object
 paid_cost: int
 choices: tuple
 target: int
 position: int

def capture_play(turn,owner,card,cost,action):
 return ReplayRecord(turn,owner,deepcopy(card),cost,tuple(action.choices),action.target,action.position)

def plays_for_turn(player,turn,exclude_uid=None):
 return tuple(deepcopy(r) for r in player.replay_history
              if r.turn==turn and r.card.uid!=exclude_uid)
