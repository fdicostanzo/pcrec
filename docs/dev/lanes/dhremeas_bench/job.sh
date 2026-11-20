#!/usr/bin/env bash
# 200-dhremeas-timing: dense-hit re-measure, on vs off vs on2 (A/A), 3 cells x 7 launches
set -u
W=/home/pcrec/projects/pcrec/worktrees/dhremeas
B=/home/pcrec/projects/pcrec/build/pcrec
D=$W/docs/dev/lanes/dhremeas_bench
case "${1:-}" in
    --dry-run)
        [ -x "$B" ] || { echo "no $B" >&2; exit 1; }
        echo "would run: dhremeas timing, 3 cells x 3 arms x 7 launches"
        echo "boxqueue: cap 1800"; echo "boxqueue: patience none"; echo "boxqueue: est 600"
        echo "boxqueue: idle-ok"
        echo "boxqueue: expect none reason=exec'd summarize prints VERDICT, rc is the job's rc"
        exit 0 ;;
    --ready) exit 0 ;;
esac
S=/var/tmp/pcrec-pcrec/scratch/dhremeas/run; rm -rf "$S"; mkdir -p "$S"
cells=("dense_unb|[^@ ]+@x|dense" "dense_bnd|[^@ ]{1,5}@x|dense" "tail_unb|[^@ ]+@x|tail")
gcc -O2 -c "$D/driver.c" -o "$S/driver.o" || exit 1
for c in "${cells[@]}"; do
  IFS='|' read -r name pat kind <<<"$c"
  for arm in on off on2; do
    fl=""; [ "$arm" = off ] && fl="-fno-req-handoff"
    "$B" -p rx --emit-main -o "$S/$name.$arm.c" --pattern "$pat" --engine=vm $fl >/dev/null || exit 1
    gcc -O2 -Dmain=gen_main -c "$S/$name.$arm.c" -o "$S/$name.$arm.o" 2>/dev/null || exit 1
    gcc "$S/$name.$arm.o" "$S/driver.o" -o "$S/$name.$arm" || exit 1
  done
  grep -h "define RX_REQ_HANDOFF" "$S/$name.on.c" "$S/$name.off.c" | sed "s/^/$name /"
done
for round in 1 2 3 4 5 6 7; do
  for c in "${cells[@]}"; do
    IFS='|' read -r name pat kind <<<"$c"
    reps=1500; [ "$kind" = tail ] && reps=300
    case $((round % 3)) in 0) ord="on off on2";; 1) ord="off on2 on";; 2) ord="on2 on off";; esac
    for arm in $ord; do
      r=$("$S/$name.$arm" "$kind" $reps) || exit 1
      echo "T $name $arm ${r%% *}"
    done
  done
done | tee "$S/raw.txt"
python3 -I "$D/summarize.py" "$S/raw.txt" | tee "$S/summary.txt"
tail -1 "$S/summary.txt" | grep -q "^VERDICT"
