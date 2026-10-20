"""Explicit historical generated weapons and locations; unvalidated."""
from .generation_cards import pool,random_cards
from .selectors import has_tribe
TOKEN_RULES={cid:('none',[]) for cid in (
 'DEEP_014','REV_509','REV_917','TOY_358','TOY_810','RLK_828',
 'WW_813','NX2_025','TOY_641','WW_412','TSC_913','TSC_913t',
 'TOY_358t','TTN_465t')}
TOKEN_RULES['EX1_539']=('character',[('damage',2)])
WEAPON_TRIGGERS={
 'DEEP_014':[('draw',1)],'REV_509':[('draw_until',3)],
 'REV_917':[('historical_family_basic_totem',)],
 'TOY_358':[('summon','TOY_358t',1)],
 'TOY_810':[('historic_zone_buff','hand',None,1,1)],
 'RLK_828':[('historic_zone_buff','hand_deck',None,1,1),('board_buff',1,1)],
 'WW_813':[('add','EX1_539',1)],
 'TSC_913t':[('area_damage','enemy_minions',2)],
}
DEATH_EFFECTS={
 'NX2_025':[random_cards(pool(mechanic='OUTCAST'))],
 'TOY_641':[('historical_draw_batch',(('type','eq','MINION'),('tribe','eq','DEMON')),'discount',(2,),'random')],
 'WW_412':[('historical_excavate_dig',False)],
 'TSC_913':[('insert_fixed','TSC_913t',1,'bottom')],
}
LOCATION_RULES={
 'ETC_449':'none','ETC_533':'friendly_minion','JAM_009':'none',
 'MIS_919':'enemy_minion','REV_290':'minion','REV_333':'friendly_minion',
 'REV_362':'friendly_minion','REV_371':'friendly_minion','REV_602':'minion',
 'REV_923':'friendly_minion','REV_983':'minion','REV_990':'minion',
 'TOY_507':'none','TOY_850':'none','TOY_359':'none',
 'TTN_465':'friendly_minion','DEEP_019':'damaged_minion',
}
LOCATION_EFFECTS={
 'ETC_449':[('historical_equipment_fan_club',)],
 'ETC_533':[('historical_equipment_reborn',)],
 'JAM_009':[('board_keyword','RUSH')],
 'MIS_919':[('historical_copy_target_delivery','hand',1,1,1,1,False)],
 'REV_290':[('buff',2,1),('draw',1)],
 'REV_333':[('historical_batch_trigger_target_death',)],
 'REV_362':[('buff',2,0),('historical_equipment_kennels',)],
 'REV_371':[('historical_equipment_library',)],
 'REV_602':[('freeze',),('summon','REV_845',1)],
 'REV_923':[('historical_family_evolve_target',1)],
 'REV_983':[('set_target_stats',3,3)],
 'REV_990':[('historical_equipment_depths',)],
 'TOY_507':[('historical_draw_batch',(('type','eq','MINION'),('mechanic','eq','BATTLECRY')),'discount',(1,),'random')],
 'TOY_850':[('historical_equipment_dollhouse',)],
 'TOY_359':[('historical_equipment_gym',)],
 'TTN_465':[('historical_equipment_giant',)],
 'DEEP_019':[('historical_equipment_expanse',)],
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|frozenset(LOCATION_RULES)


def split(game,op,ctx):
 if op[0]!='historical_equipment_gym':return None
 count=1+sum(has_tribe(game._card_data(m),'BEAST') for m in game.players[ctx['owner']].minions)
 return game._split_fixed_summon(('missiles','enemies',count),ctx)


def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
 if name=='historical_equipment_fan_club':
  for uid in (game.hero_id(owner),)+tuple(m.uid for m in p.minions):game._heal(uid,3,healer=owner,spell=False)
 elif name=='historical_equipment_reborn':
  if target is not None and target.owner==owner and p.corpses>=3:
   game._spend_corpses(owner,3);target.keywords.add('REBORN')
 elif name=='historical_equipment_kennels':
  if target is not None and has_tribe(game._card_data(target),'BEAST'):target.keywords.add('RUSH')
 elif name=='historical_equipment_library':
  from .historical_imps import is_imp
  count=1+sum(is_imp(game,m) for m in p.minions)
  if target is not None:game._buff(target,count,count)
 elif name=='historical_equipment_depths':
  if target is not None:
   game._deal_effect(target.uid,1,ctx)
   if target.health>0 and target in game.players[target.owner].minions:game._buff(target,2,0)
 elif name=='historical_equipment_dollhouse':
  entries=getattr(p,'historical_location_spell_bonuses',[])
  p.historical_location_spell_bonuses=entries+[dict(turn=game.turn,amount=1)]
 elif name=='historical_equipment_giant':
  if target is not None:game._summon(owner,'TTN_465t',entry_stats=(target.attack,target.health),entry_origin='effect',entry_site='forge_of_wills')
 elif name=='historical_equipment_expanse':
  if target is not None and target.health<target.max_health:
   game._summon(owner,target.card_id,copy_from=target,dormant_turns=1,entry_origin='copy',entry_site='crimson_expanse',entry_source=target)
 else:return False
 return True
