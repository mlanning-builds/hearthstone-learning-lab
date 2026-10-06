# Generation machinery checkpoint — 60 staged cards

October 1, 2026. This is **unfinished work inside the 785 → 845 delivery**, not a completed 60-card batch. Collectible coverage remains **785 / 1185**, with **400 remaining**. No pending recipe is included in that count.

## Implemented shared code

- Complete-contract checks reject missing metadata, unimplemented outcomes, wrong selectors, duplicate canonical identities and absent class-specific pool contracts before sampling.
- Random generation samples with replacement; Discover presents up to three distinct identities and resumes the suspended effect after selection.
- Generated hand, deck, enemy-deck-top and board destinations reuse physical cards and existing summon/hand limits. Discounts, fixed Cost, stat changes, Freeze, Taunt and Combo Attack are explicit modifiers.
- Attached Deathrattles use the existing death/silence pipeline. Conditional generation handles holding a Dragon, another Mech, and maximum Mana.
- Discover continuations remain private. Unchosen options can be shuffled into the deck, recorded as one insertion event.
- Corrected a stale catalog-audit entry for TLC_987 (Questing Assistant). It remains unimplemented; the collectible count was already excluding it.

## What is still blocked

The recipes in `expanded/generation_cards.py` are deliberately **not imported into the collectible registry or lifecycle tables**. No production generation contracts are installed. Test contracts are synthetic and do not certify real Standard membership.

Before any recipe becomes playable: review its exact eligible pool for the pinned patch/class, finish every possible result (including recursive generators), wire its lifecycle hooks, verify Discover history/events and modifier timing, and add card-level integration fixtures. Metadata candidate matching is an aid to that review, not an eligibility decision. The 50 new checks cover the shared implementation and safety boundary; they do not certify 60 cards.

## Dependency inventory

[Machine-readable candidate report](engine-audit/generation-60-2026-10-01.json) lists every request by natural owning class, matching pinned catalog identities, and missing candidates. It excludes Mercenaries/Battlegrounds because it reads only the frozen Standard catalog. It does not claim current live legality.

These are **candidate dependency counts**, before eligibility exclusions or recursive closure:

| Generator | Missing candidate identities |
| --- | ---: |
| Sky Raider | 2 |
| Scorchreaver | 2 |
| Cold Snap | 4 |
| Relic of Kings | 4 |
| Glaciate | 5 |
| Netherwalker | 5 |
| Gnawing Greenfin | 5 |
| Spiteful Chef | 6 |
| Battle Vicar | 7 |
| Neferset Weaponsmith | 7 |
| Spearheart Sentry | 8 |
| Carrier Whelp | 8 |

A low count does not guarantee an easy unlock: for example, a missing outcome can itself generate cards from a much broader pool.

## All 60 staged declarations

| ID | Card | Status |
| --- | --- | --- |
| `CATA_136` | Azshara's Triumph | Staged; not playable |
| `CATA_471` | Talanji's Last Stand | Staged; not playable |
| `CATA_474` | Spearheart Sentry | Staged; not playable |
| `CATA_484` | Winterspring Whelp | Staged; not playable |
| `CATA_556` | Carrier Whelp | Staged; not playable |
| `CATA_569` | Ceremonial Clash | Staged; not playable |
| `CATA_723` | Drakeadon Mongrel | Staged; not playable |
| `CORE_AT_062` | Ball of Spiders | Staged; not playable |
| `CORE_AV_107` | Glaciate | Staged; not playable |
| `CORE_BAR_541` | Runed Orb | Staged; not playable |
| `CORE_BT_321` | Netherwalker | Staged; not playable |
| `CORE_CATA_009` | Death's Advance | Staged; not playable |
| `CORE_CFM_781` | Shaku, the Collector | Staged; not playable |
| `CORE_DRG_024` | Sky Raider | Staged; not playable |
| `CORE_EDR_001` | Babbling Bookcase | Staged; not playable |
| `CORE_ETC_111` | Merch Seller | Staged; not playable |
| `CORE_EX1_189` | Brightwing | Staged; not playable |
| `CORE_GIL_531` | Witch's Apprentice | Staged; not playable |
| `CORE_GIL_836` | Blazing Invocation | Staged; not playable |
| `CORE_GVG_114` | Sneed's Old Shredder | Staged; not playable |
| `CORE_KAR_057` | Ivory Knight | Staged; not playable |
| `CORE_KAR_062` | Netherspite Historian | Staged; not playable |
| `CORE_KAR_069` | Swashburglar | Staged; not playable |
| `CORE_KAR_077` | Silvermoon Portal | Staged; not playable |
| `CORE_LOE_039` | Gorillabot A-3 | Staged; not playable |
| `CORE_ONY_022` | Battle Vicar | Staged; not playable |
| `CORE_REV_308` | Maze Guide | Staged; not playable |
| `CORE_TID_931` | Jackpot! | Staged; not playable |
| `CORE_UNG_912` | Jeweled Macaw | Staged; not playable |
| `CORE_WON_096` | Dark Peddler | Staged; not playable |
| `CORE_WON_337` | Ironforge Portal | Staged; not playable |
| `CORE_WON_350` | I Know a Guy | Staged; not playable |
| `Core_UNG_072` | Stonehill Defender | Staged; not playable |
| `DINO_424` | Hero's Welcome | Staged; not playable |
| `DINO_426` | Ritual of Life | Staged; not playable |
| `DINO_431` | Atlasaurus | Staged; not playable |
| `DINO_433` | Guard Duty | Staged; not playable |
| `DINO_434` | Raptor-Nest Nurse | Staged; not playable |
| `EDR_060` | Ward of Earth | Staged; not playable |
| `EDR_270` | Horn of Plenty | Staged; not playable |
| `EDR_462` | Selenic Drake | Staged; not playable |
| `EDR_530` | Daydreaming Pixie | Staged; not playable |
| `EDR_848` | Photosynthesis | Staged; not playable |
| `EDR_999` | Gnawing Greenfin | Staged; not playable |
| `END_029` | Voodoo Totem | Staged; not playable |
| `FIR_913` | Inferno Herald | Staged; not playable |
| `FIR_952` | Scorchreaver | Staged; not playable |
| `JAIL_125` | Cold Snap | Staged; not playable |
| `JAIL_460` | Concealing Confection | Staged; not playable |
| `JAIL_507` | Spiteful Chef | Staged; not playable |
| `JAIL_706` | Thief's Tools | Staged; not playable |
| `JAIL_876` | Dig for Freedom | Staged; not playable |
| `MEND_042` | Lifebloom | Staged; not playable |
| `MEND_045` | Seeding Dragon | Staged; not playable |
| `TIME_613` | Cryofrozen Champion | Staged; not playable |
| `TLC_334` | Relic of Kings | Staged; not playable |
| `TLC_477` | Threshrider's Blessing | Staged; not playable |
| `TLC_514` | Merchant of Legend | Staged; not playable |
| `TLC_516` | Neferset Weaponsmith | Staged; not playable |
| `TLC_814` | Twilight Mender | Staged; not playable |

## Validation

**1,924 / 1,924 checks passed**, zero failures/errors/skips, including 50 new generation checks. Full-suite source fingerprint stayed unchanged: `55253110f866279ce09c3d6d06502d092ed7e3c91fe894588d5d79cc70453cb4`.

Full receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/expanded_validation/validation-a7645f3ae9964bcda3b7b5cb3d65fd7c.json`.

**22 existing-deck games completed**, zero errors/caps; 2,754 feature decisions checked with the same fingerprint. Random receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/random_validation/summary-55253110f866-95eb42e613e942c0af952abc12519607.json`. These games do not exercise the unregistered recipes.

No training or deck search was run. No Jupyter reload/run is needed for this checkpoint. The agreed completed batch target remains 845 playable collectible implementations.
