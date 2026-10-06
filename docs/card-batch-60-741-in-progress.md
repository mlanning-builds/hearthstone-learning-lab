# Former 60-card work queue — superseded October 1, 2026

**Historical plan:** the user replaced fixed card-count batches with complete mechanic deliveries. Use the [mechanic roadmap](MECHANIC_ROADMAP.md). The 23 implemented cards below remain valid progress; the old 741 target is no longer a delivery requirement.

Baseline: 681 collectible implementations, 504 missing, pinned regular Standard snapshot 36.6.0.251952. Target: 741 implementations, 444 missing. This document is a work queue, not a claim that the target has been reached.

The first eight cards have implementations and focused scenarios: EDR_849, JAIL_101, TLC_240, TLC_444, TLC_465, EDR_810, EDR_814, EDR_817. These cover shared Bonus Effect selection/transfer and the fixed Leech family. Generated tokens are not counted as collectibles. Full-suite receipt is recorded in candidate STATUS.md once complete.

The [shared Dormant group](dormant-704.md) adds another 15 collectible implementations. Current progress: **23/60**; 37 remain in this delivery. The candidate is at 704/1185 written implementations, with 481 missing. This is not a completed 60-card release.

## Planned scope

| Family | Total batch cards | IDs |
| --- | ---: | --- |
| Bonus Effects | 6 | CATA_206, EDR_849, JAIL_101, TLC_240, TLC_444, TLC_465 |
| Leeches | 3 | EDR_810, EDR_814, EDR_817 |
| Dormant | 16 | CORE_BT_156, EDR_416, EDR_469, EDR_820, EDR_840, EDR_841, EDR_979, JAIL_850, JAIL_997, MEND_040, MEND_044, TIME_022, TIME_046, TIME_063, TIME_442, TLC_253 |
| Forced combat | 17 | CORE_BT_120, CORE_TTN_866, CS3_020, DINO_400, DINO_428, EDR_014, EDR_453, EDR_819, RLK_720, JAIL_454, JAIL_511, TIME_434, TIME_443, TLC_107, TLC_230, TLC_810, TLC_821 |
| Origin and hand entry | 7 | CORE_REV_946, DINO_409, EDR_251, EDR_256, JAIL_205, JAIL_380, TLC_364 |
| Held progress | 7 | CATA_131, CATA_132, CATA_498, FIR_911, FIR_914, FIR_916, JAIL_501 |
| Type selection | 3 | CORE_WON_141, TLC_110, TLC_222 |
| Weapon attachment | 1 | EDR_525 |

Selections remain subject to rule and dependency review. No unsupported result pool may be narrowed merely to meet the count. The Void Soul family was excluded after inspecting its actual dependency: Void Soul is collectible JAIL_732, a random Demon generator with persistent upgrades, not a simple fixed damage token.

CATA_206 remains unsupported: its held keyword pair needs a consistent hand/deck/play/recruit/copy transition contract. Do not register it with only a normal-play hook. The Dormant foundation now covers 15 selected cards; MEND_044 remains separately pending because asleep is not assumed to mean Dormant. Forced attacks still need an owner-correct resumable combat path, with interruption and death checkpoints. The forced-combat foundation is not part of the completed additions.

## Evidence for the first systems

- [Blizzard 30.2 patch notes](https://news.blizzard.com/en-us/article/24122902/30-2-patch-notes): the constructed Bonus Effect pool replaces Stealth with Elusive and restricts Rush grants on ready/already-attacked/opponent-turn minions.
- [Bloated Leech](https://hearthstone.wiki.gg/wiki/Bloated_Leech) and the pinned archive: Health transfer, rather than a damage-and-heal pair.
- Pinned Hideous Husk text: a live Leech bonus, not a permanent player upgrade.
- 14 Bonus Effect tests and 10 Leech tests pass. Coverage includes keyword exhaustion, consumed shields, play versus summon, Silence, transfer, repeated attached deathrattles, board space, stacked/removed Husk bonuses, Health changes through Armor/Shield/Immune, and separate death checkpoints between Leeches.
- Independent client comparison is still pending. Ambiguous Rush edge cases, aura-granted keyword stealing and over-steal semantics are explicitly listed in `expanded/fidelity_gaps.json`.

The pre-batch random validation completed 22 games with no caps or errors and checked 2,557 feature decisions at the 681 fingerprint. It does not validate the eight new cards or prove gameplay fidelity.
