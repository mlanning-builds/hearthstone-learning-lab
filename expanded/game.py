"""Experimental all-class rules extension; NOT complete Standard.

User-run validation is pending. Unsupported decks fail before state creation.
The original engine and saved training fingerprints are preserved.
"""
from dataclasses import dataclass, field, asdict
from copy import deepcopy
import random
from collections import deque
from .selectors import has_tribe, has_any_tribe, has_school
from .resolution import Resolution
from .lifecycle import Lifecycle
from .pools import GenerationPool, require_fixed_cards
from .locations import Locations, Location, LOCATION_RULES
from .battlefield import Battlefield
from .systems import Systems
from .secrets import Secrets, SECRETS
from engine.game import Game as LegacyGame, Player as LegacyPlayer, Minion as LegacyMinion, Card, Action, TARGETS
from engine.cards import UnsupportedCard
from .cards import registry, RULES, PASSIVE, DEATH_EFFECTS, PLAYABLE_TOKENS, END_EFFECTS, NO_CORPSE, CHOICES, WEAPON_TRIGGERS
from .decks import validate

TOTEMS=('CS2_050','CS2_051','CS2_058','NEW1_009')
BASIC_TOTEM_POOL=GenerationPool('Basic Shaman hero power',TOTEMS,
    'Existing pinned engine base-power definition; four explicit basic totems')

@dataclass
class Player(LegacyPlayer):
    secrets: list = field(default_factory=list)
    next_power_increase: int = 0
    cost_effects: list = field(default_factory=list)
    timed_cost_increases: list = field(default_factory=list)
    hero_class: str = 'DEATHKNIGHT'
    temporary_attack: int = 0
    overload_next: int = 0
    locked_mana: int = 0
    cards_played: int = 0
    frozen_until: int = -1
    fire_spell_played: bool = False

    @property
    def minions(self):
        return [entity for entity in self.board if not isinstance(entity,Location)]

    @property
    def locations(self):
        return [entity for entity in self.board if isinstance(entity,Location)]

@dataclass
class Minion(LegacyMinion):
    frozen_until: int = -1
    silenced: bool = False
    aura_attack: int = 0
    aura_health: int = 0
    temporary_attack: int = 0


class Game(Secrets, Systems, Lifecycle, Resolution, Locations, Battlefield, LegacyGame):
    VERSION='all-class-experimental-0.14'

    def __init__(self,decks,seed=0,first_player=0,max_turns=89,record=True):
        if len(decks)!=2 or first_player not in (0,1): raise ValueError('Provide two decks and first player 0 or 1')
        if type(max_turns) is not int or not 1<=max_turns<=89: raise ValueError('Invalid turn limit')
        self.cards=registry()
        for deck in decks:
            errors=validate(deck,self.cards)
            if errors: raise UnsupportedCard('; '.join(errors))
        self.seed=seed; self.rng=random.Random(seed); self.uid=0; self.players=[]
        for deck in decks:
            shuffled=list(deck.cards); self.rng.shuffle(shuffled)
            self.players.append(Player(shuffled,list(deck.cards),tuple(deck.runes),hero_class=deck.hero_class))
        self.first_player=first_player; self.current=first_player; self.phase='mulligan'; self.mulligan_done=set()
        self.turn=0; self.max_turns=max_turns; self.terminal=False; self.winner=None; self.end_reason=None
        self.record=record; self.events=[]; self.history=[]
        self._rule_events=deque(); self._draining_events=False; self._event_frames=[]
        self._damage_batch_depth=0
        self._settling=False;self._death_frame=None;self._turn_frame=None;self._resuming_turn=False
        self.pending_choice=None; self.pending_play=None; self.pending_frame=None
        for owner in (first_player,1-first_player):
            for _ in range(3 if owner==first_player else 4): self._draw(owner,private=True)

    def _summon(self,owner,cid,position=-1,attack_bonus=0,health_bonus=0,expires=False):
        m = self._create_minion(owner,cid,position,attack_bonus,health_bonus,expires)
        if m is not None:
            self._log('summon',player=owner,card=cid,entity=m.uid,
                      position=self.players[owner].board.index(m))
        return m

    def _create_minion(self,owner,cid,position=-1,attack_bonus=0,health_bonus=0,expires=False):
        if cid not in self.cards or self.cards[cid]['type']!='MINION': raise UnsupportedCard(cid)
        p=self.players[owner]
        if len(p.board)>=7: return None
        c=self.cards[cid]; health=c['health']+health_bonus
        m=Minion(self._new_id(),cid,owner,c['attack']+attack_bonus,health,health,set(c.get('mechanics',[])),summoned_turn=self.turn,expires=expires)
        if position<0: position=len(p.board)
        p.board.insert(position,m)
        self._refresh_auras()
        return m

    def _add(self,owner,cid):
        if cid not in self.cards: raise UnsupportedCard('Generated card not implemented: '+cid)
        p=self.players[owner]
        if len(p.hand)>=10: self._log('burn_generated',player=owner,card=cid)
        else: p.hand.append(Card(self._new_id(),cid))

    def _hero_attack(self,owner):
        p=self.players[owner]
        return p.temporary_attack+((p.armor if p.weapon['card_id']=='CORE_LOOT_044' else p.weapon['attack']) if p.weapon else 0)

    def _spell_damage(self,owner):
        return sum(self.cards[m.card_id].get('spellDamage',0) for m in self.players[owner].minions if not m.silenced)

    def _visible_targets(self,owner,magic=False):
        return [self.hero_id(0),self.hero_id(1)]+[m.uid for p in self.players for m in p.minions
            if not (m.owner!=owner and 'STEALTH' in m.keywords) and not (magic and 'ELUSIVE' in m.keywords)]

    def _targets_for(self,cid,owner,mode_override=None):
        data=self.cards[cid]
        mode=mode_override if mode_override is not None else (RULES[cid][0] if cid in RULES else TARGETS.get(cid,'none'))
        if mode=='combo_character': mode='character' if self.players[owner].cards_played else 'none'
        if mode=='combo_friendly_minion': mode='friendly_minion' if self.players[owner].cards_played else 'none'
        if mode=='weapon_character': mode='character' if self.players[owner].weapon else 'none'
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
            if mode=='enemy_taunt': return not friendly and 'TAUNT' in m.keywords
            if mode=='large_minion': return m.attack>=7
            if mode=='legendary_minion': return self.cards[m.card_id].get('rarity')=='LEGENDARY'
            if mode=='tribal_enemy_minion': return not friendly and has_any_tribe(self.cards[m.card_id])
            if mode=='damaged_minion': return m.health<m.max_health
            if mode=='enemy_minion': return not friendly
            if mode=='friendly_minion': return friendly
            if mode=='friendly_beast': return friendly and has_tribe(self.cards[m.card_id],'BEAST')
            if mode=='friendly_undead': return friendly and has_tribe(self.cards[m.card_id],'UNDEAD')
            if mode=='undamaged_minion': return m.health==m.max_health
            if mode=='damaged_enemy_minion': return not friendly and m.health<m.max_health
            raise UnsupportedCard('Target mode: '+mode)
        result=[uid for uid in targets if valid(uid)]
        return result or ([0] if data['type']=='MINION' else [])

    def _cost(self,card,owner):
        p=self.players[owner]; cid=card.card_id
        cost=self.cards[cid]['cost']
        if cid=='CORE_BT_801' and p.hand and card.uid in (p.hand[0].uid,p.hand[-1].uid): cost=1
        elif cid=='CORE_NEW1_022': cost-=p.weapon['attack'] if p.weapon else 0
        elif cid=='CATA_308' and any(self.cards[m.card_id].get('rarity')=='LEGENDARY' for m in p.minions): cost=1
        cost+=getattr(card,'cost_delta',0)
        for effect in p.cost_effects:
            if self._discount_matches(effect,card):cost-=effect['amount']
        for effect in p.timed_cost_increases:
            if effect['start'] <= self.turn <= effect['end'] and (
                    effect['selector']=='ALL' or self._discount_matches(effect,card)):
                cost+=effect['amount']
        return max(0,cost)

    def _attack_targets(self,m=None):
        enemy=self.players[1-self.current]
        visible=[x for x in enemy.minions if 'STEALTH' not in x.keywords]
        taunts=[] if self._active('CORE_BT_187',self.current) else [x.uid for x in visible if 'TAUNT' in x.keywords]
        targets=taunts or [self.hero_id(1-self.current)]+[x.uid for x in visible]
        if m and m.summoned_turn==self.turn and 'CHARGE' not in m.keywords:
            if 'RUSH' not in m.keywords: return []
            targets=[t for t in targets if t>0]
        if m is None and self.players[self.current].weapon and self.players[self.current].weapon['card_id']=='CORE_LOOT_044':
            targets=[t for t in targets if t>0]
        return targets

    def legal_actions(self):
        if self.terminal: return []
        if self.phase=='mulligan': return super().legal_actions()
        if self.phase=='choice':
            return [Action('choose',choices=(i,)) for i in range(len(self.pending_choice['options']))]
        p=self.players[self.current]; actions=[Action('end')]
        for c in p.hand:
            d=self.cards[c.card_id]
            if 'TRADEABLE' in d.get('mechanics',[]) and p.mana>=1 and p.deck:
                actions.append(Action('trade',source=c.uid))
            if self._cost(c,self.current)>p.mana or (d['type'] in ('MINION','LOCATION') and len(p.board)>=7): continue
            if c.card_id in SECRETS and (len(p.secrets)>=5 or any(secret.card_id==c.card_id for secret in p.secrets)): continue
            positions=range(len(p.board)+1) if d['type'] in ('MINION','LOCATION') else [-1]
            branches=CHOICES.get(c.card_id)
            if branches:
                if self._active('CORE_OG_044',self.current):
                    modes=[b[1] for b in branches if b[1]!='none']
                    # Current combined choices have at most one target restriction.
                    mode=modes[0] if modes else 'none'
                    for target in self._targets_for(c.card_id,self.current,mode):
                        actions.extend(Action('play',c.uid,target,pos,(-1,)) for pos in positions)
                else:
                    for i,(_,mode,_) in enumerate(branches):
                        for target in self._targets_for(c.card_id,self.current,mode):
                            actions.extend(Action('play',c.uid,target,pos,(i,)) for pos in positions)
            else:
                for target in self._targets_for(c.card_id,self.current):
                    actions.extend(Action('play',c.uid,target,pos) for pos in positions)
        actions.extend(self._location_actions())
        cost=self._power_cost(self.current)
        if not p.power_used and p.mana>=cost:
            k=p.hero_class
            if k in ('MAGE','PRIEST'):
                actions.extend(Action('power',target=t) for t in self._visible_targets(self.current,magic=True))
            elif k in ('PALADIN','DEATHKNIGHT'):
                if len(p.board)<7: actions.append(Action('power'))
            elif k=='SHAMAN':
                if len(p.board)<7 and set(TOTEMS)-{m.card_id for m in p.minions}: actions.append(Action('power'))
            else: actions.append(Action('power'))
        for m in p.minions:
            limit=2 if 'WINDFURY' in m.keywords else 1
            if m.frozen_until<0 and m.attacks<limit and m.attack>0:
                actions.extend(Action('attack',m.uid,t) for t in self._attack_targets(m))
        if p.frozen_until<0 and not p.hero_attacks and self._hero_attack(self.current)>0:
            actions.extend(Action('attack',self.hero_id(self.current),t) for t in self._attack_targets())
        return actions

    def step(self,action):
        if action not in self.legal_actions(): raise ValueError('Illegal action; state unchanged')
        # Preserve the full state, including RNG, if an unexpected effect fails.
        before=deepcopy(self.__dict__)
        try:
            actor=self.current; self.history.append(dict(player=actor,action=asdict(action)))
            if action.kind=='mulligan': self._mulligan(action.choices)
            elif action.kind=='end': self._end_turn()
            elif action.kind=='power': self._power(action.target)
            elif action.kind=='attack': self._attack(action.source,action.target)
            elif action.kind=='play': self._play(action)
            elif action.kind=='trade': self._trade(action.source)
            elif action.kind=='activate': self._activate_location(action)
            elif action.kind=='choose': self._resolve_choice(action.choices[0])
            else: raise ValueError('Unknown action')
            self._settle(); self.assert_invariants()
            return self.rewards(),self.terminal
        except Exception:
            self.__dict__.clear(); self.__dict__.update(before)
            raise

    def _power_cost(self,owner):
        p=self.players[owner]
        return (1 if p.hero_class=='DEMONHUNTER' else 2)+p.next_power_increase

    def _power(self,target):
        owner=self.current; p=self.players[owner]; k=p.hero_class
        cost=self._power_cost(owner)
        p.mana-=cost; p.power_used=True
        p.next_power_increase=0
        self._log('hero_power',player=owner,hero_class=k,target=target)
        if k=='WARRIOR': p.armor+=2
        elif k=='HUNTER': self._damage(self.hero_id(1-owner),2)
        elif k=='MAGE': self._damage(target,1)
        elif k=='PRIEST': self._heal(target,2)
        elif k=='DRUID': p.temporary_attack+=1; p.armor+=1
        elif k=='DEMONHUNTER': p.temporary_attack+=1
        elif k=='WARLOCK': self._draw(owner); self._damage(self.hero_id(owner),2)
        elif k=='ROGUE': self._equip(owner,'CS2_082')
        elif k=='PALADIN': self._summon(owner,'CS2_101t')
        elif k=='DEATHKNIGHT': self._summon(owner,'TOKEN_GHOUL',expires=True)
        elif k=='SHAMAN':
            candidates=BASIC_TOTEM_POOL.resolve(self.cards,self.cards,exclude={m.card_id for m in p.minions})
            if not candidates:raise UnsupportedCard('No eligible basic totem')
            self._summon(owner,self.rng.choice(candidates))
        else: raise UnsupportedCard('Hero power '+k)

    def _equip(self,owner,cid):
        d=self.cards[cid]
        self._break_weapon(owner)
        self.players[owner].weapon=dict(card_id=cid,attack=d['attack'],durability=d.get('durability') or d['health'])
        self._log('equip',player=owner,card=cid)

    def _freeze(self,target):
        if not target: return
        if target<0:
            owner=-target-1; entity=self.players[owner]; attacked=entity.hero_attacks>0; sick=False
        else:
            entity=self._find(target); owner=entity.owner; attacked=entity.attacks>0
            sick=entity.summoned_turn==self.turn and not {'CHARGE','RUSH'}&entity.keywords
        thaw=self.turn+1 if owner!=self.current else self.turn+(2 if attacked or sick else 0)
        entity.frozen_until=max(entity.frozen_until,thaw)
        self._log('freeze',target=target,until=entity.frozen_until)

    def _attack(self,source,target):
        owner=self.current; p=self.players[owner]
        if self._secret_event('attack',owner,source=source,target=target): return
        attacker=self._find(source) if source>0 else None
        weapon_id=p.weapon['card_id'] if p.weapon else None
        attack=attacker.attack if attacker else self._hero_attack(owner)
        defender=self._find(target) if target>0 else None
        # A hero's weapon is active only on that hero's own turn.
        retaliation=defender.attack if defender else 0
        sk=set(attacker.keywords) if attacker else set(self.cards[p.weapon['card_id']].get('mechanics',[])) if p.weapon else set()
        dk=set(defender.keywords) if defender else set()
        self._log('attack',player=owner,source=source,target=target)
        if attacker: attacker.attacks+=1; attacker.keywords.discard('STEALTH')
        else: p.hero_attacks+=1
        with self._damage_batch():
            dealt=self._damage(target,attack,'POISONOUS' in sk)
            returned=self._damage(source,retaliation,'POISONOUS' in dk)
            if 'LIFESTEAL' in sk: self._heal(self.hero_id(owner),dealt)
            if 'LIFESTEAL' in dk: self._heal(self.hero_id(1-owner),returned)
        if not attacker and p.weapon:
            p.weapon['durability']-=1
            if p.weapon['durability']<=0: self._break_weapon(owner)
        if not attacker:
            self._queue_event('hero_attack',owner=owner,target=target)
            for op in WEAPON_TRIGGERS.get(weapon_id,[]):
                self._effect(op,dict(owner=owner,source=None,target=target,bonus=0,lifesteal=False))
        self._settle()

    def _play(self,action):
        owner=self.current; p=self.players[owner]
        card=next(c for c in p.hand if c.uid==action.source); cid=card.card_id; d=self.cards[cid]
        outcast=card.uid in (p.hand[0].uid,p.hand[-1].uid); combo=p.cards_played>0
        cost=self._cost(card,owner); source=None
        p.cost_effects[:]=[e for e in p.cost_effects if not self._discount_matches(e,card)]
        if cid not in RULES and cid not in PASSIVE and cid not in PLAYABLE_TOKENS and cid not in LOCATION_RULES: raise UnsupportedCard(cid)
        p.hand.remove(card); p.mana-=cost
        self._log('play',player=owner,card=cid,target=action.target,position=action.position)
        source=None
        if d['type']=='SPELL' and self._secret_event('before_spell',owner):
            return
        if has_school(d,'FIRE'): p.fire_spell_played=True
        if d['type']=='MINION': source=self._summon(owner,cid,action.position,card.attack_bonus,card.health_bonus)
        elif d['type']=='LOCATION': source=self._place_location(owner,cid,action.position)
        elif d['type']=='WEAPON': self._equip(owner,cid)
        elif d['type']!='SPELL': raise UnsupportedCard('Card type '+d['type'])
        context=dict(owner=owner,source=source,target=action.target,spell=d['type']=='SPELL',bonus=self._spell_damage(owner) if d['type']=='SPELL' else 0,lifesteal='LIFESTEAL' in d.get('mechanics',[]),outcast=outcast,combo=combo)
        operations=RULES.get(cid,('none',[]))[1]
        if cid in CHOICES:
            selected=CHOICES[cid] if action.choices==(-1,) else [CHOICES[cid][action.choices[0]]]
            operations=[op for _,_,ops in selected for op in ops]
            if action.choices==(-1,) and cid=='CORE_EX1_154':
                operations=[('damage',4),('draw',1)]
            elif action.choices==(-1,) and cid=='CORE_EX1_160':
                operations=[('summon','EX1_160t',1),('board_buff',1,1)]
        self._start_play_effects(operations,context)
        p.overload_next+=d.get('overload',0); p.cards_played+=1
        context=(cid,owner,source,cost)
        if self.pending_choice: self.pending_play=context
        else: self._after_play(context)

    def _deal_effect(self,target,amount,ctx):
        if not target: return 0
        if target>0 and not any(m.uid==target for p in self.players for m in p.minions): return 0
        dealt=self._damage(target,amount+ctx.get('bonus',0))
        if ctx.get('lifesteal'): self._heal(self.hero_id(ctx['owner']),dealt)
        return dealt

    def _effect(self,op,ctx):
        owner=ctx['owner']; p=self.players[owner]; q=self.players[1-owner]
        target=ctx.get('target',0); source=ctx.get('source'); name=op[0]
        if self._system_effect(op,ctx): return
        if name in ('damage','combo_damage'):
            if name=='damage' or ctx.get('combo'): self._deal_effect(target,op[1],ctx)
        elif name=='damage_own_hero': self._deal_effect(self.hero_id(owner),op[1],ctx)
        elif name=='heal':
            if target: self._heal(target,op[1])
        elif name=='heal_own_hero': self._heal(self.hero_id(owner),op[1])
        elif name=='armor': p.armor+=op[1]
        elif name in ('draw','draw_empty','outcast_draw'):
            if name=='draw' or (name=='draw_empty' and not p.hand) or (name=='outcast_draw' and ctx.get('outcast')):
                for _ in range(op[1]):
                    self._draw(owner)
                    if self._check_heroes(): break
        elif name=='hero_attack': p.temporary_attack+=op[1]
        elif name=='weapon_buff': p.weapon['attack']+=op[1]
        elif name=='temporary_mana': p.mana=min(10,p.mana+op[1])
        elif name in ('summon','combo_summon'):
            if name=='summon' or ctx.get('combo'):
                require_fixed_cards((op[1],),self.cards)
                for _ in range(op[2]): self._summon(owner,op[1])
        elif name=='raise_corpses':
            # Raise only what fits: failed summons must not consume extra corpses.
            count=min(op[2],p.corpses,7-len(p.board))
            p.corpses-=count
            if count: self._log('spend_corpses',player=owner,amount=count)
            for _ in range(count): self._summon(owner,op[1])
        elif name=='tomb_guardians':
            summoned=[self._summon(owner,'RLK_118t3') for _ in range(2)]
            summoned=[m for m in summoned if m is not None]
            if summoned and p.corpses>=4:
                p.corpses-=4
                self._log('spend_corpses',player=owner,amount=4)
                for m in summoned: m.keywords.add('REBORN')
        elif name=='death_summon':
            for offset in range(op[2]):
                self._summon(owner,op[1],min(ctx['death_position']+offset,len(p.board)))
        elif name=='draw_both':
            # Finish both draws before terminal resolution (including fatigue).
            self._draw(owner); self._draw(1-owner)
        elif name=='draw_tribe':
            self._draw(owner,lambda card: has_tribe(card,op[1]))
        elif name=='draw_unspent_mana':
            if p.mana>0: self._draw(owner)
        elif name=='buff_random_other':
            others=[m for m in p.minions if m is not source]
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
                m=self._find(target); self._heal(target,m.max_health-m.health)
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
                    if m.attack<=op[1]: m.health=0
        elif name=='destroy_large':
            for player in self.players:
                for m in player.minions:
                    if m.attack>=op[1]: m.health=0
        elif name=='health_one':
            for player in self.players:
                for m in player.minions: m.health=m.max_health=1
        elif name=='area_damage':
            groups={'enemy_minions':[m.uid for m in q.minions], 'enemies':[self.hero_id(1-owner)]+[m.uid for m in q.minions],
                    'all_characters':self._characters(), 'all_minions':[m.uid for player in self.players for m in player.minions], 'other_minions':[m.uid for player in self.players for m in player.minions if source is None or m.uid!=source.uid]}
            with self._damage_batch():
                for uid in groups[op[1]]: self._deal_effect(uid,op[2],ctx)
        elif name=='area_heal':
            for uid in [self.hero_id(owner)]+[m.uid for m in p.minions]: self._heal(uid,op[1])
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
                if self.cards[c.card_id]['type']=='MINION' and (name=='hand_buff' or 'TAUNT' in self.cards[c.card_id].get('mechanics',[])):
                    c.attack_bonus+=op[1]; c.health_bonus+=op[2]
        elif name=='board_buff':
            for m in p.minions: self._buff(m,op[1],op[2])
        elif name=='board_keyword':
            for m in p.minions: m.keywords.add(op[1])
        elif name=='grave_strength':
            spent=5 if p.corpses>=5 else 0; p.corpses-=spent
            for m in p.minions: self._buff(m,3 if spent else 1,0)
        elif name=='blood_tap':
            spent=2 if p.corpses>=2 else 0; p.corpses-=spent
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
                if 0<=i<len(p.board) and not isinstance(p.board[i],Location): p.board[i].keywords.add('TAUNT')
        elif name=='other_murloc_health':
            for m in p.minions:
                if m is not source and has_tribe(self.cards[m.card_id],'MURLOC'): self._buff(m,0,op[1])
        elif name=='shadow_hand_buff':
            if any(has_school(self.cards[c.card_id],'SHADOW') for c in p.hand): self._buff(source,op[1],op[2])
        elif name=='discard':
            for _ in range(op[1]):
                if p.hand:
                    c=self.rng.choice(p.hand); p.hand.remove(c); self._log('discard',player=owner,card=c.card_id)
        elif name=='remove_enemy_top':
            if q.deck: self._log('remove_deck_card',player=1-owner,card=q.deck.pop())
        elif name=='random_shield_taunt':
            if p.minions: self.rng.choice(p.minions).keywords.update({'DIVINE_SHIELD','TAUNT'})
        elif name=='beast_weapon_durability':
            if any(has_tribe(self.cards[m.card_id],'BEAST') for m in p.minions): p.weapon['durability']+=op[1]
        elif name=='destroy_random_enemy':
            if q.minions: self.rng.choice(q.minions).health=0
        else: raise UnsupportedCard('Effect opcode not implemented: '+name)

    def observe(self,viewer,include_events=True):
        observation=super().observe(viewer,include_events)
        for owner,(p,public) in enumerate(zip(self.players,observation['players'])):
            public.update(hero_class=p.hero_class,hero_attack=self._hero_attack(owner),frozen=p.frozen_until>=0,
                          locked_mana=p.locked_mana,overload_next=p.overload_next,cards_played=p.cards_played,
                          secret_count=len(p.secrets),fire_spell_played=p.fire_spell_played)
            public['next_power_increase']=p.next_power_increase
            public['hero_power_cost']=self._power_cost(owner)
            public['timed_cost_increases']=deepcopy(p.timed_cost_increases)
            if owner==viewer:
                public['secrets']=[c.card_id for c in p.secrets]
                public['cost_effects']=deepcopy(p.cost_effects)
        if self.pending_choice:
            observation['pending_choice']=(
                dict(owner=self.pending_choice['owner'],kind=self.pending_choice['kind'],
                     options=[{'card_id':o['card_id']} for o in self.pending_choice['options']])
                if viewer==self.pending_choice['owner']
                                           else {'owner':self.pending_choice['owner'],'waiting':True})
        else: observation['pending_choice']=None
        for c in self.players[viewer].hand:
            public=next(h for h in observation['players'][viewer]['hand'] if h['uid']==c.uid)
            public['cost']=self._cost(c,viewer)
            public['cost_delta']=getattr(c,'cost_delta',0)
            if c.card_id in CHOICES: public['choices']=[b[0] for b in CHOICES[c.card_id]]
        # A played secret's identity is hidden even though its play is public.
        for event in observation['events']:
            if event.get('event')=='play' and event.get('player')!=viewer and event.get('card') in SECRETS:
                event['card']='SECRET'
        return observation
