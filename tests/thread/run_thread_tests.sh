#!/usr/bin/env bash
# tests/thread/run_thread_tests.sh -- [TS-2]/[TS-3]: concurrency, under TSan.
#
# WHY THIS EXISTS. Every other suite in this repo runs single-threaded. The
# generated matcher's contract (lib/pcrec.h: "<prefix>_search(s, n, startpos,
# m) searches s[startpos..n)") never mentions threads, and pcrec_compile() is
# documented as self-contained -- but neither claim had ever been RUN
# concurrently under a race detector before this suite existed. It exists to
# establish both properties empirically rather than by reading the emitter or
# src/core/compile.c and trusting the design.
#
# WHAT IT CHECKS, in two parts:
#   [TS-2] N threads share ONE compiled matcher and call <prefix>_search()
#          on DIFFERENT subjects concurrently; every threaded result must
#          equal a single-threaded baseline recorded before any thread was
#          spawned. Five patterns are used, chosen to hit five differently
#          SHAPED emitted engines (see "WHY THESE FIVE PATTERNS" below) --
#          the property is about the GENERATED CODE, and a single pattern
#          would only ever exercise whichever engine shape it happens to
#          pick.
#   [TS-3] Eight threads, each pinned to its OWN pattern, call
#          pcrec_compile() concurrently; every threaded compile must
#          byte-match a single-threaded baseline (the emitted C for an
#          accepting pattern, or the diagnostic for a rejected one).
#
# Both are asserted under `-fsanitize=thread`, and both are validated by
# SABOTAGE (D15's rule, same as tests/bench): a race detector that has never
# caught a race is unvalidated. See "SABOTAGE VALIDATION" below -- each
# sabotage plants a genuine data race (a real, unsynchronized, shared
# counter) in a SCRATCH COPY of the driver / a src file, and this script
# fails itself if TSan does not report it.
#
# Usage: bash tests/thread/run_thread_tests.sh
# Env: PCREC (default <root>/build/pcrec, used black-box to generate the
#        five TS-2 fixtures; never itself run under TSan -- only the
#        GENERATED code and the library sources are instrumented)
#      CC (default gcc)
#      KEEP=1 (preserve the temp dir instead of deleting it on exit)
#      THREAD_TEST_TIMEOUT (default 60; per-binary wall-clock ceiling,
#        generous headroom for TSan's ~5-15x slowdown -- every one of these
#        binaries finishes in well under a second on this box, see below)
#      THREAD_TEST_ITERS (default 300 per thread for TS-2 and TS-3 alike;
#        modest but non-trivial -- 8 threads x 300 iters x up to 8 subjects
#        is thousands of concurrent calls into the shared matcher/compiler
#        per pattern/job, plenty for TSan to see real interleavings, and the
#        whole suite (5 TS-2 builds+runs, 1 TS-3 build+run, 2 sabotage
#        builds+runs) measures well under 30s on this box)
#
# WHY THESE FIVE PATTERNS (TS-2), each chosen to land on a DIFFERENT emitted
# engine shape (read from tests/base/ and tests/bench/, per this step's
# brief):
#   - '^abc$'               fully ^-anchored -- the `start_max = 0` fast
#                            path (tests/base/anchors.rxt; grep confirms
#                            `start_max = 0 /* fully ^-anchored */` in the
#                            emitted C).
#   - 'needleXYZW'           unanchored, memchr-prefiltered literal scan --
#                            tests/bench's THROUGHPUT case (a), the plain
#                            unanchored engine with no skip table at all.
#   - 'a.*|b$'               the `$`-EOL engine with the M2.12 skip/EOL-view
#                            interaction (tests/base/eol_scan_avoidance.rxt
#                            line 147 verbatim) -- D11's own regression
#                            class, a different code shape from a bare `$`.
#   - '=[^\n]*!'             self-loop SKIP STATES -- tests/bench's
#                            THROUGHPUT case (e) verbatim, chosen there
#                            because cases (a)-(d) all emit ZERO skip
#                            tables; confirmed here too (grep for `rx_forward_stay`
#                            in the emitted C, same table name the bench
#                            comment and tests/codegen both grep for).
#   - 'catfish|cat|dog'      the M2.8 alternation TRIE (tests/base/
#                            alternation_trie.rxt line 48 verbatim) --
#                            chain_alts/trie_build, a structurally
#                            different NFA shape from a straight DFA, and
#                            the subject "catfish" checks that leftmost-
#                            first branch order survives the trie (PCRE2
#                            semantics: 'catfish' is tried before 'cat',
#                            so "catfish" as input must match the FULL
#                            "catfish", not stop at "cat" -- verified by
#                            hand against this build before this script
#                            existed).
#
# WHY EIGHT JOBS (TS-3): six accepting patterns (varied shapes, again) plus
# two REJECTING patterns ('\d', '(?=a)'), so the concurrency claim also
# covers pcrec_compile()'s ctx_fail()/longjmp error path, not just its
# success path -- both use a stack-local Ctx and jmp_buf, so this should be
# equally race-free, and this is what makes that a checked fact rather than
# an assumption.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# D45: one shared generated-code compile budget. TS-2's two builds compile a
# GENERATED matcher and are wrapped; TS-3's build the LIBRARY (compiler axis,
# not emitted code) and keep their own timeouts.
#
# EXECUTION follows the same split: TS-2's driver runs a GENERATED matcher
# under TSan and goes through gen_run (which reads the axis off TSANFLAGS,
# defined below, so a TSan run gets the 60s sanitizer budget automatically).
# TS-3's driver calls pcrec_compile() directly -- the compiler itself, not
# emitted code -- so it keeps its own $TIMEOUT, same reasoning as its build.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="thread"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
TIMEOUT="${THREAD_TEST_TIMEOUT:-60}"
ITERS="${THREAD_TEST_ITERS:-300}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "thread: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- preflight: does this $CC support -fsanitize=thread at all? ----
# Loud SKIP, not a failure -- the same convention tests/registry/pcre2_check.c
# uses for a missing libpcre2-8-0 (see tests/CLAUDE.md PC-3): "clean" and
# "cannot be measured here" are different results (D14), and a stranger's box
# without TSan support must not read as this suite having found nothing wrong.
cat > "$WORKDIR/tsan_check.c" <<'EOF'
#include <pthread.h>
static int counter = 0;
static void *worker(void *arg) { (void)arg; counter++; return 0; }
int main(void) {
    pthread_t t1, t2;
    pthread_create(&t1, 0, worker, 0);
    pthread_create(&t2, 0, worker, 0);
    pthread_join(t1, 0);
    pthread_join(t2, 0);
    return 0;
}
EOF
if ! "$CC" -fsanitize=thread -g -O1 "$WORKDIR/tsan_check.c" -o "$WORKDIR/tsan_check" -lpthread 2>"$WORKDIR/tsan_check.log"; then
    echo "SKIP: $CC does not support -fsanitize=thread on this box -- tests/thread cannot run here." >&2
    echo "  compiler error:" >&2
    sed 's/^/  /' "$WORKDIR/tsan_check.log" >&2
    exit 0
fi

# ---- PCREC: black-box, used only to GENERATE C text for TS-2 fixtures.  ----
# Never itself run under TSan -- see the file header. Must already exist;
# this suite does not build it (never writes into build/, per the mandate).
if [ ! -x "$PCREC" ]; then
    bad "PCREC binary not found or not executable: $PCREC (run 'make' first, or set PCREC=)"
    echo
    echo "thread: 0 pass, 1 fail (setup failure, nothing else ran)" >&2
    exit 1
fi

TSANFLAGS="-fsanitize=thread -g -O1"
CFLAGS_COMMON="-std=gnu11 -Wall -Wextra"

# [M5-SEAM] FOUND, not enumerated by directory. This was a hand-listed set of
# five top-level directories, one glob deep, which is an assumption about the
# tree's SHAPE rather than about its contents: `src/gen/enc/` (the encoding
# backends) is two levels down and fell straight out of the TSan library the
# day it landed. Here the failure was loud (an undefined reference), but the
# same shape is how a concurrency check quietly ends up testing a library
# assembled from a different source set than the one that ships.
LIBSRCS=()
while IFS= read -r f; do
    LIBSRCS+=("$f")
done < <(find "$ROOT_DIR/src" -name '*.c' | sort)
if [ "${#LIBSRCS[@]}" -eq 0 ]; then
    bad "no compiler sources found under $ROOT_DIR/src -- the TSan library cannot be assembled"
    echo
    echo "thread: 0 pass, 1 fail (setup failure, nothing else ran)" >&2
    exit 1
fi

# ============================================================
# [TS-2] N threads, ONE compiled matcher, DIFFERENT subjects.
# ============================================================
echo "== [TS-2] generated-code concurrency, ${ITERS} iters/thread, 8 threads =="

# write_subjects <dir> <name> -- the per-pattern subject battery. Each list
# mixes match/no-match, boundary cases (empty string, match exactly at the
# start/end), and one longer buffer so a thread spends real time inside the
# engine rather than returning instantly -- more chance for TSan to see an
# actual interleaving, not just a scheduling no-op.
write_subjects() {
    local dir="$1" name="$2"
    case "$name" in
        anchored)
            cat > "$dir/subjects.inc" <<'EOF'
static const char *const subjects[] = {
    "abc", "xabc", "abcx", "ABC", "", "abcabc", "aabcc", "abc\n",
};
EOF
            ;;
        memchr)
            cat > "$dir/subjects.inc" <<'EOF'
static const char *const subjects[] = {
    "the needleXYZW is here", "no such thing", "needleXYZW",
    "needleXYZ only", "xneedleXYZWx", "", "NEEDLEXYZW", "needl",
};
EOF
            ;;
        eol)
            cat > "$dir/subjects.inc" <<'EOF'
static const char *const subjects[] = {
    "aXXXXX", "b", "xb", "xbx", "aaa\nbbb", "\nb", "",
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxb",
};
EOF
            ;;
        skip)
            cat > "$dir/subjects.inc" <<'EOF'
static const char *const subjects[] = {
    "key=value!", "=abc!", "=abcdef", "no equals here", "=!", "==!!", "",
    "key=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!",
};
EOF
            ;;
        trie)
            cat > "$dir/subjects.inc" <<'EOF'
static const char *const subjects[] = {
    "cat", "catfish", "dog", "cats", "the dog and cat", "banana", "",
    "there is a catfish in the pond somewhere near the dog house",
};
EOF
            ;;
    esac
}

TS2_NAMES=(anchored memchr eol skip trie)
TS2_PATTERNS=('^abc$' 'needleXYZW' 'a.*|b$' '=[^\n]*!' 'catfish|cat|dog')

ts2_ok=0
for idx in "${!TS2_NAMES[@]}"; do
    name="${TS2_NAMES[$idx]}"
    pattern="${TS2_PATTERNS[$idx]}"
    dir="$WORKDIR/ts2_$name"
    mkdir -p "$dir"

    perr="$(timeout "$TIMEOUT" "$PCREC" -p rx -o "$dir/gen.c" -- "$pattern" 2>&1 >/dev/null)"
    if [ $? -ne 0 ]; then
        bad "TS-2 '$name': pcrec failed to compile pattern '$pattern': $perr"
        continue
    fi

    write_subjects "$dir" "$name"

    # The skip-table pattern must actually emit one, or it silently degrades
    # into re-measuring the same shape as the memchr case (the same trap
    # tests/bench's CLAUDE.md documents for its own case (e)).
    if [ "$name" = "skip" ] && ! grep -q 'rx_forward_stay[0-9]*\[256\]' "$dir/gen.c"; then
        bad "TS-2 'skip': pattern '$pattern' emitted NO forward skip table -- this case can no longer test self-loop skip states under concurrency, which is the only thing it is for"
        continue
    fi

    # D45: the shared budget, not a local 60. TSANFLAGS carries -fsanitize=,
    # so gen_timeout_secs reports the SANITIZER budget here automatically.
    gen_cc "TS-2 '$name'" "$CC" $TSANFLAGS $CFLAGS_COMMON -I"$dir" \
        -o "$dir/ts2" "$SCRIPT_DIR/ts2_driver.c" "$dir/gen.c" -lpthread
    berr_rc=$?; berr="$GEN_CC_LOG"
    if [ "$berr_rc" -ne 0 ]; then
        bad "TS-2 '$name': $CC failed to build the TSan driver: $berr"
        continue
    fi

    out="$(gen_run "TS-2 '$name'" "$dir/ts2" 8 "$ITERS" 2>&1)"; rc=$?
    if echo "$out" | grep -q "WARNING: ThreadSanitizer"; then
        bad "TS-2 '$name' ($pattern): ThreadSanitizer reported a race -- see output below"
        echo "$out" >&2
        continue
    fi
    if [ "$rc" -ge 124 ]; then
        bad "TS-2 '$name' ($pattern): timed out (rc=$rc)"
        continue
    fi
    if [ "$rc" -ne 0 ]; then
        bad "TS-2 '$name' ($pattern): driver exited $rc: $out"
        continue
    fi
    case "$out" in
        *"mismatches=0"*) ;;
        *) bad "TS-2 '$name' ($pattern): threaded run disagreed with the single-threaded baseline: $out"
           continue ;;
    esac
    ts2_ok=$((ts2_ok + 1))
    ok "TS-2 '$name' ($pattern): $out"
done

# ============================================================
# [TS-3] 8 threads, EACH its own pattern, concurrent pcrec_compile().
# ============================================================
echo
echo "== [TS-3] library concurrency, ${ITERS} iters/thread, 8 threads x 8 patterns =="

ts3_dir="$WORKDIR/ts3"
mkdir -p "$ts3_dir"
berr="$(timeout 120 "$CC" $TSANFLAGS $CFLAGS_COMMON -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
    -o "$ts3_dir/ts3" "$SCRIPT_DIR/ts3_driver.c" "${LIBSRCS[@]}" -lpthread 2>&1)"
if [ $? -ne 0 ]; then
    bad "TS-3: $CC failed to build the TSan library+driver: $berr"
else
    out="$(timeout "$TIMEOUT" "$ts3_dir/ts3" "$ITERS" 2>&1)"; rc=$?
    if echo "$out" | grep -q "WARNING: ThreadSanitizer"; then
        bad "TS-3: ThreadSanitizer reported a race -- see output below"
        echo "$out" >&2
    elif [ "$rc" -ge 124 ]; then
        bad "TS-3: timed out (rc=$rc)"
    elif [ "$rc" -ne 0 ]; then
        bad "TS-3: driver exited $rc: $out"
    else
        case "$out" in
            *"mismatches=0"*) ok "TS-3: $out" ;;
            *) bad "TS-3: a threaded compile disagreed with its single-threaded baseline: $out" ;;
        esac
    fi
fi

# ============================================================
# SABOTAGE VALIDATION -- a race detector that never caught a race is
# unvalidated (D15's rule, applied here as it is throughout tests/bench).
# Both sabotages plant a REAL, unsynchronized, shared write and require
# ThreadSanitizer to report it; if it does not, that is a FAILURE of this
# suite's own credibility, not a shrug.
# ============================================================
echo
echo "== sabotage validation (proves TSan is actually watching) =="

# ---- TS-2 sabotage: a shared global counter, incremented by every thread
# on every call, with no synchronization at all. This is NOT the same bug
# class TS-2 exists to rule out in the GENERATED code (that code has no
# mutable globals to begin with) -- it is a controlled positive: proof that
# if a race like this ever existed anywhere in the instrumented binary,
# this exact build-and-run recipe would surface it.
sab_dir="$WORKDIR/sabotage_ts2"
mkdir -p "$sab_dir"
sed \
    -e '/^typedef struct {$/,/^} ThreadArg;$/{
        /^typedef struct {$/i\
static long g_calls = 0;  /* SABOTAGE: shared, unsynchronized, incremented every call */
    }' \
    -e 's/int found = rx_search((const unsigned char \*)subjects\[i\], n, 0, caps);/int found = rx_search((const unsigned char *)subjects[i], n, 0, caps);\n            g_calls++;  \/* SABOTAGE: unsynchronized write from every thread *\//' \
    "$SCRIPT_DIR/ts2_driver.c" > "$sab_dir/ts2_driver_sabotaged.c"

nmarks=$(grep -c "SABOTAGE" "$sab_dir/ts2_driver_sabotaged.c")
if [ "$nmarks" -ne 2 ]; then
    bad "TS-2 sabotage: the sed patch did not apply as expected ($nmarks/2 markers) -- ts2_driver.c's shape changed and this sabotage needs updating, so it proves nothing this run"
else
    # reuse the 'anchored' fixture's gen.c -- any of the five would do
    gen_cc "TS-2 sabotage" "$CC" $TSANFLAGS $CFLAGS_COMMON -I"$WORKDIR/ts2_anchored" \
        -o "$sab_dir/ts2_sab" "$sab_dir/ts2_driver_sabotaged.c" "$WORKDIR/ts2_anchored/gen.c" -lpthread
    berr_rc=$?; berr="$GEN_CC_LOG"
    if [ "$berr_rc" -ne 0 ]; then
        bad "TS-2 sabotage: $CC failed to build the sabotaged driver: $berr"
    else
        sab_out="$(TSAN_OPTIONS="halt_on_error=1" gen_run "TS-2 sabotage" "$sab_dir/ts2_sab" 8 "$ITERS" 2>&1)"
        if echo "$sab_out" | grep -q "SUMMARY: ThreadSanitizer: data race.*ts2_driver_sabotaged\.c"; then
            ok "TS-2 sabotage: TSan caught the planted race -- $(echo "$sab_out" | grep "SUMMARY: ThreadSanitizer")"
        else
            bad "TS-2 sabotage: TSan did NOT report the planted race -- the harness would not have caught a real one either. Output: $sab_out"
        fi
    fi
fi

# ---- TS-3 sabotage: a genuine COPY of src/core/compile.c with a file-scope
# static counter added and incremented, unsynchronized, on every call --
# exactly the shape TS-3's own header comment says it guards against ("a
# future file-scope counter or cache in the compiler").
sab_src_dir="$WORKDIR/sabotage_ts3_src"
mkdir -p "$sab_src_dir"
cp "$ROOT_DIR/src/core/compile.c" "$sab_src_dir/compile.c"
python3 - "$sab_src_dir/compile.c" <<'PYEOF'
import sys
p = sys.argv[1]
s = open(p).read()
marker = "int pcrec_compile(const char *pattern, const pcrec_options *opt,\n                  pcrec_output *out, pcrec_error *err)\n{"
if marker not in s:
    print("MARKER_NOT_FOUND")
    sys.exit(1)
s = s.replace(
    marker,
    "static int g_compile_calls = 0;  /* SABOTAGE: file-scope counter, unsynchronized */\n\n" + marker +
    "\n    g_compile_calls++;  /* SABOTAGE: unsynchronized write from every caller */"
)
open(p, "w").write(s)
PYEOF
if [ $? -ne 0 ]; then
    bad "TS-3 sabotage: src/core/compile.c's pcrec_compile() signature has changed and the sabotage patch no longer applies -- this sabotage needs updating, so it proves nothing this run"
else
    nmarks=$(grep -c "SABOTAGE" "$sab_src_dir/compile.c")
    if [ "$nmarks" -ne 2 ]; then
        bad "TS-3 sabotage: expected 2 SABOTAGE markers in the patched copy, found $nmarks"
    else
        sab3_dir="$WORKDIR/sabotage_ts3"
        mkdir -p "$sab3_dir"
        SAB_LIBSRCS=()
        for f in "${LIBSRCS[@]}"; do
            case "$f" in
                */src/core/compile.c) ;;   # replaced by the sabotaged copy
                *) SAB_LIBSRCS+=("$f") ;;
            esac
        done
        SAB_LIBSRCS+=("$sab_src_dir/compile.c")
        berr="$(timeout 120 "$CC" $TSANFLAGS $CFLAGS_COMMON -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
            -o "$sab3_dir/ts3_sab" "$SCRIPT_DIR/ts3_driver.c" "${SAB_LIBSRCS[@]}" -lpthread 2>&1)"
        if [ $? -ne 0 ]; then
            bad "TS-3 sabotage: $CC failed to build the sabotaged library+driver: $berr"
        else
            sab_out="$(TSAN_OPTIONS="halt_on_error=1" timeout "$TIMEOUT" "$sab3_dir/ts3_sab" "$ITERS" 2>&1)"
            if echo "$sab_out" | grep -q "SUMMARY: ThreadSanitizer: data race.*compile\.c.*pcrec_compile"; then
                ok "TS-3 sabotage: TSan caught the planted race -- $(echo "$sab_out" | grep "SUMMARY: ThreadSanitizer")"
            else
                bad "TS-3 sabotage: TSan did NOT report the planted race -- the harness would not have caught a real one either. Output: $sab_out"
            fi
        fi
    fi
fi

echo
echo "thread: $pass pass, $fail fail (TS-2 patterns: $ts2_ok/${#TS2_NAMES[@]})"
[ "$fail" -eq 0 ]
