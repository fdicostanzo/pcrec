#!/bin/sh
# docs/design/mrl_impl/probes/throughput.sh — what MRL pruning COSTS on the
# common path, measured against the SHIPPED compiler.
#
# D18's speed mandate and D22's "must not be traded against execution speed"
# apply to the bound, which sits on the FORWARD path. D51 ruling 1's adoption
# bar was <= 2% at FULL CLAMP DENSITY, taken from k23_design.md §6's prototype
# measurement; this re-takes it against the emitter.
#
# THE ARMS ARE THE TWO BUILDS THAT ACTUALLY SHIP, and that is a deliberate
# difference from §6's instrument. §6 had a third, PLACEBO arm — the clamp
# emitted at the same sites with `minrest` forced to 0, so it could never fire
# — which separates the clamp's own instructions from the code-layout drift
# that inserting ANY code causes. That arm needs a compiler flag nobody would
# ship, and the question a build lane owes is not "what do these instructions
# cost" but "what does adopting this cost", which is exactly the pruned-vs-
# denied pair. So the figure below INCLUDES layout drift, and §6's own reading
# applies: the effect sits inside a ~3% band whose sign varies by shape, and
# layout's share of it swung from 12% to 59% across three strides there. A
# number from this probe should be read as a ceiling on the cost, not as an
# attribution of it.
#
# THE SHAPES ARE §6's DENSE ROWS: a non-empty follow, so `minrest` is nonzero
# at EVERY replica and 50 of 50 sites carry a bound (§6's sparse rows clamp
# only 9 of 50, i.e. 18% of what ships). Strides 1, 2 and 3, because the
# lattice rule's integer division exists only above stride 1.
#
# The subject MATCHES and matches early, so the bound is pure added work with
# nothing to save — the arm that is unfair to the feature.
#
# LC_ALL=C throughout (R24 M-F1). Pinned with taskset when it is permitted,
# and it SAYS which, because an unpinned timing run on this box is a different
# measurement.
#
# Usage: throughput.sh [REPS] [TRIALS]
# Env:   BENCH_CPU (default 2, matching tests/bench/compare/compare.sh)

set -u
export LC_ALL=C

REPS="${1:-20000}"
TRIALS="${2:-9}"
BENCH_CPU="${BENCH_CPU:-2}"

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
PCREC="${PCREC:-$ROOT/build/pcrec}"
CC="${CC:-gcc}"

if taskset -c "$BENCH_CPU" true 2>/dev/null; then
    PIN="taskset -c $BENCH_CPU"
    PIN_NOTE="taskset -c $BENCH_CPU"
else
    PIN=""
    PIN_NOTE="NOT PINNED (taskset unavailable or not permitted)"
fi

D=$(mktemp -d "${TMPDIR:-/tmp}/mrlthru.XXXXXX")
trap 'rm -rf "$D"' EXIT

cat > "$D/drv.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "gen.h"
int main(int argc, char **argv)
{
    long reps = atol(argv[1]);
    size_t n = (size_t)atol(argv[2]);
    unsigned char *s = malloc(n + 2);
    ptrdiff_t caps[RX_NCAPS][2];
    struct timespec t0, t1;
    long i;
    volatile int sink = 0;
    memset(s, 'a', n);
    s[n] = 'b';
    /* warm */
    for (i = 0; i < 100; i++) sink += rx_search(s, n + 1, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (i = 0; i < reps; i++) sink += rx_search(s, n + 1, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf("%.1f\n", ((double)(t1.tv_sec - t0.tv_sec) * 1e9
                      + (double)(t1.tv_nsec - t0.tv_nsec)) / (double)reps);
    free(s);
    return sink == 0;
}
EOF

echo "# MRL pruning: cost on the common path, shipped compiler"
echo "# date:    $(date -u '+%Y-%m-%d %H:%M:%SZ')"
echo "# repo:    $(git -C "$ROOT" rev-parse --short HEAD)"
echo "# gcc:     $($CC --version | head -1)"
echo "# pinning: $PIN_NOTE"
echo "# load:    $(cut -d' ' -f1-3 /proc/loadavg) (1/5/15 min, $(nproc) cores)"
echo "# reps:    $REPS per trial, best of $TRIALS (best, not median: the"
echo "#          minimum is the least contaminated sample on a shared box)"
echo "# arms:    default vs -fno-length-prune. INCLUDES layout drift; see header."
echo
printf '%-34s %-3s %-8s %-12s %-12s %s\n' pattern W n pruned denied delta
printf '%-34s %-3s %-8s %-12s %-12s %s\n' ---- - ---- ---- ---- ----

one() {   # one <pattern> <stride> <n>
    pat="$1"; w="$2"; n="$3"
    for arm in on off; do
        rm -rf "$D/$arm"; mkdir -p "$D/$arm"
        flags=""
        [ "$arm" = off ] && flags="-fno-length-prune"
        # shellcheck disable=SC2086
        "$PCREC" -p rx $flags -o "$D/$arm/gen.c" -- "$pat" >/dev/null 2>&1 || {
            printf '%-34s %-3s %-8s %s\n' "$pat" "$w" "$n" "pcrec-fail"; return; }
        $CC -O2 -w -I "$D/$arm" -o "$D/$arm/t" "$D/drv.c" "$D/$arm/gen.c" \
            >/dev/null 2>&1 || {
            printf '%-34s %-3s %-8s %s\n' "$pat" "$w" "$n" "cc-fail"; return; }
    done
    best_on=""; best_off=""
    i=1
    while [ "$i" -le "$TRIALS" ]; do
        v=$($PIN "$D/on/t" "$REPS" "$n")
        best_on=$(printf '%s\n%s\n' "$best_on" "$v" | grep -v '^$' | sort -g | head -1)
        v=$($PIN "$D/off/t" "$REPS" "$n")
        best_off=$(printf '%s\n%s\n' "$best_off" "$v" | grep -v '^$' | sort -g | head -1)
        i=$((i + 1))
    done
    delta=$(awk -v a="$best_on" -v b="$best_off" 'BEGIN{printf "%+.2f%%", 100*(a-b)/b}')
    printf '%-34s %-3s %-8s %-12s %-12s %s\n' "$pat" "$w" "$n" \
           "${best_on} ns" "${best_off} ns" "$delta"
}

# §6's DENSE rows: a real follow, so every replica carries a bound.
one '(a{2,4}){10,50}b'          1 200
one '((?:aa){2,4}){10,50}b'     2 200
one '((?:aaa){2,4}){10,50}b'    3 200
# The exemplar's own shape at a length where NOTHING explodes, i.e. the
# population §8 predicts pays without being paid: the bound is emitted at
# every replica and never fires usefully.
one '(a{10,20}){10,50}b'        1 400
# An ORDINARY pattern with a bounded quantifier -- §8's "bounds will be
# emitted for them; the prediction is that they never fire and never change a
# verdict". This is what that costs.
one '(\d{3})-(\d{4})b'          1 16
one '([a-z]{2,4}){2,8}b'        1 40
