"""Persistent physical base stats, distinct from removable enchantments."""
from copy import deepcopy

def base_stats(game,entity,owner=None):
 data=game._card_data(entity) if not hasattr(entity,'max_health') else game.cards[entity.card_id]
 if data.get('type')!='MINION':return None
 stored=getattr(entity,'base_stat_override',None)
 if owner is not None and game.players[owner].crystal_core:stored=(5,5)
 return tuple(stored) if stored is not None else (data['attack'],data['health'])

def carry_base_stats(source,destination):
 if hasattr(source,'base_stat_override'):destination.base_stat_override=deepcopy(source.base_stat_override)
