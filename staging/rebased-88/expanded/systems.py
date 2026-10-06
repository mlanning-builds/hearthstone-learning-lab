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
from .discover_offer import capture_offer
from .locations import Location
from .permanents import Permanent
from engine.cards import UnsupportedCard
from .cards import (AURAS, CONDITIONAL_ATTACK, TRIGGERS, WEAPON_TRIGGERS,
                    START_EFFECTS, CHOICES)


class Systems:
    def _discount_matches(self,effect,card):
        d=self.cards[card.card_id]; wanted=effect['selector']
        if wanted=='RAFAAM':
            from .rafaam import FAMILY
            return card.card_id in FAMILY
        if wanted=='TEMPORARY':return self._is_temporary(card)
        return (wanted=='ALL' or wanted==d['type'] or
                (wanted in TRIBES and has_tribe(d,wanted)) or
                wanted in d.get('mechanics',[]))

    def _active(self, cid, owner):
        return any(m.card_id == cid and not m.silenced and m.health > 0
                   for m in self.players[owner].minions)

    def _hero_immune(self,owner):
        from .cards import HERO_IMMUNE_AURAS
        return bool(self.players[owner].hero_immune_expiry_players) or any(self._active(cid,owner) for cid in HERO_IMMUNE_AURAS)

    def _effective_keywords(self, minion):
        """Intrinsic/enchantment keywords plus current continuous board rules.

        Derived keywords never enter stored enchantments or copy snapshots.
        Silence removes intrinsic rules, but external auras still apply.
        """
        if minion.dormant:return set()
        keywords=set(minion.keywords)
        if hasattr(minion,'_muradin_hammer'):keywords.update(('WINDFURY','DEATHRATTLE'))
        if minion.card_id=='TIME_619t':
            from .fabled_effects import BOONS
            keywords.update(BOONS[cid] for cid in self.players[minion.owner].bwonsamdi_boons)
        if getattr(minion,'_control_no_attack_until',-1)>=self.turn:keywords.add('CANT_ATTACK')
        if self.players[minion.owner].dragons_have_rush and has_tribe(self.cards[minion.card_id],'DRAGON'):keywords.add('RUSH')
        if minion.attached_death_effects:keywords.add('DEATHRATTLE')
        keywords.update(e['keyword'] for e in minion.temporary_keywords)
        if ('IMMUNE_WHILE_ATTACKING' in keywords and
                any(window['source']==minion.uid for window in getattr(self,'_attack_windows',[]))):
            keywords.add('IMMUNE')
        from .cards import FRIENDLY_KEYWORD_AURAS
        if minion in self.players[minion.owner].minions:
            for cid,keyword in FRIENDLY_KEYWORD_AURAS.items():
                if self._active(cid,minion.owner):keywords.add(keyword)
        if (not minion.silenced and minion.card_id=='CATA_613'
                and not any(m is not minion for m in self.players[minion.owner].minions)):
            keywords.add('IMMUNE')
        if self._active('CATA_898',1-minion.owner):keywords.add('TAUNT')
        # Pinned Migrating Elekk text has intrinsic Taunt but omits its tag.
        if minion.card_id=='MEND_303' and not minion.silenced:keywords.add('TAUNT')
        return keywords

    def _event_listeners(self):
        return [(m, TRIGGERS[m.card_id]) for m in sorted([m for p in self.players for m in p.all_minions],key=lambda m:m.uid)
                     if not m.silenced and m.card_id in TRIGGERS and
                     (not m.dormant or str(TRIGGERS[m.card_id][0]).startswith('dormant_'))]

    def _queue_event(self, kind, **data):
        self._quest_family_event(kind,data)
        self._evolving_event(kind,data)
        self._imbue_consumer_event(kind,data)
        self._b60_event(kind,data)
        listeners=self._event_listeners()
        self._rule_events.append((kind, data, listeners))
        self._autocast_event(kind,data)
        self._obligation_event(kind,data)
        self._trace_phase("event_queued", event_kind=kind, listener_uids=[m.uid for m,_ in listeners])

    def _gain_armor(self,owner,amount):
        if amount<=0:return 0
        self.players[owner].armor+=amount
        self._log('armor',player=owner,amount=amount)
        self._queue_event('armor_gained',owner=owner,amount=amount)
        return amount

    def _trigger_matches(self, wanted, kind, data, m):
        if wanted=='after_owner_card_played':
            return (kind in ('minion_played','spell_cast','dormant_other_card_played')
                    and data['owner']==m.owner and data.get('source')!=m.uid
                    and m.health>0 and not m.dormant)
        if wanted=='friendly_armor_gained':
            return kind=='armor_gained' and data['owner']==m.owner and m.health>0
        dormant_match=self._dormant_trigger_matches(wanted,kind,data,m)
        if dormant_match is not None:return dormant_match
        if m.dormant:return False
        if wanted in ('friendly_card_drawn', 'enemy_card_drawn'):
            return kind == 'card_drawn' and m.health > 0 and (data['owner'] == m.owner) == (wanted == 'friendly_card_drawn')
        if wanted == 'other_friendly_minion_played':
            return kind == 'minion_played' and data['owner'] == m.owner and data['source'] != m.uid and m.health > 0
        if wanted == 'local_cannoneers_fire':
            return kind == wanted and data['owner'] == m.owner and m.health > 0
        if isinstance(wanted,str):
            result=self._b60_trigger_matches(wanted,kind,data,m)
            if result is not None:return result
        if isinstance(wanted,tuple) and wanted[0]=='summon':
            return self._summon_trigger_matches(wanted,kind,data,m)
        if wanted=='self_shield_lost':return kind=='shield_lost' and data['target']==m.uid and m.health>0
        if wanted=='self_survived_damage':
            return kind=='damage' and data['target']==m.uid and m.health>0
        if wanted=='friendly_minion_survived_damage':
            return kind=='damage' and m.health>0 and any(
                target.uid==data['target'] and target.health>0
                for target in self.players[m.owner].minions)
        if isinstance(wanted,tuple) and len(wanted)==2 and wanted[0]=='minion_cost_played':
            return (kind=='minion_played' and data['owner']==m.owner and
                    data.get('cost')==wanted[1] and data.get('source')!=m.uid and m.health>0)
        if isinstance(wanted,tuple) and len(wanted)==2 and wanted[0]=='minion_mechanic_played':
            return kind=='minion_played' and data['owner']==m.owner and wanted[1] in self.cards[data['card_id']].get('mechanics',[])
        if isinstance(wanted,tuple) and len(wanted)==2 and wanted[0]=='spell_school_played':
            return kind=='spell_played' and data['owner']==m.owner and has_school(self.cards[data['card_id']],wanted[1])
        if isinstance(wanted,tuple) and len(wanted)==2 and wanted[0]=='spell_school_cast':
            return kind=='spell_cast' and data['owner']==m.owner and has_school(self.cards[data['card_id']],wanted[1])
        return (
            (wanted=='any_spell_played' and kind=='spell_played') or
            (wanted=='spell_played' and kind=='spell_played' and data['owner']==m.owner) or
            (wanted == 'friendly_shield_lost' and kind == 'shield_lost' and
             data['owner'] == m.owner and m.health>0) or
            (wanted == 'friendly_discard' and kind == 'discard' and data['owner'] == m.owner) or
            (wanted == 'friendly_minion_discard' and kind == 'discard' and data['owner'] == m.owner and self.cards[data['card'].card_id]['type']=='MINION') or
            (wanted == 'friendly_hero_damaged_own_turn' and kind == 'damage' and
             data['target'] == self.hero_id(m.owner) and self.current == m.owner) or
            (wanted == 'damaged_self' and kind == 'damage' and data['target'] == m.uid) or
            (wanted == 'damaged_minion' and kind == 'damage' and data['target'] > 0) or
            (wanted == 'hero_power_used' and kind == 'hero_power_used' and data['owner'] == m.owner) or
            (wanted == 'defended_self' and kind in ('minion_attack','hero_attack') and data['target'] == m.uid) or
            (wanted == 'attacking_self' and kind == 'before_minion_attack' and data['source'] == m.uid) or
            (wanted == 'attacked_self' and kind == 'minion_attack' and data['source'] == m.uid) or
            (wanted == 'friendly_shatter' and kind == 'card_shattered' and data['owner']==m.owner) or
            (wanted == 'hero_attack' and kind == 'hero_attack' and data['owner'] == m.owner) or
            (wanted == 'spell_cast_on_minion' and kind == 'spell_cast' and
             data['owner']==m.owner and data.get('targeted_minion',False)) or
            (wanted == 'spell_cast' and kind == 'spell_cast' and data['owner'] == m.owner) or
            (wanted == 'other_repeated_minion_played' and kind == 'minion_played' and
             data['owner']==m.owner and data['source']!=m.uid and data.get('previously_played',False)) or
            (wanted == 'elemental_played' and kind == 'minion_played' and
             data['owner'] == m.owner and data['source'] != m.uid and
             has_tribe(self.cards[data['card_id']], 'ELEMENTAL')))

    def _event_frame(self, event, allow_choices):
        if event[0]=='captured_effects':
            data=event[1]
            return dict(kind=event[0],data={},listeners=[],listener=0,operations=data['operations'],operation=0,context=data['context'],key=None,allow_choices=True,post_operation=False)
        follow=self._follow_event_frame(event,allow_choices)
        if follow is not None:return follow
        kind, data, listeners = event
        self._trace_phase('event_begin', event_kind=kind, listener_uids=[m.uid for m,_ in listeners])
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
                op = self._take_effect_operation(frame, frame['context'])
                frame['post_operation'] = True
                self._effect_checkpoint(op, frame['context'])
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
            if any(f['key'] == key for f in self._event_frames) and not (
                    (m.card_id=='DINO_400' and wanted=='friendly_armor_gained') or
                    (m.card_id=='EDR_471' and wanted=='damaged_self')):
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

    @staticmethod
    def _set_minion_attack(m,amount):
        m.attack=max(0,amount)
        m.attack_deficit=min(0,amount)

    def _adjust_minion_attack(self,m,amount):
        self._set_minion_attack(m,m.attack+m.attack_deficit+amount)

    def _buff(self,m,attack,health):
        if self._fire_immune_target(m.uid):return
        if m.dormant:return
        self._adjust_minion_attack(m,attack)
        m.health+=health
        m.max_health+=health
        self._colossal_stat_checkpoint()
        self._champion_checkpoint()

    def _refresh_auras(self):
        self._recover_overdraw()
        board = [m for p in self.players for m in p.all_minions]
        desired = {m.uid: [0, 0] for m in board}
        for owner, p in enumerate(self.players):
            for i, source in enumerate(p.board):
                if isinstance(source,(Location,Permanent)) or source.dormant: continue
                if source.health <= 0 or source.silenced:
                    continue
                if source.card_id=='CATA_493':
                    bonus=2*len(p.discard_history)
                    desired[source.uid][0]+=bonus
                    desired[source.uid][1]+=bonus
                aura = AURAS.get(source.card_id)
                if source.card_id in ('CATA_565t','CATA_153t','CATA_153t1'):aura=('adjacent',self._herald_value(source),0)
                if aura:
                    group, attack, health = aura
                    for j, m in enumerate(p.board):
                        if isinstance(m,(Location,Permanent)) or m.dormant: continue
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
                        (condition == 'large_deck' and len(p.deck)>=25) or
                        (condition == 'weapon' and p.weapon is not None)):
                        desired[source.uid][0] += amount
        for m in board:
            if not m.dormant and hasattr(m,'_muradin_hammer'):
                desired[m.uid][0]+=m._muradin_hammer['attack']
                desired[m.uid][1]+=m._muradin_hammer['durability']
            attack, health = desired[m.uid]
            self._adjust_minion_attack(m,attack-m.aura_attack)
            delta = health-m.aura_health
            m.max_health += delta
            if delta > 0 and m.health > 0:
                m.health += delta
            elif delta < 0:
                m.health = min(m.health, m.max_health)
            m.aura_attack, m.aura_health = attack, health
        self._colossal_stat_checkpoint()

    def _damage(self, target, amount, poisonous=False, *, damage_source=..., damage_owner=None, damage_cause=None):
        from .cards import INCOMING_DAMAGE_MODIFIERS
        source=getattr(self,'_damage_origin',None) if damage_source is ... else damage_source
        if damage_owner is None and damage_source is not ... and source is not None:damage_owner=source.owner
        if damage_owner is not None and (type(damage_owner) is not int or damage_owner not in (0,1)):
            raise ValueError('Invalid damage controller')
        if amount<=0:return 0
        if self._replace_plague_damage(target,amount,source):return 0
        if target>0 and self._permanent_entity(target) is not None:return 0
        if target>0 and (self._dormant_entity(target) is not None and self._dormant_entity(target).dormant):return 0
        if target<0 and self._hero_immune(-target-1):return 0
        if target<0 and self.players[-target-1].divine_shield:
            owner=-target-1
            if self._lasting_shield_hit(self.players[owner],owner):return 0
            self.players[owner].divine_shield=False
            self._log('divine_shield_lost',player=owner,target=target)
            self._queue_event('shield_lost',owner=owner,target=target)
            return 0
        if target<0:
            from .cards import HERO_DAMAGE_WEAPON_REPLACEMENTS
            owner=-target-1;weapon=self.players[owner].weapon
            if weapon and HERO_DAMAGE_WEAPON_REPLACEMENTS.get(weapon['card_id'])=='lose_durability':
                weapon['durability']-=1
                self._log('prevent_damage',player=owner,card=weapon['card_id'],amount=amount)
                if weapon['durability']<=0:self._break_weapon(owner)
                return 0
        if target>0:
            minion=self._find(target)
            if 'IMMUNE' in self._effective_keywords(minion):return 0
            modifier=INCOMING_DAMAGE_MODIFIERS.get(minion.card_id)
            if modifier and not minion.silenced:
                multiplier,extra=modifier
                amount=amount*multiplier+extra
        shielded=target>0 and 'DIVINE_SHIELD' in minion.keywords
        if shielded and self._lasting_shield_hit(minion,minion.owner):return 0
        target_owner=-target-1 if target<0 else minion.owner
        before_health=self.players[-target-1].health if target<0 else None
        was_alive=target>0 and minion.health>0
        if target<0 and self._onyxia_active(-target-1):
            owner=-target-1;p=self.players[owner];absorbed=min(p.armor,amount)
            p.armor-=absorbed
            self._replace_hero_health_loss(owner,amount-absorbed)
            dealt=absorbed
            if dealt:self._log('damage',target=target,amount=dealt)
        else:
            dealt = super()._damage(target, amount, poisonous)
        if target<0 and self.players[-target-1].health!=before_health:self.players[-target-1].hero_health_changed_turn=True
        if shielded and 'DIVINE_SHIELD' not in minion.keywords:
            self._queue_event('shield_lost',owner=minion.owner,target=target)
        if dealt:
            if target>0 and was_alive:self._entity_damage(minion,getattr(self,'_damage_origin',None) if damage_source is ... else damage_source,dealt)
            if target<0:
                self.players[-target-1].hero_damage_taken_turn+=dealt
                self.players[-target-1].hero_damage_events_turn+=1
            self._queue_event('damage', target=target, amount=dealt, damage_owner=damage_owner, target_owner=target_owner, source_uid=getattr(source,'uid',None), damage_cause=damage_cause)
            self._zone_damage_trigger(target)
        return dealt

    def _replace_spell_damage(self,target,amount,ctx):
        if target<=0 or amount<=0 or not ctx.get('spell'):return False
        m=next((m for p in self.players for m in p.minions if m.uid==target),None)
        cid=ctx.get('card_id')
        if m is None or m.health<=0 or m.silenced or m.owner!=ctx['owner'] or cid not in self.cards:return False
        if m.card_id=='TIME_217' and has_school(self.cards[cid],'NATURE'):
            from .generation_cards import pool,random_cards
            request=pool(card_type='MINION',minimum=5,maximum=5)
            self._generation_candidates(request,m.owner)
            self._rule_events.append(('captured_effects',dict(operations=(random_cards(request,destination='board'),),
                context=dict(owner=m.owner,source=m,target=0,bonus=0,lifesteal=False)),[]))
            return True
        if m.card_id=='TIME_214' and has_school(self.cards[cid],'NATURE'):
            self._buff(m,2,1)
            self._log('damage_replaced',entity=m.uid,card=m.card_id,spell=cid,amount=amount)
            return True
        return False

    def _freeze_from_damage(self,source,target,dealt):
        from .cards import DAMAGE_FREEZERS
        if dealt>0 and source is not None and not source.silenced and source.card_id in DAMAGE_FREEZERS:
            self._freeze(target)

    def _heal(self,target,amount,*,healer=None,_after_shadow=False,spell=False):
        if self._fire_immune_target(target):return 0
        if target>0 and self._dormant_entity(target) is not None and self._dormant_entity(target).dormant:return 0
        entity=self.players[-target-1] if target<0 else self._find(target)
        if healer is not None and amount>0 and not _after_shadow:
            amount+=self.players[healer].permanent_healing_bonus
            if spell:amount*=self._spell_multiplier(healer)
        if not _after_shadow and self._ruby_heal(target,amount,healer):return 0
        if target<0 and entity.healing_block_expiry_players:return 0
        if not _after_shadow and healer is not None and amount>0 and entity.health>0:
            target_owner=-target-1 if target<0 else entity.owner
            shadows=[m for m in self.players[healer].minions if m.card_id=='TLC_821' and not m.silenced and m.health>0]
            if target_owner!=healer and shadows:
                # Capture healable amount before the forced attacks. A target
                # at full health triggers attacks but receives no later healing.
                capped=max(0,min(amount,entity.max_health-entity.health))
                operations=[('force_shadow_heal_attack',m.uid,target) for m in shadows]
                operations.append(('force_finish_heal',target,capped))
                self._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=dict(owner=healer,source=None,target=target,bonus=0,lifesteal=False)),[]))
                self._settle(allow_event_choices=True)
                return 0
        before=entity.health
        if target<0:
            actual=max(0,min(amount,entity.max_health-entity.health))
            entity.health+=actual
            self._log('heal',target=target,amount=actual)
        else:super()._heal(target,amount)
        restored=max(0,entity.health-before)
        if target<0 and entity.health!=before:
            entity.hero_health_changed_turn=True
            if restored:entity.hero_healed_turn=True
        if healer is not None and restored:
            self.players[healer].healing_done_turn+=restored
            self._colossal_healed(healer,restored)
        return restored

    def _silence(self, m):
        if self._fire_immune_target(m.uid):return
        if m.dormant:return 
        data = self.cards[m.card_id]
        m.silenced = True
        m.remembered_discards.clear()
        m.rule_state.clear()
        for private_field in ('_infinity_cost_receipts','remembered_draw','secret_discard','_bound_card','_bound_minion','_devoured_cards','_fragile_illusion','_illusion_possible'):
            if hasattr(m,private_field):delattr(m,private_field)
        m.attached_death_effects.clear()
        m.temporary_keywords.clear()
        m.imbue_attack_expiries.clear()
        m.keywords.clear()
        m.expires = False
        m.frozen_until = -1
        m.temporary_attack = 0
        # External auras survive recipient silence. Keep their bookkeeping
        # until refresh removes only contributions whose source is now inactive.
        # Resetting it here would reapply health auras and heal damaged minions.
        old_max_health = m.max_health
        from .base_stats import base_stats
        attack,health=base_stats(self,m)
        self._set_minion_attack(m,attack+m.aura_attack)
        m.max_health = health + m.aura_health
        if m.max_health > old_max_health and m.health > 0:
            # Removing a health reduction restores maximum and current health
            # together, preserving damage already taken.
            m.health += m.max_health - old_max_health
        else:
            m.health = min(m.health, m.max_health)
        m._colossal_stat_snapshot=(m.attack,m.max_health)
        self._refresh_auras()
        self._log('silence', entity=m.uid)

    def _transform(self, m, cid):
        if self._fire_immune_target(m.uid):return m
        if m.dormant:return m
        owner = m.owner
        self._colossal_preflight(cid,owner=owner)
        self._herald_entry_preflight(owner,cid)
        position = self.players[owner].board.index(m)
        self.players[owner].board.pop(position)
        new = self._create_minion(owner, cid, position)
        for field in ('_control_return','_control_no_attack_until'):
            if hasattr(m,field):setattr(new,field,deepcopy(getattr(m,field)))
        self._colossal_enter(new)
        # A transformed minion is a fresh, exhausted entity; Charge/Rush are
        # evaluated by normal attack legality. Transformation is not a summon.
        self._refresh_auras()
        self._log('transform', entity=m.uid, replacement=new.uid, card=cid)
        self._trace_entity('replacement_result', new, previous_uid=m.uid)
        return new

    def _bounce(self, m, cost_delta=0):
        if m.dormant:return 
        p = self.players[m.owner]
        if len(p.hand) >= 10:
            # Returning to a full hand destroys the minion; deathrattles still apply.
            m.health = 0
            return
        p.board.remove(m)
        c = Card(self._new_id(), m.card_id)
        from .base_stats import carry_base_stats
        carry_base_stats(m,c)
        c.cost_delta = cost_delta
        self._carry_origin(m,c)
        self._restore_crafted(c)
        if 'rewinds_remaining' in getattr(m,'rule_state',{}):
            self._b60_state(c)['rewinds_remaining']=m.rule_state['rewinds_remaining']
        self._enter_hand(m.owner,c)
        self._refresh_auras()
        self._log('return_to_hand', player=m.owner, entity=m.uid)
        from .generation_extensions import RETURN_EFFECTS
        operations=RETURN_EFFECTS.get(m.card_id,()) if not m.silenced else ()
        if operations:
            self._rule_events.append(('captured_effects',dict(operations=tuple(operations),
                context=dict(owner=m.owner,source=None,target=0,bonus=0,lifesteal=False)),[]))

    def _draw(self, owner, predicate=None, private=False, *, include_burned=False):
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
            self._damage(self.hero_id(owner), p.fatigue,damage_source=None)
            self._log('fatigue', player=owner, damage=p.fatigue)
            return
        return self._take_deck_draw(owner, index, private=private, include_burned=include_burned)

    def _shuffle_hand_card(self, owner, card, *, actor=None):
        p=self.players[owner]
        if not any(c is card for c in p.hand):raise UnsupportedCard('Shuffle source is not in hand')
        p.hand.remove(card)
        clean=Card(card.uid,card.card_id)
        self._carry_origin(card,clean)
        if getattr(card,'rule_state',{}).get('shatter_combined'):
            self._b60_state(clean)['shatter_combined']=True
        p.deck.append(clean)
        self.rng.shuffle(p.deck)
        self._refresh_auras()
        self._record_deck_insertion(owner,owner if actor is None else actor,1,'shuffle')
        self._log('shuffle_from_hand',player=owner)
        return clean

    def _own_shuffle_count(self,owner):
        return sum(entry['kind']=='shuffle' and entry['actor']==owner and entry['destination']==owner
                   for entry in self.players[owner].shuffle_history)

    def _record_deck_insertion(self, destination, actor, count, kind):
        # Public event metadata only: no identities or deck positions.
        if destination not in (0,1) or actor not in (0,1):raise ValueError('Invalid shuffle player')
        if type(count) is not int or count<1:raise ValueError('Shuffle count must be positive')
        if kind not in ('shuffle','trade'):raise ValueError('Unknown deck insertion kind')
        self.players[destination].shuffle_history.append(dict(
            turn=self.turn,actor=actor,destination=destination,count=count,kind=kind))
        quest=self.players[destination].quest
        if kind=='shuffle' and actor==destination and quest and quest['card_id']=='TLC_513':
            self._quest_progress(destination,1)

    def _trade(self, uid):
        p = self.players[self.current]
        c = next(c for c in p.hand if c.uid == uid)
        p.hand.remove(c)
        p.mana -= 1
        self._b60_spend_mana(self.current,1)
        self._draw(self.current)
        # Preserve enchantments and the relative order of the remaining deck.
        p.deck.insert(self.rng.randrange(len(p.deck)+1), c)
        self._refresh_auras()
        self._record_deck_insertion(self.current,self.current,1,'trade')
        self._log('trade', player=self.current, card=c.card_id)

    def _break_weapon(self, owner):
        p = self.players[owner]
        weapon = p.weapon
        if not weapon:
            return
        physical_card = p.equipped_card
        p.weapon = None
        p.equipped_card = None
        self._log('weapon_broken',player=owner,card=weapon['card_id'])
        from .cards import DEATH_EFFECTS
        for op in list(DEATH_EFFECTS.get(weapon['card_id'], []))+weapon.get('attached_death_effects',[]):
            self._effect(op, dict(owner=owner,source=None,target=0,bonus=0,
                                 lifesteal=False,death_position=len(p.board),broken_weapon=weapon,broken_weapon_card=physical_card))

    def _discover_deck(self, owner):
        p = self.players[owner]
        options = deck_choice_options(p.deck, self.cards, 3, self.rng)
        if not options:
            return
        self.pending_choice = dict(owner=owner, kind='draw_from_deck', options=options)
        self.phase = 'choice'

    def _discard_cards(self, owner, cards):
        """Remove an entire discard batch before exposing any discard event.

        Selection is the caller's responsibility. Snapshot listeners before
        removal; newly summoned listeners cannot observe earlier discards.
        """
        player=self.players[owner];cards=list(cards)
        if len({id(c) for c in cards})!=len(cards) or any(
                not any(c is held for held in player.hand) for c in cards):
            raise ValueError('Discard batch requires distinct cards in the owner hand')
        listeners=self._event_listeners()
        snapshots=[deepcopy(c) for c in cards]
        for card in cards:
            player.hand.remove(card)
            player.discard_history.append(card.card_id)
            self._log('discard',player=owner,card=card.card_id)
        self._refresh_auras()
        from .generation_extensions import DISCARD_EFFECTS
        for card in snapshots:
            self._zone_card_removed(owner,card,'hand','discard')
            self._rule_events.append(('discard',dict(owner=owner,card=card),list(listeners)))
            operations=DISCARD_EFFECTS.get(card.card_id,())
            if operations:
                self._rule_events.append(('captured_effects',dict(operations=tuple(operations),
                    context=dict(owner=owner,source=None,physical_card=card,target=0,bonus=0,lifesteal=False)),[]))

    def _discard_card(self, owner, card):
        self._discard_cards(owner,[card])

    def _discard_random(self, owner, count):
        if type(count) is not int or count<0:raise ValueError('Invalid discard count')
        candidates=list(self.players[owner].hand);selected=[]
        for _ in range(min(count,len(candidates))):
            card=self.rng.choice(candidates);candidates.remove(card);selected.append(card)
        self._discard_cards(owner,selected)

    @staticmethod
    def _is_discover_choice(choice):
        # Explicit semantics: a shared choice UI is not proof of Discover.
        # composed "top" is Dredge (TLC_521), not Discover.
        return ((choice['kind']=='refresh_discover' and choice.get('completed_discover',False)) or choice['kind'] in {'dark_global','lasting_deck','draw_from_deck', 'temporary_deck',
                                    'local_enemy_top', 'local_resurrect',
                                    'suspicious_discover','contraband_discover','generation_discover','learned_mentor','evolving_dragon','choicegen_discover','dark_deck','map_discover'} or
                (choice['kind'] == 'composed_zone' and
                 choice.get('mode') in {'copy', 'draw_bottom'}))

    def _record_discover(self, owner, offer=None):
        player = self.players[owner]
        player.discoveries_this_turn += 1
        player.discoveries_total += 1
        # Count is public; selected identity and physical destination are not.
        self._log('discover', player=owner)
        if offer is not None:self._queue_event('discover_completed',owner=owner,offer=offer)

    def _resolve_choice(self, index, *, resume=True):
        """Apply one selection; internal callers may retain the enclosing frame.

        A selection can itself open another choice. Never discard that child or
        resume parent effects ahead of it. Automatic selection policy belongs
        to the caller, separately from applying the selected option.
        """
        choice = self.pending_choice
        if choice['kind']=='rewind':
            self._rewind_choose(index)
            return
        self._trace_phase('choice_selected', choice_kind=choice['kind'], owner=choice['owner'], index=index)
        owner = choice['owner']
        p = self.players[owner]
        selected = choice['options'][index]
        offer = capture_offer(choice,index,getattr(p.equipped_card,'uid',None))
        # The selected choice is consumed before its effect can open a child.
        self.pending_choice = None
        self.phase = 'play'
        self._discovery_result = None
        if self._finish_choice(choice,selected):pass
        elif self._forge_choice(choice,selected):pass
        elif self._craft_choice(choice,selected):pass
        elif self._counterfeit_choice(choice,selected):pass
        elif self._osk_choice(choice,selected):pass
        elif self._remaining_setup_choice(choice,selected):pass
        elif self._investigation_choice(choice,selected):pass
        elif self._tiny_choice(choice,selected):pass
        elif self._genn_choice(choice,selected):pass
        elif self._quest_family_choice(choice,selected):pass
        elif self._fabled_choice(choice,selected):pass
        elif self._evolving_choice(choice,selected):pass
        elif self._herald_choice(choice,selected):pass
        elif self._future_summon_choice(choice,selected):pass
        elif self._map_choice(choice,selected):pass
        elif self._leyline_choice(choice,selected):pass
        elif self._imbue_consumer_choice(choice,selected):pass
        elif self._mutation_choice(choice,selected):pass
        elif self._dark_global_choice(choice,selected):pass
        elif self._entity_choice(choice,selected):pass
        elif self._lasting_choice(choice,selected):pass
        elif self._learned_choice(choice,selected):pass
        elif self._stored_choice(choice,selected):pass
        elif self._dark_choice(choice,selected):pass
        elif self._autocast_choice(choice,selected):pass
        elif self._spell_cast_choice(choice,selected):pass
        elif self._imbue_choice(choice,selected):pass
        elif self._choicegen_choice(choice,selected):pass
        elif self._generation_choice(choice,selected):pass
        elif self._temporary_choice(choice,selected):pass
        elif self._local_choice(choice,selected):pass
        elif self._b60_choice(choice,selected):pass
        elif self._persistent_choice(choice,selected):pass
        elif self._composed_choice(choice,selected):pass
        elif choice['kind']=='hand_discard':
            original=next((c for c in p.hand if c.uid==selected['uid']),None)
            if original is None:raise UnsupportedCard('Selected discard left hand during choice')
            if 'remember_source' in choice:
                source=next((m for m in p.minions if m.uid==choice['remember_source']),None)
                if source is not None:source.remembered_discards.append(original.card_id)
            self._discard_card(owner,original)
        elif choice['kind']=='hand_shuffle':
            original=next((c for c in p.hand if c.uid==selected['uid']),None)
            if original is None:raise UnsupportedCard('Selected hand card left hand during choice')
            self._shuffle_hand_card(owner,original)
        elif choice['kind']=='hand_copy':
            original=next((c for c in p.hand if c.uid==selected['uid']),None)
            if original is None:raise UnsupportedCard('Selected hand card left hand during choice')
            if len(p.hand)<10:
                self._clone_hand_card(owner,original)
                self._refresh_auras()
        elif choice['kind']=='hand_transform':
            position=next((i for i,c in enumerate(p.hand) if c.uid==selected['uid']),None)
            if position is None:raise UnsupportedCard('Selected hand card left hand during choice')
            previous=p.hand[position]
            p.hand[position]=Card(self._new_id(),choice['replacement'])
            p.hand[position]._hand_entry_turn=getattr(previous,'_hand_entry_turn',self.turn)
            self._refresh_auras()
        elif choice['kind']=='self_effect':
            source=next((m for m in p.minions if m.uid==choice['source_uid']),None)
            if source is not None:self._effect(selected['operation'],dict(owner=owner,source=source,target=0,bonus=0,lifesteal=False,automatic_choices=choice.get('_automatic',False)))
        elif choice['kind']=='fixed_summon':
            self._summon(owner,selected['card_id'], entry_origin='choice', entry_site='systems._resolve_choice')
        elif choice['kind']=='draw_from_deck':
            value = p.deck.pop(selected['index'])
            cid = value.card_id if isinstance(value, Card) else value
            if len(p.hand) < 10:
                self._discovery_result=self._enter_hand(owner,value if isinstance(value,Card) else Card(self._new_id(),cid))
            else:
                self._burn_deck_card(owner,value)
        else:raise UnsupportedCard('Unknown choice kind: '+choice['kind'])
        if self._is_discover_choice(choice):
            self._record_discover(owner,offer)
            self._defer_discover_followups(owner,self._discovery_result)
        del self._discovery_result
        if self.pending_choice is choice:
            self.pending_choice = None
        self.phase = 'choice' if self.pending_choice is not None else 'play'
        if not resume or self.pending_choice is not None:
            return
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
        if not self._resume_power_sequence():
            return
        if self._minion_after_play_frame is not None:
            self._resume_minion_after_play()
            if self.pending_choice is not None or self.terminal:
                return
        context = self.pending_play
        self.pending_play = None
        if context and not self.terminal:
            self._after_play(context)

    def _after_play(self, context):
        if self._rewind_offer(context):return
        if self.terminal:
            return
        cid, owner, source, cost, targeted_minion = context
        self._trace_phase('after_play', card_id=cid, owner=owner, source_uid=getattr(source,'uid',None))
        kind = self.cards[cid]['type']
        if kind == 'MINION':
            return self._start_minion_after_play(context)
        if kind == 'SPELL':
            self._secret_event('after_spell',owner)
            self._queue_event('spell_cast', owner=owner,card_id=cid,cost=cost,targeted_minion=targeted_minion,physical_card=source)
        if kind in ('WEAPON','LOCATION','HERO'):
            self._queue_event('dormant_other_card_played',owner=owner,card_id=cid)
        self._secret_event('after_card',owner)
        self._publish_follow(owner,source)
        self._settle(allow_event_choices=True)

    def _system_effect(self, op, ctx):
        """Return False for opcodes handled by the original explicit resolver."""
        owner=ctx['owner']; p=self.players[owner]; q=self.players[1-owner]
        source=ctx.get('source'); target=ctx.get('target',0); name=op[0]
        if name=='next_power_set_cost':
            p.next_power_cost_effects.append(dict(kind='set',amount=op[1]))
        elif name=='opponent_next_power_cost':
            q.next_power_increase+=op[1]
            q.next_power_cost_effects.append(dict(kind='add',amount=op[1]))
        elif name=='opponent_next_turn_cost':
            # Persistent for the entire next opponent turn, never consumed by play.
            start=self.turn+1 if self.current==owner else self.turn+2
            q.timed_cost_increases.append(dict(selector=op[1],amount=op[2],start=start,end=start))
        elif name=='refresh_power':
            p.power_used=False
            if p.secondary_power is not None:p.secondary_power['used']=False
        elif name=='heal_both_heroes':
            self._heal(self.hero_id(owner),op[1],healer=owner,spell=ctx.get('spell',False))
            self._heal(self.hero_id(1-owner),op[1],healer=owner,spell=ctx.get('spell',False))
        elif name=='draw_school':
            self._draw(owner,lambda c:has_school(c,op[1]))
        elif name=='combo_copy_self':
            if ctx.get('combo'):self._system_effect(('copy_self_right',op[1]),ctx)
        elif name=='death_summon_group':
            for offset,cid in enumerate(op[1],start=op[2] if len(op)>2 else 0):
                self._summon(owner,cid,min(ctx['death_position']+offset,len(p.board)), entry_origin='deathrattle', entry_site="systems._system_effect:name == 'death_summon_group'", entry_source=ctx.get('source'))
        elif name=='gain_corpses':
            gained=self._gain_corpses(owner,op[1])
            self._log('gain_corpse',player=owner,amount=gained)
        elif name=='damage_enemy_heal_own':
            # One effect: healing completes before the resolution checkpoint.
            self._damage(self.hero_id(1-owner),op[1],damage_source=source,damage_owner=owner)
            self._heal(self.hero_id(owner),op[2],healer=owner,spell=ctx.get('spell',False))
        elif name=='summon_right':
            for offset in range(op[2]):
                self._summon(owner,op[1],p.board.index(source)+1+offset, entry_origin='effect', entry_site="systems._system_effect:name == 'summon_right'", entry_source=ctx.get('source'))
        elif name=='copy_self_right':
            for _ in range(op[1]):
                self._summon(owner,source.card_id,p.board.index(source)+1,copy_from=source, entry_origin='copy', entry_site="systems._system_effect:name == 'copy_self_right'", entry_source=ctx.get('source'))
        elif name=='corpse_missiles':
            spent=min(op[1],p.corpses);self._spend_corpses(owner,spent)
            for _ in range(spent):
                targets=[self.hero_id(1-owner)]+[m.uid for m in q.minions]
                self._damage(self.rng.choice(targets),op[2],damage_source=source,damage_owner=owner)
                self._settle()
                if self.terminal:break
        elif name=='secret':
            self._place_secret(owner,op[1],ctx.get('physical_card'))
        elif name=='next_cost_set':
            p.cost_effects.append(dict(selector=op[1],set_cost=op[2],expires=self.turn if op[3]=='turn' else None))
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
        elif name=='empty_crystals':
            owners={'friendly':(owner,), 'enemy':(1-owner,), 'both':(owner,1-owner)}[op[1]]
            for recipient in owners:
                player=self.players[recipient]
                player.max_mana=min(player.mana_capacity,player.max_mana+op[2])
        elif name=='match_max_mana':p.max_mana=max(p.max_mana,q.max_mana)
        elif name=='swap_stats':
            if target:
                m=self._find(target);attack,health=m.attack,m.health
                self._set_minion_attack(m,health+m.aura_attack);m.health=m.max_health=attack+m.aura_health
        elif name=='temporary_attack_buff':
            if target:
                m=self._find(target);self._adjust_minion_attack(m,op[1]);m.temporary_attack+=op[1]
        elif name in ('destroy_gain_health','destroy_hurt_hero'):
            if target:
                m=self._find(target);health=m.health;m.health=0
                if name=='destroy_gain_health':self._buff(source,0,health)
                else:self._damage(self.hero_id(owner),health,damage_source=source,damage_owner=owner)
        elif name=='copy_enemy_deck':
            if q.deck:
                value=self.rng.choice(q.deck)
                self._clone_hand_card(owner,value if isinstance(value,Card) else Card(self._new_id(),value),source_owner=1-owner)
        elif name=='pull_enemy_hand':
            choices=[c for c in q.hand if self.cards[c.card_id]['type']=='MINION']
            if choices and len(q.board)<7:
                c=self.rng.choice(choices);q.hand.remove(c)
                self._summon(1-owner,c.card_id,attack_bonus=c.attack_bonus,health_bonus=c.health_bonus, entry_origin='recruit', entry_zone='hand', entry_site="systems._system_effect:name == 'pull_enemy_hand'", entry_source=c)
        elif name=='recruit':
            choices=[i for i,v in enumerate(p.deck) if self.cards[v.card_id if isinstance(v,Card) else v]['type']=='MINION'
                     and self.cards[v.card_id if isinstance(v,Card) else v]['cost']<=op[1]]
            if choices and len(p.board)<7:
                v=p.deck.pop(self.rng.choice(choices))
                self._summon(owner,v.card_id if isinstance(v,Card) else v,
                             attack_bonus=v.attack_bonus if isinstance(v,Card) else 0,
                             health_bonus=v.health_bonus if isinstance(v,Card) else 0, entry_origin='recruit', entry_zone='deck', entry_site="systems._system_effect:name == 'recruit'", entry_source=v)
        elif name=='damage_hero_attack':
            if target:self._deal_effect(target,self._hero_attack(owner),ctx)
        elif name=='combo_buff':
            if target and ctx.get('combo'):self._buff(self._find(target),op[1],op[2])
        elif name=='discover_deck':self._discover_deck(owner)
        elif name=='copy_cast_spell_to_other_player':
            event=ctx['event']
            self._clone_hand_card(1-event['owner'],Card(self._new_id(),event['card_id']),source_owner=event['owner'])
        elif name=='add_opponent':
            for _ in range(op[2]):self._add(1-owner,op[1])
        elif name=='fill_hand':
            while len(p.hand)<10:self._add(owner,op[1])
        elif name=='destroy_self':
            if source and source in p.minions:source.health=0
        elif name in ('buff_event_target','buff_event_source'):
            entity_id=ctx['event']['source' if name=='buff_event_source' else 'target']
            victim=next((m for player in self.players for m in player.minions
                         if m.uid==entity_id and m.health>0),None)
            if victim is not None:self._buff(victim,op[1],op[2])
        elif name=='spend_corpses_damage_summoned':
            victim=next((m for player in self.players for m in player.minions
                         if m.uid==ctx['event']['source'] and m.health>0),None)
            if victim is not None and victim.owner!=owner and p.corpses>=op[1]:
                self._spend_corpses(owner,op[1])
                self._deal_effect(victim.uid,op[2],ctx)
        elif name=='buff_self_turns_taken':
            if source:self._buff(source,op[1]*p.turns_taken,op[2]*p.turns_taken)
        elif name=='buff_self':
            if source:self._buff(source,op[1],op[2])
        elif name=='keyword_self':
            if source:source.keywords.add(op[1])
        elif name=='buff_spell_cost':
            cost=ctx['event']['cost']
            self._buff(source,cost*(op[1] if len(op)>1 else 1),cost*(op[2] if len(op)>2 else 0))
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
                for m in player.minions:
                    if not self._fire_immune_target(m.uid,ctx):m.health=0
        elif name in ('set_others_attack','set_others_health','set_enemies_stats'):
            for player in ([q] if name=='set_enemies_stats' else self.players):
                for m in player.minions:
                    if m is source or self._fire_immune_target(m.uid,ctx):continue
                    if name!='set_others_health':self._set_minion_attack(m,op[1]+m.aura_attack)
                    if name!='set_others_attack':m.health=m.max_health=(op[2] if len(op)>2 else op[1])+m.aura_health
        elif name=='damage_resummon':
            if target:
                m=self._find(target);cid=m.card_id;self._deal_effect(target,op[1],ctx)
                died=m.health<=0;self._settle()
                if died and not self.terminal:self._summon(owner,cid, entry_origin='effect', entry_site="systems._system_effect:name == 'damage_resummon'", entry_source=ctx.get('source'))
        elif name=='missile_hit':
            group=op[1]
            choices=([self.hero_id(1-owner)]+[m.uid for m in q.minions if m.health>0] if group=='enemies' else
                     [m.uid for m in q.minions if m.health>0] if group=='enemy_minions' else
                     [u for u in self._characters() if (source is None or u!=source.uid) and (u<0 or self._find(u).health>0)])
            if choices and not self.terminal:self._deal_effect(self.rng.choice(choices),1,dict(ctx,bonus=0,spell_multiplier_applied=True))
        elif name in ('missiles','attack_missiles'):
            group=op[1] if name=='missiles' else 'enemies'
            shots=(op[2]+ctx.get('bonus',0)) if name=='missiles' else max(0,source.attack)
            if name=='missiles' and ctx.get('spell'):shots*=self._spell_multiplier(owner)
            for _ in range(shots):
                choices=([self.hero_id(1-owner)]+[m.uid for m in q.minions if m.health>0] if group=='enemies' else
                         [m.uid for m in q.minions if m.health>0] if group=='enemy_minions' else
                         [u for u in self._characters() if (source is None or u!=source.uid) and (u<0 or self._find(u).health>0)])
                if not choices or self.terminal:break
                self._deal_effect(self.rng.choice(choices),1,dict(ctx,bonus=0,spell_multiplier_applied=True))
                self._settle()
        elif name=='set_hero_health':
            p.hero_health_changed_turn |= p.health!=op[1]
            p.health=p.max_health=op[1]
        elif name=='random_heal':
            for _ in range(op[1]):
                choices=([self.hero_id(owner)] if p.health<p.max_health else [])+[m.uid for m in p.minions if m.health<m.max_health]
                if not choices:break
                self._heal(self.rng.choice(choices),1,healer=owner,spell=ctx.get('spell',False))
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
        elif name=='damage_buff_if_dead':
            if target:
                victim=self.players[-target-1] if target<0 else self._find(target)
                self._deal_effect(target,op[1],ctx)
                died=victim.health<=0
                self._settle()
                if died and not self.terminal:
                    self._effect(('buff_random_friendly',op[2],op[3]),ctx)
        elif name in ('damage_heal_enemy_if_dead','damage_armor_if_dead'):
            if target:
                m=self._find(target);self._deal_effect(target,op[1],ctx)
                died=m.health<=0;self._settle()
                if died and not self.terminal:
                    if name=='damage_heal_enemy_if_dead':self._heal(self.hero_id(1-owner),op[2],healer=owner,spell=ctx.get('spell',False))
                    else:self._gain_armor(owner,op[2])
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
