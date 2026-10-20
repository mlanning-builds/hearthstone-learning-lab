"""Historical Paladin weapon programs with physical equipped-instance guards."""
from copy import deepcopy
from .generation_cards import pool
from .historical_saidan import add as add_stat
MAULS=tuple('LOOT_286t'+str(i) for i in range(1,5))
TOKEN_RULES={
 'AT_077':('none',[('historical_batch_joust','MINION',False,(('weapon_buff',0,1),))]),
 'AV_341':('none',[]),'BAR_875':('none',[]),'BT_018':('none',[]),
 'DAL_571':('none',[('historical_utility_weapon_mystery',)]),
 'EX1_366':('none',[]),
 'GDB_726':('none',[('historical_family_libram_discount',1)]),
 'GIL_596':('none',[]),'ICC_071':('none',[]),'LOOT_286':('none',[]),
 'LOOT_500':('none',[]),'OG_222':('none',[('historical_utility_weapon_rally',)]),
 'SCH_523':('none',[]),'SCH_523t':('none',[]),'SW_048':('none',[]),
 'SW_314':('none',[]),'TRL_304':('none',[]),
 'TRL_543':('none',[('damage_own_hero',5)]),'VAC_921':('none',[]),
 'WC_032':('none',[]),
 'VAC_917t':('minion',[('buff',1,2)]),
 'LOOT_286t1':('none',[('summon','CS2_101t',2)]),
 'LOOT_286t2':('none',[('board_keyword','TAUNT')]),
 'LOOT_286t3':('none',[('board_buff',1,0)]),
 'LOOT_286t4':('none',[('board_keyword','DIVINE_SHIELD')]),
}
DEATH_EFFECTS={
 'AV_341':[('historical_utility_weapon_horn',)],
 'GDB_726':[('historical_family_libram_discount',1)],
 'LOOT_500':[('historical_utility_weapon_valanyr',)],
 'WC_032':[('board_keyword','DIVINE_SHIELD')],
}
WEAPON_TRIGGERS={
 'BAR_875':[('historical_utility_weapon_sword',)],
 'BT_018':[('historical_utility_weapon_rod',)],
 'GIL_596':[('board_buff',1,1)],
 'TRL_304':[('historical_utility_weapon_farraki',)],
 'VAC_921':[('add','VAC_917t',1)],
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def identify(game,card):
 if card.card_id=='LOOT_286':
  from .pools import require_fixed_cards
  require_fixed_cards(MAULS,game.cards)
  card.card_id=game.rng.choice(MAULS)

def snapshot_spell(game,card,owner):
 p=game.players[owner]
 if p.weapon and p.weapon['card_id']=='SCH_523' and not p.weapon.get('historical_spellburst_used'):
  card._historical_maul_uid=p.equipped_card.uid

def summoned(game,minion):
 p=game.players[minion.owner]
 if p.weapon and p.weapon['card_id']=='EX1_366' and minion.health>0 and not minion.dormant:
  game._buff(minion,1,1)
  from .historical_arsenal_batches import lose_durability
  lose_durability(game,minion.owner,1)

def event(game,kind,data):
 owner=data.get('owner')
 if owner not in (0,1):return
 p=game.players[owner];weapon=p.weapon
 if weapon is None:return
 cid=weapon['card_id'];uid=getattr(p.equipped_card,'uid',None)
 op=None
 if kind=='shield_lost' and data.get('target',0)>0:
  if cid=='ICC_071':op=('historical_utility_weapon_shield',uid,False)
  elif cid=='SW_048':op=('historical_utility_weapon_shield',uid,True)
 if kind=='spell_cast' and cid=='SCH_523' and not weapon.get('historical_spellburst_used') and getattr(data.get('physical_card'),'_historical_maul_uid',None)==uid:
  weapon['historical_spellburst_used']=True
  op=('historical_utility_weapon_student',max(0,data['cost']))
 if op:game._rule_events.append(('captured_effects',dict(operations=(op,),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid)),[]))

def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_utility_weapon_mystery':
  if p.secrets:game._buff_weapon(owner,1,0)
 elif name=='historical_utility_weapon_rally':
  for m in p.minions:
   if 'DIVINE_SHIELD' in game._effective_keywords(m):game._buff(m,1,1)
 elif name=='historical_utility_weapon_horn':
  candidates=[c for c in p.hand if game._card_data(c)['type']=='MINION']
  if candidates:
   lowest=min(game._cost(c,owner) for c in candidates);card=game.rng.choice([c for c in candidates if game._cost(c,owner)==lowest])
   if len(p.board)<7:
    p.hand.remove(card);game._summon(owner,card.card_id,entry_source=card,entry_zone='hand',entry_origin='effect',entry_site='cavalry_horn')
 elif name=='historical_utility_weapon_valanyr':
  candidates=[c for c in p.hand if game._card_data(c)['type']=='MINION']
  if candidates:
   c=game.rng.choice(candidates);add_stat(c,'attack_bonus',4);add_stat(c,'health_bonus',2)
   state=game._b60_state(c);state.setdefault('historical_granted_deaths',[]).append(('historical_utility_weapon_reequip',))
 elif name=='historical_utility_weapon_reequip':game._equip(owner,'LOOT_500')
 elif name=='historical_utility_weapon_sword':
  candidates=[c for c in p.deck if game._card_data(c)['type']=='SPELL' and 'SECRET' in game._card_data(c).get('mechanics',())]
  if candidates:
   c=game.rng.choice(candidates)
   if isinstance(c,str):
    from engine.game import Card
    i=p.deck.index(c);c=Card(game._new_id(),c);p.deck[i]=c
   game._rule_events.append(('captured_effects',dict(operations=(('cast_zone_spell','deck',c.uid,'random'),),context=dict(ctx)),[]))
 elif name=='historical_utility_weapon_rod':
  ids=game._generation_candidates(pool(card_type='MINION',tribe='MURLOC'),owner)
  if ids:game._generation_place(game.rng.choice(ids),'hand',(),ctx)
 elif name=='historical_utility_weapon_farraki':
  if ctx.get('attack_killed') and ctx.get('attack_target_health_after',0)<0:
   candidates=[c for c in p.hand if game._card_data(c)['type']=='MINION']
   if candidates:
    c=game.rng.choice(candidates);add_stat(c,'attack_bonus',2);add_stat(c,'health_bonus',2)
 elif name=='historical_utility_weapon_shield':
  if p.weapon and getattr(p.equipped_card,'uid',None)==op[1]:
   if op[2]:
    for c in p.hand:
     if game._card_data(c)['type']=='MINION':add_stat(c,'attack_bonus',1);add_stat(c,'health_bonus',1)
    from .historical_arsenal_batches import lose_durability
    lose_durability(game,owner,1)
   else:game._buff_weapon(owner,1,0)
 elif name=='historical_utility_weapon_student':
  from engine.game import Card
  card=Card(game._new_id(),'SCH_523t');card.set_cost=op[1];card.base_stat_override=(op[1],op[1]);card._historical_student_definition=dict(attack=op[1],health=op[1],cost=op[1])
  game._summon(owner,'SCH_523t',entry_source=card,entry_origin='effect',entry_site='ceremonial_maul')
 else:return False
 return True
