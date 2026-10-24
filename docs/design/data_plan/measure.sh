#!/bin/bash
# measure.sh NAME ARGS... : main's pcrec -> gcc -O2 -c; c bytes, .text (code), .rodata (tables), total loadable
D=${OUT:-/tmp/claude-1001/datad/m}; P=${PCREC:-/home/pcrec/projects/pcrec/build/pcrec}; export TMPDIR=${TMPDIR:-$D}
name=$1; shift
gnutimeout 60 $P "$@" -o $D/$name.c >$D/$name.err 2>&1 || { echo "$name FAIL $(head -1 $D/$name.err)"; exit 0; }
gnutimeout 300 gcc -O2 -c $D/$name.c -o $D/$name.o 2>>$D/$name.err || { echo "$name GCCFAIL"; exit 0; }
eng=$(command grep -m1 '#define RX_ENGINE "' $D/$name.c | cut -d'"' -f2)
size -A $D/$name.o | awk -v n=$name -v e=$eng -v c=$(stat -c%s $D/$name.c) '
 $1==".text"{t+=$2} $1 ~ /^\.rodata/{r+=$2} $1 ~ /^\.data/{d+=$2}
 END{printf "%-12s %-4s c=%8d code=%7d tables=%7d data=%4d  load=%7d\n", n,e,c,t,r,d,t+r+d}'
