# Compound draw continuation integration

This change improves existing card behavior; coverage remains 680 written collectible implementations, with 505 missing from the frozen Standard catalog.

## Converted effects

Eight existing effect families now yield to the shared scheduler between individual draws:

- Bottom-of-deck draws (TIME_023).
- Distinct-cost draws (TIME_031), retaining selected costs across interruptions.
- Conditional second draw (JAIL_377), retaining the first card's cost decision.
- Cascading draw discounts (CATA_570), retaining the remaining discount budget.
- Hand refill (TIME_601), retaining the initial draw count.
- Excess-damage draws (TIME_858), retaining the damage result.
- Area-damage death-count draws (CATA_526), counting removed original victims after the damage checkpoint.
- Random-target kill-count draws (CORE_CATA_007), retaining the original kill count.

Counts and progress live in private continuation payloads, not public player observations. The implementation uses the same play/event/death/turn operation splitter as the previous draw groups. It does not open nested play frames.

## Verification

14 additional scenarios exercise real card plays, per-draw listener resolution, no eligible distinct costs, fatigue termination, zero-cost discount chains, intervening Discover choices, and deterministic replay of a suspended sequence. The focused draw suite has 42 passing scenarios. Full suite: **1511 passed**, zero failures/errors. Source-matched receipt: `validation-dcd4eaf08c49491aa2715bbc4dd8eac2.json`; literal dependency audit has no missing IDs. Candidate STATUS.md records the fingerprint and receipt path.

The continuation checks intentionally inject a choice-producing draw listener to test scheduler suspension; that fixture is a stress scenario, not an assertion that Eredar Deceptor normally Discovers.

## Limits and next work

No independent game-client traces were collected. Refill draw-count semantics, casts-when-drawn, and direct internal effect calls or nested wrappers that bypass frame splitting still need review. Simultaneous draw-both terminal behavior is preserved. The goal remains incomplete; this integration is not a claim of full Hearthstone timing fidelity.

No training, deck search, or notebook execution was required. Existing regression checks ran locally.
