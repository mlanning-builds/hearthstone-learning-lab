"""Explicit broad historical spell programs; all additions unvalidated.

Programs are keyed by frozen identities. Shared helpers preserve physical cards,
full generation membership and resumable damage/draw/copy continuations.
"""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,board_pool,random_cards,discover
from .historical_draw_batches import draw
from .historical_resurrection_batches import resurrect
from .historical_damage_spells import follow
from .historical_saidan import add as add_stat
from .selectors import has_tribe,classes
from .discover_offer import DiscoverOffer

def op(name,*args):return ('historical_utility_archive_'+name,)+args
MINION=(('type','eq','MINION'),)
SPELL=(('type','eq','SPELL'),)
WEAPON=(('type','eq','WEAPON'),)
OWN_SPELL=pool(card_type='SPELL',classes='own_or_neutral')
TOKEN_RULES={
 'AT_015':('enemy_minion',[('historical_copy_target_delivery','hand',1,None,None,1,False)]),
 'AT_016':('none',[op('board_stats','swap')]),
 'AT_022':('none',[('damage_random_enemy',4)]),
 'AT_024':('historic_demon',[('buff',3,3)]),
 'AT_025':('none',[op('destroy_sample',2),('discard',2)]),
 'AT_033':('none',[op('opponent_cards',3,'hand',False)]),
 'AT_035':('none',[('on_draw_shuffle','AT_035t',3,1)]),
 'AT_035t':('none',[op('opponent_summon','AT_036t',1)]),
 'AT_056':('minion',[op('neighbors',2)]),
 'AT_061':('none',[op('lock_load')]),
 'AT_068':('none',[('historic_board_buff','friendly_taunts',2,2)]),
 'AT_078':('none',[op('coliseum')]),
 'AV_108':('none',[('area_damage','all_minions',5)]),
 'AV_109':('none',[('armor',10),('schedule_turn_effect','start',1,1,(op('lose_armor',5),))]),
 'AV_147':('none',[('schedule_turn_effect','end',0,3,(draw(SPELL+(('mechanic','eq','SECRET'),),'set_cost',(1,)),))]),
 'AV_213':('none',[op('draw_state','vitality',1)]),
 'AV_224':('minion',[op('hit_follow',3,'spring_trap')]),
 'AV_259':('character',[op('hit_follow',3,'frostbite')]),
 'AV_268':('none',[('schedule_turn_effect','end',0,3,(('summon','AV_257t',1),))]),
 'AV_277':('none',[('on_draw_shuffle','AV_316t4',4,0)]),
 'AV_281':('none',[op('draw_state','felfire',1)]),
 'AV_285':('none',[('missiles','enemy_minions',5),op('repeat_hand','AV_285')]),
 'AV_292':('minion',[('buff',2,2),('tribe_board_buff','BEAST',1,1)]),
 'AV_315':('minion',[op('hit_follow',3,'deliverance')]),
 'AV_322':('damaged_minion',[op('snowed')]),
 'AV_324':('minion',[op('devour')]),
 'AV_329':('minion',[('buff',0,2),op('bless')]),
 'AV_330':('none',[op('naaru')]),
 'AV_338':('minion',[('buff',2,1),('keyword','DIVINE_SHIELD'),('temporary_keyword_target','LIFESTEAL','end')]),
 'AV_360':('none',[('schedule_turn_effect','end',0,3,(('summon','AV_211t',1),))]),
 'AV_657':('none',[('schedule_turn_effect','end',0,3,(op('graveyard'),))]),
 'AV_657t':('none',[]),
 'AV_660':('none',[('schedule_turn_effect','end',0,3,(('area_damage','all_minions',1),))]),
 'AV_664':('none',[('schedule_turn_effect','end',0,3,(('board_buff',0,2),))]),
 'AV_710':('none',[discover(pool(card_type='MINION',mechanic='DEATHRATTLE',classes='other'),cost_delta=-2)]),
 'BAR_032':('minion',[op('piercing')]),
 'BAR_306':('none',[('schedule_turn_effect','start',1,1,(('area_damage','all_minions',3),))]),
 'BAR_308':('minion',[('buff',3,5)]),
 'BAR_705':('none',[('schedule_turn_effect','start',1,1,(op('silence_enemies'),))]),
 'BAR_841':('none',[op('bulk_up')]),
 'BAR_845':('none',[op('sweep_reward',2,'armor')]),
 'BAR_881':('none',[op('sermon')]),
 'BAR_910':('friendly_minion',[('destroy',),('area_damage','enemy_minions',2)]),
 'BAR_911':('none',[op('sweep_reward',5,'burn')]),
 'BAR_913':('none',[op('altar')]),
 'BOT_042':('none',[op('weapons_project')]),
 'BOT_042t':('none',[]),
 'BOT_084':('none',[random_cards(pool(mechanic='DEATHRATTLE'),2)]),
 'BOT_087':('none',[op('opponent_cards',10,'deck',True)]),
 'BOT_099':('none',[op('hand_copy','MINION')]),
 'BOT_219':('minion',[('buff',2,2),('add','BOT_219t',1)]),
 'BOT_219t':('minion',[('buff',2,2)]),
 'BOT_234':('none',[op('board_stats','one')]),
 'BOT_242':('none',[op('myra')]),
 'BOT_263':('none',[op('left_minion')]),
 'BOT_299':('none',[op('omega')]),
 'BOT_402':('none',[op('secret_plan')]),
 'BOT_437':('friendly_minion',[('buff',3,3),('keyword','RUSH'),op('expire_target')]),
 'BOT_438':('none',[op('board_death','mech')]),
 'BOT_508':('friendly_deathrattle',[('historical_batch_trigger_target_death',)]*2),
 'BOT_517':('minion',[op('swap_target')]),
 'BOT_521':('none',[op('ectomancy')]),
 'BOT_529':('friendly_minion',[('historical_mutation_copy_board',5,5,())]),
 'BOT_568':('none',[op('draw_state','soularium',3)]),
 'BOT_909':('none',[('filtered_draw',MINION+(('attack','eq',1),),2)]),
 'BRM_005':('none',[('historic_board_damage','non_demons',2)]),
 'BRM_011':('character',[('damage',2),('unlock_mana',)]),
 'BRM_015':('none',[op('revenge')]),
 'BRM_017':('none',[resurrect()]),
 'BT_113':('minion',[('buff',2,2),op('totemic')]),
 'BT_124':('none',[draw(WEAPON,'buff',(1,1))]),
 'BT_134':('minion',[('damage',3)]),
 'BT_135':('none',[op('glowflies')]),
 'BT_135t':('none',[]),
 'BT_163':('none',[op('attack_group','BT_163t',4)]),
 'BT_163t':('none',[]),
 'BT_199':('enemy_minion',[op('felbolt')]),
 'BT_205':('character',[('damage',3),('historical_hand_buff','BEAST',None,3,3,True)]),
 'BT_213':('none',[draw(MINION+(('tribe','eq','BEAST'),),'buff',(3,3))]),
 'BT_233':('minion',[('damage',2),('armor',2)]),
 'BT_252':('character',[('heal',3),discover(OWN_SPELL)]),
 'BT_300':('none',[('draw',3)]),
 'BT_302':('none',[op('draw_state','portal',1)]),
 'BT_354':('none',[op('blade_dance')]),
 'BT_427':('none',[op('feast')]),
 'BT_488':('historic_friendly_demon',[('historical_mutation_copy_board',None,None,())]),
 'BT_490':('enemy_minion',[('silence',),('outcast_operation',('draw',1))]),
 'BT_514':('none',[('area_damage','all_minions',1),('area_damage','all_minions',1)]),
 'BT_752':('none',[op('immune')]),
 'CFM_630':('none',[('temporary_mana',1)]),
 'CFM_690':('character',[('damage',3),('historical_if_combo',('historical_ritual_jade',False,False))]),
 'CFM_716':('none',[op('fishes')]),
 'CFM_752':('none',[draw(MINION+(('mechanic','eq','TAUNT'),),'buff',(2,2))]),
 'CFM_905':('none',[('filtered_draw',MINION+(('cost','eq',1),),3)]),
 'CFM_940':('none',[discover(pool(card_type='MINION',mechanic='TAUNT',classes='own_or_neutral'),attack=1,health=2)]),
 'CS2_003':('none',[op('mind_vision')]),
 'CS2_038':('minion',[op('board_death','ancestral')]),
 'CS2_061':('character',[('damage',2),('heal_own_hero',2)]),
 'CS2_063':('enemy_minion',[op('corruption')]),
 'CS2_084':('minion',[op('health_one')]),
 'CS2_103':('friendly_minion',[('buff',2,0),('keyword','CHARGE')]),
 'CS2_104':('damaged_minion',[('buff',3,3)]),
 'CS2_236':('minion',[op('divine_spirit')]),
 'CS3_009':('none',[random_cards(pool(card_type=kind,classes='WARRIOR')) for kind in ('MINION','SPELL','WEAPON')]),
 'CS3_029':('none',[op('pursuit')]),
 'DAL_141':('none',[('autocast_random',pool(card_type='SPELL',mechanic='SECRET',classes='PALADIN'),1),('add','DAL_141ts',1)]),
 'DAL_141ts':('none',[('autocast_random',pool(card_type='SPELL',mechanic='SECRET',classes='PALADIN'),1)]),
 'DAL_371':('minion',[('damage',4),discover(OWN_SPELL)]),
 'DAL_373':('character',[('damage',2),('add','DAL_373ts',1)]),
 'DAL_373ts':('character',[('damage',2)]),
 'DAL_568':('friendly_minion',[('keyword','LIFESTEAL'),('add','DAL_568ts',1)]),
 'DAL_568ts':('friendly_minion',[('keyword','LIFESTEAL')]),
 'DAL_589':('none',[op('hunting_party')]),
 'DAL_605':('none',[('tribe_board_buff','DEMON',1,0),('area_damage','enemy_minions',1)]),
 'DAL_710':('none',[op('board_death','murloc')]),
 'DAL_724':('none',[resurrect('all',3)]),
 'DAL_727':('none',[draw(MINION,'buff',(2,2),priority='lowest')]),
 'DAL_728':('none',[op('escape')]),
 'DAL_769':('minion',[follow(1,'alive',op('lackey'))]),
 'DED_506':('none',[('draw',3)]),
 'DED_518':('minion',[op('cannons')]),
 'DMF_054':('none',[draw(MINION)]),
 'DMF_054t':('none',[draw(MINION,'discount',(2,))]),
 'DMF_086':('none',[op('petting')]),
 'DMF_086e':('none',[]),
 'DMF_090':('none',[('historical_hand_buff','BEAST',None,1,1,False)]),
 'DMF_090t':('none',[('historical_hand_buff','BEAST',None,2,2,False)]),
 'DMF_113':('none',[op('free_admission')]),
 'DMF_117':('none',[op('destroy_sample',1)]),
 'DMF_117t':('none',[op('destroy_sample',2)]),
 'DMF_117t2':('none',[op('destroy_sample',3)]),
 'DMF_186':('none',[random_cards(pool(card_type='MINION',minimum=4,maximum=4),destination='board')]),
 'DMF_186a':('none',[random_cards(pool(card_type='MINION',minimum=7,maximum=7),destination='board')]),
 'DMF_187':('none',[discover(OWN_SPELL),op('discount_hand_spells',1)]),
 'DMF_195':('none',[op('snack')]),
 'DMF_219':('none',[('hero_attack',4),op('immune')]),
 'DMF_225':('minion',[op('hit_follow',2,'glaive')]),
 'DMF_244':('none',[('summon','CS2_101t',3)]),
 'DMF_244t':('none',[('summon','CS2_101t',5)]),
 'DMF_512':('none',[op('cloak')]),
 'DMF_515':('none',[('filtered_draw',SPELL,1),('historical_if_combo',('filtered_draw',MINION,1))]),
 'DMF_518':('minion',[('destroy',)]),
 'DMF_522':('none',[('missiles','all_minions',5)]),
 'DMF_526':('none',[draw(MINION+(('mechanic','eq','RUSH'),))]),
 'DMF_526a':('none',[draw(MINION+(('mechanic','eq','RUSH'),),'buff',(2,1))]),
 'DMF_530':('none',[('historical_hand_buff',None,'TAUNT',5,5,True)]),
 'DMF_534':('none',[op('chaos')]),
 'DMF_730':('none',[('hero_attack',4)]),
 'DMF_730t':('none',[('hero_attack',4),('armor',6)]),
 'DRG_028':('none',[discover(pool(card_type='MINION',rarity='LEGENDARY',classes='other'))]),
 'DRG_033':('none',[('draw',3)]),
 'DRG_205':('character',[op('nether_breath')]),
 'DRG_233':('minion',[('buff',1,2),op('dragon_shield')]),
 'DRG_307':('none',[op('infinite_breath')]),
 'DRG_500':('minion',[op('molten_breath')]),
 'EX1_128':('none',[op('conceal')]),
 'EX1_181':('none',[random_cards(pool(card_type='MINION',tribe='DEMON'))]),
 'EX1_182':('none',[random_cards(pool(classes='other'))]),
 'EX1_244':('none',[('tribe_board_buff','TOTEM',0,2)]),
 'EX1_316':('friendly_minion',[('buff',4,4),op('expire_target')]),
 'EX1_317':('none',[('filtered_draw',MINION+(('tribe','eq','DEMON'),),2)]),
 'EX1_320':('character',[follow(3,'dead',random_cards(pool(card_type='MINION',tribe='DEMON'),destination='board'))]),
 'EX1_349':('none',[op('divine_favor')]),
 'EX1_365':('minion',[op('draw_state','holy_wrath',1)]),
 'EX1_409':('none',[op('upgrade')]),
 'EX1_409t':('none',[]),
 'EX1_538':('none',[op('hounds')]),
 'EX1_538t':('none',[]),
 'EX1_549':('friendly_beast',[('temporary_attack_buff',2),('temporary_keyword_target','IMMUNE','end')]),
 'EX1_596':('minion',[op('demonfire')]),
 'EX1_621':('none',[op('circle',4)]),
 'EX1_624':('character',[('damage',5),('heal_own_hero',5)]),
 'GDB_125':('none',[op('healthstone')]),
 'GDB_126':('none',[op('black_hole')]),
 'GDB_227':('none',[discover(OWN_SPELL),op('jettison')]),
 'GDB_228':('none',[('draw',2)]),
 'GDB_237':('none',[('summon','GDB_237t',2)]),
 'GDB_237t':('none',[]),
 'GDB_457':('minion',[('buff',1,2),('keyword','RUSH')]),
 'GDB_460':('minion',[('damage',3),('buff_random_hand_minion','friendly',0,3)]),
 'GDB_464':('none',[op('board_stats','lower')]),
 'GDB_844':('none',[discover(pool(card_type='MINION',tribe='BEAST',minimum=5,classes='own_or_neutral'),cost_delta=-2)]),
 'GDB_864':('none',[random_cards(pool(card_type='MINION',minimum=1,maximum=1),2,destination='board')]),
 'GDB_881':('minion',[('damage',3),('historical_mutation_discount_zones',('hand',),(('mechanic','COMBO'),),1)]),
 'GDB_902':('minion',[op('infiltrate')]),
 'GIL_134':('minion',[op('hit_follow',4,'holy_water')]),
 'GIL_145':('minion',[('buff',1,2)]),
 'GIL_203':('none',[('opponent_next_turn_cost','SPELL',5)]),
 'GIL_506':('minion',[('damage',2)]),
 'GIL_518':('minion',[('damage',4)]),
 'GIL_537':('none',[op('arsenal')]),
 'GIL_543':('friendly_character',[('damage',2),discover(pool(card_type='MINION',tribe='DEMON',classes='own_or_neutral'))]),
 'GIL_571':('none',[resurrect('beast')]),
 'GIL_637':('none',[('draw',1),op('howl')]),
 'GIL_654':('none',[('area_damage','all_minions',1)]),
 'GIL_661':('none',[('area_heal',6)]),
 'GIL_665':('none',[('historic_temporary_attack','enemy',-2,'next_start')]),
 'GIL_687':('minion',[op('hit_follow',3,'wanted')]),
 'LEG_RLK_034':('minion',[follow(3,'dead',('gain_corpses',1))]),
 'LEG_RLK_101':('none',[('draw',1),op('defrost')]),
 'LEG_RLK_705':('none',[('summon','RLK_705t',2)]),
 'RLK_705t':('none',[]),
 'LEG_RLK_715':('none',[op('draw_state','runeforging',1)]),
 'RLK_038':('enemy_character',[('damage',2),('freeze',)]),
 'RLK_122':('none',[op('fill_undead')]),
 'VAC_427':('character',[('damage',3),op('corpsicle')]),
 'VAC_445':('none',[op('attack_group','VAC_445t',5)]),
 'VAC_445t':('none',[]),
 'VAC_513':('character',[('freeze',),op('slope')]),
 'WORK_028':('none',[op('reborn_all'),('destroy_all_minions',)]),
}
DISCARD_EFFECTS={'AT_022':[('damage_random_enemy',4)],'BT_300':[('draw',3)]}
CORRUPT_FORMS={
 'DMF_054':('DMF_054t',0,0),'DMF_090':('DMF_090t',0,0),
 'DMF_117':('DMF_117t',0,0),'DMF_117t':('DMF_117t2',0,0),
 'DMF_186':('DMF_186a',0,0),'DMF_244':('DMF_244t',0,0),
 'DMF_526':('DMF_526a',0,0),'DMF_730':('DMF_730t',0,0),
}
CAST_EFFECTS={'AT_035t':(op('opponent_summon','AT_036t',1),)}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def dragon_held(game,owner):return any(has_tribe(game._card_data(c),'DRAGON') for c in game.players[owner].hand)

def split(game,operation,ctx):
 prefix='historical_utility_archive_'
 if not operation[0].startswith(prefix):return None
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner]
 if name=='opponent_cards':
  count,destination,one=operation[1:]
  mods=dict(set_cost=1) if one else {}
  return game._split_fixed_summon(random_cards(pool(classes=q.hero_class),count,destination=destination,**mods),ctx)
 if name=='opponent_summon':return game._split_fixed_summon(('replay_context',(('summon',operation[1],operation[2]),),dict(ctx,owner=1-owner)),ctx)
 if name=='hit_follow':
  state=dict(victim=game._force_live(ctx.get('target')))
  return op('hit_capture',operation[1],state),(op('after_hit',operation[2],state),)
 if name=='after_hit':
  mode,state=operation[1:];victim=state.get('victim');dead=victim is not None and victim.health<=0
  honorable=victim is not None and victim.health==0 and owner==game.current
  if mode=='spring_trap':return sequence(game,ctx,(('historical_secret_deck','one',True),)*(2 if honorable else 1))
  if mode=='frostbite' and honorable:
   return game._split_fixed_summon(('replay_context',(('next_discount','SPELL',-2,'persistent'),),dict(ctx,owner=1-owner)),ctx)
  if mode=='deliverance' and honorable:return op('fresh_summon',deepcopy(victim),3,3),()
  if dead:
   if mode=='holy_water':return ('historical_copy_target_snapshot',deepcopy(victim),'hand',1,None,None,None,False),()
   if mode=='wanted':return ('add','GAME_005',1),()
   if mode=='glaive':return op('repeat_hand','DMF_225'),()
  return ('batch30_noop',),()
 if name=='draw_state':
  mode=operation[1];count=operation[2] if len(operation)>2 else 1
  filters=MINION if mode in ('vitality','portal') else WEAPON if mode=='runeforging' else SPELL if mode=='felfire' else None
  states=[{} for _ in range(count)]
  return sequence(game,ctx,(x for state in states for x in (('historical_draw_capture',filters,'random',state),op('draw_finish',mode,state))))
 if name=='free_admission':
  a={};b={}
  return sequence(game,ctx,(('historical_draw_capture',MINION,'random',a),('historical_draw_capture',MINION,'random',b),op('admission_finish',a,b)))
 if name=='sweep_reward':
  state={}
  return op('sweep_hit',operation[1],state),(op('sweep_finish',operation[2],state),)
 if name=='piercing':
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  budget=(6+ctx.get('bonus',0))*(1 if ctx.get('spell_multiplier_applied') else game._spell_multiplier(owner))
  excess=max(0,budget-target.health)
  tail=(('replay_context',(('damage_enemy_hero',excess),),dict(ctx,bonus=0,spell_multiplier_applied=True)),) if excess else ()
  return ('damage',6),tail
 if name=='graveyard':
  candidates=[m for m in p.minions if m.health>0]
  if not candidates:return ('batch30_noop',),()
  attack=min(m.attack for m in candidates);victim=game.rng.choice([m for m in candidates if m.attack==attack])
  return op('kill_uid',victim.uid),(('summon','AV_657t',1),)
 if name=='myra':return game._split_fixed_summon(('draw',len(p.deck)),ctx)
 if name=='revenge':return ('area_damage','all_minions',3 if p.health<=12 else 1),()
 if name=='glowflies':return game._split_fixed_summon(('summon','BT_135t',sum(game._card_data(c)['type']=='SPELL' for c in p.hand)),ctx)
 if name=='feast':return game._split_fixed_summon(('draw',p.minions_died_turn),ctx)
 if name=='divine_favor':return game._split_fixed_summon(('draw',max(0,len(q.hand)-len(p.hand))),ctx)
 if name=='hounds':return game._split_fixed_summon(('summon','EX1_538t',len(q.all_minions)),ctx)
 if name=='petting':return game._split_fixed_summon(('summon','DMF_086e',1+len(p.secrets)),ctx)
 if name=='attack_group':
  cid,count=operation[1:];state=dict(summoned=[],mode='random_enemy_character')
  return sequence(game,ctx,(op('group_summon',cid,state),)*count+(('force_group_attacks',state),))
 if name=='ectomancy':
  donors=[deepcopy(m) for m in p.minions if has_tribe(game._card_data(m),'DEMON') and m.health>0]
  return sequence(game,ctx,(op('copy_snapshot',m) for m in donors))
 if name=='nether_breath':
  held=dragon_held(game,owner);context=dict(ctx,lifesteal=bool(ctx.get('lifesteal') or held))
  return game._split_fixed_summon(('replay_context',(('damage',4 if held else 2),),context),ctx)
 if name=='molten_breath':return ('damage',5),(('armor',5),) if dragon_held(game,owner) else ()
 if name=='infinite_breath':return ('area_damage','enemy_minions' if dragon_held(game,owner) else 'all_minions',2),()
 if name=='defrost':
  if p.corpses<2:return ('batch30_noop',),()
  game._spend_corpses(owner,2);return ('draw',1),()
 if name=='fill_undead':return game._split_fixed_summon(random_cards(pool(card_type='MINION',tribe='UNDEAD'),max(0,7-len(p.board)),destination='board'),ctx)
 if name=='secret_plan':
  request=pool(card_type='SPELL',mechanic='SECRET',classes='own')
  if not game._generation_candidates(request,owner):request=pool(card_type='SPELL',mechanic='SECRET',classes='HUNTER')
  return game._split_fixed_summon(discover(request),ctx)
 if name=='jettison':
  if p.armor<2:return ('batch30_noop',),()
  p.armor-=2;return game._split_fixed_summon(discover(OWN_SPELL),ctx)
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_archive_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner]
 target=game._force_live(ctx.get('target'))
 if name=='board_stats':
  for player in game.players:
   for minion in tuple(player.minions):
    if operation[1]=='swap':attack,health=minion.health,minion.attack
    elif operation[1]=='lower':attack=health=min(minion.attack,minion.health)
    else:attack=health=1
    game._set_entity_stats(minion,attack,health)
  game._refresh_auras()
 elif name=='destroy_sample':
  candidates=[m for m in q.minions if m.health>0]
  for victim in game.rng.sample(candidates,min(operation[1],len(candidates))):victim.health=0
 elif name=='neighbors':
  if target is not None:
   board=game.players[target.owner].board;index=board.index(target)
   victims=[board[i] for i in (index-1,index,index+1) if 0<=i<len(board) and board[i] in game.players[target.owner].minions and board[i].health>0]
   with game._damage_batch():
    for victim in victims:game._deal_effect(victim.uid,operation[1],ctx)
 elif name=='coliseum':
  spared=set()
  for player in game.players:
   candidates=[m for m in player.minions if m.health>0]
   if candidates:
    highest=max(m.attack for m in candidates);spared.add(game.rng.choice([m for m in candidates if m.attack==highest]).uid)
  for player in game.players:
   for minion in player.minions:
    if minion.uid not in spared:minion.health=0
 elif name=='lock_load':
  entries=getattr(p,'historical_archive_lock_load',[])
  entries=[e for e in entries if e['turn']==game.turn]
  entries.append(dict(turn=game.turn,uid=getattr(ctx.get('physical_card'),'uid',None)));p.historical_archive_lock_load=entries
 elif name=='lose_armor':p.armor=max(0,p.armor-operation[1])
 elif name=='hit_capture':operation[2]['victim']=target;game._deal_effect(ctx.get('target'),operation[1],ctx)
 elif name=='fresh_summon':
  donor=operation[1];card=game._fresh_replay_card(donor)
  game._summon(owner,donor.card_id,entry_source=card,entry_zone='hand',entry_stats=(operation[2],operation[3]),entry_origin='effect',entry_site='deliverance')
 elif name=='repeat_hand':
  card=Card(game._new_id(),operation[1]);game._make_temporary(card);game._enter_hand(owner,card)
 elif name=='draw_finish':
  mode,state=operation[1:];card=state.get('card')
  if card is None:return True
  if mode=='vitality':game._heal(game.hero_id(owner),state['cost'],healer=owner,spell=ctx.get('spell',False))
  elif mode=='felfire':game._effect(('area_damage','enemies',3 if game._card_data(card).get('spellSchool')=='FEL' else 2),ctx)
  elif mode=='holy_wrath':game._deal_effect(ctx.get('target'),state['cost'],ctx)
  elif mode=='soularium' and card in p.hand:game._make_temporary(card)
  elif mode=='portal' and card in p.hand and len(p.hand)>=8:card.cost_delta=getattr(card,'cost_delta',0)-5
  elif mode=='runeforging' and p.corpses>=1:
   game._spend_corpses(owner,1)
   if card in p.hand:card.cost_delta=getattr(card,'cost_delta',0)-1
 elif name=='admission_finish':
  cards=[state.get('card') for state in operation[1:]]
  if all(card is not None and has_tribe(game._card_data(card),'DEMON') for card in cards):
   for card in cards:
    if card in p.hand:card.cost_delta=getattr(card,'cost_delta',0)-2
 elif name=='snowed':
  uid=ctx.get('target')
  if target is not None:target.health=0
  for player in game.players:
   for minion in player.minions:
    if minion.uid!=uid:game._freeze(minion.uid)
 elif name=='devour':
  if target is not None:
   victims=[m for player in game.players for m in player.minions if m is not target and m.health>0]
   for victim in victims:
    victim.max_health-=1;victim.health-=1
   game._buff(target,0,len(victims));game._refresh_auras()
 elif name=='bless':
  if target is not None:game._set_minion_attack(target,target.health)
 elif name=='naaru':
  characters=list(game._characters())
  for uid in characters:game._heal(uid,3,healer=owner,spell=ctx.get('spell',False))
  if any(player.health<player.max_health or any(m.health<m.max_health for m in player.minions) for player in game.players):
   game._rule_events.append(('captured_effects',dict(operations=(('draw',1),),context=dict(ctx)),[]))
 elif name=='kill_uid':
  victim=game._force_live(operation[1])
  if victim is not None:victim.health=0
 elif name=='silence_enemies':
  for victim in tuple(q.minions):game._effect(('silence',),dict(ctx,target=victim.uid))
 elif name=='bulk_up':
  values=[c for c in p.hand if game._card_data(c)['type']=='MINION' and 'TAUNT' in game._card_mechanics(c)]
  if values:
   card=game.rng.choice(values);add_stat(card,'attack_bonus',1);add_stat(card,'health_bonus',1)
   game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 elif name=='sweep_hit':
  victims=[m for player in game.players for m in player.minions if m.health>0]
  with game._damage_batch():
   for victim in victims:game._deal_effect(victim.uid,operation[1],ctx)
   operation[2]['killed']=sum(m.health<=0 for m in victims)
 elif name=='sweep_finish':
  count=operation[2].get('killed',0)
  if operation[1]=='armor':game._gain_armor(owner,2*count)
  else:
   for _ in range(min(count,len(p.deck))):
    card=p.deck.pop();game._zone_card_removed(owner,card,'deck','destroy');game._log('destroy_deck_card',player=owner,card=game._card_data(card)['id'])
   game._refresh_auras()
 elif name=='sermon':
  for zone in (p.hand,p.deck):
   for i,value in enumerate(zone):
    if game._card_data(value)['type']=='MINION':
     card=value if isinstance(value,Card) else Card(game._new_id(),value);add_stat(card,'attack_bonus',1);add_stat(card,'health_bonus',1);zone[i]=card
  for minion in p.minions:game._buff(minion,1,1)
 elif name=='altar':
  for side,player in enumerate(game.players):
   for _ in range(min(3,len(player.deck))):
    card=player.deck.pop();game._zone_card_removed(side,card,'deck','destroy');game._log('destroy_deck_card',player=side,card=game._card_data(card)['id'])
  game._refresh_auras()
 elif name=='weapons_project':
  for side in (owner,1-owner):game._equip(side,'BOT_042t')
  for side in (owner,1-owner):game._gain_armor(side,6)
 elif name=='hand_copy':
  values=[c for c in p.hand if game._card_data(c)['type']=='MINION' and (operation[1]=='MINION' or has_tribe(game._card_data(c),operation[1]))]
  if values:
   card=game._copy_card(game.rng.choice(values),source_owner=owner)
   game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_source=card,entry_zone='hand',entry_origin='copy',entry_site='eureka')
 elif name=='left_minion':
  card=next((c for c in p.hand if game._card_data(c)['type']=='MINION'),None)
  if card is not None:add_stat(card,'attack_bonus',2);add_stat(card,'health_bonus',2)
 elif name in ('omega','snack'):
  request=pool(card_type='MINION',tribe='MECHANICAL',classes='own_or_neutral') if name=='omega' else OWN_SPELL
  values=game._generation_discover_candidates(request,ctx);ids=game.rng.sample(list(values),min(3,len(values)))
  if not ids:return True
  if name=='omega' and p.max_mana>=10:
   results=[game._enter_hand(owner,Card(game._new_id(),cid)) for cid in ids]
   offer=DiscoverOffer(owner,'historical_archive_omega_all',0,tuple(dict(card_id=cid) for cid in ids),getattr(p.equipped_card,'uid',None),tuple(range(len(ids))))
   game._record_discover(owner,offer)
   for result in results:game._defer_discover_followups(owner,result)
  else:
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite archive Discover')
   game.pending_choice=dict(owner=owner,kind='historical_archive_offer',mode=name,context=dict(ctx),options=[dict(card_id=cid) for cid in ids]);game.phase='choice'
 elif name=='expire_target':
  if target is not None:
   key=game._new_id();target.rule_state.setdefault('historical_archive_expirations',[]).append(key)
   game._schedule_turn_effect(game.current,'end',0,1,(op('expire_uid',target.uid,key),),source_card_id=ctx.get('card_id'))
 elif name=='expire_uid':
  victim=game._force_live(operation[1])
  if victim is not None and operation[2] in victim.rule_state.get('historical_archive_expirations',()):victim.health=0
 elif name=='board_death':
  mode=operation[1];victims=[target] if mode=='ancestral' and target is not None else list(p.minions) if mode!='ancestral' else []
  effect=random_cards(pool(card_type='MINION',tribe='MECHANICAL')) if mode=='mech' else ('summon','EX1_506a',1) if mode=='murloc' else op('resummon')
  for victim in victims:victim.attached_death_effects.append(effect);victim.keywords.add('DEATHRATTLE')
 elif name=='resummon':
  source=ctx.get('source')
  if source is not None:
   card=game._fresh_replay_card(source);game._summon(owner,source.card_id,entry_source=card,entry_zone='hand',entry_origin='resurrection',entry_site='ancestral_spirit')
 elif name=='swap_target':
  if target is not None:game._set_entity_stats(target,target.health,target.attack);game._refresh_auras()
 elif name=='copy_snapshot':
  donor=operation[1];game._summon(owner,donor.card_id,copy_from=donor,entry_origin='copy',entry_site='ectomancy')
 elif name=='totemic':
  if target is not None and has_tribe(game._card_data(target),'TOTEM'):game._summon(owner,target.card_id,copy_from=target,entry_origin='copy',entry_site='totemic_reflection')
 elif name=='group_summon':
  cid,state=operation[1:];before={m.uid for m in p.minions}
  game._summon(owner,cid,entry_origin='effect',entry_site='archive_forced_group')
  state['summoned'].extend(m.uid for m in p.minions if m.uid not in before and m.card_id==cid)
 elif name=='felbolt':
  victims=[m for m in p.minions if m.health>0];friendly=game.rng.choice(victims) if victims else None
  with game._damage_batch():
   if target is not None:game._deal_effect(target.uid,3,ctx)
   if friendly is not None:game._deal_effect(friendly.uid,3,ctx)
 elif name=='blade_dance':
  values=[m.uid for m in q.minions if m.health>0];victims=game.rng.sample(values,min(3,len(values)));amount=game._hero_attack(owner)
  with game._damage_batch():
   for uid in victims:game._deal_effect(uid,amount,ctx)
 elif name=='immune':p.historical_evasion_immune_turn=game.turn
 elif name=='fishes':
  victims=[m for player in game.players for m in player.minions if m.health>0 and m.health<m.max_health]
  with game._damage_batch():
   for victim in victims:game._deal_effect(victim.uid,3,ctx)
 elif name=='mind_vision':
  if q.hand:game._enter_hand(owner,game._copy_card(game.rng.choice(q.hand),source_owner=1-owner))
 elif name=='corruption':
  if target is not None:
   key=game._new_id();target.rule_state.setdefault('historical_archive_corruption',[]).append(key)
   game._schedule_turn_effect(owner,'start',1,1,(op('corruption_expire',target.uid,key),),source_card_id='CS2_063')
 elif name=='corruption_expire':
  victim=game._force_live(operation[1])
  if victim is not None and operation[2] in victim.rule_state.get('historical_archive_corruption',()):victim.health=0
 elif name=='health_one':
  if target is not None:target.health=target.max_health=1;game._refresh_auras()
 elif name=='divine_spirit':
  if target is not None:game._buff(target,0,target.health)
 elif name=='pursuit':p.recruit_attack_bonus+=1
 elif name=='hunting_party':
  cards=[game._copy_card(c,source_owner=owner) for c in p.hand if game._card_data(c)['type']=='MINION' and has_tribe(game._card_data(c),'BEAST')]
  for card in cards:game._enter_hand(owner,card)
 elif name=='escape':
  for minion in tuple(p.minions):
   if minion in p.board and minion.health>0:game._bounce(minion,0)
 elif name=='lackey':
  from .historical_family_batches import LACKEYS
  from .pools import require_fixed_cards
  require_fixed_cards(LACKEYS,game.cards);game._add(owner,game.rng.choice(tuple(LACKEYS)))
 elif name=='cannons':
  uid=ctx.get('target');victims=[m for player in game.players for m in player.minions if m.health>0]
  with game._damage_batch():
   for victim in victims:game._deal_effect(victim.uid,3 if victim.uid==uid else 1,ctx)
 elif name=='discount_hand_spells':
  for card in p.hand:
   if game._card_data(card)['type']=='SPELL':card.cost_delta=getattr(card,'cost_delta',0)-operation[1]
 elif name=='cloak':p.historical_valeera_stealth_until=max(getattr(p,'historical_valeera_stealth_until',-1),p.turns_taken+1)
 elif name=='chaos':
  for i,value in enumerate(p.deck):
   if game._card_data(value)['type']!='MINION':continue
   card=value if isinstance(value,Card) else Card(game._new_id(),value)
   cost=game._cost(card,owner);attack=game._card_stat(card,'attack',owner);health=game._card_stat(card,'health',owner)
   game._mutation_set_stats(card,owner,cost,health);game._set_card_cost(card,attack);p.deck[i]=card
 elif name=='dragon_shield':
  if target is not None and dragon_held(game,owner):target.keywords.add('DIVINE_SHIELD')
 elif name=='conceal':
  for minion in p.minions:game._temporary_keyword(minion,'STEALTH','next_start')
 elif name=='upgrade':
  if p.weapon:game._buff_weapon(owner,attack=1,durability=1)
  else:game._equip(owner,'EX1_409t')
 elif name=='demonfire':
  if target is not None:
   if target.owner==owner and has_tribe(game._card_data(target),'DEMON'):game._buff(target,2,2)
   else:game._deal_effect(target.uid,2,ctx)
 elif name=='circle':
  for player in game.players:
   for minion in tuple(player.minions):game._heal(minion.uid,operation[1],healer=owner,spell=ctx.get('spell',False))
 elif name=='healthstone':game._heal(game.hero_id(owner),p.hero_damage_taken_turn,healer=owner,spell=ctx.get('spell',False))
 elif name=='black_hole':
  for player in game.players:
   for minion in player.minions:
    if not has_tribe(game._card_data(minion),'DEMON'):minion.health=0
 elif name=='infiltrate':
  victims=[m.uid for player in game.players for m in player.minions if m.uid!=ctx.get('target') and m.health>0]
  with game._damage_batch():
   for uid in victims:game._deal_effect(uid,3,ctx)
 elif name=='arsenal':
  values=[c for c in p.deck if game._card_data(c)['type']=='WEAPON']
  if values:
   card=game.rng.choice(values);physical=card if isinstance(card,Card) else Card(0,card)
   game._log('reveal',player=owner,card=game._card_data(card)['id'],source='GIL_537')
   game._effect(('area_damage','all_minions',game._card_stat(physical,'attack',owner)),ctx)
 elif name=='howl':game._gain_armor(owner,len(p.hand))
 elif name=='corpsicle':
  if p.corpses>=3:
   game._spend_corpses(owner,3);card=ctx.get('physical_card') or Card(game._new_id(),'VAC_427')
   game._schedule_turn_effect(owner,'end',0,1,(op('return_card',card),),source_card_id='VAC_427')
 elif name=='return_card':game._enter_hand(owner,operation[1])
 elif name=='slope':
  count=sum(player.frozen_until>=0 for player in game.players)+sum(m.frozen_until>=0 for player in game.players for m in player.minions)
  if count:game._rule_events.append(('captured_effects',dict(operations=(('draw',count),),context=dict(ctx)),[]))
 elif name=='reborn_all':
  for player in game.players:
   for minion in player.minions:minion.keywords.add('REBORN')
 else:return False
 return True

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_archive_offer':return False
 owner=choice['owner'];card=Card(game._new_id(),selected['card_id'])
 if choice['mode']=='snack':
  game._heal(game.hero_id(owner),game._cost(card,owner),healer=owner,spell=choice['context'].get('spell',False))
 game._discovery_result=game._enter_hand(owner,card)
 return True

def event(game,kind,data):
 if kind!='spell_cast':return
 owner=data['owner'];p=game.players[owner];uid=getattr(data.get('physical_card'),'uid',None)
 count=sum(e['turn']==game.turn and e['uid']!=uid for e in getattr(p,'historical_archive_lock_load',()))
 if count:
  game._rule_events.append(('captured_effects',dict(operations=(random_cards(pool(classes='HUNTER'),count),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='AT_061')),[]))
