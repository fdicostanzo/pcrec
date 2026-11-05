#!/usr/bin/env bash
# nocompile_selftest.sh -- review 2026-10-24 r1 subst, CHK-1: self-test of the
# matrix's compile gate (run_sabotage_matrix.sh, NOCOMPILE_ERE). Two fake rows
# in a temp definitions dir (MECH_SAB_DIR), so no plant lives in the ledger,
# both on S1354's site: Sy1 the ORIGINAL plant (`return 0;`, which leaves
# `flags` unused and fails the emitted code's -Werror compile) must read
# ANOMALY (the plant does not compile) and be the run's one anomaly
# Sy2 the warning-clean plant must read DETECTED by its cells.
# [MECH-NOCOMPILE] Sy3 is Sy1's plant DECLARED `SAB_EXPECT=COMPILE-CATCH`: it
# must read DETECTED-BUILD and add no anomaly. Run A (Sy1 Sy2 Sy3) runs with
# MECH_ANOMALY_CEILING=0, so the one undeclared anomaly must make the run exit
# 1 on the ceiling alone (no unexpected row in it). Run B is Sy4, the clean
# plant DECLARED COMPILE-CATCH: the build succeeds, so it must read
# ***UNEXPECTED*** and exit 1. Two matrix runs of the subst arm (~10 min each);
# the runner takes the box lock.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d "${TMPDIR:-/tmp}/nocompile-selftest.XXXXXX")"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/defs"
row() { # id after [expect]
    cat > "$T/defs/$1_selftest.sh" <<ROW
SAB_ID='$1-selftest'
SAB_FILE='src/gen/emit_subst.c'
SAB_SUITES='subst'
SAB_DESC='compile-gate self-test row'
SAB_BEFORE='"    if (sl == -2) return (flags & PCREC_SUBST_STRICT) ? PCREC_SUBST_UNSET : 0;\n"'
SAB_AFTER='$2'
${3:+SAB_EXPECT='$3'}
ROW
}
row Sy1 '"    if (sl == -2) return 0;\n"'
row Sy2 '"    if (sl == -2) return (flags & PCREC_SUBST_STRICT) ? 0 : 0;\n"'
row Sy3 '"    if (sl == -2) return 0;\n"' COMPILE-CATCH
row Sy4 '"    if (sl == -2) return (flags & PCREC_SUBST_STRICT) ? 0 : 0;\n"' COMPILE-CATCH
bad=0
chk() { if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; bad=1; fi; }
MECH_ANOMALY_CEILING=0 MECH_SAB_DIR="$T/defs" bash "$HERE/run_sabotage_matrix.sh" Sy1 Sy2 Sy3 > "$T/out" 2>"$T/err"
rc=$?
chk "the run counts exactly the one anomaly (rc=$rc)" 'grep -qE "anomalies: 1," "$T/out"'
chk "the ceiling alone fails the run (rc=1, unexpected: 0)" '[ "$rc" = 1 ] && grep -qE "unexpected: 0," "$T/out" && grep -q "exceed the ceiling 0" "$T/out"'
chk "Sy1 reads ANOMALY (the plant does not compile)" 'grep -qE "^Sy1-selftest.*ANOMALY \(the plant does not compile" "$T/out"'
chk "Sy1 never reads DETECTED" '! grep -qE "^Sy1-selftest.* DETECTED *$" "$T/out"'
chk "Sy2 reads DETECTED" 'grep -qE "^Sy2-selftest.* DETECTED *$" "$T/out"'
chk "Sy3 (declared) reads DETECTED-BUILD" 'grep -qE "^Sy3-selftest.*	DETECTED-BUILD " "$T/out"'
MECH_ANOMALY_CEILING=0 MECH_SAB_DIR="$T/defs" bash "$HERE/run_sabotage_matrix.sh" Sy4 > "$T/out4" 2>"$T/err4"
rc4=$?
chk "Sy4 (declared, builds) reads UNEXPECTED and exits 1 (rc=$rc4)" '[ "$rc4" = 1 ] && grep -qE "^Sy4-selftest.*NO ARM.S ARTIFACT FAILED TO COMPILE.*UNEXPECTED" "$T/out4" && grep -qE "unexpected: 1," "$T/out4"'
[ "$bad" = 0 ] && echo "nocompile_selftest: DONE rc=0" || { echo "nocompile_selftest: DONE rc=1"; cat "$T/out" "$T/err" "$T/out4" | tail -40; }
exit "$bad"
