#!/bin/bash
S=$S; W=/home/pcrec/projects/pcrec
k=$1; n=$2; shift 2
python3 -I $S/gen.py $k $n > $S/p.pat || { echo "$k $n GENFAIL"; exit; }
sz=$(stat -c %s $S/p.pat)
t0=$(date +%s.%N)
( ulimit -s ${STK:-432}; exec $W/scripts/watchdog -s ${WALL:-60} -m ${MEM:-2g} -S growsurv -- $S/pcrec_stk -p rx --features all "$@" -o $S/p.out.c --pattern "$(cat $S/p.pat)" ) >$S/p.log 2>&1
rc=$?
t1=$(date +%s.%N)
printf '%s n=%s len=%s rc=%s t=%.1fs :: %s\n' $k $n $sz $rc $(echo "$t1 - $t0" | bc) "$(tail -c 160 $S/p.log | tr '\n' ' ')"
