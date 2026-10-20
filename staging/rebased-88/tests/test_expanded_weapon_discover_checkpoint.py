"""Weapon choices retain a resolution frame across lethal combat damage."""
import unittest
import test_expanded_generation as fixtures
from expanded import Action


class WeaponChoiceCheckpointTests(unittest.TestCase):
 def test_staff_discover_after_lethal_attack_then_deathrattle(self):
  game=fixtures.GenerationTests().game();p,q=game.players
  p.hero_class='DRUID'
  game._equip(0,'JAIL_875')
  victim=game._summon(1,'CORE_EX1_012');victim.health=1
  action=next(a for a in game.legal_actions() if a.kind=='attack' and a.source==-1 and a.target==victim.uid)
  game.step(action)
  self.assertIsNotNone(game.pending_choice)
  self.assertTrue(game._event_frames or game.pending_frame or game._death_frame)
  game.assert_invariants()
  game.step(next(a for a in game.legal_actions() if a.kind=='choose'))
  self.assertNotIn(victim,q.minions)
  self.assertTrue(any(e['event']=='death' and e['entity']==victim.uid for e in game.events))
  game.assert_invariants()

if __name__=='__main__':unittest.main()
