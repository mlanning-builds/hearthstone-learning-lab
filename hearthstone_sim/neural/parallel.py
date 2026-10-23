"""Synchronous CPU rollout workers. Never update weights or launch at import."""

from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import torch
from collections import OrderedDict
from pathlib import Path
import json
import atexit
import uuid
from concurrent.futures import wait

_LEARNER = _OPPONENT = _ENCODER = None
_BATCH = _OPPONENT_KEY = None
_WEIGHT_CACHE = OrderedDict()
_POOL = _POOL_KEY = None


def initialize(model_config, encoder_config, weights):
    global _LEARNER, _OPPONENT, _ENCODER, _BATCH, _OPPONENT_KEY
    _BATCH = _OPPONENT_KEY = None
    _WEIGHT_CACHE.clear()
    torch.set_num_threads(1)
    from hearthstone_sim._bootstrap import activate

    activate()
    from .model import TransformerPolicyValue
    from .encoding import VisibleEncoder
    from expanded.cards import registry

    _LEARNER = TransformerPolicyValue(model_config).eval()
    _LEARNER.load_state_dict(weights)
    _LEARNER.requires_grad_(False)
    _OPPONENT = TransformerPolicyValue(model_config).eval()
    _OPPONENT.requires_grad_(False)
    _ENCODER = VisibleEncoder(encoder_config, registry())


def execute(task):
    """One game from the batch-frozen policy and an explicit independent RNG."""
    from .runner import collect_game, GameCapture
    from .checkpoints import load

    global _BATCH, _OPPONENT_KEY
    batch = task.get("_batch_id")
    if batch is not None and batch != _BATCH:
        _LEARNER.load_state_dict(task["_learner_weights"])
        _BATCH = batch
        _OPPONENT_KEY = None
    descriptor = task.get("descriptor")
    # The heuristic never reads an opponent network.
    if not task["heuristic"]:
        if descriptor:
            path = Path(descriptor["path"])
            stat = path.stat()
            key = (
                str(path.resolve()),
                descriptor["sha256"],
                json.dumps(task["compatibility"], sort_keys=True),
                stat.st_ino,
                stat.st_size,
                stat.st_mtime_ns,
            )
            if key not in _WEIGHT_CACHE:
                _WEIGHT_CACHE[key] = load(path, task["compatibility"], descriptor["sha256"])[
                    "model"
                ]
                if len(_WEIGHT_CACHE) > 2:
                    _WEIGHT_CACHE.popitem(last=False)
            else:
                _WEIGHT_CACHE.move_to_end(key)
            if _OPPONENT_KEY != key:
                _OPPONENT.load_state_dict(_WEIGHT_CACHE[key])
                _OPPONENT_KEY = key
        else:
            key = ("current", batch)
            if _OPPONENT_KEY != key:
                _OPPONENT.load_state_dict(_LEARNER.state_dict())
                _OPPONENT_KEY = key
    capture = GameCapture(task["metadata"], task["folder"], task["name"], trace=task["trace"])
    return collect_game(
        _LEARNER,
        _OPPONENT,
        _ENCODER,
        task["pair"],
        seed=task["seed"],
        learner_seat=task["seat"],
        first_player=task["first"],
        max_actions=task["max_actions"],
        generator=torch.Generator().manual_seed(task["action_seed"]),
        ppo=task["ppo"],
        diagnostic=capture,
        heuristic_opponent=task["heuristic"],
    )


def action_seed(generator):
    # Exactly one master RNG draw per attempt; worker completion order cannot affect sampling.
    return int(torch.randint(0, 2**63 - 1, (), generator=generator).item())


class BatchCollector:
    """Ordered results; all workers see identical learner weights for this PPO batch.

    Reserve first-attempt seeds before dispatch, then assign retries beyond that
    reservation. Speculative results after a threshold stop never enter PPO.
    """

    def __init__(self, workers, model_config, encoder_config, weights, tasks):
        global _POOL, _POOL_KEY
        key = (workers, model_config, encoder_config)
        if _POOL is not None and _POOL_KEY != key:
            shutdown_pool()
        if _POOL is None:
            _POOL = ProcessPoolExecutor(
                max_workers=workers,
                mp_context=multiprocessing.get_context("spawn"),
                initializer=initialize,
                initargs=(model_config, encoder_config, weights),
            )
            _POOL_KEY = key
        self.pool = _POOL
        self.batch_id = uuid.uuid4().hex
        # Runner provides a detached CPU clone; all futures finish before PPO mutates its model.
        self.weights = weights
        tasks = [dict(t, _batch_id=self.batch_id, _learner_weights=weights) for t in tasks]
        self.tasks = tasks
        self.futures = []
        try:
            self.futures = [self.pool.submit(execute, t) for t in tasks]
        except BaseException:
            self.close()
            raise

    def result(self, index):
        return self.futures[index].result()

    def retry(self, task):
        return self.pool.submit(
            execute, dict(task, _batch_id=self.batch_id, _learner_weights=self.weights)
        ).result()

    def close(self):
        for future in self.futures:
            future.cancel()
        wait(self.futures)
        self.futures.clear()
        self.tasks = []
        self.weights = None


def shutdown_pool():
    global _POOL, _POOL_KEY
    if _POOL is not None:
        _POOL.shutdown(wait=True, cancel_futures=True)
        _POOL = None
        _POOL_KEY = None


atexit.register(shutdown_pool)
