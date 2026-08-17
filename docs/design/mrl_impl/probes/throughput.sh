#!/bin/sh
# docs/design/mrl_impl/probes/throughput.sh — what MRL pruning COSTS on the
# common path, measured against the SHIPPED compiler.
#
# D18's speed mandate and D22's "must not be traded against execution speed"
# apply to the bound, which sits on the FORWARD path. D51 ruling 1's adoption
# bar was <= 2% at FULL CLAMP DENSITY, taken from k23_design.md §6's prototype
# measurement; this re-takes it against the emitter.
#
# THREE ARMS, because two cannot answer the question. §6's own instrument had
# a PLACEBO for a reason this probe reproduced the hard way: its first version
# ran pruned-vs-denied only and reported +27.8% on a 12 ns pattern whose VM is
# never even entered on the subject being timed. That is not the clamp; it is
# what inserting any code at all does to the layout of a translation unit.
#
#   PRUNED  — the shipped default.
#   DENIED  — `-fno-length-prune`, byte-for-byte pre-MRL pcrec. The
#             pruned-vs-denied delta is the ADOPTION cost, which is what D51's
#             bar is about, and it includes layout.
#   PLACEBO — the pruned artifact with the two MRL macros REDEFINED so the
#             bound is computed with the same instruction shape and can never
#             bind: `minrest` forced to 0 and the ceiling forced to the subject
#             end, so `MRL_SHORT` is `n < pos` (never) and `MRL_CAP` is the
#             largest lattice point at or below the furthest position the scan
#             could reach anyway. Same comparisons, same integer division, same
#             site count, no pruning. §6's placebo, reachable without a
#             compiler flag because it is a two-line edit of the emitted C.
#
# So `clamp` (pruned vs placebo) is the bound's own instructions, and
# `layout` (placebo vs denied) is everything else the insertion moved. §6
# measured layout's share swinging from 12% to 59% across three strides, so
# the split is not a constant and should not be quoted as one.
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
echo "# arms:    pruned / placebo (bound cannot bind) / denied (-fno-length-prune)."
echo "#          clamp = pruned vs placebo; layout = placebo vs denied; total = pruned vs denied."
echo
printf '%-30s %-2s %-5s %-10s %-10s %-10s %-9s %-9s %s\n' \
       pattern W n pruned placebo denied clamp layout total
printf '%-30s %-2s %-5s %-10s %-10s %-10s %-9s %-9s %s\n' \
       ---- - ---- ---- ---- ---- ---- ---- ----

one() {   # one <pattern> <stride> <n>
    pat="$1"; w="$2"; n="$3"
    for arm in on off; do
        rm -rf "$D/$arm"; mkdir -p "$D/$arm"
        flags=""
        [ "$arm" = off ] && flags="-fno-length-prune"
        # shellcheck disable=SC2086
        "$PCREC" -p rx $flags -o "$D/$arm/gen.c" -- "$pat" >/dev/null 2>&1 || {
            printf '%-30s %-2s %-5s %s\n' "$pat" "$w" "$n" "pcrec-fail"; return; }
        $CC -O2 -w -I "$D/$arm" -o "$D/$arm/t" "$D/drv.c" "$D/$arm/gen.c" \
            >/dev/null 2>&1 || {
            printf '%-30s %-2s %-5s %s\n' "$pat" "$w" "$n" "cc-fail"; return; }
    done
    # The PLACEBO: the pruned artifact, its two macros made unable to bind.
    rm -rf "$D/pl"; mkdir -p "$D/pl"
    sed -e 's/^\( *\)((rx_ceil) < (size_t)(mr_) || (rx_ceil) - (size_t)(mr_) < (p_))/\1((n) < (size_t)0 || (n) - (size_t)0 < (p_))/' \
        -e 's/^\( *\)((p_) + (size_t)(w_) \* (((rx_ceil) - (size_t)(mr_) - (p_)) \/ (size_t)(w_)))/\1((p_) + (size_t)(w_) * (((n) - (size_t)0 - (p_)) \/ (size_t)(w_)))/' \
        "$D/on/gen.c" > "$D/pl/gen.c"
    cp "$D/on/gen.h" "$D/pl/gen.h" 2>/dev/null
    if ! cmp -s "$D/on/gen.c" "$D/pl/gen.c"; then
        $CC -O2 -w -I "$D/pl" -o "$D/pl/t" "$D/drv.c" "$D/pl/gen.c" \
            >/dev/null 2>&1 || { printf '%-30s %s\n' "$pat" "placebo-cc-fail"; return; }
        have_pl=1
    else
        # No macro to neutralise: the artifact carries no bound, so the
        # placebo IS the pruned arm and the clamp column is 0 by construction.
        have_pl=0
    fi
    best_on=""; best_off=""; best_pl=""
    i=1
    while [ "$i" -le "$TRIALS" ]; do
        v=$($PIN "$D/on/t" "$REPS" "$n")
        best_on=$(printf '%s\n%s\n' "$best_on" "$v" | grep -v '^$' | sort -g | head -1)
        v=$($PIN "$D/off/t" "$REPS" "$n")
        best_off=$(printf '%s\n%s\n' "$best_off" "$v" | grep -v '^$' | sort -g | head -1)
        if [ "$have_pl" = 1 ]; then
            v=$($PIN "$D/pl/t" "$REPS" "$n")
            best_pl=$(printf '%s\n%s\n' "$best_pl" "$v" | grep -v '^$' | sort -g | head -1)
        fi
        i=$((i + 1))
    done
    [ "$have_pl" = 1 ] || best_pl="$best_on"
    printf '%-30s %-2s %-5s %-10s %-10s %-10s %-9s %-9s %s\n' "$pat" "$w" "$n" \
        "$best_on" "$best_pl" "$best_off" \
        "$(awk -v a="$best_on" -v b="$best_pl"  'BEGIN{printf "%+.2f%%", 100*(a-b)/b}')" \
        "$(awk -v a="$best_pl" -v b="$best_off" 'BEGIN{printf "%+.2f%%", 100*(a-b)/b}')" \
        "$(awk -v a="$best_on" -v b="$best_off" 'BEGIN{printf "%+.2f%%", 100*(a-b)/b}')"
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
