#!/bin/sh
# K23 head-to-head: BASELINE vs MRL-PRUNED vs MEMOIZED, on one shape.
#
# Reports, for each arm and each subject length: exact steps, the answer, the
# emitted .c size, the gcc compile time, and (memo only) the table size in
# bytes. The point of the table column is that it is the memo arm's whole
# problem: it is Theta(program points x subject length) and it is not a
# compile-time constant, which is what collides with allocation-freedom.
#
# Usage: head2head.sh 'PATTERN' OUTER_MIN INNER_MIN STRIDE LEN[,LEN...] [MEMOCAP]
LC_ALL=C; export LC_ALL

PAT="$1"; OMIN="$2"; IMIN="$3"; STRIDE="$4"; LENS="$5"; MEMOCAP="${6:-4096}"
HERE=$(cd "$(dirname "$0")" && pwd)
: "${PCREC:=$(cd "$HERE/../../../.." && pwd)/build/pcrec}"
: "${K23_TMP:=${TMPDIR:-/tmp}/k23h2h.$$}"
: "${K23_BUDGET:=1000000000000}"
: "${K23_TIMEOUT:=300}"
mkdir -p "$K23_TMP" || exit 1

timeout 60 "$PCREC" -p rx --emit-main --step-budget="$K23_BUDGET" \
    -o "$K23_TMP/base.c" -- "$PAT" || { echo "emit-fail"; exit 1; }

instrument() {  # $1 = in, $2 = out
    {
        cat <<'PROBE_HEAD'
#include <stdio.h>
#include <stdlib.h>
static long long rx_probe_steps = 0;
static void rx_probe_report(void){ fprintf(stderr, "STEPS %lld\n", rx_probe_steps); }
PROBE_HEAD
        sed -e 's/if (--w->budget < 0) return RX_R_STEPS;/rx_probe_steps++; if (--w->budget < 0) return RX_R_STEPS;/' \
            -e 's/^    if (argc < 2) { fprintf(stderr, "usage/    atexit(rx_probe_report);\n    if (argc < 2) { fprintf(stderr, "usage/' \
            "$1"
    } > "$2"
    [ "$(grep -c 'rx_probe_steps++' "$2")" = 1 ] || { echo "PATCH-FAIL $2" >&2; exit 1; }
}

python3 "$HERE/prune_proto.py" "$K23_TMP/base.c" "$K23_TMP/prune.c" \
    --outer-min "$OMIN" --inner-min "$IMIN" --stride "$STRIDE" || exit 1
instrument "$K23_TMP/base.c"  "$K23_TMP/base.i.c"
instrument "$K23_TMP/prune.c" "$K23_TMP/prune.i.c"
# the memo patch is applied to the INSTRUMENTED file, because it inserts its
# table-size report next to the step report's atexit hook
python3 "$HERE/memo_proto.py" "$K23_TMP/base.i.c" "$K23_TMP/memo.i.c" \
    --bits --cap "$MEMOCAP" || exit 1

printf 'arm\tbytes_c\tcc_s\ttable_B\n'
for A in base prune memo; do
    SZ=$(wc -c < "$K23_TMP/$A.i.c")
    T0=$(date +%s.%N)
    gcc -O2 -o "$K23_TMP/$A.bin" "$K23_TMP/$A.i.c" || { echo "cc-fail $A"; exit 1; }
    T1=$(date +%s.%N)
    printf '%s\t%s\t%.2f\t-\n' "$A" "$SZ" "$(echo "$T1 - $T0" | bc)"
done

printf '\nn\tbase_steps\tbase_out\tprune_steps\tprune_out\tmemo_steps\tmemo_out\tmemo_tableB\n'
for L in $(echo "$LENS" | tr ',' ' '); do
    SUBJ=$(python3 -c "import sys; sys.stdout.write('a'*$L)")
    printf '%s' "$L"
    for A in base prune memo; do
        OUT=$(timeout "$K23_TIMEOUT" "$K23_TMP/$A.bin" "$SUBJ" 2>"$K23_TMP/e.txt")
        S=$(sed -n 's/^STEPS //p' "$K23_TMP/e.txt" | tail -1)
        printf '\t%s\t%s' "${S:--}" "$(echo "$OUT" | tr -d '\n' | cut -c1-24)"
    done
    printf '\t%s\n' "$(sed -n 's/^MEMOBYTES //p' "$K23_TMP/e.txt" | tail -1)"
done
[ -n "$K23_KEEP" ] || rm -rf "$K23_TMP"
