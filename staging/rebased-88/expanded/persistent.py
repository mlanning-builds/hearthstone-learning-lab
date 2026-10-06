"""Shared attached-card modifiers, persistent identity buffs, and choices."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .selectors import has_tribe


class PersistentEffects:
    def _is_recruit(self,cid):
        return self.cards[cid]['name']=='Silver Hand Recruit'

    def _persistent_choice(self,choice,selected):
        owner=choice['owner'];p=self.players[owner];kind=choice['kind']
        if kind=='held_modifier':
            c=next((c for c in p.hand if c.uid==selected['uid']),None)
            if c is None:raise UnsupportedCard('Chosen card left hand')
            mode=choice['mode'];amount=choice['amount']
            if mode=='spell_damage':c.spell_damage_bonus=getattr(c,'spell_damage_bonus',0)+amount
            elif mode=='growing_discount':c.growing_discounts=getattr(c,'growing_discounts',[])+[dict(owner=owner,amount=amount)]
            elif mode=='radiating_discount':
                center=p.hand.index(c)
                for i,card in enumerate(p.hand):card.cost_delta=getattr(card,'cost_delta',0)-max(0,amount-abs(i-center))
            else:raise UnsupportedCard('Unknown held modifier')
        elif kind=='rightmost':
            other=self.players[1-owner];c=next((c for c in other.hand if c.uid==choice['uid']),None)
            if c is not None:
                if selected['mode']=='copy':self._clone_hand_card(owner,c,source_owner=1-owner)
                else:c.cost_delta=getattr(c,'cost_delta',0)+2
        elif kind=='persistent_effect':
            ctx=choice['context'];op=selected['operation']
            if choice.get('remember_keyword'):ctx.setdefault('selected_keywords',[]).append(op[1])
            self._effect(op,ctx)
        elif kind=='steal_health':
            source=choice['source'];m=next((m for player in self.players for m in player.minions if m.uid==selected['uid']),None)
            if m is not None:
                self._buff(m,0,-choice['amount'])
                if source in p.minions:self._buff(source,0,choice['amount'])
        else:return False
        return True

    def _effect_choice(self,ctx,options,remember=False):
        if options:
            self.pending_choice=dict(owner=ctx['owner'],kind='persistent_effect',context=ctx,
                remember_keyword=remember,options=[dict(card_id=ctx['source'].card_id,label=label,operation=op) for label,op in options])
            self.phase='choice'

    def _persistent_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];q=self.players[1-owner]
        source=ctx.get('source');target=ctx.get('target',0)
        if name=='recruit_bonus':
            p.recruit_attack_bonus+=op[1];p.recruit_health_bonus+=op[2]
            for m in p.minions:
                if self._is_recruit(m.card_id):self._buff(m,op[1],op[2])
        elif name=='one_shield_recruit':
            m=self._summon(owner,'CS2_101t',entry_origin='effect',entry_site='shield_recruit',entry_source=source)
            if m is not None:m.keywords.add('DIVINE_SHIELD')
        elif name=='double_recruits':
            for m in p.minions:
                if self._is_recruit(m.card_id):self._buff(m,m.attack,m.health);m.keywords.add('TAUNT')
        elif name=='choose_held_modifier':
            options=[dict(card_id=c.card_id,uid=c.uid) for c in p.hand if op[1]!='spell_damage' or self.cards[c.card_id]['type']=='SPELL']
            if options:self.pending_choice=dict(owner=owner,kind='held_modifier',mode=op[1],amount=op[2],options=options);self.phase='choice'
        elif name=='zone_spell_damage':
            for zone in (p.hand,p.deck):
                for i,c in enumerate(zone):
                    if self._card_data(c)['type']=='SPELL':
                        if not isinstance(c,Card):c=Card(self._new_id(),c);zone[i]=c
                        c.spell_damage_bonus=getattr(c,'spell_damage_bonus',0)+op[1]*ctx.get('kindred_repeats',1)
        elif name=='add_spell_damage':
            if len(p.hand)<10:
                self._add(owner,op[1]);p.hand[-1].spell_damage_bonus=op[2]
            else:self._add(owner,op[1])
        elif name=='draw_fire_spell_damage':
            c=self._draw_filtered(owner,(('school','eq','FIRE'),))
            if c is not None and ctx.get('kindred'):c.spell_damage_bonus=getattr(c,'spell_damage_bonus',0)+op[1]*ctx.get('kindred_repeats',1)
        elif name=='inspect_rightmost':
            if q.hand:
                c=q.hand[-1];self.pending_choice=dict(owner=owner,kind='rightmost',uid=c.uid,
                    options=[dict(card_id=c.card_id,label='Copy',mode='copy'),dict(card_id=c.card_id,label='Increase cost',mode='tax')]);self.phase='choice'
        elif name=='choose_corpses_stats':
            self._effect_choice(ctx,[(str(n)+' Corpses',('spend_corpses_stats',n)) for n in (10,20,30) if p.corpses>=n])
        elif name=='spend_corpses_stats':
            if p.corpses>=op[1]:self._spend_corpses(owner,op[1]);self._buff(source,op[1],op[1])
        elif name=='choose_unique_keyword':
            self._effect_choice(ctx,[(key,('keyword_self',key)) for key in ('RUSH','TAUNT','DIVINE_SHIELD','WINDFURY') if key not in ctx.get('selected_keywords',[])],remember=True)
        elif name=='inherit_deathrattles_turn':
            for record in p.death_records:
                if record['turn']==self.turn:source.attached_death_effects.extend(deepcopy(record['operations']))
        elif name=='choose_cenarius':
            self._effect_choice(ctx,[('Growth',('buff_other_minions',1,3)),('Ancient',('summon','EDR_209t5',1))])
        elif name=='buff_other_minions':
            for m in p.minions:
                if m is not source:self._buff(m,op[1],op[2])
        elif name=='combo_overload_keywords':
            if ctx.get('combo'):
                p.overload_next+=2;p.overloaded_total+=2
                self._temporary_keyword(source,'IMMUNE','end');source.keywords.add('WINDFURY')
        elif name=='at_current_end_add':
            self._schedule_turn_effect(self.current,'end',0,1,(('add_to_player',owner,op[1]),))
        elif name=='add_to_player':self._add(op[1],op[2])
        elif name=='return_spell_if_dead':
            if any(r.get('entity') is not None and r['entity'].uid==target for player in self.players for r in player.death_records):
                self._schedule_turn_effect(owner,'end',0,1,(('add','END_025',1),))
        elif name=='resistance_aura':
            start=self.turn+1;q.timed_cost_increases.append(dict(selector='SPELL',amount=1,start=start,end=start+2+2*getattr(ctx.get('physical_card'),'rule_state',{}).get('aura_duration_delta',0),aura_owner=owner,source_card_id='TTN_851'))
        elif name=='draw_locked':
            c=self._draw(owner)
            if c is not None:c.play_lock=dict(owner=owner,until=p.turns_taken+2)
        elif name=='bounce_locked':
            if target:
                m=self._find(target);recipient=m.owner;hand=self.players[recipient].hand;before=len(hand);self._bounce(m)
                if len(hand)>before:hand[-1].play_lock=dict(owner=recipient,until=self.players[recipient].turns_taken+2)
        elif name=='fill_enemy_deck_copies':
            if q.deck:
                for _ in range(10-len(p.hand)):
                    value=self.rng.choice(q.deck);card=deepcopy(value) if isinstance(value,Card) else Card(self._new_id(),value)
                    card.cost_delta=getattr(card,'cost_delta',0)-op[1];self._clone_hand_card(owner,card,source_owner=1-owner)
        elif name=='reveal_spell_missiles':
            options=[c for c in p.deck if self._card_data(c)['type']=='SPELL']
            if options:
                c=self.rng.choice(options);self._log('reveal',player=owner,card=self._card_data(c)['id'])
                if self._card_stat(c,'cost',owner)>=op[1]:self._effect(('missiles','enemy_minions',op[2]),ctx)
        elif name=='recruit_deck_uid':
            index=next((i for i,c in enumerate(p.deck) if getattr(c,'uid',None)==op[1]),None)
            if len(p.board)<7 and index is not None:
                c=p.deck.pop(index);self._summon(owner,self._card_data(c)['id'],attack_bonus=getattr(c,'attack_bonus',0),health_bonus=getattr(c,'health_bonus',0),entry_origin='recruit',entry_zone='deck',entry_site='bottom_demons',entry_source=c)
                self._refresh_auras()
        elif name=='discard_entire_hand':self._discard_cards(owner,list(p.hand))
        elif name=='choose_steal_health':
            visible=set(self._visible_targets(owner));options=[dict(card_id=m.card_id,uid=m.uid) for m in q.minions if m.uid in visible]
            if options:self.pending_choice=dict(owner=owner,kind='steal_health',source=source,amount=op[1],options=options);self.phase='choice'
        else:return False
        return True
