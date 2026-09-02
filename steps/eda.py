"""EDA: per-dose summaries of the cleaned data.

Reads only what QC produced, never data/raw.csv. That is the whole point of a chain: this step's
input hash is the previous step's output hash, so the lineage is a fact about the bytes rather than
a claim about the order someone ran things in.
"""
import csv, json
from statistics import mean, pstdev

by_dose = {}
with open("work/clean.csv", newline="") as f:
    for row in csv.DictReader(f):
        by_dose.setdefault(int(row["dose_mg"]), []).append(float(row["response"]))

summary = {
    "n": sum(len(v) for v in by_dose.values()),
    "byDose": {
        str(d): {"n": len(v), "mean": round(mean(v), 3), "sd": round(pstdev(v), 3),
                 "min": round(min(v), 2), "max": round(max(v), 2)}
        for d, v in sorted(by_dose.items())
    },
}
with open("work/summary.json", "w") as f:
    json.dump(summary, f, indent=2, sort_keys=True)
    f.write("\n")

print("eda: " + ", ".join(f"{d}mg n={s['n']} mean={s['mean']}" for d, s in summary["byDose"].items()))
