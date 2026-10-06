"""Physical set-aside cards, bound summons and remembered resurrection outcomes.

Private objects stay off rule_state and scheduled-operation arguments. Public
observations expose only explicit views; operations refer to opaque local IDs.
"""
from copy import deepcopy
from engine.game import Card

RULES={
 'CATA_EVENT_001':('none',[('stored_fire_choice',)]),
 'CAP_805':('none',[('stored_slime',)]),
 'CAP_805t':('none',[('stored_resummon',)]),
 'CAP_806':('none',[('stored_reborn_army',)]),
 'CATA_481':('none',[('stored_devour',)]),
 'CORE_RLK_086':('none',[]),
 'EDR_454':('none',[]),
 'EDR_818':('none',[]),
 'JAIL_852':('none',[('stored_mix_hands',)]),
 'TIME_706':('none',[('stored_starting_hand',)]),
 'TIME_EVENT_998':('none',[('stored_future_hand',)]),
 'TLC_841':('none',[('stored_jars',)]),
}
TOKEN_IDS={'CAP_805t','EDR_454t','EDR_818t','TLC_841t'}
DEATH_EFFECTS={
 'CATA_481':[('stored_return_devoured',)],
 'CORE_RLK_086':[('stored_weapon_kills',)],
 'EDR_454t':[('stored_release',)],
 'TLC_841t':[('stored_release',)],
 'EDR_818':[('stored_beetles',)],
}
START_EFFECTS={'EDR_818t':('owner',[('stored_reform',)])}

class StoredCards:
    def _stored_save(self,owner,kind,values):
        if not hasattr(self,'_stored_payloads'):self._stored_payloads={}
        key=self._new_id();self._stored_payloads[key]=dict(owner=owner,kind=kind,values=values)
        return key

    def _stored_choice(self,choice,selected):
        if choice['kind']!='stored_fire':return False
        owner=choice['owner'];card=next(c for c in self.players[owner].hand if c.uid==selected['uid'])
        snapshot=self._stored_payloads.pop(choice['payload'])['values'][0]
        if not hasattr(card,'_phoenix_fires'):card._phoenix_fires=[]
        card._phoenix_fires.append(dict(remaining=3,snapshot=snapshot,last_tick=None))
        return True

    def _stored_turn_entries(self,phase):
        if phase!='end':return []
        return [dict(source=None,order=c.uid,operations=(('stored_fire_tick',c.uid),))
                for c in self.players[self.current].hand if getattr(c,'_phoenix_fires',None)]

    def _stored_entry(self,minion,card):
        for field in ('_bound_card','_bound_minion'):
            if hasattr(card,field):
                setattr(minion,field,deepcopy(getattr(card,field)))
                minion.keywords.add('DEATHRATTLE')

    def _stored_split(self,op,ctx):
        name=op[0];owner=ctx['owner'];source=ctx.get('source');ops=[]
        if name=='stored_fire_tick':
            card=next((c for c in self.players[owner].hand if c.uid==op[1]),None)
            expired=[]
            for fire in getattr(card,'_phoenix_fires',[]):
                if fire['last_tick']==self.turn:continue
                fire['last_tick']=self.turn;fire['remaining']-=1
                if fire['remaining']<=0:expired.append(fire)
            if not expired:return ('batch30_noop',),()
            # Discard once; every independent attached enchantment that expires
            # at this checkpoint contributes its own bound summon.
            ops=[('stored_discard_bound',card)]+[('stored_fire_summon',fire['snapshot']) for fire in expired]
        elif name=='stored_slime':
            payload=[[m.card_id for m in p.minions if m.health>0] for p in self.players]
            key=self._stored_save(owner,'slime',payload)
            return ('destroy_all_minions',), (('stored_give_slime',key),)
        elif name=='stored_resummon':
            card=ctx.get('physical_card')
            ids=list(getattr(card,'_resummon_ids',()))
            self.rng.shuffle(ids);ops=[('summon',cid,1) for cid in ids]
        elif name=='stored_weapon_kills':
            ids=list(ctx.get('broken_weapon',{}).get('stored_kills',()))
            self.rng.shuffle(ids);ops=[('summon',cid,1) for cid in ids]
        elif name=='stored_return_devoured':
            ops=[('stored_return_one',recipient,card) for recipient,card in getattr(source,'_devoured_cards',())]
        elif name=='stored_reborn_army':
            ids=list(self.players[owner].reborn_history);self.rng.shuffle(ids)
            group={'summoned':[],'mode':'random'}
            ops=[('force_summon_one',cid,group) for cid in ids]+[('force_group_attacks',group)]
        elif name=='stored_beetles':
            ops=[('death_summon','EDR_818t',min(7,max(0,source.attack)))] if source else []
        else:return None
        if not ops:return ('batch30_noop',),()
        first,tail=self._split_fixed_summon(ops[0],ctx)
        return first,tail+tuple(ops[1:])

    def _stored_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];source=ctx.get('source')
        if name=='stored_fire_choice':
            options=[dict(card_id=c.card_id,uid=c.uid) for c in p.hand]
            if options and source is not None:
                key=self._stored_save(owner,'phoenix',[deepcopy(source)])
                self.pending_choice=dict(owner=owner,kind='stored_fire',options=options,payload=key)
                self.phase='choice'
        elif name=='stored_discard_bound':
            card=op[1]
            if any(c is card for c in p.hand):self._discard_card(owner,card)
        elif name=='stored_fire_summon':
            self._summon(owner,op[1].card_id,copy_from=op[1],entry_origin='effect',entry_site='stored_fire_summon')
        elif name=='stored_weapon_kills':
            ids=list(ctx.get('broken_weapon',{}).get('stored_kills',()))
            self.rng.shuffle(ids)
            self._rule_events.append(('captured_effects',dict(operations=tuple(('summon',cid,1) for cid in ids),context=ctx),[]))
        elif name=='stored_give_slime':
            payload=self._stored_payloads.pop(op[1])['values']
            for recipient,ids in enumerate(payload):
                card=Card(self._new_id(),'CAP_805t');card._resummon_ids=list(ids)
                self._enter_hand(recipient,card)
        elif name=='stored_devour':
            enemy=self.players[1-owner]
            selected=self.rng.sample(list(enemy.hand),min(2,len(enemy.hand)))
            for card in selected:enemy.hand.remove(card)
            if source is not None:
                if not hasattr(source,'_devoured_cards'):source._devoured_cards=[]
                source._devoured_cards.extend((1-owner,card) for card in selected)
                self._sleep_minion(source,2)
            self._refresh_auras()
        elif name=='stored_return_one':
            # Each trigger returns a copy: duplicated Deathrattles remain valid.
            card=deepcopy(op[2]);card.uid=self._new_id();self._enter_hand(op[1],card)
        elif name=='stored_egg':
            target=self._force_live(ctx.get('target',0))
            if target:
                egg=self._summon(owner,'EDR_454t',ctx.get('summon_position',-1),entry_origin='location',entry_site='stored_egg')
                if egg:egg._bound_minion=deepcopy(target)
        elif name=='stored_release':
            bound=getattr(source,'_bound_minion',None)
            card=getattr(source,'_bound_card',None)
            if bound is not None:
                self._summon(owner,bound.card_id,ctx.get('death_position',-1),copy_from=bound,entry_origin='deathrattle',entry_site='stored_release')
            elif card is not None:
                self._summon(owner,card.card_id,ctx.get('death_position',-1),card.attack_bonus,card.health_bonus,
                             entry_origin='recruit',entry_site='stored_release',entry_zone='hand',entry_source=card)
        elif name=='stored_jars':
            for index,card in enumerate(p.hand):
                if self.cards[card.card_id]['type']!='MINION':continue
                jar=Card(self._new_id(),'TLC_841t');jar._bound_card=deepcopy(card)
                jar._hand_entry_turn=self.turn;p.hand[index]=jar
            self._refresh_auras()
        elif name=='stored_mix_hands':
            sizes=[len(player.hand) for player in self.players]
            cards=self.players[0].hand+self.players[1].hand;self.rng.shuffle(cards)
            for player in self.players:player.hand=[]
            for recipient,size in enumerate(sizes):
                for _ in range(size):self._enter_hand(recipient,cards.pop())
            self._refresh_auras()
        elif name=='stored_starting_hand':
            key=self._stored_save(owner,'hand',list(p.hand));p.hand=[]
            for card in getattr(p,'_starting_hand',[]):self._enter_hand(owner,self._copy_card(card))
            self._schedule_turn_effect(owner,'end',0,1,(('stored_swap_back',key),),source_card_id='TIME_706')
            self._refresh_auras()
        elif name=='stored_swap_back':
            values=self._stored_payloads.pop(op[1])['values'];p.hand=[]
            for card in values:self._enter_hand(owner,card)
            self._refresh_auras()
        elif name=='stored_future_hand':
            values=[c for c in p.hand if self.cards[c.card_id]['type']=='MINION']
            p.hand[:]=[c for c in p.hand if self.cards[c.card_id]['type']!='MINION']
            key=self._stored_save(owner,'future',values)
            self._schedule_turn_effect(owner,'start',2,1,(('stored_future_return',key),),source_card_id='TIME_EVENT_998')
            self._refresh_auras()
        elif name=='stored_future_return':
            for card in self._stored_payloads.pop(op[1])['values']:
                card.attack_bonus+=5;card.health_bonus+=5;self._enter_hand(owner,card)
            self._refresh_auras()
        elif name=='stored_reform':
            if source is None or source not in p.minions:return True
            beetles=[m for m in p.minions if m.card_id=='EDR_818t' and m.health>0]
            if not beetles:return True
            position=min(p.board.index(m) for m in beetles)
            attack=sum(m.attack for m in beetles);health=sum(m.health for m in beetles)
            for m in beetles:p.board.remove(m)
            self._refresh_auras()
            self._summon(owner,'EDR_818',position,attack-7,health-7,entry_origin='effect',entry_site='stored_reform')
        else:return False
        return True

    def _stored_view(self,value):
        result={}
        if getattr(value,'_phoenix_fires',None):result['phoenix_turns_remaining']=[fire['remaining'] for fire in value._phoenix_fires]
        if hasattr(value,'_bound_card'):
            card=value._bound_card
            result['bound_minion']=dict(card_id=card.card_id,attack=self._card_stat(card,'attack'),health=self._card_stat(card,'health'))
        if hasattr(value,'_bound_minion'):
            m=value._bound_minion
            result['bound_minion']=dict(card_id=m.card_id,attack=m.attack,health=m.health,max_health=m.max_health)
        if hasattr(value,'_devoured_cards'):result['devoured_count']=len(value._devoured_cards)
        if hasattr(value,'_resummon_ids'):result['resummon_ids']=list(value._resummon_ids)
        if hasattr(value,'_learned_spell'):result['learned_spell']=value._learned_spell
        return result
