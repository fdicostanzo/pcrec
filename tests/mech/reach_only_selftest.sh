#!/usr/bin/env bash
# reach_only_selftest.sh -- [MECH-REACHONLY] self-test of REACH_ONLY=1.
# Three fake rows in a temp definitions dir (MECH_SAB_DIR), so no plant lives
# in the ledger: Sx1 a probe that reaches, Sx2 a probe made to fail (must read
# UNREACHED and fail the run), Sx3 a failing probe DECLARED UNREACHED (must
# read declared-UNREACHED and not fail the run). Two runs: Sx1+Sx3 must exit 0
# and name both words; Sx1+Sx2 must exit 1. Builds the clean tree twice
# (~1 min each); take the box lock like any mech run (the runner does).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d "${TMPDIR:-/tmp}/reach-only-selftest.XXXXXX")"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/defs"
row() { # id probe expect-extra
    cat > "$T/defs/$1_selftest.sh" <<ROW
SAB_ID='$1-selftest'
SAB_FILE='src/core/sb.c'
SAB_SUITES='corpus'
SAB_DESC='reach-only self-test row'
SAB_BEFORE='x'
SAB_AFTER='y'
SAB_REACH='$2'
SAB_REACH_EXPECT='MARK-OK'
$3
ROW
}
row Sx1 'echo MARK-OK' ''
row Sx2 'echo something-else' ''
row Sx3 'echo something-else' "SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='self-test declared dead'"
bad=0
chk() { if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; bad=1; fi; }
run() { MECH_SAB_DIR="$T/defs" REACH_ONLY=1 bash "$HERE/run_sabotage_matrix.sh" "$@" > "$T/out" 2>"$T/err"; echo $?; }
rc="$(run Sx1 Sx3)"
chk "declared-UNREACHED does not fail the run (rc=$rc)" '[ "$rc" = 0 ]'
chk "Sx1 reads REACHED" 'grep -qE "^Sx1-selftest.*REACHED" "$T/out"'
chk "Sx3 reads declared-UNREACHED" 'grep -q "declared-UNREACHED" "$T/out"'
chk "DONE trailer rc=0" 'grep -q "^mech-reach-only: DONE rc=0 " "$T/out"'
rc="$(run Sx1 Sx2)"
chk "failing probe fails the run (rc=$rc)" '[ "$rc" = 1 ]'
chk "Sx2 reads UNREACHED" 'grep -qE "^Sx2-selftest.*UNREACHED" "$T/out"'
chk "DONE trailer rc=1" 'grep -q "^mech-reach-only: DONE rc=1 " "$T/out"'
[ "$bad" = 0 ] && echo "reach_only_selftest: DONE rc=0" || { echo "reach_only_selftest: DONE rc=1"; cat "$T/out" "$T/err" | tail -30; }
exit "$bad"
