"""Physical card origins, copy ancestry, and hand-entry boundaries.

Private lineage stays off dataclass serialization. Owner-visible predicates are
published deliberately, never opponent deck identities or physical origin IDs.
"""
from copy import deepcopy
from .identities import canonical_identity,identity_resolver
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
        card=Card(self._new_id(),source if isinstance(source,str) else source.card_id)
        if isinstance(source,str):return card
        # Learned spells belong to generated definitions, not removable buffs.
        if hasattr(source,'_learned_spell'):card._learned_spell=source._learned_spell
        if hasattr(source,'_learned_card'):card._learned_card=deepcopy(source._learned_card)
        if hasattr(source,'_historical_shadow'):card._historical_shadow=deepcopy(source._historical_shadow)
        if hasattr(source,'_historical_guidance_spells'):card._historical_guidance_spells=deepcopy(source._historical_guidance_spells)
        if getattr(source,'_golden',False):card._golden=True
        from .historical_bottle_spells import preserve as preserve_bottle
        preserve_bottle(source,card)
        if card.card_id=='TOY_879t' and hasattr(source,'_historical_resealed_cards'):card._historical_resealed_cards=deepcopy(source._historical_resealed_cards)
        if hasattr(source,'_historical_ship_definition'):
            card._historical_ship_definition=deepcopy(source._historical_ship_definition)
            card.base_stat_override=(card._historical_ship_definition['attack'],card._historical_ship_definition['health'])
        if getattr(source,'_historical_permanent_stats',False):
            card._historical_permanent_stats=True;card.base_stat_override=deepcopy(source.base_stat_override)
        if hasattr(source,'_historical_student_definition'):
            card._historical_student_definition=deepcopy(source._historical_student_definition)
            card.set_cost=card._historical_student_definition['cost']
            card.base_stat_override=(card._historical_student_definition['attack'],card._historical_student_definition['health'])
        if hasattr(source,'_historical_jade_definition'):
            card._historical_jade_definition=deepcopy(source._historical_jade_definition)
            card.base_stat_override=(card._historical_jade_definition['attack'],card._historical_jade_definition['health'])
        if hasattr(source,'_crafted_definition'):
            card._crafted_definition=deepcopy(source._crafted_definition)
            self._restore_crafted(card)
        return card

    @staticmethod
    def _carry_origin(source, target, *, copied=False, source_owner=None):
        if target is None:
            return
        if getattr(source,'card_id',None)==getattr(target,'card_id',None) and hasattr(source,'_suspicious_overlay'):
            target._suspicious_overlay=deepcopy(source._suspicious_overlay)
        if getattr(source,'_golden',False):target._golden=True
        from .historical_copy_lineage import carry
        carry(source, target, copied=copied, source_owner=source_owner)
        if getattr(source,'card_id',None)==getattr(target,'card_id',None) and hasattr(source,'_historical_ship_definition'):
            target._historical_ship_definition=deepcopy(source._historical_ship_definition)
        links=getattr(source,'_historical_kologarn_links',None)
        if hasattr(target,'_historical_kologarn_links'):delattr(target,'_historical_kologarn_links')
        if not copied and getattr(source,'card_id',None)==getattr(target,'card_id',None) and links is not None:
            target._historical_kologarn_links=tuple(links)
        if getattr(source,'card_id',None)==getattr(target,'card_id',None) and hasattr(source,'_brox_chain'):
            target._brox_chain=source._brox_chain
        if getattr(source,'card_id',None)==getattr(target,'card_id',None) and hasattr(source,'_learned_spell'):
            target._learned_spell=source._learned_spell
            if hasattr(source,'_learned_card'):target._learned_card=deepcopy(source._learned_card)
        if getattr(source,'card_id',None)==getattr(target,'card_id',None) and hasattr(source,'_crafted_definition'):
            target._crafted_definition=deepcopy(source._crafted_definition)
        if getattr(source,'card_id',None)=='NX2_033' and getattr(target,'card_id',None)=='NX2_033':
            if not hasattr(target,'rule_state'):target.rule_state={}
            target.rule_state['historical_thaddius_parity']=getattr(source,'rule_state',{}).get('historical_thaddius_parity',1)
        for key in ('_starting_owner', '_starting_identity', '_copied_from_owner'):
            if hasattr(target, key):delattr(target, key)
        if not copied:
            for key in ('_starting_owner', '_starting_identity'):
                if hasattr(source, key):setattr(target, key, getattr(source, key))
        ancestry = source_owner if copied and source_owner is not None else getattr(source, '_copied_from_owner', None)
        if ancestry is not None:target._copied_from_owner = ancestry

    def _started_in_deck(self, card, owner):
        if not hasattr(card,'card_id'):return False
        data = self._card_data(card)
        identity = canonical_identity(data,self.cards)
        from .historical_starships import TERRAN_ORIGINS
        if data['id'] in TERRAN_ORIGINS:identity=canonical_identity(self.cards[TERRAN_ORIGINS[data['id']]],self.cards)
        if data['id'] in ('UNG_027t2','UNG_027t4'):identity=canonical_identity(self.cards['UNG_027'],self.cards)
        from .historical_galakrond_batches import FORMS
        if data['id'] in FORMS:identity=canonical_identity(self.cards[FORMS[data['id']][0]],self.cards)
        from .historical_infuse_batches import INFUSED_ORIGINS
        if data['id'] in INFUSED_ORIGINS:identity=canonical_identity(self.cards[INFUSED_ORIGINS[data['id']]],self.cards)
        return getattr(card, '_starting_owner', None) == owner and getattr(card, '_starting_identity', None) == identity

    @staticmethod
    def _copied_from_opponent(card, owner):
        return getattr(card, '_copied_from_owner', None) == 1-owner

    def _enter_hand(self, owner, card, *, creator_uid=None):
        return self._zone_manager.enter_hand(self,owner=owner,card=card,creator_uid=creator_uid)

    def _copy_card(self, value, *, source_owner=None):
        card = deepcopy(value) if isinstance(value, Card) else Card(self._new_id(), value)
        card.uid = self._new_id()
        # Newly inserted deck cards may carry the source player's effective
        # Crystal Core base without a stored override on the physical card yet.
        if (source_owner in (0,1) and self.players[source_owner].crystal_core
                and self._card_data(value)['type']=='MINION'):
            card.base_stat_override=(5,5)
        self._carry_origin(value, card, copied=True, source_owner=source_owner)
        from .historical_ritual_batches import CTHUN_IDS
        if card.card_id in CTHUN_IDS and source_owner in (0,1):card._historical_ritual_rebase=True
        if hasattr(card, '_hand_entry_turn'):del card._hand_entry_turn
        if hasattr(card, '_drawn_turn'):del card._drawn_turn
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
            from .historical_anomalies import apply_start as apply_anomalies
            apply_anomalies(self)
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
