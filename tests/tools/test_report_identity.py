import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('stress_tool',ROOT/'tools/stress_candidate.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ReportIdentityTests(unittest.TestCase):
    def test_later_run_cannot_replace_earlier_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            first=module.save_report(root,dict(fingerprint='a'*64,games=11))
            second=module.save_report(root,dict(fingerprint='a'*64,games=22))
            self.assertNotEqual(first['run_id'],second['run_id'])
            self.assertEqual(json.loads(Path(first['report_path']).read_text())['games'],11)
            self.assertEqual(json.loads((root/'summary.json').read_text())['run_id'],second['run_id'])
            self.assertEqual(list(root.glob('*.tmp')),[])
    def test_report_input_is_not_mutated(self):
        with tempfile.TemporaryDirectory() as tmp:
            original=dict(fingerprint='b'*64)
            saved=module.save_report(Path(tmp),original)
            self.assertNotIn('run_id',original)
            self.assertEqual(json.loads(Path(saved['report_path']).read_text()),saved)

class FailureIdentityTests(unittest.TestCase):
    def test_repeated_seed_preserves_both_failure_replays(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);case=dict(fingerprint='a'*64,game_seed=71,actions=[{'kind':'end'}])
            first=module.save_failure(root,case);original=first.read_bytes()
            case['actions'].append({'kind':'end'})
            second=module.save_failure(root,case)
            self.assertNotEqual(first,second);self.assertEqual(first.read_bytes(),original)
            self.assertEqual(json.loads(second.read_text()),case)
    def test_collision_never_overwrites_existing_replay(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as tmp:
            case=dict(fingerprint='b'*64,game_seed=1,actions=[])
            with patch.object(module.uuid,'uuid4',return_value=SimpleNamespace(hex='fixed')):
                path=module.save_failure(Path(tmp),case);original=path.read_bytes()
                with self.assertRaises(FileExistsError):module.save_failure(Path(tmp),case)
                self.assertEqual(path.read_bytes(),original)

class ObservationValidatorTests(unittest.TestCase):
    def game(self,leak=False,bad_actions=False,nonserializable=False):
        from types import SimpleNamespace
        def observe(viewer,include_events=False):
            players=[{},{}]
            if leak:players[1-viewer]['hand']=[]
            return dict(players=players,legal_actions=[{'kind':'choose'}] if bad_actions else [],
                        events=[object()] if nonserializable else [])
        return SimpleNamespace(pending_choice=None,phase='play',current=0,
                               legal_actions=lambda:[],observe=observe)
    def test_private_zone_leak_rejected(self):
        with self.assertRaises(AssertionError):module.validate_observations(self.game(leak=True))
    def test_wrong_actions_rejected(self):
        with self.assertRaises(AssertionError):module.validate_observations(self.game(bad_actions=True))
    def test_unserializable_event_rejected(self):
        with self.assertRaises(TypeError):module.validate_observations(self.game(nonserializable=True),include_events=True)

class FeatureValidatorTests(unittest.TestCase):
    def game(self):
        import sys
        sys.path.insert(0,str(ROOT/'staging/rebased-88'))
        from expanded import Game,random_deck
        return Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
    def test_mulligan_features_are_checked_without_state_changes(self):
        game=self.game();before=json.dumps(game.observe(0),sort_keys=True);rng=game.rng.getstate()
        self.assertEqual(module.validate_features(game),len(game.legal_actions()))
        self.assertEqual(json.dumps(game.observe(0),sort_keys=True),before);self.assertEqual(game.rng.getstate(),rng)
    def test_terminal_game_needs_no_candidate_rows(self):
        from types import SimpleNamespace
        self.assertEqual(module.validate_features(SimpleNamespace(terminal=True)),0)
    def test_bad_shape_and_nonfinite_features_are_rejected(self):
        from unittest.mock import patch
        game=self.game();count=len(game.legal_actions())
        for rows in ([],[{'bad':float('nan')}] * count):
            with patch('expanded.features.encode_decision',return_value=rows):
                with self.assertRaises(AssertionError):module.validate_features(game)
