"""Experimental summon listeners using the existing checkpoint scheduler.

This is not a complete Hearthstone phase model. Capturing an event never drains
arbitrary effects in the middle of a helper; play/Reborn have explicit release
boundaries. See fidelity gap summon_listener_phase_order before broadening use.
"""
from copy import deepcopy
from .identities import canonical_identity,identity_resolver
from .selectors import has_tribe


class SummonEvents:
    def _summon_trigger_matches(self, wanted, kind, data, listener):
        if kind != 'minion_summoned' or len(wanted) != 3:
            return False
        if listener.health <= 0 or listener.uid == data['source']:
            return False
        if listener.card_id=='TOY_511' and data.get('goldbeard_creator_uid')==listener.uid:return False
        relation, tribe = wanted[1:]
        if relation not in ('friendly','enemy','either'):
            raise ValueError('Unknown summon relation: '+str(relation))
        if relation == 'friendly' and data['owner'] != listener.owner:
            return False
        if relation == 'enemy' and data['owner'] == listener.owner:
            return False
        return tribe is None or has_tribe(self._event_card_data(data),tribe)

    def _capture_summon_event(self, minion, origin):
        from .historical_obligation_spells import summoned as obligation_summoned
        obligation_summoned(self,minion)
        from .historical_pool_weapons import summoned as weapon_summoned
        weapon_summoned(self,minion)
        from .historical_hand_batches import summoned
        summoned(self,minion)
        player=self.players[minion.owner]
        ids=getattr(player,'historical_summoned_ids',{});ids[minion.card_id]=ids.get(minion.card_id,0)+1;player.historical_summoned_ids=ids
        tribes=getattr(player,'historical_summoned_tribes',{})
        from .selectors import TRIBES
        for tribe in TRIBES:
            if tribe!='ALL' and has_tribe(self._card_data(minion),tribe):tribes[tribe]=tribes.get(tribe,0)+1
        player.historical_summoned_tribes=tribes
        if any(m.card_id=='TTN_401' and not m.silenced for m in player.minions):self._refresh_auras()
        data=dict(owner=minion.owner,card_id=minion.card_id,source=minion.uid,origin=origin,printed_tribes=tuple(self._card_data(minion).get('races',())),entry_attack=minion.attack,entry_health=minion.health,printed_cost=self._card_data(minion)['cost'],entry_keywords=tuple(sorted(self._effective_keywords(minion))),entry_deathrattle='DEATHRATTLE' in self._effective_keywords(minion))
        data['goldbeard_creator_uid']=getattr(minion,'_historical_goldbeard_creator_uid',None)
        from .historical_tribal_batches import summon_callbacks
        callbacks=summon_callbacks(self,minion)
        if callbacks:data['historical_tribal_callbacks']=callbacks
        listeners=[] if minion.dormant else [(m,rule) for m,rule in self._event_listeners()
                   if isinstance(rule[0],tuple) and rule[0][0]=='summon'
                   and self._summon_trigger_matches(rule[0],'minion_summoned',data,m)]
        if any(listener.card_id=='TOY_511' for listener,_ in listeners):data['historical_goldbeard_donor']=deepcopy(minion)
        refresh=self._power_capture_summon(minion)
        if refresh is not None:data['refresh_power_uid']=refresh
        if self._quest_capture_summon(minion):data['quest_murloc']=True
        from .historical_sidequest_spell_batch import summon_listener
        data['historical_sidequest_listener']=summon_listener(self,minion.owner)
        from .historical_aura_finish_batch import summon_listener as aura_finish_listener
        data['historical_aura_finish_listener']=aura_finish_listener(self,minion.owner)
        if not listeners and refresh is None and not data.get('quest_murloc') and not callbacks and not data['historical_sidequest_listener'] and not data['historical_aura_finish_listener']:
            return
        event=('minion_summoned',data,listeners)
        if origin in ('play','reborn'):
            self._pending_summon_events[minion.uid]=event
            self._trace_phase('summon_notification_deferred',subject=minion.uid,origin=origin)
        else:
            self._enqueue_summon_event(event)

    def _enqueue_summon_event(self,event):
        from .historical_aura_finish_batch import summoned as aura_finish_summoned
        aura_finish_summoned(self,event[1])
        from .historical_sidequest_spell_batch import event as sidequest_batch_event
        sidequest_batch_event(self,event[0],event[1])
        self._power_publish_summon(event[1])
        self._quest_publish_summon(event[1])
        callbacks=event[1].get('historical_tribal_callbacks',())
        if callbacks:self._rule_events.append(('captured_effects',dict(operations=callbacks,context=dict(owner=event[1]['owner'],source=None,target=0,bonus=0,lifesteal=False)),[]))
        self._rule_events.append(event)
        self._trace_phase('event_queued',event_kind=event[0],subject=event[1]['source'],
                          listener_uids=[m.uid for m,_ in event[2]])

    def _publish_pending_summon(self,minion):
        event=self._pending_summon_events.pop(minion.uid,None)
        # A departed/replaced played subject does not publish a stale callback.
        if event is not None and minion in self.players[minion.owner].all_minions and minion.health>0:
            if minion.dormant:
                self._power_publish_summon(event[1])
            else:
                self._enqueue_summon_event(event)

    def _start_minion_after_play(self, context):
        if self._minion_after_play_frame is not None:
            from engine.cards import UnsupportedCard
            raise UnsupportedCard('Nested minion after-play sequences are not supported')
        self._minion_after_play_frame=dict(context=context,stage=0)
        return self._resume_minion_after_play()

    def _resume_minion_after_play(self):
        """Finish one checkpoint before advancing to the next publication.

        Cursor advancement precedes dispatch so choices resume exactly once.
        This explicit candidate ordering is not full client conformance.
        """
        frame=self._minion_after_play_frame
        if frame is None:
            return True
        cid,owner,source,cost,_=frame['context']
        while not self.terminal and self.pending_choice is None:
            stage=frame['stage']
            if stage==4:
                self._minion_after_play_frame=None
                return True
            frame['stage']+=1
            if stage==0:
                self._trace_phase('minion_postplay_stage',stage='summon',card_id=cid)
                if source is not None:self._publish_pending_summon(source)
            elif stage==1:
                self._trace_phase('minion_postplay_stage',stage='played',card_id=cid)
                def identity(card_id):
                    card=self.cards[card_id]
                    return canonical_identity(card,self.cards)
                repeated=sum(identity(entry['card_id'])==identity(cid)
                             for entry in self.players[owner].played_history)>1
                self._queue_event('minion_played',owner=owner,card_id=cid,
                                  source=source.uid if source else 0,cost=cost,historical_played_entry_attack=getattr(source,'rule_state',{}).get('historical_played_entry_attack') if source is not None else None,entry_attack=source.attack if source is not None else None,previously_played=repeated,printed_tribes=tuple(self._card_data(source if source is not None else cid).get('races',())))
            elif stage==2:
                self._trace_phase('minion_postplay_stage',stage='after_card_secrets',card_id=cid)
                self._secret_event('after_card',owner,source=source.uid if source else 0,card_id=cid)
            else:
                self._publish_follow(owner,source)
            self._settle(allow_event_choices=True)
        if self.terminal:
            self._minion_after_play_frame=None
            return True
        return False
