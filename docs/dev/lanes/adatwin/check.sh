#!/bin/bash
# adatwin/check.sh OUT -- the correctness gate (no clock), flat/check.sh's legs with adatwin's arms. Exit 0 only if
# every leg is green, every plant is red on at least one cell, and both adaptive switches were exercised. Writes
# OUT/check.log (one line per leg and cell), OUT/switch_real.tsv (real-subject mode counts) and prints a summary.
#
#   B  battery (abat.c: flat's subjects plus kind 6, long dense/sparse alternations): every arm's output == the walk's,
#      three seeds
#   S  the same battery under ASan+UBSan, rc 0 and output == the walk's
#   P  plants ADAPT.sw, ADAPT.wlo, ADAPTC.sw must DIFFER from the walk on the battery for at least one cell each
#   X  the -DADAPT_COUNT battery builds (seed 1): the summed M->W and W->M switch counts of ADAPT and ADAPTC must both
#      be > 0 (the battery reaches both directions of the mode switch, which is where the plants sit)
#   R  real subjects: every arm's GRID_FIXED=0 answer == the walk's; the count builds' mode counts to switch_real.tsv
#   O  oracle: the walk's answer == libpcre2 10.46 (flat/oracle.py) on each J1 cell's smallest subject; the anchors'
#      walk answer == grid2's own libpcre2 oracle.tsv line
set -u
OUT=${1:?usage: check.sh OUT}
HERE=$(cd "$(dirname "$0")" && pwd)
FLAT=$(cd "$HERE/../flat" && pwd)
ARMS="V1 M64 OBS ADAPT ADAPTC ADAPT1C"
PLANTS="ADAPT.sw ADAPT.wlo ADAPTC.sw"
GRID2=${GRID2:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}
CPUS=${CPUS:-12-15}
LOG=$OUT/check.log; : > "$LOG"
export ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=print_stacktrace=1
T=$OUT/tmp/check; mkdir -p "$T"; : > "$T/answers.tsv"
printf 'cell\tsubject\tarm\tbytes\tmask_stretches\twalk_stretches\tswitch_mw\tswitch_wm\n' > "$OUT/switch_real.tsv"
fail=0
cells=$(ls "$OUT/bat")
for c in $cells; do
  b=$OUT/bat/$c; m=$(cat "$b/members")
  for seed in 1 2 3; do
    taskset -c "$CPUS" "$b/walk" "$m" "$b/corpus" $seed > "$T/$c.walk.$seed" || { echo "B $c walk seed=$seed RC" >> "$LOG"; fail=1; }
    for a in $ARMS; do
      taskset -c "$CPUS" "$b/$a" "$m" "$b/corpus" $seed > "$T/$c.$a.$seed"
      cmp -s "$T/$c.walk.$seed" "$T/$c.$a.$seed" && echo "B $c $a seed=$seed OK" >> "$LOG" || { echo "B $c $a seed=$seed FAIL" >> "$LOG"; fail=1; }
    done
    for a in walk $ARMS; do
      taskset -c "$CPUS" "$b/$a.san" "$m" "$b/corpus" $seed > "$T/$c.$a.san.$seed" 2> "$T/$c.$a.san.$seed.err"; rc=$?
      if [ $rc = 0 ] && [ ! -s "$T/$c.$a.san.$seed.err" ] && cmp -s "$T/$c.walk.$seed" "$T/$c.$a.san.$seed"; then echo "S $c $a seed=$seed OK" >> "$LOG"
      else echo "S $c $a seed=$seed FAIL rc=$rc" >> "$LOG"; fail=1; fi
    done
    for a in $PLANTS; do
      taskset -c "$CPUS" "$b/$a" "$m" "$b/corpus" $seed > "$T/$c.$a.$seed"
      cmp -s "$T/$c.walk.$seed" "$T/$c.$a.$seed" && echo "P $c $a seed=$seed EQUIV" >> "$LOG" || echo "P $c $a seed=$seed RED $(diff "$T/$c.walk.$seed" "$T/$c.$a.$seed" | grep -c '^<') lines" >> "$LOG"
    done
  done
  for a in ADAPT ADAPTC; do
    taskset -c "$CPUS" "$b/$a.cnt" "$m" "$b/corpus" 1 2> "$T/$c.$a.cnt.err" > /dev/null
    echo "X $c $a $(tr -d '\n' < "$T/$c.$a.cnt.err")" >> "$LOG"
  done
  for s in $(python3 -I "$HERE/../grid1/arms.py" "$OUT" groups timed | awk -F'\t' -v c="$c" '$1==c{print $2}'); do
    w=$(GRID_FIXED=0 taskset -c "$CPUS" "$OUT/bin/$c/walk/run" "$OUT/subj/$s" all | sed 's/ passes=.*//')
    echo "$c	$s	$w" >> "$T/answers.tsv"
    for a in ADAPT ADAPTC ADAPT1C; do
      p=$OUT/subj/$s; by=$( [ -d "$p" ] && cat "$p"/b* | wc -c || wc -c < "$p")
      ct=$(GRID_FIXED=0 taskset -c "$CPUS" "$OUT/bin/$c/$a/cnt" "$p" all 2>&1 >/dev/null | sed -n 's/^adapt: //p' | tr ' ' '\n' | sed 's/.*=//' | tr '\n' '\t')
      printf '%s\t%s\t%s\t%s\t%s\n' "$c" "$s" "$a" "$by" "${ct%$'\t'}" >> "$OUT/switch_real.tsv"
    done
    for a in $ARMS; do
      x=$(GRID_FIXED=0 taskset -c "$CPUS" "$OUT/bin/$c/$a/run" "$OUT/subj/$s" all | sed 's/ passes=.*//')
      [ "$x" = "$w" ] && echo "R $c $s $a OK $w" >> "$LOG" || { echo "R $c $s $a FAIL '$x' vs '$w'" >> "$LOG"; fail=1; }
    done
  done
done
# O: libpcre2 on the smallest subject of each J1 cell; grid2's oracle for the anchors
python3 -I "$FLAT/oracle.py" "$OUT" "$T/answers.tsv" "$GRID2/oracle.tsv" >> "$LOG" || fail=1
for p in $PLANTS; do
  red=$(awk -v p=$p '$1=="P" && $3==p && $5=="RED" {print $2}' "$LOG" | sort -u | tr '\n' ' ')
  echo "plant $p caught on: ${red:-NONE}"; [ -n "$red" ] || fail=1
done
for a in ADAPT ADAPTC; do
  mw=$(awk -v a=$a '$1=="X" && $3==a' "$LOG" | sed -n 's/.*switch_mw=\([0-9]*\).*/\1/p' | awk '{s+=$1} END{print s+0}')
  wm=$(awk -v a=$a '$1=="X" && $3==a' "$LOG" | sed -n 's/.*switch_wm=\([0-9]*\).*/\1/p' | awk '{s+=$1} END{print s+0}')
  echo "switches $a battery seed 1: M->W $mw  W->M $wm"; { [ "$mw" -gt 0 ] && [ "$wm" -gt 0 ]; } || fail=1
done
for leg in B S R O; do printf '%s ok=%s fail=%s  ' $leg "$(awk -v l=$leg '$1==l' "$LOG" | grep -c ' OK')" "$(awk -v l=$leg '$1==l' "$LOG" | grep -c ' FAIL')"; done; echo
[ $fail = 0 ] && echo "check: GREEN" || echo "check: RED (see $LOG)"
exit $fail
