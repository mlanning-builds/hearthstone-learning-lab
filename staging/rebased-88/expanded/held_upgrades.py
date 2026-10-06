"""Physical held counters, turn upgrades, and remaining-mana snapshots.

Timers are explicit turn-frame entries. They never advance from observation,
from opponent turns, or repeatedly from end-turn multipliers.
"""
MANA_THRESHOLDS={'CATA_131':4,'CATA_132':8,'CATA_140':25}
SMOLDERING={'FIR_911','FIR_914','FIR_916'}
TURN_UPGRADES=SMOLDERING|{'CATA_498','CATA_206'}

class HeldUpgrades:
    def _held_spend(self,owner,amount):
        if amount<=0:return
        for c in self.players[owner].hand:
            limit=MANA_THRESHOLDS.get(c.card_id)
            if limit:
                state=self._b60_state(c)
                state['held_mana_spent']=min(limit,state.get('held_mana_spent',0)+amount)

    def _held_turn_entries(self,phase):
        if phase!='end':return []
        return [dict(source=None,order=c.uid,operations=(('held_tick',c.uid,c.card_id),))
                for c in self.players[self.current].hand if c.card_id in TURN_UPGRADES]

    def _held_split(self,op,ctx):
        name=op[0];card=ctx.get('physical_card')
        if name=='held_whelps':
            ready=self._b60_state(card).get('held_mana_spent',0)>=8
            ops=(('summon','CATA_132t',1),)*2 if ready else (('add','CATA_132t',2),)
            return ops[0],ops[1:]
        if name=='held_draw':
            count=1+self._b60_state(card).get('held_turn_ends',0)
            return ('draw',1), (('draw',count-1),) if count>1 else ()

    def _held_effect(self,op,ctx):
        name=op[0]
        if not name.startswith('held_') or name not in ('held_tick','held_ramp','held_buff','held_area','held_cleave','held_picklock'):return False
        owner=ctx['owner'];p=self.players[owner];card=ctx.get('physical_card')
        if name=='held_tick':
            card=next((c for c in p.hand if c.uid==op[1] and c.card_id==op[2]),None)
            if card is None:return True
            state=self._b60_state(card)
            if state.get('held_last_tick')==self.turn:return True
            state['held_last_tick']=self.turn
            state['held_turn_ends']=state.get('held_turn_ends',0)+1
            if card.card_id=='CATA_206':self._reroll_held_bonus(card)
            if card.card_id in SMOLDERING and state['held_turn_ends']>=3:self._discard_card(owner,card)
        elif name=='held_ramp':
            if self._b60_state(card).get('held_mana_spent',0)>=4:
                gain=min(1,p.mana_capacity-p.max_mana);p.max_mana+=gain;p.mana=min(p.mana_capacity,p.mana+gain)
            else:self._effect(('temporary_mana',1),ctx)
        elif name=='held_picklock':
            self._deal_effect(ctx.get('target',0),self._b60_state(card).get('picklock_value',1),ctx)
        else:
            age=self._b60_state(card).get('held_turn_ends',0)
            if name=='held_buff':self._effect(('buff',1+age,1+age),ctx)
            elif name=='held_area':self._effect(('area_damage','enemy_minions',1+age),ctx)
            elif name=='held_cleave':
                enemies=self.players[1-owner].minions
                victims=self.rng.sample(enemies,min(2,len(enemies)))
                with self._damage_batch():
                    for m in victims:self._deal_effect(m.uid,2+age,ctx)
        return True
