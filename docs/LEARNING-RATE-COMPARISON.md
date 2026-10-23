# Saved-model learning-rate pilot

Open `notebooks/20_learning_rate_comparison.ipynb` after notebook 18 finishes. The first cell performs only read-only checks. The owner starts the second code cell.

- Same immutable continuum-000005703.json: 176 decks, 16 per class.
- Latest integrity-verified campaign checkpoint selected at Start, not preparation time. Both arms copy its weights, Adam moments, RNG states, opponent league, tactical progress and global schedule position. Only learning rate differs between arms (0.0001 and 0.00005).
- Six CPU threads, four collectors; two 64-game batches per arm. Existing opponent mixture, PPO epochs/minibatch/KL guard, safety counters and lessons retained. Arms develop their own self-play snapshots as a consequence of treatment.
- Both arms use the same frozen evaluation anchors, held-out seeds and 32 cases per opponent. The shortened monitoring schedule is identical in both arms. No new initial evaluation: both start with identical weights. Evaluation is a small, single-seed pilot, not a reliable strength ranking across every matchup.
- Ninety-minute soft budget across both arms. Active batches/evaluations can exceed it. Incomplete/failed arms are explicitly inconclusive, with partial checkpoints retained. Start again creates a new study; it does not silently resume an incomplete pilot or promote a winner.
- All writes go under runs/learning_rate_comparison. Main campaign checkpoint discovery excludes these outputs. No campaign weights, saved receipts, or notebook 18 are modified.
- Start refuses overlapping training, failed latest campaign checkpoints, and unreviewed source/panel changes. Staged engine fixes must be reviewed and migrated after the active run before this pilot can use repaired sources. No automatic compatibility bypass.

Non-training validation: four targeted checks cover state-preserving copies, overlap refusal, clean notebook syntax, and unchanged live neural fingerprint. Read-only preflight validates all 176 deck lists and engine/neural compatibility. No training, optimizer update or policy evaluation was executed during preparation.
