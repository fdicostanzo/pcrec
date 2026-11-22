#!/usr/bin/env bash
# tests/codegen/run_skip_pins.sh -- the E-find search rows' `skip` COLUMN, held
# to the ARTIFACT (review r72 CHECKS-1, lane bsu1fix; block_span.md §3).
#
# `skip` is the plan position a search row's head already proved, which the
# candidate test then drops (window.c: stop_skip for a memchr/pair/walk stop,
# hors_skip for D-hors's probe). A row whose `skip` returned -1 would re-test
# the proved position: every answer stays right, the artifact only gets a
# redundant compare per candidate, so no corpus, oracle or G2 pin sees it
# (plants V1 and V2 of r72 were SILENT-MOVE against every suite the lane ran:
# the .rxt corpus, test-memfn-forms/-rows/-finder/-d27frame, test-codegen).
#
# TWO CELLS, each read off the default-build artifact of one pattern, with the
# expected counts LITERAL here (reasoned from the pattern, not read from the
# emitter): the candidate test of a width-w window pattern states each tested
# position as a class compare, and the probed or stopped position must not be
# among them.
#   hors  `[0-9a-f]{17}`: D-hors probes position 16 once (the hoisted byte
#         `rx_mf1_b = S[C + 16]`), and the candidate test is positions 0..15:
#         `S[C + 16]` is spelt ONCE (the probe), `S[C + 15]` FOUR times (two
#         ranges, each `>= && <=`).
#   stop  `ab[0-9]{26}`: the stop is the `b` at offset 1 (memchr for 98): the
#         test holds `S[C] == 97` and NO `S[C + 1] == 98`; position 2 is a
#         digit class (two spellings) as the control that the test is there.
# Light: two compiles of the CLI, no C compile. In `make test-codegen`.
#
# Usage: bash tests/codegen/run_skip_pins.sh   Env: PCREC
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # pcrec_run
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
[ -x "$PCREC" ] || { echo "FAIL: skip-pins: no compiler at $PCREC -- run \`make\` first" >&2; exit 1; }

count() { # count <file> <fixed string>: occurrences (not lines)
    grep -oF -- "$2" "$1" | wc -l | tr -d ' '
}
expect() { # expect <label> <file> <string> <n>
    local got
    got=$(count "$2" "$3")
    if [ "$got" = "$4" ]; then ok "$1: \`$3\` x$4"; else bad "$1: \`$3\` x$got, expected $4"; fi
}

emit() { pcrec_run "$PCREC" -p rx --emit-main -o "$WORKDIR/$1.c" --pattern "$2" >/dev/null 2>&1 \
    || bad "$1: pcrec did not compile \`$2\`"; }

emit hors '[0-9a-f]{17}'
expect hors "$WORKDIR/hors.c" 'rx_mf1_s[rx_mf1_c + 16]' 1
expect hors "$WORKDIR/hors.c" 'rx_mf1_s[rx_mf1_c + 15]' 4

emit stop 'ab[0-9]{26}'
expect stop "$WORKDIR/stop.c" 'rx_mf1_s[rx_mf1_c + 1] == 98' 0
expect stop "$WORKDIR/stop.c" 'rx_mf1_s[rx_mf1_c] == 97' 1
expect stop "$WORKDIR/stop.c" 'rx_mf1_s[rx_mf1_c + 2]' 2

# K35: the floor, so a script that read nothing cannot pass.
[ "$pass" -ge 5 ] || bad "skip-pins: only $pass checks passed, floor 5"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
