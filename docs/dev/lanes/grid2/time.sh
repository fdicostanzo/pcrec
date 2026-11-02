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
#   - the CROSS-LAUNCH TRIGGER [rev3 C7] beside it: a group in which ANY arm's per-launch medians
#     spread (max - min over the launches) by more than the group's own A/A floor
#     |median(base#b) - median(base)| gets the same RERUN_EXTRA more launches, once (the within-launch
#     rule cannot see a walk that is bimodal ACROSS launches, which gridread found). The threshold is
#     max(that A/A floor, NULL): a floor that happens to be ~0 must not make every group rerun
#     (DEVIATION from the spec's text, which names the A/A floor alone; stated in grid2r3_report.md);
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
#   bash time.sh --estimate | --counts | --paranoid | --selftest-resume
#
# RESUME (rulepilot, 2026-11-02): RESUME=1 with an existing raw file skips every group already COMPLETE
# in it and re-times the rest whole. A group is complete only when the log (RESUME_LOG, default
# $OUT/time_<RAW_TAG|PHASE>.log; the caller APPENDS to it) has its "# group N done: CELL SUBJ MODE ..."
# line(s) AND the raw file holds exactly launches x arms-per-launch rows for it (summed over its done lines,
# a BREACH requeue adds a second one). The rows of a group in this run's list that is NOT complete (the
# group in progress at a kill) are moved to $RAW.discarded and the group runs again whole; the raw file is
# otherwise only appended to. Each group launches its OWN base copies, so a resumed group is
# methodologically identical to an uninterrupted one (no state crosses a group boundary but the quiet gate).
# GROUPS_FILE=F (lines "cell<TAB>subject<TAB>mode") restricts the run to those groups, in the phase's order.
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
SEC_STREAM=${SEC_STREAM:-0.65}  # a launch of a streamed 4 MiB subject: MEASURED by the DRY run (0.61-0.65 s; grid1's 64 MiB streams cost 0.95 s)
RERUN_SHARE=${RERUN_SHARE:-0.2} # estimate only: EP69
STEP=${1:-time}
cd "$OUT" || exit 2
. "$HERE/paranoid.sh"
start=$(date +%s)
mkdir -p "$OUT/time"

excluded() { grep -qx "$1 $2" "$OUT/excluded" 2>/dev/null; }
unreached() { grep -qxF "$(printf '%s\t%s\t%s' "$1" "$2" "$3")" "$OUT/unreached" 2>/dev/null; }
groups() {
  python3 -I "$G1/arms.py" "$OUT" groups timed "$1" | awk -F'\t' -v re="$CELLS_RE" '$1 ~ re' |
  if [ -n "${GROUPS_FILE:-}" ]; then awk -F'\t' 'NR==FNR{k[$1"\t"$2"\t"$3]=1; next} (($1"\t"$2"\t"$3) in k)' "$GROUPS_FILE" -; else cat; fi
}
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

declare -A DONE=()
resume_prepare() {   # RAW LOG: fill DONE[cell|subj|mode] for the complete groups, discard the partial ones' rows
  local raw=$1 log=$2 c s m a l n k key keep disc
  declare -A RC=() DL=()
  DONE=()
  if [ -s "$raw" ]; then
    while IFS=$'\t' read -r c s m n; do RC["$c|$s|$m"]=$n; done < <(awk -F'\t' 'NR>1{n[$2"\t"$3"\t"$4]++} END{for(x in n)print x"\t"n[x]}' "$raw")
  fi
  if [ -s "$log" ]; then
    while IFS=$'\t' read -r c s m l; do DL["$c|$s|$m"]=$(( ${DL["$c|$s|$m"]:-0} + l )); done < <(
      awk '/^# group [0-9]+ done: /{l=1; if(match($0, / launches=[0-9]+/)) l=substr($0, RSTART+10, RLENGTH-10); print $5"\t"$6"\t"$7"\t"l}' "$log")
  fi
  keep=$(mktemp "${RAWDIR:-$OUT/time}/.resume.XXXXXX")
  while IFS=$'\t' read -r c s m a; do
    key="$c|$s|$m"
    k=$(wc -w <<<"$(arms_of "$c" "$s" "$m" "$a")")
    if [ -n "${DL[$key]:-}" ] && [ "${RC[$key]:-0}" -eq $(( DL[$key] * k )) ]; then DONE[$key]=1; fi
    printf '%s\t%s\t%s\t%s\n' "$([ "${DONE[$key]:-}" = 1 ] && echo K || echo L)" "$c" "$s" "$m" >> "$keep"
  done < <(groups "$PHASE")
  if [ -s "$raw" ] && awk -F'\t' 'NR==FNR{if($1=="L")l[$2"\t"$3"\t"$4]=1; next} FNR>1 && (($2"\t"$3"\t"$4) in l){f=1} END{exit !f}' "$keep" "$raw"; then
    disc=$raw.discarded
    awk -F'\t' -v D="$disc" 'NR==FNR{if($1=="L")l[$2"\t"$3"\t"$4]=1; next} FNR==1{print; next} (($2"\t"$3"\t"$4) in l){print >> D; next} {print}' "$keep" "$raw" > "$keep.raw" &&
      mv "$keep.raw" "$raw"
    echo "# resume: partial group rows moved to $disc"
  fi
  rm -f "$keep" "$keep.raw"
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
  --selftest-resume)   # no clock, no binaries, no slot: fabricated raw + log in a scratch dir, groups/arms_of stubbed
    T=$(mktemp -d "${TMPDIR:-/var/tmp}/timesh_selftest.XXXXXX") || exit 2
    groups() { printf 'c1\ts1\tall\ta0,a1\nc1\ts2\tall\ta0,a1\nc2\ts1\tall\ta0,a1,a2\nc3\ts1\tall\ta0,a1\n'; }
    arms_of() { local n; case "$1" in c2) n=6;; *) n=5;; esac; seq 1 $n; }
    R=$T/raw.tsv; L=$T/log
    row() { printf 'EXT\t%s\t%s\tall\t1\t0\ta0\t1.00\tx\t0.1\t1\n' "$1" "$2" >> "$R"; }
    printf 'phase\tcell\tsubject\tmode\tround\tpos\tarm\tns\tanswer\tload1\tts\n' > "$R"
    for i in $(seq 15); do row c1 s1; done; echo '# group 1 done: c1 s1 all load1-at-start=1 load1-at-end=1 waits=0 launches=3' > "$L"   # complete (5 x 3)
    for i in $(seq 10); do row c1 s2; done                                                                                                  # killed mid-group, no done line
    for i in $(seq 18); do row c2 s1; done; echo '# group 2 done: c2 s1 all load1-at-start=1 load1-at-end=1 waits=0 launches=3' >> "$L"      # complete (6 x 3)
    for i in $(seq 14); do row c3 s1; done; echo '# group 3 done: c3 s1 all load1-at-start=1 load1-at-end=1 waits=0 launches=3' >> "$L"      # done line but 14 != 15 rows
    RAWDIR=$T; resume_prepare "$R" "$L" > /dev/null
    bad=0
    [ "${DONE[c1|s1|all]:-}" = 1 ] || { echo "FAIL: c1 s1 should be complete"; bad=1; }
    [ "${DONE[c2|s1|all]:-}" = 1 ] || { echo "FAIL: c2 s1 (6 arms) should be complete"; bad=1; }
    [ -z "${DONE[c1|s2|all]:-}" ] || { echo "FAIL: c1 s2 (no done line) must not be complete"; bad=1; }
    [ -z "${DONE[c3|s1|all]:-}" ] || { echo "FAIL: c3 s1 (short rows) must not be complete"; bad=1; }
    [ "$(awk -F'\t' 'NR>1 && $2=="c1" && $3=="s1"' "$R" | wc -l)" = 15 ] || { echo "FAIL: complete rows disturbed"; bad=1; }
    [ "$(awk -F'\t' 'NR>1 && $3=="s2"' "$R" | wc -l)" = 0 ] || { echo "FAIL: partial rows still in raw"; bad=1; }
    [ "$(wc -l < "$R.discarded")" = 24 ] || { echo "FAIL: discarded rows $(wc -l < "$R.discarded") != 24"; bad=1; }
    [ "$(head -1 "$R" | cut -f1)" = phase ] || { echo "FAIL: header lost"; bad=1; }
    rm -rf "$T"
    [ "$bad" = 0 ] && echo "selftest-resume: PASS (complete kept, partial and short groups discarded, header and complete rows intact)"
    exit "$bad" ;;
  *) echo "usage: time.sh [--estimate|--counts|--paranoid|--selftest-resume]"; exit 2 ;;
esac

RAWDIR=${RAWDIR:-$OUT/time}; mkdir -p "$RAWDIR"
RAW=$RAWDIR/raw_${RAW_TAG:-$PHASE}.tsv
RESUME=${RESUME:-0}
if [ "$RESUME" = 1 ] && [ -s "$RAW" ]; then
  resume_prepare "$RAW" "${RESUME_LOG:-$OUT/time_${RAW_TAG:-$PHASE}.log}"
  echo "# RESUME: ${#DONE[@]} groups already complete in $RAW are skipped; the rest run whole (each group launches its own base copies)"
else
  printf 'phase\tcell\tsubject\tmode\tround\tpos\tarm\tns\tanswer\tload1\tts\n' > "$RAW"
fi
[ "${NOCLOCK:-0}" = 1 ] && echo "# NOCLOCK RUN: no clock; every ns below is the placeholder 1.00"
echo "# grid2 time.sh method=$METHOD $(date -u) $(uname -n) phase=$PHASE load1=$(cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) cpu=$CPU launches=$LAUNCHES rerun_extra=$RERUN_EXTRA rerun_null=$RERUN_NULL cross_launch_trigger=on base_copies=$BASE_COPIES loadmax=$LOADMAX loadbreach=$LOADBREACH"
echo "# ns = ns per pass (median over launches of each launch's 7-round median); delta = arm - base; floor = |base#b - base| (A/A); aac = |base#c - base| (the held-out A/A);"
echo "# spread = per-launch min..max as % of the arm's median; per_match = delta / matches (all mode); verdict NULL when |delta| <= floor"
echo "# raw per-launch values: $RAW"
st=${PASS_STATUS:-$OUT/time_${PHASE}.status}; if [ "$RESUME" = 1 ]; then touch "$st"; else : > "$st"; fi
if ! perf_probe; then echo "# optional counter passes (items 6-7) will skip loudly:"; paranoid_report /dev/null "$st"; fi
printf '%-10s %-38s %-5s %-6s %12s %12s %11s %9s %9s %13s %10s %s\n' cell subject mode arm ns base delta floor aac spread per_match verdict
rows=0; skipped=0; groups_done=0; reruns=0; xreruns=0; requeued=0
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
      local medb nullv j bad=0 xbad=0 xthr flnow xarm xlo xhi pv
      medb=$(med "${M[$B]}"); nullv=$(awk -v m="$medb" -v e="$RERUN_NULL" 'BEGIN{print m*e}')
      for ((j = 1; j <= LAUNCHES; j++)); do
        awk -v a="${PL["$B,$j"]}" -v b="${PL["$B#b,$j"]}" -v n="$nullv" 'BEGIN{d=a-b; if(d<0)d=-d; exit !(d>n)}' && bad=1
      done
      # the cross-launch trigger [rev3 C7]
      flnow=$(awk -v a="$(med "${M[$B]}")" -v b="$(med "${M["$B#b"]:-${M[$B]}}")" 'BEGIN{d=a-b; if(d<0)d=-d; print d}')
      xthr=$(awk -v f="$flnow" -v n="$nullv" 'BEGIN{print (f>n)?f:n}')
      for V in "${A[@]}"; do
        xlo=; xhi=
        for ((j = 1; j <= LAUNCHES; j++)); do
          pv=${PL["$V,$j"]}
          xlo=$(awk -v a="$xlo" -v b="$pv" 'BEGIN{print (a==""||b<a)?b:a}'); xhi=$(awk -v a="$xhi" -v b="$pv" 'BEGIN{print (a==""||b>a)?b:a}')
        done
        awk -v lo="$xlo" -v hi="$xhi" -v t="$xthr" 'BEGIN{exit !(hi-lo>t)}' && { xbad=1; xarm=$V; }
      done
      if [ "$bad" = 1 ] || [ "$xbad" = 1 ]; then
        rr=1; reruns=$((reruns + 1)); nlaunch=$((LAUNCHES + RERUN_EXTRA))
        [ "$xbad" = 1 ] && xreruns=$((xreruns + 1))
        echo "# rerun: $c $s $m (within-launch A/A beyond NULL=$nullv: $bad; cross-launch spread of ${xarm:-none} beyond max(A/A floor, NULL)=$xthr: $xbad): +$RERUN_EXTRA launches"
      fi
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
  if [ "${DONE["$c|$s|$m"]:-}" = 1 ]; then skipped=$((skipped + 1)); continue; fi
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
echo "time.sh: COMPLETE rows=$rows groups=$groups_done reruns=$reruns xreruns=$xreruns requeued=$requeued wall=$(( $(date +%s) - start ))s resumed_skipped=$skipped"
