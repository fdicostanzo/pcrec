#!/bin/bash
# probex.sh KIND N [pcrec args]: .rxt route (no 128KB arg limit); STK kb (default 8192)
S=$S; W=/home/pcrec/projects/pcrec
k=$1; n=$2; shift 2
(printf 'pattern '; python3 -I $S/gen.py $k $n; echo) > $S/px.rxt
sz=$(stat -c %s $S/px.rxt); t0=$(date +%s.%N)
( ulimit -s ${STK:-8192}; exec $W/scripts/watchdog -s ${WALL:-60} -m ${MEM:-2g} -S growsurv -- $S/pcrec_stk -p rx --features all "$@" -o $S/px.out.c $S/px.rxt ) >$S/px.log 2>&1
rc=$?; t1=$(date +%s.%N)
printf '%s n=%s len=%s stk=%s rc=%s t=%.1fs :: %s\n' $k $n $sz ${STK:-8192} $rc $(echo "$t1 - $t0" | bc) "$(tail -c 150 $S/px.log | tr '\n' ' ')"
