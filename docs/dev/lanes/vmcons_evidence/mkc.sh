#!/bin/bash
# mkc.sh K NAME BMODE DMODE R : lane vmcons COMPOSED twin of vmbc's b/K_stock/rx.c (base lane/trailgc 801ad1214)
#   BMODE: vmopt_tg.py mode (Bd BCd BdU BCdU) or none;  DMODE: altd mode (none A ALkf);  R: R or none
S=/var/tmp/pcrec-pcrec/scratch/vmcons; V=/var/tmp/pcrec-pcrec/scratch/vmbc; A=/var/tmp/pcrec-pcrec/scratch/altd; O=/var/tmp/pcrec-pcrec/scratch/trailgc
W=/home/pcrec/projects/pcrec/worktrees/vmcons
k=$1; n=$2; bm=$3; dm=$4; r=$5; d=$S/b/${k}_$n; mkdir -p $d; cp $V/b/${k}_stock/rx.h $d/rx.h; : > $d/log
cp $V/b/${k}_stock/rx.c $d/s0.c
if [ $bm != none ]; then python3 -I $S/tools/vmopt_tg.py -m $bm $d/s0.c $d/s1.c 2>>$d/log || { cat $d/log; exit 1; }; else cp $d/s0.c $d/s1.c; fi
if [ $dm != none ]; then
  mm=${dm%%[pfk]*}; RULE=all; FOL=0; case $dm in *k*) RULE=kind;; esac; case $dm in *f*) FOL=1;; esac
  ALTD_TMP=$S/tmp ALTD_RULE=$RULE ALTD_FOLLOW=$FOL ALTD_CFLAGS="-I$W/lib -I$d" python3 -I $S/tools/altd.py -m $mm $d/s1.c $A/$k.ir $d/s2.c 2>>$d/log || { cat $d/log; exit 1; }
else cp $d/s1.c $d/s2.c; fi
if [ $r = R ]; then python3 -I $S/tools/variants.py R $d/s2.c $d/rx.c 2>>$d/log || { cat $d/log; exit 3; }; else cp $d/s2.c $d/rx.c; fi
F="-std=gnu11 -I$W/lib -I$d -DHDR=\"rx.h\" -DPFX_search=rx_search -DPFX_search_in=rx_search_in -DPFX_NCAPS=RX_NCAPS -DPFX_RESUME_FRAME_SIZE=RX_RESUME_FRAME_SIZE -DPFX_TRAIL_FRAME_SIZE=RX_TRAIL_FRAME_SIZE -DPFX_buffers=rx_buffers"
gcc -O2 -g $F -o $d/drv $O/drv.c $d/rx.c 2>$d/gcc.log || { head $d/gcc.log; exit 1; }
gcc -O2 $F -o $d/cdrv $V/cdrv.c $d/rx.c 2>>$d/gcc.log || { head $d/gcc.log; exit 1; }
python3 -I - $d/rx.c $d/rxp.c <<'PY'
import sys
t=open(sys.argv[1]).read()
t=t.replace("#define RX_PUSH(lbl_, p_) do {", "unsigned long long altd_npush;\n#define RX_PUSH(lbl_, p_) do { altd_npush++;",1)
open(sys.argv[2],"w").write(t)
PY
gcc -O2 $F -DPDRV -o $d/pdrv $A/pdrv.c $d/rxp.c 2>>$d/gcc.log || echo "pdrv build failed (R twin renames the push macro?)"
tail -3 $d/log | cut -c1-300
