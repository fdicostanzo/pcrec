#!/usr/bin/env bash
# docs/design/memfn/r17b_prime/fdb2/sabotage/run_skb2.sh [OUTDIR] -- runs each
# SKB2-*.sh plant here SOLO, the matrix's way (tests/mech/run_sabotage_matrix.sh
# header): a fresh `git archive HEAD` tree per plant, the edit through
# tests/mech/lib/replace.py (refused unless the anchor appears SAB_COUNT
# times), `make -j4`, then the row's suite (memfnfinder =
# tests/memfn/run_finder.sh). DETECTED iff the suite fails. The plants carry
# PLACEHOLDER ids (SKB2-n): main allocates real ids and moves them into
# tests/mech/sabotages/, where the matrix runs them.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
OUT="${1:-$ROOT/build/land/skb2}"
mkdir -p "$OUT"
for f in "$HERE"/SKB2-*.sh; do
    id=$(basename "$f" .sh)
    t="$OUT/$id"; rm -rf "$t"; mkdir -p "$t/tree"
    git -C "$ROOT" archive HEAD | tar -x -C "$t/tree"
    ( . "$f"
      printf '%s' "$SAB_BEFORE" > "$t/before"; printf '%s' "$SAB_AFTER" > "$t/after"
      python3 "$ROOT/tests/mech/lib/replace.py" "$t/tree/$SAB_FILE" "$t/before" "$t/after" "${SAB_COUNT:-1}" ) \
        > "$t/apply.log" 2>&1 || { echo "$id APPLY-FAILED"; continue; }
    if ! (cd "$t/tree" && gnutimeout 900 make -j4 > "$t/build.log" 2>&1); then echo "$id BUILD-FAILED (DETECTED by the build)"; continue; fi
    (cd "$t/tree" && TMPDIR="$t" gnutimeout 900 bash tests/memfn/run_finder.sh > "$t/suite.log" 2>&1); rc=$?
    nf=$(grep -E '^checks failed:' "$t/suite.log" | awk '{s+=$3} END {print s+0}')
    if [ "$rc" -ne 0 ]; then echo "$id DETECTED (memfnfinder rc=$rc, $nf checks failed)"; else echo "$id NOT-DETECTED"; fi
    rm -rf "$t/tree"
done
