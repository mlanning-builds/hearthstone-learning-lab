"""Explicit replacement Hero Powers and reversible power swaps.

Base class powers keep their existing implementation. Replacement identity and
state are public; frozen token records remain hash-reviewed like other cards.
"""
from copy import deepcopy
from engine.cards import UnsupportedCard
from .selectors import has_tribe
from .imbue import IMBUE_POWERS, TOKEN_IDS as IMBUE_TOKEN_IDS, PLAYABLE_TOKENS as IMBUE_PLAYABLE_TOKENS

RULES={
    'TLC_513t':('none',[('summon','TLC_513t2',2),('dusk_ninja_returns',)]),
    'CORE_EX1_323':('none',[('equip','EX1_323w')]),
    'JAIL_EVENT_101':('none',[('replace_or_upgrade_star',)]),
    'TLC_632':('none',[('temporary_sulfuras_power',)]),
    'JAIL_446':('none',[('secondary_corpse_power',)]),
}
TOKEN_IDS={'TLC_513t','TLC_513hp','JAIL_446hp','EX1_tk33','EX1_tk34','EX1_323w','JAIL_EVENT_101hp','TLC_632t','TLC_632t2'}
TOKEN_IDS.update(IMBUE_TOKEN_IDS)
PLAYABLE_TOKENS={'TLC_513t','EX1_tk34','EX1_323w'}
PLAYABLE_TOKENS.update(IMBUE_PLAYABLE_TOKENS)
HERO_POWERS={'CATA_190h':'CATA_190p','TLC_513t':'TLC_513hp','CORE_EX1_323':'EX1_tk33'}

class HeroPowers:
    def _start_power_effects(self,owner,operations,target=0):
        """Run ordered power operations through the same choice checkpoints as cards."""
        return self._start_play_effects(operations,
            dict(owner=owner,source=None,target=target,bonus=0,lifesteal=False))

    def _resume_power_sequence(self):
        frame=getattr(self,'_power_frame',None)
        if frame is None:return True
        if self.pending_choice is not None or self.pending_frame is not None:return False
        self._settle(allow_event_choices=True)
        if self.pending_choice is not None:return False
        if frame['phase']=='effects':
            if self._rewind_power_offer():return False
            # Advance before publishing; a listener may suspend for a choice.
            frame['phase']='after_use'
            self.players[frame['owner']].hero_power_uses+=1
            self._queue_event('hero_power_used',owner=frame['owner'])
            self._settle(allow_event_choices=True)
            if self.pending_choice is not None:return False
        self._power_frame=None
        return True

    def _replace_primary_power(self,owner,power):
        p=self.players[owner]
        p.primary_power=deepcopy(power)
        if p.primary_power is not None:p.primary_power['uid']=self._new_id()
        p.power_used=False

    def _play_hero_card(self,owner,cid):
        if cid not in HERO_POWERS:raise UnsupportedCard('Hero replacement not implemented: '+cid)
        p=self.players[owner];data=self.cards[cid]
        # This is the modern HERO card, not the old 15-Health minion version.
        p.hero_card_id=cid
        if cid!='CATA_190h':p.hero_class=data['cardClass']
        self._gain_armor(owner,data.get('armor',0))
        self._replace_primary_power(owner,dict(card_id=HERO_POWERS[cid]))

    def _replacement_power_cost(self,owner):
        power=self.players[owner].primary_power
        return power.get('cost',self.cards[power['card_id']]['cost']) if power is not None else None

    def _replacement_power_available(self,owner):
        power=self.players[owner].primary_power
        if power is None:return False
        if power.get('upgraded_starting_class') in ('PALADIN','DEATHKNIGHT','SHAMAN'):return len(self.players[owner].board)<7
        if power['card_id'] in ('END_003p','JAIL_800hp1','JAIL_800hp2'):return False  # Passive, never an activatable action.
        return power['card_id'] not in ('EX1_tk33','EDR_847p') or len(self.players[owner].board)<7

    def _replacement_power_targets(self,owner):
        if not self._replacement_power_available(owner):return ()
        if self.players[owner].primary_power.get('upgraded_starting_class') in ('MAGE','PRIEST'):return tuple(self._visible_targets(owner,magic=True))
        if self.players[owner].primary_power['card_id']=='EDR_448p':
            visible=set(self._visible_targets(owner,magic=True))
            return tuple(m.uid for m in self.players[owner].minions
                         if m.uid in visible and m.health>0 and not m.dormant)
        return (0,)

    def _replacement_power_effect(self,owner,target=0):
        p=self.players[owner];power=p.primary_power
        if power is None:return False
        if 'upgraded_starting_class' in power:
            self._start_power_effects(owner,self._genn_power_operations(owner),target=target);return True
        cid=power['card_id']
        if cid in IMBUE_POWERS.values():
            self._start_power_effects(owner,self._imbue_power_operations(owner)*(2 if cid=='END_000p' and self._active('END_036',owner) else 1),target=target)
        elif cid=='CATA_190p':
            self._start_power_effects(owner,(('hero_attack',5),))
        elif cid=='TLC_513hp':
            self._start_power_effects(owner,(('origin_draw',False,False),('origin_draw',False,False)))
        elif cid=='EX1_tk33':
            self._summon(owner,'EX1_tk34',entry_origin='hero_power',entry_site='replacement_power')
        elif cid in ('TLC_632t','TLC_632t2','JAIL_EVENT_101hp','UNG_934t2'):
            candidates=[self.hero_id(1-owner)]+[m.uid for m in self.players[1-owner].minions if m.health>0]
            amount=power.get('damage',2) if cid=='JAIL_EVENT_101hp' else 8
            self._damage(self.rng.choice(candidates),amount,damage_source=None,damage_owner=owner)
            if cid in ('TLC_632t','TLC_632t2'):
                power['remaining']-=1
                if power['remaining']==0:self._replace_primary_power(owner,power['restore'])
                else:power['card_id']='TLC_632t2'
        else:raise UnsupportedCard('Replacement Hero Power: '+cid)
        return True

    def _power_capture_summon(self,minion):
        power=self.players[minion.owner].primary_power
        if power and power['card_id']=='JAIL_EVENT_101hp' and has_tribe(self.cards[minion.card_id],'DEMON'):
            return power['uid']
        return None

    def _power_publish_summon(self,data):
        expected=data.get('refresh_power_uid')
        if expected is None:return
        p=self.players[data['owner']]
        if p.primary_power and p.primary_power.get('uid')==expected:
            p.power_used=False

    def _hero_power_effect(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner]
        if op[0]=='dusk_ninja_returns':
            p.ninja_returns=True
        elif op[0]=='replace_or_upgrade_star':
            if p.primary_power and p.primary_power['card_id']=='JAIL_EVENT_101hp':
                p.primary_power['damage']=p.primary_power.get('damage',2)+1
            else:self._replace_primary_power(owner,dict(card_id='JAIL_EVENT_101hp',damage=2))
        elif op[0]=='secondary_corpse_power':
            p.secondary_power=dict(card_id='JAIL_446hp',used=False)
        elif op[0]=='temporary_sulfuras_power':
            self._replace_primary_power(owner,dict(card_id='TLC_632t',remaining=2,restore=deepcopy(p.primary_power)))
        else:return False
        return True
