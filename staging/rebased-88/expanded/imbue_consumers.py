"""All nineteen staged Imbue consumers and persistent payoff hooks.

No collectible registration. Missing class powers and complete generation
contracts remain admission gates, including for cross-class stolen cards.
"""
from engine.cards import UnsupportedCard
from .generation_cards import pool,random_cards,discover
from .selectors import has_tribe
from .imbue import PINNED_VALUES

WILD_GODS={'EDR_031','EDR_209','EDR_259','EDR_421','EDR_430','EDR_471','EDR_480','EDR_489','EDR_527','EDR_819','EDR_895'}
WILD_POOL=pool(card_type='MINION',rarity='LEGENDARY',mechanic='WILD_GOD')
TWO=pool(card_type='MINION',minimum=2,maximum=2)
I=('imbue',1)
RULES={
 'EDR_226':('none',[('filtered_draw',(('tribe','eq','BEAST'),),1),I]),
 'EDR_227':('none',[]),
 'EDR_231':('character',[('heal',4),('draw',1),I]),
 'EDR_264':('none',[random_cards(TWO,destination='board',keyword='TAUNT'),I]),
 'EDR_449':('none',[I]),
 'EDR_451':('none',[I]),
 'EDR_518':('none',[I,('imbue_hand_discount',)]),
 'EDR_519':('none',[I,('imbue_trigger_power',)]),
 'EDR_800':('none',[I]),
 'EDR_845':('none',[]),
 'EDR_852':('none',[I]),
 'EDR_860':('imbue_two_minion',[('imbue_if',2,('damage',4))]),
 'EDR_871':('none',[('add','EDR_851t',1),I]),
 'EDR_888':('none',[('imbue_wild_god',)]),
 'EDR_970':('none',[('imbue_enemy_attack',-2),I]),
 'END_000':('character',[('damage',2),I]),
 'END_001':('none',[I]),
 'END_003':('none',[('filtered_draw',(('tribe','eq','UNDEAD'),),1),('imbue',2)]),
 'FIR_921':('none',[('imbue_if',2,('draw',2))]),
}
DEATH_EFFECTS={'EDR_227':[I],'EDR_451':[I]}

def requests_for(cid):return {'EDR_264':{TWO},'EDR_888':{WILD_POOL}}.get(cid,set())

class ImbueConsumers:
    def _imbue_consumer_preflight(self,cid,owner):
        for request in requests_for(cid):self._generation_candidates(request,owner)

    def _imbue_start_game(self,owner):
        p=self.players[owner]
        if p.imbue_start_checked:return
        p.imbue_start_checked=True
        if 'EDR_845' in self._opening_effect_ids(owner) and all(self.cards[cid].get('spellSchool')=='NATURE' for cid in p.starting_deck if self.cards[cid]['type']=='SPELL'):
            p.hamuul_active=True;self._imbue(owner)

    def _imbue_consumer_event(self,kind,data):
        if kind!='spell_cast':return
        owner=data['owner'];p=self.players[owner]
        if p.hamuul_active:
            p.hamuul_spells+=1
            if p.hamuul_spells%3==0:
                self._rule_events.append(('captured_effects',dict(operations=(I,),
                    context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))

    def _imbue_consumer_play(self,owner,source):
        if source is None or not has_tribe(self.cards[source.card_id],'UNDEAD'):return
        p=self.players[owner];first=p.undead_play_turn!=self.turn;p.undead_play_turn=self.turn
        power=p.primary_power
        if first and power and power['card_id']=='END_003p':
            amount=int(PINNED_VALUES['END_003p']['TAG_SCRIPT_DATA_NUM_1'])+power['imbue_level']-1
            self._buff(source,amount,0)

    def _imbue_expire_attack(self,owner):
        for player in self.players:
            for m in player.all_minions:
                retained=[]
                for effect in m.imbue_attack_expiries:
                    if effect['owner']==owner:
                        self._adjust_minion_attack(m,-effect['amount'])
                    else:retained.append(effect)
                m.imbue_attack_expiries=retained
        self._refresh_auras()

    def _imbue_consumer_split(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner]
        if op[0]=='imbue_if':
            return self._split_fixed_summon(op[2],ctx) if p.imbue_count>=op[1] else (('batch30_noop',),())
        if op[0]=='imbue_wild_god':
            mods={'set_cost':1} if p.imbue_count>=4 else {}
            return self._split_fixed_summon(discover(WILD_POOL,**mods),ctx)
        if op[0]=='imbue_trigger_power':
            power=p.primary_power
            if power is None:raise UnsupportedCard('Free triggering of this base Hero Power is not connected')
            if power['card_id']=='END_003p':return ('batch30_noop',),() # passive has no activated body
            if power['card_id']=='END_000p':raise UnsupportedCard('Free Rogue Imbue Rewind timing awaits conformance review')
            operations=self._imbue_power_operations(owner)
            targets=self._replacement_power_targets(owner)
            if not targets:return ('batch30_noop',),()
            target=self.rng.choice(targets) if len(targets)>1 else targets[0]
            context=dict(owner=owner,source=None,target=target,bonus=0,lifesteal=False)
            return self._replay_split(('replay_context',operations,context),ctx)
        return None

    def _imbue_consumer_choice(self,choice,selected):
        if choice['kind']!='imbue_discount':return False
        p=self.players[choice['owner']];card=next((c for c in p.hand if c.uid==selected['uid']),None)
        if card is None:raise UnsupportedCard('Selected minion left hand')
        card.cost_delta=getattr(card,'cost_delta',0)-1;self._refresh_auras();return True

    def _imbue_consumer_effect(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner]
        if op[0]=='imbue_hand_discount':
            options=[dict(card_id=c.card_id,uid=c.uid) for c in p.hand if self.cards[c.card_id]['type']=='MINION']
            if options:
                if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite a pending choice')
                self.pending_choice=dict(kind='imbue_discount',owner=owner,options=options);self.phase='choice'
        elif op[0]=='imbue_enemy_attack':
            for m in self.players[1-owner].minions:
                self._adjust_minion_attack(m,op[1]);m.imbue_attack_expiries.append(dict(owner=owner,amount=op[1]))
        else:return False
        return True
