"""Explicit death-history and resurrection spell outcomes; unvalidated."""
from .selectors import has_tribe,has_class
from .identities import canonical_identity
from .generation_cards import pool,random_cards
from .death_inheritance import capture
TOKEN_RULES={
 'ETC_208':('none',[('historical_death_spell_resurrect','large_beasts')]),
 'RLK_652':('none',[('historical_death_spell_resurrect','small_all')]),
 'RLK_812':('none',[('historical_death_spell_resurrect','small_one')]),
 'TOY_886':('none',[('historical_death_spell_resurrect','last_demon')]),
 'TTN_855t':('none',[('historical_death_spell_resurrect','class_three')]),
 'TTN_855':('none',[('historical_death_spell_resurrect','class_four')]),
 'JAM_008':('none',[('historical_death_spell_dead_air',)]),
 'RLK_536':('friendly_minion',[('historical_batch_trigger_target_death',),('historical_death_spell_destroy_target',)]),
 'ETC_424':('minion',[('historical_death_spell_spread',)]),
 'WW_812':('none',[('historical_death_spell_saddle',)]),
 'TID_715':('none',[('historical_death_spell_colossal_hands',)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_death_spell_resurrect':
  mode=op[1];records=list(p.death_records);stats=None
  if mode=='large_beasts':records=[r for r in records if has_tribe(game._card_data(r['entity']),'BEAST') and game._card_data(r['entity']).get('cost',0)>=5]
  elif mode in ('small_all','small_one'):records=[r for r in records if game._card_data(r['entity']).get('cost',0)<=(2 if mode=='small_all' else 3)]
  elif mode=='last_demon':records=[r for r in records if has_tribe(game._card_data(r['entity']),'DEMON')][-1:]
  elif mode in ('class_three','class_four'):records=[r for r in records if has_class(game._card_data(r['entity']),p.hero_class)];stats=(2,2)
  if mode=='small_one':records=[game.rng.choice(records)] if records else []
  elif stats is not None:
   selected=[]
   for _ in range(4 if mode=='class_four' else 3):
    if not records:break
    record=game.rng.choice(records);selected.append(record)
    identity=canonical_identity(game._card_data(record['entity']),game.cards)
    records=[r for r in records if canonical_identity(game._card_data(r['entity']),game.cards)!=identity]
   records=selected
  elif mode in ('large_beasts','small_all'):game.rng.shuffle(records)
  operations=tuple(('historical_death_spell_summon',game._fresh_replay_card(r['entity']),stats) for r in records)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_death_spell_dead_air':
  targets=[m for m in p.minions if m.health>0 and has_tribe(game._card_data(m),'UNDEAD') and not game._fire_immune_target(m.uid,ctx)]
  states=tuple(dict(uid=m.uid,card=game._fresh_replay_card(m)) for m in targets)
  return ('historical_death_spell_destroy_uids',tuple(state['uid'] for state in states)),tuple(('historical_death_spell_resummon_confirmed',state) for state in states)
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
 if name=='historical_death_spell_summon':
  card=op[1];game._summon(owner,card.card_id,entry_source=card,entry_zone='deck',entry_origin='resurrection',entry_stats=op[2],entry_site='historical_death_spell')
 elif name=='historical_death_spell_destroy_target':
  if target is not None and not game._fire_immune_target(target.uid,ctx):target.health=0
 elif name=='historical_death_spell_destroy_uids':
  for uid in op[1]:
   minion=next((m for m in p.minions if m.uid==uid),None)
   if minion is not None and not game._fire_immune_target(uid,ctx):minion.health=0
 elif name=='historical_death_spell_resummon_confirmed':
  state=op[1]
  if any(r['entity'].uid==state['uid'] for r in p.death_records):
   card=state['card'];game._summon(owner,card.card_id,entry_source=card,entry_zone='deck',entry_origin='resurrection',entry_site='dead_air')
 elif name=='historical_death_spell_spread':
  if target is not None:
   board=game.players[target.owner].board;index=board.index(target)
   operations=capture(game,target,game._unrepeated_death_operations(target))
   from copy import deepcopy
   for i,minion in enumerate(board):
    if abs(i-index)==1 and minion in game.players[target.owner].minions:minion.attached_death_effects.extend(deepcopy(operations))
 elif name=='historical_death_spell_saddle':
  effect=random_cards(pool(card_type='MINION',tribe='BEAST',maximum=3),destination='board')
  for minion in p.minions:minion.attached_death_effects.append(effect)
 elif name=='historical_death_spell_colossal_hands':
  values=game._generation_created_candidates(pool(card_type='MINION',mechanic='COLOSSAL'),ctx)
  if values:
   cid=game.rng.choice(values);card=game._add(owner,cid)
   if card is not None:card.cost_delta=getattr(card,'cost_delta',0)-(2)
   game._add(1-owner,cid)
 else:return False
 return True
