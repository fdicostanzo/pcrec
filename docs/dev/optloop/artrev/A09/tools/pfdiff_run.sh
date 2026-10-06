#!/bin/bash
# usage: run.sh ARM -- compare rx_prefilter's return and window START, orig vs ARM, at every search_from
D=/Users/fdicostanzo/pcrec/worktrees/rvA09-cell/build-artrev/loglines_level_context
W=$D/scratch_rv/pfdiff; T=$W/b_$1; mkdir -p $T
gcc-16 -O1 -g -fsanitize=address,undefined -w -c -I$D/arms/orig -DARMNAME=orig $W/wrap.c -o $T/o.o && \
gcc-16 -O1 -g -fsanitize=address,undefined -w -c -I$D/arms/$1 -DARMNAME=twin $W/wrap.c -o $T/t.o && \
gcc-16 -O1 -g -fsanitize=address,undefined $W/main.c $T/o.o $T/t.o -o $T/x && \
$T/x $D/../../docs/dev/optloop/artrev/A09/edge_subjects/e-*.bin $D/../subjects/loglines/search/s-*.bin $D/../subjects/loglines/throughput/t-016k-*.bin $D/../subjects/loglines/throughput/t-064k-hit.bin
