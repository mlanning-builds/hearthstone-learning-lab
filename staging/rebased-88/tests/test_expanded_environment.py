import unittest
from expanded import random_deck
from expanded.environment import PolicyEnvironment

class PolicyEnvironmentTests(unittest.TestCase):
    def decks(self):return [random_deck('MAGE',31),random_deck('DEATHKNIGHT',53)]
    def test_full_standard_default_is_blocked(self):
        with self.assertRaisesRegex(RuntimeError,'Full Standard is not ready'):PolicyEnvironment()
    def test_reset_and_action_sequence_are_reproducible(self):
        a=PolicyEnvironment(experimental=True);b=PolicyEnvironment(experimental=True)
        x=a.reset(self.decks(),seed=13,max_actions=12);y=b.reset(self.decks(),seed=13,max_actions=12)
        for _ in range(8):
            self.assertEqual(x,y)
            x=a.step(0,revision=x['revision']);y=b.step(0,revision=y['revision'])
        self.assertEqual(x,y)
    def test_actor_switches_and_opponent_hand_is_hidden(self):
        env=PolicyEnvironment(experimental=True);d=env.reset(self.decks(),seed=13,max_actions=12)
        actor=d['actor'];self.assertNotIn('hand',d['observation']['players'][1-actor])
        d=env.step(0,revision=d['revision']);self.assertNotEqual(actor,d['actor'])
        self.assertNotIn('hand',d['observation']['players'][1-d['actor']])
    def test_stale_and_invalid_actions_do_not_change_state(self):
        env=PolicyEnvironment(experimental=True);d=env.reset(self.decks(),seed=13,max_actions=12)
        with self.assertRaises(ValueError):env.step(-1,revision=d['revision'])
        self.assertEqual(d,env.decision())
        new=env.step(0,revision=d['revision'])
        with self.assertRaises(ValueError):env.step(0,revision=d['revision'])
        self.assertEqual(new,env.decision())
        env.reset(self.decks(),seed=13,max_actions=12)
        with self.assertRaises(ValueError):env.step(0,revision=new['revision'])
    def test_budget_is_truncation_not_a_draw_or_win(self):
        env=PolicyEnvironment(experimental=True);d=env.reset(self.decks(),seed=13,max_actions=1)
        d=env.step(0,revision=d['revision'])
        self.assertTrue(d['truncated']);self.assertFalse(d['terminated'])
        self.assertEqual(d['rewards'],[0,0]);self.assertEqual(d['actions'],[])
        with self.assertRaises(RuntimeError):env.step(0,revision=d['revision'])
    def test_policy_cannot_mutate_game_through_returned_payload(self):
        env=PolicyEnvironment(experimental=True);d=env.reset(self.decks(),seed=13,max_actions=12)
        d['observation']['players'][d['actor']]['health']=-100
        d['actions'].clear()
        fresh=env.decision();self.assertEqual(fresh['observation']['players'][fresh['actor']]['health'],30)
        self.assertTrue(fresh['actions'])
