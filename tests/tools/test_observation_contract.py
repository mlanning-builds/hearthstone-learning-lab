"""Metamorphic checks of policy-visible hidden-zone independence."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'staging/rebased-88'))
from expanded import Game,Action,random_deck
from expanded.game import Card

class ObservationContractTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
    def test_opponent_hidden_hand_identity_and_buffs_do_not_change_view(self):
        before=self.g.observe(0);p=self.g.players[1]
        for c in p.hand:
            c.card_id='Core_CS2_200';c.attack_bonus=7;c.health_bonus=9;c.cost_delta=-2
        self.assertEqual(self.g.observe(0),before)
    def test_hidden_deck_order_does_not_change_either_view(self):
        before=[self.g.observe(i) for i in (0,1)]
        for p in self.g.players:p.deck.reverse()
        self.assertEqual([self.g.observe(i) for i in (0,1)],before)
    def test_observation_reads_do_not_consume_randomness_or_change_histories(self):
        state=self.g.rng.getstate();events=deepcopy(self.g.events);history=deepcopy(self.g.history)
        first=self.g.observe(0)
        for _ in range(5):
            self.g.observe(1);self.assertEqual(self.g.observe(0),first)
        self.assertEqual(self.g.rng.getstate(),state)
        self.assertEqual(self.g.events,events);self.assertEqual(self.g.history,history)
    def test_own_weapon_hand_bonus_is_visible_without_exposing_it_to_opponent(self):
        c=Card(self.g._new_id(),'EDR_457t');self.g.players[0].hand=[c]
        other_before=self.g.observe(1);c.attack_bonus=4
        own=self.g.observe(0)['players'][0]['hand'][0]
        self.assertEqual(own['attack_bonus'],4)
        self.assertEqual(self.g.observe(1),other_before)
    def test_own_hand_cost_matches_play_calculation(self):
        c=Card(self.g._new_id(),'CORE_CS2_029');c.cost_delta=-1
        p=self.g.players[0];p.hand=[c]
        p.cost_effects=[dict(selector='SPELL',amount=2,expires=None)]
        before=deepcopy(p.cost_effects)
        own=self.g.observe(0)['players'][0]['hand'][0]
        self.assertEqual(own['cost'],self.g._cost(c,0));self.assertEqual(own['cost'],1)
        self.assertEqual(own['cost_delta'],-1);self.assertEqual(p.cost_effects,before)
    def test_opponent_owned_choice_actions_are_private_to_owner(self):
        self.g.phase='choice'
        self.g.pending_choice=dict(owner=1,kind='hand_copy',options=[dict(card_id='CORE_CS2_029',uid=101)])
        self.assertEqual(self.g.observe(0)['legal_actions'],[])
        actions=self.g.observe(1)['legal_actions']
        self.assertEqual(len(actions),1);self.assertEqual(actions[0]['kind'],'choose')
    def test_hidden_option_count_does_not_change_waiting_players_view(self):
        self.g.phase='choice'
        self.g.pending_choice=dict(owner=1,kind='hand_copy',options=[dict(card_id='CORE_CS2_029',uid=101)])
        before=self.g.observe(0)
        self.g.pending_choice['options'].append(dict(card_id='CORE_EX1_506',uid=102))
        self.assertEqual(self.g.observe(0),before)
