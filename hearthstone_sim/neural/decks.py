"""Pinned external competitive lists. No random deck construction or substitutions."""

import hashlib
import json
from pathlib import Path

DEFAULT_PANEL = Path(__file__).resolve().parents[2] / "configs/neural_competitive_decks.json"


def load_panel(path=DEFAULT_PANEL):
    from hearthstone_sim._bootstrap import activate

    activate()
    from expanded.decks import Deck, validate
    from standard.catalog import load_catalog, verify_data
    from expanded.fabled_decks import companion_ids

    raw = Path(path).read_bytes()
    data = json.loads(raw)
    if data.get("schema") != "fixed-competitive-decks-v1":
        raise ValueError("Unsupported fixed deck panel")
    if data.get("patch") != verify_data()["patch"]:
        raise ValueError("Deck panel patch differs from frozen catalog")
    standard = {c["id"] for c in load_catalog()}
    decks = {}
    for entry in data["decks"]:
        name = entry["id"]
        if name in decks:
            raise ValueError("Duplicate deck name")
        deck = Deck(
            entry["hero_class"],
            tuple(entry["cards"]),
            tuple(entry["runes"]),
            beatrix_minion=entry.get("beatrix_minion"),
            contraband_beasts=tuple(entry.get("contraband_beasts", ())),
            etc_band=tuple(entry.get("etc_band", ())),
            zilliax_modules=tuple(entry.get("zilliax_modules", ())),
        )
        errors = validate(deck)
        outside = set(deck.cards) - standard - companion_ids(deck.cards)
        if outside:
            errors.append("Not in pinned Standard catalog: " + str(sorted(outside)))
        if errors:
            raise ValueError(name + ": " + "; ".join(errors))
        if not entry.get("source", "").startswith("https://"):
            raise ValueError("Fixed competitive list needs a source URL")
        decks[name] = deck
    if len(decks) < 2:
        raise ValueError("At least two fixed competitive decks required")
    return decks, dict(sha256=hashlib.sha256(raw).hexdigest(), document=data)
