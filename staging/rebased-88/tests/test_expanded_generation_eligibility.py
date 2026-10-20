"""Generation exclusion rules preserve hand generation and physical selection."""
import unittest
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.generation import request_matches
from expanded.generation_cards import pool,random_cards,discover
from engine.cards import UnsupportedCard

class GenerationEligibilityTests(unittest.TestCase):
 def setUp(self):self.fx=fixtures.GenerationTests();self.g=self.fx.game()
 def test_colossal_can_be_generated_in_hand_but_not_randomly_on_board(self):
  req=pool(card_type='MINION',minimum=6,maximum=6);cid='CATA_139'
  self.assertTrue(request_matches(req,self.g.cards[cid],'MAGE'))
  self.fx.install(self.g,req,[cid]);state=self.g.rng.getstate()
  op=random_cards(req,destination='board')
  self.assertEqual(op[1].excluded_mechanic,'COLOSSAL')
  with self.assertRaises(UnsupportedCard):self.g._generation_candidates(op[1],0)
  self.assertEqual(self.g.rng.getstate(),state);self.assertFalse(self.g.players[0].board)
  self.fx.run_ops(self.g,[random_cards(req)])
  self.assertEqual([c.card_id for c in self.g.players[0].hand],[cid])
 def test_board_discover_uses_same_exclusion(self):
  req=pool(card_type='MINION');op=discover(req,destination='board')
  self.assertFalse(request_matches(op[1],self.g.cards['CATA_550'],'MAGE'))
  self.fx.install(self.g,op[1],['CATA_550'])
  with self.assertRaises(UnsupportedCard):self.fx.run_ops(self.g,[op])
  self.assertIsNone(self.g.pending_choice)
 def test_regular_quests_excluded_but_sidequest_remains_eligible(self):
  req=pool(card_type='SPELL')
  self.assertFalse(request_matches(req,self.g.cards['TLC_460'],'MAGE'))
  from standard.catalog import load_catalog
  sidequest=next(c for c in load_catalog() if c['id']=='TLC_EVENT_400')
  self.assertTrue(request_matches(req,sidequest,'MAGE'))
 def test_all_three_rune_cards_excluded_from_generation(self):
  records=[c for c in cards.registry().values() if sum(c.get('runeCost',{}).values())>=3]
  self.assertTrue(records)
  for c in records:self.assertFalse(request_matches(pool(),c,'DEATHKNIGHT'),c['id'])
 def test_existing_physical_deck_quest_is_still_discoverable(self):
  self.g.players[0].deck=['TLC_460'];self.g._discover_deck(0)
  self.assertEqual([o['card_id'] for o in self.g.pending_choice['options']],['TLC_460'])
  self.g.step(Action('choose',choices=(0,)))
  self.assertEqual(self.g.players[0].hand[0].card_id,'TLC_460')

if __name__=='__main__':unittest.main()
