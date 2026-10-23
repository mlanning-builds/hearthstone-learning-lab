"""Stateless effect execution and ordered dispatch; frames belong to the game."""
from .historical_saidan import add as _saidan_add
from engine.cards import UnsupportedCard
from .pools import require_fixed_cards
from .selectors import has_tribe, has_school


class EffectExecutor:
    __slots__ = ()

    def execute(self,game,op,ctx):
        from .game import Minion
        if game._fire_effect_guard(op,ctx):return
        effect_context=getattr(game,'_active_effect_context',{})
        game._active_effect_context=ctx
        previous=game.pending_choice
        own_healing_frame=not hasattr(game,'_healing_replacement_frame')
        if own_healing_frame:game._healing_replacement_frame=set()
        damage_source=getattr(game,'_damage_origin',None)
        game._damage_origin=ctx.get('source')
        from .death_inheritance import bearer_uses
        tracked=[m for player in game.players for m in player.minions if m.health>0 and
                 (m.card_id=='CATA_185' or m.attached_death_effects and bearer_uses(game,m,'entity_replicate_killer'))]
        ichman_source=ctx.get('source')
        ichman_victims=([m for player in game.players for m in player.minions if m.health>0]
                        if getattr(ichman_source,'rule_state',{}).get('historical_ichman_turn')==game.turn else [])
        try:
            game._dispatch_effect(op,ctx)
            if any(m.health<=0 for m in ichman_victims):
                from .historical_copy_batches import ichman_killed
                ichman_killed(game,ichman_source)
            source=ctx.get('source')
            if source is not None and isinstance(source,Minion):
                for m in tracked:
                    if m.health<=0 and m in game.players[m.owner].board:
                        m.rule_state.setdefault('killed_by_minion',source.uid)
        finally:
            game._active_effect_context=effect_context
            game._damage_origin=damage_source
            if own_healing_frame:del game._healing_replacement_frame
        choice=game.pending_choice
        if choice is not None and choice is not previous:
            # The innermost effect owns its choice. An enclosing automatic
            # spell must not relabel a triggered minion's player choice.
            choice.setdefault('_automatic',bool(ctx.get('automatic_choices',False)))

    def checkpoint(self,game,op,ctx):
        game._effect(op,ctx)
        game._colossal_stat_checkpoint()
        game._champion_checkpoint()
        game._resolve_automatic_choices()

    def dispatch(self,game,op,ctx):
        if op[0].startswith(('inherited_','unreviewed_inherited_')):
            from .death_inheritance import execute
            if execute(game,op,ctx):return
        from .automatic_cards import place_automatic_card
        if place_automatic_card(game,op,ctx):return
        if op[0]=='kindred_twice_next':game.players[ctx['owner']].kindred_twice=True;return
        from .historical_infuse_batches import execute as historical_infuse_effect
        if historical_infuse_effect(game,op,ctx):return
        from .historical_tribal_batches import execute as historical_tribal_batches_effect
        if historical_tribal_batches_effect(game,op,ctx):return
        from .historical_treasure_batches import execute as historical_treasure_batches_effect
        if historical_treasure_batches_effect(game,op,ctx):return
        from .historical_galakrond_batches import execute as historical_galakrond_effect
        if historical_galakrond_effect(game,op,ctx):return
        from .historical_ritual_batches import execute as historical_ritual_effect
        if historical_ritual_effect(game,op,ctx):return
        from .historical_secret_batches import execute as historical_secret_effect
        if historical_secret_effect(game,op,ctx):return
        from .historical_resource_batches import execute as historical_resource_effect
        if historical_resource_effect(game,op,ctx):return
        from .historical_sleep_batches import execute as historical_sleep_effect
        if historical_sleep_effect(game,op,ctx):return
        from .historical_arsenal_batches import execute as historical_arsenal_effect
        if historical_arsenal_effect(game,op,ctx):return
        from .historical_hand_batches import execute as historical_hand_effect
        if historical_hand_effect(game,op,ctx):return
        from .historical_play_batches import execute as historical_play_effect
        if historical_play_effect(game,op,ctx):return
        from .historical_resurrection_batches import execute as historical_resurrection_effect
        if historical_resurrection_effect(game,op,ctx):return
        from .historical_drawn_batches import execute as historical_drawn_effect
        if historical_drawn_effect(game,op,ctx):return
        from .historical_upgrade_batches import execute as historical_upgrade_effect
        if historical_upgrade_effect(game,op,ctx):return
        from .historical_copy_batches import execute as historical_copy_effect
        if historical_copy_effect(game,op,ctx):return
        from .historical_family_batches import execute as historical_family_effect
        if historical_family_effect(game,op,ctx):return
        from .historical_mutation_batches import execute as historical_mutation_effect
        if historical_mutation_effect(game,op,ctx):return
        from .historical_prime_batches import execute as historical_prime_effect
        if historical_prime_effect(game,op,ctx):return
        from .historical_event_batches import execute as historical_event_effect
        if historical_event_effect(game,op,ctx):return
        from .historical_keyword_batches import execute as historical_keyword_effect
        if historical_keyword_effect(game,op,ctx):return
        from .historical_draw_batches import execute as historical_draw_effect
        if historical_draw_effect(game,op,ctx):return
        from .historical_zone_batches import execute as historical_zone_effect
        if historical_zone_effect(game,op,ctx):return
        from .historical_condition_batches import execute as historical_condition_effect
        if historical_condition_effect(game,op,ctx):return
        from .historical_board_primitives import execute as historical_board_effect
        if historical_board_effect(game,op,ctx):return
        if game._finish_effect(op,ctx):return
        if game._historical_conditional_effect(op,ctx):return
        if game._historical_removal_effect(op,ctx):return
        if game._historical_scaling_effect(op,ctx):return
        if game._historical_buff_effect(op,ctx):return
        if game._historical_hand_effect(op,ctx):return
        if game._forge_effect(op,ctx):return
        if game._craft_effect(op,ctx):return
        if game._counterfeit_effect(op,ctx):return
        if game._osk_effect(op,ctx):return
        if game._remaining_setup_effect(op,ctx):return
        if game._investigation_effect(op,ctx):return
        if game._tiny_effect(op,ctx):return
        if game._ruby_effect(op,ctx):return
        if game._stat_rule_effect(op,ctx):return
        if game._genn_effect(op,ctx):return
        if game._replacement_effect(op,ctx):return
        if game._deadline_effect(op,ctx):return
        if game._infinity_effect(op,ctx):return
        if game._quest_family_effect(op,ctx):return
        if game._muradin_effect(op,ctx):return
        if game._azshara_effect(op,ctx):return
        if game._gelbin_effect(op,ctx):return
        if game._brox_effect(op,ctx):return
        if game._garona_effect(op,ctx):return
        if game._rafaam_effect(op,ctx):return
        if game._fabled_effect(op,ctx):return
        if game._obligation_effect(op,ctx):return
        if game._learned_effect(op,ctx):return
        if game._zone_trigger_effect(op,ctx):return
        owner=ctx['owner']; p=game.players[owner]; q=game.players[1-owner]
        target=ctx.get('target',0); source=ctx.get('source'); name=op[0]
        if game._temporary_control_effect(op,ctx):return
        if game._evolving_effect(op,ctx):return
        if game._imbue_effect(op,ctx):return
        if game._cast_spell_effect(op,ctx):return
        if game._permanent_effect(op,ctx):return
        if game._dream_effect(op,ctx):return
        if game._quest_effect(op,ctx):return
        if game._hero_power_effect(op,ctx):return
        if name=='discover_after':game._discover_after(op);return
        if game._secret_effect(op,ctx): return
        if game._choicegen_effect(op,ctx): return
        if game._historic_colossal_effect(op,ctx):return
        if game._magnetic_effect(op,ctx):return
        if game._colossal_body_effect(op,ctx): return
        if game._herald_effect(op,ctx): return
        if game._future_summon_effect(op,ctx): return
        if game._autocast_effect(op,ctx): return
        if game._map_effect(op,ctx): return
        if game._leyline_effect(op,ctx): return
        if game._generation_effect(op,ctx): return
        if game._tribal_effect(op,ctx): return
        if game._alternate_effect(op,ctx): return
        if game._force_effect(op,ctx): return
        if game._on_draw_effect(op,ctx): return
        if game._replay_effect(op,ctx): return
        if game._prepare_effect(op,ctx): return
        if game._temporary_effect(op,ctx): return
        if game._held_effect(op,ctx): return
        if game._origin_effect(op,ctx): return
        if game._dormant_effect(op,ctx): return
        if game._bonus_effect(op,ctx): return
        if game._draw_event_effect(op,ctx): return
        if game._local_effect(op,ctx): return
        if game._b60_effect(op,ctx): return
        if game._persistent_effect(op,ctx): return
        if game._composed_effect(op,ctx): return
        if game._batch30_effect(op,ctx): return
        if game._imbue_consumer_effect(op,ctx): return
        if game._rewindgen_effect(op,ctx): return
        if game._mutation_effect(op,ctx): return
        if game._entity_effect(op,ctx): return
        if game._lasting_effect(op,ctx): return
        if game._stored_effect(op,ctx): return
        if game._dark_global_effect(op,ctx): return
        if game._dark_effect(op,ctx): return
        if game._rewind_effect(op,ctx): return
        if game._shatter_effect(op,ctx): return
        if game._batch_effect(op,ctx): return
        if game._system_effect(op,ctx): return
        if name in ('damage','combo_damage'):
            if name=='damage' or ctx.get('combo'): game._deal_effect(target,op[1],ctx)
        elif name=='damage_own_hero': game._deal_effect(game.hero_id(owner),op[1],ctx)
        elif name=='bounce':
            minion=game._force_live(target) if target and target>0 else None
            if minion is not None:game._bounce(minion)
        elif name=='heal':
            if target: game._heal(target,op[1],healer=owner,spell=ctx.get('spell',False),power=ctx.get('power',False))
        elif name=='repeat_end_effects':
            p.end_repeat_expiries.append(p.turns_taken+op[1]-1+getattr(ctx.get('physical_card'),'rule_state',{}).get('aura_duration_delta',0))
        elif name=='schedule_turn_effect':
            game._schedule_turn_effect(owner,op[1],op[2],op[3]+getattr(ctx.get('physical_card'),'rule_state',{}).get('aura_duration_delta',0),op[4],source_card_id=ctx.get('card_id'))
        elif name=='hero_divine_shield': p.divine_shield=True
        elif name=='permanent_healing_bonus': p.permanent_healing_bonus+=op[1]
        elif name=='heal_own_hero': game._heal(game.hero_id(owner),op[1],healer=owner,spell=ctx.get('spell',False),power=ctx.get('power',False))
        elif name=='armor': game._gain_armor(owner,op[1])
        elif name in ('draw','draw_empty','outcast_draw'):
            if name=='draw' or (name=='draw_empty' and not p.hand) or (name=='outcast_draw' and ctx.get('outcast')):
                for _ in range(op[1]):
                    game._draw(owner)
                    if game._check_heroes(): break
        elif name=='hero_attack': game._gain_hero_attack(owner,op[1])
        elif name=='weapon_buff': game._buff_weapon(owner,attack=op[1],durability=op[2] if len(op)>2 else 0)
        elif name=='temporary_mana':
            from .mana_accounting import grant_temporary
            grant_temporary(p,op[1])
        elif name in ('summon','combo_summon'):
            if name=='summon' or ctx.get('combo'):
                require_fixed_cards((op[1],),game.cards)
                for _ in range(op[2]): game._summon(owner,op[1], entry_origin='effect', entry_site="game._effect:name == 'summon' or ctx.get('combo')", entry_source=ctx.get('source'))
        elif name=='raise_corpses':
            # Raise only what fits: failed summons must not consume extra corpses.
            count=min(op[2],p.corpses,7-len(p.board))
            game._spend_corpses(owner,count)
            for _ in range(count): game._summon(owner,op[1], entry_origin='effect', entry_site="game._effect:name == 'raise_corpses'", entry_source=ctx.get('source'))
        elif name=='tomb_guardians':
            require_fixed_cards((op[1],),game.cards)
            summoned=[game._summon(owner,op[1], entry_origin='effect', entry_site="game._effect:name == 'tomb_guardians'", entry_source=ctx.get('source')) for _ in range(2)]
            summoned=[m for m in summoned if m is not None]
            if summoned and p.corpses>=4:
                game._spend_corpses(owner,4)
                for m in summoned: m.keywords.add('REBORN')
        elif name=='death_summon':
            start=op[3] if len(op)>3 else 0
            for offset in range(start,start+op[2]):
                game._summon(owner,op[1],min(ctx['death_position']+offset,len(p.board)), entry_origin='deathrattle', entry_site="game._effect:name == 'death_summon'", entry_source=ctx.get('source'))
        elif name=='draw_both':
            # Finish both draws before terminal resolution (including fatigue).
            game._draw(owner); game._draw(1-owner)
        elif name=='draw_tribe':
            game._draw(owner,lambda card: has_tribe(card,op[1]))
        elif name=='draw_unspent_mana':
            if p.mana>0: game._draw(owner)
        elif name=='buff_random_other':
            others=[m for m in p.minions if m is not source and
                    (len(op)<4 or has_tribe(game.cards[m.card_id],op[3]))]
            if others: game._buff(game.rng.choice(others),op[1],op[2])
        elif name=='add':
            for _ in range(op[2]): game._add(owner,op[1])
        elif name=='buff':
            if target and any(m.uid==target for player in game.players for m in player.minions): game._buff(game._find(target),op[1],op[2])
        elif name=='keyword':
            if target and any(m.uid==target for player in game.players for m in player.minions): game._find(target).keywords.add(op[1])
        elif name=='freeze':
            if target<0 or any(m.uid==target for player in game.players for m in player.minions): game._freeze(target)
        elif name=='freeze_enemies':
            for m in q.minions: game._freeze(m.uid)
        elif name=='destroy':
            # Earlier effects/triggers can remove the locked target before resolution.
            victim=next((m for player in game.players for m in player.minions if m.uid==target),None)
            if victim is not None: victim.health=0
        elif name=='buff_board_count':
            if target: game._buff(game._find(target),len(p.minions),len(p.minions))
        elif name=='heal_full':
            if target:
                m=game._find(target); game._heal(target,m.max_health-m.health,healer=owner,spell=ctx.get('spell',False),power=ctx.get('power',False))
        elif name=='damage_self': game._deal_effect(source.uid,op[1],ctx)
        elif name=='damage_random_enemy_minion':
            if q.minions: game._deal_effect(game.rng.choice(q.minions).uid,op[1],ctx)
        elif name=='freeze_self': game._freeze(source.uid)
        elif name=='double_self_attack': game._buff(source,source.attack,0)
        elif name=='double_self_health': game._buff(source,0,source.health)
        elif name=='reverse_deck': p.deck.reverse()
        elif name=='draw_until':
            for _ in range(max(0,op[1]-len(p.hand))):
                game._draw(owner)
                if game._check_heroes(): break
        elif name=='damage_armor': game._deal_effect(target,p.armor,ctx)
        elif name=='destroy_small':
            for player in game.players:
                for m in player.minions:
                    if m.attack<=op[1] and not game._fire_immune_target(m.uid,ctx): m.health=0
        elif name=='destroy_large':
            for player in game.players:
                for m in player.minions:
                    if m.attack>=op[1] and not game._fire_immune_target(m.uid,ctx): m.health=0
        elif name=='health_one':
            for player in game.players:
                for m in player.minions:
                    if not game._fire_immune_target(m.uid,ctx):m.health=m.max_health=1
        elif name=='area_damage':
            groups={'enemy_minions':[m.uid for m in q.minions], 'enemies':[game.hero_id(1-owner)]+[m.uid for m in q.minions],
                    'other_characters':[uid for uid in game._characters() if source is None or uid!=source.uid], 'all_characters':game._characters(), 'all_minions':[m.uid for player in game.players for m in player.minions], 'other_minions':[m.uid for player in game.players for m in player.minions if source is None or m.uid!=source.uid]}
            with game._damage_batch():
                for uid in groups[op[1]]: game._deal_effect(uid,op[2],ctx)
        elif name=='area_heal':
            for uid in [game.hero_id(owner)]+[m.uid for m in p.minions]: game._heal(uid,op[1],healer=owner,spell=ctx.get('spell',False),power=ctx.get('power',False))
        elif name in ('damage_draw_if_dead','damage_draw_if_alive'):
            if target:
                game._deal_effect(target,op[1],ctx); dead=game._find(target).health<=0
                game._settle()
                if not game.terminal and dead==(name=='damage_draw_if_dead'):
                    for _ in range(op[2] if len(op)>2 else 1):
                        game._draw(owner)
                        if game._check_heroes(): break
        elif name=='hand_buff' or name=='taunt_hand_buff':
            for c in p.hand:
                if game.cards[c.card_id]['type']=='MINION' and (name=='hand_buff' or 'TAUNT' in game._card_mechanics(c)):
                    _saidan_add(c,'attack_bonus',op[1]); _saidan_add(c,'health_bonus',op[2])
        elif name=='board_buff':
            for m in p.minions: game._buff(m,op[1],op[2])
        elif name=='board_expire':
            for m in p.minions:m.expires=True
        elif name=='board_keyword':
            for m in p.minions: m.keywords.add(op[1])
        elif name=='grave_strength':
            spent=5 if p.corpses>=5 else 0; game._spend_corpses(owner,spent)
            for m in p.minions: game._buff(m,3 if spent else 1,0)
        elif name=='blood_tap':
            spent=2 if p.corpses>=2 else 0; game._spend_corpses(owner,spent)
            game._effect(('hand_buff',2 if spent else 1,2 if spent else 1),ctx)
        elif name=='asphyxiate':
            if q.minions:
                highest=max(m.attack for m in q.minions); game.rng.choice([m for m in q.minions if m.attack==highest]).health=0
        elif name=='self_hand_health': game._buff(source,0,len(p.hand))
        elif name=='self_enemy_hand_health': game._buff(source,0,-len(q.hand))
        elif name=='self_weapon_attack': game._buff(source,p.weapon['attack'] if p.weapon else 0,0)
        elif name=='adjacent_taunt':
            index=p.board.index(source)
            for i in (index-1,index+1):
                if 0<=i<len(p.board) and p.board[i] in p.minions: p.board[i].keywords.add('TAUNT')
        elif name=='other_murloc_health':
            for m in p.minions:
                if m is not source and has_tribe(game.cards[m.card_id],'MURLOC'): game._buff(m,0,op[1])
        elif name=='shadow_hand_buff':
            if any(has_school(game.cards[c.card_id],'SHADOW') for c in p.hand): game._buff(source,op[1],op[2])
        elif name=='discard':
            game._discard_random(owner,op[1])
        elif name=='remove_enemy_top':
            if q.deck: game._log('remove_deck_card',player=1-owner,card=game._card_data(q.deck.pop())['id'])
        elif name=='random_shield_taunt':
            if p.minions: game.rng.choice(p.minions).keywords.update({'DIVINE_SHIELD','TAUNT'})
        elif name=='beast_weapon_durability':
            if any(has_tribe(game.cards[m.card_id],'BEAST') for m in p.minions): game._buff_weapon(owner,durability=op[1])
        elif name=='destroy_random_enemy':
            if q.minions: game.rng.choice(q.minions).health=0
        else: raise UnsupportedCard('Effect opcode not implemented: '+name)

