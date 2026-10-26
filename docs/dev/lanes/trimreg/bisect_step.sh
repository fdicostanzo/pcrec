#!/bin/bash
# usage: bisect_step.sh WORKTREE ; exit 0 good (<30us), 1 bad, 125 skip
W=$1; L=/home/pcrec/projects/pcrec/worktrees/trimreg/docs/dev/lanes/trimreg
S=/home/pcrec/projects/pcrec-bench/bench/capability/throughput/t-trim-match-60k.bin
gnutimeout 300 make -C $W -j8 build/pcrec >/dev/null 2>&1 || exit 125
rm -f $W/build/a.c $W/build/a.h
gnutimeout 60 $W/build/pcrec -p rx --features all -o $W/build/a.c --pattern '\s+$' >/dev/null 2>&1 || exit 125
grep -q 'rx_search' $W/build/a.h || exit 125
gcc -O2 -std=gnu11 -DART="\"$W/build/a.c\"" -o $W/build/drv $L/drv.c 2>/dev/null || exit 125
t=$(gnutimeout 120 $W/build/drv $S 300 | tail -1 | sed 's/.* \([0-9.]*\) ns.*/\1/')
echo "$(git -C $W rev-parse --short HEAD) $t ns"
awk -v t="$t" 'BEGIN{exit !(t<30000)}' && exit 0 || exit 1
