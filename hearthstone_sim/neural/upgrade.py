"""Narrow, explicit migration from the first neural trainer; no engine bypass."""

import hashlib
from pathlib import Path

LEGACY_CODE = "4a463aff26263a9b78300c34339a59aaf64416a8c9c94f4c449543f45de90aad"
UNCHANGED = {
    "encoding.py": "847e1aac749c13d81b3bd1e913625b86220e079c53ca8af2828b6dec9b221908",
    "model.py": "d3220c0709d728a3b1e65d7a3a20b3c7cfa4b51ff7f07848b55193f73819ae7d",
    "ppo.py": "84bcd1a476a19b109a09c7551258a3e13c27623bafeef356b5c1e636fa728d5e",
}


def compatible_upgrade(previous, expected):
    if previous.get("neural_code") != LEGACY_CODE:
        return False
    if {k: v for k, v in previous.items() if k != "neural_code"} != {
        k: v for k, v in expected.items() if k != "neural_code"
    }:
        return False
    root = Path(__file__).resolve().parent
    return all(
        hashlib.sha256((root / name).read_bytes()).hexdigest() == value
        for name, value in UNCHANGED.items()
    )
