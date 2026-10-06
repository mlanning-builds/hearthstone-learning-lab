"""Physical card origins, copy ancestry, and hand-entry boundaries.

Private lineage stays off dataclass serialization. Owner-visible predicates are
published deliberately, never opponent deck identities or physical origin IDs.
"""
from copy import deepcopy
from engine.game import Card


class Provenance:
    @staticmethod
    def _remember_crafted(card):
        if hasattr(card, '_crafted_definition'):return
        state=getattr(card,'rule_state',{})
        if not any(k in state for k in ('crafted_ops','crafted_location_ops')):return
        payload={k:deepcopy(v) for k,v in state.items() if k.startswith(('crafted_', 'forge_'))}
        card._crafted_definition=dict(state=payload, cost=getattr(card,'set_cost',None),
            stats=deepcopy(getattr(card,'base_stat_override',None)))

    @staticmethod
    def _restore_crafted(card):
        definition=getattr(card,'_crafted_definition',None)
        if definition is None:return
        card.rule_state=deepcopy(definition['state'])
        if definition['cost'] is not None:card.set_cost=definition['cost']
        if definition['stats'] is not None:card.base_stat_override=deepcopy(definition['stats'])

    def _fresh_replay_card(self, source):
        card=Card(self._new_id(),source.card_id)
        if hasattr(source,'_crafted_definition'):
            card._crafted_definition=deepcopy(source._crafted_definition)
            self._restore_crafted(card)
        return card

    @staticmethod
    def _carry_origin(source, target, *, copied=False, source_owner=None):
        if target is None:
            return
        if getattr(source,'card_id',None)==getattr(target,'card_id',None) and hasattr(source,'_learned_spell'):
            target._learned_spell=source._learned_spell
        if getattr(source,'card_id',None)==getattr(target,'card_id',None) and hasattr(source,'_crafted_definition'):
            target._crafted_definition=deepcopy(source._crafted_definition)
        for key in ('_starting_owner', '_starting_identity', '_copied_from_owner'):
            if hasattr(target, key):delattr(target, key)
        if not copied:
            for key in ('_starting_owner', '_starting_identity'):
                if hasattr(source, key):setattr(target, key, getattr(source, key))
        ancestry = source_owner if copied and source_owner is not None else getattr(source, '_copied_from_owner', None)
        if ancestry is not None:target._copied_from_owner = ancestry

    def _started_in_deck(self, card, owner):
        if not isinstance(card, Card):return False
        data = self._card_data(card)
        identity = data.get('countAsCopyOfDbfId', data.get('dbfId', data['id']))
        return getattr(card, '_starting_owner', None) == owner and getattr(card, '_starting_identity', None) == identity

    @staticmethod
    def _copied_from_opponent(card, owner):
        return getattr(card, '_copied_from_owner', None) == 1-owner

    def _enter_hand(self, owner, card):
        self._quest_deliver_ready(owner)
        if not isinstance(card, Card):card = Card(self._new_id(), card)
        if len(self.players[owner].hand) >= 10:
            self._log('burn_generated', player=owner, card=card.card_id)
            return None
        self._remember_crafted(card)
        if self.players[owner].crystal_core and self._card_data(card)['type']=='MINION':card.base_stat_override=(5,5)
        self._replace_coin(owner,card)
        if card.card_id=='TLC_452':self._osk_roll(card)
        card._hand_entry_turn = self.turn
        self.players[owner].hand.append(card)
        self._quest_hand_state(owner)
        return card

    def _copy_card(self, value, *, source_owner=None):
        card = deepcopy(value) if isinstance(value, Card) else Card(self._new_id(), value)
        card.uid = self._new_id()
        self._carry_origin(value, card, copied=True, source_owner=source_owner)
        if hasattr(card, '_hand_entry_turn'):del card._hand_entry_turn
        return card

    def _origin_played(self, owner, card):
        if not self._started_in_deck(card, owner):
            p = self.players[owner]
            p._nonstarting_plays = getattr(p, '_nonstarting_plays', 0) + 1
        if self._copied_from_opponent(card, owner):
            for held in self.players[owner].hand:
                if held.card_id in ('JAIL_432', 'JAIL_433'):
                    self._b60_state(held)['opponent_copy_played'] = True

    def _mulligan(self, choices):
        p = self.players[self.current]
        returned = [c for c in p.hand if c.uid in choices]
        p.hand = [c for c in p.hand if c.uid not in choices]
        for _ in returned:self._draw(self.current, private=True)
        p.deck.extend(returned);self.rng.shuffle(p.deck)
        self._log('mulligan', player=self.current, count=len(returned))
        self.mulligan_done.add(self.current)
        if len(self.mulligan_done) == 1:
            self.current = 1-self.current
        else:
            self._add(1-self.first_player, 'TOKEN_COIN')
            for player in self.players:player._starting_hand=deepcopy(player.hand)
            self.phase = 'play';self.current = self.first_player
            self._shatter_update()
            self._begin_turn()

    def _origin_split(self, op, ctx):
        if op == ('origin_dreamwarden',):
            state={}
            return ('origin_dreamwarden',state), (('origin_dreamwarden_buff',state),)

    def _origin_effect(self, op, ctx):
        name = op[0]
        if not name.startswith('origin_'):return False
        owner=ctx['owner'];p=self.players[owner];q=self.players[1-owner]
        if name == 'origin_clean_decks':
            for recipient, player in enumerate(self.players):
                removed=[c for c in player.deck if not self._started_in_deck(c, recipient)]
                player.deck[:]=[c for c in player.deck if self._started_in_deck(c, recipient)]
                for c in removed:
                    self._zone_card_removed(recipient,c,'deck','destroy')
                    self._log('destroy_deck_card', player=recipient, card=self._card_data(c)['id'])
            self._refresh_auras()
        elif name == 'origin_draw':
            started, spells_only = op[1:]
            indexes=[i for i,c in enumerate(p.deck) if self._started_in_deck(c,owner)==started
                     and (not spells_only or self._card_data(c)['type']=='SPELL')]
            if indexes:self._draw_index(owner,self.rng.choice(indexes))
        elif name == 'origin_dreamwarden':
            indexes=[i for i,c in enumerate(p.deck) if not self._started_in_deck(c,owner)]
            if indexes:
                self._draw_index(owner,self.rng.choice(indexes))
                op[1]['drawn']=True
        elif name == 'origin_dreamwarden_buff':
            source=ctx.get('source')
            if op[1].get('drawn') and source in p.minions and source.health>0:self._buff(source,2,2)
        elif name == 'origin_discount':
            for c in p.hand:
                eligible = self._copied_from_opponent(c,owner) if op[1]=='opponent_copy' else not self._started_in_deck(c,owner)
                if eligible:c.cost_delta=getattr(c,'cost_delta',0)-1
        elif name == 'origin_sweeper':
            if self._b60_state(ctx['physical_card']).get('opponent_copy_played'):
                self._effect(('area_damage','enemy_minions',2),ctx)
        elif name == 'origin_steal_new_hand':
            selected=[c for c in q.hand if getattr(c,'_hand_entry_turn',None)==self.turn]
            for c in selected:
                q.hand.remove(c);self._enter_hand(owner,c)
            self._refresh_auras()
        else:return False
        return True
