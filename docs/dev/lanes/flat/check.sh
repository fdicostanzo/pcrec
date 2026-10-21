#!/bin/bash
# flat/check.sh OUT -- the correctness gate (no clock). Exit 0 only if every leg is green and every plant is red
# on at least one cell. Writes OUT/check.log (one line per leg and cell) and prints a summary.
#
#   B  battery: every arm's fbat output == the walk's, three seeds (fbat.c's subjects: lengths 0..700, empty,
#      all-member, members at the last two bytes, slices around real matches)
#   S  the same battery under ASan+UBSan (the .san builds; exact-size heap subjects), rc 0 and output == the walk's
#   P  plants: F8.stale, F64.tail and F64.stale must DIFFER from the walk on the battery for at least one cell each (per cell
#      the verdict is RED = caught or EQUIV = no subject separates it; the cells listed)
#   R  real subjects: every arm's GRID_FIXED=0 answer (matches + hash over the whole subject, find-all) == the walk's
#   O  oracle: the walk's answer == libpcre2 10.46 (oracle.py) on each J1 cell's smallest subject; the anchors'
#      walk answer == grid2's own libpcre2 oracle.tsv line
set -u
OUT=${1:?usage: check.sh OUT}
HERE=$(cd "$(dirname "$0")" && pwd)
GRID2=${GRID2:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}
CPUS=${CPUS:-12-15}
LOG=$OUT/check.log; : > "$LOG"
export ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=print_stacktrace=1
T=$OUT/tmp/check; mkdir -p "$T"; : > "$T/answers.tsv"
fail=0
cells=$(ls "$OUT/bat")
for c in $cells; do
  b=$OUT/bat/$c; m=$(cat "$b/members")
  for seed in 1 2 3; do
    taskset -c "$CPUS" "$b/walk" "$m" "$b/corpus" $seed > "$T/$c.walk.$seed" || { echo "B $c walk seed=$seed RC" >> "$LOG"; fail=1; }
    for a in V1 F8 F64 M64; do
      taskset -c "$CPUS" "$b/$a" "$m" "$b/corpus" $seed > "$T/$c.$a.$seed"
      cmp -s "$T/$c.walk.$seed" "$T/$c.$a.$seed" && echo "B $c $a seed=$seed OK" >> "$LOG" || { echo "B $c $a seed=$seed FAIL" >> "$LOG"; fail=1; }
    done
    for a in walk V1 F8 F64 M64; do
      taskset -c "$CPUS" "$b/$a.san" "$m" "$b/corpus" $seed > "$T/$c.$a.san.$seed" 2> "$T/$c.$a.san.$seed.err"; rc=$?
      if [ $rc = 0 ] && [ ! -s "$T/$c.$a.san.$seed.err" ] && cmp -s "$T/$c.walk.$seed" "$T/$c.$a.san.$seed"; then echo "S $c $a seed=$seed OK" >> "$LOG"
      else echo "S $c $a seed=$seed FAIL rc=$rc" >> "$LOG"; fail=1; fi
    done
    for a in F8.stale F64.tail F64.stale; do
      taskset -c "$CPUS" "$b/$a" "$m" "$b/corpus" $seed > "$T/$c.$a.$seed"
      cmp -s "$T/$c.walk.$seed" "$T/$c.$a.$seed" && echo "P $c $a seed=$seed EQUIV" >> "$LOG" || echo "P $c $a seed=$seed RED $(diff "$T/$c.walk.$seed" "$T/$c.$a.$seed" | grep -c '^<') lines" >> "$LOG"
    done
  done
  for s in $(python3 -I "$HERE/../grid1/arms.py" "$OUT" groups timed | awk -F'\t' -v c="$c" '$1==c{print $2}'); do
    w=$(GRID_FIXED=0 taskset -c "$CPUS" "$OUT/bin/$c/walk/run" "$OUT/subj/$s" all | sed 's/ passes=.*//')
    echo "$c	$s	$w" >> "$T/answers.tsv"
    for a in V1 F8 F64 M64; do
      x=$(GRID_FIXED=0 taskset -c "$CPUS" "$OUT/bin/$c/$a/run" "$OUT/subj/$s" all | sed 's/ passes=.*//')
      [ "$x" = "$w" ] && echo "R $c $s $a OK $w" >> "$LOG" || { echo "R $c $s $a FAIL '$x' vs '$w'" >> "$LOG"; fail=1; }
    done
  done
done
# O: libpcre2 on the smallest subject of each J1 cell; grid2's oracle for the anchors
python3 -I "$HERE/oracle.py" "$OUT" "$T/answers.tsv" "$GRID2/oracle.tsv" >> "$LOG" || fail=1
for p in F8.stale F64.tail F64.stale; do
  red=$(awk -v p=$p '$1=="P" && $3==p && $5=="RED" {print $2}' "$LOG" | sort -u | tr '\n' ' ')
  echo "plant $p caught on: ${red:-NONE}"; [ -n "$red" ] || fail=1
done
for leg in B S R O; do printf '%s ok=%s fail=%s  ' $leg "$(awk -v l=$leg '$1==l' "$LOG" | grep -c ' OK')" "$(awk -v l=$leg '$1==l' "$LOG" | grep -c ' FAIL')"; done; echo
[ $fail = 0 ] && echo "check: GREEN" || echo "check: RED (see $LOG)"
exit $fail
