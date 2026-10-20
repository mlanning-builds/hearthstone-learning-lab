"""Positive Saidan gains shared by physical zone buffs and battlefield stats."""
def gain(entity,amount):
 if amount>0 and getattr(entity,'card_id',None)=='AV_345' and not getattr(entity,'silenced',False):return amount*2
 return amount

def add(entity,field,amount):
 if field not in ('attack_bonus','health_bonus'):raise ValueError('Unknown physical stat bonus')
 setattr(entity,field,getattr(entity,field)+gain(entity,amount))
