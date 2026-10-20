"""Explicit written Rewind and remaining generation recipes.

Historical requests retain complete-contract rejection. Bindings describe
implemented effects, not completed dependency closure or client certification.
"""
from . import historical_generation, conditional_discover, event_generation
from . import rewind_generators, morchie
HISTORICAL_IDS=frozenset(('TIME_013','TIME_016','TIME_040','TIME_052',
                          'TIME_444','TIME_711','TIME_857'))
REWIND_IDS=frozenset(('CORE_EDR_004_2026','TIME_000','TIME_002','TIME_014',
                      'TIME_018','TIME_033','TIME_034','TIME_035','TIME_038',
                      'TIME_602','TIME_EVENT_999','END_036'))
COLLECTIBLE_IDS=HISTORICAL_IDS|REWIND_IDS|frozenset(('TIME_446','JAIL_879'))
TOKEN_IDS=frozenset(('JAIL_879t',))
RULES={cid:historical_generation.RULES[cid] for cid in HISTORICAL_IDS}
RULES.update({cid:rewind_generators.RULES[cid] for cid in REWIND_IDS if cid!='END_036'})
RULES.update(morchie.RULES)
RULES.update(conditional_discover.RULES)
RULES.update({'JAIL_879':event_generation.RULES['JAIL_879'],
              'JAIL_879t':event_generation.TOKEN_RULES['JAIL_879t']})
DEATH_EFFECTS={cid:ops for cid,ops in historical_generation.DEATH_EFFECTS.items()
               if cid in HISTORICAL_IDS}
DEATH_EFFECTS.update(rewind_generators.DEATH_EFFECTS)
TRIGGERS={cid:ops for cid,ops in historical_generation.TRIGGERS.items()
          if cid in HISTORICAL_IDS}
CAST_EFFECTS={'JAIL_879t':event_generation.CAST_EFFECTS['JAIL_879t']}

from . import dark_gift_generators
COLLECTIBLE_IDS|=frozenset(('END_027',))
RULES['END_027']=dark_gift_generators.RULES['END_027']

LOCATION_RULES=dict(conditional_discover.LOCATION_RULES)
LOCATION_EFFECTS=dict(conditional_discover.LOCATION_EFFECTS)
