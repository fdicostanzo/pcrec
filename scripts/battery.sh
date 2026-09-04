#!/usr/bin/env bash
# scripts/battery.sh — [TT-12] STEP 1 item 5: battery_v5, the manager's
# merge/close validation chain as ONE detached, self-logging run.
#
# STAGES, IN ORDER: test -> strict -> axes -> san -> lint -> mech.
# `axes` is new here ([TT-12] STEP 2, Frank's ruling 2026-09-03: "2 yes" —
# test-axes joins the union battery once STEP 1's pairwise wall fits the
# day/night rule). Every other stage's SHAPE is this row's own STEP 1
# measurement, not carried over from the manager's earlier ad-hoc
# battery_v4.sh unchanged:
#   - `test`  : $(TEST_MAKE_J) / PROCS=$(TEST_PROCS), defaulting to
#     `-j4 PROCS=3` — MEASURED (docs/dev/lanes/tt12b_report.md's K44
#     table): of the three shapes tried (-j12 PROCS=1: 1674s, rc=2, the
#     resource CPU-cap cell reds; -j4 PROCS=3: 1115s, rc=0, clean; -j2
#     PROCS=6: 1792s, rc=0, clean), -j4 PROCS=3 is BOTH the fastest and
#     the only one with zero failures — the default here. battery_v4 ran
#     plain `make -k -j12 test` (PROCS=nproc internally, uncapped), the
#     K44 double-parallelism shape (load 47.61 measured, TT-12 STEP 0 §5).
#   - `axes`  : tests/axes/run_axes.sh's own [TT-12] STEP 1 pairing (two
#     axes concurrently at PROCS=nproc/2 each) — battery_v4 never ran this
#     stage at all.
#   - `san`   : $(SAN_PROCS)-way `-P` over the serial script loop for the
#     30 structurally single-process scripts (item 3), after the D77
#     concurrent-vs-sequential check on the five whole-corpus identity
#     scripts found no shared-resource contention — see the report.
#     battery_v4 ran this fully serial (109.6 min at ~1.9 of 12 cores
#     busy, [TT-12] STEP 0 §2).
#   - `mech`  : PROCS=6, not battery_v4's PROCS=4 — [TT-8]'s own measured
#     setting (28:43 vs 36:36 on the 118-row matrix, byte-identical rows),
#     which battery_v4 was contradicting.
#   - `strict`/`lint` are unchanged (already fast, already whole-box-idle
#     by their own nature — [TT-12] STEP 0 §1: strict 10s, lint 50s).
#
# Runs DETACHED under setsid with a PID file, waits for nothing — a lane or
# the manager launches this and polls the log/trailer at its own cron tick
# (docs/dev/learnings.md §6: artifacts, never process greps). One heavy
# suite at a time on this box (memory `pcrec-box-concurrency`) — do not
# launch this alongside another lane's own heavy run or a pcrec-bench
# window; check `uptime` first.
#
# Usage: scripts/battery.sh [LOGDIR]
#   LOGDIR   directory for the per-stage logs + PID file (default:
#            build/battery_<timestamp>/, created if missing). Printed on
#            stdout before detaching so the caller can start polling.
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR" || exit 9

TS="$(date +%Y%m%d_%H%M%S)"
LOGDIR="${1:-$ROOT_DIR/build/battery_$TS}"
mkdir -p "$LOGDIR"
PIDFILE="$LOGDIR/battery.pid"
TRAILER="$LOGDIR/trailer.log"

# [TT-12] STEP 1 item 4 (K44) — the test stage's own outer-make -j /
# inner-suite PROCS split; see docs/dev/lanes/tt12b_report.md's table.
# Overridable so a re-measurement doesn't require editing this file.
TEST_MAKE_J="${TEST_MAKE_J:-4}"
TEST_PROCS="${TEST_PROCS:-3}"
# [TT-8] mech's own measured setting, not battery_v4's PROCS=4.
MECH_PROCS="${MECH_PROCS:-6}"
# item 3 — san's -P width over the 30 structurally single-process scripts.
SAN_PROCS="${SAN_PROCS:-4}"
# item 1 — pairwise axes; run_axes.sh derives PROCS/2 itself from whatever
# PROCS it is given, so this is the PRE-pairing width (nproc by default).
AXES_PROCS="${AXES_PROCS:-$(nproc 2>/dev/null || echo 12)}"

run_battery() {
    local overall=0 rc
    {
        echo "== battery_v5 start $(date -Is) on $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
        echo "== load at start: $(uptime)"
        echo "== shape: test -j$TEST_MAKE_J PROCS=$TEST_PROCS | axes PROCS=$AXES_PROCS (paired) | san -P$SAN_PROCS | mech PROCS=$MECH_PROCS"
    } >> "$TRAILER"

    for stage in test strict axes san lint mech; do
        local slog="$LOGDIR/$stage.log"
        echo "== stage $stage START $(date -Is) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$TRAILER"
        case "$stage" in
            test)
                make -k -j"$TEST_MAKE_J" PROCS="$TEST_PROCS" test > "$slog" 2>&1
                ;;
            strict)
                make strict > "$slog" 2>&1
                ;;
            axes)
                # [CC-DIFF] STEP 2 (2026-09-04, manager's ruling): AXES_FULL=1
                # is what makes the battery's axes stage sweep the FULL set.
                # tests/axes/run_axes.sh runs the `--vm-entry-shape` ordinal's
                # two REACHABLE-BY-DEFAULT rungs unconditionally and its other
                # two only under this env, so the day's `make test-axes` pays
                # two extra corpus runs and the battery pays four. The battery
                # is where the whole product belongs; the day's suite is where
                # four permanent full-corpus runs were judged too much.
                AXES_FULL=1 PROCS="$AXES_PROCS" make test-axes > "$slog" 2>&1
                ;;
            san)
                SAN_PROCS="$SAN_PROCS" make san > "$slog" 2>&1
                ;;
            lint)
                make lint > "$slog" 2>&1
                ;;
            mech)
                PROCS="$MECH_PROCS" make mech > "$slog" 2>&1
                ;;
        esac
        rc=$?
        echo "== stage $stage rc=$rc END $(date -Is)" >> "$TRAILER"
        [ "$rc" -ne 0 ] && overall=1
    done

    echo "== BATTERY DONE rc=$overall $(date -Is)" >> "$TRAILER"
}

echo "battery.sh: logging to $LOGDIR (trailer: $TRAILER)"
echo "battery.sh: poll the trailer for stage START/END/rc lines and the final '== BATTERY DONE rc=' line"

setsid bash -c "$(declare -f run_battery); ROOT_DIR=$(printf '%q' "$ROOT_DIR"); cd \"\$ROOT_DIR\"; LOGDIR=$(printf '%q' "$LOGDIR"); TRAILER=$(printf '%q' "$TRAILER"); TEST_MAKE_J=$(printf '%q' "$TEST_MAKE_J"); TEST_PROCS=$(printf '%q' "$TEST_PROCS"); MECH_PROCS=$(printf '%q' "$MECH_PROCS"); SAN_PROCS=$(printf '%q' "$SAN_PROCS"); AXES_PROCS=$(printf '%q' "$AXES_PROCS"); run_battery" \
    < /dev/null > "$LOGDIR/setsid.log" 2>&1 &
echo $! > "$PIDFILE"
disown
echo "battery.sh: detached, pid $(cat "$PIDFILE")"
