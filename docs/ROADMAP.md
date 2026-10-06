# Full Standard simulator and learning roadmap

## Historical rewards: consolidated validation passed

**4,119/4,119 engine fixtures passed**, zero failures/errors/skips; unchanged source fingerprint `cb9ab75a52d2306c8a88f241e05e00e290f78eb76397e861d449643a4195efa6`. Receipt: `runs/expanded_validation/validation-c2563e4e121a4a898590b13fc4e15345.json`; saved log: `runs/expanded_validation/latorvius-full.log`. **27/27 dependency checks** and **22/22 terminal smoke games**, zero errors/caps, also passed on this checkpoint. Smoke receipt: `runs/random_validation/summary-cb9ab75a52d2-e3a1123fa8e34155bee22fd842cbcc5d.json`. Sessions 83139, 81634 and 85903 are complete; no validation/training is running.

This validates internal fixtures for the automatic-card fixes, extra turns, nine staged historical reward bodies, reward distribution and schema v57. It does not certify full Standard/client fidelity. **877 live; 308 staged; 270 staged collectible bodies; 38 missing.** Exact Enter the Lost City progress timing, production generation-pool closure and documented historical reward interactions remain unresolved. Shared Infinity family research is saved in `../../docs/engine-audit/infinity-family-contract.json`; no Infinity body has been counted. Earlier sections are historical checkpoints.


Scope: regular Hearthstone Standard, all 11 classes. No Mercenaries or Battlegrounds. Keep the frozen catalog and patch consistent; live legality remains separately reviewable. Authorization updated 2026-09-22: the assistant may inspect and run local validation checks as needed. Long training runs still require an explicit run budget. Assistant may inspect data/source and generate static inventories.

## Baseline

Version 0.14 remains the active notebook engine with 291 collectible implementations. The isolated candidate is `staging/rebased-88`; its [derived status](../staging/rebased-88/STATUS.md) records current implementation counts, remaining additions and the verified suite fingerprint. The full frozen catalog contains 1,185 collectible cards. Passing scenario checks does not certify complete Hearthstone correctness. Preserve the original overlay for provenance; do not install it directly.

## Delivery agreement

User preference updated October 5, 2026: minimizing Codex token spending is no longer a project constraint. Prioritize completing the simulator correctly and efficiently; do not reduce scope or stop at smaller milestones merely to conserve tokens. Platform-enforced usage limits remain separate. The existing requirement for a specified budget before long local training runs remains unchanged.

Updated October 5, 2026 at the user's request: **complete all 1,185 frozen Standard collectibles and the full simulator objective, with no 60-card delivery cap**. Work continuously through shared mechanic groups. Checkpoints record progress and verification; they do not redefine completion. Count a card only when its effects and required dependencies are connected with meaningful regression coverage. Generated tokens, scaffolding and blocked cards do not count. Run consolidated local validation without requiring Jupyter runs after every mechanic. Long training and deck search still require a run budget.

The [all-card completion queue](engine-audit/completion-queue.md) is the current dependency-based work order: **877 live registrations and 308 staged recipes**, with generated dependencies tracked separately. Every collectible has a top-level recipe, but staged recipes are not playable support. See the candidate status for validation evidence and fidelity gaps. The [mechanic roadmap](MECHANIC_ROADMAP.md) and older batch reports retain historical context; their earlier counts and batch limits are superseded.

## Current runtime checkpoints

The [Fabled checkpoint](fabled-checkpoint.md) covers frozen bundle construction and staged runtime bodies for all eleven roots and their starting companion effects. Overall staged declarations are **263/308**, leaving **45 missing across 17 categories**; live coverage remains **877/1185**. Muradin adds physical held-weapon movement and Avatar Form character triggers. Full generated pools, interaction fidelity, independent attachment evidence and bundle-aware deck search still gate completion. The preceding Muradin checkpoint validation: **3,900 full engine checks, 26 queue checks, 22 terminal random legal games and 2,463 feature decisions**. The 39 Muradin checks and six weapon-identity checks are included. These are not full Standard certification; matching receipts are in candidate STATUS.md.

The Quest-and-reward workstream now has Reach Equilibrium connected in staging (31 family fixtures); seven root families remain. Overall runtime declarations are 264/308, leaving 44 missing bodies and 877 live cards. Feature schema v53 exposes compound progress. The combined full validation is running; see candidate STATUS.md for live handles. The shared objective tracker is implemented and used by existing capped Quest counters. The inherited full-hand reward-burning bug is corrected: rewards wait for space. There are now 83 focused Quest checks passing; full regression is in progress (see candidate STATUS.md). Ordered and parallel objectives are tested but still need engine event adapters and reward integration. This does not reduce the 45 missing-body count. The [pinned source inventory](engine-audit/quest-source-inventory.json) preserves 58 root, reward and candidate dependency records, including the updated UnGoro rewards; prefix relationships remain candidates. Required shared work: multi-objective and sequential progress; minion-type/Attack snapshots, actual damage and Discover events; persistent reward effects; generated reward closure; and automatic play of unchosen Discover options. Count a root complete only when its reward works too. Origin Stone overlaps the automatic-play workstream, Ashalon with retained Adaptations, Latorvius with historical generation, Sol'etos with hand combination, and Storm the Gates with custom Zombeast construction.

The October 5 work includes all 135 remaining generation/Discover runtime declarations, six Map declarations, all seven Leyline bodies (four now live), and six of eight automatic-casting bodies. The start-of-game mana-capacity and legendary-duplication rules admit Ysera and Hogger. Deathrot Maw uses the already implemented Fel Beast family. See the [generation/Leyline/Map checkpoint](generation-lifecycle-leyline-checkpoint.md) and [automatic-casting checkpoint](automatic-casting-checkpoint.md). Candidate STATUS.md records validation against the actual source fingerprint.

Earlier staged groups remain: [12 Dark Gift generators](dark-gift-generators-checkpoint.md), [13 transformation declarations](remaining-systems-checkpoint.md), [11 Rewind declarations](rewind-generators-checkpoint.md), and [19 Imbue consumers](imbue-consumers-checkpoint.md), including the [remaining power bodies](imbue-power-bodies-checkpoint.md). Complete outcome pools, generated identities and interaction review gate live admission. Genn, Morchie, Fyrakk and Gelbin retain explicit exceptional requirements. Divergence and Alternate Reality now have staged bodies with interaction and historical-pool review gates. The queue now includes dynamic transformation cost dependencies instead of making those cards appear dependency-free.

Herald and Colossal now have all fifteen and eleven collectible runtime declarations respectively; this is staged progress, not live admission. Their remaining work is pool closure and interaction verification. The [pinned source inventory](engine-audit/herald-colossal-source-inventory.json) now preserves the 26 collectible records and 43 candidate relatives, including numeric enum IDs from the verified XML. Prefix relationships are candidates, not certified dependency mappings. Review the six class armies, their exact tokens, Herald upgrade timing and off-class behavior, generation restrictions tied to starting decks, appendage placement, and Deathwing choices together. Primary expansion documentation establishes the broad mechanic but does not settle those interaction details. Do not guess unnamed numeric metadata tags or admit a partial army as full card support.

The [future-summons checkpoint](future-summons-checkpoint.md) adds all eight Animal Companion/Void Soul bodies and routes existing Companion consumers through persistent upgrades. Talya and Creature of the Sacred Cave are live; seven new bodies remain staged for outcome closure and boundary/timing review. Live coverage is 877, with 308 staged recipes. See candidate STATUS.md for the matching verification receipt.

## Remaining-card classification

The [October 1 inventory](engine-audit/remaining-2026-10-01/cards.md) is a historical snapshot at 704 implementations. It assigns each of the then-481 remaining collectibles to exactly one primary family and one ordered workstream. Counts describe the remaining inventory, not immediate unlock promises: cross-dependencies may keep a card pending after its main shared mechanic is built. Generation dependency analysis runs alongside every stage.

The [September 30 inventory](engine-audit/remaining-2026-09-30/README.md) remains a historical snapshot at 666 implementations. The October 1 snapshot recorded 2 local candidates, 127 generation-first cards, 180 shared-rule extensions, and 172 larger-system/unusual/scope cases. Since then the 10 origin/hand-entry cards seven held-upgrade cards, and four Temporary/Follow cards were connected; see the historical [Temporary delivery](temporary-725.md) and historical [60-card delivery](batch-785.md). Follow the Evidence is now connected; five Temporary-family cards remain blocked. Existing implemented behavior also has independent-validation gaps, which are tracked separately from missing-card coverage.

## Milestones and release gates

| Milestone | Deliverable | Exit gate |
| --- | --- | --- |
| 1. Requirements and inventory | Every catalog ID accounted for; source-backed mechanics specifications; explicit missing information | Every card has reviewed requirements and generated dependencies, or is explicitly blocked with a reason. A static inventory alone does not complete this gate. |
| 2. Shared engine | Resumable phases, modifiers, selectors, zones, combat, resources and card-type lifecycles | Representative interactions, failure rollback and hidden-information checks prepared; user-run results reviewed; no known silent approximations in claimed features |
| 3. Card coverage | Composed effects and explicit exceptional definitions for all catalog cards and required generated content | No missing card behavior or dependency in the pinned full-Standard pool; staged work integrated and checked |
| 4. Independent validation | Reviewed reference outcomes, deterministic replays, randomized legal-game stress harness | Blocking discrepancies resolved; reference provenance retained; throughput measured locally |
| 5. Learning player | Full action/observation interface, legal action masking, self-play training, checkpoints | Local training resumes reliably; held-out evaluation demonstrates improvement against baselines and older checkpoints |
| 6. Deck search | Legal random initialization, mutation, paired evaluation and alternating policy/deck improvement | Candidate rankings evaluated with multiple seeds, both starting positions and uncertainty estimates |
| 7. Reproducible project | GitHub-ready documentation, dependency/license records, experiment configs and reports | A fresh local setup can reproduce a short demonstration; results state patch, budget and opponent mix |

Milestones overlap where independent work is useful, but a later milestone cannot certify an earlier unfinished dependency. Do not promise a delivery date before measuring remaining requirement families and local runtime throughput.

The [Colossal entry checkpoint](colossal-entry-checkpoint.md) adds shared summon/copy/transform entry for ten explicit layouts. It grants no completed-card credit; body abilities, appendage abilities, Herald and Magmaw remain required.

The [Herald armies checkpoint](herald-armies-checkpoint.md) adds thirteen staged source bodies and six shared Soldier/appendage ability families. These remain gated by timing, pool and off-class review; Ultraxion, Deathwing and Colossal body exceptions remain.

The [Colossal bodies checkpoint](colossal-bodies-checkpoint.md) composes Ragnaros, Azshara, Al'Akir and Vulcanos with existing shared systems. Total staged runtime declarations: 226/308; no admissions.

The [reactive Colossal checkpoint](colossal-reactive-checkpoint.md) adds Sinestra and The Black Blood using shared spell repetition and healing-triggered forced combat. Six Colossal bodies have staged runtime declarations; total 228/308, with no new admissions.

## Consolidated shared-engine block

Implement in dependency order, with a single integrated user-run release after the selected scope is complete:

1. **Resolution state:** explicit persistent frames for turns, combat, death waves, trigger continuations and choices. Preserve deterministic replay, listener snapshots and rollback. Specify self-trigger compensation from reviewed evidence before implementing it.
2. **Entity changes:** distinguish play, summon, transform, draw, generate, discard, removal, death and resurrection; define retained/reset state per transition. Review special Battlecry transformations separately.
3. **Ordered modifiers:** base values plus source, order, operation, duration and removal rules. Handle auras, silence, stat-setting, cost changes and temporary effects consistently.
4. **Selectors and pools:** class, rune, tribe including ALL/multi-type, school, position, zone and history. Maintain explicit generation rules and special pools; keep deck legality distinct from generation eligibility.
5. **Card lifecycles and resources:** minions, weapons, locations, hero cards/powers, secrets, mana/overload, corpses and deckbuilding exceptions.
6. **Integration:** rebase the staged 88 cards against these contracts. Preserve the requested 200-additional-card milestone: 112 more definitions remain to reach it. That milestone does not substitute for full catalog completion.

### Required evidence for a shared mechanic

Each reviewed specification must record:

- Constructed scope, relevant patch and source links/sections.
- Activation zone, event and phase; eligible controller and targets.
- State changes, ordering, duration, expiration and zone-transition behavior.
- Generated IDs or exact pool definition, including exceptions.
- Positive, negative and interaction scenarios with expected outcomes and provenance.
- Known contradictions, unverified behavior and implementation locations.

`docs/engine-audit/standard-rules-reference.md` is the initial reference ledger. Its unresolved topics stay unresolved until researched; do not replace them with text-based guesses.

## Learning and evaluation design

Begin with legal random decks and an untrained policy. First isolate play improvement by training/evaluating on controlled deck distributions. Freeze checkpoints when comparing decks so changing player skill does not masquerade as deck strength. Then alternate policy improvement and deck evolution while retaining diverse decks and historical opponents.

Evaluation uses an opponent league, separate training/evaluation seeds, paired starting positions and confidence intervals. Opponent hidden state must never enter the policy's observation. Report per-class candidates and a matchup matrix. Define the opponent distribution behind any overall ranking: there is no universal best-deck guarantee.

Jupyter is the control panel; reusable implementation stays in modules. Separate cells/notebooks for rules checks, smoke games, training, deck search and evaluation. Long jobs require progress, checkpoint/resume and compact report exports. Benchmark hardware and game throughput before choosing network size, run budgets or timing estimates.

## Immediate status

- [x] Save this roadmap.
- [x] Build a static inventory of all 1,185 catalog entries with separate active/staged/missing status.
- [x] Retain actual definitions/source references where statically extractable; do not infer executable behavior from text.
- [ ] Complete the source-backed semantic map for every card.
- [ ] Finish and validate the consolidated shared-engine block.
- [ ] Integrate the staged milestone and complete full card coverage.

No checks or training are required just to read this roadmap or inventory. The next requested user run should accompany an implementation milestone, not this documentation delivery.

## In-progress generation checkpoint

[Shared generation machinery and 60 staged declarations](generation-60-checkpoint.md) are written and remain outside playable coverage. This is not the next completed batch: that checkpoint kept coverage at 785; subsequent Discover work brings it to 786, and the delivery target stays 845. The candidate dependency report now ranks blockers across these generators.

Internal progress toward 845: Discover counters and Storage Scuffle bring the candidate to **786**, with **399 remaining overall**. See [Discover checkpoint](discover-history-checkpoint.md). This does not complete the 60-card delivery.

The [Discover follow-up checkpoint](discover-followups-checkpoint.md) brings the registry to **787**, with **398 remaining overall** and **58 additions still needed** for the 845 target. This is internal batch progress, not a completed delivery.

[Replacement and secondary Hero Power support](hero-powers-checkpoint.md) advances the registry to **791**. The current 785 → 845 batch is **6 / 60** connected, with 54 additions outstanding.

[Quest infrastructure and rewards](quest-checkpoint.md) advance the registry to **794**, leaving **391**. The 785 → 845 batch remains unfinished at **9 / 60**, with **51** additions outstanding.

[Dream reward closure](dreams-checkpoint.md) brings written coverage to **796**, leaving **389**. The batch remains unfinished at **11 / 60**, with **49** additions outstanding.

[Underfel Rift and untouchable objects](permanents-checkpoint.md) advance written coverage to **797**, with **388 remaining**. Current batch progress is **12 / 60**, with **48** additions still required.

Internal Rogue Quest checkpoint: Lie in Wait/Master Dusk and resumable Hero Power sequences bring written coverage to **798/1185** (**387 remaining**, **13/60** current batch). See [details](dusk-checkpoint.md). No training run or batch completion.

Internal repeatable-Quest/recruitment checkpoint: Dive the Golakka Depths and High Cultist Herenn bring coverage to **800/1185** (**385 remaining**, **15/60** current batch). See [details](summon-quests-checkpoint.md). The full delivery remains unfinished.

Internal held-keyword/attack checkpoints bring written coverage to **803/1185** (**382 remaining**, **18/60** current batch). See [held/attack rules](held-and-attack-checkpoint.md) and [armor-trigger continuation](armor-attack-checkpoint.md). The 845 delivery target remains unfinished.

[Repetition, replacement and adjacency rules](repetition-replacement-checkpoint.md) bring written coverage to **806/1185**, leaving **379**, with **21/60** connected in the current unfinished batch.

[Internal spell casting](internal-casting-checkpoint.md) advances written coverage to **809/1185**, leaving **376**, with **24/60** connected in the current unfinished delivery. Dynamic casts and automatic choices remain next.

October 5 Cho'gall follow-up: the shared Arm/Soldier handler now stages enemy-deck minion removal with snapshot-scaled rewards and live-body replacement checks. Current totals: 229/308 staged runtime declarations, 79 without, 877 live. 58 body + 42 Herald + 23 queue checks passed; previous full-suite receipts do not cover this edit. Uniform eligible-slot selection and no-op on an empty eligible pool are explicit candidate assumptions pending frozen-client evidence; no admission. Four Colossal bodies still lack declarations.

October 5 [Colossal runtime completion](colossal-completion-checkpoint.md): all 11 bodies and printed appendage abilities have staged code. Totals are 233/308 staged runtime declarations, 75 without; live coverage stays 877/1185. Missing-body implementation is complete for this group, but the explicit independent fidelity and generation-pool gates remain. Feature schema v45 includes Magmaw's remaining appendage counter. See candidate STATUS for final validation receipts.

October 5 [Herald payoff checkpoint](herald-payoffs-checkpoint.md): Deathwing and Ultraxion bring Herald runtime declarations to 15/15 and overall staged runtime declarations to 235/308 (73 without). 466 targeted engine checks and 23 queue checks pass; no full-suite rerun for this checkpoint. Live coverage remains 877/1185. Explicit fidelity and complete-pool gates remain.

October 5 [remaining-systems checkpoint](remaining-systems-checkpoint.md): twelve additional staged runtime declarations bring the inventory to **247/308, with 61 lacking runtime declarations across 21 categories**. Evolving timelines and temporary control now have staged bodies; other categories retain exceptions. Live coverage remains 877/1185. The all-card objective is unchanged. See candidate STATUS.md for current validation.

October 5 [stored families checkpoint](stored-families-checkpoint.md): all five remaining stored-spell/stored-card declarations are implemented in staging. Totals: **252/308 runtime declarations, 56 missing across 19 categories**; live coverage stays 877/1185. Learned tokens have selected-target casting and retained physical payloads; Irida and Toki share finite storage/physical completion tracking. Client interaction and complete pool gates remain. The [Fabled source inventory](engine-audit/fabled-source-inventory.json) covers all eleven roots, including Gelbin and Sindragosa outside the queue's Fabled category.


### Gorishi consolidated checkpoint

Frozen patch 36.6.0.251952: 877 live collectibles, 308 staged; 265 staged bodies and 43 missing. Six Quest/Sidequest roots remain. Shared damage attribution and staged Unleash the Colossus/Gorishi behavior now pass 3,988 engine fixtures, 27 dependency checks and 22 terminal smoke games (zero errors/caps). Fingerprint c6968b04e22c5df0d9d88046f17e044d527c096a6fc6a8ab42509c247701397c. Feature schema v54. No new live admission; stacking and trigger-order evidence remain explicit gates. Next connected family is Battle at the End Time, with reviewed semantic hand-transition notifications and complete Tick and Tock effects. See engine-audit/end-time-quest-contract.json.


### Three-Quest consolidated checkpoint

End Time, Food Chain and Mountain/Ashalon now have staged bodies with explicit fidelity gates. Frozen inventory: 877 live, 308 staged, 268 staged declarations, 40 missing bodies. Three Quest/Sidequest roots remain. Schema v55. All 4,034 engine fixtures, 27 dependency checks and 22 smoke games passed (zero failures/errors/caps), fingerprint 7b9e1e33f3b4d244425e1ac9cbdc3f10c3b7b1d001d4f4455bbea615b2c64a50. No new admission. Next shared work is captured Discover offers and automatic execution across card types for Origin Stone and the automatic-play family; see engine-audit/origin-stone-contract.json.
