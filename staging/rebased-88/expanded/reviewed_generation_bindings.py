"""Reviewed written Standard recipes, with dependency rejection preserved.

These bindings do not certify executable closure: production requests still
validate every eligible frozen outcome before sampling. Historical Dragon gift
END_027 is deliberately absent until its independent historical contract closes.
"""
from . import generation_cards as generation
from . import choice_generators as choices
from . import dark_gift_generators as gifts

GENERATION_IDS=frozenset((
 'CORE_DRG_024','CORE_EDR_001','CORE_EX1_189','CORE_GIL_531','CORE_KAR_069',
 'CORE_UNG_912','CATA_556','EDR_999','EDR_848','JAIL_125','JAIL_706',
 'JAIL_460','MEND_045','TIME_613','CATA_723','CORE_GVG_114','CORE_REV_308',
 'CORE_KAR_077','CORE_WON_337','EDR_060','DINO_431','DINO_433','CATA_569',
 'MEND_042','TLC_516','TLC_814','DINO_434','CATA_474','EDR_462','EDR_530',
 'END_029','CORE_ETC_111','CATA_136','CORE_AV_107','CORE_BAR_541','CORE_BT_321',
 'CORE_CATA_009','CORE_GIL_836','CORE_KAR_057','CORE_KAR_062','CORE_LOE_039',
 'CORE_ONY_022','CORE_WON_096','CORE_WON_350','Core_UNG_072','CATA_484',
 'DINO_424','DINO_426','EDR_270','JAIL_507','TLC_334','TLC_514','JAIL_876',
 'TLC_477','CATA_471','CORE_AT_062','CORE_TID_931','FIR_952','FIR_913','CORE_CFM_781'))
CHOICE_IDS=frozenset((
 'CAP_002','CAP_105','CAP_407','CORE_RLK_066','CORE_RLK_116','CORE_YOP_001',
 'Core_LOE_115','EDR_273','EDR_517','EDR_872','FIR_927','JAIL_123','JAIL_201',
 'JAIL_328','JAIL_451','JAIL_474','JAIL_735','JAIL_806','JAIL_861','JAIL_875',
 'JAIL_892','JAIL_986','JAIL_987','RLK_025','TIME_102','TIME_448','TIME_730',
 'TIME_872','TLC_109','TLC_434','TLC_461','TLC_462','TLC_815'))
DARK_GIFT_IDS=frozenset((
 'EDR_102','EDR_105','EDR_456','EDR_488','EDR_811','EDR_882','END_013',
 'FIR_900','FIR_920','FIR_924','FIR_939'))
COLLECTIBLE_IDS=GENERATION_IDS|CHOICE_IDS|DARK_GIFT_IDS
TOKEN_IDS=frozenset(('FP1_011',))
RULES={cid:generation.RULES[cid] for cid in GENERATION_IDS}
RULES.update({cid:choices.RULES[cid] for cid in CHOICE_IDS})
RULES.update({cid:gifts.RULES[cid] for cid in DARK_GIFT_IDS})
RULES.update({cid:generation.TOKEN_RULES[cid] for cid in TOKEN_IDS})
DEATH_EFFECTS={cid:ops for cid,ops in generation.DEATH_EFFECTS.items()
               if cid in GENERATION_IDS|TOKEN_IDS}
DEATH_EFFECTS.update({cid:ops for cid,ops in choices.DEATH_EFFECTS.items() if cid in CHOICE_IDS})
END_EFFECTS={cid:ops for cid,ops in generation.END_EFFECTS.items() if cid in GENERATION_IDS}
TRIGGERS={cid:ops for cid,ops in generation.TRIGGERS.items() if cid in GENERATION_IDS}
CHOICES={cid:ops for cid,ops in choices.CHOICES.items() if cid in CHOICE_IDS}
WEAPON_TRIGGERS={cid:ops for cid,ops in choices.WEAPON_TRIGGERS.items() if cid in CHOICE_IDS}
LOCATION_EFFECTS={cid:ops for cid,ops in choices.LOCATION_EFFECTS.items() if cid in CHOICE_IDS}
LOCATION_RULES={cid:'none' for cid in LOCATION_EFFECTS}

# Additional ordinary recipes share the same complete-membership gate.
from . import generation_extensions as extensions
EXTENSION_IDS=frozenset((
 'DINO_422','JAIL_448','JAIL_878','JAIL_912','TLC_449','TLC_469','TIME_712',
 'CATA_EVENT_400','CORE_BOT_256','CORE_CATA_006','CORE_WW_374','DINO_415',
 'EDR_465','END_005','END_015','END_020','CATA_140','CATA_499','DINO_412',
 'DINO_430','EDR_461','EDR_781','CATA_621','DINO_427','EDR_463'))
COLLECTIBLE_IDS=COLLECTIBLE_IDS|EXTENSION_IDS
TOKEN_IDS=TOKEN_IDS|frozenset(('EDR_461t',))
RULES.update({cid:extensions.RULES[cid] for cid in EXTENSION_IDS})
RULES.update({'EDR_461t':extensions.TOKEN_RULES['EDR_461t']})
for destination,source in ((DEATH_EFFECTS,extensions.DEATH_EFFECTS),
                           (END_EFFECTS,extensions.END_EFFECTS),
                           (CHOICES,extensions.CHOICES)):
    destination.update({cid:ops for cid,ops in source.items() if cid in EXTENSION_IDS})

# Event, alternate-payment and dormant consumers have explicit shared hooks.
from . import attack_generation, event_generation, health_generation
from . import dormant_generation, exceptional_generation
AUXILIARY_IDS=frozenset(('JAIL_200','JAIL_407','TIME_EVENT_997','TIME_612',
                        'TIME_615','TIME_058','END_037','JAIL_319'))
COLLECTIBLE_IDS|=AUXILIARY_IDS
for module in (attack_generation,event_generation,health_generation,
               dormant_generation,exceptional_generation):
    RULES.update({cid:rule for cid,rule in module.RULES.items() if cid in AUXILIARY_IDS})
    for destination,name in ((DEATH_EFFECTS,'DEATH_EFFECTS'),(TRIGGERS,'TRIGGERS')):
        destination.update({cid:ops for cid,ops in getattr(module,name,{}).items()
                            if cid in AUXILIARY_IDS})
