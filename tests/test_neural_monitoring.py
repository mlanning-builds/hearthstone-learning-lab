"""Monitoring, migration and long-run wiring; no live games or weight updates."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

try:
    import torch
except ImportError:
    raise unittest.SkipTest("Optional neural dependencies are not installed")
from hearthstone_sim.neural.evaluation import (
    EvaluationConfig,
    ensure_disjoint,
    result_summary,
    wilson,
    heuristic_action,
    evaluate,
)
from hearthstone_sim.neural.dashboard import Dashboard
from hearthstone_sim.neural.checkpoints import save, load, SCHEMA
from hearthstone_sim.neural.upgrade import LEGACY_CODE, compatible_upgrade
from hearthstone_sim.neural.runner import prepare, run
from hearthstone_sim.neural.model import ModelConfig


def decision(actor=0):
    return dict(
        actor=actor,
        revision=1,
        terminated=False,
        truncated=False,
        actions=[dict(kind="end")],
        observation=dict(
            viewer=actor,
            players=[dict(health=30, board=[], hand=[]), dict(health=20, board=[])],
            legal_actions=[dict(kind="end")],
        ),
    )


class MonitoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)

    def test_wilson_and_caps_are_not_fake_losses(self):
        self.assertIsNone(wilson(0, 0))
        lo, hi = wilson(50, 100)
        self.assertLess(lo, 0.5)
        self.assertGreater(hi, 0.5)
        rows = [dict(terminated=True, truncated=False, reward=r) for r in (1, 0, -1)]
        rows.append(dict(terminated=False, truncated=True, reward=None))
        result = result_summary(rows)
        self.assertEqual(
            (result["wins"], result["draws"], result["losses"], result["capped"]), (1, 1, 1, 1)
        )
        self.assertEqual(result["completed"], 3)
        self.assertAlmostEqual(result["win_rate"], 1 / 3)
        self.assertEqual(result["score"], 0.5)
        self.assertIsNone(result_summary(rows[-1:])["win_rate"])

    def test_monitoring_seed_overlap_rejected(self):
        config = EvaluationConfig(games_per_opponent=4, seed=100)
        with self.assertRaisesRegex(ValueError, "overlap"):
            ensure_disjoint(99, 0, 3, config)
        ensure_disjoint(71, 8, 10000, EvaluationConfig())

    def test_heuristic_uses_visible_lethal_and_mulligan(self):
        d = decision()
        d["observation"]["players"][0]["hero_attack"] = 21
        d["actions"] = [dict(kind="end"), dict(kind="attack", source=-1, target=-2)]
        self.assertEqual(heuristic_action(d, {}), 1)
        d["observation"]["players"][0]["hand"] = [dict(uid=7, cost=5)]
        d["actions"] = [dict(kind="mulligan", choices=[]), dict(kind="mulligan", choices=[7])]
        self.assertEqual(heuristic_action(d, {}), 1)

    def test_evaluation_is_frozen_and_does_not_touch_training_rng(self):
        from hearthstone_sim._bootstrap import activate

        activate()
        network = torch.nn.Linear(2, 1)
        weights = deepcopy(network.state_dict())
        rng_state = torch.get_rng_state().clone()
        terminal = dict(terminated=True, truncated=False, steps=2, rewards=[1, -1])
        with (
            patch("expanded.environment.PolicyEnvironment") as env,
            patch("hearthstone_sim.neural.runner.match_schedule", return_value=("A", "A", 0, 0)),
            patch("hearthstone_sim.neural.runner.policy_action", return_value=(0, -0.5, 0.1)),
        ):
            env.return_value.reset.return_value = decision()
            env.return_value.step.side_effect = [decision(1), terminal] * 4
            report = evaluate(
                network,
                {"anchor": network},
                Mock(),
                {"A": "scripted-deck"},
                {},
                config=EvaluationConfig(games_per_opponent=2),
                max_actions=5,
                emit=lambda *a, **k: None,
            )
        self.assertEqual(report["summary"]["completed"], 4)
        self.assertEqual(report["training_updates"], 0)
        self.assertEqual(report["by_deck"]["A"]["completed"], 4)
        self.assertEqual(set(report["by_opponent"]), {"heuristic", "anchor"})
        self.assertTrue(torch.equal(torch.get_rng_state(), rng_state))
        self.assertTrue(all(torch.equal(v, weights[k]) for k, v in network.state_dict().items()))

    def test_dashboard_has_progress_curve_uncertainty_and_escaped_paths(self):
        ui = Dashboard(10000)
        ui.consume(dict(event="training_progress", done=8, total=10000, eta_seconds=100))
        r = result_summary([dict(terminated=True, truncated=False, reward=1)])
        ui.consume(dict(event="evaluation_finished", global_game=8, by_opponent={"<baseline>": r}))
        ui.checkpoint = "<script>bad</script>"
        html = ui.html()
        self.assertIn("8 / 10,000", html)
        self.assertIn("<svg", html)
        self.assertIn("95% interval", html)
        self.assertNotIn("<script>bad", html)
        self.assertIn("&lt;baseline&gt;", html)

    def test_upgrade_is_explicit_narrow_and_hash_verified(self):
        old = dict(neural_code=LEGACY_CODE, engine="unchanged", model={"width": 128})
        new = dict(old, neural_code="new-monitoring-code")
        self.assertTrue(compatible_upgrade(old, new))
        self.assertFalse(compatible_upgrade(old, dict(new, engine="changed")))
        self.assertFalse(compatible_upgrade(old, dict(new, model={"width": 256})))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "old.pt"
            save(path, dict(schema=SCHEMA, compatibility=old, model={}))
            with self.assertRaisesRegex(ValueError, "mismatch"):
                load(path, new)
            self.assertEqual(load(path, new, allow_code_upgrade=True)["compatibility"], old)
            with self.assertRaisesRegex(ValueError, "mismatch"):
                load(path, dict(new, engine="changed"), allow_code_upgrade=True)

    def test_long_run_checkpoint_cadence_and_monitoring_wiring_without_learning(self):
        evaluation_report = dict(summary={}, by_opponent={"heuristic": result_summary([])})
        model_config = ModelConfig(width=16, heads=2, layers=1, feedforward=32)
        with (
            tempfile.TemporaryDirectory() as folder,
            patch(
                "hearthstone_sim.neural.runner.collect_game",
                return_value=(
                    [{"scripted": True}],
                    dict(truncated=False, terminated=True, reward=1),
                ),
            ),
            patch(
                "hearthstone_sim.neural.runner.update",
                return_value=dict(optimizer_steps=1, samples=1),
            ),
            patch(
                "hearthstone_sim.neural.runner.evaluate", return_value=evaluation_report
            ) as monitor,
        ):
            result = run(
                iterations=3,
                games_per_iteration=1,
                max_actions=5,
                seed=7,
                output=folder,
                model_config=model_config,
                allow_training=True,
                checkpoint_every_iterations=2,
                evaluation=EvaluationConfig(every_iterations=2, games_per_opponent=1),
                emit=lambda e: None,
            )
            directory = Path(result["path"]).parent
            self.assertFalse((directory / "training-000001.pt").exists())
            self.assertTrue((directory / "training-000002.pt").exists())
            checkpoint = load(result["path"], prepare(model_config=model_config)[2])
            self.assertEqual(checkpoint["global_game"], 3)
            self.assertEqual(monitor.call_count, 3)  # baseline, interval, final
            self.assertTrue(checkpoint["evaluation_anchors"])
            self.assertTrue((directory / "monitoring-history.json").exists())
            self.assertEqual(
                len(json.loads((directory / "monitoring-history.json").read_text())), 3
            )


if __name__ == "__main__":
    unittest.main()
