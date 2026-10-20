"""Explicit generated-only Lost City reward recipe.

This registers the frozen finite reward bodies and UI identities. It does not
admit the root Quest or approve any additional historical generation pool.
"""
from . import quest_families
from .adapt import ADAPTATIONS,PLANT

REWARDS=('UNG_028t','UNG_067t1','UNG_116t','UNG_829t1','UNG_920t1',
         'UNG_934t1','UNG_940t8','UNG_942t','UNG_954t1')
PLAYABLE_IDS=frozenset((*REWARDS,'TLC_602t','UNG_920t2','UNG_829t3',PLANT))
RULES={cid:quest_families.TOKEN_RULES[cid] for cid in PLAYABLE_IDS if cid!=PLANT}
RULES[PLANT]=('none',[])
TOKEN_IDS=PLAYABLE_IDS|frozenset(ADAPTATIONS)|{'UNG_934t2','UNG_829t2'}
