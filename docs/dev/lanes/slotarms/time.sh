#!/bin/bash
# slotarms/time.sh -- times the pcrec-engine arms with the kit harness's method (vecspike/time.sh):
# per (cell, subject, mode): LAUNCHES interleaved launches of V0 and V0b (the SAME binary twice; |V0b - V0|
# is the A/A floor), each pinned to CPU, each launch = drv.c's median of 7 calibrated rounds; the row is the
# median over launches. Prints ABSOLUTE ns/pass (there is no variant to subtract). NOT run by this lane.
#   bash time.sh --estimate      # row count and wall estimate, nothing timed
#   OUT=... CPU=14 LAUNCHES=5 bash time.sh > time.log 2>&1      # completion: "time.sh: COMPLETE rows=N wall=Ss"
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
OUT=${OUT:-$ROOT/build/slotarms}
CPU=${CPU:-14}
LAUNCHES=${LAUNCHES:-5}
LOADMAX=${LOADMAX:-1.5}
SEC_PER_RUN=${SEC_PER_RUN:-0.65}
CELLS=${CELLS:-$(grep -v '^#' "$HERE/arms.tsv" | cut -f1 | tr '\n' ' ')}
# the (subject, mode) list per family: C_call off `first` on tiny no-match subjects, c_byte off the 64 KiB
# no-match subject, C_match off find-all at one match per 8/64/1Ki bytes
rowsfor() { local f=$1
  for s in e0 nm8 nm64 nm1k nm64k; do echo "$s first"; done
  for L in 8 64 1k; do echo "m$f-L$L all"; done; }
fam_of() { grep -v '^#' "$HERE/arms.tsv" | awk -F'\t' -v c="$1" '$1==c{print $4}'; }
if [ "${1:-}" = --estimate ]; then
  rows=0; for c in $CELLS; do rows=$((rows + $(rowsfor "$(fam_of "$c")" | wc -l))); done
  echo "estimate: $rows timed rows x $((LAUNCHES * 2)) launches x ${SEC_PER_RUN}s = $(awk "BEGIN{printf \"%.1f\", $rows*$LAUNCHES*2*$SEC_PER_RUN/60}") min (+ load-guard waits)"
  exit 0
fi
cd "$OUT" || exit 2
start=$(date +%s)
echo "# slotarms time.sh $(date -u) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) cpu=$CPU launches=$LAUNCHES"
echo "# ns = ns per pass (median over launches of each launch's 7-round median); floor = |V0b - V0| (A/A)"
printf '%-8s %-9s %-5s %8s %12s %9s %s\n' cell subject mode matches ns floor answer
med() { tr ' ' '\n' <<<"$1" | grep . | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}'; }
rows=0
for c in $CELLS; do
  while read -r s m; do
    for t in $(seq 1 60); do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($l < $LOADMAX)}" && break; sleep 20; done
    A=""; B=""; H=""
    for i in $(seq 1 "$LAUNCHES"); do
      for V in V0 V0b; do
        out=$(taskset -c "$CPU" "bin/$c/V0/run" "subj/$s" "$m")
        v=$(sed -n 's/.*ns\/pass=\([0-9.]*\).*/\1/p' <<<"$out"); H=$(sed 's/ ns\/pass.*//' <<<"$out")
        if [ $V = V0 ]; then A="$A $v"; else B="$B $v"; fi
      done
    done
    a=$(med "$A"); b=$(med "$B"); fl=$(awk "BEGIN{x=$b-$a; printf \"%.2f\", x<0?-x:x}")
    printf '%-8s %-9s %-5s %8s %12s %9s %s\n' "$c" "$s" "$m" "$(sed -n 's/matches=\([0-9]*\).*/\1/p' <<<"$H")" "$a" "$fl" "$H"
    rows=$((rows + 1))
  done < <(rowsfor "$(fam_of "$c")")
done
echo "time.sh: COMPLETE rows=$rows wall=$(( $(date +%s) - start ))s"
