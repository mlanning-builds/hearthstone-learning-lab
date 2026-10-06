"""Resumable card-effect sequences, with explicit per-operation checkpoints.

Damage batches protect simultaneous hits; this is not a complete replacement for
Hearthstone's trigger/death scheduler. Frames are private engine state and are
included in step's deep-copy rollback, never in player observations.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from engine.cards import UnsupportedCard


@dataclass
class PlayFrame:
    operations: tuple
    context: dict
    next_operation: int = 0


class Resolution:
    def _split_fixed_summon(self, operation, context):
        if self._fire_effect_guard(operation,context):return ('batch30_noop',),()
        expanded=self._finish_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._craft_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._essence_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._osk_split(operation,context)
        if expanded is not None:return expanded
        """Split only plain fixed summons at an existing frame checkpoint.

        Keep a compact remainder in the owning frame; never allocate count
        copies. Compound payment/copy/grant helpers retain their own boundary.
        This candidate checkpoint policy is not a client timing oracle.
        """
        expanded=self._azshara_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._gelbin_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._brox_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._rafaam_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._fabled_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._learned_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._herald_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._colossal_body_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._future_summon_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._autocast_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._imbue_consumer_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._rewindgen_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._mutation_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._entity_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._stored_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._dark_global_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._dark_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._imbue_split(operation,context)
        if expanded is not None:return expanded
        if operation[0]=='descending_aoe':
            amount=operation[1]
            if amount<=0:return ('batch30_noop',),()
            tail=(('descending_aoe',amount-1),) if amount>1 else ()
            return ('area_damage','all_minions',amount),tail
        if operation[0]=='armor_aoe':
            player=self.players[context['owner']]
            spent=min(operation[1],player.armor);player.armor-=spent
            return self._split_fixed_summon(('armor_damage_waves',spent),context)
        if operation[0]=='armor_damage_waves':
            remaining=operation[1]
            if remaining<=0:return ('batch30_noop',),()
            tail=(('armor_damage_waves',remaining-1),) if remaining>1 else ()
            return ('area_damage','all_minions',1),tail
        if operation[0] in ('missiles','missile_series'):
            remaining=operation[2]+(context.get('bonus',0) if operation[0]=='missiles' else 0)
            if operation[0]=='missiles' and context.get('spell'):remaining*=self._spell_multiplier(context['owner'])
            if remaining<=0:return ('batch30_noop',),()
            tail=(('missile_series',operation[1],remaining-1),) if remaining>1 else ()
            return ('missile_hit',operation[1]),tail
        from .automatic_cards import split_automatic_card
        expanded=split_automatic_card(self,operation,context)
        if expanded is not None:return expanded
        expanded=self._cast_spell_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._dream_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._choicegen_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._leyline_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._generation_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._tribal_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._force_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._on_draw_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._replay_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._held_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._origin_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._draw_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._local_split(operation,context)
        if expanded is not None:return expanded
        expanded=self._b60_split(operation,context)
        if expanded is not None:return expanded
        if operation[0]=='summon_opponent' and operation[2]>1:
            return ('summon_opponent',operation[1],1), (('summon_opponent',operation[1],operation[2]-1),)
        if operation[0]=='fill_board_target_copies':
            player=self.players[context['owner']]
            chosen=next((m for m in player.minions if m.uid==context.get('target') and m.health>0),None)
            count=max(0,7-len(player.board)) if chosen is not None else 0
            operations=(('summon_target_copy',chosen),)*count
            return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
        if operation[0]=='resurrect_costs_reborn' and len(operation[1])>1:
            return ('resurrect_costs_reborn',operation[1][:1]), (('resurrect_costs_reborn',operation[1][1:]),)
        if operation[0]=='summon_played_one_cost':
            # Snapshot the qualifying history before child summon events run.
            operations=tuple(('summon',h['card_id'],1)
                for h in self.players[context['owner']].played_history
                if h['cost']==1 and self.cards[h['card_id']]['type']=='MINION')
            return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
        if operation[0] == 'recruits_shield':
            ops=(('one_shield_recruit',),)*operation[1]
            return (ops[0],ops[1:]) if ops else (('batch30_noop',),())
        if operation[0] == 'choose_cenarius' and self._active('CORE_OG_044',context['owner']):
            return ('buff_other_minions',1,3), (('summon','EDR_209t5',1),)
        if operation[0] == 'bottom_demons':
            from .selectors import has_tribe
            from engine.game import Card
            p=self.players[context['owner']];ops=[]
            for i,c in enumerate(p.deck[:operation[1]]):
                if self._card_data(c)['type']=='MINION' and has_tribe(self._card_data(c),'DEMON'):
                    if not isinstance(c,Card):c=Card(self._new_id(),c);p.deck[i]=c
                    ops.append(('recruit_deck_uid',c.uid))
            return (ops[0],tuple(ops[1:])) if ops else (('batch30_noop',),())
        if operation[0] == 'summon_death_identity':
            p=self.players[context['owner']]
            bonus=sum(self.cards[cid]['name']==operation[3] for cid in p.death_history)
            operations=(('summon_identity_buff',operation[1],bonus),)*operation[2]
            return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
        if operation[0]=='kindred':
            operations=tuple(operation[1])*context.get('kindred_repeats',1) if context.get('kindred') else ()
            if not operations:return ('batch30_noop',),()
            first,tail=self._split_fixed_summon(operations[0],context)
            return first,tuple(tail)+tuple(operations[1:])
        if operation[0] in ('kindred_destroy_attack','kindred_discard') and context.get('kindred') and context.get('kindred_repeats',1)>1:
            return operation,(('replay_context',(operation,),dict(context,kindred_repeats=1)),)
        if operation[0]=='kindred_cost_draws':
            return ('kindred_cost_draw_one',1),tuple(('kindred_cost_draw_one',cost) for cost in range(2,5))
        if operation[0]=='outcast_operation':
            if context.get('outcast'):return self._split_fixed_summon(operation[1],context)
            return ('batch30_noop',),()
        if operation[0]=='if_discarded':
            if context.pop('discard_succeeded',False):
                return self._split_fixed_summon(operation[1],context)
            return ('batch30_noop',),()
        if operation[0]=='if_holding':
            selected=(operation[2] if self._holding_matches(context['owner'],operation[1]) else
                      operation[3] if len(operation)>3 else ('batch30_noop',))
            return self._split_fixed_summon(selected,context)
        if operation[0] == 'when_state':
            if self._batch30_state(operation[1], context['owner']):
                return self._split_fixed_summon(operation[2], context)
            return ('batch30_noop',), ()
        if operation[0] == 'damage_then_summon_if_dead':
            # Resume after damage-triggered deaths and choices, not inside them.
            return ('damage', operation[1]), (('summon_after_target_death', operation[2]),)
        if operation[0] == 'fill_board_summon':
            count=max(0,7-len(self.players[context['owner']].board))
            return self._split_fixed_summon(('summon',operation[1],count),context)
        if operation[0] == 'death_summon':
            offset=operation[3] if len(operation)>3 else 0
            if operation[2]>1:
                return ('death_summon',operation[1],1,offset), (('death_summon',operation[1],operation[2]-1,offset+1),)
            return operation, ()
        if operation[0] == 'death_summon_group':
            cards=operation[1]
            offset=operation[2] if len(operation)>2 else 0
            if not cards:
                return operation, ()
            tail=(('death_summon_group',cards[1:],offset+1),) if len(cards)>1 else ()
            return ('death_summon',cards[0],1,offset), tail
        if operation[0] not in ('summon', 'combo_summon'):

            return operation, ()
        if operation[0] == 'combo_summon' and not context.get('combo'):
            return operation, ()
        if operation[2] <= 1:
            return operation, ()
        return ('summon', operation[1], 1), (('summon', operation[1], operation[2]-1),)

    def _take_effect_operation(self, frame, context):
        cursor=frame['operation']
        operation, tail=self._split_fixed_summon(frame['operations'][cursor], context)
        frame['operation']=cursor+1
        if tail:
            frame['operations']=frame['operations'][:cursor+1]+tail+frame['operations'][cursor+1:]
        return operation

    @contextmanager
    def _damage_batch(self):
        """Defer settle requests until all hits/healing in this batch finish.

        The caller owns the next checkpoint. Exiting does not run effects,
        including on exceptions; Game.step owns rollback on failure.
        """
        self._damage_batch_depth += 1
        healing={}
        self._lifesteal_batches.append(healing)
        self._trace_phase("damage_batch_begin", depth=self._damage_batch_depth)
        try:
            yield
        except BaseException:
            # A failed batch must not emit a completed healing effect.
            # Game.step restores damage and all other state on failure.
            raise
        else:
            for owner,amount in healing.items():
                if amount:self._heal(self.hero_id(owner),amount,healer=owner)
        finally:
            self._lifesteal_batches.pop()
            self._trace_phase("damage_batch_end", depth=self._damage_batch_depth)
            self._damage_batch_depth -= 1

    def _effect_lifesteal(self, owner, amount):
        if self._lifesteal_batches:
            batch=self._lifesteal_batches[-1]
            batch[owner]=batch.get(owner,0)+amount
        else:
            self._heal(self.hero_id(owner),amount,healer=owner)

    def _start_play_effects(self, operations, context):
        if self.pending_frame is not None:
            raise UnsupportedCard('Nested card-effect frames are not supported yet')
        self.pending_frame = PlayFrame(tuple(operations), context)
        return self._resume_play_effects()

    def _resume_play_effects(self):
        """Return True on completion, False while waiting for a choice.

        Advance before dispatch so a resumed choice cannot repeat its own
        operation. If dispatch fails, Game.step restores the entire frame,
        choice, RNG and game state together.
        """
        frame = self.pending_frame
        if frame is None:
            return True
        while not self.terminal and self.pending_choice is None:
            if frame.next_operation == len(frame.operations):
                self.pending_frame = None
                return True
            operation = frame.operations[frame.next_operation]
            frame.next_operation += 1
            if operation[0]=='repeat_held_tribe':
                filters=(('tribe','eq',operation[1]),)
                self._validate_filters(filters)
                count=1+sum(self._matches_filter(c,filters) for c in self.players[frame.context['owner']].hand)
                cursor=frame.next_operation
                frame.operations=frame.operations[:cursor]+(operation[2],)*count+frame.operations[cursor:]
                continue
            operation, tail=self._split_fixed_summon(operation, frame.context)
            if tail:
                cursor=frame.next_operation
                frame.operations=frame.operations[:cursor]+tail+frame.operations[cursor:]
            self._trace_phase("operation_begin", operation=operation[0], cursor=frame.next_operation-1)
            self._effect_checkpoint(operation, frame.context)
            self._settle(allow_event_choices=True)
            self._trace_phase("operation_checkpoint", operation=operation[0], cursor=frame.next_operation-1, waiting_choice=self.pending_choice is not None)
        if self.terminal:
            self.pending_frame = None
            self.pending_choice = None
            self.pending_play = None
            self.phase = 'finished'
            return True
        return False
