"""Eonar activated abilities; implementation pass, gameplay validation deferred."""
from engine.game import Action
from engine.cards import UnsupportedCard
from .pools import require_fixed_cards
ABILITIES=('TTN_903t','TTN_903t2','TTN_903t3')
REQUIRED=ABILITIES+('TTN_903t4',)
def active(minion):
 return minion.card_id=='TTN_903' and not minion.silenced

def remaining(minion):
 used=minion.rule_state.get('historical_titan_used',())
 return tuple(cid for cid in ABILITIES if cid not in used) if active(minion) else ()

def actions(game):
 result=[]
 for minion in game.players[game.current].minions:
  values=remaining(minion)
  if not values:continue
  keywords=game._effective_keywords(minion)
  limit=4 if 'MEGA_WINDFURY' in keywords else 2 if 'WINDFURY' in keywords else 1
  if minion.frozen_until>=0 or minion.attacks>=limit or 'CANT_ATTACK' in keywords:continue
  result.extend(Action('activate',minion.uid,choices=(ABILITIES.index(cid),)) for cid in values)
 return result

def activate(game,action):
 minion=game._force_live(action.source)
 if minion is None or action not in actions(game):raise UnsupportedCard('Unavailable Eonar ability')
 require_fixed_cards(REQUIRED,game.cards)
 cid=ABILITIES[action.choices[0]]
 minion.rule_state['historical_titan_used']=tuple(minion.rule_state.get('historical_titan_used',()))+(cid,)
 minion.attacks+=1
 context=dict(owner=minion.owner,source=minion,target=0,spell=False,bonus=0,lifesteal=False,card_id=cid)
 from .historical_utility_spells import TOKEN_RULES
 operations=tuple(TOKEN_RULES[cid][1])+(('historical_utility_eonar_after',minion.uid),)
 game._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
 game._log('titan_ability',player=minion.owner,source=minion.uid,card_id=cid)
