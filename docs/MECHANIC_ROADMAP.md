# Mechanic delivery roadmap

Updated October 5, 2026. **868 live registrations; 317 staged recipes; zero collectibles without a top-level recipe.** Runtime support remains incomplete. The [all-card completion queue](engine-audit/completion-queue.md) supersedes historical counts and delivery constraints below. Scope remains frozen regular Standard patch 36.6.0.251952, all 11 classes; live legality is separate.

The following dated checkpoints preserve implementation history. Their counts describe those checkpoints, not current coverage.

## Delivery agreement

Updated October 2, 2026 at the user's request: **the target is all 1,185 cards and the full simulator objective, with no 60-card delivery cap**. Work through shared mechanic groups continuously; checkpoints record evidence, not a smaller definition of done. Count a card only when its effects and required dependencies are connected with meaningful regression coverage. Tokens, scaffolding and blocked cards do not count. Preserve the historical batch reports below as history. Run consolidated local validation without requesting Jupyter runs after each group. Do not launch long training or deck search without a run budget.

## Ordered workstreams

The sequence favors foundations and reuse rather than raw group size. Each row groups shared mechanics needed for full coverage. The table is the October 1 historical assignment: counts are disjoint and sum to 376; the original October 1 inventory remains a historical snapshot. A mechanic can additionally help cards counted elsewhere.

| Order | Workstream | Remaining primary cards | Mechanic breakdown |
| --- | --- | ---: | --- |
| 1 | Physical card state | 6 | Temporary/attached cards blocked by other families (4); Mostly existing mechanics (2) |
| 2 | Type selection and choices | 21 | Discover history and delayed rewards (5); Bounded state/choice extensions (16) |
| 3 | Combat, modifiers and payment | 21 | Forced attacks and combat interruption (10); Damage, healing, costs and temporary control (8); Health/Corpse payment with generation dependencies (3) |
| 4 | Nested resolution | 21 | Casting/replaying cards inside effects (18); Casts/Summons When Drawn (2); Recorded Deathrattle replay with generation dependency (1) |
| 5 | Prepare, Imbue and Dark Gifts | 44 | Prepare with additional dependencies (6); Imbue and upgraded hero powers (19); Dark Gifts (19) |
| 6 | Herald and Colossal | 27 | Herald and Deathwing upgrades (15); Colossal and appendages (12) |
| 7 | Persistent upgrades and remaining related cards | 18 | Leyline scaling and persistent upgrades (7); Void Soul generation and upgrades (4); Animal Companion replacement and count (4); Dormant and awakening (3) |
| 8 | Quests, setup and hero changes | 28 | Quests and rewards (8); Setup, deckbuilding and hero replacement (20) |
| 9 | Rewind, Shatter and special rules | 63 | Rewind and alternate outcomes (17); Shatter and Advance (10); Custom or unusual persistent systems (34); Noncombat simulation scope decisions (2) |
| 10 | Generated-card dependency closure | 127 | Global generation/Discover pool dependencies (127) |
| | **Total** | **376** | |

**Completed:** physical card origin and hand-entry tracking, with all 10 directly assigned cards connected. See [delivery report](provenance-714.md).

**Completed:** held upgrades/timers, with all seven directly assigned cards and the Emerald Whelp token connected. See [delivery report](held-upgrades-721.md).

**Delivered:** Temporary expiry/discounts and the ready Follow attachment rules, connecting four cards. Six cards remain blocked by generation, Quests or drawn-card resolution; see [delivery and blockers](temporary-725.md).

**Delivered:** [60-card batch, 725 → 785](batch-785.md), including shared Prepare, drawn-card resolution, forced combat, payments, either-side placement and type groups. Five Temporary-family cards remain blocked; Follow the Evidence is now connected.

**Current target: full coverage of all 1,185 cards and the complete simulator objective.** Continue across the ordered families. The former 785 → 845 batch is historical tracking, not a stopping condition.

**Run generation dependency work alongside every stage.** The 127 generation-first cards are not 127 easy definitions or a single shared mechanic. Enumerate their exact pools, map missing results, prioritize reusable missing effects, and connect the generators as their entire pools become executable. Some families in other rows also have generation dependencies.

## What each workstream must deliver

### 1. Physical card state

Track each physical card through hand, deck, copies and transfers; add held timers, expiry and attached effects. Origin/hand-entry tracking and the timer/held-state family are implemented; extend them for temporary cards and attached effects.

Foundation for Prepare, temporary cards, delayed rewards, copied cards and correct generated-card handling.

### 2. Type selection and choices

Complete multi-type selectors; distinguish Discover from ordinary choices; record Discover history and delayed rewards. Split the 22 bounded special cases by the actual selector, choice or state helper they need.

Uses physical identity for follow-up rewards. Global Discover variants remain pending until every eligible result is implemented.

### 3. Combat, modifiers and payment

Build resumable forced attacks and pre-combat interruption; implement damage/healing replacements, alternate payments and actions that play onto either board as separate mechanic deliveries.

Forced attacks need owner-correct events, target revalidation, retaliation, kill attribution, and death/choice checkpoints. Payment and either-board actions also change legality and observations.

### 4. Nested resolution

Support a card casting/replaying another card; resume nested choices safely; finish casts/summons-when-drawn and captured Deathrattle replay.

Depends on explicit continuation frames and physical identity. Preserve counters, targets, ownership, burn rules, replacement draws and interruption.

### 5. Prepare, Imbue and Dark Gifts

Deliver each named mechanic separately, with its full progress/action model and all fixed rewards or effect options.

Uses physical state, payment/actions and nested resolution where needed. Generated rewards still require exact pool closure.

### 6. Herald and Colossal

Implement Herald progress and inherited upgrades, then appendage placement/lifecycle and each Colossal component behavior.

Uses forced combat and nested effects. Herald Soldier random generation prevents declaring the family finished before those dependencies work.

### 7. Persistent upgrades and remaining related cards

Deliver Leylines, Void Souls and Animal Companion replacements as three shared upgrade families. Complete the three Dormant-related follow-ups under their real dependencies.

Some generators require large complete pools. Iso’rath needs private hand captivity/return; Flutterwing needs the full eligible 2-Cost pool; Tranquil Clearing sleep must be researched separately from Dormant.

### 8. Quests, setup and hero changes

Build quest slots/progress/rewards and exceptional deck/setup/hero replacement rules; connect all affected cards.

Rewards may depend on earlier mechanics, exact generation pools and special systems. Revalidate deck legality, runes, starting state, hero powers and model actions.

### 9. Rewind, Shatter and special rules

Deliver Rewind rollback/RNG semantics, Shatter/Advance card identity, then split 36 unusual cards by concrete custom systems. Resolve the two noncombat cases explicitly.

Rewind requires reliable nested resolution and hidden-information rules. Unique is a planning bucket, not one reusable mechanic. Do not label timer/emote effects implemented by silently omitting them.

### 10. Generated-card dependency closure

Inventory exact eligible pools and nested dependencies from the start; connect these 127 cards continuously as dependencies become executable.

This is a parallel track and final closure gate, not a last-minute 127-card batch. Never substitute a pool restricted to currently supported cards.

## Completion gate for every mechanic

1. Record the pinned rules, ownership/timing behavior, fixed tokens and generated dependencies. Resolve material rule ambiguities or state the blocker explicitly.
2. Implement the reusable state/actions/events and attach all affected card definitions with complete dependencies.
3. Test normal behavior, boundary cases, interactions, choices/resumption, copying/transfers and public/private observations as relevant.
4. Pass the integrated regression suite; run targeted random-game checks when engine/action/state changes warrant them. Preserve source-matched receipts.
5. Update the inventory with completed IDs, still-blocked IDs and reasons. Report mechanic progress separately from independent game-fidelity verification.

## Work beyond the 481 missing definitions

The current engine also records **31 known fidelity-gap entries** covering implemented behavior. That count is a checklist inventory, not 31 equally sized tasks or a claim that every unknown is listed. Repair related existing behavior while building each mechanic, then independently compare reference outcomes. Passing internal tests does not certify Hearthstone correctness.

After coverage and fidelity gates: reconcile the desired live Standard patch and exceptional deck legality; integrate the candidate into the Jupyter workflow; establish throughput and reproducible short runs; train a self-play policy and evaluate against multiple opponents; run paired deck search with uncertainty estimates; finish GitHub reproduction instructions. A finite search can identify the strongest decks and policies found under the tested conditions, not prove a universal best deck.

## Audit trail

- [Every remaining card, grouped](engine-audit/remaining-2026-10-01/cards.md)
- [Machine-readable workstreams and card assignments](engine-audit/remaining-2026-10-01/classification.json)
- [Current candidate status](../staging/rebased-88/STATUS.md)
- [Original September 30 classification](engine-audit/remaining-2026-09-30/README.md) remains historical.
- The former [60-card queue](card-batch-60-741-in-progress.md) is superseded as a delivery contract; its 23 integrated cards remain implemented.

This planning update does not change simulator code, add card support, run tests or launch training.

## In-progress generation checkpoint

[Shared generation machinery and 60 staged declarations](generation-60-checkpoint.md) are written and remain outside playable coverage. This is not the next completed batch: that checkpoint kept coverage at 785; subsequent Discover work brings it to 786, and the delivery target stays 845. The candidate dependency report now ranks blockers across these generators.

## Discover state — internal batch progress

Discover completion counters now cover the existing deck/hand/resurrection choices and staged generated choices, excluding Dredge and ordinary choices. Storage Scuffle (`TLC_365`) is connected: **786 supported, 399 remaining**. This is **1 / 60** additions toward the 785 → 845 delivery. See [Discover checkpoint](discover-history-checkpoint.md). The full batch remains unfinished; no new Jupyter run is requested.

## Discover follow-ups — internal batch progress

Physical Discover results and deferred discounts connect Vault Breaker (`TLC_483`), bringing coverage to **787 / 1185**. Cursed Catacombs no longer emits draw triggers from its Discover selection. See [follow-up checkpoint](discover-followups-checkpoint.md). Progress toward the 60-card delivery is **2 / 60**, with 58 additions still needed. Independent after-Discover timing traces remain a documented fidelity gap.

## Replacement and secondary Hero Powers — internal batch progress

Shared power identity, reversible state, separate usage and Corpse payment connect **Lord Jaraxxus, Soul Immolation, Story of Sulfuras, and Blood Doctor Thal’ena**. Coverage is now **791 / 1185**, with **394 remaining**. The 60-card delivery is **6 / 60** connected; **54 additions remain**. See [Hero Power checkpoint](hero-powers-checkpoint.md). Remaining interaction uncertainties are recorded explicitly, not treated as independently certified.

[Quest infrastructure checkpoint](quest-checkpoint.md): Restore the Wild, Reanimate the Terror and Questing Assistant bring written coverage to **794**, with **391 remaining**. Shared Corpse payment and location Deathrattle hooks include their reward dependencies. This is **9 / 60**, with **51 more** needed for the current delivery; continue other shared groups without requesting a Jupyter run.

[Closed Dream reward pools](dreams-checkpoint.md) connect Hopeful Dryad and Shaladrassil with all ten ordinary/corrupted rewards. Written coverage is **796**, with **389 remaining**. Batch progress is **11 / 60**, with **49 additions** outstanding. Hero Elusive and copyable caster-turn destruction timers are shared foundations, not independent collectible additions.

[Untouchable permanent objects and Underfel Rift](permanents-checkpoint.md) connect Escape the Underfel and its fixed rewards, bringing coverage to **797**, with **388 remaining**. This is **12 / 60**, leaving **48 additions** for the current batch. Full-board activation and other reference-timing gaps remain explicit.

[Rogue Quest and resumable Hero Powers](dusk-checkpoint.md) connect Lie in Wait and Master Dusk with ordered filtered draws and a player-bound Ninja return listener: **798 written**, **387 remaining**, **13/60** in the current delivery. **47 additions remain**; this is not a batch handoff.

[Repeatable summon Quests and recruited combat](summon-quests-checkpoint.md) connect Dive the Golakka Depths and High Cultist Herenn: **800 written**, **376 remaining**, **15/60** in the current batch; **45 additions remain**.

## Imbue workstream in progress (October 2)

Shared state now records Imbue history for all eleven classes and maps eight pinned Hero Powers (Druid, Hunter, Mage, Paladin, Priest, Shaman, Rogue, Death Knight). Three classes have no Imbued power in this snapshot. The eight generated identities are reviewed; this is not completion of their effects or the 19 pending collectibles.

Continue the family as one workstream: implement Druid scaling summons, Hunter physical hand buffs/discounts, Mage resumable summons/missiles and triggered-use handling; then Shaman targeted evolution, Paladin portal generation/draw triggers, Priest playable choices with temporary discounts, Rogue generation/Rewind, and Death Knight first-Undead passive timing. Close all full pools, Hamuul setup, Wild God choices and the remaining consumers. Never narrow pools to implemented cards. Original activation versus upgrade refresh, hero swaps, dynamic base values and event attribution need evidence.

Sources: [official Imbue overview](https://hearthstone.blizzard.com/en-us/news/24189539/into-the-emerald-dream-is-now-live), [official class scope](https://news.blizzard.com/en-us/article/24179067/step-into-the-emerald-dream-hearthstones-next-expansion). These establish the shared mechanic, not every current power's detailed interactions. Pinned token JSON has split dynamic text; missing numeric fields must be verified before effect implementation.

Validation: 229 related tests passed in 13.900 seconds, zero failures/errors. Includes 10 new state tests covering eight power identities, three non-Imbued classes, ownership, replacement/upgrade persistence, secondary powers, invalid input, public feature encoding, explicit unsupported activation rollback and passive-power legality. Feature schema v30. This targeted run is not the full suite, and no new collectible coverage is claimed.


### Imbue power-body checkpoint

The target remains all 1,185 frozen Standard collectibles, without a batch-size completion limit. Exact build 251952 XML values are saved with source revision and hash in `expanded/imbue_values.json`. Candidate Druid, Hunter and Mage power bodies now resolve through shared power/summon machinery. 238 related tests pass, including 19 Imbue checks; this is targeted validation, not a new full-suite receipt. Five remaining bodies and all 19 collectible consumers remain open, with runtime uncertainties recorded in `expanded/fidelity_gaps.json`. Coverage remains 814 written / 371 missing.

### Targeted Imbue powers and consolidated validation

Shaman replacement powers now carry an explicit friendly minion target through normal activation and resumable effect context. Their transformation uses complete generation contracts and raises with state/RNG rollback when the required contract is missing; it never filters to supported outcomes. Druid, Hunter and Mage bodies plus shared progress are also included in this checkpoint. Four power bodies, Shaman production pools and all 19 collectible consumers remain unfinished.

The [pool planning inventory](engine-audit/imbue-pool-planning.json) enumerates frozen metadata candidates and missing definitions; membership still requires review. All-card scope is unchanged. **2598 full tests pass; 22 random games finish without errors/caps**, fingerprint `5d2c697ad0142140b81fa4573c307b7cae2796c98f0235d0aeec90f7f9843bdf`. Receipts `runs/expanded_validation/validation-a9d3c04a459745439bf648f6560534cb.json` and `runs/random_validation/summary-5d2c697ad014-79ed093bec084efdb35e52114a8b2a79.json`. Written coverage remains 814/1185, with 371 missing and separate fidelity gaps. No learning run was launched.


### Definition-first priority (user-directed)

Complete explicit recipes for every remaining collectible before returning to broad runtime interaction cleanup. New `expanded/pending_definitions.py` stages ordered operation trees outside playable registration. Current inventory: 814 live definitions, 163 staged definitions (60 already existed; 103 newly covered), and 208 without any recipe. Families include generation, Discover, Imbue, Dark Gifts, Rewind, Herald and Shatter. The [exact remaining inventory](engine-audit/pending-definitions.json) distinguishes recipe coverage from execution readiness. No runtime text parser, empty rule fallback, or promotion of incomplete cards was added. Full objective still requires all recipes to be integrated and independently validated before full-pool training.


### Second definition-first checkpoint

Added 99 explicit recipes. Totals: **814 live + 262 staged = 1,076 defined; 109 still without definitions**. The added families cover conditional/random generation, transformations, automatic casting/play, Maps, Animal Companions, Leylines and Void Souls. Runtime integration, special token identities, exact dynamic values and complete generation eligibility remain unresolved where indicated by operation arguments. No staged recipe was promoted into playable support.

Reproduce the catalog-membership, live-registration separation, mandatory rejection and source-hash inventory audit with `tools/audit_pending_definitions.py --engine-root staging/rebased-88` from the lab directory. This audit checks definitions and boundaries; it does not test card behavior.


### Top-level recipe inventory complete

Added the final 109 top-level recipes. Every frozen collectible now has either a live definition (814) or a staged top-level recipe (371). No collectible identity is absent from that inventory. **This is not completion of executable card definitions or the simulator.** Staged recipes explicitly retain unresolved symbolic operations, dependency identities, custom choice contents, dynamic values and runtime semantics; all are non-executable.

The definition-first inventory milestone is complete at the top-level sequence layer. Next resolve shared contracts, expand generated dependencies and choices, then integrate complete mechanic families. The all-card simulator and ML objective remains active. Structural audit passed for all 371 staged records; the prior 2,598-test full run predates these additions. No new behavioral pass is claimed.


### Generation integration: executable bodies and pool blockers

Six further recipes now use engine operations in `expanded/generation_extensions.py`. Temporary generation connects to the existing hand expiry system; Dethrone's Combo continuation uses shared scheduling. Nine new extension checks and the existing generation checks pass (68 total). Tests use synthetic pool contracts and do not authorize live registration.

All 60 original staged generators have missing eligible outcome definitions in the frozen metadata audit; see [exact pool blockers](engine-audit/generation-integration-blockers.json). Close these dependencies before enabling the generators. No cards were enabled in this checkpoint; live coverage remains 814. This supersedes any implication that the 104 generation recipes can all be enabled independently of the remaining mechanics.


### Live Secret integration

Promoted Explosive Runes and Mystic Misdirection from staged recipes to provisional live definitions, including reviewed Sheep metadata, played-source identity forwarding and explicit targeting/cancellation behavior. **816 live / 369 staged**. All collectible identities still have top-level recipes. **138 related tests passed** (Secrets, summon sequencing, forced combat, combat, generation), including eight new checks. Full-suite receipts from earlier checkpoints do not cover this revision. Transformation and patch-sensitive excess damage need independent client evidence; these gaps are recorded.


### Untimely Death and remaining infinite-damage Secret

Untimely Death now uses exact Secret identity and death snapshots in the resumable death queue. Focused coverage includes the immediately following turn, actual play versus summon, own-turn exclusion, clean resummons, simultaneous deaths and Reborn. **80 related tests passed. 817 live definitions / 368 staged recipes.** Independent client ordering and transformed-play association remain open, so this is provisional.

Flames of Infinity remains staged. A [firsthand Fire-immunity interaction report](https://us.forums.blizzard.com/en/hearthstone/t/flames-of-infinity-not-working-correctly-on-portal-summons/158480) shows why unconditional destruction is not an adequate implementation. Infinite damage representation, immunity and event attribution must be addressed before promotion.


### User-requested fixed batches of 60

The active batch is recorded in [the batch ledger](engine-audit/active-integration-batch.json), with exact identities and an 817-card live baseline. Do not replace its membership or count recipes/shared infrastructure as integrated cards. All 60 must satisfy the documented gates before reporting this batch complete.

Generated summon groups now retain physical UIDs and resolve their attacks through existing forced-combat checkpoints. Ankylodon's body is written but its production pool/integration remain open. Seven focused new checks plus related regression checks pass (114 total). Batch remains in progress with zero promotions so far.


### Fixed batch continuation: dynamic generation

Nine additional batch recipes now use executable engine operations (Commissary Crook, Astromancer, Ulfar, Corpse Farm, Story of Umbra, Ysondre, Bygone Echoes, Triennium Rex, Eternal Toil). Together with earlier bodies the fixed batch has **50/60 bodies written; 0/60 promoted**. Full eligible pools and integration are separate gates. Seventeen new dynamic-generation tests cover resource validation/spending, hand size, death identity, corpse/Outcast branches, recorded death counts and live Deathrattle checks. **131 related checks passed**. Live count remains 817 and no batch completion is claimed.
