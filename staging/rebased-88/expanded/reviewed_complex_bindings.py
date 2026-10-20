"""Explicit physical payload and finite construction bindings.

Bindings describe written behavior. Historical pools, Bashana allocations and
Watfin mutations keep their explicit review gates; this is not full fidelity.
"""
from . import learned_spells,custom_builders,tiny_pal,hand_investigations,stored_obligations,exceptional_finish

RULES={**learned_spells.RULES,**custom_builders.RULES,**tiny_pal.RULES,
       'TIME_041':hand_investigations.RULES['TIME_041'],
       'TIME_861':stored_obligations.RULES['TIME_861'],
       'JAIL_EVENT_100':exceptional_finish.RULES['JAIL_EVENT_100']}
TOKEN_RULES={**learned_spells.TOKEN_RULES,**custom_builders.TOKEN_RULES,**tiny_pal.TOKEN_RULES}
# Presentation-only selector cards have frozen metadata but are not independently
# playable effect definitions. Their selected parts bind the produced payload.
OPTION_IDS=frozenset('CAP_405t'+str(i) for i in range(1,10))|frozenset(cid+'b' for cid in custom_builders.TRIAL_IDS)
OPTION_IDS|=frozenset('TLC_100t'+str(tier)+str(part) for tier in range(1,4) for part in range(1,8))
TOKEN_IDS=frozenset(TOKEN_RULES)|OPTION_IDS|frozenset(('CS2_065','DINO_136t'))
PLAYABLE_TOKEN_IDS=frozenset(TOKEN_RULES)|frozenset(('CS2_065','DINO_136t'))
DEATH_EFFECTS=dict(custom_builders.DEATH_EFFECTS)
WEAPON_TRIGGERS=dict(tiny_pal.WEAPON_TRIGGERS)
LOCATION_RULES=dict(custom_builders.LOCATION_RULES)
LOCATION_EFFECTS={}
TRIGGERS={}
END_EFFECTS={}
START_EFFECTS={}

def requests_for(cid):
    result=set()
    for module in (learned_spells,custom_builders,tiny_pal,hand_investigations,stored_obligations,exceptional_finish):
        if cid in module.RULES:result.update(module.requests_for(cid))
    return result
