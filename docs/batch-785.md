# Sixty-card batch: 725 to 785

Scope: the pinned September 18, 2026 regular Standard catalog, patch 36.6.0.251952, all eleven classes. Candidate: `staging/rebased-88`. Mercenaries and Battlegrounds are excluded. Live legality is not asserted.

**60 additional collectible implementations written; 785 / 1185 total, 400 remaining.** Tokens do not count. The older root engine and notebook 08 remain preserved. No training or deck search ran.

## Shared mechanics delivered

| Group | New collectibles | Shared work |
| --- | ---: | --- |
| Prepare | 13 | Physical-card discount, mana payment, once-only preparation, turn lock; connected Battlecries, listeners, cost aura and Deathrattle |
| Draw activation and Follow the Evidence | 15 | On-draw casting/summoning, replacement draws, overdraw, enemy-deck Imp-formants, fixed shuffle payloads and explicit Shred casts |
| Forced combat | 12 | Source controller, before-attack checkpoint, normal attack preservation, summon/attack groups, lowest-health and bounded random targets |
| Either-side play | 5 | Recipient board positions, actor payment, recipient Battlecries, Overload and Deathrattles |
| Alternate payment | 4 | Health and Corpse payment, hero-healed condition, next-Murloc conversion and Agamaggan |
| Type groups | 4 | Distinct type assignment, dual types/ALL, actual deck draws and all-zone buffs |
| Effect replay | 3 | Historical Deathrattle replay and random friendly end-effect replay |
| Tribal damage | 3 | Pirate and Elemental additive damage; Beast damage multipliers |
| Held lock | 1 | Renferal's prior-play scaling and opponent-turn lock |
| **Total** | **60** | |

Follow the Evidence was included after the Imp-formant dependency became executable. Questing Assistant stays outside the count while Quest support is unfinished. No random generator was enabled by restricting it to the currently supported subset.

## Validation

**1874 checks passed**, with zero failures, errors or skips. This adds **144 checks** to the prior 1730-check baseline. The final suite ran in 140.2 seconds. **22 random legal-play games completed**, with zero errors or action caps and **2754 feature decisions checked**.

Both validations used unchanged fingerprint `bbb0e1059b9495aa04e91a16ee23abb17f250b1b1511fd9a384e2f14a13821b5`.

- [Full-suite receipt](../staging/rebased-88/runs/expanded_validation/validation-fbc88ab61fba491f89018993d7422d13.json)
- [Full-suite log](../staging/rebased-88/runs/expanded_validation/batch785-final.log)
- [Random-game receipt](../staging/rebased-88/runs/random_validation/summary-bbb0e1059b94-3a51c0271a1e4584ab19f6f640c85207.json)

The literal dependency audit checked all 785 roots and found no missing named IDs or paths; dynamic dependency coverage remains explicitly incomplete. Feature schema is **v18**: Prepare actions, alternate payment visibility and persistent Imp upgrade state change policy inputs. Earlier policy checkpoints are incompatible.

## Fidelity boundaries

These are implementations with local regression coverage, not independent certification of the Hearthstone client. `expanded/fidelity_gaps.json` records pending reference checks for Prepare/cost-conversion interactions, nested deaths, replay enchantments, type-selection weighting, empty-deck Esho, draw-listener timing and combined damage-modifier order. Do not infer readiness to find the best Standard deck from the implementation count.

The pinned card records specify the individual effects. Rule research included Blizzard's [Prepare announcement](https://hearthstone.blizzard.com/en-us/news/24276664/break-the-rules-in-escape-from-violet-hold-hearthstone-s-next-expansion), [Prepare notes](https://hearthstone.wiki.gg/wiki/Prepare), [forced attacks](https://hearthstone.wiki.gg/wiki/Force_attack), [Casts When Drawn](https://hearthstone.wiki.gg/wiki/Casts_When_Drawn), [Fatebreaker](https://hearthstone.wiki.gg/wiki/Fatebreaker), and [Agamaggan](https://hearthstone.wiki.gg/wiki/Agamaggan). Ambiguous interactions remain explicitly unverified.

## Added collectibles

| ID | Name |
| --- | --- |
| `CAP_004` | Disguised Operator |
| `CAP_104` | Blastpowder Engineer |
| `CAP_400` | Kabal Conspirator |
| `CAP_401` | Corrupt Constable |
| `CAP_402` | Follow the Evidence |
| `CAP_404` | Harsh Sentence |
| `CAP_406` | Kabal Mastermind |
| `CATA_180` | War'loc |
| `CATA_472` | Inspiring Maul |
| `CATA_EVENT_401` | Tunneling Geomancer |
| `CORE_ETC_523` | Death Metal Knight |
| `CORE_SW_439` | Vibrant Squirrel |
| `CORE_TTN_866` | Mythical Terror |
| `CORE_WON_141` | Menagerie Mug |
| `CS3_020` | Illidari Inquisitor |
| `DINO_428` | Behemoth Mask |
| `EDR_014` | Verdant Dreamsaber |
| `EDR_260` | Illusory Greenwing |
| `EDR_480` | Goldrinn |
| `EDR_489` | Agamaggan |
| `EDR_526` | Renferal, the Malignant |
| `JAIL_326` | Judgment |
| `JAIL_386` | Scramble for Gear |
| `JAIL_395` | Sewer Swimmer |
| `JAIL_435` | Rampaging Hound |
| `JAIL_442` | Disguised Doctor |
| `JAIL_444` | Sawbones |
| `JAIL_452` | Disguised Detective |
| `JAIL_453` | Jailbird |
| `JAIL_454` | Emergency Surgery |
| `JAIL_455` | Disguised Watchman |
| `JAIL_457` | Hijacked Securitybot |
| `JAIL_461` | Disguised Executioner |
| `JAIL_511` | Spire of Solitude |
| `JAIL_718` | Black Market Auctioneer |
| `JAIL_721` | Tras'tath, Soul Parasite |
| `JAIL_881` | Arcane Tripwire |
| `JAIL_890` | Captive Nathrezim |
| `JAIL_906` | Moragg |
| `JAIL_909` | Defias Wannabe |
| `JAIL_913` | Hold Them Off! |
| `JAIL_940` | Undeath Sentence |
| `JAIL_998` | Defias Smuggler |
| `RLK_720` | Gnome Muncher |
| `TIME_025` | Twilight Timehopper |
| `TIME_026` | Entropic Continuity |
| `TIME_027` | Tachyon Barrage |
| `TIME_028` | Fatebreaker |
| `TIME_029` | Ruinous Velocidrake |
| `TIME_434` | Temporal Traveler |
| `TIME_443` | Hounds of Fury |
| `TLC_106` | Endbringer Umbra |
| `TLC_107` | Stormbrewer |
| `TLC_110` | City Chief Esho |
| `TLC_222` | Flight of the Firehawk |
| `TLC_228` | Bralma Searstone |
| `TLC_230` | TREEEES!!! |
| `TLC_254` | Tortollan Storyteller |
| `TLC_436` | Reanimated Pterrordax |
| `TLC_518` | Interrogation |
