#!/bin/bash
# [OPT-REVEND] hand-twin timing, SCRATCH TIER (STUDY).
#   ./run_timing.sh [CPU]        (after run_check.sh has built work/art/)
# The bench's acceptance cells (O-91 (c) and ask (2)): five tail patterns x
# the three t-tail-*-1m SHAPES, the tail-space x t-trim-nearmiss-16k cell,
# and tail-digits x t-1m. Subjects are mksubj.py's synthesized stand-ins,
# NOT the bench's bytes. Pinned to one CPU with taskset; load1 printed per
# run, because another chain may share the box.
set -u
HERE=$(cd "$(dirname "$0")" && pwd); W=$HERE/work; S=$W/subj
A=$W/art${TWIN_FORM:+-$TWIN_FORM}   # TWIN_FORM=lower times form B (run_check.sh with the same TWIN_FORM builds it)
CPU=${1:-7}
cells="tail-digits-eol tail-word-eoz tail-space-eol tail-ext-lower-txt tail-dotstar-txt"
for name in $cells; do
    d=$A/$name
    gcc -O2 -w -I"$d" -o "$d/timedrv" "$HERE/timedrv.c" "$d/o.c" "$d/t.c" || { echo "$name CCFAIL"; continue; }
    subs="t-tail-digits-1m t-tail-txt-1m t-tail-space-1m"
    [ "$name" = tail-space-eol ] && subs="$subs t-trim-nearmiss-16k"
    [ "$name" = tail-digits-eol ] && subs="$subs t-1m"
    for s in $subs; do
        printf '%-19s %-20s load1=%s | ' "$name" "$s" "$(cut -d' ' -f1 /proc/loadavg)"
        taskset -c "$CPU" gnutimeout 300 "$d/timedrv" "$S/$s.bin" 20 15
    done
done
