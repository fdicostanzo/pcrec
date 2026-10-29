#!/usr/bin/env bash
# run every P9 variant's driver over a subject group; prints per-file rows
S=${S:?scratch dir}; B=${B:?pcrec-bench/bench}
for n in ctx-lazy-64 ctx-lazy-256 ctx-lazy-1024 ctx-greedy-256 level-context; do
  case $n in
    ctx*) T="$B/bounded/throughput/*.bin"; SH="$B/bounded/subjects/*.bin"; X="$S/subj/stress-ctx.bin $S/subj/edge-ctx.bin";;
    *) T="$B/loglines/throughput/*.bin"; SH="$B/loglines/subjects/*.bin"; X="$S/subj/stress-lvl.bin $S/subj/edge-lvl.bin";;
  esac
  for v in auto vm autoseed autofind vmfind vmfind0 vmfindm1; do
    for g in T SH X; do
      eval files=\$$g
      taskset -c 7 gnutimeout 120 $S/p9/$n-$v/drv 3 $files | sed "s/^/$n\t$v\t$g\t/"
    done
  done
done
