# Current candidate status

Candidate: `staging/rebased-88`. Checks notebook: `notebooks/13_shared_rules_checks.ipynb`.

## Scope and actual coverage

- Target: all 1,185 regular Standard collectibles in frozen patch **36.6.0.251952**, all 11 classes, generated dependencies, and the simulator/ML workflow. Excludes Mercenaries and Battlegrounds. This is not today's rotation.
- **877 live registered definitions; 308 staged recipes.** Runtime bodies in staging are not playable support. Eight earlier live definitions remain explicitly provisional in `expanded/implementation_index.json`; independent fidelity gaps remain throughout the engine.
- Feature schema **v58**. No training or deck search ran. Long training still requires an explicit run budget. No Jupyter action is needed for these local development checks.

## Crafted identity and accounting repair

**281/281 focused and regression checks passed** (`/private/tmp/crafted-identity-checks.log`). This includes seven new identity checks, final-card paths, both repaired accounting assertions, provenance, Slice replay and automatic-card suites. Crafted intrinsic definitions now survive physical copies, Silence then bounce, and fresh replay; automatic locations receive their crafted activation and Deathrattle payloads. Temporary buffs/discounts reset on fresh replay. Transformation discards the old identity. No full-suite rerun or training was performed in this follow-up.

Coverage remains **877 live / 308 staged**. This repairs shared behavior; it does not admit staged cards or close production-pool, component-composition, resurrection or independent-client fidelity gates.

## Final collectible implementation paths — accounting repair

Consolidated full-suite session **91357** completed: **4,309 checks, two accounting assertion failures, no errors**. Receipt `runs/expanded_validation/validation-f76d789579d844b3babf1e3a631ad053.json`; log `/private/tmp/final-card-paths-full.log`. The two assertions omitted the new Genn/Morchie modules; now updated while retaining their no-live-admission checks. The first run was interrupted after finding a custom-choice dispatch bug; fixed and **5/5 existing choice-continuation tests passed**. Dependency accounting **28/28 passed**; log `/private/tmp/final-card-paths-dependencies.log`. All-class smoke session **70462** completed: **11/11 terminal games, zero errors/caps**, log `/private/tmp/final-card-paths-smoke.log`. No training running.

All 26 previously missing collectible paths now have staged declarations: **308/308 staged declarations; zero without a declaration; 877 live registered collectibles**. Queue refresh completed; **80 cards still have unresolved selector/dependency mappings**. This is NOT full playable coverage. The last three exceptional consumers and curated minion forge deliberately reject absent production contracts. Custom component passives, suspicious name/tribe changes, full Fire immunity and independent interaction fidelity remain incomplete.

**91/91 new integration fixtures passed**, covering the new shared paths and all 31 Osk forms (`/private/tmp/final-card-paths-tests.log`). **112/112 existing construction/Rewind/generation/Infinity/deadline checks passed** (`/private/tmp/remaining-all-first-checks.log`). Subsequent small Fire-healing and forged-Battlecry fixes will be covered by the consolidated suite. Initial new checks caught pre-split Fire guard bypass; fixed. Earlier receipts do not validate this source. No training or deck search ran.

Schema v58 now includes public pending Kindred/next-spell effects, clock state, Sidequests, Coin/Tendril progression and owner-private contraband/investigation state. The exact outstanding implementation and evidence gates are recorded in `expanded/fidelity_gaps.json`. Production pool closure and admission remain the next major work; do not equate declaration completion with complete Standard support.

## Consolidated remaining-card group: four Infinity cards and two deadlines

**282 staged bodies / 26 missing / 877 live**, confirmed by completion queue refresh 89878 (complete). Added `END_012` Hand of Infinity, `END_018` Acolyte of Infinity, `END_024` Flames of Infinity, `TIME_024` Murozond Unbounded, `JAIL_860` Chef Neth'rek, and `TLC_602` Enter the Lost City. Shared implementations live in `expanded/infinity.py` and `expanded/turn_deadlines.py`; no live admission was changed.

**96/96 combined family checks passed**, log `/private/tmp/shared-six-tests.log` (session 83974 complete). **53/53 scheduling, extra-turn, Secret/privacy, timed/held-cost regressions passed**, log `/private/tmp/shared-six-regressions.log` (session 64858 complete). Dependency suite **32537** completed: **27/27 passed**, log `/private/tmp/shared-six-dependencies.log`. No full regression or training running. Earlier 4,162-check receipt predates these changes.

Infinity uses an explicit provisional integer cap; independent client verification of saturation/arithmetic and several layer/phase boundaries remains open. Murozond's pending effect is copied with enchantments and removed by Silence. Cost restoration removes the matching layer rather than overwriting other cost changes. Flames participates in ordered end-turn entries and ordinary damage prevention. Chef/Lost City use owner-turn deadlines, separate from doubled end effects, with exact client timing still gated. Fidelity gaps `infinity_numeric_and_timing` and `owner_turn_deadlines` distinguish staged code from verified behavior.

Continue through all 26 remaining bodies. No user Jupyter action needed; no subagents authorized.

## Zuramat's Prison: staged discard storage and replay

Added the Prison location, Whisper of the Void, and Zuramat's finite automatic replay. The final selected discard is captured before final-charge removal, so the released minion receives its pool. Each prison is independent; copied Zuramats inherit only remaining entries. Ordinary summons have no inherited pool. Replays validate all remaining candidates before consuming one random entry and use the shared resumable automatic-card path.

**44/44 Prison, evolving-location, automatic-card and Slice replay tests passed**; `/private/tmp/prison-tests.log`, session 4082 completed. Includes normal/final activation, explicit destruction, Silence, copied/empty pools, spell casting, owner-turn checks and failed replay rollback. Source-backed semantics and limitations are in `../../docs/engine-audit/zuramat-prison-contract.json` and fidelity gap `zuramat_prison_replay`.

Expected **276 staged bodies / 32 missing / 877 live** pending queue refresh **22510**, log `/private/tmp/prison-queue.log`. No training or full regression running. The earlier 4,162-check receipt predates setup and Prison work. Keep working on all remaining bodies; no user Jupyter action needed.

## Remaining-card implementation: constructed opening family

**275 staged bodies / 33 missing / 877 live**. Added Azalina and Commander Beatrix in `expanded/deck_setup.py`, with explicit `Deck.beatrix_minion`, deck-size/conflict validation, simultaneous pre-mulligan physical copying, forty starting Health, and draw-to-full Battlecry. Original submitted-deck predicates remain distinct from copied opening effects; copied cards preserve opponent ancestry without original-deck provenance. Connected copied Godfrey, Ysera, Hamuul, Mug'Zee, Broxigar and Llane setup. Hogger now duplicates surviving current deck/hand legendaries with a 99-card deck cap.

**74/74 setup-family checks passed**, including a full Azalina constructor; log `/private/tmp/deck-setup-tests.log` (session 13003 complete). After adding opponent-copy ancestry, **13/13 construction checks passed**, log `/private/tmp/deck-setup-provenance-tests.log` (session 21598 complete). Queue build 92518 complete; its counts include both bodies, but its source hash predates that final ancestry change. No full regression or training running. The 4,162-check receipt below predates this work.

These are staged bodies, not live admission. `constructed_opening_copies` records unresolved selected-card eligibility/provenance, combined setup ordering, random-deck sampling for exceptional sizes, and copied setup effects belonging to the remaining unimplemented cards. Primary-source contract: `../../docs/engine-audit/constructed-opening-contract.json`. Continue the remaining 33; do not ask for a Jupyter rerun between groups.

## Consolidated milestone and subsequent overdraw correction

**4,162/4,162 full checks passed**, zero failures/errors/skips; source unchanged. Receipt `runs/expanded_validation/validation-478bd3c5487e421190b673798c834312.json`, fingerprint `1d3ccb0b440a1261743e2ba403835896c325f579a7fc002f169d8d11c286b200`. Full session 10060 is complete. **27/27 dependency checks** and **22/22 terminal smoke games** also passed (no errors/caps). Smoke receipt `runs/random_validation/summary-1d3ccb0b440a-8f4bb0f959d54eccb9fc8bcf846ebc56.json`.

After that snapshot, corrected Godfrey/IMPFERNAL destruction via a shared deck-burn handler used by ordinary draws, deck Discover and bottom-deck selection. Recovery retains destruction triggers and caps its cache at 99; generated overflow is unchanged. Replaced the incorrect protection fixture and added return/no-repeat, capacity and deck-choice checks. **39/39 focused overdraw, recovery and Discover checks passed**, log `/private/tmp/overdraw-correction-tests.log`; session 61643 completed. The preceding full receipt predates this correction. Queue remains **273 staged bodies / 35 missing / 877 live**. No training ran.

## Mug'Zee: staged setup and passive powers

Connected original-deck predicates, one/two passive-power assignment, no passive activation actions, first-minion cost reduction from turn three, and fifth-minion printed Battlecry operation repetition. Replacing the primary leaves the secondary intact. **58/58 Mug'Zee and replacement-power checks passed**, including an actual fifth-minion paid-play fixture; log `/private/tmp/mugzee-tests.log`, session 94696 complete. Frozen reward texts and official two-power/replacement explanation ground this staged behavior; setup ordering, countered plays and full repeated-Battlecry semantics remain gated.

Expected **273 staged bodies / 35 missing; 877 live**, pending completion queue refresh. No full regression/training running. Last full receipt predates replay, removal and passive-power changes.

## Godfrey recovery order corrected from primary evidence

Official HearthstoneTeam Q&A specifies random overdraw-card returns. Replaced FIFO recovery with random selection from the remaining physical cache. **34/34 recovery, remaining-system and off-board Deathrattle fixtures passed**, including four new checks for non-FIFO selection, identity/enchantment retention, no duplication and no RNG consumption while full. Log `/private/tmp/overdraw-order-tests.log`; session 95863 complete. Recovery timing versus other hand-entry/Quest effects remains gated.

No new card body counted: **36 missing / 272 staged bodies / 877 live**. No validation or training active; prior full receipt predates recent changes. Next setup work must preserve original submitted-deck conditions and power replacement rules; Mug'Zee's two possible passive powers require both minion-cost and Battlecry-count integration.

## Off-board removal audit: overdraw paths connected

Connected ordinary draw-overflow and the two deck-choice burn paths to the shared destruction callback. Generated overflow and protected overdraw-cache cards remain separate from deck destruction. **38/38 removal and generation-lifecycle checks passed**, including explicit ordinary-overdraw, generated-overflow and protected-cache fixtures. Log `/private/tmp/zone-removal-audit-tests.log`; session 45906 complete. Burn/protection timing and cross-owner draw attribution remain independently unverified, so these fixtures are not client certification.

Queue refresh 86096 completed. **272 staged bodies / 36 missing; 877 live**, unchanged. No validation/training active. Full 4,119-check receipt predates replay and off-board removal work.

## Off-board Deathrattles: IMPFERNAL staged body

Added shared hand/deck discard/destroy callback and other-characters damage. IMPFERNAL is wired to batched discards, enemy top-deck destruction, generated-deck cleanup, rarity-based destruction, Herald deck destruction and timed hand destruction, plus ordinary board Deathrattle. **25/25 zone-trigger and off-board Deathrattle fixtures passed**, including eight new cases. Log `/private/tmp/zone-deathrattle-tests.log`; session 79295 complete. Official developer Q&A confirms discard and hand/deck destruction eligibility.

Remaining removal/burn/overdraw and replacement paths, ordering and multiplier semantics require audit; no live admission. Expected **272 staged bodies / 36 missing; 877 live**, pending queue refresh. Slice queue refresh session 98588 completed. No full validation/training active. Prior full receipt predates these changes.

## Slice and Dice: staged consumer connected

Captured current-turn owner hand-play records feed a randomized replay sequence of fresh printed cards with enemy-preferred targeting. The full replay set is checked before RNG/execution. A shared deferred end-turn request waits for action/card/trigger frames to clear and does nothing during an already-running turn phase or on a different active owner. **49/49 replay, automatic-casting, extra-turn and private-history checks passed**, log `/private/tmp/slice-replay-tests.log`; session 75153 complete. Fixed an optional power-frame access found by the first run; used an explicit synthetic Battlecry fixture instead of an unavailable card.

This is a staged body, not admission. Countered/automatic play eligibility, exclusion of earlier same-card copies, retained modifications/branches, nested recursion and forced-end priority remain explicit gaps. Expected **271 staged bodies / 37 missing; 877 live** pending queue refresh. No full validation or training running; prior full receipt predates this consumer.

## Replay targeting and primary-source constraints

Added an explicit `prefer_enemies` internal-cast/automatic-card policy: choose legal enemies when present, otherwise retain legal fallback targets. Existing strict `enemies` behavior remains unchanged. **14/14 preferred-target and automatic-card checks passed**, log `/private/tmp/preferred-target-tests.log`. A fixture initially expected the unbuffed Attack; corrected to the frozen +2/+3 effect and added a two-sided preference check.

Official HearthstoneTeam Q&A confirms random Slice and Dice replay order, friendly-side disguised replay and exclusion from random generation. Source and remaining consumer contracts saved in `../../docs/engine-audit/slice-and-dice-contract.json`. The existing history foundation preserves order but the consumer must randomize its captured replay set. Slice and Dice remains unimplemented; **38 missing collectible bodies; 877 live**. No validation or training currently running; the full 4,119-check receipt predates replay foundations.

## Physical replay history foundation

Added private turn-indexed deep snapshots of admitted hand plays, including physical card identity, paid cost, chosen branches, target and position. Retrieval preserves duplicate physical cards and excludes an exact source UID. Snapshot data is not added to observation/public logs. Internal casting does not enter this history. **28/28 replay-history, extra-turn and Origin Stone fixtures passed**, including seven new snapshot/privacy checks. Log `/private/tmp/replay-history-tests.log`; session 81938 complete. Initial tests assumed optional cost_delta existed; corrected default-zero assertions passed.

This does not implement Slice and Dice or decide its replay eligibility. Countered plays, automatic plays, transformed identities, whether to preserve card modifications/branches, Battlecry replay and final turn ending remain consumer contracts. **38 collectible bodies remain; 877 live**, unchanged. No full validation/training running; the 4,119-check milestone below predates this change.

## Historical rewards: consolidated validation passed

**4,119/4,119 engine fixtures passed**, zero failures/errors/skips; unchanged source fingerprint `cb9ab75a52d2306c8a88f241e05e00e290f78eb76397e861d449643a4195efa6`. Receipt: `runs/expanded_validation/validation-c2563e4e121a4a898590b13fc4e15345.json`; saved log: `runs/expanded_validation/latorvius-full.log`. **27/27 dependency checks** and **22/22 terminal smoke games**, zero errors/caps, also passed on this checkpoint. Smoke receipt: `runs/random_validation/summary-cb9ab75a52d2-e3a1123fa8e34155bee22fd842cbcc5d.json`. Sessions 83139, 81634 and 85903 are complete; no validation/training is running.

This validates internal fixtures for the automatic-card fixes, extra turns, nine staged historical reward bodies, reward distribution and schema v57. It does not certify full Standard/client fidelity. **877 live; 308 staged; 270 staged collectible bodies; 38 missing.** Exact Enter the Lost City progress timing, production generation-pool closure and documented historical reward interactions remain unresolved. Shared Infinity family research is saved in `../../docs/engine-audit/infinity-family-contract.json`; no Infinity body has been counted. Earlier sections are historical checkpoints.

## Historical-reward validation: launch record

Dependency validation completed **27/27 checks** (session 81634). All-class smoke validation completed **22/22 terminal games**, zero errors/caps (session 85903), fingerprint `cb9ab75a52d2306c8a88f241e05e00e290f78eb76397e861d449643a4195efa6`. Receipt: `runs/random_validation/summary-cb9ab75a52d2-e3a1123fa8e34155bee22fd842cbcc5d.json`. Full suite 83139 remains active; no current full-success claim.

Full regression session **83139**, log `/private/tmp/latorvius-full.log`; dependency tests session **81634**, log `/private/tmp/latorvius-queue-tests.log`; all-class random smoke/feature checks session **85903**, log `/private/tmp/latorvius-smoke.log`. Keep engine, hashed JSON and test sources unchanged until full regression completes. These are validation runs, not training. Previous full receipt is failed and predates recent reward work; no current full success is claimed.

Current scope remains **877 live / 308 staged; 270 staged collectible bodies / 38 missing**, schema v57. Nine historical Latorvius reward bodies plus distribution are staged; exact root Quest checkpoint, complete generated outcome contracts and documented interaction gaps remain unresolved. Goal remains incomplete.

## Latorvius reward distribution connected

Latorvius's staged Battlecry validates all nine historical rewards and direct generated dependencies plus the Murloc generation contract before RNG or generation. It selects two distinct rewards for hand and shuffles the other seven into the deck; repeated Battlecries use a fresh complete nine-reward set. **39/39 reward/distribution and Crystal Core fixtures passed**, including five distribution/preflight cases. Log `/private/tmp/latorvius-distribution-tests.log`; session 43040 complete. Prior surrounding copy/transformation/aura regression also completed **71/71**, session 74109, log `/private/tmp/crystal-core-surrounding.log`.

Enter the Lost City's exact survived-turn checkpoint is still unverified: frozen XML confirms total ten and reward identity, but does not encode the executable trigger. Wiki access returned HTTP 403. No speculative turn counter has been admitted. Full-hand reward overflow/distribution ordering and complete production outcome contracts still require review. **38 collectible bodies remain; 877 live**, unchanged. No full regression or training running.

## Crystal Core: persistent base-stat foundation

Crystal Core now has a staged body using persistent physical base-stat overrides, separate from removable enchantments. Casting resets existing minion stats/damage; future summons use the new base, and Silence/copy/bounce paths retain it. Hand observations expose adjusted stats; player state is public in feature schema v57. **66/66 reward, Crystal Core and permanent fixtures passed**, including eight unique Crystal Core tests; log `/private/tmp/crystal-core-tests.log`, session 44869 complete. An initial test version inherited duplicate reward fixtures; the final 66-check run removes that duplication.

All nine historical reward bodies now exist, but Crystal Core zone/provenance/scaling/copy cases remain explicitly incomplete, and Megafin's complete production pool remains gated. **Do not admit Latorvius yet.** Root Quest and reward distribution remain to implement. **38 collectible bodies remain; 877 live**, unchanged. Surrounding copy/transformation/aura checks are running; log `/private/tmp/crystal-core-surrounding.log`. No full regression or training running.

## Nether Portal: passive permanent support

Added passive permanent end-turn entries to the shared turn scheduler. Nether Portal occupies a board slot, cannot use the Rift activation, and summons two Imps through resumable operations. The portal is excluded from minion board clearing. **58/58 historical-reward and permanent-object checks passed**, including seven new portal fixtures. Log `/private/tmp/nether-portal-tests.log`; session 7452 completed. Exact placement/ordering, trigger multiplication and full-board casting semantics remain independently unverified.

Eight of nine Latorvius reward bodies now exist; Crystal Core remains, followed by the root Quest and reward distribution. **38 collectible bodies remain; 877 live**, unchanged. Queue rebuild session 83357 from the prior checkpoint completed successfully. No full regression or training running; previous full receipt predates these changes.

## Sulfuras and Megafin: staged reward support

Sulfuras now installs the permanent DIE, INSECT! power through existing replacement-power logic; weapon removal does not remove the power. Megafin uses a shared plain hand-fill operation with an explicit Murloc pool contract and no discount. **112/112 reward, replacement-power, power-sequence/trigger and generation-lifecycle checks passed**, including 19 historical reward fixtures. Log `/private/tmp/latorvius-power-pool-tests.log`; session 44992 complete. Initial validation invocation used a nonexistent test module; corrected invocation above passed.

Seven of nine historical reward bodies now exist. Crystal Core and Nether Portal remain, plus Enter the Lost City progress and Latorvius reward distribution. Megafin's production pool still requires complete reviewed membership/outcomes; fixtures use controlled pools. Quest timing, Adapt eligibility and historical effect interactions remain gated. **38 missing collectible bodies; 877 live**, unchanged. No full suite or training running. Queue rebuild session 83357 records all nine rewards, their direct tokens/power/Adapt dependencies and the Murloc selector.

## Latorvius historical reward effects: four more connected

Added staged Barnabus deck-minion cost setting, Queen Carnassa's twenty-Raptor shuffle and Brood draw, Amara's Health setting, and Galvadon's five sequential Adapt choices. Generic minion Adapt shares application/resumable choice handling but does not grant Ashalon's persistent player enchantment. **30/30 focused reward, Ashalon and extra-turn fixtures passed**, log `/private/tmp/latorvius-rewards-tests.log`; session 96008 complete. No full validation is running. These changes postdate the last full receipt.

Five of nine historical reward bodies now exist including Time Warp; Crystal Core, Nether Portal, Sulfuras and Megafin remain, plus root Quest and reward-distribution behavior. These are generated dependencies, not additions to Standard deck legality. **270 staged collectible bodies / 38 missing; 877 live**, unchanged. Historical reward interaction fidelity remains gated; no new admission or training.

## Time Warp: extra-turn foundation connected

The generated historical Time Warp reward now reserves an additional owner turn, with a per-player once-per-game flag. End-turn cleanup and triggers complete normally; the additional turn runs ordinary start effects, draw and resource refresh. Persistent state is exposed through observation and feature schema v56. Eleven focused fixtures passed, covering paid/internal casting, repeated use, both players, draw/resources, cleanup, end triggers, skipped-turn interaction, turn limits and features. Off-turn/cross-controller timing still requires independent evidence; no Latorvius root admission. **38 collectible bodies remain**.

The previous automatic-card full run completed **4,069 checks with one failure**, zero errors/skips and unchanged source. Receipt: `runs/expanded_validation/validation-740c5bfb006e4240abda105ef39e9ac3.json`; log: `runs/expanded_validation/automatic-cards-full.log`. The failure was the family-accounting assertion excluding Ohn'ahra's automatic-play classification. Corrected the assertion and removed an accidental Ohn'ahra location-table entry; metadata type validation now guards that table. This failed receipt is not current-code certification. Surrounding regression passed **94/94 checks**, including the corrected family accounting and extra-turn, automatic-execution, Quest weapon and lifecycle checks. Log `/private/tmp/extra-turn-surrounding.log`; session 76931 completed. Session 22391 is complete; no full run is active.

## Ohn'ahra and automatic execution: historical checkpoint


Ohn'ahra now has a staged end-turn body using sequential top-deck automatic execution. Cards leave the deck without draw/discard or paid-play events; empty/short decks cause no fatigue. Physical weapons and minion modifiers are retained. **39 focused automatic-execution/Origin Stone checks passed**, including eight Ohn'ahra fixtures. Completion queue rebuilt.

**270/308 staged declarations; 38 missing bodies; 877 live.** Dynamic top selection versus initial-three snapshot, full-board consumption, automatic triggers and controller changes remain explicit fidelity gates. No new admission.

Dependency validation passed **27/27** checks. Random smoke validation passed **22/22** terminal games, zero errors/caps; receipt `runs/random_validation/summary-cf4ea1998b17-29e5c90e385443ed934da4bdb51c9013.json`. Full suite session 22391 was polled and remains active. Latorvius's nine historical reward requirements and unresolved fidelity boundaries are now recorded in `../../docs/engine-audit/latorvius-reward-contract.json`; no new runtime body or admission is claimed.

Full consolidated suite is running as session **22391**, log `/private/tmp/automatic-cards-full.log`. Keep source/tests unchanged until it completes. Previous receipts predate these changes. No training ran.

## Forbidden Sequence / Origin Stone: staged family connected

Eight completed classified Discovers award Origin Stone. The weapon snapshots physical identity before choice resolution, captures unchosen options and queues automatic execution with charge reservation. Targeted testing found and fixed an opponent-history leak in internally cast Secrets. Completion queue rebuilt. **269/308 staged declarations; 39 missing bodies; two remaining Quest/Sidequest roots; 877 live**. No admission.

Exact durability timing, captured-trigger persistence after weapon replacement, nested Discover order, special eligibility and option modifiers remain explicit gates. Automatic-card consumer semantics are still provisional. The previous full receipt predates this family; no full validation currently active. No training ran.

## Automatic-card execution foundation

Added `expanded/automatic_cards.py` connected to resumable effect splitting. Detached physical spells reuse internal casting; minions enter without paid-hand Battlecries; weapons retain their physical card; locations and supported heroes use existing entry helpers. No temporary hand insertion, mana payment or paid-play counters. Nine direct fixtures pass. Consumer-specific semantics and hero/location modifiers remain explicit gates in `automatic_card_consumer_semantics`. No card-count reduction: **40 bodies remain**. No full validation currently active; previous full receipt predates this helper.

## Origin Stone foundation: private Discover offer snapshots

Added `expanded/discover_offer.py` and completed Discover publication through the existing explicit choice classifier. Snapshot selected and unchosen options before resolution mutates the choice; equal identities remain distinct positions. Offer details stay out of public Discover logs. This event does not itself implement Origin Stone or grant Discover semantics to arbitrary choices. **92 targeted checks passed**: 80 offer/generation/Quest/privacy checks plus 12 automatic-choice checks. Eight new offer fixtures included. No current full validation run; the 4,034 receipt below predates this change. **40 card bodies remain**. Next: consume captured offers using resumable automatic execution and weapon-identity durability accounting. No training ran.

## Mountain/Ashalon family: consolidated validation passed

Spirit of the Mountain and Ashalon now have staged bodies: one unused type per played minion, two Adapt offers, public persistent selected Adaptations, and grants to later played minions before Battlecry. Summoned minions receive no grants. **81 focused Quest/Adapt checks passed**, including nine Ashalon fixtures. Completion queue rebuilt with reward, all ten options and Plant dependency.

**268/308 staged declarations; 40 missing bodies; three remaining Quest/Sidequest roots; 877 live.** Schema v55 exposes persistent Adapt choices. Multi-type assignment, choice eligibility, Discover attribution, effect timing and stacking remain explicit fidelity gates. No live admission.

Consolidated validation for End Time, Food Chain and Ashalon passed **4,034/4,034 engine checks**, zero failures/errors/skips. Source unchanged `7b9e1e33f3b4d244425e1ac9cbdc3f10c3b7b1d001d4f4455bbea615b2c64a50`. Receipt: `runs/expanded_validation/validation-cdbcf4f99d594fb8aa8f76837671f120.json`; log: `runs/expanded_validation/ashalon-full.log`. **27/27 dependency checks**; **22/22 terminal smoke games**, zero errors/caps, 2,463 feature decisions, schema v55. Smoke receipt: `runs/random_validation/summary-7b9e1e33f3b4-a12a9081fd0445e4abf1678d70f2fea5.json`. Sessions 98135, 51034 and 28458 completed successfully; no validation currently running. These checks do not certify independent game fidelity or full Standard support.

Next shared system: automatic card execution and captured Discover offers for Origin Stone, also needed by EDR_031, JAIL_500 and CORE_WON_145. Contract: `../../docs/engine-audit/origin-stone-contract.json`. No training ran. Earlier sections below are historical checkpoints.

## Ashalon foundation: Constructed Adapt application

Added `expanded/adapt.py` with all ten explicit regular-game Adapt effects. It applies stat changes, keywords, next-owner-start Stealth and Living Spores using the frozen Plant token. Missing token metadata rejects before attachment; Mercenaries identities are not accepted. Ten focused fixtures pass, including shield regrant, stacking, Silence and Plant Deathrattle execution. Choice eligibility, repeated selections, unique-type Quest tracking and persistent grants to later played minions remain to connect and review. No new card body counted: **41 missing**, 267 staged declarations, 877 live. No full validation run is active.

## Food Chain and Shokk: staged family connected

Food Chain tracks distinct paid-play Beast Attack values 1/3/5/7. Shokk preflights complete pool contracts and sequentially Discovers 8/6/4 Attack Beasts, setting each generated card's cost to two. Missing later contracts reject before the first offer; no supported-only pool substitution. **120 targeted generation/Quest checks passed**, including nine new Food Chain tests. Completion queue rebuilt with all three pool selectors and reward dependency.

**267/308 staged declarations; 41 missing bodies; four remaining Quest/Sidequest roots; 877 live.** The paid-hand Attack snapshot requires independent review for battlefield auras, transformations, scaling and Battlecries. Production pool membership/outcome closure remains gated. No new live admissions and no full suite currently running; the previous 3,988-check receipt predates End Time and Food Chain. No training ran.

## Food Chain foundation: Attack-based generation contracts

Shared PoolRequest now supports validated Attack bounds independently of Cost. Exact Attack requests remain distinct, serializable contract keys. **58 generation checks passed**, including eight new selector checks. Frozen Shokk candidate pools contain 4 / 11 / 15 Beasts at Attack 8 / 6 / 4; complete candidate identities and catalog hash are saved in `../../docs/engine-audit/shokk-pool-candidates.json`. Membership is not yet an approved production contract. Food Chain progress and sequential Shokk Discover remain to connect; no card-count reduction in this step. Still **42 missing bodies**. No full run currently active.

## End Time family: staged, focused checks passed

Battle at the End Time tracks full then empty hand state through the shared hand-entry/reward checkpoints. Tick and Tock has staged draw-to-full and opponent-hand removal effects. **175 targeted Quest, stored-card and Shatter checks passed**, including ten End Time fixtures. Completion queue rebuilt. **266/308 staged declarations; 42 missing bodies; five remaining Quest/Sidequest roots; 877 live**. No new admission.

This implementation remains provisional: exact swap/transform boundaries, draw count with cast-when-drawn, reward insertion priority and discard-versus-removal semantics require review. See `endtime_hand_boundaries` fidelity gap and the source contract. The full 3,988-check receipt below predates this change; no full run currently active. No training ran.

## Gorishi family: consolidated validation passed

Unleash the Colossus now has staged own-turn exact-two damage progress and full-hand reward waiting. Gorishi installs a public persistent reward count; both-turn bonus damage uses a separate cause to prevent self-recursion. Repeated rewards currently queue separate two-damage hits. Stacking, death/trigger ordering and interaction fidelity remain explicit gates, not certified behavior. **265/308 staged declarations; 43 missing bodies; six remaining Quest/Sidequest roots; 877 live**. Feature schema v54 exposes Gorishi stacks.

**3,988/3,988 full engine checks passed**, zero failures/errors/skips. Source unchanged: `c6968b04e22c5df0d9d88046f17e044d527c096a6fc6a8ab42509c247701397c`. Receipt: `runs/expanded_validation/validation-74b0398a3fa84aea8b9bfb89e6a5faa6.json`; log: `runs/expanded_validation/gorishi-full.log`. **27/27 dependency checks** and **22/22 terminal smoke games** passed, zero errors/caps, 2,463 feature decisions, schema v54. Smoke receipt: `runs/random_validation/summary-c6968b04e22c-533ca59e243441e5833a0e5088a20e55.json`. Sessions 39532, 87210 and 8758 completed successfully; no validation remains running. These fixtures do not certify independent client fidelity or complete Standard support.

Next: Battle at the End Time and Tick and Tock. Contract: `../../docs/engine-audit/end-time-quest-contract.json`. Observe semantic hand departures before refill, not temporary Python list operations used for transformations. Reconcile fixed-count versus dynamic refill draws and empty-hand Deathrattle semantics before admission. No training ran.

## Damage attribution foundation: focused validation

All direct expanded-engine damage call sites now explicitly preserve controller where attributable, including effects, combat/retaliation/spill, basic and replacement powers, locations, Secrets, corpse missiles and permanent end-turn damage. Fatigue and fixed environmental refresh damage explicitly clear source attribution. Target ownership is snapshotted before damage callbacks. Location sources no longer qualify as minion killers for CATA_185. **189 targeted checks pass**, including 16 attribution fixtures, entity effects, locations and combat families. Gorishi's reward recursion, stacking and Quest adapter remain to implement/review before admission. No new card admission; still 264 staged bodies / 44 missing / 877 live. Full regression below predates these changes.

## Completed Reach Equilibrium checkpoint

Reach Equilibrium has staged parallel objectives and complete reward bodies. All **3,960/3,960** engine checks passed, zero failures/errors/skips; source unchanged `3b00231441741167bad3060acee9e169289aed567ca79c34a1207cc3c7800a7d`. Receipt: `runs/expanded_validation/validation-f6171e417aee4ec4be1162304fd9c8a2.json`; log: `runs/expanded_validation/equilibrium-full.log`. **27/27** dependency checks and **22/22** terminal smoke games passed, zero errors/caps, 2,463 feature decisions. Session 20771 completed successfully; do not poll or restart it. The earlier interrupted run was replaced by this successful run. Partial setup, reward timing and combination interactions remain admission gates. Seven Quest/Sidequest roots remain. No training ran.

## Quest progress foundation


Added `expanded/quest_progress.py`: explicit event counters, distinct-value objectives, ordered stages and parallel objectives. Completion paths emit once; one event cannot skip across two ordered stages. Input states remain unchanged, conditions reject missing/mistyped public facts, and damage occurrence counts remain separate from damage amount. Existing Quest counters use the shared capped-counter helper.

Focused validation: **51 Quest checks and 20 repeatable-Quest checks passed**, including 17 new tracker fixtures. No observation schema change. The eight staged Quest roots still need event adapters and complete rewards; **45 bodies remain missing, 263 staged declarations and 877 live definitions**. The full-suite receipt below predates this change and does not certify current source. No training ran.

The actual workspace still has a trailing space in its folder name. The new app writable-root setting omits that space; edits were applied through approved tool escalation to the existing project, without relocating or duplicating it.

## Previous completed Muradin coding and validation

Muradin, High King's Hammer and Avatar Form now have staged effects. Shared physical weapon retention, weapon stat buffs and hero Windfury are connected. Avatar Form uses one-turn character after-attack effects with public feature counts (schema v52). All eleven Fabled roots now have bodies; this is not complete family certification or live admission.

**263/308 staged runtime declarations; 45 missing bodies across 17 categories; 877 live.** Copy/Silence/return/replay and damage-attribution assumptions remain explicitly gated; see the [Fabled checkpoint](../../docs/fabled-checkpoint.md). Next connected workstream: the eight remaining Quests/Sidequests and their complete rewards. The [source inventory](../../docs/engine-audit/quest-source-inventory.json) preserves 58 frozen records and primary patch-note constraints.

Current-source validation: **3,900/3,900 full engine checks**, zero failures/errors/skips; **26/26 queue checks**; **22/22 random legal games terminal**, zero errors/caps, **2,463 feature decisions**. Includes 39 Muradin-family and six physical-weapon identity fixtures. Source unchanged: `4796e64868ffcaf3c063d34ed88ad6975aba7c1d247268877b1a0b87fb6ad4ae`. Full receipt: `runs/expanded_validation/validation-94fa4bc47ec24afe8b6653f9bb6ff11f.json`; log: `runs/expanded_validation/muradin-full.log`. Smoke receipt: `runs/random_validation/summary-4796e64868ff-a6f3a737e9ac4ea8b54a6a5a8438a242.json`. Smoke exercises admitted decks; controlled fixtures exercise staged effects. This is not full Standard certification. No training or deck search ran.

## Previous Azshara family validation

Azshara now has staged effects for both choices and both base/upgraded location pairs. Physical cross-zone upgrades preserve modifiers, durability and cooldown; the other family is removed. Choose Both destroys both, matching designer clarification. The Well generates Temporary spells with a retained double-cast modifier, including internal physical casting. Zin prepares upgraded copied stats before arrival notifications.

Totals: **262/308 staged runtime declarations; 46 missing across 18 categories; 877 live registered**. No live admissions. **Muradin is the only Fabled root still without a body.** Complete spell pools, duplicate behavior, damaged-copy/aura layering and interaction timing remain review gates. Feature schema stays v51. See the [Fabled checkpoint](../../docs/fabled-checkpoint.md).

Current-source validation: **3,855/3,855 full engine checks**, zero failures/errors/skips; **26/26 queue checks**; **22/22 random legal games terminal**, zero errors/caps, **2,463 feature decisions**. Includes all 23 Azshara fixtures. Source unchanged: `f002ad868c16e6eea15309bb3beb076f4265acc3d10c7e16ef8a0ab9785bfa54`. Full receipt: `runs/expanded_validation/validation-3886c8602b9848b291166559b04e6473.json`; log: `runs/expanded_validation/azshara-full.log`. Smoke receipt: `runs/random_validation/summary-f002ad868c16-4e4de4fc47b34351a4647ba59536a18e.json`. Smoke exercises admitted decks; controlled fixtures exercise staged effects. This is not full Standard certification.

## Previous Talanji/Medivh checkpoint

Talanji and Medivh now have staged bodies for both roots and their four companions. Boons persist as public owner state (feature schema v51); draw takes priority over resurrection, previously selected Boons cannot repeat, and summoned minions inherit their keywords. Medivh adds linked costs, Silence/destruction, Karazhan generation and shared spell damage/healing multipliers. Split damage multiplies the number of one-damage hits. Atiesh spell Lifesteal explicitly rejects pending reviewed semantics.

Totals: **261/308 staged runtime declarations; 47 missing across 18 categories; 877 live registered**. No live admissions. Two Fabled roots lack bodies: **Muradin and Azshara**. Complete pools, timing, control/Silence behavior and multiplier/cost interactions remain review gates. See the [Fabled checkpoint](../../docs/fabled-checkpoint.md).

Previous-source validation: **3,832/3,832 full engine checks**, zero failures/errors/skips; **26/26 queue checks**; **22/22 random legal games terminal**, zero errors/caps, **2,463 feature decisions**. Includes all 42 Talanji/Medivh fixtures. Source unchanged: `f6ec781e197325a3550b7836e552508dd118eee64e0f0b00faf6d9856fe8ca33`. Full receipt: `runs/expanded_validation/validation-b8841b361fe4452f856bbbaa585eeb76.json`; log: `runs/expanded_validation/talanji-medivh-full.log`. Smoke receipt: `runs/random_validation/summary-f6ec781e1973-c28d81e52dce4266a5a5538b7e6f76fe.json`. The first full run was deliberately interrupted to correct split-damage scaling before this clean rerun. Smoke exercises admitted decks; controlled fixtures exercise staged effects. This is not full Standard certification.

## Previous completed Azure-family checkpoint

The Sindragosa family now has staged Dragon-dependent Arcane discounts, Malygos double casting and Oathstone resurrection. Discounts react to death, Dormancy and Silence. Resurrection preserves repeated death identities and resolves separate summons. Unknown repetition overlap explicitly rejects. **Four Fabled root families lack bodies: Talanji, Muradin, Azshara and Medivh.** Totals: **259/308 staged declarations; 49 missing across 18 categories; 877 live**. No new live admissions. See the [Fabled checkpoint](../../docs/fabled-checkpoint.md) for remaining conformance gates and Talanji's designer evidence.

Previous-source validation: **3,790/3,790 full engine checks**, zero failures/errors/skips; **26/26 queue checks**; **22/22 random legal games terminal**, zero errors/caps, **2,463 feature decisions**. Includes all 17 new Azure-family fixtures. Source unchanged: `e919e2b3914ad42b0c1cd93bac177cb47092a1fd9872ec73b750c51985713029`. Full receipt: `runs/expanded_validation/validation-aead2d068c3644e1983687ec0e18317d.json`; log: `runs/expanded_validation/azure-full.log`. Smoke receipt: `runs/random_validation/summary-e919e2b3914a-4d1994c7d34a449b996bfce4904bf766.json`. Smoke exercises admitted decks; controlled fixtures exercise staged effects. This is not full Standard certification.

### Previous Gelbin checkpoint

Gelbin now has staged direct placement for all five frozen collectible Auras, both companions and valid stored Ursol Auras. Placement preserves physical modifiers and does not become a paid spell cast. Five Fabled root families still lack bodies. Overall: **258/308 staged runtime declarations; 50 missing across 19 categories; 877 live registered**. No live admissions. Hero-effect capacity, placement order, newest-expansion awakening interactions and timing remain review gates; see the [Fabled checkpoint](../../docs/fabled-checkpoint.md).

Previous-source validation: **3,773/3,773 full engine checks**, zero failures/errors/skips; **26/26 queue checks**; **22/22 random legal games terminal**, zero errors/caps, **2,463 feature decisions**. All 22 new Gelbin checks are included. Source unchanged: `6a0338afbf9801ca873a2036dde62bdb396f41a681bab09731dca18c732ce008`. Full receipt: `runs/expanded_validation/validation-cb325484473943c2a36e91ffa8206f3f.json`; log: `runs/expanded_validation/gelbin-full.log`. Smoke receipt: `runs/random_validation/summary-6a0338afbf98-d6eb82a5a8644b05ab062cb07a29c51a.json`. Smoke exercises admitted decks; focused fixtures exercise staged effects. This is not full Standard certification.

At this checkpoint, the next connected family was Sindragosa, Malygos and Azure Oathstone.

### Previous Broxigar checkpoint

Broxigar now has staged behavior for the original's opening disappearance, all four Portal/Demon pairs, the Axe's attack-kill Portal draw and one-time physical return. Copied final Portals can return the original to the opposing player; repeated final Deathrattles cannot create replacements. Multiple disappeared originals explicitly reject pending mirror-match binding evidence. Full-hand return disposal and timing remain documented review gates. The Axe snapshots attack lethality before weapon-break effects. **Six Fabled root families still lack runtime bodies.** Overall: **257/308 staged runtime declarations; 51 without declarations across 19 categories; 877 live registered**. Feature schema v50 exposes the public waiting-original count. No new live admissions; see the [Fabled checkpoint](../../docs/fabled-checkpoint.md).

Previous-source validation: **3,751/3,751 full engine checks**, zero failures/errors/skips; **26/26 completion-queue checks**; **22/22 random legal games terminal**, zero errors/caps, with **2,463 feature decisions checked**. All 25 new Broxigar checks are included. Source unchanged: `5b5f205a6a9f4b5282015743be97aab80c681ee34aebc9ae6224437b271d4a52`. Full receipt: `runs/expanded_validation/validation-8429e7d296304c95ab9a55028d470a3b.json`; log: `runs/expanded_validation/broxigar-full.log`. Smoke receipt: `runs/random_validation/summary-5b5f205a6a9f-20fe9bc60bdf458d9482c608ffb7d9b7.json`. Smoke tests exercise admitted decks; controlled focused fixtures exercise staged effects. Full Standard and independent client conformance remain incomplete.

The next connected group is Gelbin and Aura placement. The [pinned Aura inventory](../../docs/engine-audit/fabled-aura-source-inventory.json) uses the named PALADIN_AURA XML tag and retains source hashes. Tagged historical/context-specific entities are not automatically legal or implemented.

### Previous Rafaam/Garona checkpoint

Rafaam now has staged effects for the root, all nine companions and Baaaafam. Garona's staged bundle includes the original King Llane opening transfer, assassination, physical draw/reshuffle and Kingslayers' two-player Legendary draws. The existing Windrunner and Blood Fighter bodies remain connected. **Seven Fabled root families still lack runtime bodies.** Overall: **256/308 staged runtime declarations; 52 without declarations across 19 categories; 877 live registered**. Generic Constructed generation contracts reject all eleven Fabled roots. Owner-visible pending discounts are represented in feature schema v49. No new live admissions; see the [Fabled checkpoint](../../docs/fabled-checkpoint.md) and fidelity gaps for unresolved duplicate-King, opening-order, hero-destruction and integration cases.

Previous-source validation: **3,726/3,726 full engine checks**, zero failures/errors/skips; **26/26 completion-queue checks**; **22/22 random legal games terminal**, zero errors/caps, with **2,463 feature decisions checked**. The 37 new focused checks are included in the full suite. Source unchanged: `37ea4051340736057077119f8b2857de95e2170fb57da5cd4ea68bfdfcb67ce1`. Full receipt: `runs/expanded_validation/validation-370e8fc94253455ba1d18049a44bca3e.json`; log: `runs/expanded_validation/rafaam-garona-full.log`. Smoke receipt: `runs/random_validation/summary-37ea40513407-6462e11a39d649d4ba4b5ff5a845a7da.json`. The first full run exposed four legacy fixture errors in the new opening hook; they were corrected and covered before this clean full rerun. Smoke tests exercise admitted decks; controlled focused fixtures exercise staged effects. Full Standard and independent client conformance remain incomplete.

### Previous Fabled foundation checkpoint

Fabled construction now covers **all 11 frozen roots and 29 starting companions**, including idempotent expansion, slot accounting, duplicate/orphan rejection and Rafaam's 40-card size. Staged effect bodies cover the three Windrunner sisters and three Blood Fighters. Nine Fabled root families still need effects. Current totals: **254/308 staged runtime declarations; 54 without declarations across 19 categories; 877 live registered**. See the [Fabled checkpoint](../../docs/fabled-checkpoint.md). No live admissions. Companion interaction review, complete generation pools and bundle-aware deck-search mutation remain gates.

Previous-source validation: **3,689/3,689 full engine checks**, zero failures/errors/skips; **26/26 completion-queue checks**; **22/22 random legal games terminal**, zero errors/caps, with **2,463 feature decisions checked**. All 34 focused Fabled checks are included in the full count. Source unchanged: `e7ac9b528269b5e1c6729b52cb705535dba210ac5956ca0b86d913821b18e226`. Full receipt: `runs/expanded_validation/validation-280db921ab904e66a35746177e79632b.json`; log: `runs/expanded_validation/fabled-foundation-full.log`. Smoke receipt: `runs/random_validation/summary-e7ac9b528269-858e56334d0d48c6b2b38306f9b7946a.json`. Smoke exercises admitted decks; controlled focused fixtures exercise staged effects. This does not certify full Standard or independent client conformance.

### Previous stored-family checkpoint

The remaining **stored-spell and stored-card groups** now have staged bodies for all five pending collectibles: Bashana Runetotem, Cultivating Sprite, Highborne Mentor, Irida Sinseeker and Timelooper Toki. Current totals: **252/308 staged runtime declarations; 56 without declarations across 19 categories; 877 live registered**. See the [stored families checkpoint](../../docs/stored-families-checkpoint.md). No live admissions. Complete historical/generated pools, learned-target semantics and documented storage/upgrade timing assumptions remain review gates.

Previous-source validation: **3,655/3,655 full engine checks**, zero failures/errors/skips; **25/25 completion-queue checks**; **22/22 random legal games terminal**, zero errors/caps, with **2,463 feature decisions checked**. The 43 new focused fixtures are included in the full count. Source unchanged: `e92ff15ebda3c82416503c26a73581760cbfa1bdef325d3daee061757d4ce2ec`. Full receipt: `runs/expanded_validation/validation-fc0afc7b46564c6cbdf21b9606e65cd8.json`; log: `runs/expanded_validation/stored-families-full.log`. Smoke receipt: `runs/random_validation/summary-e92ff15ebda3-5d8d57782c7b4ed38d7ab3bf1e1e8b9c.json`. Smoke exercises admitted decks; controlled focused fixtures exercise the new staged bodies. This does not certify full Standard or independent client conformance.

### Previous verified checkpoint

Twelve additional collectibles have staged runtime bodies: the three timeline locations, Amirdrassil, Nespirah, Stormrook, Divergence, Alternate Reality, Godfrey, Cursed Chains, Husk and Warptooth. At that checkpoint: **247/308 staged runtime declarations; 61 without declarations across 21 categories; 877 live registered**. See the [remaining-systems checkpoint](../../docs/remaining-systems-checkpoint.md). No live admissions; complete pools, integration and independent interaction review remain required. Temporary control overlap explicitly rejects pending ordering support.

Previous-source validation: **3,612/3,612 full engine checks**, zero failures/errors/skips; **24/24 completion-queue checks**; **22/22 random legal games terminal**, zero errors/caps, with **2,463 feature decisions checked**. Full-suite source remained unchanged at `b9b247e49986888d2d193aa4a639a1a92484f727fa136ef7cf2f6f6335dfa368`. Receipt: `runs/expanded_validation/validation-5158115815a542c982a5ea1cc7f73430.json`; log: `runs/expanded_validation/remaining-systems-full.log`. Smoke receipt: `runs/random_validation/summary-b9b247e49986-34154aeb2eb6461fb05f235180f2fddb.json`. Smoke exercises admitted decks, not the new staged cards; 49 new focused fixtures exercise the staged systems. An initial full run exposed seven missing-card-identity event errors; the handler was corrected before this clean full rerun. These checks are not independent Hearthstone conformance certification.

All **15/15 Herald-family collectibles** and **11/11 Colossal bodies** have staged runtime declarations from the preceding checkpoints. The preceding Herald checkpoint passed 466 targeted engine checks and 23 queue checks at fingerprint `a251e59e5434894cc9bfc2ae99b94433fd2c9e6077929289948f5ac58abf2910`; that evidence does not cover current-source changes. See the [Herald payoff checkpoint](../../docs/herald-payoffs-checkpoint.md).

Since the 868-definition checkpoint, nine cards entered the live registry: Deathrot Maw; Bursting Leyline, Surge Needle, Leyline Nexus and Mystic Runesaber; Ysera, Emerald Aspect and Chainbreaker Hogger; Talya Earthstrider and Creature of the Sacred Cave. Metadata hashes, the implementation index and catalog audit are synchronized.

All **135/135 remaining generation/Discover cards have staged runtime declarations**. This includes the final five lifecycle exceptions: Vanessa, Beast Tripwire, Welcome Home!, Endtime Murozond and The Skeleton Key. Full generated pools and interaction review still gate admission.

All seven Leyline bodies and all six Map bodies are implemented. Three Leylines and all six Maps remain staged. Maps preserve original offered choices and physical deck identities; Leylines share persistent cost/effect/repetition upgrades. See the [checkpoint](../../docs/generation-lifecycle-leyline-checkpoint.md).

The opening-deck rules share configurable mana capacity across turn growth, temporary mana and ramp. Ysera's original-deck effect applies to both players; Hogger duplicates the other original Legendary minions before opening hands. Ramp after temporary mana cannot exceed the capacity.

Six of the original eight automatic-casting cards now have runtime bodies: Chaos Supplicant, Forbidden Shrine, Jailhouse Manastorm, Tricksy Improviser, Faceless Enigma and Creature of the Sacred Cave. Forbidden Shrine's earlier recipe is corrected to location activation. Internal casts share target/choice/Overload handling without becoming paid hand plays. Manastorm is persistent public owner state. Creature of the Sacred Cave is now live; five bodies remain staged, with Fyrakk and Gelbin still explicit exceptions. See the [automatic-casting checkpoint](../../docs/automatic-casting-checkpoint.md).

## Persistent future summons

All eight Animal Companion/Void Soul family cards now have runtime bodies. **Talya is live; seven sources remain staged.** The four existing Companion consumers use three persistent owner-private replacement slots and a shared extra-summon counter. Bonus summons apply once per originating effect, including choices and triggered summons. Void Souls share an owner level across existing and generated copies; weapon, Deathrattle and damage-kill rewards are connected. Full Beast/Demon outcome closure, maximum-cost behavior and independent timing/visibility review still gate the staged sources.

Creature of the Sacred Cave is admitted after verifying that every live Holy spell supports internal casting. The [future-summons checkpoint](../../docs/future-summons-checkpoint.md) records the behavior, evidence and remaining caveats. Schema v43 exposes public counters and owner-only Companion identities; the feature encoder explicitly ignores opponent identities.

## Earlier implementation checkpoints

The following counts and receipts describe historical stages, not current remaining work. Current totals are above.

### Colossal entry infrastructure

Ten Colossal bodies now share explicit appendage entry for summons, copied summons and board transformations. The helper checks all dependencies before mutation, respects board space, creates fresh parent links and captures appendage notifications before the parent. Twenty-one focused checks pass. This is entry-only work: body/limb abilities and independent timing review remain incomplete, so no cards are admitted and the 877/308 count is unchanged. Magmaw replenishment and dormant/silenced-copy entry explicitly fail closed. See the [checkpoint](../../docs/colossal-entry-checkpoint.md).

The full-suite and smoke receipts below validate the subsequent Herald checkpoint, including this entry infrastructure. The newer Colossal body checkpoint now owns the latest receipts. The subsequent Herald checkpoint connects specialized copied replacements such as `entity_tribute`; independent entry ordering review remains required.

### Herald army implementations

Thirteen of fifteen pending Herald source cards now have staged runtime declarations, bringing the total to 222 of 308 staged collectibles with runtime declarations (86 without). Six army ability families cover eighteen Soldier/appendage identities through shared owner progression, per-entity snapshots, generation contracts, Deathrattles and auras. Shrine of Twilight activates rather than firing on placement. Ultraxion, Deathwing, off-class routing and Cho'gall replacement remain explicit gaps. Independent timing/pool review still gates every source; live counts remain 877/308. See the [Herald checkpoint](../../docs/herald-armies-checkpoint.md).

Forty-two Herald checks, twenty-one Colossal entry checks, twenty-six feature checks and twenty-two queue checks pass. Schema v44 exposes public progression and hero Lifesteal while excluding internal Colossal link IDs from features. Copied Colossal replacements are now connected. Full-suite and smoke validation completed successfully; the receipts below have since been superseded by the Colossal body checkpoint.

### Colossal body implementations

Ragnaros, Azshara, Al'Akir and Vulcanos now have staged body implementations, including Vulcanos's two Plume triggers. They share the entry, army, effect replay and generation systems; 28 focused checks pass. Staged runtime declarations are now **226/308**, with **82** still missing. No live admission: **877/308** remains unchanged. See the [body checkpoint](../../docs/colossal-bodies-checkpoint.md).

Full-suite and smoke validation passed; the receipts below cover this Colossal body checkpoint. Seven Colossal body families, Ultraxion and Deathwing remain unimplemented, alongside independent ordering and pool review.

### Colossal healing and repetition

Sinestra and The Black Blood now have staged body implementations, including all three Black Blood appendages. Shared spell repetition and credited healing/forced-attack hooks bring Colossal declarations to **6/11** and total staged runtime declarations to **228/308**, leaving **80** without declarations. Multiple Sinestras and overlapping repetition providers explicitly fail closed pending stacking review. No cards admitted: **877 live / 308 staged**. Fifty focused Colossal body checks pass. See the [reactive checkpoint](../../docs/colossal-reactive-checkpoint.md).

Full-suite and smoke validation completed successfully; the receipts below cover this reactive Colossal checkpoint.

## Previous full-suite verification (Colossal source)

**3,537/3,537 full-suite tests passed**, zero failures/errors/skips. Source remained unchanged: `defff313b91fc096bcb22f334f566db3f6add7e92d3589df0174526971a293bf`.

- Full receipt: `runs/expanded_validation/validation-41529aab624c451a919ec0f0a17a9bbc.json`.
- Full log: `runs/expanded_validation/colossal-complete-full.log`.
- **22/22 smoke games terminal**, zero errors/caps; 2,463 feature decisions checked with schema v45 and the same fingerprint.
- Smoke receipt: `runs/random_validation/summary-defff313b91f-869cec8c08c94c7cad1eb7d6bf399387.json`.
- Focused groups: 97 Colossal body checks, 21 Colossal entry checks, 27 feature checks. Separately, 23 completion-queue checks passed.

The first full run was interrupted after outdated v44 schema assertions failed; those expectations were corrected before the successful full rerun. Smoke games exercise live registered decks, not staged Colossals; staged body fixtures explicitly install those definitions. Passing tests does not establish independent client conformance, full Standard support, or optimal play. Prior checkpoints remain in `runs/expanded_validation`.

## Continue here

The [all-card completion queue](../../docs/engine-audit/completion-queue.md) accounts for all 308 pending collectibles. **79 cards have unresolved selector/dependency mappings or explicit exceptional behavior**; dynamic transformation dependencies are now visible. Missing graph edges never prove pool closure. The queue records two candidate dependency cycles, including one of 166 cards, for coordinated review/admission; these are planning candidates, not approved generation pools.

All eleven Colossal bodies and their printed appendage abilities now have staged runtime code. The next work is verification and integration: generated-pool closure, independent Colossal entry/notification order, Wickerfang/Chromatus scope, Magmaw queue timing, Onyxia damage replacement and prior Sinestra stacking. The [completion checkpoint](../../docs/colossal-completion-checkpoint.md) and `expanded/fidelity_gaps.json` distinguish implemented candidate behavior from verified behavior. Ultraxion and Deathwing now have staged bodies too; independent payoff semantics remain documented verification gates.

Other remaining work includes Fabled construction, exceptional transformations/Rewind, stored effects, persistent/replacement rules, generated outcome closure, independent event-order validation, feature coverage, training and deck-search gates. The [full roadmap](../../docs/ROADMAP.md) and `expanded/fidelity_gaps.json` retain those obligations.

The saved overarching goal was inspected October 5 and remains **usageLimited**, not complete. Automatic continuation must not be promised while that limit remains. Existing authorization permits local development/validation, but not unbudgeted training.
