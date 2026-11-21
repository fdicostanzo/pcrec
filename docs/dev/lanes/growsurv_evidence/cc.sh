#!/bin/bash
W=/home/pcrec/projects/pcrec/worktrees/growsurv; S=$S
f=$1; b=${f#$W/}; b=${b//\//_}; b=${b%.c}
gcc -O2 -g -std=gnu11 -I$W/lib -I$W/src -I$W/memfn/include -I$W/memfn/src -I$W -fstack-usage -fcallgraph-info=su -c $f -o $S/o/$b.o 2>$S/o/$b.err || echo FAIL $b
