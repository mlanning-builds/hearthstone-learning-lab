"""Kazakusan: exact pinned treasure membership and five resumable choices.

Pool flag 2054 in CardDefs 251952 supplies all 28 eligible treasure identities.
No coverage-based filtering, unused archive tokens or Duels substitutes.
"""
from engine.cards import UnsupportedCard
from engine.game import Card
from .selectors import has_tribe
from .pools import require_fixed_cards
TREASURES=('ONY_005ta1', 'ONY_005ta10', 'ONY_005ta11', 'ONY_005ta12', 'ONY_005ta13', 'ONY_005ta2', 'ONY_005ta3', 'ONY_005ta4', 'ONY_005ta5', 'ONY_005ta6', 'ONY_005ta7', 'ONY_005ta8', 'ONY_005ta9', 'ONY_005tb1', 'ONY_005tb12', 'ONY_005tb13', 'ONY_005tb14', 'ONY_005tb2', 'ONY_005tb4', 'ONY_005tb5', 'ONY_005tb7', 'ONY_005tb8', 'ONY_005tb9', 'ONY_005tc1', 'ONY_005tc2', 'ONY_005tc3', 'ONY_005tc5', 'ONY_005tc6')

def paid(game,owner,card):
 if game._card_data(card)['type']!='MINION' or not has_tribe(game._card_data(card),'DRAGON'):return
 p=game.players[owner]
 p.historical_dragons_played=getattr(p,'historical_dragons_played',0)+1
 p._historical_latest_dragon_uid=card.uid

def begin(game,ctx):
 owner=ctx['owner'];p=game.players[owner]
 count=getattr(p,'historical_dragons_played',0)
 physical=ctx.get('physical_card')
 if physical is not None and getattr(p,'_historical_latest_dragon_uid',None)==physical.uid:count-=1
 if count<4:return
 require_fixed_cards(TREASURES,game.cards)
 if game.pending_choice is not None:raise UnsupportedCard('Kazakusan cannot overwrite an active choice')
 # Replacement removes the old deck; it neither destroys cards nor shuffles
 # cards into that old deck, and removes a Kil jaeden portal deck subtype.
 p.deck=[]
 offer(game,owner,(),ctx)

def offer(game,owner,picked,ctx):
 available=tuple(cid for cid in TREASURES if cid not in picked)
 require_fixed_cards(available,game.cards)
 offered=game.rng.sample(available,min(3,len(available)))
 game.pending_choice=dict(owner=owner,kind='historical_kazakusan',options=[dict(card_id=cid) for cid in offered],picked=tuple(picked),context=dict(ctx),_automatic=bool(ctx.get('automatic_choices',False)))
 game.phase='choice'

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_kazakusan':return False
 cid=selected.get('card_id')
 if cid not in {option['card_id'] for option in choice['options']} or cid in choice['picked']:raise UnsupportedCard('Invalid or repeated Kazakusan treasure')
 owner=choice['owner'];p=game.players[owner];picked=choice['picked']+(cid,)
 p.deck.extend(Card(game._new_id(),cid) for _ in range(2))
 if len(picked)<5:offer(game,owner,picked,choice['context'])
 else:
  from .historical_utility_spells import forge_quel_delar
  forge_quel_delar(game,owner)
  game.rng.shuffle(p.deck)
  game._refresh_auras();game._log('kazakusan_deck_replaced',player=owner,count=len(p.deck))
 return True
