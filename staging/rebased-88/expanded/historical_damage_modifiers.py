"""Historical passive damage/healing integration; gameplay review deferred."""

def count(game,cid,owner):
 return sum(m.card_id==cid and not m.silenced and m.health>0 for m in game.players[owner].minions)

def power_multiplier(game,owner):
 return 2**(count(game,'EX1_350',owner)+count(game,'GIL_646',owner))

def spell_multiplier(game,owner):
 return 2**count(game,'EX1_350',owner)

def incoming(game,target,amount,source):
 if target>0:
  if source is not None and source.card_id=='VAC_936' and not getattr(source,'silenced',False):amount*=8
 else:
  amount+=sum(count(game,'SW_446',owner) for owner in (0,1))
  weapon=game.players[-target-1].weapon
  if weapon is not None and weapon['card_id']=='ETC_078t':amount+=1
  if count(game,'LOE_119',-target-1):amount=min(1,amount)
  if weapon is not None and weapon['card_id']=='AV_146':amount=(amount+1)//2
 return amount

def healing_blocked(game,target):
 owner=-target-1 if target<0 else game._find(target).owner
 return bool(count(game,'LEG_RLK_115',1-owner))


def redirected_target(game,target,used):
 """One predamage redirection at a time; a bearer redirects each hit once.

 Mortally wounded bearers remain active until the shared death checkpoint.
 The caller retains damage source/controller and prevents repeated application
 of source-wide modifiers while the proposed target changes.
 """
 owner=-target-1 if target<0 else game._find(target).owner
 player=game.players[owner]
 tamsin=getattr(player,'historical_stormwind_tamsin_uid',None)
 if target<0 and owner==game.current and tamsin is not None and tamsin not in used:return game.hero_id(1-owner),tamsin
 bearers=[m for m in player.minions if not m.silenced and not m.dormant and m.uid not in used]
 candidates=[]
 if target<0:
  candidates=[m for m in bearers if m.card_id=='AT_124' or (m.card_id=='VAC_501' and game.current==owner)]
 else:
  victim=game._find(target)
  if victim in player.board:
   index=player.board.index(victim)
   candidates=[m for m in bearers if m.card_id=='TRL_535' and m in player.board and abs(player.board.index(m)-index)==1]
 if not candidates:return None
 bearer=min(candidates,key=lambda m:m.uid)
 if bearer.card_id=='VAC_501':
  opponent=game.players[1-owner]
  values=[game.hero_id(1-owner)]+[m.uid for m in opponent.minions if m.health>0]
  return game.rng.choice(values),bearer.uid
 return bearer.uid,bearer.uid
