"""Non-training contracts: no real rollout, search benchmark or optimizer step."""

import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import torch
from hearthstone_sim.neural.model import ModelConfig
from hearthstone_sim.neural.checkpoints import digest
from hearthstone_sim.research.matched_games.models import make_model, with_memory, ARMS
from hearthstone_sim.research.matched_games.budget import validate_config, next_arm, summarize
from hearthstone_sim.research.matched_games.storage import state, persist, restore
from hearthstone_sim.research.matched_games.runner import evaluation_schedule, run
from hearthstone_sim.research.matched_games.search import transition
from hearthstone_sim.research.matched_games.study import ROOT, read_config

E = dict(state=[[(1, 1.0)], [(2, 0.5)]], actions=[[(3, 1.0)], [(4, 1.0)]])
SMALL = ModelConfig(buckets=256, width=8, heads=2, layers=1, feedforward=16)


class EqualTimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)

    def test_all_models_share_legal_action_value_shapes(self):
        for arm in (*ARMS, "transformer"):
            with self.subTest(arm=arm):
                m = make_model(arm, SMALL)
                before = {k: v.clone() for k, v in m.state_dict().items()}
                logits, values = m([dict(E, memory=[E["state"]])])
                self.assertEqual(tuple(logits[0].shape), (2,))
                self.assertEqual(tuple(values.shape), (1,))
                self.assertTrue(torch.isfinite(values).all())
                self.assertTrue(all(torch.equal(before[k], v) for k, v in m.state_dict().items()))

    def test_gru_uses_ordered_observations_and_resets(self):
        torch.manual_seed(1)
        m = make_model("gru", SMALL)
        a = m([dict(E, memory=[[[(8, 1.0)]], [[(9, 1.0)]]])])[1]
        b = m([dict(E, memory=[[[(9, 1.0)]], [[(8, 1.0)]]])])[1]
        self.assertFalse(torch.equal(a, b))
        self.assertTrue(torch.equal(m([E])[1], m([dict(E, memory=[])])[1]))

    def test_memory_snapshot_not_mutable_history(self):
        history = [E["state"]] * 30
        encoded = with_memory(E, history, "gru")
        history.clear()
        self.assertEqual(len(encoded["memory"]), 15)
        self.assertNotIn("memory", with_memory(E, [], "mlp"))

    def test_budget_selects_least_trained_not_most_games(self):
        rows = {a: dict(train_seconds=100.0, games=10000) for a in ARMS}
        rows["gru"] = dict(train_seconds=10.0, games=1)
        self.assertEqual(next_arm(rows, 1800), "gru")
        self.assertIsNone(next_arm(rows, 1))

    def test_default_config_pins_safe_session_hardware_and_all_decks(self):
        cfg = read_config()
        self.assertEqual(cfg["session_seconds"], 7200)
        self.assertEqual(cfg["workers"], 4)
        self.assertEqual(cfg["threads"], 6)
        self.assertEqual(cfg["architectures"], list(ARMS))
        self.assertAlmostEqual(
            cfg["self_play_fraction"] + cfg["older_fraction"] + cfg["heuristic_fraction"], 1.0
        )
        bad = dict(cfg, workers=20)
        with self.assertRaises(ValueError):
            validate_config(bad)

    def test_balanced_common_evaluation_stream(self):
        from types import SimpleNamespace

        decks = {
            f"class-{c}-deck-{j}": SimpleNamespace(hero_class=str(c))
            for c in range(11)
            for j in range(16)
        }
        rows = evaluation_schedule(decks, 44)
        self.assertEqual(len(set(rows)), 44)
        for c in range(11):
            self.assertEqual(sum(decks[a].hero_class == str(c) for a, b, s, f in rows), 4)
        self.assertEqual({(s, f) for a, b, s, f in rows}, {(0, 0), (0, 1), (1, 0), (1, 1)})

    def test_pause_resume_preserves_partial_rollout_and_rng_without_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = state(tmp, "gru")
            m.update(games=1, train_seconds=17.0, pending_games=1)
            payload = dict(
                model={"tensor": torch.tensor([3.0])},
                optimizer={"state": {}},
                pending_samples=[dict(encoded=E)],
                pending_results=[dict(reward=1)],
                shuffle_rng=torch.Generator().get_state(),
            )
            cp = persist(tmp, "gru", m, payload, {"architecture": "gru"})
            again = state(tmp, "gru")
            restored = restore(again, {"architecture": "gru"})
            self.assertEqual(again["games"], 1)
            self.assertEqual(again["train_seconds"], 17.0)
            self.assertEqual(len(restored["pending_samples"]), 1)
            self.assertTrue(torch.equal(restored["shuffle_rng"], payload["shuffle_rng"]))
            self.assertEqual(digest(cp["checkpoint"]["path"]), cp["checkpoint"]["sha256"])

    def test_retention_preserves_milestones_and_previous_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            meta = state(tmp, "mlp")
            payload = {"model": {}, "pending_samples": []}
            for i in range(6):
                meta["train_seconds"] = i + 1
                meta = persist(
                    tmp,
                    "mlp",
                    meta,
                    payload,
                    {},
                    milestone=2 if i == 1 else None,
                    archive=True,
                    league_size=2,
                )
            self.assertLessEqual(len(list((Path(tmp) / "mlp").glob("weights-*.pt"))), 4)
            self.assertTrue(Path(meta["milestones"]["2"]["path"]).exists())
            restore(meta, {})

    def test_errors_and_caps_never_become_losses(self):
        s = summarize([dict(terminated=True, reward=1), dict(failed=True), dict(truncated=True)])
        self.assertEqual(s["completed"], 1)
        self.assertEqual(s["losses"], 0)
        self.assertEqual(s["failed"], 1)
        self.assertEqual(s["capped"], 1)

    def test_explicit_owner_training_gate(self):
        with self.assertRaisesRegex(ValueError, "owner"):
            run()

    def test_public_combat_transition_is_pure_and_shields_work(self):
        def minion(uid, attack, health, keywords=()):
            return dict(
                uid=uid,
                card_id="test",
                type="MINION",
                owner=0,
                attack=attack,
                health=health,
                max_health=health,
                attacks=0,
                summoned_turn=0,
                keywords=list(keywords),
            )

        view = dict(
            viewer=0,
            turn=4,
            events=[],
            players=[
                dict(health=30, armor=0, corpses=0, board=[minion(1, 3, 5)]),
                dict(health=30, armor=0, corpses=0, board=[minion(2, 2, 2, ["DIVINE_SHIELD"])]),
            ],
        )
        action = dict(source=1, target=2)
        after = transition(view, action)
        self.assertEqual(after["players"][0]["board"][0]["health"], 3)
        self.assertEqual(after["players"][1]["board"][0]["health"], 2)
        self.assertFalse(after["players"][1]["board"][0]["keywords"])
        self.assertEqual(view["players"][0]["board"][0]["health"], 5)

    def test_search_module_has_no_private_game_access(self):
        source = (ROOT / "hearthstone_sim/research/matched_games/search.py").read_text()
        tree = ast.parse(source)
        self.assertFalse(
            any(
                isinstance(n, ast.Attribute) and n.attr in ("_game", "rng", "deck", "hand")
                for n in ast.walk(tree)
            )
        )

    def test_notebook_has_valid_syntax_and_separate_training_gate(self):
        nb = json.loads((ROOT / "notebooks/22_model_comparison.ipynb").read_text())
        cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
        self.assertEqual(len(cells), 2)
        for c in cells:
            ast.parse("".join(c["source"]))
        self.assertNotIn("'--train'", "".join(cells[0]["source"]))
        self.assertIn("'--train'", "".join(cells[1]["source"]))


if __name__ == "__main__":
    unittest.main()


class MockedTurnTests(unittest.TestCase):
    def test_resume_does_not_recollect_completed_games_or_reset_clocks(self):
        from hearthstone_sim._bootstrap import activate

        activate()
        from hearthstone_sim.research.matched_games import runner as r

        cfg = read_config()
        cfg = dict(cfg, games_per_batch=4, turn_seconds=20, workers=4, budget_mode="time")
        updates = []
        slots = []
        clock = [0.0]

        def now():
            clock[0] += 1
            return clock[0]

        class Future:
            def __init__(self, task):
                self.task = task

            def result(self):
                slots.append(self.task["metadata"]["slot"])
                return [
                    dict(
                        encoded=E, action=0, logp=-1.0, value=0.0, advantage=1.0, **{"return": 1.0}
                    )
                ], dict(terminated=True, reward=1, cpu_seconds=0.1)

        class Pool:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def submit(self, fn, task):
                return Future(task)

        def fake_update(*args):
            updates.append(True)
            return {"optimizer_steps": 0}

        with tempfile.TemporaryDirectory() as tmp:
            cfg["output"] = tmp
            study = {"config": cfg, "fingerprint": {}, "reference": {"global_game": 19931}}
            (Path(tmp) / "study.json").write_text(json.dumps(study))
            decks = {str(i): str(i) for i in range(11)}
            with (
                patch.object(r, "make_model", side_effect=lambda a: make_model(a, SMALL)),
                patch.object(r, "_pool", return_value=Pool()),
                patch.object(r, "update", side_effect=fake_update),
                patch.object(r.tactical, "warmup", return_value={}),
                patch.object(r.time, "monotonic", side_effect=now),
            ):
                r.train_turn(study, decks, "mlp", 2, 10000, lambda e: None)
                first = state(tmp, "mlp")
                self.assertEqual(first["games"], 4)
                self.assertIn("2", first["milestones"])
                r.train_turn(study, decks, "mlp", first["train_seconds"] + 2, 10000, lambda e: None)
                final = state(tmp, "mlp")
                self.assertEqual(final["games"], 8)
                self.assertGreater(final["train_seconds"], first["train_seconds"])
            self.assertEqual(slots, list(range(8)))
            self.assertEqual(len(updates), 2)

    def test_exact_game_milestones_flush_partial_batch_and_resume(self):
        from hearthstone_sim._bootstrap import activate

        activate()
        from hearthstone_sim.research.matched_games import runner as r

        cfg = read_config()
        cfg = dict(cfg, games_per_batch=4, turn_seconds=20, workers=4, budget_mode="games")
        updates = []
        slots = []
        clock = [0.0]

        def now():
            clock[0] += 1
            return clock[0]

        class Future:
            def __init__(self, task):
                self.task = task

            def result(self):
                slots.append(self.task["metadata"]["slot"])
                return [
                    dict(
                        encoded=E, action=0, logp=-1.0, value=0.0, advantage=1.0, **{"return": 1.0}
                    )
                ], dict(terminated=True, reward=1, cpu_seconds=0.1)

        class Pool:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def submit(self, fn, task):
                return Future(task)

        def fake_update(*args):
            updates.append(True)
            return {"optimizer_steps": 0}

        with tempfile.TemporaryDirectory() as tmp:
            cfg["output"] = tmp
            study = {"config": cfg, "fingerprint": {}, "reference": {"global_game": 19931}}
            (Path(tmp) / "study.json").write_text(json.dumps(study))
            decks = {str(i): str(i) for i in range(11)}
            with (
                patch.object(r, "make_model", side_effect=lambda a: make_model(a, SMALL)),
                patch.object(r, "_pool", return_value=Pool()),
                patch.object(r, "update", side_effect=fake_update),
                patch.object(r.tactical, "warmup", return_value={}),
                patch.object(r.time, "monotonic", side_effect=now),
            ):
                r.train_turn(study, decks, "mlp", 3, 10000, lambda e: None)
                first = state(tmp, "mlp")
                self.assertEqual(first["games"], 3)
                self.assertIn("3", first["milestones"])
                r.train_turn(study, decks, "mlp", 7, 10000, lambda e: None)
                final = state(tmp, "mlp")
                self.assertEqual(final["games"], 7)
                self.assertGreater(final["train_seconds"], first["train_seconds"])
            self.assertEqual(slots, list(range(7)))
            self.assertEqual(len(updates), 2)
