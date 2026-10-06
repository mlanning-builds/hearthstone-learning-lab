# Untouchable board objects and Underfel Rift

This is internal progress toward the unfinished **785 → 845** delivery. Escape the Underfel is connected with its Rift and all three Fel Beast outcomes. Written coverage is **797/1185**, with **388 remaining**. Batch progress is **12/60**, leaving **48 additional collectibles**. Generated tokens and shared infrastructure do not increase that count.

## Implemented behavior

`Permanent` is an explicit board entity. It occupies a slot and interrupts adjacency, but does not enter ordinary minion or location lists. It cannot be attacked, targeted, damaged, buffed or removed by ordinary minion/location board wipes. It does not generate a Corpse or publish a minion-summon event. Existing minion-only aura, turn and death handlers ignore it. Creating it through the ordinary minion constructor is rejected.

Underfel Rift's spell costs the pinned five mana and opens one ready object when there is board space. Each Rift has its own once-per-owner-turn use limit. The policy action combines selecting the Rift and choosing a hand card into one `activate` decision; the client UI's reversible selection toggle is not a separate strategic action. The chosen card is removed for zero mana, without playing, drawing, discarding or destroying it. This therefore does not advance Temporary-play Quests or trigger discard effects. The removed identity is not exposed in public activation logs.

The closed Fel Beast pool contains Felscreamer, Felraptor and Felhorn with their reviewed stats and keywords. Dependencies are validated before spending the hand card or consuming RNG. Two independent summons use the existing resumable effect frame: the first summon and its triggered effects/choices finish before the second summon begins. Whole-action failure restores card, use limit, RNG, board and continuations.

Escape the Underfel reserves an opening slot using the shared Quest framework, counts six played Temporary cards and awards the Rift spell. Normal cards, prior plays, expired Temporary cards and cards thrown into the Rift do not count. Candidate play-event semantics count a countered Temporary spell.

Public board observations describe the object as `PERMANENT` with readiness; schema v23 allows policies to distinguish activation choices and board occupancy without treating the Rift as a combat unit. No training was run.

## Sources and limits

The pinned raw records establish the reward family. Blizzard's [34.0.2 patch notes](https://hearthstone.blizzard.com/en-us/news/24247520/34-0-2-patch-notes) establish the six-play requirement and five-mana reward. In the [reveal discussion](https://www.reddit.com/r/hearthstone/comments/1l9eato/new_warlock_quest_escape_the_underfel/), developer ClayByte explains activation by selecting a hand card and confirms that removal is neither discard nor destruction.

Independent client evidence is still needed for full-board activation legality, placement/adjacency, duplicate Rifts/outcomes, removed-card visibility and precise reward timing. Current candidate behavior permits activation even with no free slot, consumes the card, and summons only what fits; it is an explicitly recorded assumption, not a certified client rule. These gaps remain in `expanded/fidelity_gaps.json`.

Focused validation: **32 checks passed** covering the Quest, capped boards, fixed-pool closure, per-object limits, forbidden targets, mass effects, adjacency, event ordering, choices, rollback and feature privacy. Full-suite and random-game receipts are recorded in candidate STATUS when complete.

## Next dependency work inspected

Master Dusk's reward can reuse the replacement Hero Power framework, but its two filtered draws must resolve on-draw chains and choices sequentially. The current replacement-power dispatcher executes effects synchronously and needs an explicit continuation before connecting that reward. Ninja return effects are player-bound rather than ordinary removable enchantments; independent traces remain needed for death timing and existing Ninjas. The shared shuffle history already distinguishes trades from actual shuffles.

Commander Geddon remains unconnected: reports conflict on empty-deck/fatigue behavior, so do not infer immunity from its replacement-draw wording. No unsupported card was added merely from a plausible default.

Validation completed: **2113/2113 passed**, zero failures/errors/skips; receipt `validation-eb20b7d7477f46c4b6a70452ef6637da.json`. Random validation: **22 terminal games**, zero errors/caps, at the same fingerprint `c681ed66b4da870f00c9edfb05498fd65a9aa5c486ab2240a7965a58a722a1fb`. The general returned-token fixture now excludes explicitly registered untouchable permanents; dedicated permanent fixtures verify that ordinary minion creation is rejected.
