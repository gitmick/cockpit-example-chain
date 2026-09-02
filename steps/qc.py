"""Data QC: drop what cannot be analysed, and say what was dropped and why.

Every rejection is counted by reason rather than silently filtered. A QC step that only emits the
clean data leaves the next step unable to tell "there was nothing to drop" from "the rule never
fired", and a reader unable to tell either.

Deterministic by construction: input order is preserved, floats are formatted to a fixed number of
places, and nothing here reads a clock or a random seed. Two runs produce identical bytes, which is
what makes the resulting foton reproducible rather than merely signed.
"""
import csv, json

MISSING = "response missing"
SENTINEL = "response is the -999 not-measured sentinel"
IMPOSSIBLE = "weight is zero, which no subject has"

kept, dropped = [], {MISSING: 0, SENTINEL: 0, IMPOSSIBLE: 0}

with open("data/raw.csv", newline="") as f:
    for row in csv.DictReader(f):
        if row["response"] == "":
            dropped[MISSING] += 1
        elif float(row["response"]) == -999:
            dropped[SENTINEL] += 1
        elif float(row["weight_kg"]) == 0:
            dropped[IMPOSSIBLE] += 1
        else:
            kept.append(row)

with open("work/clean.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["subject", "dose_mg", "weight_kg", "response"], lineterminator="\n")
    w.writeheader()
    for row in kept:
        w.writerow({"subject": row["subject"], "dose_mg": row["dose_mg"],
                    "weight_kg": f'{float(row["weight_kg"]):.1f}',
                    "response": f'{float(row["response"]):.2f}'})

with open("work/qc-report.json", "w") as f:
    json.dump({"read": len(kept) + sum(dropped.values()), "kept": len(kept),
               "dropped": dropped}, f, indent=2, sort_keys=True)
    f.write("\n")

print(f"qc: {len(kept)} kept, {sum(dropped.values())} dropped")
