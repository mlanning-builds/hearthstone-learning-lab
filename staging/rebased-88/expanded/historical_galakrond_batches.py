"""Physical Galakrond upgrades, Invoke rewards and Devastations; unvalidated."""
from engine.game import Card
from .generation_cards import pool,random_cards
from .historical_draw_batches import draw

BASES=('DRG_650','DRG_610','DRG_600','DRG_620','DRG_660')
POWERS=('DRG_238p','DRG_238p2','DRG_238p3','DRG_238p4','DRG_238p5')
FORMS={cid:(base,level) for base in BASES for level,cid in enumerate((base,base+'t2',base+'t3'))}
HERO_POWERS={cid:POWERS[BASES.index(base)] for cid,(base,level) in FORMS.items()}
PRIEST_MINIONS=pool(card_type='MINION',classes='PRIEST')
DEMONS=pool(card_type='MINION',tribe='DEMON')
RULES={
 'DRG_050':('none',[('historical_galakrond_invoke',)]),
 'DRG_242':('none',[('historical_galakrond_invoke',)]),
 'DRG_303':('none',[('historical_galakrond_invoke',)]),
 'DRG_218':('none',[('historical_galakrond_invoke',)]*2),
 'DRG_202':('none',[('historical_galakrond_invoke',),('historical_galakrond_cultist',)]),
 'DRG_019':('none',[('historical_galakrond_twice','copies')]),
 'DRG_027':('none',[('historical_galakrond_twice','coins')]),
 'DRG_203':('none',[('historical_galakrond_twice','draw')]),
 'DRG_300':('none',[('historical_galakrond_twice','discount')]),
 'DRG_099':('none',[('historical_galakrond_kronx',)]),
}
TOKEN_RULES={
 'DRG_099t1':('none',[('damage_enemy_hero',5),('heal_own_hero',5)]),
 'DRG_099t2':('none',[('summon','DRG_099t2t',1)]),
 'DRG_099t3':('none',[('buff_others',2,2)]),
 'DRG_099t4':('none',[('area_damage','other_minions',5)]),
 'DRG_099t2t':('none',[]),
 'DRG_238t12t2':('none',[]),'DRG_238t14t3':('none',[]),
 'DRG_620t4':('none',[]),'DRG_620t5':('none',[]),'DRG_620t6':('none',[]),
 'DRG_238ht':('none',[]),
 'DRG_021':('none',[('historical_galakrond_invoke',)]),
 'DRG_030':('minion',[('buff',1,0),('historical_galakrond_invoke',)]),
 'DRG_246':('minion',[('destroy',),('historical_galakrond_invoke',)]),
 'DRG_247':('historical_galakrond_undamaged_character',[('damage',3),('historical_galakrond_invoke',)]),
 'DRG_248':('enemy_character',[('freeze',),('historical_galakrond_invoke',)]),
 'DRG_249':('none',[('historical_galakrond_invoke',),('area_damage','all_minions',1)]),
 'DRG_250':('none',[('historical_galakrond_invoke',),('board_buff',1,0)]),
 'DRG_217':('none',[('historical_galakrond_wolves',)]),
 'DRG_217t':('none',[]),
}
for cid,(base,level) in FORMS.items():
 count=(1,2,4)[level]
 if base=='DRG_650':operations=[draw((('type','eq','MINION'),),'buff',(4,4))]*count
 elif base=='DRG_610':operations=[draw(mode='set_cost',args=(0,))]*count
 elif base=='DRG_600':operations=[random_cards(DEMONS,count,destination='board')]
 elif base=='DRG_620':operations=[('summon',('DRG_620t4','DRG_620t5','DRG_620t6')[level],2)]
 else:operations=[('destroy_random_enemy',count)]
 if level==2:operations=operations+[('equip','DRG_238ht')]
 TOKEN_RULES[cid]=('none',operations)
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|frozenset(POWERS)
DEATH_EFFECTS={};END_EFFECTS={};TRIGGERS={}


def primary(game,owner,initial=False):
 p=game.players[owner]
 if p.hero_card_id in FORMS:return FORMS[p.hero_card_id][0]
 values=[c for c in p.hand+p.deck if game._card_data(c)['id'] in FORMS]
 old=getattr(p,'historical_main_galakrond_uid',None)
 held=next((c for c in values if getattr(c,'uid',None)==old and old is not None),None)
 if held is None and values:
  if initial:
   matching=[c for c in values if game._card_data(c).get('cardClass')==p.hero_class]
   if matching:values=matching
  held=min(values,key=lambda c:getattr(c,'uid',2**63))
 if held is None:p.historical_main_galakrond_uid=None;return None
 if not isinstance(held,Card):
  for zone in (p.hand,p.deck):
   index=next((i for i,value in enumerate(zone) if value is held),None)
   if index is not None:
    held=Card(game._new_id(),held);zone[index]=held;break
 p.historical_main_galakrond_uid=held.uid
 return FORMS[held.card_id][0]


def power_operations(power):
 if power=='DRG_238p':return (('hero_attack',3),)
 if power=='DRG_238p2':return (('historical_family_lackeys',1),)
 if power=='DRG_238p3':return (('historical_galakrond_summon','DRG_238t12t2'),)*2
 if power=='DRG_238p4':return (('historical_galakrond_summon','DRG_238t14t3'),)
 if power=='DRG_238p5':return (random_cards(PRIEST_MINIONS),)
 raise ValueError('Unknown explicit Galakrond power')


def split(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_galakrond_invoke':
  base=primary(game,owner)
  if base is None:return ('batch30_noop',),()
  power=POWERS[BASES.index(base)]
  if power=='DRG_238p5':game._generation_candidates(PRIEST_MINIONS,owner)
  return ('historical_galakrond_increment',),(('historical_galakrond_reward',power),)
 if name=='historical_galakrond_reward':
  operations=power_operations(op[1]);reward_context=dict(ctx,source=None,bonus=0,lifesteal=False,spell=False,card_id=op[1],generation_creator_id=op[1])
  return game._split_fixed_summon(('replay_context',operations,reward_context),ctx)
 if name=='historical_galakrond_twice':
  if getattr(p,'historical_invokes',0)<2:return ('batch30_noop',),()
  action={'copies':('copy_self_right',2),'coins':('add','TOKEN_COIN',3),'draw':('draw',3),'discount':('historical_keyword_discount_hand',1)}[op[1]]
  return game._split_fixed_summon(action,ctx)
 if name=='historical_galakrond_wolves':
  amount=3 if getattr(p,'historical_invokes',0)>=2 else 0
  # Pre-entry stats keep summon listeners from seeing the weaker intermediate.
  return ('historical_galakrond_wolf',amount),(('historical_galakrond_wolf',amount),)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_galakrond_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_galakrond_increment':
  p.historical_invokes=getattr(p,'historical_invokes',0)+1
  for zone in (p.hand,p.deck):
   for i,value in enumerate(zone):
    cid=game._card_data(value)['id']
    if cid not in FORMS:continue
    card=value if isinstance(value,Card) else Card(game._new_id(),cid);base,level=FORMS[cid];state=game._b60_state(card)
    progress=max(state.get('historical_galakrond_progress',0),2*level)+1;state['historical_galakrond_progress']=progress
    card.card_id=(base,base+'t2',base+'t3')[min(2,progress//2)];zone[i]=card
  game._refresh_auras();game._log('invoke',player=owner,count=p.historical_invokes)
 elif name=='historical_galakrond_summon':game._summon(owner,op[1],entry_origin='hero_power',entry_site='galakrond_reward')
 elif name=='historical_galakrond_wolf':game._summon(owner,'DRG_217t',attack_bonus=op[1],health_bonus=op[1],entry_origin='effect',entry_site='dragons_pack')
 elif name=='historical_galakrond_cultist':
  if source is not None:game._buff(source,sum(m is not source for m in p.minions),0)
 elif name=='historical_galakrond_kronx':
  if p.hero_card_id in FORMS:
   game.pending_choice=dict(owner=owner,kind='historical_galakrond_devastation',context=dict(ctx),options=[dict(card_id='DRG_099t'+str(i)) for i in range(1,5)]);game.phase='choice'
  else:game._draw(owner,lambda d:d['id'] in FORMS)
 else:return False
 return True


def targets(game,cid,owner,mode):
 if mode!='historical_galakrond_undamaged_character':return None
 return [uid for uid in game._visible_targets(owner,magic=True) if (game.players[-uid-1] if uid<0 else game._find(uid)).health==(game.players[-uid-1] if uid<0 else game._find(uid)).max_health]


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_galakrond_devastation':return False
 operations=TOKEN_RULES[selected['card_id']][1]
 game._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=choice['context']),[]))
 return True
