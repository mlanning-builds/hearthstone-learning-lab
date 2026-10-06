"""Experimental all-class rules extension; NOT complete Standard.

User-run validation is pending. Unsupported decks fail before state creation.
The original engine and saved training fingerprints are preserved.
"""
from dataclasses import dataclass, field, asdict, replace
from copy import deepcopy
import random
from collections import deque
from .selectors import has_tribe, has_any_tribe, has_school
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
    mana_capacity: int = 10
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


class Game(ExceptionalFinish,MinionForge,CustomBuilders,Morchie,RandomTargets,Counterfeits,DragonSoul,Titanographer,RemainingSetup,QuestFamilies,Muradin,Azshara,Gelbin,Broxigar,Garona,Rafaam,FabledEffects,StoredObligations,LearnedSpells,ZoneTriggers,TemporaryControl,EvolvingLocations,ColossalBodies,Herald,ColossalEntries,FutureSummons,AutomaticCasting,HandInvestigations,TinyPal,HealingReplacement,StatRules,Genn,Replacements,TurnDeadlines,InfinityEffects,DeckSetup,StartingRules,Maps,Leylines,ImbueConsumers,RewindGenerators,Transformations,DarkGiftGenerators,EntityEffects,LastingRules,StoredCards,DarkGifts,Rewind,Shatter,Imbue, Permanents, Dreams, Quests, HeroPowers, Discovery, GenerationEffects, ChoiceGenerators,TribalGroups, AlternatePlay, ForcedCombat, OnDraw, SpellCasting, EffectReplay, Prepare, TemporaryCards, HeldUpgrades, Provenance, Dormancy, BonusEffects, DrawEvents, LocalFamily, Batch60, PersistentEffects, ComposedEffects, SharedBatch30, SummonEvents, EntryTrace, Secrets, BatchEffects, Systems, Lifecycle, Resolution, Locations, Battlefield, LegacyGame):
    VERSION='all-class-experimental-0.15-candidate'

    def __init__(self,decks,seed=0,first_player=0,max_turns=89,record=True):
        if len(decks)!=2 or first_player not in (0,1): raise ValueError('Provide two decks and first player 0 or 1')
        if type(max_turns) is not int or not 1<=max_turns<=89: raise ValueError('Invalid turn limit')
        self.cards=registry()
        from .fabled_decks import expand_bundle_ids
        try:decks=[replace(deck,cards=expand_bundle_ids(deck.cards)) for deck in decks]
        except ValueError as exc:raise UnsupportedCard(str(exc)) from exc
        for deck in decks:
            errors=validate(deck,self.cards)
            if errors: raise UnsupportedCard('; '.join(errors))
        self.seed=seed; self.rng=random.Random(seed); self.uid=0; self.players=[]
        for deck in decks:
            shuffled=list(deck.cards); self.rng.shuffle(shuffled)
            physical=[]
            for cid in shuffled:
                c=Card(self._new_id(),cid);data=self.cards[cid]
                c._starting_owner=len(self.players)
                c._starting_identity=data.get('countAsCopyOfDbfId',data.get('dbfId',cid))
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
        for p in self.players:p.starting_hero_class=p.hero_class
        self._prepare_constructed_decks(decks)
        self._essence_setup()
        self._remaining_setup(decks)
        first_player=self._aya_setup()
        self._starting_rules()
        for owner in (first_player,1-first_player):
            self._imbue_start_game(owner)
            self._quest_opening_hand(owner)

    def _summon(self,owner,cid,position=-1,attack_bonus=0,health_bonus=0,expires=False,*,copy_from=None,entry_origin="unspecified",entry_site=None,entry_zone=None,entry_source=None,dormant_turns=None):
        count=self._card_summon_repetitions(owner,entry_origin)
        first=self._summon_one(owner,cid,position,attack_bonus,health_bonus,expires,copy_from=copy_from,entry_origin=entry_origin,entry_site=entry_site,entry_zone=entry_zone,entry_source=entry_source,dormant_turns=dormant_turns)
        if first is not None:
            for index in range(1,min(count,1+max(0,7-len(self.players[owner].board)))):
                self._summon_one(owner,cid,position if position<0 else position+index,attack_bonus,health_bonus,expires,copy_from=copy_from,entry_origin=entry_origin,entry_site=entry_site,entry_zone=entry_zone,entry_source=entry_source,dormant_turns=dormant_turns)
        return first

    def _summon_one(self,owner,cid,position=-1,attack_bonus=0,health_bonus=0,expires=False,*,copy_from=None,entry_origin="unspecified",entry_site=None,entry_zone=None,entry_source=None,dormant_turns=None):
        self._colossal_preflight(cid,owner=owner,copy_from=copy_from,dormant_turns=dormant_turns)
        self._herald_entry_preflight(owner,cid,copy_from)
        self._trace_phase("entry_attempt", origin=entry_origin, site=entry_site, owner=owner, card_id=cid, zone=entry_zone, source_uid=getattr(entry_source,"uid",None), source_card_id=getattr(entry_source,"card_id",None))
        if cid=='JAIL_501' and copy_from is None and entry_origin in ('play','recruit') and entry_zone=='hand':
            value=getattr(entry_source,'rule_state',{}).get('picklock_value',max(1,self.players[owner].mana))
            attack_bonus+=value-1;health_bonus+=value-1
        m = self._create_minion(owner,cid,position,attack_bonus,health_bonus,expires,copy_from=copy_from,dormant_turns=dormant_turns)
        if m is not None and m.card_id=='JAIL_330':m._champion_stats=(m.attack-m.aura_attack,m.max_health-m.aura_health)
        if m is not None and copy_from is None and isinstance(entry_source,Card) and hasattr(entry_source,'base_stat_override'):
            from .base_stats import carry_base_stats
            if not self.players[owner].crystal_core:
                old=self.cards[cid];a,h=entry_source.base_stat_override
                self._adjust_minion_attack(m,a-old['attack']);m.max_health+=h-old['health'];m.health+=h-old['health']
            carry_base_stats(entry_source,m)
        if m is not None and entry_origin in ('play','recruit') and isinstance(entry_source,Card):
            self._carry_origin(entry_source,m)
        if (m is not None and copy_from is None and isinstance(entry_source,Card)
                and entry_zone in ('hand','deck') and entry_source.card_id==cid):
            self._held_bonus_entry(m,entry_source)
            self._dark_entry(m,entry_source)
            self._stored_entry(m,entry_source)
            self._forge_entry(m,entry_source)
        if m is not None and entry_origin=='reborn':self.players[owner].reborn_history.append(cid)
        if m is not None:
            self._log('summon',player=owner,card=cid,entity=m.uid,
                      position=self.players[owner].board.index(m))
        if m is not None:
            if cid=='CAP_400t2t':
                bonus=2*self.players[owner].imp_upgrades
                if bonus:self._buff(m,bonus,bonus)
            self._colossal_enter(m)
            self._herald_on_summon(m)
            self._capture_summon_event(m, entry_origin)
        self._trace_entity("entry_result", m, origin=entry_origin, site=entry_site, owner=owner, card_id=cid, success=m is not None)
        return m

    def _create_minion(self,owner,cid,position=-1,attack_bonus=0,health_bonus=0,expires=False,*,copy_from=None,dormant_turns=None):
        if dormant_turns is not None and (type(dormant_turns) is not int or dormant_turns<=0):
            raise UnsupportedCard('Dormant duration must be a positive integer')
        if cid in PERMANENT_IDS:raise UnsupportedCard('Permanent requires explicit placement: '+cid)
        if cid not in self.cards or self.cards[cid]['type']!='MINION': raise UnsupportedCard(cid)
        p=self.players[owner]
        if len(p.board)>=7: return None
        expires=expires or cid=='HERO_11bpt'
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
            for private_field in ("_infinity_cost_receipts","remembered_draw","secret_discard","_bound_card","_bound_minion","_devoured_cards","_fragile_illusion","_illusion_possible"):
                if hasattr(copy_from,private_field):setattr(m,private_field,deepcopy(getattr(copy_from,private_field)))
            if hasattr(copy_from,'_muradin_hammer'):
                held=deepcopy(copy_from._muradin_hammer)
                held['card']=self._copy_card(copy_from._muradin_hammer['card'],source_owner=copy_from.owner if copy_from.owner!=owner else None)
                m._muradin_hammer=held
        if position<0: position=len(p.board)
        m.dormant = copy_from.dormant if copy_from is not None else INITIAL_DORMANCY.get(cid, 0)
        if dormant_turns is not None:m.dormant=dormant_turns
        m._colossal_stat_snapshot=(m.attack,m.max_health)
        p.board.insert(position,m)
        self._refresh_auras()
        if copy_from is not None:
            m.health-=copied_damage
            self._refresh_auras()
        return m

    def _add(self,owner,cid):
        self._quest_deliver_ready(owner)
        if cid not in self.cards: raise UnsupportedCard('Generated card not implemented: '+cid)
        p=self.players[owner]
        if len(p.hand)>=10: self._log('burn_generated',player=owner,card=cid)
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
        return aura+p.temporary_attack+((p.armor if p.weapon['card_id']=='CORE_LOOT_044' else p.weapon['attack']) if p.weapon else 0)

    def _spell_damage(self,owner):
        from .cards import SPELL_DAMAGE_VALUES, CONDITIONAL_SPELL_DAMAGE
        total=0
        for m in self.players[owner].minions:
            if m.silenced:continue
            total+=SPELL_DAMAGE_VALUES.get(m.card_id,self.cards[m.card_id].get('spellDamage',0))
            rule=CONDITIONAL_SPELL_DAMAGE.get(m.card_id)
            if rule:
                condition,amount=rule
                if condition=='damaged' and m.health<m.max_health:total+=amount
        return total

    def _visible_targets(self,owner,magic=False):
        return [self.hero_id(player) for player in (0,1) if (player==owner or not self._hero_immune(player)) and not (magic and self._hero_elusive(player))]+[m.uid for p in self.players for m in p.minions
            if not (m.owner!=owner and bool({'STEALTH','IMMUNE'} & self._effective_keywords(m))) and not (magic and 'ELUSIVE' in self._effective_keywords(m))]

    def _targets_for(self,cid,owner,mode_override=None):
        data=self.cards[cid]
        if cid=='CATA_496' and len(self.players[owner].board)>=7:return []
        mode=mode_override if mode_override is not None else (RULES[cid][0] if cid in RULES else TARGETS.get(cid,'none'))
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
            if mode=='enemy_character': return not friendly
            if m is None: return False
            if mode=='minion': return True
            if mode=='enemy_taunt': return not friendly and 'TAUNT' in self._effective_keywords(m)
            if mode=='small_attack_minion': return m.attack<=3
            if mode=='large_minion': return m.attack>=7
            if mode=='legendary_minion': return self.cards[m.card_id].get('rarity')=='LEGENDARY'
            if mode=='tribal_enemy_minion': return not friendly and has_any_tribe(self.cards[m.card_id])
            if mode=='damaged_minion': return m.health<m.max_health
            if mode=='enemy_minion': return not friendly
            if mode=='friendly_deathrattle':return friendly and bool(self._death_operations(m))
            if mode=='friendly_minion': return friendly
            if mode=='friendly_wisp':return friendly and self.cards[m.card_id]['name']=='Wisp'
            if mode=='enemy_minion_source_health':
                return not friendly
            if mode=='friendly_dragon':return friendly and has_tribe(self.cards[m.card_id],'DRAGON')
            if mode=='friendly_beast': return friendly and has_tribe(self.cards[m.card_id],'BEAST')
            if mode=='friendly_undead': return friendly and has_tribe(self.cards[m.card_id],'UNDEAD')
            if mode=='undamaged_minion': return m.health==m.max_health
            if mode=='damaged_enemy_minion': return not friendly and m.health<m.max_health
            raise UnsupportedCard('Target mode: '+mode)
        result=[uid for uid in targets if valid(uid)]
        return result or ([0] if data['type']=='MINION' else [])

    def _cost(self,card,owner):
        p=self.players[owner]; cid=card.card_id
        cost=max(1,p.mana) if cid=='JAIL_501' else self.cards[cid]['cost']
        if cid in ('CORE_BT_801','BT_801') and p.hand and card.uid in (p.hand[0].uid,p.hand[-1].uid): cost=1
        elif cid=='CORE_NEW1_022': cost-=p.weapon['attack'] if p.weapon else 0
        elif cid=='CATA_308' and any(self.cards[m.card_id].get('rarity')=='LEGENDARY' for m in p.minions): cost=1
        if cid=='JAIL_204' and not any(player.minions for player in self.players):cost=2
        if cid=='TIME_022' and any(m.dormant for player in self.players for m in player.all_minions):cost-=4
        if cid=='DINO_409':cost-=getattr(p,'_nonstarting_plays',0)
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
        if cid=='END_033' and any(c is not card and has_tribe(self.cards[c.card_id],'DRAGON') for c in p.hand):cost-=3
        if cid=='TLC_819' and {'HOLY','SHADOW'}<=p.spell_schools_this_turn:cost=1
        if self._kindred(cid,owner):
            from .kindred import repetitions
            cost-={'TLC_366':2,'TLC_600':3,'TLC_816':2}.get(cid,0)*repetitions(self,owner,cid,True)
        if self.cards[cid]['type']=='MINION' and p.minions_set_cost is not None:cost=p.minions_set_cost
        if has_tribe(self.cards[cid],'DRAGON') and p.dragons_played_turn==0 and self._active('EDR_844',owner):cost=1
        if self._medivh_free(cid,owner):cost=0
        cost=getattr(card,'set_cost',cost)
        if getattr(card,'_infinity_cost_layers',[]):
            from .infinity import INFINITY
            cost=INFINITY
        cost+=getattr(card,'cost_delta',0)
        from .herald import DEATHWINGS
        if cid in DEATHWINGS:cost-=p.deathwing_discount
        if cid in LEYLINES:cost-=p.leyline_discount
        cost-=sum(e['amount'] for e in getattr(card,'temporary_cost_discounts',[]) if self.turn<=e['end'])
        for effect in p.cost_effects:
            if self._discount_matches(effect,card):
                cost=effect['set_cost'] if 'set_cost' in effect else cost-effect['amount']
        cost-=self._azure_discount(owner,cid)
        cost-=self._mug_discount(owner,cid)
        # Live hand adjacency, not a permanent cost enchantment. Sabotage's
        # own surcharge caps at ten; unrelated taxes may still exceed ten.
        index=next((i for i,c in enumerate(p.hand) if c is card),None)
        if index is not None:
            surcharge=sum(p.hand[i].card_id=='CATA_186t' for i in (index-1,index+1) if 0<=i<len(p.hand))
            if surcharge and cost<10:cost=min(10,cost+surcharge)
        for effect in p.timed_cost_increases:
            if effect['start'] <= self.turn <= effect['end'] and (
                    effect['selector']=='ALL' or self._discount_matches(effect,card)):
                cost+=effect['amount']
        if self.cards[cid]['type']=='MINION':
            cost+=2*sum(m.card_id=='JAIL_890' and not m.silenced and m.health>0 for player in self.players for m in player.minions)
        return max(0,cost)

    def _attack_targets(self,m=None):
        enemy=self.players[1-self.current]
        visible=[x for x in enemy.minions if not {'STEALTH','IMMUNE'} & self._effective_keywords(x)]
        taunts=[] if self._active('CORE_BT_187',self.current) else [x.uid for x in visible if 'TAUNT' in self._effective_keywords(x)]
        targets=taunts or ([] if self._hero_immune(1-self.current) else [self.hero_id(1-self.current)])+[x.uid for x in visible]
        if m and m.summoned_turn==self.turn and 'CHARGE' not in self._effective_keywords(m):
            if 'RUSH' not in self._effective_keywords(m): return []
            targets=[t for t in targets if t>0]
        if m and 'CANT_ATTACK_HERO' in self._effective_keywords(m):
            targets=[t for t in targets if t>0]
        if m is None and self.players[self.current].weapon and self.players[self.current].weapon['card_id'] in ('CORE_LOOT_044','END_012'):
            targets=[t for t in targets if t>0]
        return targets

    def _hand_actions(self,owner):
        """Owner-scoped hand eligibility without switching turn or choice state."""
        p=self.players[owner];actions=[]
        for c in p.hand:
            d=self.cards[c.card_id]
            if c.card_id=='CORE_RLK_567':continue
            if 'TRADEABLE' in d.get('mechanics',[]) and p.mana>=1 and p.deck:
                actions.append(Action('trade',source=c.uid))
            if self._can_prepare(c,owner):actions.append(Action('prepare',source=c.uid))
            lock=getattr(c,'play_lock',None)
            if lock and lock['owner']==owner and p.turns_taken<lock['until']:continue
            played_lock=getattr(c,'rule_state',{}).get('locked_until_play')
            if played_lock and played_lock['owner']==owner and len(p.played_history)<played_lock['count']:continue
            if not self._can_pay(c,owner):continue
            if c.card_id in EITHER_SIDE:
                for side in (0,1):
                    board=self.players[owner if side==0 else 1-owner].board
                    if len(board)<7:actions.extend(Action('play',c.uid,0,pos,() if side==0 else (1,)) for pos in range(len(board)+1))
                continue
            if d['type'] in ('MINION','LOCATION') and len(p.board)>=7:continue
            if self._is_quest(c.card_id) and (p.quest is not None or len(p.secrets)>=5):continue
            if c.card_id in SECRETS and (len(p.secrets)+self._quest_slots(owner)>=5 or any(secret.card_id==c.card_id for secret in p.secrets)): continue
            positions=range(len(p.board)+1) if d['type'] in ('MINION','LOCATION') else [-1]
            branches=CHOICES.get(c.card_id)
            if branches:
                if self._active('CORE_OG_044',owner) or getattr(c,'rule_state',{}).get('choose_both'):
                    modes=[b[1] for b in branches if b[1]!='none']
                    if c.card_id=='EDR_813' and p.corpses<2:modes=[]
                    # Current combined choices have at most one target restriction.
                    mode=modes[0] if modes else 'none'
                    for target in self._targets_for(c.card_id,owner,mode):
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
        actions.extend(self._location_actions())
        actions.extend(self._permanent_actions())
        cost=self._power_cost(self.current)
        if not p.power_used and p.mana>=cost:
            k=p.hero_class
            if p.primary_power is not None:
                actions.extend(Action('power',target=t) for t in self._replacement_power_targets(self.current))
            elif k in ('MAGE','PRIEST'):
                actions.extend(Action('power',target=t) for t in self._visible_targets(self.current,magic=True))
            elif k in ('PALADIN','DEATHKNIGHT'):
                if len(p.board)<7: actions.append(Action('power'))
            elif k=='SHAMAN':
                if len(p.board)<7 and set(TOTEMS)-{m.card_id for m in p.minions}: actions.append(Action('power'))
            else: actions.append(Action('power'))
        if p.secondary_power is not None and p.secondary_power['card_id'] not in ('JAIL_800hp1','JAIL_800hp2') and not p.secondary_power['used'] and p.corpses>=self._power_cost(self.current,secondary=True):
            actions.extend(Action('power',target=t,choices=(1,)) for t in self._visible_targets(self.current,magic=True) if t>0)
        for m in p.minions:
            keywords=self._effective_keywords(m)
            limit=4 if 'MEGA_WINDFURY' in keywords else 2 if 'WINDFURY' in keywords else 1
            if m.frozen_until<0 and m.attacks<limit and m.attack>0 and 'CANT_ATTACK' not in keywords:
                actions.extend(Action('attack',m.uid,t) for t in self._attack_targets(m))
        if p.frozen_until<0 and p.hero_attacks<self._hero_attack_limit(self.current) and self._hero_attack(self.current)>0:
            actions.extend(Action('attack',self.hero_id(self.current),t) for t in self._attack_targets())
        return actions

    def step(self,action):
        if action not in self.legal_actions(): raise ValueError('Illegal action; state unchanged')
        # Preserve the full state, including RNG, if an unexpected effect fails.
        before=deepcopy(self.__dict__)
        try:
            self._trace_phase("action_begin", action=action.kind, actor=self.current)
            actor=self.current; self.history.append(dict(player=actor,action=asdict(action)))
            action=self._random_action_target(action)
            if action.kind=='mulligan': self._mulligan(action.choices)
            elif action.kind=='end': self._end_turn()
            elif action.kind=='power':
                if action.choices==(1,):self._power(action.target,secondary=True)
                else:self._power(action.target)
            elif action.kind=='attack': self._attack(action.source,action.target)
            elif action.kind=='play': self._play(action)
            elif action.kind=='trade': self._trade(action.source)
            elif action.kind=='prepare': self._prepare_card(action.source)
            elif action.kind=='activate':
                if self._permanent_entity(action.source) is not None:self._activate_permanent(action)
                else:self._activate_location(action)
            elif action.kind=='choose': self._resolve_choice(action.choices[0])
            else: raise ValueError('Unknown action')
            self._settle(); self._complete_requested_turn_end(); self._settle(); self.assert_invariants()
            self._trace_phase("action_end", action=action.kind, actor=actor, terminal=self.terminal, waiting_choice=self.pending_choice is not None)
            return self.rewards(),self.terminal
        except Exception:
            self.__dict__.clear(); self.__dict__.update(before)
            raise

    def _power_cost(self,owner,*,secondary=False):
        p=self.players[owner]
        replacement_cost=self.cards[p.secondary_power['card_id']]['cost'] if secondary else self._replacement_power_cost(owner)
        cost=replacement_cost if replacement_cost is not None else (1 if p.hero_class=='DEMONHUNTER' else 2)
        from .cards import HERO_POWER_HAND_COST_AURAS
        for cid,(maximum,cost_value) in HERO_POWER_HAND_COST_AURAS.items():
            if len(p.hand)<=maximum and self._active(cid,owner):cost=cost_value
        for effect in p.next_power_cost_effects:
            cost=effect['amount'] if effect['kind']=='set' else cost+effect['amount']
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
        self._power_frame=dict(owner=self.current,phase='effects')
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
            self._b60_spend_mana(owner,cost)
        p.next_power_increase=0
        p.next_power_cost_effects.clear()
        self._log('hero_power',player=owner,hero_class=k,target=target)
        if secondary:
            self._start_power_effects(owner,(('buff',3,0),)*self._trigger_repetitions(owner),target=target)
            return
        if self._trigger_repetitions(owner)>1:
            operations=self._repeated_power_operations(owner)*2
            if p.primary_power and p.primary_power['card_id'] in ('TLC_632t','TLC_632t2'):
                operations+=(('replacement_power_consumed',p.primary_power.get('uid')), )
            self._start_power_effects(owner,operations,target=target)
            return
        if self._replacement_power_effect(owner,target):return
        if k=='WARRIOR': self._gain_armor(owner,2)
        elif k=='HUNTER': self._damage(self.hero_id(1-owner),2,damage_source=None,damage_owner=owner)
        elif k=='MAGE': self._damage(target,1,damage_source=None,damage_owner=owner)
        elif k=='PRIEST': self._heal(target,2,healer=owner)
        elif k=='DRUID': p.temporary_attack+=1; self._gain_armor(owner,1)
        elif k=='DEMONHUNTER': p.temporary_attack+=1
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
        if physical_card is not None and physical_card.card_id != cid:
            raise ValueError('Equipped physical card identity does not match weapon')
        self._break_weapon(owner)
        self.players[owner].equipped_card = physical_card if physical_card is not None else Card(self._new_id(),cid)
        self.players[owner].equipped_card.attack_bonus=attack_bonus
        self.players[owner].weapon=dict(card_id=cid,attack=max(0,d['attack']+attack_bonus),durability=(d.get('durability') or d['health'])+self.players[owner].equipped_card.health_bonus)
        self._log('equip',player=owner,card=cid)

    def _buff_weapon(self,owner,attack=0,durability=0):
        p=self.players[owner]
        if not p.weapon:return
        p.weapon['attack']+=attack
        p.weapon['durability']+=durability
        if p.equipped_card is not None:
            p.equipped_card.attack_bonus+=attack
            p.equipped_card.health_bonus+=durability

    def _freeze(self,target):
        if self._fire_immune_target(target):return
        if target>0 and self._dormant_entity(target) is not None and self._dormant_entity(target).dormant:return
        if not target: return
        if target<0:
            owner=-target-1; entity=self.players[owner]; attacked=entity.hero_attacks>0; sick=False
        else:
            entity=self._find(target); owner=entity.owner; attacked=entity.attacks>0
            sick=entity.summoned_turn==self.turn and not {'CHARGE','RUSH'}&self._effective_keywords(entity)
        thaw=self.turn+1 if owner!=self.current else self.turn+(2 if attacked or sick else 0)
        entity.frozen_until=max(entity.frozen_until,thaw)
        self._log('freeze',target=target,until=entity.frozen_until)

    def _attack(self,source,target,*,forced=False):
        target=self._random_attack_target(source,target)
        owner=self._find(source).owner if source>0 else -source-1; p=self.players[owner]
        listeners=self._event_listeners();window=self._open_attack_window(source)
        try:
            if self._secret_event('attack',owner,source=source,target=target):return
            self._combat_sequence_depth=getattr(self,'_combat_sequence_depth',0)+1
            try:
                if source>0:
                    self._rule_events.append(('before_minion_attack',dict(owner=owner,source=source,target=target,stealthed=self._b60_pre_attack(source)),self._event_listeners()))
                    self._drain_events()
                    if self.terminal:return
                    if not any(m.uid==source and m.health>0 for m in p.minions):return
                    if target>0 and not any(m.uid==target and m.health>0 for player in self.players for m in player.minions):return
                if forced:self._resolve_combat(source,target,listeners,forced=True)
                else:self._resolve_combat(source,target,listeners)
            finally:
                self._combat_sequence_depth-=1
                self._close_attack_window(window)
                self._settle()
        finally:
            self._close_attack_window(window)

    def _resolve_combat(self,source,target,listeners,*,forced=False,excess_to_hero=False):
        attack_window=next((window for window in reversed(getattr(self,'_attack_windows',[]))
                            if window['source']==source),None)
        owner=self._find(source).owner if source>0 else -source-1; p=self.players[owner]
        attacker=self._find(source) if source>0 else None
        weapon_id=p.weapon['card_id'] if p.weapon else None
        weapon_uid=getattr(p.equipped_card,'uid',None)
        attack=self._outgoing_tribal_damage(attacker,attacker.attack) if attacker else self._hero_attack(owner)
        defender=self._find(target) if target>0 else None
        # A hero's weapon is active only on that hero's own turn.
        retaliation=self._outgoing_tribal_damage(defender,defender.attack) if defender else 0
        sk=self._effective_keywords(attacker) if attacker else set(self.cards[p.weapon['card_id']].get('mechanics',[])) if p.weapon else set()
        if attacker is None and p.hero_lifesteal_until>=self.turn:sk.add('LIFESTEAL')
        if attacker is None and p.weapon and p.weapon.get('poisonous_until',-1)>=self.turn:sk.add('POISONOUS')
        dk=self._effective_keywords(defender) if defender else set()
        neighbors=[]
        if attacker:
            pos=p.board.index(attacker);neighbors=[p.board[i].uid for i in (pos-1,pos+1) if 0<=i<len(p.board)]
        cleave=[]
        if attacker and not attacker.silenced and attacker.card_id=='CORE_SCH_605' and defender:
            board=self.players[defender.owner].board;pos=board.index(defender)
            cleave=[board[i] for i in (pos-1,pos+1) if 0<=i<len(board) and board[i] in self.players[defender.owner].minions]
        p.friendly_attacks+=1
        self._log('attack',player=owner,source=source,target=target)
        if attacker:
            if not forced:attacker.attacks+=1
            attacker.keywords.discard('STEALTH')
            attacker.temporary_keywords[:]=[e for e in attacker.temporary_keywords if e['keyword']!='STEALTH']
        else:
            p.hero_attacks+=1
            p.hero_attacks_total+=1
        spill=max(0,attack-defender.health) if excess_to_hero and defender else 0
        with self._damage_batch():
            dealt=self._damage(target,attack-spill,'POISONOUS' in sk,damage_source=attacker,damage_owner=owner)
            spilled=self._damage(self.hero_id(defender.owner),spill,damage_source=attacker,damage_owner=owner) if spill else 0
            for extra in cleave:
                extra_dealt=self._damage(extra.uid,attack,'POISONOUS' in sk,damage_source=attacker,damage_owner=owner)
                self._freeze_from_damage(attacker,extra.uid,extra_dealt)
                if 'LIFESTEAL' in sk:self._effect_lifesteal(owner,extra_dealt)
            returned=self._damage(source,retaliation,'POISONOUS' in dk,damage_source=defender,damage_owner=defender.owner if defender else None)
            self._freeze_from_damage(attacker,target,dealt)
            self._freeze_from_damage(defender,source,returned)
            if 'LIFESTEAL' in sk: self._heal(self.hero_id(owner),dealt+spilled,healer=owner)
            if 'LIFESTEAL' in dk: self._heal(self.hero_id(defender.owner),returned,healer=defender.owner)
        if attacker and attacker.card_id=='EDR_819' and not attacker.silenced and defender and defender.health<=0:
            attacker.rule_state.setdefault('combat_kills',[]).append(defender.card_id)
        attack_killed=defender is not None and defender.health<=0
        self._close_attack_window(attack_window)
        if not attacker and p.weapon and weapon_id=='CORE_RLK_086' and defender and defender.health<=0:
            p.weapon.setdefault('stored_kills',[]).append(defender.card_id)
        if not attacker and p.weapon:
            p.weapon['durability']-=1
            if p.weapon['durability']<=0: self._break_weapon(owner)
        if attacker:
            self._rule_events.append(('minion_attack',dict(owner=owner,source=source,target=target,attacker_neighbors=neighbors,killed=defender is not None and defender.health<=0,victim_card_id=defender.card_id if defender else None),listeners))
        else:
            self._rule_events.append(('hero_attack',dict(owner=owner,source=source,target=target),listeners))
            for op in WEAPON_TRIGGERS.get(weapon_id,[]):
                self._effect(op,dict(owner=owner,source=None,target=target,bonus=0,lifesteal=False,attack_damage=attack,attack_killed=attack_killed,weapon_uid=weapon_uid))
        self._avatar_after_attack(owner,attacker,sk)
        self._settle()

    def _play(self,action):
        self._rewind_begin(action)
        owner=self.current; p=self.players[owner]
        card=next(c for c in p.hand if c.uid==action.source); cid=card.card_id; d=self.cards[cid]
        self._gelbin_preflight(cid,owner)
        self._dark_global_preflight(cid,owner)
        self._mutation_preflight(cid,owner)
        self._rewindgen_preflight(cid,owner)
        self._imbue_consumer_preflight(cid,owner)
        outcast=card.uid in (p.hand[0].uid,p.hand[-1].uid); combo=p.cards_played>0
        essence_neighbors=self._essence_neighbors(card,owner)
        hand_index=p.hand.index(card)
        hand_neighbors=tuple(p.hand[i].uid for i in (hand_index-1,hand_index+1) if 0<=i<len(p.hand))
        hand_center=len(p.hand)%2==1 and p.hand[len(p.hand)//2].uid==card.uid
        if cid=='JAIL_501':self._b60_state(card)['picklock_value']=max(1,p.mana)
        cost=self._cost(card,owner); source=None
        grants=[e.get('grant_keyword') for e in p.cost_effects if self._discount_matches(e,card) and e.get('grant_keyword')]
        p.cost_effects[:]=[e for e in p.cost_effects if not e.get('consume_on_play',True) or not self._discount_matches(e,card)]
        if cid not in RULES and cid not in PASSIVE and cid not in PLAYABLE_TOKENS and cid not in LOCATION_RULES: raise UnsupportedCard(cid)
        if cid!='TIME_042t':p.hand.remove(card)
        self._quest_deliver_ready(owner)
        self._dream_higher_play(owner,card,cost)
        self._origin_played(owner,card)
        self._capture_follow(owner,card)
        self._pay_card(card,owner,cost)
        if self._check_heroes():return
        self._b60_paid_card(owner,cost)
        self._log('play',player=owner,card=cid,target=action.target,position=action.position)
        if self._is_quest(cid):p.quests_played+=1
        self._quest_card_played(owner,card)
        source=None
        self._investigation_played(owner,card)
        repeat_spell=False
        if d['type']=='SPELL':
            repeat_spell=bool(getattr(card,'rule_state',{}).get('repeat_spell')) or p.spell_repeat_charges>0 or (cost==1 and self._active('TLC_836',owner))
            repeat_spell=self._azure_repeats_spell(owner,cid,other_repeat=repeat_spell) or repeat_spell
            repeat_spell=self._colossal_repeats_spell(owner,cid,other_repeat=repeat_spell) or repeat_spell
            if p.spell_repeat_charges:p.spell_repeat_charges-=1
            self._queue_event('spell_played',owner=owner,card_id=cid,cost=cost)
            self._drain_events()
            if self.terminal:return
        if d['type']=='SPELL' and self._secret_event('before_spell',owner):
            self._publish_follow(owner)
            self._settle(allow_event_choices=True)
            return
        if has_school(d,'FIRE'): p.fire_spell_played=True
        recipient=1-owner if cid in EITHER_SIDE and action.choices==(1,) else owner
        if d['type']=='MINION': source=self._summon(recipient,cid,action.position,card.attack_bonus,card.health_bonus, entry_origin='play', entry_site='game._play', entry_zone='hand', entry_source=card)
        elif d['type']=='LOCATION':
            source=self._place_location(owner,cid,action.position);self._crafted_location_entry(source,card)
        elif d['type']=='WEAPON': self._equip(owner,cid,attack_bonus=card.attack_bonus,physical_card=card)
        elif d['type']=='HERO': self._play_hero_card(owner,cid)
        elif d['type']!='SPELL': raise UnsupportedCard('Card type '+d['type'])
        if source is not None and d['type']=='MINION':
            source.played_turn=self.turn
            self._ashalon_play(owner,source)
            self._imbue_consumer_play(owner,source)
            if 'rewinds_remaining' in getattr(card,'rule_state',{}):source.rule_state['rewinds_remaining']=card.rule_state['rewinds_remaining']
            if 'destroy_on_turn' in self._b60_state(card):source.rule_state['destroy_on_turn']=card.rule_state['destroy_on_turn']
            if not source.dormant:source.keywords.update(grants)
        targeted_minion=any(m.uid==action.target for player in self.players for m in player.minions)
        context=dict(prior_spell_count=len(p.spells_turn),physical_card=card,paid_cost=cost,card_id=cid,owner=recipient,source=source,target=action.target,kindred=self._kindred(cid,owner),spell=d['type']=='SPELL',bonus=(self._spell_damage(owner)+getattr(card,'spell_damage_bonus',0)) if d['type']=='SPELL' else 0,lifesteal='LIFESTEAL' in d.get('mechanics',[]),outcast=outcast,combo=combo,hand_center=hand_center,hand_neighbors=hand_neighbors)
        context['essence_neighbors']=essence_neighbors
        if d['type']=='SPELL':
            context['bonus']+=getattr(p,'_next_spell_bonus',0);p._next_spell_bonus=0
        from .kindred import consume_repetition
        context['kindred_repeats']=consume_repetition(self,owner,cid,context['kindred'])
        operations=(self._crafted_rule(card) or RULES.get(cid,('none',[])))[1]
        if cid in CHOICES:
            selected=CHOICES[cid] if action.choices==(-1,) else [CHOICES[cid][action.choices[0]]]
            operations=[op for _,_,ops in selected for op in ops]
            if action.choices==(-1,) and cid=='CORE_EX1_154':
                operations=[('damage',4),('draw',1)]
            elif action.choices==(-1,) and cid=='CORE_EX1_160':
                operations=[('summon','EX1_160t',1),('board_buff',1,1)]
        if 'BATTLECRY' in d.get('mechanics',[]) or (d['type']=='MINION' and self._crafted_rule(card)):operations=list(operations)*self._trigger_repetitions(owner)
        operations=self._mug_play_operations(owner,cid,operations)
        if d['type']=='MINION':operations=self._dark_play_operations(operations,card,source)
        operations=self._morchie_operations(operations,context)
        if repeat_spell:
            operations=[('repeat_spell_effects',tuple(operations),context,2)]
        from .replay_history import capture_play
        replay_record=capture_play(self.turn,owner,card,cost,action)
        self._start_play_effects(operations,context)
        p.replay_history.append(replay_record)
        overload_player=self.players[recipient] if cid=='JAIL_452' else p
        overload_player.overload_next+=d.get('overload',0);overload_player.overloaded_total+=d.get('overload',0);p.cards_played+=1
        p.played_history.append(dict(card_id=cid,cost=cost))
        p.last_paid_cost=cost
        if d['type']=='SPELL':
            p.spells_turn.append(cid)
            if d.get('spellSchool'):p.spell_schools_this_turn.add(d['spellSchool'])
            if d.get('spellSchool')=='FEL':p.fel_spells_cast+=1
        if d['type']=='MINION':
            p.played_tribes.update(d.get('races',[]));p.minion_played_this_turn=True
        if d['type']=='SPELL' and d.get('spellSchool'):p.played_schools.add(d['spellSchool'])
        context=(cid,owner,card if d['type']=='SPELL' else source,cost,targeted_minion)
        if self.pending_choice: self.pending_play=context
        else: self._after_play(context)

    def _deal_effect(self,target,amount,ctx):
        if not target: return 0
        if target>0 and not any(m.uid==target for p in self.players for m in p.minions): return 0
        source=ctx.get('source')
        poisonous=('POISONOUS' in self._effective_keywords(source)) if source is not None else ctx.get('poisonous',False)
        amount=self._outgoing_tribal_damage(source,amount+ctx.get('bonus',0))
        if ctx.get('spell'):
            multiplier=self._spell_multiplier(ctx['owner'])
            if multiplier>1 and ctx.get('lifesteal'):raise UnsupportedCard('Atiesh spell Lifesteal interaction needs reviewed semantics')
            if not ctx.get('spell_multiplier_applied'):amount*=multiplier
        if self._fire_immune_target(target,ctx):return 0
        if self._replace_spell_damage(target,amount,ctx):return 0
        dealt=self._damage(target,amount,poisonous=poisonous,damage_source=source,damage_owner=ctx['owner'])
        self._freeze_from_damage(source,target,dealt)
        if ctx.get('spell'):
            player=self.players[ctx['owner']]
            if dealt>0 and player.spell_damage_turn==0:
                for m in player.minions:
                    if m.card_id=='CATA_487' and not m.silenced and m.health>0:self._buff(m,2,0)
            player.spell_damage_turn+=dealt
        lifesteal=('LIFESTEAL' in self._effective_keywords(source)) if source is not None else ctx.get('lifesteal',False)
        if lifesteal and dealt:self._effect_lifesteal(ctx['owner'],dealt)
        return dealt

    def _effect(self,op,ctx):
        if self._fire_effect_guard(op,ctx):return
        effect_context=getattr(self,'_active_effect_context',{})
        self._active_effect_context=ctx
        previous=self.pending_choice
        own_healing_frame=not hasattr(self,'_healing_replacement_frame')
        if own_healing_frame:self._healing_replacement_frame=set()
        damage_source=getattr(self,'_damage_origin',None)
        self._damage_origin=ctx.get('source')
        tracked=[m for player in self.players for m in player.minions if m.card_id=='CATA_185' and m.health>0]
        try:
            self._dispatch_effect(op,ctx)
            source=ctx.get('source')
            if source is not None and isinstance(source,Minion):
                for m in tracked:
                    if m.health<=0 and m in self.players[m.owner].board:
                        m.rule_state.setdefault('killed_by_minion',source.uid)
        finally:
            self._active_effect_context=effect_context
            self._damage_origin=damage_source
            if own_healing_frame:del self._healing_replacement_frame
        choice=self.pending_choice
        if choice is not None and choice is not previous:
            # The innermost effect owns its choice. An enclosing automatic
            # spell must not relabel a triggered minion's player choice.
            choice.setdefault('_automatic',bool(ctx.get('automatic_choices',False)))

    def _effect_checkpoint(self,op,ctx):
        self._effect(op,ctx)
        self._colossal_stat_checkpoint()
        self._champion_checkpoint()
        self._resolve_automatic_choices()

    def _dispatch_effect(self,op,ctx):
        from .automatic_cards import place_automatic_card
        if place_automatic_card(self,op,ctx):return
        if op[0]=='kindred_twice_next':self.players[ctx['owner']].kindred_twice=True;return
        if self._finish_effect(op,ctx):return
        if self._forge_effect(op,ctx):return
        if self._craft_effect(op,ctx):return
        if self._counterfeit_effect(op,ctx):return
        if self._osk_effect(op,ctx):return
        if self._remaining_setup_effect(op,ctx):return
        if self._investigation_effect(op,ctx):return
        if self._tiny_effect(op,ctx):return
        if self._ruby_effect(op,ctx):return
        if self._stat_rule_effect(op,ctx):return
        if self._genn_effect(op,ctx):return
        if self._replacement_effect(op,ctx):return
        if self._deadline_effect(op,ctx):return
        if self._infinity_effect(op,ctx):return
        if self._quest_family_effect(op,ctx):return
        if self._muradin_effect(op,ctx):return
        if self._azshara_effect(op,ctx):return
        if self._gelbin_effect(op,ctx):return
        if self._brox_effect(op,ctx):return
        if self._garona_effect(op,ctx):return
        if self._rafaam_effect(op,ctx):return
        if self._fabled_effect(op,ctx):return
        if self._obligation_effect(op,ctx):return
        if self._learned_effect(op,ctx):return
        if self._zone_trigger_effect(op,ctx):return
        owner=ctx['owner']; p=self.players[owner]; q=self.players[1-owner]
        target=ctx.get('target',0); source=ctx.get('source'); name=op[0]
        if self._temporary_control_effect(op,ctx):return
        if self._evolving_effect(op,ctx):return
        if self._imbue_effect(op,ctx):return
        if self._cast_spell_effect(op,ctx):return
        if self._permanent_effect(op,ctx):return
        if self._dream_effect(op,ctx):return
        if self._quest_effect(op,ctx):return
        if self._hero_power_effect(op,ctx):return
        if name=='discover_after':self._discover_after(op);return
        if self._secret_effect(op,ctx): return
        if self._choicegen_effect(op,ctx): return
        if self._colossal_body_effect(op,ctx): return
        if self._herald_effect(op,ctx): return
        if self._future_summon_effect(op,ctx): return
        if self._autocast_effect(op,ctx): return
        if self._map_effect(op,ctx): return
        if self._leyline_effect(op,ctx): return
        if self._generation_effect(op,ctx): return
        if self._tribal_effect(op,ctx): return
        if self._alternate_effect(op,ctx): return
        if self._force_effect(op,ctx): return
        if self._on_draw_effect(op,ctx): return
        if self._replay_effect(op,ctx): return
        if self._prepare_effect(op,ctx): return
        if self._temporary_effect(op,ctx): return
        if self._held_effect(op,ctx): return
        if self._origin_effect(op,ctx): return
        if self._dormant_effect(op,ctx): return
        if self._bonus_effect(op,ctx): return
        if self._draw_event_effect(op,ctx): return
        if self._local_effect(op,ctx): return
        if self._b60_effect(op,ctx): return
        if self._persistent_effect(op,ctx): return
        if self._composed_effect(op,ctx): return
        if self._batch30_effect(op,ctx): return
        if self._imbue_consumer_effect(op,ctx): return
        if self._rewindgen_effect(op,ctx): return
        if self._mutation_effect(op,ctx): return
        if self._entity_effect(op,ctx): return
        if self._lasting_effect(op,ctx): return
        if self._stored_effect(op,ctx): return
        if self._dark_global_effect(op,ctx): return
        if self._dark_effect(op,ctx): return
        if self._rewind_effect(op,ctx): return
        if self._shatter_effect(op,ctx): return
        if self._batch_effect(op,ctx): return
        if self._system_effect(op,ctx): return
        if name in ('damage','combo_damage'):
            if name=='damage' or ctx.get('combo'): self._deal_effect(target,op[1],ctx)
        elif name=='damage_own_hero': self._deal_effect(self.hero_id(owner),op[1],ctx)
        elif name=='heal':
            if target: self._heal(target,op[1],healer=owner,spell=ctx.get('spell',False))
        elif name=='repeat_end_effects':
            p.end_repeat_expiries.append(p.turns_taken+op[1]-1+getattr(ctx.get('physical_card'),'rule_state',{}).get('aura_duration_delta',0))
        elif name=='schedule_turn_effect':
            self._schedule_turn_effect(owner,op[1],op[2],op[3]+getattr(ctx.get('physical_card'),'rule_state',{}).get('aura_duration_delta',0),op[4],source_card_id=ctx.get('card_id'))
        elif name=='hero_divine_shield': p.divine_shield=True
        elif name=='permanent_healing_bonus': p.permanent_healing_bonus+=op[1]
        elif name=='heal_own_hero': self._heal(self.hero_id(owner),op[1],healer=owner,spell=ctx.get('spell',False))
        elif name=='armor': self._gain_armor(owner,op[1])
        elif name in ('draw','draw_empty','outcast_draw'):
            if name=='draw' or (name=='draw_empty' and not p.hand) or (name=='outcast_draw' and ctx.get('outcast')):
                for _ in range(op[1]):
                    self._draw(owner)
                    if self._check_heroes(): break
        elif name=='hero_attack': p.temporary_attack+=op[1]
        elif name=='weapon_buff': self._buff_weapon(owner,attack=op[1])
        elif name=='temporary_mana': p.mana=min(p.mana_capacity,p.mana+op[1])
        elif name in ('summon','combo_summon'):
            if name=='summon' or ctx.get('combo'):
                require_fixed_cards((op[1],),self.cards)
                for _ in range(op[2]): self._summon(owner,op[1], entry_origin='effect', entry_site="game._effect:name == 'summon' or ctx.get('combo')", entry_source=ctx.get('source'))
        elif name=='raise_corpses':
            # Raise only what fits: failed summons must not consume extra corpses.
            count=min(op[2],p.corpses,7-len(p.board))
            self._spend_corpses(owner,count)
            for _ in range(count): self._summon(owner,op[1], entry_origin='effect', entry_site="game._effect:name == 'raise_corpses'", entry_source=ctx.get('source'))
        elif name=='tomb_guardians':
            require_fixed_cards((op[1],),self.cards)
            summoned=[self._summon(owner,op[1], entry_origin='effect', entry_site="game._effect:name == 'tomb_guardians'", entry_source=ctx.get('source')) for _ in range(2)]
            summoned=[m for m in summoned if m is not None]
            if summoned and p.corpses>=4:
                self._spend_corpses(owner,4)
                for m in summoned: m.keywords.add('REBORN')
        elif name=='death_summon':
            start=op[3] if len(op)>3 else 0
            for offset in range(start,start+op[2]):
                self._summon(owner,op[1],min(ctx['death_position']+offset,len(p.board)), entry_origin='deathrattle', entry_site="game._effect:name == 'death_summon'", entry_source=ctx.get('source'))
        elif name=='draw_both':
            # Finish both draws before terminal resolution (including fatigue).
            self._draw(owner); self._draw(1-owner)
        elif name=='draw_tribe':
            self._draw(owner,lambda card: has_tribe(card,op[1]))
        elif name=='draw_unspent_mana':
            if p.mana>0: self._draw(owner)
        elif name=='buff_random_other':
            others=[m for m in p.minions if m is not source and
                    (len(op)<4 or has_tribe(self.cards[m.card_id],op[3]))]
            if others: self._buff(self.rng.choice(others),op[1],op[2])
        elif name=='add':
            for _ in range(op[2]): self._add(owner,op[1])
        elif name=='buff':
            if target and any(m.uid==target for player in self.players for m in player.minions): self._buff(self._find(target),op[1],op[2])
        elif name=='keyword':
            if target and any(m.uid==target for player in self.players for m in player.minions): self._find(target).keywords.add(op[1])
        elif name=='freeze':
            if target<0 or any(m.uid==target for player in self.players for m in player.minions): self._freeze(target)
        elif name=='freeze_enemies':
            for m in q.minions: self._freeze(m.uid)
        elif name=='destroy':
            if target: self._find(target).health=0
        elif name=='buff_board_count':
            if target: self._buff(self._find(target),len(p.minions),len(p.minions))
        elif name=='heal_full':
            if target:
                m=self._find(target); self._heal(target,m.max_health-m.health,healer=owner,spell=ctx.get('spell',False))
        elif name=='damage_self': self._deal_effect(source.uid,op[1],ctx)
        elif name=='damage_random_enemy_minion':
            if q.minions: self._deal_effect(self.rng.choice(q.minions).uid,op[1],ctx)
        elif name=='freeze_self': self._freeze(source.uid)
        elif name=='double_self_attack': self._buff(source,source.attack,0)
        elif name=='double_self_health': self._buff(source,0,source.health)
        elif name=='reverse_deck': p.deck.reverse()
        elif name=='draw_until':
            for _ in range(max(0,op[1]-len(p.hand))):
                self._draw(owner)
                if self._check_heroes(): break
        elif name=='damage_armor': self._deal_effect(target,p.armor,ctx)
        elif name=='destroy_small':
            for player in self.players:
                for m in player.minions:
                    if m.attack<=op[1] and not self._fire_immune_target(m.uid,ctx): m.health=0
        elif name=='destroy_large':
            for player in self.players:
                for m in player.minions:
                    if m.attack>=op[1] and not self._fire_immune_target(m.uid,ctx): m.health=0
        elif name=='health_one':
            for player in self.players:
                for m in player.minions:
                    if not self._fire_immune_target(m.uid,ctx):m.health=m.max_health=1
        elif name=='area_damage':
            groups={'enemy_minions':[m.uid for m in q.minions], 'enemies':[self.hero_id(1-owner)]+[m.uid for m in q.minions],
                    'other_characters':[uid for uid in self._characters() if source is None or uid!=source.uid], 'all_characters':self._characters(), 'all_minions':[m.uid for player in self.players for m in player.minions], 'other_minions':[m.uid for player in self.players for m in player.minions if source is None or m.uid!=source.uid]}
            with self._damage_batch():
                for uid in groups[op[1]]: self._deal_effect(uid,op[2],ctx)
        elif name=='area_heal':
            for uid in [self.hero_id(owner)]+[m.uid for m in p.minions]: self._heal(uid,op[1],healer=owner,spell=ctx.get('spell',False))
        elif name in ('damage_draw_if_dead','damage_draw_if_alive'):
            if target:
                self._deal_effect(target,op[1],ctx); dead=self._find(target).health<=0
                self._settle()
                if not self.terminal and dead==(name=='damage_draw_if_dead'):
                    for _ in range(op[2] if len(op)>2 else 1):
                        self._draw(owner)
                        if self._check_heroes(): break
        elif name=='hand_buff' or name=='taunt_hand_buff':
            for c in p.hand:
                if self.cards[c.card_id]['type']=='MINION' and (name=='hand_buff' or 'TAUNT' in self._card_mechanics(c)):
                    c.attack_bonus+=op[1]; c.health_bonus+=op[2]
        elif name=='board_buff':
            for m in p.minions: self._buff(m,op[1],op[2])
        elif name=='board_expire':
            for m in p.minions:m.expires=True
        elif name=='board_keyword':
            for m in p.minions: m.keywords.add(op[1])
        elif name=='grave_strength':
            spent=5 if p.corpses>=5 else 0; self._spend_corpses(owner,spent)
            for m in p.minions: self._buff(m,3 if spent else 1,0)
        elif name=='blood_tap':
            spent=2 if p.corpses>=2 else 0; self._spend_corpses(owner,spent)
            self._effect(('hand_buff',2 if spent else 1,2 if spent else 1),ctx)
        elif name=='asphyxiate':
            if q.minions:
                highest=max(m.attack for m in q.minions); self.rng.choice([m for m in q.minions if m.attack==highest]).health=0
        elif name=='self_hand_health': self._buff(source,0,len(p.hand))
        elif name=='self_enemy_hand_health': self._buff(source,0,-len(q.hand))
        elif name=='self_weapon_attack': self._buff(source,p.weapon['attack'] if p.weapon else 0,0)
        elif name=='adjacent_taunt':
            index=p.board.index(source)
            for i in (index-1,index+1):
                if 0<=i<len(p.board) and p.board[i] in p.minions: p.board[i].keywords.add('TAUNT')
        elif name=='other_murloc_health':
            for m in p.minions:
                if m is not source and has_tribe(self.cards[m.card_id],'MURLOC'): self._buff(m,0,op[1])
        elif name=='shadow_hand_buff':
            if any(has_school(self.cards[c.card_id],'SHADOW') for c in p.hand): self._buff(source,op[1],op[2])
        elif name=='discard':
            self._discard_random(owner,op[1])
        elif name=='remove_enemy_top':
            if q.deck: self._log('remove_deck_card',player=1-owner,card=self._card_data(q.deck.pop())['id'])
        elif name=='random_shield_taunt':
            if p.minions: self.rng.choice(p.minions).keywords.update({'DIVINE_SHIELD','TAUNT'})
        elif name=='beast_weapon_durability':
            if any(has_tribe(self.cards[m.card_id],'BEAST') for m in p.minions): self._buff_weapon(owner,durability=op[1])
        elif name=='destroy_random_enemy':
            if q.minions: self.rng.choice(q.minions).health=0
        else: raise UnsupportedCard('Effect opcode not implemented: '+name)

    def observe(self,viewer,include_events=True):
        observation=super().observe(viewer,include_events)
        actor=self.pending_choice['owner'] if self.phase=='choice' and self.pending_choice else self.current
        observation['legal_actions']=[asdict(a) for a in self.legal_actions()] if viewer==actor else []
        for owner,(p,public) in enumerate(zip(self.players,observation['players'])):
            public.update(divine_shield=p.divine_shield,max_health=p.max_health,turns_taken=p.turns_taken,immune=self._hero_immune(owner),hero_class=p.hero_class,hero_attack=self._hero_attack(owner),frozen=p.frozen_until>=0,
                          locked_mana=p.locked_mana,overload_next=p.overload_next,cards_played=p.cards_played,
                          secret_count=len(p.secrets),fire_spell_played=p.fire_spell_played,hero_power_uses=p.hero_power_uses)
            for entity in public['board']:
                actual=next((m for m in p.all_minions if m.uid==entity['uid']),None)
                if 'avatar_form' in entity.get('rule_state',{}):
                    entity['rule_state']['avatar_form']=sum(b['turn']==self.turn for b in entity['rule_state']['avatar_form'])
                if actual is not None and hasattr(actual,'_muradin_hammer'):
                    held=actual._muradin_hammer
                    entity['held_hammer']=dict(card_id=held['card'].card_id,attack=held['attack'],durability=held['durability'])
                if actual is not None and hasattr(actual,'_control_return'):
                    effect=actual._control_return
                    entity['control_return']=dict(to='self' if effect['owner']==viewer else 'opponent',turns=max(0,effect['due']-self.players[effect['owner']].turns_taken))
                for effect in entity.get('imbue_attack_expiries',[]):
                    effect['expires_at_turn_of']='self' if effect.pop('owner')==viewer else 'opponent'
            if owner!=viewer:
                for entity in public['board']:
                    entity.get('rule_state',{}).pop('absorbed_spell_id',None)
            public.update(self._obligation_view(owner,viewer))
            public['broxigar_waiting']=sum(getattr(c,'_starting_owner',None)==owner for c in getattr(self,'_broxigar_waiting',[]))
            public['mana_capacity']=p.mana_capacity
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
            public['hero_lifesteal']=p.hero_lifesteal_until>=self.turn
            if owner==viewer:public['companion_ids']=list(p.companion_ids)
            public['hero_attacks_total']=p.hero_attacks_total
            public['extra_turns_pending']=p.extra_turns_pending
            public['time_warp_used']=p.time_warp_used
            public['crystal_core']=p.crystal_core
            public['kindred_twice']=getattr(p,'kindred_twice',False)
            public['next_spell_bonus']=getattr(p,'_next_spell_bonus',0)
            public['counterfeit_coin']=getattr(p,'counterfeit_coin',None)
            public['jade_size']=getattr(p,'jade_size',0)
            public['tendril_cost']=getattr(p,'tendril_cost',1)
            public['forge_sidequests']=deepcopy(getattr(p,'forge_sidequests',[]))
            public['turn_time_limit']=getattr(self,'turn_time_limit',None)
            public['turn_time_elapsed']=getattr(self,'turn_time_elapsed',0)
            if owner==viewer:public['contraband_beasts']=list(getattr(p,'contraband_beasts',()))
            if owner==viewer:public['hand_investigations']=[dict(w) for w in getattr(p,'_hand_investigations',[])]
            public['next_heal_damage']=getattr(p,'ruby_until',-1)==self.turn
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
                if getattr(entity,'_illusion_possible',False):view['illusion_possible']=True
            if owner==viewer:
                public['starting_hand']=[c.card_id for c in getattr(p,'_starting_hand',[])]
                public['set_aside_cards']=[dict(kind=entry['kind'],cards=[self._card_data(c)['id'] for c in entry['values']]) for entry in getattr(self,'_stored_payloads',{}).values() if entry['owner']==owner and entry['kind'] in ('hand','future')]
            public['discard_history']=list(p.discard_history)
            public['shuffle_history']=deepcopy(p.shuffle_history)
            public['healing_block_expiry_players']=list(p.healing_block_expiry_players)
            public['secondary_power']=deepcopy(p.secondary_power)
            if p.secondary_power is not None:public['secondary_power']['cost']=self._power_cost(owner,secondary=True)
            public['primary_power']=deepcopy(p.primary_power)
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
            public['minion_played_this_turn']=p.minion_played_this_turn
            public['minion_played_last_turn']=p.minion_played_last_turn
            public['imbue_count']=p.imbue_count
            public['hamuul_active']=p.hamuul_active
            public['hamuul_spells']=p.hamuul_spells
            public['undead_played_this_turn']=p.undead_play_turn==self.turn
            public['spell_repeat_charges']=p.spell_repeat_charges
            public['end_repeat_turns']=[max(0,end-p.turns_taken+1) for end in p.end_repeat_expiries]
            public['scheduled_effects']=[self._scheduled_effect_view(e,owner) for e in p.scheduled_effects]
            public['eternal_life']=p.eternal_life
            public['ashalon_adaptations']=list(p.ashalon_adaptations)
            public['gorishi_stacks']=p.gorishi_stacks
            public['damaged_characters_turn']=len(p.damaged_characters_turn)
            public['rule_counters']={key:deepcopy(getattr(p,key)) for key in ('fel_spells_cast','friendly_attacks','last_paid_cost','spell_damage_turn','hero_damage_taken_turn','hero_damage_events_turn','minions_died_turn','overloaded_total','healing_done_turn','permanent_healing_bonus','permanent_end_damage','spells_turn','spells_previous')}
            public['kindred_history']={key:sorted(getattr(p,key)) for key in ('played_tribes','played_schools','previous_tribes','previous_schools')}
            if owner!=viewer:
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
                public['nonstarting_cards_played']=getattr(p,'_nonstarting_plays',0)
                public['secrets']=[c.card_id for c in p.secrets]
                public['cost_effects']=deepcopy(p.cost_effects)
        if self.pending_choice:
            observation['pending_choice']=(
                dict(owner=self.pending_choice['owner'],kind=self.pending_choice['kind'],
                     **({'remaining':self.pending_choice['remaining']} if self.pending_choice['kind'] in ('rewind','herald_cataclysm') else {}),
                     **({'picks':list(self.pending_choice['picks'])} if self.pending_choice['kind']=='herald_cataclysm' else {}),
                     options=[dict(card_id=o['card_id'],**{key:o[key] for key in ('label','uid','dark_gift','attack','health','cost') if key in o}) for o in self.pending_choice['options']])
                if viewer==self.pending_choice['owner']
                                           else {'owner':self.pending_choice['owner'],'waiting':True})
        else: observation['pending_choice']=None
        for c in self.players[viewer].hand:
            public=next(h for h in observation['players'][viewer]['hand'] if h['uid']==c.uid)
            public['cost']=self._cost(c,viewer)
            public['payment_kind']=self._payment_kind(c,viewer)
            public['cost_delta']=getattr(c,'cost_delta',0)
            public['temporary']=self._is_temporary(c)
            lock=getattr(c,'rule_state',{}).get('locked_until_play')
            public['plays_until_unlocked']=max(0,lock['count']-len(self.players[viewer].played_history)) if lock and lock['owner']==viewer else 0
            if c.card_id=='CATA_206':public['bonus_effects']=list(self._held_bonus_pair(c))
            public['follow_effects']=deepcopy([e for e in getattr(c,'_follow_effects',[]) if e['end']>=self.turn])
            public['started_in_deck']=self._started_in_deck(c,viewer)
            public['copied_from_opponent']=self._copied_from_opponent(c,viewer)
            public['entered_hand_this_turn']=getattr(c,'_hand_entry_turn',None)==self.turn
            for field in ('spell_damage_bonus','growing_discounts','play_lock','rule_state'):
                if hasattr(c,field):public[field]=deepcopy(getattr(c,field))
            public.update(self._stored_view(c))
            public['toki_return_tasks']=[dict(task=i,remaining=len(t['required']-t['played'])) for i,t in enumerate(getattr(self.players[viewer],'_toki_tasks',[])) if c.uid in t['required']-t['played']]
            public['temporary_cost_discounts']=deepcopy(getattr(c,'temporary_cost_discounts',[]))
            if hasattr(c,'set_cost'):public['set_cost']=c.set_cost
            if self.cards[c.card_id]['type']=='MINION':
                public['attack']=self._card_stat(c,'attack',viewer)
                public['health']=self._card_stat(c,'health',viewer)
            if c.card_id in CHOICES: public['choices']=[b[0] for b in CHOICES[c.card_id]]
        # A played secret's identity is hidden even though its play is public.
        for event in observation['events']:
            if event.get('event') in ('play','internal_spell_cast','internal_spell_complete') and event.get('player')!=viewer and event.get('card') in SECRETS:
                event['card']='SECRET'
        return observation
