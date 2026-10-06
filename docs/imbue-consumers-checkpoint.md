# All Imbue consumers — October 5, 2026

**868 live registrations; 317 staged recipes. No new live registrations.** All nineteen remaining Imbue card declarations now have staged runtime code in `expanded/imbue_consumers.py`. This is completion of their candidate consumer layer, not full Imbue support: three class powers, complete outcome pools and conformance gates remain open.

| Shared behavior | Cards |
| --- | --- |
| Draw, heal, damage, add a Wisp, then Imbue | Exotic Houndmaster, Aspect's Embrace, Spirit Gatherer, Eventuality, Finality |
| Battlecry / Deathrattle Imbue | Umbraclaw, Lunarwing Messenger, Goldpetal Drake, Flutterwing Guardian, Bitterbloom Knight, Jagged Edge of Time |
| Complete-pool summon followed by Imbue | Aegis of Light |
| Physical hand-minion discount choice | Living Garden |
| Free triggering after Imbue | Wisprider |
| Two-Imbue threshold effects | Resplendent Dreamweaver, Petal Picker |
| Start-game qualification and persistent spell counter | Hamuul Runetotem |
| Explicit Wild God Discover and four-Imbue discount | Malorne the Waywatcher |
| Enemy Attack reduction until caster's next turn | Kaldorei Priestess |

The existing Druid, Hunter, Mage and Shaman power bodies are reused. Death Knight's passive now tracks the first Undead played each turn and grants the pinned scaling Attack bonus; summons do not consume that play slot. State and hook code are connected, but consumers remain outside the live card registry.

## Shared state and model visibility

Hamuul checks the saved starting deck once, records qualification and counts player `spell_cast` events across turns. Every third event queues an Imbue. Spells cast by other cards currently do not publish that player event; this follows the existing casting boundary and remains a conformance-review item.

Temporary Attack changes retain negative Attack bookkeeping, stack independently, expire at the applying player's next turn, clear on Silence and copy with the minion. Observations identify the expiration turn relative to the viewer. Schema v36 exposes Hamuul progress and whether an Undead has already been played this turn.

Malorne uses an explicit eleven-identity Wild God candidate set, never a text parser or all-Legendary fallback. A separately installed complete outcome contract is still required; no default production contract is approved by this change.

## Validation

46 focused consumer checks and 12 queue checks passed. They cover all nineteen declarations, thresholds, missing-pool/power rollback, nested choices, Lifesteal, free triggers, counters across turns, stacked/copied/silenced debuffs, Death Knight's first-play behavior, internal spell execution and observation privacy. Consolidated regression: **3,086/3,086 tests passed**, zero failures/errors/skips. All **22 smoke games finished**, zero errors/caps, with 2,508 feature decisions checked. Both runs used unchanged fingerprint `7d37c47413f0f3e1fd26777c09ff9af26351bbac345569034d770e684065c4ff`. Receipts are recorded in the [candidate status](../staging/rebased-88/STATUS.md).

## Remaining Imbue work at this checkpoint

The subsequent [power-body checkpoint](imbue-power-bodies-checkpoint.md) connects the three candidate bodies below; complete pools and independent conformance gates remain.

- Paladin: Emerald Portal insertion, dynamic scaling and Casts When Drawn.
- Priest: playable-card eligibility, choice and Temporary discount behavior.
- Rogue: generated minion discount and Rewind of Hero Power activation.
- Complete production pools for random outcomes, including Shaman, Aegis and Wild Gods.
- Independent evidence for startup and trigger ordering, Hamuul cast attribution, Wisprider targeting/use counters across classes, power replacement/refresh, Death Knight timing and dormant plays, and enchantment interactions.

Wisprider fails explicitly for unimplemented powers and unsupported base-power triggers; it does not silently skip their effects. Staged tests with controlled pools do not establish complete card support. Known limitations are tracked in `expanded/fidelity_gaps.json`.

Printed effects come from the frozen catalog, and power values from build 251952 XML stored in `expanded/imbue_values.json`. The [official Wisprider listing](https://hearthstone.blizzard.com/en-gb/cards/114292-wisprider/) confirms its trigger text. [Wild God discussion](https://us.forums.blizzard.com/en/hearthstone/t/what-is-a-wild-gods/144163) supplies supporting context, not an approved pool or timing oracle. No training or deck search ran.
