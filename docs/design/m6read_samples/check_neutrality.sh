#!/bin/sh
# [M6-READ] OBJECT-CODE NEUTRALITY CHECK for the style-sample pairs.
#
# The readability pass may only add comments and rename identifiers.
# Neither can change what the machine executes, so the before/after
# artifacts must compile to the same code. This script proves it for the
# samples in this directory; README.md ("Where the gate lives") says
# where the landed version belongs.
#
# WHAT "NEUTRAL" MEANS HERE, precisely -- the sample stage found this
# needs stating, because the naive check gives a false alarm:
#
#   (a) EXECUTED CODE must be byte-identical. Compared as the raw
#       contents of .text and .rodata, which contain no names at all.
#       This is the property that matters and the one this gate enforces.
#
#   (b) INTERNAL SYMBOL NAMES change by construction. Renaming a static
#       function or a function-local static array renames its
#       internal-linkage symbol, which is visible in `objdump -d`
#       annotations, in the symbol table and in debug info. It is not
#       executed code, it does not survive `strip`, and no caller can
#       observe it -- but a check that diffs disassembly TEXT will flag
#       it. This script reports the delta rather than hiding it.
#
#   (c) EXPORTED symbols must not change at all. Checked separately: any
#       difference in the GLOBAL symbols is a real ABI break and fails.
#
# Exit 0 = neutral. Exit 1 = executed code or an exported symbol moved.

set -e
cd "$(dirname "$0")"
CC=${CC:-gcc}
CFLAGS="-O2 -g0 -std=gnu11 -Wall -Wextra"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
rc=0

for pair in dfa vm; do
    for side in before after; do
        o="$TMP/${pair}_${side}.o"
        $CC $CFLAGS -c "${pair}_${side}.c" -o "$o"
        # (a) executed code and constant data, as raw bytes
        # grep -v drops objdump's banner, which names the .o file
        { objdump -s -j .text "$o"; objdump -s -j .rodata "$o"; } \
            | grep -v 'file format' > "$TMP/${pair}_${side}.bytes"
        # (c) exported (global) symbols only
        nm --defined-only -g "$o" | awk '{print $2, $3}' | sort \
            > "$TMP/${pair}_${side}.gsyms"
        # (b) informational: all symbols
        nm "$o" | awk '{print $NF}' | sort > "$TMP/${pair}_${side}.allsyms"
    done

    if diff -q "$TMP/${pair}_before.bytes" "$TMP/${pair}_after.bytes" >/dev/null; then
        echo "PASS $pair (a) .text + .rodata byte-identical"
    else
        echo "FAIL $pair (a) executed code differs:"
        diff -u "$TMP/${pair}_before.bytes" "$TMP/${pair}_after.bytes" | head -40
        rc=1
    fi

    if diff -q "$TMP/${pair}_before.gsyms" "$TMP/${pair}_after.gsyms" >/dev/null; then
        echo "PASS $pair (c) exported symbols unchanged"
    else
        echo "FAIL $pair (c) exported symbols differ -- ABI BREAK:"
        diff -u "$TMP/${pair}_before.gsyms" "$TMP/${pair}_after.gsyms"
        rc=1
    fi

    n=$(diff "$TMP/${pair}_before.allsyms" "$TMP/${pair}_after.allsyms" \
        | grep -c '^[<>]' || true)
    echo "INFO $pair (b) internal symbol names renamed: $n (expected, not executed code)"
done
exit $rc
