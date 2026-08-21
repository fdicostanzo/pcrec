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
# THE BUDGET IS CPU-PRIMARY WITH A WALL BACKSTOP (Frank, 2026-08-16,
# twenty-fifth session; D45 third addendum). The original wall-only budget
# measured the wrong clock: tests/base/k18_cost_gates.rxt's 6,433-line
# artifact needs a MEASURED 2.53 s of CPU whether the box is quiet or not,
# but under `make -j12` contention its WALL time crossed the then-5 s budget
# and flaked a battery — the work didn't change, the scheduling did. So:
#
#   - gen_cpu_secs: CPU-time budget, 10 s plain / 60 s sanitizer
#     (GENCPU/GENCPU_SAN) — the PRIMARY bound. CPU is load-RESILIENT, not
#     perfectly load-independent: contention inflates cycles-per-
#     instruction, MEASURED on the k18_cost_gates artifact at 2.53 s CPU
#     quiet -> 3.52 s under 11 register-spinners -> >5 s under a real
#     `make -j12` gcc mix (memory-subsystem thrash; that >2x inflation
#     failed the first 5 s CPU default in battery). 10 s is ~4x the quiet
#     cost and ~2x the worst real-contended measurement — far tighter than
#     any wall bound can safely sit, because wall stretches WITHOUT BOUND
#     under load while CPU inflation tops out near 2x. A pathological
#     compile still dies after 10 s of actual work no matter the load.
#     Frank's original calibration ("maybe 5s") was right — it was
#     attached to the wrong clock. INTEGER seconds (RLIMIT_CPU is).
#     One shared pair for compiles AND matcher runs; if the two ever need
#     different CPU budgets, split the knob WITH the measurement.
#   - gen_timeout_secs: wall-clock BACKSTOP, 60 s plain / 180 s sanitizer
#     (GENTIMEOUT/GENTIMEOUT_SAN). CPU cannot see a process that is stuck
#     WITHOUT working (blocked on I/O, deadlocked — burns no CPU), so wall
#     stays, loose. It must sit ABOVE the CPU budget times the worst
#     plausible contention factor, or a working-but-contended process hits
#     the wall first and the verdict lies about which failure happened
#     (hence 180 on the sanitizer axis, 3x its 60 s CPU budget).
#
# Two bounds, two failure classes, two diagnoses — the step-budget /
# frame-capacity precedent (engine_m4.md par.4.5) applied to the harness
# itself. Sanitizer instrumentation is legitimately several times slower
# (MEASURED: UBSan 4.5x plain on the bounded-repeat shape — docs/testing.md
# has the curve). All env-overridable; D45's revisit-when is explicit: if a
# LEGITIMATE artifact is measured needing more, raise the default WITH the
# measurement recorded, never silently. (History: plain wall was 5 s from
# the ruling, 10 s briefly on 2026-08-16 when the k18_cost_gates flake
# first fired the revisit-when — superseded the same day by CPU-primary.)
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
        *-fsanitize=*) printf '%s\n' "${GENTIMEOUT_SAN:-180}" ;;
        *)             printf '%s\n' "${GENTIMEOUT:-60}" ;;
    esac
}

# gen_cpu_secs — the CPU-time budget (the PRIMARY bound; see the header) for
# one generated-code compile or one matcher execution, on the current axis.
gen_cpu_secs() {
    case " ${GENCFLAGS:-} ${CFLAGS:-} ${TSANFLAGS:-} ${SANFLAGS:-} " in
        *-fsanitize=*) printf '%s\n' "${GENCPU_SAN:-60}" ;;
        *)             printf '%s\n' "${GENCPU:-10}" ;;
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

# _gen_cc_run <compiler> <argv...> — [TT-3] the ccache-cacheability shape fix.
#
# WHY THIS EXISTS. ccache cannot cache a combined compile-AND-link invocation
# (a .c source with -o and no -c): it only recognizes the single
# preprocess-and-compile-to-one-object shape. Nearly every gen_cc call site in
# this tree passes one or more .c sources straight to `-o <binary>` in ONE
# gcc invocation (compile driver.c/gen.c and link in the same command), which
# is exactly the shape ccache passes through uncached — MEASURED 2026-08-21:
# only 540/5466 compile calls were cacheable under a naive PATH-masquerade
# wiring (build/battery_union2.log). This function is the SINGLE place that
# reshapes the call: split each .c source into its own `-c` compile (the
# shape ccache caches), then link the resulting objects — same inputs, same
# compiler, same flags, same final artifact, different invocation SHAPE.
#
# GATED on CCACHE=1 (house style, same shape as LINTGEN above): when unset
# (the default), this is byte-for-byte the original one-shot call — no shape
# change, no ccache dependency, nothing about a plain `make test` differs.
# A call that already passes `-c` (pc4's split-by-hand, the D45 controls, the
# codegen multi-engine fixture) is already the cacheable shape and is left
# untouched either way.
_gen_cc_run() {
    local cc="$1"
    shift
    if [ "${CCACHE:-0}" != "1" ]; then
        "$cc" "$@"
        return $?
    fi
    local a has_c=0
    for a in "$@"; do
        if [ "$a" = "-c" ]; then has_c=1; break; fi
    done
    if [ "$has_c" -eq 1 ]; then
        "$cc" "$@"
        return $?
    fi
    local out="" flags=() csrcs=()
    local args=("$@") n i
    n=${#args[@]}
    i=0
    while [ "$i" -lt "$n" ]; do
        a="${args[$i]}"
        if [ "$a" = "-o" ] && [ -z "$out" ]; then
            out="${args[$((i + 1))]}"
            i=$((i + 2))
            continue
        fi
        case "$a" in
            *.c) csrcs+=("$a") ;;
            *) flags+=("$a") ;;
        esac
        i=$((i + 1))
    done
    # Safety net: not the compile+link shape this split understands (no -o,
    # or no .c sources at all — e.g. linking pre-built .o's) — run the
    # original call rather than guess at a reshaping.
    if [ -z "$out" ] || [ "${#csrcs[@]}" -eq 0 ]; then
        "$cc" "$@"
        return $?
    fi
    local tmp objs=() rc=0 src ob
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/gen_cc_split.XXXXXX")" || return 1
    for src in "${csrcs[@]}"; do
        ob="$tmp/$(basename "$src" .c).o"
        "$cc" "${flags[@]}" -c -o "$ob" "$src"
        rc=$?
        if [ "$rc" -ne 0 ]; then
            rm -rf "$tmp"
            return "$rc"
        fi
        objs+=("$ob")
    done
    "$cc" "${flags[@]}" -o "$out" "${objs[@]}"
    rc=$?
    rm -rf "$tmp"
    return "$rc"
}
export -f _gen_cc_run

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
    local cpu wall rc
    cpu="$(gen_cpu_secs)"
    wall="$(gen_timeout_secs)"
    # RLIMIT_CPU soft-only (hard raised as an escalation backstop, failure
    # ignored): at the soft limit the kernel delivers SIGXCPU, which gcc's
    # driver reports as "CPU time limit exceeded signal terminated program
    # cc1" (MEASURED) — textually distinct from an OOM-kill's "Killed
    # signal", so a CPU breach never masquerades as a crash or vice versa.
    # Soft=hard would escalate straight to SIGKILL and destroy exactly that
    # distinction. The rlimit is per-process, not per-tree; the pathology
    # class is one cc1 grinding, and cc1 gets its own bounded counter.
    # The whole split sequence (compile, compile, ..., link when CCACHE=1)
    # runs under the SAME budget as the original one-shot call — ccache
    # makes a hit near-instant, so the sum comfortably fits, and a real
    # miss on every source is still bounded by the same numbers a plain
    # compile was bounded by.
    GEN_CC_LOG="$(timeout "$wall" bash -c \
        'ulimit -S -t "$1" 2>/dev/null; ulimit -H -t $(($1 + 30)) 2>/dev/null; shift; _gen_cc_run "$@"' \
        _ "$cpu" "$@" 2>&1)"
    rc=$?
    if [ "$rc" -eq 152 ] || printf '%s' "$GEN_CC_LOG" | grep -q 'CPU time limit exceeded'; then
        GEN_CC_LOG="D45 CPU BUDGET: compiling generated C for [$what] exceeded ${cpu}s of CPU time.
  This is a FAILURE, not a slow box (docs/dev/decisions.md D45): CPU time is
  load-independent, so this compile genuinely NEEDS more than ${cpu}s of work —
  a compile-time regression in the emitter or a pathological emitted shape.
  Reproduce:  $*
  If the artifact legitimately needs more, raise the budget with the
  measurement recorded in docs/testing.md -- GENCPU (plain, now ${GENCPU:-10}s)
  or GENCPU_SAN (sanitizer axes, now ${GENCPU_SAN:-60}s).
  Compiler output was:
$GEN_CC_LOG"
        [ "$rc" -ne 0 ] || rc=1
    elif [ "$rc" -eq 124 ]; then
        GEN_CC_LOG="D45 WALL BACKSTOP: compiling generated C for [$what] exceeded ${wall}s of
  wall time WITHOUT exceeding ${cpu}s of CPU — it was STUCK, not working
  (blocked, deadlocked, or swapping; a compile doing too much work is killed
  by the CPU budget first). Investigate what it was waiting on, not how big
  the artifact is.
  Reproduce:  $*
  Overrides: GENTIMEOUT (plain, now ${GENTIMEOUT:-60}s) / GENTIMEOUT_SAN
  (sanitizer axes, now ${GENTIMEOUT_SAN:-180}s)."
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
#
# SINCE THE CPU-PRIMARY ruling (see the header), this wall number plays two
# roles: (a) gen_run's wall BACKSTOP behind the gen_cpu_secs primary — kept
# TIGHT (not 60/180 like the compile backstop) because legitimate runs are
# three orders of magnitude below it, and a tight backstop bounds the waste
# from a stuck run; the cost is that a SPINNER under >2x contention can hit
# wall before CPU and draw verdict=timeout instead of cpukill, which the log
# line's own cpu= field disambiguates at a glance; (b) the SOLE bound at
# cheap-shape inner-loop sites (harness cells, vm_oracle/fuzz run loops),
# which have no CPU limit — fine, because their legit costs never approach
# it, so the contention-flake geometry that bit the compile budget cannot
# arise there.
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
        -l "$what" -c "$(gen_cpu_secs)" -s "$(gen_run_secs)" -m "${GENRUNMEM:-512m}" \
        -L "${WATCHDOG_LOG:-$GEN_LIB_ROOT/build/watchdog.log}" -- "$@"
}

# Runnable as a command so NON-SHELL suites get the same number from the same
# file rather than re-deriving the rule:  bash tests/lib/gen_timeout.sh secs
if [ "${1:-}" = "secs" ]; then gen_timeout_secs; fi
if [ "${1:-}" = "runsecs" ]; then gen_run_secs; fi
if [ "${1:-}" = "cpusecs" ]; then gen_cpu_secs; fi
