#!/bin/bash
# substd27: regenerate the corpus, run every family, the API drivers and the CLI suite.
# usage: run_all.sh [PCREC]    (default: the substd27 cell's build/pcrec)
# Writes out/ (scratch) and prints one summary line per suite.
set -u
S=$(cd "$(dirname "$0")" && pwd)
P=${1:-/home/pcrec/projects/pcrec/worktrees/substd27-cell/build/pcrec}
export OUT_ROOT=${OUT_ROOT:-$S/out}
mkdir -p "$OUT_ROOT"
timeout 60 python3 "$S/corpus/gen_corpus.py" > /dev/null
timeout 60 python3 "$S/corpus/gen_fuzz.py" 600 2627 > /dev/null
for f in "$S"/corpus/d_*.tsv; do
  fam=$(basename "$f" .tsv | sed 's/^d_//')
  timeout 3000 python3 "$S/lib/run_diff.py" "$f" --work "$OUT_ROOT/$fam" --pcrec "$P" > "$OUT_ROOT/diff_$fam.log" 2>&1
  echo "diff $fam: $(tail -1 "$OUT_ROOT/diff_$fam.log")"
done
OUT="$OUT_ROOT/api" timeout 1800 sh "$S/api/build.sh" "$P" > "$OUT_ROOT/api.log" 2>&1
grep '^==' "$OUT_ROOT/api.log" | sed 's/^/api /'
OUT="$OUT_ROOT/cli" timeout 1800 bash "$S/cli/cli.sh" "$P" > "$OUT_ROOT/cli.log" 2>&1
echo "cli: $(tail -1 "$OUT_ROOT/cli.log")"
