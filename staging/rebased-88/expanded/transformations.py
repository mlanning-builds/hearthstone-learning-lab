"""Staged random transformations; complete reviewed outcome pools are required.

These declarations are not playable registrations. Genn lives in genn.py;
Divergence and Alternate Reality remain review-gated.
"""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool
from .selectors import classes

RULES={
 'TIME_030':('none',[('mutation_split_minion',)]),
 'TIME_707':('none',[('mutation_alternate_reality',)]),
 'CATA_567':('none',[('mutation_board',1,True)]),
 'CATA_979':('none',[('mutation_choose_hand','split_spell')]),
 'EDR_493':('none',[('mutation_hand_demons',)]),
 'EDR_529':('none',[]),
 'EDR_873':('none',[('mutation_deck_druid',)]),
 'JAIL_313':('none',[('mutation_choose_hand','alchemy')]),
 'JAIL_EVENT_102':('none',[('mutation_bribe',)]),
 'TIME_049':('none',[]),
 'TIME_055':('none',[]),
 'TIME_859':('none',[('mutation_anomalize',)]),
 'TLC_235':('minion',[('mutation_life_cycle',)]),
}
START_EFFECTS={'TIME_049':('owner',[('mutation_self',5)])}
TRIGGERS={'TIME_055':('self_survived_damage',[('mutation_self',7)])}
UNRESOLVED={

}

def cost_pool(cost,card_type='MINION'):
    return pool(card_type=card_type,minimum=cost,maximum=cost)

def requests_for(cid):
    return {
      'TIME_707':{pool(era='past',mechanic='CHOOSE_ONE')},
      'EDR_493':{pool(card_type='MINION',tribe='DEMON')},
      'EDR_873':{pool(classes='DRUID')},
      'JAIL_EVENT_102':{cost_pool(2),cost_pool(3)},
      'TIME_049':{cost_pool(5)},'TIME_055':{cost_pool(7)},
      'TIME_859':{cost_pool(10),cost_pool(1)},
    }.get(cid,set())

class Transformations:
    def _b60_transform_card(self,card,cid,*,stats=None):
        if card.card_id=='EDR_529' and self.cards[cid]['type']=='MINION':
            owner=next((i for i,p in enumerate(self.players) if any(c is card for c in p.hand+p.deck)),None)
            if owner is None:raise UnsupportedCard('Podling transformation requires its zone owner')
            values=self._generation_candidates(cost_pool(self.cards[cid]['cost']+2),owner)
            if not values:return
            cid=self.rng.choice(values)
        return super()._b60_transform_card(card,cid,stats=stats)

    def _mutation_validate_replacements(self,card,request,owner):
        values=self._generation_candidates(request,owner)
        if card.card_id=='EDR_529' and not getattr(card,'silenced',False):
            for cost in {self.cards[cid]['cost']+2 for cid in values if self.cards[cid]['type']=='MINION'}:
                self._generation_candidates(cost_pool(cost),owner)

    def _transform(self,m,cid):
        if m.dormant:return m
        if m.card_id=='EDR_529' and not m.silenced and self.cards[cid]['type']=='MINION':
            outcomes=self._generation_candidates(cost_pool(self.cards[cid]['cost']+2),m.owner)
            if not outcomes:return m
            cid=self.rng.choice(outcomes)
        return super()._transform(m,cid)

    def _mutation_preflight(self,cid,owner):
        for request in sorted(requests_for(cid),key=repr):self._generation_candidates(request,owner)

    def _mutation_pick(self,request,owner):
        values=self._generation_candidates(request,owner)
        return self.rng.choice(values) if values else None

    def _mutation_replace_card(self,card,cid,*,retain_stats=False,retain_cost=False):
        old=self.cards[card.card_id]
        stats=(old.get('attack',0)+card.attack_bonus,old.get('health',0)+card.health_bonus)
        cost=getattr(card,'set_cost',old['cost'])
        self._b60_transform_card(card,cid,stats=stats if retain_stats else None)
        if retain_cost:card.set_cost=cost

    def _mutation_split(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner]
        operations=[]
        if name=='mutation_board':
            for m in list(p.minions):
                if self._fire_immune_target(m.uid,ctx):continue
                request=cost_pool(self.cards[m.card_id]['cost']+op[1])
                self._generation_candidates(request,owner)
                # Replacement abilities need their entire outcome closure too.
                if m.card_id=='EDR_529' and not m.silenced:
                    self._generation_candidates(cost_pool(request.minimum+2),owner)
                operations.append(('mutation_board_one',m.uid,request,op[2]))
        elif name=='mutation_hand_demons':
            request=pool(card_type='MINION',tribe='DEMON');self._generation_candidates(request,owner)
            for c in list(p.hand):
                if self.cards[c.card_id]['type']=='MINION':
                    self._mutation_validate_replacements(c,request,owner)
                    operations.append(('mutation_hand_one',c.uid,request))
        elif name=='mutation_deck_druid':
            request=pool(classes='DRUID');self._generation_candidates(request,owner)
            # Preserve physical cards and positions; this is neither draw nor shuffle.
            for i,value in enumerate(p.deck):
                cid=value.card_id if hasattr(value,'card_id') else value
                if 'NEUTRAL' in classes(self.cards[cid]):operations.append(('mutation_deck_one',i,request))
        elif name=='mutation_life_cycle':
            m=self._force_live(ctx.get('target',0))
            if m is not None and not m.dormant:
                request=cost_pool(self.cards[m.card_id]['cost']);self._generation_candidates(request,m.owner)
                operations=[('destroy',),('mutation_replace_dead',m.owner,self.players[m.owner].board.index(m),request)]
        elif name=='mutation_bribe':
            for recipient in (owner,1-owner):self._generation_candidates(cost_pool(2),recipient)
            self._generation_candidates(cost_pool(3),owner)
            operations=[('mutation_summon',recipient,cost_pool(2),None) for recipient in (owner,1-owner) for _ in range(2)]
            operations.append(('mutation_board',1,False))
        elif name=='mutation_anomalize':
            for cost in (10,1):self._generation_candidates(cost_pool(cost),owner)
            state={'summoned':[]}
            operations=[('mutation_summon',owner,cost_pool(cost),state) for cost in (10,1)]
            operations.append(('mutation_scramble',state))
        else:return None
        return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())

    def _mutation_choice(self,choice,selected):
        if choice['kind']!='mutation_hand':return False
        owner=choice['owner'];p=self.players[owner]
        card=next((c for c in p.hand if c.uid==selected['uid']),None)
        if card is None:raise UnsupportedCard('Selected transformation card left hand')
        mode=choice['mode'];cost=choice['costs'][card.uid]
        request=cost_pool(cost+(5 if mode=='alchemy' else 0),'SPELL')
        values=self._generation_candidates(request,owner)
        if not values:return True
        if mode=='alchemy':self._mutation_replace_card(card,self.rng.choice(values),retain_cost=True)
        elif mode=='split_spell':
            identities=[self.rng.choice(values) for _ in range(2)]
            self._mutation_replace_card(card,identities[0])
            self._enter_hand(owner,Card(self._new_id(),identities[1]))
        else:raise UnsupportedCard('Unknown hand transformation mode')
        self._refresh_auras();return True

    def _mutation_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner]
        if name=='mutation_alternate_reality':
            values=self._generation_candidates(pool(era='past',mechanic='CHOOSE_ONE'),owner)
            if not values and (p.hand or p.deck):raise UnsupportedCard('Empty historical Choose One replacement pool')
            for zone in (p.hand,p.deck):
                for i in range(len(zone)):
                    card=Card(self._new_id(),self.rng.choice(values));card.cost_delta=-1
                    zone[i]=card
            self._refresh_auras()
        elif name=='mutation_split_minion':
            import math
            choices=[c for c in p.hand if self.cards[c.card_id]['type']=='MINION']
            if choices:
                card=self.rng.choice(choices);data=self.cards[card.card_id]
                cost=math.ceil(self._cost(card,owner)/2)
                attack=math.ceil((data['attack']+card.attack_bonus)/2)
                health=math.ceil((data['health']+card.health_bonus)/2)
                copy=self._clone_hand_card(owner,card)
                for result in (card,copy):
                    if result is None:continue
                    result.attack_bonus=attack-data['attack'];result.health_bonus=health-data['health']
                    result.set_cost=cost;result.cost_delta=0
                    result.temporary_cost_discounts=[]
                self._refresh_auras()
        elif name=='mutation_board_one':
            m=self._force_live(op[1])
            if m is not None and not m.dormant and not self._fire_immune_target(m.uid,ctx):
                cid=self._mutation_pick(op[2],owner)
                if cid:
                    original=m.card_id;result=self._transform(m,cid)
                    if op[3] and result is not m:result.attached_death_effects.append(('death_summon',original,1))
        elif name=='mutation_hand_one':
            card=next((c for c in p.hand if c.uid==op[1]),None)
            if card is not None:
                cid=self._mutation_pick(op[2],owner)
                if cid:self._mutation_replace_card(card,cid,retain_stats=True,retain_cost=True)
        elif name=='mutation_deck_one':
            value=p.deck[op[1]];cid=self._mutation_pick(op[2],owner)
            if cid:
                if hasattr(value,'card_id'):self._mutation_replace_card(value,cid)
                else:p.deck[op[1]]=cid
        elif name=='mutation_replace_dead':
            cid=self._mutation_pick(op[3],op[1])
            if cid:self._summon(op[1],cid,op[2],entry_origin='effect',entry_site='mutation_life_cycle')
        elif name=='mutation_summon':
            cid=self._mutation_pick(op[2],op[1])
            if cid:
                m=self._summon(op[1],cid,entry_origin='effect',entry_site='mutation_summon')
                if m is not None and op[3] is not None:op[3]['summoned'].append(m.uid)
        elif name=='mutation_scramble':
            members=[self._force_live(uid) for uid in op[1]['summoned']]
            members=[m for m in members if m is not None and not m.dormant]
            values=[value for m in members for value in (m.attack,m.health)]
            self.rng.shuffle(values)
            for i,m in enumerate(members):
                self._set_minion_attack(m,values[2*i]);m.health=m.max_health=values[2*i+1]
            self._refresh_auras()
        elif name=='mutation_self':
            m=ctx.get('source')
            if m is not None and m in self.players[m.owner].minions and m.health>0 and not m.silenced:
                cid=self._mutation_pick(cost_pool(op[1]),owner)
                if cid:self._transform(m,cid)
        elif name=='mutation_choose_hand':
            mode=op[1]
            if mode not in ('alchemy','split_spell'):raise UnsupportedCard('Unknown hand transformation mode')
            cards=[c for c in p.hand if mode=='alchemy' or self.cards[c.card_id]['type']=='SPELL']
            costs={c.uid:self._cost(c,owner) for c in cards}
            for cost in set(costs.values()):self._generation_candidates(cost_pool(cost+(5 if mode=='alchemy' else 0),'SPELL'),owner)
            if cards:
                if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite a pending transformation choice')
                self.pending_choice=dict(owner=owner,kind='mutation_hand',mode=mode,costs=costs,
                    options=[dict(card_id=c.card_id,uid=c.uid) for c in cards]);self.phase='choice'
        else:return False
        return True
