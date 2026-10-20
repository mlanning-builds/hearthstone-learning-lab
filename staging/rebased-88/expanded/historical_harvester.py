"""Harvester tracks physical originals across supported persistent zones.

Implementation only: trigger timing and transfer edge cases await owner-approved
review. A departed or identity-changed original never substitutes another card.
"""
from .historical_copy_lineage import matches_original
ROOT_RULES={'REV_011':('none',[])}
TRIGGERS={'REV_011':(('historical_copy_event','harvester_play'),[('historical_harvester_steal',)])}


def record_play(game,owner,card,source):
 reference=getattr(card,'_historical_copy_source',None)
 if reference is None:return
 pending=getattr(game.players[owner],'_historical_harvester_plays',{})
 key=(card.card_id,getattr(source,'uid',None) if game.cards[card.card_id]['type']=='MINION' else None)
 pending[key]=reference
 game.players[owner]._historical_harvester_plays=pending


def tag_event(game,kind,data):
 if kind not in ('minion_played','spell_cast','dormant_other_card_played'):return
 owner=data.get('owner')
 if owner not in (0,1):return
 key=(data.get('card_id'),data.get('source') if kind=='minion_played' else None)
 reference=getattr(game.players[owner],'_historical_harvester_plays',{}).pop(key,None)
 if reference is not None:data['historical_harvester_link']=reference


def execute(game,op,ctx):
 if op[0]!='historical_harvester_steal':return False
 owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner]
 reference=ctx.get('event',{}).get('historical_harvester_link')
 if reference is None or reference[0]!=1-owner:return True
 for zone in ('hand','deck'):
  cards=getattr(q,zone)
  card=next((c for c in cards if matches_original(c,reference)),None)
  if card is not None:
   cards.remove(card);game._enter_hand(owner,card);game._refresh_auras()
   game._log('harvester_stolen',player=owner,card=card.card_id,zone=zone)
   return True
 for entity in tuple(q.board):
  if not matches_original(entity,reference):continue
  if len(p.board)>=7:return True
  q.board.remove(entity);entity.owner=owner;p.board.append(entity)
  if hasattr(entity,'attacks'):entity.attacks=0;entity.summoned_turn=game.turn
  game._refresh_auras();game._log('harvester_stolen',player=owner,card=entity.card_id,zone='board')
  return True
 for card in tuple(q.secrets):
  if not matches_original(card,reference):continue
  from .historical_secret_batches import admissible
  if admissible(game,owner,card.card_id):
   q.secrets.remove(card);game._place_secret(owner,card.card_id,physical=card)
   game._log('harvester_stolen',player=owner,card=card.card_id,zone='secret')
  return True
 card=q.equipped_card
 if card is not None and matches_original(card,reference):
  from .historical_copy_batches import execute as copy_execute
  copy_execute(game,('historical_copy_steal_weapon',),ctx)
 return True
