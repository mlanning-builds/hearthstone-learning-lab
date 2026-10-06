"""After-Discover ordering and physical identity across resolution scopes."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import DEATH_EFFECTS
from expanded.generation_cards import discover,pool
from expanded.pools import GenerationPool

class DiscoverFollowupTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',1),random_deck('HUNTER',2)],seed=83)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*12;p.mana=p.max_mana=10;p.health=30
        g._summon(0,'TLC_483')
        return g
    def ops(self,g,ops):g._start_play_effects(ops,dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def choose(self,g):g.step(Action('choose',choices=(0,)))
    def test_discounts_selected_physical_copy_only(self):
        g=self.game();existing=g._enter_hand(0,Card(g._new_id(),'CORE_CS2_029'))
        selected=Card(g._new_id(),'CORE_CS2_029');g.players[0].deck=[selected]
        g._discover_deck(0);self.choose(g)
        self.assertIs(g.players[0].hand[-1],selected);self.assertEqual(g._cost(selected,0),3);self.assertEqual(g._cost(existing,0),4)
    def test_two_vault_breakers_stack(self):
        g=self.game();g._summon(0,'TLC_483');g._discover_deck(0);self.choose(g)
        self.assertEqual(g._cost(g.players[0].hand[0],0),2)
    def test_silenced_breaker_does_not_discount(self):
        g=self.game();g._silence(g.players[0].minions[0]);g._discover_deck(0);self.choose(g)
        self.assertEqual(g._cost(g.players[0].hand[0],0),4)
    def test_other_player_breaker_does_not_discount(self):
        g=self.game();g._discover_deck(1);self.choose(g)
        self.assertEqual(g._cost(g.players[1].hand[0],1),4)
    def test_callback_after_remaining_card_effect(self):
        g=self.game();self.ops(g,[('discover_deck',),('reset_hand_costs',)]);self.choose(g)
        self.assertEqual(g._cost(g.players[0].hand[0],0),3)
    def test_two_discovers_finish_before_callbacks(self):
        g=self.game();self.ops(g,[('discover_deck',),('discover_deck',),('reset_hand_costs',)])
        self.choose(g);self.assertEqual(g._cost(g.players[0].hand[0],0),4)
        self.choose(g);self.assertEqual([g._cost(c,0) for c in g.players[0].hand],[3,3])
    def test_breaker_killed_by_later_effect_no_longer_triggers(self):
        g=self.game();self.ops(g,[('discover_deck',),('destroy_all_minions',)]);self.choose(g)
        self.assertEqual(g._cost(g.players[0].hand[0],0),4)
    def test_burn_does_not_discount_another_copy(self):
        g=self.game()
        for _ in range(10):g._add(0,'CORE_CS2_029')
        g._discover_deck(0);self.choose(g)
        self.assertTrue(all(g._cost(c,0)==4 for c in g.players[0].hand))
        self.assertEqual(g.players[0].discoveries_total,1)
    def test_opponent_hand_copy_discount_leaves_original(self):
        g=self.game();original=g._enter_hand(1,Card(g._new_id(),'CORE_CS2_029'))
        self.ops(g,[('zone_choice','enemy','hand','copy')]);self.choose(g)
        self.assertEqual(g._cost(original,1),4);self.assertEqual(g._cost(g.players[0].hand[0],0),3)
    def test_selected_enemy_deck_card_retains_identity_and_discount(self):
        g=self.game();original=Card(g._new_id(),'CORE_CS2_122');g.players[1].deck=[original]
        self.ops(g,[('local_enemy_deck_top',)]);self.choose(g)
        self.assertIs(g.players[1].deck[-1],original);self.assertEqual(original.cost_delta,-1)
    def test_temporary_selected_card_discount_and_expiry(self):
        g=self.game();self.ops(g,[('temporary_deck_discover',)]);self.choose(g)
        c=g.players[0].hand[0];self.assertEqual(g._cost(c,0),3);self.assertTrue(g._is_temporary(c))
        g.step(Action('end'));self.assertFalse(g.players[0].hand)
    def test_dredge_does_not_discount(self):
        g=self.game();c=Card(g._new_id(),'CORE_CS2_029');g.players[1].deck=[c]
        self.ops(g,[('zone_choice','enemy','deck','top')]);self.choose(g)
        self.assertFalse(hasattr(c,'cost_delta'))
    def test_generated_fixed_cost_then_vault_discount(self):
        g=self.game();r=pool();g._generation_pools={(r,'MAGE'):GenerationPool('fixture',('CORE_CS2_029',),'synthetic test')}
        self.ops(g,[discover(r,set_cost=1)]);self.choose(g)
        self.assertEqual(g._cost(g.players[0].hand[0],0),0)
    def test_event_scope_callback(self):
        g=self.game();g._rule_events.append(('captured_effects',dict(operations=(('discover_deck',),('reset_hand_costs',)),context=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)),[]))
        g._settle(allow_event_choices=True);self.choose(g)
        self.assertEqual(g._cost(g.players[0].hand[0],0),3);self.assertFalse(g._event_frames)
    def test_death_scope_callback(self):
        g=self.game();m=g._summon(0,'EDR_851t')
        with patch.dict(DEATH_EFFECTS,{'EDR_851t':[('discover_deck',),('reset_hand_costs',)]}):
            m.health=0;g._settle(allow_event_choices=True);self.choose(g)
        self.assertEqual(g._cost(g.players[0].hand[0],0),3);self.assertIsNone(g._death_frame)
    def test_turn_scope_callback(self):
        g=self.game();g._schedule_turn_effect(0,'end',0,1,(('discover_deck',),('reset_hand_costs',)))
        g.step(Action('end'));self.choose(g)
        self.assertEqual(g._cost(g.players[0].hand[0],0),3);self.assertEqual(g.current,1)
    def test_catacombs_does_not_cast_when_drawn_card(self):
        g=self.game();g.players[0].deck=['SW_439t']
        self.ops(g,[('temporary_deck_discover',)]);self.choose(g)
        self.assertEqual([c.card_id for c in g.players[0].hand],['SW_439t']);self.assertEqual(len(g.players[0].minions),1)
    def test_catacombs_does_not_summon_when_drawn_card(self):
        g=self.game();g.players[0].deck=['EDR_260t']
        self.ops(g,[('temporary_deck_discover',)]);self.choose(g)
        self.assertEqual([c.card_id for c in g.players[0].hand],['EDR_260t']);self.assertEqual(len(g.players[0].minions),1)
