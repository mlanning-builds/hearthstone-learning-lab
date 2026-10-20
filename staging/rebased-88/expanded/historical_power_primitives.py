"""Explicit pinned Inspire and fixed-action historical minions.

These generated dependencies do not enter Standard deck construction and do
not alter the membership of any random pool. Metadata supplies printed stats
and keywords; each action and owner-only Inspire trigger is listed explicitly.
"""
TRIGGERS={
 'AT_012':('hero_power_used',[('historical_heroes_damage',4)]),
 'AT_039':('hero_power_used',[('hero_attack',2)]),
 'AT_066':('hero_power_used',[('weapon_buff',1,0)]),
 'AT_082':('hero_power_used',[('buff_self',1,0)]),
 'AT_083':('hero_power_used',[('temporary_keyword_self','WINDFURY','end')]),
 'AT_089':('hero_power_used',[('buff_self',0,1)]),
 'AT_090':('hero_power_used',[('buff_others',1,1)]),
 'AT_091':('hero_power_used',[('heal_own_hero',2)]),
 'AT_100':('hero_power_used',[('summon','CS2_101t',1)]),
 'AT_113':('hero_power_used',[('add','CS2_152',1)]),
 'AT_119':('hero_power_used',[('buff_self',2,2)]),
}
RULES={cid:('none',[]) for cid in TRIGGERS}
RULES.update({
 'AT_012':('none',[('historical_heroes_damage',4)]),
 'AT_009':('none',[]),
 'AT_094':('none',[('damage_random_enemy',1)]),
 'AT_057':('friendly_beast',[('temporary_keyword_target','IMMUNE','end')]),
})
DEATH_EFFECTS={'AT_009':[('add','EX1_277',3)]}
TOKEN_RULES={'CS2_152':('none',[])}
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
