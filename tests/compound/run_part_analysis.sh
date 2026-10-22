#!/usr/bin/env bash
# tests/compound/run_part_analysis.sh -- [K113] a compound's parts read the
# walking attempt's RESOLVED analysis chain and analysis object, never a
# second resolution of the same options (the measure set's rule, run_part_
# measures.sh; PcrecEmitIn.meas carries both). Sabotage rows S1331-S1332.
#
# A -DPCREC_KS_TRACE build of this tree. The trace writes `KSTRACE analysis -
# resolve -` each time a chain is resolved and one `KSRCTRACE object` line per
# query kind each time the analysis object is built. The split witness
# '^\s+|\s+$' (checked to stamp RX_COMPOUND "split": P with parts f and q)
# must write exactly as many of each as the CONTROL, a pattern that is no
# compound: the parts' share is zero. Two arms: no --analysis (the build's
# default chain) and --analysis default (a named one).
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
W="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-partanalysis.XXXXXX")"
[ "${KEEP:-0}" = 1 ] || trap 'rm -rf "$W"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $*"; pass=$((pass + 1)); }
bad() { echo "FAIL: $*"; fail=$((fail + 1)); }
WIT='^\s+|\s+$'

KST="$W/kst"
if ! "$TIMEOUT_BIN" 900 make -s -C "$ROOT_DIR" -j4 BUILD_DIR="$KST" \
        CFLAGS="-O2 -g -DPCREC_KS_TRACE" all > "$W/kst.log" 2>&1; then
    echo "FAIL: the -DPCREC_KS_TRACE build failed: $(tail -3 "$W/kst.log" | tr '\n' ' ')"
    echo "run_part_analysis: FAIL"
    exit 1
fi

# run NAME PATTERN ARGS..: the C to W/NAME.c, the trace to W/NAME.err
run() {
    local n=$1 p=$2; shift 2
    "$TIMEOUT_BIN" 60 "$KST/pcrec" -p rx "$@" -o "$W/$n.c" --pattern "$p" 2> "$W/$n.err"
}
count() { grep -c "$1" "$2"; }

for arm in "D" "N --analysis default"; do
    set -- $arm; name=$1; shift
    if ! run "$name.w" "$WIT" "$@" || ! run "$name.c" 'a(b|c)+d' "$@"; then
        bad "$name: a compile failed: $(head -1 "$W/$name.w.err" "$W/$name.c.err" | tr '\n' ' ')"; continue
    fi
    if [ "$(sed -n 's/^#define RX_COMPOUND "\(.*\)"$/\1/p' "$W/$name.w.c")" != split ]; then
        bad "$name: the witness is not a split compound: the arm measures nothing"; continue
    fi
    rw=$(count '^KSTRACE	analysis	-	resolve	-$' "$W/$name.w.err")
    rc=$(count '^KSTRACE	analysis	-	resolve	-$' "$W/$name.c.err")
    if [ "$rc" -ge 1 ] && [ "$rw" = "$rc" ]; then
        ok "$name: the compound resolves the analysis chain $rw time(s), as the non-compound control: its parts resolve none"
    else
        bad "$name: the compound resolved the chain $rw time(s), the control $rc (a part resolved its own)"
    fi
    ow=$(count '^KSRCTRACE	object	' "$W/$name.w.err")
    oc=$(count '^KSRCTRACE	object	' "$W/$name.c.err")
    if [ "$oc" -ge 1 ] && [ "$ow" = "$oc" ]; then
        ok "$name: the compound builds the analysis object $ow kind line(s), as the control: its parts build none"
    else
        bad "$name: the compound built $ow object kind line(s), the control $oc (a part built its own)"
    fi
done
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] && [ "$pass" -ge 4 ] && { echo "run_part_analysis: PASS"; exit 0; }
[ "$pass" -ge 4 ] || echo "FAIL: population: $pass checks passed, under the floor 4 (K35)"
echo "run_part_analysis: FAIL"
exit 1
