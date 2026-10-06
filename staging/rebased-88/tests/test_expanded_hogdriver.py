import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HogdriverTests(unittest.TestCase):
    def game(self,deck):
        g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        g.players[0].deck=list(deck);return g
    def play(self,g):
        c=Card(g._new_id(),'JAIL_462');g.players[0].hand.append(c);g.step(Action('play',c.uid,position=0))
        return g.players[0].minions[0]
    def test_two_minions_enable_immediate_hero_attack(self):
        g=self.game(['CORE_WON_351','CORE_EX1_319']);m=self.play(g)
        self.assertIn('CHARGE',m.keywords);self.assertIn(Action('attack',m.uid,-2),g.legal_actions())
        self.assertEqual(len(g.players[0].hand),2);self.assertEqual(g.players[0].deck,[])
    def test_mixed_types_in_either_order_do_not_grant_charge(self):
        for deck in (['CORE_CS2_029','CORE_WON_351'],['CORE_WON_351','CORE_CS2_029']):
            g=self.game(deck);m=self.play(g);self.assertNotIn('CHARGE',m.keywords)
    def test_missing_draws_do_not_satisfy_condition(self):
        for deck,health in (([],27),(['CORE_WON_351'],29)):
            g=self.game(deck);m=self.play(g);self.assertNotIn('CHARGE',m.keywords);self.assertEqual(g.players[0].health,health)
    def test_lethal_fatigue_stops_sequence(self):
        g=self.game([]);g.players[0].health=1;m=self.play(g)
        self.assertTrue(g.terminal);self.assertEqual(g.players[0].fatigue,1);self.assertNotIn('CHARGE',m.keywords)
    def test_summoning_does_not_draw_or_grant_charge(self):
        g=self.game(['CORE_WON_351','CORE_EX1_319']);m=g._summon(0,'JAIL_462')
        self.assertEqual(len(g.players[0].deck),2);self.assertNotIn('CHARGE',m.keywords)
    def test_silence_removes_charge(self):
        g=self.game(['CORE_WON_351','CORE_EX1_319']);m=self.play(g);g._silence(m)
        self.assertNotIn(Action('attack',m.uid,-2),g.legal_actions())
