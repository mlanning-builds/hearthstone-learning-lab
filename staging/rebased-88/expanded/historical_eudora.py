"""Eudora sidequest and the complete frozen CardDefs tag-3431 loot pool.

New implementation; gameplay and exact event priority remain unvalidated.
"""
from engine.cards import UnsupportedCard
from .pools import require_fixed_cards
from .selectors import classes,HERO_CLASSES
TREASURES=('VAC_464t10', 'VAC_464t11', 'VAC_464t12', 'VAC_464t14', 'VAC_464t15', 'VAC_464t16', 'VAC_464t17', 'VAC_464t18', 'VAC_464t19', 'VAC_464t2', 'VAC_464t20', 'VAC_464t21', 'VAC_464t22', 'VAC_464t23', 'VAC_464t24', 'VAC_464t25', 'VAC_464t26', 'VAC_464t27', 'VAC_464t28', 'VAC_464t29', 'VAC_464t3', 'VAC_464t30', 'VAC_464t4', 'VAC_464t5', 'VAC_464t6', 'VAC_464t7', 'VAC_464t8', 'VAC_464t9')

def start(game,owner):
 p=game.players[owner]
 if getattr(p,'eudora_sidequest',None) is not None:return
 if len(p.secrets)+game._quest_slots(owner)>=5:
  game._log('quest_fizzle',player=owner,card='VAC_464t',reason='capacity');return
 require_fixed_cards(TREASURES,game.cards)
 p.eudora_sidequest=dict(card_id='VAC_464t',progress=0,total=3)
 game._log('quest_start',player=owner,card='VAC_464t')

def played(game,owner,card):
 p=game.players[owner];q=getattr(p,'eudora_sidequest',None)
 if q is None:return
 printed=classes(game._card_data(card)) & HERO_CLASSES
 if not printed or p.hero_class in printed:return
 q['progress']+=1
 game._log('quest_progress',player=owner,card='VAC_464t',progress=q['progress'])
 if q['progress']<3:return
 p.eudora_sidequest=None
 game._log('quest_complete',player=owner,card='VAC_464t')
 game._rule_events.append(('captured_effects',dict(operations=(('historical_eudora_reward',),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))

def offer(game,owner,remaining,ctx):
 if game.pending_choice is not None:raise UnsupportedCard('Eudora cannot overwrite a pending choice')
 require_fixed_cards(TREASURES,game.cards)
 ids=game.rng.sample(TREASURES,3)
 game.pending_choice=dict(owner=owner,kind='historical_eudora',options=[dict(card_id=cid) for cid in ids],remaining=remaining,context=dict(ctx),_automatic=bool(ctx.get('automatic_choices',False)))
 game.phase='choice'

def execute(game,op,ctx):
 if op[0]=='historical_eudora_start':start(game,ctx['owner']);return True
 if op[0]=='historical_eudora_reward':offer(game,ctx['owner'],2,ctx);return True
 return False

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_eudora':return False
 cid=selected.get('card_id')
 if cid not in {item['card_id'] for item in choice['options']}:raise UnsupportedCard('Eudora treasure was not offered')
 game._add(choice['owner'],cid)
 if choice['remaining']>1:offer(game,choice['owner'],choice['remaining']-1,choice['context'])
 return True
