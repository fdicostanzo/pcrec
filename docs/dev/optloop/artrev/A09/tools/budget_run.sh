#!/bin/bash
# usage: run.sh ARM STEPS WORK -- orig vs ARM with the step/work budgets shrunk, plus _in with 0/1 frames and trail
D=/Users/fdicostanzo/pcrec/worktrees/rvA09-cell/build-artrev/loglines_level_context
W=$D/scratch_rv/budget; T=$W/b_$1_$2_$3; mkdir -p $T/o $T/t
for a in orig:o $1:t; do src=${a%%:*}; dst=$T/${a##*:}; cp $D/artifact.h $dst/; sed -e "s/^#define RX_STEP_BUDGET .*/#define RX_STEP_BUDGET $2LL/" -e "s/^#define RX_WORK_BUDGET .*/#define RX_WORK_BUDGET $3LL/" $D/arms/$src/artifact.c > $dst/artifact.c; done
gcc-16 -O1 -g -fsanitize=address,undefined -w -c -I$T/o -DARMNAME=orig $D/scratch_rv/pfdiff/wrap.c -o $T/o.o && \
gcc-16 -O1 -g -fsanitize=address,undefined -w -c -I$T/t -DARMNAME=twin $D/scratch_rv/pfdiff/wrap.c -o $T/t.o && \
gcc-16 -O1 -g -fsanitize=address,undefined -I$D $W/main.c $T/o.o $T/t.o -o $T/x && \
$T/x $D/../../docs/dev/optloop/artrev/A09/edge_subjects/e-*.bin $D/../subjects/loglines/search/s-*.bin $D/../subjects/loglines/throughput/t-016k-hit.bin
