import json
import unittest
from expanded import random_deck
from expanded.trajectories import record_episode

class TrajectoryTests(unittest.TestCase):
    def collect(self,policies=None,limit=1):
        decks=[random_deck('MAGE',31),random_deck('WARRIOR',53)]
        return list(record_episode(decks,policies or [lambda d:0]*2,policy_ids=['a','b'],
                                   seed=71,max_actions=limit,experimental=True))
    def test_cap_has_no_terminal_reward_label(self):
        records=self.collect();self.assertEqual([r['record'] for r in records],['episode','decision','outcome'])
        self.assertTrue(records[-1]['truncated']);self.assertIsNone(records[-1]['terminal_rewards'])
        json.dumps(records)
    def test_decision_contains_only_actor_hand(self):
        decision=self.collect()[1];players=decision['observation']['players'];actor=decision['actor']
        self.assertIn('hand',players[actor]);self.assertNotIn('hand',players[1-actor])
        self.assertNotIn('replay_only',decision)
        self.assertEqual(decision['action'],decision['legal_actions'][decision['action_index']])
    def test_policy_mutation_cannot_corrupt_recorded_input(self):
        def mutating(d):
            d['observation']['players'][d['actor']]['health']=-999
            d['actions'].clear()
            return 0
        decision=self.collect([mutating]*2)[1]
        self.assertEqual(decision['observation']['players'][decision['actor']]['health'],30)
        self.assertTrue(decision['legal_actions'])
    def test_completed_game_has_terminal_labels(self):
        def pass_turn(d):return next(i for i,a in enumerate(d['actions']) if a['kind'] in ('mulligan','end'))
        records=self.collect([pass_turn]*2,200);outcome=records[-1]
        self.assertTrue(outcome['terminated']);self.assertFalse(outcome['truncated'])
        self.assertEqual(len(outcome['terminal_rewards']),2)
    def test_same_seed_and_policies_reproduce_records(self):
        self.assertEqual(self.collect(limit=4),self.collect(limit=4))
    def test_save_episode_round_trip_and_no_overwrite(self):
        import hashlib,tempfile
        from pathlib import Path
        from expanded.trajectories import save_episode
        records=self.collect()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'episode.jsonl';receipt=save_episode(path,iter(records))
            self.assertEqual([json.loads(line) for line in path.read_text().splitlines()],json.loads(json.dumps(records)))
            self.assertEqual(receipt['sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
            with self.assertRaises(FileExistsError):save_episode(path,iter(records))
    def test_incomplete_episode_is_not_published(self):
        import tempfile
        from pathlib import Path
        from expanded.trajectories import save_episode
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'episode.jsonl'
            with self.assertRaises(ValueError):save_episode(path,iter(self.collect()[:-1]))
            self.assertEqual(list(Path(tmp).iterdir()),[])
    def test_capped_episode_cannot_be_mislabelled_as_draw(self):
        import tempfile
        from pathlib import Path
        from expanded.trajectories import save_episode
        records=self.collect();records[-1]['terminal_rewards']=[0,0]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):save_episode(Path(tmp)/'bad.jsonl',records)
