"""Staged event-driven generation; complete open pools remain required."""
from .generation_cards import pool,random_cards
BATTLECRY=pool(card_type='MINION',mechanic='BATTLECRY')
BEAST_FIVE=pool(card_type='MINION',tribe='BEAST',minimum=5,maximum=5)
THREE=pool(card_type='MINION',minimum=3,maximum=3)
TRIPWIRE='JAIL_879t'
RULES={
 'JAIL_407':('none',[]),
 'JAIL_879':('none',[random_cards(BEAST_FIVE,destination='board'),('on_draw_shuffle',TRIPWIRE,2,0)]),
 'TIME_EVENT_997':('location',[('generation_reopen_attach',THREE)]),
}
TRIGGERS={'JAIL_407':('after_owner_card_played',[random_cards(BATTLECRY,cost_delta=-2)])}
CAST_EFFECTS={TRIPWIRE:(random_cards(BEAST_FIVE,destination='board'),)}
TOKEN_RULES={TRIPWIRE:('none',list(CAST_EFFECTS[TRIPWIRE]))}
def requests_for(cid):
 return {'JAIL_407':{BATTLECRY},'JAIL_879':{BEAST_FIVE},'TIME_EVENT_997':{THREE}}.get(cid,set())
