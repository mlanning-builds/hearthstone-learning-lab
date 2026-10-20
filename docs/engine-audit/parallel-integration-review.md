# Parallel simulator integration review

This batch connects 223 additional Standard recipes to the real candidate registry, moving the written count from 959 to 1,182 of the frozen 1,185 cards. It adds ten historical Colossal roots and Webspinner, bringing the separate historical-body inventory from 477 to 488. Binding counts measure written implementations; they do not establish a complete executable simulator.

The three unbound Standard cards are Victor Nefarius (`CATA_470`), Storm the Gates (`TLC_EVENT_400`), and Avatar of Hearthstone (`CORE_WON_145`). The first two need exact curated construction components and inherited behavior, including multiple Battlecry targets, passive effects and auras. Avatar needs the in-game Standard pack distribution and complete automatic-play semantics. The existing guarded interfaces do not substitute guessed outcomes.

## Implemented families and shared corrections

The generation track connects explicit generation, Discover, Dark Gift, Rewind, historical and conditional recipes, and Tripwire's Cast When Drawn hook. The Eternal Hold now places a Location and executes Discover when activated. Full metadata membership is checked independently of implemented behavior. Unsupported outcomes reject rather than disappearing from pools.

The complex track connects transformations, automatic casting, future summons, learned spells, physical stored obligations, Tiny Pal, and finite Kazakus/Elise construction choices. Automatic deck consumption now takes the same top card as drawing. Divergence preserves complementary odd Cost/Attack halves and minimum-one Health. Internal execution validates all Choose One branches before consuming state or RNG. Learned minions and crafted Locations reject missing physical payloads. Elise copied stats enter before summon reactions.

The historical track completes all thirteen frozen Colossal roots and their literal appendages. Its production membership and metadata hashes are independently derived; limb positions use frozen XML tags. Neptulon attacks through its Hands with attack-window immunity. Nellie's Ship stores private physical crew and exposes it only to the owner. Gigafin and its Maw use linked disposal/return state.

The remaining Standard Herald, Colossal and Imbue recipes are bound with their exact children. Herald Soldiers receive Rush before entry reactions. Single-class off-class Herald routing and distinct Deathwing Cataclysms are explicit. Shared-system recipes also connect Leylines, Maps, Fabled companions, Osk forms, counterfeit Coins, construction choices and turn deadlines.

Generated minion stat overrides, Taunt/Freeze and other entry keywords now precede entry notifications, including each repeated summon. The counterfeit potion now includes its exact vanilla 5/5 Kabal Demon dependency; two existing Choose One effects gained their verified internal opcode/target admission. Bwonsamdi receives all chosen Boons before arrival; Osk's six-cost summon receives Taunt and Lifesteal before arrival. Free Wisprider active powers repeat under Deios while preserving paid-use accounting. Paid Wisprider Battlecries and Imbue increments repeat independently.

## Outcome closure and limits

The [membership receipt](generation-closure-1182.json) records actual runtime pool-resolution checks across all eleven classes: 93 reviewed generation roots have complete declared membership and written outcomes; 41 remain blocked or gated. This is **membership and written-outcome closure**, not certification of complete play, internal casts, nested dependencies or interactions.

The full canonical past universe contains 4,921 collectible identities. `TIME_052` can request 3,226 historical minions, of which **2,878 remain unwritten**. Historical bodies are thus a major completion requirement even after almost every Standard source recipe is connected. The simulator cannot truthfully be called full Standard or training-ready.

Additional production guards remain for Bashana spell-budget allocation, Watfin mutations, generated Underbelly contraband, ambiguous Herald routing, stacked spell repetition and Vyranoth remainder allocation. These are not represented by the three-card unbound count. There are 157 overlapping known fidelity entries, not 157 independent missing cards. The candidate's readiness check remains false.

## Validation

Focused production and shared-rule checks passed for the affected families. The first consolidated run executed 5,064 cases with unchanged source and reported 34 failures and 40 errors. Most were stale expectations that newly connected production pools would remain unavailable, or raw custom tokens without required physical state. Review also found the missing Kabal Demon dependency and two internal admission hooks. A second unchanged-source run passed 5,063 cases; its remaining Shrine fixture relied on an unavailable four-cost pool that was now complete. The repaired Shrine/internal suite passes all 34 cases. The final consolidated run passes all **5,064 non-training cases**, with zero failures, errors, skips or unexpected successes and unchanged source. Its fingerprint is `692fa31c059461557afa36ec00abe4ae1e048ff87a620e41aed8a5256a1f8e26`; completion time is `2026-10-07T20:55:28.539823+00:00`. Passing includes explicit rejection/rollback scenarios and is not full simulator certification. Immutable records of the failed runs are preserved; neither failed run is represented as passing. Root tooling: 41 checks passed. No training, learning, deck search or notebook cells were executed. GitHub remains paused. Existing models and experiment records remain preserved.

Current validated counts: 1,182 Standard bindings, 488 historical collectible bodies, 3 unbound Standard sources, and 157 known overlapping fidelity entries. The readiness gate still reports `full_standard_ready=False`. See the [public validation record](public-rule-validation-2026-10-06.json).
