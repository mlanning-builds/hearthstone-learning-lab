"""Complete literal Kazakus/Mixologist potion construction; unvalidated."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,random_cards

COST_CHOICES={1:'CFM_621t11',5:'CFM_621t12',10:'CFM_621t13'}
POTIONS={1:'CFM_621t',5:'CFM_621t14',10:'CFM_621t15'}
# Key: (actual ingredient identity, target mode, executable operations).
PARTS={
 1:{'damage':('CFM_621t2','character',(('damage',3),)),
    'area':('CFM_621t4','none',(('area_damage','all_minions',2),)),
    'freeze':('CFM_621t5','none',(('historical_potion_freeze',1),)),
    'demon':('CFM_621t10','none',(('summon','CFM_621_m4',1),)),
    'resurrect':('CFM_621t37','none',(('historical_resurrection_pick','all',1,()),)),
    'health':('CFM_621t6','none',(('board_buff',0,2),)),
    'draw':('CFM_621t8','none',(('draw',1),)),
    'random_demon':('CFM_621t9','none',(random_cards(pool(card_type='MINION',tribe='DEMON')),)),
    'armor':('CFM_621t3','none',(('armor',4),))},
 5:{'damage':('CFM_621t16','character',(('damage',5),)),
    'area':('CFM_621t18','none',(('area_damage','all_minions',4),)),
    'wool':('CFM_621t21','none',(('historical_potion_wool',False),)),
    'freeze':('CFM_621t19','none',(('historical_potion_freeze',2),)),
    'demon':('CFM_621t20','none',(('summon','CFM_621_m2',1),)),
    'resurrect':('CFM_621t38','none',(('historical_resurrection_pick','all',2,()),)),
    'health':('CFM_621t24','none',(('board_buff',0,4),)),
    'draw':('CFM_621t22','none',(('draw',2),)),
    'random_demon':('CFM_621t23','none',(random_cards(pool(card_type='MINION',tribe='DEMON'),2),)),
    'armor':('CFM_621t17','none',(('armor',7),))},
 10:{'damage':('CFM_621t25','character',(('damage',8),)),
    'area':('CFM_621t33','none',(('area_damage','all_minions',6),)),
    'wool':('CFM_621t29','none',(('historical_potion_wool',True),)),
    'freeze':('CFM_621t27','none',(('historical_potion_freeze',3),)),
    'demon':('CFM_621t28','none',(('summon','CFM_621_m3',1),)),
    'resurrect':('CFM_621t39','none',(('historical_resurrection_pick','all',3,()),)),
    'health':('CFM_621t32','none',(('board_buff',0,6),)),
    'draw':('CFM_621t30','none',(('draw',3),)),
    'random_demon':('CFM_621t31','none',(random_cards(pool(card_type='MINION',tribe='DEMON'),3),)),
    'armor':('CFM_621t26','none',(('armor',10),))},
}
# Stable execution order independent of the order the two choices were picked.
# Damage precedes freezing; summons follow board removal and precede Health.
ORDER=('damage','area','wool','freeze','demon','resurrect','health','draw','random_demon','armor')
TOKEN_RULES={cid:(mode,list(ops)) for tier in PARTS.values() for cid,mode,ops in tier.values()}
TOKEN_RULES.update({cid:('none',[('crafted_spell',)]) for cid in tuple(POTIONS.values())+('VAC_523t',)})
TOKEN_RULES.update({cid:('none',[('historical_potion_cost_guard',)]) for cid in COST_CHOICES.values()})
TOKEN_RULES.update({cid:('none',[]) for cid in ('CFM_621_m2','CFM_621_m3','CFM_621_m4','CFM_621_m5')})
ROOT_RULES={'CFM_621':('none',[('historical_potion_begin','kazakus')]),'VAC_523':('none',[('historical_potion_begin','mixologist')])}

def offer(game,owner,family,tier,picked=(),automatic=False):
 values=[key for key in PARTS[tier] if key not in picked]
 selected=game.rng.sample(values,3)
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite potion construction choice')
 game.pending_choice=dict(owner=owner,kind='historical_potion_part',options=[dict(card_id=PARTS[tier][key][0],ingredient=key) for key in selected],family=family,tier=tier,picked=tuple(picked),_automatic=automatic)
 game.phase='choice'

def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_potion_'):return False
 owner=ctx['owner'];player=game.players[owner]
 if name=='historical_potion_begin':
  family=op[1]
  if family=='kazakus':
   from .identities import canonical_identity
   identities=[canonical_identity(game._card_data(card),game.cards) for card in player.deck]
   if len(identities)!=len(set(identities)):return True
  from .pools import require_fixed_cards
  require_fixed_cards(tuple(TOKEN_RULES),game.cards)
  automatic=bool(ctx.get('automatic_choices',False))
  if family=='mixologist':offer(game,owner,family,1,automatic=automatic)
  else:
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite potion cost choice')
   game.pending_choice=dict(owner=owner,kind='historical_potion_cost',options=[dict(card_id=cid,tier=tier) for tier,cid in COST_CHOICES.items()],_automatic=automatic)
   game.phase='choice'
 elif name=='historical_potion_cost_guard':raise UnsupportedCard('Potion cost choice requires its construction context')
 elif name=='historical_potion_freeze':
  targets=[m for m in game.players[1-owner].minions if m.health>0]
  for target in game.rng.sample(targets,min(op[1],len(targets))):game._freeze(target.uid)
 elif name=='historical_potion_wool':
  targets=[m for side in (game.players if op[1] else (game.players[1-owner],)) for m in side.minions if m.health>0]
  if not op[1] and targets:targets=[game.rng.choice(targets)]
  for target in targets:
   if target in game.players[target.owner].minions and target.health>0:game._transform(target,'CFM_621_m5')
 else:return False
 return True

def resolve_choice(game,choice,selected):
 kind=choice['kind']
 if kind=='historical_potion_cost':
  offer(game,choice['owner'],'kazakus',selected['tier'],automatic=choice.get('_automatic',False));return True
 if kind!='historical_potion_part':return False
 picked=choice['picked']+(selected['ingredient'],);tier=choice['tier'];family=choice['family'];owner=choice['owner']
 if len(picked)<2:offer(game,owner,family,tier,picked,choice.get('_automatic',False));return True
 parts=[PARTS[tier][key] for key in ORDER if key in picked]
 card=Card(game._new_id(),'VAC_523t' if family=='mixologist' else POTIONS[tier])
 card.rule_state=dict(crafted_ops=tuple(operation for cid,mode,ops in parts for operation in ops),crafted_target='character' if 'damage' in picked else 'none',crafted_ingredients=tuple(PARTS[tier][key][0] for key in ORDER if key in picked),crafted_family=family)
 game._enter_hand(owner,card)
 return True
