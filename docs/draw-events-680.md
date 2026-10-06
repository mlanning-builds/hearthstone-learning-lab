# Shared draw events: 678 → 680

The candidate now has 680 written collectible implementations and 505 missing from the frozen 1,185-card Standard catalog. This is shared-engine progress within the next consolidated milestone, not a completed large card release.

## Changes

- Normal, indexed, filtered and explicit cross-player transfer draws share one successful deck-to-hand transition.
- Successful draws queue a private snapshot for existing listeners. Drawn identities are not added to public draw logs.
- Burn, fatigue, generation, deck Discover and opening-hand draws do not publish a successful-draw event.
- Ordinary multi-draw, filtered multi-draw, draw-and-pick, draw-type checks, opponent-draw/copy and minion-draw/buff groups use resumable per-draw checkpoints.
- Keymaster Alabaster (CORE_SCH_717) copies the opponent's drawn card with a new physical identity and cost 1. Eredar Deceptor (CORE_TTN_843) summons its reviewed 1/1 Rush Demon token TTN_843t1 on its controller's successful draw.

The pinned archive supplies the exact Core records and generated dependency. The [card-draw reference](https://hearthstone.wiki.gg/wiki/Card_draw) distinguishes successful draws from overdraw, fatigue and other deck-to-hand transitions. This reference is supporting rules evidence, not an independently replayed client trace.

## Verification and remaining work

28 new scenarios cover successful draws, failed filtered draws, burn/fatigue, full board/hand, silence, listener snapshots, private observations, physical copy independence, cross-player transfer, turn-start draws, per-draw checkpoints, choices, terminal interruption and deterministic replay. Full suite: **1,497 passed**, zero failures/errors; receipt `validation-c791191dc7af4a8083bd353276c041d0.json` matches current source. Literal dependency audit has no missing IDs. Candidate STATUS.md records the full receipt path and source fingerprint.

The shared draw system is **not complete**. The subsequent [compound-draw integration](compound-draw-continuations.md) converts distinct-cost, cheap-repeat, excess/kill, cascading-discount and refill effects to per-draw frame continuations. Future casts-when-drawn, independent timing evidence, refill-count semantics and internal calls that bypass frame splitting remain explicit gaps in `expanded/fidelity_gaps.json`.

No training or deck search ran. No user notebook run is needed for this integration. Full Standard readiness remains false.
