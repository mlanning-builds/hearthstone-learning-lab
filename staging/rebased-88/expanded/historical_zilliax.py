"""Physical Zilliax construction and all eight module effects; unvalidated.

Explicit two-module construction only. No random-generation distribution is
inferred, and bare zero-stat Zilliax entities are rejected at entry/play boundaries.
"""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .minion_forge import ForgePart
SOURCE='Frozen 36.6.0.251952 explicit Zilliax module definitions; behavior unvalidated'
MODULES=tuple('TOY_330t'+str(i) for i in range(92,100))
PARTS={
 'TOY_330t92':ForgePart('TOY_330t92',death_operations=(('historical_copy_death_shuffle',),),source=SOURCE),
 'TOY_330t93':ForgePart('TOY_330t93',intrinsics=(('end_effects',(('damage_own_hero',3),)),),source=SOURCE),
 'TOY_330t94':ForgePart('TOY_330t94',intrinsics=(('start_effects',(('double_self_attack',),)),),source=SOURCE),
 'TOY_330t95':ForgePart('TOY_330t95',intrinsics=(('friendly_attack',1),),source=SOURCE),
 'TOY_330t96':ForgePart('TOY_330t96',keywords=('ELUSIVE','POISONOUS'),source=SOURCE),
 'TOY_330t97':ForgePart('TOY_330t97',operations=(('copy_self_right',1),),source=SOURCE),
 'TOY_330t98':ForgePart('TOY_330t98',intrinsics=(('cost_rule','friendly_minions'),),source=SOURCE),
 'TOY_330t99':ForgePart('TOY_330t99',keywords=('DIVINE_SHIELD','TAUNT','LIFESTEAL','RUSH'),source=SOURCE),
}
FORMS=('TOY_330',)+tuple('TOY_330t'+str(i) for i in range(5,13))
FIXED_TOKEN_IDS=frozenset(MODULES)|frozenset(FORMS)


def build(game,modules,card_id='TOY_330'):
 if card_id not in FORMS:raise UnsupportedCard('Unknown Zilliax cosmetic identity')
 if not isinstance(modules,tuple) or len(modules)!=2 or len(set(modules))!=2 or any(cid not in PARTS for cid in modules):
  raise UnsupportedCard('Zilliax requires two distinct explicit modules')
 from .pools import require_fixed_cards
 require_fixed_cards((card_id,)+modules,game.cards)
 first,second=(PARTS[cid] for cid in modules)
 data=[game.cards[cid] for cid in modules]
 card=Card(game._new_id(),card_id)
 card.base_stat_override=(sum(c['attack'] for c in data),sum(c['health'] for c in data))
 card.set_cost=sum(c['cost'] for c in data)
 card.rule_state=deepcopy(dict(crafted_zilliax=True,crafted_target='none',crafted_ops=first.operations+second.operations,forge_parts=modules,forge_tribes=('MECHANICAL',),forge_keywords=tuple(sorted(set(first.keywords+second.keywords))),forge_death=first.death_operations+second.death_operations,forge_intrinsics=first.intrinsics+second.intrinsics))
 game._remember_crafted(card)
 return card



def selection_errors(deck,expanded):
 modules=getattr(deck,'zilliax_modules',())
 present=any(cid in FORMS for cid in expanded)
 if not present:return ['Zilliax modules require Zilliax in the submitted deck.'] if modules else []
 if not isinstance(modules,tuple) or len(modules)!=2 or any(cid not in PARTS for cid in modules) or len(set(modules))!=2:
  return ['Zilliax requires two distinct explicit module IDs.']
 return []


def setup(game,decks):
 for owner,deck in enumerate(decks):
  player=game.players[owner];player._starting_custom_definitions={};player._starting_custom_cards={}
  modules=getattr(deck,'zilliax_modules',())
  if not modules:continue
  for index,original in enumerate(tuple(player.deck)):
   if original.card_id not in FORMS:continue
   card=build(game,modules,original.card_id);card.uid=original.uid
   game._carry_origin(original,card)
   player.deck[index]=card
   definition=deepcopy(dict(game.cards[card.card_id]))
   definition.update(cost=card.set_cost,attack=card.base_stat_override[0],health=card.base_stat_override[1],races=['MECHANICAL'])
   keywords=set(card.rule_state['forge_keywords'])
   if card.rule_state['crafted_ops']:keywords.add('BATTLECRY')
   if card.rule_state['forge_death']:keywords.add('DEATHRATTLE')
   definition['mechanics']=sorted(keywords)
   player._starting_custom_definitions[card.card_id]=definition
   player._starting_custom_cards[card.card_id]=deepcopy(card)


ROOT_RULES={'TOY_330':('none',[('historical_zilliax_validate',)])}
TOKEN_RULES={cid:('none',[('historical_zilliax_validate',)]) for cid in FORMS if cid!='TOY_330'}


def definition(entity):
 state=getattr(entity,'rule_state',{})
 if state.get('crafted_zilliax'):return state
 return getattr(entity,'_crafted_definition',{}).get('state',{})


def require_definition(entity):
 state=definition(entity);parts=state.get('forge_parts',())
 if (not state.get('crafted_zilliax') or not isinstance(parts,tuple)
     or len(parts)!=2 or len(set(parts))!=2 or any(cid not in PARTS for cid in parts)):
  raise UnsupportedCard('Zilliax requires its physical two-module definition; random bare generation is forbidden')
 return state


def execute(game,op,ctx):
 if op[0]!='historical_zilliax_validate':return False
 require_definition(ctx.get('physical_card') or ctx.get('source'))
 return True
