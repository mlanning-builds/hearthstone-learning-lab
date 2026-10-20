from expanded.static_metadata import thaw
import unittest
from unittest.mock import patch
from copy import deepcopy
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded import conditional_discover as cd
from engine.cards import UnsupportedCard

class ConditionalDiscoverTests(unittest.TestCase):
    def setUp(self):
        self.helper=fixtures.GenerationTests();self.g=self.helper.game()
        d=thaw(self.g.cards['CS3_025']);d.update(id='DEMON_TEST',dbfId=-99771,races=['DEMON'],cost=5)
        self.g.cards[d['id']]=d
        patcher=patch.dict(cards.RULES,{'DEMON_TEST':('none',[])})
        patcher.start();self.addCleanup(patcher.stop)
    def start(self):
        self.helper.install(self.g,cd.DEMON,['DEMON_TEST'])
        self.helper.run_ops(self.g,cd.LOCATION_EFFECTS['TIME_446'])
    def choose(self):
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='choose'))
    def test_registered_complete_pool_opens_choice_before_discount(self):
        self.assertIn('TIME_446',cards.COLLECTIBLE_IDS)
        self.helper.run_ops(self.g,cd.LOCATION_EFFECTS['TIME_446'])
        self.assertIsNotNone(self.g.pending_choice)
        self.assertFalse(self.g.players[0].cost_effects)
    def test_choice_before_discount_and_next_minion_only(self):
        self.start();self.assertFalse(self.g.players[0].cost_effects);self.choose()
        p=self.g.players[0];c=p.hand[0];self.assertEqual(self.g._cost(c,0),1)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertFalse(p.cost_effects)
    def test_minion_in_deck_blocks_discount(self):
        self.g.players[0].deck.append('CS3_025');self.start();self.choose()
        self.assertFalse(self.g.players[0].cost_effects)
    def test_empty_deck_qualifies(self):
        self.g.players[0].deck=[];self.start();self.choose()
        self.assertEqual(self.g.players[0].cost_effects[0]['set_cost'],1)
    def test_clone_pending_choice(self):
        self.start();clone=deepcopy(self.g);a=next(a for a in self.g.legal_actions() if a.kind=='choose')
        self.g.step(a);clone.step(a);self.assertEqual(self.g.observe(0),clone.observe(0))
