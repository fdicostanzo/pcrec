#!/bin/bash
# init.sh NAME N K "I list" SUBJ...   (uses NAME_base.c)
H="$(cd "$(dirname "$0")" && pwd)"
name=$1; n=$2; k=$3; il=$4; shift 4
python3 $H/twin.py ${name}_base.c ${name}_tw.c
gcc-16 -O2 -DTW_MODE=0 -DTW_INIT=0 -DTW_N=1 -DTW_K=1 -o ${name}_i_step ${name}_tw.c $H/drv.c
gcc-16 -O2 -DTW_MODE=1 -DTW_INIT=0 -DTW_N=1 -DTW_K=1 -o ${name}_i_rs ${name}_tw.c $H/drv.c
vs="step rs"; for i in $il; do gcc-16 -O2 -DTW_MODE=3 -DTW_INIT=$i -DTW_N=$n -DTW_K=$k -o ${name}_i_$i ${name}_tw.c $H/drv.c; vs="$vs $i"; done
echo "== $name N=$n K=$k"
for s in "$@"; do printf "%-14s" $(basename $s .bin); for v in $vs; do r=$(./${name}_i_$v $s 7); echo -n "$v=$(echo $r | sed 's/.*med_ns_per_B=\([0-9.]*\).*/\1/') "; done; echo; done
