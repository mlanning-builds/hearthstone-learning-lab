# Current candidate status

Candidate: `staging/rebased-88`; validation notebook: `notebooks/13_shared_rules_checks.ipynb`.

## Objective and coverage

- Complete all **1,185** frozen regular Standard collectibles and the full simulator/learning objective. Overall scope remains all cards; integration checkpoints now use user-requested batches of 60. All 11 classes; exclude Mercenaries and Battlegrounds.
- Written collectible definitions: **817 / 1185** live definitions; **368 remain staged**. Eight recent definitions remain explicitly provisional (Cloudstrider, Treasuregill, Tyrande, Niri, Ursol, Explosive Runes, Mystic Misdirection, Untimely Death). Written counts do not certify full behavior. Patch **36.6.0.251952**, the frozen catalog rather than today's live rotation.
- Internal casting admission: **368 definitions / 270 already implemented collectible spells**. All currently defined playable spell bodies have paths; untransformed Shadow of Demise remains intentionally rejected. This is not full catalog coverage, independent client conformance, or permission to filter a random pool.

- Feature schema: **v30**. Older policy schemas are incompatible.

## Definition-first workstream

User priority: write all remaining definitions before resolving broader execution gaps. `expanded/pending_definitions.py` contains explicit ordered effect recipes with separate spell, Battlecry, Deathrattle, trigger and setup hooks. It is deliberately not imported into playable card registration. Metadata keywords/stats remain sourced from the frozen catalog. Dynamic Herald numbers, token dependencies, full pools, Rewind snapshots and other unresolved runtime behavior remain integration requirements.

**817 live definitions + 368 staged top-level recipes cover all 1,185 collectible identities. Zero identities lack a top-level recipe.** This does not mean complete executable definitions: symbolic operations, generated token identities, custom option contents, exact dynamic values, event timing and complete generation pools remain unresolved in staged recipes. All 368 remaining recipes are marked `executable=False` and excluded from live registration. The initial 60 generation recipes were preserved; subsequent passes added 103, 99 and 109 new recipes respectively.

The current audit verifies all 371 belong to the frozen catalog, none overlap live card registration, each has a nonempty hook definition, and attempts to integrate through the staged boundary fail explicitly. It records source hashes in `../../docs/engine-audit/pending-definitions.json`. This is structural validation, not behavioral verification. Next: resolve the shared operation/dependency contracts and promote complete families into the engine with focused behavior tests.

The full-suite receipt below predates this newly added standalone module; no newer full-suite result is claimed.

## Active 60-card integration batch

The fixed membership and baseline are in `../../docs/engine-audit/active-integration-batch.json`: 60 generation cards selected from the remaining staged set, baseline 817 live definitions. This batch stays open until its members meet live registration, complete dependency/pool support and behavioral/regression validation. Shared prerequisites do not count as completed cards.

Current work: generated summon groups now bind each successful physical summon and perform forced attacks after the summon group, through existing event checkpoints. No replacement attacker is chosen when the bound minion is gone; control changes use the attacker's current owner. Ankylodon's Deathrattle has an engine-operation body in `generation_extensions.py` but remains outside playable registration pending complete pools. **114 related tests passed**, including seven new generated-attack cases. No batch cards have yet been promoted. The full 60-card batch is not complete; the goal stays active.

### Current batch continuation

Nine additional batch cards now have executable operation bodies: Commissary Crook, Astromancer, Ulfar, Corpse Farm, Story of Umbra, Ysondre, Bygone Echoes, Triennium Rex and Eternal Toil. This brings the fixed batch to **50/60 engine bodies written**, including previously existing bodies. This is not enabled-card progress: **0/60 batch promotions** so far; live coverage remains 817.

Shared operations resolve dynamic cost pools, validate pools before consuming the requested resource, bind generated Deathrattles to the actual live entity, and distinguish a killed target from a returned/removed one. **131 related tests passed**, including 17 new dynamic-generation cases. Dynamic pool selectors still need complete production contracts; all new bodies remain outside live registration. No full-suite result is claimed.

## Earlier checkpoint: death-triggered Secret

Untimely Death is now registered provisionally. Death capture queues the exact Secret identity and a dead-minion snapshot; the resummon runs through the shared event/death scheduler without consuming the same Secret twice across simultaneous deaths. The normal play marker distinguishes played minions from generated summons. Clean resummons and Reborn are separate events.

**80 related checks passed**, including seven new focused cases and an actual play/end-turn/death sequence. Live definitions: **817**; staged recipes: **368**. The prior full-suite receipt does not cover this revision. Ordering and transformed/controller-changed minions remain documented conformance gaps. Flames of Infinity remains staged; infinite damage must preserve damage rules, including Fire immunity, rather than becoming unconditional destruction.

## Earlier Secret integration

Explosive Runes and Mystic Misdirection are registered with reviewed pinned metadata and the Sheep dependency. Minion after-play Secret handling now passes the played source identity. Runes damages that surviving source and spills excess to the opponent; Misdirection replaces the minion attacker and cancels its attack. Both retain explicit fidelity gaps and provisional status.

**138 related checks passed**, including eight new Secret behavior checks. No new full-suite or random-game receipt is claimed. **Live definitions: 816; staged: 369.** The earlier generation checkpoint below is historical. Next continue implementing missing runtime mechanics and pool outcomes; the entire Standard/ML objective remains open.

## Generation integration checkpoint (earlier)

`expanded/generation_extensions.py` now contains engine-operation bodies for Karov the Broken, Guard Dog, Soothsayer, Bloodpetal Biome, Tunnel Terror and Dethrone. Generation now supports marking individual results Temporary before hand entry, and a Combo branch uses the normal operation scheduler. **68 generation tests passed**, including nine extension checks against explicitly synthetic pools. These tests verify the bodies, not real pool membership or complete playable cards. No keyword-entry timing change was made; investigation did not establish a bug.

**Newly enabled cards: 0. Live coverage remains 814.** The audit of the original 60 generators shows each has at least one missing outcome definition (including recursive dependencies); exact blockers are saved in `../../docs/engine-audit/generation-integration-blockers.json`. None were silently removed from eligible outcomes. Remaining work includes complete pool membership, outcome implementation and registration. The full-suite receipt below predates these runtime changes.

## Current change and evidence

Imbue progress and all eight power identities are connected. Druid, Hunter and Mage have candidate active bodies using the exact build 251952 numeric metadata saved in `expanded/imbue_values.json`. Shaman now uses shared targeted replacement-power actions and transforms through the reviewed generation-pool interface; its full production pools remain unavailable. The other four power bodies and all 19 associated collectible consumers remain unfinished. No new collectible coverage is credited. Death Knight timing, first replacement refresh, token cost/art mapping, empty-hand activation and triggered power sequences remain open.

**2598 tests passed**, zero failures/errors; **22 random games completed**, zero errors/caps. Matching fingerprint `5d2c697ad0142140b81fa4573c307b7cae2796c98f0235d0aeec90f7f9843bdf`. There are 24 focused Imbue checks. Random games exercise currently registered cards, so they do not establish Imbue consumer correctness or full Standard fidelity.

Receipts:
- `runs/expanded_validation/validation-a9d3c04a459745439bf648f6560534cb.json`
- `runs/random_validation/summary-5d2c697ad014-79ed093bec084efdb35e52114a8b2a79.json`
- `runs/expanded_validation/imbue-powers-full.log`

The planning inventory `../../docs/engine-audit/imbue-pool-planning.json` lists missing generation dependencies from the frozen catalog. These are metadata candidates, not approved runtime pools: Paladin Dragons have 32 missing definitions, Priest minions/spells 24, and Rogue other-class minions 140. Shaman's per-cost pools are listed individually. Production pools and independent runtime evidence remain required.

The target remains all 1,185 frozen Standard cards with no batch-size cap. Next work is the remaining Imbue powers, their complete pools and all associated consumers, then the remaining shared mechanic families. No training or deck search has run.

## Still unfinished

Missing collectibles and generated dependencies, remaining casting conditions and consumer exceptions, full random pools, independently verified event/choice/target attribution and death timing, live legality verification, and full learning/deck-search/reproducibility gates remain open. Passing fixtures is not full Standard certification. Sixty staged generation declarations remain outside playable coverage.

No training or deck search has run. Long runs require an explicit budget. The full goal remains active.

See [mechanic roadmap](../../docs/MECHANIC_ROADMAP.md), [full roadmap](../../docs/ROADMAP.md), [casting checkpoint history](../../docs/internal-casting-checkpoint.md), [casting inventory](../../docs/engine-audit/internal-casting-current.json), and [archived status history](../../docs/status-history-before-outcast.md). Machine-readable fidelity gaps: `expanded/fidelity_gaps.json`.


# Before stored-card batch (October 2, 2026)

# Current candidate status

Candidate: `staging/rebased-88`. Checks notebook: `notebooks/13_shared_rules_checks.ipynb`.

## Scope and actual coverage

- Target: all 1,185 regular Standard collectibles in frozen patch **36.6.0.251952**, all 11 classes, generated dependencies, and the simulator/ML workflow. Excludes Mercenaries and Battlegrounds. This snapshot is not a claim about today's rotation.
- **844 live registered definitions; 341 staged recipes.** A staged recipe is not executable support. Eight earlier live definitions remain explicitly provisional (see `expanded/implementation_index.json`). Full Standard fidelity remains incomplete.
- Feature schema v30. No training or deck search has run; long training requires an explicit budget.

## Fixed 60-card batch

`../../docs/engine-audit/active-integration-batch.json` preserves the exact membership and baseline of 817. Do not replace its members, count operation bodies as completed cards, or close the batch before all 60 meet the recorded gates.

**2 members are now live:** Costume Merchant (`DINO_427`) and Gelbin's Triumph (`CATA_621`). Their explicit Mask and Paladin Aura pools contain only already implemented outcomes, including dual-class Acceleration Aura. Combo discounts and extra Aura duration are attached to the generated physical card. Full regression passed (2,671 checks). The fixed batch is **2/60 enabled and regression-validated**, and remains open.

**59/60 have engine-operation bodies; that is not 59 playable cards.** Primordial Lord still needs its historical Colossal pool and behavior. Other staged bodies need complete production pools and hook integration. Recent additions cover Merithra's held Mana/fill-hand effect, Disposable Acolytes' discard effect, Tortotem's multiple-type filter, Taka's selected stats/death payload, the Moon upgrade, Twilight Influence's target branch, and Harbinger's return trigger. Their synthetic-pool tests do not establish production completion or independent timing conformance.

The corrected batch dependency report identifies **340 distinct missing direct metadata outcomes out of the 341 staged collectibles**. Broad generation reaches nearly the entire remaining engine; these are planning candidates, not approved pools. Dynamic and historical selectors are explicitly flagged and require additional review. This explains why this batch cannot be finished as an isolated 60-card task. Resolve dependency families while retaining the fixed batch ledger; do not silently filter out unsupported outcomes.

## Latest shared mechanics

Added 25 live collectibles, retaining the fixed 60-card batch membership:

- Shatter: all five split spell pairs, Stolen Power, and Misplaced Pyromancer (7 collectibles). Includes physical half placement, combination, hand capacity, mulligan transition, combined copies/shuffling and hidden-identity observations.
- Rewind: Chrono Daggers, Portal Vanguard, Conflux Crasher, Bygone Doomspeaker, Cease to Exist, Aeon Rend and the four-Shade summon (7 collectibles). Includes pre-play restoration, fresh random rolls, single final payment/history, explicit keep/rewind decisions, delayed after-play listeners, lethal handling and used Rewind state through bounce.
- Dark Gifts: Wallow, Overgrown Horror, Xavius, Nightmare Fuel, Frostburn Matriarch, Cindersword and Dragon Turtle (7 collectibles). Uses the ten Constructed gifts, eligible distinct offers, physical deck choices, Wallow propagation, copy/Battlecry/Reborn gifts and gift-dependent payoffs. Global-pool Dark Gift generators remain staged.

- Forced combat: Warmaul Challenger (Core), Briarspawn Drake, Ursoc and Wilted Shadow. Repeated attacks bind physical targets, excess damage splits before Shield, Ursoc retains attack kills for resurrection, and Wilted Shadow attacks before the capped enemy heal.

The 106 new focused checks pass. These are candidate implementations, not independent client conformance. Outstanding checks include exact gift-offer probabilities, Living Nightmare ordering, arbitrary Shatter enchantment precedence and Rewind counter interactions with Silence. No training has run.

## Verification

**2,777/2,777 full-suite checks passed**, zero failures/errors/skips, with unchanged source fingerprint `fdedfe284b21f90b26ea9de7d30cfd27286b892b122adf24e8c3f51826ea419a`. Receipt: `runs/expanded_validation/validation-d80e8da3fa6c42bf9e4967b6e0ca5c65.json`. Detailed log: `runs/expanded_validation/shared-mechanics-combat-full.log`.

Current random smoke: **22/22 games terminal**, zero errors or caps, 2,333 feature decisions checked. Receipt: `runs/random_validation/summary-fdedfe284b21-40333f15421749a89fe4fc763a7c7a2e.json`. Both runs validate the same source fingerprint. These checks do not certify full Standard fidelity.

## Continue here

Use the exact-batch report (`generation-integration-blockers.json`), not the original 60-recipe report, for prioritization. Closed-family generation is in `expanded/generation_families.py`; staged runtime bodies and hooks are in `expanded/generation_extensions.py`. Registry admission remains explicit in `expanded/cards.py` with pinned metadata hashes in `reviewed_cards.json`.

Known open issues include full outcome closure, historical/generated tokens, independent event ordering and interaction evidence, remaining mechanics, ML observations for additional state, and all learning/deck-search gates. The saved goal was reported as `usageLimited` on October 2; it is not complete, and automatic continuation must not be promised while that limit remains.

Prior receipts/history are preserved in `../../docs/status-history-before-closed-generation.md`. The full roadmap remains `../../docs/ROADMAP.md`; machine-readable known fidelity gaps remain `expanded/fidelity_gaps.json`.


## Status before persistent replacement integration

# Current candidate status

Candidate: `staging/rebased-88`. Checks notebook: `notebooks/13_shared_rules_checks.ipynb`.

## Scope and actual coverage

- Target: all 1,185 regular Standard collectibles in frozen patch **36.6.0.251952**, all 11 classes, generated dependencies, and the simulator/ML workflow. Excludes Mercenaries and Battlegrounds. This snapshot is not a claim about today's rotation.
- **855 live registered definitions; 330 staged recipes.** A staged recipe is not executable support. Eight earlier live definitions remain explicitly provisional (see `expanded/implementation_index.json`). Full Standard fidelity remains incomplete.
- Feature schema v31. No training or deck search has run; long training requires an explicit budget.

## Fixed 60-card batch

`../../docs/engine-audit/active-integration-batch.json` preserves the exact membership and baseline of 817. Do not replace its members, count operation bodies as completed cards, or close the batch before all 60 meet the recorded gates.

**2 members are now live:** Costume Merchant (`DINO_427`) and Gelbin's Triumph (`CATA_621`). Their explicit Mask and Paladin Aura pools contain only already implemented outcomes, including dual-class Acceleration Aura. Combo discounts and extra Aura duration are attached to the generated physical card. Full regression passed (2,671 checks). The fixed batch is **2/60 enabled and regression-validated**, and remains open.

**59/60 have engine-operation bodies; that is not 59 playable cards.** Primordial Lord still needs its historical Colossal pool and behavior. Other staged bodies need complete production pools and hook integration. Recent additions cover Merithra's held Mana/fill-hand effect, Disposable Acolytes' discard effect, Tortotem's multiple-type filter, Taka's selected stats/death payload, the Moon upgrade, Twilight Influence's target branch, and Harbinger's return trigger. Their synthetic-pool tests do not establish production completion or independent timing conformance.

The corrected batch dependency report identifies **329 distinct missing direct metadata outcomes out of the 330 staged collectibles**. Broad generation reaches nearly the entire remaining engine; these are planning candidates, not approved pools. Dynamic and historical selectors are explicitly flagged and require additional review. This explains why this batch cannot be finished as an isolated 60-card task. Resolve dependency families while retaining the fixed batch ledger; do not silently filter out unsupported outcomes.

## Latest shared mechanics

Added **11 live collectibles** through physical storage and resurrection systems: Slime 'em!, Raith Van Geist, Iso'rath, Destructive Phoenix, Frostmourne, Clutch of Corruption, Nythendra, Togwaggle, Smuggler King, The Fins Beyond Time, Runi, Temporal Guardian, and Entomologist Toru.

The batch clears 10 of the 12 staged stored-card definitions, plus Raith. Irida Sinseeker and Timelooper Toki remain staged. The fixed 60-card batch still has 2 completed members; these 11 are dependencies outside its membership.

`expanded/stored_cards.py` handles bound copies, physical set-aside hands, attached discard timers and remembered resurrection. Clutch uses location cooldowns; Frostmourne captures its last killing blow; successful Reborn summons are recorded for Raith. Private payload objects do not enter observations. Schema v31 adds starting-hand memory, Reborn history and owner-only set-aside cards to the learning features.

47 new focused checks pass. Full batch details, card IDs, sources and independent-conformance limits: `../../docs/stored-cards-batch.md`. No training ran. Prior shared-mechanic changes and receipts are preserved in the status history.

## Verification

**2,824/2,824 full-suite checks passed**, zero failures/errors/skips, unchanged source fingerprint `394befffbd476136c0036673be8e2123b542e3d707637f652533b95e9fc09064`. Receipt: `runs/expanded_validation/validation-9e5d62b9beb6491f9f2504d64c018578.json`. Detailed log: `runs/expanded_validation/stored-cards-full.log`.

**22/22 smoke games terminal**, zero errors or caps, **2,291 feature decisions checked** under schema v31. Receipt: `runs/random_validation/summary-394befffbd47-6f93ac6502764028a101aa22bfd5a760.json`. Both runs validate the same source fingerprint. These checks do not certify full Standard fidelity or optimal play.

## Continue here

Use the exact-batch report (`generation-integration-blockers.json`), not the original 60-recipe report, for prioritization. Closed-family generation is in `expanded/generation_families.py`; staged runtime bodies and hooks are in `expanded/generation_extensions.py`. Registry admission remains explicit in `expanded/cards.py` with pinned metadata hashes in `reviewed_cards.json`.

Known open issues include full outcome closure, historical/generated tokens, independent event ordering and interaction evidence, remaining mechanics, ML observations for additional state, and all learning/deck-search gates. The saved goal was reported as `usageLimited` on October 2; it is not complete, and automatic continuation must not be promised while that limit remains.

Prior receipts/history are preserved in `../../docs/status-history-before-closed-generation.md`. The full roadmap remains `../../docs/ROADMAP.md`; machine-readable known fidelity gaps remain `expanded/fidelity_gaps.json`.


## Status before physical entity integration

# Current candidate status

Candidate: `staging/rebased-88`. Checks notebook: `notebooks/13_shared_rules_checks.ipynb`.

## Scope and actual coverage

- Target: all 1,185 regular Standard collectibles in frozen patch **36.6.0.251952**, all 11 classes, generated dependencies, and the simulator/ML workflow. Excludes Mercenaries and Battlegrounds. This snapshot is not a claim about today's rotation.
- **862 live registered definitions; 323 staged recipes.** A staged recipe is not executable support. Eight earlier live definitions remain explicitly provisional (see `expanded/implementation_index.json`). Full Standard fidelity remains incomplete.
- Feature schema v32. No training or deck search has run; long training requires an explicit budget.

## Fixed 60-card batch

`../../docs/engine-audit/active-integration-batch.json` preserves the exact membership and baseline of 817. Do not replace its members, count operation bodies as completed cards, or close the batch before all 60 meet the recorded gates.

**2 members are now live:** Costume Merchant (`DINO_427`) and Gelbin's Triumph (`CATA_621`). Their explicit Mask and Paladin Aura pools contain only already implemented outcomes, including dual-class Acceleration Aura. Combo discounts and extra Aura duration are attached to the generated physical card. Full regression passed (2,671 checks). The fixed batch is **2/60 enabled and regression-validated**, and remains open.

**59/60 have engine-operation bodies; that is not 59 playable cards.** Primordial Lord still needs its historical Colossal pool and behavior. Other staged bodies need complete production pools and hook integration. Recent additions cover Merithra's held Mana/fill-hand effect, Disposable Acolytes' discard effect, Tortotem's multiple-type filter, Taka's selected stats/death payload, the Moon upgrade, Twilight Influence's target branch, and Harbinger's return trigger. Their synthetic-pool tests do not establish production completion or independent timing conformance.

The corrected batch dependency report identifies **322 distinct missing direct metadata outcomes out of the 323 staged collectibles**. Broad generation reaches nearly the entire remaining engine; these are planning candidates, not approved pools. Dynamic and historical selectors are explicitly flagged and require additional review. This explains why this batch cannot be finished as an isolated 60-card task. Resolve dependency families while retaining the fixed batch ledger; do not silently filter out unsupported outcomes.

## Latest shared mechanics

Added **7 live collectibles**: Alexstrasza, Guardian of Life; Commander Geddon; Falric; Toreth the Unbreaking; Barbed Thorn; Gullible Guard; and Tranquil Clearing. The fixed 60-card batch remains 2/60 complete; these seven are dependencies outside its membership.

`expanded/lasting_rules.py` connects player-bound health rewards, physical turn-draw replacement, a common corpse-gain multiplier, shield hit counters, weapon enchantments and activation-player dormancy timing. Tranquil Clearing is correctly implemented as a location. Schema v32 includes the new public player state.

**48 focused checks passed.** Detailed contracts, sources and independent-conformance limits: `../../docs/lasting-rules-batch.md`. No training ran.

## Verification

**2,872/2,872 full-suite checks passed**, zero failures/errors/skips, unchanged source fingerprint `d0f3b1c3c52b829035ce9ef0ade8f61725d6a5a99b5869be99ad8ad33b088dca`. Receipt: `runs/expanded_validation/validation-736ce74b6f8e4e72b2d1813279698447.json`. Detailed log: `runs/expanded_validation/lasting-rules-full.log`.

**22/22 smoke games terminal**, zero errors or caps, **2,552 feature decisions checked** under schema v32. Receipt: `runs/random_validation/summary-d0f3b1c3c52b-3b8715ad823c4c0f820ab6945fe5b225.json`. Both runs validate the same source fingerprint. These checks do not certify full Standard fidelity or optimal play.

## Continue here

Use the exact-batch report (`generation-integration-blockers.json`), not the original 60-recipe report, for prioritization. Closed-family generation is in `expanded/generation_families.py`; staged runtime bodies and hooks are in `expanded/generation_extensions.py`. Registry admission remains explicit in `expanded/cards.py` with pinned metadata hashes in `reviewed_cards.json`.

Known open issues include full outcome closure, historical/generated tokens, independent event ordering and interaction evidence, remaining mechanics, ML observations for additional state, and all learning/deck-search gates. The saved goal was reported as `usageLimited` on October 2; it is not complete, and automatic continuation must not be promised while that limit remains.

Prior receipts/history are preserved in `../../docs/status-history-before-closed-generation.md`. The full roadmap remains `../../docs/ROADMAP.md`; machine-readable known fidelity gaps remain `expanded/fidelity_gaps.json`.
