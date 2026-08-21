#!/bin/sh
# [M6-READ] OBJECT-CODE NEUTRALITY CHECK for the style-sample pair.
#
# The readability pass may only add comments and rename locals. Neither
# can change what the compiler emits, so the two artifacts must compile
# to the same machine code. This script proves it for the samples in
# this directory; the landed version of this gate is described in
# README.md ("Where the gate lives").
#
# Compares, for each before/after pair:
#   (a) the disassembly of every function (objdump -d), and
#   (b) the .rodata bytes, which is where the tables live.
# The only permitted difference is the object file's own name in
# objdump's banner line, which is stripped.
#
# Exit 0 = neutral. Exit 1 = a difference was found; the diff is printed.

set -e
cd "$(dirname "$0")"
CC=${CC:-gcc}
CFLAGS="-O2 -g0 -std=gnu11 -Wall -Wextra"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
rc=0

for pair in dfa vm; do
    for side in before after; do
        $CC $CFLAGS -c "${pair}_${side}.c" -o "$TMP/${pair}_${side}.o"
        objdump -d --no-show-raw-insn "$TMP/${pair}_${side}.o" \
            | sed '1,2d' > "$TMP/${pair}_${side}.txt"
        objdump -s -j .rodata "$TMP/${pair}_${side}.o" \
            | sed '1,2d' > "$TMP/${pair}_${side}.rodata"
    done
    if diff -u "$TMP/${pair}_before.txt" "$TMP/${pair}_after.txt" > "$TMP/${pair}.diff" \
       && diff -u "$TMP/${pair}_before.rodata" "$TMP/${pair}_after.rodata" \
            >> "$TMP/${pair}.diff"; then
        echo "PASS $pair: disassembly and .rodata identical"
    else
        echo "FAIL $pair: object code differs"
        cat "$TMP/${pair}.diff"
        rc=1
    fi
done
exit $rc
