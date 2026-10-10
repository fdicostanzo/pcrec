#!/usr/bin/env bash
# tests/revend/run_window_twin.sh -- [OPT-REVEND] L2: the WINDOW-IDENTITY TWIN
# (docs/design/locate_finish.md §5 L3's answer-level control, E9's shape;
# LR-S2, LR-S4). For every block of stage2_captures.rxt and every row of
# window_twin_patterns.tsv: the `rev-end` build against the `-fno-rev-end`
# build (the inlined prefilter's window, then the search's answer and every
# capture) and against libpcre2 (the search's answer and every group), over
# every subject on the pattern's alphabet to length 5-7 at every character
# boundary, with the E-VR count asserted 0 on every exact hybrid.
# window_twin.py's own header has the strata and the exit rule.
#
# OPT-IN (`make test-revend-twin`, ~30 s): it links libpcre2-8 and its oracle
# leg is the reference 10.46's answers (on another libpcre2 a red names the
# library first). SKIPS loudly without libpcre2 (PC-3's rule). Mech arm
# `revtwin`.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/wintwin.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
if ! printf '#include <pcre2.h>\n' | gcc -DPCRE2_CODE_UNIT_WIDTH=8 -E - >/dev/null 2>&1; then
    echo "SKIP: window twin: no libpcre2-8 headers (the oracle leg needs them)"
    echo "checks passed: 0"; echo "checks failed: 0"; exit 0
fi
# One bound on the whole sweep (window_twin.py bounds each compile and run).
"$TIMEOUT_BIN" 1800 python3 -I "$SCRIPT_DIR/window_twin.py" "$PCREC" "$WORK" > "$WORK/out" 2> "$WORK/err"
rc=$?
cat "$WORK/out"
head -40 "$WORK/err" >&2
if [ "$rc" -eq 0 ]; then echo "checks passed: 1"; echo "checks failed: 0"
else echo "checks passed: 0"; echo "checks failed: 1"; fi
exit "$rc"
