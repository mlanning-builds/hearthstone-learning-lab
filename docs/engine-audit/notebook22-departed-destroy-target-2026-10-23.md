# Notebook 22 destroy-target repair

The owner-started research run paused with ValueError:_find after 136 completed MLP games. Generic destroy execution assumed a locked target remained on the battlefield. It now does nothing when that entity has left, while subsequent operations continue. Live-target destruction is unchanged.

93 targeted non-training checks passed: effect executor (4), effect replay (16), choice continuation (5), entity effects (46), targeted spell trigger (7), research contracts (15). Lint and resume preflight passed. This is not a full simulator regression or independent client certification. No training was started during repair.

The study has an explicit engine-repair migration. The original 19,931-game Transformer checkpoint is unchanged; a study-local copy carries the repaired engine compatibility. The complete MLP resume payload was compared after migration: weights, Adam, random states and pending trajectories/results are identical. Counters remain 136 completed games, two learning batches, eight pending games, 128 completed tactical warm-up steps. The original failure receipt and pre-repair notebook output remain archived. The failure remains in historical accounting and its blocking flag is resolved. Study metadata and configuration backups are in runs/research_matched_games/repairs/departed-destroy-target-2026-10-23.
