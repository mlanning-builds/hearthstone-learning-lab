"""Shared experimental rules. No text parsing, approximate generation, or training.

All effect dispatch is explicit. Events hold listener snapshots, not a scan of
whatever happens to exist when a queued event eventually resolves.
"""
from collections import deque
from copy import deepcopy
from dataclasses import asdict
from engine.game import Card, Action
from .selectors import TRIBES, has_tribe, has_school
from .pools import deck_choice_options
from .locations import Location
from engine.cards import UnsupportedCard
from .cards import (AURAS, CONDITIONAL_ATTACK, TRIGGERS, WEAPON_TRIGGERS,
                    START_EFFECTS, CHOICES)


class Systems:
    def _discount_matches(self,effect,card):
        d=self.cards[card.card_id]; wanted=effect['selector']
        return (wanted==d['type'] or
                (wanted in TRIBES and has_tribe(d,wanted)) or
                wanted in d.get('mechanics',[]))

    def _active(self, cid, owner):
        return any(m.card_id == cid and not m.silenced and m.health > 0
                   for m in self.players[owner].minions)

    def _queue_event(self, kind, **data):
        listeners = [(m, TRIGGERS[m.card_id]) for m in sorted([m for p in self.players for m in p.minions],key=lambda m:m.uid)
                     if not m.silenced and m.card_id in TRIGGERS]
        self._rule_events.append((kind, data, listeners))

    def _trigger_matches(self, wanted, kind, data, m):
        return (
            (wanted == 'damaged_self' and kind == 'damage' and data['target'] == m.uid) or
            (wanted == 'damaged_minion' and kind == 'damage' and data['target'] > 0) or
            (wanted == 'hero_attack' and kind == 'hero_attack' and data['owner'] == m.owner) or
            (wanted == 'spell_cast' and kind == 'spell_cast' and data['owner'] == m.owner) or
            (wanted == 'elemental_played' and kind == 'minion_played' and
             data['owner'] == m.owner and data['source'] != m.uid and
             has_tribe(self.cards[data['card_id']], 'ELEMENTAL')))

    def _event_frame(self, event, allow_choices):
        kind, data, listeners = event
        return dict(kind=kind, data=data, listeners=list(listeners), listener=0,
                    operations=None, operation=0, context=None, key=None,
                    allow_choices=allow_choices, post_operation=False)

    def _advance_event_frame(self, frame):
        # Frames contain plain data and entity references, so Game.step can
        # deep-copy a suspended choice and roll it back without generators.
        if frame['post_operation']:
            frame['post_operation'] = False
            if self._check_heroes():
                return False
        if frame['operations'] is not None:
            if frame['operation'] < len(frame['operations']):
                op = frame['operations'][frame['operation']]
                frame['operation'] += 1
                frame['post_operation'] = True
                self._effect(op, frame['context'])
                if self.pending_choice is not None and not frame['allow_choices']:
                    raise UnsupportedCard('Choices inside this event boundary are not supported')
                return True
            frame['operations'] = None
            frame['key'] = None
            frame['context'] = None
            if self._check_heroes():
                return False
        while frame['listener'] < len(frame['listeners']):
            m, (wanted, operations) = frame['listeners'][frame['listener']]
            frame['listener'] += 1
            if m not in self.players[m.owner].board or m.silenced:
                continue
            if not self._trigger_matches(wanted, frame['kind'], frame['data'], m):
                continue
            key = (m.uid, wanted)
            if any(f['key'] == key for f in self._event_frames):
                raise UnsupportedCard('Re-entrant trigger compensation is not supported')
            frame.update(operations=tuple(operations), operation=0, key=key,
                         context=dict(owner=m.owner,source=m,target=0,bonus=0,
                                      lifesteal=False,event=frame['data']))
            return True
        return False

    def _drain_events(self, allow_choices=False):
        if self._draining_events or self.pending_choice is not None:
            return
        self._draining_events = True
        try:
            while (self._event_frames or self._rule_events) and not self.terminal:
                if not self._event_frames:
                    self._event_frames.append(self._event_frame(
                        self._rule_events.popleft(), allow_choices))
                frame = self._event_frames[-1]
                siblings = self._rule_events
                self._rule_events = deque()
                try:
                    remains = self._advance_event_frame(frame)
                    children = list(self._rule_events)
                finally:
                    self._rule_events = siblings
                if not remains:
                    self._event_frames.pop()
                for child in reversed(children):
                    self._event_frames.append(self._event_frame(child, frame['allow_choices']))
                if self.pending_choice is not None:
                    return
        finally:
            self._draining_events = False
            if self.terminal:
                self._event_frames.clear()
                self._rule_events.clear()
                self.pending_choice = None
                self.pending_frame = None
                self.pending_play = None

    def _refresh_auras(self):
        board = [m for p in self.players for m in p.minions]
        desired = {m.uid: [0, 0] for m in board}
        for owner, p in enumerate(self.players):
            for i, source in enumerate(p.board):
                if isinstance(source,Location): continue
                if source.health <= 0 or source.silenced:
                    continue
                aura = AURAS.get(source.card_id)
                if aura:
                    group, attack, health = aura
                    for j, m in enumerate(p.board):
                        if isinstance(m,Location): continue
                        matches = m is not source and (
                            group == 'others' or
                            (group == 'adjacent' and abs(i-j) == 1) or
                            (group in TRIBES and has_tribe(self.cards[m.card_id],group)))
                        if matches:
                            desired[m.uid][0] += attack
                            desired[m.uid][1] += health
                conditional = CONDITIONAL_ATTACK.get(source.card_id)
                if conditional:
                    condition, amount = conditional
                    if ((condition == 'damaged' and source.health < source.max_health) or
                        (condition == 'enemy_turn' and self.current != owner) or
                        (condition == 'weapon' and p.weapon is not None)):
                        desired[source.uid][0] += amount
        for m in board:
            attack, health = desired[m.uid]
            m.attack += attack-m.aura_attack
            delta = health-m.aura_health
            m.max_health += delta
            if delta > 0 and m.health > 0:
                m.health += delta
            elif delta < 0:
                m.health = min(m.health, m.max_health)
            m.aura_attack, m.aura_health = attack, health

    def _damage(self, target, amount, poisonous=False):
        if target > 0 and 'IMMUNE' in self._find(target).keywords:
            return 0
        dealt = super()._damage(target, amount, poisonous)
        if dealt:
            self._queue_event('damage', target=target, amount=dealt)
        return dealt

    def _silence(self, m):
        data = self.cards[m.card_id]
        m.silenced = True
        m.keywords.clear()
        m.expires = False
        m.frozen_until = -1
        m.temporary_attack = 0
        # External auras survive recipient silence. Keep their bookkeeping
        # until refresh removes only contributions whose source is now inactive.
        # Resetting it here would reapply health auras and heal damaged minions.
        old_max_health = m.max_health
        m.attack = data['attack'] + m.aura_attack
        m.max_health = data['health'] + m.aura_health
        if m.max_health > old_max_health and m.health > 0:
            # Removing a health reduction restores maximum and current health
            # together, preserving damage already taken.
            m.health += m.max_health - old_max_health
        else:
            m.health = min(m.health, m.max_health)
        self._refresh_auras()
        self._log('silence', entity=m.uid)

    def _transform(self, m, cid):
        owner = m.owner
        position = self.players[owner].board.index(m)
        self.players[owner].board.pop(position)
        new = self._create_minion(owner, cid, position)
        # A transformed minion is a fresh, exhausted entity; Charge/Rush are
        # evaluated by normal attack legality. Transformation is not a summon.
        self._refresh_auras()
        self._log('transform', entity=m.uid, replacement=new.uid, card=cid)
        return new

    def _bounce(self, m, cost_delta=0):
        p = self.players[m.owner]
        if len(p.hand) >= 10:
            # Returning to a full hand destroys the minion; deathrattles still apply.
            m.health = 0
            return
        p.board.remove(m)
        c = Card(self._new_id(), m.card_id)
        c.cost_delta = cost_delta
        p.hand.append(c)
        self._refresh_auras()
        self._log('return_to_hand', player=m.owner, entity=m.uid)

    def _draw(self, owner, predicate=None, private=False):
        p = self.players[owner]
        if predicate is None:
            index = len(p.deck)-1
        else:
            options = [i for i, c in enumerate(p.deck)
                       if predicate(self.cards[c.card_id if isinstance(c, Card) else c])]
            if not options:
                return
            index = self.rng.choice(options)
        if index < 0:
            p.fatigue += 1
            self._damage(self.hero_id(owner), p.fatigue)
            self._log('fatigue', player=owner, damage=p.fatigue)
            return
        value = p.deck.pop(index)
        cid = value.card_id if isinstance(value, Card) else value
        if len(p.hand) >= 10:
            self._log('burn', player=owner, card=cid)
            return
        c = value if isinstance(value, Card) else Card(self._new_id(), cid)
        p.hand.append(c)
        if not private:
            self._log('draw', player=owner)
        return c

    def _trade(self, uid):
        p = self.players[self.current]
        c = next(c for c in p.hand if c.uid == uid)
        p.hand.remove(c)
        p.mana -= 1
        self._draw(self.current)
        # Preserve enchantments and the relative order of the remaining deck.
        p.deck.insert(self.rng.randrange(len(p.deck)+1), c)
        self._log('trade', player=self.current, card=c.card_id)

    def _break_weapon(self, owner):
        p = self.players[owner]
        weapon = p.weapon
        if not weapon:
            return
        p.weapon = None
        self._log('weapon_broken',player=owner,card=weapon['card_id'])
        from .cards import DEATH_EFFECTS
        for op in DEATH_EFFECTS.get(weapon['card_id'], []):
            self._effect(op, dict(owner=owner,source=None,target=0,bonus=0,
                                 lifesteal=False,death_position=len(p.board)))

    def _discover_deck(self, owner):
        p = self.players[owner]
        options = deck_choice_options(p.deck, self.cards, 3, self.rng)
        if not options:
            return
        self.pending_choice = dict(owner=owner, kind='draw_from_deck', options=options)
        self.phase = 'choice'

    def _resolve_choice(self, index):
        choice = self.pending_choice
        owner = choice['owner']
        p = self.players[owner]
        selected = choice['options'][index]
        value = p.deck.pop(selected['index'])
        cid = value.card_id if isinstance(value, Card) else value
        if len(p.hand) < 10:
            p.hand.append(value if isinstance(value,Card) else Card(self._new_id(),cid))
        else:
            self._log('burn',player=owner,card=cid)
        self.pending_choice = None
        self.phase = 'play'
        # Resume suspended child triggers before the parent card sequence.
        self._settle(allow_event_choices=True)
        if self.pending_choice is not None or self.terminal:
            return
        self._resume_turn()
        if self.pending_choice is not None or self.terminal:
            return
        # A second choice may suspend the same card again. Keep its final
        # callback until all remaining operations have finished.
        if not self._resume_play_effects():
            return
        context = self.pending_play
        self.pending_play = None
        if context and not self.terminal:
            self._after_play(context)

    def _after_play(self, context):
        if self.terminal:
            return
        cid, owner, source, cost = context
        kind = self.cards[cid]['type']
        if kind == 'SPELL':
            self._secret_event('after_spell',owner)
            self._queue_event('spell_cast', owner=owner,card_id=cid,cost=cost)
        elif kind == 'MINION':
            self._queue_event('minion_played',owner=owner,card_id=cid,
                              source=source.uid if source else 0,cost=cost)
        self._secret_event('after_card',owner)
        self._settle(allow_event_choices=True)

    def _system_effect(self, op, ctx):
        """Return False for opcodes handled by the original explicit resolver."""
        owner=ctx['owner']; p=self.players[owner]; q=self.players[1-owner]
        source=ctx.get('source'); target=ctx.get('target',0); name=op[0]
        if name=='opponent_next_power_cost':
            q.next_power_increase+=op[1]
        elif name=='opponent_next_turn_cost':
            # Persistent for the entire next opponent turn, never consumed by play.
            start=self.turn+1 if self.current==owner else self.turn+2
            q.timed_cost_increases.append(dict(selector=op[1],amount=op[2],start=start,end=start))
        elif name=='refresh_power':
            p.power_used=False
        elif name=='heal_both_heroes':
            self._heal(self.hero_id(owner),op[1])
            self._heal(self.hero_id(1-owner),op[1])
        elif name=='draw_school':
            self._draw(owner,lambda c:has_school(c,op[1]))
        elif name=='combo_copy_self':
            if ctx.get('combo'):self._system_effect(('copy_self_right',op[1]),ctx)
        elif name=='death_summon_group':
            for offset,cid in enumerate(op[1]):
                self._summon(owner,cid,min(ctx['death_position']+offset,len(p.board)))
        elif name=='gain_corpses':
            p.corpses+=op[1]
            self._log('gain_corpse',player=owner,amount=op[1])
        elif name=='damage_enemy_heal_own':
            # One effect: healing completes before the resolution checkpoint.
            self._damage(self.hero_id(1-owner),op[1])
            self._heal(self.hero_id(owner),op[2])
        elif name=='summon_right':
            for offset in range(op[2]):
                self._summon(owner,op[1],p.board.index(source)+1+offset)
        elif name=='copy_self_right':
            data=self.cards[source.card_id]
            for _ in range(op[1]):
                copy=self._summon(owner,source.card_id,p.board.index(source)+1,
                                  source.attack-source.aura_attack-data['attack'],
                                  source.max_health-source.aura_health-data['health'])
                if copy:
                    copy.health=copy.max_health-(source.max_health-source.health)
                    copy.keywords=set(source.keywords)
        elif name=='corpse_missiles':
            spent=min(op[1],p.corpses);p.corpses-=spent
            self._log('spend_corpses',player=owner,amount=spent)
            for _ in range(spent):
                targets=[self.hero_id(1-owner)]+[m.uid for m in q.minions]
                self._damage(self.rng.choice(targets),op[2])
                self._settle()
                if self.terminal:break
        elif name=='secret':
            p.secrets.append(Card(self._new_id(),op[1]))
        elif name=='next_discount':
            p.cost_effects.append(dict(selector=op[1],amount=op[2],expires=self.turn if op[3]=='turn' else None))
        elif name=='draw_discount':
            card=self._draw(owner)
            if card:card.cost_delta=getattr(card,'cost_delta',0)-op[1]
        elif name=='silence':
            if target:self._silence(self._find(target))
        elif name=='transform':
            if target:self._transform(self._find(target),op[1])
        elif name=='bounce_all_enemies':
            for m in list(q.minions):self._bounce(m)
        elif name in ('bounce_random_enemy','bounce_random_friendly'):
            board=q.minions if name=='bounce_random_enemy' else p.minions
            if board:self._bounce(self.rng.choice(board),op[1] if len(op)>1 else 0)
        elif name=='destroy_enemy_weapon':self._break_weapon(1-owner)
        elif name=='equip':self._equip(owner,op[1])
        elif name=='match_max_mana':p.max_mana=max(p.max_mana,q.max_mana)
        elif name=='swap_stats':
            if target:
                m=self._find(target);attack,health=m.attack,m.health
                m.attack=health+m.aura_attack;m.health=m.max_health=attack+m.aura_health
        elif name=='temporary_attack_buff':
            if target:
                m=self._find(target);m.attack+=op[1];m.temporary_attack+=op[1]
        elif name in ('destroy_gain_health','destroy_hurt_hero'):
            if target:
                m=self._find(target);health=m.health;m.health=0
                if name=='destroy_gain_health':self._buff(source,0,health)
                else:self._damage(self.hero_id(owner),health)
        elif name=='copy_enemy_deck':
            if q.deck:
                value=self.rng.choice(q.deck)
                self._add(owner,value.card_id if isinstance(value,Card) else value)
        elif name=='pull_enemy_hand':
            choices=[c for c in q.hand if self.cards[c.card_id]['type']=='MINION']
            if choices and len(q.board)<7:
                c=self.rng.choice(choices);q.hand.remove(c)
                self._summon(1-owner,c.card_id,attack_bonus=c.attack_bonus,health_bonus=c.health_bonus)
        elif name=='recruit':
            choices=[i for i,v in enumerate(p.deck) if self.cards[v.card_id if isinstance(v,Card) else v]['type']=='MINION'
                     and self.cards[v.card_id if isinstance(v,Card) else v]['cost']<=op[1]]
            if choices and len(p.board)<7:
                v=p.deck.pop(self.rng.choice(choices))
                self._summon(owner,v.card_id if isinstance(v,Card) else v,
                             attack_bonus=v.attack_bonus if isinstance(v,Card) else 0,
                             health_bonus=v.health_bonus if isinstance(v,Card) else 0)
        elif name=='damage_hero_attack':
            if target:self._deal_effect(target,self._hero_attack(owner),ctx)
        elif name=='combo_buff':
            if target and ctx.get('combo'):self._buff(self._find(target),op[1],op[2])
        elif name=='discover_deck':self._discover_deck(owner)
        elif name=='add_opponent':
            for _ in range(op[2]):self._add(1-owner,op[1])
        elif name=='fill_hand':
            while len(p.hand)<10:self._add(owner,op[1])
        elif name=='buff_self':
            if source:self._buff(source,op[1],op[2])
        elif name=='keyword_self':
            if source:source.keywords.add(op[1])
        elif name=='buff_spell_cost':self._buff(source,ctx['event']['cost'],0)
        elif name=='buff_random_friendly':
            if p.minions:self._buff(self.rng.choice(p.minions),op[1],op[2])
        elif name=='buff_others':
            for m in p.minions:
                if m is not source:self._buff(m,op[1],op[2])
        elif name=='full_health_buff':
            if source.health==source.max_health:self._buff(source,op[1],op[2])
        elif name=='damage_enemy_hero':self._deal_effect(self.hero_id(1-owner),op[1],ctx)
        elif name=='destroy_all_minions':
            for player in self.players:
                for m in player.minions:m.health=0
        elif name in ('set_others_attack','set_others_health','set_enemies_stats'):
            for player in ([q] if name=='set_enemies_stats' else self.players):
                for m in player.minions:
                    if m is source:continue
                    if name!='set_others_health':m.attack=op[1]+m.aura_attack
                    if name!='set_others_attack':m.health=m.max_health=(op[2] if len(op)>2 else op[1])+m.aura_health
        elif name=='damage_resummon':
            if target:
                m=self._find(target);cid=m.card_id;self._deal_effect(target,op[1],ctx)
                died=m.health<=0;self._settle()
                if died and not self.terminal:self._summon(owner,cid)
        elif name in ('missiles','attack_missiles'):
            group=op[1] if name=='missiles' else 'enemies'
            shots=(op[2]+ctx.get('bonus',0)) if name=='missiles' else max(0,source.attack)
            for _ in range(shots):
                choices=([self.hero_id(1-owner)]+[m.uid for m in q.minions] if group=='enemies' else
                         [m.uid for m in q.minions] if group=='enemy_minions' else
                         [u for u in self._characters() if source is None or u!=source.uid])
                if not choices or self.terminal:break
                self._deal_effect(self.rng.choice(choices),1,dict(ctx,bonus=0))
                self._settle()
        elif name=='random_heal':
            for _ in range(op[1]):
                choices=([self.hero_id(owner)] if p.health<30 else [])+[m.uid for m in p.minions if m.health<m.max_health]
                if not choices:break
                self._heal(self.rng.choice(choices),1)
        elif name=='death_attack_gift':
            if p.minions:self._buff(self.rng.choice(p.minions),source.attack,0)
        elif name=='dragon_held_aoe':
            if any(has_tribe(self.cards[c.card_id],'DRAGON') for c in p.hand):
                self._effect(('area_damage','all_minions',op[1]),ctx)
        elif name=='remove_cheap_decks':
            for player in self.players:
                player.deck[:]=[v for v in player.deck if self.cards[v.card_id if isinstance(v,Card) else v]['cost']>op[1]]
        elif name=='remove_own_top':
            for _ in range(min(op[1],len(p.deck))):p.deck.pop()
        elif name=='unlock_mana':
            if self.current==owner:
                p.mana+=p.locked_mana;p.locked_mana=0
            p.overload_next=0
        elif name in ('damage_heal_enemy_if_dead','damage_armor_if_dead'):
            if target:
                m=self._find(target);self._deal_effect(target,op[1],ctx)
                died=m.health<=0;self._settle()
                if died and not self.terminal:
                    if name=='damage_heal_enemy_if_dead':self._heal(self.hero_id(1-owner),op[2])
                    else:p.armor+=op[2]
        elif name=='descending_aoe':
            for amount in range(op[1],0,-1):
                self._effect(('area_damage','all_minions',amount),ctx);self._settle()
                if self.terminal:break
        elif name=='board_count_aoe':
            self._effect(('area_damage','all_minions',1+sum(len(player.minions) for player in self.players)),ctx)
        elif name=='armor_aoe':
            spent=min(op[1],p.armor);p.armor-=spent
            for _ in range(spent):
                self._effect(('area_damage','all_minions',1),ctx);self._settle()
                if self.terminal:break
        else:return False
        return True
