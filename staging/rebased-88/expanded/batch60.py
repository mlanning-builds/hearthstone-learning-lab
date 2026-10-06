"""Shared held progress and explicit combat/death payload operations.

No card-text interpreter and no reduced random generation pools. Physical card
progress lives on Card objects; private remembered hand IDs never enter views.
"""
from copy import deepcopy
from engine.game import Card
from .selectors import has_tribe, has_school
from .batch60_cards import MOON_TRANSFORMS, DRAGON_TRANSFORMS
from .generation_extensions import HELD_TRANSFORMS


class Batch60:
    @staticmethod
    def _b60_state(entity):
        if not hasattr(entity,'rule_state'):entity.rule_state={}
        return entity.rule_state

    def _b60_transform_card(self,card,cid,*,stats=None):
        # Transformations in hand keep enchantments and the physical identity.
        if card.card_id!=cid and hasattr(card,'_learned_spell'):del card._learned_spell
        card.card_id=cid
        if stats is not None:
            card.attack_bonus=stats[0]-self.cards[cid].get('attack',0)
            card.health_bonus=stats[1]-self.cards[cid].get('health',0)

    def _b60_mark_mirrors(self):
        for p in self.players:
            for c in p.hand:
                if c.card_id in ('CORE_RLK_567','DINO_407','TIME_876'):
                    state=self._b60_state(c)
                    if 'mirror' not in state:
                        state['mirror']=c.card_id
                        if c.card_id=='DINO_407':
                            cid=self.players[1-self.players.index(p)].last_minion_played
                            if cid:self._b60_transform_card(c,cid,stats=(3,4));c.set_cost=3;c._copied_from_owner=1-self.players.index(p)

    def _b60_event(self,kind,data):
        self._b60_mark_mirrors()
        if kind=='spell_cast' and 'card_id' in data:
            owner=data['owner'];cid=data['card_id']
            for c in list(self.players[owner].hand):
                s=self._b60_state(c)
                if c.card_id in MOON_TRANSFORMS or c.card_id in HELD_TRANSFORMS:
                    s['spells']=s.get('spells',0)+1
                    if s['spells']>=3:
                        self._b60_transform_card(c,(MOON_TRANSFORMS | HELD_TRANSFORMS)[c.card_id])
                if c.card_id=='TIME_213' and has_school(self.cards[cid],'NATURE'):s['nature']=True
                if s.get('mirror')=='CORE_RLK_567':
                    original=data.get('physical_card')
                    if original is not None:
                        uid=c.uid;entry=getattr(c,'_hand_entry_turn',None);copied=self._copy_card(original).__dict__;copied['uid']=uid;copied['_hand_entry_turn']=entry
                        c.__dict__.clear();c.__dict__.update(copied)
                        self._b60_state(c)['mirror']='CORE_RLK_567'
                    else:self._b60_transform_card(c,cid)
        if kind=='minion_played':
            owner=data['owner'];cid=data['card_id']
            if has_tribe(self.cards[cid],'DRAGON'):self.players[owner].dragons_played_turn+=1
            self.players[owner].last_minion_played=cid
            for recipient,p in enumerate(self.players):
                for c in p.hand:
                    s=self._b60_state(c)
                    if recipient==owner:
                        if c.card_id=='TIME_702':s['minion']=True
                        if c.card_id in DRAGON_TRANSFORMS and has_tribe(self.cards[cid],'DRAGON'):
                            self._b60_transform_card(c,DRAGON_TRANSFORMS[c.card_id])
                    elif s.get('mirror')=='DINO_407':self._b60_transform_card(c,cid,stats=(3,4));c.set_cost=3;c._copied_from_owner=owner

    def _b60_spend_mana(self,owner,amount):
        self._held_spend(owner,amount)
        p=self.players[owner]
        if amount>0 and p.mana==0:
            for m in p.minions:
                if m.card_id=='CATA_130' and not m.silenced and m.health>0:self._buff(m,1,1)

    def _b60_paid_card(self,owner,cost):
        if cost!=2:return
        p=self.players[owner]
        for zone in (p.hand,p.deck):
            for i,c in enumerate(zone):
                if self._card_data(c)['id']=='JAIL_470':
                    if not isinstance(c,Card):c=Card(self._new_id(),c);zone[i]=c
                    s=self._b60_state(c);s['shots']=s.get('shots',1)+1

    def _b60_turn_start(self,owner):
        self._b60_mark_mirrors()
        p=self.players[owner]
        for player in self.players:player.dragons_played_turn=0
        for c in list(p.hand):
            s=self._b60_state(c)
            if c.card_id=='EDR_843':
                s['turns']=s.get('turns',0)+1
                if s['turns']>=3:self._b60_transform_card(c,'EDR_843t1')
            if s.get('mirror')=='TIME_876':
                options=[v for v in self.players[1-owner].hand if self.cards[v.card_id]['type']=='MINION']
                if options:self._b60_transform_card(c,self.rng.choice(options).card_id);c._copied_from_owner=1-owner
        # Destruction is not a discard. The enchantment follows the minion
        # from hand to board; leaving either zone resets ordinary enchantments.
        for c in list(p.hand):
            if self._b60_state(c).get('destroy_on_turn',float('inf'))<=p.turns_taken:
                p.hand.remove(c);self._zone_card_removed(owner,c,'hand','destroy');self._log('destroy_hand_card',player=owner,card=c.card_id)
        for m in p.minions:
            if self._b60_state(m).get('destroy_on_turn',float('inf'))<=p.turns_taken:m.health=0

    def _b60_turn_end(self,owner):
        p=self.players[owner]
        for zone in (p.hand,p.deck):
            for i,c in enumerate(zone):
                if self._card_data(c)['id']=='TLC_827':
                    if not isinstance(c,Card):c=Card(self._new_id(),c);zone[i]=c
                    c.attack_bonus+=1

    def _b60_pre_attack(self,source):
        if source<=0:return False
        m=self._find(source);stealthed='STEALTH' in self._effective_keywords(m)
        if stealthed:
            for c in self.players[m.owner].hand:
                if c.card_id=='CAP_006':self._b60_state(c)['stealth_attack']=True
        return stealthed

    def _b60_trigger_matches(self,wanted,kind,data,m):
        if not wanted.startswith('b60_'):return None
        if m.health<=0:return False
        if wanted=='b60_stealthed_attack':return kind=='before_minion_attack' and data['owner']==m.owner and data.get('stealthed',False)
        if wanted=='b60_other_attack':return kind=='before_minion_attack' and data['owner']==m.owner and data['source']!=m.uid
        if wanted=='b60_adjacent_attack':return kind=='minion_attack' and (data['source']==m.uid or m.uid in data.get('attacker_neighbors',()))
        if wanted=='b60_attack_kill':return kind=='minion_attack' and data['source']==m.uid and data.get('killed',False)
        if wanted=='b60_any_death':return kind=='minion_died'
        if wanted=='b60_friendly_death':return kind=='minion_died' and data['owner']==m.owner
        if wanted=='b60_undead_death':return kind=='minion_died' and data['owner']==m.owner and has_tribe(self.cards[data['card_id']],'UNDEAD')
        return False

    def _b60_choice(self,choice,selected):
        if choice['kind']=='b60_secret_hand':
            choice['source'].secret_discard=(1-choice['owner'],selected['uid'])
        elif choice['kind']=='b60_health_one':
            m=next((m for p in self.players for m in p.minions if m.uid==selected['uid']),None)
            if m:m.health=m.max_health=1+m.aura_health
        else:return False
        return True

    def _b60_add_payload(self,owner,cid,payload):
        p=self.players[owner];before=len(p.hand);self._add(owner,cid)
        if len(p.hand)>before:self._b60_state(p.hand[-1]).update(payload)

    def _b60_split(self,op,ctx):
        """Expand compound effects at existing resumable checkpoints."""
        name=op[0];owner=ctx['owner'];p=self.players[owner]
        if name=='b60_draw_played':
            ids=list(dict.fromkeys(r['card_id'] for r in p.played_history))
            ops=[('b60_draw_identity',cid) for cid in ids]
        elif name=='b60_held_shots':
            ops=[('damage_random_enemy',1)]*self._b60_state(ctx['physical_card']).get('shots',1)
        elif name=='b60_missiles_repeat':
            before=sum(len(v.death_history) for v in self.players)
            return ('missiles','enemies',3),(('b60_missiles_if_death',before),)
        else:return None
        return (ops[0],tuple(ops[1:])) if ops else (('batch30_noop',),())

    def _b60_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];q=self.players[1-owner]
        source=ctx.get('source');target=ctx.get('target',0);event=ctx.get('event',{})
        if name=='b60_attack_damage':self._deal_effect(target,source.attack,ctx)
        elif name=='b60_dragon_rush':p.dragons_have_rush=True
        elif name=='b60_held_nature':
            if self._b60_state(ctx['physical_card']).get('nature'):self._buff(source,1,1);self._draw(owner)
        elif name=='b60_held_armor':
            if self._b60_state(ctx['physical_card']).get('minion'):self._gain_armor(owner,5)
        elif name=='b60_stealth_damage':self._deal_effect(target,3 if self._b60_state(ctx['physical_card']).get('stealth_attack') else 1,ctx)
        elif name=='b60_silent_strike':
            if target:
                m=self._find(target)
                if 'STEALTH' in self._effective_keywords(m) and q.minions:self._deal_effect(self.rng.choice(q.minions).uid,m.attack,ctx)
        elif name=='b60_discount_random':
            if p.hand:
                c=self.rng.choice(p.hand);c.cost_delta=getattr(c,'cost_delta',0)-op[1]
        elif name=='b60_damage_others':
            if event.get('target',0)>0 and source.health>0:
                with self._damage_batch():
                    for m in list(q.minions):
                        if m.uid!=event['target']:self._deal_effect(m.uid,source.attack,ctx)
        elif name=='b60_omen_grow':
            s=self._b60_state(source);s['omen_damage']=s.get('omen_damage',1)+1
        elif name=='b60_omen_damage':self._effect(('area_damage','enemies',self._b60_state(source).get('omen_damage',1)),ctx)
        elif name=='b60_survived_missiles':
            if source.health>0 and event.get('target',0)>0:self._effect(('missiles','enemies',source.attack),ctx)
        elif name=='b60_escape':
            if source.health>0:
                self._draw(owner)
                if source in p.board:p.board.remove(source);self._refresh_auras();self._log('remove_from_game',player=owner,entity=source.uid)
        elif name=='b60_attacker_health':
            m=next((m for m in p.minions if m.uid==event['source']),None)
            if m:m.health=m.max_health=source.health+m.aura_health
        elif name=='b60_copy_victim':self._add(owner,event['victim_card_id'])
        elif name=='b60_weapon_other':
            choices=[m.uid for m in q.minions if m.uid!=target]+([self.hero_id(1-owner)] if target!=self.hero_id(1-owner) else [])
            if choices:self._deal_effect(self.rng.choice(choices),ctx.get('attack_damage',self._hero_attack(owner)),ctx)
        elif name=='b60_gain_dead_attack':self._buff(source,event['attack'],0)
        elif name=='b60_reborn_corpses':
            if 'REBORN' not in self._effective_keywords(source) and p.corpses>=3:
                self._spend_corpses(owner,3);source.keywords.add('REBORN')
        elif name=='b60_draw_remember':
            c=self._draw(owner)
            if c is not None:source.remembered_draw=c.uid
        elif name=='b60_discard_remembered':
            c=next((c for c in p.hand if c.uid==getattr(source,'remembered_draw',None)),None)
            if c:self._discard_card(owner,c)
        elif name=='b60_bones':
            if target:
                m=self._find(target);a,h=m.attack,m.health;m.health=0
                self._b60_add_payload(owner,'TLC_829t',dict(buff_attack=a,buff_health=h))
        elif name=='b60_payload_buff':
            if target:
                s=self._b60_state(ctx['physical_card']);self._buff(self._find(target),s.get('buff_attack',0),s.get('buff_health',0))
        elif name=='b60_breath':self._b60_add_payload(owner,'CATA_464t',dict(damage=source.attack))
        elif name=='b60_payload_damage':self._deal_effect(target,self._b60_state(ctx['physical_card']).get('damage',1),ctx)
        elif name=='b60_secret_hand':
            options=self.rng.sample(q.hand,min(3,len(q.hand)))
            if options:
                self.pending_choice=dict(kind='b60_secret_hand',owner=owner,source=source,options=[dict(card_id=c.card_id,uid=c.uid) for c in options]);self.phase='choice'
        elif name=='b60_discard_secret':
            recipient,uid=getattr(source,'secret_discard',(1-owner,None))
            c=next((c for c in self.players[recipient].hand if c.uid==uid),None)
            if c:self._discard_card(recipient,c)
        elif name=='b60_destroy_last_played':
            for m in q.minions:
                if m.played_turn==self.turn-1:m.health=0
        elif name=='b60_draw_identity':
            indices=[i for i,c in enumerate(p.deck) if self._card_data(c)['id']==op[1]]
            if indices:self._draw_index(owner,self.rng.choice(indices))
        elif name=='b60_health_one':
            if target:
                m=self._find(target);m.health=m.max_health=1+m.aura_health
        elif name=='b60_other_health_one':
            if any(has_tribe(self.cards[c.card_id],'DRAGON') for c in p.hand):
                allowed=set(self._visible_targets(owner,magic=True));options=[dict(card_id=m.card_id,uid=m.uid) for m in q.minions if m.uid!=target and m.uid in allowed]
                if options:self.pending_choice=dict(kind='b60_health_one',owner=owner,options=options);self.phase='choice'
        elif name=='b60_draw_discount':
            remaining=op[1]
            while remaining>0 and not self.terminal:
                c=self._draw(owner,include_burned=True)
                if c is None:break
                cost=self._cost(c,owner);c.cost_delta=getattr(c,'cost_delta',0)-remaining
                remaining=max(0,remaining-cost)
        elif name=='b60_next_murloc':
            p.cost_effects.append(dict(selector='MURLOC',amount=1,expires=None,grant_keyword='DIVINE_SHIELD' if ctx.get('kindred') else None))
        elif name=='b60_minion_cost':p.minions_set_cost=op[1]
        elif name=='b60_doomed_hand':
            for c in p.hand:
                if self.cards[c.card_id]['type']=='MINION':
                    c.attack_bonus+=3;c.health_bonus+=3;self._b60_state(c)['destroy_on_turn']=p.turns_taken+3
        elif name=='b60_attach':
            if target:self._find(target).attached_death_effects.append(op[1])
        elif name=='b60_infest':
            choices=[m for m in p.minions if m.health>0]
            if choices:
                m=self.rng.choice(choices);self._buff(m,2,2);m.attached_death_effects.append(('b60_infest',))
        elif name=='b60_pterrordax':
            m=self._summon(owner,'TLC_831t',ctx.get('death_position',-1),entry_origin='deathrattle',entry_site='pterrordax',entry_source=source)
            if m:
                total=0
                for other in [v for player in self.players for v in player.minions if v is not m]:
                    amount=min(1,max(0,other.health));self._buff(other,0,-amount);total+=amount
                self._buff(m,0,total)
        elif name=='b60_hatch':
            bonus=self._b60_state(source).get('egg_bonus',0)
            self._summon(owner,'CATA_210t',ctx.get('death_position',-1),attack_bonus=bonus,health_bonus=bonus,entry_origin='deathrattle',entry_site='twilight_egg',entry_source=source)
        elif name=='b60_egg_grow':
            s=self._b60_state(source);s['egg_bonus']=s.get('egg_bonus',0)+1
        elif name=='b60_heal_excess':
            actual=self._heal(self.hero_id(owner),op[1],healer=owner,spell=ctx.get('spell',False))
            excess=op[1]+p.permanent_healing_bonus-actual
            if excess:self._effect(('damage_random_enemy',excess),ctx)
        elif name=='b60_shuffle_all':
            for player in self.players:
                for m in list(player.minions):
                    if self._fire_immune_target(m.uid,ctx):continue
                    player.board.remove(m);recipient=self.rng.randrange(2);deck=self.players[recipient].deck
                    card=Card(self._new_id(),m.card_id);self._carry_origin(m,card)
                    deck.insert(self.rng.randrange(len(deck)+1),card);self._record_deck_insertion(recipient,owner,1,'shuffle')
            self._refresh_auras()
        elif name in ('b60_overkill_discount','b60_torch'):
            if target:
                amount=op[1] if name=='b60_overkill_discount' else self._b60_state(ctx['physical_card']).get('damage',8)
                old=self._find(target).health
                # Torch explicitly ignores Spell Damage in the pinned record.
                damage_ctx=dict(ctx,bonus=0) if name=='b60_torch' else ctx
                dealt=self._deal_effect(target,amount,damage_ctx);excess=max(0,dealt-old)
                if excess:
                    if name=='b60_torch':self._b60_add_payload(owner,'CATA_585',dict(damage=excess))
                    elif p.hand:
                        c=self.rng.choice(p.hand);c.cost_delta=getattr(c,'cost_delta',0)-excess
        elif name=='b60_death_missiles':self._effect(('missiles','enemies',6 if p.minions_died_turn else 3),ctx)
        elif name=='b60_missiles_if_death':
            if sum(len(v.death_history) for v in self.players)>op[1]:self._effect(('missiles','enemies',3),ctx)
        else:return False
        return True
