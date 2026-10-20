"""Physical improving weapon state and captured equipped-weapon listeners."""
from .generation_cards import pool
KEY='historical_festival_upgrades'
WEAPONS=('ETC_317','ETC_405','ETC_518','ETC_520','ETC_832','ETC_521','ETC_312','MIS_101','WW_347','ETC_388','ETC_813','ETC_423')
TOKEN_RULES={cid:('none',[]) for cid in WEAPONS+('ETC_521t','ETC_387bt','ETC_423t','REV_933','REV_933t')}
DEATH_EFFECTS={cid:[('historical_growing_weapon_death',cid)] for cid in ('ETC_317','ETC_405','ETC_518','ETC_520','ETC_832','ETC_388','ETC_813','ETC_423')}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def improve(game,owner):
 p=game.players[owner]
 if p.weapon is None:return
 value=p.weapon.get(KEY,0)+1;p.weapon[KEY]=value
 if p.equipped_card is not None:game._b60_state(p.equipped_card)[KEY]=value


def equip(game,owner):
 p=game.players[owner]
 if p.weapon is not None and p.weapon['card_id'] in WEAPONS:p.weapon[KEY]=getattr(p.equipped_card,'rule_state',{}).get(KEY,0)


def paid(game,owner,card,cost,outcast):
 p=game.players[owner];weapon=p.weapon
 if weapon is None:return
 cid=weapon['card_id'];data=game._card_data(card)
 if (cid=='ETC_317' and data['type']=='MINION' or
     cid=='ETC_405' and outcast and 'OUTCAST' in game._card_mechanics(card) or
     cid=='ETC_518' and 'COMBO' in game._card_mechanics(card) or
     cid=='ETC_388' and cost>=5):
  improve(game,owner)


def event(game,kind,data):
 from .historical_pool_weapons import event as pool_weapon_event
 pool_weapon_event(game,kind,data)
 owner=data.get('owner')
 if owner not in (0,1):return
 p=game.players[owner];weapon=p.weapon
 if weapon is None:return
 cid=weapon['card_id'];uid=getattr(p.equipped_card,'uid',None)
 if cid=='ETC_520' and kind=='armor_gained' and data.get('amount',0)>0:improve(game,owner)
 if cid=='ETC_832' and kind=='spell_cast':improve(game,owner)
 if cid=='ETC_813' and kind=='historical_overloaded' and data.get('amount',0)>0:improve(game,owner)
 operation=None
 if cid=='ETC_521' and kind=='spell_cast':operation=('historical_growing_weapon_keyboard',uid,max(0,data['cost']))
 elif cid=='ETC_312' and kind=='hero_power_used':operation=('historical_growing_weapon_wear',uid)
 elif cid=='WW_347' and kind=='minion_played':
  minion=game._force_live(data.get('source'))
  if minion is not None and 'TAUNT' in game._effective_keywords(minion):operation=('historical_growing_weapon_durability',uid)
 if operation:game._rule_events.append(('captured_effects',dict(operations=(operation,),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid)),[]))


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_growing_weapon_death':
  count=1+ctx.get('broken_weapon',{}).get(KEY,getattr(ctx.get('broken_weapon_card'),'rule_state',{}).get(KEY,0))
  cid=op[1]
  if cid=='ETC_317':game._effect(('buff_random_friendly',count,count),ctx)
  elif cid=='ETC_405':game._effect(('draw',count),ctx)
  elif cid=='ETC_518':game._effect(('refresh_mana',count),ctx)
  elif cid=='ETC_520':game._effect(('area_damage','all_minions',count),ctx)
  elif cid=='ETC_388':
   for _ in range(count):game._summon(owner,'ETC_387bt',entry_origin='deathrattle',entry_site='timber_tambourine')
  elif cid=='ETC_423':game._summon(owner,'ETC_423t',entry_stats=(count,count),entry_origin='deathrattle',entry_site='arcanite_ripper')
  elif cid=='ETC_813':p.cost_effects.append(dict(selector='SPELL',amount=count,remaining_uses=1,expires=None))
  elif cid=='ETC_832':
   values=game._generation_created_candidates(pool(card_type='MINION',tribe='BEAST',minimum=count,maximum=count),ctx)
   if values:game._summon(owner,game.rng.choice(values),entry_origin='deathrattle',entry_site='jungle_jammer')
 elif name=='historical_growing_weapon_axe':
  for minion in tuple(p.minions):
   if minion.health>0 and minion.health<minion.max_health:game._buff(minion,op[1],op[2])
 elif name in ('historical_growing_weapon_keyboard','historical_growing_weapon_wear','historical_growing_weapon_durability'):
  if p.weapon is None or getattr(p.equipped_card,'uid',None)!=op[1]:return True
  if name=='historical_growing_weapon_durability':game._buff_weapon(owner,0,1)
  else:
   if name=='historical_growing_weapon_keyboard':game._summon(owner,'ETC_521t',entry_stats=(op[2],op[2]),entry_origin='effect',entry_site='cosmic_keyboard')
   if p.weapon is not None and getattr(p.equipped_card,'uid',None)==op[1]:
    from .historical_arsenal_batches import lose_durability
    lose_durability(game,owner,1)
 else:return False
 return True


def hero_health_changed(game,owner):
 if owner==game.current and game.players[owner].weapon is not None and game.players[owner].weapon['card_id']=='ETC_423':improve(game,owner)

WEAPON_TRIGGERS={'REV_933':[('historical_growing_weapon_axe',1,2)],'REV_933t':[('historical_growing_weapon_axe',2,2)]}
