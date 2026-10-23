"""Shared experimental rules. No text parsing, approximate generation, or training.

All effect dispatch is explicit. Events hold listener snapshots, not a scan of
whatever happens to exist when a queued event eventually resolves.
"""
from collections import deque
from copy import deepcopy
from dataclasses import asdict
from engine.game import Card, Action
from .selectors import TRIBES, SCHOOLS, has_tribe, has_school
from .locations import Location
from .permanents import Permanent
from engine.cards import UnsupportedCard
from .cards import (AURAS, CONDITIONAL_ATTACK, TRIGGERS, WEAPON_TRIGGERS,
                    START_EFFECTS, CHOICES)


class Systems:
    def _discount_matches(self,effect,card):
        d=self._card_data(card); wanted=effect['selector']
        if wanted.startswith('HISTORICAL_PROTOSS_'):
            from .historical_copy_batches import PROTOSS_CARDS,PROTOSS_MINIONS,PROTOSS_SPELLS
            members={'HISTORICAL_PROTOSS_CARD':PROTOSS_CARDS,'HISTORICAL_PROTOSS_MINION':PROTOSS_MINIONS,'HISTORICAL_PROTOSS_SPELL':PROTOSS_SPELLS}
            return card.card_id in members[wanted]
        if wanted=='RAFAAM':
            from .rafaam import FAMILY
            return card.card_id in FAMILY
        if wanted=='HISTORICAL_FOREIGN':
            from .selectors import has_class
            return not has_class(d,self.players[effect['owner']].hero_class) and not has_class(d,'NEUTRAL')
        if wanted=='TEMPORARY':return self._is_temporary(card)
        return (wanted=='ALL' or wanted==d['type'] or
                (wanted in TRIBES and has_tribe(d,wanted)) or
                (wanted in SCHOOLS and has_school(d,wanted)) or
                wanted in d.get('mechanics',[]))

    def _active(self, cid, owner):
        from .forge_intrinsics import values
        property_name={'CATA_898':'enemy_taunt','TIME_617':'suppress_draw'}.get(cid)
        return any(not m.silenced and m.health>0 and
                   (m.card_id==cid or property_name is not None and any(values(m,property_name)))
                   for m in self.players[owner].minions)

    def _hero_stealth(self,owner):
        from .historical_valeera import stealth
        return stealth(self,owner)

    def _hero_immune(self,owner):
        from .cards import HERO_IMMUNE_AURAS
        attacking=any(w['source']==self.hero_id(owner) for w in getattr(self,'_attack_windows',()))
        if attacking and self._active('SCH_538',owner):return True
        if attacking and self.players[owner].weapon and self.players[owner].weapon['card_id']=='DS1_188':return True
        if attacking and self.players[owner].weapon and self.players[owner].weapon['card_id'] in ('ONY_005tb1','VAC_464t14'):return True
        if attacking and self.current==owner and self.players[owner].weapon and 'IMMUNE_WHILE_ATTACKING' in self.players[owner].weapon.get('historical_keywords',()):return True
        if attacking and self.current==owner and self.players[owner].weapon and self.players[owner].weapon.get('historical_paralytic',False):return True
        if getattr(self.players[owner],'historical_lumia_immune_turn',None)==self.turn:return True
        if getattr(self.players[owner],'historical_swing_immune_turn',None)==self.turn:return True
        if getattr(self.players[owner],'historical_ice_block_turn',None)==self.turn:return True
        if getattr(self.players[owner],'historical_evasion_immune_turn',None)==self.turn:return True
        if self.current==owner and (self._active('ETC_081',owner) or self._active('KAR_712',owner)):return True
        return bool(self.players[owner].hero_immune_expiry_players) or any(self._active(cid,owner) for cid in HERO_IMMUNE_AURAS)

    def _effective_keywords(self, minion):
        """Intrinsic/enchantment keywords plus current continuous board rules.

        Derived keywords never enter stored enchantments or copy snapshots.
        Silence removes intrinsic rules, but external auras still apply.
        """
        if minion.dormant:return set()
        keywords=set(minion.keywords)
        from .historical_timed_spells import deputization_layers
        if deputization_layers(self,minion):keywords.add('LIFESTEAL')
        if minion.card_id=='AT_109' and not minion.silenced and minion.rule_state.get('historical_inspire_attack_turn')==self.turn:
            keywords.discard('CANT_ATTACK')
        from .historical_passive_stats import attack_keywords
        keywords.update(attack_keywords(self,minion))
        if not minion.silenced and minion.card_id in ('TID_712t','TID_712t2','GDB_230','TSC_218','TID_080') and any(w['source']==minion.uid for w in getattr(self,'_attack_windows',[])):
            keywords.add('IMMUNE')
        if hasattr(minion,'_muradin_hammer'):keywords.update(('WINDFURY','DEATHRATTLE'))
        if minion.card_id=='TIME_619t':
            from .fabled_effects import BOONS
            keywords.update(BOONS[cid] for cid in self.players[minion.owner].bwonsamdi_boons)
        if getattr(minion,'_control_no_attack_until',-1)>=self.turn:keywords.add('CANT_ATTACK')
        if getattr(self.players[minion.owner],'historical_jaina_elementals_lifesteal',False) and has_tribe(self._card_data(minion),'ELEMENTAL'):keywords.add('LIFESTEAL')
        if getattr(self.players[minion.owner],'historical_boom_mechs_rush',False) and has_tribe(self._card_data(minion),'MECHANICAL'):keywords.add('RUSH')
        if self.players[minion.owner].dragons_have_rush and has_tribe(self._card_data(minion),'DRAGON'):keywords.add('RUSH')
        if not minion.silenced:
            if minion.card_id=='GIL_685' and minion.attack>=3:keywords.update(('TAUNT','LIFESTEAL'))
            if minion.card_id=='WC_015' and not any(m is not minion and m.health>0 for m in self.players[minion.owner].minions):keywords.add('POISONOUS')
            if minion.card_id=='BT_713t':keywords.add('STEALTH')
            if minion.card_id=='BT_197t' and self.current!=minion.owner:keywords.add('ELUSIVE')
        if minion.attached_death_effects:keywords.add('DEATHRATTLE')
        if minion.rule_state.get('historical_spell_damage',0):keywords.add('SPELLPOWER')
        if minion.rule_state.get('historical_fire_spell_damage',0):keywords.add('SPELLPOWER')
        keywords.update(e['keyword'] for e in minion.temporary_keywords)
        from .historical_passive_stats import continuous_keywords
        keywords.update(continuous_keywords(self,minion,keywords))
        from .historical_aura_finish_batch import keywords as aura_finish_keywords
        keywords.update(aura_finish_keywords(self,minion))
        if ('IMMUNE_WHILE_ATTACKING' in keywords and
                any(window['source']==minion.uid for window in getattr(self,'_attack_windows',[]))):
            keywords.add('IMMUNE')
        from .cards import FRIENDLY_KEYWORD_AURAS
        if minion in self.players[minion.owner].minions:
            for cid,rule in FRIENDLY_KEYWORD_AURAS.items():
                if isinstance(rule,tuple):
                    group,keyword=rule
                    if group!='others':raise UnsupportedCard('Unknown friendly keyword aura scope: '+str(group))
                    active=any(source is not minion and source.card_id==cid and not source.silenced and source.health>0
                               for source in self.players[minion.owner].minions)
                else:
                    keyword=rule;active=self._active(cid,minion.owner)
                if active:keywords.add(keyword)
        if (not minion.silenced and minion.card_id=='CATA_613'
                and not any(m is not minion for m in self.players[minion.owner].minions)):
            keywords.add('IMMUNE')
        if self._active('CATA_898',1-minion.owner):keywords.add('TAUNT')
        # Pinned Migrating Elekk text has intrinsic Taunt but omits its tag.
        if minion.card_id=='MEND_303' and not minion.silenced:keywords.add('TAUNT')
        if minion.card_id=='TSC_026' and not minion.silenced and any(m.card_id=='TSC_026t' and m.health>0 for m in self.players[minion.owner].all_minions):keywords.add('IMMUNE')
        if minion.rule_state.get('historical_opponent_elusive') and minion.owner!=self.current:keywords.add('ELUSIVE')
        from .forge_intrinsics import values as intrinsic_values
        if has_tribe(self._card_data(minion),'BEAST') and any(
                source.health>0 and intrinsic_values(source,'beast_charge')
                for source in self.players[minion.owner].minions):
            keywords.add('CHARGE')
        return keywords

    def _event_listeners(self):
        base=[(m, TRIGGERS[m.card_id]) for m in sorted([m for p in self.players for m in p.all_minions],key=lambda m:m.uid)
                     if not m.silenced and m.card_id in TRIGGERS and
                     (not m.dormant or str(TRIGGERS[m.card_id][0]).startswith('dormant_'))]
        from .historical_sleep_batches import listeners as historical_sleep_listeners
        base.extend(historical_sleep_listeners(self))
        from .historical_starships import listeners as starship_listeners
        base.extend(starship_listeners(self))
        from .forge_intrinsics import listeners
        from .historical_keyword_batches import listeners as keyword_listeners
        return sorted(base+self._magnetic_listeners()+listeners(self)+keyword_listeners(self),key=lambda item:item[0].uid)

    def _queue_event(self, kind, **data):
        from .historical_obligation_spells import event as obligation_event
        obligation_event(self,kind,data)
        from .historical_stormwind_questline_finish import event as stormwind_event
        stormwind_event(self,kind,data)
        from .historical_condition_spell_batch import event as condition_batch_event
        condition_batch_event(self,kind,data)
        from .historical_sidequest_spell_batch import event as sidequest_batch_event
        sidequest_batch_event(self,kind,data)
        from .historical_spellstone_finish import event as stone_finish_event
        stone_finish_event(self,kind,data)
        from .historical_spell_archive_batch import event as archive_event
        archive_event(self,kind,data)
        from .historical_hand_batches import held_event
        from .historical_infuse_batches import held_death
        held_death(self,kind,data)
        held_event(self,kind,data)
        self._quest_family_event(kind,data)
        from .historical_nature_pool import event as nature_event
        nature_event(self,kind,data)
        from .historical_mage_quests import event as mage_quest_event
        mage_quest_event(self,kind,data)
        self._evolving_event(kind,data)
        self._imbue_consumer_event(kind,data)
        self._b60_event(kind,data)
        from .historical_keyword_batches import tag_event
        tag_event(self,kind,data)
        from .historical_harvester import tag_event as tag_harvester_event
        tag_harvester_event(self,kind,data)
        listeners=self._event_listeners()
        self._rule_events.append((kind, data, listeners))
        from .historical_copy_batches import pirate_zone_event
        pirate_zone_event(self,kind,data)
        from .historical_copy_batches import persistent_spell_event
        persistent_spell_event(self,kind,data)
        from .historical_dark_heroes import event as dark_hero_event
        dark_hero_event(self,kind,data)
        from .historical_frozen_heroes import event as frozen_hero_event
        frozen_hero_event(self,kind,data)
        from .historical_masquerade import event as masquerade_event
        masquerade_event(self,kind,data)
        self._autocast_event(kind,data)
        self._obligation_event(kind,data)
        from .historical_growing_weapons import event as growing_weapon_event
        growing_weapon_event(self,kind,data)
        from .historical_lingering_spells import event as lingering_spell_event
        lingering_spell_event(self,kind,data)
        from .historical_secret_archive import event as archive_secret_event
        archive_secret_event(self,kind,data)
        self._trace_phase("event_queued", event_kind=kind, listener_uids=[m.uid for m,_ in listeners])

    def _record_hero_stat_gain(self,owner,kind,amount):
        if amount<=0:return
        player=self.players[owner];state=getattr(player,'historical_hero_stat_gains',{})
        if state.get('turn')!=self.turn:state=dict(turn=self.turn,attack=0,armor=0)
        state[kind]+=amount;player.historical_hero_stat_gains=state
        if kind=='attack':self._queue_event('historical_hero_attack_gained',owner=owner,amount=amount)

    def _gain_hero_attack(self,owner,amount):
        before=self._hero_attack(owner)
        self.players[owner].temporary_attack+=amount
        self._record_hero_stat_gain(owner,'attack',self._hero_attack(owner)-before)

    def _gain_armor(self,owner,amount):
        if amount<=0:return 0
        amount+=2*sum(m.card_id=='ETC_355' and not m.silenced and not m.dormant and m.health>0 for m in self.players[owner].minions)
        previous_attack=self._hero_attack(owner)
        self.players[owner].armor+=amount
        self._record_hero_stat_gain(owner,'attack',self._hero_attack(owner)-previous_attack)
        self._record_hero_stat_gain(owner,'armor',amount)
        player=self.players[owner]
        player.historical_armor_gained=getattr(player,'historical_armor_gained',0)+amount
        from .historical_held_upgrades import progress as held_spellstone_progress
        held_spellstone_progress(self,owner,'jasper',amount)
        player.historical_armor_changed_turn=self.turn
        self._gain_hero_attack(owner,amount*getattr(player,'historical_odyn',0))
        self._log('armor',player=owner,amount=amount)
        self._queue_event('armor_gained',owner=owner,amount=amount)
        return amount

    def _trigger_matches(self, wanted, kind, data, m):
        from .historical_starships import matches as starship_matches
        starship_result=starship_matches(self,wanted,kind,data,m)
        if starship_result is not None:return starship_result
        from .historical_upgrade_batches import matches as historical_upgrade_matches
        upgrade_match=historical_upgrade_matches(self,wanted,kind,data,m)
        if upgrade_match is not None:return upgrade_match
        from .historical_copy_batches import matches as historical_copy_matches
        copy_match=historical_copy_matches(self,wanted,kind,data,m)
        if copy_match is not None:return copy_match
        from .historical_event_batches import matches as historical_event_matches
        event_result=historical_event_matches(self,wanted,kind,data,m)
        if event_result is not None:return event_result
        from .historical_keyword_batches import matches as keyword_matches
        result=keyword_matches(self,wanted,kind,data,m)
        if result is not None:return result
        magnetic=self._magnetic_trigger_matches(wanted,kind,data,m)
        if magnetic is not None:return magnetic
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
        if isinstance(wanted,tuple) and wanted[0]=='friendly_tribe_attacked':
            attacker=self._find(data.get('source',0)) if kind=='minion_attack' else None
            return attacker is not None and data['owner']==m.owner and has_tribe(self._card_data(attacker),wanted[1])
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
            return kind=='minion_played' and data['owner']==m.owner and wanted[1] in self._event_card_data(data).get('mechanics',[])
        if isinstance(wanted,tuple) and len(wanted)==2 and wanted[0]=='spell_school_played':
            return kind=='spell_played' and data['owner']==m.owner and has_school(self._event_card_data(data),wanted[1])
        if isinstance(wanted,tuple) and len(wanted)==2 and wanted[0]=='spell_school_cast':
            return kind=='spell_cast' and data['owner']==m.owner and has_school(self._event_card_data(data),wanted[1])
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
             has_tribe(self._event_card_data(data), 'ELEMENTAL')))

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
            if m not in self.players[m.owner].board or (m.silenced and not (isinstance(wanted,tuple) and wanted[0]=='magnetic_attack')):
                continue
            if not self._trigger_matches(wanted, frame['kind'], frame['data'], m):
                continue
            key = (m.uid, wanted)
            if any(f['key'] == key for f in self._event_frames) and not (
                    (m.card_id=='DINO_400' and wanted=='friendly_armor_gained') or
                    (m.card_id=='EDR_471' and wanted=='damaged_self') or
                    (m.card_id=='REV_377' and wanted==('historical_copy_event','courier')) or
                    (m.card_id=='TOY_511' and wanted==('summon','friendly','PIRATE')) or
                    # Umbra observes the minions summoned by a triggered
                    # Deathrattle as well as the original summoned minion.
                    (m.card_id=='UNG_900' and wanted==('summon','friendly',None))):
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

    def _set_minion_attack(self,m,amount):
        from .historical_saidan import gain as saidan_gain
        before=m.attack+m.attack_deficit
        if m.health>0 and any(m is value for value in self.players[m.owner].minions):amount=before+saidan_gain(m,amount-before)
        m.attack=max(0,amount)
        m.attack_deficit=min(0,amount)
        if amount>before and m.health>0 and m in self.players[m.owner].minions:
            self._queue_event('historical_minion_attack_gained',owner=m.owner,source=m.uid,amount=amount-before)

    def _adjust_minion_attack(self,m,amount):
        self._set_minion_attack(m,m.attack+m.attack_deficit+amount)

    def _buff(self,m,attack,health):
        if self._fire_immune_target(m.uid):return
        if m.dormant:return
        from .historical_saidan import gain as saidan_gain
        health=saidan_gain(m,health)
        self._adjust_minion_attack(m,attack)
        m.health+=health
        m.max_health+=health
        self._colossal_stat_checkpoint()
        for player in self.players:
            for minion in player.minions:
                if minion.rule_state.get('historical_permanent_frozen') and minion.frozen_until<0 and not self._active('DRG_068',minion.owner):self._freeze(minion.uid)
        self._champion_checkpoint()

    def _refresh_auras(self):
        self._observe_control_changes()
        from .historical_student_spells import refresh_hand_ranks
        refresh_hand_ranks(self)
        from .historical_starships import refresh_terran
        refresh_terran(self)
        from .historical_copy_batches import refresh_fortunes
        refresh_fortunes(self)
        from .historical_copy_batches import check_star_collisions
        check_star_collisions(self)
        self._recover_overdraw()
        from .historical_utility_spells import forge_quel_delar
        for owner in (0,1):forge_quel_delar(self,owner)
        board = [m for p in self.players for m in p.all_minions]
        desired = {m.uid: [0, 0] for m in board}
        for owner, p in enumerate(self.players):
            from .historical_tribal_batches import aura as tribal_aura
            for target in p.minions:
                a,h=tribal_aura(self,target);desired[target.uid][0]+=a;desired[target.uid][1]+=h
                from .historical_aura_finish_batch import attack_bonus as aura_finish_attack_bonus
                desired[target.uid][0]+=aura_finish_attack_bonus(self,target)
                from .historical_timed_spells import deputization_layers
                desired[target.uid][0]+=2*deputization_layers(self,target)
                if target.card_id in ('ONY_005ta11','VAC_464t11') and not target.silenced:
                    count=len(getattr(p,'_historical_cast_records',()))
                    desired[target.uid][0]+=count;desired[target.uid][1]+=count
            from .historical_copy_batches import ZERG_IDS
            for target in p.minions:
                if target.card_id in ZERG_IDS:
                    desired[target.uid][0]+=getattr(p,'historical_zerg_attack_bonus',0)
            for i, source in enumerate(p.board):
                if isinstance(source,(Location,Permanent)) or source.dormant: continue
                if source.health <= 0 or source.silenced:
                    continue
                if source.card_id=='CATA_493':
                    bonus=2*len(p.discard_history)
                    desired[source.uid][0]+=bonus
                    desired[source.uid][1]+=bonus
                historical_attack,historical_health=self._historical_passive_aura_values(source)
                desired[source.uid][0]+=historical_attack
                desired[source.uid][1]+=historical_health
                from .forge_intrinsics import values as intrinsic_values
                friendly_attack=sum(intrinsic_values(source,'friendly_attack'))
                if friendly_attack:
                    for other in p.minions:
                        if other is not source and other.health>0:desired[other.uid][0]+=friendly_attack
                beast_attack=sum(intrinsic_values(source,'beast_attack'))
                if beast_attack:
                    for other in p.minions:
                        if other is not source and other.health>0 and has_tribe(self._card_data(other),'BEAST'):
                            desired[other.uid][0]+=beast_attack
                adjacent_attack=sum(intrinsic_values(source,'adjacent_attack'))
                if adjacent_attack:
                    for j,m in enumerate(p.board):
                        if (abs(i-j)==1 and not isinstance(m,(Location,Permanent))
                                and not m.dormant and m.health>0):
                            desired[m.uid][0]+=adjacent_attack
                from .historical_passive_stats import aura_bonuses
                if source.card_id in ('AT_075','ETC_337','ULD_173','ULD_179','ETC_107'):
                    for target,extra_attack,extra_health in aura_bonuses(self,source):
                        desired[target.uid][0]+=extra_attack;desired[target.uid][1]+=extra_health
                aura = AURAS.get(source.card_id)
                if source.card_id in ('CATA_565t','CATA_153t','CATA_153t1'):aura=('adjacent',self._herald_value(source),0)
                if aura:
                    group, attack, health = aura
                    for j, m in enumerate(p.board):
                        if isinstance(m,(Location,Permanent)) or m.dormant: continue
                        matches = m is not source and (
                            group == 'others' or
                            (group == 'adjacent' and abs(i-j) == 1) or
                            (group in TRIBES and has_tribe(self._card_data(m),group)))
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
        for owner,p in enumerate(self.players):
            bonus=self._historic_crabatoa_aura(owner)
            for m in p.minions:
                if m.card_id in ('TSC_937t','TSC_937t3') and not m.dormant:desired[m.uid][0]+=bonus
            if p.weapon:
                from .historical_arsenal_batches import weapon_aura
                weapon_bonus=(bonus if p.weapon['card_id']=='TSC_937t2' else 0)+weapon_aura(self,owner)
                previous_attack=self._hero_attack(owner)
                p.weapon['attack']+=weapon_bonus-p.weapon.get('aura_attack',0)
                p.weapon['aura_attack']=weapon_bonus
                self._record_hero_stat_gain(owner,'attack',self._hero_attack(owner)-previous_attack)
        from .historical_final_spell_roots import celestial_bonuses
        celestial_bonuses(self,desired)
        for m in board:
            if not m.dormant and hasattr(m,'_muradin_hammer'):
                for held in [m._muradin_hammer]+list(getattr(m,'_muradin_extra_hammers',())):
                    desired[m.uid][0]+=held['attack']
                    desired[m.uid][1]+=held['durability']
            attack, health = desired[m.uid]
            self._adjust_minion_attack(m,attack-m.aura_attack)
            from .historical_saidan import gain as saidan_gain
            delta = saidan_gain(m,health-m.aura_health)
            m.max_health += delta
            if delta > 0 and (m.health > 0 or getattr(m,'_historical_zero_health_entry',False)):
                m.health += delta
            elif delta < 0:
                m.health = min(m.health, m.max_health)
            m.aura_attack, m.aura_health = attack, health
            if m.card_id=='EX1_335' and not m.silenced and not m.dormant:self._set_minion_attack(m,max(0,m.health))
        self._colossal_stat_checkpoint()
        for player in self.players:
            for minion in player.minions:
                if minion.rule_state.get('historical_permanent_frozen') and minion.frozen_until<0 and not self._active('DRG_068',minion.owner):self._freeze(minion.uid)

        # Track continuous hero Attack separately from weapon activation;
        # simply entering a turn with a weapon does not count as a gain.
        for owner,player in enumerate(self.players):
            weapon_attack=(player.armor if player.weapon['card_id']=='CORE_LOOT_044' else player.weapon['attack']) if player.weapon else 0
            aura=self._hero_attack(owner)-player.temporary_attack-weapon_attack
            previous=getattr(player,'historical_hero_aura_attack',0)
            player.historical_hero_aura_attack=aura
            self._record_hero_stat_gain(owner,'attack',aura-previous)

        from .historical_tribal_batches import watch_hands
        watch_hands(self)

    def _damage(self, target, amount, poisonous=False, *, damage_source=..., damage_owner=None, damage_cause=None, _historical_redirected=frozenset(), _historical_source_modified=False):
        from .cards import INCOMING_DAMAGE_MODIFIERS
        source=getattr(self,'_damage_origin',None) if damage_source is ... else damage_source
        if damage_owner is None and damage_source is not ... and source is not None:damage_owner=source.owner
        if damage_owner is not None and (type(damage_owner) is not int or damage_owner not in (0,1)):
            raise ValueError('Invalid damage controller')
        context=getattr(self,'_active_effect_context',{})
        blocked_uid=context.get('historical_shudderblock_uid')
        if (blocked_uid is not None and not context.get('spell') and
                not any(window['source']==blocked_uid for window in getattr(self,'_attack_windows',())) and
                getattr(source,'uid',None)==blocked_uid and target==self.hero_id(1-context['owner'])):
            return 0
        if amount<=0:return 0
        from .historical_damage_modifiers import incoming
        if not _historical_source_modified:amount=incoming(self,target,amount,source)
        if self._replace_plague_damage(target,amount,source):return 0
        if target>0 and self._permanent_entity(target) is not None:return 0
        if target>0 and (self._dormant_entity(target) is not None and self._dormant_entity(target).dormant):return 0
        if target>0:
            victim=next((m for player in self.players for m in player.minions if m.uid==target),None)
            if victim is not None:
                amount*=2**sum(m.card_id=='RLK_952' and not m.silenced and m.health>0 for m in self.players[self.current].minions if m.owner!=victim.owner)
            if victim is not None and victim.health==victim.max_health:
                amount*=2**sum(m.card_id=='GDB_472' and not m.silenced and not m.dormant and m.health>0 for m in self.players[1-victim.owner].minions)
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
            if weapon and weapon['card_id']=='ETC_084' and owner==self.current:
                from .historical_arsenal_batches import lose_durability
                lose_durability(self,owner,1)
                self._heal(target,2,healer=owner)
                self._log('prevent_damage',player=owner,card='ETC_084',amount=amount)
                return 0
            if weapon and HERO_DAMAGE_WEAPON_REPLACEMENTS.get(weapon['card_id'])=='lose_durability':
                from .historical_arsenal_batches import lose_durability
                lose_durability(self,owner,1)
                self._log('prevent_damage',player=owner,card=weapon['card_id'],amount=amount)
                return 0
        from .historical_damage_modifiers import redirected_target
        redirection=redirected_target(self,target,_historical_redirected)
        if redirection is not None:
            destination,bearer=redirection
            self._log('historical_damage_redirected',target=target,destination=destination,bearer=bearer,amount=amount)
            return self._damage(destination,amount,poisonous,damage_source=source,damage_owner=damage_owner,damage_cause=damage_cause,
                                _historical_redirected=_historical_redirected|{bearer},_historical_source_modified=True)
        if target>0:
            minion=self._find(target)
            target_health_before=minion.health
            target_attack_before=minion.attack
            if 'IMMUNE' in self._effective_keywords(minion):return 0
            amount*=2**minion.rule_state.get('historical_hallucination_layers',0)
            modifier=INCOMING_DAMAGE_MODIFIERS.get(minion.card_id)
            if modifier and not minion.silenced:
                multiplier,extra=modifier
                amount=amount*multiplier+extra
        if target>0:
            tar=getattr(self,'historical_tar_slick',{})
            if tar.get('turn')==self.turn:amount*=2**tar.get('layers',0)
        if target>0 and not minion.silenced and minion.card_id in ('YOP_035','VAC_527'):amount=min(1,amount)
        if target>0 and minion.rule_state.get('historical_riot_turn')==self.turn and not minion.silenced:
            amount=min(amount,max(0,minion.health-1));poisonous=False
            if amount<=0:return 0
        if target>0 and minion.rule_state.get('historical_shout_turn')==self.turn:
            amount=min(amount,max(0,minion.health-1))
            if amount<=0:return 0
        shielded=target>0 and 'DIVINE_SHIELD' in minion.keywords
        if shielded and self._lasting_shield_hit(minion,minion.owner):return 0
        if target<0 and self.players[-target-1].turns_taken<getattr(self.players[-target-1],'historical_alibi_until',-1):amount=min(amount,1)
        if target<0:
            from .historical_iconic_followups import prevent_fatal
            if prevent_fatal(self,-target-1,amount):return 0
        target_owner=-target-1 if target<0 else minion.owner
        before_health=self.players[-target-1].health if target<0 else None
        before_armor=self.players[-target-1].armor if target<0 else None
        was_alive=target>0 and minion.health>0
        if target<0 and self._onyxia_active(-target-1):
            owner=-target-1;p=self.players[owner];absorbed=min(p.armor,amount)
            p.armor-=absorbed
            self._replace_hero_health_loss(owner,amount-absorbed)
            dealt=absorbed
            if dealt:self._log('damage',target=target,amount=dealt)
        else:
            dealt = super()._damage(target, amount, poisonous)
        if target<0 and self.players[-target-1].health!=before_health:
            self.players[-target-1].hero_health_changed_turn=True
            if -target-1==self.current:
                self.players[-target-1].historical_own_health_changes=getattr(self.players[-target-1],'historical_own_health_changes',0)+1
                from .historical_growing_weapons import hero_health_changed
                hero_health_changed(self,-target-1)
        if target<0 and self.players[-target-1].armor!=before_armor:self.players[-target-1].historical_armor_changed_turn=self.turn
        if shielded and 'DIVINE_SHIELD' not in minion.keywords:
            self._queue_event('shield_lost',owner=minion.owner,target=target)
        if dealt and target>0 and was_alive and minion.health<=0 and damage_cause=='hero_power' and damage_owner in (0,1):
            listeners=[m.uid for m in self.players[damage_owner].minions if m.card_id=='TRL_315' and not m.silenced and m.health>0]
            if listeners:
                self._rule_events.append(('captured_effects',dict(operations=tuple(('draw',1) for _ in listeners),
                    context=dict(owner=damage_owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
        if dealt and target>0 and minion.card_id=='AV_143':
            minion.rule_state['historical_korrak_exact_lethal']=was_alive and dealt==target_health_before and minion.health<=0
        if dealt:
            if target>0 and was_alive:self._entity_damage(minion,getattr(self,'_damage_origin',None) if damage_source is ... else damage_source,dealt)
            if target<0:
                self.players[-target-1].hero_damage_taken_turn+=dealt
                self.players[-target-1].hero_damage_events_turn+=1
                if any(self._active('GDB_144',owner) for owner in (0,1)):self.players[-target-1].historical_lumia_immune_turn=self.turn
            self._queue_event('damage', target=target, amount=dealt, damage_owner=damage_owner, target_owner=target_owner, source_uid=getattr(source,'uid',None), damage_cause=damage_cause, target_health_before=target_health_before if target>0 else None,target_attack_before=target_attack_before if target>0 else None)
            self._zone_damage_trigger(target)
        return dealt

    def _replace_spell_damage(self,target,amount,ctx):
        if target<=0 or amount<=0 or not ctx.get('spell'):return False
        m=next((m for p in self.players for m in p.minions if m.uid==target),None)
        cid=ctx.get('card_id')
        if m is None or m.health<=0 or m.silenced or m.owner!=ctx['owner'] or cid not in self.cards:return False
        if m.card_id=='TIME_217' and has_school(self.cards[cid],'NATURE'):
            from .generation_cards import pool,random_cards,board_pool
            request=board_pool(pool(card_type='MINION',minimum=5,maximum=5))
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
        magnetic_freezer=source is not None and any(part['card_id']=='TTN_077' for part in source.rule_state.get('magnetic_parts',()))
        if dealt>0 and source is not None and not source.silenced and (source.card_id in DAMAGE_FREEZERS or magnetic_freezer):
            self._freeze(target)

    def _heal(self,target,amount,*,healer=None,_after_shadow=False,spell=False,power=False,_receipt=None):
        # Repeated spell effects defer death settlement across their copies
        # and choices. An on-board target may recover before that boundary.
        healable=next((m for p in self.players for m in p.minions
                       if m.uid==target and (m.health>0 or self._spell_repeat_depth)),None) if target>0 else None
        if target>0 and healable is None:
            self._log('effect_fizzled',effect='heal',target=target,reason='target_departed_or_dead')
            return 0
        if self._fire_immune_target(target):return 0
        if target>0 and self._dormant_entity(target) is not None and self._dormant_entity(target).dormant:return 0
        entity=self.players[-target-1] if target<0 else self._find(target)
        if healer is not None and amount>0 and not _after_shadow:
            amount+=self.players[healer].permanent_healing_bonus
            if spell:amount*=self._spell_multiplier(healer)
            if power:
                from .historical_damage_modifiers import power_multiplier
                amount*=power_multiplier(self,healer)
            amount*=2**sum(m.card_id=='BOT_236' and not m.silenced and not m.dormant and m.health>0 for m in self.players[healer].minions)
        if not _after_shadow and self._ruby_heal(target,amount,healer):return 0
        from .historical_damage_modifiers import healing_blocked
        if healing_blocked(self,target):return 0
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
        if target>0 and amount>0 and entity.health>0:self._queue_event('historical_healing_effect',target=target,healer=healer,amount=amount)
        before=entity.health
        if target<0:
            actual=max(0,min(amount,entity.max_health-entity.health))
            entity.health+=actual
            self._log('heal',target=target,amount=actual)
        else:super()._heal(target,amount)
        restored=max(0,entity.health-before)
        if restored and target>0 and entity.card_id=='AV_143':entity.rule_state.pop('historical_korrak_exact_lethal',None)
        if target<0 and entity.health!=before:
            entity.hero_health_changed_turn=True
            if -target-1==self.current:
                entity.historical_own_health_changes=getattr(entity,'historical_own_health_changes',0)+1
                from .historical_growing_weapons import hero_health_changed
                hero_health_changed(self,-target-1)
            if restored:
                entity.hero_healed_turn=True
                self._queue_event('historical_hero_health_gained',owner=-target-1,amount=restored)
        if healer is not None and restored:
            self.players[healer].healing_done_turn+=restored
            self.players[healer].historical_healing_done_total=getattr(self.players[healer],'historical_healing_done_total',0)+restored
            self._colossal_healed(healer,restored)
        if restored:self._queue_event('historical_healed',target=target,restored=restored,healer=healer)
        if before>0 and amount>0:
            excess=max(0,amount-max(0,entity.max_health-before))
            if _receipt is not None:_receipt['overheal']=excess
            if target>0 and excess:self._queue_event('historical_overheal',target=target,overheal=excess,restored=restored,healer=healer)
        return restored

    def _silence(self, m):
        if self._fire_immune_target(m.uid):return
        if m.dormant:return 
        data = self.cards[m.card_id]
        m.silenced = True
        m.remembered_discards.clear()
        m.rule_state.clear()
        for private_field in ('_infinity_cost_receipts','remembered_draw','secret_discard','_bound_card','_bound_minion','_devoured_cards','_nellie_crew','_fragile_illusion','_illusion_possible','_jandice_illusion','_magnetic_upgrades'):
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
        from .historical_replacements import vashj_replaces,vashj_summon
        if vashj_replaces(self,m,cid):return vashj_summon(self,m,cid)
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
        return self._zone_manager.bounce(self,m=m,cost_delta=cost_delta)

    def _draw(self, owner, predicate=None, private=False, *, include_burned=False):
        return self._zone_manager.draw(self,owner=owner,predicate=predicate,private=private,include_burned=include_burned)

    def _shuffle_hand_card(self, owner, card, *, actor=None):
        return self._zone_manager.shuffle_hand_card(self,owner=owner,card=card,actor=actor)

    def _own_shuffle_count(self,owner):
        return sum(entry['kind']=='shuffle' and entry['actor']==owner and entry['destination']==owner
                   for entry in self.players[owner].shuffle_history)

    def _record_deck_insertion(self, destination, actor, count, kind, *, cards, suppress_elekk=False):
        return self._zone_manager.record_deck_insertion(self,destination=destination,actor=actor,count=count,kind=kind,cards=cards,suppress_elekk=suppress_elekk)

    def _trade(self, uid):
        p = self.players[self.current]
        c = next(c for c in p.hand if c.uid == uid)
        p.hand.remove(c)
        p.mana -= 1
        self._b60_spend_mana(self.current,1)
        from .historical_play_batches import WINDUPS
        if c.card_id in WINDUPS:
            state=self._b60_state(c);state['historical_windup']=state.get('historical_windup',0)+1
        from .historical_trade_spell_finish import progress as trade_progress
        trade_progress(self,c)
        # Replacement applies once even with multiple active Jaxons. Keep
        # the traded physical card outside the selectable deck until drawing.
        if any(m.card_id=='SW_045' and not m.silenced and m.health>0 for m in p.minions):
            from .pools import deck_choice_options
            options=deck_choice_options(p.deck,self.cards,3,self.rng)
            if options:
                for option in options:
                    value=p.deck[option['index']]
                    option['physical_uid']=getattr(value,'uid',None)
                self.pending_choice=dict(owner=self.current,kind='historical_jaxon_draw',options=options)
                self.phase='choice'
                self._start_play_effects((('historical_copy_trade_finish',),),dict(owner=self.current,source=None,target=0,spell=False,bonus=0,trade_card=c))
                return
        self._draw(self.current)
        # Preserve enchantments and the relative order of the remaining deck.
        p.deck.insert(self.rng.randrange(len(p.deck)+1), c)
        self._refresh_auras()
        self._record_deck_insertion(self.current,self.current,1,'trade',cards=(c,))
        self._log('trade', player=self.current, card=c.card_id)
        from .historical_trade_spell_finish import after_trade
        after_trade(self,self.current,c)

    def _break_weapon(self, owner):
        p = self.players[owner]
        weapon = p.weapon
        if not weapon:
            return
        from .historical_movements import record
        record(self,'destroyed')
        physical_card = p.equipped_card
        if physical_card is not None:
            history=getattr(p,'historical_broken_weapons',[]);history.append(deepcopy(physical_card));p.historical_broken_weapons=history
        self._queue_event('historical_weapon_broken',owner=owner,card_id=weapon['card_id'])
        p.weapon = None
        p.equipped_card = None
        self._log('weapon_broken',player=owner,card=weapon['card_id'])
        from .cards import DEATH_EFFECTS
        operations=(list(DEATH_EFFECTS.get(weapon['card_id'], []))+
                    list(weapon.get('attached_death_effects',[])))*self._deathrattle_repetitions(owner,weapon=True)
        from .historical_physical_forms import weapon_death_source
        death_source=weapon_death_source(weapon,physical_card)
        for op in operations:
            self._effect(op, dict(owner=owner,source=death_source,target=0,bonus=0,
                                 lifesteal='LIFESTEAL' in weapon.get('historical_keywords',()),poisonous='POISONOUS' in weapon.get('historical_keywords',()),death_position=len(p.board),broken_weapon=weapon,broken_weapon_card=physical_card))

    def _discover_deck(self, owner):
        return self._choice_resolver.discover_deck(self,owner)

    def _discard_cards(self, owner, cards):
        return self._zone_manager.discard_cards(self,owner=owner,cards=cards)

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
        return ((choice['kind']=='historical_physical_spell' and choice.get('discovering',False)) or (choice['kind']=='historical_infuse_choice' and choice.get('mode')=='relic') or (choice['kind']=='historical_treasure' and choice.get('mode') in ('crown','lackey','manager','artifact','cast','hurt','armor','elysiana','mystery','hipster','importer','maruut','murozond','ivory','amalgam','follow_fireheart','follow_hataaru','suspicious','chromatic','power_basic','power_upgraded','malygos','pillar')) or (choice['kind']=='historical_play_zone' and choice.get('discovering',False)) or (choice['kind']=='refresh_discover' and choice.get('completed_discover',False)) or choice['kind'] in {'historical_deck_finish','historical_history_batch','historical_continuation_gift','historical_archive_offer','historical_nature_offer','historical_mage_offer','historical_mage_deck_discover','historical_utility_potion','historical_music_movement','historical_change_transform','historical_generated_spell','historical_deck_spell','historical_tavish_secret','historical_etc_band','historical_jaxon_draw','historical_amulet_vendor','historical_future_location','historical_stitch','historical_griftah','historical_theotar','historical_held_spell','historical_secret_discover','historical_resurrection','dark_global','lasting_deck','draw_from_deck', 'temporary_deck',
                                    'local_enemy_top', 'local_resurrect',
                                    'suspicious_discover','contraband_discover','generation_discover','learned_mentor','evolving_dragon','choicegen_discover','dark_deck','map_discover'} or
                (choice['kind'] == 'composed_zone' and
                 choice.get('mode') in {'copy', 'draw_bottom'}))

    def _record_discover(self, owner, offer=None):
        return self._choice_resolver.record_discover(self,owner,offer)

    def _resolve_choice(self, index, *, resume=True):
        return self._choice_resolver.resolve(self,index,resume=resume)

    def _after_play(self, context):
        if self._rewind_offer(context):return
        if self.terminal:
            return
        cid, owner, source, cost, targeted_minion = context
        history=self.players[owner].replay_history
        if history and history[-1].card.card_id==cid:
            from .historical_obligation_spells import paid as obligation_paid
            obligation_paid(self,owner,history[-1].card)
        self._trace_phase('after_play', card_id=cid, owner=owner, source_uid=getattr(source,'uid',None))
        kind = self.cards[cid]['type']
        from .historical_spellstone_finish import paid as stone_finish_paid
        stone_finish_paid(self,owner,cid)
        edges=getattr(self.players[owner],'_historical_edge_plays',{}).pop((cid,getattr(source,'uid',None)),None)
        if edges is not None:self._queue_event('historical_edge_play',owner=owner,card_id=cid,source=getattr(source,'uid',None),left=edges[0],right=edges[1],cost=cost)
        pending_overloads=getattr(self.players[owner],'historical_play_overloads',{})
        overload=pending_overloads.pop(getattr(source,'uid',None),0)
        if overload:self._queue_event('historical_overload_card_played',owner=owner,card_id=cid,amount=overload)
        if overload:
            from .historical_elemental_questline import played as elemental_played
            elemental_played(self,owner)
            from .historical_whizbang_quests import progress as whizbang_progress
            whizbang_progress(self,owner,'overload')
        if 'COMBO' in self.cards[cid].get('mechanics',()):self._queue_event('historical_combo_card_played',owner=owner,card_id=cid)
        if kind == 'MINION':
            return self._start_minion_after_play(context)
        if kind == 'SPELL':
            self._secret_event('after_spell',owner)
            self._queue_event('spell_cast', owner=owner,card_id=cid,cost=cost,targeted_minion=targeted_minion,physical_card=source,cast_target=getattr(source,'_historical_cast_target',{}))
            from .historical_copy_batches import publish_zentimo
            publish_zentimo(self,owner,source)
            from .historical_copy_batches import publish_choose_spell
            publish_choose_spell(self,owner,source)
            if 'SECRET' in self.cards[cid].get('mechanics',()):self._queue_event('historical_secret_played',owner=owner,card_id=cid)
        if kind in ('WEAPON','LOCATION','HERO'):
            self._queue_event('dormant_other_card_played',owner=owner,card_id=cid)
        self._secret_event('after_card',owner,card_id=cid)
        self._publish_follow(owner,source)
        self._settle(allow_event_choices=True)

    def _system_effect(self, op, ctx):
        """Return False for opcodes handled by the original explicit resolver."""
        owner=ctx['owner']; p=self.players[owner]; q=self.players[1-owner]
        source=ctx.get('source'); target=ctx.get('target',0); name=op[0]
        if name=='inherit_friendly_deathrattle':
            event=ctx['event'];operations=event.get('inherited_operations',())
            if operations:
                from .death_inheritance import check_supported
                check_supported(operations)
                source.attached_death_effects.extend(deepcopy(operations))
        elif name=='next_power_set_cost':
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
            if op[2] and source not in p.board:
                raise UnsupportedCard('Right-side summon source left play; continuation ordering requires review')
            initial_offset=op[3] if len(op)>3 else 0
            for offset in range(op[2]):
                self._summon(owner,op[1],p.board.index(source)+1+initial_offset+offset, entry_origin='effect', entry_site="systems._system_effect:name == 'summon_right'", entry_source=ctx.get('source'))
        elif name=='copy_self_right':
            for _ in range(op[1]):
                position=p.board.index(source)+1 if source in p.board else min(ctx.get('summon_position',len(p.board)),len(p.board))
                self._summon(owner,source.card_id,position,copy_from=source, entry_origin='copy', entry_site="systems._system_effect:name == 'copy_self_right'", entry_source=ctx.get('source'))
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
            choices=[i for i,v in enumerate(p.deck) if self._card_data(v)['type']=='MINION'
                     and self._card_stat(v,'cost',owner)<=op[1]]
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
            physical=event.get('physical_card')
            if physical is None:
                raise UnsupportedCard('Spell-copy event is missing its physical card')
            # Preserve constructed effects, chosen ingredients and provenance.
            # A new bare card ID cannot represent a player-crafted spell.
            self._clone_hand_card(1-event['owner'],physical,source_owner=event['owner'])
        elif name=='add_opponent':
            for _ in range(op[2]):self._add(1-owner,op[1])
        elif name=='fill_hand':
            while len(p.hand)<getattr(p,'hand_capacity',10):self._add(owner,op[1])
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
                     [m.uid for player in self.players for m in player.minions if m.health>0] if group=='all_minions' else
                     [u for u in self._characters() if (source is None or u!=source.uid) and (u<0 or self._find(u).health>0)])
            if choices and not self.terminal:self._deal_effect(self.rng.choice(choices),1,dict(ctx,bonus=0,spell_multiplier_applied=True))
        elif name in ('missiles','attack_missiles'):
            group=op[1] if name=='missiles' else 'enemies'
            shots=(op[2]+ctx.get('bonus',0)) if name=='missiles' else max(0,source.attack)
            if name=='missiles' and ctx.get('spell'):shots*=self._spell_multiplier(owner)
            for _ in range(shots):
                choices=([self.hero_id(1-owner)]+[m.uid for m in q.minions if m.health>0] if group=='enemies' else
                         [m.uid for m in q.minions if m.health>0] if group=='enemy_minions' else
                     [m.uid for player in self.players for m in player.minions if m.health>0] if group=='all_minions' else
                         [u for u in self._characters() if (source is None or u!=source.uid) and (u<0 or self._find(u).health>0)])
                if not choices or self.terminal:break
                self._deal_effect(self.rng.choice(choices),1,dict(ctx,bonus=0,spell_multiplier_applied=True))
                self._settle()
        elif name=='set_hero_health':
            if owner==self.current and p.health!=op[1]:
                p.historical_own_health_changes=getattr(p,'historical_own_health_changes',0)+1
                from .historical_growing_weapons import hero_health_changed
                hero_health_changed(self,owner)
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
            if any(has_tribe(self._card_data(c),'DRAGON') for c in p.hand):
                self._effect(('area_damage','all_minions',op[1]),ctx)
        elif name=='remove_cheap_decks':
            for recipient,player in enumerate(self.players):
                removed=[v for v in player.deck if self._card_data(v)['cost']<=op[1]]
                player.deck[:]=[v for v in player.deck if self._card_data(v)['cost']>op[1]]
                for value in removed:self._zone_card_removed(recipient,value,'deck','destroy')
        elif name=='remove_own_top':
            for _ in range(min(op[1],len(p.deck))):
                value=p.deck.pop();self._zone_card_removed(owner,value,'deck','destroy')
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
