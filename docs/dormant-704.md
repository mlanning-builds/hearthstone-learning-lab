# Shared Dormant system — 15 collectible implementations

Candidate: `staging/rebased-88`. Pinned regular Standard snapshot: 36.6.0.251952, September 18, 2026. These are written implementations with internal scenarios, not independent client certification or a live-rotation claim.

Added: CORE_BT_156, EDR_416, EDR_469, EDR_820, EDR_840, EDR_841, EDR_979, JAIL_850, JAIL_997, MEND_040, TIME_022, TIME_046, TIME_063, TIME_442, TLC_253. The Sheep and three Dreadseed records are fixed dependencies and do not inflate the collectible count.

The shared board now distinguishes active minions from Dormant entities. Both occupy board slots; normal targeting, damage, buffs, aura effects, attacks and ordinary listeners operate only on active minions. Dormant state is visible to both players. Feature schema v14 marks this observation change; older policy checkpoints must not silently use it.

Owner-turn countdowns run in the existing turn continuation system. The same foundation handles Hero Power awakening, a full board, newest-expansion card plays, the Ogre's growth/wake roll, and a Warden's exact imprisoned entity. Ancient of Yore uses the resumable Armor/draw turn queue while Dormant. Awakening restores summoning sickness; Rush and Charge retain their normal restrictions. The Hound Dreadseed's awakening grants temporary hero Attack, including repeat awakenings.

Nozdormu's newest expansion is explicitly pinned to ESCAPEFROM_VIOLET_HOLD. Updating the catalog requires reviewing that identity. Tranquil Clearing remains unsupported: its wording is “falls asleep,” and it has not been silently implemented as Dormant.

## Checks and limits

44 focused scenarios cover all 15 collectible entries, the three Dreadseeds, both Wyvern branches, board limits, either player's board, active aura source/recipient removal, preserved buffs/damage, Silence, external timers, repeated awakening, temporary effect expiry, death releases, invalid-action rollback and visible Dormant state. The full regression suite passed **1,597 tests**, with zero failures/errors. Its source-matched receipt is recorded in candidate STATUS.md. The general returned-token scenario now checks that Dormant tokens cannot be bounced until awakened, and become Dormant again when replayed.

Random legal-play validation completed 22/22 games with no errors or action caps and checked 2,402 feature decisions. Receipt: `staging/rebased-88/runs/random_validation/summary-a0a4b3ac27e7-b20238572ff24cbd98fd370e419a0422.json`. This is compatibility/invariant testing of implemented decks, not training or a client-fidelity oracle.

The new tests also caught a temporary hero-Attack lifetime issue when a Hound awakens during the opponent's turn. Temporary hero Attack now expires at that turn's end for either owner. Captive references are encoded by visible side/board position rather than arbitrary entity numbers.

Copy, transform and summon-notification interactions need independent reference traces. The current explicit behavior is preserved in `expanded/fidelity_gaps.json`: copying preserves the source's active/Dormant state; transformation starts printed dormancy; initial Dormant entries and awakenings do not emit ordinary summon callbacks. These assumptions are not described as certified behavior. Countered-spell Nozdormu progression and exact ordering against other start-turn triggers also remain reference-validation work.

## Sources

- Pinned card records and tags in `data/standard/all_cards.json.gz` and `card_tags.json` supply identities, text and fixed tokens.
- [Advanced rulebook, board entities and adjacency](https://hearthstone.wiki.gg/wiki/Advanced_rulebook?section=46): Dormant entities occupy board slots but are not normal minion/character targets; they block adjacency damage paths.
- [Dormant rules](https://hearthstone.wiki.gg/wiki/Dormant-related): awakening and copy exceptions require separate treatment.
- [Tranquil Clearing](https://hearthstone.wiki.gg/wiki/Tranquil_Clearing): wording checked separately from Dormant.

This is progress within the existing 60-card delivery: 8 previous additions + 15 Dormant additions = 23/60, with 37 still outstanding.
