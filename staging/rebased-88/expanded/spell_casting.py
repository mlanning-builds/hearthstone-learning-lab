"""Internal spell effects run within the caller's resumable operation frame.

A minion casts these spells; this is not a paid hand play. Spell context is
separate from the casting minion so Poisonous/Lifesteal are not inherited.
"""
from copy import deepcopy
from engine.cards import UnsupportedCard
from engine.game import Card
from .cards import RULES, CHOICES
from .spell_casting_cards import INTERNAL_SPELLS

# Admission is by shared executable operation family, never by filtering a
# consumer's random pool. Unsupported selected cards still fail explicitly.
INTERNAL_TARGETS={'historical_recruit','historical_shield_minion','historical_copy_protoss_target','historical_copy_hand_minion','historical_galakrond_undamaged_character','none','character','minion','enemy_minion','friendly_minion',
                  'damaged_minion','undamaged_minion','enemy_character',
                  'friendly_beast','friendly_undead','large_minion','damaged_enemy_minion',
                  'friendly_character','legendary_minion','friendly_wisp','weapon_required',
                  'repeated_enemy_character','small_attack_minion','historical_attack_at_least_five'}
INTERNAL_OPERATIONS={'historical_copy_swap_decks','historical_copy_snapshot_restore','historical_infuse_relic','historical_infuse_all_totems','historical_infuse_totem_choice','historical_infuse_destroy_small','historical_infuse_bats','historical_infuse_touch_return','historical_infuse_evolve','historical_draw_batch','historical_treasure_goblet','historical_treasure_crown','historical_galakrond_invoke','historical_galakrond_wolves','forge_sidequest','crafted_spell','counterfeit_jade','counterfeit_potion','counterfeit_resurrect','essence_chain','ruby_sanctum','lost_city_start','slice_replay','request_end_turn','crystal_core','nether_portal','time_warp','aura_random_shield_buff','brox_portal','learned_bulb_cast','herald','herald_hero_lifesteal','companions_replace','companions_random','companions_all','companions_choose','void_soul_cast','damage_add_if_dead','autocast_spend_mana','imbue','rewindgen_budget','rewindgen_holy','rewindgen_sands','generation_summon_attack','mutation_board','mutation_bribe','mutation_anomalize','mutation_life_cycle','stored_slime','stored_resummon','stored_egg','dark_deck_discover','shatter_board_death','shatter_copy_target','shatter_generate_combined','generate_random',
                     'rewind_shade','rewind_draw_buff','rewind_discard_both','rewind_silence_destroy','damage','draw','summon','area_damage','buff','armor','keyword',
                     'destroy','add','hero_attack','board_buff','heal','freeze',
                     'freeze_enemies','heal_own_hero','area_heal','temporary_mana',
                     'summon_fixed_random','filtered_draw','discover_deck',
                     'temporary_deck_discover','held_draw','held_buff','held_area',
                     'held_cleave','held_picklock','b60_payload_damage','b60_payload_buff',
                     'secret','set_target_stats','set_target_stats_by_owner',
                     'on_draw_shuffle','damage_lowest_health_enemy','damage_random_enemy',
                     'missiles','next_discount','opponent_next_turn_cost','board_keyword',
                     'zone_minion_buff','damage_own_hero','destroy_crystals','gain_full_crystals',
                     'discard','fill_board_summon','summon_from_zone','zone_choice',
                     'heal_full','weapon_buff','destroy_large','destroy_small','destroy_battlefield',
                     'health_one','transform','equip','recruit','random_heal','set_hero_health',
                     'repeat_end_effects','draw_empty','draw_discount','draw_locked','draw_bottom',
                     'draw_distinct_costs','draw_pick','draw_if_cheap','draw_minions_mana_buff',
                     'opponent_draw_copy','tribal_draw_pair','buff_board_count','tribe_board_buff',
                     'buff_random_hand_tribe','hand_buff','shield_character','all_zone_tribe_buff',
                     'grant_death_target','board_expire','bounce_locked','bounce_then_summon',
                     'damage_random_enemy_minion','damage_armor','damage_history','freeze_random_enemies',
                     'historical_hand_buff','historical_heroes_heal','historical_heroes_damage',
                     'add_spell_damage','insert_fixed','resistance_aura','return_spell_if_dead',
                     'damage_then_summon_if_dead','summon_death_identity','copy_deaths_this_turn',
                     'held_tribe_summon','damage_draw_if_dead','damage_draw_if_alive',
                     'damage_resummon','damage_buff_if_dead','damage_heal_enemy_if_dead',
                     'descending_aoe','board_count_aoe','armor_aoe',
                     'raise_corpses','tomb_guardians','grave_strength','blood_tap','asphyxiate',
                     'summon_spend_mana_buff','summon_corpse_keyword',
                     'aoe_draw_dead','random_minion_damage_draw_kills',
                     'choose_boon','fabled_resurrect_dragons','resurrect_highest','resurrect_costs_reborn','summon_played_one_cost',
                     'recruits_shield','bottom_demons','destroy_all_minions',
                     'buff_shared_type','tribal_damage','origin_draw','origin_discount',
                     'barnabus_draw','draw_summon_set_stats','discard_filtered',
                     'force_summon_group','force_enemy_into_target','fill_board_target_copies',
                     'b60_silent_strike','b60_stealth_damage','b60_health_one','b60_other_health_one',
                     'b60_torch','b60_overkill_discount','b60_death_missiles','b60_held_armor',
                     'freeze_neighbors_destroy_damaged','random_distinct_damage','damage_other_random',
                     'damage_owner_draw','damage_summon_count','shuffle_dead_target',
                     'replace_or_upgrade_star','temporary_sulfuras_power','refresh_power',
                     'dormant_confinement','prepare_judgment','bonus_target','replay_dead_minions',
                     'local_dead_dragon','local_enemy_deck_top','destroy_random_enemy',
                     'local_enemy_summon','summon_opponent','b60_shuffle_all','b60_infest',
                     'dream_all','dream_awaken','dream_bounce','dream_nightmare','dream_shuffle',
                     'dream_destroy_yseras','temporary_keyword_target','quest_start','repeat_copy_damage',
                     'historical_guff_crystal','historical_mint_metamorphosis','historical_mint_skull','historical_mint_skull_draw','follow_attach','outcast_draw','enemy_edges_damage','feast_raptors','kindred_cost_draws',
                     'add_opponent','combo_add','damage_hand_center','on_draw_hurt_owner',
                     'quest_murloc_reward','open_permanent','health_by_relation','schedule_stored_payload','leyline_cast','leyline_upgrade','leyline_choose'}

# These families execute through the ordinary resumable dispatcher. Admission
# does not approve or shrink their outcome pools: resolution still validates
# each complete contract before offering cards or consuming random outcomes.
INTERNAL_OPERATIONS.update({'historical_copy_sludge_damage','historical_copy_mankrik','historical_copy_give_curse','historical_copy_plague_effect','historical_copy_shuffle_plagues','historical_copy_toxin_bounce','historical_copy_literal_family','damage_enemy_hero','generate_discover','generation_discount_school',
    'choicegen_discover','choicegen_remaining_mana','choicegen_corpse_discover',
    'choicegen_damage_discover','choicegen_discovered_summon',
    'choicegen_two_mana_discount','choicegen_no_minion_discount','choicegen_violet',
    'choicegen_cosmic_again','dark_global_discover','mutation_split_minion',
    'mutation_alternate_reality','mutation_choose_hand','mutation_hand_demons',
    'mutation_deck_druid','companions_extra','corpse_target_damage'})

INTERNAL_OPERATIONS.add('historical_copy_cthun_piece')

INTERNAL_OPERATIONS.update({'historical_copy_vistah_start','historical_copy_protoss_draw','historical_copy_protoss_next','historical_copy_protoss_spell','historical_copy_hallucination','historical_copy_photon','historical_copy_weapon_poison','historical_copy_spore','historical_drawn_eruption','historical_copy_cup_muscle','historical_copy_divine_brew'})

class SpellCasting:
    def _spell_cast_choice(self,choice,selected):
        if choice['kind']!='absorb_spell':return False
        owner=choice['owner'];hand=self.players[owner].hand
        card=next((c for c in hand if c.uid==selected['uid']),None)
        if card is None:raise UnsupportedCard('Selected spell left hand before absorption')
        hand.remove(card)
        # Absorption records identity, not a castable physical enchantment copy.
        choice['source'].rule_state['absorbed_spell_id']=card.card_id
        self._refresh_auras()
        return True

    def _supports_internal_spell(self,cid,owner=None):
        if cid not in self.cards or self.cards[cid]['type']!='SPELL':return False
        actor=self.current if owner is None else owner
        if actor not in (0,1):raise ValueError('Invalid internal spell owner')
        if any(op[0]=='herald' for op in RULES.get(cid,('none',()))[1]):
            from .herald import SOLDIERS
            if self.players[actor].hero_class not in SOLDIERS:
                from .selectors import classes
                if len(classes(self.cards[cid])&set(SOLDIERS))!=1:return False
        if cid in INTERNAL_SPELLS or cid=='CATA_186t':
            operations=RULES.get(cid,('none',()))[1]
            return not operations or self._supports_internal_operations(operations)
        if cid in CHOICES:
            # Check every possible branch before random branch selection or
            # physical-zone consumption. An unsupported branch is not removed.
            return bool(CHOICES[cid]) and all(mode in INTERNAL_TARGETS and
                self._supports_internal_operations(operations) for _,mode,operations in CHOICES[cid])
        definition=RULES.get(cid)
        return (definition is not None and bool(definition[1]) and definition[0] in INTERNAL_TARGETS and
                self._supports_internal_operations(definition[1]))

    def _supports_internal_operations(self,operations):
        for op in operations:
            if not isinstance(op,(tuple,list)) or not op or not isinstance(op[0],str):return False
            if op[0]=='schedule_turn_effect':
                if len(op)!=5 or not self._supports_internal_operations(op[4]):return False
            elif op[0]=='historical_play_finale':
                if len(op)!=2 or not self._supports_internal_operations(op[1]):return False
            elif op[0]=='historical_damage_then':
                if len(op)!=4 or not self._supports_internal_operations(op[3]):return False
            elif op[0] in ('historical_summoning_naga_follow','historical_copy_quickdraw_operation'):
                if len(op)!=2 or not self._supports_internal_operations((op[1],)):return False
            elif op[0]=='when_state':
                if len(op)!=3 or not self._supports_internal_operations((op[2],)):return False
            elif op[0]=='b60_attach':
                if len(op)!=2 or not self._supports_internal_operations((op[1],)):return False
            elif op[0]=='kindred':
                if len(op)!=2 or not self._supports_internal_operations(op[1]):return False
            elif op[0]=='historical_dredge':
                from .composed import DREDGE_MODES
                if len(op)!=2 or op[1] not in DREDGE_MODES:return False
            elif op[0] in ('outcast_operation','combo_operation'):
                if len(op)!=2 or not self._supports_internal_operations((op[1],)):return False
            elif op[0]=='if_discarded':
                if len(op)!=2 or not self._supports_internal_operations((op[1],)):return False
            elif op[0]=='if_holding':
                if len(op) not in (3,4) or not self._supports_internal_operations(op[2:]):return False
            elif op[0] in ('generation_attach','generation_attach_board','generation_if_outcast',
                           'generation_if_combo','dark_global_if_dragon'):
                if len(op)!=2 or not self._supports_internal_operations((op[1],)):return False
            elif op[0] in ('generation_if_holding','generation_if_other_tribe'):
                if len(op)!=3 or not self._supports_internal_operations((op[2],)):return False
            elif op[0]=='generation_mana_branch':
                if len(op)!=4 or not self._supports_internal_operations(op[2:]):return False
            elif op[0] not in INTERNAL_OPERATIONS:return False
        return True

    def _resolve_automatic_choices(self):
        """Apply only choices owned by an automatic spell, without reentry.

        The scheduler retains the enclosing operation cursor. A triggered
        player's choice ends this loop and suspends that same scheduler.
        """
        count=0
        while not self.terminal and self.pending_choice is not None and self.pending_choice.get('_automatic',False):
            count+=1
            if count>256:raise UnsupportedCard('Automatic choice chain exceeds verified depth')
            choice=self.pending_choice
            if not choice['options']:raise UnsupportedCard('Automatic choice has no options')
            index=0 if len(choice['options'])==1 else self.rng.randrange(len(choice['options']))
            self._log('automatic_choice',player=choice['owner'],kind=choice['kind'],index=index)
            self._resolve_choice(index,resume=False)

    def _cast_spell_split(self,op,ctx):
        name=op[0];owner=ctx['owner'];source=ctx.get('source')
        if name=='store_highest_spell_aura':
            player=self.players[owner]
            candidates=[c for c in player.hand if self.cards[c.card_id]['type']=='SPELL']
            if not candidates:return ('batch30_noop',),()
            highest=max(self._cost(c,owner) for c in candidates)
            candidates=[c for c in candidates if self._cost(c,owner)==highest]
            card=candidates[0] if len(candidates)==1 else self.rng.choice(candidates)
            if not self._supports_internal_spell(card.card_id,owner):
                raise UnsupportedCard('Stored aura spell not admitted: '+card.card_id)
            player.hand.remove(card);self._refresh_auras()
            token=Card(self._new_id(),op[1])
            token.stored_spell=card;token.aura_duration=op[2]
            return self._cast_spell_split(('cast_physical_spell',token,'random'),ctx)
        if name=='cast_stored_spell':
            original=ctx.get('stored_card')
            if original is None:raise UnsupportedCard('Scheduled spell is missing its stored card')
            card=deepcopy(original);card.uid=self._new_id()
            return self._cast_spell_split(('cast_physical_spell',card,op[1]),ctx)
        if name=='repeat_spell_effects':
            operations,context,count=op[1:]
            if not isinstance(count,int) or isinstance(count,bool) or not 1<=count<=256:
                raise UnsupportedCard('Invalid spell repetition count')
            if not context.get('spell'):
                raise UnsupportedCard('Spell repetition requires spell context')
            # Repeat the selected effect, not a new hand play or random cast.
            # Keep physical identity/context; each body owns its mutable work state.
            copies=tuple(('repeat_spell_copy',deepcopy(operations),dict(context)) for _ in range(count))
            return ('spell_repeat_begin',),copies+(('spell_repeat_end',),)
        if name=='repeat_spell_copy':
            operations,context=op[1:];target=context.get('target',0)
            if target>0 and not any(m.uid==target for p in self.players for m in p.minions):
                return ('internal_spell_fizzle',context.get('card_id')),()
            return self._replay_split(('replay_context',operations,context),ctx)
        if name=='cast_absorbed_spell':
            cid=getattr(source,'rule_state',{}).get('absorbed_spell_id')
            return self._cast_spell_split(('cast_fixed_spell',cid,'random'),ctx) if cid else (('batch30_noop',),())
        if name=='cast_deck_spell':
            deck=self.players[owner].deck
            candidates=[i for i,c in enumerate(deck) if self._card_data(c)['type']=='SPELL'
                        and self._card_stat(c,'cost',owner)<=op[1]]
            if not candidates:return ('batch30_noop',),()
            index=self.rng.choice(candidates);card=deck[index]
            if not isinstance(card,Card):card=Card(self._new_id(),card);deck[index]=card
            return self._cast_spell_split(('cast_zone_spell','deck',card.uid,op[2]),ctx)
        if name=='b60_death_missiles':
            return self._split_fixed_summon(('missiles','enemies',6 if self.players[owner].minions_died_turn else 3),ctx)
        if name in ('damage_owner_draw','damage_summon_count','b60_torch','b60_overkill_discount'):
            if not ctx.get('target'):return ('batch30_noop',),()
            state={}
            return ('damage_amount_hit',op,state),(('damage_amount_finish',op,state),)
        if name=='damage_amount_finish':
            original,state=op[1:]
            if not state:return ('batch30_noop',),()
            if original[0]=='damage_owner_draw':
                draw_context=dict(ctx,owner=state['victim_owner'])
                return self._replay_split(('replay_context',(('draw',1),),draw_context),ctx)
            if original[0]=='damage_summon_count':
                count=min(state['dealt'],max(0,7-len(self.players[owner].board)))
                if count:return self._split_fixed_summon(('summon',original[2],count),ctx)
                return ('batch30_noop',),()
            return ('damage_excess_reward',original[0],state['excess']),()
        if name in ('damage_add_if_dead','damage_draw_if_dead','damage_draw_if_alive','damage_resummon',
                    'damage_buff_if_dead','damage_heal_enemy_if_dead'):
            if not ctx.get('target'):return ('batch30_noop',),()
            state={}
            return ('damage_outcome_hit',op,state),(('damage_outcome_finish',op,state),)
        if name=='damage_outcome_finish':
            original,state=op[1:];kind=original[0]
            if not state or state['dead']!=(kind!='damage_draw_if_alive'):
                return ('batch30_noop',),()
            if kind.startswith('damage_draw_'):
                result=('draw',original[2] if len(original)>2 else 1)
            elif kind=='damage_add_if_dead':result=('add',original[2],1)
            elif kind=='damage_resummon':result=('summon',state['card_id'],1)
            elif kind=='damage_buff_if_dead':result=('buff_random_friendly',original[2],original[3])
            else:result=('heal_enemy_hero',original[2])
            return self._split_fixed_summon(result,ctx)
        if name=='shadow_rounds':
            return ('damage',2),(('shadow_rounds_continue',ctx.get('target',0)),)
        if name=='shadow_rounds_continue':
            if not any(r['entity'].uid==op[1] for p in self.players for r in p.death_records):
                return ('batch30_noop',),()
            op=('cast_fixed_spell','JAIL_515','enemies');name=op[0]
        if name=='archmage_cast':
            records=self.players[owner].death_records
            count=sum(self.cards[r['card_id']]['name']=='Captured Archmage' and
                      (source is None or r['entity'].uid!=source.uid) for r in records)
            if count<4:return ('batch30_noop',),()
            op=('cast_fixed_spell',op[1],'enemies');name=op[0]
        if name=='combo_cast_fixed_spell':
            if not ctx.get('combo'):return ('batch30_noop',),()
            op=('cast_fixed_spell',)+op[1:];name=op[0]
        if name not in ('cast_fixed_spell','cast_physical_spell','cast_zone_spell'):return None
        depth=ctx.get('internal_cast_depth',0)+1
        if depth>256:raise UnsupportedCard('Internal cast chain exceeds verified depth')
        card=None;zone=None;hand_center=False
        if name=='cast_zone_spell':
            zone_name,uid,policy=op[1:]
            if zone_name not in ('hand','deck'):raise ValueError('Unknown internal spell zone')
            zone=getattr(self.players[owner],zone_name)
            card=next((c for c in zone if isinstance(c,Card) and c.uid==uid),None)
            if card is None:return ('batch30_noop',),()
            cid=card.card_id
            hand_center=(zone_name=='hand' and len(zone)%2==1 and zone[len(zone)//2] is card)
        elif name=='cast_physical_spell':
            card,policy=op[1:]
            if not isinstance(card,Card):raise ValueError('Internal cast requires a physical Card')
            if any(card is c for p in self.players for c in p.hand+p.deck):
                raise UnsupportedCard('Use zone casting to consume a card still in hand or deck')
            cid=card.card_id
        else:cid,policy=op[1:]
        if not self._supports_internal_spell(cid,owner):
            raise UnsupportedCard('Internal spell not admitted: '+str(cid))
        if policy not in ('random','enemies','prefer_enemies','prefer_source','prefer_selected','selected'):raise ValueError('Unknown internal target policy')
        # Consumption is not drawing, discarding, paying for, or playing a card.
        # Keep the actual object so held upgrades, origin and enchantments survive.
        if zone is not None:
            zone.remove(card)
            self._refresh_auras()
        mode,operations,branch=self._internal_spell_branch(cid,owner)
        crafted=self._crafted_rule(card)
        if crafted:mode,operations=crafted
        if cid=='SCH_521':mode='minion' if owner==self.current and ctx.get('combo',self.players[owner].cards_played>0) else 'damaged_minion'
        target_source=ctx.get('horror_target_source')
        targets=self._targets_for(target_source if target_source=='DAL_431t' else cid,owner,mode)
        if policy in ('enemies','prefer_enemies'):
            enemy_targets=[] if mode=='historical_copy_hand_minion' else [uid for uid in targets if uid==0 or
                     ((-uid-1 if uid<0 else self._find(uid).owner)!=owner)]
            if enemy_targets or policy=='enemies':targets=enemy_targets
        if not targets:
            return ('internal_spell_fizzle',cid),()
        preferred=getattr(source,'uid',None)
        if policy=='selected':
            target=ctx.get('target',0)
            if mode=='none' or (mode is None and RULES[cid][0]=='none'):target=0
            if target not in targets:return ('internal_spell_fizzle',cid),()
        elif policy=='prefer_selected' and ctx.get('target',0) in targets:target=ctx.get('target',0)
        elif policy=='prefer_source' and preferred in targets:target=preferred
        else:target=targets[0] if len(targets)==1 else self.rng.choice(targets)
        if card is None:card=Card(self._new_id(),cid)
        # Off-turn casts refer to the owner's just-finished turn, whose
        # played-school set is rolled into previous_schools at their next start.
        history=(self.players[owner].previous_schools if owner==self.current
                 else self.players[owner].played_schools)
        kindred=bool(self.cards[cid].get('spellSchool') in history)
        # Preserve the initiating play's snapshot across interrupted sequences;
        # the root card may already have been counted while its frame waits.
        combo=(owner==self.current and bool(ctx.get('combo',self.players[owner].cards_played>0)))
        context=dict(owner=owner,source=None,target=target,card_id=cid,spell=True,
                     bonus=self._spell_damage(owner,cid,card),
                     lifesteal='LIFESTEAL' in self.cards[cid].get('mechanics',()),
                     physical_card=card,paid_cost=0,combo=combo,outcast=False,kindred=kindred,hand_center=hand_center,
                     caster_uid=preferred,internal_cast_depth=depth,automatic_choices=True,
                     choose_one_branch=branch)
        from .kindred import consume_repetition
        context['kindred_repeats']=consume_repetition(self,owner,cid,kindred)
        from .historical_utility_spells import conductivity_program
        operations=conductivity_program(self,operations,context)
        context['stormwind_spell_damage_state']=dict(seen=False)
        body=('replay_context',deepcopy(operations),context)
        other_repeat=getattr(self.players[owner],'historical_brukan_spells_twice',False) or (self.cards[cid].get('spellSchool')=='ARCANE' and self._active('RLK_541',owner)) or bool(getattr(card,'rule_state',{}).get('repeat_spell')) or (self._card_stat(card,'cost',owner)<=2 and self._active('VAC_507',owner)) or (self._card_stat(card,'cost',owner)==1 and self._active('TLC_836',owner))
        other_repeat=self._azure_repeats_spell(owner,cid,other_repeat=other_repeat) or other_repeat
        if self._colossal_repeats_spell(owner,cid,other_repeat=other_repeat) or other_repeat:
            body=('repeat_spell_effects',tuple(operations),context,2)
        return ('internal_spell_begin',context),(body,('internal_spell_complete',context))

    def _internal_spell_branch(self,cid,owner):
        branches=CHOICES.get(cid)
        if not branches:return None,RULES[cid][1],None
        from .historical_combined_choices import combined,consume
        if cid not in ('WORK_025','VAC_907') and combined(self,owner):
            modes={mode for _,mode,_ in branches if mode!='none'}
            if cid=='EDR_813' and self.players[owner].corpses<2:modes=set()
            if len(modes)>1:raise UnsupportedCard('Combined internal spell has incompatible target modes')
            mode=next(iter(modes),'none')
            operations=[op for _,_,ops in branches for op in ops]
            if cid=='CORE_EX1_154':operations=[('damage',4),('draw',1)]
            elif cid=='CORE_EX1_160':operations=[('summon','EX1_160t',1),('board_buff',1,1)]
            elif cid=='YOD_001':operations=[('add','YOD_001ts',1),('draw',1),('summon','YOD_001t',1)]
            consume(self,owner)
            return mode,operations,-1
        # Select the branch first, then find its targets; never bias the branch
        # distribution by the number of targets or silently switch a failed branch.
        index=0 if len(branches)==1 else self.rng.randrange(len(branches))
        _,mode,operations=branches[index]
        return mode,operations,index

    def _cast_spell_effect(self,op,ctx):
        name=op[0]
        if name=='schedule_stored_payload':
            token=ctx.get('physical_card');card=getattr(token,'stored_spell',None)
            turns=getattr(token,'aura_duration',None)
            if card is None or type(turns) is not int or turns<1:
                raise UnsupportedCard('Stored Aura spell requires its spell payload and duration')
            turns+=getattr(token,'rule_state',{}).get('aura_duration_delta',0)
            self._schedule_turn_effect(ctx['owner'],'end',0,turns,(('cast_stored_spell','random'),),
                                       source_card_id=ctx['card_id'],stored_card=card)
            self._log('spell_aura_created',player=ctx['owner'],card=card.card_id,turns=turns)
            return True
        if name=='next_spells_twice':
            player=self.players[ctx['owner']]
            player.spell_repeat_charges=max(player.spell_repeat_charges,op[1])
            return True
        if name=='double_played_minion':
            uid=ctx.get('event',{}).get('source')
            target=next((m for m in self.players[ctx['owner']].minions if m.uid==uid and m.health>0),None)
            if target is not None:
                # Stat doubling adds the current values as a buff; wounds remain.
                self._buff(target,target.attack,target.health)
            return True
        if name=='spell_repeat_begin':
            if self._spell_repeat_depth>=256:raise UnsupportedCard('Spell repetition nesting exceeds verified depth')
            self._spell_repeat_depth+=1
            self._trace_phase('spell_repeat_begin',depth=self._spell_repeat_depth)
            return True
        if name=='spell_repeat_end':
            if self._spell_repeat_depth<=0:raise UnsupportedCard('Unbalanced spell repetition frame')
            self._spell_repeat_depth-=1
            self._trace_phase('spell_repeat_end',depth=self._spell_repeat_depth)
            return True
        if name=='choose_absorb_spell':
            owner=ctx['owner'];source=ctx.get('source')
            if source is None:return True
            options=[dict(card_id=c.card_id,uid=c.uid) for c in self.players[owner].hand
                     if self.cards[c.card_id]['type']=='SPELL' and self._cost(c,owner)<=op[1]]
            if options:
                self.pending_choice=dict(kind='absorb_spell',owner=owner,source=source,options=options)
                self.phase='choice'
            return True
        if name=='damage_amount_hit':
            original,state=op[1:];target=ctx['target']
            victim=self.players[-target-1] if target<0 else self._find(target)
            if victim is None:return True
            state['victim_owner']=-target-1 if target<0 else victim.owner
            before=victim.health
            torch=original[0]=='b60_torch'
            amount=self._b60_state(ctx['physical_card']).get('damage',8) if torch else original[1]
            dealt=self._deal_effect(target,amount,dict(ctx,bonus=0) if torch else ctx)
            state['dealt']=dealt;state['excess']=max(0,dealt-before)
            return True
        if name=='damage_excess_reward':
            mode,excess=op[1:];owner=ctx['owner']
            if excess:
                if mode=='b60_torch':self._b60_add_payload(owner,'CATA_585',dict(damage=excess))
                elif self.players[owner].hand:
                    card=self.rng.choice(self.players[owner].hand)
                    card.cost_delta=getattr(card,'cost_delta',0)-excess
            return True
        if name=='damage_outcome_hit':
            original,state=op[1:];target=ctx['target']
            victim=self.players[-target-1] if target<0 else self._find(target)
            if victim is None:return True
            state['card_id']=getattr(victim,'card_id',None)
            self._deal_effect(target,original[1],ctx)
            # Preserve the existing immediate damage outcome while moving the
            # follow-up after the scheduler's child/death/choice checkpoint.
            state['dead']=victim.health<=0
            return True
        if name=='heal_enemy_hero':
            self._heal(self.hero_id(1-ctx['owner']),op[1],healer=ctx['owner'],spell=ctx.get('spell',False));return True
        if name=='internal_spell_fizzle':
            self._log('spell_fizzle',player=ctx['owner'],card=op[1]);return True
        if name not in ('internal_spell_begin','internal_spell_complete'):return False
        context=op[1];owner=context['owner'];cid=context['card_id']
        if name=='internal_spell_begin':
            from .historical_copy_batches import capture_choose_spell
            capture_choose_spell(self,owner,context['physical_card'],context.get('choose_one_branch'))
            # Keep automatic casts in their own provenance ledger: a minion
            # casting is not the player casting for personal replay pools.
            from .historical_copy_batches import record_spell_cast
            record_spell_cast(self,owner,context['physical_card'],context['target'],automatic=True)
            self.players[owner].spells_cast_turn+=1
            self._log('internal_spell_cast',player=owner,card=cid,target=context['target'],caster=context['caster_uid'],branch=context.get('choose_one_branch'))
        else:
            overload=self.cards[cid].get('overload',0)
            if cid=='YOP_024' or cid=='SCH_612' and context.get('choose_one_branch')==0:overload=0
            from .historical_resource_batches import add_overload
            add_overload(self,owner,overload)
            self._log('internal_spell_complete',player=owner,card=cid)
            from .historical_stormwind_questline_finish import finish as stormwind_finish
            stormwind_finish(self,force=True)
            from .historical_copy_batches import publish_choose_spell
            publish_choose_spell(self,owner,context['physical_card'])
        return True

INTERNAL_OPERATIONS.update({'historical_copy_justice_health'})

INTERNAL_TARGETS.add('historical_copy_madness_target')
INTERNAL_OPERATIONS.update({'historical_copy_bloodfury','historical_copy_dragonfire','historical_copy_madness','historic_temporary_attack'})

INTERNAL_OPERATIONS.add('historical_sleep_candle')

INTERNAL_OPERATIONS.add('historical_copy_unpack_suitcase')

INTERNAL_OPERATIONS.add('historical_copy_tnt_zone')

INTERNAL_OPERATIONS.add('historical_copy_epoch_shuffle')

INTERNAL_TARGETS.add('historical_copy_passions_target')
INTERNAL_OPERATIONS.update({'historical_copy_passions','historical_copy_amulet_critter','historical_copy_amulet_discount','historical_copy_phony_tracking','historical_copy_phony_mobility','historical_copy_cheese','historic_board_freeze','historical_copy_target_delivery','historical_copy_bob_coins','historical_copy_bob_triple','historical_copy_plunder_take','historical_copy_plunder_ship','refresh_mana'})

INTERNAL_OPERATIONS.update({'historical_potion_freeze','historical_potion_wool','historical_resurrection_pick'})

# Authored historical outcome programs share the existing internal cast engine.
from .historical_internal_spell_ops import IMPLEMENTED_OPERATIONS as HISTORICAL_IMPLEMENTED_OPERATIONS
INTERNAL_OPERATIONS.update(HISTORICAL_IMPLEMENTED_OPERATIONS)

INTERNAL_TARGETS.add('historical_friendly_mech')


INTERNAL_TARGETS.add('historical_friendly_shield')

INTERNAL_TARGETS.add('historical_damaged_character')

INTERNAL_OPERATIONS.update(('historical_utility_inner_rage', 'destroy', 'damage_own_hero', 'refresh_mana', 'historical_damage_then', 'historical_copy_lunar_eclipse', 'historic_opponent_draw', 'freeze_enemies', 'historical_copy_target_delivery', 'heal_own_hero', 'historical_utility_ice_lance', 'historical_utility_shadowstep', 'historical_utility_vampiric_blood', 'historical_utility_howling_blast', 'historical_utility_vanish', 'historical_utility_vanish_uid'))

INTERNAL_OPERATIONS.update(('historical_sleep_repeat_area', 'historical_utility_blood_boil', 'historical_utility_boil_tick', 'historical_utility_skull_tick', 'historical_utility_refresh_all'))

INTERNAL_OPERATIONS.update(('historical_utility_paths', 'historical_utility_ice_block', 'historical_utility_plague', 'historical_utility_plague_again'))

INTERNAL_OPERATIONS.update(('historical_utility_frost_hand_copies', 'historical_utility_metamorphosis', 'historical_utility_attack_secret'))

INTERNAL_OPERATIONS.update(('historical_utility_soul_mirror', 'historical_utility_mirror_copy', 'historical_utility_mirror_attacks', 'historical_utility_mirror_attack', 'historical_utility_mirror_resolve'))

INTERNAL_OPERATIONS.update(("forge_sidequest","forge_zombeast_plain"))

INTERNAL_OPERATIONS.update(('historical_eudora_start','historical_eudora_reward'))

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|set(('historical_tour_begin','historical_tour_generate','historical_tour_mind_control','historical_tour_swipe','historical_tour_shadowflame','historical_tour_brawl','historical_tour_mortal','historical_tour_eviscerate','historical_copy_shadow_madness'))

INTERNAL_TARGETS=INTERNAL_TARGETS|{'historical_copy_shadow_madness_target'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_elise_shuffle','historical_elise_open'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|set(('historical_ungoro_mimic','historical_ungoro_scales','historical_ungoro_envenom','historical_ungoro_spore','historical_ungoro_reflection','historical_ungoro_genesis','historical_ungoro_echo','historical_ungoro_cleave'))

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|set(('historical_ungoro_mist','historical_ungoro_mist_destroy','historical_ungoro_explore','historical_ungoro_dinomancy','historical_ungoro_feeding'))

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_ungoro_stampede','historical_ungoro_mana_bind'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_ungoro_living','historical_ungoro_living_crystals'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_zola_golden'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_scythe_discover'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_unsleep_copy','historical_utility_ramming_speed'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_boom_squad'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_forbidden_words'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_dark_skies','historical_utility_dark_skies_hit'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_plot_twist','historical_utility_plot_shuffle'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_repeat_brew'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'held_scheme_area'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_virnaal'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_crackle','historical_utility_primal_fusion','historical_utility_earthen_might','historical_utility_potion_illusion'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_transform_board'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_healing_wave','historical_utility_reincarnate','historical_utility_reincarnate_summon'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_landslide'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_rockbiter','historical_utility_elemental_destruction','historical_utility_lightning_breath'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_vivid_spores','historical_utility_devolving_missiles','historical_utility_devolving_hit'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_elementary_reaction'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_runic','historical_utility_runic_summon'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_charged_call'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_sapphire_copy'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_moment_discovery'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_brukan'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_quest_accepted'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_zephrys_wish'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_ramp_excess'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'historical_utility_overdraft'}

INTERNAL_TARGETS=INTERNAL_TARGETS|{'historical_friendly_demon'}

# Shared native handlers also execute for detached pack/replay spell casts.
INTERNAL_TARGETS.update({'location','combo_character'})
INTERNAL_OPERATIONS.update({'temporary_control','entity_tribute','generation_if_corpses',
 'generation_damage_branch','generation_hero_attack_summons','generation_refresh_offer',
 'generation_fill_health_hand','generation_reopen_attach','map_discover','mountain_start',
 'endtime_start','forbidden_start','colossus_start','equilibrium_start','foodchain_start'})
# These physical spells have no immediate effect when cast without held setup.
INTERNAL_SPELLS=set(INTERNAL_SPELLS)|{'CATA_EVENT_110','CORE_RLK_567'}

INTERNAL_OPERATIONS.add('combo_damage')

# Original Holy spell printings reuse their native attack/silence/damage handlers.
INTERNAL_OPERATIONS.update({'historical_utility_wish_attack','historic_board_silence','historical_utility_lightbomb'})

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'empty_crystals'}

INTERNAL_OPERATIONS=INTERNAL_OPERATIONS|{'shadow_rounds'}

INTERNAL_OPERATIONS.add('choose_fixed_summon')

INTERNAL_OPERATIONS.update({'historical_utility_pool_sheep','historical_utility_pool_shattering','historical_utility_pool_shatter','historical_utility_pool_flamecannon','historical_utility_pool_phaser','historical_utility_pool_dormant'})

INTERNAL_TARGETS.add('historical_frozen_minion')

from .historical_pool_spells import TOKEN_RULES as POOL_SPELL_RULES
INTERNAL_OPERATIONS.update(op[0] for _,ops in POOL_SPELL_RULES.values() for op in ops)

INTERNAL_OPERATIONS.add('historical_ritual_jade')

from .historical_pool_state import TOKEN_RULES as POOL_STATE_RULES
INTERNAL_OPERATIONS.update(op[0] for _,ops in POOL_STATE_RULES.values() for op in ops)

INTERNAL_OPERATIONS.update({'historical_utility_pool_supernova','historical_utility_pool_huddle','historical_utility_pool_ray'})

INTERNAL_OPERATIONS.update({'historical_utility_pool_flow_target','historical_utility_pool_waves','historical_utility_pool_waves_finish'})

INTERNAL_OPERATIONS.update({'historical_secret_v2_mirror','historical_secret_v2_vaporize','historical_secret_v2_portal'})

INTERNAL_OPERATIONS.add('historical_utility_pool_finale')

INTERNAL_OPERATIONS.update({'historical_utility_pool_wildfire','historical_utility_pool_siphon','historical_utility_pool_blast_wave'})

INTERNAL_OPERATIONS.update({'historical_utility_pool_blast_damage','historical_utility_pool_blast_rewards'})

INTERNAL_OPERATIONS.update({'historical_utility_pool_results','historical_utility_pool_conjure'})

INTERNAL_OPERATIONS.update({'historical_secret_v2_bender_summon','historical_secret_v2_death','historical_secret_v2_effigy'})

INTERNAL_OPERATIONS.update({'historical_utility_pool_ignite','historical_utility_pool_combustion_target','historical_utility_pool_tsunami','historical_utility_pool_water_summon'})

INTERNAL_OPERATIONS.update({'historical_utility_pool_creation','historical_utility_pool_ring'})

INTERNAL_OPERATIONS.update({'historical_utility_pool_combustion','historical_utility_pool_rolling','historical_utility_pool_overflow','historical_utility_pool_remnant'})

INTERNAL_OPERATIONS.update({'historical_secret_v2_archive_'+name for name in ('cache','companion','shield','repent','justice','destroy','hit','copy','turn')})

INTERNAL_OPERATIONS.update({'historical_secret_v2_archive_'+name for name in ('evasion','avenge','dispatch','death','return','redemption','plagiarize_turn','plagiarize_cards')})

INTERNAL_OPERATIONS.update({'historical_secret_v2_archive_ice_return','historical_secret_v2_archive_redirect'})

INTERNAL_OPERATIONS.add('historical_secret_v2_archive_banana')

INTERNAL_OPERATIONS.update({'historical_utility_mage_deck_'+name for name in ('tower','tower_cast','fury','sea','burndown','lunacy','moonlit','sea_summon','ignite_hand')})

INTERNAL_OPERATIONS.update({'historical_utility_mage_offer_'+name for name in ('font','pocket','gift','pocket_open','scroll_tick')})

INTERNAL_OPERATIONS.update({'historical_utility_mage_quest_'+name for name in ('sidequest','gambit','allies_reset','dawngrasp','school_offer')})

INTERNAL_OPERATIONS.update({'historical_utility_pool_rune','historical_utility_pool_rune_step','historical_secret_v2_archive_yogg_replace'})

INTERNAL_OPERATIONS.add('batch30_noop')
INTERNAL_OPERATIONS.update({'historical_utility_nature_'+name for name in ('mulch','revive','spikeshell','opponent_crystals','gloop','germination','crystalsong','corrosive','embiggen','dreams','seeds','woods','recycle','toxic','infest','compost','trail','trail_begin','draw_sequence','draw_finish','heal_all','trail_end','bear_tick')})

INTERNAL_OPERATIONS.update({'historic_full_heal_board','historic_full_heal_heroes'})

INTERNAL_OPERATIONS.update({'historical_utility_archive_piercing', 'historical_utility_archive_weapons_project', 'historical_utility_archive_hit_follow', 'historical_utility_archive_kill_uid', 'historical_utility_archive_defrost', 'historical_utility_archive_coliseum', 'historical_utility_archive_divine_favor', 'historical_utility_archive_conceal', 'historical_utility_archive_devour', 'historical_utility_archive_lock_load', 'historical_utility_archive_naaru', 'historical_utility_archive_graveyard', 'historical_utility_archive_corruption_expire', 'historical_utility_archive_discount_hand_spells', 'historical_utility_archive_hunting_party', 'historical_utility_archive_arsenal', 'historical_utility_archive_free_admission', 'historical_utility_archive_health_one', 'historical_utility_archive_opponent_cards', 'historical_utility_archive_sweep_reward', 'historical_utility_archive_reborn_all', 'historical_utility_archive_hounds', 'historical_utility_archive_infinite_breath', 'historical_utility_archive_draw_finish', 'historical_utility_archive_petting', 'historical_utility_archive_circle', 'historical_utility_archive_escape', 'historical_utility_archive_hit_capture', 'historical_utility_archive_bless', 'historical_utility_archive_board_stats', 'historical_utility_archive_hand_copy', 'historical_utility_archive_repeat_hand', 'historical_utility_archive_sweep_hit', 'historical_utility_archive_bulk_up', 'historical_utility_archive_expire_uid', 'historical_utility_archive_neighbors', 'historical_utility_archive_snowed', 'historical_utility_archive_fresh_summon', 'historical_utility_archive_sermon', 'historical_utility_archive_altar', 'historical_utility_archive_swap_target', 'historical_utility_archive_glowflies', 'historical_utility_archive_ectomancy', 'historical_utility_archive_board_death', 'historical_utility_archive_group_summon', 'historical_utility_archive_chaos', 'historical_utility_archive_draw_state', 'historical_utility_archive_snack', 'historical_utility_archive_divine_spirit', 'historical_utility_archive_slope', 'historical_utility_archive_howl', 'historical_utility_archive_blade_dance', 'historical_utility_archive_corruption', 'historical_utility_archive_secret_plan', 'historical_utility_archive_jettison', 'historical_utility_archive_infiltrate', 'historical_utility_archive_healthstone', 'historical_utility_archive_pursuit', 'historical_utility_archive_mind_vision', 'historical_utility_archive_cloak', 'historical_utility_archive_admission_finish', 'historical_utility_archive_feast', 'historical_utility_archive_demonfire', 'historical_utility_archive_left_minion', 'historical_utility_archive_after_hit', 'historical_utility_archive_totemic', 'historical_utility_archive_felbolt', 'historical_utility_archive_lose_armor', 'historical_utility_archive_return_card', 'historical_utility_archive_upgrade', 'historical_utility_archive_myra', 'historical_utility_archive_lackey', 'historical_utility_archive_black_hole', 'historical_utility_archive_dragon_shield', 'historical_utility_archive_corpsicle', 'historical_utility_archive_fishes', 'historical_utility_archive_silence_enemies', 'historical_utility_archive_cannons', 'historical_utility_archive_molten_breath', 'historical_utility_archive_attack_group', 'historical_utility_archive_destroy_sample', 'historical_utility_archive_opponent_summon', 'historical_utility_archive_resummon', 'historical_utility_archive_immune', 'historical_utility_archive_expire_target', 'historical_utility_archive_revenge', 'historical_utility_archive_sweep_finish', 'historical_utility_archive_copy_snapshot', 'historical_utility_archive_fill_undead', 'historical_utility_archive_nether_breath', 'historical_utility_archive_omega'})
INTERNAL_TARGETS.update({"historic_demon","historic_friendly_demon","friendly_deathrattle"})

INTERNAL_OPERATIONS.update(['area_damage', 'armor', 'board_buff', 'buff', 'damage', 'destroy', 'destroy_all_minions', 'destroy_crystals', 'destroy_random_enemy', 'discard', 'draw', 'draw_until', 'freeze', 'generate_discover', 'generate_random', 'heal_own_hero', 'hero_attack', 'historic_board_buff', 'historic_board_keyword', 'historic_board_silence', 'historical_batch_trigger_target_death', 'historical_copy_healing_damage_turn', 'historical_copy_recruit_one', 'historical_copy_target_delivery', 'historical_damage_then', 'historical_draw_batch', 'historical_hand_discard_select', 'historical_if_combo', 'historical_utility_archive_coliseum', 'historical_utility_archive_destroy_sample', 'historical_utility_archive_lock_load', 'historical_utility_archive_neighbors', 'historical_utility_archive_opponent_cards', 'historical_utility_continuation_adjacent_damage', 'historical_utility_continuation_battle_rage_copies', 'historical_utility_continuation_buff_enemy_count', 'historical_utility_continuation_copy_target', 'historical_utility_continuation_crushing_walls', 'historical_utility_continuation_deck_buff', 'historical_utility_continuation_demonheart', 'historical_utility_continuation_destroy_low', 'historical_utility_continuation_discount_random_spell', 'historical_utility_continuation_doom', 'historical_utility_continuation_draw_if_beast', 'historical_utility_continuation_enemy_attack_one', 'historical_utility_continuation_enemy_deck_copies', 'historical_utility_continuation_enemy_hand_discount', 'historical_utility_continuation_fel_gorger_damage', 'historical_utility_continuation_flurry', 'historical_utility_continuation_forbidden_heal', 'historical_utility_continuation_gift', 'historical_utility_continuation_give_target', 'historical_utility_continuation_halve_decks', 'historical_utility_continuation_harbor', 'historical_utility_continuation_heal_friends', 'historical_utility_continuation_malt', 'historical_utility_continuation_odd_destroy', 'historical_utility_continuation_outcast_opponent_draw', 'historical_utility_continuation_overwhelm', 'historical_utility_continuation_pilfer', 'historical_utility_continuation_random_attack', 'historical_utility_continuation_random_buff', 'historical_utility_continuation_random_hand_beast', 'historical_utility_continuation_reckless', 'historical_utility_continuation_reserved', 'historical_utility_continuation_shuffle_hand_copies', 'historical_utility_continuation_top_demon', 'historical_utility_continuation_trigger_all', 'keyword', 'missiles', 'on_draw_shuffle', 'schedule_turn_effect', 'set_target_stats', 'silence', 'temporary_next_discount', 'transform', 'weapon_buff'])
INTERNAL_TARGETS.add("historic_undead")

INTERNAL_OPERATIONS.update(['historical_copy_recruit_one', 'historical_play_zone_offer', 'historical_resurrection_pick', 'historical_utility_physical_darkest', 'historical_utility_physical_deck_copy', 'historical_utility_physical_draw_conditional', 'historical_utility_physical_draw_finish', 'historical_utility_physical_gallery', 'historical_utility_physical_kill_group', 'historical_utility_physical_lens', 'historical_utility_physical_lens_finish', 'historical_utility_physical_mindgames', 'historical_utility_physical_nightmare', 'historical_utility_physical_opponent_hand', 'historical_utility_physical_small_beasts', 'historical_utility_physical_summon_copy', 'historical_utility_physical_whelps', 'schedule_turn_effect'])

INTERNAL_OPERATIONS.update(['armor', 'board_buff', 'buff', 'damage', 'generate_discover', 'historical_utility_archive_health_one', 'historical_utility_repeat_batch_after', 'historical_utility_repeat_batch_demon_discount', 'historical_utility_repeat_batch_hit', 'historical_utility_repeat_batch_launch_discount', 'historical_utility_repeat_batch_start', 'historical_utility_repeat_batch_step', 'next_discount', 'tribe_board_buff'])

INTERNAL_OPERATIONS.update(['board_buff', 'buff', 'damage', 'generate_discover', 'heal', 'historical_damage_then', 'historical_event_spell_damage', 'historical_utility_finish_batch_damage_group', 'historical_utility_finish_batch_defense', 'historical_utility_finish_batch_duelists', 'historical_utility_finish_batch_forbidden_minion', 'historical_utility_finish_batch_four_buffs', 'historical_utility_finish_batch_heal_uid', 'historical_utility_finish_batch_kill_uid', 'historical_utility_finish_batch_lightwarden', 'historical_utility_finish_batch_pawns', 'historical_utility_finish_batch_pouch', 'historical_utility_finish_batch_quasar', 'historical_utility_finish_batch_scheduled_heal', 'historical_utility_finish_batch_ship_damage', 'historical_utility_finish_batch_ship_destroy', 'historical_utility_finish_batch_ship_draw', 'historical_utility_finish_batch_survival', 'historical_utility_finish_batch_tentacles', 'schedule_turn_effect', 'summon', 'temporary_keyword_target'])

INTERNAL_OPERATIONS.update(['add', 'buff', 'historical_event_spell_damage', 'historical_utility_mount_batch_attach', 'historical_utility_mount_batch_delayed_dreadsteed', 'historical_utility_mount_batch_recruit', 'historical_utility_mount_batch_resummon_one_health', 'keyword', 'summon'])

INTERNAL_TARGETS.add("historic_beast")

INTERNAL_OPERATIONS.update(['damage_own_hero', 'historical_utility_history_batch_death_hand', 'historical_utility_history_batch_offer', 'historical_utility_history_batch_resurrect', 'historical_utility_history_batch_summon'])

INTERNAL_OPERATIONS.update(['damage', 'historical_utility_archive_destroy_sample', 'historical_utility_stone_finish_diamond', 'historical_utility_stone_finish_scheme', 'historical_utility_stone_finish_tick', 'summon'])

INTERNAL_OPERATIONS.update(['buff', 'historical_utility_zone_spell_council', 'historical_utility_zone_spell_demonic_project', 'historical_utility_zone_spell_deviate', 'historical_utility_zone_spell_entomb', 'historical_utility_zone_spell_espionage', 'historical_utility_zone_spell_evolve_copy', 'historical_utility_zone_spell_frenzy', 'historical_utility_zone_spell_glide', 'historical_utility_zone_spell_parrrley', 'historical_utility_zone_spell_revolve', 'historical_utility_zone_spell_scream', 'historical_utility_zone_spell_shuffle_hand', 'historical_utility_zone_spell_transform_group', 'historical_utility_zone_spell_transform_uid'])

INTERNAL_OPERATIONS.update(['historical_family_basic_totem', 'historical_utility_damage_finish_after', 'historical_utility_damage_finish_area', 'historical_utility_damage_finish_area_after', 'historical_utility_damage_finish_area_hit', 'historical_utility_damage_finish_bola', 'historical_utility_damage_finish_capture', 'historical_utility_damage_finish_hand_gain', 'historical_utility_damage_finish_hit', 'historical_utility_damage_finish_implosion'])

INTERNAL_OPERATIONS.update(['buff', 'force_recruit_pair', 'historical_utility_combat_spell_attack', 'historical_utility_combat_spell_duel', 'historical_utility_combat_spell_group', 'historical_utility_combat_spell_hysteria', 'historical_utility_combat_spell_kill', 'historical_utility_combat_spell_recover', 'historical_utility_combat_spell_recruit', 'historical_utility_combat_spell_return', 'historical_utility_combat_spell_start', 'historical_utility_combat_spell_summon'])

INTERNAL_OPERATIONS.update({'historical_utility_sidequest_batch_start','historical_utility_sidequest_batch_sanctuary'})

INTERNAL_OPERATIONS.update(['buff', 'historical_utility_aura_finish_attach_attack', 'historical_utility_aura_finish_aura', 'historical_utility_aura_finish_curse', 'historical_utility_aura_finish_expire'])

INTERNAL_OPERATIONS.update(['add', 'buff', 'damage', 'destroy', 'generate_random', 'historical_draw_batch', 'historical_utility_condition_batch_aimed', 'historical_utility_condition_batch_barricade', 'historical_utility_condition_batch_breach', 'historical_utility_condition_batch_breach_repeat', 'historical_utility_condition_batch_clarity', 'historical_utility_condition_batch_commence', 'historical_utility_condition_batch_divinity', 'historical_utility_condition_batch_faith', 'historical_utility_condition_batch_faith_one', 'historical_utility_condition_batch_felosophy', 'historical_utility_condition_batch_fiend', 'historical_utility_condition_batch_heights', 'historical_utility_condition_batch_hero_health', 'historical_utility_condition_batch_luminance', 'historical_utility_condition_batch_omen', 'historical_utility_condition_batch_return', 'historical_utility_condition_batch_ritual', 'historical_utility_condition_batch_shield_recruit', 'historical_utility_repeat_batch_launch_discount', 'insert_fixed', 'keyword', 'schedule_turn_effect', 'summon'])

INTERNAL_OPERATIONS.update(['damage', 'generate_discover', 'generate_random', 'historical_if_combo', 'historical_offer_open', 'historical_offer_pair', 'historical_prime_part', 'historical_utility_archive_opponent_cards', 'historical_utility_generation_finish_metal', 'historical_utility_generation_finish_repeat_ray', 'on_draw_shuffle', 'summon', 'summon_fixed_random'])

INTERNAL_OPERATIONS.update(['historical_draw_batch', 'historical_utility_deck_finish_draw_deaths', 'historical_utility_deck_finish_draw_uid', 'historical_utility_deck_finish_guess', 'historical_utility_deck_finish_guess_offer', 'historical_utility_deck_finish_offer', 'historical_utility_deck_finish_publish_all', 'historical_utility_deck_finish_shuffle_copies', 'historical_utility_deck_finish_trigger_card', 'historical_utility_deck_finish_trigger_state'])

INTERNAL_OPERATIONS.update(['area_damage', 'damage_enemy_hero', 'gain_corpses', 'historical_family_basic_totem', 'historical_if_combo', 'historical_utility_delayed_finish_agony', 'historical_utility_delayed_finish_attach', 'historical_utility_delayed_finish_control', 'historical_utility_delayed_finish_copy', 'historical_utility_delayed_finish_curse_enemy', 'historical_utility_delayed_finish_death_roll', 'historical_utility_delayed_finish_embrace', 'historical_utility_delayed_finish_resummon_twice', 'historical_utility_delayed_finish_sensory', 'historical_utility_delayed_finish_sensory_after', 'historical_utility_delayed_finish_summon_card', 'historical_utility_delayed_finish_talismans', 'historical_utility_delayed_finish_voodoo', 'on_draw_shuffle', 'summon'])

INTERNAL_OPERATIONS.add('historical_utility_delayed_finish_held_curse_damage')

INTERNAL_OPERATIONS.add('historical_utility_repeat_batch_zerg_buff')

INTERNAL_OPERATIONS.update(['add', 'armor', 'buff', 'damage', 'destroy', 'equip', 'historical_utility_identified_adjacent', 'historical_utility_identified_hope', 'historical_utility_identified_recruit', 'historical_utility_identified_return', 'historical_utility_identified_shadow', 'historical_utility_identified_turncoat', 'historical_utility_trade_finish_amulet', 'historical_utility_trade_finish_biscuit', 'historical_utility_trade_finish_shipment', 'keyword', 'summon'])

INTERNAL_TARGETS.update({'historical_finish_attack_four', 'historical_finish_coerce', 'historical_finish_friendly_location'})
INTERNAL_OPERATIONS.update(['buff', 'companion_random_series', 'damage', 'destroy', 'generate_discover', 'heal_own_hero', 'historical_copy_literal_family', 'historical_draw_batch', 'historical_utility_damage_finish_hit', 'historical_utility_repeat_batch_start', 'historical_utility_summon_finish_banana', 'historical_utility_summon_finish_banelings', 'historical_utility_summon_finish_cannon', 'historical_utility_summon_finish_companions', 'historical_utility_summon_finish_consume', 'historical_utility_summon_finish_entree', 'historical_utility_summon_finish_explode', 'historical_utility_summon_finish_forbid', 'historical_utility_summon_finish_meeting', 'historical_utility_summon_finish_orbital_discover', 'historical_utility_summon_finish_orbital_reborn', 'historical_utility_summon_finish_rat', 'historical_utility_summon_finish_scheme', 'historical_utility_summon_finish_siren', 'historical_utility_summon_finish_time_out', 'historical_utility_summon_finish_zerg_rush', 'keyword', 'summon_fixed_random', 'summon_opponent'])

INTERNAL_OPERATIONS.update(['add', 'armor', 'buff', 'hero_attack', 'historical_play_zone_offer', 'historical_utility_stormwind_begin', 'historical_utility_stormwind_discount_drawn', 'historical_utility_stormwind_distractor', 'historical_utility_stormwind_gizmo', 'historical_utility_stormwind_gyroblade', 'historical_utility_stormwind_juggernaut', 'historical_utility_stormwind_kurtrus', 'historical_utility_stormwind_seed_reward', 'historical_utility_stormwind_shard', 'historical_utility_stormwind_tamsin', 'historical_utility_stormwind_target_power', 'historical_utility_stormwind_tavish', 'historical_utility_stormwind_upgrade_power', 'historical_utility_stormwind_warrior_weapon', 'historical_utility_stormwind_zero_power', 'insert_fixed', 'keyword', 'open_permanent', 'recruit_bonus'])

INTERNAL_OPERATIONS.update(('historical_utility_final_combat_cleave','historical_utility_final_combat_hero_minions_only','historical_utility_final_combat_hero_cleave'))

# Audited historical spell handlers use the shared automatic spell frame.
# Physical held upgrades, Combo, targets and choice ownership remain handled
# by _cast_spell_split; admission does not change any generation membership.
INTERNAL_OPERATIONS.update(('historical_utility_protect_innocent', 'deck_minions_set_cost', 'historical_copy_enemy_draw', 'historical_batch_sample_damage', 'historical_utility_wish_bloodlust', 'historical_utility_wish_coldblood', 'historical_utility_togwaggle_scheme', 'historical_copy_evolve_target', 'historical_copy_solar_eclipse', 'historical_family_lackeys', 'historical_utility_wish_betrayal', 'historical_utility_wish_soulforest', 'historical_copy_enemy_random_two', 'historical_utility_wish_battlerage', 'historical_utility_wish_explosive', 'historical_utility_wish_flare', 'historical_utility_wish_savagery', 'bounce', 'historical_utility_darkbomb', 'historical_batch_manathirst_damage', 'historical_utility_lackey_discover', 'taunt_hand_buff', 'historical_upgrade_adapt', 'historical_copy_next_payment'))

INTERNAL_OPERATIONS.update(('historical_utility_audit_front','historical_utility_audit_bones','historical_utility_audit_bones_continue','historical_utility_audit_different_types','historical_utility_audit_skirt'))

INTERNAL_OPERATIONS.update(('historical_utility_audit_icecrown','historical_utility_audit_blackrock','historical_utility_audit_brochure_damage'))

INTERNAL_OPERATIONS.update(('historical_utility_audit_doomerang','historical_utility_audit_weapon_hit','historical_utility_audit_weapon_return'))

INTERNAL_OPERATIONS.update(('historical_copy_history_replay','historical_copy_history_card'))

from .historical_obligation_spells import PREFIX as OBLIGATION_PREFIX
INTERNAL_OPERATIONS.update(OBLIGATION_PREFIX+name for name in ('mana_burn','shout','flanking','performers','acrobatics','passage','shadows','shadow_summon','comet','acrobatics_arm','passage_restore','watched_summon','summon_arm'))

INTERNAL_OPERATIONS.update(OBLIGATION_PREFIX+name for name in ('yoink','yoink_used','guidance','guidance_both'))

from .historical_final_spell_roots import PREFIX as FINAL_ROOT_PREFIX
INTERNAL_OPERATIONS.update(FINAL_ROOT_PREFIX+name for name in ('kangor','dwarf','impfestation','dwarf_one','imp_pair','imp_summon','imp_attacks','mech_return','darkness','champions','champion_side'))

# Emerald Portal is also cast by explicit deck/physical spell effects.
INTERNAL_OPERATIONS.add('imbue_portal')
