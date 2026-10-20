"""Opening Maestra disguise with private restoration state."""
from copy import deepcopy
from .selectors import has_class
ROOT_RULES={'SW_050':('none',[])}

def setup(game):
 from .historical_copy_batches import BASIC_POWERS
 from .pools import require_fixed_cards
 for owner,player in enumerate(game.players):
  if 'SW_050' not in game._opening_effect_ids(owner):continue
  candidates=tuple(hero_class for hero_class in BASIC_POWERS if hero_class!=player.starting_hero_class)
  require_fixed_cards(tuple(BASIC_POWERS[hero_class] for hero_class in candidates),game.cards)
  player._historical_maestra=dict(hero_class=player.hero_class,hero_card_id=getattr(player,'hero_card_id',None),power=deepcopy(player.primary_power))
  disguise=game.rng.choice(candidates);player.hero_class=disguise;player.hero_card_id=None
  cid=BASIC_POWERS[disguise]
  game._replace_primary_power(owner,dict(card_id=cid,basic_starting_class=disguise,cost=1 if getattr(player,'historical_genn',False) else game.cards[cid]['cost']))
  # The opponent sees only the assumed class/power, not a setup announcement.

def reveal(game,owner):
 player=game.players[owner];saved=getattr(player,'_historical_maestra',None)
 if saved is None:return
 del player._historical_maestra
 player.hero_class=saved['hero_class'];player.hero_card_id=saved['hero_card_id']
 game._replace_primary_power(owner,deepcopy(saved['power']))
 game._log('maestra_revealed',player=owner,hero_class=player.hero_class)

def event(game,kind,data):
 if kind not in ('minion_played','spell_cast','dormant_other_card_played'):return
 owner=data['owner'];player=game.players[owner]
 if not hasattr(player,'_historical_maestra') or not has_class(game.cards[data['card_id']],'ROGUE'):return
 game._rule_events.append(('captured_effects',dict(operations=(('historical_maestra_reveal',),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
