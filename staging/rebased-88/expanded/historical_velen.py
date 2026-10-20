"""Velen's played-Draenei history with distinct replay source semantics."""
from copy import deepcopy
from .selectors import has_tribe
ROOT_RULES={'GDB_131':('none',[])}
DEATH_EFFECTS={'GDB_131':[('historical_velen_repeat',)]}

def record_play(game,owner,card,source):
 if game._card_data(card)['type']!='MINION' or not has_tribe(game._card_data(card),'DRAENEI'):return
 from .identities import canonical_identity
 if canonical_identity(game._card_data(card),game.cards)==canonical_identity(game.cards['GDB_131'],game.cards):return
 # Printed Deathrattles exclude unrelated enchantments attached to the card.
 deaths=deepcopy(game._printed_death_operations(card.card_id))
 battlecries=[record for record in getattr(game.players[owner],'_historical_battlecry_records',()) if record['played_uid']==card.uid]
 battlecry=deepcopy(battlecries[-1]) if battlecries else None
 if not deaths and battlecry is None:return
 records=getattr(game.players[owner],'_historical_velen_records',[])
 records.append(dict(card=deepcopy(card),uid=getattr(source,'uid',None),battlecry=battlecry,death_operations=deaths))
 game.players[owner]._historical_velen_records=records

def death_source(game,owner,record):
 uid=record['uid']
 # A surviving original retains its current stats and physical memories.
 for player in game.players:
  for minion in player.all_minions:
   if minion.uid==uid and minion.card_id==record['card'].card_id:return minion
 # Off-board references use a fresh base bearer, never Velen's identity/stats.
 from .game import Minion
 card=game._fresh_replay_card(record['card']);data=game._card_data(card)
 source=Minion(game._new_id(),card.card_id,owner,data['attack'],data['health'],data['health'],set(data.get('mechanics',())),summoned_turn=game.turn)
 if getattr(card,'rule_state',{}).get('forge_parts') is not None:game._forge_entry(source,card)
 return source

def split(game,op,ctx):
 name=op[0];owner=ctx['owner']
 if name=='historical_velen_repeat':
  records=deepcopy(getattr(game.players[owner],'_historical_velen_records',()))
  operations=[]
  for record in records:
   if record['battlecry'] is not None:operations.append(('historical_velen_battlecry',record['battlecry']))
   if record['death_operations']:operations.append(('historical_velen_death',record))
  if not operations:return ('batch30_noop',),()
  head,tail=game._split_fixed_summon(operations[0],ctx)
  return head,tuple(tail)+tuple(operations[1:])
 if name=='historical_velen_battlecry':
  from .historical_copy_batches import repeat_battlecry_program
  return repeat_battlecry_program(game,op[1],dict(ctx,automatic_choices=True))
 if name=='historical_velen_death':
  record=op[1];source=death_source(game,owner,record)
  context=dict(ctx,source=source,physical_card=deepcopy(record['card']),card_id=record['card'].card_id,target=0,spell=False,bonus=0,lifesteal='LIFESTEAL' in game._effective_keywords(source),automatic_choices=True)
  return game._split_fixed_summon(('replay_context',record['death_operations'],context),ctx)
 return None
