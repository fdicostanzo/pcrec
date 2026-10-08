#!/usr/bin/env bash
# [DEC-FALLBACK] STEP 0: build the probed scratch compilers and run the census
# over the whole .rxt corpus for every variant. Scratch only (build/decfb0/);
# nothing under src/ changes. ~1 min at -j6. usage: run_census.sh  (from the repo root)
set -eu
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
D="$ROOT/docs/design/decision_families/decfb0"
S="$ROOT/build/decfb0"; mkdir -p "$S"
python3 "$D/build_ref.py" "$S"
for v in plain lowsize lowdfa lowboth; do python3 "$D/census.py" "$ROOT" "$S" "$v" 1; done
python3 "$D/summarize.py" "$S" plain lowsize lowdfa lowboth > "$D/results.md"
echo "BYTES_DIFF rows (probed vs unprobed build/pcrec, plain): $(grep -c BYTES_DIFF "$S/census_plain.tsv" || true)"
