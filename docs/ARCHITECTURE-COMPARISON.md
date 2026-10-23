# Bounded architecture-comparison pilot

Question: with the same visible representation, PPO procedure, frozen training opponent and game budget, how do a mean-pooled MLP and the existing small Transformer differ in learning, cost and playing strength?

This is a feasibility pilot for a later study, not a completed research paper. No experiments were launched during implementation. The owner starts `notebooks/19_architecture_comparison.ipynb`. The player-development notebook, saved player and original runs remain separate and unchanged.

## First chunk and resources

One launch targets 128 training games per architecture: 256 total, two complete 64-game PPO batches each. Architectures run sequentially, with two CPU threads and no parallel collectors. There is a 90-minute soft wall-clock limit, checked between games. A last game or PPO update can finish after that limit. A time-limit pause saves the pending samples, results, model, Adam state, action/shuffle RNGs, next seed and schedule position; the next launch catches up the unfinished paired round. A launch after a completed pair adds another 128 games per model. It never launches an unbounded sweep.

A planning estimate is 30–90 minutes for the initial pair, including evaluation; the actual first run must establish timing. There are 44 baseline plus 44 post-chunk evaluation cases per model (176 total on the first complete pair); later chunks reuse the cached initial baseline and evaluate again at their new endpoint. Manual interruption resumes the newest durable checkpoint but can lose unsaved games since that save. Launch guards prevent overlapping a player-training run or another research run.

## Controls

Both learner models start fresh, using initialization seed 113. The existing 2,408+ game model is never loaded into either learner. Both receive the identical versioned structured encoder, all visible fields, action candidates, eleven-class fixed training roster, matchup/seat/opening schedule, PPO learning rate 0.0001, minibatch 64, four maximum epochs, KL limit 0.02 and terminal rewards. No tactical lessons are applied to either learner. PPO's KL early stop can yield different actual update counts; those differences are recorded, not hidden.

The MLP shares the field embedding approach and action/value head form, replaces inter-entity attention with mean pooling and a two-layer context MLP, and has its own newly initialized weights. It sees the same features but compresses their relationships differently. Parameter counts are reported; they are not exactly matched, so this first experiment compares two practical configurations rather than proving an effect of attention alone.

The same saved Transformer is frozen as opponent for both learners, identified by exact checkpoint hash in `runs/research_mlp_transformer/study.json`. It is not a handwritten player and is not updated during research. This first experiment is PPO against a common fixed opponent, not an architecture-specific self-play league. A common opponent reduces differences in the training environment between architectures. It does not establish robustness against diverse players.

Game schedules and environment seed sequences begin identically for both models. Different actions, game lengths and failures naturally produce different trajectories. Independent policy/optimizer RNG states are saved for each arm. Fairness means matched protocols and exposure budgets, not identical action sequences or identical realized outcomes.

## Evaluation and reporting

Each 44-case evaluation balances all eleven learner/opponent classes, both learner seats and both opening seats along one fixed cyclic set of class matchups. It is NOT the complete 484-pair/seat/opening schedule. Both models face the same frozen opponent, game seeds and cases. Evaluation never changes weights and uses an independent RNG/seed range. Training and evaluation do not share game seeds.

Report score (win + half draw), raw W/D/L, caps, failures, confidence intervals for win rate, parameters, learning metrics, PPO steps, game actions and per-game timing. Training attempt receipts retain errors and caps, including replacements. Failed/capped attempts consume a seed but not a successful-game slot or gradient; repeated errors/caps stop the experiment. This can bias the completed sample pool and must remain visible in comparisons. Checkpoint game count is collected successful games; a time-limit checkpoint can also contain an unfinished learning batch. Equal-budget comparisons are labeled complete only when both arms reach the target and have completed their updates and endpoint evaluation.

These evaluations use new seeds on the SAME decks and SAME opponent used for training. Treat them as monitoring, not unseen-deck/opponent generalization or a sealed final test. A single training seed and 44 cases provide very limited statistical evidence. No strong ranking should be inferred from this first chunk.

## Before writing comparative conclusions

Freeze the full protocol after this timing pilot. Add independent training seeds (a budgeted initial target of at least three, ideally five or more), a frozen opponent panel, truly held-out deck lists, a separate final seed set, repeated uncertainty estimates, equal-experience and equal-wall-time curves, per-class breakdowns and a matched hyperparameter-tuning budget. Report model size and parameter-matched ablations where relevant. Save simulator/config/source hashes, environment versions and run receipts. Document simulator approximations and unresolved fidelity; results describe this simulator, not independently certified human ladder strength.

Later phases may add recurrent memory, a larger Transformer and inference-time search. Search needs a separate compute budget and must never inspect actual hidden cards or future RNG outcomes. Those contenders are outside this initial implementation.

## Pilot engine repair before the first research run

The unstarted study was explicitly re-pinned from engine `7ff7d54270d01b72c4317f931b3ec5cc7126d783eb702348c6728240331844df` to `6375d2791cba908d5ce8fd134629997807a6841499f1244e96852e4a612b1fc8`. Historical Dragon/zone/highest-cost discounts now initialize optional physical-card cost deltas before subtracting; already-existing deltas continue to accumulate. The generated live Deathrattle producer captures the minion's board position for the replay context, following the existing live-replay positioning contract. Primitive dispatch still requires a valid context rather than silently substituting a position.

Six new scripted checks cover fresh/stacked Dragon discounts, unchanged non-Dragon cards, bare-ID deck discounts, selected highest-cost cards, Discover-then-summon Deathrattles, board-cap behavior and departed sources. In total 184 related engine checks plus nine research checks passed, and research preflight passed. These are internal checks, not independent game-client certification. No training or evaluation runs were launched.

`tools/prepare_research_engine_repairs.py` accepts only the exact unstarted study, engine versions and frozen opponent hash. It refuses to rewrite a started study, preserves the previous study manifest, and records a local repair receipt. The original 2,920-game model (`abb3d50a6c121e3d24cad5969230bdba6332fd3f8610e4cdeab7820e34b5b366`) is unchanged. Both new research learners remain fresh; the saved player is only their common frozen opponent.
