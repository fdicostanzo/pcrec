#!/bin/bash
# rr.sh CELL MODE ITERS FILES... : 6 launches each of CELL.a / CELL.d round-robin
c=$1; mode=$2; it=$3; shift 3
ra=""; rd=""
for l in 1 2 3 4 5 6; do ra="$ra $(timeout 120 ./$c.a $mode $it 7 "$@" | cut -d' ' -f1)"; rd="$rd $(timeout 120 ./$c.d $mode $it 7 "$@" | cut -d' ' -f1)"; done
ha=$(./$c.a $mode 1 1 "$@" | cut -d' ' -f3); hd=$(./$c.d $mode 1 1 "$@" | cut -d' ' -f3)
python3 -c "
import statistics as s; a=sorted(float(x) for x in '$ra'.split()); d=sorted(float(x) for x in '$rd'.split())
print('%-8s %s adaptive=%.0f deny=%.0f adaptive/deny=x%.3f  a=[%.0f..%.0f] d=[%.0f..%.0f] answers-same=%s'%('$c','$mode',s.median(a),s.median(d),s.median(a)/s.median(d),a[0],a[-1],d[0],d[-1],'$ha'=='$hd'))"
