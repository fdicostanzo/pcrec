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
#   Budgets (all overridable):
#     COMPILE_BUDGET_SECS          (default 2)     total pcrec time, COMPILE-SPEED
#     GCC_O1_BUDGET_SECS           (default 5)     per-pattern, GCC-TIME
#     GCC_O2_BUDGET_SECS           (default 10)    per-pattern, GCC-TIME
#     THROUGHPUT_NEEDLE_MIN_MBPS   (default 200)   subject (a), THROUGHPUT
#     THROUGHPUT_NOMATCH_MIN_MBPS  (default 50)    subject (b), THROUGHPUT
#     THROUGHPUT_ALT_MIN_MBPS      (default 50)    subject (c), THROUGHPUT
#     LINEARITY_MAX_RATIO          (default 8.0)   4MB/1MB time ratio, THROUGHPUT
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

COMPILE_BUDGET_SECS="${COMPILE_BUDGET_SECS:-2}"
GCC_O1_BUDGET_SECS="${GCC_O1_BUDGET_SECS:-5}"
GCC_O2_BUDGET_SECS="${GCC_O2_BUDGET_SECS:-10}"
THROUGHPUT_NEEDLE_MIN_MBPS="${THROUGHPUT_NEEDLE_MIN_MBPS:-200}"
THROUGHPUT_NOMATCH_MIN_MBPS="${THROUGHPUT_NOMATCH_MIN_MBPS:-50}"
THROUGHPUT_ALT_MIN_MBPS="${THROUGHPUT_ALT_MIN_MBPS:-50}"
LINEARITY_MAX_RATIO="${LINEARITY_MAX_RATIO:-8.0}"

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

# record_budget <label> <verdict PASS|FAIL>
# Prints the verdict and, on FAIL, bumps budget_failures (which only
# affects the exit code when SKIP_BUDGETS != 1).
record_budget() {
    local label="$1" verdict="$2"
    echo "  $label -> $verdict"
    [ "$verdict" = "FAIL" ] && budget_failures=$((budget_failures + 1))
    return 0
}

# record_hard_error <message>
record_hard_error() {
    echo "run_bench.sh: HARNESS FAILURE: $1" >&2
    hard_errors=$((hard_errors + 1))
}

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

kw_dir="$WORKDIR/keyword_scale"
mkdir -p "$kw_dir"
kw_pat_file="$kw_dir/pattern.txt"

kw_gen_err="$(python3 - "$KEYWORD_COUNT" "$kw_pat_file" 2>&1 <<'PYEOF'
import random, sys
count = int(sys.argv[1])
random.seed(20260809)
alpha = "abcdefghijklmnopqrstuvwxyz"
words = set()
while len(words) < count:
    words.add("".join(random.choice(alpha) for _ in range(random.randint(4, 12))))
with open(sys.argv[2], "w") as f:
    f.write("|".join(sorted(words)))
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

# (c) 8 MB random text, a(b|c)+d matches planted every 256 KB, first one
# close to the start so a correct (linear, early-exit) engine stays fast
# here too.
buf = bytearray(rand_lower(n))
step = 256 * 1024
p = 4096
while p < n - 16:
    run = bytes(random.choice(b"bc") for _ in range(random.randint(1, 6)))
    match = b"a" + run + b"d"
    buf[p:p + len(match)] = match
    p += step
with open(os.path.join(outdir, "altd_8mb.bin"), "wb") as f:
    f.write(buf)

# linearity subjects
with open(os.path.join(outdir, "alla_1mb.bin"), "wb") as f:
    f.write(b"a" * (1 * MB))
with open(os.path.join(outdir, "alla_4mb.bin"), "wb") as f:
    f.write(b"a" * (4 * MB))

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
# RB_RC ("ok", "dnf", or "error")
run_bdriver() {
    local bin="$1" subj="$2" iters="$3" tmo="$4"
    local out rc
    out="$(timeout "$tmo" "$bin" "$subj" "$iters" 2>&1)"
    rc=$?
    RB_SECS=""; RB_MBPS=""
    if [ $rc -eq 124 ]; then
        RB_RC="dnf"
        RB_RAW="$out"
    elif [ $rc -ne 0 ]; then
        RB_RC="error"
        RB_RAW="$out"
    else
        RB_RC="ok"
        RB_RAW="$out"
        if [[ "$out" =~ secs=([0-9.]+)\ mbps=([0-9.]+) ]]; then
            RB_SECS="${BASH_REMATCH[1]}"
            RB_MBPS="${BASH_REMATCH[2]}"
        else
            RB_RC="error"
        fi
    fi
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
            echo "  (a) needleXYZW  over needle_8mb.bin: ${RB_SECS}s, ${RB_MBPS} MB/s (budget > ${THROUGHPUT_NEEDLE_MIN_MBPS} MB/s)"
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
        run_bdriver "$tdir/t" "$subj_dir/alla_8mb.bin" 1 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            echo "  (b) a*b         over alla_8mb.bin:  ${RB_SECS}s, ${RB_MBPS} MB/s (budget > ${THROUGHPUT_NOMATCH_MIN_MBPS} MB/s)"
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

    # ---- (c) a(b|c)+d over 8 MB random text, matches planted ----
    tdir="$WORKDIR/tp_alt"
    build_bench_bin "$tdir" 'a(b|c)+d'
    if [ "$BB_OK" = "1" ]; then
        run_bdriver "$tdir/t" "$subj_dir/altd_8mb.bin" 10 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            echo "  (c) a(b|c)+d    over altd_8mb.bin:  ${RB_SECS}s, ${RB_MBPS} MB/s (budget > ${THROUGHPUT_ALT_MIN_MBPS} MB/s)"
            if num_gt "$RB_MBPS" "$THROUGHPUT_ALT_MIN_MBPS"; then
                record_budget "THROUGHPUT (c) alternation" "PASS"
            else
                record_budget "THROUGHPUT (c) alternation" "FAIL"
            fi
        elif [ "$RB_RC" = "dnf" ]; then
            echo "  (c) a(b|c)+d    over altd_8mb.bin:  DNF (exceeded ${RUN_TIMEOUT}s timeout)"
            record_budget "THROUGHPUT (c) alternation" "FAIL"
        else
            record_hard_error "bdriver crashed/errored on subject (c): $RB_RAW"
        fi
    fi

    echo
    echo "  -- linearity check (R1 A-2): a*b over 1 MB vs 4 MB of 'a' --"
    # Reuses the (b) binary (same pattern 'a*b'); a fresh binary is built in
    # case (b)'s build failed for some pattern-specific reason.
    tdir="$WORKDIR/tp_linearity"
    build_bench_bin "$tdir" 'a*b'
    lin_ok=1
    secs_1mb=""; secs_4mb=""
    if [ "$BB_OK" = "1" ]; then
        run_bdriver "$tdir/t" "$subj_dir/alla_1mb.bin" 1 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            secs_1mb="$RB_SECS"
            echo "    1 MB: ${secs_1mb}s"
        elif [ "$RB_RC" = "dnf" ]; then
            echo "    1 MB: DNF (exceeded ${RUN_TIMEOUT}s timeout)"
            lin_ok=0
        else
            record_hard_error "bdriver crashed/errored on linearity 1MB subject: $RB_RAW"
            lin_ok=0
        fi

        run_bdriver "$tdir/t" "$subj_dir/alla_4mb.bin" 1 "$RUN_TIMEOUT"
        if [ "$RB_RC" = "ok" ]; then
            secs_4mb="$RB_SECS"
            echo "    4 MB: ${secs_4mb}s"
        elif [ "$RB_RC" = "dnf" ]; then
            echo "    4 MB: DNF (exceeded ${RUN_TIMEOUT}s timeout -- expected on the old O(n^2) emitter, see A-2)"
            lin_ok=0
        else
            record_hard_error "bdriver crashed/errored on linearity 4MB subject: $RB_RAW"
            lin_ok=0
        fi
    else
        lin_ok=0
    fi

    if [ "$lin_ok" = "1" ]; then
        # Guard against a near-zero 1MB timing (division blowup) on a very
        # fast engine; a sub-millisecond 1MB scan is linear by construction.
        ratio=$(awk -v s1="$secs_1mb" -v s4="$secs_4mb" \
            'BEGIN{ if (s1 < 0.0005) s1 = 0.0005; printf "%.3f", s4/s1 }')
        echo "    ratio (4MB/1MB): $ratio (budget < ${LINEARITY_MAX_RATIO}, linear ~4.0, quadratic ~16.0)"
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
[ "$SKIP_BUDGETS" = "1" ] && echo "SKIP_BUDGETS=1: budget failures do not affect exit code"

if [ "$hard_errors" -gt 0 ]; then
    exit 1
fi
if [ "$budget_failures" -gt 0 ] && [ "$SKIP_BUDGETS" != "1" ]; then
    exit 1
fi
exit 0
