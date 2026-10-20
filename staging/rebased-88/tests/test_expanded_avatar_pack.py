"""Avatar execution fixtures; distribution weights are explicit test inputs.

Hand-space behavior: Blizzard 31.2 patch notes,
https://hearthstone.blizzard.com/en-us/news/24163459/31-2-patch-notes
These fixtures do not claim to reproduce the client's pack probability law.
"""
import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from engine.cards import UnsupportedCard

class AvatarPackTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
 def contract(self,ids):
  self.g.standard_pack_contract=dict(source='ordered test fixture',outcomes=((1,tuple(ids)),))
 def run_pack(self):self.fx.run_ops(self.g,(('standard_pack',),))
 def test_full_hand_has_no_hand_entry_or_burn(self):
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  held=tuple(self.p.hand);mana=self.p.mana;played=self.p.cards_played
  self.contract(['CORE_EX1_162']*5)
  with patch.object(self.g,'_add',side_effect=AssertionError('pack entered hand')):
   self.run_pack()
  self.assertEqual(tuple(self.p.hand),held)
  self.assertEqual(len(self.p.minions),5)
  self.assertEqual(len({m.uid for m in self.p.minions}),5)
  self.assertEqual((self.p.mana,self.p.cards_played),(mana,played))
 def test_full_board_does_not_skip_later_spells(self):
  for _ in range(7):self.g._summon(0,'CORE_EX1_162')
  self.contract(['CORE_EX1_162']*4+['CORE_CS2_029'])
  before=sum(p.health for p in self.g.players)+sum(m.health for p in self.g.players for m in p.minions)
  self.run_pack()
  after=sum(p.health for p in self.g.players)+sum(m.health for p in self.g.players for m in p.minions)
  self.assertLess(after,before)
  self.assertFalse(self.p.hand)
 def test_all_possible_outcomes_are_preflighted_before_rng(self):
  self.g.standard_pack_contract=dict(source='fixture',outcomes=((1000,('CORE_EX1_162',)*5),(1,('UNKNOWN_PACK_CARD',)*5)))
  before=self.g.rng.getstate();held=tuple(self.p.hand);board=tuple(self.p.minions)
  with self.assertRaises(UnsupportedCard):self.run_pack()
  self.assertEqual(self.g.rng.getstate(),before)
  self.assertEqual(tuple(self.p.hand),held);self.assertEqual(tuple(self.p.minions),board)
 def test_explicit_distribution_required(self):
  self.g.standard_pack_contract=None
  before=self.g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'distribution'):self.run_pack()
  self.assertEqual(self.g.rng.getstate(),before)
 def test_invalid_weights_and_pack_sizes_reject_before_rng(self):
  for weight,ids in ((True,('CORE_EX1_162',)*5),(0,('CORE_EX1_162',)*5),(1,('CORE_EX1_162',)*4)):
   with self.subTest(weight=weight,size=len(ids)):
    self.g.standard_pack_contract=dict(source='fixture',outcomes=((weight,ids),));before=self.g.rng.getstate()
    with self.assertRaises(UnsupportedCard):self.run_pack()
    self.assertEqual(self.g.rng.getstate(),before)

if __name__=='__main__':unittest.main()
