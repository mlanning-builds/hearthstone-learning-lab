"""Literal Standard integrations with fixed dependencies.

These bindings connect existing shared handlers to the real registry. They do
not approve broad random pools or imply independent client certification.
"""
from . import colossal_bodies, colossals, herald

COLOSSALS=frozenset(('CATA_139','CATA_150','CATA_151','CATA_300','CATA_432','CATA_550','CATA_726'))
RULES={cid:colossal_bodies.RULES[cid] for cid in COLOSSALS}
RULES.update({'CS3_035':('none',[]),'JAIL_800':('none',[])})
TOKEN_IDS=frozenset(cid for root in COLOSSALS for cid,side in colossals.LAYOUTS[root])|frozenset(('CATA_725t','JAIL_800hp1','JAIL_800hp2'))
TOKEN_RULES={cid:('none',[]) for cid in TOKEN_IDS if cid not in ('JAIL_800hp1','JAIL_800hp2')}
DEATH_EFFECTS={cid:ops for cid,ops in {**herald.DEATH_EFFECTS,**colossal_bodies.DEATH_EFFECTS}.items() if cid in TOKEN_IDS or cid in COLOSSALS}
END_EFFECTS={cid:ops for cid,ops in {**herald.END_EFFECTS,**colossal_bodies.END_EFFECTS}.items() if cid in TOKEN_IDS or cid in COLOSSALS}
PLAYABLE_TOKENS=frozenset(TOKEN_RULES)

# Compound quests, a healing replacement and physical automatic card replay.
from . import quest_families, healing_replacement, automatic_casting
QUESTS=frozenset(('TLC_460','TLC_817'))
REWARDS=frozenset(('TLC_460t','TLC_817t','TLC_817t2','TLC_817t3','TLC_817t4','TLC_817t5'))
RULES.update({cid:quest_families.RULES[cid] for cid in QUESTS})
RULES['CATA_301']=('none',[])
LOCATION_RULES={'CATA_301':'none'}
LOCATION_EFFECTS={'CATA_301':healing_replacement.RULES['CATA_301'][1]}
RULES.update({cid:automatic_casting.RULES[cid] for cid in ('EDR_031','JAIL_500')})
TOKEN_RULES.update({cid:quest_families.TOKEN_RULES[cid] for cid in REWARDS})
TOKEN_IDS=TOKEN_IDS|REWARDS
PLAYABLE_TOKENS=PLAYABLE_TOKENS|REWARDS
DEATH_EFFECTS.update({cid:ops for cid,ops in quest_families.DEATH_EFFECTS.items() if cid in REWARDS})
END_EFFECTS['EDR_031']=automatic_casting.END_EFFECTS['EDR_031']

from . import imbue_consumers
RULES.update({cid:imbue_consumers.RULES[cid] for cid in ("EDR_860","EDR_888","FIR_921")})

from . import zone_triggers
RULES['JAIL_398']=zone_triggers.RULES['JAIL_398']
DEATH_EFFECTS['JAIL_398']=zone_triggers.DEATH_EFFECTS['JAIL_398']

from . import fabled_effects
RULES['TIME_852']=fabled_effects.RULES['TIME_852']
AZURE_TOKENS=frozenset(('TIME_852t1','TIME_852t3'))
TOKEN_RULES.update({cid:fabled_effects.TOKEN_RULES[cid] for cid in AZURE_TOKENS})
TOKEN_IDS|=AZURE_TOKENS
PLAYABLE_TOKENS|=AZURE_TOKENS

FINITE_IMBUE=frozenset(('EDR_226','EDR_227','EDR_845','EDR_871','EDR_519','END_003'))
RULES.update({cid:imbue_consumers.RULES[cid] for cid in FINITE_IMBUE})
DEATH_EFFECTS.update({cid:ops for cid,ops in imbue_consumers.DEATH_EFFECTS.items() if cid in FINITE_IMBUE})

from . import rafaam,garona,muradin,broxigar
FINITE_FABLED=(rafaam,garona,muradin,broxigar)
WEAPON_TRIGGERS={}
for family in FINITE_FABLED:
    RULES.update(family.RULES)
    TOKEN_RULES.update(family.TOKEN_RULES)
    TOKEN_IDS|=frozenset(family.TOKEN_RULES)
    PLAYABLE_TOKENS|=frozenset(family.TOKEN_RULES)
    DEATH_EFFECTS.update(getattr(family,'DEATH_EFFECTS',{}))
    WEAPON_TRIGGERS.update(getattr(family,'WEAPON_TRIGGERS',{}))

from . import replacements,random_targets,evolving_locations
RULES.update({cid:replacements.RULES[cid] for cid in ('TIME_064','JAIL_443')})
RULES.update(random_targets.RULES)
RULES['JAIL_887']=evolving_locations.RULES['JAIL_887']
LOCATION_RULES['JAIL_887']=evolving_locations.LOCATION_RULES['JAIL_887']
PRISON_TOKENS=frozenset(('JAIL_887t2','JAIL_887t3'))
TOKEN_RULES.update({cid:evolving_locations.TOKEN_RULES[cid] for cid in PRISON_TOKENS})
TOKEN_IDS|=PRISON_TOKENS
PLAYABLE_TOKENS|=PRISON_TOKENS
END_EFFECTS['JAIL_887t2']=evolving_locations.END_EFFECTS['JAIL_887t2']

# Exact-two damage quest and its fixed persistent reward.
RULES['TLC_631']=quest_families.RULES['TLC_631']
TOKEN_RULES['TLC_631t']=quest_families.TOKEN_RULES['TLC_631t']
TOKEN_IDS|=frozenset(('TLC_631t',))
PLAYABLE_TOKENS|=frozenset(('TLC_631t',))

# Imbue producers have finite paid effects. Broad power pools remain guarded.
FINITE_IMBUE_PRODUCERS=frozenset(('EDR_231', 'EDR_449', 'EDR_451', 'EDR_518', 'EDR_800', 'EDR_852', 'EDR_970', 'END_000', 'END_001'))
RULES.update({cid:imbue_consumers.RULES[cid] for cid in FINITE_IMBUE_PRODUCERS})
DEATH_EFFECTS.update({cid:ops for cid,ops in imbue_consumers.DEATH_EFFECTS.items() if cid in FINITE_IMBUE_PRODUCERS})

FINITE_HERALDS=frozenset(('CATA_525', 'CATA_530', 'CATA_565', 'CATA_580', 'CATA_725', 'CATA_160', 'CATA_561'))
RULES.update({cid:herald.RULES[cid] for cid in FINITE_HERALDS})
HERALD_TOKENS=frozenset(('CATA_525t', 'CATA_565t', 'CATA_580t', 'CATA_725t', 'CATA_561t'))
TOKEN_RULES.update({cid:('none',[]) for cid in HERALD_TOKENS})
TOKEN_IDS|=HERALD_TOKENS
PLAYABLE_TOKENS|=HERALD_TOKENS
DEATH_EFFECTS.update({cid:ops for cid,ops in herald.DEATH_EFFECTS.items() if cid in FINITE_HERALDS or cid in HERALD_TOKENS})
END_EFFECTS.update({cid:ops for cid,ops in herald.END_EFFECTS.items() if cid in HERALD_TOKENS})
from . import generation_cards
RULES['FIR_952']=generation_cards.RULES['FIR_952']

from . import health_generation,maps
RULES['TLC_467']=health_generation.RULES['TLC_467']
DEATH_EFFECTS['TLC_467']=health_generation.DEATH_EFFECTS['TLC_467']
RULES['TLC_900']=maps.RULES['TLC_900']

from . import temporary_control
RULES['TLC_229']=quest_families.RULES['TLC_229']
TOKEN_RULES['TLC_229t14']=quest_families.TOKEN_RULES['TLC_229t14']
TOKEN_IDS|=frozenset(('TLC_229t14',))
PLAYABLE_TOKENS|=frozenset(('TLC_229t14',))
RULES.update(temporary_control.RULES)

from . import infinity
RULES.update(infinity.RULES)
DEATH_EFFECTS.update(infinity.DEATH_EFFECTS)

from . import gelbin
RULES.update(gelbin.RULES)
TOKEN_RULES.update(gelbin.TOKEN_RULES)
TOKEN_IDS|=frozenset(gelbin.TOKEN_RULES)
PLAYABLE_TOKENS|=frozenset(gelbin.TOKEN_RULES)

# Complete frozen Secret pools; generated casts retain entity-cast semantics.
from . import automatic_casting
RULES.update({cid:automatic_casting.RULES[cid] for cid in ('JAIL_321','TIME_860')})

# Fixed opening replacement and already-registered Essence family.
from . import dragon_soul
RULES.update(dragon_soul.RULES)

# Reviewed generator recipes. Complete outcome preflight remains mandatory.
from . import reviewed_generation_bindings as generation_bindings
RULES.update({cid:rule for cid,rule in generation_bindings.RULES.items() if cid in generation_bindings.COLLECTIBLE_IDS})
DEATH_EFFECTS.update(generation_bindings.DEATH_EFFECTS)
END_EFFECTS.update(generation_bindings.END_EFFECTS)
WEAPON_TRIGGERS.update(generation_bindings.WEAPON_TRIGGERS)
LOCATION_RULES.update(generation_bindings.LOCATION_RULES)
LOCATION_EFFECTS.update(generation_bindings.LOCATION_EFFECTS)

# Reviewed complex families retain complete outcome admission checks.
from . import transformations, future_summons, historical_generation
RULES.update(transformations.RULES)
RULES.update({cid:automatic_casting.RULES[cid] for cid in ('CATA_786','EDR_520','JAIL_122')})
RULES.update(future_summons.RULES)
RULES['CATA_EVENT_000']=historical_generation.RULES['CATA_EVENT_000']
DEATH_EFFECTS.update(future_summons.DEATH_EFFECTS)
WEAPON_TRIGGERS.update(future_summons.WEAPON_TRIGGERS)
LOCATION_RULES.update(automatic_casting.LOCATION_RULES)
LOCATION_EFFECTS.update(automatic_casting.LOCATION_EFFECTS)

from . import reviewed_system_bindings as system_bindings
RULES.update(system_bindings.RULES)
TOKEN_RULES.update(system_bindings.TOKEN_RULES)
TOKEN_IDS|=system_bindings.TOKEN_IDS
PLAYABLE_TOKENS|=system_bindings.TOKEN_IDS
DEATH_EFFECTS.update(system_bindings.DEATH_EFFECTS)
LOCATION_RULES.update(system_bindings.LOCATION_RULES)
LOCATION_EFFECTS.update(system_bindings.LOCATION_EFFECTS)
from . import reviewed_rewind_bindings as rewind_bindings
RULES.update({cid:rewind_bindings.RULES[cid] for cid in rewind_bindings.COLLECTIBLE_IDS})
TOKEN_RULES.update({cid:rewind_bindings.RULES[cid] for cid in rewind_bindings.TOKEN_IDS})
TOKEN_IDS|=rewind_bindings.TOKEN_IDS
PLAYABLE_TOKENS|=rewind_bindings.TOKEN_IDS
DEATH_EFFECTS.update(rewind_bindings.DEATH_EFFECTS)
from . import reviewed_large_families as large_bindings
RULES.update(large_bindings.RULES)
TOKEN_RULES.update(large_bindings.TOKEN_RULES)
TOKEN_IDS|=large_bindings.FIXED_TOKEN_IDS
PLAYABLE_TOKENS|=large_bindings.PLAYABLE_TOKEN_IDS
DEATH_EFFECTS.update(large_bindings.DEATH_EFFECTS)
END_EFFECTS.update(large_bindings.END_EFFECTS)
LOCATION_RULES.update(large_bindings.LOCATION_RULES)
LOCATION_EFFECTS.update(large_bindings.LOCATION_EFFECTS)
# Fire-budget recipe retains complete internal-spell admission and immunity checks.
from . import exceptional_finish
RULES['FIR_959']=exceptional_finish.RULES['FIR_959']
LOCATION_RULES.update(rewind_bindings.LOCATION_RULES)
LOCATION_EFFECTS.update(rewind_bindings.LOCATION_EFFECTS)
from . import reviewed_complex_bindings as complex_bindings
RULES.update(complex_bindings.RULES)
TOKEN_RULES.update(complex_bindings.TOKEN_RULES)
TOKEN_IDS|=complex_bindings.TOKEN_IDS
PLAYABLE_TOKENS|=complex_bindings.PLAYABLE_TOKEN_IDS
DEATH_EFFECTS.update(complex_bindings.DEATH_EFFECTS)
WEAPON_TRIGGERS.update(complex_bindings.WEAPON_TRIGGERS)
LOCATION_RULES.update(complex_bindings.LOCATION_RULES)
LOCATION_EFFECTS.update(complex_bindings.LOCATION_EFFECTS)

# Full pinned Zombeast component contracts now back this sidequest.
RULES['TLC_EVENT_400']=('none',[('forge_sidequest',)])

# Curated source table and explicit component behaviors back this construction.
RULES['CATA_470']=('none',[('forge_dragon',)])
