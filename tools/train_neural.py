"""Owner-run Transformer PPO CLI. Defaults to read-only preflight, never training."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", action="store_true", help="Explicitly start weight updates")
    parser.add_argument(
        "--preflight", action="store_true", help="Validate configuration without playing games"
    )
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--games-per-iteration", type=int, default=8)
    parser.add_argument("--max-actions", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=71)
    parser.add_argument("--device", choices=["cpu", "auto", "mps", "cuda"], default="cpu")
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument(
        "--panel", type=Path, default=ROOT / "configs/neural_competitive_decks.json"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "runs/neural_ppo")
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--opponent", type=Path, action="append", default=[])
    parser.add_argument("--width", type=int, default=128)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--layers", type=int, default=3)
    parser.add_argument("--feedforward", type=int, default=384)
    parser.add_argument("--history-events", type=int, default=64)
    parser.add_argument("--max-state-tokens", type=int, default=768)
    parser.add_argument("--learning-rate", type=float, default=0.0003)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--minibatch", type=int, default=16)
    parser.add_argument("--self-play-fraction", type=float, default=0.25)
    parser.add_argument("--league-size", type=int, default=32)
    parser.add_argument("--evaluation-every-iterations", type=int, default=0)
    parser.add_argument("--evaluation-games-per-opponent", type=int, default=64)
    parser.add_argument("--evaluation-seed", type=int, default=1_000_000_000)
    parser.add_argument("--checkpoint-every-iterations", type=int, default=1)
    parser.add_argument(
        "--allow-code-upgrade",
        action="store_true",
        help="Explicitly migrate the first trainer checkpoint; requires unchanged engine, model, encoder and PPO",
    )
    parser.add_argument("--failure-fraction", type=float, default=0.02)
    parser.add_argument("--failure-min-attempts", type=int, default=100)
    parser.add_argument("--failure-repeats", type=int, default=5)
    parser.add_argument("--retry-cap", type=int, default=20)
    parser.add_argument("--trace-first", type=int, default=6)
    parser.add_argument("--trace-every", type=int, default=16)
    parser.add_argument("--evaluation-at", type=int, nargs="*", default=[])
    parser.add_argument("--evaluate-at-start", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    if not 0 <= args.failure_fraction <= 1 or min(args.failure_min_attempts, args.failure_repeats, args.retry_cap) < 1 or min(args.trace_first, args.trace_every) < 0:
        parser.error("Invalid safety thresholds")
    if args.train and args.preflight:
        parser.error("Choose --train or --preflight")
    if args.threads < 1:
        parser.error("Positive thread count required")
    try:
        import torch
    except ImportError:
        parser.error(
            'Install the neural extra in this interpreter: python -m pip install -e ".[neural,notebook]"'
        )
    from hearthstone_sim.neural.model import ModelConfig, TransformerPolicyValue
    from hearthstone_sim.neural.encoding import EncoderConfig
    from hearthstone_sim.neural.ppo import PPOConfig
    from hearthstone_sim.neural.runner import prepare, run, choose_device
    from hearthstone_sim.neural.evaluation import EvaluationConfig, ensure_disjoint
    from hearthstone_sim.neural.checkpoints import load

    torch.set_num_threads(args.threads)
    model = ModelConfig(
        width=args.width, heads=args.heads, layers=args.layers, feedforward=args.feedforward
    )
    encoder = EncoderConfig(
        history_events=args.history_events, max_state_tokens=args.max_state_tokens
    )
    ppo = PPOConfig(learning_rate=args.learning_rate, epochs=args.epochs, minibatch=args.minibatch)
    evaluation = EvaluationConfig(
        args.evaluation_every_iterations, args.evaluation_games_per_opponent, args.evaluation_seed
    )
    if (
        min(
            args.iterations,
            args.games_per_iteration,
            args.max_actions,
            args.checkpoint_every_iterations,
        )
        < 1
    ):
        parser.error("Positive training and checkpoint budgets required")
    if not args.train:
        decks, metadata, compatibility = prepare(args.panel, model, encoder)
        previous = (
            load(args.resume, compatibility, allow_code_upgrade=args.allow_code_upgrade)
            if args.resume
            else None
        )
        if evaluation.every_iterations:
            ensure_disjoint(
                args.seed,
                previous["global_game"] if previous else 0,
                args.iterations * args.games_per_iteration,
                evaluation,
            )
        # Model construction is initialization, not a training step.
        network = TransformerPolicyValue(model)
        print(
            json.dumps(
                dict(
                    event="preflight_passed",
                    training_started=False, evaluate_at_start=args.evaluate_at_start,
                    safety=dict(failure_fraction=args.failure_fraction, failure_min_attempts=args.failure_min_attempts, failure_repeats=args.failure_repeats, retry_cap=args.retry_cap, trace_first=args.trace_first, trace_every=args.trace_every),
                    decks=[
                        dict(id=name, hero_class=d.hero_class, cards=len(d.cards))
                        for name, d in decks.items()
                    ],
                    parameters=sum(p.numel() for p in network.parameters()),
                    device=choose_device(args.device),
                    model=asdict(model),
                    ppo=asdict(ppo),
                    planned_training_games=args.iterations * args.games_per_iteration,
                    evaluation=asdict(evaluation),
                    checkpoint_every_games=args.checkpoint_every_iterations
                    * args.games_per_iteration,
                    approximate_checkpoint_storage_gb=sum(p.numel() for p in network.parameters())
                    * 16
                    * (args.iterations // args.checkpoint_every_iterations + 2)
                    / 1e9,
                    resume_verified=previous is not None,
                    code_upgrade=bool(previous and previous["compatibility"] != compatibility),
                    compatibility=compatibility,
                ),
                indent=2,
            )
        )
        return
    run(
        iterations=args.iterations,
        games_per_iteration=args.games_per_iteration,
        max_actions=args.max_actions,
        seed=args.seed,
        output=args.output,
        panel=args.panel,
        device=args.device,
        model_config=model,
        encoder_config=encoder,
        ppo=ppo,
        resume=args.resume,
        opponents=args.opponent,
        self_play_fraction=args.self_play_fraction,
        league_size=args.league_size,
        allow_training=True,
        evaluation=evaluation if evaluation.every_iterations else None,
        checkpoint_every_iterations=args.checkpoint_every_iterations,
        allow_code_upgrade=args.allow_code_upgrade,
        failure_fraction=args.failure_fraction, failure_min_attempts=args.failure_min_attempts,
        failure_repeats=args.failure_repeats, retry_cap=args.retry_cap,
        trace_first=args.trace_first, trace_every=args.trace_every, evaluation_at=args.evaluation_at, evaluate_at_start=args.evaluate_at_start,
    )


if __name__ == "__main__":
    main()
