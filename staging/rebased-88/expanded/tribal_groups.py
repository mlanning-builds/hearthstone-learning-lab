"""Shared type assignment, deck draws, and explicit tribe damage modifiers."""
from engine.game import Card
from .selectors import effective_tribes,common_tribes,has_tribe
RULES={
 'CORE_WON_141':('none',[('tribal_group_buff',3)]),
 'TLC_110':('none',[('tribal_esho',)]),
 'TLC_222':('none',[('tribal_draw_pair',)]),
 'TLC_254':('none',[]),
 'CAP_104':('none',[]),'EDR_480':('none',[]),'TLC_228':('none',[]),
 'EDR_526':('none',[('tribal_trap_hand',)]),
}
END_EFFECTS={'TLC_254':[('tribal_group_buff',7)]}


class TribalGroups:
    def _distinct_type_group(self,values,limit):
        # Match physical candidates to different types. Reassignment keeps a
        # dual-type/ALL candidate from blocking a single-type candidate.
        order=list(range(len(values)));self.rng.shuffle(order)
        assigned={};selected=[]
        def match(index,seen):
            kinds=sorted(effective_tribes(self.cards[getattr(values[index],'card_id',values[index])]));self.rng.shuffle(kinds)
            for kind in kinds:
                if kind in seen:continue
                seen.add(kind)
                if kind not in assigned or match(assigned[kind],seen):
                    assigned[kind]=index;return True
            return False
        for index in order:
            if match(index,set()):selected.append(index)
            if len(selected)>=limit:break
        return [values[i] for i in selected]

    def _tribal_split(self,op,ctx):
        if op[0]!='tribal_draw_pair':return None
        p=self.players[ctx['owner']]
        for i,c in enumerate(p.deck):
            if not isinstance(c,Card):p.deck[i]=Card(self._new_id(),c)
        chosen=self._distinct_type_group(p.deck,2)
        ops=[('tribal_draw_physical',c) for c in chosen]+[('tribal_buff_drawn',chosen)]
        return ops[0],tuple(ops[1:])

    def _outgoing_tribal_damage(self,source,amount):
        if source is None or amount<=0:return amount
        owner=source.owner;card=self.cards[source.card_id]
        active=[m for m in self.players[owner].minions if not m.silenced and m.health>0]
        multiplier=2**sum(m.card_id=='EDR_480' for m in active) if has_tribe(card,'BEAST') else 1
        extra=sum(m.card_id=='CAP_104' for m in active) if owner==self.current and has_tribe(card,'PIRATE') else 0
        if has_tribe(card,'ELEMENTAL'):extra+=sum(m.card_id=='TLC_228' for m in active)
        return amount*multiplier+extra

    def _tribal_effect(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner];name=op[0]
        if name=='tribal_group_buff':
            for m in self._distinct_type_group([m for m in p.minions if m.health>0],op[1]):self._buff(m,1,1)
        elif name=='tribal_esho':
            minions=[self._card_data(c) for c in p.deck if self._card_data(c)['type']=='MINION']
            if common_tribes(minions):
                self._effect(('buff_other_minions',2,2),ctx)
                self._effect(('zone_minion_buff',('hand','deck'),2,2),ctx)
        elif name=='tribal_draw_physical':
            c=op[1]
            if any(c is v for v in p.deck):self._draw_index(owner,next(i for i,v in enumerate(p.deck) if c is v))
        elif name=='tribal_buff_drawn':
            for c in op[1]:
                if any(c is v for v in p.hand):c.attack_bonus+=1;c.health_bonus+=1
                else:
                    m=getattr(c,'_drawn_minion',None)
                    if m is not None and m in self.players[m.owner].minions and m.health>0:self._buff(m,1,1)
        elif name=='tribal_trap_hand':
            q=self.players[1-owner];count=1+sum(e['card_id']=='EDR_526' for e in p.played_history)
            for c in self.rng.sample(q.hand,min(count,len(q.hand))):
                existing=getattr(c,'play_lock',{})
                until=max(q.turns_taken+2,existing.get('until',0) if existing.get('owner')==1-owner else 0)
                c.play_lock=dict(owner=1-owner,until=until)
        else:return False
        return True
