# Scope checkpoint — 2026-09-23

Static inventory only. No simulator, notebook, game, training or engine fixture executed.

Catalog: **1185**. Effects written: **503**. Missing: **682**.
Current suite receipt matches candidate: **False**. Last receipt: 1095 checks; do not treat it as current.

All card IDs have inventory rows. **Semantic mapping is not complete:** reviewed owners remain null for all rows. This block establishes the ledger and a review queue; it does not complete milestone 1.

| Priority | Shared system | Candidate cards* | Missing effects* |
| --- | --- | ---: | ---: |
| 1 | Play, summon, death and turn event ordering | 790 | 491 |
| 2 | Stats, costs, auras, copy and Silence | 620 | 370 |
| 3 | Generation eligibility and resumable choices | 408 | 331 |
| 4 | Format and exceptional deck construction | 24 | 24 |
| 5 | Attack legality, damage and healing | 616 | 293 |
| 6 | Draw, discard, shuffle, resurrection and history | 427 | 272 |
| 7 | Mana, Corpses, class resources and Hero Powers | 128 | 85 |
| 8 | Secrets, locations and activations | 52 | 29 |
| 9 | Dormant and awakening | 17 | 17 |
| 10 | Quests, progress and rewards | 14 | 14 |
| 11 | Hero replacement and alternate powers | 9 | 9 |
| 12 | Rewind and state restoration | 19 | 19 |
| 13 | Modern composite mechanics | 114 | 94 |
| 14 | Unclassified card-specific behavior | 9 | 1 |

*Overlapping text/tag hints, not verified affected-card counts or additive totals. Exact candidate IDs, matching terms, entry points and prerequisites are in the JSON files.

## Files

- `coverage-ledger.json`: raw card records/tags, references, receipt linkage and explicit unknowns for every catalog ID.
- `coverage-ledger.csv`: compact inventory for browsing.
- `shared-system-backlog.json`: prioritized provisional groups, exact IDs, prerequisites and source entry points.
- `generated-references.json`: non-target literal references, kept separate from collectible coverage.
- `generation-pools.json`: unresolved pool review queue and required schema.
- `rule-document-index.json`: existing document references; their URLs are not automatically trusted as conformance evidence.
- `known-fidelity-gaps.json`: snapshot of the existing gap register.
- `rule-evidence-checklist.md`: twelve high-impact scenarios and evidence acceptance requirements.

## Next bounded block

Proposed ceiling: 90 active minutes. Review the summon/play lifecycle and its affected-card mapping first. Deliver an explicit phase contract, a checked source-to-event map, and evidence status for scenarios 1–4. Implement no new collectible cards. If independent outcomes cannot be established, report the missing evidence and stop instead of guessing. Other mechanic-family mappings remain a review backlog; no whole-project completion estimate yet.

## Following block delivered

The [summon/play phase contract](../summon-contract-2026-09-23/CONTRACT.md) maps current entry paths and proposes explicit provenance/continuations. The first four independent scenarios remain unverified; the recruitment setup was corrected against pinned card costs. Engine code was not changed.
