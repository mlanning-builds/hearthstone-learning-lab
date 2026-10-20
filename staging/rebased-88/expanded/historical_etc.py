"""Player-bound E.T.C. band, physical selection and finite depletion.

The band is submitted explicitly; generated/stolen E.T.C.s use the controller's
remaining band. Sideboard cards never enter opening deck predicates.
"""
from engine.game import Card
from engine.cards import UnsupportedCard
ROOT_RULES={'ETC_080':('none',[('historical_etc_discover',)])}
# Explicit launch exclusions supplement metadata START_OF_GAME. The current
# client blacklist requires independent review; this is not a certified list.
EXCLUDED=frozenset(('ETC_080','BOT_914','DAL_800','SW_050','TOY_700','DRG_600','DRG_610','DRG_620','DRG_640','DRG_660'))


def setup(game,decks):
 for owner,deck in enumerate(decks):
  game.players[owner]._historical_etc_band=[Card(game._new_id(),cid) for cid in getattr(deck,'etc_band',())]


def execute(game,op,ctx):
 if op[0]!='historical_etc_discover':return False
 owner=ctx['owner'];band=getattr(game.players[owner],'_historical_etc_band',())
 if not band:return True
 from .pools import require_fixed_cards
 require_fixed_cards(tuple(c.card_id for c in band),game.cards)
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite E.T.C. Discover')
 game.pending_choice=dict(owner=owner,kind='historical_etc_band',options=[dict(card_id=c.card_id,uid=c.uid) for c in band],_automatic=bool(ctx.get('automatic_choices',False)))
 game.phase='choice'
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_etc_band':return False
 owner=choice['owner'];band=getattr(game.players[owner],'_historical_etc_band',[])
 card=next((c for c in band if c.uid==selected['uid']),None)
 if card is None:raise UnsupportedCard('Selected band member no longer available')
 band.remove(card)
 game._discovery_result=game._enter_hand(owner,card)
 game._refresh_auras()
 return True
