"""Explicit frozen historical hand/hero primitives, generated dependencies only.

No generation membership is inferred and no text is interpreted at runtime.
"""
from .historical_saidan import add as _saidan_add
RULES={
 'AT_105':('none',[('damage_self',3)]),
 'BAR_069':('none',[('damage_self',6)]),
 'BOT_448':('none',[('damage_self',6)]),
 'VAC_934':('none',[('damage_self',10)]),
 'AT_111':('none',[('historical_heroes_heal',4)]),
 'BAR_309':('none',[('historical_heroes_heal',5)]),
 'DMF_066':('none',[('historical_heroes_damage',4)]),
 'GVG_009':('none',[('historical_heroes_damage',3)]),
 'UNG_803':('none',[('historical_heroes_damage',1)]),
 'VAC_419':('none',[('historical_heroes_damage',4)]),
 'CFM_334':('none',[('historical_hand_buff','BEAST',None,2,2,True)]),
 'CFM_338':('none',[('historical_hand_buff','BEAST',None,1,1,True)]),
 'CFM_650':('none',[('historical_hand_buff','MURLOC',None,1,1,True)]),
 'CFM_685':('none',[('historical_hand_buff',None,None,5,5,True)]),
 'CFM_853':('none',[('historical_hand_buff',None,None,1,1,True)]),
 'DAL_147':('none',[('historical_hand_buff','DRAGON',None,3,3,False)]),
 'DMF_189':('none',[('historical_hand_buff',None,None,2,2,True)]),
 'DMF_531':('none',[('historical_hand_buff',None,None,1,1,True)]),
 'ULD_256':('none',[('taunt_hand_buff',2,2)]),
 'TSC_632':('none',[('historical_hand_buff','MECHANICAL',None,1,1,True)]),
 'GDB_722':('none',[('historical_hand_buff','DRAENEI',None,2,1,False)]),
 'SW_315':('none',[('filtered_draw',(('type','eq','MINION'),),1),('hand_buff',1,1)]),
}
DEATH_EFFECTS={
 'CFM_120':[('historical_heroes_heal',4)],
 'CFM_336':[('historical_hand_buff',None,None,2,2,True)],
 'DRG_049':[('historical_hand_buff','DRAGON',None,2,2,True)],
 'TSC_614':[('historical_hand_buff','MURLOC',None,1,1,False)],
 'BOT_443':[('historical_hand_buff','DEMON',None,1,1,False)],
 'GDB_722':RULES['GDB_722'][1],
}
END_EFFECTS={
 'CFM_639':[('hand_buff',1,1)],
 'CFM_754':[('historical_hand_buff',None,None,2,2,True)],
 'ETC_105':[('historical_hand_buff',None,None,2,2,True)],
 'ULD_258':[('taunt_hand_buff',2,2)],
}
START_EFFECTS={'BAR_033':('owner',[('hand_buff',1,1)])}
for cid in DEATH_EFFECTS.keys()|END_EFFECTS.keys()|START_EFFECTS.keys():
 RULES.setdefault(cid,('none',[]))
GENERATED_IDS=frozenset(RULES)

class HistoricalHandPrimitives:
 def _historical_hand_effect(self,op,ctx):
  name=op[0];owner=ctx['owner']
  if name=='historical_hand_buff':
   tribe,keyword,attack,health,random_one=op[1:]
   eligible=[]
   for c in self.players[owner].hand:
    data=self.cards[c.card_id]
    races=data.get('races') or (data.get('race'),)
    if data['type']=='MINION' and (tribe is None or tribe in races or 'ALL' in races) and (keyword is None or keyword in self._card_mechanics(c)):
     eligible.append(c)
   if random_one and eligible:eligible=[self.rng.choice(eligible)]
   for c in eligible:_saidan_add(c,'attack_bonus',attack);_saidan_add(c,'health_bonus',health)
  elif name=='historical_heroes_heal':
   for player in (owner,1-owner):self._heal(self.hero_id(player),op[1],healer=owner,spell=ctx.get('spell',False))
  elif name=='historical_heroes_damage':
   for player in (owner,1-owner):self._deal_effect(self.hero_id(player),op[1],ctx)
  else:return False
  return True
