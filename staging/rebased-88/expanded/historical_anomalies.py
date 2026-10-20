"""Explicit constructed anomaly effects and Cho gall opening selection.

The complete active pool is archived from the pinned CardDefs tag 2895.
Unwritten effects never disappear from that pool. Selecting an unsupported
active effect fails before setup mutates players; no substitute is sampled.
"""
from engine.cards import UnsupportedCard
ACTIVE_IDS=('TTN_002t1','TTN_002t11','TTN_002t14','TTN_002t15','TTN_002t20','TTN_002t21','TTN_002t22','TTN_002t24','TTN_002t30','TTN_002t32','TTN_002t35','TTN_002t36','TTN_002t41','TTN_002t43','TTN_002t44','TTN_002t45','TTN_002t5','TTN_002t50','TTN_002t9')
UNWRITTEN_IDS=frozenset()
IMPLEMENTED_IDS=frozenset(ACTIVE_IDS)-UNWRITTEN_IDS
START_ADDITIONS={'TTN_002t14':('OG_134',),'TTN_002t36':('OG_123','OG_123'),'TTN_002t50':('TTN_922',)}
def active(game,cid):return cid in getattr(game,'historical_anomaly_ids',())
def configure(game,ids):
 ids=tuple(ids)
 if len(ids)>2 or len(set(ids))!=len(ids) or any(cid not in ACTIVE_IDS for cid in ids):raise UnsupportedCard('Invalid constructed anomaly selection')
 if any(cid not in IMPLEMENTED_IDS for cid in ids):raise UnsupportedCard('Selected anomaly effect remains unwritten')
 if getattr(game,'historical_anomalies_started',False):raise UnsupportedCard('Cannot change anomalies after activation')
 game.historical_anomaly_ids=ids

def apply_start(game):
 if getattr(game,'historical_anomalies_started',False):return
 ids=tuple(getattr(game,'historical_anomaly_ids',()))
 if not ids:return
 configure(game,ids)
 # Full preflight precedes every mutation, including random draw/entry work.
 for cid in ids:
  for dependency in START_ADDITIONS.get(cid,()):
   if dependency not in game.cards:raise UnsupportedCard('Unwritten anomaly dependency: '+dependency)
 if 'TTN_002t1' in ids:
  from .genn import POWERS
  if any(POWERS[p.hero_class] not in game.cards for p in game.players):raise UnsupportedCard('Missing upgraded anomaly Hero Power')
 game.historical_anomalies_started=True
 from copy import deepcopy
 opening_hands=tuple(tuple(deepcopy(card) for card in p.hand) for p in game.players)
 for cid in ids:
  for owner,p in enumerate(game.players):
   if cid=='TTN_002t1':
    from .genn import POWERS
    power=POWERS[p.hero_class]
    game._replace_primary_power(owner,dict(card_id=power,upgraded_starting_class=p.hero_class,cost=game.cards[power]['cost']))
   elif cid=='TTN_002t11':
    p.max_mana=min(p.mana_capacity,p.max_mana+1);p.mana=min(p.max_mana,p.mana+1)
   elif cid=='TTN_002t22':
    # Freeze both hands before either player receives copies. Sample physical
    # slots, so two native copies of one identity retain their multiplicity.
    candidates=opening_hands[1-owner]
    for original in game.rng.sample(candidates,min(2,len(candidates))):
     game._enter_hand(owner,game._copy_card(original,source_owner=1-owner))
   elif cid=='TTN_002t24':p.max_health+=5;p.health+=5
   elif cid=='TTN_002t32':
    for card in p.hand:card.cost_delta=getattr(card,'cost_delta',0)-1
   elif cid=='TTN_002t5':
    for _ in range(2):game._draw(owner)
   elif cid in START_ADDITIONS:
    for dependency in START_ADDITIONS[cid]:game._add(owner,dependency)
   # Golden is an all-card presentation property, not an enchantment that
   # should disappear on Silence, transform, copies or later generation.
   elif cid=='TTN_002t35':p.historical_all_cards_golden=True
 game._refresh_auras();game._log('anomalies_activated',cards=ids)

def card_discount(game,owner,card):
 if game.current!=owner:return 0
 p=game.players[owner];kind=game._card_data(card)['type']
 if kind=='MINION' and active(game,'TTN_002t43') and not p.minion_played_this_turn:return 1
 if kind=='SPELL' and active(game,'TTN_002t45') and not p.spells_turn:return 1
 return 0

def hero_attack(game,owner):return int(game.current==owner and active(game,'TTN_002t41'))
def power_discount(game):return int(active(game,'TTN_002t9'))

def turn_entries(game,phase):
 if phase!='end':return []
 result=[]
 for cid in getattr(game,'historical_anomaly_ids',()):
  if cid not in ('TTN_002t15','TTN_002t20','TTN_002t30'):continue
  result.append(dict(source=None,order=-1,card_id=cid,operations=(('historical_utility_anomaly_end',cid),)))
 return result

def end_effect(game,owner,cid):
 p=game.players[owner]
 if cid=='TTN_002t15':
  if p.mana>0:game._draw(owner)
 elif cid=='TTN_002t20':
  if p.mana>0:game._add(owner,'TOKEN_COIN')
 elif cid=='TTN_002t30':
  candidates=[m for m in p.minions if m.health>0]
  if candidates:game._buff(game.rng.choice(candidates),0,1)
 else:raise UnsupportedCard('Unknown anomaly end effect')


def capture_first_play(game,owner,card):
 if not active(game,'TTN_002t21') or game.current!=owner:return None
 p=game.players[owner]
 if getattr(p,'_historical_twist_play_turn',None)==game.turn:return None
 p._historical_twist_play_turn=game.turn
 from copy import deepcopy
 # Freeze the physical definition before Battlecry/transform/hand mutations.
 game._remember_crafted(card)
 return deepcopy(card)

def shuffle_play_copy(game,owner,source):
 p=game.players[owner];card=game._fresh_replay_card(source)
 game._carry_origin(source,card,copied=True,source_owner=owner)
 p.deck.insert(game.rng.randrange(len(p.deck)+1),card)
 game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 game._log('anomaly_shuffle_copy',player=owner)

def draw_index(game,owner,index,*,private=False,eligible=None):
 if private or game.phase!='play' or game.current!=owner or not active(game,'TTN_002t44'):return index
 p=game.players[owner]
 if getattr(p,'_historical_opportunity_draw_turn',None)==game.turn:return index
 # The condition belongs to a draw attempt, not the subsequent receive
 # callback, which can recurse through a Casts When Drawn card.
 p._historical_opportunity_draw_turn=game.turn
 choices=range(len(p.deck)) if eligible is None else eligible
 affordable=[i for i in choices if game._cost(p.deck[i],owner)<=p.mana]
 return game.rng.choice(affordable) if affordable else index


def choose_opening(game):
 """One anomaly at 50% with one owner, guaranteed with both owners.

 Multiple copies within one submitted deck do not create extra rolls. Use the
 complete pinned active pool, uniformly, without implementation filtering.
 """
 present=tuple('YOG_530' in game._opening_effect_ids(owner) for owner in (0,1))
 if not any(present):return
 if IMPLEMENTED_IDS!=frozenset(ACTIVE_IDS):raise UnsupportedCard('Cho gall requires every active anomaly effect')
 if all(present) or game.rng.randrange(2)==0:
  configure(game,(game.rng.choice(ACTIVE_IDS),))
  game._log('anomaly_revealed',cards=game.historical_anomaly_ids)
 else:game.historical_anomaly_ids=()
