"""Standalone scientific figures at saved 1,000-game milestones."""

from pathlib import Path
import hashlib
import json
import os
from .models import ARMS

LABELS = {
    "mlp": "MLP",
    "gru": "GRU",
    "large_transformer": "Larger Transformer",
    "transformer": "Saved small Transformer (19,931 games)",
    "transformer_search": "Saved small + combat look-ahead",
}
COLORS = {
    "mlp": "#2476c7",
    "gru": "#0b9368",
    "large_transformer": "#9d4ac5",
    "transformer": "#475569",
    "transformer_search": "#d28a09",
}


def render(output, rows, milestones, reference):
    out = Path(output)
    folder = out / "plots"
    folder.mkdir(parents=True, exist_ok=True)
    # Changes in current batches update the table, but only new milestone data
    # triggers figure work. This keeps plotting outside the learning hot path.
    data = {
        "snapshots": {a: r.get("milestones", {}) for a, r in rows.items()},
        "evaluations": milestones,
        "reference": reference,
    }
    key = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    marker = folder / "input.sha256"
    png = folder / "learning-curves.png"
    if marker.exists() and marker.read_text() == key and png.exists():
        return png
    os.environ.setdefault("MPLCONFIGDIR", str(folder / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    for arm in ARMS:
        points = []
        for m in milestones:
            r = m["reports"].get(arm)
            if (
                r
                and r["summary"]["completed"]
                and not r["summary"]["failed"]
                and not r["summary"]["capped"]
            ):
                points.append((m["games"], r))
        x = [p[0] for p in points]
        y = [100 * p[1]["summary"]["win_rate"] for p in points]
        axes[0].plot(x, y, "o-", label=LABELS[arm], color=COLORS[arm], markersize=4)
        if points:
            axes[0].fill_between(
                x,
                [100 * p[1]["summary"]["wilson95"][0] for p in points],
                [100 * p[1]["summary"]["wilson95"][1] for p in points],
                color=COLORS[arm],
                alpha=0.10,
            )
        axes[1].plot(
            x,
            [100 * p[1]["tactics"]["correct"] / p[1]["tactics"]["total"] for p in points],
            "o-",
            color=COLORS[arm],
            label=LABELS[arm],
            markersize=4,
        )
        snapshots = sorted(rows[arm].get("milestones", {}).values(), key=lambda s: s["games"])
        axes[2].plot(
            [p["games"] for p in snapshots],
            [p["actual_train_seconds"] / 3600 for p in snapshots],
            "o-",
            color=COLORS[arm],
            label=LABELS[arm],
            markersize=4,
        )
    for arm, ref in reference.items():
        if (
            not ref
            or not ref["summary"]["completed"]
            or ref["summary"]["failed"]
            or ref["summary"]["capped"]
        ):
            continue
        axes[0].axhline(
            100 * ref["summary"]["win_rate"], color=COLORS[arm], linestyle="--", label=LABELS[arm]
        )
        axes[1].axhline(
            100 * ref["tactics"]["correct"] / ref["tactics"]["total"],
            color=COLORS[arm],
            linestyle="--",
        )
    axes[2].scatter(
        [19931],
        [48270.724491532 / 3600],
        marker="x",
        s=65,
        color=COLORS["transformer"],
        label="Saved player: recorded timer subtotal*",
    )
    titles = [
        "Win rate against fixed opponents",
        "Tactical questions (24 scripted positions)",
        "Time spent to reach each game count",
    ]
    for ax, title in zip(axes, titles):
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Completed training games per alternative")
        ax.grid(alpha=0.2)
        ax.set_xlim(0, 20000)
    axes[0].set_ylabel("Win rate (%)")
    axes[0].set_ylim(0, 100)
    axes[1].set_ylabel("Correct (%)")
    axes[1].set_ylim(0, 105)
    axes[2].set_ylabel("Active training hours")
    axes[0].legend(fontsize=7, loc="best")
    axes[2].legend(fontsize=7, loc="best")
    fig.suptitle(
        "Matched-game comparison · reference lines already have 19,931 games · single-seed pilot",
        fontsize=12,
    )
    fig.savefig(png, dpi=150)
    fig.savefig(folder / "learning-curves.svg")
    plt.close(fig)
    marker.write_text(key)
    return png
