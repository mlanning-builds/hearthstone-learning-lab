"""Historical death-history consumers and bound copied effects, unvalidated.

Selections use physical death records, retaining repeated deaths. Resurrections
create fresh printed entities; copied Deathrattles bind donor-owned memory.
"""
from copy import deepcopy
from engine.game import Card
from .selectors import has_tribe,has_class
from .death_inheritance import capture


def resurrect(selector='all',count=1,keywords=()):
 return ('historical_resurrection_pick',selector,count,tuple(keywords))

RULES={
 'KAR_204':('none',[resurrect()]),'WON_057':('none',[resurrect()]),
 'ULD_268':('none',[resurrect(keywords=('REBORN',))]),
 'RLK_531':('none',[resurrect('undead',keywords=('REBORN',))]),
 'BAR_334':('none',[resurrect('frenzy',2),('area_damage','other_minions',1)]),
 'EX1_190':('none',[resurrect('this_turn',-1)]),
 'OG_133':('none',[resurrect('deathrattle',-1)]),
 'RLK_832':('none',[resurrect('undead_since_last_turn',-1)]),
 'TTN_857':('none',[resurrect('own_attack_'+str(n)) for n in (2,3,4)]),
 'DED_008':('none',[('historical_resurrection_last_death_copy',)]),
 'ICC_098':('none',[('historical_resurrection_death_hand',)]),
 'TOY_383':('none',[('historical_resurrection_shuffle',5)]),
 'TRL_537':('none',[('historical_resurrection_gain_deaths',3)]),
 'LOE_019':('friendly_minion',[('historical_resurrection_copy_target_death',)]),
 'UNG_800':('friendly_minion',[('historical_batch_trigger_target_death',)]),
 'KAR_041':('minion',[('historical_resurrection_destroy_remember',)]),
 'BT_126':('none',[('historical_resurrection_destroy_others',)]),
 'ETC_428':('none',[('historical_resurrection_corpse_death',5)]),
}
DEATH_EFFECTS={
 'ICC_825':[resurrect('beast')],
 'ICC_835':[resurrect('taunt',-1)],
 'RLK_813':[resurrect('undead')],
 'GDB_468':[resurrect('other_deathrattle')],
}
END_EFFECTS={'DAL_721':[resurrect('other_undead')]}
END_EVERY_EFFECTS={'FP1_013':[resurrect('this_turn',-1)]}
# The remembered payload is attached per destruction, rather than a global CID.
for cid in DEATH_EFFECTS.keys()|END_EFFECTS.keys()|END_EVERY_EFFECTS.keys():RULES.setdefault(cid,('none',[]))
RULES.update({
 'MAW_011':('none',[('historical_resurrection_discover','gain_trigger')]),
 'ULD_727':('none',[('historical_resurrection_discover','shuffle')]),
 'SCH_162':('none',[('historical_resurrection_death_whelp',)]*2),
 'TOY_607':('none',[('historical_resurrection_mech_pair',)]),
 'RLK_913':('none',[]),
})
DEATH_EFFECTS.update({
 'SCH_621':[('historical_resurrection_decay',)],
 'TOY_893':[('historical_resurrection_decay',)],
 'FP1_014':[('historical_resurrection_pair','FP1_015','FP1_014t')],
 'FP1_015':[('historical_resurrection_pair','FP1_014','FP1_014t')],
})
TRIGGERS={'RLK_913':(('historical_event','source_attack_kill'),[('historical_resurrection_attack_victim',)])}
for cid in DEATH_EFFECTS:RULES.setdefault(cid,('none',[]))
TOKEN_RULES={'SCH_162t':('none',[]),'FP1_014t':('none',[])}
RULES.update({
 'LOOT_520':('none',[('historical_resurrection_deck_death',)]),
 'BOT_243':('none',[('historical_resurrection_discover_generated_death',)]),
 'REV_310':('none',[('historical_resurrection_draw_death',False)]),
 'DRG_031':('none',[('historical_resurrection_draw_death',True)]),
 'AV_312':('friendly_minion',[('historical_resurrection_sacrifice_recruit',)]),
 'ULD_269':('friendly_minion',[('historical_resurrection_destroy_return',)]),
 'BT_196':('minion',[('historical_resurrection_drawn_destroy',)]),
 'VAC_341':('enemy_minion',[('destroy',)]),
 'RLK_658':('friendly_undead',[('historical_resurrection_undead_attack',)]),
})
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def eligible(game,record,selector,ctx):
 owner=ctx['owner'];cid=record['card_id'];data=game.cards[cid];entity=record['entity'];source=ctx.get('source')
 if selector=='ogre_gang':
  from .identities import canonical_identity
  return cid in ('WW_418','WW_419','WW_420') or canonical_identity(data,game.cards)=='CS2_200'
 if selector=='all':return True
 if selector=='this_turn':return record['turn']==game.turn
 if selector in ('undead','other_undead','undead_since_last_turn'):
  return has_tribe(data,'UNDEAD') and (selector!='other_undead' or source is None or cid!=source.card_id) and (selector!='undead_since_last_turn' or record['turn']>game.players[owner].last_turn_ended)
 if selector=='demon':return has_tribe(data,'DEMON')
 if selector=='beast':return has_tribe(data,'BEAST')
 if selector=='taunt':return 'TAUNT' in entity.keywords
 if selector in ('deathrattle','other_deathrattle'):return 'DEATHRATTLE' in data.get('mechanics',()) and (selector!='other_deathrattle' or source is None or cid!=source.card_id)
 if selector=='frenzy':return 'FRENZY' in data.get('mechanics',())
 if selector.startswith('own_attack_'):return data.get('attack')==int(selector.rsplit('_',1)[1]) and has_class(data,game.players[owner].hero_class)
 raise ValueError('Unknown explicit resurrection selector: '+selector)


def records(game,ctx,selector='all',both=False):
 owners=(ctx['owner'],1-ctx['owner']) if both else (ctx['owner'],)
 return [record for owner in owners for record in game.players[owner].death_records if eligible(game,record,selector,ctx)]


def bound_deaths(game,record):
 donor=record['entity']
 return capture(game,donor,game._unrepeated_death_operations(donor))


def split(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_resurrection_draw_death':
  if op[1] and not ctx.get('combo'):return ('batch30_noop',),()
  state={}
  return ('historical_draw_capture',(('type','eq','MINION'),('mechanic','eq','DEATHRATTLE')),'random',state),(('historical_resurrection_gain_drawn',state),)
 if name in ('historical_resurrection_sacrifice_recruit','historical_resurrection_destroy_return','historical_resurrection_undead_attack'):
  victim=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
  if victim is None:return ('batch30_noop',),()
  if name=='historical_resurrection_sacrifice_recruit':following=('summon_from_zone','deck',(('type','eq','MINION'),('cost','eq',game._card_stat(victim,'cost',owner)+1)))
  elif name=='historical_resurrection_destroy_return':following=('summon',victim.card_id,1)
  else:following=('board_buff',victim.attack,0)
  return ('destroy',),(following,)
 if name=='historical_resurrection_mech_pair':
  values=[r for r in records(game,ctx) if has_tribe(game.cards[r['card_id']],'MECHANICAL') and game.cards[r['card_id']].get('cost',0)>=5]
  selected=[]
  for _ in range(2):
   if not values:break
   chosen=game.rng.choice(values);selected.append(chosen);values=[r for r in values if r['card_id']!=chosen['card_id']]
  operations=[]
  states=[]
  for record in selected:
   state={};states.append(state);operations.append(('historical_resurrection_capture_summon',record['card_id'],state))
  operations.extend(('historical_resurrection_force',state) for state in states)
  return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())
 if name=='historical_resurrection_force':
  uid=op[1].get('uid');minion=game._force_live(uid) if uid is not None else None
  if minion is None:return ('batch30_noop',),()
  target=game._force_target(owner,'random_enemy_character')
  return game._force_split(('force_pair',uid,target),ctx) if target is not None else (('batch30_noop',),())
 if name=='historical_resurrection_pick':
  candidates=records(game,ctx,op[1]);count=op[2]
  selected=game.rng.sample(candidates,len(candidates) if count<0 else min(count,len(candidates)))
  operations=tuple(('historical_resurrection_summon',r['card_id'],op[3],0,0) for r in selected)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_resurrection_destroy_others':
  victims=[m for m in p.minions if m is not source and m.health>0]
  operations=tuple(('historical_resurrection_capture_destroy',m.uid) for m in victims)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_resurrection_corpse_death':
  if p.corpses<op[1]:return ('batch30_noop',),()
  candidates=[r for r in records(game,ctx) if game._unrepeated_death_operations(r['entity'])]
  if not candidates:return ('batch30_noop',),()
  selected=game.rng.choice(candidates);operations=bound_deaths(game,selected)
  game._spend_corpses(owner,op[1])
  if source is not None:source.attached_death_effects.extend(deepcopy(operations))
  return game._split_fixed_summon(('replay_context',operations,dict(ctx)),ctx)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_resurrection_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source');target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
 if name=='historical_resurrection_deck_death':
  values=[c for c in p.deck if game._card_data(c)['type']=='MINION']
  if values and source is not None:source.attached_death_effects.extend(card_deaths(game,game.rng.choice(values),owner))
 elif name=='historical_resurrection_gain_drawn':
  card=op[1].get('card')
  if card is not None and source is not None:source.attached_death_effects.extend(card_deaths(game,card,owner))
 elif name=='historical_resurrection_drawn_destroy':
  if getattr(ctx.get('physical_card'),'_drawn_turn',None)==game.turn:
   for player in game.players:
    for minion in player.minions:
     if minion is not source:minion.health=0
  elif target is not None:target.health=0
 elif name=='historical_resurrection_discover_generated_death':
  from .generation_cards import pool
  from engine.cards import UnsupportedCard
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite generated Deathrattle Discover')
  values=game._generation_discover_candidates(pool(card_type='MINION',mechanic='DEATHRATTLE',classes='own_or_neutral'),ctx)
  if values:
   offered=game.rng.sample(values,min(3,len(values)))
   game.pending_choice=dict(owner=owner,kind='historical_resurrection',mode='generated_death',source_uid=getattr(source,'uid',None),options=[dict(card_id=cid) for cid in offered])
   game.phase='choice'
 elif name=='historical_resurrection_discover':
  from engine.cards import UnsupportedCard
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite resurrection Discover')
  values=records(game,ctx,'deathrattle' if op[1]=='gain_trigger' else 'all')
  unique={}
  for record in values:unique.setdefault(record['card_id'],record)
  if unique:
   offered=game.rng.sample(sorted(unique),min(3,len(unique)))
   game.pending_choice=dict(owner=owner,kind='historical_resurrection',mode=op[1],source_uid=getattr(source,'uid',None),records=tuple(deepcopy(unique[cid]) for cid in offered),options=[dict(card_id=cid,index=i) for i,cid in enumerate(offered)])
   game.phase='choice'
 elif name=='historical_resurrection_capture_summon':
  minion=game._summon(owner,op[1],entry_origin='resurrection',entry_site='inventor_boom')
  if minion is not None:op[2]['uid']=minion.uid
 elif name=='historical_resurrection_decay':
  if source is not None:
   decay=source.rule_state.get('historical_resurrection_decay',0)+1;data=game.cards[source.card_id]
   if data.get('health',0)>decay:
    minion=game._summon(owner,source.card_id,attack_bonus=-decay,health_bonus=-decay,entry_origin='resurrection',entry_site='rattlegore_decay')
    if minion is not None:minion.rule_state['historical_resurrection_decay']=decay
 elif name=='historical_resurrection_pair':
  if any(op[1] in player.death_history for player in game.players):game._summon(owner,op[2],entry_origin='resurrection',entry_site='thaddius_pair')
 elif name=='historical_resurrection_attack_victim':
  cid=ctx['event'].get('victim_card_id')
  if cid is not None:game._summon(owner,cid,entry_origin='resurrection',entry_site='bonelord_kill')
 elif name=='historical_resurrection_death_whelp':
  values=[r for r in records(game,ctx) if game._unrepeated_death_operations(r['entity'])]
  operations=bound_deaths(game,game.rng.choice(values)) if values else ()
  minion=game._summon(owner,'SCH_162t',entry_origin='effect',entry_site='vectus_whelp')
  if minion is not None:minion.attached_death_effects.extend(operations)
 elif name=='historical_resurrection_summon':
  game._summon(owner,op[1],attack_bonus=op[3],health_bonus=op[4],entry_keywords=op[2],entry_origin='resurrection',entry_site='historical_death_history',entry_source=source)
 elif name=='historical_resurrection_last_death_copy':
  values=records(game,ctx,'deathrattle')
  if values:game._add(owner,values[-1]['card_id'])
 elif name=='historical_resurrection_death_hand':
  values=records(game,ctx,'deathrattle',both=True)
  if values:game._add(owner,game.rng.choice(values)['card_id'])
 elif name=='historical_resurrection_shuffle':
  values=records(game,ctx)
  for record in game.rng.sample(values,min(op[1],len(values))):
   card=Card(game._new_id(),record['card_id']);game._set_card_cost(card,0);p.deck.insert(game.rng.randrange(len(p.deck)+1),card);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_resurrection_gain_deaths':
  values=[r for r in records(game,ctx) if game._unrepeated_death_operations(r['entity'])]
  if source is not None:
   for record in game.rng.sample(values,min(op[1],len(values))):source.attached_death_effects.extend(bound_deaths(game,record))
 elif name=='historical_resurrection_copy_target_death':
  if source is not None and target is not None:source.attached_death_effects.extend(capture(game,target,game._unrepeated_death_operations(target)))
 elif name in ('historical_resurrection_destroy_remember','historical_resurrection_capture_destroy'):
  if name=='historical_resurrection_capture_destroy':target=next((m for m in p.minions if m.uid==op[1] and m.health>0),None)
  if target is not None:
   if source is not None:
    bonus=1 if name=='historical_resurrection_capture_destroy' else 0
    source.attached_death_effects.append(('historical_resurrection_summon',target.card_id,(),bonus,bonus))
   target.health=0
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_resurrection':return False
 owner=choice['owner'];p=game.players[owner]
 if choice['mode']=='generated_death':
  card=Card(game._new_id(),selected['card_id']);operations=card_deaths(game,card,owner)
  game._enter_hand(owner,card)
  source=next((m for m in p.minions if m.uid==choice['source_uid'] and m.health>0),None)
  if source is not None:source.attached_death_effects.extend(operations)
  return True
 record=choice['records'][selected['index']]
 if choice['mode']=='shuffle':
  card=Card(game._new_id(),record['card_id']);p.deck.insert(game.rng.randrange(len(p.deck)+1),card);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 else:
  source=next((m for m in p.minions if m.uid==choice['source_uid'] and m.health>0),None)
  if source is not None:
   operations=bound_deaths(game,record);source.attached_death_effects.extend(deepcopy(operations))
   if operations:game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=owner,source=source,target=0,bonus=0,lifesteal=False)),[]))
 return True


def card_deaths(game,value,owner):
 # A detached donor supplies printed rules and physical stored memories without
 # entering the board, firing a summon, spending resources or using a board slot.
 from .game import Minion
 card=value if isinstance(value,Card) else Card(game._new_id(),value)
 data=game._card_data(card);attack=game._card_stat(card,'attack',owner);health=game._card_stat(card,'health',owner)
 donor=Minion(card.uid,card.card_id,owner,attack,health,health,set(data.get('mechanics',())))
 for field,value in vars(card).items():
  if field not in ('uid','card_id','attack_bonus','health_bonus','cost_delta'):setattr(donor,field,deepcopy(value))
 game._stored_entry(donor,card);game._forge_entry(donor,card)
 return capture(game,donor,game._unrepeated_death_operations(donor))


def physical_targets(game,card,owner,current):
 if card.card_id=='BT_196' and getattr(card,'_drawn_turn',None)==game.turn:return [0]
 if card.card_id=='VAC_341':
  attack=game._card_stat(card,'attack',owner)
  return [uid for uid in current if uid and game._find(uid).attack<=attack] or [0]
 return current
