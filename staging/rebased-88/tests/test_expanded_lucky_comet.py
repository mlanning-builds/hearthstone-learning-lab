"""Lucky Comet repeats Combo bodies without duplicating unrelated Battlecries."""
import unittest
from expanded import Action
import test_expanded_generation as fixtures

class LuckyCometTests(unittest.TestCase):
 def setUp(self):self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
 def play(self,cid,target=0):
  card=self.g._add(0,cid)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid and a.target==target))
 def test_native_combo_damage_repeats_at_distinct_boundaries(self):
  self.p.cards_played=1;self.p.historical_comet_charges=1
  self.play('CORE_EX1_134',-2)
  self.assertEqual(self.q.health,24);self.assertEqual(self.p.historical_comet_charges,0)
 def test_multiple_comets_are_consumed_by_the_same_next_minion(self):
  self.p.cards_played=1;self.p.historical_comet_charges=2
  self.play('CORE_EX1_134',-2)
  self.assertEqual(self.q.health,24);self.assertEqual(self.p.historical_comet_charges,0)
  self.p.mana=10;self.play('CORE_EX1_134',-2);self.assertEqual(self.q.health,21)
 def test_combo_discount_does_not_duplicate_generated_mask(self):
  self.p.cards_played=1;self.p.historical_comet_charges=1
  self.play('DINO_427')
  self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.hand[0].cost_delta,-4)
 def test_combo_weapon_buff_applies_twice_to_one_weapon(self):
  self.p.cards_played=1;self.p.historical_comet_charges=1
  self.play('TLC_516')
  self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.hand[0].attack_bonus,4)
 def test_inactive_combo_still_consumes_next_minion_enchantment(self):
  self.p.cards_played=0;self.p.historical_comet_charges=1
  self.play('CORE_EX1_134')
  self.assertEqual(self.q.health,30);self.assertEqual(self.p.historical_comet_charges,0)
 def test_private_eye_repeats_the_replacement_combo_program(self):
  self.p.cards_played=1;self.p.historical_comet_charges=1
  from engine.game import Card
  ids=('CORE_EX1_289','CORE_EX1_287','EX1_294','EX1_295')
  self.p.deck=[Card(self.g._new_id(),cid) for cid in ids]
  self.play('REV_826')
  self.assertEqual(len(self.p.secrets),4);self.assertFalse(self.p.deck)
