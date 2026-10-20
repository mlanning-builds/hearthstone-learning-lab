"""Explicit reviewed shared-system recipes; outcome admission remains mandatory."""
from . import leylines,maps,remaining_setup,stat_rules,counterfeits,evolving_locations,fabled_effects,titanographer,turn_deadlines,quest_families
RULES={}
for module,ids in (
 (leylines,('MEND_501','MEND_502','MEND_505')),
 (maps,('TLC_435','TLC_464','TLC_824')),
 (remaining_setup,('CATA_614','JAIL_831')),
 (stat_rules,('CATA_213',)),
 (counterfeits,('JAIL_504',)),
 (evolving_locations,('TIME_217','TIME_436','CATA_527','FIR_907')),
 (fabled_effects,('TIME_211','TIME_609','TIME_619','TIME_890')),
 (titanographer,('TLC_452',)),
 (turn_deadlines,('TLC_602',)),
 (quest_families,('TLC_830',)),
):
 for cid in ids:RULES[cid]=module.RULES[cid]
COLLECTIBLE_IDS=frozenset(RULES)
TOKEN_RULES=dict(leylines.TOKEN_RULES)
TOKEN_RULES.update(counterfeits.TOKEN_RULES)
TOKEN_RULES.update({cid:fabled_effects.TOKEN_RULES[cid] for cid in (*fabled_effects.SISTERS[1:],'TIME_619t','TIME_619t2','TIME_890t')})
TOKEN_RULES.update(titanographer.TOKEN_RULES)
TOKEN_RULES.update({cid:quest_families.TOKEN_RULES[cid] for cid in ('TLC_830t',)})
TOKEN_RULES.update({'CATA_527t2':('none',[]),'JAIL_504tt01':('none',[]),'CFM_621_m2':('none',[])})
LOCATION_RULES={cid:evolving_locations.LOCATION_RULES[cid] for cid in ('TIME_436','TIME_436t1','TIME_436t2','CATA_527','FIR_907')}
LOCATION_RULES.update({cid:fabled_effects.LOCATION_RULES[cid] for cid in (*fabled_effects.azshara.WELL,*fabled_effects.azshara.ZIN,'TIME_890t2')})
LOCATION_EFFECTS={cid:fabled_effects.LOCATION_EFFECTS[cid] for cid in (*fabled_effects.azshara.WELL,*fabled_effects.azshara.ZIN,'TIME_890t2')}
TOKEN_IDS=frozenset(TOKEN_RULES)|frozenset(set(LOCATION_RULES)-COLLECTIBLE_IDS)|frozenset(titanographer.TOKENS)|frozenset(fabled_effects.BOONS)
DEATH_EFFECTS={cid:leylines.DEATH_EFFECTS[cid] for cid in ('MEND_501',)}
DEATH_EFFECTS['TIME_619t']=fabled_effects.DEATH_EFFECTS['TIME_619t']
TRIGGERS={'CATA_527t2':evolving_locations.TRIGGERS['CATA_527t2']}
CHOICES={'TIME_211':fabled_effects.CHOICES['TIME_211']}
