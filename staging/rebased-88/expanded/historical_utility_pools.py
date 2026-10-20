"""Explicit pool declarations for newly written utility spell consumers.

State-dependent preflight uses current board/counters and never filters outcomes
by implemented coverage. Runtime consumers recheck pools when effects resolve.
"""
from .generation_cards import PoolRequest,pool,board_pool
from .transformations import evolve_pool

def requests_for(game,cid,owner):
 from .historical_utility_spells import TOKEN_RULES
 from .historical_zone_spell_batch import requests_for as zone_spell_requests
 from .historical_summon_faction_finish import requests_for as summon_faction_requests
 from .historical_stormwind_questline_finish import requests_for as stormwind_requests
 found=set(zone_spell_requests(game,cid,owner))|summon_faction_requests(game,cid,owner)|stormwind_requests(game,cid,owner)
 if cid in ('YOP_024','YOP_024t'):found.add(pool(card_type='SPELL',classes='own_or_neutral'))
 from .historical_final_spell_roots import requests_for as final_root_requests
 found.update(final_root_requests(game,cid,owner))
 def walk(value):
  if isinstance(value,PoolRequest):found.add(value)
  elif isinstance(value,(tuple,list)):
   for child in value:walk(child)
 walk(TOKEN_RULES.get(cid,()))
 if cid in ('AT_033','BOT_087'):found.add(pool(classes=game.players[1-owner].hero_class))
 if cid=='AT_061':found.add(pool(classes='HUNTER'))
 if cid=='BOT_299':found.add(pool(card_type='MINION',tribe='MECHANICAL',classes='own_or_neutral'))
 if cid=='BOT_402':
  request=pool(card_type='SPELL',mechanic='SECRET',classes='own')
  if not game._generation_candidates(request,owner):request=pool(card_type='SPELL',mechanic='SECRET',classes='HUNTER')
  found.add(request)
 if cid=='RLK_122':found.add(board_pool(pool(card_type='MINION',tribe='UNDEAD')))
 if cid=='BOT_438':found.add(pool(card_type='MINION',tribe='MECHANICAL'))
 if cid=='ONY_032':found.add(pool(card_type='SPELL',classes='other'))
 if cid=='WON_323':found.add(board_pool(pool(card_type='MINION',tribe='DEMON')))
 if cid=='GIL_696':found.add(pool(classes=game.players[1-owner].hero_class))
 if cid=='TRL_324':
  cost=min(10,game.players[owner].armor);found.add(board_pool(pool(card_type='MINION',minimum=cost,maximum=cost)))
 if cid=='SW_440':found.add(pool(card_type='MINION',mechanic='DEATHRATTLE',classes='own_or_neutral'))
 if cid=='TRL_082':
  for m in game.players[owner].minions:found.add(evolve_pool(game._card_stat(m,'cost',m.owner),1))
 if cid=='TOY_700t':
  mana=game.players[owner].mana
  found.update((pool(card_type='SPELL',classes='DRUID',maximum=mana),pool(card_type='MINION',classes='DRUID',maximum=mana),pool(card_type='MINION',classes='NEUTRAL',maximum=mana)))
 if cid=='YOD_023':
  found.update(pool(card_type='MINION',tribe=tribe,classes='own_or_neutral') for tribe in ('MECHANICAL','DRAGON'))
 if cid=='GIL_586':found.add(pool(card_type='MINION',tribe='ELEMENTAL'))
 if cid=='BOT_245':found.add(pool(card_type='MINION',rarity='LEGENDARY',excluded_mechanic='COLOSSAL'))
 if cid=='SW_035':
  count=sum(bool(record.get('overload_card',game.cards[record['card_id']].get('overload',0))) for record in game.players[owner].played_history)
  cost=min(10,1+count)
  found.add(pool(card_type='MINION',minimum=cost,maximum=cost,classes='own_or_neutral',excluded_mechanic='COLOSSAL'))
 if cid in ('OG_027','CFM_696','SCH_235','DAL_071','LOOT_504','YOD_020'):
  sides=(owner,) if cid=='OG_027' else (1-owner,) if cid in ('CFM_696','SCH_235') else (0,1)
  deltas=(1,) if cid in ('OG_027','DAL_071','LOOT_504') else (3,) if cid=='YOD_020' else (-1,-2,-3) if cid=='SCH_235' else (-1,)
  for side in sides:
   for minion in game.players[side].minions:
    if minion.health>0:
     cost=game._card_stat(minion,'cost',minion.owner)
     for delta in deltas:found.add(evolve_pool(cost,delta))
 if cid=='BT_018':found.add(pool(card_type='MINION',tribe='MURLOC'))
 if cid=='AT_044':found.add(pool(card_type='MINION'))
 if cid=='DAL_352':found.add(pool(card_type='MINION',classes='DRUID'))
 if cid=='OG_045':found.add(pool(card_type='MINION',tribe='BEAST'))
 if cid=='AV_283':found.add(pool(card_type='SPELL',classes='MAGE',maximum=20))
 if cid=='BT_021':found.add(pool(card_type='MINION',classes='MAGE'))
 if cid=='GDB_133':found.add(pool(card_type='SPELL',classes='own_or_neutral'))
 if cid=='DMF_108':
  from engine.game import Card
  for value in game.players[owner].deck:
   if game._card_data(value)['type']=='SPELL':
    cost=min(10,game._cost(value if isinstance(value,Card) else Card(0,value),owner)+3)
    found.add(pool(card_type='SPELL',minimum=cost,maximum=cost))
 if cid=='DAL_578':found.add(board_pool(pool(card_type='MINION',minimum=6,maximum=6)))
 if cid in ('DMF_105','DMF_105t'):
  request=pool(card_type='SPELL',mechanic='SECRET',classes='own')
  if not game._generation_candidates(request,owner):request=pool(card_type='SPELL',mechanic='SECRET',classes='MAGE')
  found.add(request)
 if cid=='BOT_254':
  cost=max(0,2+game._spell_damage(owner,cid))
  found.add(board_pool(pool(card_type='MINION',minimum=cost,maximum=cost)))
 if cid in ('DAL_177','DAL_177ts'):
  for player in game.players:
   for target in player.minions:
    cost=game._card_stat(target,'cost',target.owner)
    found.add(board_pool(pool(card_type='MINION',minimum=cost,maximum=cost)))
 if cid=='TRL_317':found.add(pool(card_type='SPELL',classes='MAGE'))
 if cid=='GDB_301':found.add(pool(card_type='SPELL',school='FIRE'))
 if cid=='WORK_012':found.add(board_pool(pool(card_type='MINION',tribe='NAGA')))
 if cid=='BT_006':found.add(pool(card_type='SPELL',classes='MAGE'))
 if cid=='BT_291' and not any(game._card_data(c)['type']=='MINION' for c in game.players[owner].deck):found.add(pool(card_type='MINION',minimum=5,maximum=5))
 if cid=='DRG_106':
  from .selectors import has_tribe
  if any(has_tribe(game._card_data(c),'DRAGON') for c in game.players[owner].hand):found.add(pool(card_type='SPELL',classes='own_or_neutral'))
 return found
