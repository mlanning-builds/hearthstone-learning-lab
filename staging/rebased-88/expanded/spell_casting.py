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
INTERNAL_TARGETS={'none','character','minion','enemy_minion','friendly_minion',
                  'damaged_minion','undamaged_minion','enemy_character',
                  'friendly_beast','friendly_undead','large_minion','damaged_enemy_minion',
                  'friendly_character','legendary_minion','friendly_wisp','weapon_required',
                  'repeated_enemy_character'}
INTERNAL_OPERATIONS={'forge_sidequest','crafted_spell','counterfeit_jade','counterfeit_potion','counterfeit_resurrect','essence_chain','ruby_sanctum','lost_city_start','slice_replay','request_end_turn','crystal_core','nether_portal','time_warp','aura_random_shield_buff','brox_portal','learned_bulb_cast','herald','herald_hero_lifesteal','companions_replace','companions_random','companions_all','companions_choose','void_soul_cast','damage_add_if_dead','autocast_spend_mana','imbue','rewindgen_budget','rewindgen_holy','rewindgen_sands','generation_summon_attack','mutation_board','mutation_bribe','mutation_anomalize','mutation_life_cycle','stored_slime','stored_resummon','stored_egg','dark_deck_discover','shatter_board_death','shatter_copy_target','shatter_generate_combined','generate_random',
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
                     'follow_attach','outcast_draw','enemy_edges_damage','feast_raptors','kindred_cost_draws',
                     'add_opponent','combo_add','damage_hand_center','on_draw_hurt_owner',
                     'quest_murloc_reward','open_permanent','health_by_relation','schedule_stored_payload','leyline_cast','leyline_upgrade','leyline_choose'}

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

    def _supports_internal_spell(self,cid):
        if cid not in self.cards or self.cards[cid]['type']!='SPELL':return False
        if cid in INTERNAL_SPELLS or cid in CHOICES or cid=='CATA_186t':return True
        definition=RULES.get(cid)
        return (definition is not None and bool(definition[1]) and definition[0] in INTERNAL_TARGETS and
                self._supports_internal_operations(definition[1]))

    def _supports_internal_operations(self,operations):
        for op in operations:
            if op[0]=='schedule_turn_effect':
                if len(op)!=5 or not self._supports_internal_operations(op[4]):return False
            elif op[0]=='when_state':
                if len(op)!=3 or not self._supports_internal_operations((op[2],)):return False
            elif op[0]=='b60_attach':
                if len(op)!=2 or not self._supports_internal_operations((op[1],)):return False
            elif op[0]=='kindred':
                if len(op)!=2 or not self._supports_internal_operations(op[1]):return False
            elif op[0]=='outcast_operation':
                if len(op)!=2 or not self._supports_internal_operations((op[1],)):return False
            elif op[0]=='if_discarded':
                if len(op)!=2 or not self._supports_internal_operations((op[1],)):return False
            elif op[0]=='if_holding':
                if len(op) not in (3,4) or not self._supports_internal_operations(op[2:]):return False
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
            if not self._supports_internal_spell(card.card_id):
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
        if not self._supports_internal_spell(cid):
            raise UnsupportedCard('Internal spell not admitted: '+str(cid))
        if policy not in ('random','enemies','prefer_enemies','prefer_source','selected'):raise ValueError('Unknown internal target policy')
        # Consumption is not drawing, discarding, paying for, or playing a card.
        # Keep the actual object so held upgrades, origin and enchantments survive.
        if zone is not None:
            zone.remove(card)
            self._refresh_auras()
        mode,operations,branch=self._internal_spell_branch(cid,owner)
        crafted=self._crafted_rule(card)
        if crafted:mode,operations=crafted
        targets=self._targets_for(cid,owner,mode)
        if policy in ('enemies','prefer_enemies'):
            enemy_targets=[uid for uid in targets if uid==0 or
                     ((-uid-1 if uid<0 else self._find(uid).owner)!=owner)]
            if enemy_targets or policy=='enemies':targets=enemy_targets
        if not targets:
            return ('internal_spell_fizzle',cid),()
        preferred=getattr(source,'uid',None)
        if policy=='selected':
            target=ctx.get('target',0)
            if mode=='none' or (mode is None and RULES[cid][0]=='none'):target=0
            if target not in targets:return ('internal_spell_fizzle',cid),()
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
                     bonus=self._spell_damage(owner)+getattr(card,'spell_damage_bonus',0),
                     lifesteal='LIFESTEAL' in self.cards[cid].get('mechanics',()),
                     physical_card=card,paid_cost=0,combo=combo,outcast=False,kindred=kindred,hand_center=hand_center,
                     caster_uid=preferred,internal_cast_depth=depth,automatic_choices=True,
                     choose_one_branch=branch)
        from .kindred import consume_repetition
        context['kindred_repeats']=consume_repetition(self,owner,cid,kindred)
        body=('replay_context',deepcopy(operations),context)
        other_repeat=bool(getattr(card,'rule_state',{}).get('repeat_spell')) or (self._card_stat(card,'cost',owner)==1 and self._active('TLC_836',owner))
        other_repeat=self._azure_repeats_spell(owner,cid,other_repeat=other_repeat) or other_repeat
        if self._colossal_repeats_spell(owner,cid,other_repeat=other_repeat) or other_repeat:
            body=('repeat_spell_effects',tuple(operations),context,2)
        return ('internal_spell_begin',context),(body,('internal_spell_complete',context))

    def _internal_spell_branch(self,cid,owner):
        branches=CHOICES.get(cid)
        if not branches:return None,RULES[cid][1],None
        if self._active('CORE_OG_044',owner):
            modes={mode for _,mode,_ in branches if mode!='none'}
            if cid=='EDR_813' and self.players[owner].corpses<2:modes=set()
            if len(modes)>1:raise UnsupportedCard('Combined internal spell has incompatible target modes')
            mode=next(iter(modes),'none')
            operations=[op for _,_,ops in branches for op in ops]
            if cid=='CORE_EX1_154':operations=[('damage',4),('draw',1)]
            elif cid=='CORE_EX1_160':operations=[('summon','EX1_160t',1),('board_buff',1,1)]
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
            self._log('internal_spell_cast',player=owner,card=cid,target=context['target'],caster=context['caster_uid'],branch=context.get('choose_one_branch'))
        else:
            overload=self.cards[cid].get('overload',0)
            self.players[owner].overload_next+=overload
            self.players[owner].overloaded_total+=overload
            self._log('internal_spell_complete',player=owner,card=cid)
        return True
