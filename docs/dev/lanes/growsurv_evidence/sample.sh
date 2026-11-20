#!/bin/bash
# sample.sh KIND N SECS [args] : interrupt after SECS, print top frames
S=$S
k=$1; n=$2; t=$3; shift 3
python3 -I $S/gen.py $k $n > $S/s.pat
printf 'set pagination off\nset debuginfod enabled off\nrun\nbt 14\n' > $S/gdbs
( ulimit -v 6000000; timeout 120 gdb -q -batch -x $S/gdbs --args $S/pcrec_stk -p rx --features all "$@" -o $S/s.out.c --pattern "$(cat $S/s.pat)" > $S/s.log 2>&1 ) &
sleep $t
pid=$(pgrep -n -x pcrec_stk); [ -n "$pid" ] && kill -INT $pid
wait
grep -E '^#' $S/s.log | sed -E 's/\(.*\) at / at /; s#/home/pcrec/projects/pcrec/worktrees/growsurv/##; s/0x[0-9a-f]+ in //' | cut -c1-110
echo "<= $k $n"
