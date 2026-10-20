"""Historical Treant, Totem, Recruit and Murloc consumers; unvalidated."""
from engine.game import Card
from .selectors import has_tribe
from .generation_cards import pool,random_cards,discover

TREANTS=frozenset(('CATA_134t3','DAL_256t2','DMF_061t2','DRG_311t','END_009t','ETC_373t','EX1_158t','EX1_573t','EX1_tk9','FP1_019t','GIL_663t','MEND_046t','MIS_301t','REV_336t2','SW_422t','TLC_230t','TTN_950t2','ULD_137t','VAN_EX1_tk9','VAN_EX1_tk9b'))
TREANTS=TREANTS|frozenset(('AV_760t3','CATA_131','EDR_271t','EDR_495','EDR_500','EDR_861','JAM_028','SCH_612t','UNG_111t1'))
INFUSE_FORMS={'REV_935':(2,'REV_935t'),'REV_958':(3,'REV_958t')}
RULES={
 'BOT_419':('none',[('historical_tribal_treant_discover',pool(card_type='SPELL',classes='own_or_neutral'))]),
 'BOT_523':('none',[]),'DRG_319':('none',[('historical_tribal_goru',)]),
 'DMF_240':('none',[('historical_tribal_lothraxion',)]),
 'REV_955':('none',[]),
 'GIL_583':('none',[('historical_tribal_eat_totems',)]),
 'KAR_021':('none',[]),'OG_028':('none',[]),'REV_838':('none',[]),
 'REV_921':('none',[('historical_tribal_stonewright',)]),
 'REV_935':('none',[]),
 'REV_958':('none',[('historical_tribal_recruits',False)]),
 'TID_004':('none',[('historical_tribal_murloc_discount',)]),
 'CFM_699':('none',[('historical_tribal_health_murloc',)]),
 'DMF_707':('none',[]),'OG_006':('none',[('historical_tribal_vilefin',)]),
 'WW_333':('none',[]),
}
TOKEN_RULES={
 'REV_935t':('none',[]),'REV_958t':('none',[('historical_tribal_recruits',True)]),
 'OG_006a':('none',[]),
}
END_EFFECTS={'REV_935':[('historical_family_basic_totem',)],'REV_935t':[('historical_family_basic_totem',)]*2}
DEATH_EFFECTS={'REV_955':[('historical_tribal_stewart',)]}
TRIGGERS={
 'KAR_021':('spell_cast',[('historical_family_basic_totem',)]),
 'DMF_707':(('historical_event','friendly_murloc_death'),[random_cards(pool(card_type='MINION',rarity='LEGENDARY'))]),
}
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'OG_006b'}


def held_death(game,kind,data):
 from .historical_infuse_batches import held_death as shared_infuse
 shared_infuse(game,kind,data)


def aura(game,minion):
 p=game.players[minion.owner]
 treant=getattr(p,'historical_treant_bonus',0) if minion.card_id in TREANTS else 0
 totem=2*getattr(p,'historical_stonewrights',0) if has_tribe(game._card_data(minion),'TOTEM') else 0
 return treant+totem+getattr(p,'historical_eliza',0),treant


def summon_callbacks(game,minion):
 p=game.players[minion.owner];operations=[]
 if minion.card_id=='TTN_900t' and not minion.silenced:
  count=max(0,getattr(p,'historical_summoned_ids',{}).get('TTN_900t',0)-1)
  operations.append(('historical_copy_earthen_growth',minion.uid,count))
 if not minion.dormant and game._is_recruit(minion.card_id):
  count=getattr(p,'historical_stewart_pending',0)
  if count:p.historical_stewart_pending=0;operations.append(('historical_tribal_recruit_stewart',minion.uid,count))
  if getattr(p,'historical_lothraxion',False):operations.append(('historical_tribal_recruit_shield',minion.uid))
 return tuple(operations)


def watch_hands(game):
 if not hasattr(game,'_rule_events'):return
 for owner,p in enumerate(game.players):
  if len(p.hand)>=3:continue
  for m in p.minions:
   if m.card_id=='WW_333' and not m.silenced and m.health>0 and not m.rule_state.get('historical_howdy_queued'):
    m.rule_state['historical_howdy_queued']=True
    game._rule_events.append(('captured_effects',dict(operations=(('historical_tribal_howdy',m.uid,pool(card_type='MINION',tribe='MURLOC')),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))


def split(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_tribal_eat_totems':
  state={'victims':[m for m in p.minions if m.health>0 and has_tribe(game._card_data(m),'TOTEM')]}
  return ('historical_tribal_destroy_totems',state),(('historical_tribal_eat_finish',state),)
 if name=='historical_tribal_recruits':return ('historical_tribal_recruit',op[1]),(('historical_tribal_recruit',op[1]),)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_tribal_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_tribal_goru':p.historical_treant_bonus=getattr(p,'historical_treant_bonus',0)+1;game._refresh_auras()
 elif name=='historical_tribal_stonewright':p.historical_stonewrights=getattr(p,'historical_stonewrights',0)+1;game._refresh_auras()
 elif name=='historical_tribal_treant_discover':
  if any(m.card_id in TREANTS for m in p.minions):game._effect(discover(op[1]),ctx)
 elif name=='historical_tribal_lothraxion':p.historical_lothraxion=True
 elif name=='historical_tribal_stewart':p.historical_stewart_pending=getattr(p,'historical_stewart_pending',0)+1
 elif name=='historical_tribal_recruit_stewart':
  m=next((m for m in p.minions if m.uid==op[1] and m.health>0),None)
  if m is not None:game._buff(m,3*op[2],3*op[2]);m.attached_death_effects.extend([('historical_tribal_stewart',)]*op[2]);m.keywords.add('DEATHRATTLE')
 elif name=='historical_tribal_recruit_shield':
  m=next((m for m in p.minions if m.uid==op[1] and m.health>0),None)
  if m is not None:m.keywords.add('DIVINE_SHIELD')
 elif name=='historical_tribal_recruit':game._summon(owner,'CS2_101t',attack_bonus=2 if op[1] else 0,entry_keywords=('DIVINE_SHIELD',) if op[1] else (),entry_site='buffet_biggun')
 elif name=='historical_tribal_destroy_totems':
  for m in op[1]['victims']:
   if m.health>0:m.health=0
 elif name=='historical_tribal_eat_finish':
  count=sum(any(r['entity'].uid==m.uid for r in p.death_records) for m in op[1]['victims'])
  if source is not None:game._buff(source,2*count,2*count)
 elif name=='historical_tribal_murloc_discount':p.cost_effects.append(dict(selector='MURLOC',amount=2,remaining_uses=2,expires=None))
 elif name=='historical_tribal_health_murloc':p.payment_effects.append(dict(kind='historical_murloc_health',turn=game.turn))
 elif name=='historical_tribal_vilefin':game._replace_primary_power(owner,dict(card_id='OG_006b'))
 elif name=='historical_tribal_howdy':
  m=next((m for m in p.minions if m.uid==op[1] and m.health>0 and not m.silenced),None)
  if m is not None:
   m.rule_state.pop('historical_howdy_queued',None)
   if len(p.hand)<3:
    game._effect(('generate_one',op[2],'hand',()),dict(ctx,source=m,card_id=m.card_id))
    watch_hands(game)
 else:return False
 return True
