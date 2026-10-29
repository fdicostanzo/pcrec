#!/bin/bash
# rate.sh : per-call instructions:u ((11-1)/10), pushes/byte; _in NF=4M NT=64M (lane vmcons, altd's method)
S=/var/tmp/pcrec-pcrec/scratch/vmcons; T=/home/pcrec/projects/pcrec-bench/bench/unusual/throughput
cnt() { perf stat -x, -e $1 "${@:2}" 2>&1 >/dev/null | awk -F, 'NR==1{print $1}'; }
per() { local ev=$1; shift; local a b; a=$(REPS=11 cnt $ev "$@"); b=$(REPS=1 cnt $ev "$@"); echo "scale=2; ($a-$b)/10/1000000" | bc; }
export NF=4194304 NT=67108864
for s in ${SUBJ:-nest-paren-32k nest-brace-100k js-1m idents-1m splice-1m comment-5m}; do
  k=cscan; [ $s = js-1m ] && k=json
  line="$s"
  for m in $MODES; do
    d=$S/b/${k}_$m
    i=$(per instructions:u $d/drv $T/$s.bin r)
    p=$([ -x $d/pdrv ] && $d/pdrv $T/$s.bin | sed 's/.*pushes\/byte=//' || echo -)
    line="$line $m i=$i p=$p"
  done
  echo "$line load=$(cut -d' ' -f1 /proc/loadavg)"
done
