"""Explicit fixed outcomes and physical-zone primitives; review deferred."""
from .historical_saidan import add as _saidan_add
from engine.game import Card
from .selectors import has_tribe,has_school

RULES={
 'AV_136':('none',[('add','AV_136t',2)]),
 'BT_160':('none',[('historical_batch_grant_other_deaths',(('summon','BT_160t',1),))]),
 'BT_214':('none',[('summon_from_zone','hand',(('type','eq','MINION'),('tribe','eq','BEAST')))]*3),
 'DMF_202':('none',[('historical_batch_hand_count_summon','DMF_523t')]),
 'ICC_069':('none',[('add','CS2_027',1)]),
 'OG_122':('none',[('add','EX1_014t',2)]),
 'RLK_548':('none',[('add','RLK_843',1)]),
 'SW_070':('none',[('add','TOKEN_COIN',1)]),
 'TRL_348':('none',[('add','TRL_348t',1)]),
 'WON_013':('none',[('add','WON_013t',2)]),
 'YOD_029':('none',[('summon','YOD_029t',2)]),
 'YOG_403':('none',[('summon','EX1_158t',1)]),
 'GVG_110':('none',[('summon','GVG_110t',2)]),
 'WON_345':('none',[]),
 'CFM_755':('none',[('historical_batch_hand_weapon_buff',1,1)]),
 'TSC_943':('none',[('historical_batch_all_weapon_buff',1,1)]),
 'BOT_038':('historical_friendly_mech',[('buff',1,1),('historical_batch_trigger_target_death',)]),
 'LEG_RLK_079':('enemy_character',[('damage',2),('damage_own_hero',2)]),
 'LEG_CS3_031':('character',[('historical_batch_friendly_heal_enemy_damage',8)]),
 'EX1_590':('none',[('historical_batch_eat_shields',3,3)]),
 'OG_051':('none',[('historical_batch_spend_mana_buff',1,1)]),
 'OG_254':('none',[('historical_batch_eat_secrets',)]),
 'OG_337':('none',[('historical_batch_enemy_count_buff',0,1)]),
 'EX1_304':('none',[('historical_batch_eat_adjacent',)]),
 'GIL_515':('friendly_minion',[('historical_batch_eat_target',)]),
 'UNG_840':('none',[('historical_batch_destroy_cheap_deck',3)]),
 'ICC_701':('none',[('historical_batch_destroy_cost_spells',1)]),
 'MAW_029':('none',[('historical_batch_weapon_buff_or_draw',1,1)]),
 'ICC_912':('none',[('historical_batch_deck_keyword_self',('TAUNT','DIVINE_SHIELD','LIFESTEAL','WINDFURY'))]),
}
DEATH_EFFECTS={
 'DMF_523':[('add','DMF_523t',2)],
 'ETC_321':[('summon','BOT_270t',3)],
 'ICC_065':[('add','ICC_026t',2)],
 'KAR_094':[('add','KAR_094a',1)],
 'LOOT_363':[('add','CS2_101t',3)],
 'LOOT_534':[('add','TOKEN_COIN',1)],
 'REV_952':[('add','CS2_101t',2)],
 'RLK_542':[('add','RLK_843',2)],
 'SCH_707':[('add','SCH_707t',1)],
 'SCH_708':[('add','SCH_708t',1)],
 'SCH_709':[('add','SCH_709t',1)],
 'SW_070':[('add_opponent','TOKEN_COIN',1)],
 'SW_463':[('summon','SW_463t',2)],
 'ULD_250':[('add','ULD_215t',2)],
 'VAC_514':[('summon','VAC_514t',1)],
 'WON_013':[('add','WON_013t',2)],
 'YOG_403':[('summon','EX1_158t',1)],
 'TOY_908':[('summon','GVG_110t',2)],
 'GIL_805':[('summon_from_zone','hand',(('type','eq','MINION'),('mechanic','eq','DEATHRATTLE')))],
 'SW_021':[('summon_from_zone','deck',(('type','eq','MINION'),))],
 'WON_345':[('summon_from_zone','deck',(('type','eq','MINION'),('mechanic','eq','TAUNT')))],
 'WW_440':[('summon_from_zone','deck',(('type','eq','MINION'),('tribe','eq','ELEMENTAL'))),('summon_from_zone','deck',(('type','eq','MINION'),('tribe','eq','BEAST')))],
}
RULES.update({
 'EX1_089':('none',[('historical_batch_opponent_crystal',1)]),
 'BT_717':('character',[('historical_batch_damage_stealth_if_kill',2)]),
 'DRG_213':('none',[('historical_batch_sample_damage','enemy',2,4)]),
 'BOT_104':('none',[('historical_batch_missiles','non_mechs',5)]),
 'BOT_544':('none',[('historical_batch_missiles','friendly_other',6)]),
 'BT_732':('none',[('historical_batch_missiles','all_other',6)]),
 'KAR_095':('none',[('historical_batch_menagerie',1,1)]),
 'KAR_702':('none',[('historical_batch_menagerie',2,2)]),
 'GVG_107':('none',[('historical_batch_random_keywords',('WINDFURY','TAUNT','DIVINE_SHIELD'))]),
 'TOY_370':('none',[('damage_random_enemy',2)]*3),
})
DEATH_EFFECTS.update({
 'AV_102':[('historical_batch_sample_freeze','enemy',2)],
 'DAL_563':[('historical_batch_sample_buff','friendly_other',2,2,2)],
})

for cid in DEATH_EFFECTS:RULES.setdefault(cid,('none',[]))
TOKEN_RULES={cid:('none',[]) for cid in ('BT_160t','DMF_523t','KAR_094a','SCH_707t','SCH_708t','SCH_709t','SW_463t','TRL_348t','ULD_215t','VAC_514t','WON_013t','YOD_029t')}
TOKEN_RULES.update({
 'AV_136t':('minion',[('buff',0,2)]),
 'RLK_843':('character',[('historical_batch_manathirst_damage',8,2,3)]),
 'GVG_110t':('none',[]),
})
DEATH_EFFECTS['GVG_110t']=[('historical_batch_random_enemy_damage',1,4)]
RULES.update({
 'BAR_329':('none',[('summon_from_zone','deck',(('type','eq','MINION'),('mechanic','eq','DEATHRATTLE'),('cost','le',5)))]*3),
 'YOD_028':('none',[('summon_from_zone','deck',(('type','eq','MINION'),('cost','eq',1)))]),
 'BAR_307':('none',[('historical_batch_count_missiles','spells_hand','enemy_minions',1,0)]),
 'BOT_601':('none',[('historical_batch_count_missiles','hand','enemies',1,0)]),
 'DED_007':('none',[('historical_batch_count_missiles','beasts','enemies',2,1)]),
})
DEATH_EFFECTS.update({
 'BAR_325':[('summon_from_zone','hand',(('type','eq','MINION'),('mechanic','eq','DEATHRATTLE'),('cost','le',3)))],
 'BAR_326':[('summon_from_zone','hand',(('type','eq','MINION'),('mechanic','eq','DEATHRATTLE'),('cost','le',4)))],
 'BOT_267':[('summon_from_zone','hand',(('type','eq','MINION'),('cost','le',2)))],
 'WW_809':[('historic_when',('source_attack',4),(('summon','WW_809',1),))],
})
for cid in DEATH_EFFECTS:RULES.setdefault(cid,('none',[]))
RULES.update({
 'LOOT_375':('none',[('summon_from_zone','deck',(('type','eq','MINION'),('cost','le',4)))]),
 'ONY_009':('none',[('summon_from_zone','deck',(('type','eq','MINION'),('tribe','eq','BEAST'),('cost','le',5)))]),
 'LOOT_511':('none',[('summon_from_zone','deck',(('type','eq','MINION'),('tribe','eq','BEAST')))]),
 'LOOT_521':('none',[('summon_from_zone','deck',(('type','eq','MINION'),('attack','eq',attack))) for attack in (1,2,3)]),
 'AT_058':('none',[('historical_batch_joust','MINION',True,())]),
 'AT_104':('none',[('historical_batch_joust','MINION',False,(('heal_own_hero',7),))]),
 'AT_108':('none',[('historical_batch_joust','MINION',False,(('keyword_self','CHARGE'),))]),
 'AT_112':('none',[('historical_batch_joust','MINION',False,(('keyword_self','TAUNT'),('keyword_self','DIVINE_SHIELD')))]),
 'AT_133':('none',[('historical_batch_joust','MINION',False,(('buff_self',1,1),))]),
 'LOOT_170':('none',[('historical_batch_joust','SPELL',True,())]),
})
DEATH_EFFECTS.update({
 'LOOT_184':[('summon_from_zone','deck',(('type','eq','MINION'),('cost','eq',8)))],
 'LOOT_306':[('summon_from_zone','deck',(('type','eq','MINION'),('tribe','eq','DEMON')))],
 'LOOT_314':[('summon_from_zone','deck',(('type','eq','MINION'),('cost','le',4)))]*2,
 'LOOT_511':RULES['LOOT_511'][1],
})
for cid in DEATH_EFFECTS:RULES.setdefault(cid,('none',[]))
from .generation_cards import pool,random_cards
RULES.update({
 'NX2_021':('none',[('historical_batch_mana_branch',7,(('heal_own_hero',5),),(('damage_own_hero',5),))]),
 'RLK_219':('none',[('historical_batch_mana_branch',6,(('historical_batch_heal_friendly_characters',6),),(('historical_batch_heal_friendly_characters',3),))]),
 'RLK_951':('enemy_minion',[('historical_batch_mana_branch',6,(('silence',),('freeze',)),(('freeze',),))]),
 'RLK_221':('none',[('historical_batch_mana_branch',10,(random_cards(pool(card_type='MINION',minimum=8,maximum=8),destination='board'),),(('historic_when',('mana_at_least',5),(random_cards(pool(card_type='MINION',minimum=3,maximum=3),destination='board'),)),))]),
 'ONY_024':('enemy_minion',[('historical_batch_armor_damage',)]),
 'BOT_424':('none',[]),
})
DEATH_EFFECTS['BOT_424']=[('historical_batch_empty_zones_destroy',)]
# Literal deaths and source-stat recipes keep their ordinary operation checkpoints.
DEATH_EFFECTS.update({
 'CFM_316':[('historical_batch_attack_summons','CFM_316t')],
 'CFM_759':[('historic_when',('source_attack',2),(('draw',1),))],
 'DAL_749':[('historic_when',('source_attack',4),(('summon','DAL_749',1),))],
 'DED_522':[('equip','DED_522t')],
 'DMF_085':[('damage_random_enemy',2)]*4,
 'DRG_071':[('historical_batch_shuffle_literal','DRG_071t',2,True)],
 'FP1_029':[('historical_batch_other_draw',1)],
 'UNG_086':[('summon_from_zone','hand',(('type','eq','MINION'),('attack','ge',5)))],
 'UNG_914':[('historical_prime_shuffle','UNG_914t1')],
 'UNG_957':[('historical_prime_shuffle','UNG_957t1')],
 'VAC_943':[('historical_batch_current_summon','VAC_943t')],
 'YOG_500':[('historical_batch_armor_resummon',4,'YOG_500')],
 'YOG_523':[('add','YOG_514',2)],
})
RULES['YOG_500']=('none',[('armor',4)])
END_EFFECTS={
 'CS2_059':[('buff_random_other',0,1)],
 'DEEP_023':[('historical_batch_heal_friendly_characters',2)],
 'ULD_215':[('summon','ULD_215t',1)],
 'YOG_517':[('add','YOG_514',1)],
}
for cid in DEATH_EFFECTS.keys()|END_EFFECTS.keys():RULES.setdefault(cid,('none',[]))
TOKEN_RULES.update({cid:('none',[]) for cid in ('CFM_316t','DED_522t','DRG_071t','UNG_914t1','UNG_957t1','VAC_943t','ULD_215t')})
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
DAMAGE_FREEZERS=frozenset(('YOD_029t',))


def split(game,op,ctx):
 if op[0]=='historical_batch_attack_summons':
  source=ctx.get('source');count=max(0,source.attack) if source is not None else 0
  return game._split_fixed_summon(('summon',op[1],count),ctx)
 if op[0]=='historical_batch_mana_branch':
  operations=op[2] if game.players[ctx['owner']].max_mana>=op[1] else op[3]
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+tuple(operations[1:])
 if op[0]=='historical_batch_joust':
  owner=ctx['owner'];revealed=[]
  for player_id in (owner,1-owner):
   player=game.players[player_id];indices=[i for i,c in enumerate(player.deck) if game._card_data(c)['type']==op[1]]
   index=game.rng.choice(indices) if indices else None
   revealed.append(index)
   if index is not None:game._log('joust_reveal',player=player_id,card=game._card_data(player.deck[index])['id'])
  own,other=revealed
  won=own is not None and (other is None or game._card_stat(game.players[owner].deck[own],'cost',owner)>game._card_stat(game.players[1-owner].deck[other],'cost',1-owner))
  if not won:return ('batch30_noop',),()
  operations=(('historical_batch_joust_draw',own),) if op[2] else tuple(op[3])
  return operations[0],operations[1:]
 if op[0]=='historical_batch_count_missiles':
  p=game.players[ctx['owner']]
  count=len(p.hand) if op[1]=='hand' else sum(game._card_data(c)['type']=='SPELL' for c in p.hand) if op[1]=='spells_hand' else sum(has_tribe(game._card_data(m),'BEAST') for m in p.minions if m is not ctx.get('source'))
  return split(game,('historical_batch_count_shots',op[2],count+op[4],op[3]),ctx)
 if op[0]=='historical_batch_count_shots':
  if op[2]<=0:return ('batch30_noop',),()
  first=('damage_random_enemy_minion' if op[1]=='enemy_minions' else 'damage_random_enemy',op[3])
  return first, (('historical_batch_count_shots',op[1],op[2]-1,op[3]),) if op[2]>1 else ()
 if op[0]=='historical_batch_missiles':
  if op[2]<=0:return ('batch30_noop',),()
  return ('historical_batch_missile_one',op[1]),(('historical_batch_missiles',op[1],op[2]-1),) if op[2]>1 else ()
 if op[0]=='historical_batch_hand_count_summon':
  count=sum(game._card_data(c)['type']=='MINION' for c in game.players[ctx['owner']].hand)
  return game._split_fixed_summon(('summon',op[1],count),ctx)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_batch_') and name!='historical_union_discover':return False
 owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner];source=ctx.get('source');target_id=ctx.get('target',0)
 if name=='historical_batch_shuffle_literal':
  from engine.game import Card
  from .pools import require_fixed_cards
  require_fixed_cards((op[1],),game.cards)
  recipient=1-owner if op[3] else owner;deck=game.players[recipient].deck
  cards=[Card(game._new_id(),op[1]) for _ in range(op[2])]
  for card in cards:deck.insert(game.rng.randrange(len(deck)+1),card)
  game._record_deck_insertion(recipient,owner,op[2],'shuffle',cards=cards)
 elif name=='historical_batch_other_draw':game._draw(1-owner)
 elif name=='historical_batch_current_summon':
  if game.current==owner:game._summon(owner,op[1])
 elif name=='historical_batch_armor_resummon':
  if p.armor>=op[1]:
   p.armor-=op[1];game._summon(owner,op[2])
 elif name=='historical_batch_attack_summons':
  if source is not None:game._effect(('summon',op[1],max(0,source.attack)),ctx)
 elif name=='historical_batch_empty_zones_destroy':
  if not p.deck and not p.hand and not p.board:q.health=0
 elif name=='historical_batch_armor_damage':game._deal_effect(target_id,p.armor,ctx)
 elif name=='historical_batch_heal_friendly_characters':
  for uid in [game.hero_id(owner)]+[m.uid for m in p.minions]:game._heal(uid,op[1],healer=owner,spell=ctx.get('spell',False))
 elif name=='historical_batch_joust_draw':game._take_deck_draw(owner,op[1],include_burned=True)
 elif name=='historical_union_discover':
  from engine.cards import UnsupportedCard
  values=[]
  for request in op[1]:values.extend(game._generation_discover_candidates(request,ctx))
  values=tuple(sorted(set(values)))
  if values:
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite a pending choice')
   options=game.rng.sample(values,min(3,len(values)))
   game._generation_choice_context=dict(context=dict(ctx),destination='hand',modifiers=())
   game.pending_choice=dict(owner=owner,kind='generation_discover',options=[dict(card_id=cid) for cid in options]);game.phase='choice'
 elif name=='historical_batch_grant_other_deaths':
  from copy import deepcopy
  for m in p.minions:
   if m is not source:m.attached_death_effects.extend(deepcopy(op[1]))
 elif name=='historical_batch_trigger_target_death':
  target=next((m for player in game.players for m in player.minions if m.uid==target_id and m.health>0),None)
  if target is not None:
   operations=game._death_operations(target)
   if operations:game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=target.owner,source=target,target=0,bonus=0,lifesteal=False,
    death_position=game.players[target.owner].board.index(target)+1)),[]))
 elif name=='historical_batch_manathirst_damage':game._deal_effect(target_id,op[3] if p.max_mana>=op[1] else op[2],ctx)
 elif name=='historical_batch_random_enemy_damage':
  targets=[game.hero_id(1-owner)]+[m.uid for m in q.minions if m.health>0]
  if targets:game._deal_effect(game.rng.choice(targets),game.rng.randint(op[1],op[2]),ctx)
 elif name in ('historical_batch_sample_damage','historical_batch_sample_freeze','historical_batch_sample_buff'):
  from .historical_board_primitives import selected
  values=selected(game,op[1],ctx);victims=game.rng.sample(values,min(op[2],len(values)))
  if name=='historical_batch_sample_damage':
   with game._damage_batch():
    for victim in victims:game._deal_effect(victim.uid,op[3],ctx)
  elif name=='historical_batch_sample_freeze':
   for victim in victims:game._freeze(victim.uid)
  else:
   for victim in victims:game._buff(victim,op[3],op[4])
 elif name=='historical_batch_missile_one':
  from .historical_board_primitives import selected
  values=[m for m in selected(game,op[1],ctx) if m.health>0]
  if values:game._deal_effect(game.rng.choice(values).uid,1,ctx)
 elif name=='historical_batch_menagerie':
  for tribe in ('BEAST','DRAGON','MURLOC'):
   values=[m for m in p.minions if m is not source and m.health>0 and has_tribe(game._card_data(m),tribe)]
   if values:game._buff(game.rng.choice(values),op[1],op[2])
 elif name=='historical_batch_random_keywords':
  for m in p.minions:
   if m is not source and m.health>0:m.keywords.add(game.rng.choice(op[1]))
 elif name=='historical_batch_opponent_crystal':
  gain=min(op[1],max(0,q.mana_capacity-q.max_mana));q.max_mana+=gain;q.mana=min(q.max_mana,q.mana+gain)
 elif name=='historical_batch_damage_stealth_if_kill':
  if target_id:
   victim=game._find(target_id) if target_id>0 else None
   game._deal_effect(target_id,op[1],ctx)
   if victim is not None and victim.health<=0 and source is not None:source.keywords.add('STEALTH')
 elif name=='historical_batch_hand_weapon_buff':
  choices=[c for c in p.hand if game._card_data(c)['type']=='WEAPON']
  if choices:
   card=game.rng.choice(choices);_saidan_add(card,'attack_bonus',op[1]);_saidan_add(card,'health_bonus',op[2])
 elif name=='historical_batch_all_weapon_buff':
  for zone in ('hand','deck'):
   values=getattr(p,zone)
   for i,value in enumerate(values):
    if game._card_data(value)['type']=='WEAPON':
     card=value if isinstance(value,Card) else Card(game._new_id(),value)
     _saidan_add(card,'attack_bonus',op[1]);_saidan_add(card,'health_bonus',op[2]);values[i]=card
  game._buff_weapon(owner,attack=op[1],durability=op[2])
 elif name=='historical_batch_friendly_heal_enemy_damage':
  if target_id:
   target_owner=-target_id-1 if target_id<0 else game._find(target_id).owner
   if target_owner==owner:game._heal(target_id,op[1],healer=owner,spell=ctx.get('spell',False))
   else:game._deal_effect(target_id,op[1],ctx)
 elif name=='historical_batch_eat_shields':
  count=0
  for player in game.players:
   for m in player.minions:
    if 'DIVINE_SHIELD' in game._effective_keywords(m):
     m.keywords.discard('DIVINE_SHIELD');m.temporary_keywords[:]=[x for x in m.temporary_keywords if x['keyword']!='DIVINE_SHIELD'];count+=1
     game._queue_event('shield_lost',owner=m.owner,target=m.uid)
  if source is not None:game._buff(source,op[1]*count,op[2]*count)
 elif name=='historical_batch_spend_mana_buff':
  amount=p.mana;p.mana=0;game._b60_spend_mana(owner,amount)
  if source is not None:game._buff(source,op[1]*amount,op[2]*amount)
 elif name=='historical_batch_eat_secrets':
  count=len(q.secrets)
  for secret in list(q.secrets):game._reveal_secret(1-owner,secret)
  if source is not None:game._buff(source,count,count)
 elif name=='historical_batch_enemy_count_buff':
  if source is not None:game._buff(source,len(q.minions)*op[1],len(q.minions)*op[2])
 elif name=='historical_batch_eat_adjacent':
  from .historical_board_primitives import selected
  values=selected(game,'adjacent',ctx);attack=sum(m.attack for m in values);health=sum(m.health for m in values)
  for m in values:
   if not game._fire_immune_target(m.uid,ctx):m.health=0
  if source is not None:game._buff(source,attack,health)
 elif name=='historical_batch_eat_target':
  victim=next((m for player in game.players for m in player.minions if m.uid==target_id and m.health>0),None)
  if victim is not None and not game._fire_immune_target(victim.uid,ctx):
   attack,health=victim.attack,victim.health;victim.health=0
   if source is not None:game._buff(source,attack,health)
 elif name=='historical_batch_destroy_cheap_deck':
  p.deck[:]=[c for c in p.deck if game._card_stat(c,'cost',owner)>op[1]]
 elif name=='historical_batch_destroy_cost_spells':
  for recipient,player in enumerate(game.players):
   for zone in ('hand','deck'):
    values=getattr(player,zone)
    values[:]=[c for c in values if not(game._card_data(c)['type']=='SPELL' and game._card_stat(c,'cost',recipient)==op[1])]
 elif name=='historical_batch_weapon_buff_or_draw':
  if p.weapon:game._buff_weapon(owner,attack=op[1],durability=op[2])
  else:game._draw_filtered(owner,(('type','eq','WEAPON'),))
 elif name=='historical_batch_deck_keyword_self':
  if source is not None:
   for keyword in op[1]:
    if any(game._card_data(c)['type']=='MINION' and keyword in game._card_mechanics(c) for c in p.deck):source.keywords.add(keyword)
 else:return False
 return True
