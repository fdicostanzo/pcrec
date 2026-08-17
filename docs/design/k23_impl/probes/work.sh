#!/bin/sh
# K23 probe: FORWARD SCAN WORK alongside the step count, for one pattern.
#
# WHAT THIS IS NOT, stated first because R26 M2/E6 found the note asserting
# otherwise: this is NOT D49's `RX_ERR_WORK` meter. That meter charges at
# emitter-chosen sites and landed in the counter-K build AFTER this lane
# measured; no generated matcher this lane can produce contains a single one
# of its charge points. What this counts is a LANE PROXY with one precise
# definition:
#
#   one unit = one iteration of a span-loop scan body, i.e. one execution of
#   `{ rx_cur += W; it_++; }` -- one stride of greedy forward walking.
#
# That is the FORWARD work the step counter is structurally blind to
# (engine_m4.md 4.2 charges only at the `rx_fail` resumption), which is the
# quantity D49 exists to bound; it is not the same NUMBER D49 will produce.
# Any ratio derived from it is a proxy ratio and must be labelled as one.
# Re-anchoring against the real meter is owed once counter-K lands on main.
#
# Usage:  work.sh 'PATTERN' LEN[,LEN...] [UNIT] [PRUNE_ARGS...]
#   prints one line per length:  "<len> <steps> <work> <verdict>"
#   With PRUNE_ARGS (e.g. --outer-min 10 --inner-min 10 --stride 1
#   --replicas 50 [--clamp-scan]) the matcher is patched by prune_proto.py
#   first, so baseline and pruned arms are produced by the SAME instrument.
#
# LC_ALL=C: R24 M-F1's collation defect. See this directory's CLAUDE.md.
LC_ALL=C; export LC_ALL

PAT="$1"; LENS="$2"; UNIT="${3:-a}"
shift 3 2>/dev/null || shift $#
HERE=$(cd "$(dirname "$0")" && pwd)
: "${PCREC:=$(cd "$HERE/../../../.." && pwd)/build/pcrec}"
: "${K23_TMP:=${TMPDIR:-/tmp}/k23work.$$}"
: "${K23_TIMEOUT:=600}"
: "${K23_BUDGET:=1000000000000}"
mkdir -p "$K23_TMP" || exit 1
cleanup() { [ -n "$K23_KEEP" ] || rm -rf "$K23_TMP"; }

SRC="$K23_TMP/m.c"
if ! timeout 60 "$PCREC" -p rx --emit-main --step-budget="$K23_BUDGET" \
        -o "$SRC" -- "$PAT" >"$K23_TMP/emit.log" 2>&1; then
    echo "-1 -1 emit-fail"; cleanup; exit 0
fi

if [ $# -gt 0 ]; then
    if ! python3 "$HERE/prune_proto.py" "$SRC" "$K23_TMP/p.c" "$@" \
            >"$K23_TMP/prune.log" 2>&1; then
        echo "-1 -1 prune-fail"; cat "$K23_TMP/prune.log" >&2; cleanup; exit 0
    fi
    SRC="$K23_TMP/p.c"
fi

PSRC="$K23_TMP/i.c"
cat > "$PSRC" <<'PROBE_HEAD'
#include <stdio.h>
#include <stdlib.h>
static long long rx_probe_steps = 0;
static long long rx_probe_work  = 0;
static void rx_probe_report(void){
    fprintf(stderr, "STEPS %lld WORK %lld\n", rx_probe_steps, rx_probe_work);
}
PROBE_HEAD
# Two substitutions. The scan-body one is applied to EVERY scan site (the
# emitter writes one per replica), so unlike the single-site step patch its
# expected count is "at least one" and is asserted as such below.
sed -e 's/if (--w->budget < 0) return RX_R_STEPS;/rx_probe_steps++; if (--w->budget < 0) return RX_R_STEPS;/' \
    -e 's/{ rx_cur += \([0-9]*\); it_++; }/{ rx_cur += \1; it_++; rx_probe_work++; }/g' \
    -e 's/^    if (argc < 2) { fprintf(stderr, "usage/    atexit(rx_probe_report);\n    if (argc < 2) { fprintf(stderr, "usage/' \
    "$SRC" >> "$PSRC"

NINC=$(grep -c 'rx_probe_steps++' "$PSRC")
NWORK=$(grep -c 'rx_probe_work++' "$PSRC")
NHOOK=$(grep -c 'atexit(rx_probe_report)' "$PSRC")
if [ "$NINC" != "1" ] || [ "$NHOOK" != "1" ] || [ "$NWORK" -lt 1 ]; then
    echo "-1 -1 patch-fail($NINC,$NWORK,$NHOOK)"; cleanup; exit 0
fi

if ! timeout 600 gcc -O2 -o "$K23_TMP/m" "$PSRC" >"$K23_TMP/cc.log" 2>&1; then
    echo "-1 -1 cc-fail"; cleanup; exit 0
fi

for L in $(echo "$LENS" | tr ',' ' '); do
    SUBJ=$(python3 -c "
import sys
u='$UNIT'; L=$L
sys.stdout.write((u * (-(-L // len(u)) if u else 0))[:L])")
    OUT=$(timeout "$K23_TIMEOUT" "$K23_TMP/m" "$SUBJ" 2>"$K23_TMP/e.txt")
    S=$(sed -n 's/^STEPS \([0-9]*\) WORK .*/\1/p' "$K23_TMP/e.txt" | tail -1)
    W=$(sed -n 's/^STEPS [0-9]* WORK \([0-9]*\)/\1/p' "$K23_TMP/e.txt" | tail -1)
    if [ -z "$S" ]; then
        echo "$L -1 -1 timeout"
    else
        case "$OUT" in
            match*)   V=match ;;
            nomatch*) V=nomatch ;;
            steps*)   V=steps ;;
            *)        V=other ;;
        esac
        echo "$L $S $W $V"
    fi
done
cleanup
