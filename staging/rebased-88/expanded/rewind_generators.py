"""Staged Rewind consumers using complete, explicit generation contracts.

No playable registration. Morchie's staged outcome sequence is implemented in
morchie.py; interactions and independent timing review still gate admission.
"""
from engine.cards import UnsupportedCard
from .generation_cards import pool,PoolRequest,random_cards,discover
from .dark_gift_generators import request as gift_request,discover as gift_discover

BEAST_GIFT=gift_request(tribe='BEAST')
BUDGET_POOL=pool(card_type='MINION',maximum=12)
HOLY=pool(card_type='SPELL',school='HOLY')
NATURE=pool(card_type='SPELL',school='NATURE')
WEAPON=pool(card_type='WEAPON')
ANY_SPELL=pool(card_type='SPELL')
OWN_SPELL=pool(card_type='SPELL',classes='own')
RULES={
 'CORE_EDR_004_2026':('none',[('rewindgen_gift',)]),
 'TIME_000':('none',[random_cards(pool(card_type='MINION'),cost_delta=-3)]),
 'TIME_002':('none',[random_cards(OWN_SPELL,2)]),
 'TIME_014':('none',[('rewindgen_budget',12,0)]),
 'TIME_018':('none',[('rewindgen_holy',)]),
 'TIME_033':('none',[('rewindgen_cast',NATURE),('rewindgen_cast',NATURE)]),
 'TIME_034':('none',[('rewindgen_weapons',)]),
 'TIME_035':('none',[]),
 'TIME_038':('none',[random_cards(pool(card_type='MINION',rarity='LEGENDARY'),2,'board')]),
 'TIME_602':('none',[('generation_summon_attack',pool(card_type='MINION',tribe='BEAST',minimum=3,maximum=3),1)]),
 'TIME_EVENT_999':('none',[('rewindgen_sands',)]),
}
DEATH_EFFECTS={'TIME_035':[random_cards(pool(mechanic='REWIND'))]}
REWINDS={cid:3 if cid=='TIME_038' else 1 for cid in RULES if cid!='TIME_035'}
# Explicit frozen keyword membership: metadata omits the Rewind mechanic tag.
# Mentioning Rewind in an effect (Time Machine/Morchie) does not grant it.
REWIND_CARD_IDS=set(REWINDS)|{'TIME_001','TIME_003','TIME_004','TIME_008','TIME_433','TIME_441','TIME_610'}
UNRESOLVED={}

def requests_for(cid):
    result=set()
    def walk(value):
        if isinstance(value,PoolRequest):result.add(value)
        elif isinstance(value,(list,tuple)):
            for child in value:walk(child)
    walk(RULES.get(cid,()));walk(DEATH_EFFECTS.get(cid,()))
    result.update({'TIME_014':{BUDGET_POOL},'TIME_018':{HOLY},'TIME_034':{WEAPON},
                   'TIME_EVENT_999':{ANY_SPELL,OWN_SPELL}}.get(cid,set()))
    return result

class RewindGenerators:
    def _rewindgen_preflight(self,cid,owner):
        for request in sorted(requests_for(cid),key=repr):self._generation_candidates(request,owner)
        if cid=='CORE_EDR_004_2026':self._dark_global_candidates(BEAST_GIFT,owner,cid)
        if cid=='TIME_034':self._generation_candidates(WEAPON,1-owner)
        if cid=='TIME_033':self._rewindgen_cast_candidates(NATURE,owner)

    def _rewindgen_cast_candidates(self,request,owner):
        values=self._generation_candidates(request,owner)
        unsupported=[cid for cid in values if not self._supports_internal_spell(cid)]
        if unsupported:raise UnsupportedCard('Rewind cast outcomes lack internal support: '+', '.join(unsupported))
        return values

    def _rewindgen_split(self,op,ctx):
        name=op[0];owner=ctx['owner']
        if name=='rewindgen_budget':
            remaining,steps=op[1:]
            # The reviewed full <=12 pool is validated even if the board is full.
            values=self._generation_candidates(BUDGET_POOL,owner)
            if remaining<=0 or len(self.players[owner].board)>=7:return ('batch30_noop',),()
            values=[cid for cid in values if self.cards[cid]['cost']<=remaining]
            if not values:return ('batch30_noop',),()
            if steps>=256:raise UnsupportedCard('Mana-budget summon chain exceeds verified depth')
            cid=self.rng.choice(values);cost=self.cards[cid]['cost']
            return ('summon',cid,1),(('rewindgen_budget',remaining-cost,steps+1),)
        if name=='rewindgen_holy':
            values=self._generation_candidates(HOLY,owner)
            if not values:return ('batch30_noop',),()
            ids=[self.rng.choice(values) for _ in range(2)]
            return ('add',ids[0],1),(('add',ids[1],1),('heal_own_hero',sum(self.cards[cid]['cost'] for cid in ids)))
        if name=='rewindgen_cast':
            values=self._rewindgen_cast_candidates(op[1],owner)
            return self._split_fixed_summon(('cast_fixed_spell',self.rng.choice(values),'random'),ctx) if values else (('batch30_noop',),())
        if name=='rewindgen_weapons':
            values=[self._generation_candidates(WEAPON,recipient) for recipient in (owner,1-owner)]
            ids=[self.rng.choice(v) if v else None for v in values]
            operations=[('rewindgen_equip',recipient,cid) for recipient,cid in zip((owner,1-owner),ids) if cid]
            operations.append(('rewindgen_weapon_buff',))
            return operations[0],tuple(operations[1:])
        if name=='rewindgen_sands':
            card=ctx.get('physical_card')
            used=getattr(card,'rule_state',{}).get('rewinds_remaining',1)<1
            return self._split_fixed_summon(discover(OWN_SPELL if used else ANY_SPELL),ctx)
        return None

    def _rewindgen_effect(self,op,ctx):
        owner=ctx['owner']
        if op[0]=='rewindgen_gift':
            return self._dark_global_effect(gift_discover(BEAST_GIFT,cost_delta=-int(bool(ctx.get('kindred')))*ctx.get('kindred_repeats',1)),ctx)
        if op[0]=='rewindgen_equip':self._equip(op[1],op[2]);return True
        if op[0]=='rewindgen_weapon_buff':
            self._buff_weapon(owner,1,1)
            return True
        return False
