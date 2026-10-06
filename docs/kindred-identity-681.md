# Kindred identity and partner selection

Current candidate: 681 written collectible implementations, 504 missing from the frozen 1,185-card Standard catalog. This is shared-rule progress within the consolidated milestone, not a completed large card delivery.

The pinned card records do not reliably encode Kindred in `mechanics` or `referencedTags`. `expanded/kindred.py` now declares all 27 actual Kindred collectible identities in the pinned catalog. Torga and Primalfin Challenger merely refer to Kindred and are excluded. No runtime card-text parser is used.

Torga (TLC_102) draws a Kindred card from the actual deck, then a partner from the remaining deck. Minion partners share a recognized Constructed minion type; spell partners share a spell school. Dual-type and All-type minions are handled by the common selectors. The two draws use the shared continuation scheduler, preserve physical card modifiers, and can suspend at an intervening choice.

The existing live Kindred check now uses the canonical selector with singular `race` fallback and recognized type filtering. A reusable common-type intersection helper is also available; it does not yet connect City Chief Esho or decide that card's empty-deck semantics.

## Evidence

Printed definitions and hashes come from the pinned local catalog. The [Torga reference](https://hearthstone.wiki.gg/wiki/Torga) records the September 2025 fix to drawing an activating partner. This is supporting evidence, not an independently replayed client trace.

18 focused scenarios cover missing keyword metadata, false-positive references, both minion types, All types, spell schools, no Kindred/partner, physical modifiers, full-hand burn, listener timing, choice replay and live Kindred behavior. Full suite: **1529 passed**, zero failures/errors. Source-matched receipt: `validation-7e865a9c8b764f8a9ae67d9aa1696f5b.json`. Candidate STATUS.md records its full path and fingerprint.

Remaining questions are explicit in `expanded/fidelity_gaps.json`: independent random-selection and overdraw traces, and the other type-family cards' multi-type assignment and empty-deck rules. Menagerie Mug, City Chief Esho, Flight of the Firehawk and Tortollan Storyteller remain unimplemented. Their text alone does not establish all those interactions.

No training or deck search ran. Full Standard readiness remains false.
