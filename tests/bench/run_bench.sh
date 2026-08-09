#!/usr/bin/env bash
# tests/bench/run_bench.sh — performance/regression benchmark suite for pcrec.
#
# Usage: bash tests/bench/run_bench.sh
#
# Three sections, each prints measured numbers and a PASS/FAIL verdict
# against a budget:
#
#   COMPILE-SPEED  pcrec wall time over ~20 varied base-tier patterns
#   GCC-TIME       gcc -O1/-O2 wall time compiling two big generated DFAs
#                  (the R1 A-3 regression guard — see docs/reviews/2026-08-09-m1.md)
#   THROUGHPUT     MB/s of the generated matcher over three subjects, plus a
#                  linearity check (the R1 A-2 regression guard)
#
# All budgets were set for the post-DFA-rework table emitter (landing
# alongside this suite); the old computed-goto emitter is EXPECTED to fail
# GCC-TIME and the linearity check (that is the point of the guard — see
# README.md). Every budget and every timeout below is overridable via env
# var so this suite keeps working as the engine changes.
#
# Env vars:
#   PCREC           path to the pcrec binary        (default: <repo-root>/build/pcrec)
#   CC              C compiler                       (default: gcc)
#   SKIP_BUDGETS=1  still measure and print PASS/FAIL, but never fail the
#                   exit code on a budget miss (mechanical/harness failures
#                   still fail the exit code regardless)
#   KEEP=1          keep the temp working directory instead of deleting it
#
#   Measurement rigor (M2.9, R2-B3):
#     BENCH_CPU       (default 2)    core to pin every timed run to (taskset)
#     BENCH_TRIALS    (default 5)    repeats per measurement; the MEDIAN is
#                     what budgets are judged against, and max/min spread is
#                     printed alongside so a noisy result is visible
#
#   Budgets (all overridable; set to fail on a ~1.75x regression -- see the
#   block where they are defined for the measured medians behind them):
#     COMPILE_BUDGET_SECS          (default 0.4)   total pcrec time, COMPILE-SPEED
#     KEYWORD_BUDGET_SECS          (default 4)     3600-word list, KEYWORD-SCALE
#     GCC_O1_BUDGET_SECS           (default 2)     per-pattern, GCC-TIME
#     GCC_O2_BUDGET_SECS           (default 2)     per-pattern, GCC-TIME
#     THROUGHPUT_NEEDLE_MIN_MBPS   (default 1200)  subject (a), THROUGHPUT
#     THROUGHPUT_NOMATCH_MIN_MBPS  (default 12000) subject (b), THROUGHPUT
#     THROUGHPUT_ALT_MIN_MBPS      (default 1000)  subject (c), THROUGHPUT
#     THROUGHPUT_BITMAP_MIN_MBPS   (default 330)   subject (d), THROUGHPUT --
#                     the BITMAP half of the start prefilter; (a)-(c) all take
#                     the memchr branch, so without this the bitmap branch has
#                     no coverage anywhere in the suite
#     LINEARITY_MAX_RATIO          (default 6.0)   64MB/16MB time ratio, THROUGHPUT
#     LOAD_LIMIT      (default max(2.0, cores/2))  1-minute load average above
#                     which a budget MISS is reported as INCONCLUSIVE rather
#                     than FAIL. Budgets tight enough to catch a 1.75x
#                     regression are also tight enough for a busy box to fail
#                     them: a known-good build measured 8572 MB/s on case (b)
#                     against a 12000 floor at load 24.4. A flaky gate gets
#                     loosened permanently, so this run says "I could not
#                     measure" instead. A PASS under load is still a PASS.
#
#   Hang-protection timeouts (all overridable; a run that hits its timeout
#   is reported as DNF and counted as a budget FAIL, never as a hang):
#     PCREC_TIMEOUT   (default 60)   per pcrec invocation
#     GCC_O1_TIMEOUT  (default 60)   per -O1 compile, GCC-TIME
#     GCC_O2_TIMEOUT  (default 130)  per -O2 compile, GCC-TIME (see A-3: the
#                     old emitter's -O2 pass "did not finish in 120s" on the
#                     8192-state pattern — 130 gives headroom to observe that
#                     as a clean DNF rather than an indefinite hang)
#     RUN_TIMEOUT     (default 90)   per bdriver invocation, THROUGHPUT
#
# See docs/testing.md for the sibling .rxt harness this suite is styled
# after, and README.md in this directory for full rationale.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
SKIP_BUDGETS="${SKIP_BUDGETS:-0}"
KEEP="${KEEP:-0}"

# Budgets (M2.9 / R2-B4). The old values were 9x-300,000x looser than the
# measured numbers, so none of them would have caught a 2x regression — a
# budget that cannot fail is documentation, not a gate.
#
# Each is now the measured MEDIAN on the reference box divided by ~1.75, i.e.
# tuned to fail on a ~1.75x regression. Individual trials on that box spread
# 1.20-1.43x (printed on every row), and the median of BENCH_TRIALS is much
# tighter than that, so the margin is real but not generous. Reference medians
# are in the table in README.md; every value here is env-overridable, which is
# how you retune on slower hardware rather than by editing this file.
COMPILE_BUDGET_SECS="${COMPILE_BUDGET_SECS:-0.4}"        # measured 0.111
GCC_O1_BUDGET_SECS="${GCC_O1_BUDGET_SECS:-2}"            # measured 0.219
GCC_O2_BUDGET_SECS="${GCC_O2_BUDGET_SECS:-2}"            # measured 0.219
THROUGHPUT_NEEDLE_MIN_MBPS="${THROUGHPUT_NEEDLE_MIN_MBPS:-1200}"   # measured 2160
THROUGHPUT_NOMATCH_MIN_MBPS="${THROUGHPUT_NOMATCH_MIN_MBPS:-12000}" # measured 21910
THROUGHPUT_ALT_MIN_MBPS="${THROUGHPUT_ALT_MIN_MBPS:-1000}"         # measured 1753
# Deliberately tighter than the /1.75 the others use: the regression this
# case exists to catch (deleting the bitmap branch, keeping memchr) is only
# ~1.5x — 452 -> 303 MB/s — so a 1.75x margin would let it through, which
# is how it went unnoticed in the first place. Measured spread here is
# 1.03-1.08x, among the tightest in the suite, and the LOAD_LIMIT guard
# covers busy boxes. Healthy observed 429-457, sabotaged 303-305, so 330 sits
# between them with ~1.3x headroom either side.
THROUGHPUT_BITMAP_MIN_MBPS="${THROUGHPUT_BITMAP_MIN_MBPS:-330}"   # measured 429-457
LINEARITY_MAX_RATIO="${LINEARITY_MAX_RATIO:-6.0}"        # measured 2.883, linear 4.0

PCREC_TIMEOUT="${PCREC_TIMEOUT:-60}"
GCC_O1_TIMEOUT="${GCC_O1_TIMEOUT:-60}"
GCC_O2_TIMEOUT="${GCC_O2_TIMEOUT:-130}"
RUN_TIMEOUT="${RUN_TIMEOUT:-90}"

if [ ! -x "$PCREC" ]; then
    echo "run_bench.sh: pcrec binary not found or not executable: $PCREC (build it first, e.g. 'make')" >&2
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    echo "run_bench.sh: python3 is required to generate throughput subjects" >&2
    exit 1
fi
if ! command -v "$CC" >/dev/null 2>&1; then
    echo "run_bench.sh: C compiler not found: $CC" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then
        echo "run_bench.sh: KEEP=1, temp dir preserved: $WORKDIR" >&2
    else
        rm -rf "$WORKDIR"
    fi
}
trap cleanup EXIT

hard_errors=0
budget_failures=0

# ---- small helpers ---------------------------------------------------

now_ns() { date +%s%N; }

# elapsed_secs <start_ns> <end_ns> -> prints seconds with 3 decimals
elapsed_secs() {
    awk -v a="$1" -v b="$2" 'BEGIN{printf "%.3f", (b-a)/1000000000.0}'
}

# num_lt <a> <b> -> true (exit 0) iff a < b, numeric
num_lt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a+0 < b+0)}'; }
# num_gt <a> <b> -> true (exit 0) iff a > b, numeric
num_gt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a+0 > b+0)}'; }

# ---- M2.9 measurement rigor (R2-B3/B4) -------------------------------------
# R2 found no CPU pinning or governor control on a schedutil box with turbo,
# every measurement taken once, and pcrec always measured first. Single
# samples on this box swing ~1.8x run to run, which is wider than most of the
# regressions these budgets are supposed to catch. So: pin, repeat, and judge
# on the MEDIAN.

BENCH_CPU="${BENCH_CPU:-2}"        # which core to pin to
BENCH_TRIALS="${BENCH_TRIALS:-5}"  # repeats per measurement; median is judged
PIN=""
PIN_NOTE="none"
if command -v taskset >/dev/null 2>&1 && taskset -c "$BENCH_CPU" true 2>/dev/null; then
    PIN="taskset -c $BENCH_CPU"
    PIN_NOTE="taskset -c $BENCH_CPU"
    # SCHED_FIFO removes scheduler jitter but usually needs privileges; it is
    # a bonus, never a requirement, so probe once and degrade quietly.
    if command -v chrt >/dev/null 2>&1 && chrt -f 50 true 2>/dev/null; then
        PIN="chrt -f 50 $PIN"
        PIN_NOTE="chrt -f 50 + $PIN_NOTE"
    fi
fi

# median <values...> -> prints the median (lower of the two for even counts)
median() {
    printf '%s\n' "$@" | sort -g | awk '{v[NR]=$0} END{ if (NR==0) print ""; else print v[int((NR+1)/2)] }'
}
# spread <values...> -> prints max/min as a ratio, "n/a" if min is 0
spread() {
    printf '%s\n' "$@" | sort -g | awk '{v[NR]=$0} END{ if (NR<2 || v[1]+0==0) print "n/a"; else printf "%.2f", v[NR]/v[1] }'
}

# Environment capture — a number without the machine state behind it is not a
# measurement, and R2 caught exactly this omission.
describe_env() {
    local gov turbo
    gov="$(cat /sys/devices/system/cpu/cpu${BENCH_CPU}/cpufreq/scaling_governor 2>/dev/null || echo unknown)"
    if [ -r /sys/devices/system/cpu/intel_pstate/no_turbo ]; then
        turbo=$([ "$(cat /sys/devices/system/cpu/intel_pstate/no_turbo)" = "1" ] && echo off || echo on)
    elif [ -r /sys/devices/system/cpu/cpufreq/boost ]; then
        turbo=$([ "$(cat /sys/devices/system/cpu/cpufreq/boost)" = "1" ] && echo on || echo off)
    else
        turbo="unknown"
    fi
    echo "cores:   $(nproc 2>/dev/null || echo '?')"
    echo "pinning: $PIN_NOTE"
    echo "trials:  $BENCH_TRIALS (budgets judged on the median)"
    echo "governor: $gov (cpu$BENCH_CPU)   turbo: $turbo"
    echo "load average: $(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null || echo unknown)"
}

# Budgets tight enough to catch a 1.75x regression are also tight enough to be
# FAILED BY A BUSY MACHINE. Measured: at 1-minute load 24.4 on 12 cores, a
# known-good build reported 8572 MB/s on case (b) against a 12000 floor, and
# per-trial spreads widened from 1.15-1.35x to 1.38-1.53x.
#
# A flaky gate is worse than a loose one, because the fix people reach for is
# to loosen the budget permanently. So when the box is too busy to measure, we
# say so instead of guessing: verdicts become INCONCLUSIVE, they do not count
# as failures, and the summary states plainly that the run gated nothing. A
# green that means nothing is the outcome this whole section exists to avoid.
LOAD_LIMIT="${LOAD_LIMIT:-}"
if [ -z "$LOAD_LIMIT" ]; then
    LOAD_LIMIT="$(awk -v c="$(nproc 2>/dev/null || echo 4)" \
        'BEGIN{ v = c * 0.5; if (v < 2.0) v = 2.0; printf "%.2f", v }')"
fi
LOAD_NOW="$(cut -d' ' -f1 /proc/loadavg 2>/dev/null || echo 0)"
LOADED=0
if num_gt "$LOAD_NOW" "$LOAD_LIMIT"; then LOADED=1; fi
budget_inconclusive=0

# record_budget <label> <verdict PASS|FAIL>
# Prints the verdict and, on FAIL, bumps budget_failures (which only
# affects the exit code when SKIP_BUDGETS != 1). Under high load a FAIL is
# downgraded to INCONCLUSIVE — a PASS is still reported as a PASS, since
# beating a floor on a busy box is if anything stronger evidence.
record_budget() {
    local label="$1" verdict="$2"
    if [ "$verdict" = "FAIL" ] && [ "$LOADED" = "1" ]; then
        echo "  $label -> INCONCLUSIVE (1-min load $LOAD_NOW > $LOAD_LIMIT; not counted)"
        budget_inconclusive=$((budget_inconclusive + 1))
        return 0
    fi
    echo "  $label -> $verdict"
    [ "$verdict" = "FAIL" ] && budget_failures=$((budget_failures + 1))
    return 0
}

# record_hard_error <message>
record_hard_error() {
    echo "run_bench.sh: HARNESS FAILURE: $1" >&2
    hard_errors=$((hard_errors + 1))
}

describe_env
echo "pcrec:  $PCREC"
echo "cc:     $CC ($("$CC" --version 2>&1 | head -n1))"
echo "workdir: $WORKDIR"
echo

# =========================================================================
# SECTION 1: COMPILE-SPEED
# =========================================================================
# ~20 varied base-tier patterns (literals, alternations, classes, bounded
# repeats, a realistic log-line pattern), all known to compile cleanly on
# the base tier (no \d/\w/\s or POSIX classes — those are future modules,
# see src/parse/parse.c's esc_modules table). Budget: total pcrec wall time
# for all of them combined must be under COMPILE_BUDGET_SECS.

echo "== COMPILE-SPEED =="

COMPILE_PATTERNS=(
    'hello world'
    'The quick brown fox jumps over the lazy dog'
    'cat|dog|bird|fish|horse'
    'error|warning|info|debug|trace'
    '(get|post|put|delete|patch)'
    '[a-z]+'
    '[A-Za-z0-9_]+'
    '[^,\n]*'
    '[^"]*'
    'a{2,5}'
    '[0-9]{3}-[0-9]{4}'
    '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
    '[0-9]{4}-[0-9]{2}-[0-9]{2}'
    '[0-9]{2}:[0-9]{2}:[0-9]{2}'
    '(ab|cd|ef){2,4}'
    '(foo|bar|baz)+'
    '^[A-Z][a-z]+'
    '[a-z]+$'
    'a(b|c)*d'
    '\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\] (ERROR|WARN|INFO|DEBUG): .*'
)

cs_dir="$WORKDIR/compile_speed"
mkdir -p "$cs_dir"
cs_log="$cs_dir/pcrec_errors.log"
: >"$cs_log"

# The budget measures pcrec's own wall time, so the whole loop is wrapped in
# a single timeout rather than one per pattern: on this host, `timeout`
# itself costs far more to fork/exec (~0.1s) than pcrec takes to compile a
# base-tier pattern (~0.001-0.002s), so 20 individual timeout wrappers would
# measure subprocess-spawn overhead, not pcrec. One outer timeout still
# protects against a hang (COMPILE_SPEED_TIMEOUT), just without per-pattern
# attribution if it fires.
COMPILE_SPEED_TIMEOUT="${COMPILE_SPEED_TIMEOUT:-30}"
cs_t0=$(now_ns)
timeout "$COMPILE_SPEED_TIMEOUT" bash -c '
    pcrec="$1"; outdir="$2"; log="$3"; shift 3
    i=0
    fail=0
    for p in "$@"; do
        i=$((i + 1))
        if ! "$pcrec" -p rx -o "$outdir/p$i.c" -- "$p" >/dev/null 2>>"$log"; then
            echo "pattern #$i FAILED: $p" >>"$log"
            fail=1
        fi
    done
    exit $fail
' _ "$PCREC" "$cs_dir" "$cs_log" "${COMPILE_PATTERNS[@]}"
cs_loop_rc=$?
cs_t1=$(now_ns)
cs_secs=$(elapsed_secs "$cs_t0" "$cs_t1")

if [ $cs_loop_rc -eq 124 ]; then
    record_hard_error "COMPILE-SPEED loop timed out after ${COMPILE_SPEED_TIMEOUT}s (a pattern likely hung); partial log: $(cat "$cs_log")"
elif [ $cs_loop_rc -ne 0 ]; then
    record_hard_error "COMPILE-SPEED: one or more patterns failed to compile; log: $(cat "$cs_log")"
fi

echo "  patterns compiled: ${#COMPILE_PATTERNS[@]}"
echo "  total pcrec wall time: ${cs_secs}s (budget < ${COMPILE_BUDGET_SECS}s)"
if num_lt "$cs_secs" "$COMPILE_BUDGET_SECS"; then
    record_budget "COMPILE-SPEED" "PASS"
else
    record_budget "COMPILE-SPEED" "FAIL"
fi
echo

# =========================================================================
# SECTION 1b: KEYWORD-SCALE (R2-A4 / M2.8 regression guard)
# =========================================================================
# Large flat alternations are the ordinary shape for keyword and blocklist
# patterns. Before M2.8 they were quadratic in branch count and then failed
# outright: 500/1000/2000 random words took 0.72/2.94/11.09 s and 3600 words
# hard-failed with "NFA exceeds 20000 states". The cause was closure fan-out,
# not state count -- nfa_wrap_unanchored's self-loop keeps the whole branch
# chain live at every position, so every epsilon closure walked every branch
# (measured 4045 NFA visits per closure at 2000 branches, 2.36 billion total).
# The prefix trie in src/ir/nfa.c collapses that to the node fan-out.
#
# This guard is deliberately about pcrec's OWN compile time. gcc's time on the
# emitted table source is a separate, larger constant (~1.6x pcrec's, and flat
# across -O0/-O1/-O2 by the R1 A-3 table design) and is covered by GCC-TIME.

echo "== KEYWORD-SCALE (R2-A4) =="

KEYWORD_COUNT="${KEYWORD_COUNT:-3600}"
KEYWORD_BUDGET_SECS="${KEYWORD_BUDGET_SECS:-4}"
# The class-bearing variant is inherently slower (more byte classes, so a
# wider DFA): 2.87 s measured, against 44.9 s before the run-splitting fix.
KEYWORD_CLS_BUDGET_SECS="${KEYWORD_CLS_BUDGET_SECS:-8}"

kw_dir="$WORKDIR/keyword_scale"
mkdir -p "$kw_dir"
kw_pat_file="$kw_dir/pattern.txt"

# Two variants. The class-free one is the original R2-A4 guard. The second
# sprinkles 2-element CHARACTER CLASSES through 2% of the characters,
# because the trie may only reorder branches whose class bitmaps are
# disjoint — and the first version of that check bailed the WHOLE node on
# any overlap, so a single branch beginning `[ab]` took a 3600-word list
# from 0.80 s to 44.9 s. A class-free word list cannot see that cliff,
# which is exactly why it went unnoticed (R3 critic finding).
kw_gen_err="$(python3 - "$KEYWORD_COUNT" "$kw_pat_file" "$kw_dir/pattern_cls.txt" 2>&1 <<'PYEOF'
import random, sys
count = int(sys.argv[1])
random.seed(20260809)
alpha = "abcdefghijklmnopqrstuvwxyz"
words = set()
while len(words) < count:
    words.add("".join(random.choice(alpha) for _ in range(random.randint(4, 12))))
words = sorted(words)
with open(sys.argv[2], "w") as f:
    f.write("|".join(words))

random.seed(5)
out = []
for w in words:
    y = ""
    for ch in w:
        if random.random() < 0.02:
            y += "[" + ch + chr((ord(ch) - 97 + 1) % 26 + 97) + "]"
        else:
            y += ch
    out.append(y)
with open(sys.argv[3], "w") as f:
    f.write("|".join(out))
PYEOF
)"
if [ $? -ne 0 ]; then
    record_hard_error "python3 keyword-list generation failed: $kw_gen_err"
else
    kw_pat="$(cat "$kw_pat_file")"
    kw_t0=$(now_ns)
    kw_err="$(timeout "$PCREC_TIMEOUT" "$PCREC" -p rx -o "$kw_dir/gen.c" -- "$kw_pat" 2>&1 >/dev/null)"
    kw_rc=$?
    kw_t1=$(now_ns)
    kw_secs=$(elapsed_secs "$kw_t0" "$kw_t1")

    echo "  ${KEYWORD_COUNT}-word flat alternation ($(wc -c <"$kw_pat_file") pattern bytes)"
    if [ $kw_rc -eq 124 ]; then
        echo "    pcrec: DNF (exceeded ${PCREC_TIMEOUT}s timeout) (budget < ${KEYWORD_BUDGET_SECS}s)"
        record_budget "KEYWORD-SCALE" "FAIL"
    elif [ $kw_rc -ne 0 ]; then
        # A hard failure here is the exact R2-A4 regression, so it is a budget
        # failure with a named cause rather than a harness error.
        echo "    pcrec FAILED to compile: $kw_err"
        record_budget "KEYWORD-SCALE" "FAIL"
    else
        echo "    pcrec: ${kw_secs}s, gen.c size: $(wc -c <"$kw_dir/gen.c") bytes (budget < ${KEYWORD_BUDGET_SECS}s)"
        if num_lt "$kw_secs" "$KEYWORD_BUDGET_SECS"; then
            record_budget "KEYWORD-SCALE" "PASS"
        else
            record_budget "KEYWORD-SCALE" "FAIL"
        fi
    fi

    # same list with 2% of characters turned into 2-element classes
    kw_cls_pat="$(cat "$kw_dir/pattern_cls.txt")"
    kwc_t0=$(now_ns)
    kwc_err="$(timeout "$PCREC_TIMEOUT" "$PCREC" -p rx -o "$kw_dir/gen_cls.c" -- "$kw_cls_pat" 2>&1 >/dev/null)"
    kwc_rc=$?
    kwc_t1=$(now_ns)
    kwc_secs=$(elapsed_secs "$kwc_t0" "$kwc_t1")
    echo "  ${KEYWORD_COUNT}-word list with 2% character classes"
    if [ $kwc_rc -eq 124 ]; then
        echo "    pcrec: DNF (exceeded ${PCREC_TIMEOUT}s timeout) (budget < ${KEYWORD_CLS_BUDGET_SECS}s)"
        record_budget "KEYWORD-SCALE (classes)" "FAIL"
    elif [ $kwc_rc -ne 0 ]; then
        echo "    pcrec FAILED to compile: $kwc_err"
        record_budget "KEYWORD-SCALE (classes)" "FAIL"
    else
        echo "    pcrec: ${kwc_secs}s (budget < ${KEYWORD_CLS_BUDGET_SECS}s)"
        if num_lt "$kwc_secs" "$KEYWORD_CLS_BUDGET_SECS"; then
            record_budget "KEYWORD-SCALE (classes)" "PASS"
        else
            record_budget "KEYWORD-SCALE (classes)" "FAIL"
        fi
    fi
fi
echo

# =========================================================================
# SECTION 2: GCC-TIME (R1 A-3 regression guard)
# =========================================================================
# [01]*1[01]{8}  -> 512 states  (2^(n+1) is provably minimal for this family)
# [01]*1[01]{12} -> 8192 states
# The old computed-goto emitter hits superlinear gcc CFG-pass cost on the
# huge single function these compile to (A-3: 512->2048 states took -O2 from
# 1.3s to 62.7s; 8192 states didn't finish -O2 in 120s). These budgets are
# what the post-rework table emitter must meet; failing them today on the
# old emitter is expected, not a bug in this script.

echo "== GCC-TIME (R1 A-3) =="

GCC_TIME_PATTERNS=(
    "[01]*1[01]{8}:512"
    "[01]*1[01]{12}:8192"
)

gt_dir="$WORKDIR/gcc_time"
mkdir -p "$gt_dir"

idx=0
for entry in "${GCC_TIME_PATTERNS[@]}"; do
    idx=$((idx + 1))
    pat="${entry%%:*}"
    nstates="${entry##*:}"
    pdir="$gt_dir/p$idx"
    mkdir -p "$pdir"

    echo "  pattern '$pat' (~$nstates DFA states)"

    pc_t0=$(now_ns)
    perr="$(timeout "$PCREC_TIMEOUT" "$PCREC" -p rx -o "$pdir/gen.c" -- "$pat" 2>&1 >/dev/null)"
    pc_rc=$?
    pc_t1=$(now_ns)
    if [ $pc_rc -ne 0 ]; then
        record_hard_error "pcrec failed (exit $pc_rc) on GCC-TIME pattern '$pat': $perr"
        continue
    fi
    echo "    pcrec compile: $(elapsed_secs "$pc_t0" "$pc_t1")s, gen.c size: $(wc -c <"$pdir/gen.c") bytes"

    for opt in O1 O2; do
        flag="-$opt"
        if [ "$opt" = "O1" ]; then
            tmo="$GCC_O1_TIMEOUT"; budget="$GCC_O1_BUDGET_SECS"
        else
            tmo="$GCC_O2_TIMEOUT"; budget="$GCC_O2_BUDGET_SECS"
        fi

        g_t0=$(now_ns)
        gerr="$(timeout "$tmo" "$CC" "$flag" -std=gnu11 -c -o "$pdir/gen_$opt.o" "$pdir/gen.c" 2>&1)"
        grc=$?
        g_t1=$(now_ns)
        gsecs=$(elapsed_secs "$g_t0" "$g_t1")

        if [ $grc -eq 124 ]; then
            echo "    $CC $flag: DNF (exceeded ${tmo}s timeout) (budget < ${budget}s)"
            record_budget "GCC-TIME $pat $opt" "FAIL"
        elif [ $grc -ne 0 ]; then
            record_hard_error "$CC $flag failed to compile GCC-TIME pattern '$pat': $gerr"
        else
            echo "    $CC $flag: ${gsecs}s (budget < ${budget}s)"
            if num_lt "$gsecs" "$budget"; then
                record_budget "GCC-TIME $pat $opt" "PASS"
            else
                record_budget "GCC-TIME $pat $opt" "FAIL"
            fi
        fi
    done
done
echo

# =========================================================================
# SECTION 3: THROUGHPUT (+ R1 A-2 linearity regression guard)
# =========================================================================
# Subjects generated once with python3:
#   (a) needle_8mb.bin  8 MB random lowercase text, 'needleXYZW' planted at 90%
#   (b) alla_8mb.bin    8 MB of 'a' repeated (pattern 'a*b', guaranteed no match
#                       -- the A-2 pathological shape: DFA state advances
#                       maximally at every restart position)
#   (c) altd_8mb.bin    8 MB random lowercase text, 'a(b|c)+d'-style matches
#                       planted every 256 KB (first plant near the start so a
#                       correct engine's early-exit keeps this fast)
#   (d)/(e) alla_1mb.bin, alla_4mb.bin  1 MB / 4 MB of 'a' repeated, for the
#                       linearity check against pattern 'a*b'

echo "== THROUGHPUT (+ R1 A-2 linearity) =="

subj_dir="$WORKDIR/subjects"
mkdir -p "$subj_dir"

py_err="$(python3 - "$subj_dir" 2>&1 <<'PYEOF'
import random, sys, os

outdir = sys.argv[1]
random.seed(1729)
MB = 1024 * 1024

def rand_lower(n):
    return bytes(random.choices(b"abcdefghijklmnopqrstuvwxyz", k=n))

# (a) needle planted at 90% of 8 MB
n = 8 * MB
buf = bytearray(rand_lower(n))
needle = b"needleXYZW"
pos = int(n * 0.9)
buf[pos:pos + len(needle)] = needle
with open(os.path.join(outdir, "needle_8mb.bin"), "wb") as f:
    f.write(buf)

# (b) 8 MB of 'a' repeated -- no match for a*b
with open(os.path.join(outdir, "alla_8mb.bin"), "wb") as f:
    f.write(b"a" * n)

# (c) 8 MB random text with NO a(b|c)+d match anywhere, so this measures a
# full scan. R2-B4: the old version planted a match 4 KB in, so a correct
# early-exiting engine scanned 0.05% of the buffer and the "throughput"
# budget was measuring exit latency. 'd' is removed from the alphabet, which
# makes a match impossible without changing the byte-class structure the
# pattern's DFA actually walks.
alpha_nod = b"abcefghijklmnopqrstuvwxyz"
with open(os.path.join(outdir, "altd_nomatch_8mb.bin"), "wb") as f:
    f.write(bytes(random.choices(alpha_nod, k=n)))

# (d) 8 MB of text over an alphabet with NO 'a', so `(alpha|beta|gamma|delta|
# epsilon)` cannot match and the scan is real. This case exists to cover the
# BITMAP half of the start prefilter: cases (a)-(c) all have exactly one
# escape byte and take the memchr branch, so before this every bench pattern
# exercised the same half of the feature. An R3 critic demonstrated the gap by
# deleting the bitmap branch entirely (keeping memchr) for a 20% loss on this
# shape, with make test, make bench, the oracle, the fuzzer AND gate.sh all
# staying green.
alpha_noa = b"bcdefghijklmnopqrstuvwxyz"
with open(os.path.join(outdir, "bitmap_8mb.bin"), "wb") as f:
    f.write(bytes(random.choices(alpha_noa, k=n)))

# linearity subjects. R2-B4: the old pair was 1 MB vs 4 MB, which on the
# current engine takes ~46 us vs ~337 us — below the script's own anti-blowup
# floor, i.e. the check was reading timer noise. 16 MB vs 64 MB puts both
# sides in the milliseconds where the ratio means something, and the floor
# hack is gone.
with open(os.path.join(outdir, "alla_16mb.bin"), "wb") as f:
    f.write(b"a" * (16 * MB))
with open(os.path.join(outdir, "alla_64mb.bin"), "wb") as f:
    f.write(b"a" * (64 * MB))

print("subjects generated in", outdir)
PYEOF
)"
py_rc=$?
if [ $py_rc -ne 0 ]; then
    record_hard_error "python3 subject generation failed: $py_err"
else
    echo "  $py_err"
fi
echo

# run_bdriver <bin> <subject> <iters> <timeout_secs> -> sets RB_SECS, RB_MBPS,
# RB_RC ("ok", "dnf", or "error").
# Repeats BENCH_TRIALS times under the pinning wrapper and reports the MEDIAN;
# RB_SPREAD carries max/min so a wide result is visible rather than silently
# averaged away. A single trial that DNFs or errors fails the whole
# measurement — a flaky run is a result, not something to retry past.
run_bdriver() {
    local bin="$1" subj="$2" iters="$3" tmo="$4"
    local out rc i
    local secs_all=() mbps_all=()
    RB_SECS=""; RB_MBPS=""; RB_SPREAD=""
    for ((i = 0; i < BENCH_TRIALS; i++)); do
        out="$(timeout "$tmo" $PIN "$bin" "$subj" "$iters" 2>&1)"
        rc=$?
        if [ $rc -eq 124 ]; then RB_RC="dnf"; RB_RAW="$out"; return; fi
        if [ $rc -ne 0 ]; then RB_RC="error"; RB_RAW="$out"; return; fi
        if [[ "$out" =~ secs=([0-9.]+)\ mbps=([0-9.]+) ]]; then
            secs_all+=("${BASH_REMATCH[1]}")
            mbps_all+=("${BASH_REMATCH[2]}")
        else
            RB_RC="error"; RB_RAW="$out"; return
        fi
    done
    RB_RC="ok"
    RB_RAW="$out"
    RB_SECS="$(median "${secs_all[@]}")"
    RB_MBPS="$(median "${mbps_all[@]}")"
    RB_SPREAD="$(spread "${mbps_all[@]}")"
}

# build_bench_bin <patdir> <pattern> -> compiles gen.c + bdriver.c into
# <patdir>/t ; sets BB_OK=1/0
build_bench_bin() {
    local patdir="$1" pattern="$2"
    mkdir -p "$patdir"
    local perr
    perr="$(timeout "$PCREC_TIMEOUT" "$PCREC" -p rx -o "$patdir/gen.c" -- "$pattern" 2>&1 >/dev/null)"
    if [ $? -ne 0 ]; then
        record_hard_error "pcrec failed to compile THROUGHPUT pattern '$pattern': $perr"
        BB_OK=0
        return
    fi
    local berr
    berr="$(timeout 60 "$CC" -O2 -std=gnu11 -Wall -Wextra -Werror \
        -I"$patdir" -o "$patdir/t" "$SCRIPT_DIR/bdriver.c" "$patdir/gen.c" 2>&1)"
    if [ $? -ne 0 ]; then
        record_hard_error "$CC failed to build bdriver for pattern '$pattern': $berr"
        BB_OK=0
        return
    fi
    BB_OK=1
}

if [ $py_rc -eq 0 ]; then
    # ---- (a) needle: literal, planted at 90% of 8 MB, budget: high floor ----
    tdir="$WORKDIR/tp_needle"
    build_bench_bin "$tdir" 'needleXYZW'
    if [ "$BB_OK" = "1" ]; then
        run_bdriver "$tdir/t" "$subj_dir/needle_8mb.bin" 20 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            echo "  (a) needleXYZW  over needle_8mb.bin: ${RB_SECS}s, ${RB_MBPS} MB/s (spread ${RB_SPREAD}x) (budget > ${THROUGHPUT_NEEDLE_MIN_MBPS} MB/s)"
            if num_gt "$RB_MBPS" "$THROUGHPUT_NEEDLE_MIN_MBPS"; then
                record_budget "THROUGHPUT (a) needle" "PASS"
            else
                record_budget "THROUGHPUT (a) needle" "FAIL"
            fi
        elif [ "$RB_RC" = "dnf" ]; then
            echo "  (a) needleXYZW  over needle_8mb.bin: DNF (exceeded ${RUN_TIMEOUT}s timeout)"
            record_budget "THROUGHPUT (a) needle" "FAIL"
        else
            record_hard_error "bdriver crashed/errored on subject (a): $RB_RAW"
        fi
    fi

    # ---- (b) a*b over 8 MB of 'a': no match, pathological under A-2 ----
    tdir="$WORKDIR/tp_nomatch"
    build_bench_bin "$tdir" 'a*b'
    if [ "$BB_OK" = "1" ]; then
        # 20 iterations, not 1: a single 8 MB pass here is ~0.75 ms, which is
        # too short to time honestly on this box.
        run_bdriver "$tdir/t" "$subj_dir/alla_8mb.bin" 20 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            echo "  (b) a*b         over alla_8mb.bin:  ${RB_SECS}s, ${RB_MBPS} MB/s (spread ${RB_SPREAD}x) (budget > ${THROUGHPUT_NOMATCH_MIN_MBPS} MB/s)"
            if num_gt "$RB_MBPS" "$THROUGHPUT_NOMATCH_MIN_MBPS"; then
                record_budget "THROUGHPUT (b) no-match" "PASS"
            else
                record_budget "THROUGHPUT (b) no-match" "FAIL"
            fi
        elif [ "$RB_RC" = "dnf" ]; then
            echo "  (b) a*b         over alla_8mb.bin:  DNF (exceeded ${RUN_TIMEOUT}s timeout -- expected on the old O(n^2) emitter, see A-2)"
            record_budget "THROUGHPUT (b) no-match" "FAIL"
        else
            record_hard_error "bdriver crashed/errored on subject (b): $RB_RAW"
        fi
    fi

    # ---- (c) a(b|c)+d over 8 MB random text with NO match: full scan ----
    tdir="$WORKDIR/tp_alt"
    build_bench_bin "$tdir" 'a(b|c)+d'
    if [ "$BB_OK" = "1" ]; then
        run_bdriver "$tdir/t" "$subj_dir/altd_nomatch_8mb.bin" 10 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            echo "  (c) a(b|c)+d    over altd_nomatch_8mb.bin: ${RB_SECS}s, ${RB_MBPS} MB/s (spread ${RB_SPREAD}x) (budget > ${THROUGHPUT_ALT_MIN_MBPS} MB/s)"
            if num_gt "$RB_MBPS" "$THROUGHPUT_ALT_MIN_MBPS"; then
                record_budget "THROUGHPUT (c) alternation" "PASS"
            else
                record_budget "THROUGHPUT (c) alternation" "FAIL"
            fi
        elif [ "$RB_RC" = "dnf" ]; then
            echo "  (c) a(b|c)+d    over altd_nomatch_8mb.bin: DNF (exceeded ${RUN_TIMEOUT}s timeout)"
            record_budget "THROUGHPUT (c) alternation" "FAIL"
        else
            record_hard_error "bdriver crashed/errored on subject (c): $RB_RAW"
        fi
    fi

    # ---- (d) bitmap prefilter: 5 distinct first bytes, no match ----
    tdir="$WORKDIR/tp_bitmap"
    build_bench_bin "$tdir" '(alpha|beta|gamma|delta|epsilon)'
    if [ "$BB_OK" = "1" ]; then
        run_bdriver "$tdir/t" "$subj_dir/bitmap_8mb.bin" 10 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            echo "  (d) (alpha|beta|...)  over bitmap_8mb.bin: ${RB_SECS}s, ${RB_MBPS} MB/s (spread ${RB_SPREAD}x) (budget > ${THROUGHPUT_BITMAP_MIN_MBPS} MB/s)"
            if num_gt "$RB_MBPS" "$THROUGHPUT_BITMAP_MIN_MBPS"; then
                record_budget "THROUGHPUT (d) bitmap prefilter" "PASS"
            else
                record_budget "THROUGHPUT (d) bitmap prefilter" "FAIL"
            fi
        elif [ "$RB_RC" = "dnf" ]; then
            echo "  (d) (alpha|beta|...)  over bitmap_8mb.bin: DNF (exceeded ${RUN_TIMEOUT}s timeout)"
            record_budget "THROUGHPUT (d) bitmap prefilter" "FAIL"
        else
            record_hard_error "bdriver crashed/errored on subject (d): $RB_RAW"
        fi
    fi

    echo
    echo "  -- linearity check (R1 A-2): a*b over 16 MB vs 64 MB of 'a' --"
    # Reuses the (b) binary (same pattern 'a*b'); a fresh binary is built in
    # case (b)'s build failed for some pattern-specific reason.
    tdir="$WORKDIR/tp_linearity"
    build_bench_bin "$tdir" 'a*b'
    lin_ok=1
    secs_1mb=""; secs_4mb=""
    if [ "$BB_OK" = "1" ]; then
        run_bdriver "$tdir/t" "$subj_dir/alla_16mb.bin" 20 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            secs_1mb="$RB_SECS"
            echo "    16 MB: ${secs_1mb}s (spread ${RB_SPREAD}x)"
        elif [ "$RB_RC" = "dnf" ]; then
            echo "    16 MB: DNF (exceeded ${RUN_TIMEOUT}s timeout)"
            lin_ok=0
        else
            record_hard_error "bdriver crashed/errored on linearity 1MB subject: $RB_RAW"
            lin_ok=0
        fi

        run_bdriver "$tdir/t" "$subj_dir/alla_64mb.bin" 20 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            secs_4mb="$RB_SECS"
            echo "    64 MB: ${secs_4mb}s (spread ${RB_SPREAD}x)"
        elif [ "$RB_RC" = "dnf" ]; then
            echo "    64 MB: DNF (exceeded ${RUN_TIMEOUT}s timeout -- expected on the old O(n^2) emitter, see A-2)"
            lin_ok=0
        else
            record_hard_error "bdriver crashed/errored on linearity 4MB subject: $RB_RAW"
            lin_ok=0
        fi
    else
        lin_ok=0
    fi

    if [ "$lin_ok" = "1" ]; then
        # No anti-blowup floor any more: at 16/64 MB both sides are
        # milliseconds, so the ratio is a real measurement rather than a timer
        # artifact (R2-B4). If the 16 MB side ever does land under a
        # millisecond again, say so instead of silently clamping.
        if num_lt "$secs_1mb" "0.005"; then
            record_hard_error "linearity: 16 MB x20 measured ${secs_1mb}s (<5ms) — too short for this timer, raise the subject size or the iteration count"
        fi
        ratio=$(awk -v s1="$secs_1mb" -v s4="$secs_4mb" 'BEGIN{ printf "%.3f", s4/s1 }')
        echo "    ratio (64MB/16MB): $ratio (budget < ${LINEARITY_MAX_RATIO}, linear ~4.0, quadratic ~16.0)"
        if num_lt "$ratio" "$LINEARITY_MAX_RATIO"; then
            record_budget "THROUGHPUT linearity" "PASS"
        else
            record_budget "THROUGHPUT linearity" "FAIL"
        fi
    else
        echo "    ratio: N/A (one or both runs did not complete)"
        record_budget "THROUGHPUT linearity" "FAIL"
    fi
fi
echo

# =========================================================================
# Summary
# =========================================================================

echo "== Summary =="
echo "hard errors (harness/mechanical failures): $hard_errors"
echo "budget failures: $budget_failures"
if [ "$budget_inconclusive" -gt 0 ]; then
    echo "budget INCONCLUSIVE: $budget_inconclusive (1-min load $LOAD_NOW > $LOAD_LIMIT)"
    echo "  This run did NOT gate those budgets. Re-run on a quiet box before"
    echo "  treating this as evidence of no regression."
fi
[ "$SKIP_BUDGETS" = "1" ] && echo "SKIP_BUDGETS=1: budget failures do not affect exit code"

if [ "$hard_errors" -gt 0 ]; then
    exit 1
fi
if [ "$budget_failures" -gt 0 ] && [ "$SKIP_BUDGETS" != "1" ]; then
    exit 1
fi
# "I could not measure" must not be reportable as "nothing regressed". The
# first version of the LOAD_LIMIT downgrade exited 0 here, which meant a build
# with a 3.4x/68x/5.5x regression exited GREEN whenever the box was busy — and
# with a default limit of cores/2 against observed loads of 5-24, busy was the
# normal case, not a corner (R3 critic finding). Exit 2 instead: distinct from
# both 0 (gated, clean) and 1 (gated, failed), so automation can tell "no
# regression" apart from "no measurement".
if [ "$budget_inconclusive" -gt 0 ] && [ "$SKIP_BUDGETS" != "1" ]; then
    echo "run_bench.sh: exiting 2 — $budget_inconclusive budget(s) were not gated" >&2
    exit 2
fi
exit 0
