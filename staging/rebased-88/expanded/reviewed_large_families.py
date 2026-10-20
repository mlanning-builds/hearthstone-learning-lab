"""Explicit remaining Herald, Colossal, and Imbue bindings.

Pool guards remain exact and complete; registration is separate from independent
client conformance of shared timing, cost, and repetition interactions.
"""
from . import herald,colossal_bodies,imbue_consumers
HERALD_IDS=frozenset(('CATA_156','CATA_158','CATA_492','CATA_497','CATA_722','CATA_780','CATA_785','CATA_190h'))
COLOSSAL_IDS=frozenset(('CATA_153','CATA_154','CATA_155','CATA_488'))
IMBUE_IDS=frozenset(('EDR_264',))
ROOT_IDS=HERALD_IDS|COLOSSAL_IDS|IMBUE_IDS
RULES={**{cid:herald.RULES[cid] for cid in HERALD_IDS},**{cid:colossal_bodies.RULES[cid] for cid in COLOSSAL_IDS},'EDR_264':imbue_consumers.RULES['EDR_264']}
FIXED_TOKEN_IDS=frozenset(('CATA_190p','CATA_190t10','CATA_190t11','CATA_190t12','CATA_190t13','CATA_190t14','CATA_158t','CATA_780t','CATA_153t','CATA_153t1','CATA_154t','CATA_154t1','CATA_155t','CATA_155t1','CATA_488t','CATA_488t2'))
PLAYABLE_TOKEN_IDS=FIXED_TOKEN_IDS-{'CATA_190p'}
TOKEN_RULES={cid:('none',list(ops)) for cid,ops in herald.CATACLYSMS.items()}
TOKEN_RULES.update({cid:('none',[]) for cid in PLAYABLE_TOKEN_IDS if cid not in TOKEN_RULES})
DEATH_EFFECTS={cid:herald.DEATH_EFFECTS[cid] for cid in HERALD_IDS if cid in herald.DEATH_EFFECTS}
LOCATION_RULES={cid:herald.LOCATION_RULES[cid] for cid in HERALD_IDS if cid in herald.LOCATION_RULES}
LOCATION_EFFECTS={cid:herald.LOCATION_EFFECTS[cid] for cid in HERALD_IDS if cid in herald.LOCATION_EFFECTS}
END_EFFECTS={cid:colossal_bodies.END_EFFECTS[cid] for cid in COLOSSAL_IDS if cid in colossal_bodies.END_EFFECTS}
TRIGGERS={cid:ops for cid,ops in colossal_bodies.TRIGGERS.items() if cid in ('CATA_488t','CATA_488t2')}

def requests_for(cid):
 if cid in COLOSSAL_IDS:return colossal_bodies.requests_for(cid)
 if cid in IMBUE_IDS:return imbue_consumers.requests_for(cid)
 if cid=='CATA_190h':return {herald.LEGENDARY_DRAGONS}
 return set()
