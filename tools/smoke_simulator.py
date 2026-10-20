"""Fast bounded rule sanity check through the active public API; no learning."""
from dataclasses import asdict
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def main() -> int:
    from hearthstone_sim import Action, Game
    from hearthstone_sim.status import code_fingerprint
    from simulator_workflow import benchmark_decks, preflight
    from stress_candidate import validate_observations

    before = code_fingerprint()
    decks = benchmark_decks()
    scope = preflight(decks)
    if not scope["known_checks_passed"]:
        raise AssertionError(scope)
    game = Game(decks, seed=97, record=False)
    game.step(Action("mulligan"))
    game.step(Action("mulligan"))
    validate_observations(game)
    from copy import deepcopy
    clone = deepcopy(game)
    for _ in range(12):
        if game.terminal:
            break
        legal = game.legal_actions()
        action = next((a for a in legal if a.kind == "play"), legal[-1])
        game.step(action)
        clone.step(action)
        game.assert_invariants()
        validate_observations(game)
        if game.observe(game.current) != clone.observe(clone.current):
            raise AssertionError("Deterministic replay diverged")
    if before != code_fingerprint():
        raise AssertionError("Source changed during smoke check")
    print(json.dumps({"smoke": "passed", "decks": [asdict(d) for d in decks],
                      "fingerprint": before, "training_executed": False}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
