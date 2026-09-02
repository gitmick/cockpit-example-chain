"""Model: least squares of response on dose, in plain arithmetic.

No library, and that is deliberate rather than austere. The fit is four sums and a division, so the
result is a function of the input bytes and nothing else — no BLAS variant, no threading order, no
version of a solver that changed its tie-breaking between releases. The environment is pinned by
digest anyway; this makes the pin something the numbers do not actually depend on.
"""
import csv, json

xs, ys, subjects = [], [], []
with open("work/clean.csv", newline="") as f:
    for row in csv.DictReader(f):
        xs.append(float(row["dose_mg"]))
        ys.append(float(row["response"]))
        subjects.append(row["subject"])

n = len(xs)
mx, my = sum(xs) / n, sum(ys) / n
sxx = sum((x - mx) ** 2 for x in xs)
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
slope = sxy / sxx
intercept = my - slope * mx

ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
ss_tot = sum((y - my) ** 2 for y in ys)
r2 = 1 - ss_res / ss_tot

with open("work/model.json", "w") as f:
    json.dump({"form": "response ~ intercept + slope * dose_mg", "n": n,
               "intercept": round(intercept, 4), "slope": round(slope, 4),
               "r2": round(r2, 4), "residualSd": round((ss_res / n) ** 0.5, 4)},
              f, indent=2, sort_keys=True)
    f.write("\n")

with open("work/predictions.csv", "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["subject", "dose_mg", "observed", "predicted", "residual"])
    for s, x, y in zip(subjects, xs, ys):
        p = intercept + slope * x
        w.writerow([s, f"{x:.0f}", f"{y:.2f}", f"{p:.2f}", f"{y - p:.2f}"])

print(f"model: slope={slope:.4f} intercept={intercept:.4f} r2={r2:.4f} n={n}")
