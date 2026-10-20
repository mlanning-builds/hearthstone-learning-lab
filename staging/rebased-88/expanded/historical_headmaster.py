"""Headmaster's ordered physical death window, frozen before Spellburst."""
from copy import deepcopy

def begin(game,card):
 card._historical_headmaster_cursors=tuple(len(player.death_records) for player in game.players)

def complete(game,data):
 card=data.get('physical_card');cursors=getattr(card,'_historical_headmaster_cursors',None)
 if cursors is None:return
 records=[record for owner,player in enumerate(game.players) for record in player.death_records[cursors[owner]:]]
 records.sort(key=lambda record:record.get('death_order',record['entity'].uid))
 data['historical_headmaster_deaths']=tuple(deepcopy(record['entity']) for record in records)
 del card._historical_headmaster_cursors

def split(game,op,ctx):
 if op[0]!='historical_headmaster_summon':return None
 # Snapshot entities already frozen when the spell completed, before other
 # Spellburst listeners can create or destroy additional minions.
 entities=ctx.get('event',{}).get('historical_headmaster_deaths',())
 operations=tuple(('historical_headmaster_one',entity) for entity in entities)
 return (operations[0],operations[1:]) if operations else (('batch30_noop',),())

def execute(game,op,ctx):
 if op[0]!='historical_headmaster_one':return False
 owner=ctx['owner'];entity=op[1]
 if len(game.players[owner].board)>=7:return True
 card=game._fresh_replay_card(entity)
 game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_source=card,entry_origin='resurrection',entry_site='headmaster_spellburst')
 return True
