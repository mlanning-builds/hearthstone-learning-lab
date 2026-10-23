"""Scripted reproductions of pilot mutation/discover failures; no gameplay runs."""
import unittest
from unittest.mock import patch
from expanded import Action
from expanded.game import Card
from expanded.cards import DEATH_EFFECTS
from expanded.generation_cards import pool
from expanded.generation_extensions import RULES
import test_expanded_generation as fixtures

class PilotEngineRepairs(unittest.TestCase):
    def setUp(self):self.helper=fixtures.GenerationTests();self.g=self.helper.game()
    def apply(self,op):self.g._effect(op,dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def test_dragon_discount_initializes_optional_modifier_and_stacks(self):
        dragon=Card(self.g._new_id(),'CATA_556');other=Card(self.g._new_id(),'CORE_CS2_179')
        self.g.players[0].hand=[dragon,other];self.assertFalse(hasattr(dragon,'cost_delta'))
        self.apply(('historical_mutation_dragons_hand',1,1,1));self.apply(('historical_mutation_dragons_hand',1,1,1))
        self.assertEqual((dragon.cost_delta,dragon.attack_bonus,dragon.health_bonus),(-2,2,2))
        self.assertFalse(hasattr(other,'cost_delta'));self.assertEqual(other.attack_bonus,0)
        self.assertEqual(self.g._cost(dragon,0),0)
    def test_zone_discount_accepts_bare_deck_ids_and_fresh_hand_cards(self):
        self.g.players[0].hand=[Card(self.g._new_id(),'CATA_556')];self.g.players[0].deck=['CATA_556']
        self.apply(('historical_mutation_discount_zones',('hand','deck'),(('tribe','DRAGON'),),2))
        self.assertEqual(self.g.players[0].hand[0].cost_delta,-2)
        self.assertIsInstance(self.g.players[0].deck[0],Card);self.assertEqual(self.g.players[0].deck[0].cost_delta,-2)
    def test_highest_cost_discount_initializes_selected_card_only(self):
        low=Card(self.g._new_id(),'CORE_CS2_179');high=Card(self.g._new_id(),'CORE_CS2_029')
        self.g.players[0].hand=[low,high]
        self.apply(('historical_mutation_discount_extreme',(('type','SPELL'),),1))
        self.assertEqual(high.cost_delta,-1);self.assertFalse(hasattr(low,'cost_delta'))
    def test_discover_summoned_deathrattle_receives_live_board_position(self):
        left=self.g._summon(0,'CORE_CS2_179')
        request=RULES['DINO_415'][1][0][1];cid='CORE_EX1_110'
        self.helper.install(self.g,request,[cid]);self.helper.run_ops(self.g,RULES['DINO_415'][1])
        self.g.step(Action('choose',choices=(0,)))
        board=self.g.players[0].board
        self.assertEqual([m.card_id for m in board],['CORE_CS2_179','TOKEN_BAINE',cid])
        self.assertIs(board[0],left);self.assertNotIn(cid,self.g.players[0].death_history)
        self.assertEqual(self.g.players[0].corpses,0)
    def test_live_trigger_keeps_multi_summon_order_and_board_cap(self):
        for _ in range(4):self.g._summon(0,'CORE_CS2_179')
        m=self.g._summon(0,'CORE_EX1_110')
        with patch.dict(DEATH_EFFECTS,{'CORE_EX1_110':[('death_summon','EDR_851t',3)]}):
            # CORE_EX1_110 uses a special printed operation; use attached operations to test the extra summons.
            m.attached_death_effects=[('death_summon','EDR_851t',3)]
            self.apply(('generation_trigger_live_deathrattle',m.uid));self.g._settle(allow_event_choices=True)
        self.assertEqual(len(self.g.players[0].board),7);self.assertIn(m,self.g.players[0].board)
        self.assertEqual(self.g.players[0].corpses,0)
    def test_departed_source_trigger_fizzles_without_summoning(self):
        m=self.g._summon(0,'CORE_EX1_110');self.g.players[0].board.remove(m)
        self.apply(('generation_trigger_live_deathrattle',m.uid));self.g._settle()
        self.assertEqual(self.g.players[0].board,[])
