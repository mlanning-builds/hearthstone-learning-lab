"""Architecture-generic isolated collection; bounded memory reset per game."""

import time
import torch
from hearthstone_sim.neural.runner import prepare, GameCapture
from hearthstone_sim.neural.encoding import VisibleEncoder
from hearthstone_sim.neural.ppo import PPOConfig, terminal_gae
from .models import make_model, with_memory

_MODELS = {}
_ENCODER = None
_ARCH = None
_SEARCH = None


def initialize(architecture, search=None):
    global _MODELS, _ENCODER, _ARCH, _SEARCH
    torch.set_num_threads(1)
    prepare()
    from expanded.cards import registry

    _ARCH = architecture
    _SEARCH = search
    _MODELS = {}
    _ENCODER = VisibleEncoder(card_definitions=registry())


def execute(task):
    global _MODELS
    for role, spec in [("learner", task["learner"]), ("opponent", task["opponent"])]:
        if spec is None:
            continue
        key = (spec["architecture"], spec["key"])
        if role not in _MODELS or _MODELS[role][0] != key:
            model = make_model(spec["architecture"]).eval()
            model.load_state_dict(spec["weights"])
            model.requires_grad_(False)
            _MODELS[role] = (key, model)
    return game(_MODELS["learner"][1], _MODELS.get("opponent", (None, None))[1], _ENCODER, task)


def game(learner, opponent, encoder, task):
    from expanded.environment import PolicyEnvironment
    from hearthstone_sim.neural.evaluation import heuristic_action
    from .search import choose

    architecture = task["learner"]["architecture"]
    op_arch = (task["opponent"] or {}).get("architecture", "transformer")
    ppo = PPOConfig(**task["ppo"])
    rng = torch.Generator().manual_seed(task["action_seed"])
    capture = GameCapture(task["metadata"], task.get("folder"), task["name"])
    samples = []
    history = [[], []]
    search_stats = dict(decisions=0, searched=0, nodes=0, reasons={})
    start = time.monotonic()
    cpu = time.process_time()
    learner.eval()
    if opponent is not None:
        opponent.eval()
    try:
        decision = capture.reset(
            PolicyEnvironment,
            task["pair"],
            seed=task["seed"],
            max_actions=task["max_actions"],
            first_player=task["first"],
        )
        while not decision["terminated"] and not decision["truncated"]:
            actor = decision["actor"]
            own = actor == task["seat"]
            model = learner if own else opponent
            t = time.monotonic()
            if not own and task["heuristic"]:
                action = heuristic_action(decision, encoder.cards)
                logp = val = 0.0
            else:
                enc = encoder.encode(decision)
                enc = with_memory(enc, history[actor], architecture if own else op_arch)
                with torch.no_grad():
                    logits, values = model([enc])
                    action = int(torch.multinomial(logits[0].softmax(-1), 1, generator=rng))
                    logp = float(logits[0].log_softmax(-1)[action])
                    val = float(values[0])
                history[actor].append(enc["state"])
                history[actor] = history[actor][-15:]
                if (own and task.get("search")) or (not own and op_arch == "transformer_search"):
                    action, stat = choose(
                        decision,
                        model,
                        encoder,
                        action,
                        task["search"] if own else task["op_search"],
                    )
                    if own:
                        search_stats["decisions"] += 1
                        search_stats["searched"] += int(stat["searched"])
                        search_stats["nodes"] += stat["nodes"]
                    if own and stat["reason"]:
                        search_stats["reasons"][stat["reason"]] = (
                            search_stats["reasons"].get(stat["reason"], 0) + 1
                        )
                    # Search is evaluation-only: these probabilities are NOT PPO samples.
                if own and not task.get("evaluation"):
                    samples.append(dict(encoded=enc, action=action, logp=logp, value=val))
            capture.inference_seconds += time.monotonic() - t
            decision = capture.step(action)
        reward = None if decision["truncated"] else decision["rewards"][task["seat"]]
        result = dict(
            seed=task["seed"],
            terminated=decision["terminated"],
            truncated=decision["truncated"],
            failed=False,
            reward=reward,
            actions=decision["steps"],
            search=search_stats,
        )
        if decision["truncated"]:
            samples = []
        elif samples:
            advantages, returns = terminal_gae(
                [s["value"] for s in samples], reward, ppo.gamma, ppo.gae_lambda
            )
            for s, a, v in zip(samples, advantages, returns):
                s.update(advantage=a, **{"return": v})
        result = capture.finish(result)
    except Exception as error:
        samples = []
        result = capture.failure(error)
    result.update(wall_seconds=time.monotonic() - start, cpu_seconds=time.process_time() - cpu)
    return samples, result
