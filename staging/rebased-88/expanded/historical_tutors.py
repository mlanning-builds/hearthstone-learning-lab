"""Explicit printed historical draw selectors; physical deck draws, no generation."""
def draw(*filters,count=1,discount=0):
 return ('filtered_draw',tuple(filters),count,*((-discount,) if discount else ()))
SPELL=('type','eq','SPELL');MINION=('type','eq','MINION')
RULES={
 'AV_101':('none',[draw(SPELL,('school','eq','FROST'))]),
 'BAR_873':('none',[draw(SPELL,('school','eq','HOLY'))]),
 'BOT_291':('none',[draw(SPELL,('cost','ge',5))]),
 'BAR_551':('none',[draw(SPELL,('cost','eq',n)) for n in (1,2,3)]),
 'DMF_525':('none',[draw(MINION,('tribe','eq',tribe)) for tribe in ('MECHANICAL','DRAGON','PIRATE')]),
 'DMF_704':('none',[draw(('type','eq','WEAPON'))]),
 'DRG_010':('none',[draw(MINION,('mechanic','eq','RUSH'))]),
 'GIL_580':('none',[draw(MINION,('mechanic','eq','RUSH'))]),
 'GIL_581':('none',[draw(MINION,('tribe','eq','ELEMENTAL'))]),
 'ICC_801':('none',[draw(MINION,('mechanic','eq','DIVINE_SHIELD'))]),
 'LOOT_033':('none',[draw(('type','eq','WEAPON'))]),
 'NEW1_016':('none',[draw(MINION,('tribe','eq','PIRATE'))]),
 'NX2_014':('none',[draw(SPELL,('cost','eq',1))]),
 'SW_029':('none',[draw(MINION,('tribe','eq','PIRATE'))]),
 'TOY_517':('none',[draw(MINION,('mechanic','eq','RUSH'))]),
 'TSC_034':('none',[draw(MINION,('tribe','eq','MURLOC'),count=3)]),
 'UNG_020':('none',[draw(('mechanic','eq','SECRET'))]),
 'UNG_913':('none',[draw(MINION,('cost','eq',1),count=2)]),
 'ETC_418':('none',[draw(('type','eq','WEAPON'))]),
 'SW_043':('none',[draw(SPELL,('school','eq','FEL'),discount=2)]),
 'WON_139':('none',[draw(MINION,('tribe','eq','MECHANICAL'),discount=2)]),
 'WW_351':('none',[draw(MINION,('tribe','eq','BEAST'),discount=3)]),
}
GENERATED_IDS=frozenset(RULES)
