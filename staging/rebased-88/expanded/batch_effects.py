"""Shared explicit effects for the 200-card milestone; no rules-text execution."""
from copy import deepcopy
from engine.game import Card
from .selectors import has_tribe, shares_tribe, has_school, effective_tribes, TRIBES, CARD_TYPES, SCHOOLS
from .pools import require_fixed_cards


class BatchEffects:
    def _kindred(self,cid,owner):
        p=self.players[owner];d=self.cards[cid]
        if d['type']=='SPELL':return bool(d.get('spellSchool') and d['spellSchool'] in p.previous_schools)
        if d['type']!='MINION':return False
        kinds=effective_tribes(d)
        previous=TRIBES if 'ALL' in p.previous_tribes else p.previous_tribes & TRIBES
        return bool(kinds & previous)

    def _recruit_from_zone(self,owner,zone_name,filters,*,position=-1,keyword=None,
                           site="batch_effects._batch_effect:name == 'summon_from_zone'"):
        if zone_name not in ('hand','deck'):raise ValueError('Invalid summon source zone')
        filters=self._validate_filters(filters)
        p=self.players[owner];zone=getattr(p,zone_name)
        choices=[i for i,card in enumerate(zone) if self._card_data(card)['type']=='MINION'
                 and self._matches_filter(card,filters,hand_owner=owner if zone_name=='hand' else None,zone_owner=owner)]
        if not choices or len(p.board)>=7:return None
        card=zone.pop(self.rng.choice(choices))
        summoned=self._summon(owner,self._card_data(card)['id'],position=position,
            attack_bonus=getattr(card,'attack_bonus',0),health_bonus=getattr(card,'health_bonus',0),
            entry_origin='recruit',entry_site=site,entry_zone=zone_name,entry_source=card)
        if summoned is not None and not summoned.dormant and keyword:summoned.keywords.add(keyword)
        self._refresh_auras()
        self._trace_entity('recruit_initialized',summoned,owner=owner,zone=zone_name)
        return summoned

    def _card_data(self,value):
        return self.cards[value.card_id if isinstance(value,Card) else value]

    @staticmethod
    def _set_card_cost(card,cost):
        card.set_cost=cost
        card.cost_delta=0
        if hasattr(card,'temporary_cost_discounts'):card.temporary_cost_discounts=[]

    def _card_stat(self,value,key,owner=None):
        base=self._card_data(value).get(key,0)
        cid=self._card_data(value)['id']
        if key in ('attack','health') and self._card_data(value)['type']=='MINION':
            from .base_stats import base_stats
            base=base_stats(self,value,owner)[0 if key=='attack' else 1]
        if cid=='JAIL_501' and owner is not None and key in ('attack','health','cost') and any(c is value for c in self.players[owner].hand):base=max(1,self.players[owner].mana)
        if cid=='CATA_493' and owner is not None and key in ('attack','health'):
            base+=2*len(self.players[owner].discard_history)
        if owner is not None and key in ('attack','health') and self._is_recruit(cid):
            base+=getattr(self.players[owner],'recruit_'+key+'_bonus')
        if not isinstance(value,Card):return base
        if key=='cost':base=getattr(value,'set_cost',base)
        bonus={'attack':'attack_bonus','health':'health_bonus','cost':'cost_delta'}.get(key)
        return max(0,base+getattr(value,bonus,0)) if bonus else base

    @staticmethod
    def _validate_filters(filters):
        # Validate the entire declaration before evaluating cards: an empty
        # deck or an early non-match must not hide a broken effect definition.
        filters=tuple(filters)
        for clause in filters:
            if not isinstance(clause,(tuple,list)) or len(clause)!=3:
                raise ValueError('Card filter must be a (field, relation, value) triple')
            key,relation,wanted=clause
            if key in ('attack','health','cost'):
                if relation not in ('eq','ge','le') or type(wanted) is not int:
                    raise ValueError('Invalid numeric card filter: '+repr(clause))
            elif key=='id':
                if relation!='in' or not isinstance(wanted,tuple) or not wanted or any(not isinstance(cid,str) or not cid for cid in wanted):
                    raise ValueError('Invalid card identity set: '+repr(clause))
            elif key in ('tribe','mechanic','type','school'):
                if relation!='eq' or not isinstance(wanted,str) or not wanted:
                    raise ValueError('Invalid identity card filter: '+repr(clause))
                if key=='tribe' and wanted not in TRIBES:
                    raise ValueError('Unknown Constructed tribe: '+wanted)
                if key=='school' and wanted not in SCHOOLS:
                    raise ValueError('Unknown Constructed spell school: '+wanted)
                if key=='type' and wanted not in CARD_TYPES:
                    raise ValueError('Unknown Constructed card type: '+wanted)
            else:
                raise ValueError('Unknown card filter field: '+str(key))
        return filters

    def _matches_filter(self,value,filters,hand_owner=None,zone_owner=None):
        filters=self._validate_filters(filters)
        d=self._card_data(value)
        for key,relation,wanted in filters:
            if key=='id':
                if d['id'] not in wanted:return False
            elif key=='tribe':
                if not has_tribe(d,wanted):return False
            elif key=='school':
                if not has_school(d,wanted):return False
            elif key=='mechanic':
                if wanted not in self._card_mechanics(value):return False
            elif key=='type':
                if d['type']!=wanted:return False
            else:
                # Absence of attack/health is not a printed zero stat.
                if key not in d:return False
                actual=(self._cost(value,hand_owner) if key=='cost' and hand_owner is not None
                        else self._card_stat(value,key,hand_owner if hand_owner is not None else zone_owner))
                if relation=='eq' and actual!=wanted:return False
                if relation=='ge' and actual<wanted:return False
                if relation=='le' and actual>wanted:return False
        return True

    def _holding_matches(self,owner,filters):
        filters=self._validate_filters(filters)
        return any(self._matches_filter(c,filters,hand_owner=owner) for c in self.players[owner].hand)

    def _draw_index(self,owner,index):
        p=self.players[owner]
        if not p.deck:
            return self._draw(owner)
        return self._take_deck_draw(owner,index)

    def _draw_filtered(self,owner,filters):
        filters=self._validate_filters(filters)
        choices=[i for i,v in enumerate(self.players[owner].deck) if self._matches_filter(v,filters,zone_owner=owner)]
        return self._draw_index(owner,self.rng.choice(choices)) if choices else None

    def _discount_cards(self,cards,amount):
        for card in cards:card.cost_delta=getattr(card,'cost_delta',0)-amount

    def _clone_hand_card(self,owner,card,*,source_owner=None):
        p=self.players[owner]
        if len(p.hand)>=10:
            self._log('burn_generated',player=owner,card=card.card_id);return
        clone=self._copy_card(card,source_owner=source_owner);return self._enter_hand(owner,clone)

    def _batch_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];q=self.players[1-owner]
        target=ctx.get('target',0);source=ctx.get('source')
        if name in ('summon_spend_mana_buff','summon_corpse_keyword'):
            require_fixed_cards((op[1],),self.cards)
            summoned=[self._summon(owner,op[1], entry_origin='effect', entry_site="batch_effects._batch_effect:name in ('summon_spend_mana_buff', 'summon_corpse_keyword')", entry_source=ctx.get('source')) for _ in range(op[2])]
            summoned=[m for m in summoned if m is not None]
            if name=='summon_spend_mana_buff':
                spent=p.mana;p.mana=0
                self._b60_spend_mana(owner,spent)
                if spent:self._log('spend_mana_effect',player=owner,amount=spent)
                for m in summoned:self._buff(m,spent,spent)
            elif summoned and p.corpses>=op[3]:
                self._spend_corpses(owner,op[3])
                for m in summoned:m.keywords.add(op[4])
        elif name=='held_tribe_summon':
            if any(has_tribe(self.cards[c.card_id],op[1]) for c in p.hand):
                require_fixed_cards((op[2],),self.cards)
                for _ in range(op[3]):self._summon(owner,op[2], entry_origin='effect', entry_site="batch_effects._batch_effect:name == 'held_tribe_summon'", entry_source=ctx.get('source'))
        elif name=='buff_shared_type':
            if target:
                chosen=self._find(target)
                selected=[m for m in p.minions if m is chosen or shares_tribe(self.cards[chosen.card_id],self.cards[m.card_id])]
                for m in selected:self._buff(m,op[1],op[2])
        elif name=='buff_random_hand_minion':
            owners={'friendly':(owner,), 'enemy':(1-owner,), 'both':(owner,1-owner)}[op[1]]
            for recipient in owners:
                candidates=[c for c in self.players[recipient].hand if self.cards[c.card_id]['type']=='MINION']
                if candidates:
                    card=self.rng.choice(candidates)
                    card.attack_bonus+=op[2];card.health_bonus+=op[3]
        elif name=='buff_random_hand_tribe':
            candidates=[c for c in p.hand if has_tribe(self.cards[c.card_id],op[1])]
            if candidates:
                card=self.rng.choice(candidates)
                card.attack_bonus+=op[2];card.health_bonus+=op[3]
        elif name=='refresh_mana':
            p.mana=max(p.mana,min(max(0,p.max_mana-p.locked_mana),p.mana+op[1]))
        elif name=='damage_lowest_health_enemy':
            candidates=[(self.hero_id(1-owner),q.health)]+[(m.uid,m.health) for m in q.minions]
            lowest=min(health for _,health in candidates)
            targets=[uid for uid,health in candidates if health==lowest]
            self._deal_effect(self.rng.choice(targets),op[1],ctx)
        elif name=='damage_random_enemy':
            targets=[self.hero_id(1-owner)]+[m.uid for m in q.minions]
            self._deal_effect(self.rng.choice(targets),op[1],ctx)
        elif name in ('set_target_stats','set_target_stats_by_owner'):
            if target:
                m=self._find(target)
                attack,health=op[1:3] if name=='set_target_stats' or m.owner==owner else op[3:5]
                self._set_minion_attack(m,attack+m.aura_attack)
                m.temporary_attack=0
                m.health=m.max_health=health+m.aura_health
        elif name=='resurrect_distinct_min_cost':
            distinct={}
            for cid in p.death_history:
                card=self.cards[cid]
                if card['cost']>=op[1]:
                    identity=card.get('countAsCopyOfDbfId',card.get('dbfId',cid))
                    distinct.setdefault(identity,cid)
            choices=list(distinct.values());self.rng.shuffle(choices)
            for cid in choices:
                if len(p.board)>=7:break
                self._summon(owner,cid, entry_origin='resurrection', entry_site="batch_effects._batch_effect:name == 'resurrect_distinct_min_cost'", entry_source=ctx.get('source'))
        elif name=='resurrect_highest':
            choices=[cid for cid in p.death_history if op[1] is None or has_tribe(self.cards[cid],op[1])]
            if choices:
                highest=max(self.cards[cid]['cost'] for cid in choices)
                self._summon(owner,self.rng.choice([cid for cid in choices if self.cards[cid]['cost']==highest]), entry_origin='resurrection', entry_site="batch_effects._batch_effect:name == 'resurrect_highest'", entry_source=ctx.get('source'))
        elif name=='resurrect_costs_reborn':
            for cost in op[1]:
                choices=[cid for cid in p.death_history if self.cards[cid]['cost']==cost]
                if choices:
                    m=self._summon(owner,self.rng.choice(choices), entry_origin='resurrection', entry_site="batch_effects._batch_effect:name == 'resurrect_costs_reborn'", entry_source=ctx.get('source'))
                    if m and not m.dormant:m.keywords.add('REBORN')
        elif name=='resurrect_deathrattle_copies':
            choices=[cid for cid in p.death_history if 'DEATHRATTLE' in self.cards[cid].get('mechanics',[]) and op[1]<=self.cards[cid]['cost']<=op[2] and (not op[3] or cid!=source.card_id)]
            if choices:
                cid=self.rng.choice(choices)
                for _ in range(2):self._summon(owner,cid, entry_origin='resurrection', entry_site="batch_effects._batch_effect:name == 'resurrect_deathrattle_copies'", entry_source=ctx.get('source'))
        elif name=='return_last_turn_spells':
            for cid in p.spells_previous:self._add(owner,cid)
        elif name=='summon_played_one_cost':
            for h in p.played_history:
                if h['cost']==1 and self.cards[h['card_id']]['type']=='MINION':self._summon(owner,h['card_id'], entry_origin='effect', entry_site="batch_effects._batch_effect:name == 'summon_played_one_cost'", entry_source=ctx.get('source'))
        elif name=='repeat_copy_damage':
            if any(h['card_id']==op[2] for h in p.played_history):self._effect(('area_damage','enemies',op[1]),ctx)
            else:self._deal_effect(target,op[1],ctx)
        elif name=='permanent_end_damage':p.permanent_end_damage.append(op[1])
        elif name=='return_remembered_discards':
            for cid in source.remembered_discards:
                if len(p.hand)>=10:self._log('burn_generated',player=owner,card=cid)
                else:
                    card=Card(self._new_id(),cid);card.cost_delta=-op[1];self._enter_hand(owner,card)
            self._refresh_auras()
        elif name=='discard_filtered':
            filters=self._validate_filters(op[1])
            candidates=[c for c in p.hand if self._matches_filter(c,filters,hand_owner=owner)]
            ctx['discard_succeeded']=bool(candidates)
            if candidates:self._discard_card(owner,self.rng.choice(candidates))
        elif name=='if_discarded':
            if ctx.pop('discard_succeeded',False):self._effect(op[1],ctx)
        elif name=='discard_highest_cost':
            if p.hand:
                highest=max(self._cost(c,owner) for c in p.hand)
                candidates=[c for c in p.hand if self._cost(c,owner)==highest]
                self._discard_card(owner,self.rng.choice(candidates))
        elif name=='summon_discarded_copy':
            card=ctx['event']['card']
            if self.cards[card.card_id]['type']=='MINION':
                # Graveyard copies lose hand enchantments; current board auras
                # (including the owner's discard-count aura) apply on summon.
                self._summon(owner,card.card_id, entry_origin='effect', entry_site="batch_effects._batch_effect:name == 'summon_discarded_copy'", entry_source=ctx.get('source'))
        elif name=='destroy_random_other':
            candidates=[m for player in self.players for m in player.minions if m is not source]
            if candidates:self.rng.choice(candidates).health=0
        elif name=='freeze_neighbors_destroy_damaged':
            if target:
                chosen=self._find(target);board=self.players[chosen.owner].board
                position=board.index(chosen)
                selected=[m for m in board[max(0,position-1):position+2] if m in self.players[chosen.owner].minions]
                damaged=[m for m in selected if m.health<m.max_health]
                for m in selected:self._freeze(m.uid)
                for m in damaged:m.health=0
        elif name=='empty_deck_destroy_enemy_top':
            if not p.deck:
                for _ in range(min(op[1],len(q.deck))):
                    card=q.deck.pop()
                    self._zone_card_removed(1-owner,card,'deck','destroy')
                    self._log('destroy_deck_card',player=1-owner,card=self._card_data(card)['id'])
                self._refresh_auras()
        elif name=='keyword_or_copy':
            if target:
                chosen=self._find(target)
                if op[1] in chosen.keywords:
                    self._summon(owner,chosen.card_id,p.board.index(chosen)+1,copy_from=chosen, entry_origin='copy', entry_site="batch_effects._batch_effect:name == 'keyword_or_copy'", entry_source=ctx.get('source'))
                else:chosen.keywords.add(op[1])
        elif name=='corpse_copy':
            if source is not None and p.corpses>=op[1] and len(p.board)<7:
                self._spend_corpses(owner,op[1])
                self._system_effect(('copy_self_right',1),ctx)
        elif name=='low_health_buff_copy':
            if source is not None and p.health<=op[1]:
                self._buff(source,op[2],op[3])
                self._system_effect(('copy_self_right',1),ctx)
        elif name=='attack_threshold_copy':
            if source is not None and source.attack>=op[1]:
                self._system_effect(('copy_self_right',1),ctx)
        elif name=='spell_damage_turn_copy':
            if p.spell_damage_turn:self._system_effect(('copy_self_right',1),ctx)
        elif name=='death_threshold_missiles':
            if len(p.death_history)>=op[1]:self._effect(('missiles','enemies',op[2]),ctx)
        elif name=='kindred':
            if ctx.get('kindred'):
                for operation in op[1]:
                    self._effect(operation,ctx);self._settle()
                    if self.terminal:break
        elif name=='enemy_edges_damage':
            selected=q.minions[:1]+q.minions[-1:]
            with self._damage_batch():
                for uid in dict.fromkeys(m.uid for m in selected):self._deal_effect(uid,op[1],ctx)
        elif name=='others_keyword':
            for m in p.minions:
                if m is not source:m.keywords.add(op[1])
        elif name=='kindred_random_damage_freeze':
            selected=self.rng.sample(q.minions,min(len(q.minions),op[2]))
            with self._damage_batch():
                for m in selected:
                    self._deal_effect(m.uid,op[1],ctx)
                    if ctx.get('kindred'):self._freeze(m.uid)
        elif name=='kindred_cost_draw_one':
            c=self._draw_filtered(owner,(('type','eq','MINION'),('cost','eq',op[1])))
            if c and ctx.get('kindred'):c.cost_delta=getattr(c,'cost_delta',0)-ctx.get('kindred_repeats',1)
        elif name=='kindred_cost_draws':
            for cost in range(1,5):
                c=self._draw_filtered(owner,(('type','eq','MINION'),('cost','eq',cost)))
                if c and ctx.get('kindred'):c.cost_delta=getattr(c,'cost_delta',0)-ctx.get('kindred_repeats',1)
        elif name=='kindred_destroy_attack':
            if q.minions:
                attack=(max if ctx.get('kindred') else min)(m.attack for m in q.minions)
                self.rng.choice([m for m in q.minions if m.attack==attack]).health=0
        elif name=='kindred_discard':
            victim=1-owner if ctx.get('kindred') else owner
            hand=self.players[victim].hand
            if hand:
                self._discard_card(victim,self.rng.choice(hand))
        elif name=='trigger_cinders':
            for m in list(p.minions):
                if m.card_id=='TLC_249' and not m.silenced:
                    self._effect(('missiles','enemies',2),dict(owner=owner,source=m,target=0,bonus=0,lifesteal=False))
                    self._settle()
                    if self.terminal:break
        elif name=='source_attack_damage':self._deal_effect(target,max(0,source.attack),ctx)
        elif name=='kindred_destroy_gain':
            if target:
                m=self._find(target);attack,health=m.attack,m.health;m.health=0
                self._settle()
                if ctx.get('kindred') and source in p.minions:self._buff(source,attack*ctx.get('kindred_repeats',1),max(0,health)*ctx.get('kindred_repeats',1))
        elif name=='kindred_deathrattle_draw':
            c=self._draw_filtered(owner,(('type','eq','MINION'),('mechanic','eq','DEATHRATTLE'),('cost','le',3)))
            if c and ctx.get('kindred'):self._set_card_cost(c,0)
        elif name=='filtered_draw':
            for _ in range(op[2]):
                c=self._draw_filtered(owner,op[1])
                if c and len(op)>3:c.cost_delta=getattr(c,'cost_delta',0)+op[3]
        elif name=='zone_minion_buff':
            for zone in op[1]:
                if zone not in ('hand','deck'):raise ValueError('Unsupported buff zone')
                cards=getattr(p,zone)
                for index,value in enumerate(cards):
                    data=self._card_data(value)
                    if data['type']!='MINION' or (len(op)>4 and data.get('rarity')!=op[4]):continue
                    if not isinstance(value,Card):
                        value=Card(self._new_id(),value);cards[index]=value
                    value.attack_bonus+=op[2];value.health_bonus+=op[3]
        elif name=='set_bottom_cost':
            for index in range(min(op[1],len(p.deck))):
                value=p.deck[index]
                if not isinstance(value,Card):
                    value=Card(self._new_id(),value);p.deck[index]=value
                self._set_card_cost(value,op[2])
        elif name=='draw_bottom':
            for _ in range(op[1]):
                self._draw_index(owner,0)
                if self._check_heroes():break
        elif name=='draw_distinct_costs':
            used=set()
            for _ in range(op[1]):
                choices=[i for i,v in enumerate(p.deck) if self._card_stat(v,'cost') not in used]
                if not choices:break
                i=self.rng.choice(choices);used.add(self._card_stat(p.deck[i],'cost'))
                self._draw_index(owner,i)
        elif name=='draw_if_cheap':
            c=self._draw(owner)
            if c and self._cost(c,owner)<=op[1]:self._draw(owner)
        elif name=='draw_minions_mana_buff':
            drawn=[self._draw_filtered(owner,(('type','eq','MINION'),)) for _ in range(op[1])]
            if p.max_mana>=op[2]:
                for c in drawn:
                    if c:c.attack_bonus+=op[3];c.health_bonus+=op[4]
        elif name=='barnabus_draw':
            c=self._draw_filtered(owner,(('type','eq','MINION'),))
            if c and self._card_stat(c,'attack',owner)>=5:c.health_bonus+=5;self._gain_armor(owner,5)
        elif name=='all_zone_tribe_buff':
            tribe,attack,health=op[1:]
            for c in p.hand:
                if has_tribe(self.cards[c.card_id],tribe):c.attack_bonus+=attack;c.health_bonus+=health
            for i,v in enumerate(p.deck):
                if has_tribe(self._card_data(v),tribe):
                    c=v if isinstance(v,Card) else Card(self._new_id(),v)
                    c.attack_bonus+=attack;c.health_bonus+=health;p.deck[i]=c
            for m in p.minions:
                if has_tribe(self.cards[m.card_id],tribe):self._buff(m,attack,health)
        elif name=='top_deck_minion_buff':
            left=op[1]
            for i in range(len(p.deck)-1,-1,-1):
                v=p.deck[i]
                if self._card_data(v)['type']!='MINION':continue
                c=v if isinstance(v,Card) else Card(self._new_id(),v)
                c.attack_bonus+=op[2];c.health_bonus+=op[3];p.deck[i]=c
                left-=1
                if not left:break
        elif name=='shuffle_matching_enemy_hand':
            held={c.card_id for c in p.hand}
            candidates=[c for c in q.hand if c.card_id in held]
            if candidates:self._shuffle_hand_card(1-owner,self.rng.choice(candidates),actor=owner)
        elif name=='shuffle_left_hand':
            if p.hand:self._shuffle_hand_card(owner,p.hand[0])
        elif name=='outcast_hero_immune':
            if ctx.get('outcast'):p.hero_immune_expiry_players.append(owner)
        elif name=='draw_extreme_cost':
            filters=self._validate_filters(op[1])
            if op[2] not in ('highest','lowest'):raise ValueError('Invalid cost extremum')
            candidates=[(i,self._card_stat(card,'cost',owner)) for i,card in enumerate(p.deck) if self._matches_filter(card,filters,zone_owner=owner)]
            if candidates:
                cost=(max if op[2]=='highest' else min)(cost for _,cost in candidates)
                self._draw_index(owner,self.rng.choice([i for i,value in candidates if value==cost]))
        elif name=='summon_target_copy':
            chosen=op[1]
            self._summon(owner,chosen.card_id,copy_from=chosen,entry_origin='copy',
                         entry_site='fill_board_target_copies',entry_source=ctx.get('source'))
        elif name=='fill_board_target_copies':
            chosen=next((m for m in p.minions if m.uid==target and m.health>0),None)
            if chosen is not None:
                for _ in range(7-len(p.board)):
                    self._summon(owner,chosen.card_id,copy_from=chosen, entry_origin='copy', entry_site="batch_effects._batch_effect:name == 'fill_board_target_copies'", entry_source=ctx.get('source'))
        elif name=='copy_damaged_board':
            originals=[m for m in p.minions if 0<m.health<m.max_health]
            for original in originals:
                if len(p.board)>=7:break
                copied=self._summon(owner,original.card_id,copy_from=original, entry_origin='copy', entry_site="batch_effects._batch_effect:name == 'copy_damaged_board'", entry_source=ctx.get('source'))
                if copied is not None and not copied.dormant:copied.keywords.add(op[1])
        elif name=='summon_from_zone':
            self._recruit_from_zone(owner,op[1],op[2],
                position=min(ctx['death_position'],len(p.board)) if 'death_position' in ctx else -1,
                keyword=op[3] if len(op)>3 else None)
        elif name=='draw_type_keyword':
            drawn=[]
            for _ in range(op[1]):
                card=self._draw(owner,include_burned=True)
                if card is not None:drawn.append(card)
                if self._check_heroes():return True
            if len(drawn)==op[1] and all(self.cards[c.card_id]['type']==op[2] for c in drawn):
                if source is not None and source in p.minions and source.health>0:source.keywords.add(op[3])
        elif name=='opponent_draw_copy':
            drawn=[]
            for _ in range(op[1]):
                card=self._draw(1-owner,include_burned=True)
                if card is not None:drawn.append(deepcopy(card))
                if self._check_heroes():return True
            for card in drawn:self._clone_hand_card(owner,card,source_owner=1-owner)
        elif name=='discount_hand_position':
            if p.hand:self._discount_cards([p.hand[op[1]]],op[2])
        elif name=='discount_distinct_cost_hand':
            costs=[self._cost(card,owner) for card in p.hand]
            if len(costs)==len(set(costs)):self._discount_cards(p.hand,op[1])
        elif name=='discount_random_hand':
            if op[1] not in ('friendly','enemy'):raise ValueError('Invalid hand side')
            recipient=owner if op[1]=='friendly' else 1-owner
            filters=self._validate_filters(op[2])
            candidates=[c for c in self.players[recipient].hand if self._matches_filter(c,filters,hand_owner=recipient)]
            if candidates:
                self._discount_cards([self.rng.choice(candidates)],op[3])
        elif name=='prevent_enemy_hero_healing_until_next_turn':
            q.healing_block_expiry_players.append(owner)
        elif name=='copy_random_hand_any':
            alternatives=[self._validate_filters(filters) for filters in op[1]]
            candidates=[c for c in p.hand if any(self._matches_filter(c,filters,hand_owner=owner) for filters in alternatives)]
            if candidates:
                self._clone_hand_card(owner,self.rng.choice(candidates))
                self._refresh_auras()
        elif name=='copy_lowest_enemy_hand':
            if q.hand:
                costs=[self._cost(c,1-owner) for c in q.hand]
                lowest=min(costs)
                chosen=self.rng.choice([c for c,cost in zip(q.hand,costs) if cost==lowest])
                self._clone_hand_card(owner,chosen,source_owner=1-owner)
                self._refresh_auras()
        elif name=='copy_lowest_hand_tribe':
            choices=[c for c in p.hand if has_tribe(self.cards[c.card_id],op[1])]
            if choices:
                cost=min(self._cost(c,owner) for c in choices)
                self._clone_hand_card(owner,self.rng.choice([c for c in choices if self._cost(c,owner)==cost]))
        elif name=='damage_owner_draw':
            if target:
                other=self._find(target).owner
                self._deal_effect(target,op[1],ctx);self._settle()
                if not self.terminal:self._draw(other)
        elif name=='tribe_board_buff':
            for m in p.minions:
                if has_tribe(self.cards[m.card_id],op[1]):self._buff(m,op[2],op[3])
        elif name=='source_health_damage':
            self._deal_effect(target,max(0,source.health),ctx)
        elif name=='source_health_heal':
            if target:self._heal(target,max(0,source.health),healer=owner,spell=ctx.get('spell',False))
        elif name=='buff_self_damaged_count':
            count=sum(m.health<m.max_health for player in self.players for m in player.minions)
            self._buff(source,count*op[1],count*op[2])
        elif name=='small_others_buff':
            selected=[m for m in p.minions if m is not source and m.attack<=op[1]]
            for m in selected:self._buff(m,op[2],op[3]);m.keywords.add(op[4])
        elif name=='destroy_not_class':
            for player in self.players:
                for m in player.minions:
                    d=self.cards[m.card_id]
                    if op[1] not in (d.get('classes') or [d.get('cardClass')]):m.health=0
        elif name=='destroy_battlefield':
            for player in self.players:
                for location in list(player.locations):
                    self._remove_location(location)
                for m in player.minions:m.health=0
            self._refresh_auras()
        elif name=='destroy_random_enemy_location':
            if q.locations:
                location=self.rng.choice(q.locations)
                self._remove_location(location)
                self._refresh_auras()
        elif name=='destroy_location':
            if target:
                location=next(x for player in self.players for x in player.locations if x.uid==target)
                self._remove_location(location)
                self._refresh_auras()
        elif name=='fire_turn_destroy':
            if p.fire_spell_played and target:self._find(target).health=0
        elif name=='combo_add':
            if ctx.get('combo'):self._add(owner,op[1])
        elif name=='damage_buff_attack':
            if target:
                m=self._find(target);self._deal_effect(target,op[1],ctx);self._buff(m,op[2],0)
        elif name=='own_others_damage':
            with self._damage_batch():
                for m in list(p.minions):
                    if m is not source:self._deal_effect(m.uid,op[1],ctx)
        elif name=='summon_opponent':
            for _ in range(op[2]):self._summon(1-owner,op[1], entry_origin='effect', entry_site="batch_effects._batch_effect:name == 'summon_opponent'", entry_source=ctx.get('source'))
        elif name=='choose_hand_discard':
            if self.pending_choice is not None:raise ValueError('A choice is already pending')
            if p.hand:
                self.pending_choice=dict(owner=owner,kind='hand_discard',options=[dict(card_id=c.card_id,uid=c.uid) for c in p.hand])
                if len(op)>1 and op[1]=='remember':self.pending_choice['remember_source']=source.uid
                self.phase='choice'
        elif name=='choose_hand_shuffle':
            if self.pending_choice is not None:raise ValueError('A choice is already pending')
            if p.hand:
                self.pending_choice=dict(owner=owner,kind='hand_shuffle',options=[dict(card_id=c.card_id,uid=c.uid) for c in p.hand])
                self.phase='choice'
        elif name=='choose_hand_copy':
            filters=self._validate_filters(op[1])
            options=[dict(card_id=c.card_id,uid=c.uid) for c in p.hand if self._matches_filter(c,filters,hand_owner=owner)]
            if self.pending_choice is not None:raise ValueError('A choice is already pending')
            if options:
                self.pending_choice=dict(owner=owner,kind='hand_copy',options=options)
                self.phase='choice'
        elif name=='choose_hand_transform':
            require_fixed_cards((op[1],),self.cards)
            if self.pending_choice is not None:raise ValueError('A choice is already pending')
            if p.hand:
                self.pending_choice=dict(owner=owner,kind='hand_transform',replacement=op[1],
                    options=[dict(card_id=c.card_id,uid=c.uid) for c in p.hand])
                self.phase='choice'
        elif name=='choose_self_effect':
            if source is None:return True
            if self.pending_choice is not None:raise ValueError('A choice is already pending')
            self.pending_choice=dict(owner=owner,kind='self_effect',source_uid=source.uid,
                options=[dict(card_id=source.card_id,label=label,operation=effect) for label,effect in op[1]])
            self.phase='choice'
        elif name=='choose_fixed_summon':
            require_fixed_cards(op[1],self.cards)
            if self.pending_choice is not None:raise ValueError('A choice is already pending')
            self.pending_choice=dict(owner=owner,kind='fixed_summon',options=[dict(card_id=cid) for cid in op[1]])
            self.phase='choice'
        elif name=='summon_fixed_random':
            require_fixed_cards(op[1],self.cards)
            self._summon(owner,self.rng.choice(op[1]), entry_origin='effect', entry_site="batch_effects._batch_effect:name == 'summon_fixed_random'", entry_source=ctx.get('source'))
        elif name=='summon_source_stats':
            d=self.cards[op[1]]
            self._summon(owner,op[1],attack_bonus=max(0,source.attack)-d['attack'],health_bonus=max(1,source.health)-d['health'], entry_origin='effect', entry_site="batch_effects._batch_effect:name == 'summon_source_stats'", entry_source=ctx.get('source'))
        elif name=='buff_other_damaged':
            choices=[m for m in p.minions if m is not source and m.health<m.max_health]
            if choices:self._buff(self.rng.choice(choices),op[1],op[2])
        elif name=='shield_or_buff':
            for m in p.minions:
                if 'DIVINE_SHIELD' in m.keywords:self._buff(m,op[1],op[2])
                else:m.keywords.add('DIVINE_SHIELD')
        elif name=='buff_damaged_board':
            for m in p.minions:
                if m.health<m.max_health:self._buff(m,op[1],op[2])
        elif name=='healed_this_turn_self_buff':
            if p.healing_done_turn and source:self._buff(source,op[1],op[2])
        elif name=='hero_damaged_self_buff':
            if p.hero_damage_taken_turn and source:self._buff(source,op[1],op[2])
        elif name=='discount_hand_neighbors':
            neighbors=ctx.get('hand_neighbors',())
            for card in p.hand:
                if card.uid in neighbors:card.cost_delta=getattr(card,'cost_delta',0)-op[1]
        elif name=='hand_attack_types':
            if not set(op[1]) <= {'MINION','WEAPON'}:raise ValueError('Unsupported hand Attack card type')
            for card in p.hand:
                if self.cards[card.card_id]['type'] in op[1]:card.attack_bonus+=op[2]
        elif name=='if_holding':
            filters=self._validate_filters(op[1])
            if self._holding_matches(owner,filters):self._effect(op[2],ctx)
            elif len(op)>3:self._effect(op[3],ctx)
        elif name=='damage_hand_center':
            self._deal_effect(target,op[2] if ctx.get('hand_center') else op[1],ctx)
        elif name=='held_keywords':
            filters=self._validate_filters(op[1])
            if self._holding_matches(owner,filters):source.keywords.update(op[2])
        elif name=='weapon_buff_or_equip':
            if p.weapon:self._buff_weapon(owner,attack=op[1])
            else:self._equip(owner,op[2])
        elif name=='deck_size_draw':
            if len(p.deck)>=op[1]:self._draw(owner)
        elif name=='tribal_damage':
            if target:
                chosen=self._find(target);tribes=set(self.cards[chosen.card_id].get('races',[]))
                targets=[m.uid for player in self.players for m in player.minions if m is chosen or shares_tribe(self.cards[chosen.card_id],self.cards[m.card_id])]
                with self._damage_batch():
                    for uid in targets:self._deal_effect(uid,op[1],ctx)
        elif name=='excess_draw':
            if target:
                before=max(0,self._find(target).health)
                dealt=self._deal_effect(target,op[1],ctx);self._settle()
                for _ in range(max(0,dealt-before)):
                    if self.terminal:break
                    self._draw(owner)
        elif name=='aoe_draw_dead':
            victims=[m for player in self.players for m in player.minions]
            with self._damage_batch():
                for m in victims:self._deal_effect(m.uid,op[1],ctx)
            self._settle()
            count=sum(not any(m is survivor for p2 in self.players for survivor in p2.minions) for m in victims)
            for _ in range(count):
                if self.terminal:break
                self._draw(owner)
        elif name=='damage_summon_count':
            dealt=self._deal_effect(target,op[1],ctx);self._settle()
            if not self.terminal:
                for _ in range(min(dealt,7-len(p.board))):self._summon(owner,op[2], entry_origin='effect', entry_site="batch_effects._batch_effect:name == 'damage_summon_count'", entry_source=ctx.get('source'))
        elif name=='random_minion_damage_draw_kills':
            selected=self.rng.sample(q.minions,min(len(q.minions),op[2]))
            with self._damage_batch():
                for victim in selected:self._deal_effect(victim.uid,op[1],ctx)
            killed=sum(victim.health<=0 for victim in selected)
            self._settle()
            if not self.terminal:
                for _ in range(killed):
                    self._draw(owner)
                    if self._check_heroes():break
        elif name=='random_distinct_damage':
            choices=[self.hero_id(1-owner)]+[m.uid for m in q.minions]
            selected=self.rng.sample(choices,min(len(choices),op[2]))
            with self._damage_batch():
                for uid in selected:self._deal_effect(uid,op[1],ctx)
        elif name=='damage_other_random':
            choices=[u for u in [self.hero_id(1-owner)]+[m.uid for m in q.minions] if u!=target]
            selected=self.rng.sample(choices,min(len(choices),op[3]))
            with self._damage_batch():
                self._deal_effect(target,op[1],ctx)
                for uid in selected:self._deal_effect(uid,op[2],ctx)
        elif name=='freeze_random_enemies':
            selected=self.rng.sample(q.minions,min(len(q.minions),op[1]))
            for m in selected:self._freeze(m.uid)
        elif name=='frail_ghoul':
            self._summon(owner,op[1],expires=True, entry_origin='effect', entry_site="batch_effects._batch_effect:name == 'frail_ghoul'", entry_source=ctx.get('source'))
        else:return False
        return True
