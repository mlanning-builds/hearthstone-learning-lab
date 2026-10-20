"""Explicit historical destruction, mana and weapon primitives."""
from .selectors import has_tribe
RULES={
 'EX1_066':('none',[('destroy_enemy_weapon',)]),
 'LOOT_122':('none',[('destroy_enemy_weapon',)]),
 'DRG_069':('none',[('historical_remove_armor',)]),
 'ONY_035':('none',[('destroy_random_enemy',),('discard',1)]),
 'EX1_301':('none',[('destroy_crystals',1)]),
 'DMF_115':('none',[('historical_destroy_crystals_both',1)]),
 'AT_038':('none',[('empty_crystals','friendly',1)]),
 'GVG_120':('historical_remove_beast',[('destroy',)]),
 'BOT_540':('historical_remove_mech',[('destroy',)]),
 'AV_138':('historical_remove_enemy_legendary',[('destroy',)]),
 'LOOT_111':('historical_remove_one_attack',[('destroy',)]),
 'UNG_933':('none',[('historical_destroy_damaged',)]),
 'UNG_946':('none',[('historical_weapon_armor',)]),
 'EX1_558':('none',[('historical_weapon_draw',)]),
}
DEATH_EFFECTS={'DAL_039':[('destroy_random_enemy',)],'REV_251':[('destroy_random_enemy',)],'AT_038':[('destroy_crystals',1)]}
RULES.update({cid:('none',[]) for cid in DEATH_EFFECTS if cid not in RULES})
GENERATED_IDS=frozenset(RULES)
class HistoricalRemoval:
 def _historical_removal_targets(self,cid,owner,mode):
  if not mode.startswith('historical_remove_'):return None
  result=[]
  for uid in self._targets_for(cid,owner,'minion'):
   if uid<=0:continue
   m=self._find(uid);d=self._card_data(m)
   if (mode=='historical_remove_beast' and has_tribe(d,'BEAST') or
       mode=='historical_remove_mech' and has_tribe(d,'MECHANICAL') or
       mode=='historical_remove_enemy_legendary' and m.owner!=owner and d.get('rarity')=='LEGENDARY' or
       mode=='historical_remove_one_attack' and m.attack<=1):result.append(uid)
  return result or [0]
 def _historical_removal_split(self,op,ctx):
  if op[0]=='historical_weapon_draw':
   weapon=self.players[1-ctx['owner']].weapon
   return ('destroy_enemy_weapon',), (('draw',weapon['durability']),) if weapon else ()
  return None
 def _historical_removal_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];enemy=self.players[1-owner]
  if name=='historical_remove_armor':enemy.armor=0
  elif name=='historical_destroy_crystals_both':
   for recipient in (owner,1-owner):self._composed_effect(('destroy_crystals',op[1]),dict(ctx,owner=recipient))
  elif name=='historical_destroy_damaged':
   for player in self.players:
    for m in player.minions:
     if m.health<m.max_health:m.health=0
  elif name=='historical_weapon_armor':
   amount=enemy.weapon['attack'] if enemy.weapon else 0
   self._break_weapon(1-owner);self._gain_armor(owner,amount)
  else:return False
  return True
