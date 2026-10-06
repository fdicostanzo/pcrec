#!/bin/bash
# usage: count_arm.sh ARM  -- work counts per MiB over the 12 throughput subjects
D=/Users/fdicostanzo/pcrec/worktrees/rvA09-cell/build-artrev/loglines_level_context
mkdir -p $D/scratch_rv/cnt_$1 && cp $D/artifact.h $D/scratch_rv/cnt_$1/ && python3 $D/scratch_rv/mkcount2.py $D/arms/$1/artifact.c $D/scratch_rv/cnt_$1/artifact.c && gcc-16 -O2 -I$D/scratch_rv/cnt_$1 $D/scratch_rv/drvsrc/drv2.c -o $D/scratch_rv/cnt_$1/drv && $D/scratch_rv/cnt_$1/drv $D/../subjects/loglines/throughput/t-1024k-*.bin $D/../subjects/loglines/throughput/t-016k-*.bin
