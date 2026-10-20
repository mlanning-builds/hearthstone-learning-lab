"""Explicit permanent ritual growth and shared Jade families; unvalidated."""
from engine.game import Card
from .pools import require_fixed_cards

CTHUN_IDS=frozenset(('OG_279','OG_280','WON_135'))
JADE_ART=('CFM_712_t01','CFM_712_t04','CFM_712_t07','CFM_712_t20')
COUNTERFEIT_ART=('JAIL_504tt01','JAIL_504tt04','JAIL_504tt07','JAIL_504tt20')
def ritual(a,h,taunt=False):return ('historical_ritual_grow',a,h,taunt)
RULES={
 'WON_144':('none',[]), # Continuous controller-bound ritual growth; no Battlecry.
 'OG_280':('none',[('historical_ritual_missiles',)]),
 'WON_135':('none',[('historical_ritual_missiles',)]),
 'OG_281':('none',[ritual(2,2)]),'OG_339':('none',[ritual(2,2)]),
 'OG_283':('none',[ritual(3,3)]),'WON_125':('none',[ritual(3,3)]),
 'OG_284':('none',[ritual(1,1,True)]),'WON_124':('none',[ritual(1,1,True)]),
 'OG_293':('none',[ritual(4,4)]),'WON_304':('none',[ritual(4,4)]),
 'OG_162':('character',[('damage',2),ritual(2,2)]),
 'WON_127':('character',[('damage',2),ritual(2,2)]),
 'OG_255':('none',[ritual(2,2),('historical_ritual_doomcaller',)]),
 'OG_282':('minion',[('historical_ritual_blade',)]),'WON_075':('minion',[('historical_ritual_blade',)]),
 'OG_096':('none',[('historical_ritual_ten','heal')]),
 'OG_188':('none',[('historical_ritual_ten','health')]),'WON_010':('none',[('historical_ritual_ten','health')]),
 'OG_301':('none',[('historical_ritual_ten','armor')]),'WON_111':('none',[('historical_ritual_ten','armor')]),
 'OG_131':('none',[('historical_ritual_emperor','OG_319')]),
 'WON_134':('none',[('historical_ritual_emperor','WON_134t')]),
}
END_EFFECTS={'OG_286':[ritual(1,1)]}
TRIGGERS={
 'OG_302':(('historical_event','any_death'),[ritual(1,1)]),
 'WON_322':(('historical_event','any_death'),[ritual(1,1)]),
 'OG_303':('spell_cast',[ritual(1,1)]),
 'OG_321':('damaged_self',[ritual(1,1)]),'WON_131':('damaged_self',[ritual(1,1)]),
 'OG_334':(('historical_event','any_character_healed'),[ritual(1,1)]),
 'WON_313':(('historical_event','any_character_healed'),[ritual(1,1)]),
}
for cid in END_EFFECTS.keys()|TRIGGERS.keys():RULES.setdefault(cid,('none',[]))
for cid in ('CFM_343','CFM_715','WON_118','WON_303','CFM_902','WON_136'):
 RULES[cid]=('none',[('historical_ritual_jade',False,False)])
for cid in ('CFM_312','WON_084'):RULES[cid]=('none',[('historical_ritual_jade',True,False)])
DEATH_EFFECTS={cid:[('historical_ritual_jade',False,False)] for cid in ('CFM_691','WON_067','CFM_902','WON_136')}
for cid in DEATH_EFFECTS:RULES.setdefault(cid,('none',[]))
RULES['TOY_803']=('none',[])
DEATH_EFFECTS['TOY_803']=[('historical_ritual_display_grow',),('historical_ritual_display_shuffle',2)]
TOKEN_RULES={cid:('none',[]) for cid in JADE_ART+COUNTERFEIT_ART+('OG_319','WON_134t')}
TOKEN_RULES['OG_279']=('none',[('historical_ritual_missiles',)])
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def totals(game,owner):return tuple(getattr(game.players[owner],'historical_cthun_growth',(0,0)))


def materialize(game,card,owner):
 """Freeze the current permanent base on a newly created physical body.

 Explicit set-stat copies keep their specified base. Later ritual increments
 add only the new delta, including to those copies.
 """
 cid=card.card_id
 if cid not in CTHUN_IDS and cid!='TOY_803':return
 state=game._b60_state(card)
 if cid in CTHUN_IDS and getattr(card,'_historical_ritual_rebase',False):
  if not getattr(card,'_historical_set_stats',False):
   old=getattr(card,'_historical_ritual_component',(0,0));new=totals(game,owner)
   if hasattr(card,'base_stat_override'):card.base_stat_override=(card.base_stat_override[0]-old[0]+new[0],card.base_stat_override[1]-old[1]+new[1])
   card._historical_ritual_component=new
  state.pop('historical_ritual_taunt',None)
  if getattr(game.players[owner],'historical_cthun_taunt',False):state['historical_ritual_taunt']=True
  del card._historical_ritual_rebase
 if state.get('historical_ritual_initialized'):return
 state['historical_ritual_initialized']=True
 if not hasattr(card,'base_stat_override'):
  a,h=totals(game,owner) if cid in CTHUN_IDS else (getattr(game.players[owner],'historical_display_growth',0),)*2
  if getattr(card,'_historical_set_stats',False):a=h=0
  data=game.cards[cid];card.base_stat_override=(data['attack']+a,data['health']+h)
  if cid in CTHUN_IDS:card._historical_ritual_component=(a,h)
 if cid in CTHUN_IDS and getattr(game.players[owner],'historical_cthun_taunt',False):state['historical_ritual_taunt']=True


def fresh_board(game,minion,entry_source,copy_from):
 if minion is None:return
 cid=minion.card_id
 if copy_from is not None:
  if cid in CTHUN_IDS and minion.owner!=copy_from.owner and not getattr(copy_from,'_historical_set_stats',False):
   old=getattr(copy_from,'_historical_ritual_component',(0,0));new=totals(game,minion.owner)
   permanent_increment(game,minion,new[0]-old[0],new[1]-old[1])
   if copy_from.rule_state.get('historical_ritual_taunt'):minion.keywords.discard('TAUNT')
   if getattr(game.players[minion.owner],'historical_cthun_taunt',False):minion.keywords.add('TAUNT')
  return
 if cid not in CTHUN_IDS and cid!='TOY_803':return
 if not isinstance(entry_source,Card):
  a,h=totals(game,minion.owner) if cid in CTHUN_IDS else (getattr(game.players[minion.owner],'historical_display_growth',0),)*2
  permanent_increment(game,minion,a,h)
 if cid in CTHUN_IDS and (getattr(entry_source,'rule_state',{}).get('historical_ritual_taunt') or not isinstance(entry_source,Card) and getattr(game.players[minion.owner],'historical_cthun_taunt',False)):
  minion.keywords.add('TAUNT');minion.rule_state['historical_ritual_taunt']=True


def permanent_increment(game,value,a,h):
 from .base_stats import base_stats
 if value.card_id in CTHUN_IDS:
  prior=getattr(value,'_historical_ritual_component',(0,0));value._historical_ritual_component=(prior[0]+a,prior[1]+h)
 old=base_stats(game,value)
 if isinstance(value,Card):value.base_stat_override=(old[0]+a,old[1]+h)
 else:
  game._adjust_minion_attack(value,a);value.max_health+=h;value.health+=h
  value.base_stat_override=(old[0]+a,old[1]+h)


def prepare_zones(game,owner,ids):
 p=game.players[owner];result=[]
 for zone in (p.hand,p.deck):
  for i,value in enumerate(zone):
   if game._card_data(value)['id'] not in ids:continue
   card=value if isinstance(value,Card) else Card(game._new_id(),value);materialize(game,card,owner);zone[i]=card;result.append(card)
 return result


def empower(game,owner,a,h,taunt=False):
 p=game.players[owner];cards=prepare_zones(game,owner,CTHUN_IDS)
 old=totals(game,owner);p.historical_cthun_growth=(old[0]+a,old[1]+h)
 if taunt:p.historical_cthun_taunt=True
 for card in cards:
  permanent_increment(game,card,a,h)
  if taunt:game._b60_state(card)['historical_ritual_taunt']=True
 for m in p.all_minions:
  if m.card_id in CTHUN_IDS:
   permanent_increment(game,m,a,h)
   if taunt:m.keywords.add('TAUNT');m.rule_state['historical_ritual_taunt']=True
 game._log('cthun_ritual',player=owner,attack=6+old[0]+a,health=6+old[1]+h,taunt=getattr(p,'historical_cthun_taunt',False))
 game._refresh_auras()


def ten_attack(game,owner):
 if 6+totals(game,owner)[0]>=10:return True
 p=game.players[owner]
 return any(m.card_id in CTHUN_IDS and m.attack>=10 for m in p.all_minions) or any(c.card_id in CTHUN_IDS and game._card_stat(c,'attack',owner)>=10 for c in p.hand)


def jade(game,owner,taunt=False,counterfeit=False):
 art=COUNTERFEIT_ART if counterfeit else JADE_ART;require_fixed_cards(art,game.cards)
 p=game.players[owner];size=min(30,getattr(p,'jade_size',0)+1);p.jade_size=size
 cid=art[3 if size>=20 else 2 if size>=7 else 1 if size>=4 else 0]
 card=Card(game._new_id(),cid);card.base_stat_override=(size,size);card._historical_jade_definition=dict(attack=size,health=size,cost=min(10,size))
 return game._summon(owner,cid,entry_source=card,entry_origin='effect',entry_zone='generated',entry_keywords=('TAUNT',) if taunt else (),entry_site='historical_jade')


def split(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_ritual_missiles':
  source=ctx.get('source');count=min(100,max(0,source.attack)) if source is not None else 0
  return game._split_fixed_summon(('missiles','enemies',count),ctx)
 if name=='historical_ritual_emperor':return game._split_fixed_summon(('summon',op[1],1 if ten_attack(game,owner) else 0),ctx)
 if name=='historical_ritual_blade':
  state=ctx.get('_historical_blade_snapshot')
  if state is None:
   target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
   state={'uid':getattr(target,'uid',None),'attack':max(0,target.attack) if target is not None else 0,'health':max(0,target.health) if target is not None else 0}
   ctx['_historical_blade_snapshot']=state
  return ('historical_ritual_blade_destroy',state),(ritual(state['attack'],state['health']),)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_ritual_'):return False
 owner=ctx['owner'];p=game.players[owner]
 if name=='historical_ritual_grow':empower(game,owner,*op[1:])
 elif name=='historical_ritual_jade':jade(game,owner,op[1],op[2])
 elif name=='historical_ritual_ten':
  if ten_attack(game,owner):game._effect({'heal':('heal_own_hero',10),'health':('buff_self',0,5),'armor':('armor',10)}[op[1]],ctx)
 elif name=='historical_ritual_doomcaller':
  dead=next((cid for cid in reversed(p.death_history) if cid in CTHUN_IDS),None)
  if dead:
   card=Card(game._new_id(),dead);materialize(game,card,owner);p.deck.append(card);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif name=='historical_ritual_blade_destroy':
  target=next((m for player in game.players for m in player.minions if m.uid==op[1]['uid'] and m.health>0),None)
  if target is not None:target.health=0
 elif name=='historical_ritual_display_grow':
  cards=prepare_zones(game,owner,{'TOY_803'});p.historical_display_growth=getattr(p,'historical_display_growth',0)+1
  for card in cards:permanent_increment(game,card,1,1)
  for m in p.all_minions:
   if m.card_id=='TOY_803':permanent_increment(game,m,1,1)
  game._refresh_auras()
 elif name=='historical_ritual_display_shuffle':
  cards=[]
  for _ in range(op[1]):
   card=Card(game._new_id(),'TOY_803');materialize(game,card,owner);p.deck.append(card);cards.append(card)
  game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,op[1],'shuffle',cards=cards)
 else:return False
 return True
