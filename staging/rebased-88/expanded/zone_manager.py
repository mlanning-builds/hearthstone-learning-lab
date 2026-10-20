"""Stateless physical card transitions; zones and scheduler state belong to the game.

Draws, burns, generated admission, recruitment and discards retain separate events.
"""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard


class ZoneManager:
    __slots__ = ()

    def enter_hand(self,game, owner, card, *, creator_uid=None):
        game._quest_deliver_ready(owner)
        if not isinstance(card, Card):card = Card(game._new_id(), card)
        if len(game.players[owner].hand) >= getattr(game.players[owner],'hand_capacity',10):
            from .historical_movements import record
            record(game,'destroyed')
            game._log('burn_generated', player=owner, card=card.card_id)
            return None
        from .historical_pool_weapons import identify
        identify(game,card)
        from .historical_identified_spell_finish import identify as identify_spell
        identify_spell(game,card)
        from .historical_ritual_batches import materialize
        materialize(game,card,owner)
        game._remember_crafted(card)
        if game.players[owner].crystal_core and game._card_data(card)['type']=='MINION':card.base_stat_override=(5,5)
        game._replace_coin(owner,card)
        if card.card_id=='TLC_452':game._osk_roll(card)
        from .historical_starships import transform_terran_card
        transform_terran_card(game,owner,card)
        card._hand_entry_turn = game.turn
        from .historical_transfer_student import normalize_card
        normalize_card(game,card)
        game.players[owner].hand.append(card)
        from .historical_student_spells import upgrade_card
        upgrade_card(game,owner,card)
        from .historical_copy_batches import refresh_fortunes
        refresh_fortunes(game)
        from .historical_copy_batches import mix_concoction
        card=mix_concoction(game,owner,card)
        from .historical_hand_batches import initialize_shifter
        initialize_shifter(game,owner,card)
        from .selectors import has_class
        data=game._card_data(card)
        if not has_class(data,'ROGUE') and not has_class(data,'NEUTRAL'):
            player=game.players[owner];player.historical_nonrogue_hand_additions=getattr(player,'historical_nonrogue_hand_additions',0)+1
        from .historical_galakrond_batches import FORMS,primary
        if card.card_id in FORMS:primary(game,owner)
        game._quest_hand_state(owner)
        # Private event payload: observers receive only their own hand data.
        game._queue_event('historical_hand_entry',owner=owner,card=deepcopy(card),creator_uid=creator_uid)
        return card

    def bounce(self,game, m, cost_delta=0, *, recipient=None):
        if m.dormant:return 
        destination=m.owner if recipient is None else recipient
        p = game.players[destination]
        if len(p.hand) >= getattr(p,'hand_capacity',10):
            # Returning to a full hand destroys the minion; deathrattles still apply.
            m.health = 0
            return
        game.players[m.owner].board.remove(m)
        c = Card(game._new_id(), m.card_id)
        from .base_stats import carry_base_stats
        carry_base_stats(m,c)
        c.cost_delta = cost_delta
        game._carry_origin(m,c)
        game._restore_crafted(c)
        if 'rewinds_remaining' in getattr(m,'rule_state',{}):
            game._b60_state(c)['rewinds_remaining']=m.rule_state['rewinds_remaining']
        game._enter_hand(destination,c)
        game._refresh_auras()
        game._log('return_to_hand', player=destination, entity=m.uid)
        from .generation_extensions import RETURN_EFFECTS
        operations=RETURN_EFFECTS.get(m.card_id,()) if not m.silenced else ()
        if operations:
            game._rule_events.append(('captured_effects',dict(operations=tuple(operations),
                context=dict(owner=destination,source=None,target=0,bonus=0,lifesteal=False)),[]))
        return c

    def draw(self,game, owner, predicate=None, private=False, *, include_burned=False):
        p = game.players[owner]
        if predicate is None:
            index = len(p.deck)-1
        else:
            options = [i for i, c in enumerate(p.deck)
                       if predicate(game._card_data(c))]
            if not options:
                return
            index = game.rng.choice(options)
        from .historical_anomalies import draw_index as anomaly_draw_index
        index=anomaly_draw_index(game,owner,index,private=private,eligible=None if predicate is None else options)
        if index < 0:
            p.fatigue += 1
            game._damage(game.hero_id(owner), p.fatigue,damage_source=None)
            game._log('fatigue', player=owner, damage=p.fatigue)
            return
        return game._take_deck_draw(owner, index, private=private, include_burned=include_burned)

    def shuffle_hand_card(self,game, owner, card, *, actor=None):
        p=game.players[owner]
        if not any(c is card for c in p.hand):raise UnsupportedCard('Shuffle source is not in hand')
        p.hand.remove(card)
        # Zone resets remove temporary enchantments while preserving the
        # physical compiled species/ability definition of constructed cards.
        game._remember_crafted(card)
        clean=game._fresh_replay_card(card);clean.uid=card.uid
        game._carry_origin(card,clean)
        if getattr(card,'rule_state',{}).get('shatter_combined'):
            game._b60_state(clean)['shatter_combined']=True
        p.deck.append(clean)
        game.rng.shuffle(p.deck)
        game._refresh_auras()
        game._record_deck_insertion(owner,owner if actor is None else actor,1,'shuffle',cards=(clean,))
        game._log('shuffle_from_hand',player=owner)
        return clean

    def record_deck_insertion(self,game, destination, actor, count, kind, *, cards, suppress_elekk=False):
        # Public event metadata only: no identities or deck positions.
        if destination not in (0,1) or actor not in (0,1):raise ValueError('Invalid shuffle player')
        if type(count) is not int or count<1:raise ValueError('Shuffle count must be positive')
        if kind not in ('shuffle','trade','bottom','top','swap'):raise ValueError('Unknown deck insertion kind')
        from .historical_demon_portal import discard_insertions
        if discard_insertions(game,destination):return
        cards=tuple(cards)
        if len(cards)!=count or any(not isinstance(card,Card) for card in cards):
            raise ValueError('Deck insertion requires the exact physical card payload')
        game.players[destination].shuffle_history.append(dict(
            turn=game.turn,actor=actor,destination=destination,count=count,kind=kind))
        if kind=='shuffle':
            for card in cards:
                game._queue_event('historical_card_shuffled',owner=actor,destination=destination,
                                  card=deepcopy(card),suppress_elekk=suppress_elekk)
        quest=game.players[destination].quest
        if kind=='shuffle' and actor==destination and quest and quest['card_id']=='TLC_513':
            game._quest_progress(destination,1)

    def discard_cards(self,game, owner, cards):
        """Remove an entire discard batch before exposing any discard event.

        Selection is the caller's responsibility. Snapshot listeners before
        removal; newly summoned listeners cannot observe earlier discards.
        """
        player=game.players[owner];cards=list(cards)
        if len({id(c) for c in cards})!=len(cards) or any(
                not any(c is held for held in player.hand) for c in cards):
            raise ValueError('Discard batch requires distinct cards in the owner hand')
        listeners=game._event_listeners()
        snapshots=[deepcopy(c) for c in cards]
        for card in cards:
            player.hand.remove(card)
            player.discard_history.append(card.card_id)
            if not hasattr(player,'historical_discard_cards'):player.historical_discard_cards=[]
            player.historical_discard_cards.append(deepcopy(card))
            game._log('discard',player=owner,card=card.card_id)
        game._refresh_auras()
        from .generation_extensions import DISCARD_EFFECTS as GENERATION_DISCARDS
        from .historical_hand_batches import DISCARD_EFFECTS as HISTORICAL_DISCARDS
        DISCARD_EFFECTS=dict(GENERATION_DISCARDS,**HISTORICAL_DISCARDS)
        for card in snapshots:
            game._zone_card_removed(owner,card,'hand','discard')
            game._rule_events.append(('discard',dict(owner=owner,card=card),list(listeners)))
            operations=DISCARD_EFFECTS.get(card.card_id,())
            if operations:
                game._rule_events.append(('captured_effects',dict(operations=tuple(operations),
                    context=dict(owner=owner,source=None,physical_card=card,target=0,bonus=0,lifesteal=False)),[]))

    def burn_deck_card(self,game, owner, value):
        """Destruction and Godfrey recovery are separate parts of overdraw."""
        player = game.players[owner]
        cid = game._card_data(value)['id']
        game._log('burn', player=owner, card=cid)
        if player.overdraw_return_active and len(player.overdraw_cache) < 99:
            card = value if isinstance(value, Card) else Card(game._new_id(), cid)
            card.cost_delta = getattr(card, 'cost_delta', 0) - 1
            player.overdraw_cache.append(card)
        game._zone_card_removed(owner, value, 'deck', 'destroy')

    def receive_draw(self,game, owner, value, *, private=False, include_burned=False):
        game._stormwind_draw_depth=getattr(game,"_stormwind_draw_depth",0)+1
        try:
            return self._receive_draw_inner(game,owner,value,private=private,include_burned=include_burned)
        finally:
            game._stormwind_draw_depth-=1
            if not game._stormwind_draw_depth:game._quest_deliver_ready(owner)

    def _receive_draw_inner(self,game, owner, value, *, private=False, include_burned=False):
        from .historical_movements import record
        record(game,'drawn')
        from .historical_copy_batches import ashen_draw
        ashen_draw(game,owner)
        game._quest_deliver_ready(owner)
        player = game.players[owner]
        cid = game._card_data(value)['id']
        if not isinstance(value,Card):value=Card(game._new_id(),cid)
        from .historical_copy_batches import aegwynn_draw
        aegwynn_draw(game,owner,value)
        if len(player.hand) >= getattr(player,'hand_capacity',10):
            game._burn_deck_card(owner, value)
            if include_burned:
                return value if isinstance(value, Card) else Card(game._new_id(), cid)
            return None
        if not isinstance(value,Card):value=Card(game._new_id(),cid)
        from .historical_secret_archive import before_receive_draw
        before_receive_draw(game,owner,value,private)
        from .historical_stormwind_questline_finish import before_draw as stormwind_before_draw
        stormwind_before_draw(game,owner,value,private)
        if game._on_draw_receive(owner,value,private):return None
        card = value if isinstance(value, Card) else Card(game._new_id(), cid)
        card._drawn_turn=game.turn
        game._enter_hand(owner,card)
        if player.quest and player.quest['card_id']=='ULD_140':game._quest_progress(owner,1)
        game._refresh_auras()
        from .historical_drawn_batches import received
        received(game,owner,card)
        from .historical_copy_batches import drawn_modifiers
        drawn_modifiers(game,owner,card)
        if not private:
            game._log('draw', player=owner)
            # Snapshot at the zone transition; later discounts/transforms must
            # not retroactively change the identity drawn for these listeners.
            game._queue_event('card_drawn', owner=owner, card=deepcopy(card))
        game._on_draw_post_receive(owner,card)
        return card

    def take_deck_draw(self,game, owner, index, *, private=False, include_burned=False, recipient=None):
        value = game.players[owner].deck.pop(index)
        game._refresh_auras()
        return game._receive_draw(owner if recipient is None else recipient, value,
                                  private=private, include_burned=include_burned)

    def recruit_from_zone(self,game,owner,zone_name,filters,*,position=-1,keyword=None,
                           site="batch_effects._batch_effect:name == 'summon_from_zone'"):
        if zone_name not in ('hand','deck'):raise ValueError('Invalid summon source zone')
        filters=game._validate_filters(filters)
        p=game.players[owner];zone=getattr(p,zone_name)
        choices=[i for i,card in enumerate(zone) if game._card_data(card)['type']=='MINION'
                 and game._matches_filter(card,filters,hand_owner=owner if zone_name=='hand' else None,zone_owner=owner)]
        if not choices or len(p.board)>=7:return None
        card=zone.pop(game.rng.choice(choices))
        summoned=game._summon(owner,game._card_data(card)['id'],position=position,
            attack_bonus=getattr(card,'attack_bonus',0),health_bonus=getattr(card,'health_bonus',0),
            entry_origin='recruit',entry_site=site,entry_zone=zone_name,entry_source=card)
        if summoned is not None and not summoned.dormant and keyword:summoned.keywords.add(keyword)
        game._refresh_auras()
        game._trace_entity('recruit_initialized',summoned,owner=owner,zone=zone_name)
        return summoned

