"""Physical Infuse state, explicit upgraded forms and Relics; unvalidated."""
from .historical_saidan import add as _saidan_add
from engine.game import Card
from .selectors import has_tribe
from .pools import require_fixed_cards
from .historical_draw_batches import draw
from .historical_tribal_batches import INFUSE_FORMS as EARLIER_FORMS

# Required deaths, exact next identity and optional death-type predicate.
FORMS={cid:(n,target,'') for cid,(n,target) in EARLIER_FORMS.items()}
FORMS.update({
 'REV_835':(5,'REV_835t',''),
 'REV_933':(2,'REV_933t',''),
 'MAW_009':(3,'MAW_009t','BEAST'),'MAW_033':(7,'MAW_033t',''),
 'NX2_005':(2,'NX2_005t',''),'REV_013':(5,'REV_013t',''),
 'REV_017':(5,'REV_017t',''),'REV_019':(4,'REV_019t',''),
 'REV_244':(3,'REV_244t',''),'REV_352':(3,'REV_352t',''),
 'REV_353':(4,'REV_353t',''),'REV_353t':(4,'REV_353t2',''),
 'REV_843':(3,'REV_843t',''),'REV_937':(5,'REV_937t',''),
 'REV_956':(3,'REV_956t',''),'REV_957':(4,'REV_957t',''),
 'MAW_003':(3,'MAW_003t','TOTEM'),'NX2_011':(6,'NX2_011t',''),
 'REV_252':(3,'REV_252t',''),'REV_336':(5,'REV_336t4',''),
 'REV_350':(3,'REV_350t2',''),'REV_601':(3,'REV_601t',''),
 'REV_920':(4,'REV_920t',''),'REV_938':(2,'REV_938t',''),
})
for cid in ('MAW_003','REV_252','REV_336','REV_350','REV_601','REV_920','REV_938'):FORMS['CORE_'+cid]=FORMS[cid]
INFUSED_ORIGINS={target:cid for cid,(n,target,tribe) in FORMS.items() if not cid.startswith('CORE_') and cid!=target}
INFUSED_ORIGINS['REV_353t2']='REV_353'
RELICS=('REV_834','REV_943','REV_508')
COMPANIONS=('REV_353t3','REV_353t4','REV_353t5')
RULES={
 'MAW_009':('none',[]),'MAW_031':('none',[]),
 'MAW_033':('enemy_minion',[('destroy',)]),
 'NX2_005':('none',[('historical_if_combo',('buff_self',2,2))]),
 'REV_013':('none',[]),'REV_017':('enemy_minion',[('historical_infuse_devour',False)]),
 'REV_019':('none',[('draw',1)]),'REV_244':('none',[('copy_self_right',1)]),
 'REV_352':('none',[]),'REV_353':('none',[('historical_infuse_companions',1)]),
 'REV_843':('none',[]),
 'REV_937':('none',[('historical_infuse_relic_choice',)]),
 'REV_956':('none',[]),'REV_957':('none',[]),
}
TOKEN_RULES={
 'MAW_009t':('none',[]),'MAW_033t':('enemy_minion',[('historical_infuse_control',)]),
 'NX2_005t':('none',[('historical_if_combo',('buff_self',2,2))]),
 'REV_013t':('character',[('damage',5)]),
 'REV_017t':('enemy_minion',[('historical_infuse_devour',True)]),
 'REV_019t':('none',[('draw',3)]),'REV_244t':('none',[('copy_self_right',2)]),
 'REV_352t':('none',[]),'REV_353t':('none',[('historical_infuse_companions',2)]),
 'REV_353t2':('none',[('historical_infuse_companions',3)]),
 'REV_843t':('none',[]),
 'REV_937t':('none',[('historical_infuse_relic_all',)]),
 'REV_956t':('none',[]),'REV_957t':('none',[]),
 'REV_353t3':('none',[]),'REV_353t4':('none',[]),'REV_353t5':('none',[]),
 'REV_943t':('none',[]),
 'REV_834':('none',[('historical_infuse_relic','extinction')]),
 'REV_943':('none',[('historical_infuse_relic','phantasms')]),
 'REV_508':('none',[('historical_infuse_relic','dimensions')]),
 'MAW_003':('none',[('historical_infuse_totem_choice',)]),
 'MAW_003t':('none',[('historical_infuse_all_totems',)]),
 'NX2_011':('none',[('draw',3)]),'NX2_011t':('none',[('draw',3)]),
 'REV_252':('none',[('historical_infuse_destroy_small',3)]),
 'REV_252t':('none',[('historical_infuse_destroy_small',6)]),
 'REV_336':('none',[('summon','REV_336t2',2)]),
 'REV_336t4':('none',[('summon','REV_336t3',2)]),
 'REV_336t2':('none',[]),'REV_336t3':('none',[]),
 'REV_350':('none',[('historical_infuse_bats',False)]),
 'REV_350t2':('none',[('historical_infuse_bats',True)]),'REV_350t':('none',[]),
 'REV_601':('character',[('damage',3)]),
 'REV_601t':('character',[('damage',3),('historical_infuse_touch_return',)]),
 'REV_920':('friendly_minion',[('historical_infuse_evolve',False)]),
 'REV_920t':('none',[('historical_infuse_evolve',True)]),
 'REV_938':('none',[draw((('type','eq','SPELL'),))]),
 'REV_938t':('none',[draw((('type','eq','SPELL'),),'copy_temporary')]),
}
STANDARD_RULES={'CORE_'+cid:TOKEN_RULES[cid] for cid in ('MAW_003','REV_252','REV_336','REV_350','REV_601','REV_920','REV_938')}
SINGLE_PLAY_EFFECTS={cid:[('historical_infuse_manathirst',8,4,4)] for cid in ('NX2_005','NX2_005t')}
TRIGGERS={cid:('attacking_self',[('historical_infuse_other_beasts',)]) for cid in ('MAW_009','MAW_009t')}
AURAS={'REV_353t4':('others',1,0)}
DEATH_EFFECTS={};END_EFFECTS={}
RULES['REV_835']=('none',[('historical_copy_rafaam_imps',False)])
TOKEN_RULES['REV_835t']=('none',[('historical_copy_rafaam_imps',True)])
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def held_death(game,kind,data):
 if kind!='minion_died':return
 owner=data['owner'];p=game.players[owner]
 zones=[p.hand]
 if any(m.card_id=='MAW_031' and not m.silenced and m.health>0 for m in p.minions):zones.append(p.deck)
 for zone in zones:
  for i,value in enumerate(zone):
   cid=game._card_data(value)['id']
   if cid not in FORMS:continue
   needed,target,tribe=FORMS[cid]
   if tribe and not has_tribe(game._event_card_data(data),tribe):continue
   card=value if isinstance(value,Card) else Card(game._new_id(),cid);zone[i]=card;state=game._b60_state(card)
   state.setdefault('historical_infuse_origin',cid)
   state['historical_infuse']=state.get('historical_infuse',0)+1
   if cid=='REV_843':state['historical_infuse_attack_sum']=state.get('historical_infuse_attack_sum',0)+max(0,data['attack'])
   if state['historical_infuse']<needed:continue
   state['historical_infuse']=0;card.card_id=target
   if cid=='REV_843':
    amount=state['historical_infuse_attack_sum'];_saidan_add(card,'attack_bonus',amount);_saidan_add(card,'health_bonus',amount)


def split(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_infuse_devour':
  q=game.players[1-owner];target=next((m for m in q.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is None:return ('batch30_noop',),()
  board=list(q.board);index=board.index(target);victims=[target]
  if op[1]:victims=[m for m in board[max(0,index-1):index+2] if m in q.minions and m.health>0]
  state={'victims':victims,'attack':sum(max(0,m.attack) for m in victims),'health':sum(max(0,m.health) for m in victims)}
  return ('historical_infuse_devour_wave',state),(('historical_infuse_devour_buff',state),)
 if name=='historical_infuse_companions':
  require_fixed_cards(COMPANIONS,game.cards)
  values=COMPANIONS if op[1]==3 else game.rng.sample(COMPANIONS,op[1])
  operations=tuple(('summon',cid,1) for cid in values)
  first,tail=game._split_fixed_summon(operations[0],ctx);return first,tuple(tail)+operations[1:]
 if name=='historical_infuse_relic_all':
  require_fixed_cards(RELICS,game.cards);values=list(RELICS);game.rng.shuffle(values)
  operations=tuple(('cast_fixed_spell',cid,'random') for cid in values)
  return game._split_fixed_summon(('replay_context',operations,dict(ctx)),ctx)
 if name=='historical_infuse_relic':
  power=1+getattr(p,'historical_relic_level',0)
  if op[1]=='extinction':operations=(('damage_random_enemy_minion',power),)*2
  elif op[1]=='phantasms':operations=(('historical_infuse_spirit',power),)*2
  else:operations=(draw(mode='discount',args=(power,)),)*2
  return game._split_fixed_summon(('replay_context',operations+(('historical_infuse_relic_upgrade',),),dict(ctx)),ctx)
 if name=='historical_infuse_all_totems':
  from .historical_family_batches import BASIC_TOTEMS
  require_fixed_cards(BASIC_TOTEMS,game.cards)
  return game._split_fixed_summon(('replay_context',tuple(('summon',cid,1) for cid in BASIC_TOTEMS),dict(ctx)),ctx)
 if name=='historical_infuse_bats':return ('historical_infuse_bat',op[1]),(('historical_infuse_bat',op[1]),)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_infuse_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_infuse_other_beasts':
  for m in p.minions:
   if m is not source and has_tribe(game._card_data(m),'BEAST'):game._buff(m,2,2)
 elif name=='historical_infuse_control':
  q=game.players[1-owner];target=next((m for m in q.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is not None and len(p.board)<7:
   q.board.remove(target);target.owner=owner;target.summoned_turn=game.turn;target.attacks=0;p.board.append(target);game._refresh_auras()
 elif name=='historical_infuse_devour_wave':
  for m in op[1]['victims']:
   if m.health>0:m.health=0
 elif name=='historical_infuse_devour_buff':
  if source is not None:game._buff(source,op[1]['attack'],op[1]['health'])
 elif name=='historical_infuse_manathirst':
  if p.max_mana>=op[1] and source is not None:game._buff(source,op[2],op[3])
 elif name=='historical_infuse_relic_upgrade':p.historical_relic_level=getattr(p,'historical_relic_level',0)+1
 elif name=='historical_infuse_spirit':game._summon(owner,'REV_943t',attack_bonus=op[1]-1,health_bonus=op[1]-1,entry_site='relic_of_phantasms')
 elif name in ('historical_infuse_relic_choice','historical_infuse_totem_choice'):
  if name=='historical_infuse_relic_choice':values=RELICS;mode='relic'
  else:
   from .historical_family_batches import BASIC_TOTEMS
   values=BASIC_TOTEMS;mode='totem'
  require_fixed_cards(values,game.cards)
  game.pending_choice=dict(owner=owner,kind='historical_infuse_choice',mode=mode,context=dict(ctx),options=[dict(card_id=cid) for cid in values]);game.phase='choice'
 elif name=='historical_infuse_destroy_small':
  for player in game.players:
   for m in player.minions:
    if m.attack<=op[1]:m.health=0
 elif name=='historical_infuse_bat':game._summon(owner,'REV_350t',attack_bonus=1 if op[1] else 0,health_bonus=2 if op[1] else 0,entry_site='frenzied_fangs')
 elif name=='historical_infuse_touch_return':
  cid=getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_infuse_origin','REV_601')
  game._add(owner,'CORE_REV_601' if cid=='CORE_REV_601' else 'REV_601')
 elif name=='historical_infuse_evolve':
  from .transformations import evolve_pool
  values=list(p.minions) if op[1] else [m for m in p.minions if m.uid==ctx.get('target')]
  prepared=[]
  for m in values:
   request=evolve_pool(game._card_stat(m,'cost',owner),2);candidates=game._generation_candidates(request,owner);prepared.append((m,candidates))
  selected=[(m,game.rng.choice(candidates)) for m,candidates in prepared if candidates]
  for m,cid in selected:
   if m in p.board:game._transform(m,cid)
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_infuse_choice':return False
 op=('cast_fixed_spell',selected['card_id'],'random') if choice['mode']=='relic' else ('summon',selected['card_id'],1)
 game._rule_events.append(('captured_effects',dict(operations=(op,),context=choice['context']),[]))
 return True

FORMS['MAW_012']=(3,'MAW_012t','DEMON')
INFUSED_ORIGINS['MAW_012t']='MAW_012'
