import unittest
from engine.game import Card
from engine.cards import UnsupportedCard
import test_expanded_generation as fixtures
class AutomaticCardTests(unittest.TestCase):
 def setUp(self):self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p=self.g.players[0]
 def run_card(self,cid):
  c=Card(self.g._new_id(),cid);self.fx.run_ops(self.g,[('automatic_card',c,'random')]);return c
 def test_minion_ignores_hand_capacity_and_mana(self):
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.mana=0;self.run_card('CORE_EX1_162');self.assertEqual(len(self.p.minions),1);self.assertEqual(len(self.p.hand),10);self.assertEqual(self.p.mana,0)
 def test_no_paid_play_counter(self):
  before=self.p.cards_played;self.run_card('CORE_EX1_162');self.assertEqual(self.p.cards_played,before)
 def test_physical_buffs_survive(self):
  c=Card(self.g._new_id(),'CORE_EX1_162');c.attack_bonus=3;self.fx.run_ops(self.g,[('automatic_card',c)]);self.assertEqual(self.p.minions[0].attack,self.g.cards[c.card_id]['attack']+3)
 def test_spell_uses_internal_cast(self):
  self.p.mana=2;self.run_card('TOKEN_COIN');self.assertEqual(self.p.mana,3);self.assertEqual(self.p.cards_played,0)
 def test_full_board_does_not_overflow(self):
  for _ in range(7):self.g._summon(0,'CORE_EX1_162')
  self.run_card('CORE_EX1_162');self.assertEqual(len(self.p.board),7)
 def test_attached_zone_card_rejected(self):
  c=self.g._add(0,'TOKEN_COIN')
  with self.assertRaises(UnsupportedCard):self.fx.run_ops(self.g,[('automatic_card',c)])
  self.assertIn(c,self.p.hand)
 def test_unknown_card_rejected(self):
  with self.assertRaises(UnsupportedCard):self.run_card('UNKNOWN')
 def test_location_placement(self):
  self.run_card('CORE_REV_990');self.assertEqual(len(self.p.locations),1);self.assertEqual(self.p.cards_played,0)
 def test_weapon_retains_physical_identity(self):
  c=self.run_card('CS2_082');self.assertIs(self.p.equipped_card,c)
