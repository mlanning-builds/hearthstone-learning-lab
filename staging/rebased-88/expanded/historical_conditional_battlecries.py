"""Printed historical holding/Combo effects with explicit conditional targets.

No Discover or random-generation pool is inferred. Holding checks occur after
removing the played physical card, so it cannot satisfy its own Dragon condition.
"""
from .selectors import has_tribe
DRAGON=(('tribe','eq','DRAGON'),)
def held(*ops):return [('if_holding',DRAGON,op) for op in ops]
def combo(*ops):return [('historical_if_combo',op) for op in ops]
RULES={
 'JAM_021':('none',combo(('keyword_self','POISONOUS'))),
 'AT_017':('none',held(('buff_self',1,0),('keyword_self','TAUNT'))),
 'AT_071':('none',held(('buff_self',1,0),('keyword_self','CHARGE'))),
 'AT_116':('none',held(('buff_self',1,0),('keyword_self','TAUNT'))),
 'BRM_004':('none',held(('buff_self',0,2))),
 'BRM_033':('none',held(('buff_self',1,1))),
 'BT_262':('none',held(('buff_self',1,0),('keyword_self','LIFESTEAL'))),
 'GIL_526':('none',held(('buff_self',1,0),('keyword_self','TAUNT'))),
 'GIL_601':('none',held(('buff_self',1,0),('keyword_self','RUSH'))),
 'GIL_635':('none',held(('keyword_self','TAUNT'),('keyword_self','DIVINE_SHIELD'))),
 'KAR_010':('none',held(('summon','KAR_010a',2))),
 'ONY_001':('none',held(('summon','ONY_001t',2))),
 'RLK_916':('none',held(('buff_self',1,1))),
 'TRL_323':('none',held(('armor',5))),
 'WW_819':('none',held(('empty_crystals','friendly',1))),
 'WW_826':('none',held(('refresh_mana',4))),
 'DRG_201':('none',held(('area_damage','other_characters',3))),
 'LOOT_410':('none',held(('area_damage','other_minions',3))),
 'YOD_036':('none',held(('destroy_random_enemy',1))),
 'BRM_029':('historical_held_legendary',held(('destroy',))),
 'BRM_034':('historical_held_character',held(('damage',5))),
 'DRG_081':('historical_held_character',held(('damage',2))),
 'RLK_915':('historical_held_character',held(('damage',3))),
 'WON_329':('historical_held_character',held(('damage',5))),
 'WW_820':('historical_held_enemy',held(('damage',5))),
 'TRL_569':('historical_held_enemy',held(('damage',7))),
 'TRL_326':('historical_held_damaged_enemy',held(('destroy',))),
 'KAR_033':('historical_held_small_enemy',held(('destroy',))),
 'LOOT_528':('historical_held_minion',held(('historical_swap_source_attack',))),
 'AT_028':('none',combo(('buff_self',4,0))),
 'WON_316':('none',combo(('buff_self',4,0))),
 'AV_201':('none',combo(('buff_self',3,0))),
 'OG_070':('none',combo(('buff_self',1,1))),
 'EX1_131':('none',combo(('summon','EX1_131t',1))),
 'GIL_902':('none',combo(('weapon_buff',1,0))),
 'ETC_072':('none',combo(('missiles','enemies',4))),
 'LOOT_211':('none',combo(('filtered_draw',(('type','eq','MINION'),),2))),
 'AT_030':('combo_character',[('combo_damage',1)]),
 'EX1_134':('combo_character',[('combo_damage',3)]),
 'BOT_576':('combo_friendly_minion',[('combo_buff',4,0)]),
 'ICC_809':('combo_friendly_minion',combo(('keyword','POISONOUS'))),
 'CFM_693':('combo_friendly_minion',combo(('historical_bounce_target',))),
 'NEW1_005':('historical_combo_minion',combo(('historical_bounce_target',))),
 'UNG_064':('historical_combo_minion',combo(('destroy',))),
 'EX1_613':('none',combo(('historical_combo_scaled_buff',2))),
 'UNG_063':('none',combo(('historical_combo_scaled_buff',1))),
 'DMF_519':('historical_combo_minion',combo(('historical_combo_scaled_damage',1))),
 'ICC_910':('historical_combo_minion',combo(('historical_combo_scaled_damage',2))),
 'YOD_017':('none',combo(('historical_combo_scaled_draw',))),
}
GENERATED_IDS=frozenset(RULES)
TOKEN_RULES={cid:('none',[]) for cid in ('KAR_010a','ONY_001t','EX1_131t')}
TOKEN_IDS=set(TOKEN_RULES)
DEATH_EFFECTS={
 'AT_123':held(('area_damage','all_minions',3)),
 'DRG_304':held(('area_damage','enemy_minions',3)),
}
RULES.update({cid:('none',[]) for cid in DEATH_EFFECTS})
GENERATED_IDS=frozenset(RULES)
HELD_MODES={'historical_held_legendary':'legendary_minion','historical_held_character':'character','historical_held_enemy':'enemy_minion','historical_held_damaged_enemy':'damaged_enemy_minion','historical_held_small_enemy':'enemy_minion','historical_held_minion':'minion'}
class HistoricalConditionalBattlecries:
 def _historical_conditional_card_targets(self,card,owner,targets=None):
  mode=RULES.get(card.card_id,('none',))[0]
  if mode not in HELD_MODES:return targets
  if not any(c is not card and has_tribe(self._card_data(c),'DRAGON') for c in self.players[owner].hand):return [0]
  if targets is None:targets=self._targets_for(card.card_id,owner,HELD_MODES[mode])
  if mode=='historical_held_small_enemy':targets=[uid for uid in targets if uid>0 and self._find(uid).attack<=3]
  return targets or [0]
 def _historical_conditional_targets(self,cid,owner,mode):
  if mode in HELD_MODES:
   if not self._holding_matches(owner,DRAGON):return [0]
   targets=self._targets_for(cid,owner,HELD_MODES[mode])
   if mode=='historical_held_small_enemy':targets=[uid for uid in targets if uid>0 and self._find(uid).attack<=3]
   return targets or [0]
  if mode=='historical_combo_minion':
   return self._targets_for(cid,owner,'minion') if self.players[owner].cards_played else [0]
  return None
 def _historical_conditional_split(self,op,ctx):
  if op[0]=='historical_if_combo':
   return self._split_fixed_summon(op[1],ctx) if ctx.get('combo') else (('batch30_noop',),())
  if op[0]=='historical_combo_scaled_draw':
   count=ctx.get('prior_card_count',self.players[ctx['owner']].cards_played)
   return self._split_fixed_summon(('draw',count),ctx)
  return None
 def _historical_conditional_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];source=ctx.get('source');target=ctx.get('target',0)
  if name=='historical_if_combo':
   if ctx.get('combo'):self._effect(op[1],ctx)
  elif name.startswith('historical_combo_scaled_'):
   count=ctx.get('prior_card_count',self.players[owner].cards_played)
   if name=='historical_combo_scaled_buff':self._buff(source,op[1]*count,op[1]*count)
   elif name=='historical_combo_scaled_damage':self._deal_effect(target,op[1]*count,ctx)
   else:return False
  elif name=='historical_bounce_target':
   if target:self._bounce(self._find(target))
  elif name=='historical_swap_source_attack':
   if source is not None and target:
    other=self._find(target);a,b=source.attack,other.attack
    self._set_minion_attack(source,b);self._set_minion_attack(other,a)
  else:return False
  return True
