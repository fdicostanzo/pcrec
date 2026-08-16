#!/usr/bin/env bash
# docs/design/counterk_impl/probes/bench_k.sh — the K sweep.
#
# eng_brep_design.md S4.4's axes plus counterk_design.md S4.4's two additions:
#   - K = 1 measured on a REAL counter loop, not on the frames-rung star. The
#     star differs from a counter loop by a counter write, a compare and the
#     ABSENCE of an empty-iteration guard, and S4.3's recommendation of K = 8
#     rests on an estimate that substitutes one for the other.
#   - THREE subject regimes, where the archived estimate measured one: the loop
#     satisfied at its maximum, satisfied well below it, and FAILING after
#     maximal consumption -- the regime where backtracking actually runs and
#     where K should matter most.
#
# It is a MEASUREMENT and never a gate (D18: the dial must earn its value).
# Its home once the rung exists is [BENCH-1]'s bounded-repeats family; it lives
# here while the strategy it measures is still a design note.
#
# THE K AXIS IS INERT UNTIL THE RUNG EXISTS. `--unroll` has no producer today,
# so a real K sweep cannot be walked. THE REST OF THE HARNESS IS NOT INERT
# (critic panel finding C2): bodies, N, the three subject regimes, compile
# timing and match throughput are all measurable on the strategy that ships
# TODAY, and this script now runs that measurement end to end rather than
# printing stub strings. With K collapsed the K column reads "shipped" for
# every row and the header banner says so, so it stays impossible to mistake
# a collapsed-K row for a walked K sweep.
#
# THE THROUGHPUT DRIVER. For each surviving cell this script writes and
# compiles a small C driver (`driver.c`, house pattern from the sibling probe
# `step_charge.sh`: `#include "gen.c"`, compiled with `-I` at the temp dir,
# library-mode pcrec output with no `--emit-main`) that:
#   - builds the subject IN MEMORY, not via argv (subjects are meant to scale
#     past what a shell argv can carry even though today's replication limit
#     caps N well below that -- see the body-alternation note below);
#   - takes SIZE, FILL, TAIL, REGIME and TRIALS as argv;
#   - runs `rx_search` TRIALS times and reports the MINIMUM elapsed
#     nanoseconds (CLOCK_MONOTONIC) per search -- min-of-N is the house
#     convention, eng_brep_design.md S4.3's throughput table;
#   - prints one line: "<verdict> <bytes> <ns_per_search>".
#
# THE THREE SUBJECT REGIMES are built explicitly per body from a parallel
# data table (BODY_FILL / BODY_TAIL below) rather than derived from the
# pattern text, because deriving "a string this body matches" from the regex
# source is exactly the kind of clever-instrument failure this project's
# check-design lessons warn about:
#   - max      : N copies of FILL, then TAIL      -- loop satisfied at max,   MATCH
#   - belowmax : ~N/8 copies of FILL, then TAIL    -- satisfied well below it, MATCH
#   - fail     : N copies of FILL, NO TAIL         -- maximal consumption,
#                                                      then failure -- backtracks
#                                                      through the whole loop at
#                                                      every start position
#
# VALIDATION BEFORE TIMING. Only one strategy exists today, so there is no
# second artifact to differential against; the minimum bar this script holds
# instead is that the driver's reported verdict for each regime matches the
# regime's contract (max/belowmax -> match, fail -> nomatch). A mismatch is
# printed as a loud, cell-named VALIDATION-FAILED line and that cell's number
# is never printed as if it were a real measurement -- a silently wrong
# subject makes every number meaningless.
#
# Usage: bench_k.sh [--full]
# Env:   PCREC (default build/pcrec), CC (default cc), CFLAGS_OPT (default -O2),
#        TRIALS (default 3), TIMEOUT (default 300)
set -u
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
OPT="${CFLAGS_OPT:--O2}"
TRIALS="${TRIALS:-3}"
TMO="${TIMEOUT:-300}"
FULL=0
[ "${1:-}" = "--full" ] && FULL=1

OUT=$(mktemp -d "${TMPDIR:-/tmp}/ckbench.XXXXXX")
trap 'rm -rf "$OUT"' EXIT
[ -x "$PCREC" ] || { echo "no pcrec at $PCREC -- run make first" >&2; exit 2; }

# ---- the axes -------------------------------------------------------------
# BODIES: each declines both earlier rungs, or the sweep measures those rungs
# instead of this one. Verify with probes/measure_baseline.sh, whose rung
# census is exactly this check; a body that stamps anything but VM_RUNGS 0x2
# under -fno-counter does not belong here.
#
# DROPPED: `(a(b|(c|d)))`, the design note's own fifth full-mode body. Checked
# 2026-08-16 with `--engine=vm --emit-ir` on `(a(b|(c|d))){0,16}c`: it stamps
# VM_RUNGS 0x8 (the REVERSE-DETERMINISTIC rung), not 0x2 -- a nested-group
# alternation of this exact shape is taken by rung-select before counter-K
# ever sees it, so it would measure that rung under this one's name.
# Replaced with `((a)|a(b|c))`, which keeps the "group inside an alternation"
# shape the dropped body was there for and is confirmed VM_RUNGS 0x2 at
# N in {1, 16, 1000, 4000} (rung selection did not vary with N in that check).
if [ "$FULL" -eq 1 ]; then
    NS="1 2 4 8 16 32 64 128 256 1000 4000"
    KS="1 2 4 8 16 32 0"          # 0 means "K >= N", i.e. replication
    BODIES='((a)|ab) ((ab)|b) (a(b|c)?) ((a)|ab|abc|abcd|abcde) ((a)|a(b|c))'
else
    NS="8 16 64 256 4000"
    KS="1 8 0"
    BODIES='((a)|ab) (a(b|c)?)'
fi

# BODY_FILL: a string ONE iteration of the body matches (greedy, leftmost
# alternative first -- not derived from the pattern, stated explicitly).
# BODY_TAIL: the follow byte appended after the loop; every pattern in this
# sweep is "${body}{0,N}c", so this is 'c' for all bodies today, but it stays
# a per-body table (not a bare constant) so a future body that needs a
# different follow byte does not have to change the driver-invocation code,
# only this table.
declare -A BODY_FILL=(
    ["((a)|ab)"]="a"
    ["((ab)|b)"]="ab"
    ["(a(b|c)?)"]="a"
    ["((a)|ab|abc|abcd|abcde)"]="a"
    ["((a)|a(b|c))"]="a"
)
declare -A BODY_TAIL=(
    ["((a)|ab)"]="c"
    ["((ab)|b)"]="c"
    ["(a(b|c)?)"]="c"
    ["((a)|ab|abc|abcd|abcde)"]="c"
    ["((a)|a(b|c))"]="c"
)

# ---- capability probe: is there a rung to bench? --------------------------
have_unroll=0
if "$PCREC" --unroll=8 -p rx -o "$OUT/probe.c" -- 'a' >/dev/null 2>&1; then
    have_unroll=1
fi

echo "== bench_k =="
echo "commit  $(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo '?')"
echo "gcc     $($CC --version | head -1)"
echo "opt     $OPT   trials $TRIALS   mode $([ $FULL -eq 1 ] && echo full || echo short)"
echo

if [ "$have_unroll" -eq 0 ]; then
    cat <<EOF
INERT (K AXIS ONLY): this compiler has no --unroll, so the counter rung does
not exist yet and there is no second point on the K axis to compare against
today's single strategy.

Axes a real K sweep will walk once the rung lands:
  N       $NS
  K       $KS        (0 = K >= N, i.e. replication, the ground truth)
  body    $BODIES
  regime  max / below-max / failing-after-maximal-consumption
  metric  pcrec compile s, gcc $OPT compile s, emitted lines, ns/search

What is NOT allowed to be decided here (eng_brep_design.md S4.5): K is
per-artifact tuning and must not become a per-pattern heuristic in v1. The
only per-pattern movement of K that this lane proposes is S4.2's SAFETY CLAMP,
which moves K downward to keep a bound the compiler already enforces, and it
is not a bench outcome.

>>> THE K COLUMN IS "shipped" FOR EVERY ROW BELOW. Everything else --
>>> body x N x regime x compile time x throughput -- runs for real, on
>>> today's single shipped strategy, so this harness stays exercised end to
>>> end while it waits on --unroll. Do not read a "shipped" row as a K
>>> measurement; it is one point, not an axis.
EOF
fi

# ---- the throughput driver -------------------------------------------------
# Written once; house pattern is the sibling probe step_charge.sh's driver.c
# (`#include "gen.c"`, library-mode pcrec output, compiled with -I at $OUT).
cat > "$OUT/driver.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "gen.c"
/* driver N FILL TAIL REGIME TRIALS
 *   REGIME = max      -> N copies of FILL, then TAIL (loop at its max, MATCH)
 *            belowmax -> max(1, N/8) copies of FILL, then TAIL (well below
 *                        the max, MATCH)
 *            fail     -> N copies of FILL, no TAIL (maximal consumption,
 *                        then failure -- backtracks the whole loop at every
 *                        start position)
 * The subject is built IN MEMORY, never via argv. Prints one line:
 *   "<verdict> <bytes> <ns_per_search>", ns_per_search the MINIMUM of TRIALS
 * clock_gettime(CLOCK_MONOTONIC) samples around a single rx_search call.
 */
int main(int argc, char **argv)
{
    if (argc < 6) {
        fprintf(stderr, "usage: driver N FILL TAIL REGIME TRIALS\n");
        return 2;
    }
    size_t n = strtoul(argv[1], NULL, 10);
    const char *fill = argv[2], *tail = argv[3], *regime = argv[4];
    int trials = atoi(argv[5]);
    if (trials < 1) trials = 1;
    size_t fl = strlen(fill), tl = strlen(tail);
    if (fl == 0) { fprintf(stderr, "empty fill\n"); return 2; }

    size_t copies;
    int with_tail;
    if (strcmp(regime, "max") == 0) {
        copies = n; with_tail = 1;
    } else if (strcmp(regime, "belowmax") == 0) {
        copies = n / 8; if (copies < 1) copies = 1; with_tail = 1;
    } else if (strcmp(regime, "fail") == 0) {
        copies = n; with_tail = 0;
    } else {
        fprintf(stderr, "unknown regime %s\n", regime);
        return 2;
    }

    size_t body_bytes = copies * fl;
    size_t total = body_bytes + (size_t)(with_tail ? tl : 0);
    unsigned char *s = malloc(total + 1);
    if (!s) { fprintf(stderr, "oom\n"); return 2; }
    for (size_t i = 0; i < copies; i++)
        memcpy(s + i * fl, fill, fl);
    if (with_tail) memcpy(s + body_bytes, tail, tl);

    ptrdiff_t caps[RX_NCAPS][2];
    long long best = -1;
    int rc = 0;
    for (int t = 0; t < trials; t++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        rc = rx_search(s, total, 0, caps);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        long long ns = (long long)(t1.tv_sec - t0.tv_sec) * 1000000000LL
                      + (long long)(t1.tv_nsec - t0.tv_nsec);
        if (best < 0 || ns < best) best = ns;
    }
    const char *verdict = rc == 1 ? "match" : rc == 0 ? "nomatch"
                        : rc == RX_ERR_STEPS ? "STEPS" : "FRAMES";
    printf("%s %zu %lld\n", verdict, total, best);
    free(s);
    return 0;
}
EOF

# run_cell body n kshow uflag
# Compile-time metrics on the emit-main artifact (unchanged from before), then
# -- when that succeeds -- a second, library-mode artifact + the throughput
# driver above, run once per subject regime and validated before its number
# is trusted.
run_cell () {
    body=$1; n=$2; kshow=$3; uflag=$4
    pat="${body}{0,${n}}c"
    t0=$(date +%s.%N)
    # shellcheck disable=SC2086
    if ! timeout "$TMO" "$PCREC" -p rx --engine=vm $uflag --emit-main \
             -o "$OUT/g.c" -- "$pat" >/dev/null 2>&1; then
        printf '%-16s %-6s %-5s %s\n' "$body" "$n" "$kshow" \
               'REFUSED-OR-TIMEOUT (a finding: record it, do not re-run longer)'
        return
    fi
    t1=$(date +%s.%N)
    lines=$(wc -l < "$OUT/g.c")
    t2=$(date +%s.%N)
    if ! timeout "$TMO" "$CC" $OPT -o "$OUT/g" "$OUT/g.c" 2>/dev/null; then
        printf '%-16s %-6s %-5s %-8s GCC-FAILED\n' "$body" "$n" "$kshow" "$lines"
        return
    fi
    t3=$(date +%s.%N)
    pcrec_s=$(echo "$t1 $t0" | awk '{printf "%.3f", $1-$2}')
    gcc_s=$(echo "$t3 $t2" | awk '{printf "%.3f", $1-$2}')

    # ---- the throughput half: library-mode artifact + driver -------------
    rm -f "$OUT/gen.c" "$OUT/gen.h" "$OUT/drv"
    # shellcheck disable=SC2086
    if ! timeout "$TMO" "$PCREC" -p rx --engine=vm $uflag \
             -o "$OUT/gen.c" -- "$pat" >/dev/null 2>&1; then
        printf '%-16s %-6s %-5s %-8s %-10s %-10s GEN-REFUSED (emit-main artifact compiled, library-mode did not -- a finding)\n' \
               "$body" "$n" "$kshow" "$lines" "$pcrec_s" "$gcc_s"
        return
    fi
    if ! timeout "$TMO" "$CC" $OPT -Wall -Wextra -I"$OUT" \
             -o "$OUT/drv" "$OUT/driver.c" 2>"$OUT/drv.err"; then
        printf '%-16s %-6s %-5s %-8s %-10s %-10s DRV-CC-FAILED: %s\n' \
               "$body" "$n" "$kshow" "$lines" "$pcrec_s" "$gcc_s" \
               "$(head -1 "$OUT/drv.err")"
        return
    fi

    fill=${BODY_FILL[$body]}
    tail=${BODY_TAIL[$body]}
    ns_max=INVALID ns_below=INVALID ns_fail=INVALID
    for regime in max belowmax fail; do
        case $regime in
            max|belowmax) want=match ;;
            fail)          want=nomatch ;;
        esac
        if ! res=$(timeout "$TMO" "$OUT/drv" "$n" "$fill" "$tail" "$regime" "$TRIALS" 2>/dev/null); then
            printf '%-16s %-6s %-5s %-8s regime=%-9s TIMEOUT >%ss -- A FINDING, recorded, not re-run longer\n' \
                   "$body" "$n" "$kshow" "$lines" "$regime" "$TMO"
            continue
        fi
        # shellcheck disable=SC2086
        set -- $res
        got_verdict=$1; got_bytes=$2; got_ns=$3
        if [ "$got_verdict" != "$want" ]; then
            printf '%-16s %-6s %-5s %-8s regime=%-9s VALIDATION-FAILED: wanted %s, got %s on %s bytes -- number DISCARDED\n' \
                   "$body" "$n" "$kshow" "$lines" "$regime" "$want" "$got_verdict" "$got_bytes"
            continue
        fi
        case $regime in
            max)      ns_max=$got_ns ;;
            belowmax) ns_below=$got_ns ;;
            fail)     ns_fail=$got_ns ;;
        esac
    done

    printf '%-16s %-6s %-5s %-8s %-10s %-10s %-12s %-12s %s\n' \
           "$body" "$n" "$kshow" "$lines" "$pcrec_s" "$gcc_s" \
           "$ns_max" "$ns_below" "$ns_fail"
}

# ---- the sweep --------------------------------------------------------------
# Every cell runs under `timeout`, and a timeout is a RECORDED FINDING rather
# than a reason to re-run longer (D45's posture applied to a bench that is not
# itself budgeted). This runs UNCONDITIONALLY -- with K collapsed to
# "shipped" when --unroll has no producer, walked for real once it does.
printf '%-16s %-6s %-5s %-8s %-10s %-10s %-12s %-12s %s\n' \
       body N K lines pcrec_s gcc_s 'ns/max' 'ns/belowmax' 'ns/fail'
for body in $BODIES; do
  for n in $NS; do
    if [ "$have_unroll" -eq 0 ]; then
        run_cell "$body" "$n" shipped ""
        continue
    fi
    for k in $KS; do
        if [ "$k" -eq 0 ]; then uflag="-fno-counter"; kshow="rep"
        else uflag="--unroll=$k"; kshow="$k"; fi
        run_cell "$body" "$n" "$kshow" "$uflag"
    done
  done
done
