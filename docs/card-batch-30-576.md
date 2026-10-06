# Second 30-card batch: composed effects and private choices

The candidate now has **576 / 1,185 written collectible implementations**, up from 546; **609 remain**. Scope remains the frozen September 18 regular Standard catalog (36.6.0.251952), not live September 30 legality or Mercenaries/Battlegrounds. Generated tokens are not counted as new collectibles.

## Validation

- **1300 full-suite checks passed**, zero failures or errors.
- 47 batch scenarios cover the 30 cards, alternate choices, failed conditions, copy/Silence, temporary expiry, full hands, private observations, rollback, and suspended death choices.
- Source fingerprint: `f27d15c50bd7dfe26a97a7bdbdc8792099be2986641a835b362ca9f87568c0b9`.
- Receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/expanded_validation/validation-4bd62c51adf44d37888d6543af94743e.json`.
- Log: `staging/rebased-88/runs/expanded_validation/batch30-576.log`.
- Explicit literal dependency audit: no missing IDs. Dynamic pools and independent game conformance remain unfinished.
- No training or deck search was launched.

Passing internal fixtures does not certify full Hearthstone fidelity. The experimental engine still rejects unimplemented decks and cannot yet establish the best Standard deck or policy.

## Shared behavior

- Reused scheduled effects for repeated hero Attack, delayed self-damage, and delayed Mana Crystals. Scheduled spell effects retain source identity and evaluate spell damage when resolving.
- Added temporary minion keywords and temporary per-card cost discounts. Silence clears attached minion effects; copied minions retain independent copies; expiring grants do not remove permanent keywords.
- Added granted Deathrattles to the existing death-wave and copy machinery, including grants after Silence.
- Added private choices over cards already in hands/decks and choices among successfully drawn cards. Choices suspend/resume through the existing action interface. Opponent observations reveal only that a choice is pending.
- Reused attack/damage/play triggers, condition checks, fixed generation, and per-summon checkpoints.
- Added a public hero-Health-change counter; Armor-only damage does not satisfy it.

Feature schema is now **v11**. Old policy checkpoints are incompatible; do not silently load them against the new observations.

## Card inventory

| ID | Card |
| --- | --- |
| `END_006` | Chronikar |
| `EDR_482` | Rotten Apple |
| `EDR_483` | Fractured Power |
| `TIME_050` | Sentient Hourglass |
| `CATA_469` | Chromatic Broodmother |
| `TLC_243` | Whirling Stormdrake |
| `CATA_161` | Gruesome Nightmare |
| `EDR_812` | Grotesque Runeblade |
| `JAIL_329` | Truth Seeker |
| `JAIL_880` | Black Market Overseer |
| `TIME_215` | Thunderquake |
| `EDR_813` | Morbid Swarm |
| `END_009` | Splintered Reality |
| `JAIL_225` | Nab |
| `FIR_941` | Searing Reflection |
| `TIME_043` | PMM Infinitizer |
| `CATA_533` | Flash Flood |
| `TIME_039` | Deja Vu |
| `TIME_432` | Intertwined Fate |
| `TLC_521` | Eyes in the Sky |
| `TIME_770` | Fast Forward |
| `JAIL_206` | Dark Bribe |
| `TIME_032` | Chronogor |
| `EDR_950` | Sharp-Eyed Lookout |
| `TLC_245` | Ancient Raptor |
| `TLC_246` | Ancient Pterrordax |
| `CORE_UNG_952` | Spikeridged Steed |
| `DINO_429` | Sheep Mask |
| `TIME_701` | Waveshaping |
| `TIME_614` | Liferender |

## Rule evidence and boundaries

Printed rules and token/enchantment identities are taken from the local pinned `data/standard/all_cards.json.gz`; card fingerprints are recorded in `expanded/reviewed_cards.json`. In particular, `EDR_482e` specifies end-of-turn damage for Rotten Apple. The [card's timing notes](https://hearthstone.wiki.gg/wiki/Rotten_Apple) corroborate damage on the play turn and following own turn. [Waveshaping's official card entry](https://hearthstone.blizzard.com/en-gb/cards/120746-waveshaping/) supplies its Discover/bottom-deck rule.

Flight of the Firehawk was removed from this batch before registration because multi-type selection needs additional review; Gruesome Nightmare replaced it. There is no unsupported-card fallback or reduced global generation pool in these new choices: they operate on actual in-game hands/decks.

Independent pinned-client traces remain needed for modifier ordering, private-choice sampling with differently enchanted duplicate cards, and cross-system timing. These limits remain part of the broader fidelity work; this release reports written implementations and regression evidence, not complete Standard certification.

## Jupyter

The reusable code is under `staging/rebased-88/expanded`. To repeat validation locally, open `notebooks/13_shared_rules_checks.ipynb`, restart the kernel, and Run All. It starts checks, not training. Notebook 08 remains the older engine.

Continue in groups of 30 newly implemented collectibles; keep the full Standard goal and remaining shared-system work visible alongside card counts.
