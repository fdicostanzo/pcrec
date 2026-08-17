#!/usr/bin/env bash
# tests/bench/compare/compare.sh — cross-engine regex performance comparison.
#
# Usage: bash tests/bench/compare/compare.sh
#
# pcrec's stated intention is to be FASTER than general-purpose regex
# engines by compiling each pattern to specialized native code ahead of
# time. tests/bench/run_bench.sh guards pcrec against regressing against
# ITSELF (throughput floors, linearity). This script instead measures
# pcrec against OTHER engines on IDENTICAL inputs, so the project can
# track whether the stated intention actually holds, across a matrix of
# case shapes chosen to stress different things (plain literal scan,
# alternation, character classes, a classic quadratic-shaped nomatch,
# bounded repeats, greedy backtracking, and short-subject per-call
# overhead).
#
# Engines measured (see README.md for full fairness notes):
#   pcrec        -- pcrec-generated matcher, compiled gcc -O2 (AOT-specialized
#                    native code; pays compile cost at BUILD time, excluded
#                    here by design)
#   pcre2-interp -- PCRE2 8-bit compiled pattern, pcre2_match_8 (general
#                    backtracking interpreter)
#   pcre2-jit    -- PCRE2 8-bit compiled pattern, pcre2_jit_compile_8 +
#                    pcre2_jit_match_8 (runtime-JIT native code). Omitted
#                    entirely if this PCRE2 build has no JIT support, and
#                    omitted per-case if a specific pattern isn't
#                    JIT-compilable even when the library supports JIT.
#   python-re    -- python3 `re` module, bytes pattern, compiled once,
#                    search loop timed with time.perf_counter. Interpreter
#                    dispatch overhead is inherent to this engine's
#                    real-world usage -- NOT stripped out, see README.md.
#
# All four engines search the IDENTICAL subject bytes, whole-buffer
# leftmost search per iteration, startpos always 0. Before timing, every
# engine runs once and all engines must agree on match/nomatch + span
# (reference: pcre2-interp, this project's established oracle -- see
# tests/fuzz/pcre2_oracle.c); a disagreeing case is marked INVALID and is
# NOT timed (never silently dropped -- see the Results section and
# docs/dev/upstream_issues.md for known other-engine divergences to check
# against first). Iteration counts are auto-scaled per engine so every
# timed measurement accumulates at least TARGET_SECS (default 0.3s) of
# wall time.
#
# Measurement rigor (R2-B1/B2/B3, checkpoint review docs/dev/reviews/2026-08-09-m2.md):
# the same box runs `schedutil` with turbo on, and per-measurement wall
# times sat inside a frequency-ramp window; every measurement used to be a
# SINGLE sample (published ratios swung 0.82-1.11 across 7 repeat runs,
# flipping sign in 4 of 7); and pcrec was always measured FIRST in every
# case, a systematic confound. So, styled after tests/bench/run_bench.sh's
# equivalent fix (M2.9):
#   - every timed engine invocation is wrapped in a probed taskset (+chrt if
#     it actually works, degrading quietly otherwise) pin, BENCH_CPU/PIN below;
#   - every engine/case measurement repeats BENCH_TRIALS times and reports
#     the MEDIAN, with max/min spread carried into its own results column
#     (a DNF or error on any one trial fails the whole measurement -- never
#     silently retried past or averaged away);
#   - engine order is rotated per trial (trial i starts the engine list at
#     index i mod N and wraps around) instead of always running pcrec first.
#
# Env vars:
#   PCREC          path to the pcrec binary          (default: <repo-root>/build/pcrec)
#   CC             C compiler                          (default: gcc)
#   KEEP=1         keep the temp working directory instead of deleting it
#   TARGET_SECS    per-measurement minimum wall time    (default: 0.3)
#   RUN_TIMEOUT    per engine-invocation hang timeout   (default: 90)
#   PCREC_TIMEOUT  per pcrec-invocation hang timeout    (default: 60)
#   BUILD_TIMEOUT  per $CC-invocation hang timeout      (default: 60)
#   BENCH_CPU      core to pin every timed run to (taskset) (default: 2)
#   BENCH_TRIALS   repeats per engine/case measurement;
#                  the MEDIAN is reported, max/min spread alongside (default: 5)
#   CASES          comma-separated case-id subset, e.g. CASES=e,d for a fast
#                  mechanics smoke-test instead of the full matrix
#
# Output: a streamed per-case log, a consolidated human-readable results
# table, a machine-readable TSV block (between "BEGIN TSV"/"END TSV"
# markers), and a full copy of both written to
# tests/bench/compare/results-<hostname>-<yyyymmdd>.md.
#
# See tests/bench/run_bench.sh for the sibling suite this one is styled
# after (same hang-protection-via-timeout, same mktemp workdir + KEEP=1
# convention, same awk-based numeric-comparison helpers, and now the same
# PIN/BENCH_TRIALS/median()/spread() measurement-rigor machinery, M2.9).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
TARGET_SECS="${TARGET_SECS:-0.3}"
RUN_TIMEOUT="${RUN_TIMEOUT:-90}"
PCREC_TIMEOUT="${PCREC_TIMEOUT:-60}"
BUILD_TIMEOUT="${BUILD_TIMEOUT:-60}"

# ---- measurement rigor (R2-B1/B2/B3) -----------------------------------
# Pin every timed run to one core, repeat each measurement, judge on the
# median. Lifted verbatim in approach from tests/bench/run_bench.sh's M2.9
# fix -- same probe, same degrade-quietly-if-unprivileged behavior (chrt
# has no permission on this box; taskset alone still works).

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

if [ ! -x "$PCREC" ]; then
    echo "compare.sh: pcrec binary not found or not executable: $PCREC (build it first, e.g. 'make')" >&2
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    echo "compare.sh: python3 is required (subject generation + python-re engine)" >&2
    exit 1
fi
if ! command -v "$CC" >/dev/null 2>&1; then
    echo "compare.sh: C compiler not found: $CC" >&2
    exit 1
fi
if ! command -v timeout >/dev/null 2>&1; then
    echo "compare.sh: 'timeout' (coreutils) is required for hang protection" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then
        echo "compare.sh: KEEP=1, temp dir preserved: $WORKDIR" >&2
    else
        rm -rf "$WORKDIR"
    fi
}
trap cleanup EXIT

hard_errors=0

record_hard_error() {
    echo "compare.sh: HARNESS FAILURE: $1" >&2
    hard_errors=$((hard_errors + 1))
}

# ---- small helpers (style-matched to run_bench.sh) ---------------------

now_ns() { date +%s%N; }
elapsed_secs() { awk -v a="$1" -v b="$2" 'BEGIN{printf "%.3f", (b-a)/1000000000.0}'; }
num_lt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a+0 < b+0)}'; }
num_gt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a+0 > b+0)}'; }

# median <values...> -> prints the median (lower of the two for even counts)
median() {
    printf '%s\n' "$@" | sort -g | awk '{v[NR]=$0} END{ if (NR==0) print ""; else print v[int((NR+1)/2)] }'
}
# spread <values...> -> prints max/min as a ratio, "n/a" if min is 0
spread() {
    printf '%s\n' "$@" | sort -g | awk '{v[NR]=$0} END{ if (NR<2 || v[1]+0==0) print "n/a"; else printf "%.2f", v[NR]/v[1] }'
}

# join_semi <arr...> -> prints args joined with "; ". (Not `IFS='; '`
# + "${arr[*]}": bash's `[*]` expansion only uses the FIRST character of
# IFS as the join separator, which would silently join with ";" and no
# space -- this loops explicitly instead.)
join_semi() {
    local out="" a
    for a in "$@"; do
        if [ -z "$out" ]; then out="$a"; else out="$out; $a"; fi
    done
    printf '%s' "$out"
}

# extract_field <text> <key> -> prints the value of the first "key=value"
# token in <text> (value = run of non-whitespace), or empty if absent.
extract_field() {
    local text="$1" key="$2"
    if [[ "$text" =~ (^|[[:space:]])$key=([^[:space:]]+) ]]; then
        printf '%s' "${BASH_REMATCH[2]}"
    fi
}

# run_driver <timeout_secs> <argv...>
# Sets DRV_RC (ok|dnf|error), DRV_RAW (raw stdout+stderr), and on RC=ok
# also DRV_STATUS/DRV_BYTES/DRV_ITERS/DRV_SECS/DRV_MBPS/DRV_MATCH/DRV_START/DRV_END
# parsed from the driver's one-line `status=... key=value ...` output
# (shared format across eng_pcrec.c / eng_pcre2.c / eng_py.py).
# Every invocation runs under $PIN (R2-B3; empty string when unavailable,
# word-split so it contributes zero argv elements in that case -- see
# run_bench.sh's run_bdriver for the same pattern).
run_driver() {
    local tmo="$1"; shift
    local out rc
    out="$(timeout "$tmo" $PIN "$@" 2>&1)"
    rc=$?
    DRV_RAW="$out"
    if [ $rc -eq 124 ]; then
        DRV_RC="dnf"
        return
    elif [ $rc -ne 0 ]; then
        DRV_RC="error"
        return
    fi
    DRV_STATUS="$(extract_field "$out" status)"
    if [ -z "$DRV_STATUS" ]; then
        DRV_RC="error"
        return
    fi
    DRV_RC="ok"
    DRV_BYTES="$(extract_field "$out" bytes)"
    DRV_ITERS="$(extract_field "$out" iters)"
    DRV_SECS="$(extract_field "$out" secs)"
    DRV_MBPS="$(extract_field "$out" mbps)"
    DRV_MATCH="$(extract_field "$out" match)"
    DRV_START="$(extract_field "$out" start)"
    DRV_END="$(extract_field "$out" end)"
}

# build_engine_argv <engine> <case-dir> <pattern> <subject> <iters>
# Sets global array ENGINE_ARGV to the full command line for that engine.
build_engine_argv() {
    local engine="$1" cdir="$2" pattern="$3" subject="$4" iters="$5"
    case "$engine" in
        pcrec)        ENGINE_ARGV=("$cdir/eng_pcrec" "$subject" "$iters") ;;
        pcre2-interp) ENGINE_ARGV=("$ENG_PCRE2" interp "$pattern" "$subject" "$iters") ;;
        pcre2-jit)    ENGINE_ARGV=("$ENG_PCRE2" jit "$pattern" "$subject" "$iters") ;;
        python-re)    ENGINE_ARGV=(python3 "$ENG_PY" "$pattern" "$subject" "$iters") ;;
        *) record_hard_error "build_engine_argv: unknown engine '$engine'"; ENGINE_ARGV=() ;;
    esac
}

echo "pcrec:   $PCREC"
echo "cc:      $CC ($("$CC" --version 2>&1 | head -n1))"
echo "workdir: $WORKDIR"
echo

# =========================================================================
# Build the shared (per-run, not per-case) engine binaries
# =========================================================================

echo "== BUILD =="

ENG_PCRE2="$WORKDIR/eng_pcre2"
berr="$(timeout "$BUILD_TIMEOUT" "$CC" -O2 -std=gnu11 -Wall -Wextra -Werror \
    -o "$ENG_PCRE2" "$SCRIPT_DIR/eng_pcre2.c" -ldl 2>&1)"
if [ $? -ne 0 ]; then
    record_hard_error "failed to build eng_pcre2: $berr"
    echo "compare.sh: cannot continue without eng_pcre2" >&2
    exit 1
fi
echo "  built eng_pcre2"

ENG_PY="$SCRIPT_DIR/eng_py.py"
if [ ! -f "$ENG_PY" ]; then
    record_hard_error "eng_py.py not found at $ENG_PY"
    exit 1
fi
echo "  eng_py.py: $ENG_PY"

probe_out="$(timeout 30 "$ENG_PCRE2" probe 2>&1)"
probe_rc=$?
JIT_LIB_AVAILABLE=0
PCRE2_VERSION="unknown"
if [ $probe_rc -eq 0 ]; then
    if [[ "$probe_out" =~ jit_available=([0-9]+) ]]; then
        JIT_LIB_AVAILABLE="${BASH_REMATCH[1]}"
    fi
    if [[ "$probe_out" =~ version=([^[:space:]]+) ]]; then
        PCRE2_VERSION="${BASH_REMATCH[1]//_/ }"
    fi
else
    record_hard_error "eng_pcre2 probe failed (rc=$probe_rc): $probe_out"
fi
echo "  PCRE2 version: $PCRE2_VERSION"
echo "  PCRE2 JIT available (library-level): $([ "$JIT_LIB_AVAILABLE" = "1" ] && echo yes || echo 'NO -- pcre2-jit column omitted entirely')"
echo

# =========================================================================
# Machine context header
# =========================================================================

CPU_MODEL="$(grep -m1 'model name' /proc/cpuinfo 2>/dev/null | sed 's/^model name[[:space:]]*:[[:space:]]*//')"
[ -z "$CPU_MODEL" ] && CPU_MODEL="unknown"
GCC_VER="$("$CC" --version 2>&1 | head -n1)"
PY_VER="$(python3 --version 2>&1)"
HOSTNAME_STR="$(hostname 2>/dev/null || echo unknown-host)"
DATE_YMD="$(date +%Y%m%d)"
DATE_ISO="$(date -Iseconds 2>/dev/null || date)"

# Governor/turbo capture (R2-B3) -- a number without the machine state
# behind it is not a measurement. Same probe as run_bench.sh's describe_env.
GOVERNOR="$(cat /sys/devices/system/cpu/cpu${BENCH_CPU}/cpufreq/scaling_governor 2>/dev/null || echo unknown)"
if [ -r /sys/devices/system/cpu/intel_pstate/no_turbo ]; then
    TURBO=$([ "$(cat /sys/devices/system/cpu/intel_pstate/no_turbo)" = "1" ] && echo off || echo on)
elif [ -r /sys/devices/system/cpu/cpufreq/boost ]; then
    TURBO=$([ "$(cat /sys/devices/system/cpu/cpufreq/boost)" = "1" ] && echo on || echo off)
else
    TURBO="unknown"
fi

# R3.10: sample load HERE too, before the (tens-of-minutes) case loop runs,
# not just after it (below). A single post-hoc sample only catches a box that
# got busy by the time the WHOLE matrix finished; a box that was already busy
# at the start and stayed busy throughout is exactly as invisible to a
# start-only check as run_bench.sh's old end-only... this script's problem was
# the mirror image of run_bench.sh's (R3 critic finding there): one sample,
# taken at the wrong end. LOADED (computed later, after the loop) is now
# start-loaded OR end-loaded.
LOAD_1MIN_START="$(cut -d' ' -f1 /proc/loadavg 2>/dev/null || echo 0)"

echo "== MACHINE CONTEXT =="
echo "  host:     $HOSTNAME_STR"
echo "  date:     $DATE_ISO"
echo "  cpu:      $CPU_MODEL"
echo "  load:     $(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null || echo unknown) (1/5/15 min, $(nproc 2>/dev/null || echo '?') cores)"
echo "  pinning:  $PIN_NOTE (cpu $BENCH_CPU)"
echo "  trials:   $BENCH_TRIALS per engine/case measurement (reported: median, spread column: max/min)"
echo "  governor: $GOVERNOR (cpu$BENCH_CPU)   turbo: $TURBO"
echo "  gcc:      $GCC_VER"
echo "  pcre2:    $PCRE2_VERSION (jit: $([ "$JIT_LIB_AVAILABLE" = "1" ] && echo available || echo unavailable))"
echo "  python3:  $PY_VER"
echo

# =========================================================================
# Subject generation
# =========================================================================

echo "== SUBJECTS =="

subj_dir="$WORKDIR/subjects"
mkdir -p "$subj_dir"

py_err="$(python3 - "$subj_dir" 2>&1 <<'PYEOF'
import random, sys, os

outdir = sys.argv[1]
MB = 1024 * 1024
LOWER = b"abcdefghijklmnopqrstuvwxyz"

def rand_lower(rng, n):
    return bytes(rng.choices(LOWER, k=n))

DIGITS = b"0123456789"

def rand_wordy(rng, n):
    """~n bytes of space-separated lowercase "words" (length 3-12) with an
    occasional digit run, i.e. text that behaves like real prose/log
    content rather than one giant run of [a-z]. Used for case (d): a pure
    rand_lower() filler lets '[a-z]+' at the start of the pattern greedily
    match the ENTIRE lowercase prefix of the buffer and land on the FIRST
    '@' anywhere in it (the first planted token, wherever that is), which
    is correct leftmost-match behavior but defeats the point of the case
    (measuring a scan through realistic text before finding a token) --
    see README.md's case (d) caveat. Word/digit boundaries here bound every
    '[a-z]+' run to at most 12 bytes outside the deliberately planted
    tokens, so the leftmost match genuinely lands at the first planted
    token instead of at buffer offset 0."""
    parts = []
    total = 0
    while total < n:
        if rng.random() < 0.15:
            chunk = bytes(rng.choices(DIGITS, k=rng.randint(1, 6)))
        else:
            chunk = rand_lower(rng, rng.randint(3, 12))
        parts.append(chunk)
        parts.append(b" ")
        total += len(chunk) + 1
    return b"".join(parts)[:n]

def purge_words(buf, words):
    """In-place: mutate any occurrence of any word in `words` inside `buf`
    (a bytearray of lowercase letters) so none remain. Used for subjects
    that must genuinely have NO match, where naive random generation has a
    non-negligible chance of an accidental hit (short alternation words in
    an 8 MB buffer are not astronomically rare -- see compare.sh's case (c)
    comment)."""
    passes = 0
    while passes < 200:
        passes += 1
        s = bytes(buf)
        any_hit = False
        for w in words:
            idx = s.find(w)
            while idx != -1:
                any_hit = True
                mid = idx + len(w) // 2
                target_letter = w[len(w) // 2:len(w) // 2 + 1]
                for repl in LOWER:
                    if bytes([repl]) != target_letter:
                        buf[mid] = repl
                        break
                s = bytes(buf)
                idx = s.find(w, idx + 1)
        if not any_hit:
            break
    else:
        raise RuntimeError("purge_words: did not converge after 200 passes")
    return buf

rng = random.Random(1729)

# (a) literal needle planted at 90% of 8 MB random lowercase text (match)
n = 8 * MB
buf = bytearray(rand_lower(rng, n))
needle = b"needleXYZW"
pos = int(n * 0.9)
buf[pos:pos + len(needle)] = needle
with open(os.path.join(outdir, "a_needle.bin"), "wb") as f:
    f.write(buf)

# (b) literal needle absent: independent 8 MB random lowercase text, then
# an assertion (not just a hope) that the needle truly never occurs --
# expected occurrences ~1e-8 for a 10-byte word so purging isn't needed,
# but we verify rather than assume.
buf = bytearray(rand_lower(rng, n))
s = bytes(buf)
if needle in s:
    idx = s.find(needle)
    buf[idx] = (buf[idx] + 1) % 26 + ord('a') if False else (LOWER[(LOWER.index(buf[idx]) + 1) % 26])
    assert bytes(buf).find(needle) == -1 or True  # single-byte break is sufficient; re-verify below
    while needle in bytes(buf):
        idx = bytes(buf).find(needle)
        buf[idx] = LOWER[(LOWER.index(buf[idx]) + 1) % 26]
with open(os.path.join(outdir, "b_needle_absent.bin"), "wb") as f:
    f.write(buf)

# (c) alternation '(alpha|beta|gamma|delta|epsilon)' absent: short words
# (4-7 letters) DO have non-negligible accidental-occurrence odds across
# 8 MB of random lowercase text (~1 expected combined), so purge_words is
# load-bearing here, not defensive-only.
words = [b"alpha", b"beta", b"gamma", b"delta", b"epsilon"]
buf = bytearray(rand_lower(rng, n))
purge_words(buf, words)
with open(os.path.join(outdir, "c_alt_absent.bin"), "wb") as f:
    f.write(buf)

# (d) '[a-z]+@[a-z]+\.[a-z]{2,3}' over mixed word/digit text with ~100
# planted email-ish tokens (match). '@' and '.' never occur in the filler,
# so the only possible matches are at the planted positions; the filler
# uses rand_wordy() (not rand_lower()) specifically so '[a-z]+' runs stay
# short (word-length) outside the plants -- see rand_wordy()'s docstring
# and README.md's case (d) caveat for why a pure-lowercase filler was
# wrong here (it let the leftmost match land at buffer offset 0 instead of
# at the first planted token, like it would on real mixed text).
buf = bytearray(rand_wordy(rng, n))
n_tokens = 100
step = n // (n_tokens + 1)
tlds = [b"com", b"net", b"org", b"io", b"co"]
for i in range(n_tokens):
    p = step * (i + 1)
    user = rand_lower(rng, rng.randint(3, 8))
    domain = rand_lower(rng, rng.randint(3, 8))
    tld = rng.choice(tlds)
    tok = user + b"@" + domain + b"." + tld
    buf[p:p + len(tok)] = tok
with open(os.path.join(outdir, "d_email.bin"), "wb") as f:
    f.write(buf)

# (e) 'a*b' over 8 MB of all-'a' (nomatch, the R1 A-2 pathological case --
# same shape as tests/bench/run_bench.sh's subject (b))
with open(os.path.join(outdir, "e_alla.bin"), "wb") as f:
    f.write(b"a" * n)

# (f) '[01]*1[01]{8}' over 8 MB random '0'/'1' bytes (match likely)
buf = bytes(rng.choices(b"01", k=n))
with open(os.path.join(outdir, "f_bits.bin"), "wb") as f:
    f.write(buf)

# (g) 'x{40,60}y' over random text with one planted 50-x run + y near the
# end. Filler alphabet deliberately EXCLUDES 'x' and 'y' so no accidental
# x-run (of any length) or y can occur anywhere except the plant --
# guarantees a single, deterministic match location across all engines.
filler_alphabet = bytes(c for c in LOWER if c not in b"xy")
buf = bytearray(bytes(rng.choices(filler_alphabet, k=n)))
plant_pos = n - 2000
buf[plant_pos:plant_pos + 50] = b"x" * 50
buf[plant_pos + 50:plant_pos + 51] = b"y"
with open(os.path.join(outdir, "g_runxy.bin"), "wb") as f:
    f.write(buf)

# (h) '.*=.*' over a 1 MB single line (no embedded newlines, so '.'
# unambiguously matches every byte the same way in every engine) of
# key=value text -- greedy '.*' on both sides of every '=' is a classic
# backtracking stressor for interpreter engines.
h_n = 1 * MB
parts = []
total = 0
i = 0
while total < h_n:
    kv = b"key%d=value%d;" % (i, i)
    parts.append(kv)
    total += len(kv)
    i += 1
h_buf = b"".join(parts)[:h_n]
with open(os.path.join(outdir, "h_kv.bin"), "wb") as f:
    f.write(h_buf)

# (i) 'a(b|c)+d' over a fixed 60-byte subject (short-subject regime: this
# case measures per-call overhead, not throughput -- see compare.sh).
i_buf = b"z" * 20 + b"abcbcd" + b"q" * 34
assert len(i_buf) == 60
with open(os.path.join(outdir, "i_short.bin"), "wb") as f:
    f.write(i_buf)

# (j) '([01]*)1([01]{8})' over 8 MB random '0'/'1' bytes (match likely) --
# DD-9's non-regression floor (engine_m4.md 8.5): the CAPTURE-BEARING
# sibling of case (f). Same alphabet/size as (f), own buffer (not a reuse of
# f_bits.bin) for the same reason every other case here gets its own file --
# but drawn from the shared rng at a different point in its sequence, so the
# two buffers are not byte-identical. Unlike (f), this pattern has two
# capturing groups, which routes it to the VM+prefilter hybrid engine
# (D42.1: captures on by default) rather than the pure DFA (f) takes --
# see compare.sh's case-processing loop, which builds pcrec with no
# --no-captures flag for any case, and gate.sh/floors.tsv's provenance
# comment for the measured floor this case pins.
buf = bytes(rng.choices(b"01", k=n))
with open(os.path.join(outdir, "j_bits_captures.bin"), "wb") as f:
    f.write(buf)

print("subjects generated in", outdir)
PYEOF
)"
py_rc=$?
if [ $py_rc -ne 0 ]; then
    record_hard_error "python3 subject generation failed: $py_err"
    echo "compare.sh: cannot continue without subjects" >&2
    exit 1
fi
echo "  $py_err"
echo

# =========================================================================
# Case matrix
# =========================================================================

CASE_IDS=(a b c d e f g h i j)
# CASES=<comma-separated case ids> restricts which cases process_case runs,
# e.g. CASES=e,d for a fast mechanics smoke-test instead of the full
# 10-case/~4-engine run. Subjects for ALL cases are still generated (cheap
# relative to the per-case build+measure work), so this only trims the
# expensive part.
if [ -n "${CASES:-}" ]; then
    IFS=',' read -r -a CASE_IDS <<<"$CASES"
fi

declare -A CASE_DESC=(
    [a]="literal 'needleXYZW' planted at 90% of 8 MB random text (match)"
    [b]="literal 'needleXYZW' absent, full scan over 8 MB random text (nomatch)"
    [c]="alternation of 5 words absent, full scan over 8 MB random text (nomatch)"
    [d]="email-ish token class over 8 MB random text, ~100 planted (match)"
    [e]="'a*b' over 8 MB of all-'a' -- R1 A-2 pathological nomatch shape"
    [f]="'[01]*1[01]{8}' over 8 MB random 0/1 bytes (match likely)"
    [g]="'x{40,60}y', one planted 50-x run + y near the end of 8 MB (match)"
    [h]="'.*=.*' greedy backtracking stressor over a 1 MB key=value line (match)"
    [i]="'a(b|c)+d' over a 60-byte subject -- short-subject per-call overhead regime"
    [j]="'([01]*)1([01]{8})' over 8 MB random 0/1 bytes (match likely) -- DD-9 capture-bearing sibling of (f), engine_m4.md 8.5 non-regression floor for the VM+prefilter hybrid"
)
declare -A CASE_PATTERN=(
    [a]='needleXYZW'
    [b]='needleXYZW'
    [c]='(alpha|beta|gamma|delta|epsilon)'
    [d]='[a-z]+@[a-z]+\.[a-z]{2,3}'
    [e]='a*b'
    [f]='[01]*1[01]{8}'
    [g]='x{40,60}y'
    [h]='.*=.*'
    [i]='a(b|c)+d'
    [j]='([01]*)1([01]{8})'
)
declare -A CASE_SUBJECT=(
    [a]="$subj_dir/a_needle.bin"
    [b]="$subj_dir/b_needle_absent.bin"
    [c]="$subj_dir/c_alt_absent.bin"
    [d]="$subj_dir/d_email.bin"
    [e]="$subj_dir/e_alla.bin"
    [f]="$subj_dir/f_bits.bin"
    [g]="$subj_dir/g_runxy.bin"
    [h]="$subj_dir/h_kv.bin"
    [i]="$subj_dir/i_short.bin"
    [j]="$subj_dir/j_bits_captures.bin"
)
# metric: "throughput" (MB/s, default) or "latency" (ns/call, case i)
declare -A CASE_METRIC=( [i]="latency" )
# CASE_FLAGS: extra pcrec flags for this case's build, same purpose D46 gave
# run_bench.sh's build_bench_bin -- a benched case must PIN the configuration
# it measures, or a later default change silently re-points the measurement
# at a different strategy while the floor keeps claiming otherwise.
#
# (c) and (i) are PINNED to --no-captures (M4.6b, 2026-08-17, following
# run_bench.sh's own precedent for the identical (c) pattern text). Both have
# an INCIDENTAL capturing group -- grouping only, never read -- that, once
# D42.1 made captures the default (2026-08-14), silently moved them off the
# pure DFA their floors were captured against and onto the VM+prefilter
# hybrid: found when adding (j) surfaced (c) as a 1.5x-looking "regression"
# that was actually an engine switch three days old and completely
# unflagged. Pinning restores what floors.tsv has measured for (c)/(i) since
# 2026-08-09/2026-08-11; the capture-bearing DEFAULT-path number for a
# similarly-shaped pattern is exactly what (j) exists to cover instead. See
# this directory's CLAUDE.md for the full finding write-up and the measured
# DFA-vs-hybrid gap on these two shapes (data, not a regression: the hybrid
# buys capture extraction that (c)/(i) never asked for).
declare -A CASE_FLAGS=(
    [c]="--no-captures"
    [i]="--no-captures"
)
# CASE_EXPECT_ENGINE: the durable fix for the finding above. Every case
# declares which engine its artifact MUST stamp; process_case asserts
# rx_info.engine against it right after the build, before any measurement is
# trusted. A number pins a value; this pins what the number MEASURES -- the
# next default flip that silently changes engine selection now fails loudly
# as an ENGINE MISMATCH hard error instead of aging as an unflagged multi-day
# throughput mystery the way (c)/(i) just did. "DFA" = ENGM_DFA (1), "VM" =
# ENGM_VM (2) -- see lib/pcrec.h's rx_info.engine / RX_ENGINE_WHY comments
# for what the artifact itself stamps.
declare -A CASE_EXPECT_ENGINE=(
    [a]="DFA"
    [b]="DFA"
    [c]="DFA"
    [d]="DFA"
    [e]="DFA"
    [f]="DFA"
    [g]="DFA"
    [h]="DFA"
    [i]="DFA"
    [j]="VM"
)

# =========================================================================
# Per-case processing
# =========================================================================

# Global result accumulators, filled in by process_case, read by the
# Results section below.
declare -a ALL_ROWS=()          # tab-joined: case engine status bytes iters secs metric value ratio_vs_pcrec spread
declare -A CASE_VALID=()        # id -> "valid" | "invalid" | "error"
declare -A CASE_REASON=()       # id -> human reason (invalid/error cases)
declare -A CASE_REF_VERDICT=()  # id -> "nomatch" | "match [s,e)"

process_case() {
    local id="$1"
    local pattern="${CASE_PATTERN[$id]}"
    local subject="${CASE_SUBJECT[$id]}"
    local desc="${CASE_DESC[$id]}"

    echo "== Case $id: $desc =="
    echo "   pattern: $pattern"

    local cdir="$WORKDIR/case_$id"
    mkdir -p "$cdir"

    # ---- build the pcrec matcher for this case's pattern ----
    # shellcheck disable=SC2206
    local extra_flags=(${CASE_FLAGS[$id]:-})
    local perr
    perr="$(timeout "$PCREC_TIMEOUT" "$PCREC" -p rx "${extra_flags[@]}" -o "$cdir/gen.c" -- "$pattern" 2>&1 >/dev/null)"
    if [ $? -ne 0 ]; then
        record_hard_error "pcrec failed to compile case $id pattern '$pattern': $perr"
        CASE_VALID[$id]="error"; CASE_REASON[$id]="pcrec compile failure: $perr"
        echo "   SKIPPED (pcrec compile failure)"; echo
        return
    fi

    # ---- engine assertion (M4.6b): the artifact must stamp the engine this
    # case DECLARES, or the number about to be measured is not the number
    # this case's floor claims to pin -- see CASE_EXPECT_ENGINE's own
    # comment for the finding that made this necessary (cases (c)/(i) aged
    # silently onto the VM+prefilter hybrid for three days with nothing red
    # anywhere). A mismatch is a hard error, same severity as a build
    # failure: a floor gated against the wrong engine is worse than no floor
    # at all, since it looks measured. ----
    local expect_engine="${CASE_EXPECT_ENGINE[$id]:-}"
    if [ -n "$expect_engine" ]; then
        local want_stamp got_stamp
        case "$expect_engine" in
            DFA) want_stamp="ENGM_DFA" ;;
            VM)  want_stamp="ENGM_VM" ;;
            *)   record_hard_error "case $id: CASE_EXPECT_ENGINE has an unknown value '$expect_engine'"; return ;;
        esac
        got_stamp="$(grep -oE '/\* ENGM_(DFA|VM) \*/' "$cdir/gen.c" | grep -oE 'ENGM_(DFA|VM)' | head -1)"
        if [ "$got_stamp" != "$want_stamp" ]; then
            record_hard_error "case $id: ENGINE MISMATCH -- expected $want_stamp, artifact stamps rx_info.engine = ${got_stamp:-<not found>} (see CASE_EXPECT_ENGINE and this directory's CLAUDE.md for the finding this assertion guards against)"
            CASE_VALID[$id]="error"; CASE_REASON[$id]="engine mismatch: expected $want_stamp, got ${got_stamp:-<not found>}"
            echo "   SKIPPED (engine mismatch: expected $want_stamp, got ${got_stamp:-<not found>})"; echo
            return
        fi
    fi

    local berr
    berr="$(timeout "$BUILD_TIMEOUT" "$CC" -O2 -std=gnu11 -Wall -Wextra -Werror \
        -I"$cdir" -o "$cdir/eng_pcrec" "$SCRIPT_DIR/eng_pcrec.c" "$cdir/gen.c" 2>&1)"
    if [ $? -ne 0 ]; then
        record_hard_error "$CC failed to build eng_pcrec for case $id: $berr"
        CASE_VALID[$id]="error"; CASE_REASON[$id]="\$CC build failure: $berr"
        echo "   SKIPPED (\$CC build failure)"; echo
        return
    fi

    # ---- ordered engine list for this case ----
    local engines=(pcrec pcre2-interp)
    [ "$JIT_LIB_AVAILABLE" = "1" ] && engines+=(pcre2-jit)
    engines+=(python-re)

    # ---- baseline iters=1 run per engine: doubles as the pre-timing
    # agreement check AND the calibration baseline (avoids a redundant
    # extra subprocess launch per engine). ----
    local -A base_rc base_status base_match base_start base_end base_secs base_bytes
    local eng
    for eng in "${engines[@]}"; do
        build_engine_argv "$eng" "$cdir" "$pattern" "$subject" 1
        run_driver "$RUN_TIMEOUT" "${ENGINE_ARGV[@]}"
        base_rc[$eng]="$DRV_RC"
        base_status[$eng]="${DRV_STATUS:-}"
        base_match[$eng]="${DRV_MATCH:-}"
        base_start[$eng]="${DRV_START:-}"
        base_end[$eng]="${DRV_END:-}"
        base_secs[$eng]="${DRV_SECS:-}"
        base_bytes[$eng]="${DRV_BYTES:-}"
    done

    # pcrec is the one truly mandatory engine: it's the product under test,
    # and every other engine's baseline was already attempted above
    # regardless of whether pcrec succeeded, so this check happens after
    # collection, not instead of it.
    if [ "${base_rc[pcrec]}" != "ok" ]; then
        record_hard_error "case $id: pcrec engine failed to run (rc=${base_rc[pcrec]}): ${DRV_RAW:-}"
        CASE_VALID[$id]="error"; CASE_REASON[$id]="pcrec failed to run (rc=${base_rc[pcrec]})"
        echo "   SKIPPED (mechanical failure on pcrec)"; echo
        return
    fi

    # ---- pick a reference oracle: prefer pcre2-interp (this project's
    # established oracle, see tests/fuzz/pcre2_oracle.c), fall back to
    # python-re. A single-call (iters=1) DNF on the oracle is NOT
    # necessarily a harness bug -- 'a*b' over 8 MB of all-'a' is exactly
    # the R1 A-2 catastrophic-backtracking shape, and a naive backtracking
    # interpreter (no JIT) can genuinely be quadratic on it too, just like
    # the OLD pcrec emitter was. When that happens this is reported as a
    # real result (oracle DNF), not hidden as a mechanical failure, and we
    # still measure and report pcrec (and any other engine that DID
    # finish) rather than discarding the whole case. ----
    local ref_eng=""
    for cand in pcre2-interp python-re; do
        if [ "${base_rc[$cand]:-}" = "ok" ] && [ "${base_status[$cand]:-}" = "ok" ]; then
            ref_eng="$cand"
            break
        fi
    done

    local invalid=0
    local -a reasons=()
    local -a notes=()

    for eng in pcre2-interp python-re pcre2-jit; do
        [[ " ${engines[*]} " == *" $eng "* ]] || continue
        if [ "${base_rc[$eng]:-}" != "ok" ]; then
            notes+=("$eng baseline did not return a verdict within ${RUN_TIMEOUT}s (rc=${base_rc[$eng]:-n/a}) -- reported as DNF/error below, not timed, not treated as a disagreement")
        elif [ "${base_status[$eng]}" = "jit_unavailable" ]; then
            : # not applicable, not a disagreement, noted separately below
        elif [ "${base_status[$eng]}" != "ok" ]; then
            notes+=("$eng returned status=${base_status[$eng]} (not a verdict)")
        fi
    done

    if [ -z "$ref_eng" ]; then
        notes+=("no oracle (pcre2-interp or python-re) returned a verdict within ${RUN_TIMEOUT}s -- agreement UNVERIFIED, pcrec's own result reported standalone")
    else
        local ref_match="${base_match[$ref_eng]}" ref_start="${base_start[$ref_eng]}" ref_end="${base_end[$ref_eng]}"
        for eng in pcrec pcre2-interp python-re pcre2-jit; do
            [ "$eng" = "$ref_eng" ] && continue
            [[ " ${engines[*]} " == *" $eng "* ]] || continue
            [ "${base_rc[$eng]:-}" = "ok" ] || continue                      # DNF/error: noted above, not a disagreement
            [ "${base_status[$eng]}" = "jit_unavailable" ] && continue       # not applicable, not a disagreement
            if [ "${base_status[$eng]}" != "ok" ]; then
                invalid=1
                reasons+=("$eng returned status=${base_status[$eng]} (not a verdict)")
                continue
            fi
            if [ "${base_match[$eng]}" != "$ref_match" ] || { [ "$ref_match" = "1" ] && { [ "${base_start[$eng]}" != "$ref_start" ] || [ "${base_end[$eng]}" != "$ref_end" ]; }; }; then
                invalid=1
                reasons+=("$eng disagrees with $ref_eng: match=${base_match[$eng]}/$ref_match span=[${base_start[$eng]:-},${base_end[$eng]:-})/[${ref_start:-},${ref_end:-})")
            fi
        done
    fi

    if [ $invalid -eq 1 ]; then
        local reason_str
        reason_str="$(join_semi "${reasons[@]}")"
        echo "   VERDICT: INVALID -- not timed. $reason_str"
        echo "   (check docs/dev/upstream_issues.md for a known divergence before assuming a pcrec bug)"
        CASE_VALID[$id]="invalid"
        CASE_REASON[$id]="$reason_str"
        ALL_ROWS+=("$id"$'\t'"*"$'\t'"INVALID"$'\t'-$'\t'-$'\t'-$'\t'-$'\t'-$'\t'-$'\t'-)
        echo
        return
    fi

    local early_match_note=""
    if [ -n "$ref_eng" ]; then
        CASE_VALID[$id]="valid"
        local ref_match="${base_match[$ref_eng]}" ref_start="${base_start[$ref_eng]}" ref_end="${base_end[$ref_eng]}"
        if [ "$ref_match" = "1" ]; then
            CASE_REF_VERDICT[$id]="match [$ref_start,$ref_end) (oracle: $ref_eng)"
        else
            CASE_REF_VERDICT[$id]="nomatch (oracle: $ref_eng)"
        fi
        echo "   agreement: OK vs $ref_eng (${CASE_REF_VERDICT[$id]})"

        # ---- early-match honesty guard: if the leftmost match ends well
        # before the end of the buffer, MB/s (buffer_bytes / time) reflects
        # how little of the buffer had to be scanned before an early exit,
        # not a steady-state scan rate. Every engine's MB/s figure in this
        # case is inflated by the same effect, so the numbers are still
        # fair to compare WITHIN this case's rows, but not comparable
        # across cases or to a genuine full-scan measurement. Threshold:
        # match ends before 80% of the buffer. ----
        if [ "$ref_match" = "1" ] && [ "${CASE_METRIC[$id]:-throughput}" = "throughput" ]; then
            local buf_n="${base_bytes[pcrec]:-0}"
            if awk -v e="$ref_end" -v n="$buf_n" 'BEGIN{exit !(n>0 && e < 0.8*n)}'; then
                local pct
                pct=$(awk -v e="$ref_end" -v n="$buf_n" 'BEGIN{printf "%.1f", (e/n)*100}')
                early_match_note="early match at byte $ref_end of $buf_n (${pct}% of buffer scanned) -- MB/s reflects early exit, not steady-state scan rate; compare within this case's rows only, not across cases"
                echo "   note: $early_match_note"
            fi
        fi
    else
        CASE_VALID[$id]="unverified"
        if [ "${base_match[pcrec]}" = "1" ]; then
            CASE_REF_VERDICT[$id]="pcrec reports match [${base_start[pcrec]},${base_end[pcrec]}) -- UNVERIFIED, no oracle finished"
        else
            CASE_REF_VERDICT[$id]="pcrec reports nomatch -- UNVERIFIED, no oracle finished"
        fi
        echo "   agreement: UNVERIFIED -- $(join_semi "${notes[@]}")"
    fi
    for note in "${notes[@]}"; do
        echo "   note: $note"
    done
    for eng in "${engines[@]}"; do
        if [ "${base_status[$eng]}" = "jit_unavailable" ]; then
            echo "   note: pcre2-jit could not JIT-compile this specific pattern; omitted for this case"
        fi
    done

    # Fold every note (partial-DNF among non-reference engines, JIT
    # unavailable for this pattern, early-match) into the case's stored
    # annotation so it surfaces in the verdict column of both the streamed
    # summary and the markdown report -- a DNF'd non-reference engine or an
    # early-match subject still needs to be visible even on an otherwise
    # "valid" case, not just logged and forgotten.
    local -a all_notes=("${notes[@]}")
    [ -n "$early_match_note" ] && all_notes+=("$early_match_note")
    if [ ${#all_notes[@]} -gt 0 ]; then
        CASE_REASON[$id]="$(join_semi "${all_notes[@]}")"
    fi

    # ---- scale + measure (R2-B1/B2/B3): compute each engine's target
    # iteration count from its baseline iters=1 sample (same formula as
    # before -- if the baseline already cleared TARGET_SECS the target
    # clamps to 1), then run BENCH_TRIALS independent, pinned trials at that
    # target and report the MEDIAN, carrying max/min spread alongside. A
    # single baseline sample is no longer treated as itself the
    # measurement, even when it already cleared TARGET_SECS -- BENCH_TRIALS
    # fresh process launches give a genuine spread instead of one sample
    # standing in for all of them.
    #
    # Engines whose BASELINE already failed (dnf/error) are reported as such
    # directly and never enter the trial loop -- a baseline that didn't
    # finish in RUN_TIMEOUT at iters=1 would only be MORE likely to time out
    # again at a larger iters, wasting BENCH_TRIALS full timeouts for no new
    # information. A DNF or error DURING the trial loop stops that engine's
    # remaining trials and reports DNF/error for the whole measurement --
    # never silently retried past or averaged away (whatever trials already
    # succeeded are discarded, not partially reported).
    #
    # Order interleaving (R2-B3: pcrec was always measured FIRST, a
    # systematic confound): trial i starts the per-trial engine list at
    # index (i mod N) and wraps around, so across BENCH_TRIALS trials every
    # engine leads roughly once. This is a genuine rotation across trials,
    # not a one-time shuffle -- it changes only invocation ORDER, never
    # which engines run or which engine a result is attributed to.
    local -A f_status f_secs f_iters f_bytes f_mbps f_spread target_iters
    for eng in "${engines[@]}"; do
        if [ "${base_rc[$eng]:-}" != "ok" ]; then
            f_status[$eng]="${base_rc[$eng]:-error}"
            continue
        fi
        if [ "${base_status[$eng]}" = "jit_unavailable" ]; then
            f_status[$eng]="jit_unavailable"
            continue
        fi
        if [ "${base_status[$eng]}" != "ok" ]; then
            f_status[$eng]="${base_status[$eng]}"
            continue
        fi
        local secs1="${base_secs[$eng]}"
        target_iters[$eng]=$(awk -v s="$secs1" -v t="$TARGET_SECS" \
            'BEGIN{ if (s < 0.000001) s = 0.000001; v = (t / s) * 1.2; if (v < 1) v = 1; if (v > 50000000) v = 50000000; printf "%d", v }')
    done

    local n_engines=${#engines[@]}
    local -A trial_secs trial_mbps    # eng -> space-separated values across trials
    local trial
    for ((trial = 0; trial < BENCH_TRIALS; trial++)); do
        local rot_start=$((trial % n_engines))
        local order=() k
        for ((k = 0; k < n_engines; k++)); do
            order+=("${engines[$(((rot_start + k) % n_engines))]}")
        done
        for eng in "${order[@]}"; do
            [ -n "${f_status[$eng]:-}" ] && continue  # baseline-skipped (dnf/error/jit_unavailable) or a prior trial in this loop already failed
            local iters="${target_iters[$eng]}"
            build_engine_argv "$eng" "$cdir" "$pattern" "$subject" "$iters"
            run_driver "$RUN_TIMEOUT" "${ENGINE_ARGV[@]}"
            if [ "$DRV_RC" != "ok" ] || [ "$DRV_STATUS" != "ok" ]; then
                record_hard_error "case $id: engine $eng failed on trial $trial (iters=$iters, rc=$DRV_RC): ${DRV_RAW:-}"
                f_status[$eng]="error"
                continue
            fi
            f_iters[$eng]="$iters"
            f_bytes[$eng]="$DRV_BYTES"
            trial_secs[$eng]="${trial_secs[$eng]:-}${trial_secs[$eng]:+ }$DRV_SECS"
            trial_mbps[$eng]="${trial_mbps[$eng]:-}${trial_mbps[$eng]:+ }$DRV_MBPS"
        done
    done
    for eng in "${engines[@]}"; do
        [ -n "${f_status[$eng]:-}" ] && continue  # already dnf/error/jit_unavailable
        f_status[$eng]="ok"
        f_secs[$eng]="$(median ${trial_secs[$eng]})"
        f_mbps[$eng]="$(median ${trial_mbps[$eng]})"
        # spread of secs and spread of mbps are the same ratio (mbps is a
        # constant/secs for a fixed iters, and max/min is invariant under
        # reciprocal), so one spread column covers both metrics honestly.
        f_spread[$eng]="$(spread ${trial_secs[$eng]})"
    done

    # ---- report this case's rows, compute ratio vs best-other-engine ----
    local metric="${CASE_METRIC[$id]:-throughput}"
    local pcrec_mbps="${f_mbps[pcrec]:-}" pcrec_ns=""
    if [ "$metric" = "latency" ] && [ "${f_status[pcrec]}" = "ok" ]; then
        pcrec_ns=$(awk -v s="${f_secs[pcrec]}" -v i="${f_iters[pcrec]}" 'BEGIN{ printf "%.2f", (s*1e9)/i }')
    fi

    local best_other_mbps="" best_other_ns=""
    for eng in "${engines[@]}"; do
        [ "$eng" = "pcrec" ] && continue
        [ "${f_status[$eng]}" = "ok" ] || continue
        if [ "$metric" = "throughput" ]; then
            if [ -z "$best_other_mbps" ] || awk -v a="${f_mbps[$eng]}" -v b="$best_other_mbps" 'BEGIN{exit !(a+0>b+0)}'; then
                best_other_mbps="${f_mbps[$eng]}"
            fi
        else
            local ns
            ns=$(awk -v s="${f_secs[$eng]}" -v i="${f_iters[$eng]}" 'BEGIN{ printf "%.2f", (s*1e9)/i }')
            if [ -z "$best_other_ns" ] || awk -v a="$ns" -v b="$best_other_ns" 'BEGIN{exit !(a+0<b+0)}'; then
                best_other_ns="$ns"
            fi
        fi
    done

    printf "   %-14s %-6s %10s %10s %14s %8s\n" "engine" "status" "bytes" "iters" \
        "$([ "$metric" = "latency" ] && echo "ns/call" || echo "MB/s")" "spread"
    for eng in "${engines[@]}"; do
        local st="${f_status[$eng]:-n/a}"
        if [ "$st" != "ok" ]; then
            local st_val
            case "$st" in
                dnf) st_val="DNF>${RUN_TIMEOUT}s" ;;
                jit_unavailable) st_val="n/a (pattern not JIT-compilable)" ;;
                error) st_val="ERROR" ;;
                *) st_val="$st" ;;
            esac
            printf "   %-14s %-6s %10s %10s %14s %8s\n" "$eng" "$st" "-" "-" "$st_val" "-"
            ALL_ROWS+=("$id"$'\t'"$eng"$'\t'"$st"$'\t'-$'\t'-$'\t'-$'\t'"$metric"$'\t'"$st_val"$'\t'-$'\t'-)
            continue
        fi
        local val ratio_str row_val spr="${f_spread[$eng]:-n/a}x"
        if [ "$metric" = "latency" ]; then
            val=$(awk -v s="${f_secs[$eng]}" -v i="${f_iters[$eng]}" 'BEGIN{ printf "%.2f", (s*1e9)/i }')
            row_val="$val"
            printf "   %-14s %-6s %10s %10s %14s %8s\n" "$eng" "$st" "${f_bytes[$eng]}" "${f_iters[$eng]}" "$val" "$spr"
        else
            val="${f_mbps[$eng]}"
            row_val="$val"
            printf "   %-14s %-6s %10s %10s %14s %8s\n" "$eng" "$st" "${f_bytes[$eng]}" "${f_iters[$eng]}" "$val" "$spr"
        fi
        if [ "$eng" = "pcrec" ]; then
            ratio_str="1.000 (baseline)"
        elif [ "$metric" = "throughput" ] && [ -n "$best_other_mbps" ] && [ "${f_mbps[$eng]}" = "$best_other_mbps" ]; then
            ratio_str=$(awk -v p="$pcrec_mbps" -v o="$best_other_mbps" 'BEGIN{ printf "%.3f", (o>0)? p/o : 0 }')
            ratio_str="$ratio_str (vs this engine = best-other)"
        elif [ "$metric" = "latency" ] && [ -n "$best_other_ns" ]; then
            local this_ns
            this_ns=$(awk -v s="${f_secs[$eng]}" -v i="${f_iters[$eng]}" 'BEGIN{ printf "%.2f", (s*1e9)/i }')
            if [ "$this_ns" = "$best_other_ns" ]; then
                ratio_str=$(awk -v p="$pcrec_ns" -v o="$best_other_ns" 'BEGIN{ printf "%.3f", (p>0)? o/p : 0 }')
                ratio_str="$ratio_str (vs this engine = best-other)"
            else
                ratio_str="-"
            fi
        else
            ratio_str="-"
        fi
        ALL_ROWS+=("$id"$'\t'"$eng"$'\t'"$st"$'\t'"${f_bytes[$eng]}"$'\t'"${f_iters[$eng]}"$'\t'"${f_secs[$eng]}"$'\t'"$metric"$'\t'"$row_val"$'\t'"$ratio_str"$'\t'"$spr")
    done

    if [ "$metric" = "throughput" ] && [ -n "$best_other_mbps" ] && [ -n "$pcrec_mbps" ]; then
        local overall_ratio
        overall_ratio=$(awk -v p="$pcrec_mbps" -v o="$best_other_mbps" 'BEGIN{ printf "%.3f", (o>0)? p/o : 0 }')
        echo "   ratio (pcrec MB/s / best-other-engine MB/s): $overall_ratio"
    elif [ "$metric" = "latency" ] && [ -n "$best_other_ns" ] && [ -n "$pcrec_ns" ]; then
        local overall_ratio
        overall_ratio=$(awk -v p="$pcrec_ns" -v o="$best_other_ns" 'BEGIN{ printf "%.3f", (p>0)? o/p : 0 }')
        echo "   ratio (best-other-engine ns/call / pcrec ns/call): $overall_ratio"
    fi
    echo
}

for id in "${CASE_IDS[@]}"; do
    process_case "$id"
done

# =========================================================================
# Results: human table + machine-readable TSV
# =========================================================================

echo "== RESULTS =="
echo
echo "spread = max/min across BENCH_TRIALS ($BENCH_TRIALS) trials of the value column; 'n/a' means fewer than 2 successful trials."
printf "%-4s %-13s %-8s %12s %10s %14s %10s %-22s %s\n" \
    "case" "engine" "status" "bytes" "iters" "value" "metric" "ratio-vs-pcrec" "spread"
printf '%s\n' "------------------------------------------------------------------------------------------------------------------"
for row in "${ALL_ROWS[@]}"; do
    IFS=$'\t' read -r c e st b i s m v r sp <<<"$row"
    printf "%-4s %-13s %-8s %12s %10s %14s %10s %-22s %s\n" "$c" "$e" "$st" "$b" "$i" "$v" "$m" "$r" "$sp"
done
echo

echo "== BEGIN TSV =="
printf 'case\tengine\tstatus\tbytes\titers\tsecs\tmetric\tvalue\tratio_vs_pcrec\tspread\n'
for row in "${ALL_ROWS[@]}"; do
    printf '%s\n' "$row"
done
echo "== END TSV =="
echo

valid_count=0; invalid_count=0; unverified_count=0; error_count=0
for id in "${CASE_IDS[@]}"; do
    case "${CASE_VALID[$id]:-error}" in
        valid) valid_count=$((valid_count + 1)) ;;
        invalid) invalid_count=$((invalid_count + 1)) ;;
        unverified) unverified_count=$((unverified_count + 1)) ;;
        *) error_count=$((error_count + 1)) ;;
    esac
done

echo "== Summary =="
echo "cases: ${#CASE_IDS[@]}  valid(timed): $valid_count  invalid(agreement failure): $invalid_count  unverified(oracle DNF): $unverified_count  error(mechanical): $error_count"
echo "hard errors (harness/mechanical failures): $hard_errors"
if [ $invalid_count -gt 0 ]; then
    echo "INVALID cases (see per-case log above for details):"
    for id in "${CASE_IDS[@]}"; do
        [ "${CASE_VALID[$id]:-}" = "invalid" ] && echo "  case $id: ${CASE_REASON[$id]}"
    done
fi
if [ $unverified_count -gt 0 ]; then
    echo "UNVERIFIED cases (pcrec's own result reported standalone, no oracle finished in time):"
    for id in "${CASE_IDS[@]}"; do
        [ "${CASE_VALID[$id]:-}" = "unverified" ] && echo "  case $id: ${CASE_REASON[$id]}"
    done
fi

# =========================================================================
# Write the markdown report
# =========================================================================

LOAD_AVG="$(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null || uptime | sed -n 's/.*load average:\s*//p')"
NPROC="$(nproc 2>/dev/null || echo unknown)"

# Was the box actually busy? The report used to open with an unconditional
# "PROVISIONAL (load-compromised)" title and warning regardless of measured
# load -- actively misleading now that pinning/trials/spread are in place and
# the report separately surfaces load/governor/turbo. Same LOAD_LIMIT
# threshold and 1-minute-load comparison as tests/bench/run_bench.sh's
# LOADED/INCONCLUSIVE gate: max(2.0, cores/2), overridable via LOAD_LIMIT.
LOAD_LIMIT="${LOAD_LIMIT:-}"
if [ -z "$LOAD_LIMIT" ]; then
    LOAD_LIMIT="$(awk -v c="$(nproc 2>/dev/null || echo 4)" \
        'BEGIN{ v = c * 0.5; if (v < 2.0) v = 2.0; printf "%.2f", v }')"
fi
LOAD_1MIN="$(cut -d' ' -f1 /proc/loadavg 2>/dev/null || echo 0)"
# R3.10: LOADED is now decided from BOTH samples -- the one taken before the
# case loop (LOAD_1MIN_START, above) and this one taken after it. A box that
# was quiet at the start but got busy partway through a tens-of-minutes run is
# just as load-compromised as one that was busy throughout, and a single
# post-hoc sample alone could not see the first case.
LOADED_START=0
if num_gt "$LOAD_1MIN_START" "$LOAD_LIMIT"; then LOADED_START=1; fi
LOADED_END=0
if num_gt "$LOAD_1MIN" "$LOAD_LIMIT"; then LOADED_END=1; fi
LOADED=0
if [ "$LOADED_START" = "1" ] || [ "$LOADED_END" = "1" ]; then LOADED=1; fi

# Machine-readable, for gate.sh (R3.10: "same for gate.sh if it measures" --
# gate.sh itself does not measure, it consumes THIS script's numbers, and
# until now had no way to know whether they came from a loaded box at all).
echo "== BEGIN LOAD =="
printf 'load_1min_start\t%s\n' "$LOAD_1MIN_START"
printf 'load_1min_end\t%s\n' "$LOAD_1MIN"
printf 'load_limit\t%s\n' "$LOAD_LIMIT"
printf 'loaded\t%s\n' "$LOADED"
echo "== END LOAD =="
echo

# Never silently clobber an existing snapshot. The report name is only
# host+date, so a second run on the same day used to overwrite the first —
# and the first is typically the ANNOTATED baseline other documents cite
# (the current one carries checkpoint review R2's corrections). Losing the
# baseline is precisely how a performance regression goes unnoticed, which
# is the thing M2.11's gate exists to prevent. Set REPORT_FORCE=1 to
# overwrite deliberately.
REPORT="$SCRIPT_DIR/results-$HOSTNAME_STR-$DATE_YMD.md"
if [ -e "$REPORT" ] && [ "${REPORT_FORCE:-0}" != "1" ]; then
    report_n=2
    while [ -e "$SCRIPT_DIR/results-$HOSTNAME_STR-$DATE_YMD-$report_n.md" ]; do
        report_n=$((report_n + 1))
    done
    REPORT="$SCRIPT_DIR/results-$HOSTNAME_STR-$DATE_YMD-$report_n.md"
    echo "compare.sh: a snapshot for $HOSTNAME_STR/$DATE_YMD already exists;" >&2
    echo "compare.sh: writing to $(basename "$REPORT") instead (REPORT_FORCE=1 to overwrite)" >&2
fi
{
    if [ "$LOADED" = "1" ]; then
        echo "# pcrec cross-engine performance comparison -- PROVISIONAL (load-compromised)"
        echo
        echo "Generated by \`tests/bench/compare/compare.sh\` on $DATE_ISO."
        echo
        echo "**This snapshot was captured while the box was under heavy unrelated load"
        echo "at some point during generation (1-minute load $LOAD_1MIN_START at the start,"
        echo "$LOAD_1MIN at the end -- either exceeds this report's busy-box threshold of"
        echo "$LOAD_LIMIT -- same threshold tests/bench/run_bench.sh's LOADED/INCONCLUSIVE"
        echo "gate uses, cores/2 clamped to a floor of 2.0; load average $LOAD_AVG on"
        echo "$NPROC cores at generation time) -- absolute MB/s and ns/call figures, and"
        echo "the auto-scaled iteration counts they're based on, are noisier than a"
        echo "quiet-box run and may understate every engine's true throughput to varying"
        echo "degrees. Every timed measurement was still pinned ($PIN_NOTE) and is the"
        echo "median of $BENCH_TRIALS trials (see the \`spread\` column below), which"
        echo "narrows but does not eliminate load contamination. Cross-engine RATIOS are"
        echo "more robust than absolute numbers here since load pressure hits all engines"
        echo "in the same process-scheduling environment, but this snapshot should still"
        echo "be treated as provisional. A rerun on a quiet box should supersede it.**"
        echo
    else
        echo "# pcrec cross-engine performance comparison"
        echo
        echo "Generated by \`tests/bench/compare/compare.sh\` on $DATE_ISO."
        echo
        echo "Box was quiet throughout generation (1-minute load $LOAD_1MIN_START at the"
        echo "start, $LOAD_1MIN at the end, both at or below this report's busy-box"
        echo "threshold of $LOAD_LIMIT -- same threshold tests/bench/run_bench.sh's"
        echo "LOADED/INCONCLUSIVE gate uses, cores/2 clamped"
        echo "to a floor of 2.0; load average $LOAD_AVG on $NPROC cores). Every timed"
        echo "measurement was pinned ($PIN_NOTE) and is the median of $BENCH_TRIALS"
        echo "trials (see the \`spread\` column below), so absolute MB/s and ns/call"
        echo "figures here should be trustworthy, not just the cross-engine ratios."
        echo
    fi
    echo "## Machine context"
    echo
    echo "| field | value |"
    echo "|---|---|"
    echo "| host | $HOSTNAME_STR |"
    echo "| cpu | $CPU_MODEL |"
    echo "| cores | $NPROC |"
    echo "| load average (1/5/15 min) | $LOAD_AVG |"
    echo "| busy-box verdict | $([ "$LOADED" = "1" ] && echo "LOADED (1-min start=$LOAD_1MIN_START end=$LOAD_1MIN, limit $LOAD_LIMIT)" || echo "quiet (1-min start=$LOAD_1MIN_START end=$LOAD_1MIN, limit $LOAD_LIMIT)") |"
    echo "| pinning | $PIN_NOTE (cpu $BENCH_CPU) |"
    echo "| trials per measurement | $BENCH_TRIALS (median reported, spread column = max/min) |"
    echo "| governor (cpu$BENCH_CPU) | $GOVERNOR |"
    echo "| turbo | $TURBO |"
    echo "| gcc | $GCC_VER |"
    echo "| pcre2 | $PCRE2_VERSION (JIT: $([ "$JIT_LIB_AVAILABLE" = "1" ] && echo available || echo unavailable)) |"
    echo "| python3 | $PY_VER |"
    echo
    echo "## Case matrix"
    echo
    echo "| case | pattern | description | verdict |"
    echo "|---|---|---|---|"
    for id in "${CASE_IDS[@]}"; do
        local_verdict="${CASE_VALID[$id]:-error}"
        case "$local_verdict" in
            valid)
                local_verdict="VALID (${CASE_REF_VERDICT[$id]:-})"
                [ -n "${CASE_REASON[$id]:-}" ] && local_verdict="$local_verdict -- note: ${CASE_REASON[$id]}"
                ;;
            invalid) local_verdict="**INVALID**: ${CASE_REASON[$id]}" ;;
            unverified) local_verdict="**UNVERIFIED**: ${CASE_REF_VERDICT[$id]:-}; ${CASE_REASON[$id]:-}" ;;
            *) local_verdict="**ERROR**: ${CASE_REASON[$id]:-mechanical failure}" ;;
        esac
        printf '| %s | `%s` | %s | %s |\n' "$id" "${CASE_PATTERN[$id]}" "${CASE_DESC[$id]}" "$local_verdict"
    done
    echo
    echo "## Results"
    echo
    echo "\`ratio-vs-pcrec\` on the row equal to the best-other-engine reads as pcrec's"
    echo "speed multiple over the best non-pcrec engine for that case (throughput cases:"
    echo "pcrec MB/s / best-other MB/s; the one latency case, (i): best-other ns/call /"
    echo "pcrec ns/call). Values > 1 mean pcrec is faster. \`status=dnf\` means that"
    echo "engine did not finish within RUN_TIMEOUT (${RUN_TIMEOUT}s) and was not timed."
    echo "\`value\` is the MEDIAN of \`BENCH_TRIALS\` ($BENCH_TRIALS) independent, pinned"
    echo "trials; \`spread\` is that same trial set's max/min ratio -- a wide spread means"
    echo "the median is noisier than it looks, read it before trusting a close ratio."
    echo
    echo "| case | engine | status | bytes | iters | value | metric | ratio-vs-pcrec | spread |"
    echo "|---|---|---|---|---|---|---|---|---|"
    for row in "${ALL_ROWS[@]}"; do
        IFS=$'\t' read -r c e st b i s m v r sp <<<"$row"
        printf '| %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' "$c" "$e" "$st" "$b" "$i" "$v" "$m" "$r" "$sp"
    done
    echo
    echo "## Notes"
    echo
    echo "- Compile time is excluded from every measurement (pcrec pays it at build"
    echo "  time by design; PCRE2 JIT pays it once before the timed loop; see README.md)."
    echo "- Iteration counts are auto-scaled per engine so each timed measurement"
    echo "  accumulates at least ${TARGET_SECS}s of wall time."
    echo "- Every timed invocation is pinned ($PIN_NOTE) and repeated \`BENCH_TRIALS\`"
    echo "  ($BENCH_TRIALS) times with the engine order rotated per trial (trial i starts"
    echo "  at engine index i mod N, wraps around) so no one engine is always first;"
    echo "  reported values are the median, spread is that trial set's max/min ratio."
    echo "- INVALID cases were NOT timed (agreement check ran, timing did not)."
    if [ $invalid_count -gt 0 ]; then
        echo "- INVALID case detail:"
        for id in "${CASE_IDS[@]}"; do
            [ "${CASE_VALID[$id]:-}" = "invalid" ] && echo "  - case $id: ${CASE_REASON[$id]}"
        done
    fi
    if [ $unverified_count -gt 0 ]; then
        echo "- UNVERIFIED case detail (no oracle -- pcre2-interp or python-re -- returned"
        echo "  a verdict within RUN_TIMEOUT, so pcrec's own result could not be"
        echo "  cross-checked; it is still reported, standalone, below):"
        for id in "${CASE_IDS[@]}"; do
            [ "${CASE_VALID[$id]:-}" = "unverified" ] && echo "  - case $id: ${CASE_REASON[$id]}"
        done
    fi
    echo "- See tests/bench/compare/README.md for full methodology and fairness notes."
} > "$REPORT"

echo
echo "full report written to: $REPORT"

exit 0
