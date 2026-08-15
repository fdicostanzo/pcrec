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
b_plain="$(GENCFLAGS='-O1 -std=gnu11' gen_timeout_secs)"
b_san="$(GENCFLAGS='-O1 -fsanitize=undefined' gen_timeout_secs)"
b_tsan="$(GENCFLAGS='' TSANFLAGS='-fsanitize=thread' gen_timeout_secs)"
b_env="$(GENTIMEOUT=9 GENCFLAGS='-O1' gen_timeout_secs)"
b_envs="$(GENTIMEOUT_SAN=99 GENCFLAGS='-fsanitize=address' gen_timeout_secs)"
if [ "$b_plain" = "5" ] && [ "$b_san" = "60" ] && [ "$b_tsan" = "60" ]; then
    ok "D45 budgets: 5s plain, 60s sanitizer, and the axis is read from the FLAGS (GENCFLAGS or TSANFLAGS), so a site never has to declare which axis it is on"
else
    bad "D45 budgets wrong: plain=$b_plain san=$b_san tsan=$b_tsan (expected 5/60/60)"
fi
if [ "$b_env" = "9" ] && [ "$b_envs" = "99" ]; then
    ok "D45 budgets: GENTIMEOUT / GENTIMEOUT_SAN override, per the ruling's slow-box escape"
else
    bad "D45 env overrides wrong: GENTIMEOUT->$b_env GENTIMEOUT_SAN->$b_envs"
fi

# ---- 2. the wrapper FIRES, and says so ----------------------------------
#
# A real artifact, deliberately near the compiler-side cap, under a
# deliberately tiny budget. Using a real one matters: a `sleep` stub would
# prove `timeout` works, not that this wrapper is wired into a compile.
mkdir -p "$WORKDIR/slow"
if ! "$PCREC" -p rx -o "$WORKDIR/slow/gen.c" -- '((a)|b){0,64}c' >/dev/null 2>&1; then
    bad "gen-timeout: could not build the positive-control artifact"
else
    if GENTIMEOUT=1 GENCFLAGS='-O2 -std=gnu11' \
       gen_cc "the positive control" "$CC" -O2 -std=gnu11 -c -o /dev/null "$WORKDIR/slow/gen.c"; then
        bad "gen-timeout: a compile that must exceed a 1s budget returned SUCCESS — the wrapper is not applying the timeout"
    else
        rc=$?
        if [ "$rc" -ne 124 ]; then
            bad "gen-timeout: the over-budget compile returned $rc, not 124 (timeout); the caller cannot tell a timeout from a crash"
        elif printf '%s' "$GEN_CC_LOG" | grep -q 'D45 TIMEOUT' \
             && printf '%s' "$GEN_CC_LOG" | grep -q 'the positive control' \
             && printf '%s' "$GEN_CC_LOG" | grep -q 'GENTIMEOUT'; then
            ok "gen-timeout: an over-budget compile FAILS with 124 and a diagnostic naming the case and the override (never a hang, never a silent skip)"
        else
            bad "gen-timeout: fired, but the diagnostic does not name the case and the override: $GEN_CC_LOG"
        fi
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
         tests/thread/run_thread_tests.sh; do
    grep -q 'gen_timeout\.sh' "$ROOT_DIR/$f" || missing="$missing $f"
done
if [ -z "$missing" ]; then
    ok "D45 coverage: all 7 shell suites that compile generated C source the shared helper"
else
    bad "D45 coverage: these compile generated C but do not source tests/lib/gen_timeout.sh:$missing"
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
