#!/usr/bin/env bash
# bld.sh DIR: build DIR/ID.ARM.c into DIR/ID.ARM.bin with drv.c (artifact its own TU, -O2 -fPIC like the bench shim)
S=/var/tmp/pcrec-pcrec/scratch/p48; D=$1
for c in "$D"/*.c; do
  b=${c%.c}; gcc -O2 -fPIC -c -o "$b.o" "$c" -I"$D" 2>"$b.ccerr" || { echo "CC FAIL $c"; continue; }
  gcc -O2 -o "$b.bin" "$S/drv.c" "$b.o" || echo "LD FAIL $c"
done
