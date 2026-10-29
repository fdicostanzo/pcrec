#!/bin/bash
# mk.sh K BASE MODE : twin K (cscan|json) from vmbc's b/K_BASE/rx.c (BASE stock|BCd) with altd MODE (none|A|AL) -> b/K_BASE_MODE/{drv,cdrv,pdrv}
A=/var/tmp/pcrec-pcrec/scratch/altd; V=/var/tmp/pcrec-pcrec/scratch/vmbc; O=/var/tmp/pcrec-pcrec/scratch/trailgc; W=/home/pcrec/projects/pcrec/worktrees/trailgc
k=$1; base=$2; m=$3; d=$A/b/${k}_${base}_$m; mkdir -p $d; cp $V/b/${k}_$base/rx.h $d/rx.h
mm=${m%%[pfk]*}; RULE=all; FOL=0; case $m in *p*) RULE=pref;; *k*) RULE=kind;; esac; case $m in *f*) FOL=1;; esac
if [ $m = none ]; then cp $V/b/${k}_$base/rx.c $d/rx.c; else ALTD_RULE=$RULE ALTD_FOLLOW=$FOL ALTD_CFLAGS="-I$W/lib -I$d" python3 -I $A/tools/altd.py -m $mm $V/b/${k}_$base/rx.c $A/$k.ir $d/rx.c 2>$d/altd.log || { cat $d/altd.log; exit 1; }; fi
F="-std=gnu11 -I$W/lib -I$d -DHDR=\"rx.h\" -DPFX_search=rx_search -DPFX_search_in=rx_search_in -DPFX_NCAPS=RX_NCAPS -DPFX_RESUME_FRAME_SIZE=RX_RESUME_FRAME_SIZE -DPFX_TRAIL_FRAME_SIZE=RX_TRAIL_FRAME_SIZE -DPFX_buffers=rx_buffers"
gcc -O2 -g $F -o $d/drv $O/drv.c $d/rx.c 2>$d/gcc.log || { head $d/gcc.log; exit 1; }
gcc -O2 $F -o $d/cdrv $V/cdrv.c $d/rx.c 2>>$d/gcc.log || exit 1
# push-counting build: count RX_PUSH executions
sed 's/^#define RX_PUSH(lbl_, p_) do {   /unsigned long long altd_npush; #define RX_PUSH(lbl_, p_) do { altd_npush++;/' $d/rx.c > $d/rxp.c
python3 -I - $d/rx.c $d/rxp.c <<'PY'
import sys,re
t=open(sys.argv[1]).read()
t=t.replace("#define RX_PUSH(lbl_, p_) do {", "unsigned long long altd_npush;\n#define RX_PUSH(lbl_, p_) do { altd_npush++;",1)
open(sys.argv[2],"w").write(t)
PY
gcc -O2 $F -DPDRV -o $d/pdrv $A/pdrv.c $d/rxp.c 2>>$d/gcc.log || exit 1
tail -1 $d/altd.log 2>/dev/null; true
