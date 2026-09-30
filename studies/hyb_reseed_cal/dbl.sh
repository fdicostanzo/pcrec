#!/bin/bash
# dbl.sh NAME N K FIRST SHORT0 "CAPS" SUBJ...
H="$(cd "$(dirname "$0")" && pwd)"
name=$1; n=$2; k=$3; f=$4; s0=$5; caps=$6; shift 6
python3 $H/twin.py ${name}_base.c ${name}_tw.c
gcc-16 -O2 -DTW_MODE=0 -DTW_INIT=0 -DTW_SHORT0=0 -DTW_N=1 -DTW_K=1 -o ${name}_d_step ${name}_tw.c $H/drv.c
gcc-16 -O2 -DTW_MODE=3 -DTW_INIT=$f -DTW_SHORT0=$s0 -DTW_N=$n -DTW_K=$k -o ${name}_d_nodbl ${name}_tw.c $H/drv.c
vs="step nodbl"; for c in $caps; do gcc-16 -O2 -DTW_MODE=6 -DTW_INIT=$f -DTW_SHORT0=$s0 -DTW_N=$n -DTW_K=$k -DTW_CAP=$c -o ${name}_d_$c ${name}_tw.c $H/drv.c; vs="$vs $c"; done
echo "== $name N=$n K=$k first=$f short0=$s0"
for s in "$@"; do printf "%-14s" $(basename $s .bin); for v in $vs; do r=$(./${name}_d_$v $s 7); echo -n "$v=$(echo $r | sed 's/.*med_ns_per_B=\([0-9.]*\).*/\1/') "; done; echo; done
