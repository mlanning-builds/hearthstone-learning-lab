"""Ci'Cigi's literal first-edition family and its physical dependencies."""
from copy import deepcopy
FIRST_EDITION=('TOY_913t1','TOY_913t2','TOY_913t3','TOY_400t3','TOY_400t4','TOY_400t5','TOY_400t6','TOY_400t7','TOY_400t8','TOY_401t','TOY_401t2')
POWER_IDS=('TOY_400t6p','TOY_400t6p2')
ROOT_RULES={'TOY_913':('none',[('historical_mint_generate',),('outcast_operation',('historical_mint_generate',))])}
DEATH_EFFECTS={'TOY_913':[('historical_mint_generate',)]}
TOKEN_RULES={
 'TOY_913t1':('none',[]),
 'TOY_913t2':('none',[]),
 'TOY_913t3':('character',[('historic_when',('hero_attacked',),(('damage',4),))]),
 'TOY_400t3':('none',[('hero_attack',1),('add','TOY_400t3t',1)]),
 'TOY_400t3t':('none',[('hero_attack',1)]),
 'TOY_400t4':('none',[]),
 'TOY_400t5':('none',[]),
 'TOY_400t6':('none',[('historical_mint_metamorphosis',)]),
 'TOY_400t7':('none',[]),
 'TOY_400t8':('minion',[('damage',3)]),
 'TOY_401t':('none',[('historical_mint_skull',)]),
 'TOY_401t2':('none',[]),
}
TRIGGERS={'TOY_913t2':('hero_attack',[('buff_self',1,0)]),'TOY_401t2':(('historical_event','either_edge_play'),[('area_damage','enemies',1)])}
END_EFFECTS={'TOY_400t5':[('missiles','enemies',6)]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|set(POWER_IDS)

def split(game,op,ctx):
 if op[0]!='historical_mint_skull':return None
 return ('historical_mint_skull_draw',),(('historical_mint_skull_draw',),('historical_mint_skull_draw',))

def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_mint_'):return False
 owner=ctx['owner'];player=game.players[owner]
 if name=='historical_mint_generate':
  from .pools import require_fixed_cards
  require_fixed_cards(FIXED_TOKEN_IDS,game.cards)
  game._add(owner,game.rng.choice(FIRST_EDITION))
 elif name=='historical_mint_skull_draw':
  card=game._draw(owner,include_burned=True)
  if ctx.get('outcast') and card is not None and any(card is value for value in player.hand):
   card.cost_delta=getattr(card,'cost_delta',0)-3
 elif name=='historical_mint_metamorphosis':
  from .pools import require_fixed_cards
  require_fixed_cards(POWER_IDS,game.cards)
  game._replace_primary_power(owner,dict(card_id=POWER_IDS[0],remaining=2,restore=deepcopy(player.primary_power)))
 elif name=='historical_mint_warglaives':
  if ctx.get('target',0)>0:player.hero_attacks=max(0,player.hero_attacks-1)
 else:return False
 return True
