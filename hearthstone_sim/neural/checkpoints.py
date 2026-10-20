"""Immutable local tensor checkpoints with compatibility and integrity checks."""

import hashlib
import json
import os
from pathlib import Path
import torch

SCHEMA = "transformer-ppo-checkpoint-v1"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_digest():
    root = Path(__file__).resolve().parent
    files = sorted(root.glob("*.py"))
    runner = root.parents[1] / "tools/train_neural.py"
    files.append(runner)
    h = hashlib.sha256()
    for path in files:
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def save(path, payload):
    """Exclusive final names; incomplete writes never become checkpoints."""
    path = Path(path)
    if path.exists() or path.with_suffix(".json").exists():
        raise FileExistsError(path)
    temporary = path.with_suffix(".partial")
    try:
        with temporary.open("xb") as stream:
            torch.save(payload, stream)
            stream.flush()
            os.fsync(stream.fileno())
        # Hard link is exclusive and atomic on the same filesystem.
        os.link(temporary, path)
        receipt = dict(schema=SCHEMA, path=path.name, sha256=digest(path))
        with path.with_suffix(".json").open("x") as stream:
            json.dump(receipt, stream, indent=2)
    finally:
        if temporary.exists():
            temporary.unlink()
    return dict(path=str(path.resolve()), sha256=receipt["sha256"])


def load(path, expected_compatibility, expected_sha256=None, *, allow_code_upgrade=False):
    path = Path(path)
    receipt = json.loads(path.with_suffix(".json").read_text())
    actual = digest(path)
    if receipt.get("schema") != SCHEMA or actual != receipt["sha256"]:
        raise ValueError("Checkpoint integrity failure")
    if expected_sha256 is not None and actual != expected_sha256:
        raise ValueError("Opponent checkpoint hash mismatch")
    # Do not deserialize arbitrary Python objects from model files.
    payload = torch.load(path, map_location="cpu", weights_only=True)
    if payload.get("schema") != SCHEMA:
        raise ValueError("Checkpoint schema mismatch")
    if payload["compatibility"] != expected_compatibility:
        from .upgrade import compatible_upgrade

        if not allow_code_upgrade or not compatible_upgrade(
            payload["compatibility"], expected_compatibility
        ):
            raise ValueError("Checkpoint engine/model/encoder/deck/code version mismatch")
    return payload
