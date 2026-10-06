"""Closed-pool, turn-based environment. See docs/simulator.md for scope.

Agent interface: observe(viewer), legal_actions(), step(action), rewards().
Never pass the mutable Game object to an agent: it contains private state.
"""
from dataclasses import dataclass, field, asdict
from copy import deepcopy
import random
from typing import Optional

from lab import validate
from .cards import SUPPORTED, UnsupportedCard, registry


@dataclass(frozen=True)
class Action:
    kind: str
    source: int = 0
    target: int = 0
    position: int = -1
    choices: tuple = ()


@dataclass
class Card:
    uid: int
    card_id: str
    attack_bonus: int = 0
    health_bonus: int = 0


@dataclass
class Minion:
    uid: int
    card_id: str
    owner: int
    attack: int
    health: int
    max_health: int
    keywords: set = field(default_factory=set)
    attacks: int = 0
    summoned_turn: int = 0
    expires: bool = False


@dataclass
class Player:
    deck: list
    starting_deck: list
    runes: tuple
    hand: list = field(default_factory=list)
    board: list = field(default_factory=list)
    health: int = 30
    armor: int = 0
    mana: int = 0
    max_mana: int = 0
    corpses: int = 0
    fatigue: int = 0
    power_used: bool = False
    hero_attacks: int = 0
    weapon: Optional[dict] = None


TARGETS = {
    'CORE_CS2_189': 'character', 'CORE_EX1_011': 'character',
    'CORE_UNG_084': 'character', 'CORE_ULD_191': 'friendly_minion',
    'RLK_958': 'friendly_undead', 'CORE_EDR_002': 'friendly_undead',
    'RLK_024': 'minion',
}
# Cards without an immediate on-play effect; their keywords/deathrattles are
# explicitly implemented elsewhere. No unknown card receives a vanilla fallback.
PASSIVE = {
    'CORE_CS2_179', 'Core_CS2_200', 'CORE_EX1_096', 'CORE_EX1_110',
    'CORE_GIL_558', 'CORE_GVG_085', 'CORE_LOOT_137', 'CORE_LOOT_413',
    'CORE_NEW1_023', 'CORE_SW_068', 'CORE_ULD_723', 'CS3_038', 'RLK_511', 'RLK_067',
}


class Game:
    VERSION = 'dk-subset-0.1'

    def __init__(self, decks, profiles, seed=0, first_player=0, max_turns=89, record=True):
        if len(decks) != 2 or len(profiles) != 2 or first_player not in (0, 1):
            raise ValueError('Provide two decks/profiles and first_player 0 or 1.')
        if type(max_turns) is not int or not 1 <= max_turns <= 89:
            raise ValueError('max_turns must be between 1 and 89.')
        self.cards = registry()
        pool = [c for cid, c in self.cards.items() if cid in SUPPORTED]
        for deck, profile in zip(decks, profiles):
            unknown = set(deck) - SUPPORTED
            if unknown:
                raise UnsupportedCard('Unsupported cards: ' + ', '.join(sorted(unknown)))
            errors = validate(deck, pool, profile)
            if errors:
                raise ValueError('; '.join(errors))
        self.seed = seed
        self.rng = random.Random(seed)
        self.uid = 0
        self.players = []
        for deck, profile in zip(decks, profiles):
            shuffled = list(deck)
            self.rng.shuffle(shuffled)
            self.players.append(Player(shuffled, list(deck), tuple(profile)))
        self.first_player = first_player
        self.current = first_player
        self.phase = 'mulligan'
        self.mulligan_done = set()
        self.turn = 0
        self.max_turns = max_turns
        self.terminal = False
        self.winner = None
        self.end_reason = None
        self.record = record
        self.events = []
        self.history = []
        for owner in (first_player, 1-first_player):
            for _ in range(3 if owner == first_player else 4):
                self._draw(owner, private=True)

    def _new_id(self):
        self.uid += 1
        return self.uid

    def _log(self, event, **details):
        if self.record:
            self.events.append(dict(turn=self.turn, event=event, **details))

    def _draw(self, owner, predicate=None, private=False):
        p = self.players[owner]
        if predicate is None:
            index = len(p.deck)-1
        else:
            options = [i for i, cid in enumerate(p.deck) if predicate(self.cards[cid])]
            if not options:
                return
            index = self.rng.choice(options)
        if index < 0:
            p.fatigue += 1
            self._damage(self.hero_id(owner), p.fatigue)
            self._log('fatigue', player=owner, damage=p.fatigue)
            return
        cid = p.deck.pop(index)
        if len(p.hand) == 10:
            self._log('burn', player=owner, card=cid)
        else:
            p.hand.append(Card(self._new_id(), cid))
            if not private:
                self._log('draw', player=owner)

    @staticmethod
    def hero_id(owner):
        return -owner-1

    def _find(self, uid):
        for p in self.players:
            for m in p.board:
                if m.uid == uid:
                    return m
        raise ValueError('No minion with this entity ID.')

    def _characters(self):
        return [-1, -2] + [m.uid for p in self.players for m in p.board]

    def _targets(self, cid, owner):
        mode = TARGETS.get(cid)
        if not mode:
            return [0]
        targets = self._characters()
        if mode == 'minion':
            targets = [uid for uid in targets if uid > 0]
        elif mode.startswith('friendly'):
            targets = [m.uid for m in self.players[owner].board
                       if mode != 'friendly_undead' or 'UNDEAD' in self.cards[m.card_id].get('races', [])]
        if self.cards[cid]['type'] == 'SPELL':
            targets = [uid for uid in targets if uid < 0 or 'ELUSIVE' not in self._find(uid).keywords]
        return targets or ([0] if self.cards[cid]['type'] == 'MINION' else [])

    def _attack_targets(self, m=None):
        enemy = self.players[1-self.current]
        taunts = [x.uid for x in enemy.board if 'TAUNT' in x.keywords]
        targets = taunts or [self.hero_id(1-self.current)] + [x.uid for x in enemy.board]
        if m and m.summoned_turn == self.turn and 'CHARGE' not in m.keywords:
            if 'RUSH' not in m.keywords:
                return []
            targets = [uid for uid in targets if uid > 0]
        return targets

    def legal_actions(self):
        if self.terminal:
            return []
        p = self.players[self.current]
        if self.phase == 'mulligan':
            ids = [c.uid for c in p.hand]
            return [Action('mulligan', choices=tuple(uid for i, uid in enumerate(ids) if mask & (1 << i)))
                    for mask in range(1 << len(ids))]
        actions = [Action('end')]
        for c in p.hand:
            data = self.cards[c.card_id]
            if data['cost'] > p.mana or (data['type'] == 'MINION' and len(p.board) >= 7):
                continue
            positions = range(len(p.board)+1) if data['type'] == 'MINION' else [-1]
            for target in self._targets(c.card_id, self.current):
                actions.extend(Action('play', c.uid, target, pos) for pos in positions)
        if p.mana >= 2 and not p.power_used and len(p.board) < 7:
            actions.append(Action('power'))
        for m in p.board:
            if m.attacks == 0 and m.attack > 0:
                actions.extend(Action('attack', m.uid, target) for target in self._attack_targets(m))
        if p.weapon and p.weapon['attack'] > 0 and not p.hero_attacks:
            actions.extend(Action('attack', self.hero_id(self.current), t) for t in self._attack_targets())
        return actions

    def step(self, action):
        if action not in self.legal_actions():
            raise ValueError('Illegal action; state was not changed.')
        actor = self.current
        self.history.append(dict(player=actor, action=asdict(action)))
        if action.kind == 'mulligan':
            self._mulligan(action.choices)
        elif action.kind == 'end':
            self._end_turn()
        elif action.kind == 'power':
            p = self.players[actor]
            p.mana -= 2
            p.power_used = True
            self._summon(actor, 'TOKEN_GHOUL', expires=True)
            self._log('hero_power', player=actor)
        elif action.kind == 'attack':
            self._attack(action.source, action.target)
        elif action.kind == 'play':
            self._play(action)
        self._settle()
        self.assert_invariants()
        return self.rewards(), self.terminal

    def _mulligan(self, choices):
        p = self.players[self.current]
        returned = [c.card_id for c in p.hand if c.uid in choices]
        p.hand = [c for c in p.hand if c.uid not in choices]
        # Replacements come before rejected physical cards return to the deck.
        for _ in returned:
            self._draw(self.current, private=True)
        p.deck.extend(returned)
        self.rng.shuffle(p.deck)
        self._log('mulligan', player=self.current, count=len(returned))
        self.mulligan_done.add(self.current)
        if len(self.mulligan_done) == 1:
            self.current = 1-self.current
        else:
            self.players[1-self.first_player].hand.append(Card(self._new_id(), 'TOKEN_COIN'))
            self.phase = 'play'
            self.current = self.first_player
            self._begin_turn()

    def _begin_turn(self):
        self.turn += 1
        p = self.players[self.current]
        p.max_mana = min(10, p.max_mana+1)
        p.mana = p.max_mana
        p.power_used = False
        p.hero_attacks = 0
        for m in p.board:
            m.attacks = 0
        self._log('turn', player=self.current, mana=p.mana,
                  health=[x.health for x in self.players], corpses=[x.corpses for x in self.players])
        self._draw(self.current)
        self._settle()

    def _end_turn(self):
        owner = self.current
        p = self.players[owner]
        for m in list(p.board):
            if m.expires:
                m.health = 0
                self._settle()
                if self.terminal:
                    return
        p.mana = 0
        if self.turn >= self.max_turns:
            self._finish(None, 'turn_limit')
            return
        self.current = 1-owner
        self._begin_turn()

    def _summon(self, owner, cid, position=-1, attack_bonus=0, health_bonus=0, expires=False):
        if cid not in self.cards or self.cards[cid]['type'] != 'MINION':
            raise UnsupportedCard(cid)
        p = self.players[owner]
        if len(p.board) >= 7:
            return None
        c = self.cards[cid]
        health = c['health'] + health_bonus
        m = Minion(self._new_id(), cid, owner, c['attack']+attack_bonus, health, health,
                   set(c.get('mechanics', [])), summoned_turn=self.turn, expires=expires)
        if position < 0:
            position = len(p.board)
        p.board.insert(position, m)
        self._log('summon', player=owner, card=cid, entity=m.uid, position=position)
        return m

    def _damage(self, target, amount, poisonous=False):
        """Return damage dealt, including overkill, or zero if shield prevented it."""
        if amount <= 0:
            return 0
        if target < 0:
            p = self.players[-target-1]
            absorbed = min(p.armor, amount)
            p.armor -= absorbed
            p.health -= amount-absorbed
        else:
            m = self._find(target)
            if 'DIVINE_SHIELD' in m.keywords:
                m.keywords.remove('DIVINE_SHIELD')
                self._log('shield_lost', entity=target)
                return 0
            m.health -= amount
            if poisonous:
                m.health = min(0, m.health)
        self._log('damage', target=target, amount=amount)
        return amount

    def _heal(self, target, amount):
        if target < 0:
            p = self.players[-target-1]
            actual = min(amount, 30-p.health)
            p.health += actual
        else:
            m = self._find(target)
            actual = min(amount, m.max_health-m.health)
            m.health += actual
        self._log('heal', target=target, amount=actual)

    def _buff(self, m, attack, health):
        m.attack += attack
        m.health += health
        m.max_health += health

    def _check_heroes(self):
        dead = [i for i, p in enumerate(self.players) if p.health <= 0]
        if dead and not self.terminal:
            self._finish(None if len(dead) == 2 else 1-dead[0], 'lethal')
        return self.terminal

    def _settle(self):
        while not self._check_heroes():
            dead = sorted([(m, i) for p in self.players for i, m in enumerate(p.board) if m.health <= 0],
                          key=lambda pair: pair[0].uid)
            if not dead:
                return
            for m, _ in dead:
                self.players[m.owner].board.remove(m)
                self.players[m.owner].corpses += 1
                self._log('death', player=m.owner, card=m.card_id, entity=m.uid)
            for m, pos in dead:
                p = self.players[m.owner]
                if m.card_id in ('CORE_EX1_096', 'RLK_708'):
                    self._draw(m.owner)
                elif m.card_id == 'RLK_511':
                    self._draw(m.owner, lambda c: c['type'] == 'SPELL' and c.get('spellSchool') == 'FROST')
                elif m.card_id == 'CORE_EX1_110':
                    self._summon(m.owner, 'TOKEN_BAINE', min(pos, len(p.board)))
                elif m.card_id in ('CORE_LOOT_413', 'CORE_SW_068'):
                    amount = 3 if m.card_id == 'CORE_LOOT_413' else 8
                    p.armor += amount
                    self._log('armor', player=m.owner, amount=amount)
            for m, pos in dead:
                if 'REBORN' in m.keywords:
                    reborn = self._summon(m.owner, m.card_id, min(pos, len(self.players[m.owner].board)))
                    if reborn:
                        reborn.keywords.discard('REBORN')
                        reborn.health = 1

    def _attack(self, source, target):
        p = self.players[self.current]
        attacker = self._find(source) if source > 0 else None
        attack = attacker.attack if attacker else p.weapon['attack']
        retaliation = self._find(target).attack if target > 0 else 0
        defender_keywords = set(self._find(target).keywords) if target > 0 else set()
        source_keywords = set(attacker.keywords) if attacker else {'LIFESTEAL'}
        self._log('attack', player=self.current, source=source, target=target)
        if attacker:
            attacker.attacks += 1
        else:
            p.hero_attacks += 1
        # Both damage amounts are captured before either combatant is removed.
        dealt = self._damage(target, attack, 'POISONOUS' in source_keywords)
        returned = self._damage(source, retaliation, 'POISONOUS' in defender_keywords)
        if 'LIFESTEAL' in source_keywords:
            self._heal(self.hero_id(self.current), dealt)
        if 'LIFESTEAL' in defender_keywords:
            self._heal(self.hero_id(1-self.current), returned)
        if not attacker:
            p.weapon['durability'] -= 1
            if p.weapon['durability'] <= 0:
                self._log('weapon_broken', player=self.current)
                p.weapon = None
        self._settle()

    def _play(self, action):
        owner = self.current
        p = self.players[owner]
        card = next(c for c in p.hand if c.uid == action.source)
        c = self.cards[card.card_id]
        cid = card.card_id
        p.hand.remove(card)
        p.mana -= c['cost']
        self._log('play', player=owner, card=cid, target=action.target, position=action.position)
        m = None
        if c['type'] == 'MINION':
            m = self._summon(owner, cid, action.position, card.attack_bonus, card.health_bonus)
        elif c['type'] == 'WEAPON':
            p.weapon = dict(card_id=cid, attack=c['attack'], durability=c['durability'] or c['health'])
        target = action.target
        if cid in PASSIVE:
            pass
        elif cid == 'TOKEN_COIN':
            p.mana = min(10, p.mana+1)
        elif cid in ('CORE_CS2_189', 'CORE_UNG_084'):
            if target:
                self._damage(target, 1 if cid == 'CORE_CS2_189' else 3)
        elif cid == 'CORE_EX1_011':
            if target:
                self._heal(target, 2)
        elif cid == 'CORE_ULD_191':
            if target:
                self._buff(self._find(target), 0, 2)
        elif cid == 'RLK_958':
            if target:
                self._buff(self._find(target), 2, 0)
        elif cid == 'CORE_ULD_271':
            self._damage(m.uid, 3)
        elif cid == 'CORE_GIL_622':
            self._damage(self.hero_id(1-owner), 3)
            self._heal(self.hero_id(owner), 3)
        elif cid == 'CORE_EX1_506':
            self._summon(owner, 'TOKEN_SCOUT', p.board.index(m)+1)
        elif cid == 'RLK_503':
            p.corpses += 1
            self._log('gain_corpse', player=owner, amount=1)
        elif cid == 'RLK_708':
            self._draw(owner)
        elif cid == 'CORE_RLK_062':
            for _ in range(2):
                copy = self._summon(owner, cid, p.board.index(m)+1,
                                    m.attack-c['attack'], m.max_health-c['health'])
                if copy:
                    copy.health = m.health
                    copy.keywords = set(m.keywords)
        elif cid == 'CORE_RLK_505':
            spent = min(5, p.corpses)
            p.corpses -= spent
            self._log('spend_corpses', player=owner, amount=spent)
            for _ in range(spent):
                targets = [self.hero_id(1-owner)] + [x.uid for x in self.players[1-owner].board]
                self._damage(self.rng.choice(targets), 2)
                self._settle()
                if self.terminal:
                    break
        elif cid == 'CORE_RLK_087':
            enemies = self.players[1-owner].board
            if enemies:
                best = max(x.attack for x in enemies)
                self.rng.choice([x for x in enemies if x.attack == best]).health = 0
        elif cid == 'CORE_EDR_002':
            self._find(target).keywords.add('POISONOUS')
        elif cid == 'RLK_024':
            amount = self._damage(target, 6)
            self._heal(self.hero_id(owner), amount)
        elif cid == 'RLK_048':
            for minion in p.board:
                self._buff(minion, 1, 1)
                minion.keywords.add('ELUSIVE')
        elif cid == 'RLK_707':
            spent = 5 if p.corpses >= 5 else 0
            p.corpses -= spent
            self._log('spend_corpses', player=owner, amount=spent)
            for minion in p.board:
                self._buff(minion, 3 if spent else 1, 0)
        elif cid == 'CORE_RLK_712':
            spent = 2 if p.corpses >= 2 else 0
            p.corpses -= spent
            self._log('spend_corpses', player=owner, amount=spent)
            for hand_card in p.hand:
                if self.cards[hand_card.card_id]['type'] == 'MINION':
                    hand_card.attack_bonus += 2 if spent else 1
                    hand_card.health_bonus += 2 if spent else 1
        elif cid == 'RLK_709':
            for enemy in [self.hero_id(1-owner)] + [x.uid for x in self.players[1-owner].board]:
                self._damage(enemy, 2)
            self._settle()
            if not self.terminal:
                self._draw(owner)
        else:
            raise UnsupportedCard('No on-play implementation for ' + cid)
        self._settle()

    def _finish(self, winner, reason):
        self.terminal = True
        self.phase = 'finished'
        self.winner = winner
        self.end_reason = reason
        self._log('finished', winner=winner, reason=reason)

    def rewards(self):
        if not self.terminal or self.winner is None:
            return (0, 0)
        return (1, -1) if self.winner == 0 else (-1, 1)

    def observe(self, viewer, include_events=True):
        if viewer not in (0, 1):
            raise ValueError('Viewer must be 0 or 1.')
        players = []
        for owner, p in enumerate(self.players):
            public = dict(health=p.health, armor=p.armor, mana=p.mana, max_mana=p.max_mana,
                          corpses=p.corpses, fatigue=p.fatigue, hand_count=len(p.hand),
                          deck_count=len(p.deck), power_used=p.power_used, hero_attacks=p.hero_attacks,
                          weapon=deepcopy(p.weapon),
                          board=[dict(**{k: v for k, v in asdict(m).items() if k != 'keywords'},
                                      keywords=sorted(m.keywords)) for m in p.board])
            if owner == viewer:
                public.update(hand=[asdict(c) for c in p.hand], starting_deck=list(p.starting_deck), runes=list(p.runes))
            players.append(public)
        return dict(version=self.VERSION, viewer=viewer, current_player=self.current, turn=self.turn,
                    phase=self.phase, players=players, terminal=self.terminal, winner=self.winner,
                    events=deepcopy(self.events) if include_events else [],
                    legal_actions=[asdict(a) for a in self.legal_actions()] if viewer == self.current else [])

    def assert_invariants(self):
        ids = []
        for p in self.players:
            assert 0 <= len(p.board) <= 7 and 0 <= len(p.hand) <= 10
            assert 0 <= p.mana <= 10 and 0 <= p.max_mana <= 10
            assert p.corpses >= 0 and p.armor >= 0
            if p.weapon:
                assert p.weapon['durability'] > 0
            ids.extend(c.uid for c in p.hand)
            ids.extend(m.uid for m in p.board)
            if not self.terminal:
                assert all(0 < m.health <= m.max_health and m.attack >= 0 for m in p.board)
        assert len(ids) == len(set(ids))
