# Herald armies checkpoint

Scope: regular Standard, frozen patch 36.6.0.251952. Counts remain 877 live collectibles and 308 staged recipes. This change adds implementation bodies, not admissions or independent rules certification.

## Shared implementation

Thirteen Herald source cards have staged runtime declarations. One owner counter drives six army families, with eighteen Soldier/appendage ability identities sharing the same rules:

| Army | Shared ability |
| --- | --- |
| Warrior | Deathrattle damage to a random enemy, using the entity's saved magnitude |
| Demon Hunter | Temporary hero Attack when summoned |
| Shaman | Adjacent-minion Attack aura |
| Rogue | A random other-class spell with a scaled discount |
| Death Knight | An exact-Cost random minion that costs Health this turn |
| Warlock | Destroy the minion immediately to the right and gain stats |

The source cards compose the common action with their printed secondary effects. Shrine of Twilight is explicitly a location activation: placing it does not Herald or draw. Its last activation can use the freed location slot. Scorching Ravager grants Rush only to the Soldier it actually summoned. Fel Infusion grants turn-scoped hero Lifesteal; combat and visible features consume that state.

Rogue and Death Knight require full generation contracts before entry. Missing pools or unsupported outcomes are not filtered. For a supported Herald hero class, the candidate routes to that owner's army; unsupported off-class routing raises rather than guessing. Ultraxion and Deathwing remain explicit unimplemented exceptions. Cho'gall's enemy-deck replacement also raises until reviewed.

The Colossal copied-replacement path (`entity_tribute`) now preflights dependencies and creates fresh appendages and parent links. The body remains a transformation, not a summon. Ordinary transformation into a Soldier does not run its when-summoned ability.

## Timing and evidence gates

The candidate snapshots a Soldier's level before incrementing Herald progress. Levels double after two uses and again after four, capped at four times the base magnitude. Existing board entities retain their snapshot; copies retain the source snapshot; fresh entries use current owner progress. A full board still increments progress without producing a Soldier or its summon effect. These timing, copy/silence/bounce and full-board choices need independent target-patch traces before admission.

The [official announcement](https://hearthstone.blizzard.com/en-us/news/24245219) supports the six armies and two/four-use thresholds. It does not establish all runtime timing choices above. Base ability magnitudes come from numeric XML enum 2, preserved with the pinned source hash in `expanded/herald_values.json`. Card-text placeholders and ambiguous enum 4632 are not used as Herald action counts.

Remaining gates include exact generation membership and starting-deck restrictions; off-class army selection; event ordering with choices/deaths; Ultraxion discount scope; Deathwing replacement and Cataclysm choices; Cho'gall replacement; and all remaining Colossal body abilities and Magmaw's replenishment lifecycle.

## Verification and observations

Forty-two Herald checks exercise all six families, source lifecycles, board capacity, snapshot scaling, missing-pool rollback, copied replacements and internal casting. Twenty-one Colossal entry checks and twenty-six feature checks pass. Twenty-two queue checks pass.

Feature schema v44 exposes public Herald progress and active hero Lifesteal. The encoder retains the visible army multiplier while excluding internal Colossal parent/appendage entity identifiers, so arbitrary episode IDs do not become learning signals. No training or deck search ran.

Full-suite and smoke receipts are recorded in the candidate STATUS.md when complete. The queue grants thirteen staged runtime declarations but keeps every admission gate.

## Final validation

Full suite: **3,439/3,439 passed**, zero failures/errors/skips and unchanged source. Receipt: `staging/rebased-88/runs/expanded_validation/validation-5337663d3a4d4b59b9ded1a161980a28.json`. Fingerprint: `1d306285bd77c2803b4ed13deeb8c7b550c2dd461f68e917c059f0736f5afc22`.

Smoke: **22/22 terminal games**, zero errors/caps, 2,463 feature decisions with v44 and the same fingerprint. Receipt: `staging/rebased-88/runs/random_validation/summary-1d306285bd77-e8e79d9072494967b2e25aaff48e97e9.json`. These games exercise registered cards; staged Herald coverage comes from the focused fixtures.

Queue: 877 live, 308 staged, 222 staged runtime declarations and 86 missing declarations. Eighty-one cards have unresolved selectors/dependencies or explicit exceptional behavior, including the newly recorded Ultraxion/Deathwing exceptions. Twenty-two queue checks pass.
