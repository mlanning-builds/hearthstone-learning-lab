"""Staged Health-payment generators using physical-card enchantments."""
from .generation_cards import pool,PoolRequest,random_cards,discover
SPELL=pool(card_type='SPELL',classes='own_or_neutral')
UNDEAD=pool(card_type='MINION',tribe='UNDEAD')
FEL=pool(card_type='SPELL',school='FEL')
RULES={
 'TIME_612':('none',[discover(SPELL)]),
 'TIME_615':('none',[('generation_fill_health_hand',UNDEAD)]),
 'TLC_467':('none',[]),
}
DEATH_EFFECTS={'TLC_467':[random_cards(FEL,2,health_payment='permanent')]}
HEALTH_PAYMENT_IDS={'TIME_612'}

def requests_for(cid):
    result=set()
    def walk(value):
        if isinstance(value,PoolRequest):result.add(value)
        elif isinstance(value,(tuple,list)):
            for child in value:walk(child)
    for table in (RULES,DEATH_EFFECTS):walk(table.get(cid,()))
    return result
