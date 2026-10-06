"""Closed-pool generation primitives; production declarations remain gated.

No automatic pool construction and no substitution of supported outcomes. The
caller must install complete reviewed GenerationPool contracts, keyed by request
and current hero class. The default is rejection before RNG or state mutation.
"""
from copy import deepcopy
from engine.cards import UnsupportedCard
from engine.game import Card
from .pools import GenerationPool
from .selectors import has_tribe, has_school, classes, HERO_CLASSES, effective_tribes
from .generation_cards import requests_for, pool


def request_matches(request, data, hero_class):
    # Frozen Constructed Fabled roots are excluded from generated-card pools.
    # Deck/hand selection and explicit copies do not use this predicate.
    from .fabled_decks import BUNDLES
    if data.get("id") in BUNDLES:return False
    if request.excluded_mechanic and request.excluded_mechanic in data.get('mechanics',()):return False
    if request.rune and data.get('runeCost',{}).get(request.rune,0)<=0:return False
    if request.family:
        from .generation_families import FAMILIES
        if data.get('id') not in FAMILIES[request.family]:return False
    if request.card_type and data.get('type') != request.card_type:
        return False
    if request.tribe and not has_tribe(data, request.tribe):
        return False
    if request.school and not has_school(data, request.school):
        return False
    if len(effective_tribes(data)) < request.minimum_tribes:
        return False
    if request.attack_minimum is not None or request.attack_maximum is not None:
        attack=data.get('attack')
        if type(attack) is not int:return False
        if request.attack_minimum is not None and attack<request.attack_minimum:return False
        if request.attack_maximum is not None and attack>request.attack_maximum:return False
    cost = data.get('cost')
    if cost is None or cost < request.minimum:
        return False
    if request.maximum is not None and cost > request.maximum:
        return False
    if request.rarity and data.get('rarity') != request.rarity:
        return False
    if request.mechanic=='WILD_GOD':
        from .imbue_consumers import WILD_GODS
        if data.get('id') not in WILD_GODS:return False
    elif request.mechanic=='REWIND':
        from .rewind_generators import REWIND_CARD_IDS
        if data.get('id') not in REWIND_CARD_IDS:return False
    elif request.mechanic and request.mechanic not in data.get('mechanics', ()):
        return False
    values = classes(data)
    if request.classes == 'own' and hero_class not in values:
        return False
    if request.classes == 'own_or_neutral' and not ({hero_class, 'NEUTRAL'} & values):
        return False
    if request.classes == 'other' and (hero_class in values or not (values & HERO_CLASSES)):
        return False
    if request.classes not in ('any', 'own', 'own_or_neutral', 'other') and request.classes not in values:
        return False
    return True


class GenerationEffects:
    def _generation_candidates(self, request, owner):
        hero_class = self.players[owner].hero_class
        contract = getattr(self, '_generation_pools', {}).get((request, hero_class))
        if contract is None:
            from .generation_families import reviewed_contract
            contract=reviewed_contract(request,hero_class)
        if not isinstance(contract, GenerationPool):
            raise UnsupportedCard('Generation pool has no reviewed membership contract: ' + str(request))
        candidates = contract.resolve(self.cards, self.cards)
        if request.era=='past':
            from .historical_generation import validate_past_candidates
            validate_past_candidates(candidates,self.cards)
        # Do not silently filter an invalid reviewed contract either.
        canonical = [self.cards[cid].get('countAsCopyOfDbfId', self.cards[cid].get('dbfId', cid)) for cid in candidates]
        if len(canonical) != len(set(canonical)):
            raise UnsupportedCard('Generation contract contains duplicate canonical identities')
        invalid = [cid for cid in candidates if not request_matches(request, self.cards[cid], hero_class)]
        if invalid:
            raise UnsupportedCard('Generation contract contains ineligible identities: ' + ', '.join(invalid))
        return candidates

    def _generation_discover_candidates(self,request,ctx):
        values=self._generation_candidates(request,ctx['owner'])
        source=ctx.get('card_id')
        def canonical(cid):
            d=self.cards[cid]
            return d.get('countAsCopyOfDbfId',d.get('dbfId',cid))
        return tuple(cid for cid in values if source not in self.cards or canonical(cid)!=canonical(source))

    def _generation_preflight(self, card_id, owner):
        # Includes later death/end/attached effects. Called BEFORE paying/playing
        # by a future reviewed registration, never a permissive support fallback.
        from .generation_extensions import requests_for as extension_requests
        for request in sorted(requests_for(card_id) | extension_requests(card_id), key=repr):
            self._generation_candidates(request, owner)

    def _generation_split(self, op, ctx):
        name = op[0]
        owner = ctx['owner']
        if name=='generation_fill_board':
            count=max(0,7-len(self.players[owner].board))
            return self._generation_split(('generate_random',op[1],count,'board',()),ctx)
        if name=='generation_hero_attack_summons':
            cost=op[1]+self.players[owner].hero_attacks_total
            request=pool(card_type='MINION',minimum=cost,maximum=cost)
            return self._generation_split(('generate_random',request,op[2],'board',()),ctx)
        if name=='generation_fill_health_hand':
            count=max(0,10-len(self.players[owner].hand))
            return self._generation_split(('generate_random',op[1],count,'hand',(('health_payment','turn'),)),ctx)
        if name == 'generation_fill_plain_hand':
            count=max(0,10-len(self.players[owner].hand))
            return self._generation_split(('generate_random',op[1],count,'hand',()),ctx)
        if name == 'generation_fill_hand':
            # Snapshot free slots and held progress once. Child effects cannot
            # turn a fill-hand operation into an unbounded refill loop.
            count=max(0,10-len(self.players[owner].hand))
            physical=ctx.get('physical_card')
            ready=(getattr(physical,'rule_state',{}).get('held_mana_spent',0)>=op[2])
            modifiers=(('set_cost',1),) if ready else ()
            return self._generation_split(('generate_random',op[1],count,'hand',modifiers),ctx)
        if name == 'generation_dynamic_summon':
            player=self.players[owner];mode=op[1]
            if mode=='hand_size':cost=len(player.hand)
            elif mode=='remaining_mana':cost=player.mana
            elif mode=='corpses_up_to':cost=min(op[2],player.corpses)
            elif mode=='death_source_cost':
                source=ctx.get('source')
                if source is None:raise UnsupportedCard('Missing death source for generation')
                cost=self.cards[source.card_id]['cost']
            else:raise UnsupportedCard('Unknown dynamic generation selector: '+mode)
            request=pool(card_type='MINION',minimum=cost,maximum=cost)
            self._generation_candidates(request,owner)
            return ('generation_pay_resource',mode,cost),(('generate_one',request,'board',()),)
        if name == 'generation_repeat_deaths':
            count=self.players[owner].death_history.count(op[1])
            return self._generation_split(('generate_random',op[2],count,'board',()),ctx)
        if name == 'generation_if_corpses':
            if self.players[owner].corpses<op[1]:return ('batch30_noop',),()
            # Validate the nested generation before spending its resource.
            self._generation_candidates(op[2],owner)
            return ('generation_pay_resource','corpses_up_to',op[1]),(('generate_one',op[2],'board',()),)
        if name == 'generation_if_outcast':
            return self._split_fixed_summon(op[1],ctx) if ctx.get('outcast') else (('batch30_noop',),())
        if name == 'generation_damage_branch':
            uid=ctx.get('target',0)
            if not any(m.uid==uid and m.health>0 for player in self.players for m in player.minions):
                return ('batch30_noop',),()
            return ('damage',op[1]),(('generation_after_damage',uid,op[2]),)
        if name == 'generation_summon_attack':
            request,count=op[1:]
            if type(count) is not int or count<0:raise ValueError('Invalid generation summon count')
            self._generation_candidates(request,owner)
            if count==0:return ('batch30_noop',),()
            state={'summoned':[],'mode':'random_enemy_character'}
            operations=[('generation_capture_summon',request,state)]*count
            operations.append(('force_group_attacks',state))
            return operations[0],tuple(operations[1:])
        if name == 'generate_random':
            count = op[2]
            if type(count) is not int or count < 0:
                raise ValueError('Generation count must be a nonnegative integer')
            # Full closure validation precedes even a zero request.
            candidates = self._generation_candidates(op[1], owner)
            if count == 0 or not candidates:
                return ('batch30_noop',), ()
            if op[3] == 'deck':
                state = {'inserted': 0}
                operations = [('generation_deck_one', op[1], op[4], state)] * count + [('generation_record_shuffle', state)]
                return operations[0], tuple(operations[1:])
            first = ('generate_one', op[1], op[3], op[4])
            tail = (('generate_random', op[1], count-1, op[3], op[4]),) if count > 1 else ()
            return first, tail
        if name == 'generation_if_combo':
            return self._split_fixed_summon(op[1], ctx) if ctx.get('combo') else (('batch30_noop',), ())
        if name == 'generation_if_holding':
            condition = any(has_tribe(self._card_data(c), op[1]) for c in self.players[owner].hand)
            return self._split_fixed_summon(op[2], ctx) if condition else (('batch30_noop',), ())
        if name == 'generation_if_other_tribe':
            condition = any(m is not ctx.get('source') and m.health > 0 and has_tribe(self.cards[m.card_id], op[1]) for m in self.players[owner].minions)
            return self._split_fixed_summon(op[2], ctx) if condition else (('batch30_noop',), ())
        if name == 'generation_mana_branch':
            return self._split_fixed_summon(op[2] if self.players[owner].max_mana >= op[1] else op[3], ctx)
        return None

    def _generation_place(self, cid, destination, modifiers, ctx, *, record_shuffle=True):
        owner = ctx['owner']
        data = self.cards[cid]
        mods = dict(modifiers)
        allowed = {'attack', 'health', 'combo_attack', 'double_stats', 'stats', 'set_cost', 'cost_delta', 'freeze', 'keyword', 'heal_cost', 'shuffle_unchosen', 'temporary', 'trigger_deathrattle', 'combo_cost_delta', 'duration_delta','prepare','follow','repeat_spell','choose_both','locked_until_play','growing_discount','health_payment','dormant_turns'}
        if set(mods) - allowed:
            raise UnsupportedCard('Unknown generation modifiers: ' + ', '.join(sorted(set(mods)-allowed)))
        if 'dormant_turns' in mods and (destination!='board' or type(mods['dormant_turns']) is not int or mods['dormant_turns']<=0):
            raise UnsupportedCard('Dormant generation requires a board destination and positive integer duration')
        if 'health_payment' in mods and mods['health_payment'] not in ('turn','permanent'):
            raise UnsupportedCard('Unknown health-payment duration')
        if destination not in ('hand', 'board', 'deck', 'enemy_top', 'bottom'):
            raise UnsupportedCard('Unknown generation destination: ' + str(destination))
        if destination == 'board' and data['type'] != 'MINION':
            raise UnsupportedCard('Generation board destination requires a minion')
        card = Card(self._new_id(), cid)
        card.attack_bonus = mods.get('attack', 0) + (mods.get('combo_attack', 0) if ctx.get('combo') else 0)
        card.health_bonus = mods.get('health', 0)
        if mods.get('double_stats'):
            card.attack_bonus += data.get('attack', 0)
            card.health_bonus += data.get('health', 0)
        if 'stats' in mods:
            card.attack_bonus = mods['stats'][0] - data.get('attack', 0)
            card.health_bonus = mods['stats'][1] - data.get('health', 0)
        if 'set_cost' in mods:
            card.cost_delta = mods['set_cost'] - data.get('cost', 0)
        else:
            card.cost_delta = mods.get('cost_delta', 0)
        if ctx.get('combo'):card.cost_delta+=mods.get('combo_cost_delta',0)
        if mods.get('duration_delta'):
            self._b60_state(card)['aura_duration_delta']=mods['duration_delta']
        if mods.get('temporary'):
            self._make_temporary(card)
        for key in ('prepare','repeat_spell','choose_both'):
            if mods.get(key):self._b60_state(card)[key]=True
        if mods.get('health_payment'):
            state=self._b60_state(card);state['health_payment']=True
            if mods['health_payment']=='turn':state['health_payment_until']=self.turn
        if mods.get('growing_discount'):
            card.growing_discounts=[dict(owner=owner,amount=mods['growing_discount'])]
        if mods.get('follow'):
            card._follow_effects=[dict(card_id=mods['follow'],end=self.turn)]
        if mods.get('locked_until_play'):
            self._b60_state(card)['locked_until_play']=dict(owner=owner,
                count=len(self.players[owner].played_history)+1+int(ctx.get('physical_card') is not None))
        result = None
        if destination == 'hand':
            result = self._enter_hand(owner, card)
        elif destination == 'board':
            if data['type'] != 'MINION':
                raise UnsupportedCard('Generation board destination requires a minion')
            result = self._summon(owner, cid, attack_bonus=card.attack_bonus,
                                  health_bonus=card.health_bonus, entry_origin='effect',
                                  entry_site='generation', entry_source=ctx.get('source'),
                                  dormant_turns=mods.get('dormant_turns'))
            if result:
                if mods.get('freeze'):
                    self._freeze(result.uid)
                if mods.get('keyword'):
                    result.keywords.add(mods['keyword'])
        elif destination in ('deck', 'enemy_top', 'bottom'):
            recipient = 1-owner if destination == 'enemy_top' else owner
            deck = self.players[recipient].deck
            if destination == 'enemy_top':
                deck.append(card)
            elif destination=='bottom':
                deck.insert(0,card)
            else:
                deck.insert(self.rng.randrange(len(deck)+1), card)
                if record_shuffle:
                    self._record_deck_insertion(recipient, owner, 1, 'shuffle')
            result = card
        else:
            raise UnsupportedCard('Unknown generation destination: ' + str(destination))
        if mods.get('trigger_deathrattle') and destination=='board' and result is not None:
            self._rule_events.append(('captured_effects',dict(
                operations=(('generation_trigger_live_deathrattle',result.uid),),
                context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
        if mods.get('heal_cost'):
            self._heal(self.hero_id(owner), data.get('cost', 0), healer=owner,spell=ctx.get('spell',False))
        return result

    def _generation_effect(self, op, ctx):
        name = op[0]
        if name=='generation_full_heal':
            p=self.players[ctx['owner']]
            self._heal(self.hero_id(ctx['owner']),max(0,p.max_health-p.health),healer=ctx['owner'],spell=ctx.get('spell',False))
        elif name=='generation_skip_turn':
            self.players[ctx['owner']].skipped_turns_pending+=1
        elif name=='generation_refresh_offer':
            if self._check_heroes():return True
            candidates=self._generation_discover_candidates(op[1],ctx)
            ids=self.rng.sample(list(candidates),min(3,len(candidates)))
            if ids:
                if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite pending choice')
                self.pending_choice=dict(owner=ctx['owner'],kind='refresh_discover',
                    request=op[1],context=dict(ctx),options=[dict(card_id=cid) for cid in ids]+
                    [dict(card_id='JAIL_319',label='Refresh options',refresh=True)])
                self.phase='choice'
        elif name=='generation_reopen_attach':
            location=next((x for p in self.players for x in p.locations if x.uid==ctx['target']),None)
            if location is not None:
                self._generation_candidates(op[1],location.owner)
                location.ready_turn=self.turn
                location.attached_death_effects.append(('generate_one',op[1],'board',()))
        elif name == 'generation_trigger_live_deathrattle':
            minion=self._force_live(op[1])
            if minion is not None:
                operations=self._death_operations(minion)
                if operations:
                    self._rule_events.append(('captured_effects',dict(operations=operations,
                        context=dict(owner=minion.owner,source=minion,target=0,bonus=0,lifesteal=False)),[]))
        elif name == 'generation_pay_resource':
            if op[1]=='remaining_mana':
                self.players[ctx['owner']].mana-=op[2]
                self._b60_spend_mana(ctx['owner'],op[2])
                self._refresh_auras()
            elif op[1]=='corpses_up_to':self._spend_corpses(ctx['owner'],op[2])
        elif name == 'generation_attach_other_cost':
            for minion in self.players[ctx['owner']].minions:
                if minion is not ctx.get('source'):
                    minion.attached_death_effects.append(('generation_dynamic_summon','death_source_cost'))
        elif name == 'generation_after_damage':
            target=next((m for player in self.players for m in player.minions if m.uid==op[1] and m.health>0),None)
            if target is not None:self._draw(ctx['owner'])
            elif any(record['entity'].uid==op[1] for player in self.players for record in player.death_records):
                candidates=self._generation_candidates(op[2],ctx['owner'])
                if candidates:self._generation_place(self.rng.choice(candidates),'board',(),ctx)
        elif name == 'generation_capture_summon':
            candidates=self._generation_candidates(op[1],ctx['owner'])
            if candidates:
                minion=self._generation_place(self.rng.choice(candidates),'board',(),ctx)
                if minion:op[2]['summoned'].append(minion.uid)
        elif name == 'generate_one':
            candidates = self._generation_candidates(op[1], ctx['owner'])
            if candidates:
                # Separate random requests sample WITH replacement. Discover
                # instead samples distinct identities below.
                self._generation_place(self.rng.choice(candidates), op[2], op[3], ctx)
        elif name == 'generation_deck_one':
            candidates = self._generation_candidates(op[1], ctx['owner'])
            if candidates:
                self._generation_place(self.rng.choice(candidates), 'deck', op[2], ctx, record_shuffle=False)
                op[3]['inserted'] += 1
        elif name == 'generation_record_shuffle':
            if op[1]['inserted']:
                self._record_deck_insertion(ctx['owner'], ctx['owner'], op[1]['inserted'], 'shuffle')
        elif name in ('generate_discover', 'generation_discover_absorb'):
            candidates = self._generation_discover_candidates(op[1],ctx)
            ids = self.rng.sample(list(candidates), min(3, len(candidates)))
            if ids:
                if self.pending_choice is not None:
                    raise UnsupportedCard('Generation cannot overwrite a pending choice')
                self._generation_choice_context = dict(context=dict(ctx),
                    destination=op[2] if name=='generate_discover' else 'absorb',
                    modifiers=op[3] if name=='generate_discover' else ())
                self.pending_choice = dict(owner=ctx['owner'], kind='generation_discover',
                                           options=[dict(card_id=cid) for cid in ids])
                self.phase = 'choice'
        elif name in ('generation_attach', 'generation_attach_board'):
            targets = list(self.players[ctx['owner']].minions) if name.endswith('_board') else [m for p in self.players for m in p.minions if m.uid == ctx.get('target')]
            for m in targets:
                m.attached_death_effects.append(deepcopy(op[1]))
        elif name == 'generation_discount_school':
            for card in self.players[ctx['owner']].hand:
                if has_school(self._card_data(card), op[1]):
                    card.cost_delta = getattr(card, 'cost_delta', 0) - op[2]
        else:
            return False
        return True

    def _generation_choice(self, choice, selected):
        if choice['kind']=='refresh_discover':
            if selected.get('refresh'):
                # Fixed environmental damage: no spell bonus or Lifesteal.
                if self.rng.randrange(5)==0:self._damage(self.hero_id(choice['owner']),5,damage_source=None)
                self._rule_events.append(('captured_effects',dict(
                    operations=(('generation_refresh_offer',choice['request']),),
                    context=choice['context']),[]))
            else:
                self._discovery_result=self._generation_place(selected['card_id'],'hand',(),choice['context'])
                choice['completed_discover']=True
            return True
        if choice['kind'] != 'generation_discover':
            return False
        state = self._generation_choice_context
        # Delete continuation only after successful placement; step rollback
        # restores it along with RNG and zones on failure.
        if state['destination']=='absorb':
            source=state['context'].get('source')
            live=self._force_live(source.uid) if source is not None else None
            if live is source:
                data=self.cards[selected['card_id']]
                self._buff(live,data.get('attack',0),data.get('health',0))
                live.attached_death_effects.append(('summon',selected['card_id'],1))
            self._discovery_result=None
        else:
            self._discovery_result=self._generation_place(selected['card_id'], state['destination'], state['modifiers'], state['context'])
        if dict(state['modifiers']).get('shuffle_unchosen'):
            count = 0
            for option in choice['options']:
                if option is not selected:
                    self._generation_place(option['card_id'], 'deck', (), state['context'], record_shuffle=False)
                    count += 1
            if count:
                owner = choice['owner']
                self._record_deck_insertion(owner, owner, count, 'shuffle')
        del self._generation_choice_context
        return True
