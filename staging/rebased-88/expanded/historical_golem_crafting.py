"""All literal Golem Shaper choices and compiled physical definitions."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard

BODIES={1:'BAR_079_m1',5:'BAR_079_m2',10:'BAR_079_m3'}
KEYWORDS={'BAR_079t4':'RUSH','BAR_079t5':'TAUNT','BAR_079t6':'DIVINE_SHIELD','BAR_079t7':'LIFESTEAL','BAR_079t8':'STEALTH','BAR_079t9':'POISONOUS'}
# The archive reuses the Wildvine choice identity at the upper tier. The
# compiled value and explicit option label carry its tier-specific +4/+4.
POWERS={
 1:{'wildvine':('BAR_079t10',(('buff_others',1,1),),()),'copy':('BAR_079t11',(('copy_self_right',1),),()),'freeze':('BAR_079t12',(('historical_golem_freeze',1),),()),'damage':('BAR_079t13',(('historical_golem_fire',1),),()),'spell_damage':('BAR_079t14',(),(('spell_damage',1),)),'draw':('BAR_079t15',(('draw',1),),())},
 5:{'wildvine':('BAR_079t10b',(('buff_others',2,2),),()),'copy':('BAR_079t11',(('copy_self_right',1),),()),'freeze':('BAR_079t12b',(('historical_golem_freeze',2),),()),'damage':('BAR_079t13b',(('historical_golem_fire',2),),()),'spell_damage':('BAR_079t14b',(),(('spell_damage',2),)),'draw':('BAR_079t15b',(('draw',2),),())},
 10:{'wildvine':('BAR_079t10b',(('buff_others',4,4),),()),'copy':('BAR_079t11',(('copy_self_right',1),),()),'freeze':('BAR_079t12c',(('historical_golem_freeze',-1),),()),'damage':('BAR_079t13c',(('historical_golem_fire',-1),),()),'spell_damage':('BAR_079t14c',(),(('spell_damage',4),)),'draw':('BAR_079t15c',(('draw',4),),())},
}
TOKEN_IDS=frozenset(BODIES.values())|set(KEYWORDS)|{value[0] for tier in POWERS.values() for value in tier.values()}
TOKEN_RULES={cid:('none',[('historical_golem_unbound',)]) for cid in TOKEN_IDS}
ROOT_RULES={'BAR_079':('none',[('historical_golem_begin',)])}

def bound_payload(entity):
 state=getattr(entity,'rule_state',{})
 if state.get('crafted_golem'):return True
 return bool(getattr(entity,'_crafted_definition',{}).get('state',{}).get('crafted_golem'))

def offer(game,owner,kind,options,**state):
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Golem construction choice')
 game.pending_choice=dict(owner=owner,kind=kind,options=options,**state);game.phase='choice'

def split(game,op,ctx):
 if op[0]!='historical_golem_fire':return None
 owner=ctx['owner'];source=ctx.get('source')
 targets=[m for m in game.players[1-owner].minions if m.health>0]
 chosen=list(targets) if op[1]<0 else game.rng.sample(targets,min(op[1],len(targets)))
 operations=[]
 for minion in chosen:
  context=dict(ctx,target=minion.uid,spell=False,bonus=0,lifesteal=source is not None and 'LIFESTEAL' in game._effective_keywords(source))
  operations.append(('replay_context',(('damage',3),),context))
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+tuple(operations[1:])

def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_golem_'):return False
 owner=ctx['owner'];player=game.players[owner]
 if name=='historical_golem_begin':
  if any(game._card_stat(card,'cost',owner)==4 for card in player.deck):return True
  from .pools import require_fixed_cards
  require_fixed_cards(TOKEN_IDS,game.cards)
  offer(game,owner,'historical_golem_size',[dict(card_id=cid,tier=tier) for tier,cid in BODIES.items()],_automatic=bool(ctx.get('automatic_choices',False)))
 elif name=='historical_golem_unbound':raise UnsupportedCard('Golem body/choice requires its physical construction payload')
 elif name=='historical_golem_freeze':
  targets=[m for m in game.players[1-owner].minions if m.health>0]
  chosen=targets if op[1]<0 else game.rng.sample(targets,min(op[1],len(targets)))
  for minion in chosen:game._freeze(minion.uid)
 else:return False
 return True

def resolve_choice(game,choice,selected):
 kind=choice['kind'];owner=choice['owner'];automatic=choice.get('_automatic',False)
 if kind=='historical_golem_size':
  ids=game.rng.sample(list(KEYWORDS),3)
  offer(game,owner,'historical_golem_keyword',[dict(card_id=cid) for cid in ids],tier=selected['tier'],_automatic=automatic);return True
 if kind=='historical_golem_keyword':
  tier=choice['tier'];keys=game.rng.sample(list(POWERS[tier]),3)
  options=[dict(card_id=POWERS[tier][key][0],power=key) for key in keys]
  if tier==10:
   for option in options:
    if option['power']=='wildvine':option['label']='Wildvine: Give your other minions +4/+4.'
  offer(game,owner,'historical_golem_power',options,tier=tier,keyword=selected['card_id'],_automatic=automatic);return True
 if kind!='historical_golem_power':return False
 tier=choice['tier'];cid,operations,intrinsics=POWERS[tier][selected['power']]
 card=Card(game._new_id(),BODIES[tier]);keyword=KEYWORDS[choice['keyword']]
 card.rule_state=deepcopy(dict(crafted_ops=operations,crafted_target='none',crafted_golem=True,forge_parts=(choice['keyword'],cid),forge_tribes=(),forge_keywords=(keyword,),forge_death=(),forge_intrinsics=intrinsics))
 game._enter_hand(owner,card)
 return True
