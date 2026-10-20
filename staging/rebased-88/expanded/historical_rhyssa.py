"""Rhyssa repeats activated Secret effects without replaying physical cards."""
ROOT_RULES={'DAL_573':('none',[])}

def trigger(game,owner,secret,operations,context):
 repetitions=2 if any(m.card_id=='DAL_573' and not m.silenced and m.health>0 for m in game.players[owner].minions) else 1
 game._reveal_secret(owner,secret)
 for operation in operations:game._effect(operation,context)
 if repetitions>1:
  repeated=(('historical_rhyssa_notify',secret.card_id),)+tuple(operations)
  game._rule_events.append(('captured_effects',dict(operations=repeated,context=dict(context)),[]))
  game._settle(allow_event_choices=True)

def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];enemy=game.players[1-owner]
 if name=='historical_rhyssa_notify':
  game._queue_event('historical_secret_revealed',owner=owner,card_id=op[1])
  game._log('secret_trigger_repeated',player=owner,card=op[1])
 elif name=='historical_rhyssa_transform':
  target=next((m for player in game.players for m in player.minions if m.uid==op[1] and m.health>0),None)
  if target is not None:game._transform(target,'CS2_tk1')
 elif name=='historical_rhyssa_bounce':
  target=next((m for player in game.players for m in player.minions if m.uid==op[1] and m.health>0),None)
  if target is not None:game._bounce(target,2)
 elif name=='historical_rhyssa_runes':
  target=next((m for m in enemy.minions if m.uid==op[1] and m.health>0),None)
  amount=6+ctx.get('bonus',0);excess=max(0,amount-(target.health if target is not None else 0))
  with game._damage_batch():
   if target is not None:game._damage(target.uid,amount,damage_source=None,damage_owner=owner)
   if excess:game._damage(game.hero_id(1-owner),excess,damage_source=None,damage_owner=owner)
 elif name=='historical_rhyssa_pressure':
  values=[m for m in enemy.minions if m.health>0]
  if values:game.rng.choice(values).health=0
 elif name=='historical_rhyssa_resummon':
  game._summon(owner,op[1],min(op[2],len(game.players[owner].board)),entry_origin='secret',entry_site='untimely_death',entry_source=ctx.get('secret_card'))
 elif name=='historical_rhyssa_infinity':
  from .infinity import INFINITY
  values=[m for m in enemy.minions if m.health>0]
  if values:
   high=max(m.health for m in values);target=game.rng.choice([m for m in values if m.health==high])
   game._damage(target.uid,INFINITY,damage_owner=owner,damage_source=None)
 else:return False
 return True
