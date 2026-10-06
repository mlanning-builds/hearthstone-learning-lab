"""Staged construction choices and an explicit, deterministic turn clock.

The caller supplies elapsed decision time: simulator throughput is never used
as a game rule. Client animation/rope grace periods remain a fidelity gate.
"""
import math
from engine.cards import UnsupportedCard
from .generation_cards import pool,discover
from .selectors import HERO_CLASSES
RULES={'CS3_035':('none',[]),'JAIL_831':('none',[('contraband_discover',)]),
       'CATA_614':('none',[('informant_discover',)])}
def requests_for(cid):
    return {pool(card_type='SPELL',classes=k) for k in HERO_CLASSES} if cid=='CATA_614' else set()
class RemainingSetup:
    def _remaining_setup(self,decks):
        self.turn_time_limit=15 if all('CS3_035' in self._opening_effect_ids(i) for i in range(2)) else None
        self.turn_time_elapsed=0
        for p,deck in zip(self.players,decks):p.contraband_beasts=tuple(deck.contraband_beasts)
    def elapse_decision_time(self,seconds):
        if not isinstance(seconds,(int,float)) or not math.isfinite(seconds) or seconds<0:raise ValueError('Invalid elapsed seconds')
        if self.phase!='play' or self.terminal:raise ValueError('Turn clock requires an actionable play phase')
        self.turn_time_elapsed=getattr(self,'turn_time_elapsed',0)+seconds
        limit=getattr(self,'turn_time_limit',None)
        if limit is not None and self.turn_time_elapsed>=limit:
            from engine.game import Action
            self.step(Action('end'))
            return True
        return False
    def _remaining_held_entries(self,phase):
        if phase!='end':return []
        return [dict(source=None,order=c.uid,operations=(('informant_swap',c.uid),))
                for c in self.players[self.current].hand if c.card_id=='CATA_614']
    def _remaining_setup_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner]
        if name=='informant_swap':
            card=next((c for c in p.hand if c.uid==op[1] and c.card_id=='CATA_614'),None)
            if card is not None:
                state=self._b60_state(card);old=state.get('informant_class',p.hero_class)
                state['informant_class']=self.rng.choice(sorted(HERO_CLASSES-{old}))
        elif name=='informant_discover':
            k=getattr(ctx.get('physical_card'),'rule_state',{}).get('informant_class',p.hero_class)
            self._effect(discover(pool(card_type='SPELL',classes=k)),ctx)
        elif name=='contraband_discover':
            ids=getattr(p,'contraband_beasts',())
            if not ids:raise UnsupportedCard('Generated Underbelly has no reviewed fallback contraband pool')
            if any(cid not in self.cards for cid in ids):raise UnsupportedCard('Contraband selection lacks executable dependency')
            self.pending_choice=dict(owner=owner,kind='contraband_discover',discover=True,options=[dict(card_id=cid) for cid in ids]);self.phase='choice'
        else:return False
        return True
    def _remaining_setup_choice(self,choice,selected):
        if choice['kind']!='contraband_discover':return False
        from engine.game import Card
        card=Card(self._new_id(),selected['card_id']);card.cost_delta=-3
        self._discovery_result=self._enter_hand(choice['owner'],card)
        return True
