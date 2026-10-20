"""Explicit historical generation declarations, separate from pool closure.

Every pool uses its complete generation contract. No outcome membership is
inferred from rules text or restricted to implemented cards. A missing outcome
still fails before sampling; a written body is not a closed generation pool.
"""
from .generation_cards import pool,random_cards,discover,PoolRequest


def random(request,count=1,destination='hand'):
 return random_cards(request,count,destination)


def choose(**kwargs):
 kwargs.setdefault('classes','own_or_neutral')
 return discover(pool(**kwargs))

RULES={
 'AT_118':('none',[random(pool(classes='PALADIN'))]),
 'BOT_533':('none',[random(pool(card_type='MINION',tribe='ELEMENTAL'))]),
 'BOT_539':('none',[choose(card_type='SPELL',minimum=5)]),
 'DAL_163':('none',[choose(card_type='MINION',classes='MAGE')]),
 'DAL_416':('none',[choose(card_type='SPELL',classes='other')]),
 'DMF_122':('none',[choose(card_type='SPELL',mechanic='SECRET')]),
 'ETC_326':('none',[choose(card_type='MINION',rarity='LEGENDARY')]),
 'EX1_188':('none',[random(pool(card_type='MINION',tribe='BEAST'),destination='board')]),
 'GIL_212':('none',[random(pool(card_type='MINION',minimum=1,maximum=1),2)]),
 'GIL_549':('none',[random(pool(era='past',card_type='MINION',rarity='LEGENDARY'))]),
 'GVG_042':('none',[random(pool(card_type='MINION',tribe='MURLOC'),4)]),
 'KAR_009':('none',[random(pool(card_type='SPELL',classes='MAGE'))]),
 'LOE_003':('none',[choose(card_type='SPELL')]),
 'LOE_006':('none',[discover(pool(mechanic='DEATHRATTLE',classes='own_or_neutral'),cost_delta=-1)]),
 'LOE_023':('none',[choose(minimum=1,maximum=1)]),
 'LOE_029':('none',[choose(minimum=3,maximum=3)]),
 'LOE_047':('none',[choose(card_type='MINION',tribe='BEAST')]),
 'OG_207':('none',[random(pool(card_type='MINION',minimum=3,maximum=3),destination='board')]),
 'RLK_547':('none',[discover(pool(card_type='SPELL'),cost_delta=-1)]),
 'SW_059':('none',[discover(pool(card_type='MINION',tribe='MECHANICAL',classes='own_or_neutral'),cost_delta=-1)]),
 'TOY_006':('none',[choose(minimum=2,maximum=2)]),
 'TTN_714':('none',[choose(card_type='WEAPON',classes='any')]),
 'ULD_186':('none',[random(pool(card_type='MINION',mechanic='REBORN'))]),
 'ULD_188':('none',[choose(minimum=4,maximum=4)]),
 'UNG_078':('none',[random(pool(card_type='MINION',attack_minimum=5))]),
 'UNG_846':('none',[random(pool(card_type='SPELL',classes='MAGE'))]),
 'VAC_430':('none',[choose(card_type='MINION',tribe='PIRATE')]),
 'VAC_438':('none',[choose(card_type='LOCATION',classes='any')]),
 'WON_056':('none',[discover(pool(mechanic='DEATHRATTLE',classes='own_or_neutral'),cost_delta=-1)]),
}
DEATH_EFFECTS={
 'BOT_401':[random(pool(card_type='MINION',rarity='LEGENDARY'))],
 'DAL_587':[random(pool(card_type='SPELL',classes='HUNTER'))],
 'GIL_816':[random(pool(card_type='MINION',tribe='DRAGON'))],
 'GVG_096':[random(pool(card_type='MINION',minimum=2,maximum=2),destination='board')],
 'GVG_105':[random(pool(card_type='MINION',minimum=4,maximum=4),destination='board')],
 'ICC_027':[random(pool(card_type='MINION',tribe='DRAGON'))],
 'ICC_702':[random(pool(card_type='MINION',mechanic='DEATHRATTLE'))],
 'LOE_050':[random(pool(card_type='MINION',minimum=1,maximum=1),destination='board')],
 'RLK_914':[random(pool(card_type='SPELL',school='SHADOW'))],
 'SW_006':[random(pool(card_type='MINION',minimum=3,maximum=3),destination='board')],
 'ULD_282':[random(pool(card_type='MINION',minimum=1,maximum=1))],
}
END_EFFECTS={
 'CFM_663':[random(pool(card_type='MINION',tribe='DEMON'))],
 'DAL_553':[random(pool(card_type='MINION',minimum=6,maximum=6),destination='board')],
 'LOOT_394':[random(pool(card_type='MINION',minimum=1,maximum=1),destination='board')],
}
TRIGGERS={
 'AT_018':('hero_power_used',[random(pool(card_type='MINION',rarity='LEGENDARY'),destination='board')]),
 'WON_063':('hero_power_used',[random(pool(card_type='MINION',rarity='LEGENDARY'),destination='board')]),
 'AT_076':('hero_power_used',[random(pool(card_type='MINION',tribe='MURLOC'),destination='board')]),
 'AT_127':('hero_power_used',[random(pool(card_type='SPELL'))]),
 'WON_328':('hero_power_used',[('buff_others',1,1)]),
 'WON_058':('hero_power_used',[('historical_heroes_damage',4)]),
 'AT_110':('hero_power_used',[('historic_bounce_source',)]),
}
RULES.update({
 'AT_018':('none',TRIGGERS['AT_018'][1]),
 'WON_063':('none',TRIGGERS['WON_063'][1]),
 'WON_058':('none',[('historical_heroes_damage',4)]),
 'BAR_065':('none',[choose(card_type='SPELL')]),
 'DRG_102':('none',[choose(card_type='MINION',tribe='DRAGON')]),
 'DRG_229':('none',[choose(card_type='MINION',tribe='DRAGON')]),
 'DRG_254':('none',[choose(card_type='MINION',tribe='DRAGON')]),
 'DRG_313':('none',[choose(card_type='MINION',tribe='DRAGON')]),
 'REV_947':('none',[choose(classes='PALADIN')]),
 'SCH_245':('none',[choose(card_type='SPELL')]),
 'ULD_195':('none',[choose(card_type='MINION',mechanic='TAUNT')]),
 'ULD_309':('none',[discover(pool(classes='own_or_neutral'),cost_delta=-1)]),
 'TTN_484':('none',[discover(pool(era='past',card_type='MINION',rarity='LEGENDARY',classes='PRIEST'))]),
 'REV_945':('none',[discover(pool(card_type='SPELL',mechanic='SECRET',classes='other'))]),
 'YOG_524':('none',[random(pool(mechanic='OVERLOAD'))]),
 'JAM_032':('none',[random(pool(card_type='SPELL',school='FIRE',classes='MAGE')),random(pool(card_type='SPELL',school='FIRE',classes='WARLOCK'))]),
 'BRM_030':('none',[('historic_opponent_class_generate','SPELL',2)]),
 'GIL_827':('none',[('historic_opponent_class_generate',None,1)]),
 'BRM_026':('none',[('historic_opponent_one_cost_summon',)]),
 'LOOT_154':('none',[('historic_opponent_one_cost_summon',)]),
 'EX1_306':('none',[('discard',1)]),
 'OG_109':('none',[('discard',1)]),
})
DEATH_EFFECTS.update({
 'ETC_349':[random(pool(era='past',card_type='MINION',minimum=5,maximum=5),destination='board')],
 'OG_330':[('historic_opponent_class_generate',None,1)],
 'WON_317':[('historic_opponent_class_generate',None,1)],
 'OG_109':[('draw',1)],
 'LOE_061':[('buff_random_other',3,3)],
 'RLK_957':[('buff_random_other',2,1,'UNDEAD')],
 'WON_138':[('buff_random_other',2,2,'PIRATE')],
 'FP1_022':[('summon_from_zone','hand',(('type','eq','MINION'),('tribe','eq','DEMON')))],
 'BT_509':[('summon_from_zone','hand',(('type','eq','MINION'),('tribe','eq','DEMON')))],
})
END_EFFECTS.update({
 'WON_108':[('historical_hand_buff',None,None,2,2,True)],
 'BT_486':[('summon_from_zone','deck',(('type','eq','MINION'),('tribe','eq','DEMON')))],
})
TRIGGERS.update({
 'DAL_774':('spell_cast',[random(pool(card_type='MINION',tribe='BEAST',minimum=3,maximum=3),destination='board')]),
 'GIL_664':('spell_cast',[random(pool(card_type='MINION',minimum=2,maximum=2),destination='board')]),
 'GIL_807':('spell_cast',[('filtered_draw',(('type','eq','MINION'),),1)]),
 'GIL_819':('b60_friendly_death',[random(pool(card_type='SPELL',classes='SHAMAN'))]),
 'ETC_540':('spell_cast',[random(pool(card_type='SPELL',school='FIRE'))]),
 'ULD_329':('spell_cast',[random(pool(card_type='MINION',classes='MAGE'))]),
 'UNG_963':('spell_cast',[random(pool(card_type='SPELL',classes='PRIEST'))]),
})
RULES.update({
 'CFM_321':('none',[('historical_union_discover',tuple(pool(classes=c) for c in ('HUNTER','PALADIN','WARRIOR')))]),
 'CFM_649':('none',[('historical_union_discover',tuple(pool(classes=c) for c in ('MAGE','PRIEST','WARLOCK')))]),
 'CFM_852':('none',[('historical_union_discover',tuple(pool(classes=c) for c in ('DRUID','ROGUE','SHAMAN')))]),
 'WON_130':('none',[('historical_union_discover',tuple(pool(classes=c) for c in ('MAGE','PRIEST','WARLOCK')))]),
 'WON_331':('none',[('historical_union_discover',tuple(pool(classes=c) for c in ('HUNTER','PALADIN','WARRIOR')))]),
 'WON_332':('none',[('historical_union_discover',tuple(pool(classes=c) for c in ('DRUID','ROGUE','SHAMAN')))]),
 'BAR_030':('none',[('historical_union_discover',(pool(card_type='MINION',tribe='BEAST',classes='own_or_neutral'),pool(card_type='SPELL',mechanic='SECRET',classes='own_or_neutral'),pool(card_type='WEAPON',classes='own_or_neutral')))]),
})

RULES.update({
 'WON_045':('none',[discover(pool(card_type='SPELL',classes='own_or_neutral'),heal_cost=True)]),
 'DAL_609':('none',[choose(card_type='SPELL')]),
 'TTN_925':('none',[choose(card_type='SPELL',classes='other',maximum=3)]),
 'SCH_350':('none',[('historical_if_combo',choose(card_type='SPELL',classes='MAGE'))]),
 'ETC_077':('none',[('historical_if_combo',random(pool(mechanic='COMBO')))]),
})
DEATH_EFFECTS.update({
 'DEEP_005':[random(pool(card_type='MINION',mechanic='DEATHRATTLE',maximum=3),2,'board')],
 'TSC_645':[random(pool(card_type='MINION',tribe='MECHANICAL',maximum=3),2,'board')],
 'GDB_862':[random_cards(pool(card_type='SPELL',school='HOLY'),2,cost_delta=-3)],
 'WORK_010':[random(pool(card_type='MINION',minimum=8,maximum=8),destination='board')],
})
RULES.update({cid:('none',[('autocast_random',pool(card_type='SPELL',minimum=5),1)]) for cid in ('OG_087','WON_036')})
END_EFFECTS['SCH_537']=[('autocast_random',pool(card_type='SPELL',maximum=3),1)]

SPELL_DAMAGE_VALUES={'DRG_102':2,'SCH_245':1}
for cid in TRIGGERS:RULES.setdefault(cid,('none',[]))

for cid in DEATH_EFFECTS.keys()|END_EFFECTS.keys():RULES.setdefault(cid,('none',[]))
GENERATED_IDS=frozenset(RULES)


def requests_for(cid):
 result=set()
 def walk(value):
  if isinstance(value,PoolRequest):result.add(value)
  elif isinstance(value,(tuple,list)):
   for child in value:walk(child)
 walk(RULES.get(cid,()));walk(DEATH_EFFECTS.get(cid,()));walk(END_EFFECTS.get(cid,()));walk(TRIGGERS.get(cid,()))
 return result
