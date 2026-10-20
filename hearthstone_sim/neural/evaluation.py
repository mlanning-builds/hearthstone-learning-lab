"""Frozen-opponent monitoring; independent RNGs, no optimizer or replay reuse."""

from dataclasses import dataclass
import math
import torch


@dataclass(frozen=True)
class EvaluationConfig:
    every_iterations: int = 64
    games_per_opponent: int = 64
    seed: int = 1_000_000_000

    def __post_init__(self):
        if any(type(v) is not int for v in self.__dict__.values()):
            raise ValueError("Evaluation settings must be integers")
        if self.every_iterations < 0 or self.games_per_opponent < 1 or self.seed < 0:
            raise ValueError("Invalid evaluation settings")


def ensure_disjoint(train_seed, start_game, training_games, config):
    training = range(train_seed + start_game, train_seed + start_game + training_games)
    if any(config.seed + i in training for i in range(config.games_per_opponent)):
        raise ValueError("Evaluation and training game seeds overlap")


def wilson(wins, total):
    if not total:
        return None
    z = 1.959963984540054
    rate = wins / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    half = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def result_summary(results):
    completed = [r for r in results if r["terminated"] and not r["truncated"]]
    wins = sum(r["reward"] == 1 for r in completed)
    draws = sum(r["reward"] == 0 for r in completed)
    losses = sum(r["reward"] == -1 for r in completed)
    return dict(
        failed=sum(r.get("failed", False) for r in results),
        attempted=len(results),
        completed=len(completed),
        capped=sum(r["truncated"] for r in results),
        wins=wins,
        draws=draws,
        losses=losses,
        win_rate=wins / len(completed) if completed else None,
        score=(wins + 0.5 * draws) / len(completed) if completed else None,
        win_rate_wilson95=wilson(wins, len(completed)),
    )


def heuristic_action(decision, cards):
    """Independent hand-written baseline; only current policy-visible data.

    Prioritizes lethal attacks, favorable trades, spending mana and developing
    minions. This is a transparent weak baseline, not an expert opponent.
    """
    view = decision["observation"]
    actor = decision["actor"]
    own, other = view["players"][actor], view["players"][1 - actor]
    entities = {
        e["uid"]: e
        for p in view["players"]
        for zone in ("hand", "board")
        for e in p.get(zone, ())
        if isinstance(e, dict) and "uid" in e
    }

    def score(action):
        kind = action["kind"]
        source = entities.get(action.get("source"), {})
        target = entities.get(action.get("target"), {})
        if kind == "mulligan":
            wanted = {
                c["uid"]
                for c in own.get("hand", ())
                if c.get("cost", cards.get(c.get("card_id"), {}).get("cost", 0)) >= 4
            }
            return 100 - len(wanted.symmetric_difference(action.get("choices", ())))
        if kind == "choose":
            options = (view.get("pending_choice") or {}).get("options", ())
            chosen = [options[i] for i in action.get("choices", ())]
            return sum(
                cards.get(c.get("card_id"), {}).get("cost", 0) if isinstance(c, dict) else 0
                for c in chosen
            )
        if kind == "attack":
            attack = own.get("hero_attack", 0) if action["source"] < 0 else source.get("attack", 0)
            if action.get("target") == -1 - (1 - actor):
                return 10000 if attack >= other["health"] + other.get("armor", 0) else 20 + attack
            return 25 + target.get("attack", 0) if attack >= target.get("health", 10**6) else 5
        if kind == "play":
            definition = cards.get(source.get("card_id"), {})
            cost = source.get("cost", definition.get("cost", 0))
            return 15 + cost + (source.get("attack", 0) + source.get("health", 0)) / 4
        return dict(activate=12, power=8, prepare=4, forge=3, trade=2, end=-100).get(kind, 0)

    return max(range(len(decision["actions"])), key=lambda i: score(decision["actions"][i]))


def evaluate(learner, anchors, encoder, decks, cards, *, config, max_actions, emit,
             folder=None, iteration=0, engine_fingerprint=None, failure_fraction=0.02,
             failure_min_attempts=100, failure_repeats=5, safety=None):
    """Same monitoring cases across snapshots, never training on these returns.

    Repeated monitoring is validation, not a fresh unbiased final test. Caps
    are reported separately. Wilson intervals describe completed-game wins
    (draws count as non-wins), approximate for the fixed matchup panel.
    """
    from .runner import match_schedule, policy_action, GameCapture, new_safety_state, account_attempt, failure_limit
    import time
    safety = safety if safety is not None else new_safety_state()
    stopped = None
    from expanded.environment import PolicyEnvironment

    all_results = []
    opponents = [("heuristic", None)] + list(anchors.items())
    learner.eval()
    for opponent_index, (name, opponent) in enumerate(opponents):
        if opponent is not None:
            opponent.eval()
        rows = []
        for index in range(config.games_per_opponent):
            left, right, seat, first = match_schedule(list(decks), index, config.seed)
            pair = [None, None]
            pair[seat] = decks[left]
            pair[1 - seat] = decks[right]
            capture = GameCapture(dict(seed=config.seed+index, learner_deck=left,
                opponent_deck=right, learner_seat=seat, first_player=first,
                opponent=name, engine_fingerprint=engine_fingerprint), folder,
                f"evaluation-{iteration:06d}-{opponent_index}-{index:04d}")
            try:
                decision = capture.reset(PolicyEnvironment, pair, seed=config.seed+index,
                                         max_actions=max_actions, first_player=first)
                rng = torch.Generator().manual_seed(config.seed + 100000 * opponent_index + index)
                while not decision["terminated"] and not decision["truncated"]:
                    inference_start = time.monotonic()
                    if decision["actor"] == seat:
                        action, _, _ = policy_action(learner, encoder.encode(decision), rng)
                    elif opponent is None:
                        action = heuristic_action(decision, cards)
                    else:
                        action, _, _ = policy_action(opponent, encoder.encode(decision), rng)
                    capture.inference_seconds += time.monotonic()-inference_start
                    decision = capture.step(action)
                result = dict(
                    opponent=name,
                    seed=config.seed + index,
                    learner_deck=left,
                    opponent_deck=right,
                    learner_seat=seat,
                    first_player=first,
                    terminated=decision["terminated"],
                    truncated=decision["truncated"],
                    actions=decision["steps"],
                    reward=decision["rewards"][seat] if decision["terminated"] else None,
                )
                result = capture.finish(result)
            except Exception as error:
                result = capture.failure(error)
            account_attempt(safety, result, left, right)
            stopped = failure_limit(safety, failure_fraction, failure_min_attempts, failure_repeats)
            rows.append(result)
            all_results.append(result)
            emit("evaluation_game", opponent=name, done=len(rows), total=config.games_per_opponent)
            if stopped:
                break
        if stopped:
            break
    by_opponent = {
        name: result_summary([r for r in all_results if r["opponent"] == name])
        for name, _ in opponents
    }
    matchups = {}
    for row in all_results:
        key = " / ".join((row["opponent"], row["learner_deck"], row["opponent_deck"]))
        matchups.setdefault(key, []).append(row)
    return dict(
        schema="frozen-opponent-monitoring-v1", safety=safety, stopped=stopped,
        summary=result_summary(all_results),
        by_opponent=by_opponent,
        by_matchup={k: result_summary(v) for k, v in matchups.items()},
        by_deck={
            name: result_summary([r for r in all_results if r["learner_deck"] == name])
            for name in decks
        },
        games=all_results,
        seed=config.seed,
        training_updates=0,
        interpretation="Fixed-panel monitoring, not expert strength or an unbiased final test. Caps excluded from win-rate denominators.",
    )
