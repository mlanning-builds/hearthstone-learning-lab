"""Staged Standard generation/choice continuations, not playable registration.

Complete reviewed outcome contracts remain mandatory. State belongs to physical
cards or suspended choices; no card-text inference or supported-only pools.
"""
from engine.cards import UnsupportedCard
from engine.game import Card
from .generation_cards import pool,PoolRequest,random_cards,discover
from .selectors import has_tribe,classes

OWN='own_or_neutral'
SPELL=pool(card_type='SPELL',classes=OWN)
MINION=pool(card_type='MINION',classes=OWN)
BEAST=pool(card_type='MINION',tribe='BEAST',classes=OWN)
UNDEAD=pool(card_type='MINION',tribe='UNDEAD',classes=OWN)
FIVE=pool(card_type='MINION',minimum=5,maximum=5,classes=OWN)
EIGHT=pool(card_type='MINION',minimum=8,maximum=8)
BLOOD=pool(rune='blood')
UNHOLY=pool(rune='unholy')
FROST=pool(rune='frost')
CHOOSE=pool(mechanic='CHOOSE_ONE',classes=OWN)
STEALTH=pool(card_type='MINION',mechanic='STEALTH',classes=OWN)

def choice(request,mode='plain',**mods):
    return ('choicegen_discover',request,mode,tuple(mods.items()))

RULES={
 'CAP_002':('none',[choice(STEALTH,follow='CAP_002')]),
 'CAP_105':('none',[discover(pool(card_type='MINION',tribe='PIRATE',classes=OWN)),('summon','CAP_107t',2)]),
 'CAP_407':('none',[choice(pool(card_type='MINION',minimum=5,classes=OWN),prepare=True)]),
 'CORE_RLK_066':('none',[('choicegen_corpse_discover',1,BLOOD)]),
 'CORE_RLK_116':('none',[('choicegen_undead_history',UNHOLY)]),
 'CORE_YOP_001':('none',[discover(pool(mechanic='OUTCAST')),('next_discount','OUTCAST',1,'permanent')]),
 'Core_LOE_115':('none',[]),
 'EDR_273':('none',[discover(pool(mechanic='CHOOSE_ONE',classes='other'))]),
 'EDR_517':('none',[choice(SPELL,'destination')]),
 'EDR_872':('none',[]),
 'FIR_927':('none',[discover(pool(minimum=5,maximum=5,classes=OWN)),('schedule_turn_effect','start',1,1,(('choicegen_temporary_crystal',),))]),
 'JAIL_123':('none',[choice(pool(card_type='SPELL',minimum=5,classes=OWN),repeat_spell=True)]),
 'JAIL_201':('none',[]),
 'JAIL_328':('none',[]),
 'JAIL_451':('none',[choice(FIVE,'corpse_copy')]),
 'JAIL_474':('none',[('choicegen_two_mana_discount',)]),
 'JAIL_735':('none',[('choicegen_violet',)]),
 'JAIL_806':('none',[('choicegen_start_no_spells',)]),
 'JAIL_861':('none',[choice(CHOOSE,'plain_opponent_copy',choose_both=True)]),
 'JAIL_875':('none',[]),
 'JAIL_892':('character',[('damage',2),random_cards(pool(card_type='SPELL',classes='DEMONHUNTER'),destination='deck'),('generation_if_outcast',('choicegen_cosmic_again',))]),
 'JAIL_986':('none',[('choicegen_playable_spell',)]),
 'JAIL_987':('none',[]),
 'RLK_025':('minion',[('choicegen_damage_discover',3,FROST)]),
 'TIME_102':('none',[random_cards(EIGHT,growing_discount=1)]),
 'TIME_448':('none',[discover(MINION),discover(MINION),('choicegen_no_minion_discount',)]),
 'TIME_730':('none',[discover(BEAST,'bottom',attack=5,health=5),discover(BEAST,'bottom',attack=5,health=5)]),
 'TIME_872':('none',[('choicegen_fill_enemy',)]),
 'TLC_109':('none',[('choicegen_destroy_top_rarity',)]),
 'TLC_434':('none',[choice(UNDEAD,'keep_all')]),
 'TLC_461':('none',[('choicegen_remaining_mana',)]),
 'TLC_462':('none',[('choicegen_discovered_summon',)]),
 'TLC_815':('none',[random_cards(pool(card_type='MINION',minimum=4,maximum=4),destination='board',keyword='TAUNT'),('kindred',[random_cards(pool(card_type='MINION',minimum=4,maximum=4),destination='board',keyword='TAUNT')])]),
}
CHOICES={
 'Core_LOE_115':[('Discover a minion','none',[discover(MINION)]),('Discover a spell','none',[discover(SPELL)])],
 'EDR_872':[('Mage spell','none',[discover(pool(card_type='SPELL',classes='MAGE'))]),('Druid spell','none',[discover(pool(card_type='SPELL',classes='DRUID'))])],
 'JAIL_201':[('Hero Attack','none',[('hero_attack',2)]),('Druid card','none',[random_cards(pool(classes='DRUID'))])],
}
DEATH_EFFECTS={'JAIL_328':[('choicegen_no_neutral',)]}
LOCATION_EFFECTS={'JAIL_987':[random_cards(pool(card_type='MINION',classes='SHAMAN'),locked_until_play=True)]}
WEAPON_TRIGGERS={'JAIL_875':[('choicegen_staff',)]}
DYNAMIC_REQUESTS={
 'JAIL_328':{pool(classes='PALADIN')},'JAIL_474':{EIGHT},'JAIL_735':{EIGHT},
 'JAIL_806':{pool(card_type='SPELL',minimum=5)},'JAIL_875':{pool(classes='DRUID')},
 'JAIL_892':{pool(card_type='SPELL',classes='DEMONHUNTER')},
 'JAIL_986':{pool(card_type='SPELL')},'TIME_872':{pool(card_type='MINION',minimum=1,maximum=1)},
 'TLC_109':{pool(rarity=r,classes=OWN) for r in ('COMMON','RARE','EPIC','LEGENDARY','FREE')},
 'TLC_462':{pool(card_type='MINION',minimum=n,maximum=n) for n in (2,4)},
}

def requests_for(cid):
    result=set(DYNAMIC_REQUESTS.get(cid,()))
    def walk(value):
        if isinstance(value,PoolRequest):result.add(value)
        elif isinstance(value,(tuple,list)):
            for child in value:walk(child)
    for table in (RULES,CHOICES,DEATH_EFFECTS,WEAPON_TRIGGERS,LOCATION_EFFECTS):walk(table.get(cid,()))
    return result

class ChoiceGenerators:
    def _choicegen_undead_died(self,owner):
        return any(r['turn']>self.players[owner].last_turn_ended and has_tribe(self.cards[r['card_id']],'UNDEAD')
                   for r in self.players[owner].death_records)

    def _choicegen_split(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner]
        if name=='choicegen_corpse_discover':
            if p.corpses<op[1]:return ('batch30_noop',),()
            self._generation_candidates(op[2],owner)
            return ('generation_pay_resource','corpses_up_to',op[1]),(discover(op[2]),)
        if name=='choicegen_undead_history':
            return self._split_fixed_summon(discover(op[1]),ctx) if self._choicegen_undead_died(owner) else (('batch30_noop',),())
        if name=='choicegen_damage_discover':
            target=next((m for player in self.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
            if target is None:return ('batch30_noop',),()
            return ('damage',op[1]),(('choicegen_if_target_died',target.uid,op[2]),)
        if name=='choicegen_cosmic_again':
            return ('damage',2),(random_cards(pool(card_type='SPELL',classes='DEMONHUNTER'),destination='deck'),)
        if name=='choicegen_two_mana_discount':
            amount=sum(h['cost']==2 for h in p.played_history)
            return self._split_fixed_summon(random_cards(EIGHT,2,cost_delta=-amount),ctx)
        if name=='choicegen_violet':
            count=2 if ctx.get('prior_spell_count',len(p.spells_turn))>=3 else 1
            return self._split_fixed_summon(random_cards(EIGHT,count,destination='board'),ctx)
        if name=='choicegen_start_no_spells':
            no_spells=not any(self.cards[c]['type']=='SPELL' for c in p.starting_deck)
            return self._split_fixed_summon(random_cards(pool(card_type='SPELL',minimum=5),cost_delta=-5 if no_spells else 0),ctx)
        if name=='choicegen_no_neutral':
            if any('NEUTRAL' in classes(self._card_data(c)) for c in p.deck):return ('batch30_noop',),()
            return self._split_fixed_summon(random_cards(pool(classes='PALADIN'),cost_delta=-2),ctx)
        if name=='choicegen_fill_enemy':
            request=pool(card_type='MINION',minimum=1,maximum=1)
            count=max(0,7-len(self.players[1-owner].board))
            # Membership uses the caster's request context, summons use recipient.
            self._generation_candidates(request,owner)
            ops=[('choicegen_enemy_one',request)]*count
            return (ops[0],tuple(ops[1:])) if ops else (('batch30_noop',),())
        return None

    def _choicegen_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner]
        if name=='choicegen_discover':
            values=self._generation_discover_candidates(op[1],ctx)
            ids=self.rng.sample(list(values),min(3,len(values)))
            if ids:
                if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite generation choice')
                self.pending_choice=dict(owner=owner,kind='choicegen_discover',mode=op[2],modifiers=op[3],
                    context=dict(ctx),options=[dict(card_id=cid) for cid in ids])
                self.phase='choice'
        elif name=='choicegen_remaining_mana':
            self._generation_effect(discover(pool(minimum=p.mana,maximum=p.mana,classes=OWN)),ctx)
        elif name=='choicegen_destroy_top_rarity':
            if p.deck:
                value=p.deck[-1];rarity=self._card_data(value).get('rarity')
                if not rarity:raise UnsupportedCard('Destroyed top card has no reviewed rarity')
                request=pool(rarity=rarity,classes=OWN)
                self._generation_candidates(request,owner)
                p.deck.pop();self._zone_card_removed(owner,value,'deck','destroy');self._log('destroy_deck',player=owner,card=self._card_data(value)['id']);self._refresh_auras()
                self._generation_effect(discover(request),ctx)
        elif name=='choicegen_if_target_died':
            if any(r['entity'].uid==op[1] for player in self.players for r in player.death_records):
                self._generation_effect(discover(op[2]),ctx)
        elif name=='choicegen_no_minion_discount':
            if not any(self._card_data(c)['type']=='MINION' for c in p.deck):
                for c in p.hand:
                    if self.cards[c.card_id]['type']=='MINION':c.cost_delta=getattr(c,'cost_delta',0)-2
                self._refresh_auras()
        elif name=='choicegen_discovered_summon':
            cost=4 if p.discoveries_this_turn else 2
            self._generation_effect(('generate_one',pool(card_type='MINION',minimum=cost,maximum=cost),'board',()),ctx)
        elif name=='choicegen_staff':
            self._generation_effect(discover(pool(classes='DRUID'),cost_delta=-self._hero_attack(owner)),ctx)
        elif name=='choicegen_enemy_one':
            values=self._generation_candidates(op[1],owner)
            if values:self._generation_place(self.rng.choice(values),'board',(),dict(ctx,owner=1-owner))
        elif name=='choicegen_playable_spell':
            values=self._generation_candidates(pool(card_type='SPELL'),owner)
            values=[cid for cid in values if self._cost(Card(0,cid),owner)<=p.mana]
            if values:self._generation_place(self.rng.choice(values),'hand',(('temporary',True),),ctx)
        elif name=='choicegen_temporary_crystal':
            delta=max(0,min(1,p.mana_capacity-p.max_mana));p.max_mana+=delta;p.mana=min(p.mana_capacity,p.mana+delta)
            if delta:self._schedule_turn_effect(owner,'end',0,1,(('choicegen_remove_crystal',delta),))
        elif name=='choicegen_remove_crystal':
            p.max_mana=max(0,p.max_mana-op[1]);p.mana=min(p.mana,p.max_mana)
        else:return False
        return True

    def _choicegen_choice(self,choice,selected):
        if choice['kind'] not in ('choicegen_discover','choicegen_destination'):return False
        owner=choice['owner'];p=self.players[owner];cid=selected['card_id']
        if choice['kind']=='choicegen_destination':
            self._discovery_result=self._generation_place(cid,selected['destination'],(),dict(owner=owner))
            return True
        if choice['kind']!='choicegen_discover':return False
        mode=choice['mode'];ctx=choice['context'];mods=choice['modifiers']
        if mode=='destination':
            self.pending_choice=dict(owner=owner,kind='choicegen_destination',options=[
                dict(card_id=cid,label='Keep',destination='hand'),
                dict(card_id=cid,label="Opponent's next draw",destination='enemy_top')])
            self.phase='choice'
            return True
        chosen=[selected]
        if mode=='keep_all' and p.corpses>=5:
            self._spend_corpses(owner,5)
            chosen=[selected]+[o for o in choice['options'] if o is not selected]
        result=None
        for option in chosen:
            card=self._generation_place(option['card_id'],'hand',mods,ctx)
            if option is selected:result=card
        self._discovery_result=result
        if mode=='corpse_copy' and p.corpses>=5:
            self._spend_corpses(owner,5)
            self._summon(owner,cid,entry_origin='copy',entry_site='blood_clone')
        elif mode=='plain_opponent_copy':self._generation_place(cid,'hand',(),dict(owner=1-owner))
        elif mode not in ('plain','corpse_copy','keep_all'):raise UnsupportedCard('Unknown generation choice policy: '+mode)
        self._refresh_auras()
        return True
