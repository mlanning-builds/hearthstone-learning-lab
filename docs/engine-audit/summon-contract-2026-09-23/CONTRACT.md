# Summon/play phase contract — specification checkpoint

2026-09-23. Regular Standard, frozen build 251952. Specification and static source review only. No simulator code was changed or executed. This document separates observed implementation, proposed architecture, and unverified game timing.

## Decision

Introduce explicit entry provenance and resumable phase records before enabling general summon listeners. Do not put an unconditional event dispatch in `_create_minion` or drain listeners immediately in `_summon`: that would conflate played minions, effect summons and transformation, and could interrupt existing effect helpers before they finish applying state.

The next safe implementation increment is provenance and trace plumbing with behavior-preservation checks. Actual listener timing requires independently established outcomes for the cases below; it is not authorized by a historical simulator's behavior alone.

## Current source map

`source-event-map.json` contains file hashes, line numbers, enclosing functions and expressions for every direct call to the tracked helpers in candidate `expanded/*.py`. It finds 36 `_summon` call sites, two `_create_minion` calls, six `_queue_event` calls and 28 `_settle` calls. These are call sites, not executed paths or distinct rules. Inherited engine paths and dynamic dispatch remain outside this map.

| Path | Current behavior established by source reading | Consequence |
| --- | --- | --- |
| `Game._play` | Pays/removes card; a minion enters through `_summon`; its declared operations run through `PlayFrame`; history updates and `_after_play` follow, or are partly deferred around choices. | A played minion must retain its own phase context through Battlecry and suspension. |
| `Game._summon` | Calls `_create_minion`, then logs a successful summon. No general rule-event notification here. | Display logging does not notify summon listeners. |
| `Game._create_minion` | Checks board cap, creates/copies entity, inserts it, refreshes auras and restores copy damage. | It is a low-level construction helper, not a universal summon boundary. |
| `Systems._transform` | Uses `_create_minion` directly for replacement. | Do not treat every construction as a summon. |
| `Systems._after_play` | Publishes `minion_played` for minions after effects; spell/secret paths differ. | Existing played listeners cannot simply stand in for summon listeners. |
| `summon_from_zone` | Selects and pops one physical source card, summons it, then adds optional Rush/Lifesteal and refreshes auras. | A new callback inside `_summon` would observe a different state than one after the helper returns. |
| `Lifecycle._advance_death_wave` | Runs captured death operations, then Reborn; Reborn uses `_summon`, then removes Reborn and sets health to 1. | Notification timing must account for post-construction state; a callback inside `_summon` would see the pre-adjustment entity. |
| `Game._effect(area_damage)` | Collects targets and damages inside `_damage_batch`. | Death settling is deferred within the batch. |
| `Resolution._resume_play_effects` | Calls `_settle` after each operation. Crowd Control declares two area-damage operations. | Current top-level path settles between its two pulses. This is a source fact, not independent timing certification. |
| `Systems._drain_events` / `Lifecycle._settle` | Event frames process children; settling refuses reentry while events are draining; nested card-effect frames are rejected. | A generic callback can expose unsupported nesting/choice cases. |

## Proposed internal contract

These are architecture requirements. Phase names below are internal names, not claims about Blizzard's implementation.

1. **Validate and establish origin.** The enclosing action owns legality/payment. A minion-entry request identifies `origin_kind` (played card, effect summon, recruit, Reborn, hero power, secret, location or replacement), controller, source entity/card, source zone, intended position, parent frame, and stable action ID. Store IDs rather than relying on a source entity remaining alive.
2. **Attempt entry.** Check destination capacity and eligibility at a defined boundary. Record success/failure and source-zone disposition. Failed entry must not be indistinguishable from successful entry. Source-zone consumption rules are operation-specific; do not move all cards out of their zones before attempting entry.
3. **Construct and initialize.** Apply the chosen transfer/copy/rebirth policy, allocate a fresh entity identity where required, insert it and refresh derived state. Distinguish intrinsic entry initialization from explicit later card effects. Reborn's 1-health state and Recruiter's subsequent Rush grant cannot be silently assumed to occupy the same timing boundary.
4. **Resolve origin-specific work.** A hand-play path owns Battlecry/Choose One and play-only listeners; an effect summon does not execute Battlecry merely because the minion has one. Replacement is a separate path. Keep exact pre/after-listener boundaries as reviewed policies rather than string-matching “whenever” or “after.”
5. **Publish rule notifications at defined boundaries.** Separate entered-play, play and summon concepts. Capture listener eligibility and event payload at the boundary selected by the reviewed policy. Logs are separate from executable events. Historical evidence motivates multiple boundaries but does not fix their 2026 ordering.
6. **Resume parent work exactly once.** A choice suspends the entire chain, including unfinished summon batches and the parent effect. No continued loop, double resource consumption or repeated insertion after resume. Terminal outcomes clear continuations. Failed actions preserve the existing full-state/RNG rollback guarantee.
7. **Settle at explicit checkpoints.** Damage batches, individual summons, Battlecry operations, death waves and end-turn operations must each declare their checkpoint behavior. Do not derive death timing accidentally from whichever helper called `_settle`.

A proposed `EntryFrame` carries: action ID, parent frame ID, origin kind, controller, source identifiers, source zone/physical card ID, requested position, transfer policy, stage, resulting entity ID, success, pending notifications and continuation cursor. A proposed `SummonBatchFrame` carries intended attempts, next-attempt cursor and parent frame. Both must be plain serializable/deep-copyable data and remain private to the engine. They are design proposals, not existing classes.

### Unresolved timing policies — no defaults disguised as facts

- When played minions notify summon listeners relative to their Battlecry and play listeners.
- Whether a newly entered listener reacts to itself or earlier entries in a batch, and what happens when listeners change control/die mid-resolution.
- Which state Khadgar duplicates and whether later effect-granted Rush belongs on extra copies.
- Reborn health/keyword initialization versus summon notifications and auras.
- Death processing between summons within one operation, within Battlecry, and inside nested triggers.
- Notification order across Secrets, locations, heroes and minions; entity UID is not automatically a complete timestamp model.

No new gameplay listener should be enabled with an unreviewed policy merely to increase card coverage.

## First four scenarios: evidence and corrected setups

| Scenario | Valid setup and variants | Evidence status | Required result before activation |
| --- | --- | --- | --- |
| 1. Murloc Tidecaller | Use `CORE_EX1_509` and play `CORE_EX1_506` Murloc Tidehunter, which summons a Scout. Vary board space and listener order. Use direct effect summons separately. | Both exact texts are in the frozen catalog. General summon listeners absent in current code. No independent build-251952 trace collected. | Number/order of notifications for played minion and Scout, state at each notification, and full-board failure behavior. |
| 2. Khadgar | Use Mage-legal `CORE_DAL_575` with a legal neutral summoning card; compare ordinary minion play to effect-created summons, multiple copies and board limits. | Historical Fireplace code distinguishes player-origin plays from effect sources and copies summons; its behavior is reference only. No pinned trace. | Provenance filtering, copy-state boundary, recursion/multiple-source behavior, position and capacity outcomes. |
| 3. Scarlet Recruiter | Use `JAIL_516` with neutral `CORE_DMF_067` Prize Vendor (2 mana) in its deck. Contrast Vendor's normal play with recruitment; vary one/two free slots. | Earlier checklist incorrectly suggested 5-mana Hogdriver without a cost reduction. Corrected here. Existing source grants Rush after `_summon` returns. | Recruiting must be checked separately from playing; capture draw/Battlecry behavior, keyword visibility, deck removal and listener order. Cross-class interactions need a documented legal generation/control route or must be labeled synthetic. |
| 4. Crowd Control | Use `JAIL_307` against a DK opponent's `CORE_RLK_745` Malignant Horror; prepare a legal damaged state so the first pulse is lethal. Add separately legal death/aura fixtures rather than inventing a mixed-class deck. | Current source settles between two top-level pulses; historical engine architecture is comparison evidence. No independent pinned outcome. | Record first damage batch, death processing, Reborn and second batch in sequence, including board caps and aura-source death. |

All four scenarios remain independently unverified for the target build. The useful result of this block is the phase contract and exact uncertainty list, not four invented pass marks.

## Sources and limits

- Frozen catalog card IDs/text: `data/standard/cards.json`, build 251952; source hashes retained in the scope ledger.
- Candidate source: file hashes and exact line anchors in `source-event-map.json`.
- Historical architecture reference: [Fireplace actions at pinned revision](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/actions.py), `Play` and `Summon`; [Khadgar declaration](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/dalaran/mage.py). Reviewed as primary evidence of that project's implementation, not of current Hearthstone behavior. No upstream code copied.
- The wiki search located relevant summon/Battlecry discussions, but their historical timing descriptions do not provide pinned client conformance. No rules are certified from snippets.
- Blizzard's how-to-play link redirected to a general landing page and supplied no detailed phase contract. An unrelated patch result did not establish regular Standard timing and was not used.

## Next bounded increment

Maximum 90 active minutes: implement private summon-origin/phase tracing with unchanged gameplay and targeted behavior-preservation checks. Cover all 36 current `_summon` call sites and explicitly exclude transformation. Save traces for play, recruit, Reborn, hero-power and deathrattle paths, including choices and rollback. User runs simulator checks unless execution is separately requested. Enable no new cards/listeners and start no training.

This increment can make the architecture observable without guessing timing. Changing actual dispatch order remains gated on resolving the independent evidence questions above. Do not repeatedly repeat the same source audit when the missing input is external evidence.

## Tracing increment written

See [entry tracing](../../entry-tracing.md). All 36 direct call sites are labeled; private bounded diagnostics and thirteen regression fixtures are written. Gameplay dispatch remains unchanged, and local validation is pending. Use notebook 13.

## Experimental listener path written

The [shared listener implementation](../../summon-listeners.md) now handles three declarative consumers at existing checkpoints. It is awaiting local checks and retains the explicitly unverified multi-summon/Secret/recursive phase cases. The full summon-phase milestone is not complete.
