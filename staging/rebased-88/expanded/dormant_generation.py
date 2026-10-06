"""Staged Dormant generation with pre-entry inactivity."""
from .generation_cards import pool,random_cards
TWO=pool(card_type='MINION',minimum=2,maximum=2)
RULES={'TIME_058':('none',[])}
DEATH_EFFECTS={'TIME_058':[random_cards(TWO,destination='board',dormant_turns=2)]}
def requests_for(cid):return {TWO} if cid in RULES else set()
