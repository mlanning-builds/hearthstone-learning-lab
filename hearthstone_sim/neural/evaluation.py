"""Frozen-opponent monitoring; independent RNGs, no optimizer or replay reuse."""

from dataclasses import dataclass
import math


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


def evaluate(
    learner,
    anchors,
    encoder,
    decks,
    cards,
    *,
    config,
    max_actions,
    emit,
    folder=None,
    iteration=0,
    engine_fingerprint=None,
    failure_fraction=0.02,
    failure_min_attempts=100,
    failure_repeats=5,
    safety=None,
    cache_dir=None,
    workers=4,
):
    """Same monitoring cases across snapshots, never training on these returns.

    Repeated monitoring is validation, not a fresh unbiased final test. Caps
    are reported separately. Wilson intervals describe completed-game wins
    (draws count as non-wins), approximate for the fixed matchup panel.
    """
    from .runner import match_schedule, new_safety_state, account_attempt, failure_limit

    safety = safety if safety is not None else new_safety_state()
    journal = None
    seen = set(safety.get("evaluation_case_ids", ()))
    if cache_dir is not None:
        from .evaluation_cache import EvaluationJournal, identity

        journal = EvaluationJournal(
            cache_dir,
            identity(learner, anchors, encoder, decks, config, max_actions, engine_fingerprint),
        )
    stopped = None

    all_results = []
    opponents = [("heuristic", None)] + list(anchors.items())
    learner.eval()
    from .evaluation_workers import case, EvaluationPool

    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError("Evaluation workers must be between one and four")
    pool = EvaluationPool(workers, learner, anchors, encoder) if workers > 1 else None

    def make_task(opponent_index, name, index):
        left, right, seat, first = match_schedule(list(decks), index, config.seed)
        pair = [None, None]
        pair[seat] = decks[left]
        pair[1 - seat] = decks[right]
        # Speculative failures are kept apart; only consumed results enter safety/cache.
        diagnostic_folder = (
            folder
            if pool is None or folder is None
            else __import__("pathlib").Path(folder) / "evaluation-worker-diagnostics"
        )
        return dict(
            metadata=dict(
                seed=config.seed + index,
                learner_deck=left,
                opponent_deck=right,
                learner_seat=seat,
                first_player=first,
                opponent=name,
                engine_fingerprint=engine_fingerprint,
            ),
            pair=pair,
            folder=diagnostic_folder,
            name=f"evaluation-{iteration:06d}-{opponent_index}-{index:04d}",
            action_seed=config.seed + 100000 * opponent_index + index,
            max_actions=max_actions,
        )

    def fill(opponent_index, name, start):
        for future_index in range(start, min(start + workers, config.games_per_opponent)):
            key = (opponent_index, future_index)
            if key not in pool.pending and not (journal and journal.read(*key) is not None):
                pool.submit(key, make_task(opponent_index, name, future_index))

    try:
        for opponent_index, (name, opponent) in enumerate(opponents):
            if opponent is not None:
                opponent.eval()
            rows = []
            if pool is not None:
                fill(opponent_index, name, 0)
            for index in range(config.games_per_opponent):
                left, right, seat, first = match_schedule(list(decks), index, config.seed)
                pair = [None, None]
                pair[seat] = decks[left]
                pair[1 - seat] = decks[right]
                result = journal.read(opponent_index, index) if journal else None
                cached = result is not None
                if not cached:
                    task = make_task(opponent_index, name, index)
                    if pool is None:
                        result = case(learner, opponent, encoder, cards, task)
                    else:
                        key = (opponent_index, index)
                        if key not in pool.pending:
                            pool.submit(key, task)
                        result = pool.result(key)
                    if pool is not None:
                        # Bounded speculation; accounting/journal writes remain in serial order.
                        fill(opponent_index, name, index + 1)
                    if journal:
                        journal.write(opponent_index, index, result)
                case_id = journal.case_id(opponent_index, index) if journal else None
                if case_id is None or case_id not in seen:
                    account_attempt(safety, result, left, right)
                    if case_id is not None:
                        safety.setdefault("evaluation_case_ids", []).append(case_id)
                        seen.add(case_id)
                stopped = failure_limit(
                    safety, failure_fraction, failure_min_attempts, failure_repeats
                )
                rows.append(result)
                all_results.append(result)
                emit(
                    "evaluation_game",
                    opponent=name,
                    done=len(rows),
                    total=config.games_per_opponent,
                    cached=cached,
                )
                if stopped:
                    break
            if stopped:
                break
    finally:
        if pool is not None:
            pool.close()
    by_opponent = {
        name: result_summary([r for r in all_results if r["opponent"] == name])
        for name, _ in opponents
    }
    matchups = {}
    for row in all_results:
        key = " / ".join((row["opponent"], row["learner_deck"], row["opponent_deck"]))
        matchups.setdefault(key, []).append(row)
    return dict(
        schema="frozen-opponent-monitoring-v1",
        safety=safety,
        stopped=stopped,
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
