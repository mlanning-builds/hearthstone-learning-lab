"""Shared board slots with separate minion and location behavior."""
from copy import deepcopy
from dataclasses import asdict
from .locations import Location
from .permanents import Permanent, PERMANENT_IDS


class Battlefield:
    def _find(self, uid):
        for p in self.players:
            for m in p.minions:
                if m.uid==uid:return m
        raise ValueError('No minion with this entity ID.')

    def _characters(self):
        return [-1,-2]+[m.uid for p in self.players for m in p.minions]

    def _public_entity(self, entity):
        if isinstance(entity,Permanent):
            return dict(uid=entity.uid,card_id=entity.card_id,owner=entity.owner,
                        type='PERMANENT',ready=entity.used_turn!=self.players[entity.owner].turns_taken)

        if isinstance(entity,Location):
            return dict(**asdict(entity),type='LOCATION',ready=self.turn>=entity.ready_turn)
        return dict(**{k:v for k,v in asdict(entity).items() if k!='keywords'},
                    keywords=sorted(self._effective_keywords(entity)),type='DORMANT' if entity.dormant else 'MINION')

    def observe(self, viewer, include_events=True):
        if viewer not in (0, 1):
            raise ValueError('Viewer must be 0 or 1.')
        players = []
        for owner, p in enumerate(self.players):
            public = dict(health=p.health, armor=p.armor, mana=p.mana, max_mana=p.max_mana,
                          corpses=p.corpses, fatigue=p.fatigue, hand_count=len(p.hand),
                          deck_count=len(p.deck), power_used=p.power_used, hero_attacks=p.hero_attacks,
                          weapon=deepcopy(p.weapon),
                          board=[self._public_entity(m) for m in p.board])
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
            assert 0 <= p.mana <= p.mana_capacity and 0 <= p.max_mana <= p.mana_capacity
            assert p.corpses >= 0 and p.armor >= 0
            if p.weapon:
                assert p.weapon['durability'] > 0
            ids.extend(c.uid for c in p.hand)
            ids.extend(m.uid for m in p.board)
            if not self.terminal:
                # A decision inside an event can suspend before the death
                # checkpoint; mortally wounded entities still await removal.
                suspended_resolution = self.pending_choice is not None and bool(
                    self._event_frames or self._death_frame or self._turn_frame or self.pending_frame)
                assert all(m.health <= m.max_health and m.attack >= 0 and m.attack_deficit <= 0 and
                           (m.attack == 0 or m.attack_deficit == 0) and
                           (m.health > 0 or suspended_resolution) for m in p.minions)
                assert all(m.durability>0 for m in p.locations)
                assert all(obj.card_id in PERMANENT_IDS and obj.owner==self.players.index(p) for obj in p.permanents)
        assert len(ids) == len(set(ids))
