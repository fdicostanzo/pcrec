#!/usr/bin/env bash
# tests/lib/run_gen_timeout_tests.sh — D45's own checks.
#
# D45 makes every compile of generated C run under a budget and makes exceeding
# it a loud FAILURE. That is a property of the TEST INFRASTRUCTURE, which means
# nothing else in the tree can see it: if the wrapper silently stopped applying
# the timeout, every suite would keep passing and the next pathological
# artifact would hang a battery for hours again — which is exactly what
# happened before the ruling, and exactly the shape tests/codegen exists to
# guard against for optimizations ("could be disabled with zero signal").
#
# So the wrapper gets a positive control (it FIRES, loudly, naming the case)
# and a COVERAGE assertion (every suite that compiles generated C actually
# routes through it). The second is the one that survives contact with future
# work: a new compile site added without the wrapper is the realistic way this
# protection erodes, and a grep is the only thing that notices.
#
# Usage: bash tests/lib/run_gen_timeout_tests.sh
# Env: CC, KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$ROOT_DIR/.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

. "$ROOT_DIR/tests/lib/gen_timeout.sh"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "gen-timeout: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- 1. the budget, per axis and per override ---------------------------
#
# Every scenario states its COMPLETE environment, all six variables, rather
# than setting the one it cares about and inheriting the rest.
#
# That is not tidiness. `gen_timeout_secs` reads GENCFLAGS, CFLAGS, SANFLAGS
# AND TSANFLAGS, so under `make ubsan`/`make asan` the ambient environment
# already carries `-fsanitize=` in several of them — and a "plain axis"
# scenario that sets only GENCFLAGS INHERITS THE VERY AXIS IT IS SIMULATING
# and reports 60 where it asserted 5. These checks failed exactly that way on
# the sanitizer legs of the composed battery while passing on the plain one: a
# unit check that reads its own ambient state is not a unit check.
#
# The checks BELOW this section deliberately do NOT do this — they compile real
# artifacts and should follow whichever axis the suite is actually running on.
axis() {   # axis <GENCFLAGS> <CFLAGS> <SANFLAGS> <TSANFLAGS> <GENTIMEOUT> <GENTIMEOUT_SAN>
    GENCFLAGS="$1" CFLAGS="$2" SANFLAGS="$3" TSANFLAGS="$4" \
    GENTIMEOUT="$5" GENTIMEOUT_SAN="$6" gen_timeout_secs
}
b_plain="$(axis '-O1 -std=gnu11' '' '' '' '' '')"
b_gen="$(axis '-O1 -fsanitize=undefined' '' '' '' '' '')"
b_cf="$(axis '-O1' '-fsanitize=address' '' '' '' '')"
b_san="$(axis '-O1' '' '-fsanitize=undefined' '' '' '')"
b_tsan="$(axis '-O1' '' '' '-fsanitize=thread' '' '')"
b_env="$(axis '-O1' '' '' '' 9 '')"
b_envs="$(axis '-fsanitize=address' '' '' '' '' 99)"
if [ "$b_plain" = "60" ] && [ "$b_gen" = "180" ] && [ "$b_cf" = "180" ] \
   && [ "$b_san" = "180" ] && [ "$b_tsan" = "180" ]; then
    ok "D45 wall BACKSTOP: 60s plain / 180s sanitizer (CPU-primary since 2026-08-16 — see gen_timeout.sh header), axis read from ANY of the four flag variables"
else
    bad "D45 wall backstop wrong: plain=$b_plain gencflags=$b_gen cflags=$b_cf sanflags=$b_san tsanflags=$b_tsan (expected 60/180/180/180/180)"
fi

# ---- 1a2. the CPU-PRIMARY budget (D45 third addendum, 2026-08-16) --------
caxis() {  # caxis <GENCFLAGS> <CFLAGS> <SANFLAGS> <TSANFLAGS> <GENCPU> <GENCPU_SAN>
    GENCFLAGS="$1" CFLAGS="$2" SANFLAGS="$3" TSANFLAGS="$4" \
    GENCPU="$5" GENCPU_SAN="$6" gen_cpu_secs
}
c_plain="$(caxis '-O1 -std=gnu11' '' '' '' '' '')"
c_cf="$(caxis '-O1' '-fsanitize=address' '' '' '' '')"
c_san="$(caxis '-O1' '' '-fsanitize=undefined' '' '' '')"
c_env="$(caxis '-O1' '' '' '' 2 '')"
c_envs="$(caxis '-fsanitize=address' '' '' '' '' 22)"
if [ "$c_plain" = "5" ] && [ "$c_cf" = "60" ] && [ "$c_san" = "60" ] \
   && [ "$c_env" = "2" ] && [ "$c_envs" = "22" ]; then
    ok "D45 CPU budget (the PRIMARY bound): 5s plain / 60s sanitizer, GENCPU/GENCPU_SAN overrides — load-independent, so it never flakes under -j"
else
    bad "D45 CPU budget wrong: plain=$c_plain cflags=$c_cf sanflags=$c_san env=$c_env envsan=$c_envs (expected 5/60/60/2/22)"
fi
if [ "$b_env" = "9" ] && [ "$b_envs" = "99" ]; then
    ok "D45 budgets: GENTIMEOUT / GENTIMEOUT_SAN override, per the ruling's slow-box escape"
else
    bad "D45 env overrides wrong: GENTIMEOUT->$b_env GENTIMEOUT_SAN->$b_envs"
fi

# ---- 1b. the same, for PCREC's OWN invocation (R23 V1) -------------------
#
# The harness's pcrec invocation carried a bare hardcoded `timeout 60` that
# did not scale with the axis, which is the gap the K18 rewrite folded into
# this file. Checked here for the reason section 1 exists at all: a budget
# nothing asserts is a budget that quietly becomes a literal again. Hermetic
# in the same way and for the same reason.
paxis() {  # paxis <GENCFLAGS> <CFLAGS> <SANFLAGS> <TSANFLAGS> <PCRECTIMEOUT> <PCRECTIMEOUT_SAN>
    GENCFLAGS="$1" CFLAGS="$2" SANFLAGS="$3" TSANFLAGS="$4" \
    PCRECTIMEOUT="$5" PCRECTIMEOUT_SAN="$6" pcrec_timeout_secs
}
p_plain="$(paxis '-O1 -std=gnu11' '' '' '' '' '')"
p_cf="$(paxis '-O1' '-fsanitize=address' '' '' '' '')"
p_san="$(paxis '-O1' '' '-fsanitize=undefined' '' '' '')"
p_env="$(paxis '-O1' '' '' '' 7 '')"
p_envs="$(paxis '-fsanitize=address' '' '' '' '' 77)"
if [ "$p_plain" = "20" ] && [ "$p_cf" = "60" ] && [ "$p_san" = "60" ] \
   && [ "$p_env" = "7" ] && [ "$p_envs" = "77" ]; then
    ok "R23 V1: pcrec's OWN invocation budget is axis-aware too (20s plain, 60s sanitizer, PCRECTIMEOUT/PCRECTIMEOUT_SAN overrides) — not the hardcoded 60 it used to carry"
else
    bad "pcrec budget wrong: plain=$p_plain cflags=$p_cf sanflags=$p_san env=$p_env envsan=$p_envs (expected 20/60/60/7/77)"
fi
if grep -qE 'timeout[ \t]+[0-9]+[ \t]+"\$PCREC"' "$ROOT_DIR/tests/harness/run.sh"; then
    bad "R23 V1: tests/harness/run.sh has gone back to a hand-rolled numeric timeout on pcrec's own invocation"
else
    ok "R23 V1: no hand-rolled numeric timeout remains on pcrec's own invocation in the harness"
fi
# ...and the same for the harness's per-cell MATCHER run, which carried a
# hardcoded `timeout 10` from before D45 (axis-blind: sanitizer cells shared
# the plain budget) until the twenty-fifth session routed it through
# gen_run_secs.
if grep -qE 'timeout[ \t]+[0-9]+[ \t]+"\$bdir/t"' "$ROOT_DIR/tests/harness/run.sh"; then
    bad "gen_run: tests/harness/run.sh has gone back to a hand-rolled numeric timeout on the per-cell matcher run"
else
    ok "gen_run: the harness's per-cell matcher run reads the shared run budget, not a hand-rolled number"
fi

# ---- 1c. the same, for EXECUTION of generated matchers (gen_run) ---------
#
# The twenty-fifth session's addition: D45 bounded every COMPILE and nothing
# bounded EXECUTION, so a merely-slow matcher read as a hang (nine battery
# minutes, 2026-08-15, tests/vm/CLAUDE.md). Same rule, same shape, same
# hermeticity reasoning as sections 1/1b.
raxis() {  # raxis <GENCFLAGS> <CFLAGS> <SANFLAGS> <TSANFLAGS> <GENRUNTIMEOUT> <GENRUNTIMEOUT_SAN>
    GENCFLAGS="$1" CFLAGS="$2" SANFLAGS="$3" TSANFLAGS="$4" \
    GENRUNTIMEOUT="$5" GENRUNTIMEOUT_SAN="$6" gen_run_secs
}
r_plain="$(raxis '-O1 -std=gnu11' '' '' '' '' '')"
r_cf="$(raxis '-O1' '-fsanitize=address' '' '' '' '')"
r_san="$(raxis '-O1' '' '-fsanitize=undefined' '' '' '')"
r_env="$(raxis '-O1' '' '' '' 3 '')"
r_envs="$(raxis '-fsanitize=address' '' '' '' '' 33)"
if [ "$r_plain" = "10" ] && [ "$r_cf" = "60" ] && [ "$r_san" = "60" ] \
   && [ "$r_env" = "3" ] && [ "$r_envs" = "33" ]; then
    ok "gen_run budgets: matcher EXECUTION is axis-aware too (10s plain, 60s sanitizer, GENRUNTIMEOUT/GENRUNTIMEOUT_SAN overrides)"
else
    bad "gen_run budgets wrong: plain=$r_plain cflags=$r_cf sanflags=$r_san env=$r_env envsan=$r_envs (expected 10/60/60/3/33)"
fi

# ---- 2. the wrapper FIRES, and says so ----------------------------------
#
# A real artifact, deliberately near the compiler-side cap, under a
# deliberately tiny budget. Using a real one matters: a `sleep` stub would
# prove `timeout` works, not that this wrapper is wired into a compile.
#
# HERMETIC for the same reason as section 1 — this scenario is "the plain axis
# with a 1s budget", and inheriting an ambient `-fsanitize=` would silently
# make the budget 60s and the compile succeed, turning a positive control into
# a vacuous pass on exactly the axes it most needs to hold.
mkdir -p "$WORKDIR/slow"
if ! "$PCREC" -p rx -o "$WORKDIR/slow/gen.c" -- '((a)|b){0,64}c' >/dev/null 2>&1; then
    bad "gen-timeout: could not build the positive-control artifact"
else
    # (a) CPU fire: a real compile that needs >1s of CPU, under GENCPU=1 with
    # a generous wall — the CPU budget must kill it and say CPU, not wall.
    # The rc is the gcc DRIVER's own report of cc1's SIGXCPU death (measured
    # 1 or 4 depending on how gcc words it), so the assertion is on the
    # diagnostic, plus rc != 124 (it must NOT read as a wall timeout).
    if GENCFLAGS='-O2 -std=gnu11' CFLAGS='' SANFLAGS='' TSANFLAGS='' \
       GENCPU=1 GENCPU_SAN='' GENTIMEOUT=60 GENTIMEOUT_SAN='' \
       gen_cc "the positive control" "$CC" -O2 -std=gnu11 -c -o /dev/null "$WORKDIR/slow/gen.c"; then
        bad "gen-timeout: a compile that must exceed a 1s CPU budget returned SUCCESS — the CPU limit is not being applied"
    else
        rc=$?
        if [ "$rc" -eq 124 ]; then
            bad "gen-timeout: the over-CPU-budget compile was reported as a WALL timeout (124) — the two bounds are confused"
        elif printf '%s' "$GEN_CC_LOG" | grep -q 'D45 CPU BUDGET' \
             && printf '%s' "$GEN_CC_LOG" | grep -q 'the positive control' \
             && printf '%s' "$GEN_CC_LOG" | grep -q 'GENCPU'; then
            ok "gen-timeout: an over-CPU-budget compile FAILS with a diagnostic naming the case, the CPU clock, and the override (never a hang)"
        else
            bad "gen-timeout: CPU control fired (rc=$rc) but the diagnostic is wrong: $GEN_CC_LOG"
        fi
    fi
    # (b) wall backstop WIRED: same real compile, GENTIMEOUT=1 with a
    # generous CPU budget — coreutils timeout must fire and the diagnostic
    # must say BACKSTOP. (A working compile hitting the backstop is the
    # verdict-mislabel geometry the defaults are sized to avoid; here it is
    # forced deliberately, as a WIRING control, because a genuinely blocked
    # compile cannot be staged with a real artifact.)
    if GENCFLAGS='-O2 -std=gnu11' CFLAGS='' SANFLAGS='' TSANFLAGS='' \
       GENCPU=999 GENCPU_SAN='' GENTIMEOUT=1 GENTIMEOUT_SAN='' \
       gen_cc "the backstop control" "$CC" -O2 -std=gnu11 -c -o /dev/null "$WORKDIR/slow/gen.c"; then
        bad "gen-timeout: a compile that must exceed a 1s wall backstop returned SUCCESS — the backstop is not wired"
    else
        rc=$?
        if [ "$rc" -ne 124 ]; then
            bad "gen-timeout: the backstop control returned $rc, not 124"
        elif printf '%s' "$GEN_CC_LOG" | grep -q 'D45 WALL BACKSTOP'; then
            ok "gen-timeout: the wall backstop is wired through a real compile and its diagnostic says BACKSTOP (stuck), not work"
        else
            bad "gen-timeout: backstop fired but the diagnostic is wrong: $GEN_CC_LOG"
        fi
    fi
fi

# ---- 2b. gen_run FIRES on a real over-budget RUN -------------------------
#
# A REAL generated matcher whose execution is budget-bound to a few seconds:
# `(a*)*b` under --engine=vm with a step budget sized so the run takes ~5 s
# NATURALLY (measured 4.6 s at --step-budget=400000000 on 'a'x200, ending in
# an honest err_steps) — so if the wrapper silently stopped killing, this
# control still terminates instead of hanging the section. A sleep stub would
# prove watchdog works (scripts/test_watchdog.sh already does); a real
# artifact proves the wrapper is WIRED into a matcher execution.
#
# There is deliberately NO memory-kill (122) sibling control here: a generated
# matcher is allocation-free by construction, so no real artifact can runaway
# on RSS — the 122 path's positive control lives in scripts/test_watchdog.sh
# (case 5), and gen_run adds only the budget selection this section covers.
mkdir -p "$WORKDIR/slowrun"
slow_subj="$(printf 'a%.0s' $(seq 200))"
if ! "$PCREC" -p rx --engine=vm --step-budget=400000000 \
        -o "$WORKDIR/slowrun/gen.c" -- '(a*)*b' >/dev/null 2>&1 \
   || ! gen_cc "the run positive control" "$CC" -O1 -std=gnu11 \
        -I "$WORKDIR/slowrun" -o "$WORKDIR/slowrun/t" \
        "$ROOT_DIR/tests/vm/vm_driver.c" "$WORKDIR/slowrun/gen.c"; then
    bad "gen-run: could not build the run positive-control artifact"
else
    # (a) CPU fire: the artifact spins CPU by construction, so under GENCPU=1
    # with a generous wall it must die by cpukill (123), not timeout.
    run_out="$(GENCFLAGS='-O1 -std=gnu11' CFLAGS='' SANFLAGS='' TSANFLAGS='' \
        GENCPU=1 GENCPU_SAN='' GENRUNTIMEOUT=30 GENRUNTIMEOUT_SAN='' \
        WATCHDOG_SECTION=gen-timeout WATCHDOG_LOG="$WORKDIR/wd.log" \
        gen_run "the run cpu control" "$WORKDIR/slowrun/t" "$slow_subj" 2>"$WORKDIR/wd.err")"
    rc=$?
    if [ "$rc" -ne 123 ]; then
        bad "gen-run: a run that must exceed a 1s CPU budget returned $rc, not 123 (output: '$run_out')"
    elif ! grep -q "verdict=cpukill" "$WORKDIR/wd.log" 2>/dev/null; then
        bad "gen-run: CPU control killed with 123 but the log verdict is not cpukill: $(tail -c 300 "$WORKDIR/wd.log" 2>/dev/null)"
    else
        ok "gen-run: an over-CPU-budget matcher EXECUTION is killed with 123 and verdict=cpukill — load-independent, a real artifact"
    fi
    # (b) wall fire: same artifact under GENRUNTIMEOUT=1 with a generous CPU
    # budget — the wall bound must fire with 124/verdict=timeout.
    run_out="$(GENCFLAGS='-O1 -std=gnu11' CFLAGS='' SANFLAGS='' TSANFLAGS='' \
        GENCPU=999 GENCPU_SAN='' GENRUNTIMEOUT=1 GENRUNTIMEOUT_SAN='' \
        WATCHDOG_SECTION=gen-timeout WATCHDOG_LOG="$WORKDIR/wd.log" \
        gen_run "the run positive control" "$WORKDIR/slowrun/t" "$slow_subj" 2>"$WORKDIR/wd.err")"
    rc=$?
    if [ "$rc" -ne 124 ]; then
        bad "gen-run: a run that must exceed a 1s wall budget returned $rc, not 124 — the wrapper is not applying the run timeout (output: '$run_out')"
    elif ! grep -q "verdict=timeout" "$WORKDIR/wd.log" 2>/dev/null \
         || ! grep -q "the run positive control" "$WORKDIR/wd.log" 2>/dev/null; then
        bad "gen-run: fired with 124 but the watchdog log line is missing or does not name the case: $(tail -c 300 "$WORKDIR/wd.log" 2>/dev/null)"
    else
        ok "gen-run: an over-wall-budget matcher EXECUTION is killed with 124 and a log line naming the case (never a hang) — a real artifact, budget-bound so the control terminates even if the wrapper breaks"
    fi
fi

# ...and an ordinary run is untouched, hermetically on the plain axis.
if [ -x "$WORKDIR/slowrun/t" ]; then
    fast_out="$(GENCFLAGS='-O1 -std=gnu11' CFLAGS='' SANFLAGS='' TSANFLAGS='' \
        GENRUNTIMEOUT='' GENRUNTIMEOUT_SAN='' \
        WATCHDOG_SECTION=gen-timeout WATCHDOG_LOG="$WORKDIR/wd.log" \
        gen_run "the run pass-through control" "$WORKDIR/slowrun/t" 'aaab')"
    fast_rc=$?
    # 'match 0 4 3 3' is oracle-verified: python re.match(r'(a*)*b','aaab')
    # gives span (0,4), span(1) (3,3) — the last (a*) iteration is empty.
    if [ "$fast_rc" -eq 0 ] && [ "$fast_out" = "match 0 4 3 3" ]; then
        ok "gen-run: an ordinary run passes through untouched (stdout intact, exit 0, inside the budget)"
    else
        bad "gen-run: ordinary run disturbed under the wrapper: rc=$fast_rc out='$fast_out'"
    fi
fi

# ---- 3. an ordinary failure is NOT reported as a timeout -----------------
#
# 124 is `timeout`'s status and is checked exactly. A compiler that fails to
# compile, segfaults, or is OOM-killed must pass its own status through, or the
# reader goes looking for a slow machine instead of the real fault -- and this
# tree HAS such a case: K7's `a{0,65535}` is SIGKILLed for memory.
printf 'this is not C\n' > "$WORKDIR/bad.c"
if gen_cc "a deliberate syntax error" "$CC" -c -o /dev/null "$WORKDIR/bad.c"; then
    bad "gen-timeout: a file that cannot compile returned SUCCESS"
elif [ "$?" -eq 124 ]; then
    bad "gen-timeout: an ordinary compile ERROR was reported as a timeout"
elif printf '%s' "$GEN_CC_LOG" | grep -qi 'error'; then
    ok "gen-timeout: an ordinary compile error passes the compiler's own status and output through, NOT a timeout"
else
    bad "gen-timeout: compile error lost the compiler's output: $GEN_CC_LOG"
fi

# ---- 4. a normal compile is untouched ------------------------------------
mkdir -p "$WORKDIR/fast"
if "$PCREC" -p rx -o "$WORKDIR/fast/gen.c" -- 'a(b|c)+d' >/dev/null 2>&1 \
   && gen_cc "a normal artifact" "$CC" -O1 -std=gnu11 -Wall -Wextra -Werror \
             -c -o /dev/null "$WORKDIR/fast/gen.c"; then
    ok "gen-timeout: an ordinary generated artifact compiles inside the budget with the wrapper in place"
else
    bad "gen-timeout: an ordinary artifact failed under the wrapper: $GEN_CC_LOG"
fi

# ---- 5. COVERAGE: every generated-C compile site routes through it -------
#
# The check that survives future work. D45 names the suites; this asserts each
# one actually sources the helper, so a compile site added later without it is
# caught here rather than by the next multi-hour hang.
missing=""
for f in tests/harness/run.sh tests/cli/run_cli_tests.sh \
         tests/codegen/run_codegen_tests.sh tests/codegen/run_ir_listing.sh \
         tests/vm/run_vm_tests.sh tests/registry/run_pc4.sh \
         tests/thread/run_thread_tests.sh tests/possessify/run_possdiff.sh; do
    grep -q 'gen_timeout\.sh' "$ROOT_DIR/$f" || missing="$missing $f"
done
if [ -z "$missing" ]; then
    ok "D45 coverage: all 8 shell suites that compile generated C source the shared helper"
else
    bad "D45 coverage: these compile generated C but do not source tests/lib/gen_timeout.sh:$missing"
fi
# EXECUTION coverage (twenty-fifth session): suites that RUN generated
# matchers route the run through gen_run (shell) or read the run budget from
# this file (python inner loops, where a per-run watchdog's startup cost
# would multiply the sweep's runtime — the number is shared even where the
# wrapper is not). This list grows as suites adopt the run bound; a suite
# listed here that drops the helper is caught the same way section 5's
# compile list catches it.
runmissing=""
for f in tests/vm/run_vm_tests.sh tests/possessify/run_possdiff.sh \
         tests/possessify/run_possessify_tests.sh tests/codegen/run_ir_listing.sh \
         tests/thread/run_thread_tests.sh tests/cli/run_cli_tests.sh \
         tests/registry/run_pc4.sh; do
    grep -q 'gen_run ' "$ROOT_DIR/$f" || runmissing="$runmissing $f"
done
grep -q 'runsecs' "$ROOT_DIR/tests/vm/vm_oracle.py" \
    || runmissing="$runmissing tests/vm/vm_oracle.py(runsecs)"
grep -q 'runsecs' "$ROOT_DIR/tests/fuzz/fuzz.py" \
    || runmissing="$runmissing tests/fuzz/fuzz.py(runsecs)"
if [ -z "$runmissing" ]; then
    ok "gen_run coverage: the wired suites route matcher EXECUTION through the shared run budget"
else
    bad "gen_run coverage: these no longer route matcher execution through the shared budget:$runmissing"
fi

# the two python suites take the SAME number from the SAME file rather than
# re-deriving the rule
pymissing=""
for f in tests/vm/vm_oracle.py tests/fuzz/fuzz.py; do
    grep -q 'gen_timeout\.sh' "$ROOT_DIR/$f" || pymissing="$pymissing $f"
done
if [ -z "$pymissing" ]; then
    ok "D45 coverage: both python suites read the budget from tests/lib/gen_timeout.sh (one rule, not one per language)"
else
    bad "D45 coverage: these python suites do not read the shared budget:$pymissing"
fi
# ...and no compile OF GENERATED CODE still carries a hand-rolled timeout,
# which is how the tree looked before D45: three different numbers in three
# files, none of them shared.
#
# The rule has to be precise about "generated", or it flags the wrong things.
# It did on its first run: tests/thread's TS-3 builds libpcrec ITSELF under
# TSan, which is compiler-axis code and outside D45's scope, and a broad grep
# called that a violation. So the scan joins backslash continuations and keeps
# only commands that actually name a generated source. tests/bench is excluded
# for a different and stronger reason: its timeouts ARE its measurement (it
# reports DNF against a compile-time budget), so replacing them with a shared
# one would delete the instrument.
stray="$(for f in $(find "$ROOT_DIR/tests" -name '*.sh' -not -path '*/bench/*'); do
    awk -v F="$f" '
        { line = line $0 }
        /\\$/ { sub(/\\$/, "", line); next }
        { if (line ~ /timeout[ \t]+[0-9]+[ \t]+"?\$\{?CC/ && line ~ /gen[a-z_]*\.c/)
              printf "%s: %s\n", F, substr(line, 1, 100)
          line = "" }
    ' "$f"
done)"
if [ -z "$stray" ]; then
    ok "D45: no compile of GENERATED code still carries a hand-rolled timeout (tests/bench excluded: its budgets ARE its measurement)"
else
    bad "D45: hand-rolled timeouts on generated-code compiles remain:
$stray"
fi

echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "gen-timeout: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
