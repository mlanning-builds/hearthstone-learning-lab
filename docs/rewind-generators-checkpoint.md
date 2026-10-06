# Remaining Rewind runtime — October 5, 2026

**868 live registrations; 317 staged recipes. No new live cards admitted.** Eleven of the twelve remaining Rewind-family cards now have staged runtime declarations, with Morchie explicitly unresolved. Complete outcome pools and interaction review remain necessary for production admission.

| Cards | Runtime |
| --- | --- |
| Semi-Stable Portal; Aeon Wizard | Random generation with a discount or own-class restriction |
| Instant Multiverse | Resumable 12-Mana summon budget, board-space limits and normal Overload |
| Mend the Timeline | Two random Holy spells and one heal using their combined printed Costs |
| Druid of Regrowth | Two random Nature spells through the internal casting system |
| Stadium Announcer | Both players equip weapons; only the caster's weapon gets +1/+1 |
| Time Machine | Deathrattle generation from an explicit Rewind-keyword pool |
| Mister Clocksworth | Two Legendary summons with three available rerolls |
| Wormhole | Random 3-Cost Beast summon and forced attack |
| Sands of Time | Any-class spell Discover followed by own-class eligibility after Rewind |
| Raptor Herald | Beast Dark Gift Discover with Kindred discount |

Existing snapshot logic is reused rather than duplicated. Focused checks exercise restored resources, hand/board contents, counters, randomness, repeated choices and surviving Rewind charges after bouncing a minion. Staged cards remain absent from the live registry. Test fixtures temporarily install their declarations and controlled outcome pools.

## Metadata and learning fixes

The frozen card records omit Rewind from their `mechanics` arrays. The engine now has an explicit 17-card keyword membership list, verified against the frozen printed effects. Time Machine and Morchie mention Rewind without having it and are excluded from that list. This fixes both candidate-pool planning and runtime selector matching; it does not automatically approve a generation pool.

Chooser observations now expose the remaining Rewind budget. Schema v35 encodes it separately for Keep and Rewind actions, avoiding a shared state-only feature that would cancel when comparing those choices. Opponents still see only a waiting choice; snapshots remain private.

Internal casting admits the newly implemented Rewind spell operations and the prior transformation spell operations through the existing resumable scheduler. Internal casts do not initiate a paid-play Rewind or count as a card played from hand.

## Validation

41 focused Rewind-generator tests and 11 completion-queue tests passed. Consolidated regression: **3,040/3,040 tests passed**, zero failures/errors/skips. All **22 smoke games finished**, zero errors/caps, with 2,508 feature decisions checked. Both runs used unchanged fingerprint `0f264629e7ff595e4a8fb85ec9f55fea7dc77dee85fa11b87d04379f596e3fe5`. Receipts are recorded in the [candidate status](../staging/rebased-88/STATUS.md).

Coverage includes three rerolls without extra payment or duplicate final summons; missing-pool rollback; explicit keyword membership; private, action-dependent budget features; zero-cost/full-board budget termination; combined healing and hand overflow; both-player equipment; forced combat; nested Discover; Kindred gifts; and automatic internal spell choices.

## Remaining gates

Every production outcome must be supported, including every eligible Nature spell's internal casting path. Pools are never truncated to supported cards. Timing, RNG order, mana-budget distribution, healing aggregation, weapon destruction events and nested interactions still need independent conformance evidence. The 256-step budget-summon limit raises an error for pathological chains; it is an engine safety limit, not an asserted Hearthstone rule.

Morchie's potential-outcome retention needs its own implementation and evidence. Ordinary repeated execution is not treated as equivalent. The [Morchie reference](https://hearthstone.wiki.gg/wiki/Morchie) notes automatic outcome retention instead of the normal Keep/Rewind choice; this does not resolve resource, identity or event interactions. The general mechanic is described in [Blizzard's expansion announcement](https://hearthstone.blizzard.com/en-us/news/24226328).

Known gaps are recorded in `expanded/fidelity_gaps.json`; the [all-card completion queue](engine-audit/completion-queue.md) now includes the eleven runtime declarations and corrected Rewind dependencies. No training or deck search ran.
