import unittest
from expanded.historical_colossal import LAYOUTS
import test_expanded_generation as fixtures

class BehemothDuplicateTests(unittest.TestCase):
 def test_multiple_bodies_choose_oldest_not_parent_or_board_edge(self):
  g=fixtures.GenerationTests().game();p,q=g.players
  first=g._summon(0,'TSC_216');second=g._summon(0,'TSC_216')
  lure=next(m for m in p.minions if m.card_id=='TSC_216t')
  p.board.remove(first);p.board.append(first)
  enemy=g._summon(1,'CS2_231');before=(first.health,second.health)
  g._start_play_effects([('historic_behemoth_lure',)],dict(owner=0,source=lure,target=0,bonus=0,lifesteal=False))
  g._settle(allow_event_choices=True)
  self.assertEqual((first.health,second.health),(before[0]-1,before[1]))
  self.assertFalse(q.minions)
 def test_lure_does_not_follow_enemy_behemoth(self):
  g=fixtures.GenerationTests().game();p,q=g.players
  g._summon(1,'TSC_216');lure=g._summon(0,'TSC_216t')
  before=[(m.uid,m.health) for m in q.minions]
  g._start_play_effects([('historic_behemoth_lure',)],dict(owner=0,source=lure,target=0,bonus=0,lifesteal=False))
  g._settle(allow_event_choices=True)
  self.assertEqual(before,[(m.uid,m.health) for m in q.minions])
