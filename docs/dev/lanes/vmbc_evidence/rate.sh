#!/bin/bash
# rate.sh : per-call instructions:u ((11-1)/10) and min-of-5 cycles:u, stock vs B/C/BC twins (D183 base), _in NF=4M NT=64M
V=/var/tmp/pcrec-pcrec/scratch/vmbc; T=/home/pcrec/projects/pcrec-bench/bench/unusual/throughput
cnt() { perf stat -x, -e $1 "${@:2}" 2>&1 >/dev/null | awk -F, 'NR==1{print $1}'; }
per() { local ev=$1; shift; local a b; a=$(REPS=11 cnt $ev "$@"); b=$(REPS=1 cnt $ev "$@"); echo "scale=2; ($a-$b)/10/1000000" | bc; }
minc() { local m=; for i in 1 2 3 4 5; do v=$(per cycles:u "$@"); if [ -z "$m" ] || [ "$(echo "$v < $m" | bc)" = 1 ]; then m=$v; fi; done; echo $m; }
export NF=4194304 NT=67108864
for s in ${SUBJ:-idents-1m nest-brace-100k splice-1m js-1m nest-paren-32k comment-5m}; do
  k=cscan; [ $s = js-1m ] && k=json
  line="$s"
  for m in ${MODES:-stock B C BC}; do
    i=$(per instructions:u $V/b/${k}_$m/drv $T/$s.bin r)
    c=$([ -n "$NOCYC" ] && echo - || minc $V/b/${k}_$m/drv $T/$s.bin r)
    line="$line $m i=$i c=$c"
  done
  echo "$line load=$(cut -d' ' -f1 /proc/loadavg)"
done
