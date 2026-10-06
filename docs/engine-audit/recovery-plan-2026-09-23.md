# Engine decision and bounded completion plan

Date: 2026-09-23. Scope: regular Hearthstone Standard, all 11 classes, the full pinned catalog. Mercenaries and Battlegrounds are excluded. This document supersedes the work sequence in the earlier engine comparison and rules review; their historical evidence remains available.

## Decision

Retain the current Python candidate as the provisional foundation. Do not start a wholesale migration or resume incremental card expansion. First complete a bounded architecture and coverage specification. No inspected alternative establishes a cheaper route to this project's full Standard target. This is a decision under uncertainty, not a claim that our engine is more correct or faster.

The earlier audit recommended Fireplace, then a rules review reversed that recommendation. Work subsequently continued through many card additions without a complete capability map or independent correctness gate. Repeating that pattern would not solve the problem. Existing notebooks, models, reports, root engine, and candidate are preserved.

## Evidence checked

| Option | Evidence | Decision for this project |
| --- | --- | --- |
| Fireplace | Python; README documents patch 17.6 coverage and Python 3.10+. Pinned source audit finds 174 historical Core candidates in our 1,185-record pool; no Death Knight class-card candidates. Current local Python is 3.9.6. | Useful rules architecture reference; migration still needs modern systems, most cards, and an environment/adapter change. No migration now. |
| RosettaStone | C++; latest inspected pinned revision includes August 2026 location work. README's Standard table describes older sets. Pinned source audit finds 178 Core candidates, no Death Knight class-card candidates; inspected Python exports do not expose a gameplay action interface. | Recent maintenance does not establish current Standard coverage. Would add binding/build work. No migration now. |
| SabberStone | C#; README's 98% coverage claim explicitly dates to July 2019 and Year of the Dragon. | Historical infrastructure/reference, not demonstrated target-patch support. |
| Spellsource | Java card engine; current README describes a community-authored game. Its missing-card count combines public and private card content. `.gitmodules` points at an internal content repository that was not publicly accessible in this review. | Potential lead, but public, licensed, target-patch executable coverage is unverified. Do not use its headline count to justify migration. |
| Hearthbreaker | Python; README explicitly says development stopped and cards stop at The Grand Tournament. | Not a current Standard replacement. |
| HearthEnv | Python/Gym wrapper built on Fireplace. | Useful interface example; does not independently solve missing game rules/cards. |

This was a source/documentation audit, not an installation, performance benchmark, or conformance test of these alternatives. Search cannot prove no suitable fork exists. Network metadata access failed; current upstream activity was not verified uniformly. Do not describe all projects as abandoned.

The saved static audit pins Fireplace `47a2572a000db66645bb74a425a090d51f1004fa` (2025-12-19) and RosettaStone `e10749b5f0c08d3a6135bce317cb11d1738846ad` (2026-08-04). Rechecking its per-card rows against today's 503 written IDs leaves 27 Fireplace and 23 RosettaStone candidates outside our written set. These overlap and must not be added together. They are source candidates, not validated imports. The old report's 39 each used a 253-card local baseline.

Licensing inventory: Fireplace and SabberStone declare AGPLv3-or-later; the prior pinned audit records AGPL for RosettaStone; Hearthbreaker declares MIT. Spellsource component/card licensing and HearthEnv licensing were not established in this review. No upstream code was copied. Verify exact component licenses and retain notices before any reuse or GitHub distribution; no project license was selected here.

Primary sources:
- https://github.com/jleclanche/fireplace
- https://github.com/utilForever/RosettaStone
- https://github.com/utilForever/RosettaStone/commits/main/
- https://github.com/HearthSim/SabberStone
- https://github.com/hiddenswitch/Spellsource
- https://github.com/hiddenswitch/Spellsource/blob/master/.gitmodules
- https://github.com/danielyule/hearthbreaker
- https://github.com/albertwujj/HearthEnv

Local reproducible evidence: `docs/engine-audit/engine-source-audit.json`, its audit script, `staging/rebased-88/expanded/implementation_index.json`, and `staging/rebased-88/expanded/fidelity_gaps.json`.

## Actual baseline

- Frozen target: 1,185 catalog records; legality exceptions still need independent verification against the pinned patch/date.
- Last validated candidate: 502 written implementations, 1,095 passing checks. These are internal regression checks, not proof of Hearthstone equivalence.
- Working candidate: 503 written implementations, including Arachnathid; latest change unvalidated. 682 records have no written implementation.
- Root active engine: 291 implementations. Do not confuse its notebook with the candidate.
- Fidelity-gap register: 19 entries, explicitly not exhaustive. Generated-pool closure, general enchantment/copy behavior and event ordering remain incomplete.
- Local training/checkpoint/evaluation scaffolding exists. No demonstrated strong trained policy or best Standard deck exists.

The preceding validation attempt was not executed because automatic approval review hit a usage-limit error. This audit does not retry that action or make its results current.

## Completion milestones and gates

| Milestone | Usable result | Acceptance evidence | Stop/replan condition |
| --- | --- | --- | --- |
| 1. Complete scope and architecture map | Every collectible and reachable generated object has an explicit implementation/dependency status and owning shared system. | Catalog hash, exact IDs, reviewed effect mapping, generated-pool definitions, and named unknowns. Distinguish metadata imported, effect written, dependencies complete, regression checked, independently checked. | Any unclassified effects remain visible; no claim that a keyword/text scanner certifies behavior. |
| 2. Shared rules foundation | Consistent play, summon, death, choice, combat, cost/enchantment and zone-transition lifecycles. | Independent expected traces plus regression fixtures for each boundary. Include countered spells, simultaneous deaths, summon listeners, copy/Silence, modifier order, choices that suspend/resume, control changes, and hidden information. | If evidence is missing, affected behavior remains unverified; do not invent outcomes to make tests pass. |
| 3. Full pinned Standard support | All legal decks and all reachable generated effects can execute. | No missing card effects/dependencies; checked legality exceptions, runes, class/copy/deck-size rules; all required mechanic families implemented, including those identified in milestone 1. Full-pool mode fails closed if any prerequisite is missing. | Never silently remove unsupported cards from random generation or deck search. |
| 4. Reproducible Jupyter release | User can install, Run All, observe progress, interrupt, resume, and inspect failures. | Clean-environment notebook check; deterministic replay; both-seat hidden-information checks; fingerprinted reports; bounded diverse integration games; games/sec and memory measurements on this Mac. | Any unresolved integration failure or incompatible checkpoint blocks release. Random games alone do not certify rules. |
| 5. Learn to play | A policy improves against a frozen, diverse evaluation panel on fixed legal decks. | Local explicit training budget; random/tactical baselines and past-policy opponents; held-out seeds and both seats; learning curves and uncertainty estimates. | No improvement or exploit-driven wins trigger diagnosis, not a longer automatic training run. |
| 6. Search decks | Strongest decks found per class and across a declared opponent distribution. | Start from legal random decks; alternate deck proposals and policy improvement. Include Death Knight rune profiles. Re-evaluate finalists on untouched seeds/opponents; paired comparisons, confidence intervals, and cap accounting. | Report panel-specific strength and uncertainty; do not label results universally optimal. |
| 7. GitHub handoff | Reproducible hobby project others can run. | README, pinned data provenance, supported-patch declaration, suitable license/notices, small sample results, install/run instructions, and excluded large artifacts. | Publishing remains a separate user-authorized action. |

Full Standard is the intended release scope throughout. Small scenarios are development checks, not a substitute product or a claim to have completed that scope. Imported card text/tags supply parameters and hints; they do not contain a complete executable rules program. Shared systems should handle repeated behavior; exceptional card behavior still needs explicit definitions.

## Next block: specification only, maximum 90 minutes of active work

This is a proposed ceiling for the next implementation-planning block, not a completion estimate for the whole project. No automatic continuation beyond it. Do not start another card batch or long training run within it.

Deliverables:
1. One machine-readable coverage ledger covering all 1,185 IDs, preserving raw text/tags and linking existing implementation/dependency/validation evidence. Mark automated grouping as provisional. Include generated objects/pools separately; do not inflate collectible coverage with tokens.
2. A prioritized shared-system backlog with exact affected IDs, current code entry points, prerequisites, independent evidence required, and acceptance examples. Start with summon/event phases, enchantment/copy/cost ordering, and complete generation eligibility; confirm priorities from the ledger rather than assuming every missing card fits those groups.
3. A rule-evidence checklist with the first 12 high-impact independent scenarios. Reuse valid existing evidence; separate authoritative documentation, patch-matched client traces, historical engine behavior, and assumptions.
4. A checkpoint report: completed artifacts, remaining unclassified work, what the next bounded block would deliver, and its proposed limit. If the ledger cannot be reviewed within the limit, deliver the partial ledger honestly and stop; do not switch to easy card additions.

Do not attach a new effort estimate to the whole project until milestone 1 identifies the remaining systems and a representative system block has been measured. Exact token use is not inferred from elapsed time. Any long training run requires its own explicit game/time budget, entered in Jupyter by the user or explicitly authorized.

## Rules preventing another development loop

- Each block names one capability deliverable and acceptance checks before edits begin.
- Card-count and test-count growth are supporting metrics, never the release milestone.
- A general "go" advances one declared block; it does not authorize an unbounded succession of new blocks.
- At the block limit, report outcome and remaining gaps. No background continuation is scheduled by this plan.
- Change the engine decision only when new evidence shows a better route: accessible source and license, exact target-patch coverage, a working Jupyter-facing adapter, independent rule checks, and a concrete migration-versus-repair comparison.
- Keep the older decision documents as provenance, with this plan linked as the current work sequence.

## Scope checkpoint delivered

See [2026-09-23 scope checkpoint](scope-2026-09-23/CHECKPOINT.md), [full ledger](scope-2026-09-23/coverage-ledger.json), and [twelve rule-evidence scenarios](scope-2026-09-23/rule-evidence-checklist.md). Inventory is complete; semantic ownership and generated-pool closure are explicitly unfinished. No engine or training execution occurred. The proposed next block is the summon/play phase specification, capped at 90 active minutes.
