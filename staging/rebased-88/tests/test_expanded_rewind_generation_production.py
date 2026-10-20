"""Actual bindings, complete Demon/Beast pools and explicit historical guards."""
import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action
from expanded.game import Card
from expanded import event_generation,conditional_discover
from expanded.cards import RULES
from engine.cards import UnsupportedCard
from standard.catalog import CLASSES

class RewindGenerationProductionTests(unittest.TestCase):
 def setUp(self):self.g=fixtures.GenerationTests().game();self.p=self.g.players[0]
 def play(self,cid):
  c=self.g._enter_hand(0,Card(self.g._new_id(),cid))
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  return c
 def test_tripwire_paid_play_summons_and_shuffles_two_exact_spells(self):
  self.p.deck=[]
  self.play('JAIL_879')
  self.assertEqual(len(self.p.minions),1)
  self.assertEqual(self.g.cards[self.p.minions[0].card_id]['cost'],5)
  self.assertEqual([c.card_id for c in self.p.deck],['JAIL_879t','JAIL_879t'])
  self.assertEqual(self.p.shuffle_history[-1]['count'],2)
 def test_tripwire_draw_casts_without_payment_and_draws_replacement(self):
  self.p.mana=0
  self.p.deck=['TOKEN_COIN','JAIL_879t']
  self.g._draw(0);self.g._settle(allow_event_choices=True)
  self.assertEqual(len(self.p.minions),1)
  self.assertEqual(self.g.cards[self.p.minions[0].card_id]['cost'],5)
  self.assertEqual([c.card_id for c in self.p.hand],['TOKEN_COIN'])
  self.assertEqual(self.p.mana,0)
  self.assertFalse(self.p.played_history)
  self.assertFalse(self.p.deck)
 def test_conditional_discover_keeps_selected_demon_and_arms_next_minion_cost(self):
  self.p.deck=[]
  self.play('TIME_446')
  self.assertIsNone(self.g.pending_choice)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='activate'))
  self.g.step(Action('choose',choices=(0,)))
  c=self.p.hand[-1];d=self.g.cards[c.card_id]
  self.assertIn('DEMON',d.get('races',()))
  self.assertGreaterEqual(d['cost'],5)
  self.assertEqual(self.g._cost(c,0),1)
  self.assertEqual(self.p.discoveries_total,1)
 def test_conditional_discover_with_deck_minion_does_not_arm_cost(self):
  self.p.deck=['CORE_CS2_189']
  self.play('TIME_446')
  self.assertIsNone(self.g.pending_choice)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='activate'))
  self.g.step(Action('choose',choices=(0,)))
  c=self.p.hand[-1]
  self.assertEqual(self.g._cost(c,0),self.g.cards[c.card_id]['cost'])
 def test_demon_and_beast_production_pools_close_for_all_classes(self):
  for hero in CLASSES:
   self.p.hero_class=hero
   self.assertEqual(len(self.g._generation_candidates(conditional_discover.DEMON,0)),22)
   self.assertEqual(len(self.g._generation_candidates(event_generation.BEAST_FIVE,0)),16)
 @patch('expanded.generation_families.reviewed_contract',return_value=None)
 @patch('expanded.generation_catalog.standard_contract',return_value=None)
 @patch('expanded.historical_generation_catalog.historical_contract',return_value=None)
 def test_unreviewed_historical_pool_rolls_back_paid_summon(self,*contracts):
  c=self.g._enter_hand(0,Card(self.g._new_id(),'TIME_711'))
  before=self.g.observe(0);rng=self.g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'membership contract'):
   self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(self.g.observe(0),before)
  self.assertEqual(self.g.rng.getstate(),rng)
