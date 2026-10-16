#!/bin/bash
# grid2/f2perf.sh -- the OPTIONAL perf passes of the zen4-grid2 slot (r17b_prime.md §5.4):
#   item 6  F2's branch-miss pass on the K arms {walk, V1, A1} of every item-1 group
#           (streamed subjects, the group's own mode);
#   item 7  F2's STREAMED pass: hex-run, bounded, dfa-hat x {walk V1 A1 A3} x prose/docs/code
#           (g2-real-*-S: 16 x 64 KiB windows of spike1's 1 MiB files).
# Both come from $OUT/arms_f2.tsv (design2.py). grid1/f2perf.sh's method, with the group's
# mode and a per-buffer byte count (a streamed subject is a directory).
#
#   OUT=... STATUS=$OUT/slot.status CPU=14 [F2_ITEM=6|7|both] bash f2perf.sh > $OUT/f2.log 2>&1
#   completion line: "f2perf: COMPLETE rows=<N> wall=<s>s"  or  "f2perf: SKIPPED <why>"
#
# PERMISSION FIRST: `perf stat` must be usable by this user (kernel.perf_event_paranoid <= 2).
# When it is not, the script writes F2_SKIPPED to the status file, PRINTS THE SUGGESTION
# (paranoid.sh: the current paranoid level, that 2 or lower enables this pass, what it adds, the
# two commands), records `counters skipped:perf_event_paranoid=N` in the provenance, and exits
# 0. It never runs sysctl or sudo and never writes under /etc. Perf is never required (D166
# add. 1): a skip changes nothing downstream.
#
# METHOD (no wall clock): each cell runs the arm's own driver in fixed mode (gdrv.c
# GRID_FIXED=K: one answer pass + K passes) and once with K = 0 (the answer pass alone); the
# counts' difference over K is the per-pass count. Events: cycles, instructions, branches,
# branch-misses (user space only, `:u`). LAUNCHES launches per cell, interleaved across the
# cell's arms, every one recorded in $OUT/f2/raw.tsv.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
G1=$(cd "$HERE/../grid1" && pwd)
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}
STATUS=${STATUS:-$OUT/f2.status}
CPU=${CPU:-14}
LAUNCHES=${LAUNCHES:-3}
EVENTS=${EVENTS:-cycles:u,instructions:u,branches:u,branch-misses:u}
start=$(date +%s)
cd "$OUT" || exit 2
. "$HERE/paranoid.sh"
F2_ITEM=${F2_ITEM:-both}
skip() { echo "F2_SKIPPED $* $(date -Is)" >> "$STATUS"; echo "f2perf: SKIPPED $*"; paranoid_report /dev/null "$STATUS"; exit 0; }

if ! perf_probe; then skip "perf_event_paranoid=$(paranoid_level): ${PERF_WHY}"; fi
par=$(paranoid_level)

mkdir -p "$OUT/f2"
RAW=$OUT/f2/raw.tsv
printf 'cell\tsubject\tarm\tlaunch\tK\tevent\tcount_K\tcount_0\tper_pass\n' > "$RAW"
excluded() { grep -qx "$1 $2" "$OUT/excluded" 2>/dev/null; }
pstat() {   # K bin subj mode off -> "event value" lines
  GRID_OFF=$5 GRID_FIXED=$1 perf stat -x, -e "$EVENTS" -- taskset -c "$CPU" "$2" "$3" "$4" 2>&1 >/dev/null |
    awk -F, '$3 ~ /:u$|^[a-z-]+$/ && $1 ~ /^[0-9]+$/ {print $3" "$1}'
}
echo "# grid2 f2perf $(date -u) $(uname -n) paranoid=$par cpu=$CPU launches=$LAUNCHES events=$EVENTS"
printf '%-8s %-9s %-5s %16s %16s %14s %14s %12s\n' cell subject arm cycles/pass instr/pass branches/pass misses/pass misses/KiB
rows=0
# item 6: the K arms {walk V1 A1} of every item-1 group, read from groups2.tsv (item 1, 2 or 12;
# f3-wcls is not an item-1 group); item 7: arms_f2.tsv's g2-real-* rows (the gate-only rows are never perf'd)
: > "$OUT/tmp/f2.groups"
if [ "$F2_ITEM" = 6 ] || [ "$F2_ITEM" = both ]; then
  awk -F'\t' 'NR > 1 && ($1 == 1 || $1 == 12 || $1 == 2) && $2 != "f3-wcls" {
      n = split($5, a, ","); o = ""
      for (i = 1; i <= n; i++) if (a[i] == "walk" || a[i] == "V1" || a[i] == "A1") o = o (o == "" ? "" : ",") a[i]
      print $2 "\t" $3 "\t" $4 "\t" o }' "$OUT/groups2.tsv" >> "$OUT/tmp/f2.groups"
fi
if [ "$F2_ITEM" = 7 ] || [ "$F2_ITEM" = both ]; then
  python3 -I "$G1/arms.py" "$OUT" groups f2 | awk -F'\t' '$2 ~ /^g2-real-/' >> "$OUT/tmp/f2.groups"
fi
while IFS=$'\t' read -r c s m arms; do
  nm=${s%@*}; off=0; [ "$s" != "$nm" ] && off=${s#*@}
  if [ -d "subj/$nm" ]; then n=$(stat -c %s "subj/$nm/$(ls "subj/$nm" | grep -v '^\.' | head -1)"); else n=$(stat -c %s "subj/$nm"); fi
  K=64; [ "$n" -le 262144 ] && K=1024
  declare -A V=()
  for i in $(seq 1 "$LAUNCHES"); do
    for a in ${arms//,/ }; do
      excluded "$c" "$a" && continue
      declare -A Z=(); declare -A Q=()
      while read -r ev val; do Z[$ev]=$val; done < <(pstat 0 "bin/$c/$a/run" "subj/$nm" "$m" "$off")
      while read -r ev val; do Q[$ev]=$val; done < <(pstat "$K" "bin/$c/$a/run" "subj/$nm" "$m" "$off")
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
echo "F2_DONE item=$F2_ITEM rows=$rows wall=$(( $(date +%s) - start ))s $(date -Is)" >> "$STATUS"
echo "f2perf: COMPLETE rows=$rows wall=$(( $(date +%s) - start ))s"
