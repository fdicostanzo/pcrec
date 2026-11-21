#!/bin/bash
S=$S
k=$1; n=$2; shift 2
python3 -I $S/gen.py $k $n > $S/h.pat
( ulimit -s ${STK:-432}; timeout 90 gdb -q -batch -x $S/gdbc3 --args $S/pcrec_stk -p rx --features all "$@" -o $S/h.out.c --pattern "$(cat $S/h.pat)" 2>&1 | grep -E '^#' | sed -E 's/^#[0-9]+ +(0x[0-9a-f]+ in )?([A-Za-z_0-9.]+).*/\2/' | sort | uniq -c | sort -rn | head -${TOP:-4} | awk '{printf "%s=%s ",$2,$1}')
echo "<= $k $n $*"
