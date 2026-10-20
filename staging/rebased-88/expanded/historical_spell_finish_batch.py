"""Historical summons, physical buffs and Starship conditionals; unvalidated."""
from engine.game import Card
from .generation_cards import pool,random_cards,discover
from .historical_draw_batches import draw
from .historical_damage_spells import follow
from .selectors import has_tribe
from .historical_saidan import add
from .historical_starships import building

def op(name,*args):return ('historical_utility_finish_batch_'+name,)+args
TOKEN_RULES={
 'GDB_102':('none',[discover(pool(card_type='MINION',mechanic='STARSHIP_PIECE',classes='other'),cost_delta=-1)]),
 'GDB_465':('historical_galakrond_undamaged_character',[('damage',5)]),
 'GDB_474':('none',[op('ship_draw')]),
 'GDB_845':('minion',[op('ship_damage')]),
 'GDB_476':('minion',[op('ship_destroy')]),
 'GDB_467':('none',[op('quasar')]),
 'YOD_015':('none',[discover(pool(card_type='MINION',minimum=2,maximum=2,classes='own_or_neutral'),destination='board',health=3)]),
 'TRL_305':('none',[discover(pool(card_type='MINION',minimum=6,maximum=6,classes='own_or_neutral'),destination='board',keywords=('TAUNT','DIVINE_SHIELD'))]),
 'YOP_029':('none',[op('pouch')]),
 'OG_101':('none',[op('forbidden_minion')]),
 'OG_114':('none',[op('tentacles')]),
 'OG_114a':('none',[]),
 'OG_061':('character',[('damage',1),('summon','OG_061t',1)]),
 'OG_061t':('none',[]),
 'OG_314':('minion',[follow(1,'alive',('summon','OG_314b',1))]),
 'OG_314b':('none',[]),
 'DMF_706':('none',[op('duelists')]),
 'DMF_706t':('none',[]),
 'KAR_026':('none',[op('pawns')]),
 'KAR_026t':('none',[]),
 'WC_003':('none',[('schedule_turn_effect','start',1,1,(('summon','WC_003t',2),))]),
 'WC_003t':('none',[]),
 'GVG_010':('minion',[('buff',2,4),('historical_event_spell_damage','target',1)]),
 'GVG_012':('character',[('heal',3),op('lightwarden')]),
 'SCH_138':('minion',[('buff',8,8),('temporary_keyword_target','CANT_ATTACK_HERO','end')]),
 'SCH_136':('minion',[('buff',2,2),op('scheduled_heal')]),
 'DED_502':('minion',[op('defense')]),
 'LOE_113':('none',[('board_buff',2,2)]),
 'SCH_609':('none',[op('survival')]),
 'WON_051':('none',[op('four_buffs')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def split(game,operation,ctx):
 prefix='historical_utility_finish_batch_'
 if not operation[0].startswith(prefix):return None
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='ship_draw':
  operation=draw(None,'discount',(2,)) if building(game,owner) is not None else draw()
  first,tail=game._split_fixed_summon(operation,ctx);return first,tuple(tail)+(operation,)
 if name=='ship_damage':
  extra=building(game,owner) is not None;target=game._force_live(ctx.get('target'))
  neighbors=adjacent(game,target) if extra and target is not None else []
  return op('damage_group',tuple([target.uid]+[m.uid for m in neighbors]) if target else ()),()
 if name=='ship_destroy':
  target=game._force_live(ctx.get('target'));neighbors=adjacent(game,target) if target is not None and building(game,owner) is not None else []
  chosen=game.rng.choice(neighbors) if neighbors else None
  return ('destroy',),((op('kill_uid',chosen.uid),) if chosen is not None else ())
 if name=='pouch':return game._split_fixed_summon(discover(pool(minimum=p.mana,maximum=p.mana,classes='own_or_neutral')),ctx)
 if name=='forbidden_minion':
  mana=p.mana;p.mana=0;return game._split_fixed_summon(random_cards(pool(card_type='MINION',minimum=mana,maximum=mana),destination='board'),ctx)
 if name in ('tentacles','duelists','pawns'):
  if name=='tentacles':count=p.mana;p.mana=0;cid='OG_114a'
  elif name=='duelists':count=2 if p.hero_attacks else 1;cid='DMF_706t'
  else:count=len(game.players[1-owner].all_minions);cid='KAR_026t'
  return game._split_fixed_summon(('summon',cid,count),ctx)
 return None

def adjacent(game,target):
 board=game.players[target.owner].board;i=board.index(target)
 return [board[j] for j in (i-1,i+1) if 0<=j<len(board) and board[j] in game.players[target.owner].minions and board[j].health>0]

def execute(game,operation,ctx):
 prefix='historical_utility_finish_batch_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner];target=game._force_live(ctx.get('target'))
 if name=='quasar':
  for c in tuple(p.hand):game._shuffle_hand_card(owner,c,actor=owner)
  for i,value in enumerate(p.deck):
   c=value if isinstance(value,Card) else Card(game._new_id(),value);c.cost_delta=getattr(c,'cost_delta',0)-3;p.deck[i]=c
 elif name=='damage_group':
  with game._damage_batch():
   for uid in operation[1]:
    if game._force_live(uid) is not None:game._deal_effect(uid,3,ctx)
 elif name=='kill_uid':
  victim=game._force_live(operation[1])
  if victim is not None:victim.health=0
 elif name=='lightwarden':
  uid=ctx.get('target');entity=game.players[-uid-1] if uid<0 else target
  if entity is not None and entity.health<entity.max_health:game._rule_events.append(('captured_effects',dict(operations=(('summon','EX1_001',1),),context=dict(ctx)),[]))
 elif name=='scheduled_heal':
  if target is not None:
   key=game._new_id();target.rule_state.setdefault('historical_finish_heals',[]).append(key)
   game._schedule_turn_effect(game.current,'end',0,1,(op('heal_uid',target.uid,key),),source_card_id=ctx.get('card_id'))
 elif name=='heal_uid':
  victim=game._force_live(operation[1])
  if victim is not None and operation[2] in victim.rule_state.get('historical_finish_heals',()):game._heal(victim.uid,victim.max_health-victim.health,healer=owner,spell=ctx.get('spell',False))
 elif name=='defense':
  if target is not None:
   attack,health=max(0,target.attack-1),max(0,target.health-1);game._set_entity_stats(target,1,1);game._refresh_auras()
   values=[c for c in p.hand if game._card_data(c)['type']=='MINION']
   if values:
    c=game.rng.choice(values);add(c,'attack_bonus',attack);add(c,'health_bonus',health)
 elif name=='survival':
  for zone in (p.hand,p.deck):
   for i,value in enumerate(zone):
    if game._card_data(value)['type']=='MINION':
     c=value if isinstance(value,Card) else Card(game._new_id(),value);add(c,'attack_bonus',4);add(c,'health_bonus',4);zone[i]=c
  for m in p.minions:game._buff(m,4,4)
 elif name=='four_buffs':
  cards=[c for c in p.hand if game._card_data(c)['type']=='MINION']
  for amount in (4,3,2,1):
   if not cards:break
   c=game.rng.choice(cards);cards.remove(c);add(c,'attack_bonus',amount);add(c,'health_bonus',amount)
 else:return False
 return True
