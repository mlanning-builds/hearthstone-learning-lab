"""Frozen Harmonic/Dissonant effects and physical hand swaps; unvalidated."""
from .generation_cards import pool,discover
from .historical_saidan import add as add_stat
PAIRS={cid:cid+'t' for cid in ('ETC_314','ETC_379','ETC_427','ETC_506','ETC_717')}
PAIRS.update({'WORK_050':'WORK_050t','WORK_017':'WORK_017t','WORK_030':'WORK_030t'})
SWAPS=dict(PAIRS);SWAPS.update({value:key for key,value in PAIRS.items()})
TOKEN_RULES={
 'ETC_314':('none',[('area_damage','all_minions',3),('historical_harmonic_popstar',6)]),
 'ETC_314t':('none',[('area_damage','all_minions',6),('historical_harmonic_popstar',3)]),
 'ETC_314t2':('none',[]),
 'ETC_379':('none',[('hero_attack',2),('armor',4)]),
 'ETC_379t':('none',[('hero_attack',4),('armor',2)]),
 'ETC_427':('none',[('historical_harmonic_metal',4,2)]),
 'ETC_427t':('none',[('historical_harmonic_metal',2,4)]),
 'ETC_506':('none',[discover(pool(card_type='MINION',minimum=5,maximum=5,classes='own_or_neutral'),destination='board',attack=1,health=1)]),
 'ETC_506t':('none',[discover(pool(card_type='MINION',minimum=1,maximum=1,classes='own_or_neutral'),destination='board',attack=5,health=5)]),
 'ETC_717':('character',[('damage',1),('weapon_buff',3,0)]),
 'ETC_717t':('character',[('damage',3),('weapon_buff',1,0)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def turn_entries(game,phase):
 if phase!='end':return []
 return [dict(source=None,order=card.uid,card_id=card.card_id,operations=(('historical_harmonic_swap',card.uid,card.card_id),))
         for card in tuple(game.players[game.current].hand) if card.card_id in SWAPS]

def execute(game,op,ctx):
 owner=ctx['owner'];player=game.players[owner]
 if op[0]=='historical_harmonic_popstar':
  game._summon(owner,'ETC_314t2',entry_stats=(op[1],op[1]),entry_origin='effect',entry_site='harmonic_pop')
 elif op[0]=='historical_harmonic_metal':
  cards=[card for card in player.hand if game._card_data(card)['type']=='MINION']
  for card in game.rng.sample(cards,min(op[1],len(cards))):
   add_stat(card,'attack_bonus',op[2]);add_stat(card,'health_bonus',op[2])
 elif op[0]=='historical_harmonic_swap':
  card=next((card for card in player.hand if card.uid==op[1] and card.card_id==op[2]),None)
  if card is not None:card.card_id=SWAPS[card.card_id]
 else:return False
 return True
