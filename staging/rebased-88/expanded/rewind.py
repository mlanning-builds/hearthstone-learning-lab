"""Paid-play Rewind snapshots and closed-outcome card implementations.

Rewind restores the pre-play game state while retaining the advanced RNG and
player decision history. It is a separate choice from the Battlecry, and is not
activated by recruiting a minion or by an internal spell cast. Lethal ends the
game without a choice. Snapshot contents never enter public observations.
"""
from copy import deepcopy
from engine.game import Card
from .rewind_generators import REWINDS as STAGED_REWINDS

RULES={
 'TIME_001':('none',[('damage_random_enemy',2)]*3),
 'TIME_003':('none',[('rewind_draw_buff',2,2)]),
 'TIME_004':('none',[('damage_random_enemy',7)]),
 'TIME_008':('none',[('rewind_discard_both',)]),
 'TIME_433':('none',[('rewind_silence_destroy',)]),
 'TIME_610':('none',[('rewind_shade',)]*4),
 'TIME_441':('none',[('random_distinct_damage',4,2)]),
}
TOKEN_IDS={'TIME_610t2'}
REWINDS={cid:1 for cid in RULES}

class Rewind:
    def _rewind_begin(self,action):
        if getattr(self,'_rewind_replaying',False):return
        self._rewind_state=None
        card=next(c for c in self.players[self.current].hand if c.uid==action.source)
        maximum=REWINDS.get(card.card_id,STAGED_REWINDS.get(card.card_id,0))
        count=getattr(card,'rule_state',{}).get('rewinds_remaining',maximum)
        if maximum and count and self._active('END_036',self.current):
            self._rewind_state=dict(keep_all=True,remaining=count,owner=self.current,card_id=card.card_id)
            return
        if maximum and count:
            snapshot=deepcopy({k:v for k,v in self.__dict__.items() if not k.startswith('_rewind_')})
            self._rewind_state=dict(snapshot=snapshot,action=action,remaining=count,owner=self.current,card_id=card.card_id)

    def _rewind_offer(self,context):
        state=getattr(self,'_rewind_state',None)
        if not state or state['remaining']<=0 or self.terminal:return False
        if context[0]!=state['card_id'] or context[1]!=state['owner']:return False
        state['after_play']=context
        self.pending_choice=dict(owner=state['owner'],kind='rewind',remaining=state['remaining'],options=[
            dict(card_id=state['card_id'],label='Keep timeline',rewind=False),
            dict(card_id=state['card_id'],label='Rewind',rewind=True)])
        self.phase='choice'
        return True

    def _rewind_choose(self,index):
        state=self._rewind_state
        if state.get('kind')=='power':
            return self._rewind_power_choose(index)
        if index==0:
            context=state['after_play'];self._rewind_state=None
            self.pending_choice=None;self.phase='play';self._after_play(context)
            return
        rng=self.rng.getstate();history=deepcopy(self.history)
        remaining=state['remaining']-1;action=state['action'];snapshot=state['snapshot']
        self.__dict__.clear();self.__dict__.update(deepcopy(snapshot))
        self.rng.setstate(rng);self.history=history
        card=next(c for c in self.players[state['owner']].hand if c.uid==action.source)
        self._b60_state(card)['rewinds_remaining']=remaining
        self._rewind_state=dict(snapshot=snapshot,action=action,remaining=remaining,owner=state['owner'],card_id=state['card_id']) if remaining else None
        self._rewind_replaying=True
        self._log('rewind',player=state['owner'])
        try:self._play(action)
        finally:self._rewind_replaying=False

    def _rewind_effect(self,op,ctx):
        name=op[0];owner=ctx['owner']
        if name=='rewind_shade':
            minion=self._summon(owner,'TIME_610t2',entry_origin='effect',entry_site='rewind_shade')
            self._grant_bonus_effects(minion,2)
        elif name=='rewind_draw_buff':
            card=self._draw_filtered(owner,(('type','eq','MINION'),))
            if card is not None:card.attack_bonus+=op[1];card.health_bonus+=op[2]
        elif name=='rewind_discard_both':
            # Select both random cards before any discard listener resolves.
            for recipient in (owner,1-owner):self._discard_random(recipient,1)
        elif name=='rewind_silence_destroy':
            choices=list(self.players[1-owner].minions)
            if choices:
                target=self.rng.choice(choices);self._silence(target);target.health=0
        else:return False
        return True

    def _rewind_power_begin(self,target,*,secondary=False):
        if getattr(self,'_rewind_replaying',False):return
        power=self.players[self.current].primary_power
        if secondary or not power or power['card_id']!='END_000p':return
        if self._active('END_036',self.current):
            self._rewind_state=None
            return
        snapshot=deepcopy({k:v for k,v in self.__dict__.items() if not k.startswith('_rewind_')})
        self._rewind_state=dict(kind='power',snapshot=snapshot,target=target,
            remaining=1,owner=self.current,card_id=power['card_id'])

    def _rewind_power_offer(self):
        state=getattr(self,'_rewind_state',None)
        if not state or state.get('kind')!='power' or not state['remaining']:return False
        # A lethal outcome cannot be rerolled. Hero death checking is otherwise
        # deferred until after the complete power sequence.
        if self.terminal or any(p.health<=0 for p in self.players):
            self._rewind_state=None
            return False
        self.pending_choice=dict(owner=state['owner'],kind='rewind',remaining=1,options=[
            dict(card_id=state['card_id'],label='Keep timeline',rewind=False),
            dict(card_id=state['card_id'],label='Rewind',rewind=True)])
        self.phase='choice'
        return True

    def _rewind_power_choose(self,index):
        state=self._rewind_state
        if index==0:
            self._rewind_state=None;self.pending_choice=None;self.phase='play'
            self._resume_power_sequence()
            return
        rng=self.rng.getstate();history=deepcopy(self.history)
        self.__dict__.clear();self.__dict__.update(deepcopy(state['snapshot']))
        self.rng.setstate(rng);self.history=history
        self._rewind_state=None;self._rewind_replaying=True
        self._log('rewind',player=state['owner'])
        try:self._power(state['target'])
        finally:self._rewind_replaying=False
