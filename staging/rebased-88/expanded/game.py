"""Experimental all-class rules extension; NOT complete Standard.

User-run validation is pending. Unsupported decks fail before state creation.
The original engine and saved training fingerprints are preserved.
"""
from .historical_saidan import add as _saidan_add
from dataclasses import dataclass, field, asdict, replace
from copy import deepcopy
import random
from collections import deque
from .identities import canonical_identity,identity_resolver
from .selectors import has_tribe, has_any_tribe, has_school, has_class, classes as card_classes
from .quest_families import QuestFamilies
from .muradin import Muradin
from .azshara import Azshara
from .gelbin import Gelbin
from .broxigar import Broxigar
from .garona import Garona
from .rafaam import Rafaam
from .fabled_effects import FabledEffects
from .stored_obligations import StoredObligations
from .learned_spells import LearnedSpells
from .zone_triggers import ZoneTriggers
from .temporary_control import TemporaryControl
from .evolving_locations import EvolvingLocations
from .resolution import Resolution
from .shatter import Shatter
from .rewind import Rewind
from .dark_gifts import DarkGifts
from .dark_gift_generators import DarkGiftGenerators
from .stored_cards import StoredCards
from .lasting_rules import LastingRules
from .entity_effects import EntityEffects
from .transformations import Transformations
from .rewind_generators import RewindGenerators
from .imbue_consumers import ImbueConsumers
from .entry_trace import EntryTrace
from .summons import SummonEvents
from .batch30 import SharedBatch30
from .composed import ComposedEffects
from .persistent import PersistentEffects
from .batch60 import Batch60
from .local_family import LocalFamily
from .draw_events import DrawEvents
from .bonus_effects import BonusEffects
from .dormant import Dormancy
from .provenance import Provenance
from .held_upgrades import HeldUpgrades
from .temporary import TemporaryCards
from .imbue import Imbue
from .hero_powers import HeroPowers
from .quests import Quests, QUESTS
from .dreams import Dreams
from .permanents import Permanents, Permanent, PERMANENT_IDS
from .discovery import Discovery
from .generation import GenerationEffects
from .choice_generators import ChoiceGenerators
from .tribal_groups import TribalGroups
from .alternate_play import AlternatePlay, EITHER_SIDE
from .forced_combat import ForcedCombat
from .on_draw import OnDraw
from .starting_rules import StartingRules
from .deck_setup import DeckSetup
from .infinity import InfinityEffects
from .turn_deadlines import TurnDeadlines
from .replacements import Replacements
from .genn import Genn
from .stat_rules import StatRules
from .tiny_pal import TinyPal
from .healing_replacement import HealingReplacement
from .exceptional_finish import ExceptionalFinish
from .minion_forge import MinionForge
from .custom_builders import CustomBuilders
from .morchie import Morchie
from .random_targets import RandomTargets
from .counterfeits import Counterfeits
from .dragon_soul import DragonSoul
from .titanographer import Titanographer
from .remaining_setup import RemainingSetup
from .hand_investigations import HandInvestigations
from .future_summons import FutureSummons, COMPANIONS
from .colossals import ColossalEntries
from .colossal_bodies import ColossalBodies
from .herald import Herald, ARMY_OF, multiplier
from .automatic_casting import AutomaticCasting
from .maps import Maps
from .leylines import Leylines, LEYLINES
from .prepare import Prepare
from .historical_upgrades import HistoricalUpgrades
from .effect_replay import EffectReplay
from .spell_casting import SpellCasting
from .dormant_cards import INITIAL as INITIAL_DORMANCY
from .lifecycle import Lifecycle
from .batch_effects import BatchEffects
from .pools import GenerationPool, require_fixed_cards
from .locations import Locations, Location, LOCATION_RULES
from .battlefield import Battlefield
from .systems import Systems
from .secrets import Secrets, SECRETS
from engine.game import Game as LegacyGame, Player as LegacyPlayer, Minion as LegacyMinion, Card, Action, TARGETS
from engine.cards import UnsupportedCard
from .cards import registry, HELD_TARGETS, RULES, PASSIVE, DEATH_EFFECTS, PLAYABLE_TOKENS, END_EFFECTS, NO_CORPSE, CHOICES, WEAPON_TRIGGERS, COIN_IDS
from .decks import validate

TOTEMS=('CS2_050','CS2_051','CS2_058','NEW1_009')
BASIC_TOTEM_POOL=GenerationPool('Basic Shaman hero power',TOTEMS,
    'Existing pinned engine base-power definition; four explicit basic totems')

@dataclass
class Player(LegacyPlayer):
    equipped_card: object = field(default=None, repr=False)
    avatar_form: list = field(default_factory=list)
    eternal_life: bool = False
    ashalon_adaptations: list = field(default_factory=list)
    gorishi_stacks: int = 0
    damaged_characters_turn: set = field(default_factory=set)
    temporary_mana_available: int = 0
    mana_capacity: int = 10
    hand_capacity: int = 10
    manastorm_effects: int = 0
    companion_ids: list = field(default_factory=lambda:list(COMPANIONS))
    companion_extra: int = 0
    companion_upgrades: int = 0
    void_soul_level: int = 1
    bwonsamdi_boons: list = field(default_factory=list)
    herald_count: int = 0
    deathwing_discount: int = 0
    overdraw_return_active: bool = False
    overdraw_cache: list = field(default_factory=list)
    hero_lifesteal_until: int = -1
    hero_attacks_total: int = 0
    extra_turns_pending: int = 0
    crystal_core: bool = False
    time_warp_used: bool = False
    skipped_turns_pending: int = 0
    leyline_discount: int = 0
    leyline_effect: int = 0
    leyline_repeats: int = 0
    last_turn_ended: int = -1
    imbue_start_checked: bool = False
    hamuul_active: bool = False
    hamuul_spells: int = 0
    undead_play_turn: int = -1
    full_moon: bool = False
    life_rewards: int = 0
    geddon_draw: bool = False
    sorry_enabled: bool = False
    shield_hits: int = 0
    quest: dict = None
    quests_played: int = 0
    primary_power: dict = None
    secondary_power: dict = None
    hero_card_id: str = None
    ninja_returns: bool = False
    murloc_summon_bonus: int = 0
    discoveries_this_turn: int = 0
    discoveries_total: int = 0
    payment_effects: list = field(default_factory=list)
    hero_healed_turn: bool = False
    imp_upgrades: int = 0
    dragons_have_rush: bool = False
    dragons_played_turn: int = 0
    last_minion_played: str = None
    minions_set_cost: int = None
    max_health: int = 30
    recruit_attack_bonus: int = 0
    recruit_health_bonus: int = 0
    divine_shield: bool = False
    turns_taken: int = 0
    minion_played_this_turn: bool = False
    minion_played_last_turn: bool = False
    minions_died_turn: int = 0
    spells_cast_turn: int = 0
    hero_damage_events_turn: int = 0
    hero_health_changed_turn: bool = False
    overloaded_total: int = 0
    hero_immune_expiry_players: list = field(default_factory=list)
    healing_block_expiry_players: list = field(default_factory=list)
    hero_power_uses: int = 0
    spell_schools_this_turn: set = field(default_factory=set)
    discard_history: list = field(default_factory=list)
    shuffle_history: list = field(default_factory=list)
    secrets: list = field(default_factory=list)
    replay_history: list = field(default_factory=list)
    played_history: list = field(default_factory=list)
    death_history: list = field(default_factory=list)
    death_records: list = field(default_factory=list)
    spells_turn: list = field(default_factory=list)
    spells_previous: list = field(default_factory=list)
    fel_spells_cast: int = 0
    friendly_attacks: int = 0
    last_paid_cost: int = 0
    spell_damage_turn: int = 0
    hero_damage_taken_turn: int = 0
    healing_done_turn: int = 0
    permanent_healing_bonus: int = 0
    reborn_history: list = field(default_factory=list)
    scheduled_effects: list = field(default_factory=list)
    end_repeat_expiries: list = field(default_factory=list)
    permanent_end_damage: list = field(default_factory=list)
    played_tribes: set = field(default_factory=set)
    played_schools: set = field(default_factory=set)
    previous_tribes: set = field(default_factory=set)
    previous_schools: set = field(default_factory=set)
    next_power_increase: int = 0
    next_power_cost_effects: list = field(default_factory=list)
    cost_effects: list = field(default_factory=list)
    timed_cost_increases: list = field(default_factory=list)
    hero_class: str = 'DEATHKNIGHT'
    temporary_attack: int = 0
    overload_next: int = 0
    locked_mana: int = 0
    cards_played: int = 0
    spell_repeat_charges: int = 0
    imbue_count: int = 0
    frozen_until: int = -1
    fire_spell_played: bool = False

    @property
    def all_minions(self):
        return [entity for entity in self.board if not isinstance(entity,(Location,Permanent))]

    @property
    def minions(self):
        return [entity for entity in self.all_minions if not entity.dormant]

    @property
    def permanents(self):
        return [entity for entity in self.board if isinstance(entity,Permanent)]

    @property
    def locations(self):
        return [entity for entity in self.board if isinstance(entity,Location)]

@dataclass
class Minion(LegacyMinion):
    imbue_attack_expiries: list = field(default_factory=list)
    dormant: int = 0
    rule_state: dict = field(default_factory=dict)
    played_turn: int = -1
    attached_death_effects: list = field(default_factory=list)
    temporary_keywords: list = field(default_factory=list)
    attack_deficit: int = 0
    remembered_discards: list = field(default_factory=list)
    frozen_until: int = -1
    silenced: bool = False
    aura_attack: int = 0
    aura_health: int = 0
    temporary_attack: int = 0


from .magnetic import Magnetic,MAGNETIC_IDS
from .historical_colossal import HistoricalColossal

from .historical_hand_primitives import HistoricalHandPrimitives

from .historical_battlecry_buffs import HistoricalBattlecryBuffs

from .historical_scaling import HistoricalScaling

from .historical_passive_stats import HistoricalPassiveStats
from .historical_removal import HistoricalRemoval

from .historical_conditional_battlecries import HistoricalConditionalBattlecries

class Game(HistoricalConditionalBattlecries,HistoricalPassiveStats,HistoricalRemoval,HistoricalScaling,HistoricalBattlecryBuffs,HistoricalHandPrimitives,HistoricalColossal,Magnetic,HistoricalUpgrades,ExceptionalFinish,MinionForge,CustomBuilders,Morchie,RandomTargets,Counterfeits,DragonSoul,Titanographer,RemainingSetup,QuestFamilies,Muradin,Azshara,Gelbin,Broxigar,Garona,Rafaam,FabledEffects,StoredObligations,LearnedSpells,ZoneTriggers,TemporaryControl,EvolvingLocations,ColossalBodies,Herald,ColossalEntries,FutureSummons,AutomaticCasting,HandInvestigations,TinyPal,HealingReplacement,StatRules,Genn,Replacements,TurnDeadlines,InfinityEffects,DeckSetup,StartingRules,Maps,Leylines,ImbueConsumers,RewindGenerators,Transformations,DarkGiftGenerators,EntityEffects,LastingRules,StoredCards,DarkGifts,Rewind,Shatter,Imbue, Permanents, Dreams, Quests, HeroPowers, Discovery, GenerationEffects, ChoiceGenerators,TribalGroups, AlternatePlay, ForcedCombat, OnDraw, SpellCasting, EffectReplay, Prepare, TemporaryCards, HeldUpgrades, Provenance, Dormancy, BonusEffects, DrawEvents, LocalFamily, Batch60, PersistentEffects, ComposedEffects, SharedBatch30, SummonEvents, EntryTrace, Secrets, BatchEffects, Systems, Lifecycle, Resolution, Locations, Battlefield, LegacyGame):
    VERSION='all-class-experimental-0.15-candidate'

    def __init__(self,decks,seed=0,first_player=0,max_turns=89,record=True,*,transfer_student_form=None,starting_deck_contracts=None,special_approximations=True):
        from .historical_transfer_student import BOARD_FORMS
        if transfer_student_form is not None and transfer_student_form not in BOARD_FORMS:raise ValueError('Invalid Transfer Student board form')
        self.transfer_student_form=transfer_student_form
        self.special_approximations=bool(special_approximations)
        self.approximation_profile=None
        if len(decks)!=2 or first_player not in (0,1): raise ValueError('Provide two decks and first player 0 or 1')
        if type(max_turns) is not int or not 1<=max_turns<=89: raise ValueError('Invalid turn limit')
        from .static_metadata import freeze_registry
        self.cards=freeze_registry(registry())
        opening_rng=random.Random(seed)
        if self.special_approximations:
            from .special_approximations import install,opening_contracts
            install(self)
            roots={cid for deck in decks for cid in deck.cards}.intersection(('BOT_914','DAL_800','TOY_700'))
            defaults=opening_contracts(self.cards,roots)
            starting_deck_contracts={**defaults,**(starting_deck_contracts or {})}
            if self.transfer_student_form is None:
                self.transfer_student_form=opening_rng.choice(sorted(BOARD_FORMS))
        from .historical_starting_decks import replace_submitted
        decks,self._starting_deck_selections=replace_submitted(decks,self.cards,opening_rng,starting_deck_contracts)
        recipe_owners={row['owner'] for row in self._starting_deck_selections}
        from .fabled_decks import expand_bundle_ids
        try:decks=[deck if owner in recipe_owners else replace(deck,cards=expand_bundle_ids(deck.cards)) for owner,deck in enumerate(decks)]
        except ValueError as exc:raise UnsupportedCard(str(exc)) from exc
        for deck_owner,deck in enumerate(decks):
            if deck_owner in recipe_owners:continue  # Entire sourced recipe pool was validated before selection.
            errors=validate(deck,self.cards)
            if errors: raise UnsupportedCard('; '.join(errors))
        from .action_runner import ActionRunner
        self._action_runner=ActionRunner()
        from .combat_resolver import CombatResolver
        self._combat_resolver=CombatResolver()
        from .choice_resolver import ChoiceResolver
        self._choice_resolver=ChoiceResolver()
        from .zone_manager import ZoneManager
        self._zone_manager=ZoneManager()
        from .effect_executor import EffectExecutor
        self._effect_executor=EffectExecutor()
        self.seed=seed; self.rng=opening_rng; self.uid=0; self.players=[]
        for deck in decks:
            shuffled=list(deck.cards); self.rng.shuffle(shuffled)
            physical=[]
            for cid in shuffled:
                c=Card(self._new_id(),cid);data=self.cards[cid]
                c._starting_owner=len(self.players)
                c._starting_identity=canonical_identity(data,self.cards)
                physical.append(c)
            self.players.append(Player(physical,list(deck.cards),tuple(deck.runes),hero_class=deck.hero_class))
        self.first_player=first_player; self.current=first_player; self.phase='mulligan'; self.mulligan_done=set()
        self.turn=0; self.max_turns=max_turns; self.terminal=False; self.winner=None; self.end_reason=None
        self.record=record; self.events=[]; self.history=[]
        self._entry_trace_limit=0; self._entry_trace_rows=deque(); self._entry_trace_serial=0
        self._pending_summon_events={}
        self._minion_after_play_frame=None
        self._rule_events=deque(); self._draining_events=False; self._event_frames=[]
        self._damage_batch_depth=0
        self._spell_repeat_depth=0
        self._lifesteal_batches=[]
        self._settling=False;self._death_frame=None;self._turn_frame=None;self._resuming_turn=False
        self.pending_choice=None; self.pending_play=None; self.pending_frame=None
        if self.approximation_profile is not None:self._log('approximation_profile',**self.approximation_profile)
        for p in self.players:p.starting_hero_class=p.hero_class
        from .historical_experimental_decks import apply_setup as apply_experimental_setup
        apply_experimental_setup(self,self._starting_deck_selections)
        self._prepare_constructed_decks(decks)
        from .zombeast_pools import install as install_zombeast_pools
        install_zombeast_pools(self)
        from .nefarius_pools import install as install_nefarius_pools
        install_nefarius_pools(self)
        from .historical_anomalies import choose_opening as choose_anomaly
        choose_anomaly(self)
        self._essence_setup()
        self._remaining_setup(decks)
        first_player=self._aya_setup()
        self._starting_rules()
        from .historical_masquerade import setup as setup_masquerade
        setup_masquerade(self)
        for owner in (first_player,1-first_player):
            self._imbue_start_game(owner)
        from .historical_scythe import setup as setup_scythe
        setup_scythe(self)
        for owner in (first_player,1-first_player):
            self._quest_opening_hand(owner)

    def _activate_board_action(self,action):
        from .historical_eonar import active,activate
        source=self._force_live(action.source)
        if source is not None and active(source):activate(self,action)
        elif self._permanent_entity(action.source) is not None:self._activate_permanent(action)
        else:self._activate_location(action)

    def _after_action_rules(self):
        if self.pending_choice is None and not self.terminal:
            from .historical_demon_portal import refill
            for owner in (0,1):refill(self,owner)
            from .historical_stormwind_questline_finish import finish as finish_stormwind
            if self.pending_frame is None and self.pending_play is None and finish_stormwind(self,clear_paid=True):self._settle(allow_event_choices=True)

    def _summon(self,owner,cid,position=-1,attack_bonus=0,health_bonus=0,expires=False,*,copy_from=None,entry_origin="unspecified",entry_site=None,entry_zone=None,entry_source=None,dormant_turns=None,entry_stats=None,entry_keywords=(),entry_frozen=False,entry_remove_keywords=()):
        count=self._card_summon_repetitions(owner,entry_origin)
        first=self._summon_one(owner,cid,position,attack_bonus,health_bonus,expires,copy_from=copy_from,entry_origin=entry_origin,entry_site=entry_site,entry_zone=entry_zone,entry_source=entry_source,dormant_turns=dormant_turns,entry_stats=entry_stats,entry_keywords=entry_keywords,entry_frozen=entry_frozen,entry_remove_keywords=entry_remove_keywords)
        if first is not None:
            for index in range(1,min(count,1+max(0,7-len(self.players[owner].board)))):
                self._summon_one(owner,cid,position if position<0 else position+index,attack_bonus,health_bonus,expires,copy_from=copy_from,entry_origin=entry_origin,entry_site=entry_site,entry_zone=entry_zone,entry_source=entry_source,dormant_turns=dormant_turns,entry_stats=entry_stats,entry_keywords=entry_keywords,entry_frozen=entry_frozen,entry_remove_keywords=entry_remove_keywords)
        return first

    def _summon_one(self,owner,cid,position=-1,attack_bonus=0,health_bonus=0,expires=False,*,copy_from=None,entry_origin="unspecified",entry_site=None,entry_zone=None,entry_source=None,dormant_turns=None,entry_stats=None,entry_keywords=(),entry_frozen=False,entry_remove_keywords=()):
        from .historical_transfer_student import form_for
        cid=form_for(self,cid)
        if copy_from is None and isinstance(entry_source,Card) and entry_source.card_id==cid and hasattr(entry_source,'_historical_retained_minion'):
            copy_from=deepcopy(entry_source._historical_retained_minion)
            from .base_stats import base_stats
            self._set_minion_attack(copy_from,base_stats(self,entry_source,owner)[0]+entry_source.attack_bonus)
            copy_from.max_health=self._card_stat(entry_source,'health',owner);copy_from.health=copy_from.max_health
            if cid=='WON_144':
                from .historical_ritual_batches import totals
                copy_from.max_health-=totals(self,owner)[1];copy_from.health=copy_from.max_health
            copy_from.aura_attack=copy_from.aura_health=0
        from .historical_zilliax import FORMS as ZILL_FORM_IDS,require_definition as require_zilliax
        if cid in ZILL_FORM_IDS:
            definition_source=copy_from if copy_from is not None else entry_source
            require_zilliax(definition_source)
        if cid=='DAL_431t':
            from .historical_horror_crafting import bound_payload as horror_bound
            if not any(horror_bound(value) for value in (entry_source,copy_from) if value is not None):
                raise UnsupportedCard('Drustvar Horror entry requires its physical taught definition')
        from .historical_golem_crafting import BODIES,bound_payload
        if cid in BODIES.values() and not any(bound_payload(value) for value in (entry_source,copy_from) if value is not None):
            raise UnsupportedCard('Custom Golem entry requires its physical compiled definition')
        # A composite is a physical compiled definition, even on a fresh
        # resurrection/Reborn entry; ordinary enchantments are not replayed.
        if (copy_from is None and isinstance(entry_source,Minion) and entry_source.card_id==cid
                and 'forge_parts' in getattr(entry_source,'_crafted_definition',{}).get('state',{})):
            entry_source=self._fresh_replay_card(entry_source)
        if dormant_turns is None and copy_from is None and isinstance(entry_source,Card) and entry_source.card_id==cid:
            from .forge_intrinsics import values as forge_values
            durations=forge_values(entry_source,'dormant_turns')
            if durations:
                if len(set(durations))!=1:raise UnsupportedCard('Conflicting composite Dormant durations require review')
                dormant_turns=durations[0]
        from .historical_starships import STARSHIPS,CONSTRUCTION
        if cid==CONSTRUCTION:raise UnsupportedCard('Construction is an untouchable board object')
        if cid in STARSHIPS and not (hasattr(entry_source,'_historical_ship_definition') or hasattr(copy_from,'_historical_ship_definition')):
            raise UnsupportedCard('Starship summon requires an assembled physical definition')
        if entry_stats is not None and (not isinstance(entry_stats,tuple) or len(entry_stats)!=2 or any(type(v) is not int or v<0 for v in entry_stats) or entry_stats[1]==0):raise UnsupportedCard('Invalid explicit entry stats')
        if not isinstance(entry_keywords,tuple) or any(not isinstance(k,str) or not k for k in entry_keywords):raise UnsupportedCard('Invalid explicit entry keywords')
        if not isinstance(entry_remove_keywords,tuple) or any(not isinstance(k,str) or not k for k in entry_remove_keywords):raise UnsupportedCard('Invalid explicit entry keyword removals')
        if type(entry_frozen) is not bool:raise UnsupportedCard('Invalid explicit entry Frozen state')
        self._colossal_preflight(cid,owner=owner,copy_from=copy_from,dormant_turns=dormant_turns)
        self._herald_entry_preflight(owner,cid,copy_from)
        self._trace_phase("entry_attempt", origin=entry_origin, site=entry_site, owner=owner, card_id=cid, zone=entry_zone, source_uid=getattr(entry_source,"uid",None), source_card_id=getattr(entry_source,"card_id",None))
        if cid=='JAIL_501' and copy_from is None and entry_origin in ('play','recruit','discard') and entry_zone=='hand':
            value=getattr(entry_source,'rule_state',{}).get('picklock_value',max(1,self.players[owner].mana))
            attack_bonus+=value-1;health_bonus+=value-1
        from .historical_ritual_batches import materialize
        if isinstance(entry_source,Card) and entry_source.card_id==cid:materialize(self,entry_source,owner)
        m = self._create_minion(owner,cid,position,attack_bonus,health_bonus,expires,copy_from=copy_from,dormant_turns=dormant_turns,future_return=entry_origin=='future')
        if m is not None and m.card_id=='JAIL_330':m._champion_stats=(m.attack-m.aura_attack,m.max_health-m.aura_health)
        if m is not None and copy_from is None and isinstance(entry_source,Card) and hasattr(entry_source,'base_stat_override'):
            from .base_stats import carry_base_stats
            if not self.players[owner].crystal_core:
                from .base_stats import base_stats
                old_attack,old_health=base_stats(self,cid,owner);a,h=entry_source.base_stat_override
                self._adjust_minion_attack(m,a-old_attack);m.max_health+=h-old_health;m.health+=h-old_health
            carry_base_stats(entry_source,m)
        if m is not None and entry_origin in ('play','recruit','discard') and isinstance(entry_source,Card):
            self._carry_origin(entry_source,m)
        # A taught spell is intrinsic to a physical generated definition on every entry.
        if m is not None and isinstance(entry_source,Card) and entry_source.card_id==cid and hasattr(entry_source,'_learned_spell'):
            m._learned_spell=entry_source._learned_spell
            if hasattr(entry_source,'_learned_card'):m._learned_card=deepcopy(entry_source._learned_card)
        if (m is not None and copy_from is None and isinstance(entry_source,Card)
                and entry_zone in ('hand','deck','discard') and entry_source.card_id==cid):
            if cid=='NX2_033':m.rule_state['historical_thaddius_parity']=getattr(entry_source,'rule_state',{}).get('historical_thaddius_parity',1)
            self._held_bonus_entry(m,entry_source)
            self._dark_entry(m,entry_source)
            self._stored_entry(m,entry_source)
        if m is not None and copy_from is None and isinstance(entry_source,Card) and entry_zone in ('hand','deck','discard') and entry_source.card_id!=cid:
            from .historical_form_batches import FORMS
            if entry_source.card_id in FORMS:
                self._held_bonus_entry(m,entry_source)
                self._dark_entry(m,entry_source)
                self._stored_entry(m,entry_source)
        if m is not None and copy_from is None and isinstance(entry_source,Card) and entry_source.card_id==cid:
            self._forge_entry(m,entry_source)
        if m is not None and isinstance(entry_source,Card) and entry_source.card_id==cid:
            value=getattr(entry_source,'rule_state',{}).get('historical_fire_spell_damage',0)
            if value:m.rule_state['historical_fire_spell_damage']=value
            state=getattr(entry_source,'rule_state',{})
            if copy_from is None and state.get('historical_granted_deaths'):
                m.attached_death_effects.extend(deepcopy(state['historical_granted_deaths']));m.keywords.add('DEATHRATTLE')
            aegwynn=state.get('historical_aegwynn_stacks',0) if copy_from is None else 0
            if aegwynn:
                m.rule_state['historical_spell_damage']=m.rule_state.get('historical_spell_damage',0)+2*aegwynn
                m.attached_death_effects.extend(('historical_copy_aegwynn_death',) for _ in range(aegwynn))
                m.keywords.update(('SPELLPOWER','DEATHRATTLE'))
            if state.get('historical_darkvein_spell') is not None:
                m.attached_death_effects.append(('historical_copy_darkvein_cast',deepcopy(state['historical_darkvein_spell'])));m.keywords.add('DEATHRATTLE')
            m.attached_death_effects.extend(('historical_copy_talritha',) for _ in range(state.get('historical_talritha_deaths',0)))
            ouroboros=state.get('historical_ouroboros_deaths',0)
            if ouroboros:
                m.attached_death_effects.extend(('summon','VAC_945t',1) for _ in range(ouroboros));m.keywords.add('DEATHRATTLE')

            keyword=state.get('historical_imposter_keyword')
            if keyword:m.keywords.add(keyword)
            if state.get('historical_imposter_spell_damage'):m.rule_state['historical_imposter_spell_damage']=state['historical_imposter_spell_damage']
        if m is not None and copy_from is None and isinstance(entry_source,Card) and getattr(entry_source,'rule_state',{}).get('historical_shaffar_beacon'):
            m.rule_state['historical_shaffar_beacon']=True;m.keywords.add('SPELLBURST')
        from .historical_ritual_batches import fresh_board
        if entry_origin!='future':fresh_board(self,m,entry_source,copy_from)
        from .historical_starships import initialize as initialize_starship
        initialize_starship(self,m,entry_source,copy_from)
        if m is not None and entry_stats is not None:self._set_entity_stats(m,*entry_stats)
        if m is not None:
            from .historical_location_timed import entry as crystal_cove_entry
            crystal_cove_entry(self,m)
        if m is not None and copy_from is None:
            from .historical_sleep_batches import entry
            entry(self,m)
            from .historical_copy_batches import SPIRIT_IDS
            if m.card_id in SPIRIT_IDS:
                m.keywords.discard('STEALTH');m.temporary_keywords.append(dict(keyword='STEALTH',phase='start',turn=self.turn+(2 if owner==self.current else 1)))
        if m is not None:
            from .historical_play_batches import summon_bonus
            summon_bonus(self,m)
        if m is not None:
            m.keywords.update(entry_keywords)
            m.keywords.difference_update(entry_remove_keywords)
            if entry_frozen:self._freeze(m.uid)
        if (m is not None and copy_from is None and isinstance(entry_source,Card)
                and entry_source.card_id==cid and entry_zone in ('hand','deck','discard')):
            m.health-=getattr(entry_source,'rule_state',{}).get('historical_hand_damage',0)
        if m is not None and entry_origin=='reborn':self.players[owner].reborn_history.append(cid)
        if m is not None:
            self._log('summon',player=owner,card=cid,entity=m.uid,
                      position=self.players[owner].board.index(m))
        if m is not None:
            if cid=='CAP_400t2t':
                bonus=2*self.players[owner].imp_upgrades
                if bonus:self._buff(m,bonus,bonus)
            if entry_origin=='play':self._ashalon_play(self.current,m)
            self._colossal_enter(m)
            self._herald_on_summon(m)
            if not m.dormant and has_tribe(self._card_data(m),'DRAGON') and getattr(self.players[owner],'historical_timewarden_until',-1)>=self.turn:m.keywords.update(('TAUNT','DIVINE_SHIELD'))
            if entry_origin=='goldbeard':m._historical_goldbeard_creator_uid=getattr(entry_source,'uid',None)
            self._capture_summon_event(m, entry_origin)
        self._trace_entity("entry_result", m, origin=entry_origin, site=entry_site, owner=owner, card_id=cid, success=m is not None)
        return m

    def _create_minion(self,owner,cid,position=-1,attack_bonus=0,health_bonus=0,expires=False,*,copy_from=None,dormant_turns=None,future_return=False):
        from .historical_transfer_student import form_for
        cid=form_for(self,cid)
        if dormant_turns is not None and (type(dormant_turns) is not int or dormant_turns==0 or dormant_turns < -1):
            raise UnsupportedCard('Dormant duration must be positive or -1 for a conditional awakening')
        if cid in PERMANENT_IDS:raise UnsupportedCard('Permanent requires explicit placement: '+cid)
        if cid not in self.cards or self.cards[cid]['type']!='MINION': raise UnsupportedCard(cid)
        p=self.players[owner]
        if len(p.board)>=7: return None
        if future_return:
            if copy_from is None:raise ValueError('Future return requires its physical minion')
            m=copy_from;m.owner=owner;m.summoned_turn=self.turn;m.attacks=0
            p.board.insert(len(p.board) if position<0 else position,m)
            self._refresh_auras()
            return m
        expires=expires or cid in ('HERO_11bpt','HERO_11bp2t')
        c=self.cards[cid]
        if copy_from is None and self._is_recruit(cid):
            attack_bonus+=p.recruit_attack_bonus;health_bonus+=p.recruit_health_bonus
        herald_level=multiplier(p.herald_count) if cid in ARMY_OF and copy_from is None else 1
        attack_bonus+=c['attack']*(herald_level-1)
        health_bonus+=c['health']*(herald_level-1)
        from .base_stats import base_stats,carry_base_stats
        base_attack,base_health=base_stats(self,cid,owner)
        health=base_health+health_bonus
        m=Minion(self._new_id(),cid,owner,base_attack+attack_bonus,health,health,set(c.get('mechanics',[])),summoned_turn=self.turn,expires=expires)
        if p.crystal_core:m.base_stat_override=(5,5)
        if cid in ARMY_OF:m.rule_state['herald_multiplier']=herald_level
        self._set_minion_attack(m,m.attack)
        if cid=='BT_197t':m.keywords.discard('ELUSIVE')
        if copy_from is not None:
            carry_base_stats(copy_from,m)
            self._set_minion_attack(m,copy_from.attack+copy_from.attack_deficit-copy_from.aura_attack)
            m.max_health=copy_from.max_health-copy_from.aura_health
            copied_damage=copy_from.max_health-copy_from.health
            m.health=m.max_health
            m.keywords=set(copy_from.keywords)
            m.frozen_until=copy_from.frozen_until
            m.temporary_attack=copy_from.temporary_attack
            m.silenced=copy_from.silenced
            m.expires=copy_from.expires
            m.remembered_discards=list(copy_from.remembered_discards)
            m.attached_death_effects=deepcopy(copy_from.attached_death_effects)
            m.temporary_keywords=deepcopy(copy_from.temporary_keywords)
            m.imbue_attack_expiries=deepcopy(copy_from.imbue_attack_expiries)
            m.rule_state=deepcopy(copy_from.rule_state)
            self._carry_origin(copy_from,m,copied=True,source_owner=copy_from.owner if copy_from.owner!=owner else None)
            for private_field in ("_infinity_cost_receipts","remembered_draw","secret_discard","_bound_card","_bound_minion","_devoured_cards","_nellie_crew","_fragile_illusion","_illusion_possible","_jandice_illusion"):
                if hasattr(copy_from,private_field):setattr(m,private_field,deepcopy(getattr(copy_from,private_field)))
            if hasattr(copy_from,'_muradin_hammer'):
                held=deepcopy(copy_from._muradin_hammer)
                held['card']=self._copy_card(copy_from._muradin_hammer['card'],source_owner=copy_from.owner if copy_from.owner!=owner else None)
                m._muradin_hammer=held
                m._muradin_extra_hammers=[]
                for original in getattr(copy_from,'_muradin_extra_hammers',()):
                    extra=deepcopy(original)
                    extra['card']=self._copy_card(original['card'],source_owner=copy_from.owner if copy_from.owner!=owner else None)
                    m._muradin_extra_hammers.append(extra)
        if position<0: position=len(p.board)
        m.dormant = copy_from.dormant if copy_from is not None else INITIAL_DORMANCY.get(cid, 0)
        if copy_from is not None and cid in ('LOOT_526','BT_850') and not m.silenced:
            m.dormant=-1;m.rule_state['historical_sleep_progress']=0
        if dormant_turns is not None:m.dormant=dormant_turns
        m._colossal_stat_snapshot=(m.attack,m.max_health)
        p.board.insert(position,m)
        if copy_from is None and m.health==0 and m.max_health==0:m._historical_zero_health_entry=True
        self._refresh_auras()
        if hasattr(m,'_historical_zero_health_entry'):del m._historical_zero_health_entry
        if copy_from is not None:
            m.health-=copied_damage
            self._refresh_auras()
        return m

    def _add(self,owner,cid):
        self._quest_deliver_ready(owner)
        if cid not in self.cards: raise UnsupportedCard('Generated card not implemented: '+cid)
        p=self.players[owner]
        if len(p.hand)>=getattr(p,'hand_capacity',10):
            from .historical_movements import record
            record(self,'destroyed')
            self._log('burn_generated',player=owner,card=cid)
        else: return self._enter_hand(owner,Card(self._new_id(),cid))

    def _hero_attack(self,owner):
        from .cards import HERO_ATTACK_AURAS
        p=self.players[owner]
        aura=0
        for m in p.minions:
            rule=HERO_ATTACK_AURAS.get(m.card_id)
            if rule and not m.silenced and m.health>0:
                condition,amount=rule
                if condition=='owner_turn' and self.current==owner:aura+=amount
        if self.current==owner and self._active('DMF_708',owner):aura+=2*sum(m.card_id=='DMF_708' and not m.silenced and m.health>0 for m in p.minions)
        from .historical_anomalies import hero_attack as anomaly_hero_attack
        aura+=anomaly_hero_attack(self,owner)
        return aura+p.temporary_attack+((p.armor if p.weapon['card_id']=='CORE_LOOT_044' else p.weapon['attack']) if p.weapon else 0)

    def _spell_damage(self,owner,cid=None,physical_card=None):
        from .cards import SPELL_DAMAGE_VALUES, CONDITIONAL_SPELL_DAMAGE
        from .forge_intrinsics import spell_damage
        total=getattr(self.players[owner],'historical_mage_spell_damage',0)+2*sum(m.card_id=='LOE_051' and not m.silenced and m.health>0 for player in self.players for m in player.minions)
        for m in self.players[owner].minions:
            total+=m.rule_state.get('historical_spell_damage',0)
            if m.silenced:continue
            total+=m.rule_state.get('historical_imposter_spell_damage',0)
            total+=SPELL_DAMAGE_VALUES.get(m.card_id,self.cards[m.card_id].get('spellDamage',0))+spell_damage(m)
            rule=CONDITIONAL_SPELL_DAMAGE.get(m.card_id)
            if rule:
                condition,amount=rule
                if condition=='damaged' and m.health<m.max_health:total+=amount
        from .historical_play_batches import spell_damage_bonus
        total+=spell_damage_bonus(self,owner,cid)+getattr(physical_card,'spell_damage_bonus',0)
        total+=sum(e['amount'] for e in getattr(self.players[owner],'historical_location_spell_bonuses',()) if e['turn']==self.turn)
        return total*2**sum(m.card_id=='TOY_807' and not m.silenced and not m.dormant and m.health>0 for m in self.players[owner].minions)

    def _visible_targets(self,owner,magic=False):
        return [self.hero_id(player) for player in (0,1) if (player==owner or (not self._hero_immune(player) and not self._hero_stealth(player))) and not (magic and self._hero_elusive(player))]+[m.uid for p in self.players for m in p.minions
            if not (m.owner!=owner and bool({'STEALTH','IMMUNE'} & self._effective_keywords(m))) and not (magic and 'ELUSIVE' in self._effective_keywords(m))]

    def _targets_for(self,cid,owner,mode_override=None):
        if cid=='EDR_813b' and self.players[owner].corpses<2:return []
        targets=self._unrestricted_targets_for(cid,owner,mode_override)
        if self.cards[cid]['type']=='SPELL' and getattr(self.players[owner],'historical_spell_no_heroes_turn',None)==self.turn:
            targets=[target for target in targets if target>=0]
        return targets

    def _unrestricted_targets_for(self,cid,owner,mode_override=None):
        data=self.cards[cid]
        from .historical_galakrond_batches import targets as galakrond_targets
        galakrond_result=galakrond_targets(self,cid,owner,mode_override if mode_override is not None else RULES.get(cid,('none',))[0])
        if galakrond_result is not None:return galakrond_result
        if cid in ('CATA_496','DAL_007') and len(self.players[owner].board)>=7:return []
        mode=mode_override if mode_override is not None else (RULES[cid][0] if cid in RULES else TARGETS.get(cid,'none'))
        if cid=='GDB_456' and mode_override is None:mode='enemy_character' if 'ELEMENTAL' in self.players[owner].previous_tribes else 'none'
        from .historical_sleep_batches import targets as historical_sleep_targets
        sleep_targets=historical_sleep_targets(self,cid,owner,mode)
        if sleep_targets is not None:return sleep_targets
        from .historical_play_batches import targets as historical_play_targets
        play_targets=historical_play_targets(self,cid,owner,mode)
        if play_targets is not None:return play_targets
        from .historical_upgrade_batches import targets as historical_upgrade_targets
        upgrade_targets=historical_upgrade_targets(self,cid,owner,mode)
        if upgrade_targets is not None:return upgrade_targets
        from .historical_drawn_batches import targets as historical_drawn_targets
        drawn_targets=historical_drawn_targets(self,cid,owner,mode)
        if drawn_targets is not None:return drawn_targets
        from .historical_copy_batches import targets as historical_copy_targets
        copy_targets=historical_copy_targets(self,cid,owner,mode)
        if copy_targets is not None:return copy_targets
        from .historical_family_batches import targets as historical_family_targets
        family_targets=historical_family_targets(self,cid,owner,mode)
        if family_targets is not None:return family_targets
        from .historical_mutation_batches import targets as historical_mutation_targets
        mutation_targets=historical_mutation_targets(self,cid,owner,mode)
        if mutation_targets is not None:return mutation_targets
        from .historical_condition_batches import targets as historical_condition_targets
        condition_targets=historical_condition_targets(self,cid,owner,mode)
        if condition_targets is not None:return condition_targets
        from .historical_board_primitives import targets as historical_board_targets
        board_targets=historical_board_targets(self,cid,owner,mode)
        if board_targets is not None:return board_targets
        conditional_targets=self._historical_conditional_targets(cid,owner,mode)
        if conditional_targets is not None:return conditional_targets
        removal_targets=self._historical_removal_targets(cid,owner,mode)
        if removal_targets is not None:return removal_targets
        historical_targets=self._historical_buff_targets(cid,owner,mode)
        if historical_targets is not None:return historical_targets
        if mode in HELD_TARGETS:
            filters,active_mode=HELD_TARGETS[mode]
            mode=active_mode if self._holding_matches(owner,filters) else 'none'
        if mode=='health_changed_enemy_minion':mode='enemy_minion' if self.players[owner].hero_health_changed_turn else 'none'
        if mode=='power_used_friendly_minion':mode='friendly_minion' if self.players[owner].power_used else 'none'
        if mode=='combo_character': mode='character' if self.players[owner].cards_played else 'none'
        if mode=='combo_friendly_minion': mode='friendly_minion' if self.players[owner].cards_played else 'none'
        if mode=='weapon_character': mode='character' if self.players[owner].weapon else 'none'
        if mode=='repeated_enemy_character':mode='none' if any(h['card_id']==cid for h in self.players[owner].played_history) else 'character'
        if mode=='imbue_two_minion':mode='minion' if self.players[owner].imbue_count>=2 else 'none'
        if mode=='kindred_enemy_minion':mode='enemy_minion' if self._kindred(cid,owner) else 'none'
        if mode=='fire_turn_minion':mode='minion' if self.players[owner].fire_spell_played else 'none'
        if mode=='location':return [x.uid for p in self.players for x in p.locations]
        if mode=='enemy_location':return [x.uid for x in self.players[1-owner].locations] or ([0] if data['type']=='MINION' else [])
        if mode=='quest_enemy_minion':mode='enemy_minion' if self.players[owner].quests_played else 'none'
        if mode=='none': return [0]
        if mode=='weapon_required': return [0] if self.players[owner].weapon else []
        targets=self._visible_targets(owner,magic=data['type']=='SPELL')
        def valid(uid):
            if mode=='character': return True
            m=self._find(uid) if uid>0 else None
            friendly=(-uid-1==owner) if uid<0 else m.owner==owner
            if mode=='friendly_character': return friendly
            if mode=='historical_damaged_character':return self.players[-uid-1].health<self.players[-uid-1].max_health if uid<0 else m.health<m.max_health
            if mode=='enemy_character': return not friendly
            if m is None: return False
            if mode=='minion': return True
            if mode=='historical_frozen_minion':return m.frozen_until>=0
            if mode=='historical_shield_minion':return 'DIVINE_SHIELD' in self._effective_keywords(m)
            if mode=='historical_friendly_shield':return friendly and 'DIVINE_SHIELD' in self._effective_keywords(m)
            if mode=='historical_recruit':return self._is_recruit(m.card_id)
            if mode=='enemy_taunt': return not friendly and 'TAUNT' in self._effective_keywords(m)
            if mode=='historical_friendly_demon':return friendly and has_tribe(self._card_data(m),'DEMON')
            if mode=='small_attack_minion': return m.attack<=3
            if mode=='large_minion': return m.attack>=7
            if mode=='historical_attack_at_least_five':return m.attack>=5
            if mode=='legendary_minion': return self.cards[m.card_id].get('rarity')=='LEGENDARY'
            if mode=='tribal_enemy_minion': return not friendly and has_any_tribe(self.cards[m.card_id])
            if mode=='damaged_minion': return m.health<m.max_health
            if mode=='enemy_minion': return not friendly
            if mode=='friendly_deathrattle':return friendly and bool(self._death_operations(m))
            if mode=='friendly_minion': return friendly
            if mode=='friendly_wisp':return friendly and self.cards[m.card_id]['name']=='Wisp'
            if mode=='enemy_minion_source_health':
                return not friendly
            if mode=='friendly_dragon':return friendly and has_tribe(self._card_data(m),'DRAGON')
            if mode=='friendly_beast': return friendly and has_tribe(self._card_data(m),'BEAST')
            if mode=='friendly_undead': return friendly and has_tribe(self._card_data(m),'UNDEAD')
            if mode=='undamaged_minion': return m.health==m.max_health
            if mode=='damaged_enemy_minion': return not friendly and m.health<m.max_health
            raise UnsupportedCard('Target mode: '+mode)
        result=[uid for uid in targets if valid(uid)]
        return result or ([0] if data['type']=='MINION' else [])

    def _cost(self,card,owner):
        p=self.players[owner]; cid=card.card_id
        cost=max(1,p.mana) if cid=='JAIL_501' else self._card_data(card)['cost']
        if getattr(p,'historical_experimental_zero_lackeys',False):
            from .historical_family_batches import LACKEYS
            if cid in LACKEYS:cost=0
        if cid=='TOY_400t8' and p.hand and card.uid in (p.hand[0].uid,p.hand[-1].uid):cost=0
        if cid in ('CORE_BT_801','BT_801') and p.hand and card.uid in (p.hand[0].uid,p.hand[-1].uid): cost=1
        elif cid=='CORE_NEW1_022': cost-=p.weapon['attack'] if p.weapon else 0
        elif cid=='CATA_308' and any(self.cards[m.card_id].get('rarity')=='LEGENDARY' for m in p.minions): cost=1
        if cid=='SCH_357':cost-=getattr(card,'rule_state',{}).get('historical_fel_guardian_deaths',0)
        if cid=='VAC_558':cost-=sum(record['target_owner'] in (0,1) for record in getattr(p,'_historical_cast_records',()))
        if cid=='LOE_113':cost-=sum(has_tribe(self._card_data(m),'MURLOC') for m in p.all_minions)
        if cid=='GDB_465':
            from .historical_starships import building
            if building(self,owner) is not None:cost=1
        if cid=='DAL_716' and any(set(card_classes(self._card_data(c)))-{'NEUTRAL',p.hero_class} for c in p.hand):cost=0
        if cid=='GVG_052' and any(m.health<m.max_health for m in p.minions):cost-=4
        if cid=='SCH_623':cost-=p.weapon['attack'] if p.weapon else 0
        if cid=='TRL_555':cost-=len(p.all_minions)
        if cid=='AV_108':cost-=p.armor
        if cid=='BAR_308':cost-=sum(self._card_data(c)['type']=='SPELL' for c in p.hand)
        if cid=='BT_134' and p.max_mana>=7:cost=0
        if cid=='DED_506' and getattr(card,'_drawn_turn',None)==self.turn:cost=3
        if cid=='DMF_518':cost-=sum(not self._started_in_deck(c,owner) for c in p.deck)
        if cid=='DRG_033' and any(has_tribe(self._card_data(c),'DRAGON') for c in p.hand):cost-=3
        if cid=='GIL_518' and any(player.minions_died_turn for player in self.players):cost=1
        if cid=='GDB_228':cost-=sum(has_tribe(self._card_data(m),'DRAENEI') for m in p.minions)
        if cid=='GDB_237':cost-=p.discoveries_total
        if cid=='JAIL_204' and not any(player.minions for player in self.players):cost=2
        if cid=='TIME_022' and any(m.dormant for player in self.players for m in player.all_minions):cost-=4
        if cid=='DINO_409':cost-=getattr(p,'_nonstarting_plays',0)
        if cid=='BT_110' and p.spells_previous:cost-=3
        if cid in ('BRM_001','BRM_003'):cost-=sum(player.minions_died_turn for player in self.players)
        if cid=='BT_132' and p.max_mana>=7:cost=0
        if cid=='DRG_314':
            from .historical_tribal_batches import TREANTS
            cost-=2*sum(m.card_id in TREANTS for m in p.minions)
        if cid=='TRL_313' and 'ELEMENTAL' in p.previous_tribes:cost=1
        if cid=='GDB_305':cost-=sum(has_tribe(self._card_data(m),'ELEMENTAL') for m in p.minions if not m.dormant)
        if cid=='VAC_700':cost-=sum(bool(card_classes(self.cards[entry['card_id']])-{'NEUTRAL'}) and p.hero_class not in card_classes(self.cards[entry['card_id']]) for entry in p.played_history)
        if cid=='JAIL_433' and getattr(card,'rule_state',{}).get('opponent_copy_played'):cost=1
        if cid=='TLC_365' and p.discoveries_this_turn:cost=0
        if cid=='TLC_520':cost-=self._own_shuffle_count(owner)
        if cid=='JAIL_514':cost-=len(p.hand)
        if cid=='CATA_452':cost-=p.spell_damage_turn
        if cid=='CATA_529':cost-=p.fel_spells_cast
        if cid=='TIME_005t7':
            from .rafaam import FAMILY
            cost-=sum(entry['card_id'] in FAMILY for entry in p.played_history)
        if cid=='FIR_919':cost-=p.cards_played
        if cid=='CATA_568':cost-=p.friendly_attacks
        if cid=='CATA_616':cost-=p.last_paid_cost
        if cid=='TIME_715':cost-=len(self.players[1-owner].minions)
        if cid=='JAIL_503':cost-=sum(c.card_id in COIN_IDS for c in p.hand)
        if cid=='JAIL_307' and len(p.deck)>=25:cost-=2
        if cid=='END_004':cost-=sum(player.minions_died_turn for player in self.players)
        if cid=='TIME_047':cost-=self.players[1-owner].hero_damage_events_turn
        if cid=='END_030':cost-=p.overloaded_total
        if cid=='EDR_477':cost-=p.hero_power_uses
        if cid=='END_033' and any(c is not card and has_tribe(self._card_data(c),'DRAGON') for c in p.hand):cost-=3
        if cid=='TLC_819' and {'HOLY','SHADOW'}<=p.spell_schools_this_turn:cost=1
        from .historical_conditional_spells import cost as conditional_spell_cost
        cost=conditional_spell_cost(self,card,owner,cost)
        from .historical_timed_spells import cost as timed_spell_cost
        cost=timed_spell_cost(self,card,owner,cost)
        cost=self._historical_intrinsic_cost(card,owner,cost)
        from .historical_family_batches import LIBRAMS
        if cid in LIBRAMS:cost-=getattr(p,'historical_libram_discount',0)
        if cid=='BOT_523':
            from .historical_tribal_batches import TREANTS
            cost-=sum(dead in TREANTS for dead in p.death_history)
        if cid in ('OG_028','REV_838'):cost-=getattr(p,'historical_summoned_tribes',{}).get('TOTEM',0)
        if cid=='SW_417':
            from .historical_play_batches import SI7_IDS
            cost-=sum(r.card.card_id in SI7_IDS for r in p.replay_history)
        if self._card_data(card).get('overload',0)>0:cost-=getattr(p,'historical_overload_discount',0)
        if has_tribe(self._card_data(card),'DEMON') and not self._started_in_deck(card,owner):cost-=getattr(p,'historical_nonstarting_demon_discount',0)
        if self._kindred(card,owner):
            from .kindred import repetitions
            cost-={'TLC_366':2,'TLC_600':3,'TLC_816':2}.get(cid,0)*repetitions(self,owner,cid,True)
        if self.cards[cid]['type']=='MINION' and p.minions_set_cost is not None:cost=p.minions_set_cost
        if has_tribe(self._card_data(card),'DRAGON') and p.dragons_played_turn==0 and self._active('EDR_844',owner):cost=1
        if self._medivh_free(cid,owner):cost=0
        cost=getattr(card,'set_cost',cost)
        from .forge_intrinsics import intrinsic_cost
        cost=intrinsic_cost(self,card,owner,cost)
        if getattr(card,'_infinity_cost_layers',[]):
            from .infinity import INFINITY
            cost=INFINITY
        cost+=getattr(card,'cost_delta',0)
        from .herald import DEATHWINGS
        if cid in DEATHWINGS:cost-=p.deathwing_discount
        if cid in LEYLINES:cost-=p.leyline_discount
        cost-=sum(e['amount'] for e in getattr(card,'temporary_cost_discounts',[]) if self.turn<=e['end'])
        if getattr(card,'rule_state',{}).get('historical_turn_zero_cost')==self.turn:cost=0
        if getattr(p,'historical_next_concoction_free',False):
            from .historical_copy_batches import CONCOCTION_IDS
            if cid in CONCOCTION_IDS:cost=0
        historical_turn_cost=getattr(card,'rule_state',{}).get('historical_turn_cost')
        if historical_turn_cost and historical_turn_cost['turn']==self.turn:cost=historical_turn_cost['cost']
        for effect in p.cost_effects:
            if self._discount_matches(effect,card):
                cost=effect['set_cost'] if 'set_cost' in effect else cost-effect['amount']
                if 'minimum' in effect:cost=max(effect['minimum'],cost)
        cost-=self._azure_discount(owner,cid)
        cost-=self._mug_discount(owner,cid)
        from .historical_anomalies import card_discount as anomaly_card_discount
        cost-=anomaly_card_discount(self,owner,card)
        # Live hand adjacency, not a permanent cost enchantment. Sabotage's
        # own surcharge caps at ten; unrelated taxes may still exceed ten.
        index=next((i for i,c in enumerate(p.hand) if c is card),None)
        if index is not None:
            surcharge=sum(p.hand[i].card_id=='CATA_186t' for i in (index-1,index+1) if 0<=i<len(p.hand))
            if surcharge and cost<10:cost=min(10,cost+surcharge)
        for effect in p.timed_cost_increases:
            if effect['start'] <= self.turn <= effect['end'] and (
                    effect['selector']=='ALL' or self._discount_matches(effect,card)):
                cost=effect['set_cost'] if 'set_cost' in effect else cost+effect['amount']
        if self.cards[cid]['type']=='MINION':
            cost+=2*sum(m.card_id=='JAIL_890' and not m.silenced and m.health>0 for player in self.players for m in player.minions)
        cost=self._historical_cost_aura(card,owner,cost)
        from .historical_starships import cost_aura as starship_cost_aura
        cost=starship_cost_aura(self,card,owner,cost)
        fever=getattr(p,'historical_frost_fever',0)
        if fever and cost<10:cost=min(10,cost+fever)
        if getattr(p,'historical_bonelord',False) and p.cards_played==0:cost=0
        return max(1 if getattr(card,'rule_state',{}).get('historical_echo_copy') else 0,cost)

    def _attack_targets(self,m=None):
        enemy=self.players[1-self.current]
        visible=[x for x in enemy.minions if not {'STEALTH','IMMUNE'} & self._effective_keywords(x)]
        taunts=[] if self._active('CORE_BT_187',self.current) else [x.uid for x in visible if 'TAUNT' in self._effective_keywords(x)]
        targets=taunts or ([] if self._hero_immune(1-self.current) or self._hero_stealth(1-self.current) else [self.hero_id(1-self.current)])+[x.uid for x in visible]
        if m and m.summoned_turn==self.turn and 'CHARGE' not in self._effective_keywords(m) and not (m.card_id=='TTN_903' and not m.silenced):
            if 'RUSH' not in self._effective_keywords(m): return []
            targets=[t for t in targets if t>0]
        if m is None and getattr(self.players[self.current],'historical_hero_minions_only_turn',-1)==self.turn:
            targets=[t for t in targets if t>0]
        if m and 'CANT_ATTACK_HERO' in self._effective_keywords(m):
            targets=[t for t in targets if t>0]
        if m is None and self.players[self.current].weapon and self.players[self.current].weapon['card_id'] in ('CORE_LOOT_044','END_012','SW_314'):
            targets=[t for t in targets if t>0]
        return targets

    def _hand_actions(self,owner):
        """Owner-scoped hand eligibility without switching turn or choice state."""
        p=self.players[owner];actions=[]
        for c in p.hand:
            d=self.cards[c.card_id]
            if c.card_id in ('LOOT_104','ICC_827t','CORE_RLK_567','RLK_567','GDB_118t','GDB_118t2','JAM_037t'):continue
            if 'TRADEABLE' in self._card_mechanics(c) and p.mana>=1 and p.deck:
                actions.append(Action('trade',source=c.uid))
            if self._can_prepare(c,owner):actions.append(Action('prepare',source=c.uid))
            if self._can_forge(c,owner):actions.append(Action('forge',source=c.uid))
            lock=getattr(c,'play_lock',None)
            if lock and lock['owner']==owner and lock.get('not_before',-1)<=p.turns_taken<lock['until']:continue
            played_lock=getattr(c,'rule_state',{}).get('locked_until_play')
            if played_lock and played_lock['owner']==owner and len(p.played_history)<played_lock['count']:continue
            if getattr(p,'historical_edge_lock_turn',None)==self.turn and c not in (p.hand[0],p.hand[-1]):continue
            if getattr(c,'rule_state',{}).get('historical_unplayable_turn')==self.turn:continue
            from .historical_location_timed import frozen_locked
            if frozen_locked(self,owner,c):continue
            if not self._can_pay(c,owner):continue
            if c.card_id=='VAC_955t' and len(p.board)>=7:continue
            if c.card_id in EITHER_SIDE:
                for side in (0,1):
                    board=self.players[owner if side==0 else 1-owner].board
                    if len(board)<7:actions.extend(Action('play',c.uid,0,pos,() if side==0 else (1,)) for pos in range(len(board)+1))
                continue
            if d['type'] in ('MINION','LOCATION') and len(p.board)>=7 and not (d['type']=='MINION' and c.card_id in MAGNETIC_IDS):continue
            from .historical_sidequest_spell_batch import TOTALS as historical_sidequest_totals
            if c.card_id in historical_sidequest_totals or c.card_id in ('DRG_323','DRG_324'):
                if len(p.secrets)+self._quest_slots(owner)>=5 or any(q['card_id']==c.card_id for q in getattr(p,'historical_mage_sidequests',())):continue
            if self._is_quest(c.card_id) and (p.quest is not None or len(p.secrets)>=5):continue
            if c.card_id in SECRETS and (len(p.secrets)+self._quest_slots(owner)>=5 or any(secret.card_id==c.card_id for secret in p.secrets)): continue
            positions=([i for i in range(len(p.board)) if self._magnetic_target(c,owner,i) is not None] if d['type']=='MINION' and len(p.board)>=7 else range(len(p.board)+1) if d['type'] in ('MINION','LOCATION') else [-1])
            from .physical_choices import branches as physical_branches, combined_targets
            branches=physical_branches(c,CHOICES)
            if branches:
                from .historical_combined_choices import combined
                if c.card_id not in ('WORK_025','VAC_907') and combined(self,owner,c):
                    targets=combined_targets(self,owner,c,branches)
                    if c.card_id=='EDR_813' and p.corpses<2:targets=[0]
                    for target in targets:
                        actions.extend(Action('play',c.uid,target,pos,(-1,)) for pos in positions)
                else:
                    for i,(_,mode,_) in enumerate(branches):
                        if c.card_id=='EDR_813' and i==1 and p.corpses<2:continue
                        for target in self._targets_for(c.card_id,owner,mode):
                            actions.extend(Action('play',c.uid,target,pos,(i,)) for pos in positions)
            else:
                crafted=self._crafted_rule(c)
                card_targets=self._targets_for(c.card_id,owner,crafted[0]) if crafted else self._learned_targets(c,owner)
                if card_targets is None:card_targets=self._targets_for(c.card_id,owner)
                if c.card_id=='DAL_723':
                    remaining=max(0,p.mana-self._cost(c,owner))
                    card_targets=[uid for uid in card_targets if uid>0 and self._find(uid).attack<=remaining]
                card_targets=self._historical_conditional_card_targets(c,owner,card_targets)
                from .historical_upgrade_batches import card_targets as upgrade_card_targets
                card_targets=upgrade_card_targets(self,c,owner,card_targets)
                from .historical_condition_batches import physical_targets
                card_targets=physical_targets(self,c,owner,card_targets)
                from .historical_resurrection_batches import physical_targets as resurrection_targets
                card_targets=resurrection_targets(self,c,owner,card_targets)
                from .historical_play_batches import physical_targets as play_targets
                card_targets=play_targets(self,c,owner,card_targets)
                if c.card_id=='TIME_435':card_targets=[t for t in card_targets if not t or self._find(t).health<=self._card_stat(c,'health',owner)] or [0]
                for target in card_targets:
                    actions.extend(Action('play',c.uid,target,pos) for pos in positions)
        return actions

    def legal_actions(self):
        self._b60_mark_mirrors()
        if self.terminal: return []
        if self.phase=='mulligan': return super().legal_actions()
        if self.phase=='choice':
            return [Action('choose',choices=(i,)) for i in range(len(self.pending_choice['options']))]
        p=self.players[self.current]; actions=[Action('end')]
        actions.extend(self._hand_actions(self.current))
        from .historical_eonar import actions as eonar_actions
        actions.extend(eonar_actions(self))
        actions.extend(self._location_actions())
        actions.extend(self._permanent_actions())
        cost=self._power_cost(self.current)
        from .historical_family_batches import power_available,powers_disabled
        if power_available(self,self.current) and p.mana>=cost:
            k=p.hero_class
            if p.primary_power is not None:
                actions.extend(Action('power',target=t) for t in self._replacement_power_targets(self.current))
            elif k=='HUNTER' and (getattr(p,'historical_stormwind_power_targets',False) or self._active('DRG_253',self.current) or self._active('GVG_087',self.current)):
                visible=self._visible_targets(self.current,magic=True)
                actions.extend(Action('power',target=t) for t in visible if t>0 or t==self.hero_id(1-self.current))
            elif k in ('MAGE','PRIEST'):
                actions.extend(Action('power',target=t) for t in self._visible_targets(self.current,magic=True))
            elif k in ('PALADIN','DEATHKNIGHT'):
                if len(p.board)<7: actions.append(Action('power'))
            elif k=='SHAMAN':
                if len(p.board)<7 and set(TOTEMS)-{m.card_id for m in p.minions}: actions.append(Action('power'))
            else: actions.append(Action('power'))
        if not powers_disabled(self) and p.secondary_power is not None and p.secondary_power['card_id'] not in ('JAIL_800hp1','JAIL_800hp2') and not p.secondary_power['used'] and p.corpses>=self._power_cost(self.current,secondary=True):
            actions.extend(Action('power',target=t,choices=(1,)) for t in self._visible_targets(self.current,magic=True) if t>0)
        for m in p.minions:
            from .historical_eonar import remaining as titan_remaining
            if titan_remaining(m):continue
            keywords=self._effective_keywords(m)
            limit=4 if 'MEGA_WINDFURY' in keywords else 2 if 'WINDFURY' in keywords else 1
            if m.frozen_until<0 and m.attacks<limit and m.attack>0 and 'CANT_ATTACK' not in keywords:
                actions.extend(Action('attack',m.uid,t) for t in self._attack_targets(m))
        if p.frozen_until<0 and p.hero_attacks<self._hero_attack_limit(self.current) and self._hero_attack(self.current)>0:
            actions.extend(Action('attack',self.hero_id(self.current),t) for t in self._attack_targets() if t>0 or self._hero_can_attack_face(self.current))
        return actions

    def step(self,action):
        return self._action_runner.run(self,action)

    def _power_cost(self,owner,*,secondary=False):
        p=self.players[owner]
        replacement_cost=self.cards[p.secondary_power['card_id']]['cost'] if secondary else self._replacement_power_cost(owner)
        cost=replacement_cost if replacement_cost is not None else (1 if p.hero_class=='DEMONHUNTER' else 2)
        if not secondary and p.primary_power is None and getattr(p,'historical_genn',False):cost=1
        if not secondary:
            from .historical_stormwind_questline_finish import power_cost as stormwind_power_cost
            cost=stormwind_power_cost(self,owner,cost)
        from .cards import HERO_POWER_HAND_COST_AURAS
        for cid,(maximum,cost_value) in HERO_POWER_HAND_COST_AURAS.items():
            if len(p.hand)<=maximum and self._active(cid,owner):cost=cost_value
        from .historical_family_batches import power_cost
        cost=power_cost(self,owner,cost)
        for effect in p.next_power_cost_effects:
            if effect.get('expires',self.turn)<self.turn or effect.get('not_before',self.turn)>self.turn:continue
            cost=effect['amount'] if effect['kind']=='set' else cost+effect['amount']
        from .historical_anomalies import power_discount as anomaly_power_discount
        cost-=anomaly_power_discount(self)
        if p.weapon is not None and p.weapon['card_id']=='ETC_312':cost=0
        return max(0,cost)

    def _check_heroes(self):
        # A Hero Power use includes its after-use triggers. Resolve the win
        # check at the end of that sequence, not between its phases.
        if (self._spell_repeat_depth or getattr(self,'_power_sequence_depth',0) or getattr(self,'_power_frame',None)
                or getattr(self,'_combat_sequence_depth',0)):return False
        if not self.terminal:self._hero_resurrections()
        return super()._check_heroes()

    def _power(self,target,*,secondary=False):
        if getattr(self,'_power_frame',None) is not None:
            raise UnsupportedCard('Hero Power sequence already in progress')
        self._rewind_power_begin(target,secondary=secondary)
        player=self.players[self.current]
        bonus=sum(value['amount'] for value in getattr(player,'historical_next_power_damage',()) if value['turn']==self.turn)+getattr(player,'historical_aimed_shot_bonus',0)
        player.historical_aimed_shot_bonus=0
        self._power_frame=dict(owner=self.current,phase='effects',freeze=getattr(player,'historical_next_power_freeze',False),damage_bonus=bonus)
        player.historical_next_power_freeze=False;player.historical_next_power_damage=[]
        self._power_sequence_depth=getattr(self,'_power_sequence_depth',0)+1
        try:
            if secondary:self._base_power(target,secondary=True)
            else:self._base_power(target)
            self._resume_power_sequence()
        finally:
            self._power_sequence_depth-=1

    def _base_power(self,target,*,secondary=False):
        owner=self.current; p=self.players[owner]; k=p.hero_class
        cost=self._power_cost(owner,secondary=secondary)
        if secondary:
            self._spend_corpses(owner,cost);p.secondary_power['used']=True
        else:
            p.mana-=cost; p.power_used=True
            state=getattr(p,'historical_power_turn',{})
            if state.get('turn')!=self.turn:state={'turn':self.turn,'count':0}
            state['count']+=1;p.historical_power_turn=state
            self._b60_spend_mana(owner,cost)
        p.next_power_increase=0
        p.next_power_cost_effects.clear()
        self._log('hero_power',player=owner,hero_class=k,target=target)
        if secondary:
            self._start_power_effects(owner,(('buff',3,0),),target=target,repeats=max(self._trigger_repetitions(owner),2 if self._active('TOY_528',owner) else 1))
            return
        power_repetitions=max(self._trigger_repetitions(owner),2 if self._active('TOY_528',owner) else 1)
        if power_repetitions>1:
            operations=self._repeated_power_operations(owner)
            if p.primary_power is None and k=='HUNTER' and target>0:operations=(('damage',2),)
            post_operations=()
            if p.primary_power and p.primary_power['card_id'] in ('TLC_632t','TLC_632t2'):
                post_operations=(('replacement_power_consumed',p.primary_power.get('uid')), )
            self._start_power_effects(owner,operations,target=target,repeats=power_repetitions,post_operations=post_operations)
            return
        if self._replacement_power_effect(owner,target):return
        if p.primary_power is None:
            operations=self._repeated_power_operations(owner)
            if k=='HUNTER' and target>0:operations=(('damage',2),)
            self._start_power_effects(owner,operations,target=target)
            return
        if k=='WARRIOR': self._gain_armor(owner,2)
        elif k=='HUNTER': self._damage(self.hero_id(1-owner),2,damage_source=None,damage_owner=owner)
        elif k=='MAGE': self._damage(target,1,damage_source=None,damage_owner=owner)
        elif k=='PRIEST': self._heal(target,2,healer=owner,power=True)
        elif k=='DRUID': self._gain_hero_attack(owner,1); self._gain_armor(owner,1)
        elif k=='DEMONHUNTER': self._gain_hero_attack(owner,1)
        elif k=='WARLOCK': self._draw(owner); self._damage(self.hero_id(owner),2,damage_source=None,damage_owner=owner)
        elif k=='ROGUE': self._equip(owner,'CS2_082')
        elif k=='PALADIN': self._summon(owner,'CS2_101t', entry_origin='hero_power', entry_site='game._base_power')
        elif k=='DEATHKNIGHT': self._summon(owner,'TOKEN_GHOUL',expires=True, entry_origin='hero_power', entry_site='game._base_power')
        elif k=='SHAMAN':
            candidates=BASIC_TOTEM_POOL.resolve(self.cards,self.cards,exclude={m.card_id for m in p.minions})
            if not candidates:raise UnsupportedCard('No eligible basic totem')
            self._summon(owner,self.rng.choice(candidates), entry_origin='hero_power', entry_site='game._base_power')
        else: raise UnsupportedCard('Hero power '+k)

    def _equip(self,owner,cid,attack_bonus=0,physical_card=None):
        d=self.cards[cid]
        from .historical_ignis_crafting import WEAPONS,payload,equip as equip_ignis
        if cid in WEAPONS and payload(physical_card) is None:raise UnsupportedCard('Runic weapon requires its physical Ignis definition')
        if physical_card is not None and physical_card.card_id != cid:
            raise ValueError('Equipped physical card identity does not match weapon')
        self._break_weapon(owner)
        previous_attack=self._hero_attack(owner)
        self.players[owner].equipped_card = physical_card if physical_card is not None else Card(self._new_id(),cid)
        self.players[owner].equipped_card.attack_bonus=attack_bonus
        self.players[owner].weapon=dict(card_id=cid,attack=max(0,d['attack']+attack_bonus),durability=(d.get('durability') or d['health'])+self.players[owner].equipped_card.health_bonus)
        self._record_hero_stat_gain(owner,'attack',self._hero_attack(owner)-previous_attack)
        equip_ignis(self,owner,self.players[owner].equipped_card)
        from .historical_growing_weapons import equip as equip_growing_weapon
        equip_growing_weapon(self,owner)
        if cid=='TSC_937t2':self._refresh_auras()
        player=self.players[owner];player.historical_equipped_weapons=getattr(player,'historical_equipped_weapons',0)+1
        self._log('equip',player=owner,card=cid)
        self._queue_event('historical_weapon_equipped',owner=owner,weapon_uid=self.players[owner].equipped_card.uid)

    def _buff_weapon(self,owner,attack=0,durability=0):
        p=self.players[owner]
        if not p.weapon:return
        previous_attack=self._hero_attack(owner)
        p.weapon['attack']+=attack
        p.weapon['durability']+=durability
        if p.equipped_card is not None:
            _saidan_add(p.equipped_card,'attack_bonus',attack)
            _saidan_add(p.equipped_card,'health_bonus',durability)
        self._record_hero_stat_gain(owner,'attack',self._hero_attack(owner)-previous_attack)

    def _freeze(self,target):
        if self._fire_immune_target(target):return
        if target>0 and self._dormant_entity(target) is not None and self._dormant_entity(target).dormant:return
        if target>0:
            minion=self._find(target)
            if self._active('DRG_068',minion.owner):return
        if not target: return
        if target<0:
            owner=-target-1; entity=self.players[owner]; attacked=entity.hero_attacks>0; sick=False
        else:
            entity=self._find(target); owner=entity.owner; attacked=entity.attacks>0
            sick=entity.summoned_turn==self.turn and not {'CHARGE','RUSH'}&self._effective_keywords(entity)
        thaw=self.turn+1 if owner!=self.current else self.turn+(2 if attacked or sick else 0)
        was_frozen=entity.frozen_until>=0
        entity.frozen_until=max(entity.frozen_until,thaw)
        if not was_frozen:self._queue_event('historical_frozen',target=target,target_owner=owner)
        self._log('freeze',target=target,until=entity.frozen_until)
        self._historic_colossal_frozen(target)

    def _attack(self,source,target,*,forced=False):
        return self._combat_resolver.attack(self,source,target,forced=forced)

    def _resolve_combat(self,source,target,listeners,*,forced=False,excess_to_hero=False):
        return self._combat_resolver.resolve(self,source,target,listeners,forced=forced,excess_to_hero=excess_to_hero)

    def _play(self,action):
        self._rewind_begin(action)
        owner=self.current; p=self.players[owner]
        card=next(c for c in p.hand if c.uid==action.source); cid=card.card_id; d=self._card_data(card)
        from .historical_location_timed import frozen_locked
        if frozen_locked(self,owner,card):raise UnsupportedCard('Frozen Over prevents playing this physical card this turn')
        echo_play='ECHO' in d.get('mechanics',()) or (d['type']=='MINION' and self._active('GIL_618',owner))
        echo_listeners=tuple(m.uid for m in p.minions if m.card_id=='GIL_510' and not m.silenced and not m.dormant and m.health>0)
        from .historical_zilliax import FORMS as ZILL_FORM_IDS,require_definition as require_zilliax
        if cid in ZILL_FORM_IDS:require_zilliax(card)
        self._gelbin_preflight(cid,owner)
        self._dark_global_preflight(cid,owner)
        self._mutation_preflight(cid,owner)
        self._rewindgen_preflight(cid,owner)
        self._imbue_consumer_preflight(cid,owner)
        outcast=card.uid in (p.hand[0].uid,p.hand[-1].uid); combo=p.cards_played>0
        essence_neighbors=self._essence_neighbors(card,owner)
        hand_index=p.hand.index(card)
        historical_play_edges=(hand_index==0,hand_index==len(p.hand)-1)
        hand_neighbors=tuple(p.hand[i].uid for i in (hand_index-1,hand_index+1) if 0<=i<len(p.hand))
        for neighbor_uid in hand_neighbors:
            neighbor=next(c for c in p.hand if c.uid==neighbor_uid)
            self._b60_state(neighbor)['historical_orbital_adjacent_turn']=self.turn
            if neighbor.card_id=='GDB_341':self._b60_state(neighbor)['historical_adjacent_plays']=self._b60_state(neighbor).get('historical_adjacent_plays',0)+1
        hand_center=len(p.hand)%2==1 and p.hand[len(p.hand)//2].uid==card.uid
        if cid=='JAIL_501':self._b60_state(card)['picklock_value']=max(1,p.mana)
        cost=self._cost(card,owner); source=None
        refresh_attack_grant=sum(bool(e.get('grant_refresh_attack')) for e in p.cost_effects if self._discount_matches(e,card))
        overload_grant=sum(e.get('grant_overload',0) for e in p.cost_effects if self._discount_matches(e,card))
        historical_minion_mods=[e['historical_minion_play'] for e in p.cost_effects if e.get('historical_minion_play') and self._discount_matches(e,card)]
        historical_deathrattle_play=d['type']=='MINION' and 'DEATHRATTLE' in self._card_mechanics(card)
        historical_immediate_death=historical_deathrattle_play and self._active('VAC_503',owner) or d['type']=='MINION' and 'BATTLECRY' in self._card_mechanics(card) and self._active('GDB_448',owner) or d['type']=='MINION' and 'die' in historical_minion_mods
        historical_experimenter=historical_deathrattle_play and self._active('BOT_566',owner)
        grants=[e.get('grant_keyword') for e in p.cost_effects if self._discount_matches(e,card) and e.get('grant_keyword')]
        from .historical_play_batches import consume_discounts
        consume_discounts(self,owner,card)
        if cid not in RULES and cid not in PASSIVE and cid not in PLAYABLE_TOKENS and cid not in LOCATION_RULES: raise UnsupportedCard(cid)
        mirror=getattr(card,'_historical_mirror_mode',None)
        if mirror=='mirage':
            # The hand bearer remains; a detached physical copy is played.
            card=self._copy_card(card,source_owner=owner)
        elif cid!='TIME_042t':p.hand.remove(card)
        if mirror is not None:
            for field in ('_historical_mirror_mode','_historical_mirror_baseline'):
                if hasattr(card,field):delattr(card,field)
        getattr(card,'rule_state',{}).pop('historical_chaos_gaze_due',None)
        self._quest_deliver_ready(owner)
        self._dream_higher_play(owner,card,cost)
        self._origin_played(owner,card)
        self._capture_follow(owner,card)
        mana_before_payment=p.mana
        self._pay_card(card,owner,cost)
        from .historical_kazakusan import paid as record_dragon_play
        record_dragon_play(self,owner,card)
        from .historical_anomalies import capture_first_play as capture_anomaly_play
        anomaly_play_copy=capture_anomaly_play(self,owner,card)
        from .physical_choices import branches as physical_branches
        physical_choice_branches=physical_branches(card,CHOICES)
        if physical_choice_branches and cid not in ('WORK_025','VAC_907'):
            from .historical_combined_choices import consume
            consume(self,owner)
        if d['type']=='SPELL':p.historical_ship_spell_played_turn=self.turn
        from .historical_copy_batches import CONCOCTION_IDS
        if cid in CONCOCTION_IDS:p.historical_next_concoction_free=False
        p.historical_frost_fever=0
        if d['type']=='SPELL':p.historical_spell_mana_spent=getattr(p,'historical_spell_mana_spent',0)+max(0,mana_before_payment-p.mana)
        from .historical_conditional_spells import paid as record_conditional_spell_payment
        record_conditional_spell_payment(self,owner,card,mana_before_payment-p.mana)
        from .historical_timed_spells import paid as timed_spell_paid
        timed_spell_paid(self,owner,card)
        from .historical_growing_weapons import paid as growing_weapon_paid
        growing_weapon_paid(self,owner,card,cost,outcast)
        from .historical_lingering_spells import paid as lingering_spell_paid
        lingering_spell_paid(self,owner,card)
        from .historical_movements import record
        record(self,'played')
        finale_after_payment=p.mana==0
        if self._check_heroes():return
        self._b60_paid_card(owner,cost)
        self._log('play',player=owner,card=cid,target=action.target,position=action.position)
        paid_record=getattr(p,'historical_paid_card_turn',{})
        if paid_record.get('turn')!=self.turn:paid_record=dict(turn=self.turn,cards=[])
        paid_record['cards'].append(deepcopy(card));p.historical_paid_card_turn=paid_record
        self._secret_event('card_paid',owner,physical_card=card)
        from .historical_copy_batches import copycat_play_admitted
        copycat_play_admitted(self,owner,card)
        from .historical_valeera import played as reflection_played
        reflection_played(self,owner,card)
        if self._is_quest(cid):p.quests_played+=1
        self._quest_card_played(owner,card,paid_cost=cost)
        source=None
        self._investigation_played(owner,card)
        repeat_spell=False
        historical_relic_extra=0
        historical_spell_bonus=0;historical_spell_lifesteal=False
        if d['type']=='SPELL':
            from .historical_location_timed import relic_extra
            historical_relic_extra=relic_extra(self,owner,cid)
            repeat_spell=getattr(p,'historical_brukan_spells_twice',False) or (has_school(d,'ARCANE') and self._active('RLK_541',owner)) or getattr(p,'historical_spell_repeat_turn',None)==self.turn or (bool(getattr(card,'rule_state',{}).get('repeat_spell')) or getattr(card,'rule_state',{}).get('historical_stargazing_turn')==self.turn) or p.spell_repeat_charges>0 or (cost<=2 and self._active('VAC_507',owner)) or (cost==1 and self._active('TLC_836',owner))
            repeat_spell=self._azure_repeats_spell(owner,cid,other_repeat=repeat_spell) or repeat_spell
            repeat_spell=self._colossal_repeats_spell(owner,cid,other_repeat=repeat_spell) or repeat_spell
            if p.spell_repeat_charges:p.spell_repeat_charges-=1
            p.historical_spell_repeat_turn=None
            historical_spell_bonus=sum(effect['amount'] for effect in getattr(p,'historical_next_spell_bonuses',()) if effect['turn']==self.turn)
            p.historical_next_spell_bonuses=[]
            if has_school(d,'FIRE'):
                historical_spell_bonus+=getattr(p,'historical_next_fire_bonus',0);p.historical_next_fire_bonus=0
            historical_spell_lifesteal=getattr(p,'historical_next_spell_lifesteal',False);p.historical_next_spell_lifesteal=False
            from .historical_keyword_batches import snapshot_spell
            snapshot_spell(self,card,owner)
            from .historical_copy_batches import record_targeted_spell
            record_targeted_spell(self,owner,card,action.target,history=False)
            self._queue_event('spell_played',owner=owner,card_id=cid,cost=cost,physical_card=card)
            self._drain_events()
            if self.terminal:return
        from .historical_copy_batches import counter_play_admitted
        if counter_play_admitted(self,owner,card,paid_cost=cost):
            # Countered cards were paid and played, but never summoned/cast.
            from .historical_frozen_heroes import event as frozen_hero_event
            frozen_hero_event(self,'dormant_other_card_played',dict(owner=owner,card_id=cid))
            from .historical_masquerade import reveal as reveal_masquerade
            if has_class(d,'ROGUE'):reveal_masquerade(self,owner)
            from .historical_obligation_spells import paid as obligation_paid
            obligation_paid(self,owner,card)
            p.cards_played+=1;p.played_history.append(dict(card_id=cid,cost=cost,overload_card=bool(d.get('overload',0)) and (cid!='YOP_024' or getattr(card,'rule_state',{}).get('historical_guidance_overload',False)) and not (cid=='SCH_612' and action.choices==(0,))))
            p.last_paid_cost=cost
            getattr(self,'_historical_spellburst_pending',{}).pop(card.uid,None)
            if anomaly_play_copy is not None:
                self._rule_events.append(('captured_effects',dict(operations=(('historical_utility_anomaly_shuffle',anomaly_play_copy),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
            self._publish_follow(owner)
            self._settle(allow_event_choices=True)
            return
        if d['type']=='SPELL':
            from .historical_copy_batches import redirect_sanctum,record_targeted_spell
            from .historical_secret_events import redirect_spellbender
            redirected=redirect_spellbender(self,owner,action.target)
            redirected=redirect_sanctum(self,owner,redirected)
            if redirected!=action.target:action=replace(action,target=redirected)
            record_targeted_spell(self,owner,card,action.target,history=False)
        if has_school(d,'FIRE'): p.fire_spell_played=True
        recipient=1-owner if cid in EITHER_SIDE and action.choices==(1,) else owner
        magnetized=False
        if d['type']=='MINION':
            for modifier in historical_minion_mods:
                if modifier=='set_8_8':self._mutation_set_stats(card,owner,8,8)
                elif modifier=='buff_2_1':_saidan_add(card,'attack_bonus',2);_saidan_add(card,'health_bonus',1)
                elif modifier=='health_2_rush':_saidan_add(card,'health_bonus',2);grants.append('RUSH')
            magnetized=self._magnetic_attach(card,recipient,action.position,grants)
            if not magnetized:
                from .historical_form_batches import resolve as resolve_historical_form
                body_id=resolve_historical_form(cid,action.choices)
                source=self._summon(recipient,body_id,action.position,card.attack_bonus,card.health_bonus, entry_origin='play', entry_site='game._play', entry_zone='hand', entry_source=card)
        elif d['type']=='LOCATION':
            source=self._place_location(owner,cid,action.position);self._crafted_location_entry(source,card)
            if source is not None:source.rule_state['historical_played_turn']=self.turn
        elif d['type']=='WEAPON': self._equip(owner,cid,attack_bonus=card.attack_bonus,physical_card=card)
        elif d['type']=='HERO': self._play_hero_card(owner,cid)
        elif d['type']!='SPELL': raise UnsupportedCard('Card type '+d['type'])
        if source is not None and d['type']=='MINION':
            source.played_turn=self.turn
            source.rule_state['historical_played_entry_attack']=source.attack
            self._imbue_consumer_play(owner,source)
            if 'rewinds_remaining' in getattr(card,'rule_state',{}):source.rule_state['rewinds_remaining']=card.rule_state['rewinds_remaining']
            if 'destroy_on_turn' in self._b60_state(card):source.rule_state['destroy_on_turn']=card.rule_state['destroy_on_turn']
            if not source.dormant:source.keywords.update(grants)
        targeted_minion=any(m.uid==action.target for player in self.players for m in player.minions)
        context=dict(finale=finale_after_payment,prior_card_count=p.cards_played,prior_spell_count=len(p.spells_turn),physical_card=card,paid_cost=cost,card_id=cid,owner=recipient,source=source,target=action.target,kindred=self._kindred(card,owner),spell=d['type']=='SPELL',bonus=(self._spell_damage(owner,cid,card)) if d['type']=='SPELL' else 0,lifesteal='LIFESTEAL' in d.get('mechanics',[]),outcast=outcast,combo=combo,hand_center=hand_center,hand_neighbors=hand_neighbors)
        context['essence_neighbors']=essence_neighbors
        if context.get('spell'):context['stormwind_spell_damage_state']=dict(seen=False)
        if d['type']=='SPELL':
            from .historical_copy_batches import record_targeted_spell
            record_targeted_spell(self,owner,card,action.target,targeting=False)
            from .historical_copy_batches import record_spell_cast
            record_spell_cast(self,owner,card,action.target)
            self._drain_events()
            if self.terminal:return
        if d['type']=='SPELL':
            context['bonus']+=getattr(p,'_next_spell_bonus',0)+historical_spell_bonus;p._next_spell_bonus=0
            context['lifesteal']=context['lifesteal'] or historical_spell_lifesteal
        from .kindred import consume_repetition
        context['kindred_repeats']=consume_repetition(self,owner,cid,context['kindred'])
        operations=(self._crafted_rule(card) or RULES.get(cid,('none',[])))[1]
        if physical_choice_branches:
            selected=physical_choice_branches if action.choices==(-1,) else [physical_choice_branches[action.choices[0]]]
            operations=[op for _,_,ops in selected for op in ops]
            from .historical_prime_batches import COMBINED_CHOICES
            if action.choices==(-1,) and cid in COMBINED_CHOICES and 'physical_choose_one' not in getattr(card,'rule_state',{}):
                operations=list(COMBINED_CHOICES[cid])
            elif action.choices==(-1,) and cid=='CORE_EX1_154':
                operations=[('damage',4),('draw',1)]
            elif action.choices==(-1,) and cid=='CORE_EX1_160':
                operations=[('summon','EX1_160t',1),('board_buff',1,1)]
        if d['type']=='SPELL' and cid in CHOICES:
            from .historical_copy_batches import capture_choose_spell
            capture_choose_spell(self,owner,card,-1 if action.choices==(-1,) else action.choices[0])
        if not magnetized:
            from .historical_copy_batches import capture_battlecry_program
            recipe=self._crafted_rule(card) or RULES.get(cid,('none',[]))
            repeat_mode=recipe[0]
            if physical_choice_branches and action.choices and action.choices!=(-1,):repeat_mode=physical_choice_branches[action.choices[0]][1]
            capture_battlecry_program(self,owner,card,repeat_mode,operations)
        if 'BATTLECRY' in d.get('mechanics',[]) or (d['type'] in ('MINION','WEAPON') and self._crafted_rule(card)):
            # Combo branches are independent triggers and are not doubled by Brann.
            battlecry_count=self._battlecry_repetitions(owner)
            if getattr(p,'historical_murmuring_turn',None)==self.turn:
                battlecry_count=max(battlecry_count,2);p.historical_murmuring_turn=None
            shudderblock=bool(getattr(p,'historical_shudderblock_pending',False) and not magnetized)
            if shudderblock:
                p.historical_shudderblock_pending=False
                battlecry_count=max(battlecry_count,3)
            if d['type']=='MINION' and 'COMBO' in d.get('mechanics',[]):
                comet=getattr(p,'historical_comet_charges',0)>0
                if comet:p.historical_comet_charges=0
                combo_count=2 if self._active('TRL_092',owner) or comet else 1
                from .combo_programs import separate as separate_combo_program
                battlecry_ops,combo_ops=separate_combo_program(operations,context,combo_count)
                operations=battlecry_ops*battlecry_count
                combo_ops=combo_ops*combo_count
            else:operations=list(operations)*battlecry_count;combo_ops=[]
            if shudderblock and source is not None:
                battlecry_context=dict(context,historical_shudderblock_uid=source.uid)
                operations=[('replay_context',tuple(operations),battlecry_context)]
            operations=list(operations)+combo_ops
        if d['type']=='MINION' and 'COMBO' in d.get('mechanics',[]) and 'BATTLECRY' not in d.get('mechanics',[]):
            comet=getattr(p,'historical_comet_charges',0)>0
            if comet:p.historical_comet_charges=0
            combo_count=2 if self._active('TRL_092',owner) or comet else 1
            from .combo_programs import separate as separate_combo_program
            base_ops,combo_ops=separate_combo_program(operations,context,combo_count)
            operations=base_ops+combo_ops*combo_count
        operations=self._mug_play_operations(owner,cid,operations)
        if d['type']=='MINION':operations=self._dark_play_operations(operations,card,source)
        operations=self._morchie_operations(operations,context)
        if magnetized:operations=[]
        from .historical_play_batches import SINGLE_PLAY_EFFECTS
        if cid in SINGLE_PLAY_EFFECTS:operations=list(operations)+list(SINGLE_PLAY_EFFECTS[cid])
        if refresh_attack_grant and d['type']=='MINION':operations=list(operations)+[('historical_resource_refresh_attack',refresh_attack_grant)]
        if d['type']=='MINION' and not magnetized:
            operations=list(operations)+[('historical_copy_next_follow',modifier) for modifier in historical_minion_mods if modifier in ('attack','copy','hero_attack')]
        if d['type']=='MINION' and source is not None and not magnetized:
            if historical_immediate_death:operations=list(operations)+[('historical_copy_recruited_kill',dict(uid=source.uid))]
            if historical_experimenter:
                source.rule_state['historical_experimenter_death']=True
                self._schedule_turn_effect(self.current,'end',0,1,(('historical_copy_experimenter_end',source.uid),),source_card_id='BOT_566')
        if d['type']=='SPELL':
            from .historical_utility_spells import conductivity_program
            operations=conductivity_program(self,operations,context)
        if repeat_spell or historical_relic_extra:
            operations=[('repeat_spell_effects',tuple(operations),context,(2 if repeat_spell else 1)+historical_relic_extra)]
        from .replay_history import capture_play
        replay_record=capture_play(self.turn,owner,card,cost,action)
        if echo_play:operations=list(operations)+[('historical_upgrade_echo',cid,echo_listeners)]
        if cid=='TSC_952':operations=list(operations)+[('historical_utility_maki_copy',)]
        if d['type']=='SPELL':
            from .historical_headmaster import begin as begin_headmaster
            begin_headmaster(self,card)
        if anomaly_play_copy is not None:operations=list(operations)+[('historical_utility_anomaly_shuffle',anomaly_play_copy)]
        self._start_play_effects(operations,context)
        p.replay_history.append(replay_record)
        overload_player=self.players[recipient] if cid=='JAIL_452' else p
        from .forge_intrinsics import values as forge_values
        overload=d.get('overload',0)+sum(forge_values(card,'overload'))
        if cid=='YOP_024' or cid=='SCH_612' and action.choices==(0,):overload-=d.get('overload',0)
        from .historical_resource_batches import add_overload,played_overload
        overload=played_overload(self,owner,card,overload+overload_grant)
        add_overload(self,recipient if cid=='JAIL_452' else owner,overload);p.cards_played+=1
        pending_overloads=getattr(p,'historical_play_overloads',{})
        pending_overloads[card.uid if d['type']=='SPELL' else getattr(source,'uid',None)]=(int(bool(getattr(card,'rule_state',{}).get('historical_guidance_overload'))) if cid=='YOP_024' else 0 if cid=='SCH_612' and action.choices==(0,) else d.get('overload',0))+sum(forge_values(card,'overload'))+overload_grant
        p.historical_play_overloads=pending_overloads
        p.played_history.append(dict(card_id=cid,cost=cost,overload_card=bool(d.get('overload',0)) and (cid!='YOP_024' or getattr(card,'rule_state',{}).get('historical_guidance_overload',False)) and not (cid=='SCH_612' and action.choices==(0,))))
        from .historical_velen import record_play as record_velen_play
        record_velen_play(self,owner,card,source)
        from .historical_harvester import record_play as record_harvester_play
        record_harvester_play(self,owner,card,source)
        counts=getattr(p,'historical_cost_turn',{})
        if counts.get('turn')!=self.turn:counts={'turn':self.turn}
        for key,qualifies in (('minions',d['type']=='MINION'),('spells',d['type']=='SPELL'),('taunts',d['type']=='MINION' and 'TAUNT' in d.get('mechanics',())),('secrets','SECRET' in d.get('mechanics',()))):
            if qualifies:counts[key]=counts.get(key,0)+1
        p.historical_cost_turn=counts
        p.last_paid_cost=cost
        if d['type']=='SPELL':
            p.spells_cast_turn+=1
            p.spells_turn.append(cid)
            if cost>=5:p.historical_big_spell_turn=self.turn
            if d.get('spellSchool'):p.spell_schools_this_turn.add(d['spellSchool'])
            if d.get('spellSchool')=='FEL':p.fel_spells_cast+=1
        if d['type']=='MINION':
            from .historical_form_batches import FORMS
            tribe_data=self._card_data(source) if source is not None and cid in FORMS else d
            p.played_tribes.update(tribe_data.get('races',[]));p.minion_played_this_turn=True
        if d['type']=='SPELL' and d.get('spellSchool'):p.played_schools.add(d['spellSchool'])
        historical_edges=getattr(p,'_historical_edge_plays',{})
        historical_edges[(cid,getattr(card if d['type']=='SPELL' else source,'uid',None))]=historical_play_edges
        p._historical_edge_plays=historical_edges
        context=(cid,owner,card if d['type']=='SPELL' else source,cost,targeted_minion)
        if self.pending_choice: self.pending_play=context
        else: self._after_play(context)

    def _deal_effect(self,target,amount,ctx):
        if not target: return 0
        if target>0 and not any(m.uid==target for p in self.players for m in p.minions): return 0
        source=ctx.get('source')
        poisonous=('POISONOUS' in self._effective_keywords(source)) if source is not None else ctx.get('poisonous',False)
        bonus=ctx.get('bonus',0)
        if ctx.get('spell') and 'ImmuneToSpellpower' in self.cards.get(ctx.get('card_id'),{}).get('mechanics',()):bonus=0
        amount=self._outgoing_tribal_damage(source,amount+bonus)
        if ctx.get('spell'):
            poisonous=poisonous or self._active('SCH_539',ctx['owner']) or getattr(self.players[ctx['owner']],'historical_spell_poisonous_turn',None)==self.turn
            if target>0:
                amount*=2**sum(m.card_id=='BT_733' and not m.silenced and m.health>0 for player in self.players for m in player.minions)
        if ctx.get('spell'):
            multiplier=self._spell_multiplier(ctx['owner'])
            if not ctx.get('spell_multiplier_applied'):amount*=multiplier
        if self._fire_immune_target(target,ctx):return 0
        if self._replace_spell_damage(target,amount,ctx):return 0
        dealt=self._damage(target,amount,poisonous=poisonous,damage_source=source,damage_owner=ctx['owner'],damage_cause='hero_power' if ctx.get('power') else None)
        from .historical_stormwind_questline_finish import spell_damage as stormwind_spell_damage
        stormwind_spell_damage(self,ctx,dealt)
        self._freeze_from_damage(source,target,dealt)
        if ctx.get('spell'):
            player=self.players[ctx['owner']]
            if dealt>0 and player.spell_damage_turn==0:
                for m in player.minions:
                    if m.card_id=='CATA_487' and not m.silenced and m.health>0:self._buff(m,2,0)
            player.spell_damage_turn+=dealt
        lifesteal=('LIFESTEAL' in self._effective_keywords(source)) if source is not None else ctx.get('lifesteal',False)
        if ctx.get('spell'):
            from .historical_resource_batches import spell_lifesteal
            lifesteal=lifesteal or spell_lifesteal(self,ctx['owner'],ctx.get('card_id'))
        if lifesteal and dealt:self._effect_lifesteal(ctx['owner'],dealt,spell=ctx.get('spell',False),power=ctx.get('power',False))
        return dealt

    def _effect(self,op,ctx):
        return self._effect_executor.execute(self,op,ctx)

    def _effect_checkpoint(self,op,ctx):
        return self._effect_executor.checkpoint(self,op,ctx)

    def _dispatch_effect(self,op,ctx):
        return self._effect_executor.dispatch(self,op,ctx)

    def observe(self,viewer,include_events=True):
        observation=super().observe(viewer,include_events)
        observation['transfer_student_form']=self.transfer_student_form
        observation['approximation_profile']=deepcopy(self.approximation_profile)
        from .approximation_policy import POLICY_VERSION,RULES as approximation_rules
        observation['additional_approximations']=dict(version=POLICY_VERSION,independently_validated=False,rules=dict(approximation_rules))
        observation['historical_dew_count']=len(getattr(self,'historical_dew_sources',()))
        tar=getattr(self,'historical_tar_slick',{})
        observation['historical_tar_layers']=tar.get('layers',0) if tar.get('turn')==self.turn else 0
        actor=self.pending_choice['owner'] if self.phase=='choice' and self.pending_choice else self.current
        observation['legal_actions']=[asdict(a) for a in self.legal_actions()] if viewer==actor else []
        for owner,(p,public) in enumerate(zip(self.players,observation['players'])):
            public['stealth']=self._hero_stealth(owner)
            public.update(divine_shield=p.divine_shield,max_health=p.max_health,turns_taken=p.turns_taken,immune=self._hero_immune(owner),hero_class=p.hero_class,hero_attack=self._hero_attack(owner),frozen=p.frozen_until>=0,
                          locked_mana=p.locked_mana,overload_next=p.overload_next,cards_played=p.cards_played,
                          secret_count=len(p.secrets),fire_spell_played=p.fire_spell_played,hero_power_uses=p.hero_power_uses)
            for entity in public['board']:
                actual=next((m for m in p.all_minions if m.uid==entity['uid']),None)
                if actual is not None:
                    from .selectors import tribes
                    entity['races']=sorted(tribes(self._card_data(actual)))
                    if hasattr(actual,'_historical_jade_definition'):entity['jade_definition']=deepcopy(actual._historical_jade_definition)
                    entity['attacked_this_turn']=getattr(self,'_historical_attack_turns',{}).get(actual.uid)==self.turn
                if actual is not None and owner==viewer and hasattr(actual,'_nellie_crew'):
                    entity['nellie_crew']=list(actual._nellie_crew)
                if 'avatar_form' in entity.get('rule_state',{}):
                    entity['rule_state']['avatar_form']=sum(b['turn']==self.turn for b in entity['rule_state']['avatar_form'])
                if actual is not None and hasattr(actual,'_muradin_hammer'):
                    held=actual._muradin_hammer
                    entity['held_hammer']=dict(card_id=held['card'].card_id,attack=held['attack'],durability=held['durability'])
                    entity['held_hammers']=[dict(card_id=h['card'].card_id,attack=h['attack'],durability=h['durability']) for h in [held]+list(getattr(actual,'_muradin_extra_hammers',()))]
                if actual is not None and hasattr(actual,'_control_return'):
                    effect=actual._control_return
                    entity['control_return']=dict(to='self' if effect['owner']==viewer else 'opponent',turns=max(0,effect['due']-self.players[effect['owner']].turns_taken))
                    if 'layers' in effect:
                        entity['control_return']['layers']=[dict(controller='self' if layer['controller']==viewer else 'opponent',end_of_turn=layer['end_timer'],deadline_player='self' if layer['deadline_owner']==viewer else 'opponent',turns=max(0,layer['due']-self.players[layer['deadline_owner']].turns_taken)) for layer in effect['layers']]
                for effect in entity.get('imbue_attack_expiries',[]):
                    effect['expires_at_turn_of']='self' if effect.pop('owner')==viewer else 'opponent'
            for entity in public['board']:entity.get('rule_state',{}).pop('historical_elekk_spells',None)
            if owner!=viewer:
                for entity in public['board']:
                    entity.get('rule_state',{}).pop('absorbed_spell_id',None)
                    entity.get('rule_state',{}).pop('historical_fatespinner',None)
                    entity.get('rule_state',{}).pop('historical_suspicious_memory',None)
                    entity.get('rule_state',{}).pop('historical_chromatic_dragon',None)
                    entity.get('rule_state',{}).pop('historical_okani_counters',None)
                    entity.get('rule_state',{}).pop('historical_gamer_games',None)
            public.update(self._obligation_view(owner,viewer))
            public['broxigar_waiting']=sum(getattr(c,'_starting_owner',None)==owner for c in getattr(self,'_broxigar_waiting',[]))
            public['mana_capacity']=p.mana_capacity
            public['starships_launched']=getattr(p,'historical_ship_launches',0)
            public['starship_launch_discount']=getattr(p,'historical_ship_discount',0)
            public['manastorm_effects']=p.manastorm_effects
            public['companion_extra']=p.companion_extra
            public['companion_upgrades']=p.companion_upgrades
            public['void_soul_level']=p.void_soul_level
            public['bwonsamdi_boons']=list(p.bwonsamdi_boons)
            public['avatar_form']=sum(b['turn']==self.turn for b in p.avatar_form)
            public['herald_count']=p.herald_count
            public['deathwing_discount']=p.deathwing_discount
            public['overdraw_return_active']=p.overdraw_return_active
            public['overdraw_cache_count']=len(p.overdraw_cache)
            if owner==viewer:public['overdraw_cache']=[dict(card_id=c.card_id,cost=self._cost(c,owner)) for c in p.overdraw_cache]
            public['hero_lifesteal']=p.hero_lifesteal_until>=self.turn or self._active('ETC_398',owner)
            if owner==viewer:public['companion_ids']=list(p.companion_ids)
            public['hero_attacks_total']=p.hero_attacks_total
            public['extra_turns_pending']=p.extra_turns_pending
            public['time_warp_used']=p.time_warp_used
            public['crystal_core']=p.crystal_core
            public['kindred_twice']=getattr(p,'kindred_twice',False)
            public['next_spell_bonus']=getattr(p,'_next_spell_bonus',0)
            public['counterfeit_coin']=getattr(p,'counterfeit_coin',None)
            public['historical_summoned_ids']=dict(getattr(p,'historical_summoned_ids',{}))
            public['historical_summoned_tribes']=dict(getattr(p,'historical_summoned_tribes',{}))
            public['historical_big_spell_this_turn']=getattr(p,'historical_big_spell_turn',None)==self.turn
            public['historical_spell_schools']=list(getattr(p,'historical_spell_schools',()))
            public['historical_last_riff']=getattr(p,'historical_last_riff',None)
            public['historical_lightshow_count']=getattr(p,'historical_lightshow_count',0)
            public['historical_crystal_cove_active']=getattr(p,'historical_crystal_cove_turn',None)==self.turn
            public['historical_relic_vault_count']=getattr(p,'historical_relic_vault',{}).get('count',0) if getattr(p,'historical_relic_vault',{}).get('turn')==self.turn else 0
            public['historical_starlight_groove']=bool(getattr(p,'historical_starlight_groove',False))
            public['historical_allies_active']=getattr(p,'historical_allies_turn',None)==self.turn
            public['historical_melomania_count']=getattr(p,'historical_melomania',{}).get('count',0) if getattr(p,'historical_melomania',{}).get('turn')==self.turn else 0
            public['historical_school_counts']=dict(getattr(p,'historical_school_counts',{}))
            public['historical_next_beast']=list(getattr(p,'historical_next_beast',()))
            public['historical_nonstarting_demon_discount']=getattr(p,'historical_nonstarting_demon_discount',0)
            public['historical_armor_gained']=getattr(p,'historical_armor_gained',0)
            public['historical_armor_changed_this_turn']=getattr(p,'historical_armor_changed_turn',None)==self.turn
            public['historical_odyn']=getattr(p,'historical_odyn',0)
            public['historical_equipped_weapons']=getattr(p,'historical_equipped_weapons',0)
            public['historical_hero_windfury']=getattr(p,'historical_hero_windfury_turn',None)==self.turn
            public['historical_forges']=getattr(p,'historical_forges',0)
            public['historical_power_turn']=dict(getattr(p,'historical_power_turn',{}))
            public['historical_libram_discount']=getattr(p,'historical_libram_discount',0)
            public['historical_draw_turn']=dict(getattr(p,'historical_draw_turn',{}))
            public['historical_nonrogue_hand_additions']=getattr(p,'historical_nonrogue_hand_additions',0)
            public['historical_stampede']=deepcopy(getattr(p,'historical_stampede',{}))
            public['temporary_mana_available']=getattr(p,'temporary_mana_available',0)
            public['historical_hero_minions_only']=getattr(p,'historical_hero_minions_only_turn',-1)==self.turn
            public['historical_hero_cleave']=getattr(p,'historical_hero_cleave_turn',-1)==self.turn
            public['historical_drawn_total']=getattr(p,'historical_drawn_total',0)
            public['historical_own_turn_damage_total']=getattr(p,'historical_own_turn_damage_total',0)
            public['historical_own_turn_damage_events']=getattr(p,'historical_own_turn_damage_events',0)
            public['historical_raza']=getattr(p,'historical_raza',False)
            public['historical_plagues_shuffled']=getattr(p,'historical_plagues_shuffled',0)
            public['historical_unending_plagues']=getattr(p,'historical_unending_plagues',False)
            from .historical_copy_batches import elemental_streak
            public['historical_elemental_streak']=elemental_streak(self,owner)
            public['historical_eonar_pending']=getattr(p,'historical_eonar_pending',False)
            public['historical_frost_fever']=getattr(p,'historical_frost_fever',0)
            public['historical_corpses_spent']=getattr(p,'historical_corpses_spent',0)
            public['historical_draw_cast_charges']=getattr(p,'historical_draw_cast_charges',0)
            public['historical_queued_turns']=['self' if queued==viewer else 'opponent' for queued in getattr(self,'_historical_turn_queue',())]
            public['historical_own_health_changes']=getattr(p,'historical_own_health_changes',0)
            public['historical_next_fire_bonus']=getattr(p,'historical_next_fire_bonus',0)
            public['historical_rommath_used']=getattr(p,'historical_rommath_used',False)
            public['historical_cast_record_count']=len(getattr(p,'_historical_cast_records',()))
            public['historical_genn']=getattr(p,'historical_genn',False)
            public['historical_topior']=getattr(p,'historical_topior',0)
            public['historical_eliza']=getattr(p,'historical_eliza',0)
            public['historical_locations_used']=getattr(p,'historical_locations_used',0)
            public['historical_excavations']=getattr(p,'historical_excavations',0)
            public['historical_excavate_tier']=getattr(p,'historical_excavate_tier',0)
            public['historical_murmuring_pending']=getattr(p,'historical_murmuring_turn',None)==self.turn
            public['historical_shudderblock_pending']=bool(getattr(p,'historical_shudderblock_pending',False))
            public['historical_aegwynn_pending']=getattr(p,'historical_aegwynn_pending',0)
            gains=getattr(p,'historical_hero_stat_gains',{})
            public['hero_attack_gained_turn']=gains.get('attack',0) if gains.get('turn')==self.turn else 0
            public['armor_gained_turn']=gains.get('armor',0) if gains.get('turn')==self.turn else 0
            public['historical_fizzle_used']=getattr(p,'historical_fizzle_used',False)
            public['historical_snapshot_used']=getattr(p,'historical_snapshot_used',False)
            public['historical_jotun']=getattr(p,'historical_jotun',False)
            public['historical_spell_drawn_this_turn']=getattr(p,'historical_first_spell_draw_turn',None)==self.turn
            public['hand_capacity']=p.hand_capacity
            public['historical_abyssal_counter']=getattr(p,'historical_abyssal_counter',0)
            public['historical_weapon_spell_bonus']=sum(e['amount'] for e in getattr(p,'historical_weapon_spell_bonuses',()) if e['turn']==self.turn)
            public['historical_spells_cast']=getattr(p,'historical_spells_cast',0)
            public['historical_dragons_played']=getattr(p,'historical_dragons_played',0)
            public['historical_anomalies']=list(getattr(self,'historical_anomaly_ids',()))
            public['all_cards_golden']=getattr(p,'historical_all_cards_golden',False)
            public['historical_cost_turn']=dict(getattr(p,'historical_cost_turn',{}))
            public['historical_lackeys_four']=getattr(p,'historical_lackeys_four',False)
            public['tribal_effects']={key:getattr(p,key,0) for key in ('historical_treant_bonus','historical_stonewrights','historical_stewart_pending','historical_lothraxion')}
            public['relic_level']=getattr(p,'historical_relic_level',0)
            public['galakrond_invokes']=getattr(p,'historical_invokes',0)
            public['jade_size']=getattr(p,'jade_size',0)
            public['cthun_ritual_growth']=list(getattr(p,'historical_cthun_growth',(0,0)))
            public['cthun_ritual_taunt']=getattr(p,'historical_cthun_taunt',False)
            public['jade_display_growth']=getattr(p,'historical_display_growth',0)
            public['tendril_cost']=getattr(p,'tendril_cost',1)
            public['forge_sidequests']=deepcopy(getattr(p,'forge_sidequests',[]))
            public['eudora_sidequest']=deepcopy(getattr(p,'eudora_sidequest',None))
            public['turn_time_limit']=self._turn_clock_limit()
            public['turn_time_elapsed']=getattr(self,'turn_time_elapsed',0)
            public['historical_spell_obligations']=dict(
                mana_burn_next=getattr(p,'historical_mana_burn_next',0),
                mana_burn_active=getattr(p,'historical_mana_burn_active',0),
                commanding_shout_active=getattr(p,'historical_shout_turn',None)==self.turn,
                lucky_comet_charges=getattr(p,'historical_comet_charges',0),
                summon_watchers=[dict(kind=t['kind'],remaining=sorted(t['remaining'])) for t in getattr(p,'_historical_summon_obligations',()) if t['turn']==self.turn],
                acrobatics_remaining=[len(t['remaining']) for t in getattr(p,'_historical_acrobatics',()) if t['turn']==self.turn])
            if owner==viewer:
                public['acrobatics_cards']=[sorted(t['remaining']) for t in getattr(p,'_historical_acrobatics',()) if t['turn']==self.turn]
                public['secret_passage_hands']=[[dict(uid=c.uid,card_id=c.card_id,cost_delta=getattr(c,'cost_delta',0),attack_bonus=getattr(c,'attack_bonus',0),health_bonus=getattr(c,'health_bonus',0),set_cost=getattr(c,'set_cost',None)) for c in task['hand']] for task in getattr(p,'_historical_passages',{}).values()]
            if owner==viewer:public['contraband_beasts']=list(getattr(p,'contraband_beasts',()))
            if owner==viewer:public['hand_investigations']=[dict(w) for w in getattr(p,'_hand_investigations',[])]
            public['next_heal_damage']=getattr(p,'ruby_until',-1)==self.turn or getattr(p,'historical_healing_damage_turn',None)==self.turn or getattr(p,'historical_healing_damage_charges',0)>0
            public['historical_healing_damage_charges']=getattr(p,'historical_healing_damage_charges',0)
            public['skipped_turns_pending']=p.skipped_turns_pending
            public['leyline_discount']=p.leyline_discount
            public['leyline_effect']=p.leyline_effect
            public['leyline_repeats']=p.leyline_repeats
            public['played_history']=deepcopy(p.played_history)
            public['death_history']=list(p.death_history)
            public['reborn_history']=list(p.reborn_history)
            public.update(full_moon=p.full_moon,life_rewards=p.life_rewards,geddon_draw=p.geddon_draw,sorry_enabled=p.sorry_enabled,shield_hits=p.shield_hits)
            for entity,view in zip(p.board,public['board']):
                view.update(self._stored_view(entity))
                from .historical_eonar import active as eonar_active, remaining as eonar_remaining
                if eonar_active(entity):view['titan_abilities']=list(eonar_remaining(entity))
                if getattr(entity,'rule_state',{}).get('historical_okani_counters'):view['okani_counter_pending']=True
                if getattr(entity,'rule_state',{}).get('historical_gamer_games'):view['gamer_challenges_pending']=len(entity.rule_state['historical_gamer_games'])
                if getattr(entity,'_illusion_possible',False):view['illusion_possible']=True
                if owner==viewer and getattr(entity,'_jandice_illusion',False):view['fragile_illusion']=bool(getattr(entity,'_fragile_illusion',False))
            if owner==viewer:
                public['starting_hand']=[c.card_id for c in getattr(p,'_starting_hand',[])]
                public['scythe_consumed']=[c.card_id for c in getattr(p,'_scythe_consumed',())]
                public['set_aside_cards']=[dict(kind=entry['kind'],cards=[self._card_data(c)['id'] for c in entry['values']]) for entry in getattr(self,'_stored_payloads',{}).values() if entry['owner']==owner and entry['kind'] in ('hand','future')]
            public['discard_history']=list(p.discard_history)
            public['shuffle_history']=deepcopy(p.shuffle_history)
            public['healing_block_expiry_players']=list(p.healing_block_expiry_players)
            public['secondary_power']=deepcopy(p.secondary_power)
            if p.secondary_power is not None:public['secondary_power']['cost']=self._power_cost(owner,secondary=True)
            public['primary_power']=deepcopy(p.primary_power)
            if owner==viewer:public['maestra_disguised']=hasattr(p,'_historical_maestra')
            public['hero_card_id']=p.hero_card_id
            public['ninja_returns']=p.ninja_returns
            public['murloc_summon_bonus']=p.murloc_summon_bonus
            public['elusive']=self._hero_elusive(owner)
            public['quest']=deepcopy(p.quest)
            public['quests_played']=p.quests_played
            public['discoveries_this_turn']=p.discoveries_this_turn
            public['discoveries_total']=p.discoveries_total
            public['payment_effects']=list(p.payment_effects)
            public['hero_healed_turn']=p.hero_healed_turn
            public['imp_upgrades']=p.imp_upgrades
            public['dragons_have_rush']=p.dragons_have_rush
            public['dragons_played_turn']=p.dragons_played_turn
            public['minions_set_cost']=p.minions_set_cost
            public['recruit_attack_bonus']=p.recruit_attack_bonus
            public['recruit_health_bonus']=p.recruit_health_bonus
            public['hero_health_changed_turn']=p.hero_health_changed_turn
            public['historical_boom_mechs_rush']=getattr(p,'historical_boom_mechs_rush',False)
            public['historical_jaina_elementals_lifesteal']=getattr(p,'historical_jaina_elementals_lifesteal',False)
            public['minion_played_this_turn']=p.minion_played_this_turn
            public['minion_played_last_turn']=p.minion_played_last_turn
            public['imbue_count']=p.imbue_count
            public['hamuul_active']=p.hamuul_active
            public['hamuul_spells']=p.hamuul_spells
            public['undead_played_this_turn']=p.undead_play_turn==self.turn
            public['spell_repeat_charges']=p.spell_repeat_charges
            public['historical_mage_spell_damage']=getattr(p,'historical_mage_spell_damage',0)
            public['historical_mage_sidequests']=deepcopy(getattr(p,'historical_mage_sidequests',[]))
            public['historical_permanent_power_damage']=getattr(p,'historical_permanent_power_damage',0)
            public['historical_power_damage_total']=getattr(p,'historical_power_damage_total',0)
            public['historical_power_armor']=getattr(p,'historical_power_armor',0)
            public['historical_power_attack']=getattr(p,'historical_power_attack',0)
            public['historical_spell_mana_spent']=getattr(p,'historical_spell_mana_spent',0)
            public['historical_holy_mana_paid']=getattr(p,'historical_holy_mana_paid',0)
            public['historical_love_stacks']=getattr(p,'historical_love_stacks',0)
            public['historical_alibi_active']=p.turns_taken<getattr(p,'historical_alibi_until',-1)
            public['historical_aimed_shot_bonus']=getattr(p,'historical_aimed_shot_bonus',0)
            public['historical_finish_auras']=deepcopy(getattr(p,'historical_finish_auras',[]))
            public['historical_stormwind_draw_discount']=getattr(p,'historical_stormwind_draw_discount',0)
            public['historical_stormwind_tamsin']=getattr(p,'historical_stormwind_tamsin_uid',None) is not None
            public['historical_stormwind_tavish']=getattr(p,'historical_stormwind_tavish',False)
            public['historical_stormwind_power_targets']=getattr(p,'historical_stormwind_power_targets',False)
            public['historical_stormwind_power_zero']=getattr(p,'historical_stormwind_zero_generation',None)==getattr(p,'historical_power_generation',0)
            public['historical_zerg_rush_this_turn']=getattr(p,'historical_zerg_rush_turn',None)==self.turn
            public['historical_inventor_auras']=deepcopy(getattr(p,'historical_inventor_auras',[]))
            public['historical_deputization_auras']=deepcopy(getattr(p,'historical_deputization_auras',[]))
            public['historical_conductivity_active']=getattr(p,'historical_conductivity_turn',None)==self.turn
            from .historical_demon_portal import PortalDeck
            public['demon_portal']=dict(active=True,bonus=p.deck.portal_bonus) if isinstance(p.deck,PortalDeck) else None
            public['historical_lightning_discounts']=deepcopy(getattr(p,'historical_lightning_discounts',[]))
            public['historical_friendly_target_spell_count']=getattr(p,'historical_friendly_target_spell_count',0)
            public['historical_healing_done_total']=getattr(p,'historical_healing_done_total',0)
            public['historical_copycat_pending']=getattr(p,'historical_copycat_pending',0)
            public['historical_protoss_spells']=getattr(p,'historical_protoss_spells',0)
            public['historical_protoss_discount']=getattr(p,'historical_protoss_discount',0)
            public['historical_spore_count']=len(getattr(p,'historical_spore_outcomes',()))
            public['historical_next_concoction_free']=bool(getattr(p,'historical_next_concoction_free',False))
            public['historical_zerg_attack_bonus']=getattr(p,'historical_zerg_attack_bonus',0)
            public['historical_cthun_pieces']=list(getattr(p,'historical_cthun_pieces',()))
            public['whizbang_quests']=deepcopy(getattr(p,'whizbang_quests',[]))
            public['brukan_spells_twice']=bool(getattr(p,'historical_brukan_spells_twice',False))
            public['historical_double_battlecries']=bool(getattr(p,'historical_double_battlecries',False))
            public['virnaal_active']=getattr(p,'historical_virnaal_turn',None)==self.turn
            public['end_repeat_turns']=[max(0,end-p.turns_taken+1) for end in p.end_repeat_expiries]
            public['scheduled_effects']=[dict(source_card_id='ETC_387',hidden=True) if owner!=viewer and e.get('historical_private_roots') else self._scheduled_effect_view(e,owner) for e in p.scheduled_effects]
            public['eternal_life']=p.eternal_life
            public['ashalon_adaptations']=list(p.ashalon_adaptations)
            public['gorishi_stacks']=p.gorishi_stacks
            public['damaged_characters_turn']=len(p.damaged_characters_turn)
            public['rule_counters']={key:deepcopy(getattr(p,key)) for key in ('fel_spells_cast','friendly_attacks','last_paid_cost','spell_damage_turn','hero_damage_taken_turn','hero_damage_events_turn','minions_died_turn','spells_cast_turn','overloaded_total','healing_done_turn','permanent_healing_bonus','permanent_end_damage','spells_turn','spells_previous')}
            public['kindred_history']={key:sorted(getattr(p,key)) for key in ('played_tribes','played_schools','previous_tribes','previous_schools')}
            if owner!=viewer:
                # Keep separately recorded public casts: subtracting hidden
                # schools would itself reveal which public school was removed.
                public['historical_school_counts']=dict(getattr(p,'_historical_public_school_counts',{}))
                public['historical_spell_schools']=sorted(public['historical_school_counts'])
                for entry in public['played_history']:
                    if entry['card_id'] in SECRETS:entry['card_id']='SECRET'
                for key in ('spells_turn','spells_previous'):
                    public['rule_counters'][key]=['SECRET' if cid in SECRETS else cid for cid in getattr(p,key)]
                # Schools derived from a hidden Secret are hidden too. Expose
                # only schools of publicly identified spells, with an explicit
                # incompleteness marker rather than leaking the actual set.
                for spell_key,school_key in (('spells_turn','played_schools'),('spells_previous','previous_schools')):
                    spells=getattr(p,spell_key)
                    public['kindred_history'][school_key]=sorted({self.cards[cid]['spellSchool'] for cid in spells
                        if cid not in SECRETS and self.cards[cid].get('spellSchool')})
                    public['kindred_history'][school_key+'_hidden']=any(cid in SECRETS for cid in spells)
            public['undead_died_since_last_turn']=self._choicegen_undead_died(owner)
            public['next_power_increase']=p.next_power_increase
            public['next_power_cost_effects']=deepcopy(p.next_power_cost_effects)
            public['hero_power_cost']=self._power_cost(owner)
            public['timed_cost_increases']=deepcopy(p.timed_cost_increases)
            if owner==viewer:
                public['etc_band']=[dict(card_id=c.card_id,uid=c.uid) for c in getattr(p,'_historical_etc_band',())]
                public['nonstarting_cards_played']=getattr(p,'_nonstarting_plays',0)
                public['secrets']=[c.card_id for c in p.secrets]
                public['cost_effects']=deepcopy(p.cost_effects)
        if self.pending_choice:
            from .historical_holmes import public_clue
            observation['pending_choice']=(
                dict(owner=self.pending_choice['owner'],kind=self.pending_choice['kind'],
                     **public_clue(self.pending_choice),
                     **({'approximate':bool(self.pending_choice.get('approximate',False))} if self.pending_choice['kind']=='historical_zephrys' else {}),
                     **({'remaining':self.pending_choice['remaining']} if self.pending_choice['kind'] in ('rewind','herald_cataclysm') else {}),
                     **({'picks':list(self.pending_choice['picks'])} if self.pending_choice['kind']=='herald_cataclysm' else {}),
                     options=[dict(card_id=o['card_id'],**{key:o[key] for key in ('label','uid','dark_gift','attack','health','cost') if key in o}) for o in self.pending_choice['options']])
                if viewer==self.pending_choice['owner']
                                           else {'owner':self.pending_choice['owner'],'waiting':True})
        else: observation['pending_choice']=None
        observation['card_movements']=dict(getattr(self,'historical_card_movements',{}))
        for c in self.players[viewer].hand:
            public=next(h for h in observation['players'][viewer]['hand'] if h['uid']==c.uid)
            public['cost']=self._cost(c,viewer)
            public['payment_kind']=self._payment_kind(c,viewer)
            if hasattr(c,'_historical_bottle_amount'):public['bottle_amount']=c._historical_bottle_amount
            if hasattr(c,'_historical_suitcase_cards'):public['packed_cards']=[dict(card_id=card.card_id,cost=self._cost(card,viewer)) for card in c._historical_suitcase_cards]
            if hasattr(c,'_historical_mirror_mode'):public['mirror_kind']=c._historical_mirror_mode
            if getattr(c,'rule_state',{}).get('historical_aegwynn_stacks',0):public['aegwynn_stacks']=c.rule_state['historical_aegwynn_stacks']
            if c.card_id=='JAM_037t':public['rock_damage']=getattr(c,'rule_state',{}).get('historical_rock_damage',8)
            if c.card_id=='VAC_955t':public['summon_cost']=getattr(c,'rule_state',{}).get('historical_cheese_level',1)
            if getattr(c,'rule_state',{}).get('historical_shaffar_beacon'):public['shaffar_beacon']=True
            if c.card_id=='NX2_033':public['thaddius_parity']=getattr(c,'rule_state',{}).get('historical_thaddius_parity',1)
            if self._card_data(c)['type']=='MINION':
                public['hand_damage']=getattr(c,'rule_state',{}).get('historical_hand_damage',0)
                public['max_health']=self._card_stat(c,'health',viewer)
                public['health']=public['max_health']-public['hand_damage']

            public['cost_delta']=getattr(c,'cost_delta',0)
            public['temporary']=self._is_temporary(c)
            public['drawn_this_turn']=getattr(c,'_drawn_turn',None)==self.turn
            lock=getattr(c,'rule_state',{}).get('locked_until_play')
            public['plays_until_unlocked']=max(0,lock['count']-len(self.players[viewer].played_history)) if lock and lock['owner']==viewer else 0
            if c.card_id=='CATA_206':public['bonus_effects']=list(self._held_bonus_pair(c))
            public['follow_effects']=deepcopy([e for e in getattr(c,'_follow_effects',[]) if e['end'] is None or e['end']>=self.turn])
            public['started_in_deck']=self._started_in_deck(c,viewer)
            public['copied_from_opponent']=self._copied_from_opponent(c,viewer)
            public['entered_hand_this_turn']=getattr(c,'_hand_entry_turn',None)==self.turn
            if hasattr(c,'_historical_retained_minion'):
                public['retained_keywords']=sorted(c._historical_retained_minion.keywords)
                public['retained_death_effects']=deepcopy(c._historical_retained_minion.attached_death_effects)
            for field in ('spell_damage_bonus','growing_discounts','play_lock','rule_state'):
                if hasattr(c,field):
                    from .visible_rules import plain_rules
                    public[field]=plain_rules(getattr(c,field))
            public.update(self._stored_view(c))
            public['toki_return_tasks']=[dict(task=i,remaining=len(t['required']-t['played'])) for i,t in enumerate(getattr(self.players[viewer],'_toki_tasks',[])) if c.uid in t['required']-t['played']]
            public['temporary_cost_discounts']=deepcopy(getattr(c,'temporary_cost_discounts',[]))
            if hasattr(c,'set_cost'):public['set_cost']=c.set_cost
            if self.cards[c.card_id]['type']=='MINION':
                from .selectors import tribes
                public['races']=sorted(tribes(self._card_data(c)))
                public['attack']=self._card_stat(c,'attack',viewer)
                public['health']=self._card_stat(c,'health',viewer)
            from .physical_choices import branches as physical_branches
            visible_branches=physical_branches(c,CHOICES)
            if visible_branches:public['choices']=[b[0] for b in visible_branches]
        # A played secret's identity is hidden even though its play is public.
        for event in observation['events']:
            if event.get('player')!=viewer and event.get('card') in ('ETC_387','ETC_387t'):
                event.pop('branch',None)
            if event.get('event') in ('play','internal_spell_cast','internal_spell_complete') and event.get('player')!=viewer and event.get('card') in SECRETS:
                event['card']='SECRET'
        return observation
