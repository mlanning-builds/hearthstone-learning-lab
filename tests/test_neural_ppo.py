"""Non-training fixtures only: no games played and no optimizer.step calls.

Numerical loss derivatives are checked without changing any model weights.
"""

from copy import deepcopy
import itertools
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    import torch
except ImportError:
    raise unittest.SkipTest("Optional neural dependencies are not installed")
from hearthstone_sim.neural.encoding import EncoderConfig, VisibleEncoder
from hearthstone_sim.neural.model import ModelConfig, TransformerPolicyValue
from hearthstone_sim.neural.ppo import PPOConfig, terminal_gae, objective
from hearthstone_sim.neural.runner import prepare, match_schedule, run, collect_game
from hearthstone_sim.neural.checkpoints import save, load, SCHEMA


def fixture(actions=2, viewer=0):
    legal = [dict(kind="play", source=7, target=-2, position=i, choices=[]) for i in range(actions)]
    players = [
        dict(health=30, hand=[dict(uid=7, card_id="VISIBLE", attack=2)], board=[]),
        dict(health=20, hand_count=3, board=[]),
    ]
    return dict(
        actor=viewer,
        actions=legal,
        observation=dict(
            viewer=viewer,
            current_player=0,
            phase="main",
            turn=3,
            players=players,
            legal_actions=legal,
            events=[dict(event="play", player=1, card="SECRET")],
        ),
    )


class NeuralFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)

    def test_all_fixed_published_decks_validate(self):
        decks, metadata, compat = prepare()
        self.assertEqual(len(decks), 4)
        self.assertTrue(all(len(d.cards) == 30 for d in decks.values()))
        self.assertEqual(metadata["document"]["patch"], "36.6.0.251952")
        self.assertEqual(len(compat["engine"]), 64)

    def test_all_matchups_seats_openings_per_cycle(self):
        names = ["a", "b", "c", "d"]
        observed = [match_schedule(names, i, 71) for i in range(64)]
        self.assertEqual(set(observed), set(itertools.product(names, names, (0, 1), (0, 1))))
        self.assertEqual(len(set(observed)), 64)

    def test_unknown_top_level_and_player_fields_are_encoded(self):
        encoder = VisibleEncoder()
        source = fixture()
        old = encoder.encode(source)
        source["observation"]["future_effect"] = dict(amount=7)
        self.assertNotEqual(old, encoder.encode(source))
        source = fixture()
        source["observation"]["players"][0]["future_effect"] = True
        self.assertNotEqual(old, encoder.encode(source))

    def test_nonvisible_top_level_input_not_consumed(self):
        encoder = VisibleEncoder()
        source = fixture()
        old = encoder.encode(source)
        source["private_game"] = dict(opponent_hand=["SECRET_CARD"], random_seed=33)
        source["rewards"] = [-1, 1]
        self.assertEqual(old, encoder.encode(source))

    def test_uid_renumbering_preserves_encoding(self):
        encoder = VisibleEncoder()
        source = fixture()
        new = deepcopy(source)
        new["observation"]["players"][0]["hand"][0]["uid"] = 9999
        for a in new["actions"]:
            a["source"] = 9999
        self.assertEqual(encoder.encode(source), encoder.encode(new))

    def test_history_window_reports_omission(self):
        encoder = VisibleEncoder(EncoderConfig(history_events=1))
        source = fixture()
        before = encoder.encode(source)
        source["observation"]["events"].insert(0, dict(event="private_does_not_exist"))
        after = encoder.encode(source)
        self.assertNotEqual(before, after)
        # Old event text is absent; only omitted count changes.
        source["observation"]["events"][0]["event"] = "different"
        self.assertEqual(after, encoder.encode(source))

    def test_overflow_and_wrong_viewer_fail(self):
        with self.assertRaisesRegex(ValueError, "overflow"):
            VisibleEncoder(EncoderConfig(max_state_tokens=1)).encode(fixture())
        source = fixture()
        source["actor"] = 1
        with self.assertRaisesRegex(ValueError, "viewer"):
            VisibleEncoder().encode(source)

    def test_visible_definition_and_action_targets_encoded(self):
        source = fixture()
        self.assertNotEqual(
            VisibleEncoder().encode(source),
            VisibleEncoder(card_definitions={"VISIBLE": dict(text="Deal 3 damage", cost=2)}).encode(
                source
            ),
        )
        old = VisibleEncoder().encode(source)
        source["actions"][0]["target"] = -1
        self.assertNotEqual(old["actions"], VisibleEncoder().encode(source)["actions"])

    def test_forward_variable_candidates_padding_and_no_weight_changes(self):
        torch.manual_seed(11)
        model = TransformerPolicyValue(
            ModelConfig(width=16, heads=2, layers=1, feedforward=32)
        ).eval()
        encoder = VisibleEncoder()
        first, second = encoder.encode(fixture(2)), encoder.encode(fixture(5))
        second["state"] += second["state"][:3]
        before = deepcopy(model.state_dict())
        with torch.no_grad():
            logits, values = model([first, second])
            single, v = model([first])
        self.assertEqual([len(x) for x in logits], [2, 5])
        self.assertEqual(values.shape, (2,))
        self.assertTrue(torch.allclose(logits[0], single[0], atol=1e-6))
        self.assertTrue(torch.isfinite(values).all())
        self.assertTrue(all(torch.equal(t, before[k]) for k, t in model.state_dict().items()))

    def test_terminal_gae_hand_computed(self):
        adv, ret = terminal_gae([0.2, 0.4], 1, gamma=1, lam=1)
        for a, b in zip(adv, [0.8, 0.6]):
            self.assertAlmostEqual(a, b)
        self.assertEqual(ret, [1.0, 1.0])
        _, ret = terminal_gae([0.0, 0.0], -1)
        self.assertEqual(ret[-1], -1)
        self.assertEqual(terminal_gae([], 0), ([], []))

    def test_clipped_ppo_loss_and_finite_derivative_without_update(self):
        # Ratio 2, positive advantage -> clipped 1.2; ratio .5, negative -> .8.
        logp = torch.tensor([2.0, 0.5]).log().requires_grad_()
        config = PPOConfig(entropy_weight=0, value_weight=0)
        loss, policy, _, kl = objective(
            logp,
            torch.zeros(2),
            torch.tensor([1.0, -1.0]),
            torch.zeros(2),
            torch.zeros(2),
            torch.zeros(2),
            torch.zeros(2),
            config,
        )
        self.assertAlmostEqual(policy.item(), -0.2, places=6)
        loss.backward()
        self.assertTrue(torch.isfinite(logp.grad).all())
        self.assertGreater(kl.item(), 0)

    def test_checkpoint_roundtrip_integrity_and_compatibility(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.pt"
            payload = dict(
                schema=SCHEMA,
                compatibility=dict(version=1),
                model=dict(weight=torch.tensor([1.0, 2.0])),
            )
            save(path, payload)
            restored = load(path, dict(version=1))
            self.assertTrue(torch.equal(restored["model"]["weight"], payload["model"]["weight"]))
            with self.assertRaises(FileExistsError):
                save(path, payload)
            with self.assertRaisesRegex(ValueError, "mismatch"):
                load(path, dict(version=2))
            with path.open("ab") as stream:
                stream.write(b"corruption")
            with self.assertRaisesRegex(ValueError, "integrity"):
                load(path, dict(version=1))

    def test_import_and_run_guard_never_start_training(self):
        with self.assertRaisesRegex(ValueError, "activation"):
            run(iterations=1, games_per_iteration=1, max_actions=1, seed=1, output="unused")

    def test_invalid_configuration(self):
        for changes in (dict(gamma=0), dict(learning_rate=float("nan")), dict(minibatch=0)):
            with self.assertRaises(ValueError):
                PPOConfig(**changes)
        with self.assertRaises(ValueError):
            ModelConfig(width=15, heads=4)

    def test_capped_game_discards_all_samples_no_reward(self):
        # Scripted environment, no live gameplay or learning.
        decision = fixture()
        decision.update(terminated=False, truncated=False, revision=1)
        terminal = deepcopy(decision)
        terminal.update(
            terminated=False,
            truncated=True,
            revision=2,
            steps=1,
            end_reason="action_limit",
            rewards=[0, 0],
        )
        with (
            patch("expanded.environment.PolicyEnvironment") as env_type,
            patch("hearthstone_sim.neural.runner.policy_action", return_value=(0, -0.5, 0.2)),
        ):
            env_type.return_value.reset.return_value = decision
            env_type.return_value.step.return_value = terminal
            samples, result = collect_game(
                unittest.mock.Mock(),
                unittest.mock.Mock(),
                VisibleEncoder(),
                [],
                seed=1,
                learner_seat=0,
                first_player=0,
                max_actions=1,
                generator=None,
                ppo=PPOConfig(),
            )
        self.assertEqual(samples, [])
        self.assertIsNone(result["reward"])

    def test_only_learner_seat_receives_training_labels(self):
        first = fixture()
        first.update(terminated=False, truncated=False, revision=1)
        second = fixture(viewer=1)
        second.update(terminated=False, truncated=False, revision=2)
        end = dict(
            terminated=True, truncated=False, steps=2, end_reason="hero_death", rewards=[1, -1]
        )
        with (
            patch("expanded.environment.PolicyEnvironment") as env_type,
            patch("hearthstone_sim.neural.runner.policy_action", return_value=(0, -0.5, 0.2)),
        ):
            env_type.return_value.reset.return_value = first
            env_type.return_value.step.side_effect = [second, end]
            samples, result = collect_game(
                unittest.mock.Mock(),
                unittest.mock.Mock(),
                VisibleEncoder(),
                [],
                seed=1,
                learner_seat=0,
                first_player=0,
                max_actions=3,
                generator=None,
                ppo=PPOConfig(),
            )
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0]["return"], 1)
        self.assertEqual(result["reward"], 1)

    def test_synthetic_model_backward_does_not_change_parameters(self):
        torch.manual_seed(9)
        model = TransformerPolicyValue(
            ModelConfig(width=16, heads=2, layers=1, feedforward=32)
        ).eval()
        before = deepcopy(model.state_dict())
        encoded = VisibleEncoder().encode(fixture())
        logits, value = model([encoded])
        # A derivative fixture only: optimizer.step is never called.
        loss = -logits[0].log_softmax(-1)[0] + value.square().mean()
        loss.backward()
        self.assertTrue(
            all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())
        )
        self.assertTrue(all(torch.equal(t, before[k]) for k, t in model.state_dict().items()))

    def test_iteration_and_resume_wiring_with_learning_and_gameplay_mocked(self):
        # Exercises real checkpoint/league/Adam-state serialization. No simulated
        # games and no learning updates; both collection and update are mocked.
        with (
            tempfile.TemporaryDirectory() as folder,
            patch(
                "hearthstone_sim.neural.runner.collect_game",
                return_value=([dict(scripted=True)], dict(truncated=False, reward=1)),
            ) as collect,
            patch(
                "hearthstone_sim.neural.runner.update",
                return_value=dict(optimizer_steps=1, samples=1, synthetic_no_learning=True),
            ) as mocked_update,
        ):
            args = dict(
                iterations=1,
                games_per_iteration=2,
                max_actions=3,
                seed=7,
                output=folder,
                model_config=ModelConfig(width=16, heads=2, layers=1, feedforward=32),
                allow_training=True,
                emit=lambda event: None,
            )
            first = run(**args)
            resumed = run(**args, resume=first["path"])
            compatibility = prepare(model_config=args["model_config"])[2]
            checkpoint = load(resumed["path"], compatibility)
            self.assertEqual(checkpoint["iteration"], 2)
            self.assertEqual(checkpoint["global_game"], 4)
            self.assertEqual(len(checkpoint["league"]), 3)
            self.assertEqual(mocked_update.call_count, 2)
            self.assertEqual(collect.call_count, 4)
            self.assertNotEqual(Path(first["path"]).parent, Path(resumed["path"]).parent)
            self.assertTrue(Path(first["path"]).exists())
            # Initial and final model equal: mocked update actually changed none.
            original = load(first["path"], compatibility)
            self.assertTrue(
                all(torch.equal(v, original["model"][k]) for k, v in checkpoint["model"].items())
            )

    def test_no_completed_games_no_optimizer_or_new_opponent(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch(
                "hearthstone_sim.neural.runner.collect_game",
                return_value=([], dict(truncated=True)),
            ),
            patch("hearthstone_sim.neural.runner.update") as update_mock,
        ):
            model_config = ModelConfig(width=16, heads=2, layers=1, feedforward=32)
            result = run(
                iterations=1,
                games_per_iteration=1,
                max_actions=1,
                seed=7,
                output=folder,
                model_config=model_config,
                allow_training=True,
                emit=lambda e: None,
            )
            checkpoint = load(result["path"], prepare(model_config=model_config)[2])
            self.assertEqual(len(checkpoint["league"]), 1)
            update_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
