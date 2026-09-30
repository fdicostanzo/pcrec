#!/bin/bash
# bench.sh NAME PATTERN ENC "N K ..." SUBJ...
: "${PCREC_BASE:?set PCREC_BASE to the branch-point (abi 46) compiler}"; H="$(cd "$(dirname "$0")" && pwd)"
name=$1; pat=$2; enc=$3; nks=$4; shift 4
eopt=""; [ "$enc" = utf8 ] && eopt="-e utf8"
$PCREC_BASE --features all -p rx $eopt -o $name.c --pattern "$pat" || exit 1
python3 $H/twin.py $name.c ${name}_tw.c
fl=$(grep -h "VM_FRAMELESS" $name.c | awk '{print $3}')
gcc-16 -O2 -DTW_MODE=0 -DTW_INIT=0 -o ${name}_step ${name}_tw.c $H/drv.c
gcc-16 -O2 -DTW_MODE=1 -DTW_INIT=0 -o ${name}_reseed ${name}_tw.c $H/drv.c
vs="step reseed"
for nk in $nks; do n=${nk%,*}; k=${nk#*,}; gcc-16 -O2 -DTW_MODE=3 -DTW_INIT=0 -DTW_N=$n -DTW_K=$k -o ${name}_b$n ${name}_tw.c $H/drv.c; vs="$vs b$n"; done
echo "== $name '$pat' enc=$enc frameless=$fl"
for s in "$@"; do printf "%-14s" $(basename $s .bin); for v in $vs; do r=$(./${name}_$v $s 7); echo -n "$v=$(echo $r | sed 's/.*matches=\([0-9]*\).*med_ns_per_B=\([0-9.]*\).*/\2(\1)/') "; done; echo; done
