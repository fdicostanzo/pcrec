#!/bin/bash
# build.sh NAME COMPILER PATTERN-FILE  -> $S/b/NAME/{gen.c,drv}
S=/var/tmp/pcrec-pcrec/scratch/trailgc3
name=$1; pc=$2; pat=$(cat $3); o=$S/b/$name; mkdir -p $o
gnutimeout 120 $pc --features all -p rx -o $o/gen.c --pattern "$pat" || { echo "compile fail $name"; exit 1; }
gcc -O2 -o $o/drv -I$o $S/drv.c $o/gen.c || exit 1
gcc -O2 -DRX_TEST_TIER_HOOK -o $o/drvh -I$o $S/drvh.c $o/gen.c || exit 1
echo "$name checks=$(command grep -c '_TRAIL_CHECK()' $o/gen.c)"
