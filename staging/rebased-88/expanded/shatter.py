"""Constructed Shatter hand transitions and the complete pinned card family.

Rules reference: Hearthstone developer ClayByte, February 9, 2026:
https://www.reddit.com/r/hearthstone/comments/1r0e5uz/new_keyword_shatter/
Splitting is deferred until an effect checkpoint, after draw modifiers and draw
listeners. Recombined physical cards retain their combined state across copies
and shuffles. Public transition logs deliberately omit the hidden identity.
"""
from copy import deepcopy
from engine.game import Card

HALVES={
 'CATA_134':('CATA_134t','CATA_134t2'),
 'CATA_306':('CATA_306t1','CATA_306t2'),
 'CATA_479':('CATA_479t','CATA_479t2'),
 'CATA_489':('CATA_489t','CATA_489t2'),
 'CATA_820':('CATA_820t','CATA_820t2'),
}
PARENTS={half:parent for parent,halves in HALVES.items() for half in halves}
TOKEN_IDS=set(PARENTS)|{'CATA_134t3','CATA_479t3'}
RULES={
 'CATA_134t':('none',[('summon','CATA_134t3',2)]),
 'CATA_134t2':('none',[('shatter_board_death', 'CATA_134t3')]),
 'CATA_306t1':('friendly_minion',[('buff',2,3),('keyword','ELUSIVE')]),
 'CATA_306t2':('friendly_minion',[('shatter_copy_target',)]),
 'CATA_479t':('none',[('summon','CATA_479t3',2)]),
 'CATA_479t2':('none',[('board_buff',1,0),('board_keyword','DIVINE_SHIELD')]),
 'CATA_489t':('character',[('damage',4)]),
 'CATA_489t2':('none',[('area_damage','enemies',2)]),
 'CATA_820t':('none',[('filtered_draw',(('type','eq','MINION'),),3)]),
 'CATA_820t2':('none',[('hand_buff',2,2)]),
 'CATA_202':('none',[('shatter_generate_combined',)]),
 'TIME_101':('none',[]),
}
for parent,(left,right) in HALVES.items():
    mode=RULES[left][0] if RULES[left][0]!='none' else RULES[right][0]
    RULES[parent]=(mode,RULES[left][1]+RULES[right][1])
TRIGGERS={'TIME_101':('friendly_shatter',[('area_damage','enemy_minions',2)])}

class Shatter:
    def _shatter_merge(self,left,right,parent):
        card=deepcopy(left);card.uid=self._new_id();card.card_id=parent
        for field in ('cost_delta','attack_bonus','health_bonus','spell_damage_bonus'):
            setattr(card,field,getattr(left,field,0)+getattr(right,field,0))
        for field in ('growing_discounts','temporary_cost_discounts','_follow_effects'):
            values=deepcopy(getattr(left,field,[])+getattr(right,field,[]))
            if values:setattr(card,field,values)
        # Non-additive physical effects survive combination. For equal setters
        # the value remains fixed, rather than incorrectly summing two costs.
        if hasattr(right,'set_cost'):card.set_cost=right.set_cost
        if hasattr(right,'play_lock'):card.play_lock=deepcopy(right.play_lock)
        state=deepcopy(getattr(left,'rule_state',{}))
        for key,value in getattr(right,'rule_state',{}).items():
            if key in ('temporary','shatter_combined'):state[key]=bool(state.get(key)) or bool(value)
            elif key=='aura_duration_delta':state[key]=state.get(key,0)+value
            elif key not in state:state[key]=deepcopy(value)
        state['shatter_combined']=True;card.rule_state=state
        return card

    def _shatter_update(self):
        if self.phase=='mulligan':return False
        changed=False
        for owner,player in enumerate(self.players):
            for original in list(player.hand):
                if original.card_id not in HALVES or getattr(original,'rule_state',{}).get('shatter_combined'):continue
                if not any(c is original for c in player.hand):continue
                left_id,right_id=HALVES[original.card_id]
                player.hand.remove(original)
                left=deepcopy(original);left.uid=self._new_id();left.card_id=left_id
                player.hand.insert(0,left)
                if len(player.hand)<10:
                    right=deepcopy(original);right.uid=self._new_id();right.card_id=right_id
                    player.hand.append(right)
                # Capture listener membership at the actual split; later
                # minions cannot retroactively observe this event.
                self._queue_event('card_shattered',owner=owner)
                self._log('shatter',player=owner)
                changed=True
            index=0
            while index+1<len(player.hand):
                left,right=player.hand[index:index+2]
                parent=PARENTS.get(left.card_id)
                if parent and right.card_id in HALVES[parent] and right.card_id!=left.card_id:
                    combined=self._shatter_merge(left,right,parent)
                    player.hand[index:index+2]=[combined]
                    self._log('shatter_combine',player=owner)
                    changed=True
                    # The combined card remains between any outer pieces.
                index+=1
        return changed

    def _shatter_effect(self,op,ctx):
        name=op[0];owner=ctx['owner']
        if name=='shatter_board_death':
            for minion in self.players[owner].minions:
                if minion.health>0:minion.attached_death_effects.append(('summon',op[1],1))
        elif name=='shatter_copy_target':
            target=next((m for p in self.players for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
            if target is not None:self._summon(owner,target.card_id,copy_from=target,entry_origin='copy',entry_site='shatter',entry_source=ctx.get('source'))
        elif name=='shatter_generate_combined':
            from .selectors import classes
            choices=[cid for cid in HALVES if self.players[owner].hero_class not in classes(self.cards[cid])]
            if choices:
                card=Card(self._new_id(),self.rng.choice(choices))
                self._b60_state(card)['shatter_combined']=True
                self._enter_hand(owner,card)
        else:return False
        return True
