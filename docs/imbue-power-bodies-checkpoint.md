# Remaining Imbue power bodies — October 5, 2026

**868 live collectibles; 317 staged recipes. No collectible was promoted.** Candidate runtime paths now exist for all eight Imbue class powers. This checkpoint adds Paladin, Priest and paid Rogue activation to the previously implemented five. Complete generation contracts and client-conformance evidence remain admission gates.

## Implemented behavior

| Power | Candidate behavior |
| --- | --- |
| Paladin — Blessing of the Dragon | Pays once and shuffles two physical Emerald Portals. The generated token is hash-pinned to the frozen archive. |
| Emerald Portal | Requests a complete exact-cost Dragon pool using the resolving owner's current Imbue count. Automatic draw activation shares the existing burn, queued effect and replacement-draw pipeline; manual casting does not draw a replacement. |
| Priest — Blessing of the Moon | Validates complete Priest minion and spell contracts before randomness. Samples one affordable option from each nonempty group using mana remaining after power payment and the generated discount. Selection grants a Temporary card; this candidate Choose path does not count as Discover. |
| Rogue — Blessing of the Bronze | Generates a discounted other-class minion from a complete contract, then offers one Rewind for a paid activation. Reroll restores the pre-payment state while preserving advanced randomness and decision history. Keeping or rerolling commits one payment and one use. |

Priest reuses the effective-cost calculation rather than a base-cost-only cutoff; uncommon aura, hand-state and inherent discount interactions still need independent evidence. No minion-board-space or spell-target filter is currently applied to its affordability test. Empty groups omit their option; two empty groups finish without a choice. These edge cases remain provisional.

Rogue suspends before publishing the power-use counter/event, consistent with the existing card Rewind completion boundary. After-use listeners can themselves open choices and resume once. The exact client timing still needs independent confirmation. Morchie extra Rewinds remain unsupported. Wisprider's free Rogue activation **explicitly fails** until its Rewind/refresh behavior is resolved; it does not silently generate a card and omit Rewind.

## Verification

31 new focused tests passed. They cover payment, portal upgrade/recipient ownership, full hand and full board, chained replacement draws, manual casts, missing-pool rollback, Priest affordability and expiration, private choices, Rogue snapshots/randomness, refreshed budgets, full hand, one-shot payment modifiers, cloning, failed-reroll rollback and nested after-use choices. Fixtures install deliberately synthetic complete contracts for the scenario; they do not certify real Standard pool membership.

**3,117/3,117 full-suite tests passed**, with zero failures/errors/skips and unchanged fingerprint `7ad2c98dcfaeb154488adcef21f7925192afdd363cebdc0173a88694618c5f0c`. All **22 smoke games finished**, zero errors/caps and 2,508 feature decisions checked against the same fingerprint. Twelve additional queue checks passed. Full-suite and smoke receipts are recorded in the [current candidate status](../staging/rebased-88/STATUS.md). Feature schema remains v36: existing Imbue progress, primary-power state, private hand/choice identities and Rewind budget already represent these paths. No training or deck search ran.

## Remaining admission gates

- Complete production contracts and executable outcomes for Priest minions/spells, Rogue other-class minions and exact-cost Dragons; the existing Shaman, Aegis and Malorne pool gates also remain.
- Independent evidence for Priest sampling/eligibility and Choose attribution, portal automatic-cast event attribution and scaling, and Rogue Rewind/use-listener ordering.
- Free Rogue triggers, Morchie modifiers and the earlier consumer interaction gaps listed in `expanded/fidelity_gaps.json`.

Printed identities, costs and base values come from the build-251952 XML already stored in `expanded/imbue_values.json`, not today's rotation. Official [Priest](https://hearthstone.blizzard.com/en-us/cards/114069/) and [Rogue](https://hearthstone.blizzard.com/en-gb/cards/121243/) listings provide reference identities. Blizzard's [35.0 patch notes](https://hearthstone.blizzard.com/en-us/news/24267727/35-0-patch-notes) independently document a Rogue power Rewind interaction fix. Player reports about [portal ownership](https://us.forums.blizzard.com/en/hearthstone/t/emerald-portal-imbue-paladin-bug/146677) and [free Rogue triggers](https://us.forums.blizzard.com/en/hearthstone/t/niri-the-crater-and-rogue-imbue/157586) are supporting leads, not conformance certification.
