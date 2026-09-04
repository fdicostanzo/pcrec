#!/usr/bin/env bash
# gen_base.sh -- regenerates studies/form_char_twins/base/*.c from a real
# build/pcrec, the six base artifacts twin_A.py/twin_B.py/twin_C.py/
# twin_D.py read. See README.md for the recipe table and what each
# artifact exercises; docs/dev/form_char_step0.md for the design.
#
# PCREC defaults to the repo's own build/pcrec, two levels up from this
# study. BENCH_CI256 defaults to pcrec-bench's altwide corpus (read-only,
# per the project's scope mandate -- CLAUDE.md); if it is not present the
# ci-256 base artifact is skipped with a warning rather than failing the
# whole run, since every OTHER base artifact needs nothing from pcrec-bench.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
PCREC="${PCREC:-$REPO_ROOT/build/pcrec}"
BENCH_CI256="${BENCH_CI256:-$REPO_ROOT/../pcrec-bench/bench/altwide/patterns/ci-256.rx}"
OUT="$HERE/base"

if [ ! -x "$PCREC" ]; then
    echo "gen_base.sh: $PCREC not found or not executable -- build it first (make -C $REPO_ROOT)" >&2
    exit 1
fi

mkdir -p "$OUT"

echo "== family A: VM literal chain, caseless, 6 sites =="
"$PCREC" -p rxA -i --engine=vm --emit-main -o "$OUT/A_abcdef.c" 'abcdef'

echo "== family B: general class [a-zA-Z0-9_], 1 site =="
"$PCREC" -p rxG --engine=vm --emit-main -o "$OUT/B_general.c" '[a-zA-Z0-9_]'

echo "== family B: sparse class [aeiou], 1 site =="
"$PCREC" -p rxS --engine=vm --emit-main -o "$OUT/B_sparse.c" '[aeiou]'

echo "== family C: DFA scan edge, small witness (?i)a{2,40}Z =="
"$PCREC" -p rxSM --engine=dfa --no-captures --emit-main -o "$OUT/C_small.c" '(?i)a{2,40}Z'

echo "== family C: DFA scan edge, NON-fold-pair witness [ace]{2,40}Z =="
"$PCREC" -p rxNP --engine=dfa --no-captures --emit-main -o "$OUT/C_nonpair.c" '[ace]{2,40}Z'

if [ -f "$BENCH_CI256" ]; then
    echo "== family C: DFA scan edge, ci-256 (pcrec-bench, read-only) =="
    CI256="$(cat "$BENCH_CI256")"
    "$PCREC" -p rxCI --emit-main -o "$OUT/C_ci256.c" -- "$CI256"
else
    echo "gen_base.sh: $BENCH_CI256 not found -- skipping the ci-256 base artifact (pcrec-bench sibling repo not present)" >&2
fi

echo "== family D: N=16 many-class atom-table crossover witness =="
"$PCREC" -p rxD16 -i --engine=vm --emit-main -o "$OUT/D_n16.c" 'abcdefghijklmnop'

echo "gen_base.sh: done -- $OUT/*.c"
