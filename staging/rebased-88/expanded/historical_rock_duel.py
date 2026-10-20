"""Physical Rock Duel token, mana payment and held end-turn explosion."""
from engine.cards import UnsupportedCard
PICK='JAM_037t'
ROOT_RULES={'JAM_037':('none',[('historical_rock_begin',)])}
TOKEN_RULES={PICK:('none',[('historical_rock_unplayable',)])}

def spend(game,owner,amount):
 player=game.players[owner]
 if amount<=0 or player.mana!=0:return
 # Snapshot only Picks actually held when this payment exhausts mana.
 # Admission to the other hand is not another mana-spend event.
 for card in list(player.hand):
  if card.card_id!=PICK:continue
  player.hand.remove(card)
  state=game._b60_state(card);state['historical_rock_damage']=state.get('historical_rock_damage',8)+2
  game._enter_hand(1-owner,card)
  game._log('rock_pass',player=owner,entity=card.uid,damage=state['historical_rock_damage'])

def turn_entries(game,phase):
 if phase!='end':return []
 return [dict(source=None,order=card.uid,operations=(('historical_rock_explode',card.uid),)) for card in game.players[game.current].hand if card.card_id==PICK]

def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_rock_'):return False
 owner=ctx['owner'];player=game.players[owner]
 if name=='historical_rock_unplayable':raise UnsupportedCard('Molten Pick of ROCK cannot be cast or played')
 if name=='historical_rock_begin':
  if ctx.get('finale',False):
   from .pools import require_fixed_cards
   require_fixed_cards((PICK,),game.cards)
   card=game._add(1-owner,PICK)
   if card is not None:game._b60_state(card)['historical_rock_damage']=8
 elif name=='historical_rock_explode':
  card=next((card for card in player.hand if card.uid==op[1] and card.card_id==PICK),None)
  if card is None:return True
  amount=getattr(card,'rule_state',{}).get('historical_rock_damage',8)
  player.hand.remove(card)
  game._zone_card_removed(owner,'hand',card,cause='destroy')
  game._refresh_auras()
  game._deal_effect(game.hero_id(owner),amount,dict(owner=owner,source=None,target=game.hero_id(owner),spell=False,bonus=0,lifesteal=False,physical_card=card,card_id=PICK))
 else:return False
 return True
