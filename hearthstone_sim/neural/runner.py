"""Explicitly owner-run PPO training. Preflight never starts games or learning."""

from copy import deepcopy
from dataclasses import asdict
import itertools
from functools import lru_cache
import json
import math
from pathlib import Path
import platform
import random
import uuid
import time
import torch
from .encoding import EncoderConfig, VisibleEncoder, SCHEMA as ENCODER_SCHEMA
from .model import ModelConfig, TransformerPolicyValue
from .ppo import PPOConfig, terminal_gae, update
from .decks import DEFAULT_PANEL, load_panel
from .checkpoints import SCHEMA, save, load, code_digest
from .evaluation import ensure_disjoint, evaluate


# Diagnostics are owner-only artifacts; none of this private state enters an encoder.
def write_json_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, default=str, allow_nan=False)


def new_safety_state():
    return dict(
        attempted=0,
        failed=0,
        completed=0,
        seed_position=0,
        signatures={},
        by_pair={},
        approximations={},
        approximation_proxies={},
    )


def account_attempt(state, result, left, right):
    state["attempted"] += 1
    state["failed"] += int(result.get("failed", False))
    state["completed"] += int(result.get("terminated", False))
    pair = state["by_pair"].setdefault(
        left + " / " + right, dict(attempted=0, failed=0, completed=0)
    )
    pair["attempted"] += 1
    pair["failed"] += int(result.get("failed", False))
    pair["completed"] += int(result.get("terminated", False))
    if result.get("signature"):
        key = result["signature"]
        state["signatures"][key] = state["signatures"].get(key, 0) + 1
    for field in ("approximations", "approximation_proxies"):
        counts = state[field].setdefault(left, {})
        for key, count in result.get(field, {}).items():
            counts[key] = counts.get(key, 0) + count


def failure_limit(state, fraction, minimum, repeats):
    if state["attempted"] >= minimum and state["failed"] / state["attempted"] > fraction:
        return "Cumulative engine failure fraction exceeded"
    if max(state["signatures"].values(), default=0) >= repeats:
        return "Repeated exception signature threshold reached"
    return None


class GameCapture:
    def __init__(self, metadata, folder=None, name="game", trace=False):
        self.metadata, self.folder, self.name = metadata, folder, name
        self.trace = trace
        self.env = None
        self.decision = None
        self.actions = []
        self.last_action = None
        self.count = 0
        self.engine_seconds = self.inference_seconds = 0.0
        self.started = time.monotonic()

    def engine_call(self, function, *args, **kwargs):
        start = time.monotonic()
        try:
            return function(*args, **kwargs)
        finally:
            self.engine_seconds += time.monotonic() - start

    def reset(self, factory, decks, **kwargs):
        self.env = self.engine_call(factory, experimental=True)
        self.decision = self.engine_call(self.env.reset, decks, **kwargs)
        return self.decision

    @staticmethod
    def board_view(decision):
        view = decision.get("observation", {})
        return dict(
            turn=view.get("turn"),
            players=[
                {k: p.get(k) for k in ("mana", "max_mana", "health", "armor", "board")}
                | {"hand_size": len(p.get("hand", ()))}
                for p in view.get("players", ())
            ],
        )

    def step(self, action):
        before = self.decision
        selected = deepcopy(before["actions"][action])
        self.last_action = selected
        self.count += 1
        row = dict(
            actor=before["actor"],
            chosen_action=selected,
            legal_action_count=len(before["actions"]),
            before=self.board_view(before),
        )
        if self.trace:
            self.actions.append(row)
        self.decision = self.engine_call(self.env.step, action, revision=before["revision"])
        if self.trace:
            row["after"] = self.board_view(self.decision)
        return self.decision

    def events(self):
        events = getattr(getattr(self.env, "_game", None), "events", ())
        return list(events) if isinstance(events, (list, tuple)) else []

    def finish(self, result):
        result["timing"] = dict(
            wall_seconds=time.monotonic() - self.started,
            engine_seconds=self.engine_seconds,
            inference_seconds=self.inference_seconds,
        )
        result["actions_per_second"] = self.count / max(result["timing"]["wall_seconds"], 1e-9)
        exact, proxy = {}, {}
        profile = {}
        for event in self.events():
            if event.get("event") == "approximation_profile":
                profile.update(event.get("policies", {}))
            if event.get("event") == "approximation_used":
                key = event.get("policy", "unknown") + ":" + event.get("rule", "unknown")
                exact[key] = exact.get(key, 0) + 1
        for event in self.events():
            if (
                event.get("event") in ("play", "internal_spell_cast")
                and event.get("card") in profile
            ):
                key = event["card"]
                proxy[key] = proxy.get(key, 0) + 1
        result.update(approximations=exact, approximation_proxies=proxy)
        if self.trace and result.get("terminated") and self.folder:
            write_json_new(
                Path(self.folder) / "traces" / (self.name + ".json"),
                dict(
                    header="Owner diagnostic; private data separated and never fed to policy",
                    metadata=self.metadata,
                    policy_visible=dict(actions=self.actions),
                    private_diagnostic=dict(events=self.events()),
                    outcome=result,
                ),
            )
        return result

    def failure(self, error):
        import traceback

        frames = traceback.extract_tb(error.__traceback__)
        handler = next(
            (f.name for f in reversed(frames) if "/expanded/" in f.filename),
            frames[-1].name if frames else "creation",
        )
        # Last played identity is contextual, not guaranteed to be the failing source.
        card = next((e.get("card") for e in reversed(self.events()) if e.get("card")), "unknown")
        signature = type(error).__name__ + ":" + handler
        current = self.decision or {}
        legal_source = "last stable decision before failure"
        if self.env is not None:
            try:
                probe = self.env.decision()
                if isinstance(probe, dict):
                    current = probe
                    legal_source = (
                        "post-failure diagnostic decision; may reflect partial resolution"
                    )
            except Exception:
                pass
        observation = current.get("observation", {})
        import hashlib

        diagnostic = dict(
            header="OWNER ONLY: may contain private engine information; never policy input",
            **self.metadata,
            exception_type=type(error).__name__,
            message=str(error),
            traceback=traceback.format_exc(),
            signature=signature,
            handler=handler,
            contextual_card=card,
            action_count=self.count,
            last_events=self.events()[-50:],
            legal_actions=current.get("actions", []),
            legal_actions_source=legal_source,
            chosen_action=self.last_action,
            timing=dict(
                wall_seconds=time.monotonic() - self.started,
                engine_seconds=self.engine_seconds,
                inference_seconds=self.inference_seconds,
            ),
            observation_hash=hashlib.sha256(
                json.dumps(observation, sort_keys=True, default=str).encode()
            ).hexdigest(),
        )
        if self.folder:
            write_json_new(
                Path(self.folder) / "failures" / ("failure-" + self.name + ".json"), diagnostic
            )
        return self.finish(
            dict(
                failed=True,
                signature=signature,
                terminated=False,
                truncated=False,
                reward=None,
                actions=self.count,
                **self.metadata,
            )
        )


def choose_device(name):
    if name == "auto":
        return (
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )
    if name not in ("cpu", "cuda", "mps"):
        raise ValueError("Use auto, cpu, cuda, or mps")
    if name == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA unavailable")
    if name == "mps" and not torch.backends.mps.is_available():
        raise ValueError("MPS unavailable")
    return name


def prepare(panel=DEFAULT_PANEL, model_config=ModelConfig(), encoder_config=EncoderConfig()):
    """Read-only preflight: validate all decks and report architecture, no game reset."""
    decks, metadata = load_panel(panel)
    from expanded.status import code_fingerprint

    if model_config.buckets != encoder_config.buckets:
        raise ValueError("Embedding bucket mismatch")
    return (
        decks,
        metadata,
        dict(
            engine=code_fingerprint(),
            neural_code=code_digest(),
            encoder_schema=ENCODER_SCHEMA,
            encoder=asdict(encoder_config),
            model=asdict(model_config),
            decks_sha256=metadata["sha256"],
            torch=str(torch.__version__),
            python=platform.python_version(),
        ),
    )


def policy_action(model, encoded, generator):
    with torch.no_grad():
        logits, value = model([encoded])
        # CPU sampling gives one portable explicit generator on CPU/MPS/CUDA.
        probabilities = logits[0].softmax(-1).cpu()
        action = int(torch.multinomial(probabilities, 1, generator=generator).item())
        logp = logits[0].log_softmax(-1)[action].item()
        return action, logp, value[0].item()


def _collect_game(
    learner,
    opponent,
    encoder,
    decks,
    *,
    seed,
    learner_seat,
    first_player,
    max_actions,
    generator,
    ppo,
    capture,
    heuristic_opponent=False,
):
    from expanded.environment import PolicyEnvironment

    decision = capture.reset(
        PolicyEnvironment, decks, seed=seed, max_actions=max_actions, first_player=first_player
    )
    samples = []
    learner.eval()
    opponent.eval()
    while not decision["terminated"] and not decision["truncated"]:
        inference_start = time.monotonic()
        actor = decision["actor"]
        policy = learner if actor == learner_seat else opponent
        if heuristic_opponent and actor != learner_seat:
            from .evaluation import heuristic_action

            action = heuristic_action(decision, encoder.cards)
            logp = value = 0.0
        else:
            encoded = encoder.encode(decision)
            action, logp, value = policy_action(policy, encoded, generator)
        capture.inference_seconds += time.monotonic() - inference_start
        if actor == learner_seat:
            samples.append(dict(encoded=encoded, action=action, logp=logp, value=value))
        decision = capture.step(action)
    result = dict(
        seed=seed,
        learner_seat=learner_seat,
        first_player=first_player,
        actions=decision["steps"],
        terminated=decision["terminated"],
        truncated=decision["truncated"],
        end_reason=decision["end_reason"],
        learner_decisions=len(samples),
        reward=None,
    )
    if decision["truncated"]:
        return [], result  # No false losses, no partial-game gradient.
    reward = decision["rewards"][learner_seat]
    advantages, returns = terminal_gae(
        [s["value"] for s in samples], reward, ppo.gamma, ppo.gae_lambda
    )
    for sample, advantage, target in zip(samples, advantages, returns):
        sample.update(advantage=advantage, **{"return": target})
    result["reward"] = reward
    return samples, result


def collect_game(*args, diagnostic=None, **kwargs):
    capture = diagnostic or GameCapture({})
    try:
        samples, result = _collect_game(*args, capture=capture, **kwargs)
        return samples, capture.finish(result)
    except Exception as error:
        return [], capture.failure(error)


@lru_cache(maxsize=2)
def _match_cycle(names, cycle, seed):
    # Equal coverage of all ordered matchups, learner seats and opening seats.
    schedule = list(itertools.product(names, names, (0, 1), (0, 1)))
    random.Random(seed + cycle).shuffle(schedule)
    return tuple(schedule)


def match_schedule(names, index, seed):
    cycle, position = divmod(index, len(names) ** 2 * 4)
    return _match_cycle(tuple(names), cycle, seed)[position]


def run(
    *,
    iterations,
    games_per_iteration,
    max_actions,
    seed,
    output,
    panel=DEFAULT_PANEL,
    device="cpu",
    model_config=ModelConfig(),
    encoder_config=EncoderConfig(),
    ppo=PPOConfig(),
    resume=None,
    opponents=(),
    self_play_fraction=0.25,
    league_size=32,
    heuristic_fraction=0.0,
    tactical_steps=0,
    collection_workers=1,
    emit=print,
    allow_training=False,
    evaluation=None,
    checkpoint_every_iterations=1,
    allow_code_upgrade=False,
    failure_fraction=0.02,
    failure_min_attempts=100,
    failure_repeats=5,
    retry_cap=20,
    trace_first=6,
    trace_every=16,
    evaluation_at=(),
    evaluate_at_start=True,
    session_seconds=0,
):
    """Only an explicit allow_training=True call can enter the learning loop.

    Resume creates a new run directory and preserves all earlier files. It
    restores Adam, sampler/shuffle/opponent RNGs, schedule and immutable league.
    Source, fixed decks, hyperparameters and device must match exactly.

    Schedule position advances only after a non-failed game (caps remain visible).
    Every attempt consumes one seed and its policy RNG draws. A failed slot retries
    the SAME pair, seat, opening and frozen opponent, using the next seed. This
    preserves nominal schedule-slot balance, not unbiased outcome sampling: errors
    can select against particular interactions. Failures and completed counts by
    pair expose that bias. A threshold stop discards the unfinished PPO batch;
    its completed slots remain counted, and resume starts at the next schedule
    slot with the saved seed/RNG positions. Evaluation does not replace failures;
    failed cases stay in its denominator as attempts, excluded from win rates.
    Execution events are exact counters; profile-card play/cast counts are only
    exposure proxies, since the engine does not label every special-policy call.
    """
    session_started = time.monotonic()
    if not math.isfinite(session_seconds) or session_seconds < 0:
        raise ValueError("Session seconds must be finite and nonnegative")
    if type(collection_workers) is not int or not 1 <= collection_workers <= 4:
        raise ValueError("Collection workers must be between one and four")
    if collection_workers > 1 and device != "cpu":
        raise ValueError("Parallel collection currently requires CPU training")
    if not allow_training:
        raise ValueError("Training requires explicit owner activation")
    for value in (
        iterations,
        games_per_iteration,
        max_actions,
        league_size,
        checkpoint_every_iterations,
    ):
        if type(value) is not int or value < 1:
            raise ValueError("Positive integer budgets required")
    if (
        type(seed) is not int
        or not math.isfinite(self_play_fraction)
        or not 0 <= self_play_fraction <= 1
    ):
        raise ValueError("Invalid seed or opponent mixture")
    if (
        not math.isfinite(heuristic_fraction)
        or not 0 <= heuristic_fraction <= 1 - self_play_fraction
        or type(tactical_steps) is not int
        or tactical_steps < 0
    ):
        raise ValueError("Invalid teacher mixture or lesson budget")
    if league_size < 2:
        raise ValueError("League must retain initial and at least one later snapshot")
    if (
        not 0 <= failure_fraction <= 1
        or min(failure_min_attempts, failure_repeats, retry_cap) < 1
        or min(trace_first, trace_every) < 0
    ):
        raise ValueError("Invalid safety thresholds")
    device = choose_device(device)
    decks, panel_metadata, compatibility = prepare(panel, model_config, encoder_config)
    from expanded.cards import registry

    encoder = VisibleEncoder(encoder_config, registry())
    torch.manual_seed(seed)
    model = TransformerPolicyValue(model_config).to(device).eval()
    optimizer = torch.optim.Adam(model.parameters(), lr=ppo.learning_rate, eps=1e-5)
    action_rng = torch.Generator().manual_seed(seed + 1)
    shuffle_rng = torch.Generator().manual_seed(seed + 2)
    league_rng = random.Random(seed + 3)
    settings = dict(
        seed=seed,
        games_per_iteration=games_per_iteration,
        max_actions=max_actions,
        ppo=asdict(ppo),
        device=device,
        self_play_fraction=self_play_fraction,
        league_size=league_size,
        heuristic_fraction=heuristic_fraction,
        tactical_steps=tactical_steps,
        collection_workers=collection_workers,
        threads=torch.get_num_threads(),
        evaluation=asdict(evaluation) if evaluation is not None else None,
        checkpoint_every_iterations=checkpoint_every_iterations,
        failure_fraction=failure_fraction,
        failure_min_attempts=failure_min_attempts,
        failure_repeats=failure_repeats,
        retry_cap=retry_cap,
        trace_first=trace_first,
        trace_every=trace_every,
        evaluation_at=list(evaluation_at),
        evaluate_at_start=evaluate_at_start,
    )
    safety = new_safety_state()
    evaluation_safety = new_safety_state()
    tactical_state = dict(completed=0)
    completed = 0
    global_game = 0
    league = []
    previous = None
    if resume:
        previous = load(resume, compatibility, allow_code_upgrade=allow_code_upgrade)
        upgraded = previous["compatibility"] != compatibility
        old_settings = previous["settings"]
        matching = all(settings.get(key) == value for key, value in old_settings.items())
        if not upgraded:
            matching = old_settings == settings
        if previous.get("kind") != "resume" or not matching:
            raise ValueError("Resume requires full training checkpoint and matching settings")
        if opponents:
            raise ValueError("Resume restores its opponent pool; do not add new opponents")
        model.load_state_dict(previous["model"])
        optimizer.load_state_dict(previous["optimizer"])
        action_rng.set_state(previous["action_rng"])
        shuffle_rng.set_state(previous["shuffle_rng"])
        league_rng.setstate(previous["league_rng"])
        tactical_state = deepcopy(previous.get("tactical_state", dict(completed=0)))
        completed = previous["iteration"]
        global_game = previous["global_game"]
        evaluation_safety = deepcopy(previous.get("evaluation_safety", new_safety_state()))
        safety = deepcopy(previous.get("safety", new_safety_state()))
        safety["seed_position"] = previous.get("safety", {}).get("seed_position", global_game)
    if evaluation is not None and evaluation.every_iterations:
        ensure_disjoint(seed, global_game, iterations * games_per_iteration, evaluation)
    folder = Path(output).resolve() / uuid.uuid4().hex
    folder.mkdir(parents=True)
    (folder / "decks.json").write_text(json.dumps(panel_metadata["document"], indent=2) + "\n")
    (folder / "config.json").write_text(
        json.dumps(
            dict(
                compatibility=compatibility,
                settings=settings,
                additional_iterations=iterations,
                resume=str(resume) if resume else None,
                continuation_kind="explicit-training-code-upgrade"
                if previous and previous["compatibility"] != compatibility
                else "exact-resume"
                if previous
                else "fresh",
                parent_compatibility=previous["compatibility"] if previous else None,
                migration=previous.get("migration") if previous else None,
                experimental=True,
                fidelity_certified=False,
            ),
            indent=2,
        )
        + "\n"
    )

    run_start_completed = safety["completed"]
    started_at = time.monotonic()
    start_game = global_game

    def notify(event, **data):
        data.setdefault("elapsed_seconds", time.monotonic() - started_at)
        emit(json.dumps(dict(event=event, **data)), flush=True) if emit is print else emit(
            dict(event=event, **data)
        )

    def freeze_snapshot(name, weights):
        descriptor = save(
            folder / name,
            dict(schema=SCHEMA, kind="opponent", compatibility=compatibility, model=weights),
        )
        return dict(name=name, **descriptor)

    if previous:
        for index, descriptor in enumerate(previous["league"]):
            old_path = Path(resume).resolve().parent / descriptor["name"]
            payload = load(
                old_path, compatibility, descriptor["sha256"], allow_code_upgrade=allow_code_upgrade
            )
            league.append(freeze_snapshot(f"restored-{index:04d}.pt", payload["model"]))
    else:
        league.append(freeze_snapshot("opponent-initial.pt", model.state_dict()))
        for index, path in enumerate(opponents):
            payload = load(path, compatibility)
            league.append(freeze_snapshot(f"imported-{index:04d}.pt", payload["model"]))
    if len(league) > league_size:
        league = [league[0]] + league[-(league_size - 1) :]
    notify(
        "started",
        folder=str(folder),
        device=device,
        parameters=sum(p.numel() for p in model.parameters()),
        total_training_games=iterations * games_per_iteration,
        starting_game=global_game,
        session_start_safety=deepcopy(safety),
        session_start_evaluation_safety=deepcopy(evaluation_safety),
    )
    anchors = {}
    anchor_descriptors = {}
    evaluation_history = []
    if previous:
        history_path = Path(resume).resolve().parent / "monitoring-history.json"
        evaluation_history = (
            json.loads(history_path.read_text())
            if history_path.exists()
            else previous.get("evaluation_history", [])
        )
        evaluation_history = [r for r in evaluation_history if r["global_game"] <= global_game]
    if evaluation is not None and evaluation.every_iterations:
        if previous and previous.get("evaluation_anchors"):
            for name, descriptor in previous["evaluation_anchors"].items():
                payload = load(
                    Path(resume).resolve().parent / descriptor["name"],
                    compatibility,
                    descriptor["sha256"],
                    allow_code_upgrade=allow_code_upgrade,
                )
                anchor_descriptors[name] = freeze_snapshot(
                    "evaluation-" + name + ".pt", payload["model"]
                )
        else:
            payload = load(league[0]["path"], compatibility, league[0]["sha256"])
            anchor_descriptors["initial-neural"] = freeze_snapshot(
                "evaluation-initial-neural.pt", payload["model"]
            )
            if previous:
                anchor_descriptors["starting-checkpoint"] = freeze_snapshot(
                    "evaluation-starting-checkpoint.pt", model.state_dict()
                )
        for name, descriptor in anchor_descriptors.items():
            frozen = deepcopy(model).eval()
            frozen.load_state_dict(
                load(descriptor["path"], compatibility, descriptor["sha256"])["model"]
            )
            for parameter in frozen.parameters():
                parameter.requires_grad_(False)
            anchors[name] = frozen

    monitoring_durations = []
    training_seconds = 0.0
    monitoring_iterations = [
        i
        for i in range(completed + 1, completed + iterations + 1)
        if evaluation is not None
        and evaluation.every_iterations
        and (i % evaluation.every_iterations == 0 or i == completed + iterations)
    ]

    latest = None
    updates_since_snapshot = previous.get("updates_since_snapshot", False) if previous else False

    def monitor(iteration, at_start=False):
        nonlocal latest
        monitoring_started = time.monotonic()
        notify(
            "evaluation_started",
            iteration=iteration,
            opponents=len(anchors) + 1,
            games_per_opponent=evaluation.games_per_opponent,
            global_game=global_game,
        )
        # Release idle collection workers before the separate evaluation pool.
        if collection_workers > 1:
            from .parallel import shutdown_pool

            shutdown_pool()
        report = evaluate(
            model,
            anchors,
            encoder,
            decks,
            registry(),
            config=evaluation,
            max_actions=max_actions,
            emit=notify,
            folder=folder,
            iteration=iteration,
            engine_fingerprint=compatibility["engine"],
            cache_dir=Path(output).resolve() / "evaluation-cache",
            failure_fraction=failure_fraction,
            failure_min_attempts=failure_min_attempts,
            failure_repeats=failure_repeats,
            safety=evaluation_safety,
        )
        if tactical_steps:
            from .tactical import assess

            report["tactical_assessment"] = assess(model, encoder)
        report.update(
            iteration=iteration,
            global_game=global_game,
            run_games=global_game - start_game,
            evaluation_kind=("resumed-start" if previous else "fresh-start")
            if at_start
            else "monitoring",
            compatibility=compatibility,
        )
        latest = save(
            folder / f"training-{iteration:06d}-evaluation{'-start' if at_start else ''}.pt",
            dict(
                schema=SCHEMA,
                kind="resume",
                compatibility=compatibility,
                settings=settings,
                model=model.state_dict(),
                optimizer=optimizer.state_dict(),
                iteration=iteration,
                global_game=global_game,
                safety=deepcopy(safety),
                evaluation_safety=deepcopy(evaluation_safety),
                action_rng=action_rng.get_state(),
                shuffle_rng=shuffle_rng.get_state(),
                league_rng=league_rng.getstate(),
                league=[dict(name=d["name"], sha256=d["sha256"]) for d in league],
                evaluation_anchors={
                    name: dict(name=d["name"], sha256=d["sha256"])
                    for name, d in anchor_descriptors.items()
                },
                evaluation_history=evaluation_history,
                updates_since_snapshot=updates_since_snapshot,
                migration=previous.get("migration") if previous else None,
                tactical_state=deepcopy(tactical_state),
                stopped=bool(report.get("stopped")),
            ),
        )
        path = folder / (
            "evaluation-000000.json" if at_start else "evaluation-%06d.json" % iteration
        )
        path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        item = dict(
            iteration=iteration,
            global_game=global_game,
            by_opponent=report["by_opponent"],
            by_deck=report.get("by_deck", {}),
            report=str(path),
            evaluation_kind=report["evaluation_kind"],
            run_games=global_game - start_game,
            checkpoint=latest,
            evaluation_safety=deepcopy(evaluation_safety),
        )
        evaluation_history.append(item)
        (folder / "monitoring-history.json").write_text(
            json.dumps(evaluation_history, indent=2) + "\n"
        )
        monitoring_durations.append(time.monotonic() - monitoring_started)
        notify("evaluation_finished", **item)
        return report.get("stopped")

    if anchors and evaluate_at_start:
        # Each new run records its own baseline, including resumed weights.
        initial_stop = monitor(completed, at_start=True)
        if initial_stop:
            notify("stopped", reason=initial_stop, failures=str(folder / "failures"))
            return latest
    if tactical_steps:
        from .tactical import resume_state

        tactical_state = resume_state(tactical_state)
    if tactical_steps > tactical_state.get("completed", 0):
        from .tactical import warmup

        tactical_state.update(
            warmup(
                model,
                optimizer,
                encoder,
                steps=tactical_steps,
                completed=tactical_state.get("completed", 0),
                allow_training=allow_training,
                emit=lambda **data: notify(**data),
            )
        )
        updates_since_snapshot = True
        latest = save(
            folder / f"training-{completed:06d}-tactical.pt",
            dict(
                schema=SCHEMA,
                kind="resume",
                compatibility=compatibility,
                settings=settings,
                model=model.state_dict(),
                optimizer=optimizer.state_dict(),
                iteration=completed,
                global_game=global_game,
                safety=deepcopy(safety),
                evaluation_safety=deepcopy(evaluation_safety),
                action_rng=action_rng.get_state(),
                shuffle_rng=shuffle_rng.get_state(),
                league_rng=league_rng.getstate(),
                league=[dict(name=d["name"], sha256=d["sha256"]) for d in league],
                evaluation_anchors={
                    name: dict(name=d["name"], sha256=d["sha256"])
                    for name, d in anchor_descriptors.items()
                },
                evaluation_history=evaluation_history,
                updates_since_snapshot=True,
                migration=previous.get("migration") if previous else None,
                tactical_state=deepcopy(tactical_state),
                stopped=False,
            ),
        )
        notify("tactical_finished", checkpoint=latest, **tactical_state)
    for iteration in range(completed + 1, completed + iterations + 1):
        if session_seconds and time.monotonic() - session_started >= session_seconds:
            notify(
                "complete",
                checkpoint=latest or dict(path=str(resume)),
                folder=str(folder),
                reason="Session time budget reached; campaign can resume",
            )
            return latest
        iteration_started = time.monotonic()
        samples = []
        results = []
        iteration_safety = new_safety_state()
        timing = dict(engine_seconds=0.0, inference_seconds=0.0, ppo_seconds=0.0)
        stop_reason = None
        periodic_trace_written = False
        attempted_actions = 0
        opponent_model = deepcopy(model).eval()
        for parameter in opponent_model.parameters():
            parameter.requires_grad_(False)
        collector = None
        tasks = []
        if collection_workers > 1:
            from .parallel import BatchCollector, action_seed

            reservation = safety["seed_position"]
            for slot in range(games_per_iteration):
                left, right, seat, first = match_schedule(list(decks), global_game + slot, seed)
                pair = [None, None]
                pair[seat] = decks[left]
                pair[1 - seat] = decks[right]
                draw = league_rng.random()
                heuristic = draw < heuristic_fraction
                descriptor = None
                if heuristic:
                    opponent_name = "heuristic"
                elif draw < heuristic_fraction + self_play_fraction:
                    opponent_name = "current-frozen"
                else:
                    descriptor = league_rng.choice(league)
                    opponent_name = descriptor["name"]
                game_seed = seed + reservation + slot
                if (
                    evaluation is not None
                    and evaluation.seed
                    <= game_seed
                    < evaluation.seed + evaluation.games_per_opponent
                ):
                    raise ValueError("Parallel reservation overlaps evaluation seeds")
                tasks.append(
                    dict(
                        pair=pair,
                        seed=game_seed,
                        seat=seat,
                        first=first,
                        left=left,
                        right=right,
                        opponent_name=opponent_name,
                        heuristic=heuristic,
                        descriptor=descriptor,
                        compatibility=compatibility,
                        action_seed=action_seed(action_rng),
                        ppo=ppo,
                        max_actions=max_actions,
                        metadata=dict(
                            seed=game_seed,
                            learner_deck=left,
                            opponent_deck=right,
                            learner_seat=seat,
                            first_player=first,
                            opponent=opponent_name,
                            engine_fingerprint=compatibility["engine"],
                        ),
                        folder=folder,
                        name=f"{iteration:06d}-{slot + 1:04d}-parallel-{reservation + slot:08d}",
                        trace=(
                            slot < trace_first
                            and safety["completed"] - run_start_completed < trace_first
                        )
                        or (
                            slot == 0
                            and trace_every > 0
                            and (iteration - completed) % trace_every == 0
                        ),
                    )
                )
            safety["seed_position"] += games_per_iteration
            collector = BatchCollector(
                collection_workers,
                model_config,
                encoder_config,
                {k: v.detach().cpu().clone() for k, v in model.state_dict().items()},
                tasks,
            )
        try:
            for game_index in range(games_per_iteration):
                if collector is not None:
                    task = tasks[game_index]
                    left, right, seat, first = (
                        task["left"],
                        task["right"],
                        task["seat"],
                        task["first"],
                    )
                    pair = task["pair"]
                    opponent_name = task["opponent_name"]
                    heuristic_opponent = task["heuristic"]
                else:
                    left, right, seat, first = match_schedule(list(decks), global_game, seed)
                    pair = [None, None]
                    pair[seat] = decks[left]
                    pair[1 - seat] = decks[right]
                    opponent_draw = league_rng.random()
                    heuristic_opponent = opponent_draw < heuristic_fraction
                    if heuristic_opponent:
                        opponent_name = "heuristic"
                    elif opponent_draw < heuristic_fraction + self_play_fraction:
                        opponent_name = "current-frozen"
                        opponent_model.load_state_dict(model.state_dict())
                    else:
                        descriptor = league_rng.choice(league)
                        payload = load(descriptor["path"], compatibility, descriptor["sha256"])
                        opponent_model.load_state_dict(payload["model"])
                        opponent_name = descriptor["name"]
                notify(
                    "game_started",
                    iteration=iteration,
                    game=game_index + 1,
                    total=games_per_iteration,
                    learner_deck=left,
                    opponent_deck=right,
                    opponent=opponent_name,
                )
                for retry in range(retry_cap + 1):
                    if (
                        (collector is None or retry > 0)
                        and evaluation is not None
                        and evaluation.seed
                        <= seed + safety["seed_position"]
                        < evaluation.seed + evaluation.games_per_opponent
                    ):
                        stop_reason = "Training retry seed overlaps evaluation seeds"
                        break
                    capture = GameCapture(
                        dict(
                            seed=seed + safety["seed_position"],
                            learner_deck=left,
                            opponent_deck=right,
                            learner_seat=seat,
                            first_player=first,
                            opponent=opponent_name,
                            engine_fingerprint=compatibility["engine"],
                        ),
                        folder,
                        f"{iteration:06d}-{game_index + 1:04d}-attempt-{safety['seed_position']:08d}",
                        trace=safety["completed"] - run_start_completed < trace_first
                        or (
                            trace_every > 0
                            and (iteration - completed) % trace_every == 0
                            and not periodic_trace_written
                        ),
                    )
                    if collector is not None:
                        if retry == 0:
                            trajectory, result = collector.result(game_index)
                        else:
                            retry_task = dict(
                                task,
                                seed=seed + safety["seed_position"],
                                action_seed=action_seed(action_rng),
                                metadata=dict(
                                    task["metadata"], seed=seed + safety["seed_position"]
                                ),
                                name=task["name"] + f"-retry-{safety['seed_position']:08d}",
                            )
                            safety["seed_position"] += 1
                            trajectory, result = collector.retry(retry_task)
                    else:
                        trajectory, result = collect_game(
                            model,
                            opponent_model,
                            encoder,
                            pair,
                            seed=seed + safety["seed_position"],
                            learner_seat=seat,
                            first_player=first,
                            max_actions=max_actions,
                            generator=action_rng,
                            ppo=ppo,
                            diagnostic=capture,
                            **({"heuristic_opponent": True} if heuristic_opponent else {}),
                        )
                    attempted_actions += result.get("actions", 0)
                    if collector is None:
                        safety["seed_position"] += 1
                    result.update(learner_deck=left, opponent_deck=right, opponent=opponent_name)
                    account_attempt(safety, result, left, right)
                    account_attempt(iteration_safety, result, left, right)
                    for key in ("engine_seconds", "inference_seconds"):
                        timing[key] += result.get("timing", {}).get(key, 0.0)
                    if result.get("failed"):
                        notify(
                            "game_failed",
                            safety=deepcopy(safety),
                            failures=str(folder / "failures"),
                        )
                        stop_reason = failure_limit(
                            safety, failure_fraction, failure_min_attempts, failure_repeats
                        )
                        if stop_reason or retry == retry_cap:
                            stop_reason = stop_reason or "Replacement retry cap reached"
                            break
                        continue
                    if result.get("terminated"):
                        periodic_trace_written = True
                    samples.extend(trajectory)
                    results.append(result)
                    break
                if stop_reason:
                    break
                global_game += 1
                notify("game_finished", **result)
                done = global_game - start_game
                elapsed = training_seconds + time.monotonic() - iteration_started
                remaining_evaluation = sum(i >= iteration for i in monitoring_iterations)
                evaluation_eta = (
                    (sum(monitoring_durations) / len(monitoring_durations) * remaining_evaluation)
                    if monitoring_durations
                    else 0
                )
                notify(
                    "training_progress",
                    done=done,
                    total=iterations * games_per_iteration,
                    global_game=global_game,
                    games_per_hour=done * 3600 / max(elapsed, 1e-9),
                    eta_seconds=(iterations * games_per_iteration - done) * elapsed / done
                    + evaluation_eta,
                )
        finally:
            if collector is not None:
                collector.close()
        timing["collection_wall_seconds"] = time.monotonic() - iteration_started
        timing["collection_workers"] = collection_workers
        update_started = time.monotonic()
        metrics = (
            update(model, optimizer, samples, ppo, shuffle_rng)
            if samples and not stop_reason
            else dict(
                samples=0,
                optimizer_steps=0,
                reason="Threshold stop: partial batch discarded"
                if stop_reason
                else "No completed-game learner samples",
            )
        )
        timing["ppo_seconds"] = time.monotonic() - update_started
        if tactical_steps and not stop_reason:
            from .tactical import refresh_if_due

            rehearsal_started = time.monotonic()
            refreshed = refresh_if_due(
                model,
                optimizer,
                encoder,
                tactical_state,
                iteration=iteration,
                enabled=True,
                allow_training=allow_training,
                emit=lambda **data: notify(**data),
            )
            if refreshed:
                updates_since_snapshot = True
                timing["tactical_refresh_seconds"] = time.monotonic() - rehearsal_started

        timing["actions_per_second"] = attempted_actions / max(
            time.monotonic() - iteration_started, 1e-9
        )
        training_seconds += time.monotonic() - iteration_started
        updates_since_snapshot = updates_since_snapshot or bool(metrics["optimizer_steps"])
        save_now = (
            iteration % checkpoint_every_iterations == 0
            or iteration == completed + iterations
            or bool(session_seconds and time.monotonic() - session_started >= session_seconds)
        )
        if save_now and updates_since_snapshot:
            league.append(freeze_snapshot(f"opponent-{iteration:06d}.pt", model.state_dict()))
            if len(league) > league_size:
                league = [league[0]] + league[-(league_size - 1) :]
        if save_now or stop_reason:
            latest = save(
                folder / f"training-{iteration:06d}.pt",
                dict(
                    schema=SCHEMA,
                    kind="resume",
                    compatibility=compatibility,
                    settings=settings,
                    model=model.state_dict(),
                    tactical_state=deepcopy(tactical_state),
                    migration=previous.get("migration") if previous else None,
                    optimizer=optimizer.state_dict(),
                    iteration=iteration if not stop_reason else iteration - 1,
                    global_game=global_game,
                    safety=deepcopy(safety),
                    evaluation_safety=deepcopy(evaluation_safety),
                    stopped=bool(stop_reason),
                    action_rng=action_rng.get_state(),
                    shuffle_rng=shuffle_rng.get_state(),
                    league_rng=league_rng.getstate(),
                    league=[dict(name=d["name"], sha256=d["sha256"]) for d in league],
                    evaluation_anchors={
                        name: dict(name=d["name"], sha256=d["sha256"])
                        for name, d in anchor_descriptors.items()
                    },
                    evaluation_history=evaluation_history,
                    timing=timing,
                    updates_since_snapshot=updates_since_snapshot and not save_now,
                ),
            )
            if save_now:
                updates_since_snapshot = False
        summary = dict(
            iteration=iteration,
            games=results,
            metrics=metrics,
            checkpoint=latest if save_now or stop_reason else None,
            safety=deepcopy(safety),
            iteration_safety=iteration_safety,
            timing=timing,
            stopped=stop_reason,
            balance_note="Each failed slot retries the identical matchup/seat/opening with the next unused seed; failures remain visible by pair. Threshold stops can leave the final batch incomplete.",
        )
        with (folder / f"iteration-{iteration:06d}.json").open("x") as stream:
            json.dump(summary, stream, indent=2, allow_nan=False)
        notify("iteration_saved", **summary)
        if stop_reason:
            notify(
                "stopped", reason=stop_reason, failures=str(folder / "failures"), checkpoint=latest
            )
            return latest
        if session_seconds and time.monotonic() - session_started >= session_seconds:
            notify(
                "complete",
                checkpoint=latest,
                folder=str(folder),
                reason="Session time budget reached; campaign can resume",
            )
            return latest
        if anchors and (
            (iteration - completed) * games_per_iteration in evaluation_at
            if evaluation_at
            else iteration % evaluation.every_iterations == 0 or iteration == completed + iterations
        ):
            evaluation_stop = monitor(iteration)
            if evaluation_stop:
                notify(
                    "stopped",
                    reason=evaluation_stop,
                    failures=str(folder / "failures"),
                    checkpoint=latest,
                )
                return latest
    with (folder / "manifest.json").open("x") as stream:
        json.dump(
            dict(
                complete=True,
                final_checkpoint=latest,
                iterations_completed=iterations,
                evaluation_history=evaluation_history,
                compatibility=compatibility,
            ),
            stream,
            indent=2,
        )
    notify("complete", checkpoint=latest, folder=str(folder))
    return latest
