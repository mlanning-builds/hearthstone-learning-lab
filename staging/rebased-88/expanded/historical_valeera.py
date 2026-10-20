"""Valeera Hero Stealth and private physical Shadow Reflection lifecycle."""
from engine.game import Card
from engine.cards import UnsupportedCard
ROOT_RULES={'ICC_827':('none',[('historical_valeera_stealth',)])}
TOKEN_RULES={'ICC_827t':('none',[('historical_valeera_unbound',)])}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'ICC_827p'}


def stealth(game,owner):
 return game.players[owner].turns_taken<getattr(game.players[owner],'historical_valeera_stealth_until',-1)


def clear(game,owner):
 player=game.players[owner]
 removed=[card for card in player.hand if getattr(card,'_historical_reflection',False)]
 player.hand[:]=[card for card in player.hand if not getattr(card,'_historical_reflection',False)]
 for card in removed:game._log('reflection_expired',player=owner,card=card.card_id)


def add(game,owner):
 power=game.players[owner].primary_power
 if power is None or power['card_id']!='ICC_827p' or game.current!=owner:return
 from .historical_family_batches import powers_disabled
 if powers_disabled(game):return
 card=Card(game._new_id(),'ICC_827t');card._historical_reflection=True
 game._enter_hand(owner,card)


def power_changed(game,owner,previous):
 power=game.players[owner].primary_power
 if previous is not None and previous['card_id']=='ICC_827p':clear(game,owner)
 if power is not None and power['card_id']=='ICC_827p':add(game,owner)


def played(game,owner,card):
 player=game.players[owner]
 for index,reflection in enumerate(tuple(player.hand)):
  if not getattr(reflection,'_historical_reflection',False):continue
  # Copy the printed/compiled definition rather than paid discounts and
  # temporary enchantments; keep the transforming Reflection entity's UID.
  result=game._fresh_replay_card(card);result.uid=reflection.uid
  result._historical_reflection=True
  player.hand[index]=result
 game._refresh_auras()


def turn_entries(game,phase):
 if phase!='start':return []
 power=game.players[game.current].primary_power
 if power is None or power['card_id']!='ICC_827p':return []
 return [dict(source=None,order=power['uid'],operations=(('historical_valeera_add',),))]


def execute(game,op,ctx):
 if op[0]=='historical_valeera_stealth':
  player=game.players[ctx['owner']]
  player.historical_valeera_stealth_until=player.turns_taken+1
  return True
 if op[0]=='historical_valeera_add':add(game,ctx['owner']);return True
 if op[0]=='historical_valeera_unbound':raise UnsupportedCard('Shadow Reflection must first transform into a played card')
 return False
