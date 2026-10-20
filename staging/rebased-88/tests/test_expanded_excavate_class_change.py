import unittest
from expanded.historical_excavate import COMMON,RARE,EPIC,CLASS_REWARDS
import test_expanded_generation as fixtures

class ExcavateClassChangeTests(unittest.TestCase):
 def setUp(self):self.g=fixtures.GenerationTests().game();self.p=self.g.players[0]
 def dig(self):
  self.g._start_play_effects([('historical_excavate_dig',False)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
  self.g._settle(allow_event_choices=True)
 def test_class_without_legendary_restarts_after_epic(self):
  self.p.hero_class='PRIEST';self.p.historical_excavate_tier=3
  self.dig();self.assertIn(self.p.hand[-1].card_id,COMMON);self.assertEqual(self.p.historical_excavate_tier,1)
 def test_reward_class_transition_uses_new_class_reward(self):
  self.p.hero_class='ROGUE';self.p.historical_excavate_tier=3
  self.dig();self.assertEqual(self.p.hand[-1].card_id,CLASS_REWARDS['ROGUE']);self.assertEqual(self.p.historical_excavate_tier,0)
 def test_class_without_legendary_keeps_three_tier_cycle(self):
  self.p.hero_class='DRUID'
  for pool in (COMMON,RARE,EPIC,COMMON):
   self.dig();self.assertIn(self.p.hand[-1].card_id,pool)
