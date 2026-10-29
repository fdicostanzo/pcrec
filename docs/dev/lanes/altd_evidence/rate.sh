#!/bin/bash
# rate.sh : per-call instructions:u ((11-1)/10) [+ min-of-5 cycles:u unless NOCYC] for altd twins; _in NF=4M NT=64M
V=/var/tmp/pcrec-pcrec/scratch/vmbc; A=/var/tmp/pcrec-pcrec/scratch/altd; T=/home/pcrec/projects/pcrec-bench/bench/unusual/throughput
cnt() { perf stat -x, -e $1 "${@:2}" 2>&1 >/dev/null | awk -F, 'NR==1{print $1}'; }
per() { local ev=$1; shift; local a b; a=$(REPS=11 cnt $ev "$@"); b=$(REPS=1 cnt $ev "$@"); echo "scale=2; ($a-$b)/10/1000000" | bc; }
minc() { local m=; for i in 1 2 3 4 5; do v=$(per cycles:u "$@"); if [ -z "$m" ] || [ "$(echo "$v < $m" | bc)" = 1 ]; then m=$v; fi; done; echo $m; }
dir() { case $1 in stock|BCd) echo $V/b/${2}_$1;; *) echo $A/b/${2}_$1;; esac; }
export NF=4194304 NT=67108864
for s in ${SUBJ:-nest-paren-32k nest-brace-100k js-1m idents-1m splice-1m comment-5m}; do
  k=cscan; [ $s = js-1m ] && k=json
  line="$s"
  for m in ${MODES:-stock stock_A stock_AL BCd BCd_A BCd_AL}; do
    d=$(dir $m $k)
    i=$(per instructions:u $d/drv $T/$s.bin r)
    c=$([ -n "$NOCYC" ] && echo - || minc $d/drv $T/$s.bin r)
    p=$([ -x $d/pdrv ] && $d/pdrv $T/$s.bin | sed 's/.*pushes\/byte=//' || echo -)
    line="$line $m i=$i c=$c p=$p"
  done
  echo "$line load=$(cut -d' ' -f1 /proc/loadavg)"
done
