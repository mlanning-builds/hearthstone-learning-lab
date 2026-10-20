"""Explicit 50/50 attack redirection and chronological Secret checks.

No legality filtering is applied to replacement targets: Forgetful can bypass
Taunt, Stealth, Immunity selection restrictions and initial Rush hero limits.
Gameplay conformance remains deferred.
"""
from engine.cards import UnsupportedCard
OWN=frozenset(('AT_088','DMF_068','GVG_065','GVG_066','GVG_088','WW_418'))

def live(game,uid):
 return next((m for p in game.players for m in p.minions if m.uid==uid and m.health>0),None)

def plan(game,source,target,*,forced=False):
 owner=live(game,source).owner if source>0 and live(game,source) is not None else -source-1
 if owner not in (0,1):return None
 used=set();checked=set()
 for _ in range(256):
  attacker=live(game,source) if source>0 else None
  if game.terminal or source>0 and attacker is None or target>0 and live(game,target) is None:return None
  pending=[]
  if attacker is not None and attacker.card_id=='WW_419' and not attacker.silenced and ('rider',source) not in used:pending.append((attacker.uid,'rider',source))
  if attacker is not None and not attacker.silenced and attacker.card_id in OWN and ('own',source) not in used:pending.append((attacker.uid,'own',source))
  if attacker is not None:
   for player in game.players:
    for m in player.minions:
     if m.card_id=='GVG_112' and not m.silenced and m.health>0 and ('mogor',m.uid) not in used:pending.append((m.uid,'mogor',m.uid))
  defender=live(game,target) if target>0 else None
  if defender is not None and defender.owner!=owner and defender.card_id=='TRL_532' and not defender.silenced and ('announcer',defender.uid) not in used:pending.append((defender.uid,'announcer',defender.uid))
  for secret in game.players[1-owner].secrets:
   if secret.uid not in checked:pending.append((getattr(secret,'_secret_entry_order',secret.uid),'secret',secret.uid))
  if not pending:return target
  _,kind,uid=min(pending)
  if kind=='secret':
   checked.add(uid)
   secret=next((c for c in game.players[1-owner].secrets if c.uid==uid),None)
   if secret is not None:
    from .historical_iconic_attack_secrets import redirect
    handled,replacement=redirect(game,1-owner,source,target,secret)
    if handled:
     target=replacement
     continue
   if game._secret_event('attack',owner,source=source,target=target,_only_secret_uid=uid):return None
   continue
  used.add((kind,uid))
  if kind=='rider':
   if game.rng.randrange(2)==0:
    if not forced:attacker.attacks+=1
    game._effect(('hero_attack',3),dict(owner=owner,source=attacker,target=0,bonus=0,lifesteal=False))
    game._log('attack_replaced',player=owner,source=source,card='WW_419')
    return None
   continue
  alternatives=[game.hero_id(1-owner)]+[m.uid for m in game.players[1-owner].minions if m.health>0]
  alternatives=[candidate for candidate in alternatives if candidate!=target]
  if alternatives and game.rng.randrange(2)==0:
   previous=target;target=game.rng.choice(alternatives);checked.clear()
   game._log('attack_redirected',source=source,previous=previous,target=target,trigger=uid)
 raise UnsupportedCard('Attack replacement sequence exceeded explicit depth limit')
