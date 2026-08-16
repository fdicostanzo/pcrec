# tests/lib/gen_timeout.sh — D45's ONE implementation of the generated-code
# compile budget. Sourced by every suite that compiles emitted C.
#
# D45 (docs/dev/decisions.md, Frank, 2026-08-15): "every compile of GENERATED
# code in the test infrastructure ... is wrapped in a timeout; exceeding it is
# a loud test FAILURE naming the case, never a hang and never a silent skip."
#
# WHY A BUDGET AT ALL. The ruling came out of a battery in which two cc1
# processes ground for 1h40m and 55m on one generated file, and the reason
# nobody noticed for that long is the point: an unbounded compile reads as
# "still running", never as "failed". A test suite with no compile bound
# cannot tell a slow machine from a hung one, so it reports neither.
#
# WHY THE NUMBERS. A normal generated-artifact compile is sub-second. Frank's
# calibration: "anything over 60 seconds is a failure ... and i'm being
# generous with 60s. maybe 5s". So 5s on the plain axes and 60s on the
# sanitizer axes, where instrumentation is legitimately several times slower
# (MEASURED on the bounded-repeat shape: UBSan is 4.5x plain at a size where
# both are fast, and diverges from there — docs/testing.md's battery section
# has the curve). Both env-overridable for a slow box, and D45's revisit-when
# is explicit: if a LEGITIMATE artifact is measured needing more, raise the
# default WITH the measurement recorded, never silently.
#
# WHY THE AXIS IS DETECTED RATHER THAN PASSED. Every call site already carries
# the axis in its flags — `-fsanitize=` is in GENCFLAGS (or CFLAGS, or
# TSANFLAGS) exactly when the compile is instrumented — so deriving the budget
# from the flags means no site has to remember to say which axis it is on, and
# a site added later gets the right budget for free. A second parameter would
# be a second thing to keep in sync with the first.

# gen_timeout_secs — the budget for the CURRENT axis, in seconds.
gen_timeout_secs() {
    case " ${GENCFLAGS:-} ${CFLAGS:-} ${TSANFLAGS:-} ${SANFLAGS:-} " in
        *-fsanitize=*) printf '%s\n' "${GENTIMEOUT_SAN:-60}" ;;
        *)             printf '%s\n' "${GENTIMEOUT:-5}" ;;
    esac
}

# pcrec_timeout_secs — the budget for ONE pcrec INVOCATION on the current axis.
#
# WHY THIS EXISTS SEPARATELY (R23 V1, the K18 design note's §5 item 12).
# tests/harness/run.sh wrapped pcrec's own invocation in a bare, hardcoded
# `timeout 60`. That predates D45 and sat OUTSIDE its mechanism: the budget
# above is derived from `-fsanitize=` in the flags of a GENERATED-CODE compile,
# and pcrec's own invocation passes no such flags — so the one compile a change
# to the compiler can actually slow down had the one budget that did not scale
# with the axis, and blowing it is scored HARNESS FAILURE rather than a graceful
# skip. K18's path-sensitive closure is exactly such a change, so it folds that
# timeout in here rather than leaving the gap documented as acceptable.
#
# WHY THESE NUMBERS, and they are NOT the generated-code ones. pcrec's own
# compiles are a different quantity: sub-millisecond for ordinary patterns, and
# MEASURED 2026-08-15 at 0.38 s plain / 0.84 s asan / 0.85 s ubsan for the
# worst case in the corpus — `tests/base/k18_deep_nesting.rxt`'s 250 nested
# nullable stars, which is the deepest nesting the parser will accept at all
# (PCREC_MAX_GROUP_DEPTH). 20 s and 60 s are ~50x and ~70x that, which is
# headroom for a slow box without being the "still running, not failed" hole
# D45 exists to close. Same revisit-when as above: if a LEGITIMATE pattern is
# measured needing more, raise the default WITH the measurement recorded.
pcrec_timeout_secs() {
    case " ${GENCFLAGS:-} ${CFLAGS:-} ${TSANFLAGS:-} ${SANFLAGS:-} " in
        *-fsanitize=*) printf '%s\n' "${PCRECTIMEOUT_SAN:-60}" ;;
        *)             printf '%s\n' "${PCRECTIMEOUT:-20}" ;;
    esac
}

# gen_cc <case-label> <compiler-argv...>
#
# Runs one compile of GENERATED C under the budget. Always leaves the
# compiler's combined output (or the timeout diagnostic) in $GEN_CC_LOG, so a
# caller reports the same way whichever happened.
#
#   0    compiled
#   124  TIMED OUT — $GEN_CC_LOG carries the D45 diagnostic, naming the case
#   n    the compiler's own status ($GEN_CC_LOG carries its output)
#
# 124 is `timeout`'s own exit status and is checked EXACTLY, not as ">= 124":
# a compiler that segfaults exits 139 and a compiler that is OOM-killed exits
# 137, and calling either of those a timeout would send the reader looking for
# a slow machine instead of a crash.
gen_cc() {
    local what="$1"
    shift
    local secs rc
    secs="$(gen_timeout_secs)"
    GEN_CC_LOG="$(timeout "$secs" "$@" 2>&1)"
    rc=$?
    if [ "$rc" -eq 124 ]; then
        GEN_CC_LOG="D45 TIMEOUT: compiling generated C for [$what] exceeded ${secs}s.
  This is a FAILURE, not a slow box (docs/dev/decisions.md D45): a normal
  generated-artifact compile is sub-second, so a compile this slow is a
  compile-time regression in the emitter or a pathological emitted shape.
  Reproduce:  $*
  If the artifact is legitimately this large, raise the budget with the
  measurement recorded in docs/testing.md -- GENTIMEOUT (plain, now ${GENTIMEOUT:-5}s)
  or GENTIMEOUT_SAN (sanitizer axes, now ${GENTIMEOUT_SAN:-60}s)."
    fi
    return $rc
}

# gen_run_secs — the budget for ONE EXECUTION of a generated matcher (or a
# driver binary built around one) on the current axis, in seconds.
#
# WHY THIS EXISTS (2026-08-16, twenty-fifth session; the gap is flagged in
# tests/vm/CLAUDE.md). D45 bounds every COMPILE of emitted C and nothing
# bounded its EXECUTION, so a matcher that is merely slow read as a hang for
# as long as it took — the [ENG-BREP] battery leg spent nine minutes that way
# on a run that was quadratic-and-correct. Same rule as D45: exceeding the
# budget is a loud FAILURE naming the case, never a hang, never a silent skip.
#
# WHY THE NUMBERS. A normal generated-matcher run is sub-millisecond;
# tests/harness/run.sh has bounded its per-cell runs at a flat 10 s since
# before D45 and nothing legitimate has ever approached it. 10 s plain keeps
# that calibration; 60 s on the sanitizer axes matches the D45 ratio
# (instrumentation is legitimately several times slower). Env-overridable,
# same revisit-when: a LEGITIMATE run measured needing more raises the
# default WITH the measurement recorded, never silently.
gen_run_secs() {
    case " ${GENCFLAGS:-} ${CFLAGS:-} ${TSANFLAGS:-} ${SANFLAGS:-} " in
        *-fsanitize=*) printf '%s\n' "${GENRUNTIMEOUT_SAN:-60}" ;;
        *)             printf '%s\n' "${GENRUNTIMEOUT:-10}" ;;
    esac
}

# gen_run <case-label> <argv...>
#
# Runs one generated-matcher execution under the budget above PLUS a memory
# ceiling, via scripts/watchdog (which see): wall timeout, peak-tree-RSS
# limit, and one log line per execution in build/watchdog.log (override:
# WATCHDOG_LOG). Suites set WATCHDOG_SECTION once so the label is findable
# among every other suite's lines. stdout/stderr pass through untouched —
# callers capture stdout exactly as they would running the binary bare.
#
#   0    ran to completion with status 0
#   124  TIMED OUT — a FAILURE (this file's rule), watchdog logged it
#   122  KILLED ON MEMORY — a FAILURE; generated matchers are allocation-free
#        by construction, so tree RSS beyond subject + driver overhead is a
#        runaway, not a big workload (default ceiling 512m: GENRUNMEM)
#   n    the binary's own status
#
# 124/122 are checked EXACTLY by callers, same reasoning as gen_cc: 139 is a
# crash and 137 an external OOM-kill, and either called "timeout" sends the
# reader hunting a slow box instead of a bug.
GEN_LIB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)"
gen_run() {
    local what="$1"
    shift
    "$GEN_LIB_ROOT/scripts/watchdog" \
        -l "$what" -s "$(gen_run_secs)" -m "${GENRUNMEM:-512m}" \
        -L "${WATCHDOG_LOG:-$GEN_LIB_ROOT/build/watchdog.log}" -- "$@"
}

# Runnable as a command so NON-SHELL suites get the same number from the same
# file rather than re-deriving the rule:  bash tests/lib/gen_timeout.sh secs
if [ "${1:-}" = "secs" ]; then gen_timeout_secs; fi
if [ "${1:-}" = "runsecs" ]; then gen_run_secs; fi
