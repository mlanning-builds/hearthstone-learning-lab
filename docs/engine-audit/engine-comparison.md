# Simulator foundation decision

> Current work sequence: [engine decision and bounded completion plan](recovery-plan-2026-09-23.md). Card expansion is on hold pending the shared-system coverage specification.

> Superseded by [our engine rules review](our-engine-rules-review.md): keep our engine and selectively adopt useful architecture. The candidate-count audit below remains valid; its migration recommendation is withdrawn.

Source audit date: 2026-09-22. Decision: use a pinned Fireplace fork as the preferred foundation for a controlled migration. Keep the existing notebooks and engines intact until the replacement passes user-run checks. This is a source-based recommendation, not a claim that migration or full Standard support is complete.

## What the comparison found

We compared both repositories against this project's frozen 1,185-record Standard catalog. This audits that snapshot; it does not independently certify today's rotation or every eligibility exception.

| Finding | Fireplace | RosettaStone |
| --- | ---: | ---: |
| Catalog records with source candidates | 174 | 178 |
| Exact current ID matches | 0 | 105 |
| Matches requiring historical aliases only | 174 | 73 |
| Candidates outside our 253 written card effects | 39 | 39 |
| Preferred candidates with differing old stats or normalized rules text | 93 | 46 |
| Death Knight class-card candidates | 0 | 0 |
| Sets containing matches | Core only | Core only |

These are **reuse candidates, not working-card counts**. Fireplace detection finds executable top-level classes/assignments; RosettaStone detection finds uncommented card registrations, which can include empty definitions. These different source structures do not support a direct quality ranking. Vanilla cards and rules supplied only by tags may work without matching this method. Conversely, a matching script may be stale, unloaded, incomplete, or missing generated cards. Equal text does not prove equal behavior; different text can be an editorial change rather than a rules change.

Neither repository is a drop-in full-Standard simulator. Importing card metadata cannot supply missing executable effects.

## Why Fireplace

Fireplace provides a Python game engine, card actions, event handling, and existing historical card logic. That is a better fit for a hobby project controlled through Jupyter than adding a C++ build and a new gameplay binding layer. The main benefit is reusing engine infrastructure, not suddenly obtaining hundreds of current card implementations.

RosettaStone has native gameplay code and recent location work. However, its Python module currently exports cards, decks, enums, loaders and utilities—not a game/action interface for reinforcement learning. Its Return of the Lich King implementation module is empty. Choosing it would add Python binding work without solving modern card coverage. No speed comparison was performed.

Fireplace also has substantial gaps: its documented rules coverage is old, its card database sets the format year to PHOENIX, and missing scripts can become empty behavior classes. We must replace that permissive loading with an explicit support manifest before using it for our experiment. Modern locations and Death Knight systems need implementation and verification.

Our current environment is Python 3.9.6; Fireplace documents Python 3.10+. Migration needs a separate compatible kernel and pinned dependencies. Do not modify the existing working environment in place. Both upstream projects use AGPL licenses; retain the applicable license and notices when distributing a derived project on GitHub.

## Concrete migration sequence

1. Create an isolated, pinned Fireplace integration alongside the existing project. Include its LFS card definitions and dependency lock. Preserve notebooks, saved models and existing results.
2. Add a small adapter exposing reset, player-visible observation, legal actions and step. Hide the opponent's hand and deck order from the policy. Include targeting, choice resolution, mulligans and end-turn actions.
3. Connect the frozen catalog to explicit deck legality and card-support manifests. Enforce class, copies, deck size and Death Knight rune restrictions. Reject unsupported effects and generated-card dependencies rather than treating them as blank cards. Replace the historical format defaults deliberately.
4. Implement shared missing systems first, including Death Knight corpses/runes and modern card types. Review and port our existing 253 written effects against the new engine; they are not automatically compatible or verified.
5. Complete the requested catalog and its generated cards. Track metadata imported, effect written, dependencies complete and behavior checked separately. Do not label the whole pool playable based on import counts.
6. Provide a Jupyter validation notebook with progress bars, actionable failures and save/resume support. The user runs it. Cover event order, deaths, targeting, choices, secrets, resource spending and deterministic seeded replay, then card-specific fixtures. Do not begin a full-Standard training run until the chosen coverage gate passes.
7. Train play decisions on fixed decks first, using an opponent pool of baselines and previous policy snapshots. Evaluate on held-out seeds with both starting seats. Then evolve legal random decks and alternate deck search with policy improvement. Evaluate finalists against the same diverse opponent pool with uncertainty estimates.

The eventual output should say “strongest deck found against this evaluation pool,” not promise a mathematically best deck. A weak or narrow opponent can make a bad deck look excellent.

## Evidence and reproducibility

- [Fireplace source](https://github.com/jleclanche/fireplace/tree/47a2572a000db66645bb74a425a090d51f1004fa), pinned revision `47a2572a000db66645bb74a425a090d51f1004fa`.
- [Fireplace database loading and defaults](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/__init__.py).
- [RosettaStone source](https://github.com/utilForever/RosettaStone/tree/e10749b5f0c08d3a6135bce317cb11d1738846ad), pinned revision `e10749b5f0c08d3a6135bce317cb11d1738846ad`.
- [RosettaStone Python exports](https://github.com/utilForever/RosettaStone/blob/e10749b5f0c08d3a6135bce317cb11d1738846ad/Extensions/RosettaPython/main.cpp).
- [RosettaStone Lich King implementation](https://github.com/utilForever/RosettaStone/blob/e10749b5f0c08d3a6135bce317cb11d1738846ad/Sources/Rosetta/PlayMode/CardSets/ReturnOfTheLichKingCardsGen.cpp).

The accompanying `engine-source-audit.json` contains one row per catalog record, candidate source paths and line numbers, alias method, metadata differences, repository revisions and input hashes. `audit_engines.py` reproduces the static comparison using local checkouts at those revisions. It reads source and data; it does not import either simulator.

```sh
python3 audit_engines.py \
  --project '/path/to/death-knight-lab' \
  --fireplace '/path/to/fireplace' \
  --rosetta '/path/to/RosettaStone' \
  --fireplace-carddefs '/path/to/materialized/CardDefs.xml' \
  --output engine-source-audit.json
```

The materialized Fireplace XML is available at `https://media.githubusercontent.com/media/jleclanche/fireplace/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/CardDefs.xml`. Its SHA-256 is recorded in the JSON. A Git LFS pointer file is not sufficient input.

No simulator imports, notebook cells, unit tests, games, training, installation or performance benchmarks were run for this audit. The project engine and notebook behavior remain unchanged. This deliverable completes the comparison and decision; the migration sequence above remains implementation work.
