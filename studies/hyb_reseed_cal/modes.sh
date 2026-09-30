#!/bin/bash
# modes.sh NAME N K SUBJ...   (NAME.c already emitted)
H="$(cd "$(dirname "$0")" && pwd)"
name=$1; n=$2; k=$3; shift 3
python3 $H/twin.py $name.c ${name}_tw.c
for m in 0 1 3 4 5; do gcc-16 -O2 -DTW_MODE=$m -DTW_INIT=0 -DTW_N=$n -DTW_K=$k -o ${name}_m$m ${name}_tw.c $H/drv.c || exit 1; done
echo "== $name N=$n K=$k  (m0 step, m1 reseed, m3 2gap, m4 2gap+entry, m5 1gap+entry)"
for s in "$@"; do printf "%-14s" $(basename $s .bin); for m in 0 1 3 4 5; do r=$(./${name}_m$m $s 7); echo -n "m$m=$(echo $r | sed 's/.*med_ns_per_B=\([0-9.]*\).*/\1/') "; done; echo; done
