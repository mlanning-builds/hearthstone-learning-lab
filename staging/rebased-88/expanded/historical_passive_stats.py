"""Explicit frozen historical continuous stat and cost rules.

Table entries are complete intrinsic recipes; selectors inspect live zones.
No historical generation membership is changed here.
"""
from .selectors import has_tribe,has_school,has_class
AURAS={'CS2_122':('others',1,0),'CS2_222':('others',1,1),
 'EX1_162':('adjacent',1,0),'EX1_565':('adjacent',2,0),
 'EX1_507':('MURLOC',2,0),'NEW1_027':('PIRATE',1,1)}
CONDITIONAL_ATTACK={
 'EX1_009':('damaged',5),'EX1_390':('damaged',3),'EX1_393':('damaged',3),
 'EX1_414':('damaged',6),'GVG_051':('damaged',1),'GIL_155':('damaged',3),
 'OG_150':('damaged',2),'OG_218':('damaged',3),'TRL_406':('damaged',4),
 'ULD_185':('damaged',2),'UNG_049':('enemy_turn',3),
 'UNG_838':('enemy_turn',4),'UNG_928':('enemy_turn',2),
 'TOY_000':('enemy_turn',2),'CFM_325':('weapon',2),'WON_351':('weapon',2)}
DYNAMIC_ATTACK={'REV_242':('imps',1),'MIS_710':('hero_attack',1),'BT_730':('full_health',2),'DAL_551':('alone',2),
 'DRG_058':('hand_dragons',2),'DRG_088':('other_ravens',3),
 'DRG_216':('overloaded',1),'GVG_013':('mech',2),
 'GVG_046':('other_beasts',1),'WON_162':('other_beasts',1),
 'GVG_095':('enemy_hand_six',4),'ICC_841':('discards',1),
 'EX1_062':('all_other_murlocs',1),'TTN_713':('owner_turn',4)}
SELF_COST={'GDB_142':'card_movements','SCH_140':'own_health_changes','VAC_439':'locations_used','LEG_RLK_744':'corpses_spent','WW_025':'elemental_streak','ICC_700':'hero_healed','AT_070':'pirates','AT_120':'power_uses','AV_134':'paid_turn',
 'BRM_009':'deaths_turn','BRM_025':'deaths_turn','BT_138':'damaged',
 'CFM_652':'enemy_three','EX1_105':'other_hand','EX1_586':'all_minions',
 'EX1_620':'missing_health','GVG_121':'enemy_hand','ICC_090':'overloaded_total',
 'NEW1_022':'weapon_attack','RLK_651':'armor','SW_062':'other_hand',
 'TRL_515':'enemy_minions','ULD_169':'all_minions','WW_366':'other_hand'}
# selector, recipient relative to source, additive delta, lower bound
COST_AURAS={'BOT_566':('DEATHRATTLE','own',-3,0),'WW_091':('FEL','own',-2,0),'BT_309':('DEMON','own',-1,0),'CS2_227':('MINION','own',3,0),'UNG_085':('MINION','own',2,0),
 'EX1_616':('MINION','both',1,0),'REV_837':('MINION','both',2,0),
 'EX1_315':('MINION','own',-2,1),'EX1_608':('SPELL','own',-1,1),
 'UNG_034':('SPELL','own',-1,1),'DAL_576':('SPELL','own',1,0),
 'ICC_083':('SPELL','enemy',1,0),'ICC_706':('SPELL','both',2,0),
 'WC_040':('SPELL','enemy',2,0),'ULD_214':('ALL','enemy',-1,0),
 'WC_006':('NATURE','own',-2,0)}
# Explicit additional frozen intrinsic costs and ordinary additive auras.
SELF_COST.update({'AV_141t':'low_health_five','AV_265':'friendly_deaths_game',
 'BAR_917':'small_deck_one','WON_308':'secrets_played_twice','CFM_760':'secrets_played_twice','DMF_226':'hero_attack_six_one',
 'GDB_320':'enemy_minions','LOOT_313':'recruits','MAW_020':'paid_turn',
 'MAW_101':'secrets_three','SW_092':'full_hand_one'})
COST_AURAS.update({'GVG_006':('MECHANICAL','own',-1,0),
 'OG_322':('WEAPON','own',-2,0),'DMF_217':('OUTCAST','own',-1,0),
 'RLK_543':('ARCANE','own',-1,0)})
COST_FLOORS={'TTN_924':2}
SPELL_DAMAGE_VALUES={'DAL_576':3}
ATTACK_RESTRICTIONS={
 'AT_109':'inspire_turn','AT_125':'heroes','BT_734':'heroes',
 'BOT_098':'spell_turn','DAL_434':'spell_damage','GIL_156':'damaged',
 'LOOT_048':'armor_three','LOOT_365':'armor_five','OG_034':'hero_attacked',
 'YOP_002':'hero_attacked','SW_057':'hand_eight',
 'BAR_074':'always','BAR_075':'always','BAR_076':'always',
 'EX1_298':'always','GIL_152':'always','TTN_931':'always',
 'SC_023':'always',
}
DYNAMIC_ATTACK['SC_023']=('location',3)
SELF_COST.update({'JAM_030':'deck_size','VAC_950':'ten_mana_one','WC_806':'frozen_enemies_twice'})
# Explicit historical cost consumers. A source's other actions are registered
# separately; a cost declaration never closes any generated outcome pool.
SELF_COST.update({'AT_041':'summoned_beasts','AV_291':'summoned_beasts','WON_003':'summoned_beasts',
 'DMF_060':'spells_cast_game','TRL_408':'spells_cast_game','RLK_213':'outcasts_played',
 'WW_387':'one_cost_plays'})
COST_AURAS.update({'BAR_082':('DEATHRATTLE','own',-1,0),'FP1_017':('BATTLECRY','both',2,0),
 'VAC_463':('foreign','own',-1,0),'BAR_545':('nonstarting','own',-2,1),
 'WW_430':('nonstarting','own',-4,1),'VAC_440':('nonstarting','enemy',2,0)})
COST_SETS={'GDB_448':('BATTLECRY',1),'AT_045':('MINION',1),'WON_012':('MINION',1),'DAL_726':('MURLOC',1),
 'LOE_038':('ALL',5),'KAR_006':('SECRET',0)}
CONDITIONAL_COSTS={'EX1_076':('first_minion',-1,None),'VAC_435':('first_spell',-2,None),
 'DAL_609':('first_spell',0,0),'BT_255':('third_spell',0,1),'REV_021':('third_minion',0,0),
 'BAR_537':('first_taunt',-2,None),'DMF_102':('first_secret',0,1)}
DYNAMIC_ATTACK['TTN_401']=('automatons',1)
DYNAMIC_ATTACK['TTN_844']=('draws_turn',1)
# These zero-action bodies execute through explicit continuous consumers below.
CONTINUOUS_IDS=frozenset(('AT_075','ETC_337','ULD_173','ULD_179','DS1_178','DED_006',
 'WW_435','DAL_742','SCH_538','TOY_102','TSC_007','YOP_035','VAC_527','BOT_039','YOP_012',
 'WW_382','AV_133','CS2_033','LOE_051','CS2_065','UNG_810','DRG_068'))
SELF_COST.update({'DEEP_004':'held_casts','WW_825':'summoned_dragons','VAC_429':'any_frozen_one','ULD_138':'big_spell_turn_zero'})
SELF_COST.update({'MIS_918':'holy_casts_game','MIS_918t':'holy_casts_game'})
COST_AURAS.update({'TSC_635':('NATURE','own',-1,0),'WW_003':('bounty','own',-1,0)})
SELF_COST['DRG_109']='nonstarting_plays'
SELF_COST['JAM_016']='equipped_weapons_twice'
SELF_COST.update({'KAR_711':'spells_cast_game','LOOT_130':'big_spell_turn_zero','SCH_139':'friendly_target_spells','TRL_300':'spell_mana_spent','TSC_829':'spell_mana_spent'})
DYNAMIC_ATTACK.update({'TID_080':('attacking_self',3),'EX1_412':('damaged_self',1),'REV_930':('damaged_self',2)})
SELF_COST.update({'AV_135':'enemy_turn_damage_five','AV_298':'nonrogue_hand_additions','DMF_528':'board_unique_types','SW_037':'draws_this_turn','TID_077':'paladin_plays','TOY_530':'draws_game','TTN_462':'own_turn_damage_total','VAC_418':'own_turn_damage_events','YOD_032':'enemy_hero_damage_this_turn','WW_373':'all_deaths_game','GDB_341':'adjacent_plays_held'})
SELF_COST['TTN_459']='plagues_shuffled'
RULES={cid:('none',[]) for table in (AURAS,CONDITIONAL_ATTACK,DYNAMIC_ATTACK,SELF_COST,COST_AURAS,COST_FLOORS,ATTACK_RESTRICTIONS,COST_SETS,CONDITIONAL_COSTS) for cid in table}
RULES.update({cid:('none',[]) for cid in CONTINUOUS_IDS})
RULES['GDB_142']=('none',[('historical_copy_ceaseless',)])
SPELL_DAMAGE_VALUES['LOE_051']=0
class HistoricalPassiveStats:
 def _historical_passive_aura_values(self,m):
  if m.card_id=='WON_144':
   from .historical_ritual_batches import totals
   return totals(self,m.owner)
  spec=DYNAMIC_ATTACK.get(m.card_id)
  if spec is None:
   from .forge_intrinsics import damaged_attack
   return (damaged_attack(m),0)
  p=self.players[m.owner];enemy=self.players[1-m.owner];kind,mult=spec
  others=[x for x in p.minions if x.uid!=m.uid and x.health>0]
  if kind=='draws_turn':
   state=getattr(p,'historical_draw_turn',{});n=state.get('count',0) if state.get('turn')==self.turn else 0
  elif kind=='automatons':
   n=max(0,getattr(p,'historical_summoned_ids',{}).get('TTN_401',0)-1)
   return (n,n)
  if kind=='hero_attack':n=self._hero_attack(m.owner)
  elif kind=='imps':
   from .historical_imps import is_imp
   n=sum(is_imp(self,value) for value in p.minions if value.health>0)
  elif kind=='location':n=int(bool(p.locations))
  elif kind=='full_health':n=int(m.health==m.max_health)
  elif kind=='alone':n=int(not others)
  elif kind=='hand_dragons':n=sum(has_tribe(self._card_data(c),'DRAGON') for c in p.hand)
  elif kind=='other_ravens':n=sum(x.card_id=='DRG_088' for x in others)
  elif kind=='overloaded':n=int(bool(p.locked_mana or p.overload_next))
  elif kind=='mech':n=int(any(has_tribe(self._card_data(x),'MECHANICAL') for x in p.minions))
  elif kind=='other_beasts':n=sum(has_tribe(self._card_data(x),'BEAST') for x in others)
  elif kind=='enemy_hand_six':n=int(len(enemy.hand)>=6)
  elif kind=='discards':n=len(p.discard_history)
  elif kind=='all_other_murlocs':n=sum(x.uid!=m.uid and has_tribe(self._card_data(x),'MURLOC') for player in self.players for x in player.minions)
  elif kind=='owner_turn':n=int(self.current==m.owner)
  elif kind=='damaged_self':n=int(m.health<m.max_health)
  elif kind=='attacking_self':n=int(any(window['source']==m.uid for window in getattr(self,'_attack_windows',())))
  return (n*mult,0)
 def _historical_intrinsic_cost(self,card,owner,cost):
  p=self.players[owner];enemy=self.players[1-owner];kind=SELF_COST.get(card.card_id)
  from .historical_copy_batches import PROTOSS_MINIONS
  if card.card_id in PROTOSS_MINIONS:cost-=getattr(p,'historical_protoss_discount',0)

  all_minions=[m for player in self.players for m in player.minions]
  if kind=='card_movements':cost-=sum(getattr(self,'historical_card_movements',{}).values())
  elif kind=='corpses_spent':cost-=getattr(p,'historical_corpses_spent',0)
  elif kind=='elemental_streak':
   from .historical_copy_batches import elemental_streak
   cost-=elemental_streak(self,owner)
  elif kind=='plagues_shuffled':cost-=getattr(p,'historical_plagues_shuffled',0)
  elif kind=='enemy_turn_damage_five':
   state=getattr(p,'historical_opponent_turn_damage',{})
   if state.get('turn')==(self.turn if self.current!=owner else self.turn-1) and state.get('amount',0)>=5:cost=1
  elif kind=='nonrogue_hand_additions':cost-=getattr(p,'historical_nonrogue_hand_additions',0)
  elif kind=='board_unique_types':
   from .quest_families import maximum_tribe_matching
   from .selectors import effective_tribes,TRIBES
   plays=[set(TRIBES)-{'ALL'} if 'ALL' in effective_tribes(self._card_data(m)) else set(effective_tribes(self._card_data(m))) for m in p.minions if m.health>0]
   cost-=len(maximum_tribe_matching(plays))
  elif kind=='draws_this_turn':
   state=getattr(p,'historical_draw_turn',{});cost-=state.get('count',0) if state.get('turn')==self.turn else 0
  elif kind=='paladin_plays':cost-=sum(has_class(self.cards[row['card_id']],'PALADIN') for row in p.played_history)
  elif kind=='draws_game':cost-=getattr(p,'historical_drawn_total',0)
  elif kind=='own_turn_damage_total':cost-=getattr(p,'historical_own_turn_damage_total',0)
  elif kind=='own_turn_damage_events':cost-=getattr(p,'historical_own_turn_damage_events',0)
  elif kind=='enemy_hero_damage_this_turn':
   state=getattr(p,'historical_enemy_hero_damage_turn',{});cost-=state.get('amount',0) if state.get('turn')==self.turn else 0
  elif kind=='all_deaths_game':cost-=sum(len(player.death_records) for player in self.players)
  elif kind=='adjacent_plays_held':cost-=getattr(card,'rule_state',{}).get('historical_adjacent_plays',0)
  elif kind=='summoned_beasts':cost-=getattr(p,'historical_summoned_tribes',{}).get('BEAST',0)
  elif kind=='spells_cast_game':cost-=getattr(p,'historical_spells_cast',0)
  elif kind=='friendly_target_spells':cost-=getattr(p,'historical_friendly_target_spell_count',0)
  elif kind=='spell_mana_spent':cost-=getattr(p,'historical_spell_mana_spent',0)
  elif kind=='equipped_weapons_twice':cost-=2*getattr(p,'historical_equipped_weapons',0)
  elif kind=='nonstarting_plays':cost-=getattr(p,'_nonstarting_plays',0)
  elif kind=='holy_casts_game':cost-=getattr(p,'historical_school_counts',{}).get('HOLY',0)
  elif kind=='held_casts':cost-=getattr(card,'rule_state',{}).get('historical_held_casts',0)
  elif kind=='summoned_dragons':cost-=getattr(p,'historical_summoned_tribes',{}).get('DRAGON',0)
  elif kind=='any_frozen_one' and (any(player.frozen_until>=0 for player in self.players) or any(m.frozen_until>=0 for m in all_minions)):cost=1
  elif kind=='big_spell_turn_zero' and getattr(p,'historical_big_spell_turn',None)==self.turn:cost=0
  elif kind=='outcasts_played':cost-=sum('OUTCAST' in self.cards[h['card_id']].get('mechanics',()) for h in p.played_history)
  elif kind=='one_cost_plays':cost-=sum(h['cost']==1 for h in p.played_history)
  elif kind=='deck_size':cost=len(p.deck)
  elif kind=='ten_mana_one' and p.max_mana>=10:cost=1
  elif kind=='frozen_enemies_twice':cost-=2*(int(enemy.frozen_until>=0)+sum(m.frozen_until>=0 for m in enemy.minions))
  elif kind=='pirates':cost-=sum(has_tribe(self._card_data(m),'PIRATE') for m in p.minions)
  elif kind=='power_uses':cost-=p.hero_power_uses
  elif kind=='paid_turn':cost-=p.cards_played
  elif kind=='deaths_turn':cost-=sum(player.minions_died_turn for player in self.players)
  elif kind=='damaged':cost-=sum(m.health<m.max_health for m in all_minions)
  elif kind=='enemy_three':cost-=2*int(len(enemy.minions)>=3)
  elif kind=='other_hand':cost-=sum(c is not card for c in p.hand)
  elif kind=='all_minions':cost-=len(all_minions)
  elif kind=='missing_health':cost-=p.max_health-p.health
  elif kind=='enemy_hand':cost-=len(enemy.hand)
  elif kind=='overloaded_total':cost-=p.overloaded_total
  elif kind=='weapon_attack':cost-=p.weapon['attack'] if p.weapon else 0
  elif kind=='armor':cost-=p.armor
  elif kind=='enemy_minions':cost-=len(enemy.minions)
  elif kind=='low_health_five' and p.health<=15:cost-=5
  elif kind=='friendly_deaths_game':cost-=len(p.death_records)
  elif kind=='small_deck_one' and len(p.deck)<=10:cost=1
  elif kind=='secrets_played_twice':cost-=2*sum('SECRET' in self.cards.get(h['card_id'],{}).get('mechanics',()) for h in p.played_history)
  elif kind=='hero_attack_six_one' and self._hero_attack(owner)>=6:cost=1
  elif kind=='recruits':cost-=sum(self._card_data(m)['id'] in ('CS2_101t','CORE_CS2_101t') for m in p.minions)
  elif kind=='secrets_three':cost-=3*len(p.secrets)
  elif kind=='full_hand_one' and len(p.hand)>=getattr(p,'hand_capacity',10):cost=1
  elif kind=='own_health_changes':cost-=getattr(p,'historical_own_health_changes',0)
  elif kind=='locations_used':cost-=2*getattr(p,'historical_locations_used',0)
  elif kind=='hero_healed' and p.hero_healed_turn:cost=0
  return cost
 def _historical_cost_aura(self,card,owner,cost):
  from .forge_intrinsics import cost_floor
  data=self._card_data(card);delta=0;floor=0
  from .selectors import has_class
  recipient=self.players[owner]
  if self.current==owner and recipient.cards_played==0 and any(m.card_id=='GIL_800' and not m.silenced and m.health>0 for player in self.players for m in player.minions):cost=0
  turn_counts=getattr(recipient,'historical_cost_turn',{})
  turn_counts=turn_counts if turn_counts.get('turn')==self.turn else {}
  for source in recipient.minions:
   if source.silenced or source.health<=0:continue
   if source.card_id=='NX2_033' and data['cost']%2==source.rule_state.get('historical_thaddius_parity',1):delta-=2
   rule=COST_SETS.get(source.card_id)
   if rule and self._discount_matches({'selector':rule[0]},card):cost=rule[1]
   conditional=CONDITIONAL_COSTS.get(source.card_id)
   if conditional:
    condition,amount,set_cost=conditional
    applicable=(condition=='first_minion' and data['type']=='MINION' and not turn_counts.get('minions',0) or
     condition=='first_spell' and data['type']=='SPELL' and not turn_counts.get('spells',0) or
     condition=='third_spell' and data['type']=='SPELL' and turn_counts.get('spells',0)%3==2 or
     condition=='third_minion' and data['type']=='MINION' and turn_counts.get('minions',0)%3==2 or
     condition=='first_taunt' and data['type']=='MINION' and 'TAUNT' in self._card_mechanics(card) and not turn_counts.get('taunts',0) or
     condition=='first_secret' and 'SECRET' in self._card_mechanics(card) and not turn_counts.get('secrets',0))
    if applicable:
     if set_cost is not None:cost=set_cost
     else:delta+=amount
  for player in self.players:
   for m in player.minions:
    spec=COST_AURAS.get(m.card_id)
    if spec is None or m.silenced or m.health<=0:continue
    selector,scope,amount,minimum=spec
    if scope=='own' and m.owner!=owner or scope=='enemy' and m.owner==owner:continue
    bounty=selector=='bounty' and (data.get('rarity')=='LEGENDARY' or bool({'EXCAVATE','QUICKDRAW','TRADEABLE'} & set(self._card_mechanics(card))))
    special=(selector=='foreign' and not has_class(data,recipient.hero_class) and not has_class(data,'NEUTRAL') or selector=='nonstarting' and not self._started_in_deck(card,owner))
    if bounty or special or selector=='ALL' or selector in self._card_mechanics(card) or selector==data['type'] or selector in ('NATURE','ARCANE','FEL') and has_school(data,selector) or selector in ('MECHANICAL','DEMON') and has_tribe(self._card_data(card),selector) or selector=='OUTCAST' and 'OUTCAST' in self._card_mechanics(card):
     delta+=amount;floor=max(floor,minimum)
  result=max(min(floor,cost),cost+delta)
  # Razorscale is a floor on the final payable cost, including set costs.
  for player in self.players:
   for m in player.minions:
    if not m.silenced and m.health>0:
     result=max(result,COST_FLOORS.get(m.card_id,0),cost_floor(m))
  return result

CLEAVE_IDS=frozenset(('TTN_471','TOY_100','REV_352t','AT_067','CS3_021','DMF_070','GVG_113','JAM_004','LOOT_078'))
RULES.update({cid:('none',[]) for cid in CLEAVE_IDS|{'DMF_087'}})
COST_AURAS['ICC_243']=('DEATHRATTLE','own',-2,0)
RULES['ICC_243']=('none',[])
# Real continuous cost consumer below; no Battlecry operations.
RULES['NX2_033']=('none',[])
# Runtime stat-gain consumers live in historical_saidan and shared setters.
RULES['AV_345']=('none',[])
GENERATED_IDS=frozenset(RULES)


def attack_keywords(game,minion):
 if minion.silenced:return set()
 if minion.health<minion.max_health and minion.card_id in ('EX1_412','REV_930'):return {'WINDFURY'} if minion.card_id=='EX1_412' else {'CHARGE'}
 if minion.card_id=='LOE_107' and sum(len(p.all_minions) for p in game.players)>1:return {'CANT_ATTACK'}
 condition=ATTACK_RESTRICTIONS.get(minion.card_id)
 if condition is None:return set()
 if condition=='heroes':return {'CANT_ATTACK_HERO'}
 p=game.players[minion.owner]
 blocked=(condition=='always' or
  condition=='inspire_turn' and minion.rule_state.get('historical_inspire_attack_turn')!=game.turn or
  condition=='spell_turn' and not p.spells_turn or
  condition=='spell_damage' and game._spell_damage(minion.owner)<=0 or
  condition=='damaged' and minion.health<minion.max_health or
  condition=='armor_three' and p.armor<3 or
  condition=='armor_five' and p.armor<5 or
  condition=='hero_attacked' and p.hero_attacks<=0 or
  condition=='hand_eight' and len(p.hand)<8)
 return {'CANT_ATTACK'} if blocked else set()


def aura_bonuses(game,source):
 p=game.players[source.owner];cid=source.card_id;result=[]
 if cid=='ETC_107':
  uid=source.rule_state.get('historical_bound_aura_target')
  result.extend((m,4,0) for player in game.players for m in player.minions if m.uid==uid and m.health>0)
 for m in p.minions:
  applies=(cid=='AT_075' and game._is_recruit(m.card_id) or
   cid=='ETC_337' and 'DIVINE_SHIELD' in game._effective_keywords(m) or
   cid=='ULD_179' and 'TAUNT' in game._effective_keywords(m) or
   cid=='ULD_173' and m is not source and bool(p.locked_mana or p.overload_next))
  if applies:result.append((m,2,0))
 return result


def continuous_keywords(game,minion,keywords):
 p=game.players[minion.owner];result=set()
 if minion.card_id=='ONY_004' and not minion.silenced:
  from .historical_copy_batches import ONYXIA_WHELPS
  if any(m.health>0 and m.card_id in ONYXIA_WHELPS for m in p.minions):result.add('IMMUNE')
 if minion.card_id=='LOOT_193' and not minion.silenced and game.current!=minion.owner:result.add('ELUSIVE')
 for player in game.players:
  for source in player.minions:
   if not source.silenced and source.health>0 and source.rule_state.get('historical_bound_aura_target')==minion.uid:
    if source.card_id=='ETC_108':result.add('STEALTH')
    if source.card_id=='ETC_109':result.add('CANT_ATTACK')
 if minion.card_id=='CS2_146' and not minion.silenced and p.weapon:result.add('CHARGE')
 if minion.card_id=='VAC_447' and not minion.silenced and not game._started_in_deck(minion,minion.owner):result.add('CHARGE')
 attacking=any(w['source']==minion.uid for w in getattr(game,'_attack_windows',()))
 for source in p.minions:
  if source.silenced or source.health<=0:continue
  cid=source.card_id
  if cid in ('GVG_122','SW_063') and source in p.board and minion in p.board and abs(p.board.index(source)-p.board.index(minion))==1:result.add('ELUSIVE' if cid=='GVG_122' else 'WINDFURY')
  if cid=='REV_014' and minion.card_id!='REV_014':result.add('STEALTH')
  if cid=='AT_075' and game._is_recruit(minion.card_id):result.add('TAUNT')
  if cid=='DS1_178' and has_tribe(game._card_data(minion),'BEAST'):result.add('CHARGE')
  if cid=='DED_006' and has_tribe(game._card_data(minion),'PIRATE'):result.add('CHARGE')
  if cid=='WW_435' and has_tribe(game._card_data(minion),'BEAST'):result.add('RUSH')
  if cid=='DAL_742' and 'WINDFURY' in keywords:result.add('MEGA_WINDFURY')
  if attacking and cid=='SCH_538' and source is not minion:result.add('IMMUNE')
  if attacking and cid=='TOY_102' and source in p.board and minion in p.board and abs(p.board.index(source)-p.board.index(minion))==1:result.add('IMMUNE')
 if not minion.silenced:
  if minion.card_id in ('TSC_007','SW_458t','VAC_410t'):result.add('IMMUNE_WHILE_ATTACKING')
  if minion.card_id in ('WW_382','GVG_111t'):result.add('MEGA_WINDFURY')
 if minion.summoned_turn==game.turn and 'RUSH' in (result|set(keywords)) and any(m.card_id=='TRL_327' and not m.silenced and m.health>0 for m in p.minions):result.add('IMMUNE')
 return result

SPELL_DAMAGE_VALUES['LEG_CS3_001']=2

from .historical_literal_bonus import COST_AURAS as LITERAL_BONUS_COST_AURAS
COST_AURAS.update(LITERAL_BONUS_COST_AURAS)

SELF_COST['UNG_061']='nonrogue_hand_additions'

COST_SETS['CORE_KAR_006']=('SECRET',0)
