#!/usr/bin/env python3
"""Record a `reproduces` claim about the visualisation step, through the cockpit.

The point is not the claim but the check behind it: cockpit_say does not accept a level the caller
states. It runs `plankton reproduces` over the two output hashes itself and records what that
answers — hand it bytes that do not match and no claim is written at all.

Honest limit, since this example is one identity: a reproduction that means something comes from a
DIFFERENT party, whose independently produced bytes agree with yours. Here the same key signs both
sides, so this shows the mechanism and the precondition, not independent corroboration. Two
participants doing it to each other is what the cockpit's own uat/setup.sh walks through.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cockpit_client import Cockpit  # noqa: E402

c = Cockpit()
svg = c.hash("work/fit.svg")
producer = c.call("cockpit_ask", {"query": "producer", "ref": svg})["fotons"][0]["id"]

out = c.call("cockpit_say", {
    "subject": producer,
    "template": "reproduces",
    "subjectOutputHash": svg,
    "reproducedOutput": "work/fit.svg",
    "reproducedFotonId": producer,
})
print(f"claim  {out['claimId']}")
print(f"level  {out['level']}   (computed by the cockpit, not stated by this script)")
print(f"       {out['confirmation']}")
c.close()
