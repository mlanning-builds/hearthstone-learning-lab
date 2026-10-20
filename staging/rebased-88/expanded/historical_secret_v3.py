"""Remaining native Secret consumers and physical Kidnap memory; unvalidated."""
from copy import deepcopy
from engine.game import Card
SECRETS={'NX2_013':'zombees','TSC_929':'emergency_maneuvers','REV_516':'vengeful_visage','WW_422':'azerite_vein','REV_828':'kidnap'}
TOKEN_RULES={cid:('none',[('secret',cid)]) for cid in SECRETS}
TOKEN_RULES.update({cid:('none',[]) for cid in ('NX2_013t','REV_828t')})
DEATH_EFFECTS={'REV_828t':[('historical_secret_v3_sack_return',)]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def event_program(game,secret,event,owner,actor,data):
 p=game.players[owner];q=game.players[actor];cid=secret.card_id
 if cid=='WW_422' and event=='card_paid':
  card=data.get('physical_card')
  if card is not None and getattr(card,'_hand_entry_turn',None)==game.turn:return (('historical_secret_v3_azerite',deepcopy(card)),)
 if cid in ('NX2_013','REV_828') and event=='after_card' and len(p.board)<7:
  target=next((m for m in q.minions if m.uid==data.get('source') and m.health>0),None)
  if target is not None:return ((('historical_secret_v3_zombees',target.uid) if cid=='NX2_013' else ('historical_secret_v3_kidnap',target.uid)),)
 if cid=='REV_516' and event=='after_attack' and data.get('target')==game.hero_id(owner) and len(p.board)<7:
  source=data.get('source_snapshot')
  if source is not None:return (('historical_secret_v3_visage',source),)
 return None


def split(game,op,ctx):
 owner=ctx['owner'];name=op[0]
 if name=='historical_secret_v3_zombee_group':
  state=dict(summoned=[]);operations=tuple(('historical_secret_v3_zombee_summon',state) for _ in range(4))+(('historical_secret_v3_zombee_attacks',state,op[1]),)
  return operations[0],operations[1:]
 if name=='historical_secret_v3_zombee_attacks':
  operations=tuple(('force_pair',uid,op[2]) for uid in op[1]['summoned'])
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_secret_v3_visage_group':
  state=dict(summoned=[],mode='random_enemy_character')
  return ('historical_secret_v3_visage_summon',op[1],state),(('historical_secret_v3_visage_attacks',state),)
 if name=='historical_secret_v3_visage_attacks':
  operations=tuple(('force_pair',uid,game.hero_id(1-owner)) for uid in op[1]['summoned'])
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 return None


def return_bound(game,bound):
 if bound is None:return
 card=game._fresh_replay_card(bound);game._carry_origin(bound,card);game._enter_hand(bound.owner,card)


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_secret_v3_azerite':
  card=game._copy_card(op[1],source_owner=1-owner);card.set_cost=0;card.cost_delta=0;game._enter_hand(owner,card)
 elif name in ('historical_secret_v3_zombees','historical_secret_v3_visage'):
  operation=('historical_secret_v3_zombee_group',op[1]) if name=='historical_secret_v3_zombees' else ('historical_secret_v3_visage_group',deepcopy(op[1]))
  game._rule_events.append(('captured_effects',dict(operations=(operation,),context=dict(ctx)),[]))
 elif name=='historical_secret_v3_zombee_summon':
  before={m.uid for m in p.minions};game._summon(owner,'NX2_013t',entry_origin='secret',entry_site='zombees')
  op[1]['summoned'].extend(m.uid for m in p.minions if m.uid not in before and m.card_id=='NX2_013t')
 elif name=='historical_secret_v3_visage_summon':
  before={m.uid for m in p.minions};source=op[1]
  game._summon(owner,source.card_id,copy_from=source,entry_origin='secret',entry_site='vengeful_visage')
  op[2]['summoned'].extend(m.uid for m in p.minions if m.uid not in before and m.card_id==source.card_id)
 elif name=='historical_secret_v3_emergency':
  from .historical_secret_batches import blocked
  secret=next((secret for secret in p.secrets if secret.uid==op[1] and secret.card_id=='TSC_929'),None)
  if secret is not None and owner!=game.current and len(p.board)<7 and not blocked(game):
   context=dict(ctx,secret_card=secret,card_id=secret.card_id)
   game._trigger_secret_program(owner,secret,(('historical_secret_v3_emergency_summon',op[2],op[3]),),context)
 elif name=='historical_secret_v3_emergency_summon':
  source=op[1];game._summon(owner,source.card_id,min(op[2],len(p.board)),copy_from=source,dormant_turns=1,entry_origin='secret',entry_site='emergency_maneuvers')
 elif name=='historical_secret_v3_kidnap':
  target=next((m for player in game.players for m in player.minions if m.uid==op[1] and m.health>0),None)
  if target is not None and len(p.board)<7:
   card=Card(game._new_id(),'REV_828t');card._bound_minion=deepcopy(target)
   game.players[target.owner].board.remove(target);game._pending_summon_events.pop(target.uid,None)
   game._summon(owner,'REV_828t',entry_source=card,entry_zone='hand',entry_origin='secret',entry_site='kidnap');game._refresh_auras()
 elif name=='historical_secret_v3_sack_return':return_bound(game,getattr(ctx.get('source'),'_bound_minion',None))
 else:return False
 return True
