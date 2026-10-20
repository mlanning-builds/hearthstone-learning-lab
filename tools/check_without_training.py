"""Run rule/tool checks without invoking training integration scenarios."""
import argparse
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"test_training_resume", "test_expanded_training", "test_expanded_learning_core"}


def without_training(suite):
    result = unittest.TestSuite()
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            result.addTests(without_training(item))
        elif item.__class__.__module__.split(".")[-1] not in EXCLUDED:
            result.addTest(item)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("supporting", "candidate"), required=True)
    parser.add_argument("--workers", type=int, choices=range(1,9), default=1, help="Independent rule workers; default preserves sequential execution")
    parser.add_argument("--progress", action="store_true", help="Print completed rule cases as workers finish; does not start training")
    args = parser.parse_args()
    if args.suite == "candidate":
        candidate = ROOT / "staging/rebased-88"
        sys.path.insert(0, str(candidate))
        from expanded.status import run_rule_fixtures
        def progress(completed,total,failures,errors):
            print(f"Rule fixtures: {completed}/{total}; failures={failures}; errors={errors}", flush=True)
        report = run_rule_fixtures(workers=args.workers, progress=progress if args.progress else None)
        print(report, flush=True)
        return 0 if report["success"] else 1
    else:
        sys.path.insert(0, str(ROOT))
        tests = ROOT / "tests/tools"
        pattern = "test_*.py"
    suite = unittest.defaultTestLoader.discover(str(tests), pattern=pattern)
    filtered = without_training(suite)
    print("Rule/tool checks only; training integration scenarios excluded.", flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(filtered)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
