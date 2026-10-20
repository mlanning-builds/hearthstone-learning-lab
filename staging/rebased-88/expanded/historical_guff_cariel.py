"""Wildheart Guff's capacity/choices and Cariel's real weapon/hand buff."""
from engine.cards import UnsupportedCard
ROOT_RULES={
 'AV_205':('none',[('historical_guff_cap',),('historical_guff_crystal',),('draw',1)]),
 'AV_206':('none',[('area_damage','enemies',2),('equip','AV_146')]),
}
TOKEN_RULES={'AV_205a':('none',[('historical_guff_crystal',)]),'AV_205pb':('none',[('draw',1)]),'AV_146':('none',[])}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'AV_205p','AV_206p'}
OPTIONS=('AV_205pb','AV_205a')

def start_power(game,owner):
 from .historical_combined_choices import combined,consume
 if combined(game,owner):
  consume(game,owner);game._start_power_effects(owner,(('draw',1),('historical_guff_crystal',)))
 else:
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Nurture choice')
  game.pending_choice=dict(owner=owner,kind='historical_guff_power',options=[dict(card_id=cid) for cid in OPTIONS]);game.phase='choice'

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_guff_power':return False
 game._start_power_effects(choice['owner'],TOKEN_RULES[selected['card_id']][1]);return True

def split(game,op,ctx):
 if op[0]!='historical_guff_random':return None
 from .historical_combined_choices import combined,consume
 owner=ctx['owner']
 if combined(game,owner):
  consume(game,owner);operations=(('historical_copy_power_draw',1),('historical_guff_crystal',))
 else:operations=(game.rng.choice((('historical_copy_power_draw',1),('historical_guff_crystal',))),)
 return game._split_fixed_summon(('replay_context',operations,ctx),ctx)

def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];player=game.players[owner]
 if name=='historical_guff_cap':
  player.mana_capacity=20;player.max_mana=min(20,player.max_mana);player.mana=min(player.mana,max(0,player.max_mana-player.locked_mana))
 elif name=='historical_guff_crystal':
  player.max_mana=min(player.mana_capacity,player.max_mana+1)
 elif name=='historical_cariel_buff':
  values=[card for card in player.hand if game._card_data(card)['type']=='MINION']
  if values:
   from .historical_saidan import add
   card=game.rng.choice(values);add(card,'attack_bonus',4);add(card,'health_bonus',4)
 else:return False
 return True
