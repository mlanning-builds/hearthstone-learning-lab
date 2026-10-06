"""Discover identity is explicit; generic choices/Dredge never advance it."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.generation_cards import pool, discover
from expanded.pools import GenerationPool
from expanded.features import encode_decision, SCHEMA

class DiscoverHistoryTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',1),random_deck('HUNTER',2)],seed=73)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*12;p.mana=p.max_mana=10;p.health=30
        return g
    def ops(self,g,ops):
        g._start_play_effects(ops,dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def choose(self,g):g.step(Action('choose',choices=(0,)))
    def test_offer_does_not_count_before_selection(self):
        g=self.game();g._discover_deck(0)
        self.assertEqual(g.players[0].discoveries_total,0)
        self.choose(g);self.assertEqual((g.players[0].discoveries_this_turn,g.players[0].discoveries_total),(1,1))
    def test_empty_pool_not_discover(self):
        g=self.game();g.players[0].deck=[];g._discover_deck(0)
        self.assertIsNone(g.pending_choice);self.assertEqual(g.players[0].discoveries_total,0)
    def test_burned_selected_card_still_counts(self):
        g=self.game()
        for _ in range(10):g._add(0,'TOKEN_COIN')
        g._discover_deck(0);self.choose(g)
        self.assertEqual(g.players[0].discoveries_total,1);self.assertEqual(len(g.players[0].hand),10)
    def test_scuffle_discount_begins_after_discover(self):
        g=self.game();c=g._enter_hand(0,Card(g._new_id(),'TLC_365'));self.assertEqual(g._cost(c,0),3)
        g._discover_deck(0);self.choose(g);self.assertEqual(g._cost(c,0),0)
    def test_scuffle_discount_applies_to_later_hand_entries(self):
        g=self.game();g._discover_deck(0);self.choose(g)
        c=g._enter_hand(0,Card(g._new_id(),'TLC_365'));self.assertEqual(g._cost(c,0),0)
    def test_scuffle_still_deals_three_damage_at_zero_mana(self):
        g=self.game();g._discover_deck(0);self.choose(g);c=g._enter_hand(0,Card(g._new_id(),'TLC_365'))
        target=g._summon(1,'CORE_CS2_122');before=target.health;g.players[0].mana=0
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target.uid))
        self.assertEqual(target.health,before-3);self.assertEqual(g.players[0].mana,0)
    def test_scuffle_does_not_target_heroes(self):
        g=self.game();g._discover_deck(0);self.choose(g);c=g._enter_hand(0,Card(g._new_id(),'TLC_365'))
        self.assertFalse(any(a.kind=='play' and a.source==c.uid and a.target<0 for a in g.legal_actions()))
    def test_turn_counter_resets_total_remains(self):
        g=self.game();g._discover_deck(0);self.choose(g);g.step(Action('end'))
        self.assertEqual((g.players[0].discoveries_this_turn,g.players[0].discoveries_total),(0,1))
        g.step(Action('end'));c=g._enter_hand(0,Card(g._new_id(),'TLC_365'));self.assertEqual(g._cost(c,0),3)
    def test_opponent_discover_does_not_discount_my_scuffle(self):
        g=self.game();c=g._enter_hand(0,Card(g._new_id(),'TLC_365'));g._discover_deck(1);self.choose(g)
        self.assertEqual(g.players[1].discoveries_total,1);self.assertEqual(g._cost(c,0),3)
    def test_temporary_deck_discover_counts(self):
        g=self.game();self.ops(g,[('temporary_deck_discover',)]);self.choose(g)
        self.assertEqual(g.players[0].discoveries_total,1)
    def test_enemy_top_discover_counts_without_gaining_card(self):
        g=self.game();g.players[1].deck=['CORE_CS2_122'];self.ops(g,[('local_enemy_deck_top',)]);self.choose(g)
        self.assertEqual(g.players[0].discoveries_total,1);self.assertFalse(g.players[0].hand)
    def test_resurrect_discover_counts(self):
        g=self.game();g.players[0].death_history=['CORE_EX1_572'] if 'CORE_EX1_572' in g.cards else [next(cid for cid,d in g.cards.items() if d.get('race')=='DRAGON')]
        self.ops(g,[('local_dead_dragon',)]);self.choose(g)
        self.assertEqual(g.players[0].discoveries_total,1)
    def test_two_deck_copy_choices_count_twice(self):
        g=self.game();self.ops(g,[('zone_choice','friendly','deck','copy'),('zone_choice','enemy','deck','copy')])
        self.choose(g);self.assertEqual(g.players[0].discoveries_total,1)
        self.choose(g);self.assertEqual(g.players[0].discoveries_total,2)
    def test_dredge_does_not_count(self):
        g=self.game();self.ops(g,[('zone_choice','enemy','deck','top')]);self.choose(g)
        self.assertEqual(g.players[0].discoveries_total,0)
    def test_fixed_summon_choice_does_not_count(self):
        g=self.game();self.ops(g,[('choose_fixed_summon',('NEW1_032','NEW1_033','NEW1_034'))]);self.choose(g)
        self.assertEqual(g.players[0].discoveries_total,0)
    def test_generated_discover_uses_same_counter(self):
        g=self.game();r=pool();g._generation_pools={(r,'MAGE'):GenerationPool('test',('TOKEN_COIN',),'synthetic test')}
        self.ops(g,[discover(r)]);self.choose(g);self.assertEqual(g.players[0].discoveries_total,1)
    def test_invalid_choice_cannot_increment_counter(self):
        g=self.game();g._discover_deck(0)
        with self.assertRaises(Exception):g.step(Action('choose',choices=(99,)))
        self.assertEqual(g.players[0].discoveries_total,0)
    def test_public_counter_without_selected_identity(self):
        g=self.game();g._discover_deck(0);self.choose(g)
        view=g.observe(1);self.assertEqual(view['players'][0]['discoveries_total'],1)
        events=[e for e in view.get('events',[]) if e.get('event')=='discover']
        self.assertTrue(events)
        self.assertTrue(all('card' not in e for e in events))
        own=g.observe(0,include_events=False)
        rows=encode_decision(dict(actor=0,observation=own,actions=own['legal_actions']))
        self.assertTrue(any('discoveries_this_turn' in key for key in rows[0]));self.assertEqual(SCHEMA,'visible-action-features-v58')
    def test_tracking_play_lifecycle_counts_once(self):
        g=self.game();card=g._enter_hand(0,Card(g._new_id(),'CORE_DS1_184'))
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid))
        self.assertEqual(g.players[0].discoveries_total,0);self.choose(g)
        self.assertEqual(g.players[0].discoveries_total,1)
        g.observe(0);g.observe(1);g.legal_actions()
        self.assertEqual(g.players[0].discoveries_total,1)
    def test_bottom_reordering_discover_counts(self):
        g=self.game();self.ops(g,[('zone_choice','friendly','deck','draw_bottom')]);self.choose(g)
        self.assertEqual(g.players[0].discoveries_total,1)
