#!/usr/bin/env bash
# span_pick stage 2, S2b: census0's CONTROL (span_cards.md §7). On smp20's site census0 must reproduce
# smp20.out (the committed golden: the rev 5 lines, incl. the `incumbent @` lines, plus ONE P-blind grid
# line) byte for byte. witness.out and the bundle listings are witness.sh's.
#   bash census0_control.sh BUNDLEDIR     (BUNDLEDIR holds default.list prose.list log.list weblog.list)
# Prints `census0 control: GREEN` or the diff and exits 1.
set -u
here=$(dirname "$(readlink -f "$0")")
B=$1
out=$(python3 -I "$here/census0.py" control "$here/witness.out" "$B/default.list" \
    -- prose="$B/prose.list" log="$B/log.list" weblog="$B/weblog.list") || { echo "census0 failed" >&2; exit 1; }
if d=$(diff "$here/smp20.out" <(printf '%s\n' "$out")); then echo "census0 control: GREEN"; else
    printf '%s\n' "$d"; echo "census0 control: RED"; exit 1; fi
