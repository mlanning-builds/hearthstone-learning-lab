"""Persistent physical base stats, distinct from removable enchantments."""
from copy import deepcopy

def base_stats(game,entity,owner=None):
 data=game._card_data(entity) if not hasattr(entity,'max_health') else game.cards[entity.card_id]
 if data.get('type')!='MINION':return None
 stored=getattr(entity,'base_stat_override',None)
 from .historical_family_batches import LACKEYS
 if owner is not None and data['id'] in LACKEYS and getattr(game.players[owner],'historical_lackeys_four',False):stored=(4,4)
 if owner is not None and game.players[owner].crystal_core:stored=(5,5)
 return tuple(stored) if stored is not None else (data['attack'],data['health'])

def carry_base_stats(source,destination):
 if hasattr(source,'base_stat_override'):destination.base_stat_override=deepcopy(source.base_stat_override)
 if getattr(source,'card_id',None)==getattr(destination,'card_id',None):
  for field in ('_historical_jade_definition','_historical_student_definition','_historical_ritual_component','_historical_set_stats','_historical_permanent_stats'):
   if hasattr(source,field):setattr(destination,field,deepcopy(getattr(source,field)))


 if getattr(source,'card_id',None)=='SCH_523t' and hasattr(source,'_historical_student_definition'):
  destination.set_cost=source._historical_student_definition['cost']
