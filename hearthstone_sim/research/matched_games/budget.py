"""Deterministic scheduling independent of hardware/game throughput."""

import math

ARMS = ("mlp", "gru", "large_transformer")


def validate_config(cfg):
    if cfg.get("schema") != "matched-game-study-v1":
        raise ValueError("Unsupported study schema")
    if cfg.get("architectures") != list(ARMS):
        raise ValueError("Pin all three alternative training architectures")
    levels = cfg.get("milestones_games", [])
    if (
        not levels
        or levels != sorted(set(levels))
        or any(not math.isfinite(x) or x <= 0 for x in levels)
    ):
        raise ValueError("Invalid game milestones")
    for key in (
        "session_seconds",
        "turn_seconds",
        "games_per_batch",
        "threads",
        "workers",
        "max_actions",
        "evaluation_cases_per_opponent",
    ):
        if type(cfg[key]) is not int or cfg[key] <= 0:
            raise ValueError("Invalid " + key)
    if cfg["workers"] > 4 or cfg["threads"] > 6:
        raise ValueError("Local memory/CPU envelope exceeded")
    if cfg.get("training_seeds") != [113]:
        raise ValueError("First study is explicitly single seed")
    if cfg["session_seconds"] > 7200:
        raise ValueError("Owner-started sessions are capped at two hours")
    if (
        cfg.get("self_play_fraction"),
        cfg.get("older_fraction"),
        cfg.get("heuristic_fraction"),
    ) != (0.6, 0.3, 0.1):
        raise ValueError("Pin the agreed 60/30/10 mixture")
    if cfg.get("memory_decisions") != 16 or cfg.get("league_size") != 8:
        raise ValueError("Pin the study memory/league policy")
    if cfg.get("budget_mode") != "games":
        raise ValueError("This study uses equal completed games")
    if levels != list(range(1000, 19001, 1000)) + [19931]:
        raise ValueError("Pin 1,000-game graphs and the 19,931-game final target")
    return cfg


def next_arm(states, target):
    available = [a for a in ARMS if states[a]["games"] < target]
    return min(available, key=lambda a: (states[a]["games"], ARMS.index(a))) if available else None


def milestone_checkpoint(snapshots, games):
    # Use the snapshot saved on crossing THIS boundary, never later weights.
    rows = [s for s in snapshots if s["games"] == games]
    return rows[0] if rows else None


def summarize(games):
    valid = [
        g for g in games if g.get("terminated") and not g.get("failed") and not g.get("truncated")
    ]
    wins = sum(g["reward"] == 1 for g in valid)
    draws = sum(g["reward"] == 0 for g in valid)
    from hearthstone_sim.neural.evaluation import wilson

    return dict(
        attempted=len(games),
        completed=len(valid),
        failed=sum(bool(g.get("failed")) for g in games),
        capped=sum(bool(g.get("truncated")) for g in games),
        wins=wins,
        draws=draws,
        losses=len(valid) - wins - draws,
        score=(wins + 0.5 * draws) / len(valid) if valid else None,
        win_rate=wins / len(valid) if valid else None,
        wilson95=wilson(wins, len(valid)) if valid else None,
    )
