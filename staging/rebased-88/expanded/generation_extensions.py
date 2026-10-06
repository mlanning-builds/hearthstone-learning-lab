"""Executable generation operation sequences; registration awaits full pools.

Unlike pending_definitions these use the engine's existing operation vocabulary.
They remain outside live RULES until complete outcome dependencies are satisfied.
"""
from .generation_cards import pool,random_cards,discover

RULES={
 'DINO_422':('none',[]),
 'JAIL_448':('none',[]),
 'JAIL_878':('none',[]),
 'JAIL_912':('none',[]),
 'TLC_449':('none',[discover(pool(card_type='MINION',minimum=1,maximum=1,classes='own_or_neutral'),temporary=True)]),
 'TLC_469':('none',[]),
 'TIME_712':('minion',[('destroy',),('generation_if_combo',random_cards(pool(card_type='MINION',minimum=8,maximum=8),destination='board'))]),
}
DEATH_EFFECTS={
 'DINO_422':[('generation_summon_attack',pool(card_type='MINION',tribe='BEAST',minimum=3,maximum=3),2)],
 'JAIL_448':[random_cards(pool(card_type='MINION',rarity='LEGENDARY'),3,stats=(1,1),set_cost=1)],
 'JAIL_878':[random_cards(pool(card_type='MINION',minimum=1,maximum=1,mechanic='DEATHRATTLE'),destination='board')],
 'JAIL_912':[('heal_own_hero',6),random_cards(pool(card_type='MINION',minimum=6,maximum=6),destination='board')],
 'TLC_469':[random_cards(pool(card_type='MINION',minimum=2,maximum=2),2,temporary=True)],
}
def requests_for(card_id):
    from .generation_cards import PoolRequest
    result=set()
    def walk(value):
        if isinstance(value,PoolRequest):result.add(value)
        elif isinstance(value,(list,tuple)):
            for item in value:walk(item)
    for table in (RULES,DEATH_EFFECTS,END_EFFECTS,TOKEN_RULES,DISCARD_EFFECTS,RETURN_EFFECTS,CHOICES):
        walk(table.get(card_id,()))
    if card_id in HELD_TRANSFORMS:walk(TOKEN_RULES[HELD_TRANSFORMS[card_id]])
    return result


RULES.update({
 'CATA_EVENT_400':('none',[('generation_dynamic_summon','remaining_mana')]),
 'CORE_BOT_256':('none',[('generation_dynamic_summon','hand_size')]),
 'CORE_CATA_006':('none',[('generation_attach_other_cost',)]),
 'CORE_WW_374':('none',[('generation_dynamic_summon','corpses_up_to',8)]),
 'DINO_415':('none',[discover(pool(card_type='MINION',mechanic='DEATHRATTLE',minimum=5,classes='own_or_neutral'),'board',trigger_deathrattle=True)]),
 'EDR_465':('none',[]),
 'END_005':('none',[random_cards(pool(card_type='MINION',minimum=4,maximum=4),destination='board'),('generation_if_corpses',4,pool(card_type='MINION',minimum=4,maximum=4)),('generation_if_outcast',random_cards(pool(card_type='MINION',minimum=4,maximum=4),destination='board'))]),
 'END_015':('none',[('kindred',[random_cards(pool(card_type='MINION',mechanic='DEATHRATTLE'),cost_delta=-2)])]),
 'END_020':('minion',[('generation_damage_branch',1,pool(card_type='MINION',minimum=1,maximum=1))]),
})
DEATH_EFFECTS.update({
 'EDR_465':[('generation_repeat_deaths','EDR_465',pool(card_type='MINION',tribe='DRAGON'))],
 'END_015':[random_cards(pool(card_type='MINION',mechanic='DEATHRATTLE'),cost_delta=-2)],
})

# Auxiliary hooks are staged with the play rule, never silently registered.
END_EFFECTS={
 'DINO_412':[random_cards(pool(card_type='MINION',minimum_tribes=2))],
}
TOKEN_RULES={
 'EDR_461t':('none',[random_cards(pool(card_type='MINION',minimum=6,maximum=6),2,'board')]),
}
HELD_TRANSFORMS={'EDR_461':'EDR_461t'}
DISCARD_EFFECTS={
 'CATA_499':[random_cards(pool(card_type='MINION',minimum=1,maximum=1),2,'board')],
}
RETURN_EFFECTS={
 'EDR_781':[random_cards(pool(card_type='MINION',minimum=2,maximum=2),2,'board')],
}
RULES.update({
 'CATA_140':('none',[('generation_fill_hand',pool(card_type='MINION',tribe='DRAGON'),25)]),
 'CATA_499':('none',DISCARD_EFFECTS['CATA_499']),
 'DINO_412':('none',[]),
 'DINO_430':('none',[('generation_discover_absorb',pool(card_type='MINION',tribe='BEAST',rarity='LEGENDARY'))]),
 'EDR_461':('none',[random_cards(pool(card_type='MINION',minimum=3,maximum=3),2,'board')]),
 'EDR_781':('none',[]),
})

RULES.update({
 'CATA_621':('none',[random_cards(pool(card_type='SPELL',family='paladin_aura',classes='PALADIN'),duration_delta=1)]),
 'DINO_427':('none',[random_cards(pool(card_type='SPELL',family='mask',classes='other'),combo_cost_delta=-2)]),
 'EDR_463':('none',[]),
})
CHOICES={
 'EDR_463':[
  ('Constricting Thorns','small_attack_minion',[('destroy',)]),
  ('Controlling Vines','none',[random_cards(pool(card_type='MINION',minimum=2,maximum=2),destination='board')]),
 ],
}
