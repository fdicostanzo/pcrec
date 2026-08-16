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
# INERT UNTIL THE RUNG EXISTS. `--unroll` has no producer today, so with no
# compiler support this script reports the axes it cannot walk and exits 0
# rather than printing numbers that are secretly about replication. A bench
# harness that silently measures the wrong strategy is exactly D46's motivating
# scenario one layer up.
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
if [ "$FULL" -eq 1 ]; then
    NS="1 2 4 8 16 32 64 128 256 1000 4000"
    KS="1 2 4 8 16 32 0"          # 0 means "K >= N", i.e. replication
    BODIES='((a)|ab) ((ab)|b) (a(b|c)?) ((a)|ab|abc|abcd|abcde) (a(b|(c|d)))'
else
    NS="8 16 64 256 4000"
    KS="1 8 0"
    BODIES='((a)|ab) (a(b|c)?)'
fi

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
INERT: this compiler has no --unroll, so the counter rung does not exist yet
and every cell below would measure replication under a different name.

Axes this sweep will walk once the rung lands:
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
EOF
    exit 0
fi

# ---- the sweep ------------------------------------------------------------
# Reached only once --unroll exists. Every cell runs under `timeout`, and a
# timeout is a RECORDED FINDING rather than a reason to re-run longer (D45's
# posture applied to a bench that is not itself budgeted).
printf '%-16s %-6s %-5s %-8s %-10s %-10s %-12s %s\n' \
       body N K lines pcrec_s gcc_s regime ns_per_search
for body in $BODIES; do
  for n in $NS; do
    for k in $KS; do
        pat="${body}{0,${n}}c"
        if [ "$k" -eq 0 ]; then uflag="-fno-counter"; kshow="rep"
        else uflag="--unroll=$k"; kshow="$k"; fi
        t0=$(date +%s.%N)
        # shellcheck disable=SC2086
        if ! timeout "$TMO" "$PCREC" -p rx --engine=vm $uflag --emit-main \
                 -o "$OUT/g.c" -- "$pat" >/dev/null 2>&1; then
            printf '%-16s %-6s %-5s %s\n' "$body" "$n" "$kshow" \
                   'REFUSED-OR-TIMEOUT (a finding: record it, do not re-run longer)'
            continue
        fi
        t1=$(date +%s.%N)
        lines=$(wc -l < "$OUT/g.c")
        t2=$(date +%s.%N)
        timeout "$TMO" "$CC" $OPT -o "$OUT/g" "$OUT/g.c" 2>/dev/null || \
            { printf '%-16s %-6s %-5s %-8s GCC-FAILED\n' "$body" "$n" "$kshow" "$lines"; continue; }
        t3=$(date +%s.%N)
        printf '%-16s %-6s %-5s %-8s %-10s %-10s %-12s %s\n' \
               "$body" "$n" "$kshow" "$lines" \
               "$(echo "$t1 $t0" | awk '{printf "%.3f", $1-$2}')" \
               "$(echo "$t3 $t2" | awk '{printf "%.3f", $1-$2}')" \
               "(throughput)" "TODO: three regimes"
    done
  done
done
