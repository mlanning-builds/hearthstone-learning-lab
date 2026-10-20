"""Literal remaining mana, held-cost and multi-choice historical spells."""
from itertools import product
from engine.game import Card
TOKEN_RULES={
 'AT_043':('none',[('gain_full_crystals',10),('historical_utility_state_discard_hand',)]),
 'BAR_539':('none',[('historical_utility_state_alignment',)]),
 'GDB_882':('none',[('summon','GDB_882t',3),('historical_utility_state_cosmic',)]),
 'GDB_882t':('none',[]),
 'ULD_726':('none',[('historical_draw_batch',(('type','eq','SPELL'),('mechanic','eq','SECRET')),'set_cost',(0,),'random')]),
 'VAC_907':('none',[]),
}
PARTS=(('Draw',('draw',2)),('Armor',('armor',5)),('Refresh',('refresh_mana',3)))
CHOICES={'VAC_907':[(' / '.join(PARTS[i][0] for i in indices),'none',[PARTS[i][1] for i in indices]) for indices in product(range(3),repeat=3)]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner]
 if op[0]=='historical_utility_state_discard_hand':game._discard_cards(owner,list(p.hand))
 elif op[0]=='historical_utility_state_alignment':
  p.mana=p.max_mana=0
  for zone in (p.hand,p.deck):
   for i,c in enumerate(zone):
    if isinstance(c,str):c=Card(game._new_id(),c);zone[i]=c
    game._set_card_cost(c,1)
 elif op[0]=='historical_utility_state_cosmic':
  if len(p.board)>=7:
   for m in p.minions:game._buff(m,1,1)
 else:return False
 return True
