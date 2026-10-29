#!/bin/bash
# jit.sh : pcre2-jit (10.46, gap/p2 jg) instructions and min-of-5 cycles per call, same method as rate.sh
G=/var/tmp/pcrec-pcrec/scratch/trailgc2/gap; T=/home/pcrec/projects/pcrec-bench/bench/unusual/throughput; P=/home/pcrec/projects/pcrec-bench/bench/unusual/patterns
cnt() { perf stat -x, -e $1 "${@:2}" 2>&1 >/dev/null | awk -F, 'NR==1{print $1}'; }
per() { local ev=$1; shift; local a b; a=$(REPS=11 cnt $ev "$@"); b=$(REPS=1 cnt $ev "$@"); echo "scale=2; ($a-$b)/10/1000000" | bc; }
minc() { local m=; for i in 1 2 3 4 5; do v=$(per cycles:u "$@"); if [ -z "$m" ] || [ "$(echo "$v < $m" | bc)" = 1 ]; then m=$v; fi; done; echo $m; }
for s in ${SUBJ:-nest-paren-32k nest-brace-100k js-1m idents-1m splice-1m comment-5m}; do
  pf=$P/cscan-onig.rx; [ $s = js-1m ] && pf=$P/wild-json-validate-onig.rx
  echo "$s jit i=$(per instructions:u $G/p2 $pf $T/$s.bin jg) c=$(minc $G/p2 $pf $T/$s.bin jg) load=$(cut -d' ' -f1 /proc/loadavg)"
done
