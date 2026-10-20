"""Historical Hagatha, Gul'dan and Kurtrus Hero programs."""
from .generation_cards import pool,random_cards
SHAMAN_SPELLS=pool(card_type='SPELL',classes='SHAMAN')
ROOT_RULES={
 'GIL_504':('none',[('area_damage','all_minions',3)]),
 'ICC_831':('none',[('historical_resurrection_pick','demon',-1,())]),
 'AV_204':('none',[('historical_dark_kurtrus',)]),
}
TOKEN_RULES={'AV_204t2':('none',[])}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'GIL_504h','ICC_831p','AV_204p'}

def event(game,kind,data):
 owner=data.get('owner')
 if owner not in (0,1):return
 player=game.players[owner];power=player.primary_power
 if power is None:return
 if power['card_id']=='GIL_504h' and kind=='minion_played':
  game._rule_events.append(('captured_effects',dict(operations=(random_cards(SHAMAN_SPELLS),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='GIL_504h')),[]))
 if power['card_id']=='AV_204p' and kind=='minion_attack':
  player.power_used=False
  game._log('kurtrus_refresh',player=owner)

def split(game,op,ctx):
 if op[0]!='historical_dark_kurtrus':return None
 count=game.players[ctx['owner']].hero_attacks_total
 operations=(('historical_dark_bat',count),)*2
 return operations[0],operations[1:]

def execute(game,op,ctx):
 owner=ctx['owner']
 if op[0]=='historical_dark_bat':
  game._summon(owner,'AV_204t2',attack_bonus=op[1],entry_origin='hero_battlecry',entry_site='kurtrus')
  return True
 if op[0]=='historical_dark_siphon':
  game._effect(('historical_copy_power_hit','target',3),dict(ctx,lifesteal=True))
  return True
 return False
