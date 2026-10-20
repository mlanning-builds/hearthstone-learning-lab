"""Physical finite portal decks; full Demon membership, fidelity unvalidated."""
from engine.game import Card
from .generation_cards import pool
from .historical_saidan import add as add_stat
DEMONS=pool(card_type='MINION',tribe='DEMON')
class PortalDeck(list):
 def __init__(self,values=(),*,bonus=0):
  super().__init__(values);self.portal_bonus=bonus

def refill(game,owner):
 deck=game.players[owner].deck
 if not isinstance(deck,PortalDeck):return
 deck[:]=[card for card in deck if getattr(card,'_historical_portal_demon',False)]
 needed=max(0,30-len(deck))
 if not needed:return
 ctx=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='GDB_145')
 values=game._generation_created_candidates(DEMONS,ctx)
 if not values:
  from engine.cards import UnsupportedCard
  raise UnsupportedCard('Demon portal has no eligible outcomes')
 for _ in range(needed):
  card=Card(game._new_id(),game.rng.choice(values));card._historical_portal_demon=True
  add_stat(card,'attack_bonus',deck.portal_bonus);add_stat(card,'health_bonus',deck.portal_bonus)
  deck.append(card)

def open_portal(game,owner):
 p=game.players[owner]
 if isinstance(p.deck,PortalDeck):return
 # Validate the full pool before removing the old deck or consuming randomness.
 game._generation_created_candidates(DEMONS,dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='GDB_145'))
 p.deck=PortalDeck();refill(game,owner);game._refresh_auras()
 game._log('demon_portal_opened',player=owner)

def grow(game,owner):
 deck=game.players[owner].deck
 if not isinstance(deck,PortalDeck):return
 deck.portal_bonus+=2
 for card in deck:
  if getattr(card,'_historical_portal_demon',False):
   add_stat(card,'attack_bonus',2);add_stat(card,'health_bonus',2)
 game._log('demon_portal_grown',player=owner,bonus=deck.portal_bonus)

def discard_insertions(game,owner):
 deck=game.players[owner].deck
 if not isinstance(deck,PortalDeck):return False
 deck[:]=[card for card in deck if getattr(card,'_historical_portal_demon',False)]
 return True
