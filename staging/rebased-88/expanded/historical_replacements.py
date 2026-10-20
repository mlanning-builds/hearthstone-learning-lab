"""Explicit replacement of battlefield transformation by a real summon."""
def vashj_replaces(game,minion,cid):
 return (minion.card_id=='REV_925' and not minion.silenced and not minion.dormant
         and minion.health>0 and minion in game.players[minion.owner].board
         and game.cards[cid]['type']=='MINION')

def vashj_summon(game,minion,cid,*,donor=None,stats=None):
 result=game._summon(minion.owner,cid,copy_from=donor,entry_stats=stats,
                     entry_origin='effect',entry_site='vashj_transform_replacement',entry_source=minion)
 # The original still occupies its slot. Failed capacity admission is not a
 # transformation and callers must not treat it as a new replacement entity.
 return result if result is not None else minion
