#!/usr/bin/env bash
# 150-parity-slot: findall_iter.md §5.3's PRE-BUILD parity run (lane parity, 2026-10-21) on
# worktrees/parity, queued with `scripts/boxqueue add --name 150-parity-slot THIS_FILE`.
#   --dry-run  a no-clock build and the quick answer gate (G2-G4: every timing binary against
#              L_old and python `re`, the PLT structure) in a scratch dir it removes; then the
#              declarations. G1 (the twin's 60-case table under ASan, ~35 s) does not fit
#              boxqueue's 30 s dry-run bound and runs first in the work instead.
#   --ready    THE QUIET GATE: ready only when the box lock is free, no queue job is running
#              and load1 < 2.0 on two consecutive checks a minute apart. Stateless: the first
#              quiet check answers 75 with "quiet-1 ... epoch=E", which the queue logs; the
#              next check reads that line back from queue.log.
#   (work)     exec taskset -c 7 parity.sh run: build, the full answer gate (a failure stops the
#              run before timing, exit 3), 5 launches x 12 subcells x 2 regimes x 9 arms,
#              arms rotated per launch, the table and the verdicts, `== parity COMPLETE 24`.
# cap: the lane's one-launch calibration (2 ms x 3 samples, 216 runs) took 4.3 s on a box at
# load 11, so a run costs ~20 ms of fixed overhead; at 20 ms x 7 samples plus calibration a
# launch is ~35 s, 5 launches ~180 s, plus build and the full gate pinned to one core
# (~90 s): ~270 s. Cap 1200 s (4.4x). Patience 4 h, then reported once.
set -u
TREE=/home/pcrec/projects/pcrec/worktrees/parity
MAIN=/home/pcrec/projects/pcrec
TW=$TREE/docs/design/findall_iter/twin
CPU=7
OUT=$TREE/build/parity/slot
case "${1:-}" in
    --dry-run)
        d=$TREE/build/parity/dry.$$
        out=$(PARITY_CPU=$CPU bash "$TW/parity.sh" smoke "$d" 2>&1); rc=$?
        rm -rf "$d"
        [ $rc = 0 ] || { printf '%s\n' "$out" | tail -5 >&2; exit 1; }
        printf '%s\n' "$out" | grep -E '^(== parity |   G[234])'
        sib=$(tr ',' '\n' < "/sys/devices/system/cpu/cpu$CPU/topology/thread_siblings_list" | grep -vx "$CPU" | head -1)
        echo "would run: taskset -c $CPU bash $TW/parity.sh run $OUT  (cpu$CPU; its SMT sibling cpu$sib idle by the quiet gate)"
        echo "boxqueue: cap 1200"
        echo "boxqueue: patience 14400"
        echo "boxqueue: expect verdicts=24 last=^== parity COMPLETE"
        exit 0 ;;
    --ready)
        st=$(bash "$MAIN/scripts/boxlock" status 2>&1 | head -1)
        case $st in free*) ;; *) echo "box lock not free: $st"; exit 75 ;; esac
        Q=${BQ_QUEUE:-$(bash "$MAIN/scripts/boxqueue" path)}
        r=$(ls -A "$Q/running" 2>/dev/null | head -1)
        [ -z "$r" ] || { echo "a queue job is running: $r"; exit 75; }
        l1=$(cut -d' ' -f1 /proc/loadavg); now=$(date +%s)
        if awk -v l="$l1" 'BEGIN { exit !(l >= 2.0) }'; then
            echo "loud load1=$l1 (quiet gate: load1 < 2.0 on two checks a minute apart)"; exit 75
        fi
        last=$(grep -E "^  pass [0-9]+ ${BQ_JOB:-150-parity-slot} " "$Q/queue.log" 2>/dev/null | tail -1)
        prev=$(printf '%s\n' "$last" | sed -n 's/.* not-ready: quiet-1 load1=[0-9.]* epoch=\([0-9]*\).*/\1/p')
        if [ -n "$prev" ] && [ $((now - prev)) -ge 50 ] && [ $((now - prev)) -le 180 ]; then
            echo "quiet twice: load1=$l1 now, the previous quiet check $((now - prev)) s ago"; exit 0
        fi
        echo "quiet-1 load1=$l1 epoch=$now (ready at the next check a minute on if load1 stays < 2.0)"
        exit 75 ;;
esac
[ -e "$OUT" ] && mv "$OUT" "$OUT.prev.$(date +%s)"
exec taskset -c "$CPU" bash "$TW/parity.sh" run "$OUT"
