"""Forced attacks retain controller and turn identity without spending attacks.

Interaction references for the explicit combat sequences:
https://hearthstone.wiki.gg/wiki/Warmaul_Challenger (30-attack Battlecry limit)
https://hearthstone.wiki.gg/wiki/Ursoc (attacking kills, not retaliation kills)
https://hearthstone.wiki.gg/wiki/Wilted_Shadow (pre-heal attacks and capped heal)
https://us.forums.blizzard.com/en/hearthstone/t/briarspawn-drake-end-of-turn-divine-shield-breaks-it/144292
The frozen Standard Core identity is used for Warmaul, not its Wild original.
"""
class ForcedCombat:
    def _open_attack_window(self,source):
        window={'source':source}
        if not hasattr(self,'_attack_windows'):self._attack_windows=[]
        self._attack_windows.append(window)
        return window

    def _close_attack_window(self,window):
        if window is None:return
        self._attack_windows[:]=[entry for entry in self._attack_windows if entry is not window]

    def _force_live(self,uid):
        return next((m for p in self.players for m in p.minions if m.uid==uid and m.health>0),None)

    def _force_attack(self,source,target):
        attacker=self._force_live(source)
        if attacker is None or source==target or self.terminal:return
        if target>0 and self._force_live(target) is None:return
        if target<0 and self.players[-target-1].health<=0:return
        context=dict(owner=attacker.owner,source=None,target=0,bonus=0,lifesteal=False)
        self._rule_events.append(('captured_effects',dict(operations=(('force_pair',source,target),),context=context),[]))
        self._settle(allow_event_choices=True)

    def _force_target(self,owner,mode):
        enemies=[m for m in self.players[1-owner].minions if m.health>0]
        targets=[m.uid for m in enemies]
        if mode=='random_enemy_character':
            targets.append(self.hero_id(1-owner))
        if mode=='lowest':
            targets.append(self.hero_id(1-owner))
            def health(uid):return self.players[-uid-1].health if uid<0 else self._find(uid).health
            minimum=min(map(health,targets));targets=[uid for uid in targets if health(uid)==minimum]
        return self.rng.choice(targets) if targets else 0

    def _force_split(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];source=ctx.get('source')
        if name=='force_pair':
            state={'source':op[1],'target':op[2],'excess_to_hero':len(op)>3 and op[3]}
            return ('force_begin',state),(('force_resolve',state),)
        if name=='force_duel':
            if source is None:return ('batch30_noop',),()
            return self._force_split(('force_duel_step',source.uid,ctx.get('target',0),30),ctx)
        if name=='force_duel_step':
            attacker=self._force_live(op[1]);defender=self._force_live(op[2])
            if op[3]<=0 or attacker is None or defender is None:return ('batch30_noop',),()
            first,tail=self._force_split(('force_pair',op[1],op[2]),ctx)
            return first,tail+(('force_duel_step',op[1],op[2],op[3]-1),)
        if name=='force_all_others':
            if source is None:return ('batch30_noop',),()
            targets=[m.uid for player in self.players for m in player.minions if m.uid!=source.uid and m.health>0]
            self.rng.shuffle(targets)
            ops=[('force_pair',source.uid,uid) for uid in targets]
        elif name=='force_resurrect_kills':
            identities=list(source.rule_state.get('combat_kills',())) if source else []
            self.rng.shuffle(identities)
            ops=[('summon',cid,1) for cid in identities]
        elif name=='force_source_excess':
            target=self._force_target(owner,'random')
            if source is None or not target:return ('batch30_noop',),()
            return self._force_split(('force_pair',source.uid,target,True),ctx)
        elif name=='force_enemies_into_source':
            if source is None:return ('batch30_noop',),()
            ops=[('force_pair',m.uid,source.uid) for m in self.players[1-owner].minions if m.health>0]
        elif name=='force_cheap_attacks':
            card=ctx.get('physical_card')
            if card is None or ctx.get('paid_cost',self._cost(card,owner))>3:return ('batch30_noop',),()
            # Targets are selected without replacement before combat resolves.
            enemies=[m for m in self.players[1-owner].minions if m.health>0]
            ops=[('force_pair',source.uid,m.uid) for m in self.rng.sample(enemies,min(2,len(enemies)))]
        elif name=='force_summon_group':
            state={'summoned':[],'mode':op[3]}
            if op[3]=='empty_deck_lowest':state['enabled']=not any(self._card_data(c)['type']=='MINION' for c in p.deck)
            ops=[('force_summon_one',op[1],state)]*op[2]+[('force_group_attacks',state)]
        elif name=='force_recruit_pair':
            filters=self._validate_filters(op[1]);state={'summoned':[]}
            ops=[('force_recruit_one',filters,state)]*2+[('force_recruits_fight',state)]
        elif name=='feast_raptors':
            state={'summoned':[]}
            ops=[('force_summon_one','DINO_136t',state)]*3+[('feast_grant',state)]
        elif name=='force_group_attacks':
            state=op[1];ops=[]
            if state.get('enabled',True):
                for uid in state['summoned']:
                    ops.append(('force_group_one',uid,state['mode']))
        elif name=='force_spire':
            state={'summoned':[],'mode':'random','stats':len(p.hand)}
            ops=[('force_summon_one','JAIL_511t',state),('force_group_attacks',state)]
        else:return None
        if not ops:return ('batch30_noop',),()
        first,tail=self._split_fixed_summon(ops[0],ctx)
        return first,tuple(tail)+tuple(ops[1:])

    def _force_effect(self,op,ctx):
        owner=ctx['owner'];source=ctx.get('source');name=op[0]
        if name=='force_shadow_heal_attack':
            attacker=self._force_live(op[1])
            if attacker and not attacker.silenced and attacker.owner==owner:self._force_attack(attacker.uid,op[2])
        elif name=='force_finish_heal':
            if op[1]<0 or self._force_live(op[1]) is not None:
                self._heal(op[1],op[2],healer=owner,_after_shadow=True)
        elif name=='force_begin':
            state=op[1];attacker=self._force_live(state['source']);target=state['target']
            if attacker is None or attacker.uid==target or (target>0 and self._force_live(target) is None):return True
            state['listeners']=self._event_listeners()
            state['window']=self._open_attack_window(attacker.uid)
            if self._secret_event('attack',attacker.owner,source=attacker.uid,target=target) or self._force_live(attacker.uid) is None:
                self._close_attack_window(state['window']);return True
            state['ready']=True
            self._rule_events.append(('before_minion_attack',dict(owner=attacker.owner,source=attacker.uid,target=target,stealthed=self._b60_pre_attack(attacker.uid)),self._event_listeners()))
        elif name=='force_resolve':
            state=op[1];attacker=self._force_live(state['source']);target=state['target']
            if not state.get('ready') or attacker is None or (target>0 and self._force_live(target) is None):
                self._close_attack_window(state.get('window'));return True
            self._combat_sequence_depth=getattr(self,'_combat_sequence_depth',0)+1
            try:self._resolve_combat(attacker.uid,target,state['listeners'],forced=True,excess_to_hero=state.get('excess_to_hero',False))
            finally:
                self._combat_sequence_depth-=1
                self._close_attack_window(state.get('window'))
        elif name=='force_summon_one':
            state=op[2];bonus=state['stats']-1 if 'stats' in state else 0
            m=self._summon(owner,op[1],attack_bonus=bonus,health_bonus=bonus,entry_origin='effect',entry_site='forced_summon',entry_source=source)
            if m:state['summoned'].append(m.uid)
        elif name=='force_recruit_one':
            m=self._recruit_from_zone(owner,'deck',op[1],site='forced_recruit_pair')
            if m:op[2]['summoned'].append(m.uid)
        elif name=='force_recruits_fight':
            pair=op[1]['summoned']
            if len(pair)==2 and all(self._force_live(uid) is not None for uid in pair):
                self._force_attack(pair[0],pair[1])
        elif name=='feast_grant':
            if ctx.get('outcast'):
                for uid in op[1]['summoned']:
                    m=self._force_live(uid)
                    if m:m.temporary_keywords.append(dict(keyword='IMMUNE_WHILE_ATTACKING',phase='end',turn=self.turn))
        elif name=='force_group_one':
            if op[2]=='random_enemy_character':
                attacker=self._force_live(op[1])
                if attacker is None:return True
                owner=attacker.owner
            target=ctx.get('target',0) if op[2]=='target' else self._force_target(owner,'lowest' if op[2]=='empty_deck_lowest' else 'random_enemy_character' if op[2]=='random_enemy_character' else 'random')
            if target:self._force_attack(op[1],target)
        elif name=='force_source_random':
            if source and self._force_live(source.uid):
                target=self._force_target(source.owner,'random')
                if target:self._force_attack(source.uid,target)
        elif name=='force_source_lowest':
            target=self._force_target(owner,'lowest')
            if source and target:self._force_attack(source.uid,target)
        elif name=='force_enemy_into_target':
            defender=self._force_live(ctx.get('target',0))
            if defender:
                target=self._force_target(defender.owner,'random')
                if target:self._force_attack(target,defender.uid)
        elif name=='force_follow_hero':
            if source:self._force_attack(source.uid,ctx['event']['target'])
        elif name=='force_pre_damage':self._deal_effect(ctx['event']['target'],op[1],ctx)
        else:return False
        return True
