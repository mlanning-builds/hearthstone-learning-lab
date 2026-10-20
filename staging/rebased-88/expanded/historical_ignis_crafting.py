"""Ignis construction and physical custom-weapon consumers; unvalidated."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
WEAPONS=('TTN_060t','TTN_060t1','TTN_060t2')
KEYWORDS=('TTN_060t3','TTN_060t4','TTN_060t5','TTN_060t6','TTN_060t9')
KEYWORD_VALUES={
 'TTN_060t3':('POISONOUS',), 'TTN_060t4':('LIFESTEAL',),
 'TTN_060t5':('WINDFURY',), 'TTN_060t6':(),
 'TTN_060t9':('IMMUNE_WHILE_ATTACKING',),
}
EFFECTS=(
 ('TTN_060t7','TTN_060t8','TTN_060t10','TTN_060t12','TTN_060t13'),
 ('TTN_060t7t','TTN_060t8t','TTN_060t10t','TTN_060t12t','TTN_060t13t'),
 ('TTN_060t7t1','TTN_060t8t1','TTN_060t10t1','TTN_060t12t1','TTN_060t13t1'),
)
SCALE=((1,2,2,2,1),(2,4,4,4,2),(4,8,8,6,3))
ROOT_RULES={'TTN_751':('none',[('historical_ignis_begin',)])}
FIXED_TOKEN_IDS=frozenset(WEAPONS+KEYWORDS+tuple(cid for row in EFFECTS for cid in row))


def offer(game,owner,stage,ids,*,weapon=None,keyword=None,automatic=False):
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Ignis construction')
 offered=tuple(ids) if stage=='size' else tuple(game.rng.sample(list(ids),min(3,len(ids))))
 game.pending_choice=dict(owner=owner,kind='historical_ignis_craft',stage=stage,weapon=weapon,keyword=keyword,_automatic=automatic,options=[dict(card_id=cid) for cid in offered])
 game.phase='choice'


def begin(game,owner,context):
 if not getattr(game.players[owner],'historical_forges',0):return
 from .pools import require_fixed_cards
 # All literal branches are checked before an offer consumes RNG.
 require_fixed_cards(FIXED_TOKEN_IDS,game.cards)
 offer(game,owner,'size',WEAPONS,automatic=bool(context.get('automatic_choices',False)))


def build(game,weapon,keyword,effect):
 tier=WEAPONS.index(weapon)
 index=EFFECTS[tier].index(effect);amount=SCALE[tier][index]
 keywords=KEYWORD_VALUES[keyword]
 battlecry=(('historical_ignis_pain',amount),) if index==3 else ()
 death=(('area_damage','enemies',amount),) if index==0 else ()
 after=(('armor',amount),) if index==1 else (('historical_ignis_summon',amount),) if index==2 else (('draw',amount),) if index==4 else ()
 card=Card(game._new_id(),weapon)
 card.rule_state=dict(crafted_ops=battlecry,crafted_target='character' if battlecry else 'none',crafted_ignis=dict(tier=tier,keyword=keyword,effect=effect,keywords=keywords,cleave=keyword=='TTN_060t6',after=after,death=death))
 game._remember_crafted(card)
 return card


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_ignis_craft':return False
 owner=choice['owner'];cid=selected['card_id'];stage=choice['stage'];automatic=choice.get('_automatic',False)
 if stage=='size':offer(game,owner,'keyword',KEYWORDS,weapon=cid,automatic=automatic)
 elif stage=='keyword':offer(game,owner,'effect',EFFECTS[WEAPONS.index(choice['weapon'])],weapon=choice['weapon'],keyword=cid,automatic=automatic)
 elif stage=='effect':
  card=build(game,choice['weapon'],choice['keyword'],cid)
  game._enter_hand(owner,card);game._refresh_auras()
 else:raise UnsupportedCard('Unknown Ignis construction stage')
 return True


def payload(card):
 return deepcopy(getattr(card,'rule_state',{}).get('crafted_ignis'))


TOKEN_RULES={cid:('none',[('historical_ignis_unbound',)]) for cid in WEAPONS}


def equip(game,owner,card):
 definition=payload(card)
 if definition is None:return
 weapon=game.players[owner].weapon
 weapon['historical_keywords']=tuple(definition['keywords'])
 weapon['historical_ignis_cleave']=definition['cleave']
 weapon['attached_death_effects']=deepcopy(list(definition['death']))


def after_attack(game,owner,card):
 definition=payload(card)
 if definition is None or not definition['after']:return
 game._rule_events.append(('captured_effects',dict(operations=definition['after'],context=dict(owner=owner,source=None,target=0,bonus=0,spell=False,lifesteal=False,card_id=card.card_id)),[]))


def split(game,op,ctx):
 if op[0]!='historical_ignis_summon':return None
 from .generation_cards import pool,random_cards
 return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=op[1],maximum=op[1]),destination='board'),ctx)


def execute(game,op,ctx):
 if op[0]=='historical_ignis_begin':begin(game,ctx['owner'],ctx);return True
 if op[0]=='historical_ignis_unbound':raise UnsupportedCard('Runic weapon requires its physical Ignis definition')
 if op[0]=='historical_ignis_pain':
  definition=payload(ctx.get('physical_card'))
  if definition is None:raise UnsupportedCard('Missing crafted weapon Battlecry payload')
  keywords=definition['keywords']
  game._deal_effect(ctx.get('target',0),op[1],dict(ctx,source=None,spell=False,bonus=0,lifesteal='LIFESTEAL' in keywords,poisonous='POISONOUS' in keywords))
  return True
 return False
