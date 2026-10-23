"""Study-local immutable checkpoints, recoverable commits and bounded retention."""

from pathlib import Path
import json
import os
import uuid
from hearthstone_sim.neural.checkpoints import save, load, digest, SCHEMA


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".partial")
    with temp.open("x") as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def state(output, arm, verify=True):
    folder = Path(output) / arm
    commits = sorted(folder.glob("commit-*.json"))
    if not commits:
        return dict(
            commit=0,
            train_seconds=0.0,
            cpu_seconds=0.0,
            games=0,
            attempts=0,
            batches=0,
            failed=0,
            capped=0,
            league=[],
            milestones={},
            checkpoint=None,
            lessons_completed=0,
        )
    # A visible commit is complete. Corruption must fail, never silently reset.
    row = json.loads(commits[-1].read_text())
    cp = row["checkpoint"]
    if verify and digest(cp["path"]) != cp["sha256"]:
        raise ValueError("Study checkpoint integrity failure")
    return row


def persist(
    output, arm, meta, payload, compatibility, milestone=None, league_size=8, archive=False
):
    folder = Path(output) / arm
    folder.mkdir(parents=True, exist_ok=True)
    result = dict(meta, commit=meta["commit"] + 1)
    cp = save(
        folder / ("weights-" + uuid.uuid4().hex + ".pt"),
        dict(payload, schema=SCHEMA, kind="equal-time-resume", compatibility=compatibility),
    )
    result["checkpoint"] = cp
    if archive:
        result["league"] = (list(meta["league"]) + [cp])[-league_size:]
    if milestone is not None:
        result["milestones"] = dict(
            meta["milestones"],
            **{
                str(milestone): dict(
                    cp, actual_train_seconds=result["train_seconds"], games=result["games"]
                )
            },
        )
    atomic_json(folder / ("commit-%09d.json" % result["commit"]), result)
    # Keep latest/previous resume, all milestones, and the configured league.
    commits = sorted(folder.glob("commit-*.json"))
    previous = json.loads(commits[-2].read_text()) if len(commits) > 1 else None
    keep = {Path(cp["path"]).resolve()}
    if previous:
        keep.add(Path(previous["checkpoint"]["path"]).resolve())
    keep.update(Path(x["path"]).resolve() for x in result["league"])
    keep.update(Path(x["path"]).resolve() for x in result["milestones"].values())
    for p in folder.glob("weights-*.pt"):
        if p.resolve() not in keep:
            p.unlink()
            p.with_suffix(".json").unlink(missing_ok=True)
    return result


def restore(meta, compatibility):
    cp = meta["checkpoint"]
    return load(cp["path"], compatibility, cp["sha256"]) if cp else None
