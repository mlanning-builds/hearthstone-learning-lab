"""Non-death minion removal and Reno's passive full-pool random spell."""
from .generation_cards import pool
SPELLS=pool(card_type='SPELL')
ROOT_RULES={'YOD_009':('none',[('historical_reno_poof',)])}
FIXED_TOKEN_IDS=frozenset(('YOD_009h',))


def turn_entries(game,phase):
 if phase!='start':return []
 power=game.players[game.current].primary_power
 if power is None or power['card_id']!='YOD_009h':return []
 return [dict(source=None,order=power['uid'],operations=(('autocast_random',SPELLS,1),))]


def execute(game,op,ctx):
 if op[0]!='historical_reno_poof':return False
 # Capture both sides before removing anything; no intermediate aura refresh
 # may turn this into death processing for a later member of the same group.
 victims=tuple((player,minion) for player in game.players for minion in player.minions)
 for player,minion in victims:
  player.board.remove(minion)
  game._pending_summon_events.pop(minion.uid,None)
  game._log('remove_from_game',player=minion.owner,entity=minion.uid,card=minion.card_id)
 game._refresh_auras()
 return True
