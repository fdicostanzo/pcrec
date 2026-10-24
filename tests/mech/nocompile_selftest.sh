#!/usr/bin/env bash
# nocompile_selftest.sh -- review 2026-10-24 r1 subst, CHK-1: self-test of the
# matrix's compile gate (run_sabotage_matrix.sh, NOCOMPILE_ERE). Two fake rows
# in a temp definitions dir (MECH_SAB_DIR), so no plant lives in the ledger,
# both on S1354's site: Sy1 the ORIGINAL plant (`return 0;`, which leaves
# `flags` unused and fails the emitted code's -Werror compile) must read
# ANOMALY (the plant does not compile) and fail the run; Sy2 the warning-clean
# plant must read DETECTED by its cells. One matrix run of the subst arm
# (clean tree + two sabotaged trees, ~10 min); the runner takes the box lock.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d "${TMPDIR:-/tmp}/nocompile-selftest.XXXXXX")"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/defs"
row() { # id after
    cat > "$T/defs/$1_selftest.sh" <<ROW
SAB_ID='$1-selftest'
SAB_FILE='src/gen/emit_subst.c'
SAB_SUITES='subst'
SAB_DESC='compile-gate self-test row'
SAB_BEFORE='"    if (sl == -2) return (flags & PCREC_SUBST_STRICT) ? PCREC_SUBST_UNSET : 0;\n"'
SAB_AFTER='$2'
ROW
}
row Sy1 '"    if (sl == -2) return 0;\n"'
row Sy2 '"    if (sl == -2) return (flags & PCREC_SUBST_STRICT) ? 0 : 0;\n"'
bad=0
chk() { if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; bad=1; fi; }
MECH_SAB_DIR="$T/defs" bash "$HERE/run_sabotage_matrix.sh" Sy1 Sy2 > "$T/out" 2>"$T/err"
rc=$?
chk "a non-compiling plant fails the run (rc=$rc)" '[ "$rc" = 1 ]'
chk "Sy1 reads ANOMALY (the plant does not compile)" 'grep -qE "^Sy1-selftest.*ANOMALY \(the plant does not compile" "$T/out"'
chk "Sy1 never reads DETECTED" '! grep -qE "^Sy1-selftest.*	DETECTED" "$T/out"'
chk "Sy2 reads DETECTED" 'grep -qE "^Sy2-selftest.*	DETECTED$" "$T/out"'
[ "$bad" = 0 ] && echo "nocompile_selftest: DONE rc=0" || { echo "nocompile_selftest: DONE rc=1"; cat "$T/out" "$T/err" | tail -30; }
exit "$bad"
