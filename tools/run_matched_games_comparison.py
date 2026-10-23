"""Owner starts training explicitly; the default only prepares and checks."""

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--train", action="store_true")
    p.add_argument("--config", default=str(ROOT / "configs/research_matched_games.json"))
    p.add_argument("--report", action="store_true")
    args = p.parse_args()
    from hearthstone_sim.research.matched_games.study import preflight

    if args.report:
        from hearthstone_sim.research.matched_games.study import read_config
        from hearthstone_sim.research.matched_games.report import build_report

        print(json.dumps(build_report(ROOT / read_config(args.config)["output"])))
        return
    if not args.train:
        print(json.dumps(preflight(args.config), indent=2))
        return
    from hearthstone_sim.research.matched_games.runner import run

    def emit(e):
        # Small stream: keep verbose per-case data in immutable study receipts.
        if e["event"] == "session_complete":
            e = {k: v for k, v in e.items() if k != "report"}
        if e["event"] == "evaluation_complete":
            e = {
                k: e[k]
                for k in (
                    "event",
                    "arm",
                    "milestone",
                    "budget_mode",
                    "actual_train_seconds",
                    "summary",
                    "tactics",
                    "searched_decisions",
                    "search_decisions",
                )
            }
        if e["event"] == "tactical_progress" and e.get("done", 0) % 16:
            return
        print(json.dumps(e), flush=True)

    run(args.config, allow_training=True, emit=emit)


if __name__ == "__main__":
    main()
