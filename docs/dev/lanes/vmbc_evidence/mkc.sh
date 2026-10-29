#!/bin/bash
# mkc.sh DIR : build DIR/cdrv from DIR/rx.c + DIR/rx.h
V=/var/tmp/pcrec-pcrec/scratch/vmbc; W=/home/pcrec/projects/pcrec/worktrees/trailgc; d=$1
gcc -O2 -std=gnu11 -I$W/lib -I$d -DHDR='"rx.h"' -DPFX_search=rx_search -DPFX_search_in=rx_search_in -DPFX_NCAPS=RX_NCAPS -DPFX_RESUME_FRAME_SIZE=RX_RESUME_FRAME_SIZE -DPFX_TRAIL_FRAME_SIZE=RX_TRAIL_FRAME_SIZE -DPFX_buffers=rx_buffers -o $d/cdrv $V/cdrv.c $d/rx.c
