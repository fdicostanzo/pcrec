#!/bin/bash
# run_pairskip.sh ART_DIR CNT_DIR SUBJ_DIR TWINS_DIR — the entries (mk_count.py + stepcount.c, the
# dfa.md §2.2 instrument) and the boundary-pair stop count (pairskip_count.py) per cell; no clock.
H=$(dirname "$0"); A=$1; C=$2; S=$3; W=$4
for n in hex8-bounded wild-waf-crs-942140-dbnames wild-codegrammar-json-constant; do
  echo "=== $n"
  python3 -I $W/mk_count.py $A/$n.c $C/$n.cnt.c && cp $A/$n.h $C/$n.h || exit 1
  gcc -O2 -w -I$C -DRXH="\"$n.h\"" -o $C/$n.cnt $W/stepcount.c $C/$n.cnt.c || exit 1
  $C/$n.cnt $S/*.bin
  python3 -I $H/pairskip_count.py $A/$n.c $S/*.bin
done
