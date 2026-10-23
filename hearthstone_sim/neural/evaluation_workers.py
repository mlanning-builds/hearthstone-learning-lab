"""Independent frozen evaluation cases; no optimizer or training RNG access."""

from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import torch

_STATE = None


def initialize(model_config, encoder_config, learner_weights, anchor_weights):
    global _STATE
    torch.set_num_threads(1)
    from hearthstone_sim._bootstrap import activate

    activate()
    from hearthstone_sim.neural.model import TransformerPolicyValue
    from hearthstone_sim.neural.encoding import VisibleEncoder
    from expanded.cards import registry

    def network(weights):
        model = TransformerPolicyValue(model_config).eval()
        model.load_state_dict(weights)
        model.requires_grad_(False)
        return model

    _STATE = (
        network(learner_weights),
        {name: network(weights) for name, weights in anchor_weights.items()},
        VisibleEncoder(encoder_config, registry()),
        registry(),
    )


def case(learner, opponent, encoder, cards, task):
    from hearthstone_sim.neural.runner import GameCapture, policy_action
    from hearthstone_sim.neural.evaluation import heuristic_action
    from expanded.environment import PolicyEnvironment
    import time

    metadata = task["metadata"]
    capture = GameCapture(metadata, task["folder"], task["name"])
    try:
        decision = capture.reset(
            PolicyEnvironment,
            task["pair"],
            seed=metadata["seed"],
            max_actions=task["max_actions"],
            first_player=metadata["first_player"],
        )
        rng = torch.Generator().manual_seed(task["action_seed"])
        while not decision["terminated"] and not decision["truncated"]:
            started = time.monotonic()
            if decision["actor"] == metadata["learner_seat"]:
                action, _, _ = policy_action(learner, encoder.encode(decision), rng)
            elif opponent is None:
                action = heuristic_action(decision, cards)
            else:
                action, _, _ = policy_action(opponent, encoder.encode(decision), rng)
            capture.inference_seconds += time.monotonic() - started
            decision = capture.step(action)
        result_metadata = {
            key: value for key, value in metadata.items() if key != "engine_fingerprint"
        }
        return capture.finish(
            dict(
                result_metadata,
                terminated=decision["terminated"],
                truncated=decision["truncated"],
                actions=decision["steps"],
                reward=decision["rewards"][metadata["learner_seat"]]
                if decision["terminated"]
                else None,
            )
        )
    except Exception as error:
        return capture.failure(error)


def execute(task):
    learner, anchors, encoder, cards = _STATE
    return case(learner, anchors.get(task["metadata"]["opponent"]), encoder, cards, task)


class EvaluationPool:
    def __init__(self, workers, learner, anchors, encoder):
        if next(learner.parameters()).device.type != "cpu":
            raise ValueError("Parallel evaluation requires CPU models")
        self.pool = ProcessPoolExecutor(
            max_workers=workers,
            mp_context=multiprocessing.get_context("spawn"),
            initializer=initialize,
            initargs=(
                learner.config,
                encoder.config,
                learner.state_dict(),
                {name: model.state_dict() for name, model in anchors.items()},
            ),
        )
        self.pending = {}

    def submit(self, key, task):
        self.pending[key] = self.pool.submit(execute, task)

    def result(self, key):
        return self.pending.pop(key).result()

    def close(self):
        for future in self.pending.values():
            future.cancel()
        self.pool.shutdown(wait=True, cancel_futures=True)
