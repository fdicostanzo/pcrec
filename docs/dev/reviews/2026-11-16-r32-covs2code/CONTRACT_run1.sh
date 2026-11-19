#!/usr/bin/env bash
# run1.sh NAME PATTERN SUBJ_PY_EXPR [pcrec args]  -> summary line
D=/var/tmp/pcrec-pcrec/scratch/crit-covs2code/CONTRACT
n="$1"; pat="$2"; py="$3"; shift 3
mkdir -p $D/c/$n; printf '%s' "$pat" > $D/c/$n/pat
python3 -I -c "
import random; random.seed(7)
L=$py
open('$D/c/$n/s.hex','w').write(''.join(x.hex()+'\n' for x in L))"
export PCREC_TMPDIR=$D TMPDIR=$D
out=$(/var/tmp/pcrec-pcrec/scratch/crit-covs2code/kit/kit.sh ${TREE:-subject} $D/c/$n/o $D/c/$n/pat $D/c/$n/s.hex "$@")
echo "$out" > $D/c/$n/kit.out
echo "$n: $(echo "$out" | grep -E 'PCREC_RC|ROUTE|^kit' | tr '\n' ' ') SAME=$(echo "$out" | grep -c ^SAME) DIFF=$(echo "$out" | grep -c ^DIFF)"
