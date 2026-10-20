"""Staged Holmes clues and rewards; exact offer generation remains gated.

A client-evidenced offer provider is required. Never sample an implemented-only
set or fabricate distractor probabilities. No production root registration.
"""
from copy import deepcopy
from engine.cards import UnsupportedCard
from .identities import canonical_identity
STAGED_RULES={'REV_022':('none',[('historical_holmes_begin',)])}
CLUES=('starting_hand','current_hand','deck')
PROMPTS=('Which card was in your opponent\'s starting hand?', 'Which card is in your opponent\'s hand?', 'Which card is in your opponent\'s deck?')

def public_clue(choice):
 if choice.get('kind')!='historical_holmes_clue':return {}
 stage=choice['stage']
 if type(stage) is not int or not 0<=stage<3:raise UnsupportedCard('Malformed Holmes clue stage')
 return dict(clue=CLUES[stage],clue_number=stage+1,prompt=PROMPTS[stage])


def snapshot(game,owner):
 opponent=game.players[1-owner]
 return tuple(tuple(deepcopy(card) for card in cards) for cards in (
  getattr(opponent,'_starting_hand',()),opponent.hand,opponent.deck))


def deliver(game,owner,picks):
 # Only solved clues contribute cards; empty zones contribute neither a
 # fabricated answer nor a random replacement reward.
 for card in picks:game._enter_hand(owner,game._copy_card(card,source_owner=1-owner))
 game._refresh_auras();game._log('holmes_solved',player=owner,count=len(picks))


def offer(game,owner,zones,stage,picks,context):
 provider=getattr(game,'historical_holmes_offer',None)
 if not callable(provider):raise UnsupportedCard('Holmes requires the complete pinned distractor/offer contract')
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Holmes clue')
 # A missing hand/deck skips that clue, rather than abandoning earlier
 # correct answers. No provider/RNG call is made for an empty target zone.
 while stage<3 and not zones[stage]:
  game._log('holmes_clue_skipped',player=owner,clue=stage+1)
  stage+=1
 if stage==3:
  deliver(game,owner,picks)
  return False
 actual=zones[stage]
 valid={canonical_identity(game._card_data(card),game.cards) for card in actual}
 # Provider receives the immutable clue snapshot and all frozen metadata;
 # implementation coverage is not an eligibility filter.
 offered=provider(game,owner,CLUES[stage],deepcopy(zones))
 if not isinstance(offered,(tuple,list)):raise UnsupportedCard('Malformed Holmes clue offer')
 ids=tuple(offered)
 if len(ids)!=3 or any(not isinstance(cid,str) or not cid for cid in ids):raise UnsupportedCard('Holmes clues require three explicit card identities')
 if any(cid not in game.cards for cid in ids):raise UnsupportedCard('Holmes offer contains an unwritten dependency')
 identities=tuple(canonical_identity(game.cards[cid],game.cards) for cid in ids)
 if len(set(identities))!=3:raise UnsupportedCard('Holmes offer repeats a canonical card identity')
 if not any(identity in valid for identity in identities):raise UnsupportedCard('Holmes clue lacks a correct answer')
 game.pending_choice=dict(owner=owner,kind='historical_holmes_clue',options=[dict(card_id=cid) for cid in ids],zones=zones,stage=stage,picks=tuple(picks),context=context,_automatic=bool(context.get('automatic_choices',False)))
 game.phase='choice'
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_holmes_clue':return False
 stage=choice['stage'];owner=choice['owner'];cid=selected.get('card_id')
 if cid not in {row['card_id'] for row in choice['options']}:raise UnsupportedCard('Holmes answer was not offered')
 identity=canonical_identity(game.cards[cid],game.cards)
 actual=next((card for card in choice['zones'][stage] if canonical_identity(game._card_data(card),game.cards)==identity),None)
 if actual is None:
  game._log('holmes_failed',player=owner,clue=stage+1)
  return True
 picks=choice['picks']+(deepcopy(actual),)
 if stage<2:
  offer(game,owner,choice['zones'],stage+1,picks,choice['context'])
 else:
  deliver(game,owner,picks)
 return True


def execute(game,op,ctx):
 if op[0]!='historical_holmes_begin':return False
 if not callable(getattr(game,'historical_holmes_offer',None)):
  raise UnsupportedCard('Holmes requires the complete pinned distractor/offer contract')
 owner=ctx['owner'];zones=snapshot(game,owner)
 offer(game,owner,zones,0,(),dict(ctx))
 return True
