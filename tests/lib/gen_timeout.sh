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

# Runnable as a command so NON-SHELL suites get the same number from the same
# file rather than re-deriving the rule:  bash tests/lib/gen_timeout.sh secs
if [ "${1:-}" = "secs" ]; then gen_timeout_secs; fi
