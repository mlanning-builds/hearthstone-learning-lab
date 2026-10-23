# Equal-game alternatives versus our saved Hearthstone player

The owner selected a practical comparison accepting different training histories, rather than retraining a fresh small-Transformer control. The preserved 19,931-game checkpoint remains unchanged. Notebook 22 trains only the alternatives. Notebook 21, its configuration, original research pilot and saved models are unchanged.

## Contenders

| Contender | Source | Question |
|---|---|---|
| Mean-pool MLP | Fresh PPO learner | Strength per completed training game without attention |
| GRU | Fresh PPO learner; bounded 16-own-decision window | Whether recent decision memory helps |
| Small Transformer | Preserved 19,931-game model | The player's actual existing baseline |
| Larger Transformer | Fresh PPO learner; width 192, six heads, six layers | Whether more capacity pays for itself |
| Small Transformer + search | Same preserved weights | Whether additional decision-time combat planning helps |

The GRU recomputes each stored window with current weights during PPO. Windows reset at episode boundaries; no stale hidden states are attached to independently shuffled decisions. This is bounded recurrent context, not unlimited game memory. All policies receive the existing legal-action and public-observation encoding. Learned weights are not transferred between architectures.

Search is an operational two-ply, three-wide, at-most-twelve-node public combat planner scored by the neural value head. It searches ordinary minion attacks only when public board mechanics meet its conservative support checks. Other actions/positions use the original policy. It has no private Game access and cannot inspect real hidden hands or deck order. Unknown secrets and full-game continuation are not modeled. Its score, supported-decision coverage, errors and added computation must be reported together; this is not full-game information-set MCTS. Tactical quiz scores for this variant are explicitly the underlying network's scores, not evidence about search.

## Time and compute

A read-only lineage audit recovered approximately **13.4085 hours** of collection/learning timers behind the saved player. This excludes evaluation, lessons and other overhead, and one early batch has incomplete timing. Thread counts, collector counts, decks, simulator versions, opponent mixtures and lessons changed historically. We cannot recreate an exact historical CPU budget from those receipts.

Each fresh alternative receives **19,931 completed training games**. Graph checkpoints occur at **1,000, 2,000, …, 19,000 and 19,931 games**. Collection stops at each exact boundary and PPO flushes the final partial batch before its checkpoint is frozen. Failed or capped attempts do not count as completed games. Every owner-started launch has a two-hour soft wall limit and rotates among alternatives in fifteen-minute turns. Resume continues the same learners and counters.

Record collection, PPO and tactical-lesson time, worker/main CPU time, evaluation time and elapsed session time separately. Training clocks include worker startup/serialization and failures. CPU timers are not a perfect accounting of process-startup overhead. Equal games measure sample efficiency; measured time describes cost on this machine. These results cannot establish how additional hardware would scale.

The saved player's reference lines already represent 19,931 games. They are not fresh learning curves. Its recovered timer subtotal is shown only at its final game count, clearly distinguished from an exact historical compute budget. Training conditions changed historically, so this is a practical comparison accepting different histories rather than a controlled architecture-only experiment.

## Common training conditions for alternatives

- Exact existing 176-deck snapshot, sixteen decks per class across all eleven classes.
- Same seed stream, matchup schedule, legal observations and rules.
- Six learning threads, four one-thread collection workers, CPU only; one alternative at a time.
- PPO learning rate 1e-4, four maximum epochs, KL safeguard 0.02, 64-game rollout batches. Common minibatches of **16**, deliberately smaller than the campaign's 64 to bound large-model memory.
- 60% batch-frozen current self-play, 30% that learner's older checkpoints, 10% heuristic. Until an older checkpoint exists, its slots use current self-play. Eight older checkpoints per alternative; this differs from the historical campaign league size.
- Same 128-step tactical warm-up and sixteen-step refresher every sixteen completed PPO batches; their time is charged.

Faster models may reach the same game count sooner; that time difference is recorded. Fixed seeds and opponent choices do not mean identical trajectories after policies diverge.

## Evaluations and reporting

At shared milestones, all five contenders face the same frozen 400-game player, preserved 19,931-game player and heuristic bot. Each opponent gets 44 held-out-seed cases balancing all eleven classes, seats and opening seats. These sample the existing roster, not an unseen-deck generalization test. Larger panels/multiple training seeds are required for publication-level conclusions. The two frozen reference evaluations are cached rather than rerun at every milestone.

Reports retain win/score intervals, opponent breakdowns, tactical categories, failed/capped games, search coverage and time per action. Caps/errors never become losses or PPO examples. Failed training games pause for engine review instead of quietly shrinking pools/retrying favorable matchups. Final-budget head-to-head comparisons cover all ten contender pairs and resume case-by-case. A common-opponent leaderboard with one training seed is exploratory.

PPO method reference: [Schulman et al., 2017](https://arxiv.org/abs/1707.06347). The chosen finite-window recurrent implementation and limited combat planner are project-specific experimental definitions, not claims of reproducing a published recurrent PPO or AlphaZero implementation.

## Start and resume

Open `notebooks/22_model_comparison.ipynb`. First cell: integrity/configuration checks only. Second cell: explicit owner training start. Run All Cells again to continue the same study. The study shares the campaign lock with notebook 21, so they cannot train simultaneously. No training is launched by imports, tests or preflight.

All new artifacts live in `runs/research_matched_games`. Source/config/simulator/reference fingerprints are pinned. Changed sources fail closed rather than mix results. Full resume payloads include weights, Adam, RNG states, partial completed-game rollouts, time counters and opponent descriptors. The latest and previous resume, every milestone and the eight-checkpoint league are retained; obsolete study-owned `weights-*` files are removed to bound disk use. Original campaign checkpoints are never pruned. Work since the last durable checkpoint can be lost on a forced process kill; a normal time-limit pause saves partial rollouts.

`results.json` and `dashboard.html` are generated inside the study folder. The dashboard embeds three graphs: win rate with 95% Wilson intervals, tactical correctness and training hours, each against completed training games. Standalone PNG and SVG figures are saved under `plots/learning-curves.*`. Graphs redraw when milestone data changes, rather than after every batch. No completed evaluation produces no score point; missing or failed evaluations are not plotted as zero. No completed evaluations means no claimed result. No models, games, search benchmarks, lesson updates or training runs were started during setup; only non-training tests/preflight were performed.

## Public checkout prerequisites

Notebook 22 is a resume profile for a local study, not a bundled pretrained demo. Its configuration pins a local 176-deck panel, preserved reference and 400-game evaluation anchor. These ignored `runs/` artifacts are not included on GitHub. To reproduce a new study, create the deck panel and reference/anchor checkpoints through the training workflows, update their paths and SHA-256 values, and use a new isolated output directory. Do not substitute unverified weights or bypass compatibility checks. Notebook 15 is the fresh-run entry point.
