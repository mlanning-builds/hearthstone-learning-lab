"""Read an existing owner diagnostic trace; never imports or starts a game."""
import argparse
import json
from pathlib import Path


def summarize(trace):
    lines = ["Owner trace: private diagnostic events; never policy inputs."]
    for event in trace.get("private_diagnostic", {}).get("events", []):
        lines.append("Turn " + str(event.get("turn", "?")) + " " + json.dumps(event, sort_keys=True))
    for action in trace.get("policy_visible", {}).get("actions", []):
        lines.append("Action " + json.dumps(action, sort_keys=True))
    lines.append("Result " + json.dumps(trace.get("outcome", {}), sort_keys=True))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    print(summarize(json.loads(args.trace.read_text())))


if __name__ == "__main__":
    main()
