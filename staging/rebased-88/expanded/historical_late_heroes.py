"""Tamsin's physical Rifts and Rokara's damage/weapon programs."""
ROOT_RULES={
 'AV_316':('none',[('area_damage','all_minions',3),('on_draw_shuffle','AV_316t4',3,0),('draw',3)]),
 'AV_202':('none',[('equip','AV_202t2')]),
}
TOKEN_RULES={'AV_316t':('none',[]),'AV_316t4':('none',[('summon','AV_316t',1)]),'AV_202t2':('none',[])}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'AV_316hp','AV_202p'}

def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];player=game.players[owner]
 if name=='historical_late_slam':
  uid=ctx.get('target',0)
  victim=next((m for other in game.players for m in other.minions if m.uid==uid),None)
  health=victim.health if victim is not None else None
  previous=getattr(player,'historical_power_damage_total',0)
  game._effect(('historical_copy_power_hit','target',2),ctx)
  dealt=getattr(player,'historical_power_damage_total',0)-previous
  if victim is not None and health>0 and victim.health<=0 and dealt==health:game._gain_armor(owner,4)
  return True
 if name=='historical_late_smash':
  if ctx.get('target',0)<=0:return True
  amount=ctx.get('attack_target_attack',0)
  keywords=ctx.get('attack_keywords',())
  game._deal_effect(game.hero_id(1-owner),amount,dict(owner=owner,source=None,target=game.hero_id(1-owner),spell=False,bonus=0,lifesteal='LIFESTEAL' in keywords,poisonous='POISONOUS' in keywords))
  return True
 return False
