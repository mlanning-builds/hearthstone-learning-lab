"""Persistent death and turn continuations for the experimental engine.

Operation boundaries are explicit. This does not certify every Hearthstone
phase exception or make arbitrary Python effect helpers resumable.
"""
from copy import deepcopy
from .cards import DEATH_EFFECTS, END_EFFECTS, START_EFFECTS, NO_CORPSE, END_EVERY_EFFECTS
from engine.cards import UnsupportedCard


class Lifecycle:
    def _end_trigger_count(self,owner):
        player=self.players[owner]
        return 2 if self._trigger_repetitions(owner)>1 or self._active('ICC_901',owner) or any(end>=player.turns_taken for end in player.end_repeat_expiries) else 1

    def _schedule_turn_effect(self,owner,phase,delay,repeats,operations,*,source_card_id=None,stored_card=None):
        if phase not in ('start','end') or type(delay) is not int or delay<0 or type(repeats) is not int or repeats<1:
            raise ValueError('Invalid scheduled turn effect')
        player=self.players[owner]
        player.scheduled_effects.append(dict(uid=self._new_id(),phase=phase,
            due=player.turns_taken+delay,remaining=repeats,operations=tuple(operations),source_card_id=source_card_id))
        if stored_card is not None:player.scheduled_effects[-1]['stored_card']=stored_card

    def _scheduled_effect_view(self,e,owner):
        p=self.players[owner]
        result=dict(source_card_id=e.get('source_card_id'),phase=e['phase'],
                    turns_until=max(0,e['due']-p.turns_taken),remaining=e['remaining'],
                    operations=deepcopy(e['operations']))
        card=e.get('stored_card')
        if card is not None:
            # Public aura payload; never serialize the Card object or its private
            # starting-deck provenance/hand-entry bookkeeping into an observation.
            result['stored_spell']=dict(card_id=card.card_id,
                cost=self._card_stat(card,'cost',owner),
                spell_damage_bonus=getattr(card,'spell_damage_bonus',0))
        return result

    def _scheduled_turn_entries(self,phase):
        player=self.players[self.current];entries=[];retained=[]
        for effect in player.scheduled_effects:
            if effect['phase']==phase and effect['due']<=player.turns_taken:
                entries.append(dict(source=None,operations=effect['operations'],order=effect['uid'],card_id=effect.get('source_card_id'),stored_card=effect.get('stored_card')))
                if phase=='end' and effect.get('source_card_id')=='RLK_591':
                    for _ in range(self._end_trigger_count(self.current)-1):entries.append(dict(source=None,operations=effect['operations'],order=effect['uid'],card_id='RLK_591'))
                effect['remaining']-=1;effect['due']=player.turns_taken+1
            if effect['remaining']>0:retained.append(effect)
        player.scheduled_effects=retained
        return entries

    def _ordered_turn_entries(self,entries,phase):
        entries.extend(self._deadline_turn_entries(phase))
        entries.extend(self._infinity_turn_entries(phase))
        entries.extend(self._permanent_turn_entries(phase))
        from .historical_stormwind_questline_finish import turn_entries as stormwind_turn_entries
        entries.extend(stormwind_turn_entries(self,phase))
        entries.extend(self._scheduled_turn_entries(phase))
        entries.extend(self._dormant_turn_entries(phase))
        entries.extend(self._osk_held_entries(phase))
        entries.extend(self._remaining_held_entries(phase))
        entries.extend(self._held_turn_entries(phase))
        from .historical_spellstone_finish import turn_entries as stone_finish_turn_entries
        entries.extend(stone_finish_turn_entries(self,phase))
        from .historical_sidequest_spell_batch import turn_entries as sidequest_batch_turn_entries
        entries.extend(sidequest_batch_turn_entries(self,phase))
        from .historical_aura_finish_batch import turn_entries as aura_finish_turn_entries
        entries.extend(aura_finish_turn_entries(self,phase))
        from .historical_delayed_spell_finish import turn_entries as delayed_finish_turn_entries
        entries.extend(delayed_finish_turn_entries(self,phase))
        from .historical_hand_batches import turn_entries
        entries.extend(turn_entries(self,phase))
        from .historical_copy_batches import curse_turn_entries
        entries.extend(curse_turn_entries(self,phase))
        from .historical_utility_spells import iconic_turn_entries
        entries.extend(iconic_turn_entries(self,phase))
        from .historical_anomalies import turn_entries as anomaly_turn_entries
        entries.extend(anomaly_turn_entries(self,phase))
        entries.extend(self._stored_turn_entries(phase))
        entries.extend(self._learned_turn_entries(phase))
        from .historical_rock_duel import turn_entries as rock_turn_entries
        entries.extend(rock_turn_entries(self,phase))
        entries.extend(self._obligation_turn_entries(phase))
        entries.extend(self._dream_turn_entries(phase))
        from .historical_amazing_reno import turn_entries as reno_turn_entries
        entries.extend(reno_turn_entries(self,phase))
        from .historical_wisdomball import turn_entries as wisdomball_turn_entries
        entries.extend(wisdomball_turn_entries(self,phase))
        from .historical_valeera import turn_entries as valeera_turn_entries
        entries.extend(valeera_turn_entries(self,phase))
        from .historical_tavish import turn_entries as tavish_turn_entries
        entries.extend(tavish_turn_entries(self,phase))
        from .historical_uluu import turn_entries as uluu_turn_entries
        entries.extend(uluu_turn_entries(self,phase))
        from .historical_harmonics import turn_entries as harmonic_turn_entries
        entries.extend(harmonic_turn_entries(self,phase))
        from .historical_timed_spells import turn_entries as timed_spell_entries
        entries.extend(timed_spell_entries(self,phase))
        from .historical_nature_pool import turn_entries as nature_entries
        entries.extend(nature_entries(self,phase))
        from .historical_mage_quests import turn_entries as mage_quest_entries
        entries.extend(mage_quest_entries(self,phase))
        from .historical_mage_offers import turn_entries as mage_offer_entries
        entries.extend(mage_offer_entries(self,phase))
        from .historical_secret_events import turn_entries as additional_secret_entries
        entries.extend(additional_secret_entries(self,phase))
        # Use entity/effect creation order, preserving stable order on ties.
        return sorted(entries,key=lambda entry:entry.get('order',
            entry['source'].uid if entry['source'] is not None else float('inf')))

    def _unrepeated_death_operations(self, m):
        printed=() if m.silenced else self._printed_death_operations(m.card_id)
        return printed+tuple(m.attached_death_effects)+self._muradin_death_operations(m)

    def _deathrattle_repetitions(self,owner,*,weapon=False):
        from .historical_aura_finish_batch import layers
        doubled=bool(layers(self,owner,'graveyard'))
        if not weapon:doubled=doubled or any(self._active(cid,owner) for cid in ('BOT_039','FP1_031','VAC_503'))
        return max(self._trigger_repetitions(owner),2 if doubled else 1)

    def _death_operations(self, m):
        if any(source.card_id=='YOP_012' and not source.silenced and source.health>0 for player in self.players for source in player.minions):return ()
        repetitions=self._deathrattle_repetitions(m.owner)
        operations=self._unrepeated_death_operations(m)*repetitions
        if m.card_id=='RLK_912' and not m.silenced and repetitions==1:
            operations+=tuple(m.attached_death_effects)+self._muradin_death_operations(m)
        return operations

    def _printed_death_operations(self, cid):
        """Base card rules, independent of a particular entity's enchantments.

        Replay callers must choose this explicitly; death-time effects and
        printed effects are different contracts.
        """
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
            from .death_inheritance import capture
            entries.append(dict(source=m,position=pos,operations=self._death_operations(m),
                                inherited_operations=capture(self,m,self._unrepeated_death_operations(m))))
            # Preserve death-time evidence independently of later Reborn,
            # source mutation, or continuation changes. Replay semantics must
            # explicitly choose printed rules versus this recorded state.
            self._historical_death_order=getattr(self,'_historical_death_order',0)+1
            self.players[m.owner].death_records.append(dict(
                death_order=self._historical_death_order,
                card_id=m.card_id,owner=m.owner,position=pos,turn=self.turn,
                entity=deepcopy(m),operations=deepcopy(entries[-1]['operations']),
                printed_operations=deepcopy(self._printed_death_operations(m.card_id))))
            from .historical_movements import record
            record(self,'destroyed')
            self.players[m.owner].death_history.append(m.card_id)
            self.players[m.owner].minions_died_turn+=1
            self.players[m.owner].board.remove(m)
            if m.silenced or m.card_id not in NO_CORPSE:
                self._gain_corpses(m.owner,1)
            self._log('death',player=m.owner,card=m.card_id,entity=m.uid)
        for entry in entries:
            m=entry['source']
            from .historical_starships import capture_piece
            capture_piece(self,m,entry['position'])
            self._secret_capture_death(m,entry['position'])
            self._queue_event('minion_died',owner=m.owner,source=m.uid,card_id=m.card_id,attack=m.attack,max_health=m.max_health,
                              inherited_operations=entry['inherited_operations'],printed_tribes=tuple(self._card_data(m).get('races',())))
            if m.card_id=='TLC_513t2' and self.players[m.owner].ninja_returns:
                # A player-bound death listener, not a silence-removable or
                # replayable Deathrattle on the Ninja itself.
                self._rule_events.append(('captured_effects',dict(
                    operations=(('on_draw_shuffle','TLC_513t2',1,0),),
                    context=dict(owner=m.owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
        self._refresh_auras()
        return dict(entries=entries,entry=0,operation=0,reborn=0,phase='effects')

    def _advance_death_wave(self):
        frame=self._death_frame
        entries=frame['entries']
        self._trace_phase('death_wave_advance', stage=frame['phase'], entry=frame['entry'], reborn=frame['reborn'])
        if frame['phase']=='effects':
            while frame['entry']<len(entries):
                entry=entries[frame['entry']];m=entry['source']
                if frame['operation']<len(entry['operations']):
                    context=dict(owner=m.owner,source=m,target=0,bonus=0,
                                 lifesteal=False,death_position=entry['position'])
                    cursor=dict(operations=entry['operations'],operation=frame['operation'])
                    op=self._take_effect_operation(cursor,context)
                    entry['operations']=cursor['operations'];frame['operation']=cursor['operation']
                    self._effect_checkpoint(op,context)
                    return
                frame['entry']+=1;frame['operation']=0
            frame['phase']='reborn'
        while frame['reborn']<len(entries):
            entry=entries[frame['reborn']];frame['reborn']+=1;m=entry['source']
            if 'REBORN' not in m.keywords: continue
            reborn=self._summon(m.owner,m.card_id,min(entry['position'],len(self.players[m.owner].board)), entry_origin='reborn', entry_site='lifecycle._advance_death_wave', entry_source=m,copy_from=m if (m.card_id=='CAP_800' or 'EDR_100t9' in self._dark_list(m)) and not m.silenced else None)
            if reborn:
                reborn.keywords.discard('REBORN');reborn.health=reborn.max_health if (m.card_id=='CAP_800' or 'EDR_100t9' in self._dark_list(m)) and not m.silenced else 1
                self._trace_entity('reborn_initialized', reborn)
                self._publish_pending_summon(reborn)
            return
        self._death_frame=None

    def _settle(self, allow_event_choices=False):
        if self._damage_batch_depth or self._draining_events or self._settling or self.pending_choice is not None:
            return
        self._quest_deliver_ready()
        self._settling=True
        try:
            while not self.terminal and self.pending_choice is None:
                self._drain_events(allow_choices=allow_event_choices or self._death_frame is not None)
                if self.pending_choice is not None or self._check_heroes(): return
                # Repeat frames retain deaths/winner checks across choices, but
                # still resolve child events at their normal operation boundary.
                if self._genn_checkpoint():continue
                if self._entity_checkpoint():continue
                if self._quest_family_hand_checkpoint():continue
                if self._lasting_checkpoint():continue
                if self._shatter_update():continue
                if self._spell_repeat_depth:return
                self._dormant_full_board()
                self._refresh_auras()
                if self._death_frame is None:
                    self._death_frame=self._capture_death_wave()
                    if self._death_frame is None:
                        if self._colossal_space_checkpoint():continue
                        return
                self._advance_death_wave()
        finally:
            self._settling=False
            if self.terminal: self._clear_continuations()

    def _clear_continuations(self):
        self._requested_turn_end=None
        self._rewind_state=None
        self._spell_repeat_depth=0
        self._attack_windows=[]
        self._power_frame=None
        self._pending_follow=None
        self._pending_summon_events.clear()
        self._minion_after_play_frame=None
        self._death_frame=None;self._turn_frame=None
        self._event_frames.clear();self._rule_events.clear()
        self.pending_frame=None;self.pending_play=None;self.pending_choice=None

    def _complete_requested_turn_end(self):
        request=getattr(self,'_requested_turn_end',None)
        if request is None:return
        if self.terminal or request!=(self.current,self.turn):
            self._requested_turn_end=None;return
        if any((self.pending_choice,self.pending_frame,self.pending_play,self._turn_frame,
                self._death_frame,self._rule_events,self._event_frames,self._pending_summon_events,
                self._minion_after_play_frame,self._pending_follow,getattr(self,'_power_frame',None))):
            return
        self._requested_turn_end=None
        self._end_turn()

    def _begin_turn(self):
        if self._turn_frame is not None: raise UnsupportedCard('Turn already in progress')
        while self.players[self.current].skipped_turns_pending:
            self.players[self.current].skipped_turns_pending-=1
            self.turn+=1
            self._log('turn_skipped',player=self.current)
            if self.turn>=self.max_turns:self._finish(None,'turn_limit');return
            self.current=1-self.current
        self.turn_time_elapsed=0
        self.turn+=1;p=self.players[self.current]
        p.turns_taken+=1
        # Thaddius changes at its controller's start in each active zone.
        # A newly generated physical card begins odd, rather than inheriting
        # a global turn parity or another copy's accumulated state.
        for zone in (p.hand,p.deck,p.minions):
            for index,entity in enumerate(zone):
                if self._card_data(entity)['id']=='NX2_033' and not getattr(entity,'silenced',False):
                    if isinstance(entity,str):
                        from engine.game import Card
                        entity=Card(self._new_id(),entity);zone[index]=entity
                    state=self._b60_state(entity)
                    state['historical_thaddius_parity']=1-state.get('historical_thaddius_parity',1)
        from .historical_brukan import rotate as rotate_brukan
        rotate_brukan(self,self.current)
        self._b60_turn_start(self.current)
        self._imbue_expire_attack(self.current)
        for player in self.players:
            for c in player.hand+player.deck:
                for effect in getattr(c,'growing_discounts',[]):
                    if effect['owner']==self.current:c.cost_delta=getattr(c,'cost_delta',0)-effect['amount']
        p.spells_previous=p.spells_turn;p.spells_turn=[]
        for player in self.players:
            player.damaged_characters_turn.clear()
            player.discoveries_this_turn=0
            player.hero_immune_expiry_players[:]=[owner for owner in player.hero_immune_expiry_players if owner!=self.current]
            player.healing_block_expiry_players[:]=[owner for owner in player.healing_block_expiry_players if owner!=self.current]
            player.spell_schools_this_turn.clear()
            player.spell_damage_turn=0
            player.hero_damage_taken_turn=0
            player.hero_damage_events_turn=0
            player.hero_health_changed_turn=False
            player.hero_healed_turn=False
            from .historical_physical_forms import expire_form_buffs
            if player is self.players[0]:expire_form_buffs(self,'start')
            for m in player.all_minions:
                m.temporary_keywords[:]=[e for e in m.temporary_keywords if not(e['phase']=='start' and e['turn']<=self.turn)]
            player.minions_died_turn=0
            player.spells_cast_turn=0
            player.healing_done_turn=0
        p.minion_played_last_turn=p.minion_played_this_turn;p.minion_played_this_turn=False
        p.historical_elemental_completed_streak=getattr(p,'historical_elemental_completed_streak',0)+1 if {'ELEMENTAL','ALL'} & p.played_tribes else 0
        p.previous_tribes=p.played_tribes;p.previous_schools=p.played_schools
        p.historical_elementals_previous=getattr(p,'historical_elementals_played',0);p.historical_elementals_played=0
        p.played_tribes=set();p.played_schools=set()
        p.max_mana=min(p.mana_capacity,p.max_mana+1);p.locked_mana=min(p.max_mana,p.overload_next)
        p.historical_mana_burn_active=getattr(p,'historical_mana_burn_next',0)
        p.historical_mana_burn_next=0
        p.overload_next=0;p.temporary_mana_available=0;p.mana=max(0,p.max_mana-p.locked_mana-p.historical_mana_burn_active)
        if p.secondary_power is not None:p.secondary_power['used']=False
        p.power_used=False;p.hero_attacks=0;p.cards_played=0;p.fire_spell_played=False
        for m in p.minions:m.attacks=0
        self._log('turn',player=self.current,mana=p.mana,locked_mana=p.locked_mana)
        self._refresh_auras()
        self._start_effects()

    def _start_effects(self):
        entries=[]
        for m in sorted([m for p in self.players for m in p.minions],key=lambda m:m.uid):
            rule=START_EFFECTS.get(m.card_id)
            operations=[]
            if rule and not m.silenced and (rule[0]=='every' or m.owner==self.current):operations.extend(rule[1])
            if m.owner==self.current:
                from .forge_intrinsics import values as intrinsic_values
                operations.extend(op for group in intrinsic_values(m,'start_effects') for op in group)
            if operations:entries.append(dict(source=m,operations=tuple(operations)))
        entries=self._ordered_turn_entries(entries,'start')
        self._turn_frame=dict(kind='start',owner=self.current,entries=entries,entry=0,
                              operation=0,entered=False,drawn=False)
        self._resume_turn()

    def _end_turn(self):
        self._b60_turn_end(self.current)
        if self._turn_frame is not None: raise UnsupportedCard('Turn already in progress')
        entries=[]
        for m in sorted([m for player in self.players for m in player.minions],key=lambda m:m.uid):
            operations=list(END_EVERY_EFFECTS.get(m.card_id,()))
            if m.owner==self.current:
                operations+=list(END_EFFECTS.get(m.card_id,()))
                # Magnetic parts retain their own end triggers on the host.
                for part in m.rule_state.get('magnetic_parts',()):
                    if part['card_id']=='TTN_730t':operations.append(('copy_self_right',1))
                    elif part['card_id']=='BOT_107':operations.append(('area_damage','other_characters',1))
                from .forge_intrinsics import values
                operations.extend(op for group in values(m,'end_effects') for op in group)
                if m.card_id=='NEW1_009':operations.insert(0,('_turn_heal_minions',))
                elif m.card_id=='CS2_058':operations.insert(0,('_turn_buff_other',))
            if operations or (m.owner==self.current and m.expires):
                repeats=self._end_trigger_count(m.owner) if operations else 1
                for index in range(repeats):
                    entries.append(dict(source=m,operations=deepcopy(tuple(operations)),
                                        expire=index==repeats-1))
        for amount in self.players[self.current].permanent_end_damage:
            entries.append(dict(source=None,operations=(('_permanent_hero_damage',amount),)))
        entries=self._ordered_turn_entries(entries,'end')
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
                    entry=f['entries'][f['entry']];m=entry['source'];p=self.players[m.owner if m is not None else f['owner']]
                    if not f['entered']:
                        if m is not None and (m not in p.board or (m.silenced and not entry.get('dormant_entry')) or bool(m.dormant) != entry.get('dormant_entry',False)):
                            # Expiring minions still expire when silenced only
                            # if the current engine's expiration flag survives.
                            if m in p.board and f['kind']=='end' and m.owner==f['owner'] and m.expires and entry.get('expire',True):m.health=0
                            f['entry']+=1;continue
                        f['entered']=True
                    if f['operation']<len(entry['operations']):
                        context=dict(owner=m.owner if m is not None else f['owner'],source=m,target=0,bonus=0,lifesteal=False)
                        if entry.get('stored_card') is not None:context['stored_card']=entry['stored_card']
                        cid=entry.get('card_id')
                        if cid and self.cards[cid]['type']=='SPELL':
                            context.update(card_id=cid,spell=True,bonus=self._spell_damage(f['owner'],cid),lifesteal='LIFESTEAL' in self.cards[cid].get('mechanics',[]))
                        cursor=dict(operations=entry['operations'],operation=f['operation'])
                        op=self._take_effect_operation(cursor,context)
                        entry['operations']=cursor['operations'];f['operation']=cursor['operation']
                        if op[0]=='_turn_add':
                            for _ in range(op[2]):self._add(f['owner'],op[1])
                        elif op[0]=='_permanent_hero_damage':
                            self._damage(self.hero_id(1-f['owner']),op[1],damage_source=None,damage_owner=f['owner'])
                        elif op[0]=='_turn_heal_minions':
                            for other in list(p.minions):self._heal(other.uid,1,healer=f['owner'])
                        elif op[0]=='_turn_buff_other':
                            others=[other for other in p.minions if other.uid!=m.uid]
                            if others:self._buff(self.rng.choice(others),1,0)
                        else:self._effect_checkpoint(op,context)
                        continue
                    if f['kind']=='end' and m is not None and m in p.board and m.owner==f['owner'] and m.expires and entry.get('expire',True):m.health=0
                    f['entry']+=1;f['operation']=0;f['entered']=False
                    continue
                if f['kind']=='start':
                    if not f['drawn']:
                        f['drawn']=True
                        if not self._active('TIME_617',f['owner']):self._turn_card_draw(f['owner'])
                        continue
                    self._turn_frame=None
                else:
                    if not f.get('control_returned'):
                        f['control_returned']=True
                        self._return_temporary_control(f['owner'])
                        continue
                    if not f.get('temporary_cleaned'):
                        f['temporary_cleaned']=True
                        self._expire_temporary_hand(f['owner'])
                        continue
                    self._turn_frame=None
                    self._finish_turn(f['owner'])
        finally:
            self._resuming_turn=False
            if self.terminal:self._clear_continuations()

    def _finish_turn(self,owner):
        from .historical_stormwind_questline_finish import end_turn as stormwind_end_turn
        stormwind_end_turn(self)
        from .historical_valeera import clear as clear_reflections
        clear_reflections(self,owner)
        from .historical_devout import flip as flip_xyrella
        flip_xyrella(self,owner)
        from .historical_mad_genius import rotate as rotate_boom
        rotate_boom(self,owner)
        from .historical_lone_ranger import rotate as rotate_reno
        rotate_reno(self,owner)
        from .historical_physical_forms import expire_form_buffs
        expire_form_buffs(self,'end')
        self._investigation_turn_finished(owner)
        self._infinity_expire()
        self.players[owner].last_turn_ended=self.turn
        self._expire_follow()
        p=self.players[owner]
        p.end_repeat_expiries[:]=[end for end in p.end_repeat_expiries if end>p.turns_taken]
        if 0<=p.frozen_until<=self.turn:p.frozen_until=-1
        for m in p.all_minions:
            if 0<=m.frozen_until<=self.turn and not m.rule_state.get('historical_permanent_frozen'):m.frozen_until=-1
        for player in self.players:
            player.temporary_attack=0
            player.avatar_form.clear()
            for m in player.all_minions:
                self._adjust_minion_attack(m,-m.temporary_attack);m.temporary_attack=0
                m.rule_state.pop('avatar_form',None)
                m.temporary_keywords[:]=[e for e in m.temporary_keywords if not(e['phase']=='end' and e['turn']<=self.turn)]
            player.cost_effects[:]=[e for e in player.cost_effects if e['expires'] is None or e['expires']>self.turn]
            player.timed_cost_increases[:]=[e for e in player.timed_cost_increases if e['end']>self.turn]
        p.payment_effects[:]=[e for e in p.payment_effects if not (isinstance(e,dict) and e.get('kind')=='historical_murloc_health' and e['turn']<=self.turn)]
        p.temporary_attack=0;p.temporary_mana_available=0;p.mana=0
        p.historical_mana_burn_active=0
        if self.turn>=self.max_turns:self._finish(None,'turn_limit');return
        if p.extra_turns_pending:
            p.extra_turns_pending-=1
            self.current=owner
        elif getattr(self,'_historical_turn_queue',None):self.current=self._historical_turn_queue.pop(0)
        else:self.current=1-owner
        self._begin_turn()
