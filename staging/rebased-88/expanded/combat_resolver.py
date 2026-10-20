"""Stateless combat execution; mutable state and card hooks belong to the game.

Normal and forced attacks use the same resolution entry point.
"""
from .cards import WEAPON_TRIGGERS
from copy import deepcopy


class CombatResolver:
    __slots__ = ()

    def attack(self,game,source,target,*,forced=False):
        target=game._random_attack_target(source,target)
        owner=game._find(source).owner if source>0 else -source-1; p=game.players[owner]
        listeners=game._event_listeners();window=game._open_attack_window(source)
        try:
            from .historical_forgetful import plan
            target=plan(game,source,target,forced=forced)
            if target is None:return
            game._combat_sequence_depth=getattr(game,'_combat_sequence_depth',0)+1
            try:
                if source>0:
                    from .historical_aura_finish_batch import before_attack as aura_finish_before_attack
                    aura_finish_before_attack(game,source)
                    game._rule_events.append(('before_minion_attack',dict(owner=owner,source=source,target=target,stealthed=game._b60_pre_attack(source)),game._event_listeners()))
                    game._drain_events()
                    if game.terminal:return
                    if not any(m.uid==source and m.health>0 for m in p.minions):return
                    if target>0 and not any(m.uid==target and m.health>0 for player in game.players for m in player.minions):return
                else:
                    from .historical_attack_weapons import before_hero_attack
                    before_hero_attack(game,owner,target)
                    game._drain_events()
                    if game.terminal:return
                    if target>0 and game._force_live(target) is None:return
                if forced:game._resolve_combat(source,target,listeners,forced=True)
                else:game._resolve_combat(source,target,listeners)
            finally:
                game._combat_sequence_depth-=1
                game._close_attack_window(window)
                game._settle()
        finally:
            game._close_attack_window(window)

    def resolve(self,game,source,target,listeners,*,forced=False,excess_to_hero=False):
        if game._historic_neptulon_combat(source,target,listeners,forced):return
        attack_window=next((window for window in reversed(getattr(game,'_attack_windows',[]))
                            if window['source']==source),None)
        owner=game._find(source).owner if source>0 else -source-1; p=game.players[owner]
        attacker=game._find(source) if source>0 else None
        weapon_id=p.weapon['card_id'] if p.weapon else None
        weapon_card=p.equipped_card
        weapon_uid=getattr(weapon_card,'uid',None)
        silverleaf_draws=p.weapon.get('historical_silverleaf_draws',0) if p.weapon and game.current==owner else 0
        attack=game._outgoing_tribal_damage(attacker,attacker.attack) if attacker else game._hero_attack(owner)
        defender=game._find(target) if target>0 else None
        attack_target_attack=defender.attack if defender is not None else 0
        if attacker is None and defender is not None and defender.health>0 and game._active('RLK_827',owner):
            # Setting Health is not damage and leaves the victim's Attack intact.
            defender.health=defender.max_health=1
            game._log('set_health',entity=defender.uid,amount=1,source='RLK_827')
        # A hero's weapon is active only on that hero's own turn.
        retaliation=game._outgoing_tribal_damage(defender,defender.attack) if defender else 0
        sk=game._effective_keywords(attacker) if attacker else set(game.cards[p.weapon['card_id']].get('mechanics',[])) if p.weapon else set()
        if attacker is None and p.weapon:sk.update(p.weapon.get('historical_keywords',()))
        if attacker is None and (p.hero_lifesteal_until>=game.turn or game._active('ETC_398',owner)):sk.add('LIFESTEAL')
        if attacker is None and p.weapon and p.weapon.get('poisonous_until',-1)>=game.turn:sk.add('POISONOUS')
        if attacker is None and game.current==owner and p.weapon and p.weapon.get('historical_leeching_until',-1)>=game.turn:sk.add('LIFESTEAL')
        dk=game._effective_keywords(defender) if defender else set()
        neighbors=[]
        if attacker:
            pos=p.board.index(attacker);neighbors=[p.board[i].uid for i in (pos-1,pos+1) if 0<=i<len(p.board)]
        cleave=[]
        from .forge_intrinsics import values as intrinsic_values
        from .historical_passive_stats import CLEAVE_IDS
        if attacker and not attacker.silenced and (attacker.card_id in CLEAVE_IDS|{'CORE_SCH_605','SC_022'} or any(intrinsic_values(attacker,'cleave')) or any(part['card_id']=='TTN_471' for part in attacker.rule_state.get('magnetic_parts',()))) and defender:
            board=game.players[defender.owner].board;pos=board.index(defender)
            cleave=[board[i] for i in (pos-1,pos+1) if 0<=i<len(board) and board[i] in game.players[defender.owner].minions]
        if attacker is None and (weapon_id in ('ICC_834w','JAM_015t3') or p.weapon and p.weapon.get('historical_ignis_cleave',False) or getattr(p,'historical_hero_cleave_turn',-1)==game.turn) and defender is not None:
            board=game.players[defender.owner].board;pos=board.index(defender)
            cleave=[board[i] for i in (pos-1,pos+1) if 0<=i<len(board) and board[i] in game.players[defender.owner].minions]
        mutalisk_face=attacker is not None and attacker.card_id=='SC_022' and not attacker.silenced and defender is not None and len(cleave)<2
        p.friendly_attacks+=1
        game._log('attack',player=owner,source=source,target=target)
        if attacker is not None:
            if not hasattr(game,'_historical_attack_turns'):game._historical_attack_turns={}
            game._historical_attack_turns[attacker.uid]=game.turn
        if attacker:
            if not forced:attacker.attacks+=1
            attacker.keywords.discard('STEALTH')
            attacker.temporary_keywords[:]=[e for e in attacker.temporary_keywords if e['keyword']!='STEALTH']
        else:
            if not forced:
                p.hero_attacks+=1
                state=getattr(p,'historical_multistrike',{})
                if target>0 and state.get('turn')==game.turn:state['minion_attacks']=state.get('minion_attacks',0)+1
            p.hero_attacks_total+=1
            from .historical_held_upgrades import progress as held_spellstone_progress
            held_spellstone_progress(game,owner,'opal',1)
            p.historical_valeera_stealth_until=-1
        spill=max(0,attack-defender.health) if excess_to_hero and defender else 0
        rhino=attacker is not None and attacker.card_id=='DMF_087' and not attacker.silenced and defender is not None
        jormungar=attacker.rule_state.get('historical_jormungar',0) if attacker is not None and not attacker.silenced else 0
        defender_health=defender.health if defender is not None else 0
        with game._damage_batch():
            dealt=game._damage(target,attack-spill,'POISONOUS' in sk,damage_source=attacker,damage_owner=owner)
            spilled=game._damage(game.hero_id(defender.owner),spill,damage_source=attacker,damage_owner=owner) if spill else 0
            if rhino and defender.health<=0 and dealt>defender_health:
                spilled+=game._damage(game.hero_id(defender.owner),dealt-defender_health,damage_source=attacker,damage_owner=owner)
            if jormungar and defender is not None and dealt>defender_health:
                for _ in range(jormungar):spilled+=game._damage(game.hero_id(1-owner),dealt-defender_health,damage_source=attacker,damage_owner=owner)
            for extra in cleave:
                extra_health=extra.health
                extra_dealt=game._damage(extra.uid,attack,'POISONOUS' in sk,damage_source=attacker,damage_owner=owner)
                if jormungar and extra_dealt>extra_health:
                    for _ in range(jormungar):
                        overflow=game._damage(game.hero_id(1-owner),extra_dealt-extra_health,damage_source=attacker,damage_owner=owner)
                        if 'LIFESTEAL' in sk:game._effect_lifesteal(owner,overflow)
                game._freeze_from_damage(attacker,extra.uid,extra_dealt)
                if 'LIFESTEAL' in sk:game._effect_lifesteal(owner,extra_dealt)
            if mutalisk_face:
                # A missing neighbor hits the enemy hero once, even if both are missing.
                face=game.hero_id(1-owner)
                extra_dealt=game._damage(face,attack,'POISONOUS' in sk,damage_source=attacker,damage_owner=owner)
                game._freeze_from_damage(attacker,face,extra_dealt)
                if 'LIFESTEAL' in sk:game._effect_lifesteal(owner,extra_dealt)
            returned=game._damage(source,retaliation,'POISONOUS' in dk,damage_source=defender,damage_owner=defender.owner if defender else None)
            game._freeze_from_damage(attacker,target,dealt)
            if attacker is None and weapon_id=='DEEP_016' and dealt>0:game._freeze(target)
            game._freeze_from_damage(defender,source,returned)
            if defender is not None and returned>0:
                defender.keywords.discard('STEALTH')
                defender.temporary_keywords[:]=[effect for effect in defender.temporary_keywords if effect['keyword']!='STEALTH']
            if 'LIFESTEAL' in sk: game._effect_lifesteal(owner,dealt+spilled)
            if 'LIFESTEAL' in dk: game._effect_lifesteal(defender.owner,returned)
        # Keep entity-scoped attacking-kill history even before an inherited
        # Deathrattle is gained. Resurrections use fresh printed definitions.
        killed=[victim for victim in ([defender] if defender is not None else [])+cleave if victim.health<=0]
        if attacker is not None and killed:
            if not hasattr(game,'_combat_kill_history'):game._combat_kill_history={}
            game._combat_kill_history.setdefault(attacker.uid,[]).extend(deepcopy(killed))
        if attacker is not None and killed:
            from .historical_copy_batches import ichman_killed
            ichman_killed(game,attacker)
        if attacker and attacker.card_id=='EDR_819' and not attacker.silenced and killed:
            attacker.rule_state.setdefault('combat_kills',[]).extend(victim.card_id for victim in killed)
        attack_killed=defender is not None and defender.health<=0
        game._close_attack_window(attack_window)
        if not attacker and p.weapon and weapon_id in ('CORE_RLK_086','ICC_314t1') and defender and defender.health<=0:
            p.weapon.setdefault('stored_kills',[]).append(defender.card_id)
        if not attacker and p.weapon:
            from .historical_arsenal_batches import lose_durability
            if weapon_id=='EX1_411' and defender is not None:
                p.weapon['attack']=max(0,p.weapon['attack']-1)
            else:lose_durability(game,owner,1)
        if attacker:
            game._rule_events.append(('minion_attack',dict(owner=owner,source=source,target=target,attacker_neighbors=neighbors,attacker_keywords=tuple(sorted(sk)),attacker_card_id=attacker.card_id,attack_damage=attack,killed=defender is not None and defender.health<=0,victim_card_id=defender.card_id if defender else None),listeners))
        else:
            from .historical_sidequest_spell_batch import event as sidequest_batch_event
            sidequest_batch_event(game,'hero_attack',dict(owner=owner,source=source,target=target))
            game._rule_events.append(('hero_attack',dict(owner=owner,source=source,target=target,killed=attack_killed,victim_card_id=defender.card_id if defender else None),listeners))
            if silverleaf_draws:
                game._rule_events.append(('captured_effects',dict(operations=(('draw',silverleaf_draws),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id='BAR_318')),[]))
            from .historical_ignis_crafting import after_attack as ignis_after_attack
            ignis_after_attack(game,owner,weapon_card)
            weapon_operations=tuple(WEAPON_TRIGGERS.get(weapon_id,()))
            if weapon_operations:
                # Weapon Discover can suspend combat before the death checkpoint.
                # Use the resumable event pipeline instead of an inline effect.
                context=dict(owner=owner,source=None,target=target,bonus=0,lifesteal=False,attack_damage=attack,attack_killed=attack_killed,weapon_uid=weapon_uid,weapon_card=weapon_card,attack_target_attack=attack_target_attack,attack_target_health_after=defender.health if defender is not None else 0,attack_keywords=tuple(sk))
                game._rule_events.append(('captured_effects',dict(operations=weapon_operations,context=context),[]))
        if target==game.hero_id(1-owner):
            game._secret_event('after_attack',owner,source=source,target=target,source_snapshot=deepcopy(attacker))
        game._avatar_after_attack(owner,attacker,sk)
        game._settle(allow_event_choices=True)

