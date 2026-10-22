#!/bin/bash
# substd27: run every family, the API drivers and the CLI suite.
# usage: run_all.sh [PCREC]    (default: $PCREC, else the tree's build/pcrec)
# Writes $OUT_ROOT (scratch) and prints one summary line per suite.
# substfix (adoption): paths from the environment; the corpus TSVs are
# committed, so this no longer regenerates them (corpus/gen_*.py by hand).
set -u
S=$(cd "$(dirname "$0")" && pwd)
P=${1:-${PCREC:-$S/../../../build/pcrec}}
T=${TIMEOUT_BIN:-timeout}
export OUT_ROOT=${OUT_ROOT:-$(mktemp -d "${TMPDIR:-/tmp}/subst-d27.XXXXXX")}
mkdir -p "$OUT_ROOT"
for f in "$S"/corpus/d_*.tsv; do
  fam=$(basename "$f" .tsv | sed 's/^d_//')
  $T 3000 python3 "$S/lib/run_diff.py" "$f" --work "$OUT_ROOT/$fam" --pcrec "$P" > "$OUT_ROOT/diff_$fam.log" 2>&1
  echo "diff $fam: $(tail -1 "$OUT_ROOT/diff_$fam.log")"
done
OUT="$OUT_ROOT/api" $T 1800 sh "$S/api/build.sh" "$P" > "$OUT_ROOT/api.log" 2>&1
echo "api exit $?"
grep '^==' "$OUT_ROOT/api.log" | sed 's/^/api /'
OUT="$OUT_ROOT/cli" $T 1800 bash "$S/cli/cli.sh" "$P" > "$OUT_ROOT/cli.log" 2>&1
echo "cli: $(tail -1 "$OUT_ROOT/cli.log")"
