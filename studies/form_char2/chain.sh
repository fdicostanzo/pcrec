#!/usr/bin/env bash
# [FORM-CHAR2] detached timing chain (ubuntubudu). Stage with: scp -r studies/form_char2/{build,run,analyze,chain}... into
# $S (see formchar2_report.md 4a). Gate: load1 < 0.5 and no `make`. Gives up cleanly at DEADLINE (box local time)
# because the bench owns the box all day 2026-10-01; never starts building/timing at or after it.
S=/home/duxevents/pcrec/.formchar2_scratch; cd $S
DEADLINE_STR="2026-10-01 06:00"
DEADLINE=$(date -d "$DEADLINE_STR" +%s)
log() { echo "$(date +%F\ %T) $*" >> $S/chain.log; }
giveup() { log "CHAIN GAVE UP: $1 (deadline $DEADLINE_STR box-local; nothing timed)"; exit 3; }
log "chain start pid $$ deadline $DEADLINE_STR"
waited=0
while :; do
  [ "$(date +%s)" -ge "$DEADLINE" ] && giveup "deadline reached while waiting for an idle box"
  l=$(cut -d' ' -f1 /proc/loadavg); m=$(pgrep -x make | wc -l)
  if awk -v l="$l" 'BEGIN{exit !(l<0.5)}' && [ "$m" = 0 ]; then break; fi
  [ $((waited % 300)) = 0 ] && log "waiting: load1=$l make_procs=$m"
  sleep 30; waited=$((waited+30))
done
# leave room: the whole build+timing is ~10 min; refuse to start inside the last 30 min before the deadline
[ $(( DEADLINE - $(date +%s) )) -lt 1800 ] && giveup "less than 30 min to deadline at quiet point"
log "quiet: load1=$l make=0 -- building"
python3 build.py $S/w --reuse --cc gcc > $S/sizes_x86.tsv 2>> $S/chain.log || { log "BUILD FAILED"; exit 1; }
[ "$(date +%s)" -ge "$DEADLINE" ] && giveup "deadline reached after build"
log "built; timing"
python3 run.py $S/w --rounds 11 --loadmax 0.5 --maxwait $(( DEADLINE - $(date +%s) - 600 )) --out $S/timing_raw.tsv >> $S/chain.log 2>&1 || { log "RUN FAILED"; exit 1; }
python3 analyze.py $S/timing_raw.tsv > $S/timing_summary.tsv 2>> $S/chain.log
log "CHAIN COMPLETE"
