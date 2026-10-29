#!/bin/bash
# mk.sh K MODE : build twin K (cscan|json) in MODE (stock|B|C|BC) into $V/b/K_MODE/drv
V=/var/tmp/pcrec-pcrec/scratch/vmbc; G=/var/tmp/pcrec-pcrec/scratch/trailgc2/gap; O=/var/tmp/pcrec-pcrec/scratch/trailgc; W=/home/pcrec/projects/pcrec/worktrees/trailgc
k=$1; m=$2; d=$V/b/${k}_$m; mkdir -p $d; cp $G/$k/rx.h $d/rx.h
if [ $m = stock ]; then cp $G/$k/rx.c $d/rx.c; else python3 $V/tools/vmopt.py -m $m $G/$k/rx.c $d/rx.c 2>$d/vmopt.log || exit 1; fi
gcc -O2 -g -std=gnu11 $EXTRA -I$W/lib -I$d -DHDR='"rx.h"' -DPFX_search=rx_search -DPFX_search_in=rx_search_in -DPFX_NCAPS=RX_NCAPS -DPFX_RESUME_FRAME_SIZE=RX_RESUME_FRAME_SIZE -DPFX_TRAIL_FRAME_SIZE=RX_TRAIL_FRAME_SIZE -DPFX_buffers=rx_buffers -o $d/drv $O/drv.c $d/rx.c 2>$d/gcc.log || { cat $d/gcc.log | head; exit 1; }
