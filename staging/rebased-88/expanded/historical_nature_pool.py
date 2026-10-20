"""Complete historical Nature outcome programs; behavioral validation deferred."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,random_cards,discover
from .selectors import has_tribe
from .historical_saidan import add as add_stat
from .identities import canonical_identity
from .discover_offer import DiscoverOffer

def op(name,*args):return ('historical_utility_nature_'+name,)+args
TOKEN_RULES={
 'AT_044':('minion',[op('mulch')]),
 'AV_333':('none',[op('revive')]),
 'BAR_549':('minion',[('buff',2,2),op('spikeshell')]),
 'BOT_054':('none',[('gain_full_crystals',2),op('opponent_crystals')]),
 'BOT_404':('none',[('filtered_draw',(('type','eq','MINION'),('cost','eq',n)),1) for n in (7,8,9,10)]),
 'BOT_444':('none',[op('gloop')]),
 'BT_128':('none',[op('draw_sequence','fungal',3)]),
 'BT_129':('friendly_minion',[op('germination')]),
 'BT_132':('minion',[('buff',1,3),('keyword','TAUNT')]),
 'CFM_713':('none',[('historical_ritual_jade',False,False),('empty_crystals','friendly',1)]),
 'DAL_351':('none',[('board_buff',1,1),('add','DAL_351ts',1)]),
 'DAL_351ts':('none',[('board_buff',1,1)]),
 'DAL_352':('none',[op('crystalsong')]),
 'DMF_732':('none',[('armor',8),random_cards(pool(card_type='MINION',minimum=8,maximum=8),destination='board')]),
 'DRG_006':('minion',[op('corrosive')]),
 'DRG_314':('none',[('draw',2)]),
 'DRG_315':('none',[op('embiggen')]),
 'DRG_318':('none',[('draw',1),op('dreams')]),
 'EX1_183':('none',[('board_buff',2,2),('board_keyword','TAUNT')]),
 'FP1_019':('none',[op('seeds')]),
 'FP1_019t':('none',[]),
 'GIL_553':('none',[op('woods')]),
 'GIL_663':('none',[('add','GIL_663t',2)]),
 'GIL_663t':('none',[]),
 'GVG_031':('enemy_minion',[op('recycle')]),
 'GVG_033':('none',[('historic_full_heal_board','all'),('historic_full_heal_heroes',)]),
 'GVG_073':('minion',[('damage',3),('damage_enemy_hero',3)]),
 'WON_306':('minion',[('damage',3),('damage_enemy_hero',3)]),
 'ICC_049':('minion',[('damage',2),op('toxic')]),
 'LOOT_047':('minion',[('buff',0,3),('armor',3)]),
 'OG_045':('none',[op('infest')]),
 'SCH_333':('none',[discover(pool(card_type='SPELL',classes='own_or_neutral')),('next_discount','SPELL',1,'persistent')]),
 'SW_437':('none',[op('compost')]),
 'ULD_273':('none',[op('heal_all',5),('draw',5)]),
 'VAC_508':('none',[op('trail')]),
 'WORK_024':('none',[('add','WORK_024t',2)]),
 'WORK_024t':('none',[]),
 'WORK_050':('none',[op('draw_sequence','brochure_minion',2)]),
 'WORK_050t':('none',[op('draw_sequence','brochure_spell',2)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def split(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('mulch')[0]:
  game._generation_candidates(pool(card_type='MINION'),1-owner)
  context=dict(ctx,owner=1-owner)
  return ('destroy',),(('replay_context',(random_cards(pool(card_type='MINION')),),context),)
 if name==op('opponent_crystals')[0]:
  return game._split_fixed_summon(('replay_context',(('gain_full_crystals',2),),dict(ctx,owner=1-owner)),ctx)
 if name==op('corrosive')[0]:
  dragon=any(has_tribe(game._card_data(c),'DRAGON') for c in p.hand)
  return ('damage',3),(('damage_enemy_hero',3),) if dragon else ()
 if name==op('woods')[0]:return game._split_fixed_summon(('summon','CS2_231',len(p.hand)),ctx)
 if name==op('seeds')[0]:
  counts=[len(player.minions) for player in game.players]
  operations=tuple(('replay_context',(('summon','FP1_019t',counts[side]),),dict(ctx,owner=side)) for side in (owner,1-owner))
  return ('destroy_all_minions',),operations
 if name==op('draw_sequence')[0]:
  mode,count=operation[1:]
  filters=(('type','eq','MINION'),) if mode=='brochure_minion' else (('type','eq','SPELL'),) if mode=='brochure_spell' else None
  states=[{} for _ in range(count)]
  operations=tuple(x for state in states for x in (('historical_draw_capture',filters,'random',state),op('draw_finish',mode,state)))
  return operations[0],operations[1:]
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_nature_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='spikeshell':
  target=game._force_live(ctx.get('target'))
  if target is not None and 'TAUNT' in game._effective_keywords(target):game._effect(('historical_copy_target_snapshot',deepcopy(target),'hand',1,None,None,None,False),ctx)
 elif name=='gloop':
  state=getattr(p,'historical_gloop',{})
  p.historical_gloop=dict(turn=game.turn,count=1+(state.get('count',0) if state.get('turn')==game.turn else 0))
 elif name=='germination':
  target=game._force_live(ctx.get('target'))
  if target is not None:game._summon(owner,target.card_id,copy_from=target,entry_keywords=('TAUNT',),entry_origin='effect',entry_site='germination')
 elif name=='draw_finish':
  mode,state=operation[1:];card=state.get('card')
  if card is None or card not in p.hand:return True
  if mode=='fungal' and game._card_data(card)['type']=='MINION':game._discard_card(owner,card)
  elif mode=='brochure_minion':add_stat(card,'attack_bonus',2);add_stat(card,'health_bonus',2)
  elif mode=='brochure_spell':card.cost_delta=getattr(card,'cost_delta',0)-1
 elif name=='embiggen':
  for i,value in enumerate(p.deck):
   if game._card_data(value)['type']!='MINION':continue
   card=value if isinstance(value,Card) else Card(game._new_id(),value)
   cost=game._cost(card,owner);add_stat(card,'attack_bonus',2);add_stat(card,'health_bonus',2)
   if cost<10:card.cost_delta=getattr(card,'cost_delta',0)+1
   p.deck[i]=card
 elif name=='dreams':
  if any(has_tribe(game._card_data(c),'DRAGON') for c in p.hand):game._effect(('empty_crystals','friendly',1),ctx)
 elif name=='recycle':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   recipient=target.owner;card=game._fresh_replay_card(target);game._carry_origin(target,card)
   game.players[recipient].board.remove(target);game._pending_summon_events.pop(target.uid,None)
   deck=game.players[recipient].deck;deck.insert(game.rng.randrange(len(deck)+1),card)
   game._record_deck_insertion(recipient,owner,1,'shuffle',cards=(card,));game._refresh_auras()
 elif name=='toxic':
  target=game._force_live(ctx.get('target'))
  if target is not None:target.keywords.add('POISONOUS')
 elif name in ('infest','compost'):
  effect=random_cards(pool(card_type='MINION',tribe='BEAST')) if name=='infest' else ('draw',1)
  for minion in p.minions:
   minion.attached_death_effects.append(effect);minion.keywords.add('DEATHRATTLE')
 elif name=='heal_all':
  for uid in list(game._characters()):game._heal(uid,operation[1],healer=owner,spell=ctx.get('spell',False))
 elif name=='trail':game._schedule_turn_effect(owner,'start',1,1,(op('trail_begin'),),source_card_id='VAC_508')
 elif name=='trail_begin':
  before=p.max_mana;game._effect(('gain_full_crystals',2),ctx);gained=p.max_mana-before
  if gained:game._schedule_turn_effect(owner,'end',0,1,(op('trail_end',gained),),source_card_id='VAC_508')
 elif name=='trail_end':p.max_mana=max(0,p.max_mana-operation[1]);p.mana=min(p.mana,p.max_mana)
 elif name=='bear_tick':
  card=next((c for c in p.hand if c.uid==operation[1] and c.card_id=='WORK_024t'),None)
  if card is not None:add_stat(card,'attack_bonus',1);add_stat(card,'health_bonus',1)
 elif name=='revive':
  from .historical_resurrection_batches import records
  choices=records(game,ctx,'beast');groups={}
  for record in choices:groups.setdefault(canonical_identity(game.cards[record['card_id']],game.cards),record)
  values=list(groups.values());offered=game.rng.sample(values,min(3,len(values)))
  if offered:
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Revive Pet Discover')
   game.pending_choice=dict(owner=owner,kind='historical_nature_offer',mode='revive',context=dict(ctx),options=[dict(card_id=row['card_id'],entity=deepcopy(row['entity'])) for row in offered])
   game.phase='choice'
 elif name=='crystalsong':
  values=game._generation_discover_candidates(pool(card_type='MINION',classes='DRUID'),ctx)
  ids=game.rng.sample(list(values),min(3,len(values)))
  if not ids:return True
  if not any(game._card_data(card)['type']=='MINION' for card in p.hand):
   results=[game._enter_hand(owner,Card(game._new_id(),cid)) for cid in ids]
   offer=DiscoverOffer(owner,'historical_crystalsong_all',0,tuple(dict(card_id=cid) for cid in ids),getattr(p.equipped_card,'uid',None),tuple(range(len(ids))))
   game._record_discover(owner,offer)
   for result in results:game._defer_discover_followups(owner,result)
  else:
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Crystalsong Discover')
   game.pending_choice=dict(owner=owner,kind='historical_nature_offer',mode='crystalsong',context=dict(ctx),options=[dict(card_id=cid) for cid in ids]);game.phase='choice'
 else:return False
 return True

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_nature_offer':return False
 owner=choice['owner'];cid=selected['card_id']
 if choice['mode']=='revive':
  source=selected['entity'];card=game._fresh_replay_card(source)
  game._discovery_result=game._summon(owner,cid,entry_source=card,entry_zone='hand',entry_origin='resurrection',entry_site='revive_pet')
 else:game._discovery_result=game._enter_hand(owner,Card(game._new_id(),cid))
 return True

def event(game,kind,data):
 if kind!='minion_died':return
 for owner,p in enumerate(game.players):
  state=getattr(p,'historical_gloop',{})
  if state.get('turn')==game.turn and state.get('count',0):
   game._rule_events.append(('captured_effects',dict(operations=(('refresh_mana',state['count']),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='BOT_444')),[]))

def turn_entries(game,phase):
 if phase!='start':return []
 return [dict(source=None,order=c.uid,card_id=c.card_id,operations=(op('bear_tick',c.uid),)) for c in game.players[game.current].hand if c.card_id=='WORK_024t']
