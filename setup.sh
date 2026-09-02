#!/usr/bin/env bash
# Build what this repo does not vendor, and check the binding before anything runs.
#
# bin/ is gitignored on purpose. Vendoring the kernel is how a checkout ends up two minor versions
# behind without anyone noticing, and an old binary reads a current store as EMPTY while exiting 0 —
# it reports "nothing is recorded" where the truthful answer is "I cannot read this store".
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
KTON_SRC=${KTON_SRC:-$(dirname "$HERE")/kton}
COCKPIT_SRC=${COCKPIT_SRC:-$(dirname "$HERE")/claude-science-cockpit}

[ -d "$KTON_SRC/reference/cmd/plankton" ] || { echo "no kton checkout at $KTON_SRC (set KTON_SRC)" >&2; exit 1; }
[ -d "$COCKPIT_SRC/cmd/cockpit" ] || { echo "no cockpit checkout at $COCKPIT_SRC (set COCKPIT_SRC)" >&2; exit 1; }

mkdir -p "$HERE/bin"
(cd "$KTON_SRC" && go build -o "$HERE/bin/plankton" ./reference/cmd/plankton)
(cd "$KTON_SRC" && go build -o "$HERE/bin/nekton"   ./nekton/reference/cmd/nekton)
(cd "$KTON_SRC" && go build -o "$HERE/bin/kton"     ./kton/reference/cmd/kton)
(cd "$COCKPIT_SRC" && go build -o "$HERE/bin/cockpit" ./cmd/cockpit)

cd "$HERE"
if [ ! -f keys/session-1.key ]; then
  # Never regenerate an existing identity: it would orphan every record already signed under it.
  bin/plankton keygen keys/session-1
  bin/nekton keygen keys/session-1-claims
  cp keys/session-1.pub keys/session-1-claims.pub registry/keys/
fi
exec bin/cockpit doctor
