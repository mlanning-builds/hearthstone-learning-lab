# Hearthstone learning lab

> Current work: [all-card completion queue](docs/engine-audit/completion-queue.md) and [candidate status](staging/rebased-88/STATUS.md). Full card integration, production generation pools and independent rules validation remain unfinished.

A hobby project to recreate regular Hearthstone Standard for local self-play learning and deck search. The intended scope is all 11 classes and the full pinned card pool, excluding Mercenaries and Battlegrounds. **Full Standard simulation and an all-card learning player are not finished.** No current result establishes the best Standard deck or strategy.

Current [scope ledger and shared-rule backlog](docs/engine-audit/scope-2026-09-23/CHECKPOINT.md) accounts for every frozen catalog card and distinguishes written effects from verified behavior.

Run [notebook 13](notebooks/13_shared_rules_checks.ipynb) for candidate rules checks. Local validation receipts and their exact source fingerprints are recorded in the [candidate status](staging/rebased-88/STATUS.md).

The latest production integrations connect Khadgar, the Gnomeregan/Silvermoon location chains, Beatrix, Azalina, Warptooth, Husk, Champion, Godfrey, Chef, the Blood Fighter bundle, Irida and Primalfin Challenger. Their independent interaction review remains provisional; staged recipes are excluded from training decks. See the [location admission evidence](docs/engine-audit/closed-admission-2026-10-06.json) and [construction/zone admission evidence](docs/engine-audit/constructed-zone-admission-2026-10-06.json).

A bounded candidate experiment completed eleven self-play games with eleven learning updates across all classes. Its [saved manifest](runs/candidate_training/68f0ff76cc7542a9bca40a993b6a8b32/manifest.json) records the source fingerprint and immutable checkpoints. A [ten-game deck search](runs/deck_search/7d55346e0a0742b583b4700fb3fa5451/manifest.json) exercised Beatrix and Azalina construction inputs, including a separate held-out evaluation. These archived runs precede the Blood Fighter admission and remain tied to their recorded source fingerprint. These are pipeline checks, not evidence of playing strength or deck optimality.

## Where the work lives

| Component | Purpose | Status |
| --- | --- | --- |
| `engine/`, `learner/`, notebooks 01–03 | Original 33-card Death Knight learning experiment | Preserved; its results do not rank Standard decks |
| `expanded/`, notebook 08 | Active simulator workbench | Explicitly implemented cards only; notebook remains unchanged by candidate work |
| `staging/rebased-88/` | Current all-class development candidate | Directory name is historical; use its [generated status](staging/rebased-88/STATUS.md) for current counts and test evidence |
| notebook 09 | Bounded random-game candidate validation | Progress display and saved failure replays; no training |
| notebook 10 | Record candidate games | Saves trajectories; no learning |
| notebook 11 | Train the experimental candidate policy | Explicit local run budgets; resumable checkpoints |
| notebook 12 | Compare decks with frozen policies | Explicit opponent panel; no training or global-best claim |
| notebook 14 | Search candidate decks with frozen policies | Bounded legal neighbors, separate held-out seeds, saved reports |

The frozen snapshot contains 1,185 collectible records at patch **36.6.0.251952**, cutoff **2026-09-18**. Imported records are not executable card effects. Live legality, special deck construction, generated dependencies and interaction fidelity still need review. See the [roadmap](docs/ROADMAP.md), [coverage inventory](docs/coverage/README.md) and [candidate notes](staging/rebased-88/README.md).

## Open Jupyter

From this project folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyterlab notebooks/09_candidate_random_validation.ipynb
```

The code has been exercised locally with Python 3.9.6. The [observed environment snapshot](environment/README.md) records exact installed versions and provides a drift check; it is not yet a verified fresh-install lockfile. The simulator and validation tools use Python's standard library; JupyterLab is needed for the notebook interface. A fresh online Jupyter installation on another computer has not yet been verified. Restart the notebook kernel after code updates.

Notebook 09 defaults to 11 candidate games, capped at 500 actions each. `CHECK_POLICY_FEATURES = True` also checks that every decision can be encoded for the learner, without updating weights. It does not train. Notebook 08 uses the active root engine, so its counts intentionally differ from candidate status. Notebook 03 starts the original subset training loop; use it only if you intend to train that older experiment.

## Run local checks without Jupyter

Candidate random-play validation, from the project root:

```sh
.venv/bin/python tools/stress_candidate.py --engine-root staging/rebased-88 --seeds 1 --max-actions 500
.venv/bin/python -m unittest discover -s tests/tools
```

The complete candidate rules suite must run from the candidate folder to import the correct engine:

```sh
cd staging/rebased-88
../../.venv/bin/python -c 'from expanded.status import run_rule_fixtures; r=run_rule_fixtures(); print(r); raise SystemExit(not r["success"])'
```

Before running the suite after a registry change, use `.venv/bin/python tools/sync_candidate_inventory.py --engine-root staging/rebased-88` to detect coverage-ledger drift. Add `--write` to reconcile those derived ledgers after the reviewed registry validates; this does not register cards or approve effects.

Run `tools/record_candidate_progress.py` from the project root after a passing candidate suite to update its status; it rejects stale receipts. Saved reports live under `runs/` directories and include source fingerprints. They are local evidence and are excluded from Git by default. A passing test suite or error-free random game batch does not establish complete Hearthstone correctness.

## Reproduction and GitHub status

The candidate shares the frozen data through a **relative** `../../data` link. Preserve the repository layout when copying it; the candidate is not a standalone package. Snapshot provenance and data hashes live in `data/standard/manifest.json`.

This folder has not been published as a repository. Remaining publication work includes a software license decision, cross-platform dependency verification (same-platform fresh installation and bounded notebook relocation checks pass), and selecting reproducible reports to distribute. The project contains Blizzard game data and is an unofficial fan experiment; a software license has not been chosen. [HearthstoneJSON documentation](https://hearthstonejson.com/docs/cards.html) describes the data source.

## Historical subset experiment guide

The following instructions describe the preserved original experiment, not the current Standard candidate.

## Experiment boundaries

- A frozen 117-card Core pool from HearthstoneJSON, downloaded September 18, 2026: Death Knight and neutral minions, spells, weapons, and locations.
- This is a subset experiment, not the full Standard format. Set membership comes from the source data. Live patch legality, temporary bans, and release status have not been independently verified.
- Deck checks enforce 30 cards, pool membership, rune compatibility, and copy limits (one legendary, two otherwise). Deck size overrides, sideboards, and other exceptional construction mechanics are outside this initial scope; audit the pool before treating output as game-importable decks.
- Random sampling uses available card copies. It is not mathematically uniform over all possible deck multisets. There are no manually chosen mana curves or card-strength scores.
- The mana curve output describes the starting population; it is not evidence of learning.

## Notebook 02: play random matches

Set `NUMBER_OF_GAMES = 100`, `DECKS_PER_RUNE_PROFILE = 2`, and `RANDOM_SEED = 42`, then Run All. The notebook checks the rules, creates 20 decks, plays 100 games, and displays a progress bar, summary, and sample turn log. It requires an even game count to balance initiative in each pairing.

Completed matches are saved after each game. Rerun with identical settings to resume; change the seed for a new experiment. The first replay is verified by reproducing its action sequence and event log. Errors stop the run instead of being counted as match results.

The playable pool contains **33 of the original 117 catalog cards**. Every included effect is explicit; the other 84 cards are rejected. This subset favors simpler effects and is not suitable for ranking Standard decks or rune combinations. See [simulator scope and validation](docs/simulator.md).

## Notebook 03: train a model

Open `03_train_model.ipynb` and Run All. Defaults: 1,000 training games, evaluation every 250 games, 100 games per evaluation. It uses your existing Jupyter installation without additional packages.

The model is a small linear softmax policy with random initial weights, trained with episodic REINFORCE and Adam. It learns only from game outcomes, with an exploration regularizer. Training mixes random opponents with frozen self-play checkpoints after an initial 250-game warmup. Monitoring and final tests use separate deck pools and seeds, never training updates. This is playing-skill learning, not deck optimization.

A progress bar and learning curve update throughout. Checkpoints save after every completed game. To continue, increase `TRAINING_GAMES` from 1,000 to 2,000 and rerun. Change the seed for a fresh model. See [training methodology](docs/training.md) for the exact features, reward, evaluation bounds, and continuation behavior.

The simulator is scenario-tested but has not been independently cross-validated against the live client. A high win rate against random play is a first benchmark, not proof of strong ladder play. Later work will add richer policies, more card coverage, and deck evolution.

## Files

- `lab.py`: deck generation, validation, inspection, and a training placeholder.
- `engine/`: game rules, explicit card support, paired experiments, replays, and notebook progress display.
- `notebooks/01_random_decks.ipynb`: inspect a random starting population.
- `notebooks/02_play_games.ipynb`: run complete random matches with one Run All.
- `notebooks/03_train_model.ipynb`: train, evaluate, inspect, and resume a learned policy.
- `learner/`: feature encoding, policy gradients, optimizer, evaluation, checkpoints, and notebook display.
- `data/core_pool.json`: frozen input, never silently refreshed.
- `data/provenance.json`: source URL, date, scope, SHA-256 hashes.
- `tests/`: card and combat fixtures, hidden-information checks, deck validation, all-rune game checks, replay verification, and checkpoint resumption.


### Record experimental candidate games

Open `notebooks/10_record_candidate_games.ipynb` after checking readiness in 09.
Set `EPISODES`, `MAX_ACTIONS`, and `SEED`, then run the recording cell. Progress
and saved-file locations are printed. Random policies play implemented candidate
decks; this is data-pipeline validation, not training or deck-strength evidence.
Each run has a unique folder under `runs/candidate_trajectories`, with per-game
JSONL files, checksums and a manifest. Incomplete/capped outcomes are explicitly
separated from terminal game labels. Never feed replay-only deck headers to a
model. Existing notebooks and the active engine are preserved.

### Experimental policy training notebook

Open `notebooks/11_train_candidate_policy.ipynb` after reviewing candidate readiness
in notebook 09. Set episode/action budgets, seed and learning rate, then run the
last cell. It starts a fresh sparse policy, trains via bounded self-play, displays
completion progress and saves immutable per-episode checkpoints with results and
replay deck definitions. Capped games do not produce learning labels. The child
process terminates when the notebook cell is interrupted. Each run has a unique
folder under `runs/candidate_training`; set `RESUME_RECEIPT` to continue from a saved episode with unchanged settings.
The engine/card pool is incomplete and these models cannot certify the best
Standard deck or strategy. No long training experiment has been launched.

Training resume continues class/deck seeds, starting-player alternation and
policy sampling from the saved episode. `EPISODES` means additional games.
The runner requires matching seed, learning rate, action cap, engine fingerprint,
feature schema and runner source checksum, and verifies the checkpoint checksum.
A resumed run writes to a new folder and records its parent receipt. Interrupted
games restart from the last saved episode, not from a mid-game state.

Notebook `12_compare_candidate_decks.ipynb` compares explicit decks with frozen
models from training episode receipts. Set checkpoint receipt paths and explicit
seed/game/action budgets; no model weights update. It writes the input plan,
checkpoint identities, runner hash, report and checksum receipt to a unique run
folder. Scores concern only the supplied opponent panel; full Standard and
global deck optimality remain unproven.

Notebook `14_search_candidate_decks.ipynb` connects local deck proposals to frozen-policy evaluation. Set two training receipt paths, search and held-out seeds, neighbor/round counts, and the total game budget. The runner reserves both starting-player orders for every round and the final baseline comparison before playing. It keeps the incumbent on tied scores and withholds a completed selection if any required game is capped. Each run saves its input plan, round reports, held-out evaluation and source-bound manifest under `runs/deck_search`.

The candidate also registers 229 generated-only historical identities. These are excluded from Standard decks and do not enable historical generation pools. See the [historical membership planning inventory](docs/engine-audit/historical-outcome-planning-2026-10-06.json) and [Blood Fighter admission evidence](docs/engine-audit/blood-fighter-admission-2026-10-06.json).
