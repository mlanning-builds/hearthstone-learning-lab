"""Composed effects, private physical-card choices, and attached effects.

No card text parsing or global generation-pool approximation is used here.
"""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .selectors import has_class
from .pools import deck_choice_options


class ComposedEffects:
    def _temporary_keyword(self,m,keyword,expiry):
        if m.dormant:return
        m.temporary_keywords.append(dict(keyword=keyword,phase='start' if expiry=='next_start' else 'end',
                                         turn=self.turn+2 if expiry=='next_start' else self.turn))

    def _set_entity_stats(self,m,attack,health):
        self._set_minion_attack(m,attack+m.aura_attack)
        m.health=m.max_health=health+m.aura_health
        m.temporary_attack=0

    def _open_zone_choice(self,owner,zone_owner,zone,mode):
        values=getattr(self.players[zone_owner],zone)
        options=deck_choice_options(values,self.cards,3,self.rng)
        if not options:return
        # Index is used only while a choice freezes the game; snapshots preserve
        # the selected physical copy's enchantments for copy effects.
        for option in options:option['snapshot']=deepcopy(values[option['index']])
        self.pending_choice=dict(owner=owner,kind='composed_zone',zone_owner=zone_owner,
                                 zone=zone,mode=mode,options=options)
        self.phase='choice'

    def _composed_choice(self,choice,selected):
        owner=choice['owner'];p=self.players[owner]
        if choice['kind']=='composed_zone':
            values=getattr(self.players[choice['zone_owner']],choice['zone']);mode=choice['mode']
            if mode=='copy':
                value=selected['snapshot']
                card=deepcopy(value) if isinstance(value,Card) else Card(self._new_id(),value)
                self._discovery_result=self._clone_hand_card(owner,card,source_owner=choice['zone_owner'] if choice['zone_owner']!=owner else None)
            elif mode=='top':
                values.append(values.pop(selected['index']))
            elif mode=='draw_bottom':
                chosen=values[selected['index']]
                rejected=[values[o['index']] for o in choice['options'] if o is not selected]
                for index in sorted([o['index'] for o in choice['options']],reverse=True):values.pop(index)
                self.rng.shuffle(rejected);values[0:0]=rejected
                if len(p.hand)<10:self._discovery_result=self._enter_hand(owner,chosen if isinstance(chosen,Card) else Card(self._new_id(),chosen))
                else:
                    self._burn_deck_card(owner,chosen)
            else:raise UnsupportedCard('Unknown zone choice mode')
            self._refresh_auras();return True
        if choice['kind']=='composed_attack':
            if selected['zone']=='hand':
                card=next((c for c in p.hand if c.uid==selected['uid']),None)
                if card is not None:card.attack_bonus+=choice['amount']
            else:
                m=next((m for m in p.minions if m.uid==selected['uid']),None)
                if m is not None:self._buff(m,choice['amount'],0)
            return True
        if choice['kind']=='composed_draw':
            card=next((c for c in p.hand if c.uid==selected['uid']),None)
            if card is None:raise UnsupportedCard('Chosen drawn card left hand')
            if choice['mode']=='discount':card.cost_delta=getattr(card,'cost_delta',0)-choice['amount']
            elif choice['mode']=='give':
                p.hand.remove(card);other=self.players[1-owner]
                if len(other.hand)<10:self._enter_hand(1-owner,card)
                else:self._log('burn_generated',player=1-owner,card=card.card_id)
            else:raise UnsupportedCard('Unknown draw choice mode')
            self._refresh_auras();return True
        return False

    def _composed_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner]
        source=ctx.get('source');target=ctx.get('target',0)
        if name=='destroy_crystals':
            p.max_mana=max(0,p.max_mana-op[1]);p.mana=min(p.mana,max(0,p.max_mana-p.locked_mana))
        elif name=='gain_full_crystals':
            gained=min(op[1],p.mana_capacity-p.max_mana);p.max_mana+=gained;p.mana=min(p.mana_capacity,p.mana+gained)
        elif name in ('temporary_keyword_self','temporary_keyword_target'):
            m=source if name.endswith('self') else next((m for player in self.players for m in player.minions if m.uid==target),None)
            if m is not None:self._temporary_keyword(m,op[1],op[2])
        elif name in ('grant_death_self','grant_death_target'):
            m=source if name.endswith('self') else next((m for player in self.players for m in player.minions if m.uid==target),None)
            if m is not None:m.attached_death_effects.extend(deepcopy(op[1]))
        elif name=='set_target_stats':
            m=next((m for player in self.players for m in player.minions if m.uid==target),None)
            if m is not None:self._set_entity_stats(m,op[1],op[2])
        elif name=='swap_self_stats':
            if source is not None and source.health>0:self._set_entity_stats(source,source.health,source.attack)
        elif name=='refresh_source_attack':
            if source is not None:self._effect(('refresh_mana',source.attack),ctx)
        elif name=='class_board_buff':
            for m in p.minions:
                if has_class(self.cards[m.card_id],op[1]):self._buff(m,op[2],op[3])
        elif name=='event_minion_keyword':
            uid=ctx.get('event',{}).get('source')
            m=next((m for m in p.minions if m.uid==uid),None)
            if m is not None:m.keywords.add(op[1])
        elif name=='weapon_previous_runes':
            if p.weapon and p.played_history:
                runes=self.cards[p.played_history[-1]['card_id']].get('runeCost',{})
                self._buff_weapon(owner,int(bool(runes.get('unholy',0))),int(bool(runes.get('blood',0))))
        elif name=='corpse_target_damage':
            if target and p.corpses>=op[1]:
                self._spend_corpses(owner,op[1]);self._deal_effect(target,op[2],ctx)
        elif name=='outcast_operation':
            if ctx.get('outcast'):self._effect(op[1],ctx)
        elif name=='when_health_changed':
            if p.hero_health_changed_turn:self._effect(op[1],ctx)
        elif name=='summon_identity_buff':
            self._summon(owner,op[1],attack_bonus=op[2],health_bonus=op[2],entry_origin='effect',entry_source=source,entry_site='death_identity')
        elif name=='shuffle_dead_target':
            records=[r for player in self.players for r in player.death_records if r.get('entity') is not None and r['entity'].uid==target]
            if records:
                card=Card(self._new_id(),records[-1]['card_id']);self._set_card_cost(card,op[1])
                p.deck.append(card);self.rng.shuffle(p.deck);self._record_deck_insertion(owner,owner,1,'shuffle')
        elif name=='draw_summon_set_stats':
            card=self._draw(owner,lambda d:d['type']=='MINION',include_burned=True)
            if card is not None:
                data=self.cards[card.card_id]
                m=self._summon(owner,card.card_id,attack_bonus=op[1]-data['attack'],health_bonus=op[2]-data['health'],entry_origin='effect',entry_source=source,entry_site='draw_summon_set_stats')
                if m is not None:m.keywords.add(op[3])
        elif name=='choose_attack_recipient':
            if source is not None:
                options=[dict(card_id=c.card_id,uid=c.uid,zone='hand') for c in p.hand if self.cards[c.card_id]['type']=='MINION']
                options += [dict(card_id=m.card_id,uid=m.uid,zone='board') for m in p.minions]
                if options:
                    self.pending_choice=dict(owner=owner,kind='composed_attack',amount=source.attack,options=options)
                    self.phase='choice'
        elif name=='zone_choice':
            self._open_zone_choice(owner,owner if op[1]=='friendly' else 1-owner,op[2],op[3])
        elif name=='draw_pick':
            drawn=[]
            for _ in range(op[1]):
                card=self._draw(owner)
                if card is not None:drawn.append(card)
                if self._check_heroes():break
            if drawn and not self.terminal:
                self.pending_choice=dict(owner=owner,kind='composed_draw',mode=op[2],amount=op[3],options=[dict(card_id=c.card_id,uid=c.uid) for c in drawn if c in p.hand])
                self.phase='choice'
        elif name=='extreme_draw_transfer':
            if p.deck:
                values=[self._card_stat(v,'cost',owner) for v in p.deck];edge=(max if op[1]=='high' else min)(values)
                index=self.rng.choice([i for i,cost in enumerate(values) if cost==edge]);recipient=owner if op[2]=='friendly' else 1-owner
                if recipient==owner:self._draw_index(owner,index)
                else:
                    self._take_deck_draw(owner,index,recipient=recipient)
        elif name=='draw_temporary_discount':
            card=self._draw(owner)
            if card is not None:
                card.temporary_cost_discounts=getattr(card,'temporary_cost_discounts',[])+[dict(amount=op[1],end=self.turn)]
        else:return False
        return True
