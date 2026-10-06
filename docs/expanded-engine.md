# Current development status

Version 0.3 now has 253 written collectible effects and 92 prepared checks; it has not been executed by the assistant. Full Standard remains incomplete. See [the current completion tracker](standard-completion.md). The notes below describe the earlier version 0.2 milestone.

# Expanded engine implementation

Status: **incomplete, unexecuted by the assistant, not full Standard**. There are 154 explicitly implemented collectible card records out of the 1,185-record catalog. 1,031 remain. All eleven base hero powers have code and prepared fixtures; altered/upgraded/Imbued powers are outside this milestone.

The user asked that notebook cells, matches, and training be left for them to run. Only source parsing, data comparisons, and packaging checks were performed. The user ran the previous 29-check suite successfully. Version 0.2 adds 14 checks (43 total); its fixtures have not been executed by the assistant and await the user’s run.

## Components

- `expanded/cards.py`: per-card target restrictions and ordered operations; explicit passive/keyword and deathrattle lists. Data hashes live in `reviewed_cards.json`. No card-text interpretation fallback.
- `expanded/decks.py`: 30-card construction for the supported pool, class and multi-class membership, DK rune requirements, legendary/ordinary copy limits, and copy-equivalent DBF IDs. Exceptional deck-size, sideboard, or replacement rules are not implemented. Relevant unsupported cards are rejected.
- `expanded/game.py`: all-class extension of the old engine, preserving old modules and model fingerprints. Includes eleven base powers, hero attack separate from weapons, weapon-specific lifesteal, Overload, spell damage, Stealth/Elusive targeting, Freeze, Combo, Outcast, direct effects and a small explicit deathrattle set. No general aura/secret/quest/Discover system yet.
- `expanded/status.py`: checks code identity, displays coverage and missing IDs, and exposes the user-run fixture runner. A fixture receipt is tied to the current code; passing it never implies full Standard readiness.
- `tests/test_expanded.py`: targeted behavioral fixtures. Available through notebook 06. Tests are not invoked at import.

A `Deck` has a hero class, a tuple of card IDs, and a rune tuple. Non-DK classes use `(0, 0, 0)`. `Game([deck_a, deck_b])` rejects unsupported input before drawing. Policies receive `observe(viewer)` only. Its `hero_attack`, class, overload, and frozen-state fields differ from the old policy schema. The old policy is **not** automatically reused.

Unanticipated effect exceptions restore game state and RNG. This is deliberately conservative and may be slow because state is copied per action. Performance optimization is deferred until rule validation.

## Known boundary

The extension remains an experimental subset across classes. It does not support current Standard decks generally, reconstruct all Hearthstone timing rules, or claim external conformance. Generated local tokens model only the effects explicitly listed. The complete reference-card archive is not used as a random generation pool. Modern mechanics such as Discover choices, Rewind, Imbue, Herald, Shatter, Prepare, and quests are not approximated.

Unsupported cards fail explicitly. Full Standard training is unavailable until the engine, legality handling, and an expanded agent interface exist and have been validated. Notebook 06 runs rule fixtures only when the user clicks Run All, then produces a missing-card report; it runs no training or match batch.


## Version 0.2 — corpse and summon batch

Notebook 07 loads the updated engine after a kernel restart. Notebook 06 and its saved outputs are preserved as the prior run; the old validation receipt will not count for changed code.

Fourteen additional cards: Army of the Dead, Boneguard Commander, Tomb Guardians, Frostwyrm’s Fury, Battlefield Necromancer, Mountain Bear, Voidlord, Lightshower Elemental, Prize Vendor, The Curator, Immortalized in Stone, Shadow Ascendant, Crystal Merchant, and Runaway Blackwing.

New operations handle raising corpses into explicitly registered tokens, applying Reborn to the actual summoned Guardians, deathrattle summons at the dead minion’s position, tribe-filtered draws, and selected end-of-turn effects. Tokens are pinned to the archived card records. There is no unrestricted generation from the full archive.

All classes now track corpses, correcting the previous DK-only implementation: [Blizzard’s 25.4 patch notes](https://hearthstone.blizzard.com/en-us/news/23913671). Risen Ghoul and Risen Footman have explicit no-corpse exceptions, as specified by their archived text; see [Risen Ghoul in Blizzard’s card library](https://hearthstone.blizzard.com/en-us/cards/79278/).

The full-board corpse spending and complex simultaneous death timing still need independent game-reference validation. Prepared checks describe intended subset behavior; passing them alone does not establish external conformance. No tests, games, notebooks, or training were executed by the assistant.
