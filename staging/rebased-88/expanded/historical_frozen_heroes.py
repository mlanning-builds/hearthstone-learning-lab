"""Deathseer transformation and Shadowreaper destruction/refresh programs."""
ROOT_RULES={
 'ICC_481':('none',[('mutation_board',2,False)]),
 'ICC_830':('none',[('historical_frozen_anduin',)]),
}
FIXED_TOKEN_IDS=frozenset(('ICC_481p','ICC_830p'))


def event(game,kind,data):
 owner=data.get('owner')
 if owner not in (0,1) or kind not in ('minion_played','spell_cast','dormant_other_card_played'):return
 player=game.players[owner]
 if player.primary_power is not None and player.primary_power['card_id']=='ICC_830p':
  player.power_used=False
  game._log('voidform_refresh',player=owner)


def execute(game,op,ctx):
 if op[0]!='historical_frozen_anduin':return False
 # One simultaneous destruction group; shared death processing handles the
 # resulting Deathrattles after every eligible living minion is marked dead.
 for player in game.players:
  for minion in tuple(player.minions):
   if minion.health>0 and minion.attack>=5:minion.health=0
 return True
