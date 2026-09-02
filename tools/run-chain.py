#!/usr/bin/env python3
"""Drive the four steps through the cockpit, over MCP.

The cockpit exposes exactly three verbs and only over MCP, so this speaks MCP rather than reaching
for the binaries: it is the same surface a Claude session gets, driven from a script so the example
is repeatable. Nothing here does any of the work — each cockpit_publish call runs the step inside
the pinned image, commits and pushes the files, signs the foton and regenerates the published union.

The chain is not declared anywhere. Step N names as its input the file step N-1 named as its
output, so the two fotons share a hash and the lineage is a fact about the bytes.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cockpit_client import Cockpit  # noqa: E402

STEPS = [
    {"name": "qc",
     "cmd": "python steps/qc.py",
     "inputs": ["steps/qc.py", "data/raw.csv"],
     "outputs": ["work/clean.csv", "work/qc-report.json"]},
    {"name": "eda",
     "cmd": "python steps/eda.py",
     "inputs": ["steps/eda.py", "work/clean.csv"],
     "outputs": ["work/summary.json"]},
    {"name": "model",
     "cmd": "python steps/model.py",
     "inputs": ["steps/model.py", "work/clean.csv"],
     "outputs": ["work/model.json", "work/predictions.csv"]},
    {"name": "viz",
     "cmd": "python steps/viz.py",
     "inputs": ["steps/viz.py", "work/predictions.csv", "work/model.json"],
     "outputs": ["work/fit.svg"]},
]


def main():
    c = Cockpit()
    previous_outputs = {}
    for step in STEPS:
        out = c.call("cockpit_publish", {"cmd": step["cmd"],
                                         "inputs": step["inputs"],
                                         "outputs": step["outputs"]})
        print(f"\n=== {step['name']} ===")
        print(f"  foton     {out['fotonId']}")
        print(f"  ran in    {out.get('executedIn', '(not run by the cockpit)')}")
        for path, h in sorted(out.get("outputHashes", {}).items()):
            # The join that makes this a chain: an output hash here reappears as an input hash of a
            # later step, and plankton finds the edge without being told about it.
            print(f"  output    {path}  {h}")
            previous_outputs[path] = h
        for line in out.get("stdout", "").splitlines():
            print(f"  said      {line}")
        # Only the cockpit can report this, and only when it ran the command itself: files the run
        # touched that this publish did not name. Not an error — a temp file is legitimate — but an
        # OUTPUT produced and not declared would otherwise be invisible until the chain failed to
        # join much later.
        for path in out.get("undeclaredChanges", []):
            print(f"  ALSO      {path}  (changed, not declared)")
    c.close()

    print("\nthe chain, by shared hash:")
    for step in STEPS[1:]:
        for i in step["inputs"]:
            if i in previous_outputs:
                print(f"  {step['name']:6s} consumes {i}  ({previous_outputs[i][:19]}…)")


if __name__ == "__main__":
    main()
