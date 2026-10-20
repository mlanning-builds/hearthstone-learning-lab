"""Persistent Mech Rush and all five Dr. Boom suit powers."""
from .generation_cards import pool,discover
MECHS=pool(card_type='MINION',tribe='MECHANICAL',classes='own_or_neutral')
POWERS=('BOT_238p1','BOT_238p2','BOT_238p3','BOT_238p4','BOT_238p6')
ROOT_RULES={'BOT_238':('none',[('historical_boom_rush',)])}
FIXED_TOKEN_IDS=frozenset(POWERS)|{'BOT_238p','BOT_312t'}


def rotate(game,owner):
 power=game.players[owner].primary_power
 if power is None or power['card_id'] not in POWERS+('BOT_238p',):return
 power['card_id']=game.rng.choice(tuple(cid for cid in POWERS if cid!=power['card_id']))
 game._log('boom_power_changed',player=owner,card=power['card_id'])


def power_operations(game,owner):
 power=game.players[owner].primary_power
 if power is None or power['card_id'] not in POWERS:return None
 cid=power['card_id']
 if cid=='BOT_238p1':return (('historical_copy_power_hit','target',3),)
 if cid=='BOT_238p2':return (('armor',7),)
 if cid=='BOT_238p3':return (('historical_boom_kaboom',),)
 if cid=='BOT_238p4':return (discover(MECHS),)
 return (('summon','BOT_312t',3),)


def split(game,op,ctx):
 if op[0]!='historical_boom_kaboom':return None
 enemy=1-ctx['owner']
 targets=(game.hero_id(enemy),)+tuple(m.uid for m in game.players[enemy].minions if m.health>0)
 operations=tuple(('replay_context',(('historical_copy_power_hit','target',1),),dict(ctx,target=uid)) for uid in targets)
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]


def execute(game,op,ctx):
 if op[0]!='historical_boom_rush':return False
 game.players[ctx['owner']].historical_boom_mechs_rush=True
 game._refresh_auras()
 return True
