#!/bin/bash
# grid1/slot.sh -- the joint timing slot: F1, then F3, then F2 (skips loudly
# when perf is denied), then the external arm sets. The kit manager launches
# it on a quiet box, detached:
#
#   setsid nohup bash /home/pcrec/projects/pcrec/worktrees/grid1/docs/dev/lanes/grid1/slot.sh >/dev/null 2>&1 </dev/null &
#
# Status file $OUT/slot.status: SLOT_START, the gates, one line per phase
# (rc + the phase log's completion line), SLOT_DONE (or SLOT_REFUSED <why>).
# Logs: $OUT/time_F1.log, time_F3.log, f2.log, time_EXT.log; per-launch raw
# values $OUT/time/raw_<PHASE>.tsv and $OUT/f2/raw.tsv.
#
# GATES (refusals are written, never silent):
#   - check.sh must have run AFTER the last change to any arm table, any ext
#     set or any binary (else SLOT_REFUSED stale-check: re-run build.sh --ext
#     and check.sh); an arm in $OUT/excluded refuses the slot unless
#     ALLOW_EXCLUDED=1 (then it is recorded and time.sh skips it);
#   - quiet box: wait up to START_WAIT seconds for load1 < LOADMAX, record
#     what was seen; time.sh's per-group gate keeps holding it.
# DRY=1 STATUS=... LOGDIR=... runs the whole slot with NO CLOCK (time.sh's DRY
# mode, no quiet wait): the end-to-end proof that the slot runs, nothing timed.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid1}
CPU=${CPU:-14}
LAUNCHES=${LAUNCHES:-5}
LOADMAX=${LOADMAX:-1.5}
START_WAIT=${START_WAIT:-1800}
S=${STATUS:-$OUT/slot.status}
LOGDIR=${LOGDIR:-$OUT}
RAWDIR=${RAWDIR:-$OUT/time}
export OUT CPU LAUNCHES LOADMAX RAWDIR
cd "$OUT" || exit 2
[ "${DRY:-0}" = 1 ] || rm -f "$OUT/SLOT_DONE"
echo "SLOT_START $(date -Is) host=$(uname -n) cpu=$CPU launches=$LAUNCHES loadmax=$LOADMAX gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null)" > "$S"
refuse() { echo "SLOT_REFUSED $* $(date -Is)" >> "$S"; exit 1; }

[ -s "$OUT/check.log" ] || refuse "no-check: run check.sh first"
stale=$(find "$OUT/arms.tsv" "$OUT/arms_f2.tsv" "$OUT/ext" "$OUT/bin" -type f -newer "$OUT/check.log" -print -quit 2>/dev/null)
[ -n "$stale" ] && refuse "stale-check: $stale is newer than check.log (re-run build.sh --ext and check.sh)"
python3 -I "$HERE/arms.py" "$OUT" validate all > "$OUT/tmp/slot.validate" 2>&1 || refuse "arm-tables-invalid: $(head -1 "$OUT/tmp/slot.validate")"
if [ -s "$OUT/excluded" ]; then
  [ "${ALLOW_EXCLUDED:-0}" = 1 ] || refuse "excluded-arms: $(wc -l < "$OUT/excluded") (cell, arm) pairs failed check.sh; ALLOW_EXCLUDED=1 times the rest"
  echo "EXCLUDED $(tr '\n' ',' < "$OUT/excluded")" >> "$S"
fi
echo "CHECK_OK $(tail -1 "$OUT/tmp/slot.validate") check.log=$(stat -c %y "$OUT/check.log" | cut -c1-19)" >> "$S"

w=0
while :; do
  l=$(cut -d' ' -f1 /proc/loadavg)
  awk "BEGIN{exit !($l < $LOADMAX)}" && break
  [ "$w" -ge "$START_WAIT" ] || [ "${DRY:-0}" = 1 ] && break
  sleep 30; w=$((w + 30))
done
echo "QUIET load1=$(cut -d' ' -f1 /proc/loadavg) waited=${w}s $( awk "BEGIN{exit !($(cut -d' ' -f1 /proc/loadavg) < $LOADMAX)}" && echo ok || echo 'NOT-QUIET-proceeding')" >> "$S"

bash "$HERE/time.sh" --counts > "$OUT/tmp/slot.counts" 2>&1     # incremental: only rows an ext set added
echo "COUNTS $(tail -1 "$OUT/tmp/slot.counts")" >> "$S"
bash "$HERE/time.sh" --estimate > "$OUT/tmp/slot.estimate" 2>&1
echo "ESTIMATE $(tail -1 "$OUT/tmp/slot.estimate")" >> "$S"

phase() {   # name timeout command...
  local n=$1 to=$2; shift 2
  echo "${n}_START $(date -Is)" >> "$S"
  gnutimeout "$to" "$@"; local rc=$?
  echo "${n}_END rc=$rc $(date -Is)" >> "$S"
  return $rc
}
phase F1 14400 env PHASE=F1 bash "$HERE/time.sh" > "$LOGDIR/time_F1.log" 2>&1; echo "F1 $(tail -1 "$LOGDIR/time_F1.log")" >> "$S"
phase F3 3600 env PHASE=F3 bash "$HERE/time.sh" > "$LOGDIR/time_F3.log" 2>&1; echo "F3 $(tail -1 "$LOGDIR/time_F3.log")" >> "$S"
phase F2 3600 env STATUS="$S" bash "$HERE/f2perf.sh" > "$LOGDIR/f2.log" 2>&1; echo "F2 $(tail -1 "$LOGDIR/f2.log")" >> "$S"
if [ -n "$(python3 -I "$HERE/arms.py" "$OUT" cells timed EXT)" ]; then
  phase EXT 14400 env PHASE=EXT bash "$HERE/time.sh" > "$LOGDIR/time_EXT.log" 2>&1; echo "EXT $(tail -1 "$LOGDIR/time_EXT.log")" >> "$S"
else
  echo "EXT none: no ext set declares a base (ext arms joined to own cells were timed in F1/F3)" >> "$S"
fi
echo "SLOT_DONE $(date -Is)" >> "$S"
[ "${DRY:-0}" = 1 ] || touch "$OUT/SLOT_DONE"
