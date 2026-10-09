#!/usr/bin/env bash
# tests/memfn/run_form_checks.sh -- C12, C13, C14 ([MEMFN], integration.md
# §9.3 I5, §10.5, §14.6, §14.7). `make test-memfn-forms`.
#
#   C12  the emitted-form ratchet: the search forms pcrec's emitters spell,
#        counted against tests/memfn/c12_ceilings.tsv (the ceilings only
#        descend; M1's REPLACE lowers the emit_dfa.c memchr row 8 -> 2, M1b's
#        deletes src/gen/runcmp.c's three rows, 12 -> 9; M2's (R4g) lowers
#        the memchr row 2 -> 1 and deletes the walk-fmt row, 9 -> 8).
#   C13  on_cand duplicability: UNREACHED, said so, until a producer exists.
#   C14  shape bounds: MF_MAX_TERM >= PCREC_OFSK_MAX_SET + 1 and friends,
#        compiled against limits.def's current values.
# The semantics, the controls and the red conditions are form_checks.py's
# header. Static plus one syntax-only compile; needs no build.
#
# THE INDEPENDENT CONTROL: C12_CEIL_ROWS_FLOOR is THIS literal, the K35 floor
# on the ceiling table's row count; it shares no source with the TSV.
#
# Usage: bash tests/memfn/run_form_checks.sh [ROOT]   (CC defaults to gcc)

set -u

C12_CEIL_ROWS_FLOOR=2   # D147 add. 12: the walk-back row deleted with N6 (not a search site), 3 -> 2; R-12 REPLACE: emit_vm.c's walk-open row (VMLAZY's normalized prefix) deleted, 2 -> 1; R-12 (Q-R12-5): enc_utf8.c's swar-hibit row (VALID), 1 -> 2

here="$(cd "$(dirname "$0")" && pwd)"
root="${1:-$(cd "$here/../.." && pwd)}"

echo "== C12/C13/C14: the emitted-form ratchet, on_cand, shape bounds =="
python3 "$here/form_checks.py" "$root" "${CC:-gcc}" "$C12_CEIL_ROWS_FLOOR"
rc=$?
if [ "$rc" -ne 0 ] && [ "$rc" -ne 1 ]; then
    echo "FAIL: form_checks.py exited $rc before reporting"
    echo "checks passed: 0"
    echo "checks failed: 1"
    exit 1
fi
exit "$rc"
