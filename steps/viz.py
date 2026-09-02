"""Visualisation: the observations and the fitted line, as hand-written SVG.

SVG rather than a plotting library, for the reason the whole example exists to show. A PNG from a
plotting stack carries creation metadata and depends on font rendering and rasterisation, so two
correct runs differ in bytes and the reproduction check that should confirm the work instead
reports a mismatch. Text written from the numbers is a function of its inputs alone.

The output is therefore reproducible in the strong sense: another party who re-runs this step
against the same predictions gets the same bytes, and a `reproduces` claim about it is L0.
"""
import csv, json

W, H, PAD = 720, 420, 56

pts = []
with open("work/predictions.csv", newline="") as f:
    for row in csv.DictReader(f):
        pts.append((float(row["dose_mg"]), float(row["observed"])))
model = json.load(open("work/model.json"))

xmin, xmax = min(x for x, _ in pts), max(x for x, _ in pts)
ymin, ymax = min(y for _, y in pts), max(y for _, y in pts)
ypad = (ymax - ymin) * 0.08
ymin, ymax = ymin - ypad, ymax + ypad

def sx(x): return PAD + (x - xmin) / (xmax - xmin) * (W - 2 * PAD)
def sy(y): return H - PAD - (y - ymin) / (ymax - ymin) * (H - 2 * PAD)

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="#fbfbfa"/>',
       f'<line x1="{PAD}" y1="{H-PAD}" x2="{W-PAD}" y2="{H-PAD}" stroke="#333"/>',
       f'<line x1="{PAD}" y1="{PAD}" x2="{PAD}" y2="{H-PAD}" stroke="#333"/>']

for x in sorted({x for x, _ in pts}):
    out.append(f'<text x="{sx(x):.1f}" y="{H-PAD+18:.1f}" font-family="sans-serif" font-size="11" '
               f'text-anchor="middle" fill="#333">{x:.0f}</text>')

# Points sorted, so the element order is a function of the data rather than of dict iteration.
for x, y in sorted(pts):
    out.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="3" fill="#2b6cb0" fill-opacity="0.55"/>')

y0 = model["intercept"] + model["slope"] * xmin
y1 = model["intercept"] + model["slope"] * xmax
out.append(f'<line x1="{sx(xmin):.1f}" y1="{sy(y0):.1f}" x2="{sx(xmax):.1f}" y2="{sy(y1):.1f}" '
           f'stroke="#c05621" stroke-width="2"/>')
out.append(f'<text x="{PAD}" y="{PAD-20:.0f}" font-family="sans-serif" font-size="14" fill="#111">'
           f'response ~ {model["intercept"]:.1f} + {model["slope"]:.3f} · dose_mg'
           f'  (n={model["n"]}, r²={model["r2"]:.3f})</text>')
out.append(f'<text x="{W/2:.0f}" y="{H-16}" font-family="sans-serif" font-size="12" '
           f'text-anchor="middle" fill="#333">dose_mg</text>')
out.append("</svg>")

with open("work/fit.svg", "w") as f:
    f.write("\n".join(out) + "\n")

print(f"viz: {len(pts)} points, fitted line, {sum(len(l) for l in out)} bytes of svg")
