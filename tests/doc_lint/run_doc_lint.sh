#!/usr/bin/env bash
# tests/doc_lint/run_doc_lint.sh -- `make test-doc-lint`: [DOC-INDEX] T1 (D192).
# Two checks, each of which must pass:
#   1. scripts/entry --selftest: the planted fixtures (one per routing row, the dormant profiles on the REAL
#      table, --over-cap rounding edges, --rev, the plan work view, the Policy templates).
#   2. scripts/entry --over-cap over the real tree: exits 0 and prints its trailer (the population line
#      scripts/gestalt reads; 0 pair indexes from T1 until unit 1).
# Unit 1 adds doc_lint.py's decisions profile here; T2 folds plan_lint in. Reads text only (no compiler).
# ROOT_DIR is overridable (the mech arm points it at a scratch tree).
set -u
ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
ENTRY="$ROOT_DIR/scripts/entry"
pass=0; fail=0

out="$(python3 -I "$ENTRY" --selftest 2>&1)"; rc=$?
printf '%s\n' "$out"
if [ "$rc" -eq 0 ]; then pass=$((pass+1)); echo "PASS: entry --selftest"; else fail=$((fail+1)); echo "FAIL: entry --selftest rc=$rc"; fi

out="$(python3 -I "$ENTRY" --over-cap 2>&1)"; rc=$?
printf '%s\n' "$out"
if [ "$rc" -eq 0 ] && printf '%s\n' "$out" | grep -q '^entry: over-cap checked '; then
    pass=$((pass+1)); echo "PASS: entry --over-cap prints its trailer"
else fail=$((fail+1)); echo "FAIL: entry --over-cap rc=$rc"; fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
