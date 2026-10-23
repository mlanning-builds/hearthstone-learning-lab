"""Bounded architecture comparison. Imports/preflight never collect games or learn."""

import hashlib
import json
import os
from pathlib import Path
import signal
import uuid
import subprocess
import time
from dataclasses import asdict
import torch
from hearthstone_sim.neural.checkpoints import load, save, digest, SCHEMA
from hearthstone_sim.neural.runner import prepare, collect_game, GameCapture, match_schedule
from hearthstone_sim.neural.encoding import VisibleEncoder
from hearthstone_sim.neural.model import ModelConfig, TransformerPolicyValue
from hearthstone_sim.neural.ppo import PPOConfig, update
from hearthstone_sim.neural.evaluation import wilson
from .models import make_model

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/research_mlp_transformer.json"
OUTPUT = ROOT / "runs/research_mlp_transformer"


def write_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(data, f, indent=2, allow_nan=False)


def code_hash():
    h = hashlib.sha256()
    for p in sorted(Path(__file__).parent.glob("*.py")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    h.update((ROOT / "tools/run_architecture_comparison.py").read_bytes())
    return h.hexdigest()


def config():
    d = json.loads(CONFIG.read_text())
    if d["schema"] != "architecture-comparison-v1" or d["training_seeds"] != [113]:
        raise ValueError("This pilot supports exactly the pinned single training seed")
    if d["chunk_games_per_model"] % d["games_per_batch"] or d["games_per_batch"] != 64:
        raise ValueError("Use whole 64-game learning batches")
    if d["evaluation_cases"] != 44 or d["soft_limit_minutes"] <= 0:
        raise ValueError("Invalid bounded pilot configuration")
    return d


def study():
    """Freeze one common opponent and source versions. No model updates or games."""
    from tools.long_training_campaign import latest_source, source_payload

    cfg = config()
    decks, _, compat = prepare(ROOT / cfg["panel"])
    fingerprint = dict(simulator=compat, research=code_hash(), config=digest(CONFIG))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / "study.json"
    if path.exists():
        s = json.loads(path.read_text())
        if s["fingerprint"] != fingerprint:
            raise ValueError(
                "Research source/config changed. Keep existing results and create a separately reviewed study; do not silently mix versions."
            )
    else:
        parent = latest_source()
        payload = source_payload(parent)
        if payload["compatibility"]["model"] != asdict(ModelConfig()):
            raise ValueError("Common opponent architecture differs")
        s = dict(
            schema=cfg["schema"],
            fingerprint=fingerprint,
            opponent=dict(
                path=str(parent), sha256=digest(parent), global_game=payload["global_game"]
            ),
            config=cfg,
        )
        write_new(path, s)
    if digest(s["opponent"]["path"]) != s["opponent"]["sha256"]:
        raise ValueError("Frozen opponent changed")
    return s, decks


def compatibility(s, architecture):
    return dict(
        study=s["fingerprint"], opponent_sha256=s["opponent"]["sha256"], architecture=architecture
    )


def latest(architecture):
    candidates = []
    for p in (OUTPUT / architecture).glob("checkpoint-*.pt"):
        if p.with_suffix(".json").exists():
            # Numeric game position, then post-update/evaluation stage; never filesystem timing.
            parts = p.stem.split("-")
            candidates.append(((int(parts[1]), int(parts[2])), p))
    return max(candidates)[1] if candidates else None


def evaluation_schedule(names):
    # Each learner class and opposing class appears four times, balancing both seats/openers.
    return [
        (names[i], names[(i + 1) % len(names)], seat, first)
        for i in range(len(names))
        for seat in (0, 1)
        for first in (0, 1)
    ]


def summarize(games):
    valid = [g for g in games if g.get("terminated") and not g.get("failed")]
    wins = sum(g["reward"] == 1 for g in valid)
    draws = sum(g["reward"] == 0 for g in valid)
    return dict(
        attempts=len(games),
        finished=len(valid),
        wins=wins,
        draws=draws,
        losses=len(valid) - wins - draws,
        failed=sum(bool(g.get("failed")) for g in games),
        capped=sum(bool(g.get("truncated")) for g in games),
        score=(wins + 0.5 * draws) / len(valid) if valid else None,
        win_interval=wilson(wins, len(valid)) if valid else None,
    )


def preflight():
    s, decks = study()
    cfg = s["config"]
    rows = []
    for architecture in cfg["architectures"]:
        torch.manual_seed(113)
        model = make_model(architecture)
        p = latest(architecture)
        saved = load(p, compatibility(s, architecture)) if p else None
        rows.append(
            dict(
                architecture=architecture,
                parameters=sum(x.numel() for x in model.parameters()),
                games=saved["games"] if saved else 0,
                resume=str(p) if p else None,
            )
        )
        del model, saved
    return dict(
        event="research_ready",
        training_started=False,
        models=rows,
        classes=len(decks),
        chunk_games_per_model=cfg["chunk_games_per_model"],
        soft_limit_minutes=cfg["soft_limit_minutes"],
        common_opponent=s["opponent"],
        scope=cfg["evaluation_scope"],
    )


def run(*, allow_training=False, emit=print):
    if not allow_training:
        raise ValueError("Owner must explicitly start research training")
    processes = subprocess.check_output(["ps", "-axo", "args="], text=True)
    if any(
        "tools/train_neural.py" in line and "--train" in line for line in processes.splitlines()
    ):
        raise RuntimeError(
            "The existing player run is active. Let it finish before starting research."
        )
    s, decks = study()
    cfg = s["config"]
    torch.set_num_threads(cfg["threads"])
    started = time.monotonic()
    deadline = started + 60 * cfg["soft_limit_minutes"]
    lock = OUTPUT / "active.lock"
    try:
        with lock.open("x") as f:
            f.write(str(os.getpid()))
    except FileExistsError:
        pid = int(lock.read_text())
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            lock.unlink()
            with lock.open("x") as f:
                f.write(str(os.getpid()))
        else:
            raise RuntimeError("Another research process is active")

    def interrupted(signum, frame):
        raise KeyboardInterrupt("Owner interrupted research")

    old_handler = signal.signal(signal.SIGTERM, interrupted)
    try:
        return _run_locked(s, decks, cfg, deadline, emit)
    finally:
        signal.signal(signal.SIGTERM, old_handler)
        lock.unlink()


def _run_locked(s, decks, cfg, deadline, emit):
    from tools.long_training_campaign import source_payload
    from expanded.cards import registry

    # A round has ONE persistent target shared by both architectures; interrupted rounds catch up.
    rounds = sorted(OUTPUT.glob("round-*.json"))
    previous = json.loads(rounds[-1].read_text()) if rounds else None
    if previous and not (OUTPUT / ("completed-" + rounds[-1].name)).exists():
        round_path = rounds[-1]
        round_info = previous
    else:
        number = len(rounds) + 1
        target = (previous["target"] if previous else 0) + cfg["chunk_games_per_model"]
        round_info = dict(number=number, target=target)
        round_path = OUTPUT / ("round-%04d.json" % number)
        write_new(round_path, round_info)
    ppo = PPOConfig(
        learning_rate=cfg["learning_rate"], minibatch=cfg["minibatch"], epochs=cfg["epochs"]
    )
    encoder = VisibleEncoder(card_definitions=registry())
    teacher = TransformerPolicyValue().eval()
    teacher.load_state_dict(source_payload(Path(s["opponent"]["path"]))["model"])
    teacher.requires_grad_(False)
    architectures = (
        cfg["architectures"] if round_info["number"] % 2 else list(reversed(cfg["architectures"]))
    )
    summaries = {}

    def expired():
        return time.monotonic() >= deadline

    for architecture in architectures:
        torch.manual_seed(113)
        model = make_model(architecture).eval()
        optimizer = torch.optim.Adam(model.parameters(), lr=ppo.learning_rate, eps=1e-5)
        rng = torch.Generator().manual_seed(114)
        shuffle = torch.Generator().manual_seed(115)
        games = 0
        seed_position = 0
        failed = 0
        signatures = {}
        batch = []
        batch_results = []
        attempt_folder = OUTPUT / architecture / "attempts" / uuid.uuid4().hex
        checkpoint = latest(architecture)
        if checkpoint:
            old = load(checkpoint, compatibility(s, architecture))
            model.load_state_dict(old["model"])
            optimizer.load_state_dict(old["optimizer"])
            rng.set_state(old["action_rng"])
            shuffle.set_state(old["shuffle_rng"])
            games = old["games"]
            seed_position = old["seed_position"]
            failed = old["failed"]
            signatures = old["signatures"]
            batch = old["pending_samples"]
            batch_results = old["pending_results"]
        if failed >= 10 or max(signatures.values(), default=0) >= 3:
            raise RuntimeError(
                "Saved research safety limit requires an engine review before continuing"
            )
        serial = 0
        if checkpoint:
            serial = int(checkpoint.stem.split("-")[2]) + 1
            del old

        def persist(model=model, optimizer=optimizer):
            nonlocal serial
            path = OUTPUT / architecture / ("checkpoint-%06d-%06d.pt" % (games, serial))
            path.parent.mkdir(parents=True, exist_ok=True)
            cp = save(
                path,
                dict(
                    schema=SCHEMA,
                    kind="research-resume",
                    compatibility=compatibility(s, architecture),
                    model=model.state_dict(),
                    optimizer=optimizer.state_dict(),
                    action_rng=rng.get_state(),
                    shuffle_rng=shuffle.get_state(),
                    games=games,
                    seed_position=seed_position,
                    failed=failed,
                    signatures=signatures,
                    pending_samples=batch,
                    pending_results=batch_results,
                ),
            )
            serial += 1
            return cp

        def evaluate_at(position, model=model):
            folder = OUTPUT / architecture / ("evaluation-%06d" % position)
            cases = []
            for i, (left, right, seat, first) in enumerate(evaluation_schedule(list(decks))):
                case_path = folder / ("case-%03d.json" % i)
                if case_path.exists():
                    result = json.loads(case_path.read_text())
                else:
                    if expired():
                        return None
                    pair = [None, None]
                    pair[seat] = decks[left]
                    pair[1 - seat] = decks[right]
                    erng = torch.Generator().manual_seed(cfg["evaluation_seed"] + i)
                    _, result = collect_game(
                        model,
                        teacher,
                        encoder,
                        pair,
                        seed=cfg["evaluation_seed"] + i,
                        learner_seat=seat,
                        first_player=first,
                        max_actions=cfg["max_actions"],
                        generator=erng,
                        ppo=ppo,
                        diagnostic=GameCapture(
                            dict(architecture=architecture, phase="evaluation", case=i),
                            folder,
                            "case-%03d" % i,
                        ),
                    )
                    result.update(learner_deck=left, opponent_deck=right)
                    write_new(case_path, result)
                cases.append(result)
                emit(
                    dict(
                        event="research_evaluation",
                        architecture=architecture,
                        games=position,
                        done=len(cases),
                        total=44,
                    )
                )
            report = summarize(cases)
            summary_path = folder / "summary.json"
            if not summary_path.exists():
                write_new(summary_path, report)
            return report

        # Save fresh initialization before any baseline work; resuming keeps its exact weights.
        if checkpoint is None:
            persist()
        if games == 0:
            if evaluate_at(0) is None:
                persist()
                emit(
                    dict(
                        event="research_paused",
                        reason="90-minute soft limit",
                        architecture=architecture,
                        games=games,
                    )
                )
                return
        while games < round_info["target"]:
            if expired():
                persist()
                emit(
                    dict(
                        event="research_paused",
                        reason="90-minute soft limit; partial batch preserved",
                        architecture=architecture,
                        games=games,
                        pending=len(batch_results),
                    )
                )
                return
            left, right, seat, first = match_schedule(list(decks), games, 113)
            pair = [None, None]
            pair[seat] = decks[left]
            pair[1 - seat] = decks[right]
            trajectory, result = collect_game(
                model,
                teacher,
                encoder,
                pair,
                seed=cfg["training_seed"] + seed_position,
                learner_seat=seat,
                first_player=first,
                max_actions=cfg["max_actions"],
                generator=rng,
                ppo=ppo,
                diagnostic=GameCapture(
                    dict(
                        architecture=architecture,
                        phase="training",
                        game=games,
                        seed=cfg["training_seed"] + seed_position,
                    ),
                    attempt_folder,
                    "train-%08d" % seed_position,
                ),
            )
            write_new(
                attempt_folder / ("attempt-%08d.json" % seed_position),
                dict(
                    slot=games,
                    seed=cfg["training_seed"] + seed_position,
                    learner_deck=left,
                    opponent_deck=right,
                    result=result,
                ),
            )
            seed_position += 1
            if result.get("failed"):
                failed += 1
                key = result["signature"]
                signatures[key] = signatures.get(key, 0) + 1
                if signatures[key] >= 3 or failed >= 10:
                    persist()
                    emit(
                        dict(
                            event="research_paused",
                            reason="Engine error safety limit",
                            architecture=architecture,
                            failed=failed,
                        )
                    )
                    return
                continue
            if result.get("truncated"):
                # Caps are never losses or gradients. Keep same slot and expose the attempt.
                failed += 1
                if failed >= 10:
                    persist()
                    emit(dict(event="research_paused", reason="Failure/cap safety limit"))
                    return
                continue
            result.update(learner_deck=left, opponent_deck=right)
            batch.extend(trajectory)
            batch_results.append(result)
            games += 1
            if len(batch_results) == cfg["games_per_batch"]:
                t = time.monotonic()
                metrics = update(model, optimizer, batch, ppo, shuffle)
                receipts = OUTPUT / architecture / ("batch-%06d.json" % games)
                report = dict(
                    games=games,
                    metrics=metrics,
                    ppo_seconds=time.monotonic() - t,
                    results=batch_results,
                    failed=failed,
                )
                batch = []
                batch_results = []
                cp = persist()
                # Commit weights first: an interrupted report write must never force retraining a saved batch.
                write_new(receipts, report)
                emit(
                    dict(
                        event="research_batch",
                        architecture=architecture,
                        games=games,
                        target=round_info["target"],
                        checkpoint=cp,
                        metrics=metrics,
                    )
                )
        report = evaluate_at(games)
        if report is None:
            persist()
            emit(
                dict(
                    event="research_paused",
                    reason="Soft limit during evaluation",
                    architecture=architecture,
                    games=games,
                )
            )
            return
        summaries[architecture] = report
        persist()
        emit(
            dict(
                event="research_arm_complete",
                architecture=architecture,
                games=games,
                evaluation=report,
            )
        )
        del model, optimizer
    final = dict(
        round=round_info, evaluations=summaries, matched_games=True, scope=cfg["evaluation_scope"]
    )
    write_new(OUTPUT / ("completed-" + round_path.name), final)
    emit(dict(event="research_round_complete", **final))
    return final
