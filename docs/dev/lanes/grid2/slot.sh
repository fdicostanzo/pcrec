#!/bin/bash
# grid2/slot.sh -- the zen4-grid2 timing slot (r17b_prime.md §5.4, D166 / D167 option (B):
# ONE streamed condition). The kit manager launches it on a quiet box, detached, with the
# slot directory as the one argument:
#
#   setsid nohup bash /home/pcrec/projects/pcrec/worktrees/<lane>/docs/dev/lanes/grid2/slot.sh \
#       /home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2 >/dev/null 2>&1 </dev/null &
#
# It does EVERYTHING in order, so the manager has one command and one status file:
#   BUILD   build.sh (design, grid1's cells and arms, ext sets, twins, subjects)   [SKIP_BUILD=1 skips]
#   CHECK   check.sh FIRST: legs R, L, C (+ O against libpcre2 10.46, U, G, U2); a PICKABLE
#           arm's answer failure FAILS the run (SLOT_FAILED, exit 3), whatever ALLOW_EXCLUDED
#           says; an excluded instrument arm (tw*, sc0) refuses the slot unless ALLOW_EXCLUDED=1
#   REQUIRED PHASES (items 1-4, timed with time.sh, method kit-grid@2):
#     F1   items 1+2  the 149 fit groups' streamed twins + the dispatch-twin arms
#     F3   items 1+2  the member-free F3 groups (+ R0 scaffold groups)
#     OB   items 3+4  the five one-byte cells, six gaps + four member-free lengths, NONE arms
#   OPTIONAL PHASES (items 6-8; a failure never fails the slot; each skips loudly):
#     F2   item 6     F2 perf on {walk, V1, A1} of every item-1 group   (f2perf.sh, F2_ITEM=6)
#     F2S  item 7     F2's streamed perf pass                           (f2perf.sh, F2_ITEM=7)
#     TRIG item 8     the pre-scan trigger probe, KEEP vs DROP          (time.sh, cells trig-*)
#
# STATUS FILE $OUT/slot.status -- one line per event; it ENDS with exactly one of
#   COMPLETE <date> required=ok optional=<done|skipped:...>         exit 0
#   FAILED <why> <date>                                              exit 1 (3: a pickable arm failed)
# Progress lines: SLOT_START, BUILD_START/END rc=, CHECK_START/END rc=, CHECK_OK, QUIET load1=
# waited= ok|NOT-QUIET-proceeding, ESTIMATE, <PHASE>_START, <PHASE>_PROGRESS groups=N (every
# 60 s while a phase runs), <PHASE>_END rc=, <PHASE> <the phase log's completion line>,
# F2_SKIPPED <why> | F2_DONE rows=, the paranoid SUGGESTION text (paranoid.sh) when counters
# are unavailable. Every file the slot writes is under $OUT; per-phase logs $OUT/time_<PHASE>.log,
# raw launches $OUT/time/raw_<PHASE>.tsv, $OUT/provenance.txt.
#
# ENV (defaults are the spec): CPU=14 LAUNCHES=3 RERUN_EXTRA=2 LOADMAX=1.5 START_WAIT=1800
#   ALLOW_EXCLUDED=0 SKIP_BUILD=0 SKIP_CHECK=0 PCREC=<kit-branch compiler> JOBS=4
# DRY=1: the tiny SUBSET (2-3 groups per item, design2.py --dry), LAUNCHES=1, no rerun, no
#   quiet wait (LOADMAX=999: a dry reading is NOT a measurement), the optional passes on the
#   subset, everything CLOCKED end to end; it prints the wall estimate of the FULL slot from
#   its own per-launch costs (estimate.py). PARANOID_ONLY=1: print the counter suggestion and exit.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
G1=$(cd "$HERE/../grid1" && pwd)
OUT=${1:-${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}}
DRY=${DRY:-0}
CPU=${CPU:-14}
LAUNCHES=${LAUNCHES:-3}
RERUN_EXTRA=${RERUN_EXTRA:-2}
LOADMAX=${LOADMAX:-1.5}
START_WAIT=${START_WAIT:-1800}
ALLOW_EXCLUDED=${ALLOW_EXCLUDED:-0}
if [ "$DRY" = 1 ]; then LAUNCHES=${LAUNCHES_DRY:-1}; RERUN_EXTRA=0; LOADMAX=999; LOADBREACH=999; START_WAIT=0; export LOADWAIT=0 LOADBREACH; fi
mkdir -p "$OUT/tmp"
export OUT CPU LAUNCHES RERUN_EXTRA LOADMAX ALLOW_EXCLUDED DRY
. "$HERE/paranoid.sh"
S=$OUT/slot.status
log() { echo "$*" >> "$S"; }
fail() { log "FAILED $* $(date -Is)"; exit "${FAILRC:-1}"; }
phase() {   # name timeout command...   -> rc; a progress line every 60 s while it runs
  local n=$1 to=$2 flag; shift 2
  flag=$OUT/tmp/phase.$n.done; rm -f "$flag"
  log "${n}_START $(date -Is)"
  ( while :; do for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do sleep 5; [ -e "$flag" ] && exit 0; done
      log "${n}_PROGRESS groups=$(grep -c '^# group ' "$OUT/time_${n}.log" 2>/dev/null || echo 0) $(date +%H:%M:%S)"; done ) &
  local pp=$!
  gnutimeout "$to" "$@"; local rc=$?
  touch "$flag"; wait "$pp" 2>/dev/null
  log "${n}_END rc=$rc $(date -Is)"
  return $rc
}

if [ "${PARANOID_ONLY:-0}" = 1 ]; then
  if perf_probe; then echo "counters available"; else paranoid_report /dev/null "${PARANOID_STATUS:-$OUT/paranoid.status}"; fi
  exit 0
fi

: > "$S"; rm -f "$OUT/SLOT_DONE"
log "SLOT_START $(date -Is) method=kit-grid@2 dry=$DRY host=$(uname -n) cpu=$CPU launches=$LAUNCHES rerun_extra=$RERUN_EXTRA loadmax=$LOADMAX gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) out=$OUT"
SLOT_T0=$(date +%s)
if ! perf_probe; then
  log "COUNTERS unavailable ($PERF_WHY): items 6-7 will skip loudly"
  paranoid_report /dev/null "$S" > /dev/null
fi

# ---- BUILD
if [ "${SKIP_BUILD:-0}" != 1 ]; then
  log "BUILD_START $(date -Is)"
  bash "$HERE/build.sh" > "$OUT/build.log" 2>&1; rc=$?
  log "BUILD_END rc=$rc $(date -Is)"; log "BUILD $(tail -1 "$OUT/build.log")"
  [ "$rc" = 0 ] || fail "build ($OUT/build.log)"
fi
# ---- CHECK, first
if [ "${SKIP_CHECK:-0}" != 1 ]; then
  log "CHECK_START $(date -Is)"
  bash "$HERE/check.sh" > "$OUT/check.out" 2>&1; rc=$?
  log "CHECK_END rc=$rc $(date -Is)"; log "CHECK $(tail -1 "$OUT/check.out")"
  [ "$rc" = 3 ] && { FAILRC=3; fail "pickable-arm-answer-failure: $(grep '^PICKABLE-FAIL' "$OUT/check2.status" | tr '\n' ',')"; }
  [ "$rc" = 0 ] || [ -s "$OUT/excluded" ] || fail "check ($OUT/check.out)"
else
  [ -s "$OUT/check.log" ] || fail "no-check: run check.sh first"
  stale=$(find "$OUT/arms.tsv" "$OUT/arms_f2.tsv" "$OUT/ext" "$OUT/bin" -type f -newer "$OUT/check.log" -print -quit 2>/dev/null)
  [ -n "$stale" ] && fail "stale-check: $stale is newer than check.log"
fi
python3 -I "$G1/arms.py" "$OUT" validate all > "$OUT/tmp/slot.validate" 2>&1 || fail "arm-tables-invalid: $(head -1 "$OUT/tmp/slot.validate")"
if [ -s "$OUT/excluded" ]; then
  log "EXCLUDED $(tr '\n' ',' < "$OUT/excluded")"
  [ "$ALLOW_EXCLUDED" = 1 ] || fail "excluded-arms: $(wc -l < "$OUT/excluded") (cell, arm) pairs failed check.sh; ALLOW_EXCLUDED=1 times the rest"
fi
log "CHECK_OK $(tail -1 "$OUT/tmp/slot.validate") check.log=$(stat -c %y "$OUT/check.log" | cut -c1-19)"

# ---- the quiet box
w=0
while :; do
  l=$(cut -d' ' -f1 /proc/loadavg)
  awk "BEGIN{exit !($l < $LOADMAX)}" && break
  [ "$w" -ge "$START_WAIT" ] && break
  sleep 30; w=$((w + 30))
done
log "QUIET load1=$(cut -d' ' -f1 /proc/loadavg) waited=${w}s $(awk "BEGIN{exit !($(cut -d' ' -f1 /proc/loadavg) < $LOADMAX)}" && echo ok || echo 'NOT-QUIET-proceeding')"

bash "$HERE/time.sh" --counts > "$OUT/tmp/slot.counts" 2>&1
log "COUNTS $(tail -1 "$OUT/tmp/slot.counts")"
bash "$HERE/time.sh" --estimate > "$OUT/tmp/slot.estimate" 2>&1
log "ESTIMATE $(tail -1 "$OUT/tmp/slot.estimate")"

# ---- REQUIRED phases
req=ok
for spec in "F1:14400:F1:." "F3:3600:F3:." "OB:14400:EXT:^o-"; do
  IFS=: read -r name to ph re <<<"$spec"
  phase "$name" "$to" env PHASE="$ph" RAW_TAG="$name" CELLS_RE="$re" PASS_STATUS="$OUT/time_${name}.status" bash "$HERE/time.sh" > "$OUT/time_${name}.log" 2>&1; rc=$?
  log "$name $(tail -1 "$OUT/time_${name}.log")"
  if [ "$rc" != 0 ] || ! tail -1 "$OUT/time_${name}.log" | grep -q 'COMPLETE'; then req="failed:$name"; break; fi
  if grep -q '# ANSWER MISMATCH' "$OUT/time_${name}.log"; then log "${name}_ANSWER_MISMATCH $(grep -c '# ANSWER MISMATCH' "$OUT/time_${name}.log")"; fi
done
[ "$req" = ok ] || fail "required-phase $req"
grep -q '# ANSWER MISMATCH' "$OUT"/time_*.log 2>/dev/null && fail "answer-mismatch in a timed launch ($(grep -l '# ANSWER MISMATCH' "$OUT"/time_*.log | tr '\n' ' '))"

# ---- OPTIONAL phases (never fail the slot)
opt=done
for spec in "F2:3600:6" "F2S:1800:7"; do
  IFS=: read -r name to item <<<"$spec"
  phase "$name" "$to" env STATUS="$S" F2_ITEM="$item" bash "$HERE/f2perf.sh" > "$OUT/${name,,}.log" 2>&1
  log "$name $(tail -1 "$OUT/${name,,}.log")"
  grep -q SKIPPED "$OUT/${name,,}.log" && opt="skipped:counters"
done
if [ "$DRY" = 1 ] || [ -n "$(python3 -I "$G1/arms.py" "$OUT" cells timed EXT | grep '^trig-')" ]; then
  phase TRIG 3600 env PHASE=EXT RAW_TAG=TRIG CELLS_RE='^trig-' PASS_STATUS="$OUT/time_TRIG.status" bash "$HERE/time.sh" > "$OUT/time_TRIG.log" 2>&1
  log "TRIG $(tail -1 "$OUT/time_TRIG.log")"
  tail -1 "$OUT/time_TRIG.log" | grep -q COMPLETE || opt="$opt+trig-failed"
fi

if [ "$DRY" = 1 ]; then
  python3 -I "$HERE/estimate.py" "$OUT" > "$OUT/dry_estimate.txt" 2>&1
  log "DRY_ESTIMATE $(tail -1 "$OUT/dry_estimate.txt")"
fi
log "WALL $(( $(date +%s) - SLOT_T0 ))s"
touch "$OUT/SLOT_DONE"
log "COMPLETE $(date -Is) required=$req optional=$opt"
exit 0
