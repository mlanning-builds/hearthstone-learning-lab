# Frozen historical weapon primitives

Registered generated-only bodies for these textless Legacy weapons:

| Identity | Frozen cost | Attack | Durability |
| --- | ---: | ---: | ---: |
| CS2_080 — Assassin's Blade | 4 | 2 | 5 |
| CS2_106 — Fiery War Axe | 2 | 3 | 2 |
| CS2_112 — Arcanite Reaper | 5 | 5 | 2 |

The source is the local `data/standard/all_cards.json.gz` archive pinned to
36.6.0.251952. Each record has zero in `durability` and its actual durability
in `health`; the existing equipment path already handles this representation.
Do not replace these records with contemporary or remembered card versions.

Two focused checks pass across all three identities: ordinary paid play
preserves cost, printed weapon stats and the physical card UID, and successive
hero attacks consume durability until the equipment leaves play. The
registry change supplies explicit empty effect lists because these records have
no printed triggered effect. It grants no historical pool membership and does
not make these identities eligible for Standard deck construction.

These bodies are now in the candidate. A new full-suite receipt is required for the changed source.
