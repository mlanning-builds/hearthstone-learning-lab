# Notebook 03: learn to play from scratch

Open `03_train_model.ipynb` in the existing Jupyter session and choose **Run → Run All Cells**. No new dependencies are needed. The default is 1,000 training games, plus separate evaluation games. A progress bar and monitoring curve update during the run. Actual time depends on the computer and other running work.

## Model and method

The model is a small **linear softmax policy**, not a neural network or language model. Its weights start as seeded Gaussian noise with standard deviation 0.01. All action preferences are learned; no expert moves or preselected strong decks are supplied. This is a deliberately modest first ML experiment that is inspectable and can run with the existing Python installation.

The policy scores each complete legal action from factual features: action kind, visible health/mana/board counts, friendly and enemy stats, its own rune profile, public keywords, card identity, target relationship, and mulligan costs. Some action/state interactions are explicit. Features are human-designed; this is not learning directly from pixels or raw card text. The model is memoryless and does not encode the full public history or complete starting deck, although those could be added later. It does not perform a search or simulate a candidate move before choosing it.

It uses episodic REINFORCE: accumulate the gradient of the log probability of each chosen move, then weight those gradients by the final game reward minus a running average for that opponent category. Win = +1, loss = -1, draw = 0. There are no rewards for damage, health, specific cards, or winning quickly. An entropy regularizer (default 0.01) encourages exploration independently of the game reward. An Adam optimizer applies one update per complete game, with a fixed gradient scale of 1/20 and norm clipping at 5. These stabilizers do not introduce expert action labels. The policy remains fixed during a game.

[OpenAI's introduction to policy optimization](https://spinningup.openai.com/en/latest/spinningup/rl_intro3.html) explains the underlying policy-gradient method. This project implements its own small policy and analytic gradients in ordinary Python; it is not using the Spinning Up software package.

## Opponents and card pools

- The first 250 games use a random legal-action opponent.
- After that, each training game independently chooses a random opponent or a frozen recent policy checkpoint with equal probability.
- The frozen opponent refreshes every 250 completed training games. It never updates inside a game. Only the learner's actions contribute gradients.
- Training, monitoring, and final tests each have 20 independently generated decks, two per rune profile, with an explicit overlap check.
- The 33-card simulator subset is unchanged. This trains **playing skill**, not deck construction. It does not find the best deck yet.

All policies receive `Game.observe` output; neither policy receives the mutable `Game`, opponent hand, opponent rune allocation, or shuffled deck orders. The learner's own hand and public board are encoded into features. The simulator and policies have separate random streams.

## Evaluation

Before training and after each 250-game block, freeze the learner and play 100 monitoring games against random play. Monitoring uses the same fixed deck pool and game seeds across checkpoints to make comparisons easier. These observations are never used for gradients, early stopping, or automatic best-model selection. The displayed line can go down; improvement is not assumed.

After the requested training count, use a separate test deck pool and seeds for 100 games against random play and 100 against the untrained initial model. The model and optimizer remain unchanged during every evaluation. The reported model is the latest model, not the checkpoint with the prettiest score.

Each evaluation pairing uses two games with starting player reversed. Win rate means outright wins divided by all games; draws count as non-wins. Draw-adjusted score is saved separately. The 95% bounds are conservative Hoeffding bounds on independent **pair averages**, so they do not treat the two correlated games within a pair as independent. They describe uncertainty within this experiment's fixed deck distribution, not generalization to full Hearthstone. Multiple monitoring points are not a simultaneous confidence claim. Repeatedly inspecting final tests and manually tuning settings would make those tests part of development; a later serious comparison should use newly held-out seeds and decks.

## Saving and continuation

`runs/training_<fingerprint>/checkpoint.json` is atomically updated after every completed game. It contains weights, Adam state, running baselines, frozen/initial opponents, results, and monitoring history. Each game has its own deterministic seed. An interrupted or failed update is discarded by reloading the last completed checkpoint. A half-played game is rerun on resume.

Rerun with identical settings to resume. **Increase `TRAINING_GAMES` from 1,000 to 2,000 to continue the same model.** Changing the seed, learning rate, evaluation settings, implementation, or card data creates a new run. Lowering the target does not undo completed training. End-of-run weights are also exported as `model_001000.json` (or the corresponding game count), preserving prior exports when you continue.

Training fingerprinting lives in `learner/`; it does not alter the existing engine or invalidate notebook 02's saved replays. `lab.train()` is an older explicit placeholder; the supported entry point for this notebook is `learner.training.train`.

## Checks and limitations

Tests verify analytic gradients against numerical finite differences, increasing the likelihood of a rewarded action, finite/stable probabilities, legal action sampling, observation-only features, disjoint deck pools, evaluation without updates, save/load, and exact checkpoint continuation. An interrupted run and a resumed run must reach identical weights and optimizer state to an uninterrupted run.

The simulator has card fixtures and random-game checks, but still lacks independent live-client validation. The model can learn weaknesses in a limited simulator or random opponent. Winning these games does not establish ladder skill, strong deckbuilding, or the best rune configuration. Later work should validate additional interactions, expand cards and opponents, add richer models/history, and only then begin deck mutation experiments.
