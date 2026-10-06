import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card

class TrackerTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('ROGUE',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def test_batch_counts_once_and_cost_floors_at_zero(self):
        g=self.game();c=Card(g._new_id(),'TLC_520');self.assertEqual(g._cost(c,0),6)
        g._record_deck_insertion(0,0,10,'shuffle');self.assertEqual(g._cost(c,0),5)
        for _ in range(7):g._record_deck_insertion(0,0,1,'shuffle')
        self.assertEqual(g._cost(c,0),0)
    def test_trade_and_other_actor_destination_excluded(self):
        g=self.game();g._record_deck_insertion(0,0,1,'trade');g._record_deck_insertion(0,1,1,'shuffle');g._record_deck_insertion(1,0,1,'shuffle')
        self.assertEqual(g._own_shuffle_count(0),0)
    def test_real_shuffle_reorders_entire_deck_and_counts(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029','CS3_025'];c=Card(g._new_id(),'CORE_WON_351');c.attack_bonus=2;g.players[0].hand=[c]
        with patch.object(g.rng,'shuffle',side_effect=lambda cards:cards.reverse()) as shuffle:
            clean=g._shuffle_hand_card(0,c)
        self.assertEqual(shuffle.call_count,1);self.assertEqual(g.players[0].deck,[clean,'CS3_025','CORE_CS2_029'])
        self.assertEqual(clean.attack_bonus,0);self.assertEqual(g._own_shuffle_count(0),1)
    def test_actual_trade_does_not_discount_tracker(self):
        g=self.game();c=Card(g._new_id(),'CORE_SW_066');g.players[0].hand=[c];g.step(Action('trade',source=c.uid))
        self.assertEqual(g._cost(Card(g._new_id(),'TLC_520'),0),6)
    def test_discounted_play_retains_rush_and_pays_cost(self):
        g=self.game();g._record_deck_insertion(0,0,1,'shuffle');c=Card(g._new_id(),'TLC_520');g.players[0].hand=[c];g.players[0].mana=5
        enemy=g._summon(1,'CS3_025');g.step(Action('play',c.uid,position=0));m=g.players[0].minions[0]
        self.assertEqual(g.players[0].mana,0);self.assertIn(Action('attack',m.uid,enemy.uid),g.legal_actions())
        self.assertNotIn(Action('attack',m.uid,-2),g.legal_actions())
