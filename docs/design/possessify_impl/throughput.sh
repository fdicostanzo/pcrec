#!/usr/bin/env bash
# docs/design/possessify_impl/throughput.sh — TWO archived cells (D35 style),
# and deliberately not a bench floor.
#
# WHY NOT A FLOOR. `make bench`'s floors exist to catch a regression in
# something that already ships. Possessification REMOVES machinery; there is
# nothing here that could regress in the direction a floor guards, and a floor
# would only pin a number the next ladder rung will move. The row's real
# validation is that the answers do not change (tests/possessify/
# run_possdiff.sh) and that the artifact's declared capacity moved with the
# machinery (run_possessify_tests.sh). These are demonstration cells, archived
# so "the loop is a forward scan" has numbers attached to it.
#
# THE PATTERN. `(x)(?:a|bc)+d` over a long run of `a` with no trailing `d` —
# the shape possessification is FOR. Every iteration succeeds, the follow never
# does, and the denied build pushes one frame per iteration to discover that.
# The possessified build cuts back to the loop's entry depth at every iteration
# boundary, so it holds one frame however long the subject is.
#
# CELL 1 — THROUGHPUT, inside both artifacts' declared limits. The comparison
# has to be run somewhere BOTH artifacts can answer, or it is a comparison of
# two different programs; cell 2 is what says where that is.
#
# CELL 2 — THE CAPABILITY BOUNDARY, which is the more interesting number and
# was found by cell 1 going wrong. Timed at 200,000 bytes, the two builds
# returned DIFFERENT results — and that is not a divergence, it is the feature:
# the denied artifact stamps `subject_ceiling = 512` and honestly returns
# RX_ERR_FRAMES above it, while the possessified one stamps no limit and
# answers. §5.1's "the failure surfaces must agree" is therefore a claim about
# the INTERSECTION of the two declared limits, and this cell measures where
# that intersection ends. It ends exactly at the stamp: the two agree on every
# length up to 511 and part at 512.
#
# Usage: bash docs/design/possessify_impl/throughput.sh [> throughput.txt]

set -u
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"

W="$(mktemp -d "${TMPDIR:-/tmp}/pthru.XXXXXX")"
trap 'rm -rf "$W"' EXIT

PAT='(x)(?:a|bc)+d'
N=${N:-500}          # inside BOTH artifacts' limits -- see cell 2
REPS=${REPS:-200000}

cat > "$W/drv.c" <<EOF
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "gen.h"
int main(int argc, char **argv)
{
    size_t n = (size_t)atol(argv[1]);
    long reps = atol(argv[2]);
    unsigned char *s = malloc(n + 2);
    s[0] = 'x';
    memset(s + 1, 'a', n);
    ptrdiff_t caps[RX_NCAPS][2];
    struct timespec t0, t1;
    int r = 0;
    if (reps == 0) { printf("%d\n", rx_search(s, n + 1, 0, caps)); return 0; }
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < reps; i++) r = rx_search(s, n + 1, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double el = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    printf("result=%-3d  %.4f s  %.1f MB/s\n", r, el,
           (reps * (double)(n + 1)) / el / 1e6);
    free(s);
    return 0;
}
EOF

echo "== [ENG-BREP] possessification: two archived cells =="
echo "date:    $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "commit:  $(cd "$ROOT_DIR" && git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "gcc:     $($CC --version | head -1)"
echo "pattern: $PAT"
echo "subject: 'x' followed by N x 'a', no trailing 'd'"
echo

for mode in possessified denied; do
    flags=""
    [ "$mode" = denied ] && flags="-fno-possessify"
    mkdir -p "$W/$mode"
    # shellcheck disable=SC2086
    "$PCREC" -p rx --engine=vm $flags -o "$W/$mode/gen.c" -- "$PAT" \
        >/dev/null 2>&1 || { echo "$mode: pcrec refused"; exit 1; }
    $CC -O2 -w -std=gnu11 -I "$W/$mode" -o "$W/$mode/t" "$W/drv.c" \
        "$W/$mode/gen.c" || { echo "$mode: did not compile"; exit 1; }
done

echo "-- cell 1: throughput at N=$N ($REPS reps), inside both declared limits"
for mode in possessified denied; do
    printf '  %-14s %s' "$mode" "$("$W/$mode/t" "$N" "$REPS")"
    printf '                 RX_BT_FRAMES=%s  subject_ceiling=%s\n' \
        "$(sed -n 's/^#define RX_BT_FRAMES //p' "$W/$mode/gen.c")" \
        "$(grep -oE '\.subject_ceiling = [0-9]+' "$W/$mode/gen.c" | grep -oE '[0-9]+$')"
done
echo "  Both results must be equal, or the timing compares two programs."
echo

echo "-- cell 2: the capability boundary (0 = nomatch, -3 = RX_ERR_FRAMES)"
printf '  %-8s %-14s %s\n' "length" "possessified" "denied"
for n in 100 400 500 510 511 512 513 1000 200000; do
    printf '  %-8s %-14s %s\n' "$n" "$("$W/possessified/t" "$n" 0)" \
                                    "$("$W/denied/t" "$n" 0)"
done
echo
echo "  The two agree on every length the DENIED artifact declares it can"
echo "  handle, and part at exactly its stamped subject_ceiling. Above it the"
echo "  denied build fails honestly (which is D44.1's honest-stamp design"
echo "  working) and the possessified build answers, because its loop no longer"
echo "  owes a frame per iteration. That is §7's prediction as a measurement:"
echo "  the stamp is EXACT at its boundary rather than conservative, in both"
echo "  builds, which is also why the failure-surface half of §5.1's comparison"
echo "  is well defined -- it is a claim about the intersection of the two"
echo "  declared limits, and this is where that intersection ends."
