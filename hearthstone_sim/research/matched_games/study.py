"""Preflight pins inputs without training, inference games or changing notebook 21."""

from pathlib import Path
from collections import Counter
import hashlib
import json
from hearthstone_sim.neural.runner import prepare
from hearthstone_sim.neural.checkpoints import digest, load
from .budget import validate_config, ARMS
from .models import make_model
from .storage import atomic_json, state

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / "configs/research_matched_games.json"


def read_config(path=DEFAULT_CONFIG):
    return validate_config(json.loads(Path(path).read_text()))


def source_hash():
    h = hashlib.sha256()
    for p in sorted(Path(__file__).parent.glob("*.py")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    h.update((ROOT / "tools/run_matched_games_comparison.py").read_bytes())
    return h.hexdigest()


def open_study(path=DEFAULT_CONFIG):
    cfg = read_config(path)
    panel = ROOT / cfg["panel"]
    reference = ROOT / cfg["reference"]
    if digest(panel) != cfg["panel_sha256"] or digest(reference) != cfg["reference_sha256"]:
        raise ValueError("Frozen panel or reference changed")
    decks, metadata, compat = prepare(panel)
    counts = Counter(d.hero_class for d in decks.values())
    if len(decks) != 176 or len(counts) != 11 or set(counts.values()) != {16}:
        raise ValueError("Expected 176 decks, 16 per class")
    # Reference read only. Never migrate or replace the campaign's checkpoint.
    ref = load(reference, compat, cfg["reference_sha256"])
    fingerprint = dict(config=digest(path), code=source_hash(), simulator=compat)
    output = ROOT / cfg["output"]
    if output.resolve().parent != (ROOT / "runs").resolve() or not output.name.startswith(
        "research_matched_games"
    ):
        raise ValueError("Use an isolated runs/research_matched_games* output directory")
    manifest = output / "study.json"
    if manifest.exists():
        study = json.loads(manifest.read_text())
        if study["fingerprint"] != fingerprint:
            raise ValueError(
                "Study source/config changed: use a new output directory; old results are preserved"
            )
    else:
        study = dict(
            schema=cfg["schema"],
            fingerprint=fingerprint,
            config=cfg,
            reference=dict(
                path=str(reference), sha256=cfg["reference_sha256"], global_game=ref["global_game"]
            ),
            created_without_training=True,
        )
        atomic_json(manifest, study)
    return study, decks, ref


def compatibility(study, arm):
    return dict(study=study["fingerprint"], architecture=arm)


def preflight(path=DEFAULT_CONFIG):
    import torch

    old_rng = torch.get_rng_state()
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        study, decks, ref = open_study(path)
        cfg = study["config"]
        out = ROOT / cfg["output"]
        models = []
        for arm in ARMS:
            torch.manual_seed(113)
            model = make_model(arm)
            meta = state(out, arm)
            models.append(
                dict(
                    architecture=arm,
                    parameters=sum(p.numel() for p in model.parameters()),
                    games=meta["games"],
                    training_hours=meta["train_seconds"] / 3600,
                    checkpoint=meta["checkpoint"],
                )
            )
            del model
        return dict(
            event="comparison_ready",
            training_started=False,
            output=str(out),
            models=models,
            search_variant="transformer_search uses the preserved 19,931-game Transformer; bounded combat look-ahead",
            reference=study["reference"],
            session_hours=cfg["session_seconds"] / 3600,
            target_games=cfg["milestones_games"][-1],
            graph_every_games=1000,
            deck_count=len(decks),
            classes=11,
            threads=cfg["threads"],
            workers=cfg["workers"],
            scope=cfg["scope"],
        )
    finally:
        torch.set_rng_state(old_rng)
        torch.set_num_threads(threads)
