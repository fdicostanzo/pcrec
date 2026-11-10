#!/usr/bin/env bash
# tests/doc_lint/run_doc_index.sh -- [DOC-INDEX] unit 1.0: the decisions
# addendum census, its committed owner table and the per-extent control
# (design docs/design/doc_index_format.md §5.2, appendix A/B).
# Checks, each of which must pass:
#   1. doc_census.py --selftest: P20 and the gate's own cases (a)/(b)/(c).
#   2. doc_census.py --check: the committed owner table equals a fresh census of
#      docs/dev/decisions.md (gates a/b/c, every ruling used).
#   3. doc_control.py --selftest: appendix B's plants P1-P21 each RED by the
#      named clause; the correct toy conversion GREEN.
#   4. doc_control.py --witnesses-table: appendix B's named witnesses hold in
#      the table.
#   5. witness sabotage: the D89 rulings flipped to D94 make check 4 fail.
# Not in `make test` yet (unit 1.0); T1's run_doc_lint.sh may chain it.
# Reads text only; ROOT_DIR is overridable.
set -u
ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
. "$ROOT_DIR/scripts/tmpdir.sh"
PY="python3 -I"
CENSUS="$ROOT_DIR/scripts/doc_census.py"
CONTROL="$ROOT_DIR/scripts/doc_control.py"
pass=0; fail=0
check() { # name, expected rc, command...
    local name="$1" want="$2"; shift 2
    out="$("$@" 2>&1)"; rc=$?
    printf '%s\n' "$out" | tail -n 40
    if [ "$rc" -eq "$want" ]; then pass=$((pass+1)); echo "PASS: $name"
    else fail=$((fail+1)); echo "FAIL: $name (rc=$rc, want $want)"; fi
}
check "census selftest" 0 $PY "$CENSUS" --selftest
check "census --check: committed table == fresh census" 0 $PY "$CENSUS" --check
check "control selftest: every plant red, toy green" 0 $PY "$CONTROL" --selftest
check "named witnesses hold in the table" 0 $PY "$CONTROL" --witnesses-table
tmp="$(mktemp -d -p "${PCREC_TMPDIR}" doc_index.XXXXXX)"
awk -F'\t' 'BEGIN{OFS="\t"} $1=="D94" && $3=="D89" {$3="D94"} {print}' \
    "$ROOT_DIR/docs/dev/doc_index/decisions_owner_rulings.tsv" > "$tmp/rulings.tsv"
$PY "$CENSUS" --emit --no-cites --rulings "$tmp/rulings.tsv" --table "$tmp/owners.tsv" >/dev/null 2>&1
check "sabotage: D89's addenda ruled to D94 fail the witnesses" 1 $PY "$CONTROL" --witnesses-table --table "$tmp/owners.tsv"
rm -rf "$tmp"
echo "checks passed: $pass"
echo "checks failed: $fail"
rc=0; [ "$fail" -eq 0 ] || rc=1
echo "run_doc_index: DONE rc=$rc"
exit $rc
