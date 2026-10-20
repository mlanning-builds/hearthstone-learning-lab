"""Exact fixed historical weapon, friendly tribe and temporary self buffs."""
from .selectors import has_tribe
RULES={
 'BAR_061':('none',[('weapon_buff',1,0)]),
 'BOT_083':('none',[('weapon_buff',1,0)]),
 'CFM_651':('none',[('weapon_buff',1,0)]),
 'GVG_023':('none',[('weapon_buff',1,0)]),
 'NEW1_024':('none',[('weapon_buff',1,1)]),
 'ETC_102':('none',[('weapon_buff',0,1)]),
 'AT_040':('friendly_beast',[('buff',0,3)]),
 'AT_096':('historical_friendly_mech',[('buff',1,1)]),
 'BOT_079':('historical_friendly_mech',[('buff',1,1)]),
 'CFM_816':('friendly_beast',[('buff',3,3)]),
 'DAL_077':('historical_friendly_murloc',[('keyword','POISONOUS')]),
 'DS1_070':('friendly_beast',[('buff',2,2),('keyword','TAUNT')]),
 'EX1_191':('friendly_minion',[('keyword','POISONOUS')]),
 'EX1_587':('friendly_minion',[('keyword','WINDFURY')]),
 'GVG_055':('historical_friendly_mech',[('buff',2,2)]),
 'GVG_083':('historical_friendly_mech',[('buff',0,4)]),
 'ICC_092':('friendly_minion',[('buff',1,0)]),
 'ICC_705':('friendly_minion',[('buff',4,4),('keyword','TAUNT')]),
 'REV_351':('friendly_beast',[('buff',2,0)]),
 'RLK_119':('friendly_undead',[('keyword','REBORN')]),
 'UNG_073':('historical_friendly_murloc',[('buff',1,1)]),
 'VAC_937':('historical_friendly_pirate',[('keyword','WINDFURY')]),
 'WON_300':('friendly_beast',[('buff',3,3)]),
 'YOP_022':('friendly_minion',[('buff',3,3)]),
 'BT_720':('none',[('historical_temporary_self_attack',4)]),
 'GIL_803':('none',[('historical_temporary_self_attack',3)]),
}
GENERATED_IDS=frozenset(RULES)
TARGET_TRIBES={'historical_friendly_mech':'MECHANICAL','historical_friendly_murloc':'MURLOC','historical_friendly_pirate':'PIRATE'}
class HistoricalBattlecryBuffs:
 def _historical_buff_targets(self,cid,owner,mode):
  tribe=TARGET_TRIBES.get(mode)
  if tribe is None:return None
  # Reuse ordinary friendly targeting visibility, dormant and eligibility checks.
  return [uid for uid in self._targets_for(cid,owner,'friendly_minion')
          if uid>0 and has_tribe(self._card_data(self._find(uid)),tribe)] or [0]
 def _historical_buff_effect(self,op,ctx):
  if op[0]!='historical_temporary_self_attack':return False
  source=ctx.get('source')
  if source is not None:
   self._adjust_minion_attack(source,op[1]);source.temporary_attack+=op[1]
  return True
