#!/bin/bash
# mkv.sh SRCDIR OUTDIR MODE [DRIVER] : twin MODE (variants.py) of SRCDIR/rx.c + rx.h into OUTDIR/{rx.c,rx.h,drv}
# DRIVER: lane trailgc's drv.c (default; modes d/r/in) or gdrv.c (global scan, default arm)
T=/var/tmp/pcrec-pcrec/scratch/trailgen; O=/var/tmp/pcrec-pcrec/scratch/trailgc; W=/home/pcrec/projects/pcrec/worktrees/trailgen
src=$1; d=$2; m=$3; drvc=${4:-$O/drv.c}
mkdir -p "$d" && cp "$src/rx.h" "$d/rx.h" || exit 1
case "$m" in *P*) sed -i 's/^#define RX_TRAIL_FRAME_SIZE 16$/#define RX_TRAIL_FRAME_SIZE 8/' "$d/rx.h";; esac
python3 -I $T/variants.py "$m" "$src/rx.c" "$d/rx.c" 2>"$d/variants.log" || { cat "$d/variants.log"; exit 3; }
gcc -O2 -g -std=gnu11 $EXTRA -I$W/lib -I"$d" -DHDR='"rx.h"' -DPFX_search=rx_search -DPFX_search_in=rx_search_in \
  -DPFX_NCAPS=RX_NCAPS -DPFX_RESUME_FRAME_SIZE=RX_RESUME_FRAME_SIZE -DPFX_TRAIL_FRAME_SIZE=RX_TRAIL_FRAME_SIZE \
  -DPFX_buffers=rx_buffers -o "$d/drv" "$drvc" "$d/rx.c" 2>"$d/gcc.log" || { head "$d/gcc.log"; exit 1; }
