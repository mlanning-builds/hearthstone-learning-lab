"""Explicit effects over existing zones; no global supported-only card pools."""
from engine.game import Card
from .pools import deck_choice_options
from .selectors import has_tribe


class LocalFamily:
    def _local_split(self, operation, context):
        if operation[0] != 'local_cannon_fire':
            return None
        source = context['source']
        extra = sum(m.card_id == 'CAP_106' and not m.silenced and m.health > 0
                    for m in self.players[source.owner].minions)
        shots = (('local_cannon_shot', source.uid),) * (1 + extra)
        return shots[0], shots[1:]

    def _local_choice(self, choice, selected):
        if choice['kind'] == 'local_enemy_top':
            deck = self.players[1-choice['owner']].deck
            value=deck.pop(selected['index'])
            value=value if isinstance(value,Card) else Card(self._new_id(),value)
            deck.append(value)
            self._discovery_result=value
        elif choice['kind'] == 'local_resurrect':
            self._discovery_result=self._summon(choice['owner'], selected['card_id'],
                         entry_origin='resurrect', entry_site='local_family._local_choice')
        else:
            return False
        return True

    def _local_effect(self, op, ctx):
        name = op[0]
        if name == 'leech_steal_health':
            owner = ctx['owner']; p = self.players[owner]; q = self.players[1-owner]
            candidates = [self.hero_id(1-owner)] + [m.uid for m in q.minions if m.health > 0]
            def health(uid):
                return q.health if uid < 0 else self._find(uid).health
            lowest = min(map(health, candidates))
            target = self.rng.choice([uid for uid in candidates if health(uid) == lowest])
            amount = 1 + sum(m.card_id == 'EDR_810' and not m.silenced and m.health > 0 for m in p.minions)
            victim = q if target < 0 else self._find(target)
            # A stat transfer, not damage or healing: shields, Armor, Immune,
            # Lifesteal, spell damage and healing multipliers do not intervene.
            victim.health -= amount
            victim.max_health -= amount
            p.health += amount
            p.max_health += amount
            p.hero_health_changed_turn = True
            if target < 0:
                q.hero_health_changed_turn = True
            self._log('steal_health', player=owner, source=ctx['source'].uid, target=target, amount=amount)
            return True
        if not name.startswith('local_'):
            return False
        owner = ctx['owner']; p = self.players[owner]; q = self.players[1-owner]
        source = ctx.get('source')
        if name == 'local_enemy_deck_top':
            # Filter real physical indexes before Discover; never a generated pool.
            indexes = [i for i, card in enumerate(q.deck) if self._card_data(card)['type'] == 'MINION']
            options = deck_choice_options([q.deck[i] for i in indexes], self.cards, 3, self.rng)
            for option in options:
                option['index'] = indexes[option['index']]
            if options:
                self.pending_choice = dict(owner=owner, kind='local_enemy_top', options=options)
                self.phase = 'choice'
        elif name == 'local_dead_dragon':
            ids = list(dict.fromkeys(cid for cid in p.death_history if has_tribe(self.cards[cid], 'DRAGON')))
            options = [dict(card_id=cid) for cid in self.rng.sample(ids, min(3, len(ids)))]
            if options:
                self.pending_choice = dict(owner=owner, kind='local_resurrect', options=options)
                self.phase = 'choice'
        elif name == 'local_deck_or_buff':
            if p.deck:
                self._discover_deck(owner)
            else:
                self._buff(source, 4, 4)
        elif name == 'local_enemy_summon':
            self._summon(1-owner, op[1], entry_origin='effect', entry_site='local_family._local_effect')
        elif name == 'local_spell_treant':
            cid = ctx['event']['card_id']
            treant = self._summon(owner, op[1], entry_origin='effect', entry_site='local_family._local_effect')
            if treant is not None:
                treant.attached_death_effects.append(('add', cid, 1))
        elif name == 'local_eat_deck_minion':
            indexes = [i for i, c in enumerate(p.deck) if self._card_data(c)['type'] == 'MINION']
            if indexes:
                card = p.deck.pop(self.rng.choice(indexes))
                self._buff(source, self._card_stat(card, 'attack', owner), self._card_stat(card, 'health', owner))
                # The consumed identity becomes a fresh hand card on death; no
                # deck enchantments or private physical IDs are exposed/copied.
                source.attached_death_effects.append(('add', self._card_data(card)['id'], 1))
        elif name == 'local_fill_enemy_coins':
            for _ in range(10-len(q.hand)):
                self._add(1-owner, op[1])
        elif name == 'local_fire_event':
            self._queue_event('local_cannoneers_fire', owner=owner)
        elif name == 'local_cannon_shot':
            cannon = next((m for m in p.minions if m.uid == op[1]), None)
            if cannon is not None and cannon.health > 0 and not cannon.silenced:
                targets = [self.hero_id(1-owner)] + [m.uid for m in q.minions if m.health > 0]
                self._deal_effect(self.rng.choice(targets), 1, dict(ctx, source=cannon, bonus=0, spell=False))
        else:
            return False
        return True
