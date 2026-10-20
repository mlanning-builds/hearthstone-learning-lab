"""Persistent Elemental Lifesteal and resumable Icy Touch kill reward."""
ROOT_RULES={'ICC_833':('none',[('summon','CS2_033',1),('historical_jaina_aura',)])}
FIXED_TOKEN_IDS=frozenset(('ICC_833h','CS2_033'))


def split(game,op,ctx):
 if op[0]!='historical_jaina_touch':return None
 owner=ctx['owner'];uid=ctx.get('target',0)
 victim=next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)
 state=dict(victim=victim,prior_damage=getattr(game.players[owner],'historical_power_damage_total',0))
 return ('historical_copy_power_hit','target',1),(('historical_jaina_after',state),)


def execute(game,op,ctx):
 owner=ctx['owner'];player=game.players[owner]
 if op[0]=='historical_jaina_aura':
  player.historical_jaina_elementals_lifesteal=True
  game._refresh_auras()
  return True
 if op[0]=='historical_jaina_after':
  state=op[1];victim=state['victim']
  dealt=getattr(player,'historical_power_damage_total',0)-state['prior_damage']
  if victim is not None and victim.health<=0 and dealt>0:
   game._summon(owner,'CS2_033',entry_origin='hero_power',entry_site='icy_touch')
  return True
 return False
