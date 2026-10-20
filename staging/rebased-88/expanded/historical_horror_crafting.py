"""Physical two-spell Drustvar Horror construction; fidelity review deferred."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool
SHAMAN_SPELLS=pool(card_type='SPELL',classes='SHAMAN')
ROOT_RULES={'DAL_431':('none',[('historical_horror_begin',SHAMAN_SPELLS)])}
TOKEN_RULES={'DAL_431t':('none',[('historical_horror_unbound',)])}

def bound_payload(entity):
 return bool(getattr(entity,'rule_state',{}).get('crafted_horror') or getattr(entity,'_crafted_definition',{}).get('state',{}).get('crafted_horror'))

def offer(game,owner,candidates,**state):
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Horror spell choice')
 game.pending_choice=dict(owner=owner,kind='historical_horror_teach',options=[dict(card_id=cid) for cid in game.rng.sample(list(candidates),min(3,len(candidates)))],**state)
 game.phase='choice'

def execute(game,op,ctx):
 if op[0]=='historical_horror_unbound':raise UnsupportedCard('Drustvar Horror requires its two physical taught spells')
 if op[0]!='historical_horror_begin':return False
 owner=ctx['owner']
 from .pools import require_fixed_cards
 require_fixed_cards(TOKEN_RULES,game.cards)
 values=game._learned_pool(op[1],owner)
 # Do not admit an implemented subset of the requested Shaman pool.
 if not values:raise UnsupportedCard('Horror has no eligible Shaman spells')
 modes={cid:game._learned_mode(cid,owner) for cid in values}
 offer(game,owner,values,values=tuple(values),modes=modes,first=None,_automatic=bool(ctx.get('automatic_choices',False)))
 return True

def split(game,op,ctx):
 if op[0]!='historical_horror_cast':return None
 cid=op[1]
 # The target is selected as a minion Battlecry. The spell keeps its own
 # damage, Overload and other casting context, without inheriting the body.
 context=dict(ctx,horror_target_source='DAL_431t')
 return game._cast_spell_split(('cast_fixed_spell',cid,'selected'),context)

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_horror_teach':return False
 owner=choice['owner'];cid=selected['card_id'];first=choice['first'];modes=choice['modes']
 if first is None:
  values=choice['values']
  if modes[cid]!='none':values=tuple(value for value in values if modes[value]=='none')
  if not values:raise UnsupportedCard('Horror second spell has no eligible untargeted outcomes')
  offer(game,owner,values,values=choice['values'],modes=modes,first=cid,_automatic=choice.get('_automatic',False))
 else:
  ids=(first,cid);target=next((modes[value] for value in ids if modes[value]!='none'),'none')
  card=Card(game._new_id(),'DAL_431t')
  card.rule_state=deepcopy(dict(crafted_horror=True,crafted_ops=tuple(('historical_horror_cast',value) for value in ids),crafted_target=target,forge_parts=ids,forge_keywords=(),forge_tribes=(),forge_death=(),forge_intrinsics=()))
  game._enter_hand(owner,card)
 return True
