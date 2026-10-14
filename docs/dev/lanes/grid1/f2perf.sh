#!/bin/bash
# grid1/f2perf.sh -- costmodel §F row F2: the perf BRANCH-MISS pass on the 1 MiB
# dense rows the cost model misses (hex-run, bounded, dfa-hat x prose1m,
# docs1m, code1m x walk, V1, A1, A3), with the same at 64 KiB as the
# learned-predictor control: arms_f2.tsv, 3 x 6 x 4 = 72 (arm, subject) cells,
# find-all mode.
#
#   OUT=... STATUS=$OUT/slot.status CPU=14 bash f2perf.sh > $OUT/f2.log 2>&1
#   completion line: "f2perf: COMPLETE rows=<N> wall=<s>s"  or  "f2perf: SKIPPED <why>"
#
# PERMISSION FIRST: `perf stat` must be usable by this user. On this box
# kernel.perf_event_paranoid is 4 (user perf denied); the script then writes a
# NAMED line "F2_SKIPPED ..." to the status file and exits 0. It never tries
# to change the setting.
#
# METHOD (no wall clock): each cell runs the arm's own driver in fixed mode
# (gdrv.c GRID_FIXED=K: one answer pass + K passes) and once with K = 0 (the
# answer pass alone: the load and the first pass); the counts' difference over
# K is the per-pass count. Events: cycles, instructions, branches,
# branch-misses (user space only, `:u`). LAUNCHES launches per cell,
# interleaved across the cell's four arms, every one recorded in
# $OUT/f2/raw.tsv; the summary prints the per-pass median and misses per KiB.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid1}
STATUS=${STATUS:-$OUT/f2.status}
CPU=${CPU:-14}
LAUNCHES=${LAUNCHES:-3}
EVENTS=${EVENTS:-cycles:u,instructions:u,branches:u,branch-misses:u}
start=$(date +%s)
cd "$OUT" || exit 2
skip() { echo "F2_SKIPPED $* $(date -Is)" >> "$STATUS"; echo "f2perf: SKIPPED $*"; exit 0; }

command -v perf > /dev/null || skip "no perf binary on PATH"
par=$(cat /proc/sys/kernel/perf_event_paranoid 2>/dev/null || echo '?')
if ! perf stat -x, -e "$EVENTS" -- true > "$OUT/tmp/f2.probe" 2>&1; then
  skip "perf_event_paranoid=$par: perf stat denied to this user ($(grep -m1 -iE 'access to|denied|permission' "$OUT/tmp/f2.probe" | cut -c1-120))"
fi
grep -q 'not supported\|not counted' "$OUT/tmp/f2.probe" && skip "perf_event_paranoid=$par: events not counted ($(head -c 200 "$OUT/tmp/f2.probe" | tr '\n' ' '))"

mkdir -p "$OUT/f2"
RAW=$OUT/f2/raw.tsv
printf 'cell\tsubject\tarm\tlaunch\tK\tevent\tcount_K\tcount_0\tper_pass\n' > "$RAW"
excluded() { grep -qx "$1 $2" "$OUT/excluded" 2>/dev/null; }
pstat() {   # K bin subj -> "event value" lines
  GRID_FIXED=$1 perf stat -x, -e "$EVENTS" -- taskset -c "$CPU" "$2" "$3" all 2>&1 >/dev/null |
    awk -F, '$3 ~ /:u$|^[a-z-]+$/ && $1 ~ /^[0-9]+$/ {print $3" "$1}'
}
echo "# grid1 f2perf $(date -u) $(uname -n) paranoid=$par cpu=$CPU launches=$LAUNCHES events=$EVENTS"
printf '%-8s %-9s %-5s %16s %16s %14s %14s %12s\n' cell subject arm cycles/pass instr/pass branches/pass misses/pass misses/KiB
rows=0
python3 -I "$HERE/arms.py" "$OUT" groups f2 > "$OUT/tmp/f2.groups"
while IFS=$'\t' read -r c s m arms; do
  n=$(stat -c %s "subj/$s"); K=64; [ "$n" -le 262144 ] && K=1024
  declare -A V=()
  for i in $(seq 1 "$LAUNCHES"); do
    for a in ${arms//,/ }; do
      excluded "$c" "$a" && continue
      declare -A Z=(); declare -A Q=()
      while read -r ev val; do Z[$ev]=$val; done < <(pstat 0 "bin/$c/$a/run" "subj/$s")
      while read -r ev val; do Q[$ev]=$val; done < <(pstat "$K" "bin/$c/$a/run" "subj/$s")
      for ev in "${!Q[@]}"; do
        pp=$(awk -v a="${Q[$ev]}" -v b="${Z[$ev]:-0}" -v k="$K" 'BEGIN{printf "%.2f", (a-b)/k}')
        printf '%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\n' "$c" "$s" "$a" "$i" "$K" "$ev" "${Q[$ev]}" "${Z[$ev]:-0}" "$pp" >> "$RAW"
        V["$a|$ev"]="${V["$a|$ev"]:-} $pp"
      done
      unset Z Q
    done
  done
  med() { tr ' ' '\n' <<<"$1" | grep . | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}'; }
  for a in ${arms//,/ }; do
    excluded "$c" "$a" && continue
    cy=$(med "${V["$a|cycles:u"]:-}"); in=$(med "${V["$a|instructions:u"]:-}")
    br=$(med "${V["$a|branches:u"]:-}"); bm=$(med "${V["$a|branch-misses:u"]:-}")
    mk=$(awk -v x="${bm:-0}" -v n="$n" 'BEGIN{printf "%.3f", x*1024/n}')
    printf '%-8s %-9s %-5s %16s %16s %14s %14s %12s\n' "$c" "$s" "$a" "$cy" "$in" "$br" "$bm" "$mk"
    rows=$((rows + 1))
  done
  unset V
done < "$OUT/tmp/f2.groups"
echo "F2_DONE rows=$rows wall=$(( $(date +%s) - start ))s $(date -Is)" >> "$STATUS"
echo "f2perf: COMPLETE rows=$rows wall=$(( $(date +%s) - start ))s"
