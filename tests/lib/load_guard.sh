# tests/lib/load_guard.sh — [TT-10] ONE implementation of THE LOAD GUARD: a
# THIRD outcome (never PASS, never FAIL — a cell the runner counts and
# prints separately) for a check whose budget is a CPU-TIME cap sized
# against a QUIET box.
#
# WHY A CPU CAP IS NOT ENOUGH ON ITS OWN. tests/resource's 45s compile-CPU
# ceiling (K7_CPU) is already wired through `scripts/watchdog -c` — CPU
# time, summed across the tree, not wall — which docs/dev/decisions.md D45
# and tests/lib/gen_timeout.sh's own header call "load-RESILIENT". Resilient
# is not immune: docs/testing.md's own measurement is that CPU-time
# ACCOUNTING itself inflates under real contention (memory-subsystem thrash,
# reduced instructions-per-cycle under SMT/cache pressure), not merely that
# wall stretches around a fixed amount of CPU work — "CPU inflation tops out
# near 2x" under a single concurrent `-j<nproc>` build. [TT-10]'s own K31
# addendum (docs/dev/plan.md) measured WORSE than that ceiling on a box at
# load average 31 on 12 cores (ratio 2.58): `tests/resource`'s 45s CPU cap
# failed at a MEASURED 53s of CPU (the A/B control's own reference build
# also crossed it, 53s vs 49s), and `tests/counterk`'s
# `((a)|ab){4000}c` cell (K32) lost 28-29 dependent cases to the shared
# corpus harness's wall backstop the same night. Both cells are green solo
# every time. A cap this sized already prices in the docs/testing.md
# "near 2x" quiet-box-vs-one-concurrent-build figure (the resource cap has
# ~2.9x headroom over its own measured 15.4s quiet cost); what it cannot
# price in is a box carrying MORE contention than that reference point, and
# there is no way to raise the cap enough to buy that back without making
# it stop bounding anything on a quiet box (D45's own tradeoff, restated
# here rather than re-litigated).
#
# THE GUARD, THEREFORE, IS NOT A DIFFERENT CAP: it is a PRE-FLIGHT READING
# that says "the box is contended enough that this cap's verdict has
# stopped meaning what it's supposed to mean" and reports a THIRD outcome
# instead of pretending a CPU-kill under those conditions is either a green
# check or a real regression. D45's budgets (K7_CPU/K7_MEM/K7_SECS,
# GENCPU/GENTIMEOUT, ...) are UNCHANGED by this file and never touched by
# it — see docs/dev/plan.md [TT-10]'s own instruction that they stay put.
#
# THE THRESHOLD, LOAD_GUARD_RATIO (default 2.0): the 1-MINUTE load average
# divided by `nproc`. Justified from the two numbers above rather than
# picked: 1.0 is "one concurrent `-j<nproc>` build", the contention level
# docs/testing.md's own "~2x inflation" figure was MEASURED at and which
# every CPU budget in this tree already prices in via its own headroom;
# 2.58 is the K31 addendum's own MEASURED failure ratio, where a 45s cap
# with ~2.9x headroom over its 15.4s quiet baseline still broke. 2.0 sits
# strictly between the two: high enough that ordinary single-build
# contention (this lane's own `-j4`, one other lane's build) never trips
# it, low enough to fire BEFORE the exact contention level the addendum
# measured actually breaking a cap — pre-empting the failure rather than
# rationalising it after the fact. Override with LOAD_GUARD_RATIO for a box
# whose core count or workload mix makes 2.0 wrong; record the measurement
# that justified the new number, the same revisit-when every D45 budget
# carries.
#
# Usage: source this file, then before running a load-sensitive cell:
#     if load_guard_tripped; then
#         inc "cell name: SKIPPED — box too contended for this cell's CPU
#              cap to mean anything ($(load_guard_ratio) > $LOAD_GUARD_RATIO)"
#         continue   # or return/skip, per caller's own loop shape
#     fi
#     ... run the cell normally, score PASS/FAIL as usual ...
# The caller owns its own `inc()` (a THIRD counter, printed and totalled
# separately from pass/fail — never folded into either, or a green
# INCONCLUSIVE run would misreport as "all cells passed" and a red one
# would misreport as a real regression).

LOAD_GUARD_RATIO="${LOAD_GUARD_RATIO:-2.0}"

# [MACPORT] tests/lib/loadavg.sh / ncpu.sh give darwin (no /proc at all) a
# REAL reading (sysctl vm.loadavg / hw.ncpu) instead of this function's own
# old "0.00, never trips" fallback — which would have meant the guard could
# never fire under real contention on this box, silently. `caller's own
# ROOT_DIR` is already how every existing sourcer of this file resolves
# its sibling libs (gen_timeout.sh, timeout_bin.sh, ...); `${BASH_SOURCE[0]%/*}`
# is this file's OWN directory, used here instead so load_guard.sh keeps
# working for a caller that sources it without having set ROOT_DIR first.
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/loadavg.sh"
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/ncpu.sh"

# load_guard_ratio — 1-minute load average / ncpu, as a decimal (2 places).
# Prints "0.00" (never trips the guard) only if load1/NCPU themselves come
# back empty/non-positive, which loadavg.sh/ncpu.sh already guard against
# on every platform this project targets — this is now a true last resort,
# not the darwin path.
load_guard_ratio() {
    local avg1 n
    avg1="$(load1)"
    n="$NCPU"
    if [ -z "$avg1" ] || [ -z "$n" ] || [ "$n" -le 0 ]; then
        echo "0.00"
        return
    fi
    awk -v a="$avg1" -v n="$n" 'BEGIN { printf "%.2f", a / n }'
}

# load_guard_tripped — exit 0 (tripped: box too contended, caller should
# report INCONCLUSIVE and skip) or 1 (fine: proceed normally). Always
# prints the reading it acted on to stderr, so a run's log carries the
# number behind the decision rather than a silent skip.
load_guard_tripped() {
    local ratio
    ratio="$(load_guard_ratio)"
    if awk -v r="$ratio" -v t="$LOAD_GUARD_RATIO" 'BEGIN { exit !(r > t) }'; then
        echo "load guard: 1-min-load/nproc ratio $ratio > threshold $LOAD_GUARD_RATIO — box too contended for this cell's CPU cap to mean anything (docs/testing.md's >2x CPU-time-inflation finding; [TT-10] K31 addendum)" >&2
        return 0
    fi
    echo "load guard: 1-min-load/nproc ratio $ratio <= threshold $LOAD_GUARD_RATIO — proceeding" >&2
    return 1
}
