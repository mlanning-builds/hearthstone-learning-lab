"""All twelve remaining Dark Gift generators, gated on complete reviewed pools.

These executable declarations are staged: they are NOT live registration.
Historical membership needs an explicit contract; no Standard-pool substitute.
"""
from dataclasses import dataclass
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,PoolRequest
from .generation import request_matches
from .pools import GenerationPool

@dataclass(frozen=True)
class GiftRequest:
    alternatives: tuple
    historical: bool=False


def request(*,historical=False,any_mechanics=(),**kwargs):
    kwargs.setdefault('card_type','MINION');kwargs.setdefault('classes','own_or_neutral')
    return GiftRequest(tuple(pool(**kwargs,mechanic=m) for m in any_mechanics) if any_mechanics else (pool(**kwargs),),historical)


def discover(req,**modifiers):return ('dark_global_discover',req,tuple(sorted(modifiers.items())))

RULES={
 'EDR_102':('none',[discover(request(rarity='LEGENDARY'))]),
 'EDR_105':('none',[discover(request(minimum=3,maximum=3))]),
 'EDR_456':('none',[('dark_global_if_dragon',discover(request(tribe='DRAGON')))]),
 'EDR_488':('none',[discover(request(mechanic='DEATHRATTLE'))]),
 'EDR_811':('none',[discover(request(tribe='UNDEAD'),corpse_cost=2)]),
 'EDR_882':('none',[discover(request(tribe='DEMON',minimum=5),shuffle_unchosen=True)]),
 'END_013':('none',[discover(request(minimum=1,maximum=1))]),
 'END_027':('none',[discover(request(tribe='DRAGON',historical=True))]),
 'FIR_900':('none',[discover(request(),cost_delta=-2)]),
 'FIR_920':('none',[discover(request(any_mechanics=('COMBO','BATTLECRY','STEALTH')))]),
 'FIR_924':('none',[discover(request(tribe='DEMON'),copy_selected=True)]),
 'FIR_939':('character',[('damage',2),discover(request(classes='WARRIOR'))]),
}


def requests_for(cid):
    result=set()
    def walk(v):
        if isinstance(v,GiftRequest):result.add(v)
        elif isinstance(v,(tuple,list)):
            for child in v:walk(child)
    walk(RULES.get(cid,()))
    return result

class DarkGiftGenerators:
    def _dark_global_candidates(self,req,owner,source_id=None):
        if not isinstance(req,GiftRequest):raise UnsupportedCard('Expected an explicit Dark Gift request')
        hero_class=self.players[owner].hero_class
        contract=getattr(self,'_dark_generation_pools',{}).get((req,hero_class))
        if req.historical and not isinstance(contract,GenerationPool):
            raise UnsupportedCard('Historical Dark Gift pool requires a reviewed historical contract')
        if contract is not None:
            if not isinstance(contract,GenerationPool):raise UnsupportedCard('Invalid Dark Gift contract')
            ids=contract.resolve(self.cards,self.cards)
        else:
            ids=tuple(dict.fromkeys(cid for alternative in req.alternatives
                      for cid in self._generation_candidates(alternative,owner)))
        invalid=[cid for cid in ids if not any(request_matches(r,self.cards[cid],hero_class) for r in req.alternatives)]
        if invalid:raise UnsupportedCard('Ineligible Dark Gift outcomes: '+', '.join(invalid))
        canonical=lambda cid:self.cards[cid].get('countAsCopyOfDbfId',self.cards[cid].get('dbfId',cid))
        if len({canonical(cid) for cid in ids})!=len(ids):raise UnsupportedCard('Duplicate canonical Dark Gift outcomes')
        if req.historical:
            from .historical_generation import validate_past_candidates
            validate_past_candidates(ids,self.cards)
        source=canonical(source_id) if source_id in self.cards else None
        return tuple(cid for cid in ids if canonical(cid)!=source)

    def _dark_global_preflight(self,cid,owner):
        for req in sorted(requests_for(cid),key=repr):self._dark_global_candidates(req,owner,cid)

    def _dark_global_split(self,op,ctx):
        if op[0]!='dark_global_if_dragon':return None
        from .selectors import has_tribe
        if any(has_tribe(self._card_data(c),'DRAGON') for c in self.players[ctx['owner']].hand):
            return self._split_fixed_summon(op[1],ctx)
        return ('batch30_noop',),()

    def _dark_global_effect(self,op,ctx):
        if op[0]!='dark_global_discover':return False
        owner=ctx['owner'];mods=dict(op[2])
        unknown=set(mods)-{'corpse_cost','cost_delta','shuffle_unchosen','copy_selected'}
        if unknown:raise UnsupportedCard('Unknown Dark Gift modifiers: '+repr(sorted(unknown)))
        ids=self._dark_global_candidates(op[1],owner,ctx.get('card_id'))
        ids=self.rng.sample(list(ids),min(3,len(ids)))
        if not ids:return True
        # No new physical entity IDs are spent to display hypothetical offers.
        cards=[Card(0,cid) for cid in ids]
        gifted=self.players[owner].corpses>=mods.get('corpse_cost',0)
        gifts=self._dark_assign(cards) if gifted else [None]*len(cards)
        if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite a pending Dark Gift choice')
        self.pending_choice=dict(owner=owner,kind='dark_global',modifiers=mods,
            options=[dict(card_id=cid,dark_gift=gift) for cid,gift in zip(ids,gifts)])
        self.phase='choice'
        return True

    def _dark_global_choice(self,choice,selected):
        if choice['kind']!='dark_global':return False
        owner=choice['owner'];p=self.players[owner];mods=choice['modifiers']
        gift=selected['dark_gift'];cost=mods.get('corpse_cost',0)
        if gift and cost:
            if p.corpses<cost:raise UnsupportedCard('Dark Gift Corpse payment no longer available')
            self._spend_corpses(owner,cost)
        if mods.get('shuffle_unchosen'):
            others=[option for option in choice['options'] if option is not selected]
            for option in others:
                card=Card(self._new_id(),option['card_id'])
                if option['dark_gift']:card=self._dark_attach(owner,card,option['dark_gift'],notify=False)
                p.deck.append(card)
            if others:
                self.rng.shuffle(p.deck);self._record_deck_insertion(owner,owner,len(others),'shuffle')
        card=Card(self._new_id(),selected['card_id']);result=self._enter_hand(owner,card)
        if result is not None:
            if gift:result=self._dark_attach(owner,result,gift)
            result.cost_delta=getattr(result,'cost_delta',0)+mods.get('cost_delta',0)
            if mods.get('copy_selected'):self._enter_hand(owner,self._copy_card(result))
        self._discovery_result=result;self._refresh_auras()
        return True
