"""Staged compound Quests and reward families, separate from live admission."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .quest_progress import objective,advance_objective
from .generation_cards import pool,discover
from .selectors import has_tribe,effective_tribes
from .adapt import ADAPTATIONS,PLANT,apply_adaptation

SHOKK_POOLS=tuple(pool(card_type='MINION',tribe='BEAST',attack_minimum=n,attack_maximum=n) for n in (8,6,4))
LATORVIUS_REWARDS=('UNG_028t','UNG_067t1','UNG_116t','UNG_829t1','UNG_920t1','UNG_934t1','UNG_940t8','UNG_942t','UNG_954t1')
MURLOCS=pool(card_type='MINION',tribe='MURLOC')
def requests_for(cid):
 if cid in ('TLC_830','TLC_830t'):return set(SHOKK_POOLS)
 return {MURLOCS} if cid in ('UNG_942t','TLC_602','TLC_602t') else set()

ROOT='TLC_817'
SUBQUESTS=('TLC_817t','TLC_817t2')
HALVES=('TLC_817t3','TLC_817t4')
COMBINED='TLC_817t5'
SCHOOLS=('HOLY','SHADOW')
RULES={ROOT:('none',[('equilibrium_start',)])}
TOKEN_RULES={cid:('none',[('equilibrium_start',i)]) for i,cid in enumerate(SUBQUESTS)}
RULES['TLC_460']=('none',[('forbidden_start',)])
TOKEN_RULES['TLC_460t']=('none',[])
TOKEN_RULES['UNG_028t']=('none',[('time_warp',)])
TOKEN_RULES.update({
 'TLC_602t':('none',[('latorvius_rewards',)]),
 'UNG_067t1':('none',[('crystal_core',)]),
 'UNG_829t1':('none',[('nether_portal',)]),
 'UNG_829t3':('none',[]),
 'UNG_934t1':('none',[('sulfuras_power',)]),
 'UNG_942t':('none',[('generation_fill_plain_hand',MURLOCS)]),
 'UNG_116t':('none',[('deck_minions_set_cost',0)]),
 'UNG_920t1':('none',[('insert_fixed','UNG_920t2',20,'shuffle')]),
 'UNG_920t2':('none',[('draw',1)]),
 'UNG_940t8':('none',[('set_hero_health',40)]),
 'UNG_954t1':('none',[('minion_adapt',)]*5),
})
RULES['TLC_229']=('none',[('mountain_start',)])
TOKEN_RULES['TLC_229t14']=('none',[('ashalon_adapt',),('ashalon_adapt',)])
RULES['TLC_830']=('none',[('foodchain_start',)])
TOKEN_RULES['TLC_830t']=('none',[('shokk_preflight',)]+[discover(p,set_cost=2) for p in SHOKK_POOLS])
RULES['END_017']=('none',[('endtime_start',)])
TOKEN_RULES['END_017t']=('none',[('draw_until',10)])
RULES['TLC_631']=('none',[('colossus_start',)])
TOKEN_RULES['TLC_631t']=('none',[('gorishi_enable',)])
TOKEN_RULES.update({HALVES[0]:('none',[('copy_self_right',1)]),HALVES[1]:('none',[]),COMBINED:('none',[('copy_self_right',1)])})
DEATH_EFFECTS={cid:[('soletos_damage',)] for cid in (HALVES[1],COMBINED)}

DEATH_EFFECTS['END_017t']=[('endtime_empty',)]

class QuestFamilies:
 def _quest_family_card_played(self,owner,card):
  q=self.players[owner].quest;d=self._card_data(card)
  if q and q.get('mountain'):
   unused=sorted(effective_tribes(d)-set(q['seen']))
   if unused:
    q['seen'].append(self.rng.choice(unused));q['progress']=len(q['seen']);self._quest_deliver_ready(owner)
  if not q or not q.get('foodchain') or d.get('type')!='MINION' or not has_tribe(d,'BEAST'):return
  attack=d.get('attack',0)+card.attack_bonus
  if attack in (1,3,5,7) and attack not in q['seen']:
   q['seen'].append(attack);q['progress']=len(q['seen']);self._quest_deliver_ready(owner)

 def _ashalon_play(self,owner,minion):
  for choice in self.players[owner].ashalon_adaptations:apply_adaptation(self,minion,choice)

 def _quest_family_choice(self,choice,selected):
  if choice['kind'] not in ('ashalon_adapt','minion_adapt'):return False
  cid=selected['card_id'];apply_adaptation(self,choice['source'],cid)
  if choice['kind']=='ashalon_adapt':self.players[choice['owner']].ashalon_adaptations.append(cid)
  return True

 def _quest_hand_state(self,owner):
  p=self.players[owner];q=p.quest
  if not q or not q.get('endtime') or self.phase=='mulligan':return
  if q['progress']==0 and len(p.hand)==10:q['progress']=1
  elif q['progress']==1 and not p.hand:q['progress']=2

 def _is_quest(self,cid):
  from .quests import QUESTS
  return cid in QUESTS or cid in RULES or cid in SUBQUESTS

 def _quest_slots(self,owner):
  q=self.players[owner].quest
  if not q:return 0
  if 'equilibrium_branches' in q:
   return sum(i not in q['rewards_delivered'] for i in range(len(q['equilibrium_branches'])))
  return 1

 def _quest_family_event(self,kind,data):
  if kind=='discover_completed':
   owner=data['owner'];p=self.players[owner];q=p.quest
   if q and q.get('forbidden'):
    q['progress']=min(8,q['progress']+1);self._quest_deliver_ready(owner)
   offer=data['offer'];weapon=p.weapon;physical=p.equipped_card
   if weapon and weapon['card_id']=='TLC_460t' and physical is not None and physical.uid==offer.weapon_uid:
    options=offer.unchosen
    if any(option.get('card_id') not in self.cards for option in options):raise UnsupportedCard('Origin Stone offer lacks executable card identity')
    operations=(('origin_execute',physical.uid,tuple(option['card_id'] for option in options)),)
    self._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
   return
  if kind=='damage':
   owner=data.get('damage_owner')
   if owner not in (0,1) or data.get('target_owner')==owner or data['amount']!=2:return
   p=self.players[owner];q=p.quest
   if q and q.get('colossus') and self.current==owner:
    q['progress']=min(12,q['progress']+1);self._quest_deliver_ready(owner)
   if p.gorishi_stacks and data.get('damage_cause')!='gorishi':
    self._rule_events.append(('captured_effects',dict(operations=tuple(('gorishi_hit',data['target']) for _ in range(p.gorishi_stacks)),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
   return
  if kind!='spell_cast':return
  owner=data['owner'];q=self.players[owner].quest
  if not q or 'equilibrium_branches' not in q:return
  school=self.cards[data['card_id']].get('spellSchool')
  state,completed=advance_objective(q['objective'],dict(kind='spell',school=school))
  q['objective']=state;q['progress']=sum(c['progress'] for c in state['children'])
  if completed:self._log('quest_objective_complete',player=owner,paths=[list(p) for p in completed])
  self._quest_deliver_ready(owner)

 def _quest_family_deliver(self,owner):
  self._quest_hand_state(owner)
  p=self.players[owner];q=p.quest
  if q and q.get('lost_city'):
   if q['progress']==10 and len(p.hand)<10:
    p.quest=None;self._add(owner,'TLC_602t')
   return True
  if q and q.get('forbidden'):
   if q['progress']==8 and len(p.hand)<10:
    p.quest=None;self._add(owner,'TLC_460t')
   return True
  if q and q.get('mountain'):
   if q['progress']==6 and len(p.hand)<10:
    p.quest=None;self._add(owner,'TLC_229t14')
   return True
  if q and q.get('foodchain'):
   if q['progress']==4 and len(p.hand)<10:
    p.quest=None;self._add(owner,'TLC_830t')
   return True
  if q and q.get('endtime'):
   if q['progress']==2 and len(p.hand)<10:
    p.quest=None;self._add(owner,'END_017t')
   return True
  if q and q.get('colossus'):
   if q['progress']==12 and len(p.hand)<10:
    p.quest=None;self._add(owner,'TLC_631t')
   return True
  if not q or 'equilibrium_branches' not in q:return False
  for index,branch in enumerate(q['equilibrium_branches']):
   if index in q['rewards_delivered'] or not q['objective']['children'][index]['complete']:continue
   if len(p.hand)>=10:break
   q['rewards_delivered'].append(index)
   self._add(owner,HALVES[branch])
   self._log('quest_reward_delivered',player=owner,card=HALVES[branch])
  if len(q['rewards_delivered'])==len(q['equilibrium_branches']):p.quest=None
  return True

 def _quest_family_hand_checkpoint(self):
  changed=False
  for owner,p in enumerate(self.players):
   while True:
    halves=[next((c for c in p.hand if c.card_id==cid),None) for cid in HALVES]
    if any(c is None for c in halves):break
    if self.cards.get(COMBINED,{}).get('type')!='MINION':raise UnsupportedCard('Missing combined Sol etos metadata')
    index=min(p.hand.index(c) for c in halves)
    for c in halves:p.hand.remove(c)
    # The combination creates the printed combined card. Hand enchantments
    # on the separate halves are not transferred to it.
    card=Card(self._new_id(),COMBINED);card._hand_entry_turn=self.turn
    p.hand.insert(index,card)
    self._log('quest_halves_combined',player=owner)
    changed=True
  if changed:self._quest_deliver_ready()
  return changed

 def _quest_family_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='time_warp':
   if not p.time_warp_used:
    p.time_warp_used=True;p.extra_turns_pending+=1
  elif op[0]=='latorvius_rewards':
   dependencies=(*LATORVIUS_REWARDS,'UNG_920t2','UNG_934t2','UNG_829t2','UNG_829t3',PLANT,*ADAPTATIONS)
   if any(cid not in self.cards for cid in dependencies):raise UnsupportedCard('Missing Latorvius reward dependency')
   self._generation_candidates(MURLOCS,owner)
   chosen=self.rng.sample(LATORVIUS_REWARDS,2)
   for cid in chosen:self._add(owner,cid)
   rest=[Card(self._new_id(),cid) for cid in LATORVIUS_REWARDS if cid not in chosen]
   p.deck.extend(rest);self.rng.shuffle(p.deck)
   self._record_deck_insertion(owner,owner,len(rest),'shuffle')
  elif op[0]=='crystal_core':
   p.crystal_core=True
   for m in p.all_minions:
    m.base_stat_override=(5,5);self._set_entity_stats(m,5,5)
   for zone in (p.hand,p.deck):
    for i,value in enumerate(zone):
     if self._card_data(value)['type']!='MINION':continue
     if not isinstance(value,Card):value=Card(self._new_id(),value);zone[i]=value
     value.base_stat_override=(5,5)
  elif op[0]=='sulfuras_power':
   if self.cards.get('UNG_934t2',{}).get('type')!='HERO_POWER':raise UnsupportedCard('Missing Sulfuras Hero Power')
   self._replace_primary_power(owner,dict(card_id='UNG_934t2'))
  elif op[0]=='deck_minions_set_cost':
   for index,value in enumerate(p.deck):
    if self._card_data(value)['type']!='MINION':continue
    if not isinstance(value,Card):value=Card(self._new_id(),value);p.deck[index]=value
    self._set_card_cost(value,op[1])
  elif op[0]=='forbidden_start':
   if p.quest is None and len(p.secrets)<5:
    if self.cards.get('TLC_460t',{}).get('type')!='WEAPON':raise UnsupportedCard('Missing Origin Stone reward')
    p.quest=dict(card_id='TLC_460',progress=0,total=8,forbidden=True)
  elif op[0]=='origin_execute':
   if p.equipped_card is None or p.equipped_card.uid!=op[1] or not p.weapon:return True
   # Reserve the triggering charge before nested Discover can enqueue more.
   p.weapon['durability']-=1
   if p.weapon['durability']<=0:self._break_weapon(owner)
   operations=tuple(('automatic_card',Card(self._new_id(),cid),'random') for cid in op[2])
   self._rule_events.appendleft(('captured_effects',dict(operations=operations,context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,automatic_choices=True)),[]))
  elif op[0]=='mountain_start':
   if p.quest is None and len(p.secrets)<5:
    if self.cards.get('TLC_229t14',{}).get('type')!='MINION':raise UnsupportedCard('Missing Ashalon reward')
    p.quest=dict(card_id='TLC_229',progress=0,total=6,mountain=True,seen=[])
  elif op[0] in ('ashalon_adapt','minion_adapt'):
   for cid in (*ADAPTATIONS,PLANT):
    if cid not in self.cards:raise UnsupportedCard('Missing Adapt dependency: '+cid)
   self.pending_choice=dict(kind=op[0],owner=owner,source=ctx.get('source'),options=[dict(card_id=cid) for cid in self.rng.sample(sorted(ADAPTATIONS),3)])
   self.phase='choice'
  elif op[0]=='foodchain_start':
   if p.quest is None and len(p.secrets)<5:
    if self.cards.get('TLC_830t',{}).get('type')!='MINION':raise UnsupportedCard('Missing Shokk reward')
    p.quest=dict(card_id='TLC_830',progress=0,total=4,foodchain=True,seen=[])
  elif op[0]=='shokk_preflight':
   for request in SHOKK_POOLS:self._generation_candidates(request,owner)
  elif op[0]=='endtime_start':
   if p.quest is None and len(p.secrets)<5:
    if self.cards.get('END_017t',{}).get('type')!='MINION':raise UnsupportedCard('Missing Tick and Tock reward')
    p.quest=dict(card_id='END_017',progress=0,total=2,endtime=True)
    self._quest_hand_state(owner)
  elif op[0]=='endtime_empty':
   self._discard_cards(1-owner,list(self.players[1-owner].hand))
  elif op[0]=='colossus_start':
   if p.quest is None and len(p.secrets)<5:
    if self.cards.get('TLC_631t',{}).get('type')!='MINION':raise UnsupportedCard('Missing Gorishi reward')
    p.quest=dict(card_id='TLC_631',progress=0,total=12,colossus=True)
  elif op[0]=='gorishi_enable':p.gorishi_stacks+=1
  elif op[0]=='gorishi_hit':
   target=op[1]
   if target<0 or any(m.uid==target and m.health>0 for side in self.players for m in side.minions):
    self._damage(target,2,damage_source=None,damage_owner=owner,damage_cause='gorishi')
  elif op[0]=='equilibrium_start':
   if p.quest is not None:
    self._log('quest_fizzle',player=owner,card=ROOT,reason='active_quest');return True
   requested=(op[1],) if len(op)>1 else (0,1)
   branches=requested[:max(0,5-len(p.secrets))]
   if not branches:
    self._log('quest_fizzle',player=owner,card=ROOT,reason='capacity');return True
   for cid in (*HALVES,COMBINED):
    if self.cards.get(cid,{}).get('type')!='MINION':raise UnsupportedCard('Missing Sol etos reward: '+cid)
   p.quest=dict(card_id=ROOT,progress=0,total=4*len(branches),equilibrium_branches=list(branches),rewards_delivered=[],objective=objective(dict(kind='parallel',children=[dict(kind='count',event='spell',total=4,where={'school':SCHOOLS[i]}) for i in branches])))
   for i in branches:self._log('quest_subquest_started',player=owner,card=SUBQUESTS[i])
  elif op[0]=='soletos_damage':
   targets=[self.hero_id(1-owner)]+[m.uid for m in self.players[1-owner].minions]
   self._deal_effect(self.rng.choice(targets),5,ctx)
  else:return False
  return True
