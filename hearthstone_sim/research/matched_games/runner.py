"""Owner-started, single-active-arm scheduler with resumable evaluation cases."""

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path
import fcntl
import json
import random
import time
import uuid
import signal
from contextlib import contextmanager
import torch
from hearthstone_sim.neural.checkpoints import digest
from hearthstone_sim.neural.runner import match_schedule
from hearthstone_sim.neural.ppo import PPOConfig, update
from hearthstone_sim.neural.encoding import VisibleEncoder
from hearthstone_sim.neural import tactical
from .study import ROOT, DEFAULT_CONFIG, open_study, compatibility
from .models import ARMS, CONTENDERS, make_model
from .budget import summarize
from .storage import state, persist, restore, atomic_json
from .collection import initialize, execute


@contextmanager
def termination_guard():
    previous = signal.getsignal(signal.SIGTERM)

    def stop(signum, frame):
        raise KeyboardInterrupt(
            "Owner stopped the research session; last durable checkpoints remain saved"
        )

    signal.signal(signal.SIGTERM, stop)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def specification(arm, weights, key):
    return dict(architecture=arm, weights=weights, key=key)


def frozen(model):
    return {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}


def load_weights(desc):
    if digest(desc["path"]) != desc["sha256"]:
        raise ValueError("Frozen weights changed")
    return torch.load(desc["path"], map_location="cpu", weights_only=True)["model"]


def evaluation_schedule(decks, count):
    names = sorted(decks)
    classes = {}
    for name in names:
        classes.setdefault(decks[name].hero_class, []).append(name)
    groups = list(sorted(classes))
    result = []
    for i in range(count):
        c = groups[i % len(groups)]
        other = groups[(i * 7 + 3) % len(groups)]
        cycle = i // len(groups)
        left = classes[c][(cycle * 3 + i) % len(classes[c])]
        right = classes[other][(cycle * 5 + i + 1) % len(classes[other])]
        result.append((left, right, cycle % 2, (cycle // 2) % 2))
    return result


def _task(
    cfg,
    decks,
    arm,
    learner,
    opponent,
    heuristic,
    slot,
    attempt,
    folder,
    evaluation=False,
    case=None,
    search=False,
):
    if evaluation:
        left, right, seat, first = case
        seed = cfg["evaluation_seed"] + attempt
    else:
        left, right, seat, first = match_schedule(list(decks), slot, cfg["training_seeds"][0])
        seed = cfg["training_seed"] + attempt
    pair = [None, None]
    pair[seat] = decks[left]
    pair[1 - seat] = decks[right]
    return dict(
        learner=learner,
        opponent=opponent,
        heuristic=heuristic,
        pair=pair,
        seat=seat,
        first=first,
        seed=seed,
        action_seed=seed + 1000000000,
        max_actions=cfg["max_actions"],
        ppo=cfg["ppo"],
        folder=str(folder),
        name="case-%09d" % attempt,
        metadata=dict(
            architecture=arm,
            phase="evaluation" if evaluation else "training",
            slot=slot,
            learner_deck=left,
            opponent_deck=right,
        ),
        evaluation=evaluation,
        search=cfg["search"] if search else None,
    )


def _pool(arm, cfg):
    return ProcessPoolExecutor(
        max_workers=cfg["workers"],
        mp_context=get_context("spawn"),
        initializer=initialize,
        initargs=(arm,),
    )


def _payload(model, optimizer, rng, shuffle, pending, results):
    return dict(
        model=model.state_dict(),
        optimizer=optimizer.state_dict(),
        torch_rng=torch.get_rng_state(),
        action_rng=rng.getstate(),
        shuffle_rng=shuffle.get_state(),
        pending_samples=pending,
        pending_results=results,
    )


def train_turn(study, decks, arm, target, deadline, emit):
    cfg = study["config"]
    out = ROOT / cfg["output"]
    meta = state(out, arm)
    compat = compatibility(study, arm)
    old = restore(meta, compat)
    torch.manual_seed(113)
    model = make_model(arm).eval()
    ppo = PPOConfig(**cfg["ppo"])
    optimizer = torch.optim.Adam(model.parameters(), lr=ppo.learning_rate, eps=1e-5)
    rng = random.Random(114)
    shuffle = torch.Generator().manual_seed(115)
    pending = []
    results = []
    if old:
        model.load_state_dict(old["model"])
        optimizer.load_state_dict(old["optimizer"])
        torch.set_rng_state(old["torch_rng"])
        rng.setstate(old["action_rng"])
        shuffle.set_state(old["shuffle_rng"])
        pending = old["pending_samples"]
        results = old["pending_results"]
        del old

    def commit(milestone=None, archive=False):
        nonlocal meta
        meta["pending_games"] = len(results)
        meta = persist(
            out,
            arm,
            meta,
            _payload(model, optimizer, rng, shuffle, pending, results),
            compat,
            milestone,
            cfg["league_size"],
            archive,
        )
        from .report import build_report

        build_report(out)
        emit(
            dict(
                event="checkpoint",
                arm=arm,
                games=meta["games"],
                train_seconds=meta["train_seconds"],
                cpu_seconds=meta["cpu_seconds"],
                pending_games=len(results),
                milestone=milestone,
                checkpoint=meta["checkpoint"],
            )
        )

    if meta.get("blocked"):
        raise RuntimeError("Study engine review required: " + meta["blocked"])
    if not meta["checkpoint"]:
        commit()
    from expanded.cards import registry

    encoder = VisibleEncoder(card_definitions=registry())
    if meta["lessons_completed"] < 128:
        started = time.monotonic()
        cpu = time.process_time()
        tactical.warmup(
            model,
            optimizer,
            encoder,
            steps=128,
            completed=meta["lessons_completed"],
            allow_training=True,
            emit=lambda **e: emit(dict(e, arm=arm)),
        )
        meta["train_seconds"] += time.monotonic() - started
        meta["cpu_seconds"] += time.process_time() - cpu
        meta["lessons_completed"] = 128
        commit()
    game_budget = cfg.get("budget_mode", "time") == "games"

    def reached():
        return meta["games"] >= target if game_budget else meta["train_seconds"] >= target

    until = min(deadline, time.monotonic() + cfg["turn_seconds"])
    league_cache = {}
    with _pool(arm, cfg) as pool:
        current = specification(arm, frozen(model), uuid.uuid4().hex)
        while time.monotonic() < until:
            # A milestone is frozen only after a completed PPO batch. Partial
            # episodes/batches are durably resumed with the SAME frozen policy.
            if not results and reached():
                commit(target)
                return
            number = min(cfg["workers"], cfg["games_per_batch"] - len(results))
            if game_budget:
                number = min(number, target - meta["games"])
            start_slot = meta["games"]
            start_attempt = meta["attempts"]
            tasks = []
            for i in range(number):
                slot = start_slot + i
                mix = slot % 10
                heuristic = mix == 9
                opponent = current
                if 6 <= mix < 9 and meta["league"]:
                    desc = meta["league"][rng.randrange(len(meta["league"]))]
                    key = desc["sha256"]
                    if key not in league_cache:
                        league_cache[key] = specification(arm, load_weights(desc), key)
                        if len(league_cache) > 2:
                            league_cache.pop(next(iter(league_cache)))
                    opponent = league_cache[key]
                tasks.append(
                    _task(
                        cfg,
                        decks,
                        arm,
                        current,
                        None if heuristic else opponent,
                        heuristic,
                        slot,
                        start_attempt + i,
                        out / arm / "diagnostics" / current["key"],
                    )
                )
            meta["attempts"] += number
            t = time.monotonic()
            cpu = time.process_time()
            futures = [pool.submit(execute, x) for x in tasks]
            collected = [f.result() for f in futures]
            meta["train_seconds"] += time.monotonic() - t
            meta["cpu_seconds"] += (
                time.process_time() - cpu + sum(r.get("cpu_seconds", 0) for _, r in collected)
            )
            blocked = None
            for samples, result in collected:
                if result.get("failed") or result.get("truncated"):
                    meta["failed"] += int(bool(result.get("failed")))
                    meta["capped"] += int(bool(result.get("truncated")))
                    blocked = result.get("signature", "action_limit")
                    meta["blocked"] = blocked
                    break
                pending.extend(samples)
                results.append(result)
                meta["games"] += 1
            emit(
                dict(
                    event="collection",
                    arm=arm,
                    games=meta["games"],
                    train_seconds=meta["train_seconds"],
                    pending_games=len(results),
                    target=target,
                    budget_mode=cfg.get("budget_mode", "time"),
                )
            )
            if blocked:
                commit()
                raise RuntimeError("Research paused for engine review: " + blocked)
            if len(results) == cfg["games_per_batch"] or (game_budget and reached()):
                emit(
                    dict(
                        event="learning_started",
                        arm=arm,
                        games=meta["games"],
                        train_seconds=meta["train_seconds"],
                    )
                )
                t = time.monotonic()
                cpu = time.process_time()
                metrics = update(model, optimizer, pending, ppo, shuffle)
                meta["train_seconds"] += time.monotonic() - t
                meta["cpu_seconds"] += time.process_time() - cpu
                meta["batches"] += 1
                if meta["batches"] % 16 == 0:
                    t = time.monotonic()
                    cpu = time.process_time()
                    tactical.warmup(model, optimizer, encoder, steps=16, allow_training=True)
                    meta["train_seconds"] += time.monotonic() - t
                    meta["cpu_seconds"] += time.process_time() - cpu
                pending = []
                results = []
                crossed = target if reached() else None
                commit(crossed, True)
                atomic_json(
                    out / arm / ("batch-%09d.json" % meta["batches"]),
                    dict(metrics=metrics, train_seconds=meta["train_seconds"], games=meta["games"]),
                )
                current = specification(arm, frozen(model), uuid.uuid4().hex)
                if crossed is not None:
                    return
        commit()


def evaluate(study, decks, ref, arm, milestone, deadline, emit):
    cfg = study["config"]
    out = ROOT / cfg["output"]
    base = "transformer" if arm in ("transformer_search", "saved_reference") else arm
    if arm in ("transformer", "transformer_search", "saved_reference"):
        desc = dict(study["reference"], actual_train_seconds=48270.724491532, games=19931)
    else:
        desc = state(out, base)["milestones"][str(milestone)]
    learner = specification(base, load_weights(desc), desc["sha256"])
    reference = study["reference"]
    anchor = ref["evaluation_anchors"]["400-game"]
    anchor_desc = dict(
        path=str(Path(reference["path"]).parent / anchor["name"]), sha256=anchor["sha256"]
    )
    opponents = {
        "heuristic": None,
        "400-game": specification("transformer", load_weights(anchor_desc), anchor["sha256"]),
        "saved-19931": specification("transformer", ref["model"], reference["sha256"]),
    }
    directory = (
        (
            out
            / (
                "reference-search-evaluation"
                if arm == "transformer_search"
                else "reference-evaluation"
            )
        )
        if arm in ("transformer", "transformer_search", "saved_reference")
        else out / "evaluations" / ("%09d" % milestone) / arm
    )
    report_path = directory / "summary.json"
    if report_path.exists():
        return True
    schedule = evaluation_schedule(decks, cfg["evaluation_cases_per_opponent"])
    records = []
    evaluation_seconds = 0.0
    with _pool(base, cfg) as pool:
        for oi, name in enumerate(cfg["evaluation_opponents"]):
            for begin in range(0, len(schedule), cfg["workers"]):
                tasks = []
                for j, case in enumerate(schedule[begin : begin + cfg["workers"]], start=begin):
                    path = directory / name / ("case-%04d.json" % j)
                    if path.exists():
                        records.append(json.loads(path.read_text()))
                        continue
                    if time.monotonic() >= deadline:
                        return False
                    task = _task(
                        cfg,
                        decks,
                        base,
                        learner,
                        opponents[name],
                        name == "heuristic",
                        j,
                        oi * 100000 + j,
                        directory / name / "diagnostics" / uuid.uuid4().hex,
                        True,
                        case,
                        arm == "transformer_search",
                    )
                    tasks.append((path, task))
                started = time.monotonic()
                futures = [pool.submit(execute, t) for _, t in tasks]
                for (path, task), future in zip(tasks, futures):
                    _, result = future.result()
                    result.update(opponent=name, case=task["metadata"]["slot"])
                    atomic_json(path, result)
                    records.append(result)
                    emit(
                        dict(
                            event="evaluation_case",
                            arm=arm,
                            milestone=milestone,
                            done=len(records),
                            total=len(schedule) * len(opponents),
                        )
                    )
                evaluation_seconds += time.monotonic() - started
    from expanded.cards import registry

    encoder = VisibleEncoder(card_definitions=registry())
    model = make_model(base).eval()
    model.load_state_dict(learner["weights"])
    tactics = tactical.assess(model, encoder)
    # Case files retain inference/CPU timing even across interrupted launches.
    report = dict(
        arm=arm,
        milestone=milestone,
        budget_mode=cfg.get("budget_mode", "time"),
        actual_train_seconds=desc["actual_train_seconds"],
        overshoot_seconds=(desc["actual_train_seconds"] - milestone)
        if cfg.get("budget_mode") == "time"
        else None,
        overshoot_games=(desc["games"] - milestone) if cfg.get("budget_mode") == "games" else None,
        games=desc["games"],
        checkpoint=desc,
        summary=summarize(records),
        by_opponent={n: summarize([r for r in records if r["opponent"] == n]) for n in opponents},
        tactics=tactics,
        search_base_tactics_only=arm == "transformer_search",
        evaluation_wall_seconds_this_segment=evaluation_seconds,
        sum_game_wall_seconds=sum(r.get("wall_seconds", 0) for r in records),
        recorded_cpu_seconds=sum(r.get("cpu_seconds", 0) for r in records),
        mean_seconds_per_action=sum(r.get("wall_seconds", 0) for r in records)
        / max(1, sum(r.get("actions", 0) for r in records)),
        search_decisions=sum(r.get("search", {}).get("decisions", 0) for r in records),
        searched_decisions=sum(r.get("search", {}).get("searched", 0) for r in records),
        single_seed=True,
    )
    atomic_json(report_path, report)
    from .report import build_report

    build_report(out)
    emit(dict(event="evaluation_complete", **report))
    return True


def run(path=DEFAULT_CONFIG, *, allow_training=False, emit=lambda e: None):
    if not allow_training:
        raise ValueError("Only the owner may start the research run")
    import subprocess

    processes = subprocess.check_output(["ps", "-axo", "args="], text=True)
    if any(
        ("tools/train_neural.py" in x or "tools/run_architecture_comparison.py" in x)
        and "--train" in x
        for x in processes.splitlines()
    ):
        raise RuntimeError("Let the player/comparison run finish first")
    study, decks, ref = open_study(path)
    cfg = study["config"]
    out = ROOT / cfg["output"]
    out.mkdir(parents=True, exist_ok=True)
    with (
        termination_guard(),
        (ROOT / "runs/all_class_campaign/active.lock").open("a+") as campaign_lock,
        (out / "active.lock").open("a+") as lock,
    ):
        try:
            fcntl.flock(campaign_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Another equal-time study is active")
        started = time.monotonic()
        deadline = started + cfg["session_seconds"]
        torch.set_num_threads(cfg["threads"])
        emit(
            dict(
                event="study_started",
                session_seconds=cfg["session_seconds"],
                budget_mode=cfg["budget_mode"],
                milestones_games=cfg["milestones_games"],
            )
        )
        for milestone in cfg["milestones_games"]:
            while time.monotonic() < deadline:
                states = {a: state(out, a) for a in ARMS}
                available = [a for a in ARMS if str(milestone) not in states[a]["milestones"]]
                if not available:
                    break
                arm = min(available, key=lambda a: (states[a]["games"], ARMS.index(a)))
                train_turn(study, decks, arm, milestone, deadline, emit)
            if time.monotonic() >= deadline:
                break
            for arm in CONTENDERS:
                if not evaluate(study, decks, ref, arm, milestone, deadline, emit):
                    break
            else:
                if milestone == cfg["milestones_games"][-1]:
                    from .tournament import tournament

                    if not tournament(study, decks, milestone, deadline, emit):
                        break
                continue
            break
        from .report import build_report

        report = build_report(out)
        emit(
            dict(
                event="session_complete",
                wall_seconds=time.monotonic() - started,
                report=report,
                training_started=True,
            )
        )
        return report
