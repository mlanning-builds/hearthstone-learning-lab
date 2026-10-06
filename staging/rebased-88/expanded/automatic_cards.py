"""Effect-driven execution of detached physical cards; never a paid hand play.

Consumer-specific replay/trigger semantics remain staged. Minion and weapon
placement does not execute a hand-play Battlecry. Spells reuse internal casting.
"""
from engine.game import Card
from engine.cards import UnsupportedCard

def validate_automatic_card(game,card):
 if not isinstance(card,Card):raise ValueError('Automatic execution requires a physical card')
 data=game.cards.get(card.card_id)
 if data is None:raise UnsupportedCard('Missing automatic card metadata')
 kind=data['type']
 from .cards import RULES,COLLECTIBLE_IDS,TOKEN_IDS
 from .locations import LOCATION_RULES
 from .hero_powers import HERO_POWERS
 if kind=='SPELL':supported=game._supports_internal_spell(card.card_id)
 elif kind=='LOCATION':supported=card.card_id in LOCATION_RULES
 elif kind=='HERO':supported=card.card_id in HERO_POWERS
 else:supported=kind in ('MINION','WEAPON') and card.card_id in (set(RULES)|COLLECTIBLE_IDS|TOKEN_IDS)
 if not supported:raise UnsupportedCard('Automatic card not implemented: '+card.card_id)
 return kind

def split_automatic_card(game,op,ctx):
 if op[0]=='prison_replay':
  source=ctx.get('source')
  if source is None or source not in game.players[ctx['owner']].minions or source.silenced:return ('batch30_noop',),()
  stored=source.rule_state.get('prison_cards',[])
  if not stored:return ('batch30_noop',),()
  for value in stored:validate_automatic_card(game,value)
  value=stored.pop(game.rng.randrange(len(stored)))
  # The discarded physical card is gone; this is a new automatic execution.
  card=game._copy_card(value)
  return ('batch30_noop',),(('automatic_card',card,'random'),)
 if op[0]=='slice_replay':
  from .replay_history import plays_for_turn
  records=plays_for_turn(game.players[ctx['owner']],game.turn)
  sources=[r.card for r in records if r.card.card_id!='JAIL_500']
  # Validate the entire captured set before consuming RNG or replaying anything.
  for card in sources:validate_automatic_card(game,card)
  game.rng.shuffle(sources)
  operations=tuple(('automatic_card',game._fresh_replay_card(card),'prefer_enemies') for card in sources)
  return ('batch30_noop',),operations
 if op[0]=='automatic_top':
  remaining=op[1]
  if type(remaining) is not int or remaining<0:raise ValueError('Invalid automatic deck count')
  if not remaining or not game.players[ctx['owner']].deck:return ('batch30_noop',),()
  value=game.players[ctx['owner']].deck[0]
  card=value if isinstance(value,Card) else Card(game._new_id(),value)
  validate_automatic_card(game,card)
  return ('automatic_detach_top',value), (('automatic_card',card,'random'),('automatic_top',remaining-1))
 if op[0]!='automatic_card':return None
 card=op[1];policy=op[2] if len(op)>2 else 'random'
 if policy not in ('random','enemies','prefer_enemies'):raise ValueError('Invalid automatic targeting policy')
 if any(card is c for p in game.players for c in p.hand+p.deck):raise UnsupportedCard('Automatic card must be detached from its source zone')
 kind=validate_automatic_card(game,card)
 if kind=='SPELL':return game._cast_spell_split(('cast_physical_spell',card,policy),ctx)
 return ('automatic_place',card),()

def place_automatic_card(game,op,ctx):
 if op[0]=='request_end_turn':
  owner=ctx['owner']
  if game.current==owner and game._turn_frame is None:
   game._requested_turn_end=(owner,game.turn)
  return True
 if op[0]=='automatic_detach_top':
  deck=game.players[ctx['owner']].deck
  if not deck or (deck[0] is not op[1] and deck[0]!=op[1]):raise UnsupportedCard('Automatic source changed before consumption')
  deck.pop(0);game._refresh_auras();return True
 if op[0]!='automatic_place':return False
 card=op[1];owner=ctx['owner'];data=game.cards[card.card_id];kind=data['type']
 if kind=='MINION':
  m=game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='recruit',entry_site='automatic_card',entry_zone='deck',entry_source=card)
  if m is not None:game._carry_origin(card,m)
 elif kind=='LOCATION':
  location=game._place_location(owner,card.card_id)
  game._crafted_location_entry(location,card)
 elif kind=='WEAPON':game._equip(owner,card.card_id,attack_bonus=card.attack_bonus,physical_card=card)
 elif kind=='HERO':game._play_hero_card(owner,card.card_id)
 else:raise UnsupportedCard('Invalid automatic placement type')
 return True
