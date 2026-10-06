"""Persistent death and turn continuations for the experimental engine.

Operation boundaries are explicit. This does not certify every Hearthstone
phase exception or make arbitrary Python effect helpers resumable.
"""
from .cards import DEATH_EFFECTS, END_EFFECTS, START_EFFECTS, NO_CORPSE
from engine.cards import UnsupportedCard


class Lifecycle:
    def _death_operations(self, m):
        if m.silenced: return ()
        cid=m.card_id
        if cid in ('CORE_EX1_096','RLK_708'): return (('draw',1),)
        if cid=='RLK_511': return (('draw_school','FROST'),)
        if cid=='CORE_EX1_110': return (('death_summon','TOKEN_BAINE',1),)
        if cid in ('CORE_LOOT_413','CORE_SW_068'):
            return (('armor',3 if cid=='CORE_LOOT_413' else 8),)
        return tuple(DEATH_EFFECTS.get(cid,()))

    def _capture_death_wave(self):
        dead=sorted([(m,p.board.index(m)) for p in self.players for m in p.minions
                     if m.health<=0],key=lambda pair:pair[0].uid)
        if not dead: return None
        entries=[]
        for m,pos in dead:
            entries.append(dict(source=m,position=pos,operations=self._death_operations(m)))
            self.players[m.owner].board.remove(m)
            if m.silenced or m.card_id not in NO_CORPSE:
                self.players[m.owner].corpses+=1
            self._log('death',player=m.owner,card=m.card_id,entity=m.uid)
        self._refresh_auras()
        return dict(entries=entries,entry=0,operation=0,reborn=0,phase='effects')

    def _advance_death_wave(self):
        frame=self._death_frame
        entries=frame['entries']
        if frame['phase']=='effects':
            while frame['entry']<len(entries):
                entry=entries[frame['entry']];m=entry['source']
                if frame['operation']<len(entry['operations']):
                    op=entry['operations'][frame['operation']]
                    frame['operation']+=1
                    self._effect(op,dict(owner=m.owner,source=m,target=0,bonus=0,
                                        lifesteal=False,death_position=entry['position']))
                    return
                frame['entry']+=1;frame['operation']=0
            frame['phase']='reborn'
        while frame['reborn']<len(entries):
            entry=entries[frame['reborn']];frame['reborn']+=1;m=entry['source']
            if 'REBORN' not in m.keywords: continue
            reborn=self._summon(m.owner,m.card_id,min(entry['position'],len(self.players[m.owner].board)))
            if reborn:
                reborn.keywords.discard('REBORN');reborn.health=1
            return
        self._death_frame=None

    def _settle(self, allow_event_choices=False):
        if self._damage_batch_depth or self._draining_events or self._settling or self.pending_choice is not None:
            return
        self._settling=True
        try:
            while not self.terminal and self.pending_choice is None:
                self._drain_events(allow_choices=allow_event_choices or self._death_frame is not None)
                if self.pending_choice is not None or self._check_heroes(): return
                self._refresh_auras()
                if self._death_frame is None:
                    self._death_frame=self._capture_death_wave()
                    if self._death_frame is None: return
                self._advance_death_wave()
        finally:
            self._settling=False
            if self.terminal: self._clear_continuations()

    def _clear_continuations(self):
        self._death_frame=None;self._turn_frame=None
        self._event_frames.clear();self._rule_events.clear()
        self.pending_frame=None;self.pending_play=None;self.pending_choice=None

    def _begin_turn(self):
        if self._turn_frame is not None: raise UnsupportedCard('Turn already in progress')
        self.turn+=1;p=self.players[self.current]
        p.max_mana=min(10,p.max_mana+1);p.locked_mana=min(p.max_mana,p.overload_next)
        p.overload_next=0;p.mana=p.max_mana-p.locked_mana
        p.power_used=False;p.hero_attacks=0;p.cards_played=0;p.fire_spell_played=False
        for m in p.minions:m.attacks=0
        self._log('turn',player=self.current,mana=p.mana,locked_mana=p.locked_mana)
        self._refresh_auras()
        self._start_effects()

    def _start_effects(self):
        entries=[]
        for m in sorted([m for p in self.players for m in p.minions],key=lambda m:m.uid):
            rule=START_EFFECTS.get(m.card_id)
            if rule and not m.silenced and (rule[0]=='every' or m.owner==self.current):
                entries.append(dict(source=m,operations=tuple(rule[1])))
        self._turn_frame=dict(kind='start',owner=self.current,entries=entries,entry=0,
                              operation=0,entered=False,drawn=False)
        self._resume_turn()

    def _end_turn(self):
        if self._turn_frame is not None: raise UnsupportedCard('Turn already in progress')
        entries=[]
        for m in list(self.players[self.current].minions):
            operations=list(END_EFFECTS.get(m.card_id,()))
            if m.card_id=='NEW1_009':operations.insert(0,('_turn_heal_minions',))
            elif m.card_id=='CS2_058':operations.insert(0,('_turn_buff_other',))
            entries.append(dict(source=m,operations=tuple(operations)))
        self._turn_frame=dict(kind='end',owner=self.current,entries=entries,entry=0,
                              operation=0,entered=False,drawn=False)
        self._resume_turn()

    def _resume_turn(self):
        if self._resuming_turn:return
        self._resuming_turn=True
        try:
            while self._turn_frame is not None and not self.terminal and self.pending_choice is None:
                self._settle(allow_event_choices=True)
                if self.terminal or self.pending_choice is not None:return
                f=self._turn_frame
                if f['entry']<len(f['entries']):
                    entry=f['entries'][f['entry']];m=entry['source'];p=self.players[m.owner]
                    if not f['entered']:
                        if m not in p.board or m.silenced:
                            # Expiring minions still expire when silenced only
                            # if the current engine's expiration flag survives.
                            if m in p.board and f['kind']=='end' and m.expires:m.health=0
                            f['entry']+=1;continue
                        f['entered']=True
                    if f['operation']<len(entry['operations']):
                        op=entry['operations'][f['operation']];f['operation']+=1
                        if op[0]=='_turn_heal_minions':
                            for other in list(p.minions):self._heal(other.uid,1)
                        elif op[0]=='_turn_buff_other':
                            others=[other for other in p.minions if other.uid!=m.uid]
                            if others:self._buff(self.rng.choice(others),1,0)
                        else:self._effect(op,dict(owner=m.owner,source=m,target=0,bonus=0,lifesteal=False))
                        continue
                    if f['kind']=='end' and m in p.board and m.expires:m.health=0
                    f['entry']+=1;f['operation']=0;f['entered']=False
                    continue
                if f['kind']=='start':
                    if not f['drawn']:
                        f['drawn']=True;self._draw(f['owner']);continue
                    self._turn_frame=None
                else:
                    self._turn_frame=None
                    self._finish_turn(f['owner'])
        finally:
            self._resuming_turn=False
            if self.terminal:self._clear_continuations()

    def _finish_turn(self,owner):
        p=self.players[owner]
        if 0<=p.frozen_until<=self.turn:p.frozen_until=-1
        for m in p.minions:
            if 0<=m.frozen_until<=self.turn:m.frozen_until=-1
        for player in self.players:
            for m in player.minions:
                m.attack-=m.temporary_attack;m.temporary_attack=0
            player.cost_effects[:]=[e for e in player.cost_effects if e['expires'] is None or e['expires']>self.turn]
            player.timed_cost_increases[:]=[e for e in player.timed_cost_increases if e['end']>self.turn]
        p.temporary_attack=0;p.mana=0
        if self.turn>=self.max_turns:self._finish(None,'turn_limit');return
        self.current=1-owner
        self._begin_turn()
