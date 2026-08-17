#!/bin/sh
# K23: what the MRL clamp COSTS on the common path (D18's speed mandate).
#
# The clamp is two integer comparisons at each outer-replica entry, on the
# forward path -- exactly the kind of per-iteration instrumentation D22 says
# must not be traded against speed. This measures it where it is most
# visible: a BENIGN matching subject, so the matcher never backtracks and the
# clamp is pure added forward work with nothing to save.
#
# Method: emit WITHOUT --emit-main, link a driver that calls <prefix>_search
# in a loop, and take the best of several timed runs per arm (best-of, not
# mean: the contaminant here is other load, which only ever adds time).
#
# CLAMP DENSITY matters and R26 E5 found the first version measuring the
# wrong one: with an EMPTY follow, minrest is 0 at the last outer_min-1
# replicas, so only 9 of 50 sites carry a clamp -- 18% of the density the
# note recommends shipping. Pass FOLLOW_MIN > 0 (with a pattern that really
# has a follow of that width, and SUFFIX to match it) to measure the dense
# case, where every replica is clamped.
#
# Usage: throughput.sh 'PATTERN' OUTER_MIN INNER_MIN STRIDE SUBJECT_LEN
#                      [ITERS] [REPS] [FOLLOW_MIN] [SUFFIX]
LC_ALL=C; export LC_ALL

PAT="$1"; OMIN="$2"; IMIN="$3"; STRIDE="$4"; LEN="$5"
ITERS="${6:-200000}"; REPS="${7:-5}"; FMIN="${8:-0}"; SUFFIX="${9:-}"
HERE=$(cd "$(dirname "$0")" && pwd)
: "${PCREC:=$(cd "$HERE/../../../.." && pwd)/build/pcrec}"
: "${K23_TMP:=${TMPDIR:-/tmp}/k23tp.$$}"
mkdir -p "$K23_TMP" || exit 1

timeout 60 "$PCREC" -p rx -o "$K23_TMP/base.c" -- "$PAT" || { echo emit-fail; exit 1; }
python3 "$HERE/prune_proto.py" "$K23_TMP/base.c" "$K23_TMP/prune.c" \
    --outer-min "$OMIN" --inner-min "$IMIN" --stride "$STRIDE" \
    --follow-min "$FMIN" || exit 1
python3 "$HERE/prune_proto.py" "$K23_TMP/base.c" "$K23_TMP/placebo.c" --placebo \
    --outer-min "$OMIN" --inner-min "$IMIN" --stride "$STRIDE" \
    --follow-min "$FMIN" || exit 1

cat > "$K23_TMP/drv.c" <<'DRV'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "m.h"
int main(int argc, char **argv)
{
    long iters = atol(argv[1]);
    size_t n = (size_t)atol(argv[2]);
    const char *suf = argc > 3 ? argv[3] : "";
    size_t sl = strlen(suf);
    unsigned char *s = malloc(n + sl + 1);
    ptrdiff_t caps[RX_NCAPS][2];
    struct timespec t0, t1;
    long i; long long acc = 0;
    memset(s, 'a', n); memcpy(s + n, suf, sl); n += sl; s[n] = 0;
    /* one warm-up search outside the timing window */
    acc += rx_search(s, n, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (i = 0; i < iters; i++) acc += rx_search(s, n, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    /* acc is printed so the loop cannot be optimized away */
    printf("%.6f %lld %td\n",
           (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec),
           acc, caps[0][1]);
    return 0;
}
DRV

printf 'arm\tbest_s\tns_per_search\tspan_end\n'
for A in base placebo prune; do
    cp "$K23_TMP/base.h" "$K23_TMP/m.h"
    gcc -O2 -I"$K23_TMP" -o "$K23_TMP/$A.bin" "$K23_TMP/drv.c" "$K23_TMP/$A.c" \
        || { echo "cc-fail $A"; exit 1; }
    BEST=""; SPAN=""
    R=0
    while [ "$R" -lt "$REPS" ]; do
        OUT=$("$K23_TMP/$A.bin" "$ITERS" "$LEN" "$SUFFIX")
        T=$(echo "$OUT" | cut -d' ' -f1); SPAN=$(echo "$OUT" | cut -d' ' -f3)
        if [ -z "$BEST" ] || [ "$(echo "$T < $BEST" | bc)" = 1 ]; then BEST="$T"; fi
        R=$((R + 1))
    done
    printf '%s\t%s\t%.1f\t%s\n' "$A" "$BEST" \
        "$(echo "$BEST * 1000000000 / $ITERS" | bc -l)" "$SPAN"
done
[ -n "$K23_KEEP" ] || rm -rf "$K23_TMP"
