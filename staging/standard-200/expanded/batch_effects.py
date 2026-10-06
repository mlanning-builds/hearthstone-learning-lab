"""Shared explicit effects for the 200-card milestone; no rules-text execution."""
from copy import deepcopy
from engine.game import Card


class BatchEffects:
    def _kindred(self,cid,owner):
        p=self.players[owner];d=self.cards[cid]
        if d['type']=='SPELL':return bool(d.get('spellSchool') and d['spellSchool'] in p.previous_schools)
        if d['type']!='MINION':return False
        tribes=set(d.get('races',[]))
        return bool(tribes and p.previous_tribes and ('ALL' in tribes or 'ALL' in p.previous_tribes or tribes&p.previous_tribes))

    def _card_data(self,value):
        return self.cards[value.card_id if isinstance(value,Card) else value]

    def _card_stat(self,value,key):
        base=self._card_data(value).get(key,0)
        if not isinstance(value,Card):return base
        bonus={'attack':'attack_bonus','health':'health_bonus','cost':'cost_delta'}.get(key)
        return max(0,base+getattr(value,bonus,0)) if bonus else base

    def _matches_filter(self,value,filters):
        d=self._card_data(value)
        for key,relation,wanted in filters:
            if key=='tribe':
                if wanted not in d.get('races',[]):return False
            elif key=='mechanic':
                if wanted not in d.get('mechanics',[]):return False
            elif key=='type':
                if d['type']!=wanted:return False
            else:
                actual=self._card_stat(value,key)
                if relation=='eq' and actual!=wanted:return False
                if relation=='ge' and actual<wanted:return False
                if relation=='le' and actual>wanted:return False
        return True

    def _draw_index(self,owner,index):
        p=self.players[owner]
        if not p.deck:
            return self._draw(owner)
        value=p.deck.pop(index);cid=self._card_data(value)['id']
        self._refresh_auras()
        if len(p.hand)>=10:
            self._log('burn',player=owner,card=cid);return None
        c=value if isinstance(value,Card) else Card(self._new_id(),cid)
        p.hand.append(c);self._log('draw',player=owner)
        self._refresh_auras()
        return c

    def _draw_filtered(self,owner,filters):
        choices=[i for i,v in enumerate(self.players[owner].deck) if self._matches_filter(v,filters)]
        return self._draw_index(owner,self.rng.choice(choices)) if choices else None

    def _clone_hand_card(self,owner,card):
        p=self.players[owner]
        if len(p.hand)>=10:
            self._log('burn_generated',player=owner,card=card.card_id);return
        clone=deepcopy(card);clone.uid=self._new_id();p.hand.append(clone)

    def _batch_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];q=self.players[1-owner]
        target=ctx.get('target',0);source=ctx.get('source')
        if name=='resurrect_highest':
            choices=[cid for cid in p.death_history if op[1] is None or op[1] in self.cards[cid].get('races',[])]
            if choices:
                highest=max(self.cards[cid]['cost'] for cid in choices)
                self._summon(owner,self.rng.choice([cid for cid in choices if self.cards[cid]['cost']==highest]))
        elif name=='resurrect_costs_reborn':
            for cost in op[1]:
                choices=[cid for cid in p.death_history if self.cards[cid]['cost']==cost]
                if choices:
                    m=self._summon(owner,self.rng.choice(choices))
                    if m:m.keywords.add('REBORN')
        elif name=='resurrect_deathrattle_copies':
            choices=[cid for cid in p.death_history if 'DEATHRATTLE' in self.cards[cid].get('mechanics',[]) and op[1]<=self.cards[cid]['cost']<=op[2] and (not op[3] or cid!=source.card_id)]
            if choices:
                cid=self.rng.choice(choices)
                for _ in range(2):self._summon(owner,cid)
        elif name=='return_last_turn_spells':
            for cid in p.spells_previous:self._add(owner,cid)
        elif name=='summon_played_one_cost':
            for h in p.played_history:
                if h['cost']==1 and self.cards[h['card_id']]['type']=='MINION':self._summon(owner,h['card_id'])
        elif name=='repeat_copy_damage':
            if any(h['card_id']==op[2] for h in p.played_history):self._effect(('area_damage','enemies',op[1]),ctx)
            else:self._deal_effect(target,op[1],ctx)
        elif name=='permanent_end_damage':p.permanent_end_damage.append(op[1])
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
        elif name=='kindred_cost_draws':
            for cost in range(1,5):
                c=self._draw_filtered(owner,(('type','eq','MINION'),('cost','eq',cost)))
                if c and ctx.get('kindred'):c.cost_delta=getattr(c,'cost_delta',0)-1
        elif name=='kindred_destroy_attack':
            if q.minions:
                attack=(max if ctx.get('kindred') else min)(m.attack for m in q.minions)
                self.rng.choice([m for m in q.minions if m.attack==attack]).health=0
        elif name=='kindred_discard':
            victim=1-owner if ctx.get('kindred') else owner
            hand=self.players[victim].hand
            if hand:
                c=self.rng.choice(hand);hand.remove(c);self._log('discard',player=victim,card=c.card_id)
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
                if ctx.get('kindred') and source in p.minions:self._buff(source,attack,max(0,health))
        elif name=='kindred_deathrattle_draw':
            c=self._draw_filtered(owner,(('type','eq','MINION'),('mechanic','eq','DEATHRATTLE'),('cost','le',3)))
            if c and ctx.get('kindred'):c.cost_delta=-self.cards[c.card_id]['cost']
        elif name=='filtered_draw':
            for _ in range(op[2]):
                c=self._draw_filtered(owner,op[1])
                if c and len(op)>3:c.cost_delta=getattr(c,'cost_delta',0)+op[3]
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
            if c and self._card_stat(c,'attack')>=5:c.health_bonus+=5;p.armor+=5
        elif name=='all_zone_tribe_buff':
            tribe,attack,health=op[1:]
            for c in p.hand:
                if tribe in self.cards[c.card_id].get('races',[]):c.attack_bonus+=attack;c.health_bonus+=health
            for i,v in enumerate(p.deck):
                if tribe in self._card_data(v).get('races',[]):
                    c=v if isinstance(v,Card) else Card(self._new_id(),v)
                    c.attack_bonus+=attack;c.health_bonus+=health;p.deck[i]=c
            for m in p.minions:
                if tribe in self.cards[m.card_id].get('races',[]):self._buff(m,attack,health)
        elif name=='top_deck_minion_buff':
            left=op[1]
            for i in range(len(p.deck)-1,-1,-1):
                v=p.deck[i]
                if self._card_data(v)['type']!='MINION':continue
                c=v if isinstance(v,Card) else Card(self._new_id(),v)
                c.attack_bonus+=op[2];c.health_bonus+=op[3];p.deck[i]=c
                left-=1
                if not left:break
        elif name=='shuffle_left_hand':
            if p.hand:
                c=p.hand.pop(0);p.deck.insert(self.rng.randrange(len(p.deck)+1),c)
                self._log('shuffle_from_hand',player=owner)
        elif name=='copy_lowest_hand_tribe':
            choices=[c for c in p.hand if op[1] in self.cards[c.card_id].get('races',[])]
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
                if op[1] in self.cards[m.card_id].get('races',[]):self._buff(m,op[2],op[3])
        elif name=='source_health_damage':
            self._deal_effect(target,max(0,source.health),ctx)
        elif name=='source_health_heal':
            if target:self._heal(target,max(0,source.health))
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
                    player.board.remove(location)
                    self._log('location_removed',player=location.owner,card=location.card_id,entity=location.uid)
                for m in player.minions:m.health=0
            self._refresh_auras()
        elif name=='destroy_location':
            if target:
                location=next(x for player in self.players for x in player.locations if x.uid==target)
                self.players[location.owner].board.remove(location)
                self._log('location_removed',player=location.owner,card=location.card_id,entity=location.uid)
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
            for _ in range(op[2]):self._summon(1-owner,op[1])
        elif name=='summon_fixed_random':
            self._summon(owner,self.rng.choice(op[1]))
        elif name=='summon_source_stats':
            d=self.cards[op[1]]
            self._summon(owner,op[1],attack_bonus=max(0,source.attack)-d['attack'],health_bonus=max(1,source.health)-d['health'])
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
        elif name=='held_keywords':
            if any(self._matches_filter(c,op[1]) for c in p.hand):source.keywords.update(op[2])
        elif name=='weapon_buff_or_equip':
            if p.weapon:p.weapon['attack']+=op[1]
            else:self._equip(owner,op[2])
        elif name=='deck_size_draw':
            if len(p.deck)>=op[1]:self._draw(owner)
        elif name=='tribal_damage':
            if target:
                chosen=self._find(target);tribes=set(self.cards[chosen.card_id].get('races',[]))
                targets=[m.uid for player in self.players for m in player.minions if m is chosen or tribes.intersection(self.cards[m.card_id].get('races',[]))]
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
                for _ in range(min(dealt,7-len(p.board))):self._summon(owner,op[2])
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
            self._summon(owner,'HERO_11bpt',expires=True)
        else:return False
        return True
