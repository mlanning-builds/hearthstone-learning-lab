"""Splitting conserves odd values and uses current physical-card state."""
import unittest
from unittest.mock import patch
from engine.game import Card
from expanded.base_stats import base_stats
import test_expanded_generation as fixtures


class PhysicalTransformationTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixtures.GenerationTests(); self.g=self.fx.game(); self.p=self.g.players[0]

    def add(self,cost=5,attack=5,health=5):
        card=Card(self.g._new_id(),'CORE_CS2_188');self.g._enter_hand(0,card)
        self.g._mutation_set_stats(card,0,attack,health);self.g._set_card_cost(card,cost)
        return card

    def split(self):self.fx.run_ops(self.g,[('mutation_split_minion',)])

    def values(self):return [tuple(self.g._card_stat(c,key,0) for key in ('cost','attack','health')) for c in self.p.hand]

    def test_independent_odd_allocations_conserve_each_value(self):
        original=self.add();uid=original.uid
        with patch.object(self.g.rng,'randrange',side_effect=[0,1,0]):self.split()
        self.assertEqual(self.values(),[(2,3,2),(3,2,3)])
        self.assertEqual(self.p.hand[0].uid,uid)
        self.assertNotEqual(self.p.hand[1].uid,uid)

    def test_even_values_need_no_random_rounding(self):
        self.add(8,8,8);before=self.g.rng.getstate();self.split()
        self.assertEqual(self.values(),[(4,4,4)]*2)
        self.assertEqual(self.g.rng.getstate(),before)

    def test_one_health_is_kept_on_both_halves(self):
        self.add(1,1,1)
        with patch.object(self.g.rng,'randrange',side_effect=[0,1]):self.split()
        self.assertEqual(self.values(),[(0,1,1),(1,0,1)])

    def test_zero_attack_and_cost_are_valid(self):
        self.add(0,0,2);self.split();self.assertEqual(self.values(),[(0,0,1)]*2)

    def test_stored_base_override_and_enchantments_are_split(self):
        card=self.add(6,2,2);card.base_stat_override=(8,10)
        card.attack_bonus=2;card.health_bonus=2;self.split()
        self.assertEqual(self.values(),[(3,5,6)]*2)
        self.assertTrue(all(c.base_stat_override==(8,10) for c in self.p.hand))

    def test_crystal_core_current_stats_and_copy_base(self):
        self.p.crystal_core=True;card=self.add(6,8,10);self.split()
        self.assertEqual(self.values(),[(3,4,5)]*2)
        self.assertTrue(all(base_stats(self.g,c,0)==(5,5) for c in self.p.hand))

    def test_payload_is_deep_copied_and_ready_before_hand_entry(self):
        card=self.add(6,8,10);card.rule_state={'stored':[{'value':3}]}
        original=self.g._enter_hand;seen=[]
        def enter(owner,value):
            seen.append(tuple(self.g._card_stat(value,key,owner) for key in ('cost','attack','health')))
            return original(owner,value)
        with patch.object(self.g,'_enter_hand',side_effect=enter):self.split()
        self.assertEqual(seen,[(3,4,5)])
        self.p.hand[1].rule_state['stored'][0]['value']=9
        self.assertEqual(card.rule_state['stored'][0]['value'],3)

    def test_full_hand_burns_second_half_after_splitting_original(self):
        self.add(6,8,10)
        for _ in range(9):self.g._add(0,'TOKEN_COIN')
        self.split();self.assertEqual(len(self.p.hand),10)
        self.assertEqual(self.values()[0],(3,4,5))
        self.assertTrue(any(e['event']=='burn_generated' for e in self.g.events))

    def test_second_split_uses_first_split_stats_and_cost(self):
        self.add(8,8,8);self.split()
        with patch.object(self.g.rng,'choice',return_value=self.p.hand[0]):self.split()
        self.assertEqual(sorted(self.values()),[(2,2,2),(2,2,2),(4,4,4)])

    def test_no_minion_does_not_consume_randomness(self):
        self.g._add(0,'TOKEN_COIN');before=self.g.rng.getstate();self.split()
        self.assertEqual(self.g.rng.getstate(),before);self.assertEqual(len(self.p.hand),1)

    def test_retained_cost_does_not_double_apply_discount(self):
        card=self.add(6,8,10);card.cost_delta=-2
        self.g._mutation_replace_card(card,'CORE_EX1_012',retain_stats=True,retain_cost=True)
        self.assertEqual(self.g._cost(card,0),4);self.assertEqual(card.cost_delta,0)
        self.assertEqual(tuple(self.g._card_stat(card,k,0) for k in ('attack','health')),(8,10))

    def test_retained_stats_respect_persistent_override(self):
        card=self.add(6,2,2);card.base_stat_override=(8,10);card.attack_bonus=2;card.health_bonus=2
        self.g._mutation_replace_card(card,'CORE_EX1_012',retain_stats=True)
        self.assertEqual(tuple(self.g._card_stat(card,k,0) for k in ('attack','health')),(10,12))
