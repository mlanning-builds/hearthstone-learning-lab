"""Reproducible legal deck diversity; construction only, never gameplay/search.

Published anchors, progressively changed variants and unrestricted legal random
lists are distinguished. Generated lists are not claimed to be competitive.
Every saved-progress position produces a new immutable panel on next launch.
"""

from dataclasses import asdict, replace
import json
from pathlib import Path
import random


def build_panel(anchor_path, destination, position):
    from .decks import load_panel

    anchors, meta = load_panel(anchor_path)
    from expanded.decks import random_deck, validate, eligible
    from expanded.cards import registry, COLLECTIBLE_IDS

    cards = registry()
    entries = []
    rejections = []
    raw = {d["id"]: d for d in meta["document"]["decks"]}
    rune_profiles = [(a, b, 3 - a - b) for a in range(4) for b in range(4 - a)]
    for class_index, (name, anchor) in enumerate(anchors.items()):
        original = dict(raw[name], kind="published-anchor", anchor=name)
        entries.append(original)
        rng = random.Random(900000000 + position * 1000 + class_index)
        used = {tuple(sorted(anchor.cards))}
        candidates = sorted(
            cid for cid in COLLECTIBLE_IDS if eligible(cards[cid], anchor.hero_class, anchor.runes)
        )
        for variant in range(7):
            swaps = (2, 2, 4, 4, 6, 6, 8)[variant]
            accepted = None
            for attempt in range(500):
                chosen = list(anchor.cards)
                for slot in rng.sample(range(len(chosen)), swaps):
                    chosen[slot] = rng.choice(candidates)
                candidate = replace(anchor, cards=tuple(chosen))
                # Special deck-size/bundle/sideboard restrictions stay enforced.
                if validate(candidate, cards) or tuple(sorted(chosen)) in used:
                    continue
                accepted = candidate
                break
            if accepted is None:
                raise ValueError("Could not construct legal variant: " + name)
            used.add(tuple(sorted(accepted.cards)))
            entries.append(
                dict(
                    asdict(accepted),
                    id=name + "-variant-" + str(variant),
                    name=name + " variant " + str(variant),
                    kind="legal-variant",
                    anchor=name,
                    source=original["source"],
                    changes=swaps,
                )
            )
        for index in range(8):
            for retry in range(500):
                seed = 1000000000 + position * 100000 + class_index * 10000 + index * 500 + retry
                runes = (
                    rune_profiles[(position + index) % len(rune_profiles)]
                    if anchor.hero_class == "DEATHKNIGHT"
                    else (0, 0, 0)
                )
                try:
                    candidate = random_deck(anchor.hero_class, seed, runes)
                except ValueError as error:
                    rejections.append(dict(seed=seed, reason=str(error)))
                    continue
                if tuple(sorted(candidate.cards)) in used:
                    continue
                break
            else:
                raise ValueError("Could not construct distinct random deck")
            used.add(tuple(sorted(candidate.cards)))
            entries.append(
                dict(
                    asdict(candidate),
                    id=name + "-random-" + str(index),
                    name=anchor.hero_class + " legal random " + str(index),
                    kind="legal-random",
                    generator_seed=seed,
                )
            )
    document = dict(
        schema="training-deck-mixture-v1",
        patch=meta["document"]["patch"],
        position=position,
        anchors_sha256=meta["sha256"],
        note="Per class: one published anchor, seven legal variants and eight unrestricted legal random decks. Generated lists are not proven competitive. Snapshot refreshes at each new saved progress position.",
        decks=entries,
        rejected_illegal_constructions=rejections,
    )
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(document, indent=2) + "\n"
    if destination.exists():
        if destination.read_text() != text:
            raise ValueError("Continuum panel snapshot changed")
    else:
        destination.write_text(text)
    load_panel(destination)
    return destination
