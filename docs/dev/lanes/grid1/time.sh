#!/bin/bash
# grid1/time.sh -- times every (cell, subject, mode) group of the merged arm
# tables (own + every ext set), spike1's method, and records EVERY launch.
# Run only after build.sh and a green check.sh; (cell, arm) pairs listed in
# $OUT/excluded are not timed. The kit manager runs it (via slot.sh) on a
# quiet box:
#
#   OUT=... PHASE=F1 CPU=14 LAUNCHES=5 bash time.sh > $OUT/time_F1.log 2>&1
#   completion line:  "time.sh: COMPLETE rows=<N> wall=<s>s"
#
#   bash time.sh --estimate     # the launch count and wall estimate per phase, nothing timed
#   bash time.sh --counts       # the counters only (no clock): $OUT/counts.tsv, incremental
#   DRY=1 bash time.sh          # the whole loop with NO CLOCK: every launch is the arm's
#                               # GRID_FIXED=0 answer run and records ns=1.00, so rotation,
#                               # the raw file, the answer compare and the completion line
#                               # are exercised end to end; LOADMAX is ignored
#
# METHOD (alpha_r17b.sh / vecspike time.sh): each run binary calibrates its
# own loop to >= 50 ms and reports the median of 7 rounds (gdrv.c). For one
# (cell, subject, mode) group, LAUNCHES rounds; in each round every arm is
# launched once, the base TWICE (the A/A pair: `base` and `base#b`, the same
# binary), the round's arm order ROTATED by one from the previous round (so no
# arm always runs first), all pinned to CPU. Reported per arm: the median over
# launches; the A/A floor |median(base#b) - median(base)|; the per-launch
# spread (min..max as % of the median). A delta inside the floor is NULL.
# Every launch is ALSO written to $OUT/time/raw_<PHASE>.tsv with its round,
# position, load1 and answer, so a reader can redo any statistic.
# QUIET GATE: before each group, wait (20 s steps, at most LOADWAIT steps)
# for load1 < LOADMAX; the group's start load1 and waits are recorded.
# In `first` mode a keep arm marked same_first by build.sh is skipped (the
# same program as its unkept twin). A group listed in $OUT/unreached (check.sh
# leg U: its site never runs) is skipped and says so.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid1}
CPU=${CPU:-14}
LAUNCHES=${LAUNCHES:-5}
LOADMAX=${LOADMAX:-1.5}
LOADWAIT=${LOADWAIT:-60}
PHASE=${PHASE:-any}
CELLS_RE=${CELLS_RE:-.}
SEC_REP=${SEC_REP:-0.65}        # measured: one launch of a repeated-subject arm, 0.45-0.85 s
SEC_STREAM=${SEC_STREAM:-0.95}  # measured: a streamed (64 MiB) subject's launch, 0.92-0.97 s
STEP=${1:-time}
cd "$OUT" || exit 2
start=$(date +%s)
mkdir -p "$OUT/time"

excluded() { grep -qx "$1 $2" "$OUT/excluded" 2>/dev/null; }
unreached() { grep -qxF "$(printf '%s\t%s\t%s' "$1" "$2" "$3")" "$OUT/unreached" 2>/dev/null; }
groups() { python3 -I "$HERE/arms.py" "$OUT" groups timed "$1" | awk -F'\t' -v re="$CELLS_RE" '$1 ~ re'; }
arms_of() {   # cell subjtoken mode arms -> the launch list (base, base#b, arms)
  local c=$1 m=$3 a; IFS=, read -r -a A <<<"$4"
  local out="${A[0]} ${A[0]}#b"
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
  python3 -I "$HERE/arms.py" "$OUT" items all > "$OUT/tmp/items.timed"
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
  --counts) counts; echo "counts: $(($(wc -l < "$OUT/counts.tsv") - 1)) rows in $OUT/counts.tsv"; exit 0 ;;
  --estimate)
    tl=0; tr=0; ts=0
    for ph in F1 F3 EXT; do
      [ "$PHASE" != any ] && [ "$PHASE" != "$ph" ] && continue
      n=0; rows=0; sec=0; g=0
      while IFS=$'\t' read -r c s m a; do
        unreached "$c" "$s" "$m" && continue
        k=$(wc -w <<<"$(arms_of "$c" "$s" "$m" "$a")")
        per=$SEC_REP; [ -d "subj/${s%@*}" ] && per=$SEC_STREAM
        n=$((n + k * LAUNCHES)); rows=$((rows + k - 2)); g=$((g + 1))
        sec=$(awk -v a="$sec" -v b="$k" -v c="$LAUNCHES" -v d="$per" 'BEGIN{print a + b*c*d}')
      done < <(groups "$ph")
      printf 'estimate %-3s groups=%d rows=%d launches=%d wall=%.1f min (+ quiet-gate waits)\n' "$ph" "$g" "$rows" "$n" "$(awk -v s="$sec" 'BEGIN{print s/60}')"
      tl=$((tl + n)); tr=$((tr + rows)); ts=$(awk -v a="$ts" -v b="$sec" 'BEGIN{print a+b}')
    done
    printf 'estimate ALL groups rows=%d launches=%d wall=%.1f min\n' "$tr" "$tl" "$(awk -v s="$ts" 'BEGIN{print s/60}')"
    exit 0 ;;
  time) ;;
  *) echo "usage: time.sh [--estimate|--counts]"; exit 2 ;;
esac

RAWDIR=${RAWDIR:-$OUT/time}; mkdir -p "$RAWDIR"
RAW=$RAWDIR/raw_$PHASE.tsv
printf 'phase\tcell\tsubject\tmode\tround\tpos\tarm\tns\tanswer\tload1\tts\n' > "$RAW"
[ "${DRY:-0}" = 1 ] && echo "# DRY RUN: no clock; every ns below is the placeholder 1.00"
echo "# grid1 time.sh $(date -u) $(uname -n) phase=$PHASE load1=$(cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) cpu=$CPU launches=$LAUNCHES loadmax=$LOADMAX"
echo "# ns = ns per pass (median over launches of each launch's 7-round median); delta = arm - base; floor = |base#b - base| (A/A);"
echo "# spread = per-launch min..max as % of the arm's median; per_match = delta / matches (all mode); verdict NULL when |delta| <= floor"
echo "# raw per-launch values: $RAW"
printf '%-10s %-34s %-5s %-6s %12s %12s %11s %9s %13s %10s %s\n' cell subject mode arm ns base delta floor spread per_match verdict
rows=0; groups_done=0
med() { tr ' ' '\n' <<<"$1" | grep . | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}'; }
while IFS=$'\t' read -r c s m arms; do
  if unreached "$c" "$s" "$m"; then echo "# skip $c $s $m: UNREACHED (site uses = 0; check.sh leg U)"; continue; fi
  waits=0
  [ "${DRY:-0}" = 1 ] || for t in $(seq 1 "$LOADWAIT"); do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($l < $LOADMAX)}" && break; waits=$t; sleep 20; done
  l0=$(cut -d' ' -f1 /proc/loadavg)
  [ "$waits" -gt 0 ] && echo "# quiet gate: $c $s $m waited ${waits}x20s, load1 now $l0"
  read -r -a A <<<"$(arms_of "$c" "$s" "$m" "$arms")"
  nm=${s%@*}; off=0; [ "$s" != "$nm" ] && off=${s#*@}
  declare -A M=(); declare -A H=()
  k=${#A[@]}
  for i in $(seq 1 "$LAUNCHES"); do
    for p in $(seq 0 $((k - 1))); do
      V=${A[$(( (p + i - 1) % k ))]}; b=${V%#b}
      if [ "${DRY:-0}" = 1 ]; then out="$(GRID_OFF=$off GRID_FIXED=0 taskset -c "$CPU" "bin/$c/$b/run" "subj/$nm" "$m" 2>&1 | sed -E 's/ passes=.*//') ns/pass=1.00"
      else out=$(GRID_OFF=$off taskset -c "$CPU" "bin/$c/$b/run" "subj/$nm" "$m" 2>&1); fi
      ns=$(sed -n 's/.*ns\/pass=\([0-9.]*\).*/\1/p' <<<"$out")
      an=$(sed 's/ ns\/pass.*//' <<<"$out")
      M[$V]="${M[$V]:-} ${ns:-NaN}"; H[$V]=$an
      printf '%s\t%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t%s\n' "$PHASE" "$c" "$s" "$m" "$i" "$p" "$V" "${ns:-NaN}" "$an" "$(cut -d' ' -f1 /proc/loadavg)" "$(date +%s)" >> "$RAW"
    done
  done
  B=${A[0]}
  v0=$(med "${M[$B]}"); v0b=$(med "${M["$B#b"]}")
  fl=$(awk "BEGIN{x=$v0b-$v0; printf \"%.2f\", x<0?-x:x}")
  mt=$(sed -n 's/matches=\([0-9]*\).*/\1/p' <<<"${H[$B]}")
  for V in "${A[@]}"; do
    [ "$V" = "$B" ] && continue
    [ "${H[$V]}" = "${H[$B]}" ] || echo "# ANSWER MISMATCH $c $s $m $V: '${H[$V]}' vs base '${H[$B]}'"
    n=$(med "${M[$V]}")
    sp=$(tr ' ' '\n' <<<"${M[$V]}" | grep . | sort -g | awk -v md="$n" 'NR==1{lo=$1} {hi=$1} END{printf "%+.1f..%+.1f%%", 100*(lo-md)/md, 100*(hi-md)/md}')
    d=$(awk "BEGIN{printf \"%+.2f\", $n-$v0}")
    pm=-; [ "$m" = all ] && [ "${mt:-0}" -gt 0 ] && pm=$(awk "BEGIN{printf \"%+.3f\", ($n-$v0)/$mt}")
    vd=$(awk "BEGIN{x=$n-$v0; a=x<0?-x:x; print (a<=$fl)?\"NULL\":(x<0?\"WIN\":\"LOSS\")}")
    [ "$V" = "$B#b" ] && vd=A/A
    printf '%-10s %-34s %-5s %-6s %12s %12s %11s %9s %13s %10s %s\n' "$c" "$s" "$m" "$V" "$n" "$v0" "$d" "$fl" "$sp" "$pm" "$vd"
    rows=$((rows + 1))
  done
  groups_done=$((groups_done + 1))
  echo "# group $groups_done done: $c $s $m load1-at-start=$l0 waits=$waits"
  unset M H
done < <(groups "$PHASE")
echo
if [ -s "$OUT/counts.tsv" ]; then
  echo "## counters (counting builds bin/<cell>/<arm>/cnt, one pass, no clock; site(G1) = the cell's site counters, the walk's own)"
  echo "# calls = rx_search calls; uses = next_candidate calls; cold = uses on an empty state; cache_hit / cache_pass = uses served"
  echo "# from / passing over the cached block; xcall = served from a block an EARLIER call filled; skipped = member tests the"
  echo "# cache made unnecessary; head_* = the prologue; blocks = block evaluations; nbuf = buffers (streamed subjects: summed)"
  awk -F'\t' -v re="$CELLS_RE" 'NR==1 || $1 ~ re' "$OUT/counts.tsv"
fi
echo "time.sh: COMPLETE rows=$rows wall=$(( $(date +%s) - start ))s"
