# Shared entry and resolution diagnostics

The candidate now labels all 36 existing direct summon call sites with origin and source-site provenance. Origins distinguish hand play, ordinary effects, copies, recruitment, resurrection, Reborn, Hero Powers, Secrets, locations, Deathrattles and choices. Transformation records a replacement rather than a summon. Unknown external/test calls retain an explicit `unspecified` origin.

`Game.configure_entry_trace(limit=2000)` enables a bounded private timeline; `limit=0` clears and disables it. `Game.entry_trace()` returns an independent JSON-serializable snapshot, including a dropped-record count. Tracing is disabled by default. Diagnostics include attempted/successful/failed entry, post-recruit grants, initialized Reborn state, action boundaries, queued event listeners, event starts, choices, top-level operations, damage batches and death-wave advancement.

These records describe current behavior. In particular, `entry_result` observes construction before a caller may grant Rush or reset Reborn health; `recruit_initialized` and `reborn_initialized` explicitly record those later states. This prevents a diagnostic boundary from being mistaken for a certified summon-listener timing rule.

No general summon listeners or new cards are enabled by this change. No dispatcher order or death checkpoint is deliberately changed. The complete event/summon milestone is still unfinished: resumable entry/batch frames and evidence-backed listener dispatch remain outstanding. The timeline is not an implementation of those frames.

Diagnostics never enter public observations, public game logs or policy features, but can contain hidden card identities. They are for debugging only. Failed `Game.step` actions roll diagnostics back with all other state. Trace sequence numbers are not action IDs and do not provide parent-frame linkage. Source IDs are included where the current call path supplies an entity; missing sources remain null rather than guessed. Inherited legacy helper paths are not newly instrumented by this patch.

## Local validation

Open `notebooks/13_shared_rules_checks.ipynb` and Run All. It uses a fresh process to avoid importing the older root engine from a previous notebook. It runs the full candidate fixture suite with progress and saved receipts, without training or a random-game batch.

Thirteen new fixtures cover opt-in behavior; bounded storage and detached snapshots; invalid configuration; play provenance; recruitment without Battlecry; Reborn initialization; transformation exclusion; failed board entry; Hero Powers; choices; rollback; trace-on/off observation/RNG equivalence; and damage-pulse boundaries. These fixtures were prepared but not executed by the assistant. Only syntax, callsite labeling and source consistency were checked statically.

Existing validation receipts predate these edits and must not be treated as passing evidence for the new candidate. Card inventory remains 503 written / 682 missing. This patch is shared infrastructure rather than a small collectible-card batch.
