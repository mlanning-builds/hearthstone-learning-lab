"""Eight explicit Stormwind Questlines and their complete generated rewards.

Progress caps within its current stage. Completion waits for the originating
resolution boundary; public quest state never contains private drawn cards.
"""
from .generation_cards import pool,random_cards
from .selectors import has_tribe
from .identities import canonical_identity

FAMILIES={
 'pirate':(('SW_028','SW_028t','SW_028t2'),(3,3,3),'SW_028t5'),
 'showdown':(('SW_039','SW_039t','SW_039t3'),(4,5,5),'SW_039t3_t'),
 'spy':(('SW_052','SW_052t','SW_052t2'),(2,2,2),'SW_052t3'),
 'seed':(('SW_091','SW_091t','SW_091t3'),(12,12,12),'SW_091t4'),
 'occasion':(('SW_313','SW_313t','SW_313t2'),(3,3,3),'SW_313t4'),
 'district':(('SW_322','SW_322t','SW_322t2'),(3,2,2),'SW_322t4'),
 'park':(('SW_428','SW_428t','SW_428t2'),(4,5,6),'SW_428t4'),
 'guidance':(('SW_433','SW_433t','SW_433t2'),(3,2,2),'SW_433t3'),
}
STAGES={cid:(family,index,totals[index],ids[index+1] if index<2 else reward) for family,(ids,totals,reward) in FAMILIES.items() for index,cid in enumerate(ids)}
QUESTS={cid:(row[2],row[3]) for cid,row in STAGES.items()}
GIZMOS=('SW_052t4','SW_052t5','SW_052t6','SW_052t7','SW_052t8_t')
JUGGERNAUT='SW_028t6'
PIRATES=pool(card_type='MINION',tribe='PIRATE',excluded_mechanic='COLOSSAL')
WARRIOR_WEAPONS=pool(card_type='WEAPON',classes='WARRIOR')
def draw(filters):return ('historical_draw_batch',filters,'none',(),'random')
def zone_offer(side,zone,filters,mode,limit=3,discovering=True):return ('historical_play_zone_offer',side,zone,tuple(filters),mode,limit,discovering)
def op(name,*args):return ('historical_utility_stormwind_'+name,)+args
TOKEN_RULES={cid:('none',[op('begin',cid)]) for cid in STAGES}
TOKEN_RULES.update({
 'SW_028t5':('none',[('open_permanent',JUGGERNAUT)]),
 JUGGERNAUT:('none',[]),
 'SW_039t3_t':('none',[op('kurtrus')]),
 'SW_052t3':('none',[('add',cid,1) for cid in GIZMOS]),
 'SW_052t4':('enemy_minion',[op('distractor')]),
 'SW_052t5':('none',[zone_offer('enemy','deck',(),'top',3,False)]),
 'SW_052t6':('minion',[('buff',2,0),('keyword','STEALTH')]),
 'SW_052t7':('none',[]),
 'SW_052t8_t':('none',[]),
 'SW_091t4':('none',[op('tamsin')]),
 'SW_313t4':('none',[('recruit_bonus',2,2)]),
 'SW_322t4':('none',[op('tavish')]),
 'SW_428t4':('none',[('hero_attack',8),('armor',8)]),
 'SW_433t3':('none',[('insert_fixed','SW_433t3a',1,'shuffle')]),
 'SW_433t3a':('none',[op('shard')]),
})
DEATH_EFFECTS={'SW_052t7':[op('gyroblade')]}
TRIGGERS={'SW_052t8_t':('attacked_self',[('historic_opponent_class_generate',None,1)])}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def enqueue(game,owner,operations,cid,**kw):
 context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid,spell=False);context.update(kw)
 game._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=context),[]))

def ready_blocked(game):
 return (getattr(game,'_stormwind_paid_resolution',False) or game.pending_frame is not None or game.pending_choice is not None or getattr(game,'_stormwind_draw_depth',0)>0 or getattr(game,'_power_frame',None) is not None or getattr(game,'_combat_sequence_depth',0)>0 or getattr(game,'_damage_batch_depth',0)>0)

def deliver(game,owner,*,force=False):
 p=game.players[owner];q=p.quest
 if not q or q['card_id'] not in STAGES:return False
 family,index,total,following=STAGES[q['card_id']]
 if q['progress']<total:return True
 if ready_blocked(game) and not q.get('stormwind_waiting_hand') and not (force and family!='showdown'):return True
 cid=q['card_id']
 if index==2:
  if len(p.hand)>=getattr(p,'hand_capacity',10):q['stormwind_waiting_hand']=True;return True
  p.quest=None;operations=(('add',following,1),)
 else:
  p.quest=dict(card_id=following,progress=0,total=STAGES[following][2])
  if family=='pirate':operations=(draw((('type','eq','WEAPON'),)),) if index==0 else (('damage_random_enemy',2),)*2
  elif family=='showdown':operations=(op('discount_drawn'),)
  elif family=='spy':operations=(op('gizmo'),)
  elif family=='seed':operations=(op('seed_reward'),)
  elif family=='occasion':operations=(('equip','CS2_091'),) if index==0 else (op('upgrade_power'),)
  elif family=='district':operations=(op('target_power'),) if index==0 else (op('zero_power'),)
  elif family=='park':operations=(('armor',5),) if index==0 else (('armor',5),('draw',1))
  else:operations=(zone_offer('own','deck',(),'draw'),)
 enqueue(game,owner,operations,cid)
 game._log('quest_reward_delivered',player=owner,card=following)
 return True

def finish(game,*,force=False,clear_paid=False):
 if clear_paid:game._stormwind_paid_resolution=False
 before=len(game._rule_events)
 for owner in (0,1):deliver(game,owner,force=force)
 return len(game._rule_events)!=before

def played(game,owner,card,paid_cost):
 if any(p.quest and p.quest['card_id'] in STAGES for p in game.players):game._stormwind_paid_resolution=True
 q=game.players[owner].quest
 if not q or q['card_id'] not in STAGES:return
 family,index,total,following=STAGES[q['card_id']];data=game._card_data(card)
 # Cost is relevant only to these objectives. Other quest listeners can
 # consume card identity/type facts without requiring payment metadata.
 if paid_cost is None and family in ('occasion','guidance'):paid_cost=game._cost(card,owner)
 if family=='pirate' and data['type']=='MINION' and has_tribe(data,'PIRATE'):game._quest_progress(owner,1)
 elif family=='spy':
  from .historical_play_batches import SI7_IDS
  if card.card_id in SI7_IDS:game._quest_progress(owner,1)
 elif family=='occasion' and paid_cost==1:
  identity=canonical_identity(data,game.cards);seen=q.setdefault('seen',[])
  if identity not in seen:seen.append(identity);game._quest_progress(owner,1)
 elif family=='guidance' and paid_cost in ((2,3,4),(5,6),(7,8))[index]:
  seen=q.setdefault('seen',[])
  if paid_cost not in seen:seen.append(paid_cost);game._quest_progress(owner,1)

def before_draw(game,owner,card,private):
 p=game.players[owner]
 discount=getattr(p,'historical_stormwind_draw_discount',0)
 if discount:card.cost_delta=getattr(card,'cost_delta',0)-discount
 q=p.quest
 if not q or q['card_id'] not in STAGES or STAGES[q['card_id']][0]!='showdown':return
 state=getattr(p,'_stormwind_draw_cards',{})
 if state.get('turn')!=game.turn:state=dict(turn=game.turn,cards=[]);p._stormwind_draw_cards=state
 state['cards'].append(card)
 game._quest_progress(owner,1)

def end_turn(game):
 for p in game.players:
  q=p.quest
  if q and q['card_id'] in STAGES and STAGES[q['card_id']][0]=='showdown':q['progress']=0;q.pop('stormwind_waiting_hand',None)
  p._stormwind_draw_cards=dict(turn=-1,cards=[])

def event(game,kind,data):
 if kind=='spell_cast':
  owner=data['owner'];p=game.players[owner]
  if getattr(p,'historical_stormwind_tavish',False):p.power_used=False;p.historical_power_turn=dict(turn=game.turn,count=0)
 if kind=='damage' and data.get('target',0)==game.hero_id(game.current):
  owner=game.current;q=game.players[owner].quest
  if q and q['card_id'] in STAGES and STAGES[q['card_id']][0]=='seed':game._quest_progress(owner,data['amount'])
 if kind=='historical_hero_attack_gained':
  owner=data['owner'];q=game.players[owner].quest
  if q and q['card_id'] in STAGES and STAGES[q['card_id']][0]=='park':game._quest_progress(owner,data['amount'])

def spell_damage(game,ctx,dealt):
 if dealt<=0 or not ctx.get('spell'):return
 state=ctx.setdefault('stormwind_spell_damage_state',dict(seen=False))
 if state['seen']:return
 state['seen']=True;owner=ctx['owner'];q=game.players[owner].quest
 if q and q['card_id'] in STAGES and STAGES[q['card_id']][0]=='district':game._quest_progress(owner,1)

def power_cost(game,owner,value):
 p=game.players[owner]
 return 0 if getattr(p,'historical_stormwind_zero_generation',None)==getattr(p,'historical_power_generation',0) else value

def hunter_targets(game,owner):
 return tuple(uid for uid in game._visible_targets(owner,magic=True) if uid>0 or uid==game.hero_id(1-owner))

def turn_entries(game,phase):
 if phase!='start':return []
 return [dict(source=None,order=obj.uid,card_id=JUGGERNAUT,operations=(op('juggernaut',obj.uid),)) for obj in game.players[game.current].permanents if obj.card_id==JUGGERNAUT for _ in range(game._trigger_repetitions(game.current))]

def requests_for(game,cid,owner):
 return {PIRATES,WARRIOR_WEAPONS} if cid in ('SW_028t5',JUGGERNAUT) else set()

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def split(game,operation,ctx):
 name=operation[0];owner=ctx['owner']
 if name==op('juggernaut')[0]:
  if not any(obj.uid==operation[1] and obj.card_id==JUGGERNAUT for obj in game.players[owner].permanents):return ('batch30_noop',),()
  return sequence(game,ctx,(random_cards(PIRATES,destination='board'),op('warrior_weapon'),('damage_random_enemy',2),('damage_random_enemy',2)))
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_stormwind_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='begin':
  empty=p.quest is None;game._quest_effect(('quest_start',operation[1]),ctx)
  if empty and p.quest and p.quest['card_id']==operation[1]:p._stormwind_draw_cards=dict(turn=game.turn,cards=[])
 elif name=='gizmo':
  from .pools import require_fixed_cards
  require_fixed_cards(GIZMOS,game.cards);game._add(owner,game.rng.choice(GIZMOS))
 elif name=='discount_drawn':
  state=getattr(p,'_stormwind_draw_cards',{})
  if state.get('turn')==game.turn:
   for card in state['cards']:card.cost_delta=getattr(card,'cost_delta',0)-1
 elif name=='kurtrus':p.historical_stormwind_draw_discount=getattr(p,'historical_stormwind_draw_discount',0)+2
 elif name=='seed_reward':game._deal_effect(game.hero_id(1-owner),3,dict(ctx,spell=False,bonus=0,lifesteal=True))
 elif name=='tamsin':p.historical_stormwind_tamsin_uid=game._new_id()
 elif name=='tavish':p.historical_stormwind_tavish=True
 elif name=='target_power':p.historical_stormwind_power_targets=True
 elif name=='zero_power':p.historical_stormwind_zero_generation=getattr(p,'historical_power_generation',0)
 elif name=='upgrade_power':
  from .genn import POWERS
  current=p.primary_power
  hero_class=p.hero_class if current is None else current.get('basic_starting_class')
  if hero_class in POWERS:
   cid=POWERS[hero_class];game._replace_primary_power(owner,dict(card_id=cid,upgraded_starting_class=hero_class,cost=game.cards[cid]['cost']))
 elif name=='distractor':
  target=game._force_live(ctx.get('target'))
  if target is not None:
   side=target.owner;card=game._bounce(target)
   if card is not None:
    taken=game.players[side].turns_taken
    card.play_lock=dict(owner=side,not_before=taken+1,until=taken+2)
 elif name=='gyroblade':
  targets=[m.uid for m in game.players[1-owner].minions if m.health>0]
  if targets:game._deal_effect(game.rng.choice(targets),ctx.get('broken_weapon',{}).get('attack',3),dict(ctx,spell=False,bonus=0))
 elif name=='warrior_weapon':
  values=game._generation_candidates(WARRIOR_WEAPONS,owner)
  if values:game._equip(owner,game.rng.choice(values))
 elif name=='shard':
  game.players[1-owner].health=0
  game._log('destroy_hero',player=1-owner,source='SW_433t3a')
 else:return False
 return True
