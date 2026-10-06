# Shared choice and generation continuations — October 5, 2026

**33 additional cards now have staged runtime declarations.** Generation and Discover together have 116 of 136 remaining declarations connected (88/102 generation, 28/34 Discover). Twenty in those two families still lack runtime declarations. This is not collectible admission: coverage remains **868 registered / 317 staged** in the frozen Standard snapshot.

The new code is `staging/rebased-88/expanded/choice_generators.py`. It reuses complete pool contracts, resumable effects, physical card modifiers, Discover accounting and action rollback. None of its 33 cards is newly registered in the live tables.

| Shared behavior | Connected cards |
| --- | --- |
| Rune selection and conditional discovery | Hematurge, Necrotic Mortician, Frost Strike |
| Choose One branches and generation | Raven Idol, Spark of Life, Secret Ingredient, Symbiosis |
| Modified or multi-stage Discover results | Follow the Footsteps, Hook n' Heave, Wanted Poster, Q'onzu, Breakout Architect, Blood Clone, Noxious Bribe, Paleomancy |
| Mana, rarity and payment-history selectors | Emberscarred Whelp, Jade Guardians, Frantic Forger, Relic Miner, Scrappy Scavenger |
| Physical-card discounts, destination and locks | Illidari Studies, Staff of Trickery, Circadiamancer, Kaldorei Cultivator, Low Security Wing |
| Conditional or repeated generation | Scarlet Bruiser, Code Violet, Hexmarshal, Cosmic Manifestations, Solitude, Undefeated Champion, Unearthed Artifacts, Gravedawn Voidbulb |

Low Security Wing runs through location activation, not placement. Bottom-deck insertion affects the owning deck and does not report a shuffle. Code Violet snapshots its prior-spell condition so a suspended choice cannot make it count itself. Generated Prepare, spell-repeat and combined-choice flags belong to the physical card. Hand locks use lifetime play history, not a counter reset each turn. Ordinary generated Discover excludes its source's canonical identity after validating the complete contract.

## Validation and visibility

62 new focused checks, 110 existing generation checks and 14 completion-queue checks passed. **3,179/3,179 full regression checks passed**, zero failures/errors/skips. All **22 smoke games finished**, zero errors/caps and 2,508 feature decisions checked. Both runs used unchanged fingerprint `ae7dd2fbe6a7a99e05274a5975c0dcb0e4c9ec619e1f98f11e9a321ac83e1914`. Full regression and smoke receipts are recorded in the [current candidate status](../staging/rebased-88/STATUS.md).

Schema v37 adds the public recent-friendly-Undead-death condition and relative play count needed to unlock the viewer's hand cards. Existing physical-card observations expose the new modifiers. Opponents cannot see private offered cards, and suspended contexts never appear in observations. Old feature-schema models must not be reused as v37 models.

## Still gated

Complete generation membership and recursively executable outcomes remain required. Controlled fixture pools are not production eligibility lists. The completion queue still accounts for all 317 cards and now marks 75 cards with unresolved selector/dependency mappings. Rune selectors are explicit; there is no runtime card-text parser.

Independent conformance remains necessary for full-hand/full-board Corpse spending, Q'onzu Discover callbacks, transfer/copy/Prepare lock interactions, repeat stacking, combined-choice targeting, Follow attribution, Forger playability, destroyed token rarity, bottom ordering and temporary mana-cap behavior. Code Violet currently follows the engine's player-played spell history; internal/repeated-cast attribution remains a known admission blocker. Details are recorded under `staged_choice_generation_continuations` in `expanded/fidelity_gaps.json`.

No training or deck search ran. No Jupyter reload is needed to continue development.
