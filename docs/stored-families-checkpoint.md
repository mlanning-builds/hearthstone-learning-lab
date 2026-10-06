# Stored-card and learned-spell checkpoint — October 5, 2026

All five remaining collectibles in the `stored_spells` and `stored_cards` queue groups now have staged runtime declarations: **Bashana Runetotem, Cultivating Sprite, Highborne Mentor, Irida Sinseeker and Timelooper Toki**. Overall: **252/308 staged runtime declarations; 56 still missing across 19 categories; 877 live registered collectibles**. No new card is admitted for training here.

## Shared behavior

Learned spells are attached to physical Treants and Pupils. The payload survives copies, returns to hand and shuffles, including Typhoon-style board shuffles, while changing the card into a different identity removes it. A paid token play exposes the learned spell's target where applicable. If that target disappears, the spell fails rather than choosing another target. Internal casting keeps its own spell context, costs no additional hand-play mana and does not inherit the minion's Lifesteal. The selected spell remains private while the token is in hand.

Highborne Mentor creates its Pupil and offers a historical, class-or-neutral spell costing at least seven. The choice suspends and resumes through the existing continuation system. Every eligible spell must have an explicit, complete pool contract and internal casting support. Incompatible Choose One targeting rejects pending review.

Bashana binds one Nature spell to each surviving Treant. The candidate allocation maximizes reachable mana up to twelve across available hand slots and selects feasible identities sequentially. This is a documented candidate distribution, not verified client RNG behavior. A full hand does not silently create a smaller approved pool. Random-pool membership and every reachable spell's behavior remain required.

Blooming Bulb keeps a physical upgrade level, casts three random spells at that level and retains its printed three-mana cost. The candidate upgrades once per owner turn start and caps at ten. Exact timing, cap and complete cast eligibility remain independent-review gates; this is not a claim that those details have been verified from the client.

Irida keeps one random physical deck card and stores the remaining cards in a finite player-owned Void payload. Two entries return each owner turn start, preserving identity, modifiers and starting-deck provenance; ordinary drawing and fatigue continue. Full-hand returns consume the removed entry without becoming a Godfrey overdraw. Multiple Battlecries currently create separate payload triggers; that interaction and ordering remain explicitly unverified.

Toki tracks three original physical generated spells. All three must be successfully played by their owner before one replacement Toki is added. Burned originals stay required; an unrelated copy, internal cast, opponent's play or transformed minion does not satisfy the task. Repeated notifications cannot pay the reward twice. Owner-visible progress and hand-card task associations contain no internal IDs; the opponent does not receive these private details.

## Evidence and validation limits

Printed effects, token identities, script values and targeting-arrow text come from the project's frozen JSON and patch-pinned XML. Additional rule notes were consulted for [Irida's finite Void and normal fatigue](https://hearthstone.wiki.gg/wiki/Irida_Sinseeker) and [Toki's full-hand and transformed-minion interactions](https://hearthstone.wiki.gg/wiki/Timelooper_Toki). [Blizzard's expansion overview](https://hearthstone.blizzard.com/en-us/news/24276664) establishes Irida's broad removed-deck mechanic but predates the later one-card retention change; the frozen record governs that change.

The full list of unresolved assumptions is in `expanded/fidelity_gaps.json`. Passing fixtures demonstrate candidate behavior, not independent client conformance. Schema v48 adds the new public and owner-only state. No training or deck search ran.

Current validation receipts are recorded in [candidate STATUS.md](../staging/rebased-88/STATUS.md).

## Next connected work

The [Fabled source inventory](engine-audit/fabled-source-inventory.json) identifies eleven frozen collectible roots using named XML tags and preserves 59 candidate prefix relatives. Prefixes are not certified dependency mappings. Nine roots are classified directly as Fabled; Gelbin and Sindragosa appear in other queue groups. Their deck-construction changes, complete companion bindings and runtime effects must be handled as one connected family. The current deck validator still accepts only implemented thirty-card decks.

Final validation: **3,655/3,655 full engine checks**, **25/25 queue checks**, **22/22 random legal games** without errors/caps, and **2,463 feature decisions**. Full-suite source remained unchanged at `e92ff15ebda3c82416503c26a73581760cbfa1bdef325d3daee061757d4ce2ec`. The receipt is `staging/rebased-88/runs/expanded_validation/validation-fc0afc7b46564c6cbdf21b9606e65cd8.json`. All 43 new focused scenarios are included in the full-suite count.
