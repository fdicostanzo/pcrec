#!/usr/bin/env bash
# scripts/test_queuemon.sh -- offline self-test of scripts/queuemon, monread and hooks/monitor_unread.sh ([MON-SCRIPT]).
# SAFETY: everything lives in a scratch dir under build/ (or $TMPDIR); queuewatch is replaced by a scripted fake (one
# `RC|line` per launch, then exit 2), the ledger is a scratch git repo, boxqueue (row 8) a recording fake. The one real
# queuewatch call runs against an EMPTY scratch queue. Never touches the live queue, state, ledger or monitor.log.
set -u
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$here/../build"; T=$(mktemp -d "${TMPDIR:-$here/../build}/queuemon.test.XXXXXX") || exit 2
trap 'rm -rf "$T"' EXIT
pass=0 fail=0
ok()  { echo "PASS: $*"; pass=$((pass+1)); }
bad() { echo "FAIL: $*"; fail=$((fail+1)); }
chk() { # chk NAME CONDITION-RC
    if [ "$2" = 0 ]; then ok "$1"; else bad "$1"; fi
}
export QUEUEMON_DIR=$T/mgr QUEUEMON_ROOT=$T/repo QUEUEMON_QW=$T/fakeqw QUEUEMON_BOXQUEUE=$T/fakebq QUEUEMON_Q=$T/q
mkdir -p "$T/mgr" "$T/repo/docs/dev" "$T/q/pending" "$T/q/running"
printf '## Runs\n' > "$T/repo/docs/dev/full_suite_ledger.md"
git -C "$T/repo" init -q && git -C "$T/repo" config user.email t@t && git -C "$T/repo" config user.name t &&
    git -C "$T/repo" add -A && git -C "$T/repo" commit -q -m init
cat > "$T/fakeqw" <<'EOS'
#!/usr/bin/env bash
f=$FAKE_SCRIPT; l=$(head -1 "$f" 2>/dev/null)
[ -n "$l" ] || { echo "queuewatch: NOT ARMED: scripted end"; exit 2; }
sed -i 1d "$f"; echo "queuewatch: ${l#*|}"; exit "${l%%|*}"
EOS
printf '#!/usr/bin/env bash\necho "$*" >> "%s/bq.calls"\n' "$T" > "$T/fakebq"
export FAKE_SCRIPT=$T/script
L1=$T/L1 L2=$T/L2 L3=$T/L3; mkdir -p "$L1" "$L2" "$L3"; touch "$L1/trailer.log" "$L3/trailer.log"
echo "2026-10-25 abc test=RED duration=1s" > "$L1/summary.txt"; echo "2026-10-25 def test=green duration=1s" > "$L2/summary.txt"
cat > "$FAKE_SCRIPT" <<EOS
0|JOB-START 300-main-fullsuite owner=main 2026-10-25T10:00:00
0|STAGE-END 300-main-fullsuite test rc=0 logdir=$L1
0|STAGE-END 300-main-fullsuite axes rc=2 logdir=$L1
0|STAGE-END 300-main-fullsuite mech rc=2 logdir=$L1
0|JOB-DONE 300-main-fullsuite outcome=failed rc=1 verdict=RED wall=9s reds=axes(rc=2) mech(rc=2) logdir=$L1
0|JOB-DONE 301-main-ok outcome=green rc=0 verdict=GREEN wall=9s logdir=$L2
0|JOB-DONE 302-kit-x outcome=failed rc=1 verdict=RED wall=9s
0|JOB-DONE 303-main-died outcome=failed rc=1 verdict=RED wall=9s logdir=$L3
0|JOB-DONE 304-lane-exp outcome=failed rc=0 verdict=GREEN wall=9s
0|JOB-DONE 305-main-c outcome=cancelled (never ran)
0|RUNNER-DEAD runner not live with 1 pending / 0 running job(s) :: x
0|RUNNER-DEAD runner not live with 1 pending / 0 running job(s) :: y
0|QUIET 310-kit-q no log growth or CPU for 1800s :: last: x
0|PENDING-STUCK 311-main-p pending for 2000s, nothing running :: x
0|DISK-HIGH /dev/x at 96% (>= 95%)
0|CI-RED abc123 99 subject
0|CI-CANCELLED abc124 100 subject
0|CI-UNAVAILABLE gh missing
0|WHAT-IS-THIS 1 2 3
6|CAP watched 3000s, nothing new - relaunch
EOS
timeout 60 bash "$here/queuemon" run; rc=$?
LOG=$T/mgr/monitor.log
has() { grep -qE -- "$1" "$LOG"; }
chk "run ends at queuewatch exit 2 (row 15) with rc 2" $([ $rc = 2 ] && echo 0 || echo 1)
has ' PROBLEM main queuewatch exit 2, queuemon ends' ; chk "row 15 PROBLEM line" $?
has ' INFO mon JOB-START 300-main-fullsuite'; chk "row 2 JOB-START INFO" $?
has ' INFO mon STAGE-END 300-main-fullsuite test rc=0'; chk "row 3 STAGE-END rc=0 INFO" $?
has ' RED main 300-main-fullsuite: stage axes RED \(rc=2\), owner triages'; chk "row 4 first red" $?
[ "$(grep -c 'stage mech RED' "$LOG")" = 0 ]; chk "row 5 later red not a message" $?
has ' INFO mon STAGE-END 300-main-fullsuite mech rc=2.*later red'; chk "row 5 logged INFO" $?
[ "$(cat "$L1/red_stages.txt" 2>/dev/null)" = mech ]; chk "row 5 appends red_stages.txt" $?
has ' RED main JOB-DONE 300-main-fullsuite .*reds=axes.*owner triages'; chk "row 7 RED with reds=" $?
has ' GREEN main 2026-10-25 def test=green'; chk "row 6 GREEN carries the summary line" $?
[ "$(git -C "$T/repo" log --format=%s | grep -c '^ledger: full suite')" = 2 ]; chk "rows 6/7 ledger commits (green + red)" $?
grep -q 'RED: 2026-10-25 abc' "$T/repo/docs/dev/full_suite_ledger.md" && grep -q '^2026-10-25 def' "$T/repo/docs/dev/full_suite_ledger.md"; chk "ledger lines appended" $?
has ' RED kit JOB-DONE 302-kit-x .*owner triages'; chk "row 7 non-fullsuite red to kit" $?
has ' RED main \[kit\] JOB-DONE 302-kit-x'; chk "kit RED also addressed to main" $?
has ' PROBLEM main run died: JOB-DONE 303-main-died'; chk "row 7 death of a full-suite job is PROBLEM" $?
has ' PROBLEM main EXPECT JOB-DONE 304-lane-exp.*expect is stale'; chk "EXPECT mismatch, other owner routed to main" $?
has ' INFO mon JOB-DONE 305-main-c'; chk "cancelled is INFO" $?
[ "$(cat "$T/bq.calls" 2>/dev/null)" = start ]; chk "row 8 one boxqueue start only" $?
has ' PROBLEM main runner dead again after one restart'; chk "row 8 second RUNNER-DEAD PROBLEM" $?
has ' PROBLEM kit QUIET 310-kit-q' && has ' PROBLEM main \[kit\] QUIET 310-kit-q'; chk "row 9 QUIET to kit and main" $?
has ' PROBLEM main PENDING-STUCK 311-main-p'; chk "row 10 PENDING-STUCK" $?
has ' PROBLEM main DISK-HIGH'; chk "row 10 DISK-HIGH" $?
has ' CI main CI-RED abc123' && has ' CI main CI-CANCELLED' && has ' CI main CI-UNAVAILABLE gh missing'; chk "rows 11-13 CI lines" $?
has ' PROBLEM main UNEXPECTED WHAT-IS-THIS 1 2 3'; chk "UNEXPECTED line is a PROBLEM" $?
[ "$(grep -c ' UP mon ' "$LOG")" = 21 ]; chk "an UP line at every launch/relaunch (21)" $?
awk 'NF < 4 || $2 !~ /^(GREEN|RED|PROBLEM|CI|INFO|UP)$/ { exit 1 }' "$LOG"; chk "every line is ISO CLASS OWNER text" $?
[ ! -e "$T/mgr/queuemon.pid" ]; chk "pid file removed at exit" $?
# single instance
printf '0|CI-RED a 1 s\n' > "$FAKE_SCRIPT"; printf '#!/usr/bin/env bash\nsleep 4; echo "queuewatch: CAP"; exit 6\n' > "$T/slowqw"
( QUEUEMON_QW=$T/slowqw timeout 10 bash "$here/queuemon" run >/dev/null 2>&1 ) & sleep 1
QUEUEMON_QW=$T/slowqw timeout 10 bash "$here/queuemon" run; rc=$?; [ $rc = 75 ]; chk "second run refused (exit 75)" $?
kill %1 2>/dev/null; wait 2>/dev/null
# real queuewatch against an EMPTY scratch queue: CAP relaunch -> UP lines
mkdir -p "$T/rq/pending" "$T/rq/running" "$T/rq/done" "$T/rq/failed"; : > "$T/rq/queue.log"; rm -f "$T/mgr/queuemon.lock"; : > "$T/mgr/monitor.log"
QUEUEMON_QW=$here/queuewatch QUEUEMON_CAP=2 QUEUEMON_QWOPTS="--queue $T/rq --every 1 --no-ci" timeout 7 bash "$here/queuemon" run >/dev/null 2>&1
[ "$(grep -c ' UP mon ' "$LOG")" -ge 2 ] && ! grep -q PROBLEM "$LOG"; chk "real queuewatch (empty scratch queue): CAP relaunches, UP lines, no problem" $?
# monread: cursor, peek, wait, liveness
: > "$LOG"; rm -f "$T"/mgr/monitor.cursor.*; export QUEUEMON_Q=$T/emptyq; mkdir -p "$T/emptyq/pending" "$T/emptyq/running"
printf '2026-10-25T10:00:00 GREEN main one\n2026-10-25T10:00:01 RED kit two\n2026-10-25T10:00:02 INFO mon three\n' > "$LOG"
[ "$(bash "$here/monread" main --peek)" = "2026-10-25T10:00:00 GREEN main one" ]; chk "monread --peek prints owner's lines" $?
[ "$(bash "$here/monread" main)" = "2026-10-25T10:00:00 GREEN main one" ]; chk "monread prints and advances" $?
[ -z "$(bash "$here/monread" main)" ]; chk "second read is empty (cursor advanced)" $?
[ "$(bash "$here/monread" kit | wc -l)" = 1 ]; chk "cursors are per owner" $?
( sleep 1; echo '2026-10-25T10:00:09 PROBLEM main late' >> "$LOG" ) &
out=$(MONREAD_EVERY=0.3 timeout 10 bash "$here/monread" main --wait); wait
[ "$out" = "2026-10-25T10:00:09 PROBLEM main late" ]; chk "--wait blocks until a new line for the owner" $?
# liveness: a queued job and a dead monitor
touch "$T/emptyq/pending/100-main-x"; rm -f "$T/mgr/queuemon.pid"
bash "$here/monread" main --peek | grep -q 'PROBLEM main monitor dead/stale: queuemon pid none'; chk "queued job + no monitor -> PROBLEM dead" $?
sleep 30 & sp=$!; echo "pid=$sp" > "$T/mgr/queuemon.pid"
[ -z "$(bash "$here/monread" main --peek)" ]; chk "queued job + live monitor + fresh log -> quiet" $?
touch -d '2 hours ago' "$LOG"
bash "$here/monread" main --peek | grep -q 'PROBLEM main monitor dead/stale: monitor.log silent'; chk "stale log -> PROBLEM stale" $?
kill $sp; rm -f "$T/emptyq/pending/100-main-x"
[ -z "$(bash "$here/monread" main --peek)" ]; chk "no job queued -> no liveness problem" $?
# hook: main only
H=$here/hooks/monitor_unread.sh; : > "$LOG"; rm -f "$T"/mgr/monitor.cursor.*
echo '2026-10-25T10:00:00 RED main hookline' > "$LOG"
out=$(printf '{"hook_event_name":"UserPromptSubmit","agent_id":"a1","prompt":"x"}' | bash "$H")
[ -z "$out" ] && [ -z "$(cat "$T/mgr/monitor.cursor.main" 2>/dev/null)" ]; chk "hook: subagent (agent_id) gets nothing, cursor untouched" $?
out=$(printf '{"hook_event_name":"UserPromptSubmit","prompt":"agent_id x"}' | bash "$H")
printf '%s' "$out" | python3 -I -c 'import sys,json
d=json.load(sys.stdin)["hookSpecificOutput"]; assert d["hookEventName"]=="UserPromptSubmit" and "hookline" in d["additionalContext"]'; chk "hook: main gets hookSpecificOutput.additionalContext JSON" $?
[ -z "$(printf '{"hook_event_name":"UserPromptSubmit"}' | bash "$H")" ]; chk "hook: shown once (cursor advanced)" $?
echo '2026-10-25T10:00:05 INFO main n' >> "$LOG"
printf '{"hook_event_name":"SessionStart","source":"startup"}' | bash "$H" | grep -q '"hookEventName": "SessionStart"'; chk "hook: SessionStart event name echoed" $?
# boxqueue autostart is inert on a scratch queue
PCREC_BOXQUEUE_DIR=$T/bqq QUEUEMON_DIR=$T/inert bash "$here/boxqueue" start >/dev/null 2>&1
[ ! -e "$T/inert" ]; chk "boxqueue start on a scratch queue does not start queuemon" $?
[ -f "$T/bqq/runner.pid" ] && bash "$here/safekill" "$(sed -n 's/^pid=\([0-9]*\).*/\1/p' "$T/bqq/runner.pid")" >/dev/null 2>&1
echo "queuemon test: $pass passed, $fail failed"
[ "$fail" = 0 ]
