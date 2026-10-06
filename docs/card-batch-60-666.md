# 60-card batch: held progress, combat events, and death payloads

Candidate coverage: **606 → 666 / 1,185 written collectible implementations**; **519 remain**. This is the pinned regular Standard snapshot, 36.6.0.251952, across all 11 classes. Mercenaries and Battlegrounds are excluded. Generated dependencies do not count toward the 60.

## Validation

- **1423 full-suite checks passed**, zero failures or errors.
- **77 new focused scenarios**, including every added collectible, negative conditions, generated cards, private choices, rollback, Silence, turn expiry, full-hand draw continuation, exact physical-card selection and overkill/shield interactions.
- Source fingerprint: `9a28ca6b4823eb9084f718db705a1a20197e056295b36518d889d17fd64256ec`.
- Receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/expanded_validation/validation-0c5c3e0144f9437989050337de30c288.json`.
- Detailed log: `staging/rebased-88/runs/expanded_validation/batch60-666.log`.
- Explicit literal dependency scan: no missing IDs. Dynamic generation pools remain separately incomplete.
- No training or deck search was launched.

## Shared systems added

Hand cards track spells cast, minions played, turns held and qualifying paid costs on their physical instances. The same hooks support Dragon transformations, the Moon spell upgrades, Molten Gold/Frostshatter/Stormfury, Reforestation and Lotus Troublemaker. Mirror cards retain their copying behavior across successive transformations. Shadow of Demise cannot be played in its base form and copies supported spell modifiers and parameterized payloads.

Combat events retain the attacked minion's identity and lethal result, plus the attacker's neighbors and pre-attack Stealth. These support attack-kill rewards, adjacency rewards, Stealth payoffs and cleave. Death waves publish notifications used by Acolyte of Death, Scavenging Flytrap and Hollow Direhorn. Missiles no longer select already lethally wounded minions while a checkpoint is pending.

Deathrattles can carry generated-spell payloads, exact drawn-card references and a privately selected enemy hand-card reference. Those private IDs stay out of opponent observations. Additional support covers permanent Dragon Rush, first-Dragon and next-Murloc modifiers, delayed destruction following a minion from hand to board, full-health enchanted Reborn, excess damage and healing, and resumable multi-card draws.

Feature schema is **v13**. Earlier policy checkpoints are incompatible. The original engine and Notebook 08 remain separate.

## Added cards

| ID | Card |
| --- | --- |
| `CATA_551` | Stonetalon Striker |
| `CATA_552` | Ebonscale Scout |
| `CATA_553` | Ebyssian |
| `TIME_213` | Primordial Overseer |
| `TIME_702` | Ebb and Flow |
| `EDR_460` | Wish of the New Moon |
| `FIR_918` | Light of the New Moon |
| `JAIL_801` | Molten Gold |
| `JAIL_803` | Frostshatter |
| `JAIL_805` | Stormfury |
| `EDR_843` | Reforestation |
| `FIR_902` | Sigil of Cinder |
| `CATA_130` | Crystalspine Cub |
| `JAIL_470` | Lotus Troublemaker |
| `CATA_210` | Twilight Egg |
| `TLC_827` | Grazing Stegodon |
| `CORE_RLK_567` | Shadow of Demise |
| `DINO_407` | Mirrex, the Crystalline |
| `TIME_876` | Shapeshifter |
| `CAP_000` | SI:7 Slayer |
| `CAP_005` | Mathias Shaw |
| `CAP_006` | Tricks of the Trade |
| `CAP_001` | Silent Strike |
| `CORE_CATA_004` | Rehgar Earthfury |
| `CORE_SCH_605` | Lake Thresher |
| `DINO_401` | The Great Dracorex |
| `EDR_421` | Omen |
| `FIR_953` | Magma Hound |
| `JAIL_030` | Escape Artist |
| `CATA_487` | Raincaller |
| `TLC_811` | Archaios |
| `TLC_247` | Primal Sabretooth |
| `CORE_CFM_344` | Finja, the Flying Star |
| `EDR_842` | Defiled Spear |
| `CORE_RLK_121` | Acolyte of Death |
| `EDR_484` | Scavenging Flytrap |
| `DINO_416` | Hollow Direhorn |
| `TLC_603` | Platysaur |
| `TLC_252` | Dissolving Ooze |
| `CATA_464` | Blackwing Experiment |
| `JAIL_303` | Ancient Augur |
| `TIME_714` | Chrono-Lord Epoch |
| `TIME_103` | Chromie |
| `CATA_554` | Earthen Roar |
| `CATA_570` | Morchok |
| `TLC_428` | Hot Spring Glider |
| `TLC_257` | Loh, the Living Legend |
| `EDR_844` | Naralex, Herald of the Flights |
| `FIR_928` | Keeper of Flame |
| `CATA_610` | Lo'Gosh's Last Stand |
| `EDR_261` | Amphibian's Spirit |
| `TLC_831` | Pterrordax Egg |
| `CAP_800` | Sinful Steed |
| `CAP_803` | Lingering Spirit |
| `EDR_232` | Typhoon |
| `CATA_978` | Sindragosa's Triumph |
| `CATA_585` | Torch |
| `JAIL_445` | Bone Flurry |
| `MEND_302` | Wasteland Vanguard |
| `TIME_212` | Lightning Rod |

## Evidence and remaining limits

The pinned local card archive supplies printed rules, types, generated identities and stats; every added record is hashed in `expanded/reviewed_cards.json`. Blizzard's [28.2 patch notes](https://hearthstone.blizzard.com/en-us/news/24008697/28-2-patch-notes) specify Shadow of Demise's exact-copy correction. Its [rules page](https://hearthstone.wiki.gg/wiki/Shadow_of_Demise) identifies the unplayable base form; the project uses the pinned Standard Core ID. The [Chromie rules page](https://hearthstone.wiki.gg/wiki/Chromie) describes drawing matching cards from the deck. These references supplement local fixtures; they do not independently validate the complete simulator.

Stormbrewer was excluded from this release because killing a combatant before combat needs a fuller interruption/continuation contract. Felwood Treant and Broodwatcher also remain unimplemented pending precise mana-spending timing. Other cards with unresolved behavior were not counted to reach 60.

All 666 entries remain **written implementations**, not full client-conformance certification. General modifier precedence, cross-zone/control-change enchantments, complete generated pools and event/death ordering remain open. In particular, deathrattles and Reborn between event-triggered missiles still use the existing outer-checkpoint model. The new related uncertainties are recorded in `expanded/fidelity_gaps.json`. Full Standard readiness remains false.

## Jupyter

Use `notebooks/13_shared_rules_checks.ipynb`. Restart the kernel and Run All to reproduce the checks. No notebook source change is required for this release; it already starts the candidate checks in a fresh process and displays progress. It does not start training.
