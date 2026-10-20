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
HERO_POWERS={'AV_113':'AV_113p','ICC_827':'ICC_827p','YOD_009':'YOD_009h','AV_207':'AV_207p','EX1_323':'EX1_tk33','BOT_238':'BOT_238p','AV_258':'AV_258pt7','AV_200':'AV_200p2','TRL_065':'TRL_065h','AV_203':'AV_203p','ICC_833':'ICC_833h','ICC_481':'ICC_481p','ICC_830':'ICC_830p','AV_205':'AV_205p','AV_206':'AV_206p','AV_316':'AV_316hp','AV_202':'AV_202p','GIL_504':'GIL_504h','ICC_831':'ICC_831p','AV_204':'AV_204p','ICC_829':'ICC_829p','ICC_834':'ICC_834h','ICC_832':'ICC_832p','SC_754':'SC_754p','CATA_190h':'CATA_190p','TLC_513t':'TLC_513hp','CORE_EX1_323':'EX1_tk33'}

HERO_POWERS.update({'TOY_829':'TOY_829hp3','TOY_829t2':'TOY_829hp3'})

HERO_POWERS.update({'SC_004':'SC_004hp','WON_092h':'WON_092p'})

HERO_POWERS['SC_400']='SC_400p'
HERO_POWERS['WW_0700']='WW_0700p'
HERO_POWERS.update({'ICC_828':'ICC_828p','CORE_ICC_828':'ICC_828p'})

class HeroPowers:
    def _start_power_effects(self,owner,operations,target=0,*,repeats=1,post_operations=()):
        program,context=self._power_program(owner,operations,target,repeats=repeats,post_operations=post_operations)
        return self._start_play_effects(program,context)

    def _power_program(self,owner,operations,target=0,*,repeats=1,post_operations=(),frame_override=None):
        """Run ordered power operations through the same choice checkpoints as cards."""
        transformed=[]
        for operation in operations:
            name=operation[0]
            if name=='damage_enemy_hero' and target>0 and getattr(self.players[owner],'historical_stormwind_power_targets',False):name='damage'
            if name=='draw':transformed.append(('historical_copy_power_draw',operation[1]))
            elif name=='origin_draw':transformed.append(('historical_copy_power_origin_draw',operation[1],operation[2]))
            elif name=='filtered_draw':transformed.append(('historical_copy_power_filtered_draw',operation[1],operation[2]))
            elif name in ('damage','damage_enemy_hero','damage_random_enemy','damage_own_hero'):
                mode={'damage_own_hero':'own_hero','damage':'target','damage_enemy_hero':'enemy_hero','damage_random_enemy':'random_enemy'}[name]
                transformed.append(('historical_copy_power_hit',mode,operation[1]))
            else:transformed.append(operation)
        # Permanent additions belong to each power trigger, including replacements.
        player=self.players[owner]
        if getattr(player,'historical_power_armor',0):transformed.append(('armor',player.historical_power_armor))
        if getattr(player,'historical_power_attack',0):transformed.append(('hero_attack',player.historical_power_attack))
        frame=frame_override if frame_override is not None else (getattr(self,'_power_frame',None) or {})
        if target and not any(op[0]=='historical_copy_power_hit' for op in transformed) and (frame.get('freeze') or self._active('ICC_068',owner)):
            transformed.append(('freeze',))
        transformed=transformed*repeats+list(post_operations)
        power=player.primary_power
        if power is not None and 'yoink_remaining' in power:
            from .historical_obligation_spells import op as obligation_op
            transformed.append(obligation_op('yoink_used',power['uid']))
        context=dict(owner=owner,source=None,target=target,bonus=0,lifesteal=False,
                     power=True,power_freeze=frame.get('freeze',False),power_damage_bonus=frame.get('damage_bonus',0)+getattr(player,'historical_permanent_power_damage',0))
        if target>0 and self._active('TRL_319',owner):
            victim=next((m for player in self.players for m in player.minions if m.uid==target),None)
            if victim is not None:
                board=self.players[victim.owner].board;index=board.index(victim)
                neighbors=[board[i] for i in (index-1,index+1) if 0<=i<len(board) and board[i] in self.players[victim.owner].minions]
                original=tuple(transformed)
                transformed=list(original)+[('replay_context',original,dict(context,target=m.uid)) for m in neighbors]
        return tuple(transformed),context

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
        p.historical_power_generation=getattr(p,"historical_power_generation",0)+1
        previous=p.primary_power
        p.primary_power=deepcopy(power)
        if p.primary_power is not None:p.primary_power['uid']=self._new_id()
        from .historical_valeera import power_changed
        power_changed(self,owner,previous)
        p.power_used=False
        p.historical_power_turn=dict(turn=self.turn,count=0)

    def _play_hero_card(self,owner,cid):
        if cid not in HERO_POWERS:raise UnsupportedCard('Hero replacement not implemented: '+cid)
        p=self.players[owner];data=self.cards[cid]
        # This is the modern HERO card, not the old 15-Health minion version.
        p.hero_card_id=cid
        if cid not in ('CATA_190h','SC_754','WW_0700'):p.hero_class=data['cardClass']
        self._gain_armor(owner,data.get('armor',0))
        self._replace_primary_power(owner,dict(card_id=HERO_POWERS[cid]))
        if cid=='WW_0700':
            from .historical_lone_ranger import rotate as rotate_reno
            rotate_reno(self,owner)
        if cid=='BOT_238':
            from .historical_mad_genius import rotate
            rotate(self,owner)

    def _replacement_power_cost(self,owner):
        power=self.players[owner].primary_power
        return power.get('cost',self.cards[power['card_id']]['cost']) if power is not None else None

    def _replacement_power_available(self,owner):
        power=self.players[owner].primary_power
        if power is None:return False
        if power.get('basic_starting_class')=='SHAMAN':
            from .game import BASIC_TOTEM_POOL
            return len(self.players[owner].board)<7 and bool(BASIC_TOTEM_POOL.resolve(self.cards,self.cards,exclude={m.card_id for m in self.players[owner].minions}))
        if power.get('basic_starting_class') in ('PALADIN','DEATHKNIGHT'):return len(self.players[owner].board)<7
        if power['card_id'] in ('AV_113p','BOT_238p6','AV_258pt','ICC_829p','OG_006b','DRG_238p3','DRG_238p4'):return len(self.players[owner].board)<7
        if power.get('upgraded_starting_class') in ('PALADIN','DEATHKNIGHT','SHAMAN'):return len(self.players[owner].board)<7
        if power['card_id'] in ('ICC_827p','YOD_009h','BOT_238p','AV_258p','AV_258pt7','GIL_504h','END_003p','JAIL_800hp1','JAIL_800hp2'):return False  # Passive, never an activatable action.
        return power['card_id'] not in ('EX1_tk33','EDR_847p') or len(self.players[owner].board)<7

    def _replacement_power_targets(self,owner):
        if not self._replacement_power_available(owner):return ()
        power=self.players[owner].primary_power
        if getattr(self.players[owner],'historical_stormwind_power_targets',False) and (power.get('basic_starting_class') or power.get('upgraded_starting_class'))=='HUNTER':
            from .historical_stormwind_questline_finish import hunter_targets
            return hunter_targets(self,owner)
        if (self.players[owner].primary_power.get('basic_starting_class') or self.players[owner].primary_power.get('upgraded_starting_class')) in ('MAGE','PRIEST'):return tuple(self._visible_targets(owner,magic=True))
        if self.players[owner].primary_power['card_id'] in ('AV_207p','AV_207p2','BOT_238p1','AV_200p2','TRL_065h','ICC_833h','ICC_830p','AV_202p','ICC_831p','EX1_625t','EX1_625t2','TOY_400t6p','TOY_400t6p2','BT_429p','BT_429p2','TOY_829hp','TOY_829hp3','WW_0700p1','WW_0700p2','WW_0700p3','WW_0700p4','WW_0700p5','WW_0700p6','WW_0700p7'):
            return tuple(self._visible_targets(owner,magic=True))
        if self.players[owner].primary_power['card_id']=='UNG_917t1':
            visible=set(self._visible_targets(owner,magic=True))
            return tuple(m.uid for player in self.players for m in player.minions if m.uid in visible and m.health>0 and not m.dormant and has_tribe(self._card_data(m),'BEAST'))
        if self.players[owner].primary_power['card_id']=='ICC_481p':
            visible=set(self._visible_targets(owner,magic=True))
            return tuple(m.uid for m in self.players[owner].minions if m.uid in visible and m.health>0 and not m.dormant)
        if self.players[owner].primary_power['card_id']=='SC_754p':
            visible=set(self._visible_targets(owner,magic=True))
            return tuple(m.uid for m in self.players[owner].minions if m.uid in visible and m.health>0) or (0,)
        if self.players[owner].primary_power['card_id']=='EDR_448p':
            visible=set(self._visible_targets(owner,magic=True))
            return tuple(m.uid for m in self.players[owner].minions
                         if m.uid in visible and m.health>0 and not m.dormant)
        return (0,)

    def _replacement_power_effect(self,owner,target=0):
        p=self.players[owner];power=p.primary_power
        if power is None:return False
        if power['card_id']=='ULD_291p':
            self._start_power_effects(owner,(('historical_utility_virnaal',),));return True
        if power['card_id']=='ULD_140p':
            from .historical_draw_batches import draw
            self._start_power_effects(owner,(draw(mode='set_cost',args=(0,)),));return True
        if power['card_id']=='UNG_917t1':
            self._start_power_effects(owner,(('buff',3,3),),target=target);return True
        if power['card_id']=='SC_400p':
            self._start_power_effects(owner,(('summon','SC_403t',1),('historical_utility_stimpack',)));return True
        if power['card_id']=='ICC_828p':
            self._start_power_effects(owner,(('forge_zombeast_plain',),));return True
        if power['card_id']=='SC_004hp':
            self._start_power_effects(owner,(('historical_utility_ravage',),));return True
        if power['card_id']=='WON_092p':
            self._start_power_effects(owner,(('hero_divine_shield',),('hero_attack',2),('historical_upgrade_hero_windfury',)));return True
        from .historical_utility_spells import reno_power_operations
        reno_operations=reno_power_operations(self,owner)
        if reno_operations is not None:
            self._start_power_effects(owner,reno_operations,target=target);return True
        if power['card_id'] in ('TOY_829hp','TOY_829hp3'):
            from .generation_cards import pool,discover
            operations=[('damage',3)]
            if power['card_id']=='TOY_829hp':operations.append(discover(pool(card_type='MINION',tribe='UNDEAD',classes='own_or_neutral')))
            self._start_power_effects(owner,operations,target=target);return True
        if 'basic_starting_class' in power:
            self._start_power_effects(owner,self._basic_power_operations(power['basic_starting_class']),target=target);return True
        if 'upgraded_starting_class' in power:
            self._start_power_effects(owner,self._genn_power_operations(owner),target=target);return True
        cid=power['card_id']
        from .historical_mad_genius import power_operations as boom_operations
        boom=boom_operations(self,owner)
        if boom is not None:
            self._start_power_effects(owner,boom,target=target);return True
        from .historical_brukan import power_operations as brukan_operations
        brukan=brukan_operations(self,owner)
        if brukan is not None:
            self._start_power_effects(owner,brukan);return True
        if cid=='AV_113p':
            self._start_power_effects(owner,(('companions_random',),));return True
        if cid=='AV_207p':
            self._start_power_effects(owner,(('historical_devout_heal',),),target=target);return True
        if cid=='AV_207p2':
            self._start_power_effects(owner,(('historical_copy_power_hit','target',5),),target=target);return True
        if cid=='AV_200p2':
            self._start_power_effects(owner,(('historical_arcane_burst',),),target=target);return True
        if cid=='TRL_065h':
            self._start_power_effects(owner,(('historical_copy_power_hit','target',2),),target=target);return True
        if cid=='AV_203p':
            self._start_power_effects(owner,(('historical_copy_coolant',),));return True
        if cid=='ICC_833h':
            self._start_power_effects(owner,(('historical_jaina_touch',),),target=target);return True
        if cid=='ICC_830p':
            self._start_power_effects(owner,(('historical_copy_power_hit','target',2),),target=target);return True
        if cid=='ICC_481p':
            self._start_power_effects(owner,(('historical_copy_evolve_target',1),),target=target);return True
        if cid=='AV_205p':
            from .historical_guff_cariel import start_power
            start_power(self,owner);return True
        if cid=='AV_206p':
            self._start_power_effects(owner,(('historical_cariel_buff',),));return True
        if cid=='AV_316hp':
            self._start_power_effects(owner,(('on_draw_shuffle','AV_316t4',1,0),('draw',1)));return True
        if cid=='AV_202p':
            self._start_power_effects(owner,(('historical_late_slam',),),target=target);return True
        if cid=='ICC_831p':
            self._start_power_effects(owner,(('historical_dark_siphon',),),target=target);return True
        if cid=='AV_204p':
            self._start_power_effects(owner,(('hero_attack',2),));return True
        if cid in ('ICC_829p','ICC_834h'):
            self._start_power_effects(owner,((('historical_ebon_horsemen',) if cid=='ICC_829p' else ('historical_ebon_bladestorm',)),));return True
        if cid=='ICC_832p':
            from .historical_combined_choices import start_power
            start_power(self,owner);return True
        if cid in ('TOY_400t6p','TOY_400t6p2','BT_429p','BT_429p2','TOY_829hp','TOY_829hp3'):
            self._start_power_effects(owner,(('damage',5),),target=target)
            power['remaining']-=1
            if power['remaining']<=0:self._replace_primary_power(owner,power.get('restore'))
            else:power['card_id']='BT_429p2' if cid in ('BT_429p','BT_429p2') else 'TOY_400t6p2'
            return True
        from .historical_copy_batches import HISTORICAL_POWER_OPERATIONS
        if cid in HISTORICAL_POWER_OPERATIONS:
            self._start_power_effects(owner,HISTORICAL_POWER_OPERATIONS[cid],target=target);return True
        from .historical_galakrond_batches import POWERS,power_operations
        if cid in POWERS:
            self._start_power_effects(owner,power_operations(cid));return True
        if cid in IMBUE_POWERS.values():
            self._start_power_effects(owner,self._imbue_power_operations(owner)*(2 if cid=='END_000p' and self._active('END_036',owner) else 1),target=target)
        elif cid=='OG_006b':self._summon(owner,'OG_006a',entry_origin='hero_power',entry_site='vilefin_power')
        elif cid=='CATA_190p':
            self._start_power_effects(owner,(('hero_attack',5),))
        elif cid=='TLC_513hp':
            self._start_power_effects(owner,(('origin_draw',False,False),('origin_draw',False,False)))
        elif cid=='EX1_tk33':
            self._summon(owner,'EX1_tk34',entry_origin='hero_power',entry_site='replacement_power')
        elif cid in ('TLC_632t','TLC_632t2','JAIL_EVENT_101hp','UNG_934t2'):
            candidates=[self.hero_id(1-owner)]+[m.uid for m in self.players[1-owner].minions if m.health>0]
            amount=power.get('damage',2) if cid=='JAIL_EVENT_101hp' else 8
            self._start_power_effects(owner,(('damage_random_enemy',amount),))
            if cid in ('TLC_632t','TLC_632t2'):
                power['remaining']-=1
                if power['remaining']==0:self._replace_primary_power(owner,power['restore'])
                else:power['card_id']='TLC_632t2'
        else:raise UnsupportedCard('Replacement Hero Power: '+cid)
        return True

    def _power_capture_summon(self,minion):
        power=self.players[minion.owner].primary_power
        if power and power['card_id']=='JAIL_EVENT_101hp' and has_tribe(self._card_data(minion),'DEMON'):
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

HERO_POWERS.update({'CORE_ICC_832':'ICC_832p','CORE_ICC_831':'ICC_831p'})
