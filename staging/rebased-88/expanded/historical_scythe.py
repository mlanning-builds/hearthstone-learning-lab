"""Souleater's Scythe opening consumption and owner-local Bound Soul pool.

All behavior is newly written and unvalidated. In-game generated Scythes do
not run Start of Game effects; stolen Souls use the caster's own pool.
"""
from engine.game import Card
from engine.cards import UnsupportedCard
from .identities import identity_resolver
from .pools import require_fixed_cards

def setup(game):
 for owner in (game.first_player,1-game.first_player):
  p=game.players[owner]
  if 'RLK_214' not in game._opening_effect_ids(owner):continue
  require_fixed_cards(('RLK_214t',),game.cards)
  resolve=identity_resolver(game.cards);selected=[];used=set()
  # Resolve after opening replacements. Foreign inserted cards are not part
  # of the submitted owner's consumption candidates (e.g. King Llane).
  for _ in range(3):
   choices=[card for card in p.deck if getattr(card,'_starting_owner',None)==owner
            and game._card_data(card)['type']=='MINION' and resolve(game._card_data(card)) not in used]
   if not choices:break
   card=game.rng.choice(choices);selected.append(card);used.add(resolve(game._card_data(card)))
  if not selected:continue
  for card in selected:p.deck.remove(card)
  p._scythe_consumed=list(selected)
  souls=[Card(game._new_id(),'RLK_214t') for _ in selected]
  p.deck.extend(souls);game.rng.shuffle(p.deck)
  # Opening replacement is not an ordinary player shuffle action.
  game._log('scythe_consumed',player=owner,count=len(selected))


def execute(game,op,ctx):
 if op[0]!='historical_scythe_discover':return False
 owner=ctx['owner'];values=tuple(getattr(game.players[owner],'_scythe_consumed',()))
 if not values:return True
 if game.pending_choice is not None:raise UnsupportedCard('Bound Soul cannot overwrite a pending choice')
 require_fixed_cards(tuple(card.card_id for card in values),game.cards)
 offered=game.rng.sample(values,len(values))
 game.pending_choice=dict(owner=owner,kind='historical_scythe',options=[dict(card_id=card.card_id,uid=card.uid) for card in offered],_automatic=bool(ctx.get('automatic_choices',False)))
 game.phase='choice'
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_scythe':return False
 owner=choice['owner'];p=game.players[owner]
 uid=selected.get('uid');cid=selected.get('card_id')
 if not any(row['uid']==uid and row['card_id']==cid for row in choice['options']):raise UnsupportedCard('Bound Soul minion was not offered')
 pool=getattr(p,'_scythe_consumed',[])
 card=next((card for card in pool if card.uid==uid and card.card_id==cid),None)
 if card is None:raise UnsupportedCard('Bound Soul consumed minion is no longer available')
 pool.remove(card)
 game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 return True
