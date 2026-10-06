# Contributing

The immediate goal is completing the frozen Standard simulator and its generated dependencies. Read the README, current candidate status, completion queue, and known fidelity gaps before choosing a card or shared mechanic.

## Set up

Create a virtual environment and install requirements.txt. Preserve the repository layout and frozen data. Use notebooks 09–14 for current candidate work.

## Change a rule

1. Ground the behavior in the pinned record and independent evidence where available.
2. Implement the explicit effect and every required token or generated dependency.
3. Add a meaningful paid-play or interaction scenario. A declaration alone is not card support.
4. Check hidden-information boundaries, physical card state, and deterministic replay.
5. Run focused checks, then the full candidate suite for a candidate behavior change.

Do not silently filter unsupported outcomes from generation pools. Keep unknown membership, probability distributions, and interaction assumptions visible.

## Run checks without training

From the repository root:

```sh
python -m unittest discover -s tests/tools
python -m unittest discover -s tools/tests
python tools/sync_candidate_inventory.py --engine-root staging/rebased-88
```

From staging/rebased-88, using the repository virtual environment:

```sh
../../.venv/bin/python -c 'from expanded.status import run_rule_fixtures; r=run_rule_fixtures(); print(r); raise SystemExit(not r["success"])'
```

Training and deck-search experiments are run manually by the project owner in Jupyter. Do not launch them as part of checks or CI. Never commit local model files, run folders, credentials, or notebook outputs.

Pull requests should explain the changed behavior, the scenarios checked, and any remaining fidelity limits. Keep changes focused and preserve the original experiment for provenance.
