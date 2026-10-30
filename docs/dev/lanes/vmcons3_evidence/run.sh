#!/bin/bash
# usage: run.sh OUTDIR NAME CFILE subj...
# Compiles CFILE (header CFILE minus .c plus .h, or the un-twinned header) with
# drv.c and runs it on each subject under scripts/watchdog. drv.c/p2.c are the
# r8 soundness critic's drivers, copied unchanged.
E=$(cd "$(dirname "$0")" && pwd)
R=/home/pcrec/projects/pcrec/worktrees/vmcons3
o=$1; n=$2; c=$3; shift 3
h=${c%.c}.h
[ -f "$h" ] || h=$(dirname "$c")/$(basename "$c" .c | sed 's/_twin.*//').h
gcc -O1 -w -o "$o/$n.bin" "$c" "$E/drv.c" -DHDR="\"$h\"" || exit 1
"$R/scripts/watchdog" -s 20 -m 1g -S vmcons3 -- "$o/$n.bin" "$@"
