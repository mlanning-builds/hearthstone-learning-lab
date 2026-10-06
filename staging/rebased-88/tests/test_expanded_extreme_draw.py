import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card

class ExtremeDrawTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=[];p.mana=p.max_mana=10
    def kill(self,silenced=False):
        m=self.g._summon(0,'CS3_024')
        if silenced:self.g._silence(m)
        m.health=0;self.g._settle()
    def test_highest_minion_ignores_more_expensive_spells(self):
        self.p.deck=['CORE_CS2_179','CS3_024','CORE_EX1_312'];self.kill()
        self.assertEqual(self.p.hand[0].card_id,'CS3_024');self.assertEqual(self.p.deck,['CORE_CS2_179','CORE_EX1_312'])
    def test_no_matching_minion_does_not_cause_fatigue(self):
        for deck in ([],['CORE_CS2_029']):
            self.p.deck=list(deck);health=self.p.health;fatigue=self.p.fatigue
            self.kill();self.assertEqual(self.p.hand,[]);self.assertEqual((self.p.health,self.p.fatigue),(health,fatigue))
    def test_ties_select_physical_deck_entries(self):
        self.p.deck=['CS3_024','CORE_CS2_179','CS3_024']
        with patch.object(self.g.rng,'choice',wraps=self.g.rng.choice) as choose:self.kill()
        self.assertEqual(choose.call_args.args[0],[0,2]);self.assertEqual(len(self.p.deck),2)
    def test_modified_deck_card_keeps_stats_and_cost(self):
        c=Card(self.g._new_id(),'CORE_CS2_179');c.cost_delta=10;c.attack_bonus=2;c.health_bonus=3
        self.p.deck=[c,'CS3_024'];self.kill()
        self.assertIs(self.p.hand[0],c);self.assertEqual((c.cost_delta,c.attack_bonus,c.health_bonus),(10,2,3))
    def test_full_hand_burns_selected_card(self):
        self.p.hand=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(10)]
        self.p.deck=['CORE_CS2_179','CS3_024'];self.kill()
        self.assertEqual(self.p.deck,['CORE_CS2_179']);self.assertEqual(len(self.p.hand),10)
    def test_silence_suppresses_draw(self):
        self.p.deck=['CS3_024'];self.kill(True);self.assertEqual(self.p.deck,['CS3_024']);self.assertEqual(self.p.hand,[])
    def test_shared_lowest_branch_and_invalid_mode(self):
        self.p.deck=['CS3_024','CORE_CS2_179']
        context=dict(owner=0,source=None,target=0)
        self.g._effect(('draw_extreme_cost',(('type','eq','MINION'),),'lowest'),context)
        self.assertEqual(self.p.hand[0].card_id,'CORE_CS2_179')
        with self.assertRaises(ValueError):self.g._effect(('draw_extreme_cost',(),'unknown'),context)
