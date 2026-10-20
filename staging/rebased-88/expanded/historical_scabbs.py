"""Scabbs' physical mass return and expiring next-card power discount."""
ROOT_RULES={'AV_203':('none',[('historical_scabbs_return',),('summon','AV_203t',2)])}
TOKEN_RULES={'AV_203t':('none',[])}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'AV_203p'}


def execute(game,op,ctx):
 if op[0]!='historical_scabbs_return':return False
 # Snapshot before any hand-entry response so a newly summoned minion is
 # never accidentally added to this return group. Locations are not minions.
 victims=tuple(m for player in game.players for m in player.minions if m.health>0 and not m.dormant)
 for minion in victims:
  if any(minion is m for player in game.players for m in player.minions) and minion.health>0:
   game._bounce(minion)
 return True
