"""Historical Freeze and conditional Dormant state machines; unvalidated."""
from .generation_cards import pool,random_cards
from .selectors import has_tribe
from .pools import require_fixed_cards

WILDSEEDS=('REV_360t','REV_360t1','REV_360t2')
DORMANT_INITIAL={'WW_375':6,'SW_077':-1,'TOY_866':-1,'TSC_657':-1,'TTN_840':-1,'GDB_842':5,
 'REV_360t':1,'REV_360t1':2,'REV_360t2':3}
AWAKEN_EFFECTS={'REV_360t2':[('equip','REV_360t4')]}
DORMANT_END_EFFECTS={'GDB_842':[('historical_sleep_gorm',)]}
WAKE_RULES={
 'SW_077':('cards',3),'TOY_866':('deaths',7),'TSC_657':('spell_mana',5),'TTN_840':('draws',4),
 'DAL_357':('healed',5),'GVG_035':('beast_deaths',2),'WON_011':('beast_deaths',2),
 'SW_323':('friendly_deaths',5),'RLK_604':('fire',1),'UNG_065':('turn_cards',4),
}
RULES={cid:('none',[]) for cid in set(DORMANT_INITIAL)|set(WAKE_RULES) if cid not in WILDSEEDS}
RULES.update({
 'AV_128':('none',[]),'VAC_328':('none',[]),
 'GVG_002':('none',[]),'ICC_088':('none',[]),'TTN_077':('none',[]),
 'AV_257':('none',[('historical_sleep_frost_stags',)]),
 'BAR_748':('none',[('historical_sleep_freeze_or_damage',4)]),
 'ICC_838':('none',[('summon','ICC_838t',2)]),
 'REV_360':('none',[('historical_sleep_wildseed',)]),
 'REV_363':('none',[('summon',cid,1) for cid in WILDSEEDS]),
 'DMF_116':('minion',[('historical_sleep_nameless',)]),
 'AV_251':('none',[]),'VAC_531':('none',[]),
})
TOKEN_RULES={cid:('none',[]) for cid in WILDSEEDS+('REV_360t4','AV_257t','ICC_838t')}
DEATH_EFFECTS={cid:[('historical_sleep_rebirth',*WAKE_RULES[cid])] for cid in ('DAL_357','GVG_035','WON_011','SW_323','RLK_604','UNG_065')}
DEATH_EFFECTS.update({'ICC_838t':[random_cards(pool(card_type='MINION',rarity='LEGENDARY'))],
 'VAC_402':[('historical_sleep_sample_frozen',3,5)]})
TRIGGERS={cid:('dormant_historical_progress',[('historical_sleep_wake_progress',)]) for cid in WAKE_RULES}
TRIGGERS.update({
 'AV_128':(('historical_event','spell_fire_thaw'),[('historical_sleep_thaw',)]),
 'AV_251':(('historical_event','enemy_frozen'),[('historical_sleep_freeze_damage',3)]),
 'VAC_531':(('summon','enemy',None),[('historical_sleep_silence_destroy_summoned',)]),
})
for cid in DEATH_EFFECTS: 
 if cid not in TOKEN_RULES:RULES.setdefault(cid,('none',[]))
RULES.update({
 'AV_222':('none',[('historical_sleep_repeat_area',1)]),
 'GIL_825':('none',[('historical_sleep_repeat_area',2)]),
 'BAR_735':('none',[('historical_sleep_healing_area',)]),
 'DED_503':('historical_hero_damage_target',[('historical_sleep_hero_damage',)]),
})
DORMANT_INITIAL.update({'BT_850':-1,'LOOT_526':-1})
WAKE_RULES['BT_850']=('enemy_warders',3)
RULES.update({'BT_850':('none',[('summon_opponent','BT_850t',3)]),'LOOT_526':('none',[('historical_sleep_candles',)]),'SW_079':('none',[])})
TRIGGERS['BT_850']=('dormant_historical_progress',[('historical_sleep_wake_progress',)])
AWAKEN_EFFECTS['BT_850']=[('historical_sleep_magtheridon_destroy',)]
TOKEN_RULES.update({'BT_850t':('none',[]),'LOOT_526t':('none',[('historical_sleep_candle',)])})
TOKEN_RULES['REV_361']=('none',[('historical_sleep_wild_spirits',)])
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
DAMAGE_FREEZERS=frozenset(('GVG_002','ICC_088','TTN_077','AV_257t'))


def entry(game,minion):
 if minion.card_id in ('AV_128','VAC_328') and not minion.silenced:
  minion.rule_state['historical_permanent_frozen']=True
  game._freeze(minion.uid)


def matches(game,wanted,kind,data,minion):
 if wanted!='dormant_historical_progress':return None
 definition=minion.rule_state.get('historical_sleep_rule',WAKE_RULES.get(minion.card_id))
 if not minion.dormant or definition is None:return False
 rule,_=definition;owner=minion.owner;amount=0
 if rule in ('cards','turn_cards'):
  if kind not in ('minion_played','spell_cast','dormant_other_card_played') or data['owner']!=owner or data.get('source')==minion.uid:return False
  amount=1
 elif rule=='enemy_warders':amount=int(kind=='minion_died' and data['owner']!=owner and game._event_card_data(data)['id']=='BT_850t')
 elif rule=='deaths':amount=int(kind=='minion_died')
 elif rule=='friendly_deaths':amount=int(kind=='minion_died' and data['owner']==owner)
 elif rule=='beast_deaths':amount=int(kind=='minion_died' and data['owner']==owner and has_tribe(game._event_card_data(data),'BEAST'))
 elif rule=='draws':amount=int(kind=='card_drawn' and data['owner']==owner)
 elif rule=='spell_mana':amount=data.get('cost',0) if kind=='spell_cast' and data['owner']==owner else 0
 elif rule=='fire':amount=int(kind=='spell_cast' and data['owner']==owner and game.cards[data['card_id']].get('spellSchool')=='FIRE')
 elif rule=='healed':amount=data['restored'] if kind=='historical_healed' and data.get('healer')==owner else 0
 if amount<=0:return False
 minion.rule_state['historical_sleep_progress']=minion.rule_state.get('historical_sleep_progress',0)+amount
 return True


def split(game,op,ctx):
 owner=ctx['owner'];source=ctx.get('source')
 if op[0]=='historical_sleep_dungar_reward':
  path=op[1]
  operations=(('historical_copy_literal_family','adventurer','board'),) if path==1 else (('heal_own_hero',10),) if path==3 else (('missiles','enemies',12),)
  return game._split_fixed_summon(('replay_context',operations,dict(ctx)),ctx)
 if op[0]=='historical_sleep_repeat_area':
  state={}
  return ('historical_sleep_capture_area',op[1],state),(('historical_sleep_repeat_after',op[1],state),)
 if op[0]=='historical_sleep_repeat_after':
  if any(victim.health<=0 for victim in op[2].get('victims',())):return split(game,('historical_sleep_repeat_area',op[1]),ctx)
  return ('batch30_noop',),()
 if op[0]=='historical_sleep_frost_stags':
  count=getattr(game.players[owner],'historical_school_counts',{}).get('FROST',0)
  return game._split_fixed_summon(('summon','AV_257t',count),ctx)
 if op[0]=='historical_sleep_gorm':
  board=game.players[owner].board
  if source not in board or not source.dormant:return ('batch30_noop',),()
  index=board.index(source)+1
  if index>=len(board) or board[index] not in game.players[owner].minions:return ('batch30_noop',),()
  return ('historical_sleep_kill',board[index].uid),(('historical_sleep_reduce',2),)
 if op[0]=='historical_sleep_sample_frozen':
  p=game.players[1-owner];values=[game.hero_id(1-owner)]+[m.uid for m in p.minions]
  selected=game.rng.sample(values,min(op[1],len(values)))
  operations=tuple(('historical_sleep_freeze_one',uid,(game.players[-uid-1] if uid<0 else game._find(uid)).frozen_until>=0,op[2]) for uid in selected)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_sleep_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_sleep_capture_area':
  victims=[m for player in game.players for m in player.minions if m is not source and m.health>0];op[2]['victims']=tuple(victims)
  with game._damage_batch():
   for victim in victims:game._deal_effect(victim.uid,op[1],ctx)
 elif name=='historical_sleep_healing_area':
  amount=p.healing_done_turn
  if amount:game._effect(('area_damage','enemy_minions',amount),ctx)
 elif name=='historical_sleep_magtheridon_destroy':
  for player in game.players:
   for minion in player.minions:
    if minion is not source:minion.health=0
 elif name=='historical_sleep_dungar_depart':
  if source is not None and not source.dormant and source.health>0:
   source.rule_state['historical_dungar_path']=op[1]
   game._sleep_minion(source,op[1])
 elif name=='historical_sleep_candles':
  from engine.game import Card
  require_fixed_cards(('LOOT_526t',),game.cards)
  cards=[Card(game._new_id(),'LOOT_526t') for _ in range(3)]
  game.players[1-owner].deck.extend(cards)
  game.rng.shuffle(game.players[1-owner].deck)
  game._record_deck_insertion(1-owner,owner,3,'shuffle',cards=cards)
 elif name=='historical_sleep_candle':
  # Candles snuff every opposing dormant Darkness, never the caster's own.
  for minion in tuple(game.players[1-owner].all_minions):
   if minion.card_id=='LOOT_526' and minion.dormant and not minion.silenced:
    progress=minion.rule_state.get('historical_sleep_progress',0)+1
    minion.rule_state['historical_sleep_progress']=progress
    if progress>=3:game._awaken(minion)
 elif name=='historical_sleep_hero_damage':
  if p.hero_damage_taken_turn:game._deal_effect(ctx.get('target',0),p.hero_damage_taken_turn,ctx)
 elif name=='historical_sleep_rebirth':
  if source is not None:
   minion=game._summon(owner,source.card_id,min(ctx.get('death_position',len(p.board)),len(p.board)),dormant_turns=-1,entry_origin='resurrection',entry_site='conditional_dormant_rebirth')
   if minion is not None:minion.rule_state['historical_sleep_rule']=(op[1],op[2])
 elif name=='historical_sleep_wake_progress':
  if source is not None and source.dormant:
   rule,needed=source.rule_state.get('historical_sleep_rule',WAKE_RULES.get(source.card_id))
   amount=p.cards_played if rule=='turn_cards' else source.rule_state.get('historical_sleep_progress',0)
   if amount>=needed:game._awaken(source)
 elif name=='historical_sleep_wild_spirits':
  require_fixed_cards(WILDSEEDS,game.cards)
  for cid in game.rng.sample(WILDSEEDS,2):game._summon(owner,cid,entry_origin='effect',entry_site='wild_spirits')
  for minion in tuple(p.all_minions):
   if minion.card_id in WILDSEEDS and minion.dormant>0:
    if minion.dormant==1:game._awaken(minion)
    else:minion.dormant-=1
 elif name=='historical_sleep_wildseed':
  require_fixed_cards(WILDSEEDS,game.cards);game._summon(owner,game.rng.choice(WILDSEEDS),entry_origin='effect',entry_site='random_wildseed')
 elif name=='historical_sleep_kill':
  target=next((m for player in game.players for m in player.minions if m.uid==op[1] and m.health>0),None)
  if target is not None:target.health=0
 elif name=='historical_sleep_reduce':
  if source is not None and source.dormant>0:
   if source.dormant<=op[1]:game._awaken(source)
   else:source.dormant-=op[1]
 elif name=='historical_sleep_thaw':
  if source is not None:source.rule_state.pop('historical_permanent_frozen',None);source.frozen_until=-1
 elif name=='historical_sleep_freeze_or_damage':
  values=[(m.uid,m.frozen_until>=0) for m in game.players[1-owner].minions]
  with game._damage_batch():
   for uid,frozen in values:
    if frozen:game._deal_effect(uid,op[1],ctx)
    else:game._freeze(uid)
 elif name=='historical_sleep_freeze_one':
  if op[2]:game._deal_effect(op[1],op[3],ctx)
  else:game._freeze(op[1])
 elif name=='historical_sleep_freeze_damage':game._deal_effect(ctx['event']['target'],op[1],ctx)
 elif name=='historical_sleep_nameless':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
  if source is not None and target is not None:
   from .historical_copy_batches import replace
   result=replace(game,source,target,(4,4));victim=result if target is source else target
   if victim is not None:game._silence(victim)
 elif name=='historical_sleep_silence_destroy_summoned':
  if game.current==owner:
   uid=ctx['event']['source'];target=next((m for m in game.players[1-owner].minions if m.uid==uid and m.health>0),None)
   if target is not None:game._silence(target);target.health=0
 else:return False
 return True


def targets(game,cid,owner,mode):
 if mode!='historical_hero_damage_target':return None
 return game._targets_for(cid,owner,'enemy_minion') if game.players[owner].hero_damage_taken_turn>0 else [0]


def listeners(game):
 return [(m,('dormant_historical_progress',[('historical_sleep_wake_progress',)])) for player in game.players for m in player.all_minions if m.dormant and not m.silenced and m.card_id not in WAKE_RULES and m.rule_state.get('historical_sleep_rule')]
