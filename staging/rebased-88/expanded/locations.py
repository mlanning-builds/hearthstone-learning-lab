"""Explicit location rules; unknown locations remain rejected by the registry."""
from .historical_saidan import add as _saidan_add
from dataclasses import dataclass, field
from engine.game import Action
from engine.cards import UnsupportedCard

LOCATION_RULES = {
    'GDB_136t':'none',
    'VAC_923t':'friendly_minion',
    'SC_751':'none',
    'WW_359t':'minion',
    'MEND_044':'minion',
    'EDR_454':'friendly_dragon',
    'TLC_433t2': 'character',
    'JAIL_511': 'none',
    'CORE_REV_990': 'minion',
    'CATA_477': 'hand_minion',
    'CATA_584': 'none',
    'JAIL_877': 'none',
}


@dataclass
class Location:
    uid: int
    card_id: str
    owner: int
    durability: int
    ready_turn: int = 0
    attached_death_effects: list = field(default_factory=list)
    rule_state: dict = field(default_factory=dict)


class Locations:
    def _remove_location(self, location):
        p=self.players[location.owner]
        if location not in p.board:return
        position=p.board.index(location)
        p.board.remove(location)
        from .historical_movements import record
        record(self,'destroyed')
        self._evolving_removed(location,position)
        self._log('location_removed',player=location.owner,card=location.card_id,entity=location.uid)
        if location.card_id=='TLC_433t2':
            self._rule_events.append(('captured_effects',dict(
                operations=(('death_summon','TLC_433t',1),),
                context=dict(owner=location.owner,source=None,target=0,bonus=0,lifesteal=False,death_position=position)),[]))
        if location.attached_death_effects:
            from copy import deepcopy
            self._rule_events.append(('captured_effects',dict(operations=tuple(deepcopy(location.attached_death_effects)),
                context=dict(owner=location.owner,source=None,target=0,bonus=0,lifesteal=False,death_position=position)),[]))
        self._refresh_auras()

    def _place_location(self, owner, cid, position=-1):
        if cid not in LOCATION_RULES:
            raise UnsupportedCard('Location not implemented: '+cid)
        p=self.players[owner]
        if len(p.board)>=7: return None
        location=Location(self._new_id(),cid,owner,self.cards[cid]['health'])
        from .historical_summon_faction_finish import LOCATION_DEATHS
        location.attached_death_effects.extend(LOCATION_DEATHS.get(cid,()))
        if position<0:position=len(p.board)
        p.board.insert(position,location)
        self._log('location_played',player=owner,card=cid,entity=location.uid,position=position)
        self._refresh_auras()
        return location

    def _location_actions(self):
        p=self.players[self.current]
        actions=[]
        for location in p.locations:
            if self.turn<location.ready_turn:continue
            mode=LOCATION_RULES[location.card_id]
            if location.card_id=='ETC_533' and p.corpses<3:continue
            if location.card_id=='GDB_136t':
                from .historical_galaxy_lens import targets as lens_targets
                targets=lens_targets(self,location)
            elif mode=='hand_card':
                targets=[c.uid for c in p.hand]
            elif mode=='hand_minion':
                targets=[c.uid for c in p.hand if self.cards[c.card_id]['type']=='MINION']
            elif mode=='none':
                targets=[0]
            else:
                targets=self._targets_for(location.card_id,self.current,mode)
            for target in targets:actions.append(Action('activate',location.uid,target))
        return actions

    def _activate_location(self, action):
        owner=self.current;p=self.players[owner]
        location=next(x for x in p.locations if x.uid==action.source)
        cid=location.card_id
        if cid=='ETC_533' and p.corpses<3:raise UnsupportedCard('Mosh Pit requires three Corpses')
        evolving=self._evolving_operations(location)
        position=p.board.index(location)
        if cid=='JAIL_887':
            from copy import deepcopy
            card=next((c for c in p.hand if c.uid==action.target),None)
            if card is None:raise UnsupportedCard('Prison requires a hand card')
            # Capture before final-charge removal publishes the Deathrattle.
            location.rule_state.setdefault('prison_cards',[]).append(deepcopy(card))
        self._log('location_activated',player=owner,card=cid,entity=location.uid,
                  target=action.target if cid not in ('CATA_477','JAIL_887') else 'PRIVATE_HAND_CARD')
        p.historical_locations_used=getattr(p,'historical_locations_used',0)+1
        self._queue_event('historical_location_used',owner=owner,source=location.uid,card_id=cid)
        location.durability-=1
        # Skip the owner's next turn: each engine turn is one player's turn.
        location.ready_turn=self.turn+4
        # Patch 32.0: final-charge summons have the freed location slot available.
        if location.durability==0:
            self._remove_location(location)
        from .fabled_effects import LOCATION_EFFECTS as FABLED_EFFECTS
        from .choice_generators import LOCATION_EFFECTS
        from .automatic_casting import LOCATION_EFFECTS as AUTO_EFFECTS
        from .herald import LOCATION_EFFECTS as HERALD_EFFECTS
        from .standard_integrations import LOCATION_EFFECTS as STANDARD_EFFECTS
        from .historical_copy_batches import TIME_LOCATION_EFFECTS
        from .historical_student_equipment import LOCATION_EFFECTS as STUDENT_LOCATION_EFFECTS
        from .historical_utility_spells import LOCATION_EFFECTS as UTILITY_LOCATION_EFFECTS
        from .historical_location_timed import LOCATION_EFFECTS as TIMED_LOCATION_EFFECTS
        if cid in TIMED_LOCATION_EFFECTS:
            self._start_play_effects(TIMED_LOCATION_EFFECTS[cid],dict(owner=owner,source=None,location_source=location,card_id=cid,target=action.target,bonus=0,lifesteal=False))
        elif cid in UTILITY_LOCATION_EFFECTS:
            self._start_play_effects(UTILITY_LOCATION_EFFECTS[cid],dict(owner=owner,source=None,location_source=location,card_id=cid,target=action.target,bonus=0,lifesteal=False))
        elif cid in STUDENT_LOCATION_EFFECTS:
            self._start_play_effects(STUDENT_LOCATION_EFFECTS[cid],dict(owner=owner,source=None,location_source=location,card_id=cid,target=action.target,bonus=0,lifesteal=False))
        elif cid in TIME_LOCATION_EFFECTS:
            self._start_play_effects(TIME_LOCATION_EFFECTS[cid],dict(owner=owner,source=location,card_id=cid,target=action.target,bonus=0,lifesteal=False))
        elif evolving is not None:
            self._start_play_effects(evolving,dict(owner=owner,source=location,card_id=cid,target=action.target,bonus=0,lifesteal=False))
        elif cid in FABLED_EFFECTS:
            self._start_play_effects(FABLED_EFFECTS[cid],dict(owner=owner,source=location,card_id=cid,target=action.target,bonus=0,lifesteal=False))
        elif cid in HERALD_EFFECTS:
            self._start_play_effects(HERALD_EFFECTS[cid],dict(owner=owner,source=location,card_id=cid,target=0,bonus=0,lifesteal=False))
        elif cid in AUTO_EFFECTS:
            self._start_play_effects(AUTO_EFFECTS[cid],dict(owner=owner,source=location,card_id=cid,target=0,bonus=0,lifesteal=False))
        elif cid in STANDARD_EFFECTS:
            self._start_play_effects(STANDARD_EFFECTS[cid],dict(owner=owner,source=location,card_id=cid,target=action.target,bonus=0,lifesteal=False))
        elif cid in LOCATION_EFFECTS:
            self._start_play_effects(LOCATION_EFFECTS[cid],dict(owner=owner,source=location,card_id=cid,target=0,bonus=0,lifesteal=False))
        elif cid=='TLC_449':
            from .generation_extensions import RULES as GENERATION_RULES
            self._start_play_effects(GENERATION_RULES[cid][1],dict(owner=owner,source=None,location_source=location,card_id=cid,target=0,bonus=0,lifesteal=False))
        elif cid=='SC_751':
            self._effect(('historical_copy_protoss_next','minion',3,False),dict(owner=owner,source=location,target=0,bonus=0,lifesteal=False))
        elif cid=='WW_359t':
            self._sleep_minion(self._dormant_entity(action.target),3)
        elif cid=='MEND_044':
            self._effect(('lasting_clearing',),dict(owner=owner,source=location,target=action.target,bonus=0,lifesteal=False))
        elif cid=='TLC_433t2':
            self._damage(action.target,4,damage_source=location,damage_owner=owner)
        elif cid=='EDR_454':
            self._effect(('stored_egg',),dict(owner=owner,source=location,target=action.target,bonus=0,lifesteal=False,summon_position=position if location.durability==0 else position+1))
        elif cid=='JAIL_511':
            self._start_play_effects([('force_spire',)],dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False))
        elif cid=='CORE_REV_990':
            target=self._find(action.target)
            self._damage(target.uid,1,damage_source=location,damage_owner=owner)
            self._buff(target,2,0)
        elif cid=='CATA_477':
            card=next(c for c in p.hand if c.uid==action.target)
            _saidan_add(card,'attack_bonus',2);_saidan_add(card,'health_bonus',2)
        elif cid=='CATA_584':
            shots=6 if p.fire_spell_played else 3
            self._effect(('missiles','enemies',shots),dict(owner=owner,source=None,
                         target=0,bonus=0,lifesteal=False))
        elif cid=='JAIL_877':
            self._summon(owner,'JAIL_877t',position if location.durability==0 else position+1, entry_origin='location', entry_site='locations._activate_location')
        else:
            raise UnsupportedCard('Location effect not implemented: '+cid)
        self._settle()

LOCATION_RULES.update({'WON_053t':'minion','WON_053t2':'none','WON_053t3':'none','WON_053t4':'none','WON_053t5':'none','WON_053t6':'none','WON_053t7':'friendly_minion'})

from .historical_student_equipment import LOCATION_RULES as STUDENT_LOCATION_RULES
LOCATION_RULES.update(STUDENT_LOCATION_RULES)

from .historical_utility_spells import LOCATION_RULES as UTILITY_LOCATION_RULES
LOCATION_RULES.update(UTILITY_LOCATION_RULES)

from .historical_location_timed import LOCATION_RULES as TIMED_LOCATION_RULES
LOCATION_RULES.update(TIMED_LOCATION_RULES)

# Bloodpetal Biome generates only when activated, never on placement.
LOCATION_RULES['TLC_449']='none'
