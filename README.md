# cockpit-example-chain

A four-step analysis, run end to end through the
[Claude-Science-Cockpit](https://github.com/deathbychoco/claude-science-cockpit): every step
executed in one digest-pinned container, every result a signed foton, and the chain between them a
fact about the bytes rather than a note in a pipeline file.

```
data/raw.csv ──▶ qc ──▶ work/clean.csv ──┬──▶ eda   ──▶ work/summary.json
                       work/qc-report.json│
                                          └──▶ model ──▶ work/model.json
                                                         work/predictions.csv ──▶ viz ──▶ work/fit.svg
```

## Running it

```bash
./setup.sh                       # builds bin/, generates the identity, checks the binding
python3 tools/run-chain.py       # the four steps, through cockpit_publish
python3 tools/claim-reproduction.py
```

`setup.sh` expects sibling checkouts of `kton` and `claude-science-cockpit`, or `KTON_SRC` and
`COCKPIT_SRC` pointing at them. Docker must be running: this repo is configured to *run* its steps,
not merely record them.

## What is worth looking at

**The chain is nowhere declared.** `tools/run-chain.py` lists four independent steps. It never says
that eda follows qc. The link exists because qc names `work/clean.csv` as an output and eda names
the same path as an input, so the two fotons carry the same hash, and:

```
$ plankton lineage $(plankton hash work/fit.svg)
sha256:7ffc3060…  kind=script  in=3 out=1     # viz
sha256:2b45e4fd…  kind=script  in=2 out=2     # model
sha256:24bd59b8…  kind=script  in=2 out=2     # qc
```

eda is correctly absent: viz does not consume its output, so it is a branch off `clean.csv`, not a
link in this chain. A lineage that listed it would be describing the order someone ran things in,
which is not what a lineage is.

**Re-running changes nothing, and that is the result.** Run `tools/run-chain.py` twice: the foton
ids are identical, and the registry still holds four records rather than eight. A byte-identical
descriptor *is* the same foton — a second producer of the same work does not create a second
record, their signature joins the existing one. Reproducibility here is not a report that says
"matched"; it is the absence of a new record.

That only holds because the steps were written for it: fixed float formatting, sorted output, no
clock, no random seed, and SVG written from the numbers instead of a plotting library, whose PNGs
carry creation metadata and depend on font rasterisation. Two correct runs of a matplotlib figure
differ in bytes, and the reproduction check that should confirm the work would report a mismatch
instead.

**Each foton pins the environment it ran in.** `cockpit_publish` runs the command inside
`python@sha256:78387bc3…` and records that same reference — the string handed to docker and the
string in the foton are one string, so what ran and what is recorded cannot diverge. The pin is
COVERED: it is part of the foton's identity, so the same command in a different image is a
different foton, and a reproduction commits to re-executing in *this* environment.

The container has no network (`--network none`). A run that reaches the internet depended on
something the foton does not pin.

**`docs/data/` is the graph, published.** union.json, keys.json and names.json are regenerated after
every record and committed in the same commit as it, so what is online is never a record behind the
registry. Point a [kton-web](https://github.com/gitmick/kton-web) viewer at them, or serve them
locally:

```bash
bin/cockpit show --web ../kton-web
```

`keys.json` holds the trust tiers this repo *configures*, not every key lying in the registry — so a
viewer re-verifies against exactly what `cockpit_ask` does.

## What this example is not

The `reproduces` claim is signed by the same identity that produced the work. It demonstrates the
mechanism — cockpit_say runs `plankton reproduces` itself and records the level it computes, rather
than believing one it was handed — but a reproduction that *means* something comes from a different
party whose independently produced bytes agree with yours. Two participants doing that to each other
is what the cockpit's own `uat/setup.sh` walks through.

The data is synthetic and the model is a straight line fitted with four sums. Neither is the point;
the point is that both are reachable from the graph, byte for byte, in the environment they ran in.
