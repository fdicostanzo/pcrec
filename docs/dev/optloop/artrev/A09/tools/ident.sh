#!/bin/bash
# usage: ident.sh ARM [--san]
cd /Users/fdicostanzo/pcrec/worktrees/rvA09-cell
export ARTREV_CC=gcc-16 ARTREV_HOST_ROOT=/Users/fdicostanzo/pcrec
S=()
for f in build-artrev/subjects/loglines/throughput/t-*.bin build-artrev/subjects/loglines/search/s-*.bin docs/dev/optloop/artrev/A09/edge_subjects/e-*.bin; do S+=(--subject "$f"); done
arm=$1; shift
python3 -B studies/artrev/artrev.py identity loglines_level_context "$arm" "${S[@]}" --corpus --battery 3000 --block 16 --match-example 'ERROR x timeout' --match-example 'CRIT timed out' "$@"
