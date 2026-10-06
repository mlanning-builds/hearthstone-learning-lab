"""Physical Discover results and continuations after the enclosing effect.

Entity references stay private and participate in whole-Game deepcopy rollback.
An ordinary choice never becomes Discover just because it returns a Card.
"""
class Discovery:
    def _defer_discover_followups(self, owner, result):
        listeners=tuple(m.uid for m in self.players[owner].minions
                        if m.card_id=='TLC_483' and not m.silenced and m.health>0)
        if result is None or not listeners:return
        op=('discover_after',owner,result,listeners)
        # Choose the innermost suspended resolution scope. Its remaining
        # operations (including further choices/modifiers) precede callbacks.
        if self._event_frames and self._event_frames[-1]['operations'] is not None:
            f=self._event_frames[-1];f['operations']=tuple(f['operations'])+(op,)
        elif self._death_frame is not None and self._death_frame['phase']=='effects':
            f=self._death_frame;e=f['entries'][f['entry']]
            e['operations']=tuple(e['operations'])+(op,)
        elif self._turn_frame is not None and self._turn_frame['entry']<len(self._turn_frame['entries']):
            f=self._turn_frame;e=f['entries'][f['entry']]
            e['operations']=tuple(e['operations'])+(op,)
        elif self.pending_frame is not None:
            self.pending_frame.operations=tuple(self.pending_frame.operations)+(op,)
        else:
            self._rule_events.append(('captured_effects',dict(operations=(op,),
                context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))

    def _discover_after(self, op):
        owner,result,listeners=op[1:]
        # A transform, burn or removal must not retarget a different physical
        # copy, even when it shares the selected card's printed identity.
        present=any(result is value for p in self.players for value in p.hand+p.deck+p.board)
        if not present:return
        active={m.uid for m in self.players[owner].minions
                if m.card_id=='TLC_483' and not m.silenced and m.health>0}
        count=sum(uid in active for uid in listeners)
        if count:result.cost_delta=getattr(result,'cost_delta',0)-count
