#!/bin/bash
# xover.sh NAME PATTERN ENC UNITPY : UNITPY is a python expr of g giving the repeating unit (bytes)
: "${PCREC_BASE:?set PCREC_BASE to the branch-point (abi 46) compiler}"; H="$(cd "$(dirname "$0")" && pwd)"
name=$1; pat=$2; enc=$3; unit=$4
eopt=""; [ "$enc" = utf8 ] && eopt="-e utf8"
$PCREC_BASE --features all -p rx $eopt -o $name.c --pattern "$pat" 2>/dev/null || { echo "$name: compile failed"; exit 1; }
pf=$(grep -h "define RX_VM_PREFILTER " $name.c | awk '{print $3}')
[ "$pf" = '"hybrid"' ] || { echo "$name: not hybrid ($pf)"; exit 0; }
python3 $H/twin.py $name.c ${name}_tw.c
fl=$(grep -h "VM_FRAMELESS" $name.c | awk '{print $3}')
lb=$(grep -h "define RX_VM_PROGRAM_BYTES" $name.c | awk '{print $3}')
gcc-16 -O2 -DTW_MODE=0 -DTW_INIT=0 -o ${name}_step ${name}_tw.c $H/drv.c
gcc-16 -O2 -DTW_MODE=1 -DTW_INIT=0 -o ${name}_reseed ${name}_tw.c $H/drv.c
line="$name fl=$fl prog=$lb :"
for g in 1 2 3 4 6 8 12 16 24 32; do
  python3 -c "
g=$g;N=1<<19;u=$unit
open('xs.bin','wb').write((u*(N//len(u)+1))[:N])"
  a=$(./${name}_step xs.bin 5 | sed 's/.*med_ns_per_B=\([0-9.]*\).*/\1/'); b=$(./${name}_reseed xs.bin 5 | sed 's/.*med_ns_per_B=\([0-9.]*\).*/\1/')
  line="$line g$g:$(python3 -c "print('%.2f'%($a/$b))")"
done
echo "$line   (step/reseed ratio; >1 means reseed wins)"
