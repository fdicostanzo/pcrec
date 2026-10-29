#!/bin/bash
# meas.sh PAT SUBJ REPS MODE VARIANTS... : instructions:u per variant (min of 3), and % vs the first variant
S=/var/tmp/pcrec-pcrec/scratch/trailgc3
p=$1; s=$2; r=$3; m=$4; shift 4; first=
for v in "$@"; do
  out=$($S/b/${p}_$v/drvh $S/subj/$s.txt 1 $m)
  i=$(perf stat -x, -e instructions:u -r 3 $S/b/${p}_$v/drv $S/subj/$s.txt $r $m 2>&1 >/dev/null | awk -F, '{print $1}')
  [ -z "$first" ] && first=$i
  printf '%-7s %-12s mode=%s %-6s instr=%-12s %+6.2f%%  [%s]\n' $p $s $m $v $i $(echo "scale=4; ($i-$first)*100/$first" | bc) "$out"
done
