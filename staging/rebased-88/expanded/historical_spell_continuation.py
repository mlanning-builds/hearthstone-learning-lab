"""Historical spell continuation batch. Written rules, behavior validation deferred."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,random_cards,discover
from .historical_draw_batches import draw
from .historical_damage_spells import follow
from .selectors import has_tribe
from .pools import require_fixed_cards

def op(name,*args):return ('historical_utility_continuation_'+name,)+args
MINION=(('type','eq','MINION'),)
BEAST=MINION+(('tribe','eq','BEAST'),)
GIFT={
 'GIFT_03':('CORE_BRM_013','EX1_617','EX1_537'),
 'GIFT_04':('RLK_057','RLK_015','RLK_024'),
 'GIFT_05':('EX1_619','CS2_093','CS2_092'),
 'GIFT_06':('EX1_259','EX1_246','CS2_046'),
 'GIFT_07':('CS2_108','EX1_606','EX1_407'),
 'GIFT_08':('SW_040','BT_035','BT_235'),
 'GIFT_09':('CS2_072','CS2_074','EX1_129'),
 'GIFT_10':('CORE_OG_047','CS2_013','CS2_012'),
 'GIFT_11':('EX1_302','EX1_309','EX1_312'),
 'GIFT_12':('CS2_004','CS2_234','CS1_113'),
}
TOKEN_RULES={
 'RLK_057':('historic_undead',[('transform','RLK_057t')]),
 'RLK_057t':('none',[]),
 'CFM_616':('none',[op('pilfer')]),
 'CS2_233':('none',[op('flurry')]),
 'BT_253':('minion',[('buff',1,2),op('copy_target')]),
 'DAL_716':('minion',[('damage',4)]),
 'DMF_119':('none',[('historical_hand_discard_select','own','lowest','none'),('board_buff',1,1)]),
 'DMF_221':('minion',[('historical_utility_archive_neighbors',1)]),
 'GVG_019':('minion',[op('demonheart')]),
 'GVG_022':('none',[('weapon_buff',3,0),('historical_if_combo',op('random_attack',3))]),
 'GVG_026':('none',[op('trigger_all')]),
 'GVG_047':('none',[('destroy_random_enemy',),('historical_if_combo',('destroy_enemy_weapon',))]),
 'GVG_052':('minion',[('destroy',)]),
 'GVG_057':('none',[('heal_own_hero',4),('hero_attack',2)]),
 'ICC_039':('minion',[('set_target_stats',3,3)]),
 'ICC_052':('friendly_deathrattle',[('historical_batch_trigger_target_death',)]),
 'ICC_078':('minion',[('freeze',),op('adjacent_damage',3)]),
 'ICC_089':('none',[draw(MINION+(('tribe','eq','MURLOC'),)),draw(MINION+(('tribe','eq','MURLOC'),))]),
 'ICC_091':('none',[op('shuffle_hand_copies')]),
 'ICC_206':('friendly_minion',[op('give_target')]),
 'ICC_207':('none',[op('enemy_deck_copies',3,False)]),
 'ICC_281':('none',[draw((('type','eq','WEAPON'),)),draw((('type','eq','WEAPON'),))]),
 'ICC_469':('friendly_minion',[('destroy',),('destroy_random_enemy',)]),
 'ICC_837':('none',[('armor',10),op('enemy_hand_discount',2)]),
 'KAR_013':('friendly_minion',[('silence',),('draw',1)]),
 'LOOT_060':('minion',[('damage',8)]),
 'LOOT_093':('none',[('historical_copy_recruit_one','deck',MINION+(('cost','le',2),),None,None)]*3),
 'LOOT_333':('none',[('historic_board_buff','recruits',2,2),('historic_board_keyword','recruits','TAUNT','permanent')]),
 'LOOT_353':('none',[op('enemy_deck_copies',1,True)]),
 'LOOT_364':('none',[op('reckless')]),
 'LOOT_370':('none',[('historical_copy_recruit_one','deck',MINION,None,None)]),
 'LOOT_417':('none',[('destroy_all_minions',),('discard',2)]),
 'LOOT_522':('none',[op('crushing_walls')]),
 'OG_048':('minion',[('buff',2,2),op('draw_if_beast')]),
 'OG_072':('none',[discover(pool(mechanic='DEATHRATTLE',classes='own_or_neutral'))]),
 'OG_100':('none',[op('destroy_low')]),
 'OG_104':('none',[('historical_copy_healing_damage_turn',)]),
 'OG_116':('none',[('missiles','all_characters',13)]),
 'OG_176':('historical_galakrond_undamaged_character',[('damage',5)]),
 'OG_198':('character',[op('forbidden_heal')]),
 'OG_239':('none',[op('doom')]),
 'OG_276':('none',[op('battle_rage_copies')]),
 'OG_311':('none',[discover(pool(card_type='MINION',classes='PALADIN'),attack=2,health=2)]),
 'ONY_008':('none',[('draw',1),('draw_until',3)]),
 'ONY_011':('none',[('missiles','enemy_minions',10)]),
 'ONY_013':('none',[('heal_own_hero',5),op('discount_random_spell',2)]),
 'ONY_025':('minion',[('buff',2,1),('keyword','RUSH')]),
 'ONY_027':('minion',[op('buff_enemy_count')]),
 'SCH_247':('none',[random_cards(pool(card_type='MINION',minimum=1,maximum=1),2)]),
 'SCH_250':('none',[op('enemy_attack_one')]),
 'SCH_307':('none',[('area_damage','all_minions',2),('on_draw_shuffle','SCH_307t',2,0)]),
 'SCH_422':('none',[draw((('mechanic','eq','OUTCAST'),))]),
 'SCH_524':('damaged_minion',[('buff',3,0),('keyword','DIVINE_SHIELD')]),
 'SCH_525':('none',[random_cards(pool(card_type='MINION',mechanic='TAUNT'),2)]),
 'SCH_604':('minion',[op('overwhelm')]),
 'SCH_606':('none',[random_cards(pool(card_type='MINION',tribe='BEAST',minimum=2,maximum=2)),random_cards(pool(card_type='MINION',tribe='BEAST',minimum=3,maximum=3))]),
 'SCH_623':('none',[('draw',2)]),
 'SCH_701':('minion',[('damage',3),('on_draw_shuffle','SCH_307t',2,0)]),
 'SW_027':('minion',[op('harbor')]),
 'SW_041':('none',[('schedule_turn_effect','start',1,1,(draw(None,'discount',(1,)),))]),
 'SW_046':('none',[('area_damage','enemy_minions',1)]),
 'SW_090':('minion',[follow(2,'dead',('heal_own_hero',3))]),
 'SW_094':('none',[('armor',8)]),
 'SW_412':('historical_galakrond_undamaged_character',[('damage',3)]),
 'SW_441':('none',[('historic_board_silence','enemy')]),
 'SW_452':('minion',[op('fel_gorger_damage')]),
 'TRL_058':('none',[('temporary_next_discount',3),discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'TRL_097':('minion',[('historical_copy_target_delivery','hand',1,None,None,None,False)]),
 'TRL_124':('none',[draw(MINION+(('tribe','eq','PIRATE'),)),draw(MINION+(('tribe','eq','PIRATE'),)),('historical_if_combo',draw((('type','eq','WEAPON'),)))]),
 'TRL_156':('none',[discover(pool(card_type='WEAPON',classes='other'))]),
 'TRL_157':('undamaged_minion',[('destroy',)]),
 'TRL_245':('none',[('historical_hand_discard_select','own','lowest','none'),('area_damage','all_minions',2)]),
 'TRL_246':('none',[op('halve_decks')]),
 'TRL_249':('friendly_minion',[('destroy',),('board_buff',1,1)]),
 'TRL_321':('damaged_minion',[('damage',4)]),
 'TRL_362':('none',[random_cards(pool(card_type='MINION',tribe='DRAGON'),2)]),
 'TRL_500':('none',[('destroy_crystals',3),op('deck_buff',2,2)]),
 'TRL_555':('minion',[('destroy',)]),
 'ULD_272':('none',[('area_damage','enemies',1),op('heal_friends',1)]),
 'ULD_328':('none',[random_cards(pool(card_type='SPELL',classes='other'),2)]),
 'ULD_429':('none',[random_cards(pool(card_type='MINION',tribe='BEAST',classes='HUNTER')),random_cards(pool(card_type='SPELL',mechanic='SECRET',classes='HUNTER')),random_cards(pool(card_type='WEAPON',classes='HUNTER'))]),
 'ULD_716':('none',[('historical_copy_recruit_one','deck',MINION+(('tribe','eq','MURLOC'),),None,None)]*7),
 'ULD_728':('minion',[('set_target_stats',1,1)]),
 'VAC_335':('none',[random_cards(pool(card_type='SPELL',classes='other',minimum=1,maximum=1),2)]),
 'VAC_414':('none',[op('malt')]),
 'VAC_460':('character',[('damage',2),('historical_if_combo',('add','GAME_005',1))]),
 'VAC_915':('character',[('damage',4),op('random_buff',4,4)]),
 'VAC_928':('none',[('draw',3),op('outcast_opponent_draw')]),
 'VAC_939':('friendly_minion',[('destroy',),('draw',3)]),
 'WC_007':('friendly_beast',[('keyword','POISONOUS')]),
 'WC_014':('none',[op('odd_destroy')]),
 'WON_023':('none',[('historical_utility_archive_lock_load',)]),
 'WON_049':('none',[('historical_utility_archive_coliseum',)]),
 'WON_071':('none',[('historical_utility_archive_opponent_cards',3,'hand',False)]),
 'WON_093':('historic_demon',[('buff',3,3)]),
 'WON_097':('none',[('missiles','all_characters',13)]),
 'WON_100':('none',[('historical_utility_archive_destroy_sample',2),('discard',2)]),
 'WON_110':('none',[draw(MINION+(('mechanic','eq','TAUNT'),),'buff',(2,2))]),
 'WON_309':('minion',[('buff',2,2),random_cards(pool(card_type='MINION',minimum=2,maximum=2),destination='board')]),
 'WON_333':('none',[discover(pool(card_type='MINION',classes='PALADIN'),attack=2,health=2)]),
 'WON_342':('enemy_minion',[('historical_copy_target_delivery','hand',1,None,None,1,False)]),
 'WON_347':('none',[op('random_hand_beast')]),
 'WORK_007':('minion',[('destroy',)]),
 'WORK_014':('minion',[('damage',4),op('top_demon',pool(card_type='MINION',tribe='DEMON',minimum=5))]),
 'WORK_021':('none',[op('reserved')]),
 'YOD_018':('none',[discover(pool(card_type='MINION',mechanic='BATTLECRY',classes='own_or_neutral'),cost_delta=-2)]),
}
TOKEN_RULES.update({cid:('none',[op('gift',cid)]) for cid in GIFT})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def split(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('doom')[0]:
  count=sum(len(player.minions) for player in game.players)
  return ('destroy_all_minions',),(('draw',count),)
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_continuation_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner];target=game._force_live(ctx.get('target'))
 if name=='gift':
  ids=GIFT[operation[1]];require_fixed_cards(ids,game.cards)
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Gift Discover')
  game.pending_choice=dict(owner=owner,kind='historical_continuation_gift',context=dict(ctx),options=[dict(card_id=cid) for cid in ids]);game.phase='choice'
 elif name=='pilfer':game._effect(('empty_crystals','friendly',len(p.minions)),ctx)
 elif name=='flurry':
  if p.weapon:
   attack=p.weapon['attack'];game._break_weapon(owner);game._effect(('area_damage','enemy_minions',attack),ctx)
 elif name=='copy_target':
  if target is not None:game._summon(owner,target.card_id,copy_from=target,entry_origin='copy',entry_site='psyche_split')
 elif name=='demonheart':
  if target is not None:
   if target.owner==owner and has_tribe(game._card_data(target),'DEMON'):game._buff(target,5,5)
   else:game._deal_effect(target.uid,5,ctx)
 elif name=='random_attack':
  if p.minions:game._buff(game.rng.choice(p.minions),operation[1],0)
 elif name=='trigger_all':
  operations=tuple(('replay_context',(('historical_batch_trigger_target_death',),),dict(ctx,target=m.uid)) for m in tuple(p.minions) if 'DEATHRATTLE' in m.keywords)
  game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(ctx)),[]))
 elif name=='adjacent_damage':
  if target is not None:
   board=game.players[target.owner].board;i=board.index(target)
   victims=[board[j] for j in (i-1,i+1) if 0<=j<len(board) and board[j] in game.players[target.owner].minions]
   with game._damage_batch():
    for m in victims:game._deal_effect(m.uid,operation[1],ctx)
 elif name=='shuffle_hand_copies':
  copies=[game._copy_card(card,source_owner=owner) for card in p.hand]
  p.deck.extend(copies);game.rng.shuffle(p.deck)
  if copies:game._record_deck_insertion(owner,owner,len(copies),'shuffle',cards=tuple(copies))
 elif name=='give_target':
  if target is not None:
   if len(q.board)>=7:target.health=0
   else:
    p.board.remove(target);target.owner=1-owner;q.board.append(target);target.summoned_turn=game.turn;target.attacks=0;game._refresh_auras()
 elif name=='enemy_deck_copies':
  candidates=[c for c in q.deck if not operation[2] or game._card_data(c)['type']=='SPELL']
  for card in game.rng.sample(candidates,min(operation[1],len(candidates))):game._enter_hand(owner,game._copy_card(card,source_owner=1-owner))
 elif name=='enemy_hand_discount':
  for card in q.hand:
   if game._card_data(card)['type']=='MINION':card.cost_delta=getattr(card,'cost_delta',0)-operation[1]
 elif name=='reckless':
  amount=p.armor;p.armor=0
  game._effect(('area_damage','all_minions',amount),ctx)
 elif name=='crushing_walls':
  victims=list(q.minions)
  for m in ([victims[0]] if len(victims)==1 else [victims[0],victims[-1]] if victims else []):m.health=0
 elif name=='draw_if_beast':
  if target is not None and has_tribe(game._card_data(target),'BEAST'):game._rule_events.append(('captured_effects',dict(operations=(('draw',1),),context=dict(ctx)),[]))
 elif name=='destroy_low':
  for player in game.players:
   for m in player.minions:
    if m.attack<=2:m.health=0
 elif name=='forbidden_heal':
  amount=p.mana;p.mana=0;game._heal(ctx['target'],amount*2,healer=owner,spell=ctx.get('spell',False))
 elif name=='battle_rage_copies':
  for m in list(p.minions):
   if m.health<m.max_health:game._effect(('historical_copy_target_snapshot',m,'hand',1,None,None,None,False),ctx)
 elif name=='discount_random_spell':
  cards=[c for c in p.hand if game._card_data(c)['type']=='SPELL']
  if cards:
   c=game.rng.choice(cards);c.cost_delta=getattr(c,'cost_delta',0)-operation[1]
 elif name=='buff_enemy_count':
  if target is not None:game._buff(target,1+len(q.all_minions),1+len(q.all_minions))
 elif name=='enemy_attack_one':
  for m in q.minions:
   delta=1-m.attack;game._adjust_minion_attack(m,delta);m.imbue_attack_expiries.append(dict(owner=owner,amount=delta))
 elif name=='overwhelm':game._deal_effect(ctx['target'],2+sum(has_tribe(game._card_data(m),'BEAST') for m in p.minions),ctx)
 elif name=='harbor':game._deal_effect(ctx['target'],5 if any(has_tribe(game._card_data(m),'PIRATE') for m in p.minions) else 2,ctx)
 elif name=='fel_gorger_damage':game._deal_effect(ctx['target'],5 if ctx.get('outcast') else 3,ctx)
 elif name=='halve_decks':
  for side,player in enumerate(game.players):
   for _ in range(len(player.deck)//2):
    c=player.deck.pop();game._zone_card_removed(side,c,'deck','destroy');game._log('destroy_deck_card',player=side,card=game._card_data(c)['id'])
  game._refresh_auras()
 elif name=='deck_buff':
  from .historical_saidan import add
  for i,c in enumerate(p.deck):
   if game._card_data(c)['type']=='MINION':
    if isinstance(c,str):c=Card(game._new_id(),c);p.deck[i]=c
    add(c,'attack_bonus',operation[1]);add(c,'health_bonus',operation[2])
 elif name=='heal_friends':
  for uid in [game.hero_id(owner)]+[m.uid for m in p.minions]:game._heal(uid,operation[1],healer=owner,spell=ctx.get('spell',False))
 elif name=='malt':game._effect(('area_damage','enemies',3 if p.hero_damage_taken_turn else 2),ctx)
 elif name=='random_buff':
  if p.minions:game._buff(game.rng.choice(p.minions),operation[1],operation[2])
 elif name=='outcast_opponent_draw':
  if not ctx.get('outcast'):game._rule_events.append(('captured_effects',dict(operations=(('draw',3),),context=dict(ctx,owner=1-owner)),[]))
 elif name=='odd_destroy':
  for player in game.players:
   for m in player.minions:
    if m.attack%2:m.health=0
 elif name=='random_hand_beast':
  from .historical_saidan import add
  values=[c for c in p.hand if game._card_data(c)['type']=='MINION' and has_tribe(game._card_data(c),'BEAST')]
  if values:
   c=game.rng.choice(values);add(c,'attack_bonus',2);add(c,'health_bonus',2)
 elif name=='top_demon':
  values=game._generation_candidates(operation[1],owner)
  if values:
   card=Card(game._new_id(),game.rng.choice(values));p.deck.append(card);game._record_deck_insertion(owner,owner,1,'top',cards=(card,))
 elif name=='reserved':
  from .historical_saidan import add
  values=[c for c in p.hand if game._card_data(c)['type']=='MINION']
  if values:
   c=game.rng.choice(values);add(c,'attack_bonus',4);add(c,'health_bonus',4)
   if len(values)==1:c.cost_delta=getattr(c,'cost_delta',0)-2
 else:return False
 return True

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_continuation_gift':return False
 card=Card(game._new_id(),selected['card_id']);game._make_temporary(card)
 game._discovery_result=game._enter_hand(choice['owner'],card)
 return True
