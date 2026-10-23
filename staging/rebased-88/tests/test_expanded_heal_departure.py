"""Departed healing targets from the saved continuation failure; scripted rules only."""
import unittest
import test_expanded_generation as fixtures

class HealDepartureTests(unittest.TestCase):
    def test_removed_target_fizzles_without_healing_replacement(self):
        g=fixtures.GenerationTests().game();m=g._summon(0,'CORE_CS2_179');uid=m.uid
        g.players[0].board.remove(m);other=g._summon(0,'CORE_CS2_179');other.health=1
        before=g.rng.getstate()
        self.assertEqual(g._heal(uid,8,healer=0,spell=True),0)
        self.assertEqual(other.health,1);self.assertEqual(g.rng.getstate(),before)
        self.assertTrue(any(e.get('effect')=='heal' and e.get('event')=='effect_fizzled' for e in g.events))
    def test_lethal_damage_then_queued_heal_does_not_raise_or_resurrect(self):
        g=fixtures.GenerationTests().game();m=g._summon(1,'CORE_CS2_179');uid=m.uid
        g._start_play_effects((('damage',20),('heal',8)),dict(owner=0,source=None,target=uid,bonus=0,lifesteal=False))
        self.assertIsNone(g._force_live(uid));g.assert_invariants()
    def test_live_target_and_hero_still_heal(self):
        g=fixtures.GenerationTests().game();m=g._summon(0,'CORE_CS2_179');m.health=1
        self.assertGreater(g._heal(m.uid,2,healer=0),0)
        g.players[0].health=20;self.assertEqual(g._heal(-1,3,healer=0),3)
