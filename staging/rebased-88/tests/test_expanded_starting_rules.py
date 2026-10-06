import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game,Action,cards
from expanded.game import Card
from expanded.decks import Deck
import test_expanded_generation as fixtures
class StartingRuleTests(unittest.TestCase):
 def game(self,a=(),b=()):
  decks=[Deck('MAGE',tuple(a)+('CORE_CS2_029',)*(30-len(a))),Deck('MAGE',tuple(b)+('CORE_CS2_029',)*(30-len(b)))]
  # These targeted construction fixtures deliberately ignore normal duplicate limits.
  with patch('expanded.game.validate',return_value=[]):return Game(decks,seed=13)
 def test_ysera_increases_both_capacities_not_starting_crystals(self):
  g=self.game(('EDR_000',));self.assertEqual([p.mana_capacity for p in g.players],[15,15]);self.assertEqual([p.max_mana for p in g.players],[0,0])
 def test_two_starting_yseras_stack(self):
  g=self.game(('EDR_000',),('EDR_000',));self.assertEqual([p.mana_capacity for p in g.players],[20,20])
 def test_generated_ysera_has_no_start_effect(self):
  g=fixtures.GenerationTests().game();g._summon(0,'EDR_000');self.assertEqual([p.mana_capacity for p in g.players],[10,10])
 def test_hogger_duplicates_other_legendaries_only(self):
  g=self.game(('JAIL_384','CS3_025','EDR_000'))
  ids=[c.card_id for c in g.players[0].deck+g.players[0].hand];self.assertEqual(len(ids),32);self.assertEqual(ids.count('JAIL_384'),1);self.assertEqual(ids.count('CS3_025'),2);self.assertEqual(ids.count('EDR_000'),2)
  self.assertEqual(g.players[0].mana_capacity,15)
 def test_starting_deck_and_new_copy_provenance(self):
  g=self.game(('JAIL_384','CS3_025'));p=g.players[0]
  self.assertEqual(len(p.starting_deck),30);copies=[c for c in p.deck+p.hand if c.card_id=='CS3_025'];self.assertEqual(len({c.uid for c in copies}),2)
  self.assertEqual(sum(g._started_in_deck(c,0) for c in copies),1)
 def test_no_other_legendaries_no_additions(self):
  p=self.game(('JAIL_384',)).players[0];self.assertEqual(len(p.deck)+len(p.hand),30)
 def fixture(self):
  g=fixtures.GenerationTests().game();g.players[0].mana_capacity=15;return g
 def run_op(self,g,op):fixtures.GenerationTests().run_ops(g,[op])
 def test_growth_past_ten_and_capacity_clamp(self):
  g=self.fixture();p=g.players[0];p.max_mana=14;p.mana=10;self.run_op(g,('gain_full_crystals',3));self.assertEqual((p.max_mana,p.mana),(15,11));g.assert_invariants()
 def test_temporary_mana_respects_new_capacity(self):
  g=self.fixture();p=g.players[0];p.mana=14;self.run_op(g,('temporary_mana',3));self.assertEqual(p.mana,15)
 def test_empty_crystal_growth_respects_capacity(self):
  g=self.fixture();p=g.players[0];p.max_mana=14;self.run_op(g,('empty_crystals','friendly',3));self.assertEqual(p.max_mana,15)
 def test_turn_growth_past_ten(self):
  g=self.fixture();g.players[0].max_mana=10;g.step(Action('end'));g.step(Action('end'));self.assertEqual(g.players[0].max_mana,11)
 def test_ysera_battlecry_gains_filled_crystals(self):
  g=self.fixture();p=g.players[0];p.max_mana=p.mana=10;c=Card(g._new_id(),'EDR_000');p.hand.append(c)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(p.max_mana,13)
  self.assertEqual(p.mana,13-g.cards['EDR_000']['cost'])
 def test_cap_public_and_cloned(self):
  g=self.fixture();self.assertEqual(g.observe(1)['players'][0]['mana_capacity'],15);self.assertEqual(deepcopy(g).players[0].mana_capacity,15)

 def test_full_crystals_after_temporary_mana_never_exceeds_capacity(self):
  g=self.fixture();p=g.players[0];p.max_mana=12;p.mana=15;self.run_op(g,('gain_full_crystals',3));self.assertEqual((p.max_mana,p.mana),(15,15));g.assert_invariants()
