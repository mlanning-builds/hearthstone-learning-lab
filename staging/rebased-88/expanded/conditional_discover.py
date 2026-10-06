"""Staged conditional Discover; complete outcome membership is not approved."""
from .generation_cards import pool,discover
DEMON=pool(card_type='MINION',tribe='DEMON',minimum=5,classes='any')
RULES={'TIME_446':('none',[discover(DEMON),('when_state','no_deck_minions',('next_cost_set','MINION',1,'permanent'))])}
def requests_for(cid):return {DEMON} if cid in RULES else set()
