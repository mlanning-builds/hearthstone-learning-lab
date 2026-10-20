"""Explicit keyword/dormancy recipes, separate from complete Zombeast pools.

These records do not install either production offer stage. Historical identity
policy, non-obstructive text exceptions, All-type inheritance and complete
stage membership still require review. No runtime rules-text classification.
"""
from .minion_forge import ForgePart
SOURCE='Pinned 36.6.0.251952 printed component behavior; membership reviewed separately'
KEYWORDS={
 'CORE_EX1_028':('STEALTH',),'CORE_GIL_558':('LIFESTEAL',),'TIME_053':(),
 'CS2_119':(),'CS2_120':(),'CS2_125':('TAUNT',),'CS2_127':('TAUNT',),
 'CS2_169':('WINDFURY',),'CS2_171':('CHARGE',),'CS2_172':(),
 'DMF_190':('WINDFURY',),'DRG_065':('RUSH','TAUNT'),
 'DRG_066':('ELUSIVE','POISONOUS'),'EX1_017':('STEALTH',),'EX1_170':('POISONOUS',),
 'GIL_143':('LIFESTEAL','RUSH'),'GIL_562':('POISONOUS','RUSH'),
 'GVG_071':(),'ICC_023':(),'ICC_419':('ELUSIVE',),'ICC_905':('LIFESTEAL',),
 'LEG_CS3_037':('RUSH',),'LOOT_125':('DIVINE_SHIELD','POISONOUS'),'LOOT_258':(),
 'OG_325':(),'OG_326':(),'UNG_808':('POISONOUS','TAUNT'),'UNG_810':('TAUNT',),
 'UNG_814':('POISONOUS','STEALTH'),
}
PARTS={cid:ForgePart(cid,keywords=keywords,source=SOURCE) for cid,keywords in KEYWORDS.items()}
PARTS.update({
 'TIME_046':ForgePart('TIME_046',keywords=('TAUNT',),source=SOURCE,intrinsics=(('dormant_turns',3),)),
 'TSC_647':ForgePart('TSC_647',keywords=('RUSH',),source=SOURCE,intrinsics=(('dormant_turns',1),)),
 'DMF_532':ForgePart('DMF_532',keywords=('TAUNT',),source=SOURCE),
 'GIL_681':ForgePart('GIL_681',source=SOURCE),
 'NX2_050':ForgePart('NX2_050',source=SOURCE),
})
