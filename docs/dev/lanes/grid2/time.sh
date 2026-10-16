#!/bin/bash
# grid2/time.sh -- the zen4-grid2 timing harness, method kit-grid@2. grid1/time.sh's method
# (spike1's), changed in the ways r17b_prime.md §5.4 and regime_eval §1.2/§2.4 state, and
# otherwise line for line:
#   - BASE COPIES: the base arm is launched THREE times per round: `base`, `base#b`, `base#c`
#     (same binary). base/base#b give the group's A/A floor (NULL); base#c is held out of
#     NULL: the independent A/A and the slot's drift/noise anchor (regime_eval §1.2);
#   - LAUNCHES defaults to 3; the RERUN RULE (pre-registered, regime_eval §1.2 [r1 M-9] and
#     EP29): a group in which |base_i - base#b_i| exceeds NULL in ANY of its launches gets
#     RERUN_EXTRA (2) more launches, once. NULL here is RERUN_NULL x median(base), RERUN_NULL
#     = 0.031 (M6, the null floor eps of the one grid1 run); the decision uses nothing else.
#     The share of groups rerun is reported;
#   - the quiet gate waits at every group boundary (as grid1), records load1 before and after
#     the group, and re-queues a group whose end load1 reached LOADBREACH once at the end of
#     the phase (`requeued`); a group that breaches twice is kept and marked `BREACH`;
#   - the counter-unavailable SUGGESTION (paranoid.sh) is printed to the log when user-space
#     counters are not available (--paranoid prints it and exits: the check's lever);
#   - NOCLOCK=1 runs the whole loop with no clock (grid1's DRY=1): every launch is the arm's
#     GRID_FIXED=0 answer run and records ns=1.00. (DRY=1 in grid2 names the tiny SUBSET
#     slot, which is clocked; see README.md.)
#
#   OUT=... PHASE=F1|F3|EXT [CELLS_RE=...] [LAUNCHES=3] bash time.sh > $OUT/time_F1.log 2>&1
#   completion line:  "time.sh: COMPLETE rows=N groups=G reruns=R requeued=Q wall=Ns"
#   bash time.sh --estimate | --counts | --paranoid
#
# METHOD (as grid1): each run binary calibrates its own loop to >= 50 ms and reports the
# median of 7 rounds (gdrv.c). For one (cell, subject, mode) group, LAUNCHES rounds; in
# each round every arm is launched once, the base THREE times, the round's order ROTATED by
# one from the previous round, all pinned to CPU. Reported per arm: the median over launches;
# the A/A floor; the per-launch spread (min..max as % of the median); the delta to the base
# and a WIN/LOSS/NULL verdict (NULL when |delta| <= floor). Every launch is also written to
# $OUT/time/raw_<PHASE>.tsv (round > LAUNCHES is a rerun round).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
G1=$(cd "$HERE/../grid1" && pwd)
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}
CPU=${CPU:-14}
LAUNCHES=${LAUNCHES:-3}
BASE_COPIES=${BASE_COPIES:-3}
RERUN_EXTRA=${RERUN_EXTRA:-2}
RERUN_NULL=${RERUN_NULL:-0.031}
LOADMAX=${LOADMAX:-1.5}
LOADBREACH=${LOADBREACH:-3.0}
LOADWAIT=${LOADWAIT:-60}
PHASE=${PHASE:-any}
CELLS_RE=${CELLS_RE:-.}
METHOD=kit-grid@2
SEC_REP=${SEC_REP:-0.65}        # a launch of a small subject (grid1 measured 0.45-0.85 s)
SEC_STREAM=${SEC_STREAM:-0.75}  # a launch of a streamed 4 MiB subject; replaced by the DRY run's measured figure
RERUN_SHARE=${RERUN_SHARE:-0.2} # estimate only: EP69
STEP=${1:-time}
cd "$OUT" || exit 2
. "$HERE/paranoid.sh"
start=$(date +%s)
mkdir -p "$OUT/time"

excluded() { grep -qx "$1 $2" "$OUT/excluded" 2>/dev/null; }
unreached() { grep -qxF "$(printf '%s\t%s\t%s' "$1" "$2" "$3")" "$OUT/unreached" 2>/dev/null; }
groups() { python3 -I "$G1/arms.py" "$OUT" groups timed "$1" | awk -F'\t' -v re="$CELLS_RE" '$1 ~ re'; }
copies() {   # base, base#b, base#c ... (BASE_COPIES of them)
  local b=$1 out="$1" k
  [ "$BASE_COPIES" -ge 2 ] && out="$out $b#b"
  [ "$BASE_COPIES" -ge 3 ] && out="$out $b#c"
  echo "$out"
}
arms_of() {   # cell subjtoken mode arms -> the launch list (base copies, then arms)
  local c=$1 m=$3 a; IFS=, read -r -a A <<<"$4"
  local out; out=$(copies "${A[0]}")
  for a in "${A[@]:1}"; do
    excluded "$c" "$a" && continue
    [ "$m" = first ] && [ -e "bin/$c/$a/same_first" ] && continue
    out="$out $a"
  done
  echo "$out"
}

counts() {   # every timed item with a counting twin, plus the site (G1) for own cells; no clock
  local f=$OUT/counts.tsv
  [ -s "$f" ] || printf 'cell\tarm\tsubject\tmode\tcounters\n' > "$f"
  python3 -I "$G1/arms.py" "$OUT" items all > "$OUT/tmp/items.timed"
  { awk -F'\t' '{print $1"\t"$2"\t"$4"\t"$5}' "$OUT/tmp/items.timed" | sort -u
    awk -F'\t' '{print $1"\tG1\t"$4"\t"$5}' "$OUT/tmp/items.timed" | sort -u; } |
  while IFS=$'\t' read -r c a s m; do
    [ -x "bin/$c/$a/cnt" ] || continue
    an=$a; [ "$a" = G1 ] && an='site(G1)'
    grep -qF "$(printf '%s\t%s\t%s\t%s\t' "$c" "$an" "$s" "$m")" "$f" && continue
    nm=${s%@*}; off=0; [ "$s" != "$nm" ] && off=${s#*@}
    line=$(GRID_OFF=$off taskset -c "${CNT_CPUS:-12-15}" gnutimeout 600 "bin/$c/$a/cnt" "subj/$nm" list "$m" 2>&1 >/dev/null | tail -1)
    printf '%s\t%s\t%s\t%s\t%s\n' "$c" "$an" "$s" "$m" "$line" >> "$f"
  done
}

case "$STEP" in
  --paranoid)   # the counter-unavailable suggestion, if the probe fails (PERF_FORCE_FAIL=1 forces it)
    st=${PASS_STATUS:-$OUT/time_${PHASE}.status}
    if perf_probe; then echo "counters available (perf stat counts user-space cycles)"; else paranoid_report /dev/null "$st"; fi
    exit 0 ;;
  --counts) counts; echo "counts: $(($(wc -l < "$OUT/counts.tsv") - 1)) rows in $OUT/counts.tsv"; exit 0 ;;
  --estimate)
    # launches x seconds per group; the rerun share adds RERUN_EXTRA x RERUN_SHARE launches per group
    ts=0; tl=0; tg=0
    for ph in F1 F3 EXT; do
      [ "$PHASE" != any ] && [ "$PHASE" != "$ph" ] && continue
      n=0; g=0; sec=0
      while IFS=$'\t' read -r c s m a; do
        unreached "$c" "$s" "$m" && continue
        k=$(wc -w <<<"$(arms_of "$c" "$s" "$m" "$a")")
        per=$SEC_REP; [ -d "subj/${s%@*}" ] && per=$SEC_STREAM
        n=$(awk -v a="$n" -v k="$k" -v l="$LAUNCHES" -v e="$RERUN_EXTRA" -v r="$RERUN_SHARE" 'BEGIN{print a + k*(l + e*r)}')
        g=$((g + 1))
        sec=$(awk -v a="$sec" -v k="$k" -v l="$LAUNCHES" -v e="$RERUN_EXTRA" -v r="$RERUN_SHARE" -v d="$per" 'BEGIN{print a + k*(l + e*r)*d}')
      done < <(groups "$ph")
      printf 'estimate %-3s groups=%d launches=%.0f wall=%.1f min (+ quiet-gate waits)\n' "$ph" "$g" "$n" "$(awk -v s="$sec" 'BEGIN{print s/60}')"
      ts=$(awk -v a="$ts" -v b="$sec" 'BEGIN{print a+b}'); tl=$(awk -v a="$tl" -v b="$n" 'BEGIN{print a+b}'); tg=$((tg + g))
    done
    printf 'estimate ALL groups=%d launches=%.0f wall=%.1f min\n' "$tg" "$tl" "$(awk -v s="$ts" 'BEGIN{print s/60}')"
    exit 0 ;;
  time) ;;
  *) echo "usage: time.sh [--estimate|--counts|--paranoid]"; exit 2 ;;
esac

RAWDIR=${RAWDIR:-$OUT/time}; mkdir -p "$RAWDIR"
RAW=$RAWDIR/raw_${RAW_TAG:-$PHASE}.tsv
printf 'phase\tcell\tsubject\tmode\tround\tpos\tarm\tns\tanswer\tload1\tts\n' > "$RAW"
[ "${NOCLOCK:-0}" = 1 ] && echo "# NOCLOCK RUN: no clock; every ns below is the placeholder 1.00"
echo "# grid2 time.sh method=$METHOD $(date -u) $(uname -n) phase=$PHASE load1=$(cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) cpu=$CPU launches=$LAUNCHES rerun_extra=$RERUN_EXTRA rerun_null=$RERUN_NULL base_copies=$BASE_COPIES loadmax=$LOADMAX loadbreach=$LOADBREACH"
echo "# ns = ns per pass (median over launches of each launch's 7-round median); delta = arm - base; floor = |base#b - base| (A/A); aac = |base#c - base| (the held-out A/A);"
echo "# spread = per-launch min..max as % of the arm's median; per_match = delta / matches (all mode); verdict NULL when |delta| <= floor"
echo "# raw per-launch values: $RAW"
st=${PASS_STATUS:-$OUT/time_${PHASE}.status}; : > "$st"
if ! perf_probe; then echo "# optional counter passes (items 6-7) will skip loudly:"; paranoid_report /dev/null "$st"; fi
printf '%-10s %-38s %-5s %-6s %12s %12s %11s %9s %9s %13s %10s %s\n' cell subject mode arm ns base delta floor aac spread per_match verdict
rows=0; groups_done=0; reruns=0; requeued=0
med() { tr ' ' '\n' <<<"$1" | grep . | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}'; }
launch() {   # cell subjtoken mode V round pos -> sets LNS LAN, appends the raw row
  local c=$1 s=$2 m=$3 V=$4 i=$5 p=$6 b=${4%%#*} nm off out
  nm=${s%@*}; off=0; [ "$s" != "$nm" ] && off=${s#*@}
  if [ "${NOCLOCK:-0}" = 1 ]; then out="$(GRID_OFF=$off GRID_FIXED=0 taskset -c "$CPU" "bin/$c/$b/run" "subj/$nm" "$m" 2>&1 | sed -E 's/ passes=.*//') ns/pass=1.00"
  else out=$(GRID_OFF=$off taskset -c "$CPU" "bin/$c/$b/run" "subj/$nm" "$m" 2>&1); fi
  LNS=$(sed -n 's/.*ns\/pass=\([0-9.]*\).*/\1/p' <<<"$out"); LAN=$(sed 's/ ns\/pass.*//' <<<"$out")
  printf '%s\t%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t%s\n' "$PHASE" "$c" "$s" "$m" "$i" "$p" "$V" "${LNS:-NaN}" "$LAN" "$(cut -d' ' -f1 /proc/loadavg)" "$(date +%s.%N)" >> "$RAW"
}
run_group() {   # cell subjtoken mode arms requeue-flag
  local c=$1 s=$2 m=$3 arms=$4 rq=${5:-0} waits=0 t l0 l1 i p k V B nlaunch rr=0
  if unreached "$c" "$s" "$m"; then echo "# skip $c $s $m: UNREACHED (site uses = 0; check.sh leg U)"; return 0; fi
  if [ "${NOCLOCK:-0}" != 1 ]; then for t in $(seq 1 "$LOADWAIT"); do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($l < $LOADMAX)}" && break; waits=$t; sleep 20; done; fi
  l0=$(cut -d' ' -f1 /proc/loadavg)
  [ "$waits" -gt 0 ] && echo "# quiet gate: $c $s $m waited ${waits}x20s, load1 now $l0"
  read -r -a A <<<"$(arms_of "$c" "$s" "$m" "$arms")"
  k=${#A[@]}; B=${A[0]}
  declare -A M=(); declare -A H=(); declare -A PL=()
  nlaunch=$LAUNCHES
  for ((i = 1; i <= nlaunch; i++)); do
    for ((p = 0; p < k; p++)); do
      V=${A[$(( (p + i - 1) % k ))]}
      launch "$c" "$s" "$m" "$V" "$i" "$p"
      M[$V]="${M[$V]:-} ${LNS:-NaN}"; H[$V]=$LAN; PL["$V,$i"]=${LNS:-NaN}
    done
    if [ "$i" = "$LAUNCHES" ] && [ "$rr" = 0 ] && [ "$BASE_COPIES" -ge 2 ] && [ "$RERUN_EXTRA" -gt 0 ] && [ "${NOCLOCK:-0}" != 1 ]; then
      # the pre-registered rerun rule: any launch with |base_i - base#b_i| > NULL
      local medb nullv j bad=0
      medb=$(med "${M[$B]}"); nullv=$(awk -v m="$medb" -v e="$RERUN_NULL" 'BEGIN{print m*e}')
      for ((j = 1; j <= LAUNCHES; j++)); do
        awk -v a="${PL["$B,$j"]}" -v b="${PL["$B#b,$j"]}" -v n="$nullv" 'BEGIN{d=a-b; if(d<0)d=-d; exit !(d>n)}' && bad=1
      done
      if [ "$bad" = 1 ]; then rr=1; reruns=$((reruns + 1)); nlaunch=$((LAUNCHES + RERUN_EXTRA)); echo "# rerun: $c $s $m (A/A disagreement beyond NULL=$nullv in a launch): +$RERUN_EXTRA launches"; fi
    fi
  done
  l1=$(cut -d' ' -f1 /proc/loadavg)
  local v0 v0b v0c fl ac mt n sp d pm vd
  v0=$(med "${M[$B]}"); v0b=$(med "${M["$B#b"]:-$v0}"); v0c=$(med "${M["$B#c"]:-$v0}")
  fl=$(awk "BEGIN{x=$v0b-$v0; printf \"%.2f\", x<0?-x:x}")
  ac=$(awk "BEGIN{x=$v0c-$v0; printf \"%.2f\", x<0?-x:x}")
  mt=$(sed -n 's/matches=\([0-9]*\).*/\1/p' <<<"${H[$B]}")
  for V in "${A[@]}"; do
    [ "$V" = "$B" ] && continue
    [ "${H[$V]}" = "${H[$B]}" ] || echo "# ANSWER MISMATCH $c $s $m $V: '${H[$V]}' vs base '${H[$B]}'"
    n=$(med "${M[$V]}")
    sp=$(tr ' ' '\n' <<<"${M[$V]}" | grep . | sort -g | awk -v md="$n" 'NR==1{lo=$1} {hi=$1} END{printf "%+.1f..%+.1f%%", 100*(lo-md)/md, 100*(hi-md)/md}')
    d=$(awk "BEGIN{printf \"%+.2f\", $n-$v0}")
    pm=-; [ "$m" = all ] && [ "${mt:-0}" -gt 0 ] && pm=$(awk "BEGIN{printf \"%+.3f\", ($n-$v0)/$mt}")
    vd=$(awk "BEGIN{x=$n-$v0; a=x<0?-x:x; print (a<=$fl)?\"NULL\":(x<0?\"WIN\":\"LOSS\")}")
    case "$V" in "$B#b"|"$B#c") vd=A/A ;; esac
    printf '%-10s %-38s %-5s %-6s %12s %12s %11s %9s %9s %13s %10s %s\n' "$c" "$s" "$m" "$V" "$n" "$v0" "$d" "$fl" "$ac" "$sp" "$pm" "$vd"
    rows=$((rows + 1))
  done
  groups_done=$((groups_done + 1))
  local flag=""
  if [ "${NOCLOCK:-0}" != 1 ] && awk "BEGIN{exit !($l1 >= $LOADBREACH)}"; then
    if [ "$rq" = 0 ]; then flag=" BREACH(requeue)"; REQ+=("$c"$'\t'"$s"$'\t'"$m"$'\t'"$arms"); requeued=$((requeued + 1))
    else flag=" BREACH(twice)"; fi
  fi
  echo "# group $groups_done done: $c $s $m load1-at-start=$l0 load1-at-end=$l1 waits=$waits launches=$nlaunch${flag}"
  unset M H PL
}
REQ=()
while IFS=$'\t' read -r c s m arms; do
  run_group "$c" "$s" "$m" "$arms" 0
done < <(groups "$PHASE")
for q in "${REQ[@]:-}"; do   # the load-breach re-queue: once
  [ -n "$q" ] || continue
  IFS=$'\t' read -r c s m arms <<<"$q"
  echo "# requeue: $c $s $m"
  run_group "$c" "$s" "$m" "$arms" 1
done
echo
if [ -s "$OUT/counts.tsv" ]; then
  echo "## counters (counting builds bin/<cell>/<arm>/cnt, one pass, no clock; site(G1) = the cell's site counters, the walk's own)"
  awk -F'\t' -v re="$CELLS_RE" 'NR==1 || $1 ~ re' "$OUT/counts.tsv"
fi
echo "time.sh: COMPLETE rows=$rows groups=$groups_done reruns=$reruns requeued=$requeued wall=$(( $(date +%s) - start ))s"
