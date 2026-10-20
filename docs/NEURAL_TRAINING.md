# Transformer PPO training

## Long-run preset and monitoring

Use `notebooks/16_long_transformer_training.ipynb` for the new owner-launched preset. The published notebook defaults to preflight only, with no checkpoint selected. Available modes are `preflight` (checks only), `trial` (400 additional games), `medium` (2,000) and `full` (10,000). Choose a training mode, select your own checkpoint if resuming, and set `START_TRAINING=True` before Run All. Baseline evaluation precedes updates; the medium preset evaluates again after 512, 1,024, 1,536 and 2,000 additional games. Local owner settings and live outputs are excluded from the published notebook. Setup/preflight alone start no games. Keep the computer awake and Jupyter running during a long run.

PPO still updates every eight games. This preset saves durable training and opponent snapshots every sixteen iterations (about 128 games), plus the final batch; it evaluates every sixty-four iterations (about 512 training games), before learning, and at the end. Each evaluation uses 64 games against each fixed opponent: the hand-written heuristic, initial neural model and saved starting checkpoint. A fresh run without a parent has only the initial neural and heuristic anchors. Evaluation results never enter PPO, and its RNGs and game seeds are separate from training. The seed ranges are checked for overlap before any game starts.

The dashboard reports completed/capped games, real optimizer steps, elapsed time, rough time remaining including estimated evaluation cost, latest durable checkpoint, per-opponent W/D/L, win rate with approximate Wilson 95% intervals and a score curve. Full JSON reports include each matchup, both seats and the game seeds. Draws count as non-wins for the win-rate interval and as half a point on the score curve. Capped games are excluded from win-rate denominators and shown explicitly. Fixed cases reused for monitoring are a validation panel, not an unbiased final test set.

The default checkpoint cadence estimates about 6 GB of new model files for 10,000 games. All old and new immutable snapshots are retained; no files are pruned. More frequent snapshots use more disk but reduce interrupted-run progress loss. At the default cadence up to 128 games of unsaved training can be lost on interruption. Each saved checkpoint includes the complete optimizer/RNG state and relative opponent archive references. Resume requires its whole run directory.

The legacy first-harness continuation uses `--allow-code-upgrade`; it is separate from the 400-game engine migration described below. Only the known original neural-code fingerprint is accepted, and the engine, encoder, architecture, decks, dependency versions and existing PPO settings must match. The model, encoder and PPO source hashes must remain identical to the first release. Old checkpoints and hashes are never edited. We preserve weights, Adam, counters, RNG streams and archived opponents. Because the monitoring/collection harness changed, this is labeled a training-code upgrade rather than bitwise replay of the old harness. Subsequent matching checkpoints use normal exact resume.

The owner completed a 400-game continuation after the original eight games. Those local weights and evaluation reports are not distributed. `tools/migrate_400_game_checkpoint.py` is a one-time, allowlisted migration for that exact local trial after the engine repairs; it preserves weights, Adam, RNGs, counters and archived opponents, verifies unchanged learning code, and records old-engine scores separately. It does not play games. It intentionally rejects other parents or source versions; normal resume compatibility checks remain strict. Its opponents are baselines, not expert players. These reports answer whether the policy improves against a stable panel while piloting the four fixed decks. They do not establish the best deck, causal card value, optimal play or strong human-level performance. Those require stronger independent opponents, broader controlled deck comparisons and fresh final-test seeds. No deck-search experiment is started by this preset.


Use `notebooks/15_transformer_ppo.ipynb` for the neural trainer. Notebook 11 is the preserved sparse linear baseline. Its JSON weights cannot be converted into trained Transformer weights.

## Start in Jupyter

From the complete checkout:

```sh
.venv/bin/python -m pip install -e '.[neural,notebook]'
.venv/bin/python -m jupyterlab notebooks/15_transformer_ppo.ipynb
```

Run setup and preflight first. They validate configuration without playing games or updating weights. To start yourself, change `START_TRAINING` to `True`, rerun setup, then execute the launch cell. Defaults are one iteration, eight games, at most 1,000 actions per game, CPU with two threads. Those are functional starter settings, not a budget sufficient for strong play.

No install, import, preflight or Make target starts training. Explicit CLI equivalent when the owner chooses to run:

```sh
.venv/bin/python tools/train_neural.py --train --iterations 1 --games-per-iteration 8 --max-actions 1000 --seed 71 --device cpu
```

CPU is the tested portable path. CUDA and Apple MPS selection are available but those accelerator execution paths have not been validated here. Automatic device selection is opt-in. Dependency ranges support the existing Python 3.9 environment; this machine uses PyTorch 2.8.0. A fresh install on another platform has not been tested for this new extra.

## Model and input boundary

`hearthstone_sim/neural/model.py` implements a 4,757,122-parameter network at default settings: width 128, four attention heads, three Transformer blocks, feedforward width 384, and separate policy and value heads. Shared field/value embeddings form entity tokens. Policy logits are produced for the current variable-length legal candidate set, preserving candidate order; no padded or illegal move can be selected. The value estimate is bounded to [-1,1]. Dropout is disabled so collection probabilities and PPO recomputation use the same policy.

`encoding.py` reads only `PolicyEnvironment` decision observations and legal actions. It adds frozen printed definitions only for visible card identities. It does not receive the private Game object, replay headers, simulator RNG, opponent hand identities or hidden deck order. Fields not present in the old linear encoder are represented generically. Runtime UIDs resolve to visible relative slots instead of being learned as arbitrary identity numbers.

The representation hashes typed paths/values into 32,768 embedding buckets. Collisions are possible. All current player fields and state entities are included except explicit bookkeeping, terminal labels and constant fidelity descriptions; the latest 64 viewer-visible events are included in order, along with an omitted-event count. Earlier public play/death information is also available where the observation exposes its histories. This finite history is not a complete belief model. Explicit state-token/field limits fail on overflow rather than silently dropping board entities or legal actions. Default state limit is 768 tokens and field limit is 8,192 per token. New mechanic-specific encoders, hidden-information search and semantic card-text pretraining remain possible improvements.

## Fixed competitive panel

`configs/neural_competitive_decks.json` pins exact lists selected from [vS report 358, September 17, 2026](https://www.vicioussyndicate.com/vs-data-reaper-report-358/):

- [Cannoneer Dragon Warrior](https://www.vicioussyndicate.com/decks/cannoneer-dragon-warrior/), published September 2.
- [Bite Attack Druid](https://www.vicioussyndicate.com/decks/bite-attack-druid/), published September 1.
- [Thalena Egg Death Knight](https://www.vicioussyndicate.com/decks/thalena-egg-death-knight-4/), published September 16.
- [Stealth Herald Rogue](https://www.vicioussyndicate.com/decks/stealth-herald-rogue/), published September 1.

The report is contemporaneous with the frozen 36.6.0.251952 snapshot. The complete lists are stored as IDs, names and multiplicities with source links. No card substitutions or strength claims are invented. All four are locally validated for class, rune, copy count, implementation and Standard membership. Rogue's Fabled companions are explicitly listed with Garona; they are not illegal standalone additions. These lists do not claim current live-patch optimality. No training-time internet lookup occurs.

All ordered deck pairs, learner seats and first-player seats appear once in each 64-game scheduling cycle, shuffled reproducibly by seed. Partial cycles need not be balanced. The opponent deck identity is recorded for receipts, not provided as privileged policy input. Editing the panel changes its hash and invalidates exact resume.

## PPO and opponents

The actor weights remain fixed throughout an iteration's collection. Each game has one learner seat and one frozen opponent. Only learner decisions enter PPO. Defaults choose the frozen current learner 25% of the time and a uniformly sampled archived neural checkpoint 75% of the time. The initial untrained neural checkpoint is always retained. No strong pretrained opponent is included. Updated iterations add a snapshot; the pool keeps the initial plus the most recent snapshots up to 32 total. Additional compatible neural checkpoints can be supplied with repeated `--opponent` arguments or the notebook list. Legacy sparse JSON checkpoints are incompatible.

The return is the learner's terminal win/draw/loss (+1/0/-1). GAE advances between successive learner decisions, with gamma 1 and lambda .95 by default. Games ending at the action cap are logged and entirely excluded from training; no fabricated loss or terminal bootstrap is assigned. Consequently, cap-heavy runs may produce few or zero samples. Draws may still train the value estimate and entropy objective.

PPO uses frozen old log probabilities/values, standardized batch advantages, clipped policy and clipped value losses, entropy regularization, Adam, minibatches, gradient clipping, and early stopping on approximate KL. Default optimizer settings are in `ppo.py`. Logged metrics include actual optimizer steps, loss components, entropy, KL, gradient norm, opponent identity, matchup and caps. PPO updates are explicit calls, never side effects of importing a model.

This is a single-process baseline with variable-length minibatches. It is not a distributed high-throughput actor/learner system and has no automatic search or deck optimization.

## Saved runs and resume

Each launch makes a new directory under `runs/neural_ppo/`. Old runs and original models are preserved. Config, fixed deck panel, iteration game summaries and a final manifest are saved. Every fully saved iteration has a `training-000001.pt` file plus a `.json` SHA-256 receipt. Opponent snapshots and receipts are immutable siblings.

To resume, set `RESUME_CHECKPOINT` to that `.pt` file. Keep the seed, device, thread count, games per iteration, action limit, model, encoder, PPO settings and panel unchanged. Iterations means additional iterations. The checkpoint restores Adam, action/shuffle/opponent random streams, game scheduling offset and archived opponents. Resume makes a new directory and copies the verified archive. Keep the entire original run directory; the checkpoint alone is insufficient for league restoration. Checkpoint loading uses PyTorch's restricted `weights_only=True` deserializer and checks source/deck/config compatibility plus file hashes. Hashes detect corruption, not authorship; use trusted checkpoints.

Interrupting terminates the notebook's child process. The last fully saved iteration is recoverable; the interrupted iteration is lost. Same-platform/version resume state is supported; cross-platform bitwise reproducibility is not asserted.

## Validation and limits

Implementation checks start no self-play training or learning updates. Fixtures test loss arithmetic and synthetic derivatives without optimizer steps, variable candidate counts, observation coverage, UID normalization, history limits, cap handling, learner-only labels, fixed deck legality, exclusive checkpoint writes, integrity checking, and mocked iteration/resume orchestration. Opening-position inference checks perform initialization only, with no game actions.

Run the non-training fixtures with `make test-neural` and safe setup with `make neural-preflight`. Strict typing remains staged for the original public facade; neural modules have syntax, numerical and functional fixtures, not a claim of complete strict typing.

The owner has run bounded local training, but no independent expert-strength benchmark has been established. Full-game stability under these decks and learning quality must be measured when the owner launches training. The repaired engine passed 5,626 non-training checks; 39 neural fixtures passed. Those results establish internal regression coverage, not learning quality or independent game fidelity. The simulator's owner-authorized approximations and independent fidelity backlog remain. A policy may learn to exploit simulator discrepancies. Strong real Hearthstone play must be evaluated against independent opponents and game behavior, not inferred from self-play wins.
