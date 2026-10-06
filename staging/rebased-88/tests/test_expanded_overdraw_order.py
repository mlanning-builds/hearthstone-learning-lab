import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from engine.game import Card
class OverdrawOrderTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p=self.g.players[0];self.p.overdraw_return_active=True
  self.cached=[Card(self.g._new_id(),cid) for cid in ('TOKEN_COIN','CORE_EX1_162','CORE_CS2_029')]
  self.p.overdraw_cache=list(self.cached)
 def test_random_selection_can_return_last_physical_card_first(self):
  for _ in range(9):self.g._add(0,'TOKEN_COIN')
  # Adding itself can open recovery checkpoints; install cache after setup.
  self.p.overdraw_cache=list(self.cached);self.p.hand=self.p.hand[:9]
  with patch.object(self.g.rng,'randrange',return_value=2) as choose:self.g._recover_overdraw()
  self.assertIs(self.p.hand[-1],self.cached[2]);choose.assert_called_once_with(3);self.assertEqual(self.p.overdraw_cache,self.cached[:2])
 def test_returned_physical_buffs_are_preserved(self):
  self.p.overdraw_cache=[self.cached[0]];self.cached[0].cost_delta=-2;self.g._recover_overdraw();self.assertIs(self.p.hand[0],self.cached[0]);self.assertEqual(self.p.hand[0].cost_delta,-2)
 def test_all_cards_return_without_duplication(self):
  self.g._recover_overdraw();self.assertEqual({c.uid for c in self.p.hand},{c.uid for c in self.cached});self.assertFalse(self.p.overdraw_cache)
 def test_no_space_does_not_consume_rng(self):
  self.p.hand=[Card(self.g._new_id(),'TOKEN_COIN') for _ in range(10)];state=self.g.rng.getstate();self.g._recover_overdraw();self.assertEqual(self.g.rng.getstate(),state);self.assertEqual(len(self.p.overdraw_cache),3)
