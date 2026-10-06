# Held upgrades and turn counters

October 1, 2026. Candidate: `staging/rebased-88`. Pinned regular Standard catalog, all 11 classes; no Mercenaries or Battlegrounds. Coverage moves from 714 to **721 / 1,185** written collectible implementations, leaving **464**. The generated Emerald Whelp does not count as an additional collectible.

## Delivered group

All seven primary cards in the roadmap's `held_progress` family are connected:

| Card | Behavior |
| --- | --- |
| Felwood Treant | Track actual mana spent while held; choose temporary mana or permanent ramp |
| Broodwatcher | Track the higher spending threshold; add or summon both Emerald Whelps |
| Rafaams' Last Stand | Increase held damage while retaining two distinct random targets |
| Smoldering Grove | Upgrade draw count, then discard on expiry |
| Smoldering Strength | Upgrade permanent minion buff, then discard on expiry |
| Smoldering Ascent | Upgrade enemy-board damage, then discard on expiry |
| Picklock | Follow remaining mana in hand; snapshot values before paying for the play |

Payments use the shared mana-spend hook, including cards, hero powers, trades and spending effects. The card being played has left hand before its payment, so it does not advance its own held requirement. Copies retain their own progress; shuffle/return reset behavior follows existing physical-card transition contracts.

Held turn effects join the resumable turn frame. The engine snapshots participating cards, revalidates them at resolution, and prevents duplicate ticks in a single turn. Expiry calls the normal discard path, preserving discard history, listeners and subsequent choices. Multi-draw and multiple summons retain individual resolution checkpoints.

Feature schema **v16** includes the newly observable held counters and dynamic values; older policy checkpoints are incompatible. No training or deck search ran.

## Rule evidence and remaining fidelity work

Pinned card records define the thresholds and Emerald Whelp. [Picklock's notes](https://hearthstone.wiki.gg/wiki/Picklock) document the minimum-one values and in-hand scaling, frozen once played. The [Smoldering Grove](https://hearthstone.wiki.gg/wiki/Smoldering_Grove), [Strength](https://hearthstone.wiki.gg/wiki/Smoldering_Strength) and [Ascent](https://hearthstone.wiki.gg/wiki/Smoldering_Ascent) pages supply their initial one-point effects and three-turn expiry. [ClayByte's reveal-thread clarification](https://www.reddit.com/r/hearthstone/comments/1rdqyzf/new_warlock_card_rafaams_last_stand/) specifies that Last Stand gains one damage per turn without adding targets.

The implementation uses owner-end boundaries for held upgrades. Independent client traces are still required for Last Stand's exact turn boundary, copy/steal age retention, return/shuffle resets, ordering with other end triggers, and Picklock's silence/stat-setting/cost-setting interactions. These are recorded in `expanded/fidelity_gaps.json`. Local checks validate the declared model; they do not certify complete Hearthstone fidelity.

## Validation

43 focused scenarios pass, covering payments, discount amounts, hero powers, countered spells, thresholds, ramp caps, hand and board capacity, timer ownership, expiry/discard notifications, copy/reset behavior, draws, spell damage, distinct targets, dynamic stats, privacy and rollback. The full candidate suite passed **1684 checks**, zero failures, errors or skips. Random validation completed **22 games**, zero errors or caps, with **2,497 feature decisions checked**. Both used unchanged fingerprint `27c58fcc9509a2318a157f336f2511980aa2dbfdf1238172312fc193fe3c318e`.

- [Full-suite receipt](../staging/rebased-88/runs/expanded_validation/validation-3c79b242425a47328762b0bf04169167.json)
- [Detailed log](../staging/rebased-88/runs/expanded_validation/held-upgrades-721.log)
- [Random-run receipt](../staging/rebased-88/runs/random_validation/summary-27c58fcc9509-2230fc88168d4a82996b47935022df86.json)

## Next mechanic

Temporary cards and attached hand effects: complete the shared expiration, discount and attachment behaviors, connect all dependent cards whose exact generated pools are ready, and keep unresolved generation dependencies explicit. There is no card-count quota. No Jupyter reload is needed for this checkpoint.
