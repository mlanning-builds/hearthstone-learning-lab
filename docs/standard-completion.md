# Full Standard completion tracker

The user requested a complete card implementation before serious training. That remains the target. This engine is **not yet full Standard**. No unspecified card is approximated or silently treated as a vanilla minion.

The pinned September 18 catalog contains 1,185 collectible records. Version 0.10 has 291 explicit effect implementations; **894 are still missing**. All eleven base hero powers remain implemented. The card inventory in expanded/catalog_audit.json includes every record, its full rules text, its current implementation state, and dependency hints for organizing the remaining work. Those hints do not execute card text and are not a certification of completeness.

## Version 0.10: next Hero Power cost

Cult Neophyte uses the existing spell-only next-turn cost rule. Blowtorch Saboteur adds a persistent, stacking surcharge consumed only when the affected player successfully uses a Hero Power. Hero Power legality and payment now share one cost function. The surcharge survives turn changes and the source minion's removal. Public observations expose the surcharge and effective Hero Power cost, without hand information. Cost-setting auras and replacement Hero Powers remain outside this implementation.

The user reported all 171 v0.9 checks passed. Eight new scenarios bring the prepared total to 179. The assistant performed static checks only, with no simulator imports or execution. Prior results do not validate v0.10; run notebook 08 locally.

## Version 0.9: next-turn card cost increases

A separate timed player modifier now supports next-turn cost increases without consuming them when a card is played. Slow Motion affects every card type; Wave of Tar damages enemy minions and taxes only enemy minions. Modifiers have explicit start/end turns, stack additively with the existing supported cost adjustments, affect newly drawn/generated cards, and are publicly observable without exposing the opponent's hand. General ordered cost-setting enchantment interactions remain future work.

Eight new scenarios bring the prepared count to 171. Versions 0.8 and 0.9 remain pending user results. Static source/metadata checks only were performed by the assistant; no simulator imports, tests, notebook cells, matches or training were run. The user should reload notebook 08, restart its kernel and run all cells, then share the final report and failure tracebacks only.

## Version 0.8: 30-card expansion

Thirty more cards and nine generated-card dependencies are written. The [batch inventory](card-batch-0.8.md) lists the frozen rules text and scope. Twenty-six new checks bring the prepared total to **163**. An existing copy-stat bug was corrected: continuous aura bonuses must be recalculated at the copy's position, not embedded in its permanent stats.

The user's saved version 0.7 run passed all 137 checks. Version 0.8 remains pending user execution. No simulator code or tests were run by the assistant. Reload notebook 08 from disk (choose **Revert** on a file-conflict prompt), then restart the kernel and run all cells.

## Version 0.7: first Locations

Minions and Locations now share the ordered seven-slot battlefield. `Player.minions` and `Player.locations` expose separate entity views; attacks, minion targets, auras, board-wide effects and death processing use the appropriate view. Public observations identify entity type, Location durability and readiness. This is an observation-schema extension; the original subset model must not be used as an expanded policy.

Four frozen-catalog Locations have explicit implementations:

- **Sanguine Depths**: one damage and +2 Attack to a minion, as one effect before settling.
- **Chamber of Aspects**: choose an own-hand minion for +2/+2; the selected card stays private.
- **Erupting Volcano**: three one-damage missiles, or six after a successfully played Fire spell this turn; no Spell Damage bonus.
- **Underbelly Network**: summon its archived 2/1 Rat token with a draw-card Deathrattle.

They cost mana to play, can activate immediately, use one durability per activation and skip the owner's next turn before reopening. Activation uses the `activate` action rather than `play`, so it does not pay mana again or emit spell/minion-play triggers. A final charge removes the Location before its effect, allowing Underbelly to summon into the freed slot. Locations do not generate corpses.

All other Locations remain rejected. Reopening triggers, Location Deathrattles, random full-pool generation, Location transformation and general Location-targeting cards still need explicit work. No unsupported Location is treated as one of these four.

The same rules review corrected countered-card tracking: a countered spell does not increment the played-card counter or satisfy Volcano's Fire-spell condition.

Twenty new prepared checks bring the total to **137**. They cover mixed boards, targeting, cooldown, all four effects, summon dependencies, privacy, failure rollback and the countered-spell correction. None were run by the assistant. This is a written implementation, not independent Hearthstone conformance certification.

References: [Blizzard's Location overview](https://news.blizzard.com/en-us/article/23850855/welcome-to-the-players-tavern), [32.0 patch notes: final-charge summons and countered-card counting](https://news.blizzard.com/en-us/article/24187196/32-0-patch-notes), and the project's frozen card/token archive. The first source establishes the broad Location rules; the second establishes those two specific updates.

## Version 0.6: damage checkpoints

Combat damage and area damage now use an explicit damage batch. Settle requests inside a batch wait until the caller's checkpoint. Settle requests during queued trigger dispatch also wait for the outer checkpoint, so nested helpers cannot remove queued damage listeners midway through dispatch. Sequential missile effects outside trigger dispatch retain their individual checkpoints.

Eight prepared checks cover nested trigger checkpoints, nested damage batches, exception cleanup, simultaneous hero lethal, combat and area damage ordering, missiles hitting Deathrattle summons, and Deathrattle/Reborn board capacity. The nested-trigger check uses a synthetic trigger to isolate scheduler behavior. This is not full timing conformance: general nested action scheduling, interruption and choices inside triggers still need work. In particular, multi-stage effects invoked inside trigger dispatch currently share its deferred death checkpoint rather than a complete nested-action scheduler.

The user's 109-check v0.5 run passed and matched its source fingerprint before this update. Version 0.6 has **117 prepared checks**, not yet executed by the assistant. Card coverage remains 253.

## Version 0.5: one card-play lifecycle

All supported cards now use the expanded engine's shared payment, entry-to-play, effect frame and after-play flow. The old subset's explicit effects have been ported without changing the original engine or saved models. Older weapons now use the shared replacement hook instead of directly overwriting the weapon slot. This update adds no cards: coverage remains 253.

Eight prepared regression checks cover discounts, single payment/logging, legacy-path removal, buffed copies, corpse spending, summon position, lethal damage/healing, weapon replacement and rollback. The weapon-death-effect check uses a synthetic effect to isolate that hook, not a new real-card rule.

## Version 0.4: resumable card effects

Card effects now keep a private action frame. A player choice pauses the remaining operations, then resumes them exactly once; after-play callbacks wait for the final choice. Repeated choices, empty options, a full hand, terminal outcomes and exception rollback have new prepared checks. The existing per-operation death/trigger checkpoints are preserved. General nested effect choices and a replacement death-resolution scheduler remain unfinished.

This is infrastructure work: the card count remains 253. Nine new continuation checks use synthetic effect sequences to exercise the engine; those sequences do not change the real card definitions.

## Shared systems now written

- Player-selected Choose One branches, plus combined Fandral effects for the listed cards.
- A private pending-choice state for Tracking from the player's actual deck.
- Snapshot-based trigger queues for selected damage, spell, minion-play, hero-attack, and turn-start events.
- Explicit continuous attack/health auras and selected conditional attack rules.
- Silence, targeted transformation, returning minions to hand, and temporary attack expiry.
- Tradeable actions preserving enchantments and deck order; persistent and next-card cost reductions.
- Weapon destruction/replacement deathrattles.
- Six explicit Secrets, hidden opponent identities, ordered revelation, and attack cancellation.
- Target restrictions, additional direct effects, fixed-token summons, and conditional draws.

The implementation remains experimental. Added cards have explicit declarations, not a generic natural-language interpreter. Card-specific behavior and cross-system ordering require user-run tests and independent validation. Discover from the unrestricted Standard pool remains blocked: selecting only implemented cards would bias the game.

## Completion requirements still open

1. Finish the remaining Location effects, reopen/destruction interactions, and other battlefield entity types; the first four Locations and shared slots are written.
2. Generalize continuations beyond top-level card effects; finish generation pools, transformation/copy enchantment semantics, and interrupted-resolution timing.
3. Remaining trigger families, Secret interactions, resurrection history, attacks caused by effects, hero replacements, and persistent player effects.
4. Dormant, Discover with complete legal pools, quests, Rewind, Imbue, Herald, Shatter, Prepare, Kindred, Fabled, Colossal, and associated tokens and exceptional construction rules.
5. Every missing card's explicit effect implementation and generated-card dependency closure.
6. Live legality verification for the pinned catalog and independent reference checks.
7. A learning policy supporting the final action and observation schema. The old saved policy is specific to the original subset.

## Validation

The user's previous 43-check run passed for version 0.2. It does not validate these changes. Version 0.3 prepared 49 additional scenario checks, for 92 total, including private choices, secret leakage, countered spells, aura removal, lethal damage triggers, Tradeable enchantments, and weapon replacement.

Version 0.4 adds nine continuation checks, bringing the prepared total to **101**. The user ran all 101 successfully on September 22; the saved receipt matched version 0.4 before these edits. Version 0.5 adds eight checks, for **109 prepared checks**. These new changes remain unvalidated until the user runs the notebook again.

The stable 08_standard_simulator.ipynb workbench shows the coverage and runs the combined checks **only when the user runs it**. Its progress bar is driven by completed checks. It starts no training or match batch. Restart the kernel before using changed engine code.

Only static Python parsing, declaration/manifest consistency, archived card comparisons, and packaging checks were performed by the assistant. No engine imports, tests, matches, or notebook cells were executed.

## Rule references

- Pinned card descriptions and token records: data/standard/cards.json, all_cards.json.gz, and expanded/reviewed_cards.json.
- Standard random-generation format boundary: [Blizzard: A New Way to Play](https://hearthstone.blizzard.com/en-gb/news/19995505).
- All-class corpse tracking: [Blizzard 25.4 patch notes](https://hearthstone.blizzard.com/en-us/news/23913671).

No claim of complete Hearthstone timing conformance is made.
