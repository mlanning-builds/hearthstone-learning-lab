"""Stateless choice execution; choices and continuation frames stay on the game."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .pools import deck_choice_options
from .discover_offer import capture_offer


class ChoiceResolver:
    __slots__ = ()

    def discover_deck(self,game, owner):
        p = game.players[owner]
        options = deck_choice_options(p.deck, game.cards, 3, game.rng)
        if not options:
            return
        game.pending_choice = dict(owner=owner, kind='draw_from_deck', options=options)
        game.phase = 'choice'

    def record_discover(self,game, owner, offer=None):
        player = game.players[owner]
        player.discoveries_this_turn += 1
        player.discoveries_total += 1
        # Count is public; selected identity and physical destination are not.
        game._log('discover', player=owner)
        if offer is not None:game._queue_event('discover_completed',owner=owner,offer=offer)

    def resolve(self,game, index, *, resume=True):
        """Apply one selection; internal callers may retain the enclosing frame.

        A selection can itself open another choice. Never discard that child or
        resume parent effects ahead of it. Automatic selection policy belongs
        to the caller, separately from applying the selected option.
        """
        choice = game.pending_choice
        if choice['kind']=='rewind':
            game._rewind_choose(index)
            return
        game._trace_phase('choice_selected', choice_kind=choice['kind'], owner=choice['owner'], index=index)
        owner = choice['owner']
        p = game.players[owner]
        selected = choice['options'][index]
        offer = capture_offer(choice,index,getattr(p.equipped_card,'uid',None))
        # The selected choice is consumed before its effect can open a child.
        game.pending_choice = None
        game.phase = 'play'
        game._discovery_result = None
        from .historical_upgrade_batches import resolve_adapt
        from .historical_resurrection_batches import resolve_choice as resolve_resurrection
        from .historical_play_batches import resolve_zone_choice
        from .historical_secret_batches import resolve_choice as resolve_secret_choice
        from .historical_galakrond_batches import resolve_choice as resolve_galakrond
        from .historical_treasure_batches import resolve_choice as resolve_treasure
        from .historical_infuse_batches import resolve_choice as resolve_infuse
        from .historical_copy_batches import resolve_held_spell_choice,resolve_pair_choice
        from .historical_discover_spells import resolve_choice as resolve_deck_spell
        from .historical_offer_spells import resolve_choice as resolve_generated_spell
        from .historical_physical_spells import resolve_choice as resolve_physical_spell
        from .historical_change_spells import resolve_choice as resolve_change_spell
        from .historical_music_spells import resolve_choice as resolve_music_spell
        from .historical_utility_spells import resolve_choice as resolve_utility_spell
        if resolve_utility_spell(game,choice,selected):pass
        elif resolve_music_spell(game,choice,selected):pass
        elif resolve_change_spell(game,choice,selected):pass
        elif resolve_physical_spell(game,choice,selected):pass
        elif resolve_generated_spell(game,choice,selected):pass
        elif resolve_deck_spell(game,choice,selected):pass
        elif resolve_pair_choice(game,choice,selected):pass
        elif resolve_held_spell_choice(game,choice,selected):pass
        elif resolve_infuse(game,choice,selected):pass
        elif resolve_treasure(game,choice,selected):pass
        elif resolve_galakrond(game,choice,selected):pass
        elif resolve_secret_choice(game,choice,selected):pass
        elif resolve_zone_choice(game,choice,selected):pass
        elif resolve_resurrection(game,choice,selected):pass
        elif resolve_adapt(game,choice,selected):pass
        elif game._finish_choice(choice,selected):pass
        elif game._forge_choice(choice,selected):pass
        elif game._craft_choice(choice,selected):pass
        elif game._counterfeit_choice(choice,selected):pass
        elif game._osk_choice(choice,selected):pass
        elif game._remaining_setup_choice(choice,selected):pass
        elif game._investigation_choice(choice,selected):pass
        elif game._tiny_choice(choice,selected):pass
        elif game._genn_choice(choice,selected):pass
        elif game._quest_family_choice(choice,selected):pass
        elif game._fabled_choice(choice,selected):pass
        elif game._evolving_choice(choice,selected):pass
        elif game._herald_choice(choice,selected):pass
        elif game._future_summon_choice(choice,selected):pass
        elif game._map_choice(choice,selected):pass
        elif game._leyline_choice(choice,selected):pass
        elif game._imbue_consumer_choice(choice,selected):pass
        elif game._mutation_choice(choice,selected):pass
        elif game._dark_global_choice(choice,selected):pass
        elif game._entity_choice(choice,selected):pass
        elif game._lasting_choice(choice,selected):pass
        elif game._learned_choice(choice,selected):pass
        elif game._stored_choice(choice,selected):pass
        elif game._dark_choice(choice,selected):pass
        elif game._autocast_choice(choice,selected):pass
        elif game._spell_cast_choice(choice,selected):pass
        elif game._imbue_choice(choice,selected):pass
        elif game._choicegen_choice(choice,selected):pass
        elif game._generation_choice(choice,selected):pass
        elif game._temporary_choice(choice,selected):pass
        elif game._local_choice(choice,selected):pass
        elif game._b60_choice(choice,selected):pass
        elif game._persistent_choice(choice,selected):pass
        elif game._composed_choice(choice,selected):pass
        elif choice['kind']=='hand_discard':
            original=next((c for c in p.hand if c.uid==selected['uid']),None)
            if original is None:raise UnsupportedCard('Selected discard left hand during choice')
            if 'remember_source' in choice:
                source=next((m for m in p.minions if m.uid==choice['remember_source']),None)
                if source is not None:source.remembered_discards.append(original.card_id)
            game._discard_card(owner,original)
        elif choice['kind']=='hand_shuffle':
            original=next((c for c in p.hand if c.uid==selected['uid']),None)
            if original is None:raise UnsupportedCard('Selected hand card left hand during choice')
            game._shuffle_hand_card(owner,original)
        elif choice['kind']=='hand_copy':
            original=next((c for c in p.hand if c.uid==selected['uid']),None)
            if original is None:raise UnsupportedCard('Selected hand card left hand during choice')
            if len(p.hand)<getattr(p,'hand_capacity',10):
                game._clone_hand_card(owner,original)
                game._refresh_auras()
        elif choice['kind']=='hand_transform':
            position=next((i for i,c in enumerate(p.hand) if c.uid==selected['uid']),None)
            if position is None:raise UnsupportedCard('Selected hand card left hand during choice')
            previous=p.hand[position]
            p.hand[position]=Card(game._new_id(),choice['replacement'])
            p.hand[position]._hand_entry_turn=getattr(previous,'_hand_entry_turn',game.turn)
            game._refresh_auras()
        elif choice['kind']=='self_effect':
            source=next((m for m in p.minions if m.uid==choice['source_uid']),None)
            if source is not None:game._effect(selected['operation'],dict(owner=owner,source=source,target=0,bonus=0,lifesteal=False,automatic_choices=choice.get('_automatic',False)))
        elif choice['kind']=='fixed_summon':
            game._summon(owner,selected['card_id'], entry_origin='choice', entry_site='systems._resolve_choice')
        elif choice['kind']=='historical_jaxon_draw':
            uid=selected.get('physical_uid')
            if uid is not None:
                index=next((i for i,c in enumerate(p.deck) if getattr(c,'uid',None)==uid),None)
            else:
                index=selected['index']
                if index>=len(p.deck) or getattr(p.deck[index],'card_id',p.deck[index])!=selected['card_id']:index=None
            if index is not None:
                game._discovery_result=game._take_deck_draw(owner,index)
        elif choice['kind']=='draw_from_deck':
            value = p.deck.pop(selected['index'])
            cid = value.card_id if isinstance(value, Card) else value
            if len(p.hand) < getattr(p,'hand_capacity',10):
                game._discovery_result=game._enter_hand(owner,value if isinstance(value,Card) else Card(game._new_id(),cid))
            else:
                game._burn_deck_card(owner,value)
        else:raise UnsupportedCard('Unknown choice kind: '+choice['kind'])
        if game._is_discover_choice(choice):
            game._record_discover(owner,offer)
            game._defer_discover_followups(owner,game._discovery_result)
        del game._discovery_result
        if game.pending_choice is choice:
            game.pending_choice = None
        game.phase = 'choice' if game.pending_choice is not None else 'play'
        if not resume or game.pending_choice is not None:
            return
        # Resume suspended child triggers before the parent card sequence.
        game._settle(allow_event_choices=True)
        if game.pending_choice is not None or game.terminal:
            return
        game._resume_turn()
        if game.pending_choice is not None or game.terminal:
            return
        # A second choice may suspend the same card again. Keep its final
        # callback until all remaining operations have finished.
        if not game._resume_play_effects():
            return
        if not game._resume_power_sequence():
            return
        if game._minion_after_play_frame is not None:
            game._resume_minion_after_play()
            if game.pending_choice is not None or game.terminal:
                return
        context = game.pending_play
        game.pending_play = None
        if context and not game.terminal:
            game._after_play(context)

