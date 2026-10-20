"""Physical top-deck execution uses the same orientation as drawing."""
import unittest
from unittest.mock import patch
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded.automatic_cards import split_automatic_card, place_automatic_card
import test_expanded_generation as fixtures


class AutomaticDeckOrderTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixtures.GenerationTests(); self.g=self.fx.game()
        self.p=self.g.players[0]

    def run_top(self,count):
        self.fx.run_ops(self.g,[('automatic_top',count)])

    def test_top_is_last_physical_card_and_stats_survive(self):
        bottom=Card(self.g._new_id(),'CORE_CS2_188')
        top=Card(self.g._new_id(),'CORE_EX1_162'); top.attack_bonus=3
        self.p.deck=[bottom,top]; self.run_top(1)
        self.assertEqual(self.p.deck,[bottom])
        self.assertEqual(self.p.minions[0].card_id,top.card_id)
        self.assertEqual(self.p.minions[0].attack,self.g.cards[top.card_id]['attack']+3)

    def test_three_cards_execute_top_to_bottom_without_draw_or_payment(self):
        self.p.deck=['CORE_CS2_188','CORE_EX1_012','CORE_EX1_162']
        self.p.mana=0; before=len(self.g.events)
        self.run_top(3)
        self.assertEqual([m.card_id for m in self.p.minions],['CORE_EX1_162','CORE_EX1_012','CORE_CS2_188'])
        self.assertEqual(self.p.deck,[]); self.assertEqual(self.p.hand,[])
        self.assertEqual(self.p.mana,0); self.assertEqual(self.p.cards_played,0)
        self.assertFalse(any(e['event']=='draw' for e in self.g.events[before:]))

    def test_spell_consumes_top_and_keeps_bottom(self):
        self.p.deck=['CORE_EX1_162','TOKEN_COIN']; self.p.mana=0
        self.run_top(1)
        self.assertEqual(self.p.mana,1); self.assertEqual(self.p.deck,['CORE_EX1_162'])
        self.assertEqual(self.p.spells_turn,[])

    def test_next_top_is_selected_after_previous_card_effect(self):
        self.p.deck=['CORE_EX1_162','TOKEN_COIN']
        original=self.g._cast_spell_effect
        def effect(op,ctx):
            if op[0]=='internal_spell_complete':self.p.deck.append('CORE_CS2_188')
            return original(op,ctx)
        with patch.object(self.g,'_cast_spell_effect',side_effect=effect):self.run_top(2)
        self.assertEqual([m.card_id for m in self.p.minions],['CORE_CS2_188'])
        self.assertEqual(self.p.deck,['CORE_EX1_162'])

    def test_unsupported_top_is_rejected_before_consumption(self):
        self.p.deck=['TOKEN_COIN','UNKNOWN']; state=self.g.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.run_top(1)
        self.assertEqual(self.p.deck,['TOKEN_COIN','UNKNOWN'])
        self.assertEqual(self.g.rng.getstate(),state)

    def test_changed_top_rejected_by_physical_identity(self):
        card=Card(self.g._new_id(),'CORE_EX1_162'); self.p.deck=[card]
        context=dict(owner=0,source=None,target=0)
        first,_=split_automatic_card(self.g,('automatic_top',1),context)
        self.p.deck.append('TOKEN_COIN')
        with self.assertRaises(UnsupportedCard):place_automatic_card(self.g,first,context)
        self.assertEqual(self.p.deck,[card,'TOKEN_COIN'])

    def test_empty_deck_does_not_fatigue(self):
        self.p.deck=[]; health=self.p.health
        self.run_top(3); self.assertEqual(self.p.health,health)
