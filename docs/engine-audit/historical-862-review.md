# Historical dependency integration: 862 bodies

This batch adds 199 explicit historical collectible implementations, moving the separate inventory from 663 to 862. Standard bindings remain 1,182 of 1,185. Counts describe written bindings; they do not certify full Hearthstone fidelity or full-format training readiness.

| Family | New historical roots |
| --- | ---: |
| Continuous stats, auras and cost rules | 65 |
| Conditional Battlecries and Combo | 50 |
| Fixed summons and their literal dependencies | 46 |
| Physical deck tutors | 22 |
| Destruction, weapons and mana crystals | 16 |

The integration uses the shared paid-play lifecycle, physical deck draws, resumable draw frames, legal target selection and live aura refresh. Conditional Dragon effects exclude the exact card being played from the holding condition. Harrison Jones captures the destroyed weapon's durability before drawing; weapon armor captures its attack before destruction. Fixed self-copy recipes preserve their printed distinction from literal token summons.

Focused checks cover every new conditional root in active/inactive states, every fixed-summon root, tutor/removal paid plays, physical draw selection, weapon stat capture, both players' crystal loss, damaged-minion destruction, and live draw/play/cost refresh. Full regression evidence is recorded in [candidate status](../../staging/rebased-88/STATUS.md) once a current fingerprint-bound receipt passes.

## Corrected Amber Warden audit

The earlier 2,718 count used a broad historical MINION request, incorrectly described as the actual Amber Warden request. Amber Warden already excluded Colossals in production. Blizzard's [34.4 patch notes](https://hearthstone.blizzard.com/en-us/blog/24245106/) confirm the Colossal exclusion; its [TITANS FAQ](https://hearthstone.blizzard.com/en-gb/expansions-adventures/titans) excludes Titans from random generation, Discover and random summons. This batch adds that Titan restriction to the shared request predicate and tests both exclusions.

The actual normalized frozen request has **3,201 eligible minion identities**, **665 with explicit registered rules**, and **2,536 without bindings** after this integration. The [membership audit](historical-minion-remaining-862.json) lists the remaining identities and source fingerprint. This is a count of runtime request membership, not independent certification of every historical eligibility rule. It does not include recursive spell/token/other-card dependencies.

## Remaining gates

Victor Nefarius (`CATA_470`), Storm the Gates (`TLCEVENT_400`) and Avatar (`CORE_WON_145`) remain unbound. Their production pool/distribution evidence remains incomplete; no guessed membership or probabilities were installed. Broader historical dependency closure, interaction fidelity and independent conformance validation also remain unfinished.

No training, self-play, policy updates, deck search or notebook cells were run. GitHub remains paused.

## Full regression receipt

All **5,196 non-training engine checks passed**, with zero failures, errors or skips and unchanged source fingerprint `eff468f3e72145f8bb484ee08932b601f8b04508e91a3be85e4eec9a1a567c87`. The immutable receipt is [validation-9692983a820847fc9421503c88c9fcfb.json](../../staging/rebased-88/runs/expanded_validation/validation-9692983a820847fc9421503c88c9fcfb.json). The separate project-tool suite passed all 69 checks. This validates the local fixtures, not full-format or independent client conformance.
