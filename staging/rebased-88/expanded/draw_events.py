"""Successful draws publish private snapshots to the shared event scheduler.

Burn, fatigue, generation, recruitment, and deck Discover are different zone
transitions. They must not silently publish a successful-draw event.
"""
from copy import deepcopy
from engine.game import Card
from .kindred import KINDRED_IDS, activates_kindred


class DrawEvents:
    def _burn_deck_card(self, owner, value):
        """Destruction and Godfrey recovery are separate parts of overdraw."""
        player = self.players[owner]
        cid = self._card_data(value)['id']
        self._log('burn', player=owner, card=cid)
        if player.overdraw_return_active and len(player.overdraw_cache) < 99:
            card = value if isinstance(value, Card) else Card(self._new_id(), cid)
            card.cost_delta = getattr(card, 'cost_delta', 0) - 1
            player.overdraw_cache.append(card)
        self._zone_card_removed(owner, value, 'deck', 'destroy')

    def _receive_draw(self, owner, value, *, private=False, include_burned=False):
        self._quest_deliver_ready(owner)
        player = self.players[owner]
        cid = self._card_data(value)['id']
        if len(player.hand) >= 10:
            self._burn_deck_card(owner, value)
            if include_burned:
                return value if isinstance(value, Card) else Card(self._new_id(), cid)
            return None
        if self._on_draw_receive(owner,value,private):return None
        card = value if isinstance(value, Card) else Card(self._new_id(), cid)
        self._enter_hand(owner,card)
        self._refresh_auras()
        if not private:
            self._log('draw', player=owner)
            # Snapshot at the zone transition; later discounts/transforms must
            # not retroactively change the identity drawn for these listeners.
            self._queue_event('card_drawn', owner=owner, card=deepcopy(card))
        return card

    def _take_deck_draw(self, owner, index, *, private=False, include_burned=False, recipient=None):
        value = self.players[owner].deck.pop(index)
        self._refresh_auras()
        return self._receive_draw(owner if recipient is None else recipient, value,
                                  private=private, include_burned=include_burned)

    def _draw_split(self, operation, context):
        name = operation[0]
        owner = context['owner']
        if name in ('barnabus_draw','draw_summon_set_stats'):
            state={}
            return ('capture_effect_draw',name,state), (('finish_effect_draw',operation,state),)
        if name == 'draw_kindred_pair':
            state = {}
            return ('draw_kindred_first', state), (('draw_kindred_partner', state),)
        if name == 'draw_until':
            count = max(0, operation[1]-len(self.players[owner].hand))
            return (('draw', 1), (('draw', count-1),)) if count else (('batch30_noop',), ())
        if name == 'draw_bottom' and operation[1] > 1:
            return ('draw_bottom', 1), (('draw_bottom', operation[1]-1),)
        if name == 'draw_distinct_costs':
            state = {'used': set(), 'remaining': operation[1]}
            return ('draw_distinct_step', state), (('draw_distinct_continue', state),)
        if name == 'draw_distinct_continue':
            state = operation[1]
            if state['remaining'] > 0:
                return ('draw_distinct_step', state), (operation,)
            return ('batch30_noop',), ()
        if name in ('draw_if_cheap', 'b60_draw_discount'):
            if name == 'b60_draw_discount' and operation[1] <= 0:
                return ('batch30_noop',), ()
            state = {'remaining': operation[1]}
            return ('draw_conditional_step', name, state), (('draw_conditional_continue', name, state),)
        if name == 'draw_conditional_continue':
            mode, state = operation[1:]
            if mode == 'draw_if_cheap':
                return (('draw', 1), ()) if state.get('repeat') else (('batch30_noop',), ())
            if state['remaining'] > 0:
                return ('draw_conditional_step', mode, state), (operation,)
            return ('batch30_noop',), ()
        if name in ('excess_draw', 'aoe_draw_dead', 'random_minion_damage_draw_kills'):
            state = {}
            return ('prepare_damage_draw', operation, state), (('finish_damage_draw', operation, state),)
        if name == 'finish_damage_draw':
            original, state = operation[1:]
            count = state.get('count', 0)
            if original[0] == 'aoe_draw_dead':
                alive = {m.uid for player in self.players for m in player.minions}
                count = sum(uid not in alive for uid in state.get('victims', ()))
            return (('draw', 1), (('draw', count-1),)) if count else (('batch30_noop',), ())
        if name in ('draw_pick', 'draw_type_keyword', 'opponent_draw_copy', 'draw_minions_mana_buff'):
            captured = []
            recipient = 1-owner if name == 'opponent_draw_copy' else owner
            filters = (('type', 'eq', 'MINION'),) if name == 'draw_minions_mana_buff' else None
            keep_burned = name in ('draw_type_keyword', 'opponent_draw_copy')
            ops = [('capture_draw', recipient, filters, keep_burned, captured, name == 'opponent_draw_copy')] * operation[1]
            ops.append(('finish_draw_group', operation, captured))
            return ops[0], tuple(ops[1:])
        if name in ('draw', 'draw_empty', 'outcast_draw'):
            count = operation[1]
            allowed = (name == 'draw' or
                       name == 'draw_empty' and not self.players[context['owner']].hand or
                       name == 'outcast_draw' and context.get('outcast'))
            if not allowed or count <= 0:
                return ('batch30_noop',), ()
            if count > 1:
                return ('draw', 1), (('draw', count-1),)
        elif name == 'filtered_draw' and operation[2] > 1:
            return (name, operation[1], 1, *operation[3:]), ((name, operation[1], operation[2]-1, *operation[3:]),)
        return None

    def _draw_event_effect(self, op, context):
        name = op[0]; owner = context['owner']; player = self.players[owner]
        if name == 'capture_effect_draw':
            mode,state=op[1:]
            card=(self._draw(owner,lambda d:d['type']=='MINION',include_burned=True)
                  if mode=='draw_summon_set_stats' else
                  self._draw_filtered(owner,(('type','eq','MINION'),)))
            if card is not None:
                state['card']=card
                state['large']=self._card_stat(card,'attack',owner)>=5
        elif name == 'finish_effect_draw':
            original,state=op[1:];card=state.get('card')
            if card is not None:
                if original[0]=='barnabus_draw':
                    if state['large']:
                        card.health_bonus+=5;self._gain_armor(owner,5)
                else:
                    data=self.cards[card.card_id]
                    minion=self._summon(owner,card.card_id,
                        attack_bonus=original[1]-data['attack'],health_bonus=original[2]-data['health'],
                        entry_origin='effect',entry_source=context.get('source'),entry_site='draw_summon_set_stats')
                    if minion is not None:minion.keywords.add(original[3])
        elif name == 'draw_kindred_first':
            indexes = [i for i, c in enumerate(player.deck) if self._card_data(c)['id'] in KINDRED_IDS]
            if indexes:
                index = self.rng.choice(indexes)
                # Remember printed identity even if the first card burns. The
                # second draw must not depend on still finding it in the hand.
                op[1]['identity'] = self._card_data(player.deck[index])['id']
                self._draw_index(owner, index)
        elif name == 'draw_kindred_partner':
            cid = op[1].get('identity')
            if cid is not None:
                indexes = [i for i, c in enumerate(player.deck) if activates_kindred(self.cards[cid], self._card_data(c))]
                if indexes:
                    self._draw_index(owner, self.rng.choice(indexes))
        elif name == 'draw_distinct_step':
            state = op[1]
            choices = [i for i, value in enumerate(player.deck) if self._card_stat(value, 'cost') not in state['used']]
            if choices and state['remaining'] > 0:
                index = self.rng.choice(choices)
                state['used'].add(self._card_stat(player.deck[index], 'cost'))
                state['remaining'] -= 1
                self._draw_index(owner, index)
            else:
                state['remaining'] = 0
        elif name == 'draw_conditional_step':
            mode, state = op[1:]
            card = self._draw(owner, include_burned=mode == 'b60_draw_discount')
            if mode == 'draw_if_cheap':
                state['repeat'] = card is not None and self._cost(card, owner) <= state['remaining']
            elif card is None:
                state['remaining'] = 0
            else:
                cost = self._cost(card, owner)
                card.cost_delta = getattr(card, 'cost_delta', 0)-state['remaining']
                state['remaining'] = max(0, state['remaining']-cost)
        elif name == 'prepare_damage_draw':
            original, state = op[1:]; mode = original[0]
            if mode == 'excess_draw':
                target = context.get('target', 0)
                if target:
                    before = max(0, self._find(target).health)
                    dealt = self._deal_effect(target, original[1], context)
                    state['count'] = max(0, dealt-before)
            else:
                victims = ([m for p in self.players for m in p.minions] if mode == 'aoe_draw_dead'
                           else self.rng.sample(self.players[1-owner].minions, min(len(self.players[1-owner].minions), original[2])))
                state['victims'] = [m.uid for m in victims]
                with self._damage_batch():
                    for minion in victims:
                        self._deal_effect(minion.uid, original[1], context)
                state['count'] = sum(m.health <= 0 for m in victims)
        elif name == 'copy_drawn_set_cost':
            card = deepcopy(context['event']['card'])
            self._set_card_cost(card, op[1])
            self._clone_hand_card(owner, card, source_owner=1-owner)
        elif name == 'capture_draw':
            card = (self._draw_filtered(op[1], op[2]) if op[2] is not None
                    else self._draw(op[1], include_burned=op[3]))
            if card is not None:
                op[4].append(deepcopy(card) if op[5] else card)
        elif name == 'finish_draw_group':
            original, cards = op[1:]; mode = original[0]
            if mode == 'draw_pick':
                options = [dict(card_id=c.card_id, uid=c.uid) for c in cards if c in player.hand]
                if options:
                    self.pending_choice = dict(owner=owner, kind='composed_draw', mode=original[2], amount=original[3], options=options)
                    self.phase = 'choice'
            elif mode == 'opponent_draw_copy':
                for card in cards:
                    self._clone_hand_card(owner, card, source_owner=1-owner)
            elif mode == 'draw_type_keyword':
                source = context.get('source')
                if (len(cards) == original[1] and all(self.cards[c.card_id]['type'] == original[2] for c in cards)
                        and source is not None and source in player.minions and source.health > 0):
                    source.keywords.add(original[3])
            elif mode == 'draw_minions_mana_buff' and player.max_mana >= original[2]:
                for card in cards:
                    if card in player.hand:
                        card.attack_bonus += original[3]; card.health_bonus += original[4]
        else:
            return False
        return True
