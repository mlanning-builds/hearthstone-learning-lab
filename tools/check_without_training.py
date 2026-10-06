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
    args = parser.parse_args()
    if args.suite == "candidate":
        candidate = ROOT / "staging/rebased-88"
        sys.path.insert(0, str(candidate))
        tests = candidate / "tests"
        pattern = "test_expanded*.py"
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
