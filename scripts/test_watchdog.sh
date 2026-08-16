#!/usr/bin/env bash
#
# test_watchdog.sh — standalone self-test for scripts/watchdog.
#
# Deliberately NOT wired into `make test` (a manager/Frank decision for
# later). Run directly:
#
#   timeout 300 scripts/test_watchdog.sh
#
# CRITICAL DESIGN RULE (project lesson): every test case here is bounded by
# coreutils `timeout`, NEVER by watchdog itself. A control must not share a
# mechanism with the thing it controls — if watchdog's own timeout logic
# were broken, a test that relied on watchdog to bound its own runtime
# could hang forever right alongside it, or silently "pass" for the wrong
# reason. Every case below that could hang is wrapped in an outer `timeout`
# that has nothing to do with the code under test.

set -u

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
WD="$SELF_DIR/watchdog"

SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/wd_test.XXXXXX")"
trap 'rm -rf "$SCRATCH"' EXIT

pass_count=0
fail_count=0

pass() {
    printf 'PASS: %s\n' "$1"
    pass_count=$((pass_count + 1))
}

fail() {
    printf 'FAIL: %s\n' "$1"
    fail_count=$((fail_count + 1))
}

log_has_keys() {
    # log_has_keys FILE : true if the last line has all required keys.
    local f="$1" line
    line="$(tail -n1 "$f")"
    for key in ts section label verdict wall cpu peak_rss_kb exit cmd; do
        case "$line" in
            *"$key="*) ;;
            *) return 1 ;;
        esac
    done
    return 0
}

log_verdict() {
    tail -n1 "$1" | grep -o 'verdict=[a-z-]*' | cut -d= -f2
}

log_peak_rss() {
    tail -n1 "$1" | grep -o 'peak_rss_kb=[0-9]*' | cut -d= -f2
}

# ---- case 1: exit pass-through ---------------------------------------------

log1="$SCRATCH/case1.log"
timeout 10 "$WD" -l case1 -L "$log1" -- bash -c 'exit 0'
rc=$?
if [ "$rc" -eq 0 ]; then pass "case1: exit 0 passes through"; else fail "case1: exit 0 -> got $rc"; fi

timeout 10 "$WD" -l case1b -L "$log1" -- bash -c 'exit 7'
rc=$?
if [ "$rc" -eq 7 ]; then pass "case1: exit 7 passes through"; else fail "case1: exit 7 -> got $rc"; fi

# ---- case 2: signal pass-through -------------------------------------------

log2="$SCRATCH/case2.log"
timeout 10 "$WD" -l case2 -L "$log2" -- bash -c 'kill -USR1 $$; sleep 5'
rc=$?
if [ "$rc" -eq 138 ]; then
    pass "case2: self-SIGUSR1 -> exit 138"
else
    fail "case2: self-SIGUSR1 -> got $rc, want 138"
fi

# ---- case 3: timeout kill ---------------------------------------------------

log3="$SCRATCH/case3.log"
pidfile3="$SCRATCH/case3.pid"
t0=$(date +%s)
timeout 10 "$WD" -l case3 -L "$log3" -s 1 -- sh -c 'echo $$ > '"$pidfile3"'; exec sleep 30'
rc=$?
t1=$(date +%s)
elapsed=$((t1 - t0))
ok=1
[ "$rc" -eq 124 ] || { ok=0; fail "case3: exit -> got $rc, want 124"; }
[ "$elapsed" -lt 5 ] || { ok=0; fail "case3: took ${elapsed}s, want <5s"; }
if [ -s "$pidfile3" ]; then
    victim="$(cat "$pidfile3")"
    if kill -0 "$victim" 2>/dev/null; then
        ok=0
        fail "case3: victim pid $victim still alive"
    fi
fi
[ "$ok" -eq 1 ] && pass "case3: -s 1 on sleep 30 -> 124, fast return, process gone"

# ---- case 4: tree kill -------------------------------------------------------

log4="$SCRATCH/case4.log"
pgidfile4="$SCRATCH/case4.pgid"
timeout 10 "$WD" -l case4 -L "$log4" -s 1 -- sh -c 'echo $$; sleep 30 & exec sleep 30' > "$pgidfile4"
rc=$?
ok=1
[ "$rc" -eq 124 ] || { ok=0; fail "case4: exit -> got $rc, want 124"; }
pgid4="$(head -n1 "$pgidfile4" 2>/dev/null)"
if [ -n "$pgid4" ]; then
    survivors="$(pgrep -g "$pgid4" 2>/dev/null)"
    if [ -n "$survivors" ]; then
        ok=0
        fail "case4: survivors in pgid $pgid4: $survivors"
    fi
else
    ok=0
    fail "case4: could not capture child pgid"
fi
[ "$ok" -eq 1 ] && pass "case4: -s 1 on 'sleep & exec sleep' -> whole tree gone"

# ---- case 5: memory kill ------------------------------------------------------

if command -v python3 >/dev/null 2>&1; then
    log5="$SCRATCH/case5.log"
    t0=$(date +%s)
    timeout 10 "$WD" -l case5 -L "$log5" -m 50m -- \
        python3 -c 'a=bytearray(200*1024*1024); import time; time.sleep(30)'
    rc=$?
    t1=$(date +%s)
    elapsed=$((t1 - t0))
    ok=1
    [ "$rc" -eq 122 ] || { ok=0; fail "case5: exit -> got $rc, want 122"; }
    [ "$elapsed" -lt 15 ] || { ok=0; fail "case5: took ${elapsed}s, want well under 30s"; }
    [ "$ok" -eq 1 ] && pass "case5: -m 50m on ~200MB alloc -> 122, killed early"
else
    printf 'SKIP: case5 (memory kill) — python3 not found\n'
fi

# ---- case 6: RSS accuracy calibration ----------------------------------------

if command -v python3 >/dev/null 2>&1; then
    log6="$SCRATCH/case6.log"
    timeout 10 "$WD" -l case6 -L "$log6" -- \
        python3 -c 'a=bytearray(100*1024*1024); import time; time.sleep(1)'
    rc=$?
    peak="$(log_peak_rss "$log6")"
    ok=1
    [ "$rc" -eq 0 ] || { ok=0; fail "case6: exit -> got $rc, want 0"; }
    if [ -n "${peak:-}" ] && [ "$peak" -ge 80000 ] && [ "$peak" -le 160000 ]; then
        :
    else
        ok=0
        fail "case6: peak_rss_kb=${peak:-<missing>}, want in [80000,160000]"
    fi
    [ "$ok" -eq 1 ] && pass "case6: metrics-only ~100MB alloc -> peak_rss_kb=$peak in range"
else
    printf 'SKIP: case6 (RSS accuracy) — python3 not found\n'
fi

# ---- case 7: log line shape ---------------------------------------------------

log7ok="$SCRATCH/case7ok.log"
timeout 10 "$WD" -l case7ok -L "$log7ok" -- bash -c 'exit 0' >/dev/null
ok=1
[ "$(wc -l < "$log7ok")" -eq 1 ] || { ok=0; fail "case7: ok-run log line count != 1"; }
log_has_keys "$log7ok" || { ok=0; fail "case7: ok-run log missing keys"; }
[ "$(log_verdict "$log7ok")" = "ok" ] || { ok=0; fail "case7: ok-run verdict != ok"; }
[ "$ok" -eq 1 ] && pass "case7: single well-formed log line for ok run"

log7to="$SCRATCH/case7to.log"
timeout 10 "$WD" -l case7to -L "$log7to" -s 1 -- sleep 30 >/dev/null
ok=1
[ "$(wc -l < "$log7to")" -eq 1 ] || { ok=0; fail "case7: timeout-run log line count != 1"; }
log_has_keys "$log7to" || { ok=0; fail "case7: timeout-run log missing keys"; }
[ "$(log_verdict "$log7to")" = "timeout" ] || { ok=0; fail "case7: timeout-run verdict != timeout"; }
[ "$ok" -eq 1 ] && pass "case7: single well-formed log line for timeout run"

# ---- case 8: env vs CLI precedence --------------------------------------------

log8="$SCRATCH/case8.log"
t0=$(date +%s)
WATCHDOG_TIMEOUT=30 timeout 10 "$WD" -l case8 -L "$log8" -s 1 -- sleep 30
rc=$?
t1=$(date +%s)
elapsed=$((t1 - t0))
ok=1
[ "$rc" -eq 124 ] || { ok=0; fail "case8: exit -> got $rc, want 124 (CLI should win)"; }
[ "$elapsed" -lt 5 ] || { ok=0; fail "case8: took ${elapsed}s, want <5s (env's 30s ignored)"; }
[ "$ok" -eq 1 ] && pass "case8: -s 1 overrides WATCHDOG_TIMEOUT=30"

# ---- case 9: missing command ---------------------------------------------------

log9="$SCRATCH/case9.log"
timeout 10 "$WD" -l case9 -L "$log9" -- /no/such/command-xyz-does-not-exist 2>/dev/null
rc=$?
if [ "$rc" -eq 127 ]; then
    pass "case9: missing command -> 127"
else
    fail "case9: missing command -> got $rc, want 127"
fi

# ---- case 10: metrics-only mode ------------------------------------------------

log10="$SCRATCH/case10.log"
timeout 10 "$WD" -l case10 -L "$log10" -- bash -c 'sleep 0.5; exit 0'
rc=$?
ok=1
[ "$rc" -eq 0 ] || { ok=0; fail "case10: exit -> got $rc, want 0"; }
[ "$(log_verdict "$log10")" = "ok" ] || { ok=0; fail "case10: verdict != ok"; }
wall="$(tail -n1 "$log10" | grep -o 'wall=[0-9.]*' | cut -d= -f2)"
if awk -v w="${wall:-0}" 'BEGIN{exit !(w>=0.3)}'; then
    :
else
    ok=0
    fail "case10: wall=${wall:-<missing>}, want >=0.3"
fi
[ "$ok" -eq 1 ] && pass "case10: metrics-only mode runs to completion, logs plausibly"

# ---- case 11: section tag (env inheritance + CLI override) --------------------

log11="$SCRATCH/case11.log"
WATCHDOG_SECTION=envsec timeout 10 "$WD" -l case11a -L "$log11" -- bash -c 'exit 0'
ok=1
tail -n1 "$log11" | grep -q "section='envsec'" \
    || { ok=0; fail "case11: WATCHDOG_SECTION=envsec not in log line"; }
WATCHDOG_SECTION=envsec timeout 10 "$WD" -l case11b -S clisec -L "$log11" -- bash -c 'exit 0'
tail -n1 "$log11" | grep -q "section='clisec'" \
    || { ok=0; fail "case11: -S clisec did not override WATCHDOG_SECTION"; }
[ "$ok" -eq 1 ] && pass "case11: section tag from env, CLI -S wins over it"

# ---- case 12: stdin passes through to the child -------------------------------
#
# watchdog backgrounds its child, and a background job in a job-control-less
# shell implicitly gets /dev/null stdin unless the spawn defeats it — so a
# wrapped `cat` reading nothing would mean every stdin-consuming wrapped
# command silently reads EOF (a real wiring bug: a wrapped test driver read
# zero subjects and measured nothing while looking healthy).
log12="$SCRATCH/case12.log"
out12="$(printf 'stdin-payload\n' | timeout 10 "$WD" -l case12 -L "$log12" -- cat)"
if [ "$out12" = "stdin-payload" ]; then
    pass "case12: stdin reaches the wrapped child (cat echoes it back)"
else
    fail "case12: wrapped cat read '$out12', want 'stdin-payload' — stdin is being swallowed"
fi

# ---- summary --------------------------------------------------------------

total=$((pass_count + fail_count))
printf '\n%d/%d passed\n' "$pass_count" "$total"
[ "$fail_count" -eq 0 ]
